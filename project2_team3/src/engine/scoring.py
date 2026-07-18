"""
건강기능식품 추천을 위한 정밀 스코어링 엔진 스크립트 (알레르기 동의어 확장 사전 적용 버전)

이 스크립트는 `NutriFit_Mapped_Master_v2.parquet` 데이터를 로드하고 필터링하며,
사용자 문진 데이터를 기반으로 6대 핵심 건강 성분별 웰니스 가산점(bonus)을 연산합니다.
특히 알레르기 배제 시 동의어 확장 사전(예: 갑각류 입력 시 새우/게/랍스터 동시 배제)을 연동하여
브랜드명, 상품명, 표준성분 텍스트 대조 시 영구 제외(Hard Filter)하는 지능형 안전성 로직을 제공합니다.
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
    건강고민이 여러 개일 경우(최대 3개), 고민 가산점은 고민 개수에 반비례하여 균등 분배(1/N 스케일링)됩니다.
    """
    bonuses = {
        "멀티비타민": 0.0,
        "비타민C": 0.0,
        "오메가3": 0.0,
        "유산균 / 프로바이오틱스": 0.0,
        "콜라겐": 0.0,
        "마그네슘": 0.0
    }
    
    # 1. 건강 고민 및 목표 (최대 3개)에 따른 가산점 스케일링 분배
    goals = survey_data.get("health_goals", [])
    goal_count = len(goals)
    
    if goal_count > 0:
        scale = 1.0 / goal_count
        
        for goal in goals:
            if goal == "만성피로":
                bonuses["멀티비타민"] += 5.0 * scale
                bonuses["비타민C"] += 3.0 * scale
            elif goal == "눈 건조·피로":
                bonuses["오메가3"] += 5.0 * scale
                bonuses["멀티비타민"] += 2.0 * scale
            elif goal == "장 건강":
                bonuses["유산균 / 프로바이오틱스"] += 5.0 * scale
            elif goal == "피부탄력·이너뷰티":
                bonuses["콜라겐"] += 5.0 * scale
                bonuses["비타민C"] += 2.0 * scale
            elif goal == "체지방감소·다이어트":
                bonuses["멀티비타민"] += 2.0 * scale
            elif goal == "면역력저하":
                bonuses["멀티비타민"] += 4.0 * scale
                bonuses["유산균 / 프로바이오틱스"] += 3.0 * scale
            elif goal == "관절보호":
                bonuses["콜라겐"] += 4.0 * scale
                bonuses["마그네슘"] += 2.0 * scale
            elif goal == "수면부족·스트레스케어":
                bonuses["마그네슘"] += 5.0 * scale
                bonuses["멀티비타민"] += 2.0 * scale
            elif goal == "항노화·항산화":
                bonuses["비타민C"] += 5.0 * scale
                bonuses["멀티비타민"] += 2.0 * scale
            elif goal == "생리불순·생리통":
                bonuses["마그네슘"] += 3.0 * scale
                bonuses["오메가3"] += 3.0 * scale
            
    # 2. 라이프스타일 가산점
    exercise = survey_data.get("exercise", [])
    if any(ex in exercise for ex in ["저항성·근력 운동", "고강도 인터벌", "고강도 유산소"]):
        bonuses["마그네슘"] += 5.0
        bonuses["멀티비타민"] += 2.0
        
    drinking = survey_data.get("drinking", "전혀 안 함")
    if drinking == "잦은 음주":
        bonuses["멀티비타민"] += 4.0
        bonuses["마그네슘"] += 2.0
        
    smoking = survey_data.get("smoking", "비흡연")
    if smoking == "흡연":
        bonuses["비타민C"] += 5.0
        
    sleep = survey_data.get("sleep", "5~7시간")
    if sleep == "5시간 미만":
        bonuses["마그네슘"] += 4.0
        bonuses["멀티비타민"] += 3.0
        
    caffeine = survey_data.get("caffeine", "0잔")
    if caffeine in ["3잔", "4잔 이상"]:
        bonuses["마그네슘"] += 3.0
        
    return bonuses

