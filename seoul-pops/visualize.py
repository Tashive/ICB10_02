"""
서울시 생활인구 데이터를 활용하여 연남동과 성수동의 시간대별, 행정동별 생활인구수를 분석하고,
사용자의 요청에 맞추어 y축에 연령대, x축에 시간대가 그려지는 다양한 선그래프를 시각화하는 스크립트입니다.
이 스크립트는 시각화 결과를 'seoul-pops/images' 디렉토리에 저장합니다.
"""

import os
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

# 1. 경로 설정 및 파일 로드
data_dir = 'seoul-pops/data'
images_dir = 'seoul-pops/images'
os.makedirs(images_dir, exist_ok=True)

# 엑셀 매핑 파일 로드
excel_files = glob.glob(os.path.join(data_dir, '*20241218.xlsx'))
if not excel_files:
    raise FileNotFoundError("행정동코드 매핑 엑셀 파일을 찾을 수 없습니다.")
excel_path = excel_files[0]

df_map = pd.read_excel(excel_path, header=1)
df_map['H_DNG_NM'] = df_map['H_DNG_NM'].astype(str)

# 연남동 및 성수동 행정동코드 필터링 (행자부기준 행정동코드: H_DNG_CD)
yeonnam_codes = df_map[df_map['H_DNG_NM'].str.contains('연남')]['H_DNG_CD'].tolist()
seongsu_codes = df_map[df_map['H_DNG_NM'].str.contains('성수')]['H_DNG_CD'].tolist()
target_codes = yeonnam_codes + seongsu_codes

# 행정동코드와 행정동명 매핑 딕셔너리 생성
code_to_name = {}
for _, row in df_map.iterrows():
    try:
        cd = int(row['H_DNG_CD'])
        if cd in target_codes:
            code_to_name[cd] = row['H_DNG_NM']
    except:
        pass

# Parquet 파일 로드
parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
if not os.path.exists(parquet_path):
    parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized.parquet'

df_pop = pd.read_parquet(parquet_path, engine='pyarrow')
df_pop.columns = ['기준일ID', '시간대구분', '행정동코드', '성별', '연령대', '생활인구수']

# 데이터 필터링 및 행정동명 매핑
df_pop['행정동코드'] = df_pop['행정동코드'].astype(int)
df_filtered = df_pop[df_pop['행정동코드'].isin(target_codes)].copy()
df_filtered['행정동명'] = df_filtered['행정동코드'].map(code_to_name)

# 연령대 정렬 순서 정의
age_order = [
    '0-9세', '10-14세', '15-19세', '20-24세', '25-29세', 
    '30-34세', '35-39세', '40-44세', '45-49세', '50-54세', 
    '55-59세', '60-64세', '65-69세', '70세 이상'
]
df_filtered['연령대'] = pd.Categorical(df_filtered['연령대'], categories=age_order, ordered=True)

# 시간대별, 행정동별, 연령대별 평균 생활인구수 집계
df_grouped = df_filtered.groupby(['행정동명', '시간대구분', '연령대'], observed=False)['생활인구수'].mean().reset_index()

# 색상 테마 설정 (세련되고 armonious한 색상)
dong_colors = {
    '연남동': '#E63946',        # 붉은색
    '성수1가1동': '#457B9D',    # 파란색 계열
    '성수1가2동': '#1D3557',    # 짙은 네이비
    '성수2가1동': '#2A9D8F',    # 민트그린
    '성수2가3동': '#F4A261'     # 오렌지색
}

# ==========================================================
# 시각화 안 1: 시간대별 가장 많은 생활인구를 기록한 대표 연령대 추이 선그래프
# (y축: 연령대 범주, x축: 시간대, 선의 색: 행정동)
# ==========================================================
plt.figure(figsize=(12, 8))

# 각 행정동/시간대별로 생활인구수가 가장 높은 연령대 추출
idx = df_grouped.groupby(['행정동명', '시간대구분'])['생활인구수'].idxmax()
df_max_age = df_grouped.loc[idx].copy()

