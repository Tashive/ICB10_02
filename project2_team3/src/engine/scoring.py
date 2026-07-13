"""
건강기능식품 추천을 위한 정밀 스코어링 엔진 스크립트 (Parquet 상대경로 버전)

이 스크립트는 `NutriFit_Mapped_Master_v2.parquet` 데이터를 상대경로로 로드하고 필터링하며,
사용자 문진 데이터(건강 고민, 라이프스타일)를 토대로 성분별 웰니스 가산점(bonus)을 계산합니다.
또한, 부작용 과거력 성분을 기반으로 추천 목록에서 해당 성분 제품을 하드 필터링(Hard Filter) 배제하며,
평점, 리뷰 수, 웰니스 보너스를 결합한 종합 웰니스 스코어를 기반으로 상위 제품을 추천합니다.
"""

import os
import re
import numpy as np
import pandas as pd

# 상대 경로 설정을 위해 파일 위치 기준의 상위 project2_team3 폴더 획득
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "0_data", "NutriFit_Mapped_Master_v2.parquet")

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"마스터 데이터 파일이 없습니다: {DATA_PATH}")
    return pd.read_parquet(DATA_PATH)

def calculate_wellness_bonus(survey_data):
    """
    유저의 라이프스타일 및 건강고민 입력을 바탕으로 6대 성분별 가산점 딕셔너리를 반환합니다.
    """
    bonuses = {
        "멀티비타민": 0.0,
        "비타민C": 0.0,
        "오메가3": 0.0,
        "유산균 / 프로바이오틱스": 0.0,
        "콜라겐": 0.0,
        "마그네슘": 0.0
    }
    
    # 1. 건강 고민 및 목표 (최대 2개)
    goals = survey_data.get("health_goals", [])
    for goal in goals:
        if goal == "만성피로":
            bonuses["멀티비타민"] += 5.0
            bonuses["비타민C"] += 3.0
        elif goal == "눈 건조·피로":
            bonuses["오메가3"] += 5.0
            bonuses["멀티비타민"] += 2.0
        elif goal == "장 건강":
            bonuses["유산균 / 프로바이오틱스"] += 5.0
        elif goal == "피부탄력·이너뷰티":
            bonuses["콜라겐"] += 5.0
            bonuses["비타민C"] += 2.0
        elif goal == "체지방감소·다이어트":
            bonuses["멀티비타민"] += 2.0
        elif goal == "면역력저하":
            bonuses["멀티비타민"] += 4.0
            bonuses["유산균 / 프로바이오틱스"] += 3.0
        elif goal == "관절보호":
            bonuses["콜라겐"] += 4.0
            bonuses["마그네슘"] += 2.0
        elif goal == "수면부족·스트레스케어":
            bonuses["마그네슘"] += 5.0
            bonuses["멀티비타민"] += 2.0
        elif goal == "항노화·항산화":
            bonuses["비타민C"] += 5.0
            bonuses["멀티비타민"] += 2.0
        elif goal == "생리불순·생리통":
            bonuses["마그네슘"] += 3.0
            bonuses["오메가3"] += 3.0
            
    # 2. 라이프스타일 가산점
    # 운동
    exercise = survey_data.get("exercise", [])
    if any(ex in exercise for ex in ["저항성·근력 운동", "고강도 인터벌", "고강도 유산소"]):
        bonuses["마그네슘"] += 5.0
        bonuses["멀티비타민"] += 2.0
        
    # 음주
    drinking = survey_data.get("drinking", "전혀 안 함")
    if drinking == "잦은 음주":
        bonuses["멀티비타민"] += 4.0
        bonuses["마그네슘"] += 2.0
        
    # 흡연
    smoking = survey_data.get("smoking", "비흡연")
    if smoking == "흡연":
        bonuses["비타민C"] += 5.0
        
    # 수면
    sleep = survey_data.get("sleep", "5~7시간")
    if sleep == "5시간 미만":
        bonuses["마그네슘"] += 4.0
        bonuses["멀티비타민"] += 3.0
        
    # 카페인
    caffeine = survey_data.get("caffeine", "0잔")
    if caffeine in ["3잔", "4잔 이상"]:
        bonuses["마그네슘"] += 3.0
        
    return bonuses

def get_recommendations(survey_data, selected_category=None, top_n=10):
    """
    유저 문진 데이터를 입력받아 가산점 및 부작용 필터(Hard Filter)를 연동해 추천 상품 목록을 반환합니다.
    카테고리가 주어지면 해당 카테고리에 우선순위를 부여하거나 필터링합니다.
    """
    df = load_data()
    
    # 1. 수치 데이터 강제 형변환 및 결측치 예외 처리
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
    df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce').fillna(0).astype(int)
    
    # 2. 부작용 성분 기반 하드 필터(Hard Filter) 배제 로직
    side_effects = list(survey_data.get("side_effects", []))
    direct_input = survey_data.get("side_effect_direct", "").strip()
    if direct_input:
        side_effects.append(direct_input)
        
    # 부작용 성분명 정제 키워드 세트 구축
    banned_keywords = []
    for se in side_effects:
        se_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', se).lower()
        if se_clean and se_clean not in ["없음", "기타직접입력"]:
            banned_keywords.append(se_clean)
            if "오메가" in se_clean:
                banned_keywords.append("epa")
                banned_keywords.append("dha")
            if "유산균" in se_clean or "프로바이오틱스" in se_clean:
                banned_keywords.extend(["유산균", "프로바이오틱스", "락토", "probiotic"])
                
    def is_banned(std_ing):
        if not isinstance(std_ing, str) or not banned_keywords:
            return False
        std_ing_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', std_ing).lower()
        for kw in banned_keywords:
            if kw in std_ing_clean:
                return True
        return False
        
    # 부작용 성분이 함유된 제품 원천 배제
    df_filtered = df[~df['표준성분'].apply(is_banned)].copy()
    
    if df_filtered.empty:
        return df_filtered
        
    # 3. 웰니스 가산점 산출
    bonuses = calculate_wellness_bonus(survey_data)
    
    def get_bonus_score(cat_str):
        if not isinstance(cat_str, str):
            return 0.0
        cats = [c.strip() for c in cat_str.split(',')]
        max_bonus = 0.0
        for c in cats:
            if c in bonuses:
                max_bonus = max(max_bonus, bonuses[c])
        return max_bonus
        
    df_filtered['wellness_bonus'] = df_filtered['최종카테고리'].apply(get_bonus_score)
    
    # 4. 종합 웰니스 스코어 산출
    df_filtered['score'] = (
        (df_filtered['rating'] * 0.7) +
        (np.log10(df_filtered['review_count'] + 1) * 0.3) +
        df_filtered['wellness_bonus']
    )
    df_filtered['score'] = df_filtered['score'].round(2)
    
    # 5. 선택 카테고리 필터링 (필요 시)
    if selected_category:
        def contains_category(cat_str):
            if not isinstance(cat_str, str):
                return False
            cats = [c.strip() for c in cat_str.split(',')]
            return selected_category in cats
        df_filtered = df_filtered[df_filtered['최종카테고리'].apply(contains_category)].copy()
        
    # 스코어 높은 순 정렬 및 상위 N개 추천
    recommended_df = df_filtered.sort_values(by='score', ascending=False)
    
    return recommended_df.head(top_n)
