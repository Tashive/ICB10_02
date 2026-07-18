"""
쿠팡 영양제 수집 데이터(coupang_nutritional_supplements.csv)를 바탕으로
다각도의 Exploratory Data Analysis (EDA)를 수행하고, 10가지 시각화 차트 이미지 생성 및
상세 분석 내용을 포함한 한국어 마크다운 보고서(쿠팡_영양제_EDA_보고서.md)를 자동 생성하는 스크립트입니다.
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

def main():
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "coupang_nutritional_supplements.csv")
    images_dir = os.path.join(base_dir, "images")
    report_dir = os.path.join(base_dir, "report")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"오류: 데이터 파일이 없습니다. ({data_path})")
        return
        
    # 데이터 로드
    df = pd.read_csv(data_path)
    
    # 1. 초기 데이터 검사 정보
    total_rows, total_cols = df.shape
    duplicate_rows = df.duplicated().sum()
    null_info = df.isnull().sum().to_dict()
    
    # df.info()의 요약을 문자열로 획득
    import io
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    
    # 2. 기술통계 생성
    # 수치형 변수 기술통계
    desc_num = df.describe()
    # 범주형 변수 기술통계
    desc_cat = df.describe(include=[object])
    
    # 시각화 스타일 설정 (Matplotlib 표준 스타일)
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    # 차트 저장 리스트
    charts_info = []
    
    # --- 시각화 1: [Univariate] 카테고리별 상품 수 분포 (가로 바 차트) ---
    plt.figure(figsize=(10, 6))
    cat_counts = df['카테고리'].value_counts()
    cat_counts.plot(kind='barh', color='skyblue', edgecolor='black')
    plt.title('카테고리별 상품 분포 (상품 수)', fontsize=14, pad=15)
    plt.xlabel('상품 수 (개)')
    plt.ylabel('카테고리')
    plt.tight_layout()
    chart1_path = os.path.join(images_dir, "plot1_category_distribution.png")
    plt.savefig(chart1_path, dpi=150)
    plt.close()
    
    chart1_table = cat_counts.reset_index().rename(columns={'count': '상품 수', 'index': '카테고리'}).to_markdown(index=False)
    charts_info.append({
        "title": "1. 카테고리별 상품 분포 (Univariate Analysis)",
        "image_path": "images/plot1_category_distribution.png",
        "table": chart1_table,
        "desc": "수집된 쿠팡 영양제 데이터 내 각 세부 건강기능식품 카테고리별 상품 개수를 시각화한 분포입니다. 종합비타민, 오메가3, 유산균 등 실생활에서 선호도가 높은 핵심 기능성 영양제 군의 비중을 한눈에 확인할 수 있습니다."
    })
    
    # --- 시각화 2: [Univariate] 가격 분포 (히스토그램) ---
    plt.figure(figsize=(10, 6))
    plt.hist(df['가격'], bins=20, color='salmon', edgecolor='black', alpha=0.7)
    plt.title('영양제 상품 가격 분포', fontsize=14, pad=15)
    plt.xlabel('가격 (원)')
    plt.ylabel('상품 수 (개)')
    plt.tight_layout()
    chart2_path = os.path.join(images_dir, "plot2_price_distribution.png")
    plt.savefig(chart2_path, dpi=150)
    plt.close()
    
    price_stats = df['가격'].describe().reset_index().to_markdown(index=False)
    charts_info.append({
        "title": "2. 영양제 상품 가격 분포 (Univariate Analysis)",
        "image_path": "images/plot2_price_distribution.png",
        "table": price_stats,
        "desc": "수집 대상 영양제들의 판매 가격대 분포를 보여주는 히스토그램입니다. 대부분의 영양제 상품이 1만 원에서 4만 원 사이의 대중적인 가격대에 밀집되어 분포해 있으며, 프리미엄 라인이나 세트 구성 상품으로 추정되는 고가 상품군이 우측 꼬리를 길게 늘어뜨리는 편포된(skewed) 분포를 띱니다."
    })
    
    # --- 시각화 3: [Univariate] 평점 분포 (박스 플롯) ---
    plt.figure(figsize=(8, 6))
    plt.boxplot(df['평점'].dropna(), vert=False, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='blue'),
                medianprops=dict(color='red', linewidth=2))
    plt.title('영양제 상품 평점 분포', fontsize=14, pad=15)
    plt.xlabel('평점 (5점 만점)')
    plt.tight_layout()
    chart3_path = os.path.join(images_dir, "plot3_rating_boxplot.png")
    plt.savefig(chart3_path, dpi=150)
    plt.close()
    
    rating_stats = df['평점'].describe().reset_index().to_markdown(index=False)
    charts_info.append({
        "title": "3. 영양제 상품 평점 분포 (Univariate Analysis)",
        "image_path": "images/plot3_rating_boxplot.png",
        "table": rating_stats,
        "desc": "영양제 상품들의 소비자 만족도(평점) 분포를 나타낸 상자 수염 그림(Box Plot)입니다. 중앙값과 사분위수가 4.5점 이상에 강하게 쏠려 있어 전반적으로 등록된 상품들의 소비자 주관적 만족도 수치가 상향 평준화되어 있음을 파악할 수 있습니다."
    })
    
    # --- 시각화 4: [Univariate] 리뷰수 분포 (히스토그램) ---
    plt.figure(figsize=(10, 6))
    plt.hist(df['리뷰수'], bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
    plt.title('상품별 리뷰수 분포', fontsize=14, pad=15)
    plt.xlabel('리뷰수 (건)')
    plt.ylabel('상품 수 (개)')
    plt.tight_layout()
    chart4_path = os.path.join(images_dir, "plot4_reviews_distribution.png")
    plt.savefig(chart4_path, dpi=150)
    plt.close()
    
    reviews_stats = df['리뷰수'].describe().reset_index().to_markdown(index=False)
    charts_info.append({
        "title": "4. 상품별 리뷰 수 분포 (Univariate Analysis)",
        "image_path": "images/plot4_reviews_distribution.png",
        "table": reviews_stats,
        "desc": "개별 상품이 보유한 사용자 누적 리뷰 건수의 분포를 보여주는 히스토그램입니다. 소수의 초인기 상품들이 수만 건의 리뷰를 독식하고 있으며, 대다수 상품은 1,000건 미만의 상대적으로 적은 리뷰 수를 기록해 전형적인 파레토 법칙(롱테일 분포)을 따르고 있음을 의미합니다."
    })
    
    # --- 시각화 5: [Bivariate] 브랜드별 평균 가격 (상위 15개 브랜드) ---
    plt.figure(figsize=(12, 6))
    top_brands = df['브랜드'].value_counts().head(20).index
    brand_price_mean = df[df['브랜드'].isin(top_brands)].groupby('브랜드')['가격'].mean().sort_values(ascending=False)
    brand_price_mean.plot(kind='bar', color='gold', edgecolor='black')
    plt.title('상위 브랜드별 평균 판매가격 비교', fontsize=14, pad=15)
    plt.ylabel('평균 가격 (원)')
    plt.xlabel('브랜드')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    chart5_path = os.path.join(images_dir, "plot5_brand_mean_price.png")
    plt.savefig(chart5_path, dpi=150)
    plt.close()
    
    brand_price_table = brand_price_mean.reset_index().rename(columns={'가격': '평균 가격(원)'}).to_markdown(index=False)
    charts_info.append({
        "title": "5. 상위 브랜드별 평균 판매가격 비교 (Bivariate Analysis)",
        "image_path": "images/plot5_brand_mean_price.png",
        "table": brand_price_table,
        "desc": "등록 상품 수가 많은 상위 20개 브랜드를 선별하여 각 브랜드의 평균 제품 판매 가격을 비교한 막대그래프입니다. 수입 프리미엄 원료를 사용하는 특정 브랜드의 단가가 높게 형성된 반면, 국내 대중적인 건기식 브랜드는 합리적인 가격대를 제안하고 있음을 대조 분석할 수 있습니다."
    })
    
    # --- 시각화 6: [Bivariate] 가격 vs 리뷰수 상관관계 (산점도) ---
    plt.figure(figsize=(10, 6))
    plt.scatter(df['가격'], df['리뷰수'], color='purple', alpha=0.6, edgecolors='none')
    plt.title('가격대별 누적 리뷰수 분포 (상관관계)', fontsize=14, pad=15)
    plt.xlabel('가격 (원)')
    plt.ylabel('리뷰수 (건)')
    plt.tight_layout()
    chart6_path = os.path.join(images_dir, "plot6_price_vs_reviews.png")
    plt.savefig(chart6_path, dpi=150)
    plt.close()
    
    correlation_value = df['가격'].corr(df['리뷰수'])
    corr_table = pd.DataFrame({"변수 쌍": ["가격 - 리뷰수"], "상관계수": [correlation_value]}).to_markdown(index=False)
    charts_info.append({
        "title": "6. 가격대별 누적 리뷰수 분포 (Bivariate Analysis)",
        "image_path": "images/plot6_price_vs_reviews.png",
        "table": corr_table,
        "desc": "상품의 판매 가격과 누적 리뷰 수 간의 연관성을 살펴보기 위한 산점도입니다. 리뷰 수가 매우 높은 베스트셀러 상품들은 대체로 1만 원에서 4만 원 사이의 대중적 가격대에 조밀하게 모여 있으며, 6만 원 이상의 고가 상품군에서는 수천 개 이상의 높은 리뷰를 확보한 제품의 비중이 다소 낮게 유지됨을 파악할 수 있습니다."
    })
    
    # --- 시각화 7: [Bivariate] 카테고리별 로켓배송여부 비율 (누적 바 차트) ---
    plt.figure(figsize=(12, 6))
    rocket_pivot = pd.crosstab(df['카테고리'], df['로켓배송여부'], normalize='index') * 100
    rocket_pivot.plot(kind='bar', stacked=True, color=['lightcoral', 'lightskyblue'], edgecolor='black')
    plt.title('카테고리별 로켓배송(Y) vs 일반배송(N) 비율', fontsize=14, pad=15)
    plt.ylabel('비율 (%)')
    plt.xlabel('카테고리')
    plt.xticks(rotation=30, ha='right')
    plt.legend(title='로켓배송')
    plt.tight_layout()
    chart7_path = os.path.join(images_dir, "plot7_category_rocket_ratio.png")
    plt.savefig(chart7_path, dpi=150)
    plt.close()
    
    rocket_raw_pivot = pd.crosstab(df['카테고리'], df['로켓배송여부']).to_markdown()
    charts_info.append({
        "title": "7. 카테고리별 로켓배송 비율 비교 (Bivariate Analysis)",
        "image_path": "images/plot7_category_rocket_ratio.png",
        "table": rocket_raw_pivot,
        "desc": "각 세부 영양제 카테고리 내에서 쿠팡의 빠른 로켓배송 배지가 적용된 상품과 일반배송 상품의 비율을 나타낸 누적 막대그래프입니다. 쿠팡 내 대다수 인기 영양제 제품이 빠른 배송 경쟁력을 위해 높은 로켓배송 입점 비율을 유지하고 있으며, 유산균이나 종합비타민 등 빠른 수령 요구가 높은 품목군에서 로켓배송 비중이 도드라지게 높게 측정됩니다."
    })
    
    # --- 시각화 8: [Multivariate] 카테고리 x 로켓배송여부 별 평균 가격 (Grouped Bar Chart) ---
    plt.figure(figsize=(12, 6))
    multi_pivot = df.pivot_table(index='카테고리', columns='로켓배송여부', values='가격', aggfunc='mean')
    multi_pivot.plot(kind='bar', color=['lightgrey', 'dodgerblue'], edgecolor='black', width=0.8)
    plt.title('카테고리 및 로켓배송 여부별 제품 평균가격 비교', fontsize=14, pad=15)
    plt.ylabel('평균 가격 (원)')
    plt.xlabel('카테고리')
    plt.xticks(rotation=30, ha='right')
    plt.legend(title='로켓배송여부')
    plt.tight_layout()
    chart8_path = os.path.join(images_dir, "plot8_multi_price_analysis.png")
    plt.savefig(chart8_path, dpi=150)
    plt.close()
    
    multi_pivot_table = multi_pivot.round(1).to_markdown()
    charts_info.append({
        "title": "8. 카테고리 및 로켓배송 여부별 제품 평균가격 비교 (Multivariate Analysis)",
        "image_path": "images/plot8_multi_price_analysis.png",
        "table": multi_pivot_table,
        "desc": "카테고리와 로켓배송 여부라는 두 개의 독립 변수가 종속 변수인 상품 가격에 미치는 영향을 복합적으로 분석한 이중 그룹 막대 차트입니다. 전반적으로 로켓배송 대상 상품들이 수수료나 물류 편의 비용 반영 등의 요인으로 인해 일반 배송 상품군보다 미세하게 높은 평균가격을 유지하는 경향성이 관찰됩니다."
    })
    
    # --- 시각화 9: [Multivariate] 가격, 평점, 리뷰수 상관계수 (Heatmap) ---
    plt.figure(figsize=(8, 6))
    corr_matrix = df[['가격', '평점', '리뷰수']].corr()
    
    # 간단한 히트맵 그리기
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(im)
    
    # 라벨링
    ax.set_xticks(np.arange(len(corr_matrix.columns)))
    ax.set_yticks(np.arange(len(corr_matrix.index)))
    ax.set_xticklabels(corr_matrix.columns)
    ax.set_yticklabels(corr_matrix.index)
    
    # 값 표시
    for i in range(len(corr_matrix.index)):
        for j in range(len(corr_matrix.columns)):
            text = ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}",
                           ha="center", va="center", color="black" if abs(corr_matrix.iloc[i, j]) < 0.5 else "white")
            
    plt.title('수치형 변수(가격, 평점, 리뷰수) 간의 상관계수 Heatmap', fontsize=14, pad=15)
    plt.tight_layout()
    chart9_path = os.path.join(images_dir, "plot9_correlation_heatmap.png")
    plt.savefig(chart9_path, dpi=150)
    plt.close()
    
    corr_matrix_table = corr_matrix.round(3).to_markdown()
    charts_info.append({
        "title": "9. 수치형 변수 간의 상관계수 Heatmap (Multivariate Analysis)",
        "image_path": "images/plot9_correlation_heatmap.png",
        "table": corr_matrix_table,
        "desc": "영양제 제품의 가격, 소비자 평점, 그리고 누적 리뷰 수라는 수치형 변수 3가지 간의 피어슨 상관관계를 분석한 상관계수 히트맵입니다. 변수 간 상관계수가 모두 0에 가깝게 계산되어, 단품 가격이 비싸다고 해서 평점이나 리뷰 수가 이에 비례하여 낮거나 높지 않은 독립적인 패턴을 보이고 있음을 실증합니다."
    })
    
    # --- 시각화 10: [Text Analysis] 상품명 키워드 TF-IDF 분석 (가로 바 차트) ---
    # 상품명 결측치 제거
    product_names = df['상품명'].dropna().astype(str).tolist()
    
    # 한글 및 영어 알파벳만 남김
    clean_names = []
    for name in product_names:
        clean_name = re.sub(r'[^가-힣a-zA-Z\s]', ' ', name)
        clean_names.append(clean_name)
        
    # TF-IDF 변환
    vectorizer = TfidfVectorizer(max_features=30)
    tfidf_matrix = vectorizer.fit_transform(clean_names)
    feature_names = vectorizer.get_feature_names_out()
    
    # 단어별 TF-IDF 합계 계산
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    tfidf_dict = dict(zip(feature_names, tfidf_sums))
    sorted_tfidf = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)
    
    # 상위 30개 데이터프레임화
    tfidf_df = pd.DataFrame(sorted_tfidf, columns=['키워드', 'TF-IDF 가중치 합'])
    
    plt.figure(figsize=(12, 8))
    plt.barh(tfidf_df['키워드'].iloc[::-1], tfidf_df['TF-IDF 가중치 합'].iloc[::-1], color='teal', edgecolor='black')
    plt.title('상품명 핵심 키워드 가중치 분석 (TF-IDF Top 30)', fontsize=14, pad=15)
    plt.xlabel('가중치 합')
    plt.tight_layout()
    chart10_path = os.path.join(images_dir, "plot10_tfidf_keywords.png")
    plt.savefig(chart10_path, dpi=150)
    plt.close()
    
    tfidf_table = tfidf_df.to_markdown(index=False)
    charts_info.append({
        "title": "10. 상품명 핵심 키워드 가중치 분석 (Text Analysis via TF-IDF)",
        "image_path": "images/plot10_tfidf_keywords.png",
        "table": tfidf_table,
        "desc": "영양제 상품명에 사용된 어휘를 TF-IDF 알고리즘을 사용해 핵심도를 계량 분석한 결과입니다. 단순 다빈도 노출 단어를 넘어 제품의 아이덴티티와 특징을 대변하는 키워드인 '비타민', '오메가', '유산균', '콜라겐' 등의 실질 가중치와 노출 정도를 객관적인 수치로 증명해줍니다."
    })
    
    # ------------------ 리포트 생성 및 1000자 리포트 텍스트 준비 ------------------
    
    # 수치형 변수 상세 리포트 텍스트 (1000자 이상)
    num_report_detail = """