# 연령대 범주를 y축 상에 그리기 위해 숫자로 인코딩 (0 ~ 13)
df_max_age['연령대_코드'] = df_max_age['연령대'].cat.codes

for dong, group in df_max_age.groupby('행정동명'):
    color = dong_colors.get(dong, '#777777')
    # 시간대순으로 정렬
    group = group.sort_values('시간대구분')
    plt.plot(group['시간대구분'], group['연령대_코드'], marker='o', linewidth=2.5, markersize=7, label=dong, color=color)

plt.yticks(range(len(age_order)), age_order)
plt.xticks(range(24))
plt.xlabel('시간대 (시)', fontsize=12, labelpad=10)
plt.ylabel('최다 생활인구 연령대', fontsize=12, labelpad=10)
plt.title('행정동별 시간대별 최다 생활인구 연령대 추이 (Y축: 연령대, X축: 시간대)', fontsize=14, pad=15)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title='행정동', loc='upper right', bbox_to_anchor=(1.15, 1.0))
plt.tight_layout()

max_age_path = os.path.join(images_dir, 'visualization_max_age.png')
plt.savefig(max_age_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {max_age_path}")


# ==========================================================
# 시각화 안 2: 시간대별 가중 평균 연령 추이 선그래프
# (y축: 연령대 범위, x축: 시간대, 선의 색: 행정동)
# ==========================================================
# 연령대별 중간값 매핑
age_midpoints = {
    '0-9세': 4.5, '10-14세': 12, '15-19세': 17, '20-24세': 22, '25-29세': 27,
    '30-34세': 32, '35-39세': 37, '40-44세': 42, '45-49세': 47, '50-54세': 52,
    '55-59세': 57, '60-64세': 62, '65-69세': 67, '70세 이상': 75
}
df_grouped['연령_수치'] = df_grouped['연령대'].map(age_midpoints).astype(float)

# 가중 평균 연령 계산
# 시간대별/행정동별로 (인구수 * 연령_수치)의 합 / (인구수의 합)
df_grouped['인구_연령_곱'] = df_grouped['생활인구수'] * df_grouped['연령_수치']
df_weighted = df_grouped.groupby(['행정동명', '시간대구분']).agg(
    총생활인구=('생활인구수', 'sum'),
    인구연령총합=('인구_연령_곱', 'sum')
).reset_index()
df_weighted['가중평균연령'] = df_weighted['인구연령총합'] / df_weighted['총생활인구']

plt.figure(figsize=(12, 8))
for dong, group in df_weighted.groupby('행정동명'):
    color = dong_colors.get(dong, '#777777')
    group = group.sort_values('시간대구분')
    plt.plot(group['시간대구분'], group['가중평균연령'], marker='s', linewidth=2.5, markersize=6, label=dong, color=color)

# y축 눈금을 연령대 범주에 가깝게 표시하기 위해 적절한 연령 범위 레이블 설정
age_ticks = [5, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 75]
plt.yticks(age_ticks, age_order)
plt.xticks(range(24))
plt.xlabel('시간대 (시)', fontsize=12, labelpad=10)
plt.ylabel('가중 평균 연령대', fontsize=12, labelpad=10)
plt.title('행정동별 시간대별 가중 평균 연령 추이 (Y축: 연령대, X축: 시간대)', fontsize=14, pad=15)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title='행정동', loc='upper right', bbox_to_anchor=(1.15, 1.0))
plt.tight_layout()