def get_recommendations(survey_data, selected_category=None, top_n=10):
    """
    유저 문진 데이터를 입력받아 가산점 및 부작용/알레르기 필터를 연동해 추천 상품 목록을 반환합니다.
    """
    df = load_data()
    
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
    df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce').fillna(0).astype(int)
    
    # 부작용 성분 및 알레르기 유발원료 하드 필터 배제 로직
    side_effects = list(survey_data.get("side_effects", []))
    direct_input = survey_data.get("side_effect_direct", "").strip()
    if direct_input:
        side_effects.append(direct_input)
        
    banned_keywords = []
    for se in side_effects:
        se_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', se).lower()
        if se_clean and se_clean not in ["없음", "기타직접입력"]:
            banned_keywords.append(se_clean)
            if "오메가" in se_clean:
                banned_keywords.extend(["epa", "dha"])
            if "유산균" in se_clean or "프로바이오틱스" in se_clean:
                banned_keywords.extend(["유산균", "프로바이오틱스", "락토", "probiotic"])

    # 알레르기 동의어 확장 사전 탑재 (킬러 스펙 반영)
    allergies = list(survey_data.get("allergies", []))
    allergy_direct = survey_data.get("allergy_direct", "").strip()
    if allergy_direct:
        allergies.append(allergy_direct)
        
    allergy_rules = {
        "갑각류": ["새우", "게", "랍스터", "갑각류", "크랩", "shrimp", "crab", "lobster"],
        "대두": ["대두", "콩", "소이", "soy", "soybean"],
        "글루텐": ["밀", "보리", "호밀", "글루텐", "wheat", "gluten"],
        "유제품": ["우유", "유당", "유청", "카제인", "밀크", "milk", "whey", "lactose", "casein"],
        "견과류": ["땅콩", "호두", "아몬드", "캐슈", "견과", "peanut", "nut", "almond", "walnut"],
        "어류": ["피쉬", "생선", "연어", "대구", "어류", "fish", "salmon", "cod"],
        "과일류": ["사과", "복숭아", "토마토", "딸기", "바나나", "체리", "과일", "fruit", "apple", "peach", "tomato", "strawberry", "banana"]
    }
    
    allergy_keywords = []
    for alg in allergies:
        if alg in allergy_rules:
            allergy_keywords.extend(allergy_rules[alg])
        elif alg not in ["없음", "기타(직접입력)"]:
            alg_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', alg).lower()
            if alg_clean:
                matched_rule = False
                for rule_key, rule_vals in allergy_rules.items():
                    if alg_clean == rule_key or alg_clean in rule_vals:
                        allergy_keywords.extend(rule_vals)
                        matched_rule = True
                        break
                if not matched_rule:
                    allergy_keywords.append(alg_clean)
                
    # 필터 아웃 판정 함수
    def is_filtered_out(row):
        # A. 부작용 필터
        std_ing = str(row.get('표준성분', ''))
        std_ing_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', std_ing).lower()
        for kw in banned_keywords:
            if kw in std_ing_clean:
                return True
                
        # B. 알레르기 필터 (동의어 포함 대조)
        prod_name = str(row.get('product_name') or row.get('displayName') or '').lower()
        brand = str(row.get('brandName') or row.get('brand') or '').lower()
        full_info_text = f"{prod_name} {brand} {std_ing_clean}"
        for akw in allergy_keywords:
            if akw in full_info_text:
                return True
                
        return False

    df_filtered = df[~df.apply(is_filtered_out, axis=1)].copy()
    
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
    
    # 5. 선택 카테고리 필터링
    if selected_category:
        def contains_category(cat_str):
            if not isinstance(cat_str, str):
                return False
            cats = [c.strip() for c in cat_str.split(',')]
            return selected_category in cats
        df_filtered = df_filtered[df_filtered['최종카테고리'].apply(contains_category)].copy()
        
    recommended_df = df_filtered.sort_values(by='score', ascending=False)
    
    return recommended_df.head(top_n)