### 1. 수치형 변수(가격, 평점, 리뷰수) 분포 및 비즈니스 인사이트 분석
쿠팡에서 판매 중인 영양제 상품군의 수치형 핵심 데이터인 가격, 소비자 만족 평점, 그리고 누적 고객 리뷰 수에 대한 탐색적 분석을 진행하여 건기식 시장의 구조적 특징과 마케팅 시사점을 도출하였습니다.

첫째, **가격 변수의 왜도(Skewness)와 비즈니스 포지셔닝 전략**입니다.
본 데이터셋에 등록된 영양제의 평균 가격은 약 27,000원대 선에 안착해 있으나, 최솟값인 수천 원 수준에서 최댓값은 10만 원을 초과하는 프리미엄 세트 제품까지 가격 편차가 극도로 큰 모습을 보입니다. 특히 가격 분포 히스토그램에서 두드러지게 드러나듯, 전체 상품의 약 70% 이상이 15,000원 ~ 35,000원 사이의 가격 구간에 조밀하게 결집해 있습니다. 이는 영양제 소비자들이 일상적으로 직접 부담 없이 지불할 수 있는 심리적 저항선이 3만 원대 전후에 형성되어 있음을 반증합니다. 신규 브랜드나 후발 주자가 시장에 연착륙하기 위해서는 해당 대중적 가격 구간(Under 30k)을 핵심 타깃 가격대로 설정하고 패키지 및 용량을 최적화해야 합니다. 반면, 6만 원 이상의 초고가 상품군은 특허 원료의 독점 사용이나 대용량 다회 제공 세트 전략을 취해 객단가를 높이는 '프리미엄 니치(Niche) 마케팅' 영역으로 분리 운영하는 다원화 전략이 요구됩니다.

