"""
이 스크립트는 brand_region_crosstab.csv 데이터를 기반으로 각 버거 프랜차이즈 브랜드(롯데리아, 맥도날드, 버거킹, KFC)
의 전국 총 매장 수를 비교하는 막대그래프(Bar Chart)를 시각화하여 저장하는 도구입니다.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'report', 'brand_region_crosstab.csv')
    output_dir = os.path.join(script_dir, '..', 'images')
    output_image_path = os.path.join(output_dir, 'brand_bar_chart.png')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the crosstab CSV
    df = pd.read_csv(csv_path)
    
    # Extract the '합계' row (total counts)
    totals_row = df[df['시도시군구명'] == '합계']
    if totals_row.empty:
        print("Error: '합계' row not found in CSV.")
        return
        
    brands = ['롯데리아', '맥도날드', '버거킹', 'KFC']
    counts = [int(totals_row[b].values[0]) for b in brands]
    
    # Sort brands and counts descending
    sorted_data = sorted(zip(brands, counts), key=lambda x: x[1], reverse=True)
    sorted_brands, sorted_counts = zip(*sorted_data)
    
    # Configure matplotlib styles
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(9, 6), facecolor='#FAFAFA')
    ax.set_facecolor('#FFFFFF')
    
    # Define custom brand colors or matching theme colors
    # 롯데리아: 빨강/오렌지계열, 맥도날드: 노랑/골드계열, 버거킹: 브라운/오렌지, KFC: 진빨강
    colors = ['#E74C3C', '#F1C40F', '#E67E22', '#C0392B']
    
    bars = ax.bar(sorted_brands, sorted_counts, color=colors, edgecolor='#555555', linewidth=0.8, width=0.6)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 20,
                f"{height:,}개",
                ha='center', va='bottom', fontsize=11, fontweight='bold', color='#333333')
                
    # Style the axes
    ax.set_title('버거 프랜차이즈 브랜드별 전국 총 매장 수 비교', fontsize=15, fontweight='bold', color='#2C3E50', pad=20)
    ax.set_ylabel('매장 수 (개)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylim(0, max(sorted_counts) * 1.15)  # Add space for text labels
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    
    ax.grid(axis='y', linestyle=':', alpha=0.6, color='#CCCCCC')
    ax.tick_params(colors='#666666', labelsize=11)
    
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    plt.close()
    
    print(f"Bar chart visualization saved successfully to {output_image_path}")

if __name__ == '__main__':
    main()