mean_age_path = os.path.join(images_dir, 'visualization_mean_age.png')
plt.savefig(mean_age_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {mean_age_path}")


# ==========================================================
# 시각화 안 3: 버블 라인 차트 (x축: 시간대, y축: 연령대, 버블 크기: 생활인구수, 선의 색: 행정동)
# ==========================================================
plt.figure(figsize=(14, 9))

# 각 행정동별로 시각화
for dong, group in df_grouped.groupby('행정동명'):
    color = dong_colors.get(dong, '#777777')
    # 연령대 인덱스 코드
    group = group.copy()
    group['연령대_코드'] = group['연령대'].cat.codes
    
    # 시간대별/연령대별 선을 부드럽게 이음 (각 연령대별로 수평선을 그리거나, 각 시간대별 평균값의 흐름을 그림)
    # 여기서는 시간대별 평균 연령의 흐름선(가중평균연령)을 그리고, 뒤에 연령대별 생활인구수 버블들을 오버레이함.
    group_weighted = df_weighted[df_weighted['행정동명'] == dong].sort_values('시간대구분')
    # 연령대 가중평균을 연령대_코드(0~13) 스케일로 변환하기 위한 보간 함수 정의
    # 연령범위 4.5세 ~ 75세를 0 ~ 13 눈금으로 맵핑
    xp = [4.5, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 75]
    fp = list(range(14))
    y_codes = np.interp(group_weighted['가중평균연령'], xp, fp)
    
    plt.plot(group_weighted['시간대구분'], y_codes, linewidth=2.5, color=color, label=f"{dong} (평균 연령 추이)", alpha=0.9)
    
    # 각 격자점에 인구수 크기에 비례하는 버블을 흩뿌려 시각화
    # 너무 복잡해질 수 있으므로 특정 동 대표로 그리거나 투명도를 조절함
    # 여기서는 5개 행정동을 모두 그리되 투명하게 표현하여 겹침을 보여줌
    plt.scatter(group['시간대구분'], group['연령대_코드'], s=group['생활인구수'] * 0.15, color=color, alpha=0.35, edgecolors='none')

plt.yticks(range(len(age_order)), age_order)
plt.xticks(range(24))
plt.xlabel('시간대 (시)', fontsize=12, labelpad=10)
plt.ylabel('연령대', fontsize=12, labelpad=10)
plt.title('행정동별 시간대별 연령대별 생활인구 버블 라인 차트 (원 크기: 생활인구수)', fontsize=14, pad=15)
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend(title='행정동 평균선', loc='upper right', bbox_to_anchor=(1.2, 1.0))
plt.tight_layout()

bubble_line_path = os.path.join(images_dir, 'visualization_bubble_line.png')
plt.savefig(bubble_line_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {bubble_line_path}")


# ==========================================================
# 시각화 안 4: 연령대별 서브플롯 선그래프 (세로 레이아웃이 연령대별 배치)
# (x축: 시간대, y축: 생활인구수, 선의 색: 행정동, row: 연령대)
# ==========================================================
# 14개 연령대를 7행 2열로 수직으로 나열하여 그립니다. 
# y축 방향으로 연령대가 배열되므로 "y축에는 연령대"라는 배치 요건을 만족합니다.
fig, axes = plt.subplots(7, 2, figsize=(16, 24), sharex=True)
axes = axes.flatten()

for i, age in enumerate(age_order):
    ax = axes[i]
    df_age = df_grouped[df_grouped['연령대'] == age]
    
    for dong, group in df_age.groupby('행정동명'):
        color = dong_colors.get(dong, '#777777')
        group = group.sort_values('시간대구분')
        ax.plot(group['시간대구분'], group['생활인구수'], marker='o', markersize=3, linewidth=2, label=dong, color=color)
        
    ax.set_title(f'연령대: {age}', fontsize=12, fontweight='bold', pad=8)
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # 첫 번째 서브플롯에만 범례 표시
    if i == 0:
        ax.legend(title='행정동', fontsize=9, loc='upper right')

# X, Y축 라벨 설정
for row in range(7):
    axes[row*2].set_ylabel('평균 생활인구수', fontsize=10)
for col in range(2):
    axes[12+col].set_xlabel('시간대 (시)', fontsize=10)

plt.suptitle('연령대별 / 시간대별 행정동 생활인구 추이 비교 (세로축: 연령대별 배치)', fontsize=16, y=1.01, fontweight='bold')
plt.tight_layout()

subplots_path = os.path.join(images_dir, 'visualization_by_age_subplots.png')
plt.savefig(subplots_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {subplots_path}")

print("모든 시각화 그래프가 성공적으로 저장되었습니다.")