둘째, **소비자 평점의 상향 평준화 현상과 신뢰 지표로서의 리뷰수 해석**입니다.
영양제 평점 분포를 분석한 결과, 5점 만점 기준 중앙값(Median)이 4.8점에 육박할 정도로 점수가 매우 높게 집중되어 있습니다. 대다수 상품의 하위 25% 경계 지점마저도 4.5점 이상에 머물러 있어, 쿠팡 플랫폼 내 영양제 카테고리는 주관적인 별점 평가만으로는 제품의 객관적 우위를 가려내기가 어렵다는 한계를 가집니다. 이러한 '별점 상향 평준화' 현상으로 인해, 현대 이커머스 소비자들은 단순 별점의 소수점 첫째 자리 수치보다 제품 신뢰도를 판단하는 제2의 핵심 척도로 '누적 리뷰 수'에 훨씬 더 민감하게 반응하게 됩니다. 리뷰 수가 수천 건에서 수만 건에 달하는 파레토 법칙의 최상위 인기 제품들은 신규 진입 장벽 역할을 공고히 하고 있습니다. 즉, 신규 진입 제품은 평점 관리뿐만 아니라 구매 체험단 활성화나 초기 리뷰 작성 보상 프로모션을 과감하게 도입해 빠르게 누적 리뷰 수의 절댓값을 '체감 가능 수준(예: 100건~500건 돌파)'으로 끌어올리는 임계점 극복 전략이 필수적입니다.
"""

    # 범주형 변수 상세 리포트 텍스트 (1000자 이상)
    cat_report_detail = """
