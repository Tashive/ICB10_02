"""
이 스크립트는 brand_region_crosstab.csv 데이터를 기반으로 각 버거 프랜차이즈 브랜드(KFC, 롯데리아, 맥도날드, 버거킹)
간의 매장 수 상관관계를 보여주는 페어플롯(Pair Plot)을 시각화하여 이미지로 저장하는 도구입니다.
사용자 요청에 따라 하삼각 행렬은 마스크 처리하고, 상삼각 영역에 산점도와 회귀선 및 우측 상단 상관계수를 표시합니다.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'report', 'brand_region_crosstab.csv')
    output_dir = os.path.join(script_dir, '..', 'images')
    output_image_path = os.path.join(output_dir, 'brand_pairplot.png')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    # Create images directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the crosstab CSV
    df = pd.read_csv(csv_path)
    
    # Exclude the '합계' row if it exists
    df = df[df['시도시군구명'] != '합계']
    
    brands = ['KFC', '롯데리아', '맥도날드', '버거킹']
    
    # Check if all brands are in the columns
    if not all(b in df.columns for b in brands):
        print("Error: Missing brand columns in CSV.")
        return
        
    # Configure matplotlib styles for high quality
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # Color palette
    hist_color = '#4A90E2' # Soft Steel Blue
    scatter_color = '#E2844A' # Soft Coral
    grid_color = '#E5E5E5'
    
    fig, axes = plt.subplots(4, 4, figsize=(14, 14), facecolor='#FAFAFA')
    
    # Subtitle / Title
    fig.suptitle('버거 프랜차이즈 브랜드별 전국 시도시군구 매장 수 상관관계 분석 (상삼각 페어플롯)', 
                 fontsize=16, fontweight='bold', color='#333333', y=0.98)
    
    for i, row_brand in enumerate(brands):
        for j, col_brand in enumerate(brands):
            ax = axes[i, j]
            
            # Mask lower triangle (i > j)
            if i > j:
                ax.set_visible(False)
                continue
                
            ax.set_facecolor('#FFFFFF')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#CCCCCC')
            ax.spines['bottom'].set_color('#CCCCCC')
            ax.grid(True, linestyle=':', alpha=0.6, color=grid_color)
            
            x_data = df[col_brand]
            y_data = df[row_brand]
            
            if i == j:
                # Diagonal: Histogram
                ax.hist(x_data, bins=15, color=hist_color, edgecolor='#2A60A2', alpha=0.85)
                # Add text to show basic stats
                mean_val = x_data.mean()
                max_val = x_data.max()
                ax.text(0.95, 0.95, f"평균: {mean_val:.1f}\n최대: {max_val}",
                        transform=ax.transAxes, verticalalignment='top', horizontalalignment='right',
                        fontsize=9, color='#333333', bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0F0F0', alpha=0.8, edgecolor='none'))
                
                # Show labels for the diagonals (since they act as edges in the masked layout)
                ax.set_xlabel(col_brand, fontsize=12, fontweight='bold', labelpad=10)
                ax.set_ylabel(row_brand, fontsize=12, fontweight='bold', labelpad=10)
            else:
                # Upper triangle: Scatter Plot with trend line
                ax.scatter(x_data, y_data, color=scatter_color, alpha=0.7, edgecolors='#A35425', linewidths=0.5, s=20)
                
                # Fit linear trend line
                if len(x_data) > 1:
                    m, c = np.polyfit(x_data, y_data, 1)
                    line_x = np.array([x_data.min(), x_data.max()])
                    ax.plot(line_x, m * line_x + c, color='#D0021B', linestyle='--', linewidth=1.5, alpha=0.8)
                    
                    # Calculate Pearson correlation coefficient
                    corr = x_data.corr(y_data)
                    # Display correlation coefficient at the top right
                    ax.text(0.95, 0.95, f"r = {corr:.2f}",
                            transform=ax.transAxes, verticalalignment='top', horizontalalignment='right',
                            fontsize=10, fontweight='bold', color='#D0021B',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFEBEB', alpha=0.8, edgecolor='none'))
            
            # Setup ticks & labels formatting
            ax.tick_params(colors='#666666', labelsize=9)
            if i != j:
                # Hide tick labels for off-diagonal plots since they share axes in a grid
                ax.set_xticklabels([])
                ax.set_yticklabels([])
            
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_image_path, dpi=300)
    plt.close()
    
    print(f"Pair plot visualization saved successfully to {output_image_path}")

if __name__ == '__main__':
    main()
