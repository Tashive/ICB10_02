"""
이 스크립트는 brand_region_crosstab.csv 데이터를 기반으로 각 버거 프랜차이즈 브랜드(KFC, 롯데리아, 맥도날드, 버거킹)
간의 매장 수 상관행렬을 계산하고, 이를 마스크 처리 없이 전체 정사각형 히트맵(Heatmap)으로 시각화하여 저장하는 도구입니다.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'report', 'brand_region_crosstab.csv')
    output_dir = os.path.join(script_dir, '..', 'images')
    output_image_path = os.path.join(output_dir, 'brand_heatmap.png')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Read data and exclude '합계' row
    df = pd.read_csv(csv_path)
    df = df[df['시도시군구명'] != '합계']
    
    brands = ['KFC', '롯데리아', '맥도날드', '버거킹']
    
    # Calculate Pearson correlation matrix
    corr = df[brands].corr()
    
    # Plot configuration
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(8, 7), facecolor='#FAFAFA')
    
    # Draw heatmap using imshow (RdYlBu_r diverging colormap)
    im = ax.imshow(corr, cmap='RdYlBu_r', vmin=0, vmax=1)  # Since all correlations are positive, 0 to 1 is suitable
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel('상관계수 (r)', rotation=-90, va="bottom", fontsize=11, fontweight='bold', labelpad=15)
    cbar.ax.tick_params(labelsize=9)
    
    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(brands)))
    ax.set_yticks(np.arange(len(brands)))
    ax.set_xticklabels(brands, fontsize=11, fontweight='bold')
    ax.set_yticklabels(brands, fontsize=11, fontweight='bold')
    
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center", rotation_mode="anchor")
    
    # Loop over data dimensions and create text annotations.
    for i in range(len(brands)):
        for j in range(len(brands)):
            val = corr.iloc[i, j]
            # Use white text for dark colors (extreme values of diverging colormap), black text for light colors
            color = "white" if val > 0.8 or val < 0.2 else "black"
            ax.text(j, i, f"{val:.2f}",
                    ha="center", va="center", color=color,
                    fontsize=14, fontweight='bold')
            
    ax.set_title('버거 프랜차이즈 브랜드간 매장 수 상관관계 히트맵', 
                 fontsize=14, fontweight='bold', color='#333333', pad=20)
    
    # Turn spines off and create white grid to separate cells
    ax.spines[:].set_visible(False)
    
    ax.set_xticks(np.arange(len(brands)+1)-.5, minor=True)
    ax.set_yticks(np.arange(len(brands)+1)-.5, minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    plt.close()
    
    print(f"Heatmap visualization saved successfully to {output_image_path}")

if __name__ == '__main__':
    main()