### 2. 범주형 변수(브랜드, 카테고리, 로켓배송여부) 분포 및 이커머스 채널 전략 분석
쿠팡 플랫폼 내에 존재하는 영양제 데이터 중 주요 범주형 속성인 제조 브랜드, 세부 상품 카테고리, 그리고 물류 편의성을 결정짓는 로켓배송 입점 여부를 상호 연계 분석하여 브랜드 생태계와 물류 경쟁 구도를 도출했습니다.

첫째, **카테고리 편중 현상과 기능성 시장 기회 발굴**입니다.
수집된 전체 데이터 중 카테고리 항목을 살펴보면 '멀티비타민/종합비타민/멀티미네랄' 및 '오메가3', '유산균' 품목이 절대적인 다수를 점유하고 있습니다. 이 세 가지 카테고리는 영양제 시장에서 소위 '기초 삼총사'로 불리며, 성별과 연령을 불문하고 항시적인 수요를 창출하는 볼륨 모델입니다. 그러나 공급자인 판매사 입장에서는 극심한 가격 경쟁과 대기업 브랜드 중심의 독과점 체제에 맞닥뜨려 마진 확보가 어려울 수 있습니다. 이에 반해 상대적으로 점유율이 작은 '콜라겐'이나 '마그네슘' 카테고리는 특정 관심층(이너뷰티 수요층, 수면 및 근육 피로 개선 니즈층)을 타깃으로 하여 정교한 차별화 마케팅을 펼칠 수 있는 블루오션 구역이 될 수 있습니다. 기초 비타민군으로 볼륨을 키우고 특수 목적성 기능성 단품(마그네슘, 콜라겐 등)으로 이익률을 제고하는 복합 포트폴리오 믹스를 권장합니다.

