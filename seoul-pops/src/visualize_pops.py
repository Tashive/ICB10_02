"""
이 스크립트는 행정동코드 매핑 엑셀 파일에서 연남동과 성수동의 행정동 코드를 추출한 후,
생활인구 Parquet 데이터에서 해당 동의 데이터를 필터링합니다.
필터링된 데이터를 바탕으로 시간대별, 행정동별 생활인구수 변화 추이를
연령대별 서브플롯(y축 방향 배치)으로 시각화한 선그래프 이미지를 생성합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    excel_path = 'seoul-pops/data/행정동코드_매핑정보_20241218.xlsx'
    parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized.parquet'
    output_img_path = 'seoul-pops/images/population_trend.png'
    
    print("1. Loading mapping Excel and finding Yeonnam/Seongsu codes...")
    df_map = pd.read_excel(excel_path)
    df_map.columns = df_map.iloc[0]
    df_map = df_map.iloc[1:].reset_index(drop=True)
    
    # Filter Yeonnam-dong and Seongsu-dong
    targets = df_map[df_map['H_DNG_NM'].str.contains('연남|성수', na=False)].copy()
    print("Found target mapping:")
    print(targets[['H_DNG_CD', 'H_DNG_NM']])
    
    # Create code to name map (ensure code is string since we casted Parquet to string category)
    code_to_name = dict(zip(targets['H_DNG_CD'].astype(str), targets['H_DNG_NM']))
    target_codes = list(code_to_name.keys())
    
    print("\n2. Loading optimized Parquet and filtering data...")
    df_pop = pd.read_parquet(parquet_path)
    
    # Filter by target codes (note that 행정동코드 in optimized parquet is string category)
    df_filtered = df_pop[df_pop['행정동코드'].isin(target_codes)].copy()
    df_filtered['행정동명'] = df_filtered['행정동코드'].astype(str).map(code_to_name)
    
    print(f"Filtered rows: {len(df_filtered)}")
    
    print("\n3. Aggregating data for visualization (mean over days)...")
    # Group by Hour, Dong Name, and Age Group to get the average population
    df_grouped = df_filtered.groupby(['시간대구분', '행정동명', '연령대'], as_index=False, observed=False)['생활인구수'].mean()
    
    print("\n4. Plotting line graph...")
    # Set Hangul Font
    plt.rc('font', family='Malgun Gothic')
    plt.rc('axes', unicode_minus=False)
    
    # We will use sns.relplot to create a FacetGrid with:
    # row='연령대' (arranges age groups along the y-axis of the grid)
    # x='시간대구분' (x-axis of each plot)
    # y='생활인구수' (y-axis value of each plot)
    # hue='행정동명' (different line colors per Dong)
    # height=3, aspect=4
    
    # Sort age groups logically if category is not sorted, but pandas category maintains correct sorting
    g = sns.relplot(
        data=df_grouped,
        x='시간대구분',
        y='생활인구수',
        hue='행정동명',
        row='연령대',
        kind='line',
        height=2.5,
        aspect=4,
        facet_kws={'sharey': False} # Allow different y-scales to observe patterns clearly
    )
    
    # Add title and adjust layout
    g.fig.subplots_adjust(top=0.95)
    g.fig.suptitle("연남동 및 성수동 시간대별/행정동별 생활인구 추이 (연령대별 분석)", fontsize=16, fontweight='bold')
    
    # Labels
    g.set_axis_labels("시간대 (0~23시)", "평균 생활인구수 (명)")
    
    # Save the plot
    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    plt.savefig(output_img_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nVisualization saved successfully to '{output_img_path}'")

if __name__ == '__main__':
    main()
