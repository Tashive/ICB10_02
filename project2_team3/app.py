"""
NutriFit 영양제 추천 스마트 대시보드 MVP (Streamlit - 상대경로 버전)

이 스크립트는 면책 공지 및 필수 개인정보 동의 화면을 시작으로,
사용자의 인구통계학적 특성, 라이프스타일, 안전성 필터(부작용 및 알레르기), 
건강 고민 등 23개 전항목 문진을 기반으로 초개인화된 영양제를 추천하는 대시보드 앱입니다.
수집된 식약처 기능성 원료 API DB(I-0040)와 연계하여 주의사항 및 기능성을 시각화합니다.
모든 파일 및 데이터 경로는 배포 환경 호환성을 위해 상대 경로로 동적 지정됩니다.
"""

import os
import sys
import json
import re
import streamlit as st
import pandas as pd

# 프로젝트 루트 경로 추가 (모듈 임포트 호환성 확보)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project2_team3.src.engine.scoring import get_recommendations

# 페이지 설정
st.set_page_config(
    page_title="NutriFit Smart Dashboard",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 식약처 DB 경로 정의 (상대 경로 적용)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "0_data", "functional_ingredient_db.json")

@st.cache_data
def load_foodsafety_db():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# 식약처 성분 지식베이스 매칭 함수
def find_foodsafety_info(standard_ingredients, db_data):
    if not db_data:
        return []
        
    tokens = [t.strip() for t in standard_ingredients.split(',')]
    matched_infos = []
    
    for token in tokens:
        token_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', token).lower()
        if not token_clean or len(token_clean) < 1:
            continue
            
        matched_count = 0
        for row in db_data:
            raw_nm = row.get("APLC_RAWMTRL_NM", "")
            if not raw_nm:
                continue
            raw_nm_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', raw_nm).lower()
            
            if token_clean in raw_nm_clean or raw_nm_clean in token_clean:
                matched_infos.append({
                    "target_token": token,
                    "raw_material": raw_nm,
                    "functionality": row.get("FNCLTY_CN", "등록된 기능성 정보가 없습니다.").strip(),
                    "precautions": row.get("IFTKN_ATNT_MATR_CN", "등록된 주의사항 정보가 없습니다.").strip(),
                    "daily_intake": row.get("DAY_INTK_CN", "등록된 권장섭취량 정보가 없습니다.").strip()
                })
                matched_count += 1
                if matched_count >= 1:
                    break
    return matched_infos