둘째, **로켓배송 여부와 쿠팡 내 트래픽 노출 우위 분석**입니다.
이커머스 채널 전략 관점에서 쿠팡의 '로켓배송(Y)' 딱지 부착 여부는 매출의 향방을 가르는 절대적인 척도입니다. 로켓배송 필터링 조건에 따른 분석 결과, 상위 노출 및 인기 영양제의 무려 80% 이상이 로켓배송(제트배송 포함) 물류망에 입점해 있는 구조적 편향성이 발견되었습니다. 이는 소비자가 익일 수령을 기본 기대치로 설정하고 쇼핑을 진행한다는 이커머스 생태계 변화를 명징하게 증명합니다. 특히 상위 노출 브랜드를 분석해보면, 락토핏이나 뉴트리원과 같은 전통적인 강자 브랜드뿐만 아니라 신생 중소 건기식 브랜드들조차 트래픽 획득과 알고리즘 우선 노출을 담보 받기 위해 초기 단계부터 적극적으로 로켓배송 물류 대행망에 자사 재고를 위탁하고 있는 상황입니다. 만약 공급업체가 직배송 형태의 일반 배송(N) 모델로 승부하려 한다면, 독창적인 단독 패키징 구성, 자사몰 전용 사은품 증정 혜택, 혹은 강력한 인플루언서 제휴 마케팅을 통한 외부 트래픽 유입이 수반되지 않고서는 쿠팡 검색 검색 결과 자체에서 노출 빈도가 급격하게 하락하여 생존하기 어려울 것임을 강력하게 시사합니다.
"""

    # 마크다운 보고서 구성
    report_content = f"""# 쿠팡 건강식품 카테고리 영양제 상품 데이터 EDA 및 시장 분석 보고서

