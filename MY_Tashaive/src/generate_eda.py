"""
TruePick 프로젝트 기획서에 명시된 가설과 검증 모델을 기반으로 가상 구매 및 리뷰 데이터를 시뮬레이션 생성하고,
20년 차 시니어 분석가 수준의 탐색적 데이터 분석(EDA)을 실행하여 시각화 차트 및 통계 분석 결과를 도출하는 스크립트입니다.
본 스크립트는 가구 유형별 소비 패턴 분석, 이커머스 플랫폼별 혜택 비교, 광고성 리뷰 필터링 스코어,
다중회귀분석 및 카이제곱 검정과 TF-IDF 리뷰 키워드 추출을 다룹니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# 맑은 고딕 한글 폰트 설정 적용 (Python 3.12 distutils 결손 에러 우회)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
from sklearn.feature_extraction.text import TfidfVectorizer
import statsmodels.api as sm
from scipy import stats

# 1. 가상 데이터 생성 설정
np.random.seed(42)
n_samples = 1000

# 가구 형태 (1인 가구 Single 60%, 다가구 Multi 40%)
household_types = np.random.choice(["Single", "Multi"], size=n_samples, p=[0.6, 0.4])

# 선호 요인 (가구 형태에 따른 확률 가중치 부여)
preferred_factors = []
for h_type in household_types:
    if h_type == "Single":
        factor = np.random.choice(["Price", "Performance", "Design", "Delivery"], p=[0.5, 0.2, 0.1, 0.2])
    else:
        factor = np.random.choice(["Price", "Performance", "Design", "Delivery"], p=[0.2, 0.5, 0.2, 0.1])
    preferred_factors.append(factor)
preferred_factors = np.array(preferred_factors)

# 주로 구매하는 플랫폼
platforms = np.random.choice(["쿠팡", "네이버 플러스 스토어", "오늘의집", "G마켓"], size=n_samples, p=[0.4, 0.3, 0.2, 0.1])

# 광고성 리뷰 여부 (Yes 30%, No 70%)
advertised_reviews = np.random.choice(["Yes", "No"], size=n_samples, p=[0.3, 0.7])

# 실구매자 리뷰 평점 (광고성 리뷰는 평점이 극단적으로 높고 편차가 작음, 일반 리뷰는 정규분포를 따름)
real_review_scores = []
for adv in advertised_reviews:
    if adv == "Yes":
        score = np.clip(np.random.normal(4.8, 0.2), 1.0, 5.0)
    else:
        score = np.clip(np.random.normal(3.8, 0.8), 1.0, 5.0)
    real_review_scores.append(round(score, 1))
real_review_scores = np.array(real_review_scores)

# 플랫폼 가격 경쟁력 점수 (1~10점)
price_competitiveness = np.random.randint(1, 11, size=n_samples)

# 실제 구매 전환 여부 (Purchase Intent)
# 로지스틱 가중치를 이용한 확률적 구매 전환 구현
# 회귀식 기반: 구매 의사는 실구매자 리뷰 평점과 가격 경쟁력에 비례하며 광고성 리뷰에는 반비례
purchase_intents = []
for idx in range(n_samples):
    adv_factor = -1.5 if advertised_reviews[idx] == "Yes" else 0.5
    score_factor = 1.2 * real_review_scores[idx]
    price_factor = 0.4 * price_competitiveness[idx]
    # 로지스틱 확률
    logits = -6.0 + score_factor + price_factor + adv_factor + np.random.normal(0, 0.5)
    prob = 1 / (1 + np.exp(-logits))
    intent = np.random.choice([1, 0], p=[prob, 1 - prob])
    purchase_intents.append(intent)
purchase_intents = np.array(purchase_intents)

# 가상 리뷰 텍스트 데이터베이스
adv_texts = [
    "업체로부터 제품을 제공받아 솔직하게 작성했습니다. 가성비 최고 최고 최고!",
    "협찬으로 쓰게 되었는데 디자인이 너무 예쁘고 주방 인테리어에 딱입니다 추천 추천합니다.",
    "체험단 이벤트로 받은 상품인데 기능이 정말 다양하고 성능이 아주 뛰어납니다. 만족 만족!",
    "소중한 체험단 기회로 구매했습니다. 공간 효율도 좋고 디자인도 마음에 듭니다.",
    "제공받아 사용해보았는데 소음도 없고 너무 훌륭합니다. 주변 지인들에게 강력 추천해요."
]

real_texts = [
    "내돈내산 솔직한 후기입니다. 배송은 빨랐는데 생각보다 소음이 좀 크네요. 가격 대비 쓸만합니다.",
    "직접 구매해서 일주일간 써봤어요. 디자인은 무난하고 성능은 아주 만족스럽습니다. 추천합니다.",
    "쿠팡에서 저렴하게 샀는데 공간 차지를 덜해서 1인 가구에 딱이네요. 배송 포장도 튼튼합니다.",
    "실제로 써보니 가격 대비 성능인 가성비는 괜찮은데 마감이 약간 아쉽네요. 그래도 만족합니다.",
    "가족들과 함께 쓰려고 샀는데 용량이 넉넉해서 좋아요. 디자인도 깔끔하고 세척도 편리합니다.",
    "배송이 하루 만에 와서 좋았어요. 기능은 단순하지만 기본 성능에 충실해서 매일 잘 쓰고 있습니다.",
    "이 가격에 이 정도 퀄리티면 훌륭합니다. 다만 코드가 약간 짧은 편이네요.",
    "직접 사용해본 결과 소음이 있긴 하지만 흡입력이 좋아서 대만족 중입니다.",
    "부모님 선물로 드렸는데 조작이 쉬워서 좋아하시네요. 강력 추천합니다.",
    "생각했던 것보다 크기가 작아서 좁은 집에 쓰기 유용하네요. 가볍게 쓰기 좋습니다."
]

review_texts = []
for adv in advertised_reviews:
    if adv == "Yes":
        review_texts.append(np.random.choice(adv_texts))
    else:
        review_texts.append(np.random.choice(real_texts))

# 2. 데이터프레임 생성 및 저장
df = pd.DataFrame({
    "user_id": [f"U{i:04d}" for i in range(1, n_samples + 1)],
    "household_type": household_types,
    "preferred_factor": preferred_factors,
    "ecommerce_platform": platforms,
    "real_review_score": real_review_scores,
    "advertised_review": advertised_reviews,
    "price_competitiveness": price_competitiveness,
    "purchase_intent": purchase_intents,
    "review_text": review_texts
})

# 폴더 자동 생성
os.makedirs("MY_Tashaive/data", exist_ok=True)
os.makedirs("MY_Tashaive/images", exist_ok=True)
os.makedirs("MY_Tashaive/report", exist_ok=True)

df.to_csv("MY_Tashaive/data/synthetic_purchase_data.csv", index=False, encoding="utf-8-sig")
print("데이터셋 생성 완료: MY_Tashaive/data/synthetic_purchase_data.csv")

# 3. 데이터 시각화 실행 (최소 10가지 차트 생성)
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

# 1. 가구 형태별 유저 분포 (원형 차트)
plt.figure()
df["household_type"].value_counts().plot.pie(autopct="%.1f%%", colors=["#3b82f6", "#10b981"], startangle=90, explode=[0.05, 0])
plt.title("가구 형태별 유저 분포 비율")
plt.ylabel("")
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot1_household_dist.png", dpi=150)
plt.close()

# 2. 가구 형태별 가전 선호 요인 비교 (누적 막대 그래프)
plt.figure()
ct = pd.crosstab(df["household_type"], df["preferred_factor"])
ct.plot(kind="bar", stacked=True, color=["#ef4444", "#3b82f6", "#10b981", "#8b5cf6"])
plt.title("가구 형태별 가전 선호 핵심 요인 비교")
plt.xlabel("가구 형태")
plt.ylabel("유저 수 (명)")
plt.xticks(rotation=0)
plt.legend(title="선호 요인")
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot2_household_preferred.png", dpi=150)
plt.close()

# 3. 선호 요인별 평균 실구매자 평점 (막대 그래프)
plt.figure()
df.groupby("preferred_factor")["real_review_score"].mean().sort_values().plot(kind="barh", color="#10b981")
plt.title("선호 요인별 평균 실구매자 리뷰 평점")
plt.xlabel("평균 평점 (5.0 만점)")
plt.ylabel("선호 요인")
plt.xlim(0, 5)
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot3_factor_score.png", dpi=150)
plt.close()

# 4. 광고성 리뷰 vs 실구매자 리뷰 분포 (막대 그래프)
plt.figure()
df["advertised_review"].value_counts().plot(kind="bar", color=["#3b82f6", "#ef4444"])
plt.title("광고성(체험단) 리뷰 vs 실구매자 일반 리뷰 분포")
plt.xlabel("광고/협찬 여부")
plt.ylabel("리뷰 수 (건)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot4_review_dist.png", dpi=150)
plt.close()

# 5. 플랫폼별 평균 가격 경쟁력 점수 (막대 그래프)
plt.figure()
df.groupby("ecommerce_platform")["price_competitiveness"].mean().sort_values().plot(kind="bar", color="#8b5cf6")
plt.title("이커머스 플랫폼별 평균 가격 경쟁력 스코어")
plt.xlabel("플랫폼")
plt.ylabel("평균 가격 경쟁력 점수 (10점 만점)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot5_platform_price.png", dpi=150)
plt.close()

# 6. 플랫폼별 구매 전환율 (꺾은선 그래프)
plt.figure()
df.groupby("ecommerce_platform")["purchase_intent"].mean().sort_values(ascending=False).plot(kind="line", marker="o", color="#ef4444", linewidth=2.5, markersize=8)
plt.title("플랫폼별 평균 구매 전환율(CVR)")
plt.xlabel("플랫폼")
plt.ylabel("구매 전환율")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot6_platform_cvr.png", dpi=150)
plt.close()

# 7. 가격 경쟁력과 구매 의사 간의 관계 (박스 플롯)
plt.figure()
df.boxplot(column="price_competitiveness", by="purchase_intent", grid=False, patch_artist=True, boxprops=dict(facecolor="#3b82f6", color="#1e3a8a"))
plt.title("구매 여부에 따른 가격 경쟁력 분포")
plt.suptitle("")
plt.xlabel("실제 구매 전환 여부 (0: 미구매, 1: 구매)")
plt.ylabel("가격 경쟁력 점수")
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot7_price_box.png", dpi=150)
plt.close()

# 8. 실구매자 평점 분포 (히스토그램)
plt.figure()
df["real_review_score"].plot(kind="hist", bins=15, color="#10b981", edgecolor="black", alpha=0.7)
plt.title("제품별 실구매자 리뷰 평점 분포 현황")
plt.xlabel("리뷰 평점")
plt.ylabel("빈도 수")
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot8_score_hist.png", dpi=150)
plt.close()

# 9. 가구 형태별 이커머스 플랫폼 점유율 (그룹 막대 그래프)
plt.figure()
pd.crosstab(df["ecommerce_platform"], df["household_type"]).plot(kind="bar", color=["#10b981", "#3b82f6"])
plt.title("가구 형태별 이커머스 플랫폼별 이용 현황")
plt.xlabel("이커머스 플랫폼")
plt.ylabel("이용 유저 수 (명)")
plt.xticks(rotation=0)
plt.legend(title="가구 형태")
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot9_platform_share.png", dpi=150)
plt.close()

# 10. 광고성 리뷰 여부별 평점 비교 (바이올린 플롯 대체 박스 플롯)
plt.figure()
df.boxplot(column="real_review_score", by="advertised_review", grid=False, patch_artist=True, boxprops=dict(facecolor="#ef4444", color="#991b1b"))
plt.title("광고성(체험단) 여부에 따른 리뷰 평점 분포 비교")
plt.suptitle("")
plt.xlabel("광고/협찬 여부")
plt.ylabel("리뷰 평점 (5.0 만점)")
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot10_adv_score_box.png", dpi=150)
plt.close()

# 11. TF-IDF 기반 상위 30개 리뷰 키워드 가중치 차트 (수평 막대 차트)
plt.figure()
vectorizer = TfidfVectorizer(max_features=30)
tfidf_matrix = vectorizer.fit_transform(df["review_text"])
feature_names = vectorizer.get_feature_names_out()
weights = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
tfidf_df = pd.DataFrame({"keyword": feature_names, "weight": weights}).sort_values("weight", ascending=True)

tfidf_df.plot(kind="barh", x="keyword", y="weight", color="#3b82f6", legend=False)
plt.title("전체 리뷰 텍스트 내 상위 30개 핵심 키워드 가중치 (TF-IDF)")
plt.xlabel("TF-IDF 평균 가중치")
plt.ylabel("핵심 키워드")
plt.tight_layout()
plt.savefig("MY_Tashaive/images/plot11_tfidf_keywords.png", dpi=150)
plt.close()

print("11가지 시각화 차트 생성 완료: MY_Tashaive/images/ 폴더 내 저장")

# 4. 통계적 검정 및 분석 결과 산출
print("\n--- 통계적 상관관계 검증 ---")

# Step 1. 가구 형태와 선호 요인 간 교차분석 (카이제곱 검정)
chi_result = stats.chi2_contingency(ct)
print(f"1. 가구별 선호 요인 교차분석 카이제곱 검정 p-value: {chi_result.pvalue:.4f}")

# Step 3. 다중회귀분석 실행 (구매 의사에 미치는 영향력)
# Purchase_Intent = b0 + b1(Real_Review_Score) + b2(Price_Competitiveness) + e
X = df[["real_review_score", "price_competitiveness"]]
X = sm.add_constant(X)
y = df["purchase_intent"]
model = sm.OLS(y, X).fit()

print("\n2. 다중회귀분석 결과 요약:")
print(model.summary())

# 결과를 텍스트 파일로 저장하여 레포트 작성 시 참고
with open("MY_Tashaive/report/stats_results.txt", "w", encoding="utf-8") as f:
    f.write("=== 카이제곱 검정 (가구 형태 vs 선호 요인) ===\n")
    f.write(f"p-value: {chi_result.pvalue}\n\n")
    f.write("=== 다중회귀분석 결과 ===\n")
    f.write(model.summary().as_text())
print("통계 분석 원천 데이터 저장 완료: MY_Tashaive/report/stats_results.txt")
