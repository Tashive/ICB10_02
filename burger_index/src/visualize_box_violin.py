"""
이 스크립트는 brand_region_crosstab.csv 데이터를 기반으로 각 버거 프랜차이즈 브랜드(KFC, 롯데리아, 맥도날드, 버거킹)
의 전국 시도시군구별 매장 수 분포를 박스플롯(Box Plot)과 바이올린 플롯(Violin Plot)으로 시각화하여 저장하는 도구입니다.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'report', 'brand_region_crosstab.csv')
    output_dir = os.path.join(script_dir, '..', 'images')
    output_image_path = os.path.join(output_dir, 'brand_box_violin.png')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the crosstab CSV and exclude the '합계' row
    df = pd.read_csv(csv_path)
    df = df[df['시도시군구명'] != '합계']
    
    brands = ['KFC', '롯데리아', '맥도날드', '버거킹']
    
    # Check if columns exist
    if not all(b in df.columns for b in brands):
        print("Error: Missing brand columns in CSV.")
        return
        
    # Extract data for plotting
    data = [df[b].values for b in brands]
    
    # Configure matplotlib styles
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # Color palette
    colors = ['#C0392B', '#E74C3C', '#F1C40F', '#E67E22'] # KFC (dark red), Lotteria (red), McDonald's (yellow), Burger King (orange)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor='#FAFAFA')
    
    # ----------------------------------------------------
    # Subplot 1: Box Plot
    # ----------------------------------------------------
    bp = ax1.boxplot(data, patch_artist=True, tick_labels=brands,
                     medianprops=dict(color='#333333', linewidth=1.5),
                     flierprops=dict(marker='o', markerfacecolor='#95A5A6', markersize=4, markeredgecolor='none'))
    
    # Color individual boxes
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor('#555555')
        patch.set_alpha(0.75)
        
    ax1.set_title('브랜드별 시도시군구 매장 수 분포 (박스플롯)', fontsize=13, fontweight='bold', color='#2C3E50', pad=15)
    ax1.set_ylabel('지역별 매장 수 (개)', fontsize=11, labelpad=10)
    ax1.grid(axis='y', linestyle=':', alpha=0.6, color='#CCCCCC')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#CCCCCC')
    ax1.spines['bottom'].set_color('#CCCCCC')
    ax1.tick_params(colors='#666666', labelsize=10)
    
    # ----------------------------------------------------
    # Subplot 2: Violin Plot
    # ----------------------------------------------------
    vp = ax2.violinplot(data, showmeans=False, showmedians=True, showextrema=True)
    
    # Color individual violins
    for body, color in zip(vp['bodies'], colors):
        body.set_facecolor(color)
        body.set_edgecolor('#555555')
        body.set_alpha(0.7)
        
    # Style the violin lines
    vp['cmedians'].set_colors('#333333')
    vp['cmedians'].set_linewidth(1.5)
    vp['cmins'].set_colors('#95A5A6')
    vp['cmaxes'].set_colors('#95A5A6')
    vp['cbars'].set_colors('#95A5A6')
    
    # Set x-ticks for violin plot
    ax2.set_xticks(np.arange(1, len(brands) + 1))
    ax2.set_xticklabels(brands)
    
    ax2.set_title('브랜드별 시도시군구 매장 수 분포 (바이올린 플롯)', fontsize=13, fontweight='bold', color='#2C3E50', pad=15)
    ax2.set_ylabel('지역별 매장 수 (개)', fontsize=11, labelpad=10)
    ax2.grid(axis='y', linestyle=':', alpha=0.6, color='#CCCCCC')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#CCCCCC')
    ax2.spines['bottom'].set_color('#CCCCCC')
    ax2.tick_params(colors='#666666', labelsize=10)
    
    # Main Title
    fig.suptitle('버거 프랜차이즈 브랜드별 전국 시도시군구 매장 수 분포 분석 (Box & Violin)', 
                 fontsize=16, fontweight='bold', color='#333333', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(output_image_path, dpi=300)
    plt.close()
    
    print(f"Box and violin plot saved successfully to {output_image_path}")

if __name__ == '__main__':
    main()