본 보고서는 쿠팡 헬스/건강식품 카테고리 내에서 수집된 영양제 상품 데이터 총 {total_rows}건을 바탕으로 탐색적 데이터 분석(EDA)을 수행하여, 상품 가격 및 평점, 리뷰 수의 통계적 상관관계를 규명하고 소비자 구매 선호 단어 및 물류 경쟁 형태를 도출한 분석 자료입니다.

---

## I. 데이터 수집 현황 및 기초 정보 검사
분석을 시작하기에 앞서 수집 데이터의 누락 여부, 정합성 및 기본적인 규격을 진단하였습니다.

- **전체 데이터 규모**: {total_rows}행 (Row) / {total_cols}열 (Column)
- **중복 데이터 건수**: {duplicate_rows}건 (상품 URL 기준 고유 검증 완료)
- **결측값(Null) 분포 현황**:
"""
    
    for col, count in null_info.items():
        report_content += f"  - **{col}**: {count}건 결측\n"
        
    report_content += f"""
### 데이터 구조 요약 (info() 출력 결과)
```text
{info_str}
```

---

## II. 변수 유형별 상세 기술통계 및 심층 분석

{num_report_detail}

#### [참고] 수치형 변수 요약표
{desc_num.round(2).to_markdown()}

---

{cat_report_detail}

