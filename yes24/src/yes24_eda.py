"""
YES24 베스트셀러 데이터 탐색적 데이터 분석(EDA) 및 시각화 스크립트

이 스크립트는 수집된 YES24 베스트셀러 데이터를 불러와 
기본 데이터 검증, 기술통계 분석, 상관관계 도출, TF-IDF 텍스트 마이닝을 수행하고,
사용자의 요구사항에 맞춘 10개의 분석 차트(Matplotlib 기반)를 생성하여 이미지 파일(plot1.png ~ plot10.png)로 저장합니다.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

# 색상 테마 정의 (스틸 블루 & 네이비)
COLOR_STEEL_BLUE = '#4682B4'
COLOR_NAVY = '#1A365D'

def load_data():
    csv_path = os.path.join("yes24", "data", "yes24_bestseller.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}")
    return pd.read_csv(csv_path)

def generate_visualizations(df, img_dir):
    os.makedirs(img_dir, exist_ok=True)
    
    # 1. 판매지수 분포 (Histogram) - plot1.png
    plt.figure(figsize=(10, 5))
    sale_index_log = np.log10(df['판매지수'].replace(0, 1))
    plt.hist(sale_index_log.dropna(), bins=30, color=COLOR_NAVY, edgecolor='white', alpha=0.9)
    plt.title('베스트셀러 도서 판매지수 분포 (로그 스케일)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('판매지수 (Log10 scale)', fontsize=12)
    plt.ylabel('도서 수', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot1.png'), dpi=150)
    plt.close()
    
    # 2. 평점 분포 (Histogram) - plot2.png
    plt.figure(figsize=(10, 5))
    plt.hist(df['평점'].dropna(), bins=20, color=COLOR_STEEL_BLUE, edgecolor='white', alpha=0.9)
    plt.title('베스트셀러 도서 평점 분포', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('평점 (10점 만점)', fontsize=12)
    plt.ylabel('도서 수', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot2.png'), dpi=150)
    plt.close()
    
    # 3. 리뷰 개수 분포 (Histogram) - plot3.png
    plt.figure(figsize=(10, 5))
    cutoff = df['리뷰개수'].quantile(0.95)
    filtered_reviews = df[df['리뷰개수'] <= cutoff]['리뷰개수']
    plt.hist(filtered_reviews.dropna(), bins=30, color=COLOR_NAVY, edgecolor='white', alpha=0.9)
    plt.title(f'베스트셀러 도서 리뷰 개수 분포 (하위 95% 데이터, 기준값: {int(cutoff)}건 이하)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('리뷰 개수 (건)', fontsize=12)
    plt.ylabel('도서 수', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot3.png'), dpi=150)
    plt.close()
    
    # 4. 분야명(장르)별 도서 수 및 평균 판매지수 (Grouped Bar Chart) - plot4.png
    fig, ax1 = plt.subplots(figsize=(12, 6))
    genre_stats = df.groupby('분야명').agg({'판매지수': 'mean', '도서명': 'count'}).rename(columns={'도서명': '도서수'})
    genre_stats = genre_stats.sort_values(by='판매지수', ascending=False)
    x = np.arange(len(genre_stats))
    width = 0.35
    ax2 = ax1.twinx()
    rects1 = ax1.bar(x - width/2, genre_stats['판매지수'], width, label='평균 판매지수', color=COLOR_NAVY)
    rects2 = ax2.bar(x + width/2, genre_stats['도서수'], width, label='도서 수', color=COLOR_STEEL_BLUE)
    ax1.set_xlabel('분야명 (장르)', fontsize=12)
    ax1.set_ylabel('평균 판매지수', color=COLOR_NAVY, fontsize=12)
    ax2.set_ylabel('도서 수', color=COLOR_STEEL_BLUE, fontsize=12)
    plt.title('분야별 도서 수 및 평균 판매지수 비교', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(genre_stats.index, rotation=45, ha='right')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot4.png'), dpi=150)
    plt.close()
    
    # 5. 정가 대비 판매가 할인율 분포 (Box Plot) - plot5.png
    plt.figure(figsize=(8, 5))
    plt.boxplot(df['할인율(%)'].dropna(), vert=False, patch_artist=True,
                boxprops=dict(facecolor=COLOR_STEEL_BLUE, color=COLOR_NAVY),
                medianprops=dict(color='red', linewidth=1.5))
    plt.title('베스트셀러 도서 할인율 분포', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('할인율 (%)', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot5.png'), dpi=150)
    plt.close()
    
    # 6. 판매지수 vs 리뷰 개수 관계 (Scatter Plot) - plot6.png
    plt.figure(figsize=(8, 6))
    plt.scatter(df['리뷰개수'], df['판매지수'], color=COLOR_STEEL_BLUE, alpha=0.6, edgecolors=COLOR_NAVY, linewidth=0.5)
    plt.title('판매지수 vs 리뷰 개수 관계', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('리뷰 개수 (건)', fontsize=12)
    plt.ylabel('판매지수', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot6.png'), dpi=150)
    plt.close()
    
    # 7. 평점 vs 판매지수 관계 (Scatter Plot) - plot7.png
    plt.figure(figsize=(8, 6))
    plt.scatter(df['평점'], df['판매지수'], color=COLOR_STEEL_BLUE, alpha=0.6, edgecolors=COLOR_NAVY, linewidth=0.5)
    plt.title('평점 vs 판매지수 관계', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('평점 (10점 만점)', fontsize=12)
    plt.ylabel('판매지수', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot7.png'), dpi=150)
    plt.close()
    
    # 8. 주요 상위 출판사 Top 15의 평균 판매지수 (Bar Chart) - plot8.png
    plt.figure(figsize=(12, 6))
    pub_counts = df['출판사'].value_counts()
    top_publishers = pub_counts.head(15).index
    pub_df = df[df['출판사'].isin(top_publishers)]
    pub_stats = pub_df.groupby('출판사').agg({'판매지수': 'mean', '도서명': 'count'}).rename(columns={'도서명': '도서수'})
    pub_stats = pub_stats.loc[top_publishers].sort_values(by='판매지수', ascending=False)
    plt.bar(pub_stats.index, pub_stats['판매지수'], color=COLOR_STEEL_BLUE, edgecolor=COLOR_NAVY)
    plt.title('도서 점유율 상위 15대 출판사의 평균 판매지수', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('출판사명', fontsize=12)
    plt.ylabel('평균 판매지수', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot8.png'), dpi=150)
    plt.close()
    
    # 9. 수치형 변수 간 상관관계 열지도 (Correlation Heatmap) - plot9.png
    fig, ax = plt.subplots(figsize=(8, 6))
    numeric_cols = ['순위', '정가', '판매가', '할인율(%)', '포인트', '판매지수', '리뷰개수', '평점']
    corr = df[numeric_cols].corr()
    im = ax.imshow(corr, cmap='RdBu', vmin=-1, vmax=1)
    fig.colorbar(im, ax=ax)
    ax.set_xticks(np.arange(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(numeric_cols)))
    ax.set_yticklabels(numeric_cols)
    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", 
                     color="black" if abs(corr.iloc[i, j]) < 0.6 else "white")
    ax.set_title('수치형 변수 간 상관관계 열지도', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot9.png'), dpi=150)
    plt.close()
    
    # 10. 도서명 TF-IDF 상위 30개 핵심 키워드 빈도 (Horizontal Bar Chart) - plot10.png
    titles_cleaned = df['도서명'].dropna().apply(lambda x: re.sub(r'[^가-힣a-zA-Z\s]', '', x))
    vectorizer = TfidfVectorizer(max_features=100, stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(titles_cleaned)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    tfidf_df = pd.DataFrame({'word': feature_names, 'score': tfidf_sums})
    top_30_keywords = tfidf_df.sort_values(by='score', ascending=False).head(30)
    
    plt.figure(figsize=(10, 8))
    plt.barh(top_30_keywords['word'][::-1], top_30_keywords['score'][::-1], color=COLOR_STEEL_BLUE)
    plt.title('베스트셀러 도서명 TF-IDF 상위 30개 키워드', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('TF-IDF Score Sum', fontsize=12)
    plt.ylabel('키워드', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot10.png'), dpi=150)
    plt.close()
    
    print("[Success] All 10 plots generated.")
    return top_30_keywords

def print_summary_stats(df, top_keywords):
    print("\n" + "="*40)
    print("=== DATA SUMMARY FOR EDA REPORT ===")
    print("="*40)
    print(f"Total Rows: {df.shape[0]}")
    print(f"Total Columns: {df.shape[1]}")
    print(f"Duplicate Rows: {df.duplicated().sum()}")
    print("\n--- Numerical Description ---")
    print(df.describe().to_string())
    print("\n--- Categorical Description ---")
    for col in ['출판사', '분야명']:
        print(f"\n[{col}] Value Counts (Top 10):")
        print(df[col].value_counts().head(10).to_string())
    print("\n--- TF-IDF Keywords Top 30 Table ---")
    print(top_keywords.to_string(index=False))

def main():
    df = load_data()
    img_dir = os.path.join("yes24", "images")
    top_keywords = generate_visualizations(df, img_dir)
    print_summary_stats(df, top_keywords)

if __name__ == "__main__":
    main()