def main():
    # 프리미엄 CSS 스타일 커스텀 주입
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+KR:wght@300;400;700&display=swap');
        
        .main-title {
            font-family: 'Outfit', 'Noto Sans KR', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #10b981, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .sub-title {
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 1.1rem;
            color: #94a3b8;
            margin-bottom: 30px;
        }
        .survey-container {
            background: rgba(30, 41, 59, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
        }
        .product-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .product-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .score-badge {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-block;
        }
        .rating-star {
            color: #fbbf24;
            font-weight: bold;
            font-size: 1.1rem;
        }
        .platform-badge {
            background: #334155;
            color: #cbd5e1;
            padding: 2px 8px;
            border-radius: 5px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">🥗 NutriFit Smart Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">식약처 공인 데이터베이스 및 초개인화 가중 스코어링 기반 웰니스 큐레이션</div>', unsafe_allow_html=True)

    db_data = load_foodsafety_db()

    # Session State 초기화
    if 'agreed' not in st.session_state:
        st.session_state.agreed = False
    if 'survey_completed' not in st.session_state:
        st.session_state.survey_completed = False
    if 'survey_data' not in st.session_state:
        st.session_state.survey_data = {}

    # ==================== 화면 분기 1: 면책 공지 및 필수 동의 화면 ====================
    if not st.session_state.agreed:
        st.subheader("🛡️ 서비스 시작 전 면책 공지 및 개인정보 활용 동의")
        
        st.warning(
            "⚠️ **서비스 안내 및 면책 공지**:\n\n"
            "본 서비스는 의학적 치료나 진단을 대체하는 의료 행위가 아니며, "
            "식약처 공공데이터를 기반으로 한 영양 정보 참고용 웰니스 큐레이션 서비스입니다."
        )
        
        st.write("서비스 이용을 위해 아래 필수 약관에 동의해 주세요.")
        
        agree_1 = st.checkbox("1. [필수] 서비스 이용약관 및 일반 개인정보 수집·이용 동의")
        agree_2 = st.checkbox("2. [필수] 만 14세 이상 이용 확인 (만 14세 미만은 이용이 제한됩니다)")
        agree_3 = st.checkbox("3. [필수] 건강 상태 및 라이프스타일(민감정보) 수집·이용 동의 (질환 정보, 복용 약물 등 수집 안내문 포함)")
        
        if st.button("동의하고 시작하기", disabled=not (agree_1 and agree_2 and agree_3)):
            st.session_state.agreed = True
            st.rerun()
            
    # ==================== 화면 분기 2: STEP 1~5 설문 문진 작성 ====================
    elif st.session_state.agreed and not st.session_state.survey_completed:
        st.subheader("📝 웰니스 초개인화 설문 (STEP 1 ~ STEP 5)")
        
        with st.form("survey_form"):
            
            # STEP 1. 기본 정보 (Demographics)
            st.markdown("### 👤 STEP1. 기본 정보")
            col_s1_1, col_s1_2 = st.columns(2)
            with col_s1_1:
                gender = st.radio("1. 성별:", ["남성", "여성", "응답하지 않음"])
                
                # 남성 전용 질문
                male_worries = []
                if gender == "남성":
                    male_worries = st.multiselect(
                        "2. [남성 전용] 고민 영역 (복수선택):",
                        ["탈모·두피 관리", "전립선 건강", "근육량 증가"]
                    )
                
                # 여성 전용 질문
                female_lifecycle = "해당없음"
                if gender == "여성":
                    female_lifecycle = st.selectbox(
                        "3. [여성 전용] 생애주기 상태:",
                        ["해당없음", "임신 준비 중", "임신 중", "수유 중", "폐경기"]
                    )
            
            with col_s1_2:
                age = st.selectbox(
                    "4. 연령대:",
                    ["20대 미만", "20대", "30대", "40대", "50대", "60대 이상"]
                )
                height = st.number_input("5-1. 키 (cm):", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
                weight = st.number_input("5-2. 몸무게 (kg):", min_value=30.0, max_value=200.0, value=65.0, step=0.1)
                
                # BMI 실시간 자동 연산
                bmi = round(weight / ((height / 100.0) ** 2), 2)
                bmi_status = "정상"
                if bmi < 18.5:
                    bmi_status = "저체중"
                elif 18.5 <= bmi < 23.0:
                    bmi_status = "정상"
                elif 23.0 <= bmi < 25.0:
                    bmi_status = "과체중"
                else:
                    bmi_status = "비만"
                st.markdown(f"**💡 자동 계산된 BMI:** `{bmi}` (분류: `{bmi_status}`)")

            # STEP 2. 라이프스타일 & 일상 습관 (Lifestyle)
            st.markdown("---")
            st.markdown("### 🏃 STEP2. 라이프스타일 & 일상 습관")
            col_s2_1, col_s2_2 = st.columns(2)
            with col_s2_1:
                exercise = st.multiselect(
                    "6. 운동 종류 및 목적 (복수선택):",
                    ["안 함·체력유지재활", "고강도 유산소", "저항성·근력 운동", "유연성·코어", "고강도 인터벌"]
                )
                drinking = st.selectbox("7. 음주 빈도:", ["전혀 안 함", "보통", "잦은 음주"])
                caffeine = st.selectbox("8. 하루 카페인 섭취:", ["0잔", "1~2잔", "3잔", "4잔 이상"])
            
            with col_s2_2:
                diet = st.selectbox(
                    "9. 식습관:",
                    ["일반식·불규칙", "육식 위주", "채식·간헐적 단식", "완벽한 비건"]
                )
                sleep = st.selectbox("10. 수면 시간:", ["5시간 미만", "5~7시간", "8시간 이상"])
                stress = st.select_slider(
                    "11. 스트레스 자가인지:",
                    options=["1단계", "2단계", "3단계", "4단계", "5단계"],
                    value="3단계"
                )

            # STEP 3. 건강 상태 & 안전성 필터 (Medical & Safety) ★필수 민감정보
            st.markdown("---")
            st.markdown("### 🛡️ STEP3. 건강 상태 & 안전성 필터 (민감 정보)")
            col_s3_1, col_s3_2 = st.columns(2)
            with col_s3_1:
                smoking = st.radio("12. 흡연 여부:", ["비흡연", "흡연"])
                allergies = st.multiselect(
                    "13. 알레르기 원료 (복수선택):",
                    ["갑각류", "대두", "글루텐", "유제품", "견과류", "어류", "없음"]
                )
            
            with col_s3_2:
                side_effects = st.multiselect(
                    "14. 과거 부작용 경험 성분 (복수선택):",
                    ["철분", "오메가3", "비타민C", "유산균", "기타 직접입력"]
                )
                side_effect_direct = ""
                if "기타 직접입력" in side_effects:
                    side_effect_direct = st.text_input("14-1. 부작용 성분 직접 입력 (쉼표 구분 가능):")
                
                diseases = st.multiselect(
                    "15. 지병 및 복용 약물 (복수선택):",
                    ["고혈압", "당뇨", "이상지질혈증", "만성 위장질환", "혈전 관련질환-항응고제", "간·신장질환", "없음·기타"]
                )

            # STEP 4. 건강 고민 및 목표 (Health Goals)
            st.markdown("---")
            st.markdown("### 🎯 STEP4. 건강 고민 및 목표")
            health_goals = st.multiselect(
                "16. 건강 고민 및 목표 (최대 2개 선택):",
                ["만성피로", "눈 건조·피로", "장 건강", "피부탄력·이너뷰티", "체지방감소·다이어트", "면역력저하", "관절보호", "수면부족·스트레스케어", "항노화·항산화", "생리불순·생리통"]
            )
            
            # STEP 5. 섭취 편의성 및 구매 성향 (Preference)
            st.markdown("---")
            st.markdown("### 🛍️ STEP5. 섭취 편의성 및 구매 성향")
            col_s5_1, col_s5_2 = st.columns(2)
            with col_s5_1:
                pill_discomfort = st.radio("17. 알약 불편감:", ["상관없음", "매우 불편함"])
                alternative_form = st.selectbox(
                    "18. 대안 제형 선호:",
                    ["소형 알약", "구미·젤리", "액상·드링크", "분말·포"]
                )
                pref_form = st.selectbox("19. 선호하는 영양제 형태:", ["젤리", "구미", "액상", "분말"])
                buy_method = st.selectbox("23. 구매 방식 선호:", ["정기구독", "1회구매", "상관없음"])
            
            with col_s5_2:
                values = st.multiselect(
                    "20. 구매 시 우선 가치 (최대 2개 선택):",
                    ["성분 함량", "원산지·브랜드", "첨가물 최소화", "복용 편의성"]
                )
                environment = st.radio("21. 복용 환경 선호:", ["거치형·대용량", "휴대형"])
                budget = st.selectbox(
                    "22. 월 예산대:",
                    ["1~3만원", "3~5만원", "5~10만원", "10만원 이상"]
                )

            # 건강 목표 및 우선가치 개수 유효성 검증
            goals_ok = len(health_goals) <= 2
            values_ok = len(values) <= 2
            
            if not goals_ok:
                st.warning("⚠️ **STEP4 건강고민**은 최대 2개까지만 선택이 가능합니다.")
            if not values_ok:
                st.warning("⚠️ **STEP5 구매 가치**는 최대 2개까지만 선택이 가능합니다.")

            submit_btn = st.form_submit_button("초개인화 영양제 추천 분석", disabled=not (goals_ok and values_ok and len(health_goals) > 0))
            
            if submit_btn:
                # 유저 입력값 데이터화
                st.session_state.survey_data = {
                    "gender": gender,
                    "male_worries": male_worries,
                    "female_lifecycle": female_lifecycle,
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "bmi": bmi,
                    "exercise": exercise,
                    "drinking": drinking,
                    "caffeine": caffeine,
                    "diet": diet,
                    "sleep": sleep,
                    "stress": stress,
                    "smoking": smoking,
                    "allergies": allergies,
                    "side_effects": side_effects,
                    "side_effect_direct": side_effect_direct,
                    "diseases": diseases,
                    "health_goals": health_goals,
                    "pill_discomfort": pill_discomfort,
                    "alternative_form": alternative_form,
                    "pref_form": pref_form,
                    "values": values,
                    "environment": environment,
                    "budget": budget,
                    "buy_method": buy_method
                }
                st.session_state.survey_completed = True
                st.rerun()

    # ==================== 화면 분기 3: 문진 분석 결과 및 큐레이션 ====================
    elif st.session_state.survey_completed:
        st.subheader("💡 뉴트리핏 초개인화 맞춤 큐레이션 결과")
        
        survey = st.session_state.survey_data
        
        # 상단 유저 요약 프로필
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                <strong>📊 분석 대상자 프로필:</strong> {survey['gender']} ({survey['age']}) | BMI: {survey['bmi']} | 
                🎯 <strong>핵심 건강고민:</strong> {', '.join(survey['health_goals'])} | 
                🚫 <strong>배제된 부작용 성분:</strong> {', '.join([s for s in survey['side_effects'] if s != '기타 직접입력'] + ([survey['side_effect_direct']] if survey['side_effect_direct'] else [])) or '없음'}
            </div>
        """, unsafe_allow_html=True)
        
        categories = ["마그네슘", "비타민C", "오메가3", "유산균 / 프로바이오틱스", "콜라겐", "멀티비타민"]
        selected_category = st.selectbox(
            "🔎 특정 추천 카테고리만 필터링하여 확인하기:",
            ["전체 맞춤 추천"] + categories,
            index=0
        )
        
        filter_cat = None if selected_category == "전체 맞춤 추천" else selected_category

        # 추천 엔진 구동
        try:
            recommendations = get_recommendations(survey, selected_category=filter_cat, top_n=10)
        except Exception as e:
            st.error(f"추천 엔진 구동 중 에러가 발생했습니다: {e}")
            if st.button("돌아가기"):
                st.session_state.survey_completed = False
                st.rerun()
            return

        if recommendations.empty:
            st.warning("⚠️ 입력하신 부작용 성분 필터 또는 맞춤 가중치 조건에 해당하는 제품이 목록에 존재하지 않거나 모두 필터링되었습니다.")
            if st.button("문진 다시 하기"):
                st.session_state.survey_completed = False
                st.rerun()
            return

        product_options = []
        for i, (idx, row) in enumerate(recommendations.iterrows()):
            platform = str(row.get('platform') or 'Unknown')
            name = str(row.get('product_name') or row.get('displayName') or '이름 없음')
            product_options.append(f"{i+1}위. [{platform}] {name[:60]}...")
            
        selected_product_label = st.selectbox(
            "🔬 식약처 공인 가이드라인을 조회할 영양제를 추천 목록에서 골라보세요:",
            product_options,
            index=0
        )
        
        selected_idx = product_options.index(selected_product_label)
        selected_row = recommendations.iloc[selected_idx]

        # 컬럼 분배
        col1, col2 = st.columns([1.2, 1.0], gap="large")

        with col1:
            st.markdown(f"### 🏆 큐레이션 추천 랭킹 TOP {len(recommendations)}")
            
            for i, (idx, row) in enumerate(recommendations.iterrows()):
                platform = str(row.get('platform') or 'Unknown')
                name = str(row.get('product_name') or row.get('displayName') or '이름 없음')
                brand = str(row.get('brandName') or row.get('brand') or '브랜드 정보 없음')
                rating = row.get('rating', 0.0)
                reviews = int(row.get('review_count', 0))
                score = row['score']
                std_ing = str(row.get('표준성분', ''))
                bonus = row.get('wellness_bonus', 0.0)

                # 선택 상품 강조 스타일
                if idx == selected_row.name:
                    card_style = "border: 2px solid #10b981; background: rgba(16, 185, 129, 0.12); box-shadow: 0 10px 25px rgba(16, 185, 129, 0.25);"
                    rank_prefix = f"🔥 {i+1}위 (선택됨)"
                else:
                    card_style = ""
                    rank_prefix = f"{i+1}위"

                st.markdown(f"""
                    <div class="product-card" style="{card_style}">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <span style="font-weight: 800; color: #10b981; font-size: 1.05rem;">{rank_prefix}</span>
                                <span class="platform-badge" style="margin-left: 8px;">{platform}</span>
                                <span style="font-size: 0.85rem; color: #94a3b8; margin-left: 8px;">{brand}</span>
                                <h4 style="margin: 8px 0 4px 0; color: #f8fafc; font-size: 1rem;">{name}</h4>
                                <span style="font-size: 0.85rem; color: #38bdf8;">🧬 표준성분: {std_ing}</span>
                                <div style="margin-top: 4px; font-size: 0.8rem; color: #a7f3d0;">💡 웰니스 맞춤 가산점: +{bonus}점</div>
                            </div>
                            <div style="text-align: right;">
                                <span class="score-badge">★ {score}</span>
                                <div style="margin-top: 5px;">
                                    <span class="rating-star">⭐ {rating:.1f}</span>
                                    <span style="font-size: 0.8rem; color: #64748b;">({reviews:,} reviews)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 🛡️ 식약처 공인 성분 지식베이스 가이드")
            
            std_ing = str(selected_row.get('표준성분', ''))
            st.info(f"📋 **선택 제품**: {selected_row.get('product_name')}\n\n🧬 **검출 표준 성분**: `{std_ing}`")
            
            st.markdown("---")

            # 식약처 DB 정보 실시간 연계 매칭
            foodsafety_infos = find_foodsafety_info(std_ing, db_data)

            if not foodsafety_infos:
                st.info("💡 본 제품의 표준성분은 고시형 비타민/마그네슘 원료로, 개별인정형 지식베이스에서 별도 조회되지 않고 표준 고시 섭취 규격에 따릅니다.")
                
                # 기본 고시 가이드
                if "마그네슘" in std_ing:
                    st.subheader("🍀 마그네슘 (Magnesium)")
                    st.write("**기능성 내용**: 에너지 이용에 필요, 신경과 근육 기능 유지에 필요")
                    st.write("**섭취 주의사항**: 신장 질환자의 경우 과량 섭취 시 고마그네슘혈증을 유발할 수 있으므로 주의")
                elif "비타민C" in std_ing:
                    st.subheader("🍀 비타민C (Vitamin C)")
                    st.write("**기능성 내용**: 결합조직 형성과 기능유지에 필요, 철의 흡수에 필요, 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요")
                    st.write("**섭취 주의사항**: 공복 섭취 시 위장 장애(속쓰림 등)를 유발할 수 있으므로 식후 섭취 권장")
                elif "비타민" in std_ing:
                    st.subheader("🍀 종합 비타민 (Multivitamin)")
                    st.write("**기능성 내용**: 체내 에너지 대사, 면역 및 항산화 등 신체 생리기능 조절에 필수적 요소")
                    st.write("**섭취 주의사항**: 종합 영양제의 경우 특정 영양소 과다 중독 방지를 위해 복용 기준량 엄수")
            else:
                tabs = st.tabs([f"🧪 {info['target_token']}" for info in foodsafety_infos])
                
                for tab, info in zip(tabs, foodsafety_infos):
                    with tab:
                        st.success(f"**식약처 공식 승인 명칭**: `{info['raw_material']}`")
                        
                        st.markdown("#### 🎯 기능성 내용")
                        for line in info['functionality'].split('\n'):
                            if line.strip():
                                st.write(f"- {line.strip()}")
                                
                        st.markdown("#### 🥄 권장 일일섭취량")
                        st.info(info['daily_intake'])
                        
                        st.markdown("#### ⚠️ 섭취 시 주의사항")
                        st.warning(info['precautions'])
            
            st.markdown("---")
            if st.button("🔄 문진 새로 작성하기"):
                st.session_state.survey_completed = False
                st.rerun()

if __name__ == "__main__":
    main()