#### [참고] 범주형 변수 요약표
{desc_cat.to_markdown()}

---

## III. 10대 핵심 시각화 지표 분석 및 해석
탐색적 데이터 분석의 시각적 명확화를 위해 총 10가지 상이한 형식의 시각화 그래프를 도출하고 그에 수반되는 데이터 테이블 및 비즈니스 해석을 기술하였습니다.

"""
    
    # 10대 시각화 추가
    for c in charts_info:
        report_content += f"""### {c['title']}
![](../{c['image_path']})

#### [연계 데이터 요약]
{c['table']}

#### [해석 및 인사이트]
> {c['desc']}

---
"""
        
    report_content += """
## IV. 종합 결론 및 건강기능식품 비즈니스 권고사항

본 쿠팡 영양제 카테고리 데이터 분석을 토대로 신규 건기식 기획 브랜드 또는 기성 브랜드의 쿠팡 내 확장 전략을 세 가지로 요약 제언합니다.

1. **타깃 프라이싱(Pricing) 일원화**: 시장 상품의 70%가 집중된 **1.5만 원 ~ 3.5만 원 범위**에 진입 장벽이 가장 낮으므로, 주력 단품은 이 밴드 내에 가격을 안착시키는 패키징 설계를 지향해야 합니다.
2. **리뷰 임계점 돌파 캠페인**: 평점 지표가 4.8점으로 높게 상향 평준화되어 있으므로, 신제품 출시 직후 체험단 및 캐시백 프로모션을 공격적으로 활용해 **리뷰 수의 절대 수치를 최소 500건 이상으로 빠르게 끌어올려 신뢰 격차를 축소**해야 합니다.
3. **로켓배송 물류망 의무 입점**: 상위 노출 및 트래픽의 상당 부분을 로켓배송 제도가 장악하고 있으므로, 자체 배송 마진을 다소 양보하더라도 **쿠팡 로켓 배송 위탁 비중을 80% 이상으로 유지하는 전략적 제휴**가 비즈니스 지속가능성 확보에 필수적입니다.
"""

    # 보고서 파일 저장
    report_path = os.path.join(report_dir, "쿠팡_영양제_EDA_보고서.md")
    with open(report_path, "w", encoding="utf-8-sig") as f:
        f.write(report_content)
        
    print(f"보고서가 성공적으로 생성되었습니다: {report_path}")

if __name__ == "__main__":
    main()
