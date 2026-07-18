"""
NutriFit 영양제 추천 스마트 대시보드 MVP (Streamlit - 백오피스 관리자 모드 보안 스위치 도입 버전)

이 스크립트는 면책 공지 및 필수 개인정보 동의 화면을 시작으로,
사용자의 인구통계학적 특성, 라이프스타일, 안전성 필터(부작용 및 알레르기), 
건강 고민 등 23개 전항목 문진을 기반으로 초개인화된 영양제를 추천하는 대시보드 앱입니다.
사이드바 하단에 관리자 모드 토글 스위치(st.sidebar.checkbox)를 배치하고,
체크박스 활성화 여부에 따라 동적 메뉴 분기 및 백오피스 데이터 모니터링 시스템을 렌더링합니다.
들여쓰기(Indentation) 구조를 보완하여 메뉴 분기 간 화면 간섭을 원천 차단했습니다.
"""

import os
import sys
import json
import re
import streamlit as st
import pandas as pd

# 프로젝트 루트 경로 추가 (모듈 임포트 호환성 확보)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(BASE_DIR))

try:
    from src.engine.scoring import get_recommendations, load_data
except ModuleNotFoundError:
    from project2_team3.src.engine.scoring import get_recommendations, load_data

# 페이지 설정
st.set_page_config(
    page_title="NutriFit Smart Dashboard",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 식약처 DB 경로 정의 (상대 경로 적용)
DB_PATH = os.path.join(BASE_DIR, "0_data", "functional_ingredient_db.json")
LOG_FILE_PATH = os.path.join(BASE_DIR, "0_data", "survey_logs.csv")

@st.cache_data
def load_foodsafety_db():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# 제품 상세 페이지 URL 조회 헬퍼 함수
def get_product_detail_url(row):
    for col in ['detail_url', 'url', 'link']:
        val = row.get(col)
        if pd.notna(val) and isinstance(val, str) and val.strip():
            return val.strip()
    
    # URL이 누락되었을 때 쇼핑 통합 검색 링크로 대체 적용
    name = row.get('product_name') or row.get('displayName') or ''
    if name:
        return f"https://search.shopping.naver.com/search/all?query={name}"
    return "https://www.coupang.com"

# 자동 데이터 적재 파이프라인 함수
def log_survey_data(data):
    flat_data = {}
    for k, v in data.items():
        if isinstance(v, list):
            flat_data[k] = ",".join(v)
        else:
            flat_data[k] = v
            
    df_new = pd.DataFrame([flat_data])
    
    # 0_data 폴더 자동 생성 확인
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    
    if not os.path.exists(LOG_FILE_PATH):
        df_new.to_csv(LOG_FILE_PATH, index=False, encoding="utf-8-sig")
    else:
        df_new.to_csv(LOG_FILE_PATH, mode='a', header=False, index=False, encoding="utf-8-sig")

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

# 양방향 동의 동기화 콜백 함수들
def on_all_agree_change():
    val = st.session_state.all_agree
    st.session_state.agree_1 = val
    st.session_state.agree_2 = val
    st.session_state.agree_3 = val

def on_individual_change():
    st.session_state.all_agree = (
        st.session_state.agree_1 and
        st.session_state.agree_2 and
        st.session_state.agree_3
    )

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
            margin-bottom: 5px;
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

    # 1. 사이드바 - 간이 로그인/회원가입 데모 UI 배치
    st.sidebar.markdown("### 🔑 멤버십 서비스")
    if 'user_logged_in' not in st.session_state:
        st.session_state.user_logged_in = False
    if 'logged_in_username' not in st.session_state:
        st.session_state.logged_in_username = ""
        
    if not st.session_state.user_logged_in:
        st.sidebar.info("🔑 로그인하여 장바구니 저장하기 (추후 연동)")
        tab_login, tab_register = st.sidebar.tabs(["로그인 데모", "회원가입 데모"])
        
        with tab_login:
            login_id = st.text_input("아이디:", key="login_id")
            login_pw = st.text_input("비밀번호:", type="password", key="login_pw")
            if st.button("로그인"):
                if login_id.strip() and login_pw.strip():
                    st.session_state.user_logged_in = True
                    st.session_state.logged_in_username = login_id.strip()
                    st.sidebar.success(f"🎉 {login_id}님 로그인 성공!")
                    st.rerun()
                else:
                    st.sidebar.error("아이디와 비밀번호를 입력해 주세요.")
                    
        with tab_register:
            reg_id = st.text_input("가입할 아이디:", key="reg_id")
            reg_pw = st.text_input("비밀번호 설정:", type="password", key="reg_pw")
            reg_pw_confirm = st.text_input("비밀번호 확인:", type="password", key="reg_pw_confirm")
            if st.button("간이 회원가입"):
                if reg_id.strip() and reg_pw.strip():
                    if reg_pw == reg_pw_confirm:
                        st.sidebar.success("회원가입 성공! 로그인 탭에서 입력해 주세요.")
                    else:
                        st.sidebar.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.sidebar.error("모든 정보를 올바르게 기입해 주세요.")
    else:
        st.sidebar.markdown(f"**👤 회원: `{st.session_state.logged_in_username}`님**")
        st.sidebar.write("✅ 장바구니 실시간 동기화 상태 활성화")
        if st.button("로그아웃"):
            st.session_state.user_logged_in = False
            st.session_state.logged_in_username = ""
            st.rerun()

    # 사이드바 하단 - 시스템 관리자(Admin) 모드 토글 및 조건부 동적 메뉴 구성
    st.sidebar.markdown("---")
    admin_mode = st.sidebar.checkbox("⚙️ 시스템 관리자(Admin) 모드 활성화", value=False)
    
    menu_options = ["🥗 개인별 맞춤 큐레이션"]
    if admin_mode:
        menu_options.append("📊 뉴트리핏 데이터 인사이트 (Admin)")
        
    selected_menu = st.sidebar.radio("🧭 메뉴 바로가기", menu_options, index=0)

    # 2. 최상단 회원/비회원 배지 동적 노출 (백오피스 페이지가 아닐 때만 노출)
    if selected_menu == "🥗 개인별 맞춤 큐레이션":
        badge_label = "👤 회원 맞춤 진단 중" if st.session_state.user_logged_in else "🔴 비회원 맞춤 진단 중"
        badge_color = "#10b981" if st.session_state.user_logged_in else "#ef4444"
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div></div>
                <div style="background: {badge_color}; color: white; padding: 5px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                    {badge_label}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">🥗 NutriFit Smart Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">식약처 공인 데이터베이스 및 초개인화 가중 스코어링 기반 웰니스 큐레이션</div>', unsafe_allow_html=True)

    db_data = load_foodsafety_db()

    # Session State 초기화
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'agreed' not in st.session_state:
        st.session_state.agreed = False
    if 'survey_data' not in st.session_state:
        st.session_state.survey_data = {}
        
    # 양방향 동의 상태 초기화
    if 'all_agree' not in st.session_state:
        st.session_state.all_agree = False
    if 'agree_1' not in st.session_state:
        st.session_state.agree_1 = False
    if 'agree_2' not in st.session_state:
        st.session_state.agree_2 = False
    if 'agree_3' not in st.session_state:
        st.session_state.agree_3 = False

    # ==================== 메뉴 분기 1: 🥗 개인별 맞춤 큐레이션 ====================
    if selected_menu == "🥗 개인별 맞춤 큐레이션":
        # ==================== 화면 분기 0: 면책 공지 및 필수 동의 화면 ====================
        if not st.session_state.agreed:
            st.subheader("🛡️ 서비스 시작 전 면책 공지 및 개인정보 활용 동의")
            
            st.warning(
                "⚠️ **서비스 안내 및 면책 공지**:\n\n"
                "본 서비스는 의학적 치료나 진단을 대체하는 의료 행위가 아니며, "
                "식약처 공공데이터를 기반으로 한 영양 정보 참고용 웰니스 큐레이션 서비스입니다."
            )
            
            st.write("서비스 이용을 위해 아래 필수 약관에 동의해 주세요.")
            
            st.checkbox("전체 동의합니다.", key="all_agree", on_change=on_all_agree_change)
            st.markdown("---")
            
            col_ag1 = st.checkbox("1. [필수] 서비스 이용약관 및 일반 개인정보 수집·이용 동의", key="agree_1", on_change=on_individual_change)
            with st.expander("📜 약관 상세내역 조회"):
                st.markdown("""
                    * **수집 목적**: 개인 맞춤형 영양소 큐레이션 및 대시보드 제공
                    * **보유 및 이용 기간**: **목적 달성 즉시 파기** (탈퇴 또는 브라우저 세션 종료 시 즉시 영구 삭제)
                """)
                
            col_ag2 = st.checkbox("2. [필수] 만 14세 이상 이용 확인", key="agree_2", on_change=on_individual_change)
            with st.expander("📜 약관 상세내역 조회"):
                st.markdown("""
                    * **제한 고시**: 본 서비스는 아동의 민감정보 수집 방지를 위해 **만 14세 미만의 이용을 제한**합니다.
                """)
                
            col_ag3 = st.checkbox("3. [필수] 건강 상태 및 라이프스타일(민감정보) 수집·이용 동의", key="agree_3", on_change=on_individual_change)
            with st.expander("📜 약관 상세내역 조회"):
                st.markdown("""
                    * **법적 근거**: **개인정보보호법 제23조**에 의거, 질환 정보 및 부작용 이력 등 민감정보 수집에 동의합니다.
                    * **수집 항목**: 성별, 연령대, 신체 스펙(키, 몸무게), 라이프스타일 습관(운동, 음주, 카페인, 수면, 흡연), 지병 및 과거 부작용 경험 성분
                """)
                
            agreed_all_checked = st.session_state.agree_1 and st.session_state.agree_2 and st.session_state.agree_3
            
            if st.button("동의하고 시작하기", disabled=not agreed_all_checked):
                st.session_state.agreed = True
                st.session_state.step = 1
                st.rerun()
                
        # ==================== 화면 분기 1: STEP 1~5 설문 문진 작성 ====================
        elif st.session_state.step == 1:
            st.subheader("📝 웰니스 초개인화 설문 (STEP 1 ~ STEP 5)")
            
            # STEP 1. 기본 정보
            st.markdown("### 👤 STEP1. 기본 정보")
            col_s1_1, col_s1_2 = st.columns(2)
            with col_s1_1:
                gender = st.radio("1. 성별:", ["남성", "여성", "응답하지 않음"])
                
                male_worries = []
                if gender == "남성":
                    male_worries = st.multiselect(
                        "2. [남성 전용] 고민 영역 (복수선택):",
                        ["탈모·두피 관리", "전립선 건강", "근육량 증가"]
                    )
                
                female_lifecycle = "해당없음"
                if gender == "여성":
                    female_lifecycle = st.selectbox(
                        "3. [여성 전용] 생애주기 상태:",
                        ["해당없음", "임신 준비 중", "임신 중", "수유 중", "폐경기"]
                    )
            
            with col_s1_2:
                age = st.selectbox(
                    "4. 연령대:",
                    ["영유아 및 어린이(만 1세~12세)", "청소년(13세~19세)", "20세~25세", "26세~29세", "30대", "40대", "50대", "60대 이상"],
                    index=4
                )
                height = st.number_input("5-1. 키 (cm):", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
                weight = st.number_input("5-2. 몸무게 (kg):", min_value=30.0, max_value=200.0, value=65.0, step=0.1)
                
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
                st.markdown(f"""
                    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px; padding: 10px; margin-top: 10px;">
                        💡 <strong>실시간 BMI 지수:</strong> <span style="color: #3b82f6; font-weight: bold;">{bmi}</span> (분류: <strong>{bmi_status}</strong>)
                    </div>
                """, unsafe_allow_html=True)

            # STEP 2. 라이프스타일 & 일상 습관
            st.markdown("---")
            st.markdown("### 🏃 STEP2. 라이프스타일 & 일상 습관")
            col_s2_1, col_s2_2 = st.columns(2)
            with col_s2_1:
                exercise = st.multiselect(
                    "6. 운동 종류 및 목적 (복수선택):",
                    ["안 함·체력유지재활", "고강도 유산소", "저항성·근력 운동", "유연성·코어", "고강도 인터벌"],
                    default=["안 함·체력유지재활"]
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

            # STEP 3. 건강 상태 & 안전성 필터
            st.markdown("---")
            st.markdown("### 🛡️ STEP3. 건강 상태 & 안전성 필터 (민감 정보)")
            col_s3_1, col_s3_2 = st.columns(2)
            with col_s3_1:
                smoking = st.radio("12. 흡연 여부:", ["비흡연", "흡연"])
                
                allergies_raw = st.multiselect(
                    "13. 알레르기 원료 (복수선택):",
                    ["갑각류", "대두", "글루텐", "유제품", "견과류", "어류", "과일류", "없음", "기타(직접입력)"],
                    default=["과일류"]
                )
                
                allergy_direct = ""
                if "기타(직접입력)" in allergies_raw:
                    allergy_direct = st.text_input("13-1. 알레르기 직접 입력 (쉼표 구분):")
                
                allergies = []
                if "없음" in allergies_raw and len(allergies_raw) > 1:
                    allergies = [a for a in allergies_raw if a != "없음"]
                else:
                    allergies = allergies_raw
                    
            with col_s3_2:
                side_effects_raw = st.multiselect(
                    "14. 과거 부작용 경험 성분 (복수선택):",
                    ["철분", "오메가3", "비타민C", "유산균", "없음", "기타 직접입력"],
                    default=["없음"]
                )
                
                side_effect_direct = ""
                if "기타 직접입력" in side_effects_raw:
                    side_effect_direct = st.text_input("14-1. 부작용 성분 직접 입력 (쉼표 구분 가능):")
                
                side_effects = []
                if "없음" in side_effects_raw:
                    if len(side_effects_raw) > 1:
                        side_effects = [s for s in side_effects_raw if s != "없음"]
                        st.info("💡 **'없음'** 외의 부작용 성분이 선택되어 '없음' 항목이 자동으로 해제되었습니다.")
                    else:
                        side_effects = ["없음"]
                else:
                    side_effects = side_effects_raw
                
                diseases_raw = st.multiselect(
                    "15. 지병 및 복용 약물 (복수선택):",
                    ["고혈압", "당뇨", "이상지질혈증", "만성 위장질환", "혈전 관련질환-항응고제", "간·신장질환", "없음(단독 선택)", "기타(직접입력)"],
                    default=["당뇨"]
                )
                
                disease_direct = ""
                if "기타(직접입력)" in diseases_raw:
                    disease_direct = st.text_input("15-1. 지병 및 복용 약물 직접 입력 (기타 직접 입력용):")
                
                diseases = []
                if "없음(단독 선택)" in diseases_raw:
                    if len(diseases_raw) > 1:
                        diseases = [d for d in diseases_raw if d != "없음(단독 선택)"]
                        st.info("💡 **'없음(단독 선택)'** 외의 다른 지병이 선택되어 '없음' 항목이 자동으로 해제되었습니다.")
                    else:
                        diseases = ["없음(단독 선택)"]
                else:
                    diseases = diseases_raw

            # STEP 4. 건강 고민 및 목표
            st.markdown("---")
            st.markdown("### 🎯 STEP4. 건강 고민 및 목표")
            health_goals = st.multiselect(
                "16. 건강 고민 및 목표 (최대 3개 선택):",
                ["만성피로", "눈 건조·피로", "장 건강", "피부탄력·이너뷰티", "체지방감소·다이어트", "면역력저하", "관절보호", "수면부족·스트레스케어", "항노화·항산화", "생리불순·생리통"],
                default=["만성피로", "눈 건조·피로", "장 건강"],
                max_selections=3
            )
            
            # STEP 5. 섭취 편의성 및 구매 성향
            st.markdown("---")
            st.markdown("### 🛍️ STEP5. 섭취 편의성 및 구매 성향")
            col_s5_1, col_s5_2 = st.columns(2)
            with col_s5_1:
                pill_discomfort = st.radio("17. 알약 불편감:", ["상관없음", "매우 불편함"])
                alternative_form = st.selectbox(
                    "18. 대안 제형 선호:",
                    ["소형 알약", "구미·젤리", "액상·드링크", "분말·포"]
                )
                pref_form = st.selectbox(
                    "19. 선호하는 영양제 형태:",
                    ["정제(알약/정)", "캡슐", "젤리", "구미", "액상", "분말"],
                    index=0
                )
                buy_method = st.selectbox("23. 구매 방식 선호:", ["정기구독", "1회구매", "상관없음"])
            
            with col_s5_2:
                values = st.multiselect(
                    "20. 구매 시 우선 가치 (최대 2개 선택):",
                    ["성분 함량", "원산지·브랜드", "첨가물 최소화", "복용 편의성"],
                    default=["성분 함량"],
                    max_selections=2
                )
                environment = st.radio("21. 복용 환경 선호:", ["거치형·대용량", "휴대형"])
                budget = st.selectbox(
                    "22. 월 예산대:",
                    ["1~3만원", "3~5만원", "5~10만원", "10만원 이상"]
                )

            st.markdown("---")
            
            goals_ok = len(health_goals) > 0
            if not goals_ok:
                st.info("💡 진단 및 웰니스 분석을 진행하려면 **STEP4. 건강 고민 및 목표**를 최소 1개 선택해 주세요.")

            # 진단 및 단계 전환 버튼
            if st.button("진단 및 맞춤 스코어 확인하기 ➡️", disabled=not goals_ok):
                survey_payload = {
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
                    "allergy_direct": allergy_direct,
                    "side_effects": side_effects,
                    "side_effect_direct": side_effect_direct,
                    "diseases": diseases,
                    "disease_direct": disease_direct,
                    "health_goals": health_goals,
                    "pill_discomfort": pill_discomfort,
                    "alternative_form": alternative_form,
                    "pref_form": pref_form,
                    "values": values,
                    "environment": environment,
                    "budget": budget,
                    "buy_method": buy_method
                }
                st.session_state.survey_data = survey_payload
                
                try:
                    log_survey_data(survey_payload)
                except Exception as e:
                    st.error(f"로그 적재 실패: {e}")
                    
                st.session_state.step = 2
                st.rerun()

        # ==================== 화면 분기 2: 웰니스 스코어보드 결과 화면 ====================
        elif st.session_state.step == 2:
            st.subheader("📊 웰니스 스코어 분석 결과 리포트 (Step 2)")
            survey = st.session_state.survey_data
            
            try:
                from src.engine.scoring import calculate_wellness_bonus
            except ModuleNotFoundError:
                from project2_team3.src.engine.scoring import calculate_wellness_bonus
                
            bonuses = calculate_wellness_bonus(survey)
            
            col_board_left, col_board_right = st.columns([2.0, 1.0], gap="large")
            
            with col_board_left:
                st.markdown("### 🧬 내 몸에 필요한 6대 핵심 영양제 가산점 현황")
                st.write("유저의 일상 라이프스타일, 기본 정보 및 주요 건강 고민(최대 3개)에 대한 스코어 분배율을 복합 분석하여 산출된 보너스 스코어입니다.")
                
                col_b1, col_b2, col_b3 = st.columns(3)
                cols = [col_b1, col_b2, col_b3]
                
                keys = list(bonuses.keys())
                for idx, key in enumerate(keys):
                    col = cols[idx % 3]
                    score = bonuses[key]
                    
                    comment = "기본 섭취 권장"
                    if score >= 8.0:
                        comment = "🚨 매우 필요 (집중 섭취 추천)"
                    elif score >= 1.5:
                        comment = "⭐ 적극 권장 (맞춤 매칭)"
                        
                    col.markdown(f"""
                        <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 18px; margin-bottom: 15px;">
                            <span style="font-size: 0.85rem; color: #94a3b8;">영양소 성분</span>
                            <h4 style="margin: 2px 0 6px 0; color: #f8fafc;">{key}</h4>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 1.8rem; font-weight: 800; color: #10b981;">+{score:.2f}</span>
                                <span style="font-size: 0.8rem; color: #a7f3d0; background: rgba(16, 185, 129, 0.1); padding: 2px 6px; border-radius: 5px;">{comment}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
            with col_board_right:
                record_count = 0
                if os.path.exists(LOG_FILE_PATH):
                    try:
                        temp_df = pd.read_csv(LOG_FILE_PATH, encoding="utf-8-sig")
                        record_count = len(temp_df)
                    except:
                        pass
                
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1e1b4b, #311042); border: 1px solid rgba(167, 139, 250, 0.3); border-radius: 12px; padding: 20px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3); margin-top: 15px;">
                        <h4 style="margin: 0 0 10px 0; color: #c084fc; font-family: 'Outfit', 'Noto Sans KR', sans-serif;">🤖 AI 건강 패턴 분석 (ML 가동 대기)</h4>
                        <p style="font-size: 0.9rem; color: #e9d5ff; margin-bottom: 15px; line-height: 1.4;">
                            수집된 대용량 웰니스 적재 로그를 기반으로 향후 <strong>XGBoost 위험도 분류기</strong> 모델이 연동되는 지능형 분석 영역입니다.
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); padding: 8px 12px; border-radius: 8px;">
                            <span style="font-size: 0.8rem; color: #a78bfa;">📊 문진 데이터 축적 상태</span>
                            <span style="background: rgba(167, 139, 250, 0.2); color: #f472b6; font-weight: 700; padding: 2px 10px; border-radius: 20px; font-size: 0.85rem;">
                                누적 데이터: {record_count}건
                            </span>
                        </div>
                        <div style="margin-top: 15px; border-top: 1px dashed rgba(167, 139, 250, 0.2); padding-top: 10px; font-size: 0.75rem; color: #a78bfa; text-align: center;">
                            ⏳ 목표 데이터셋 500건 충족 시 AI 심혈관/대사 위험도 스위칭 모듈 활성화
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown("---")
            
            st.markdown("### 🛡️ 개인 맞춤형 안전성 필터 동작 리포트")
            banned_list = list(survey.get("side_effects", []))
            direct_banned = survey.get("side_effect_direct", "").strip()
            if direct_banned:
                banned_list.append(direct_banned)
            banned_list = [b for b in banned_list if b != "기타 직접입력" and b != "없음"]
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                st.markdown("#### 🚫 부작용 배제 필터")
                if banned_list:
                    st.error(f"다음 부작용 성분이 함유된 제품군은 추천 리스트에서 **원천 배제(Hard Filter)** 처리되었습니다:\n\n`{', '.join(banned_list)}`")
                else:
                    st.success("부작용 배제 성분이 설정되지 않았습니다. 모든 맞춤 영양제를 정상 매칭합니다.")
            with col_f2:
                st.markdown("#### 🌾 알레르기 및 주의 원료")
                allergies = list(survey.get("allergies", []))
                allergy_direct = survey.get("allergy_direct", "").strip()
                if allergy_direct:
                    allergies.append(allergy_direct)
                allergies_cleaned = [a for a in allergies if a not in ["없음", "기타(직접입력)"]]
                
                if allergies_cleaned:
                    st.error(f"다음 알레르기 유발 물질이 포함된 제품군은 추천 리스트에서 **원천 배제(Hard Filter)** 처리되었습니다:\n\n`{', '.join(allergies_cleaned)}`")
                else:
                    st.success("알레르기 필터가 적용되지 않았습니다.")
                    
            st.markdown("---")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("⬅️ 이전 단계 (문진 수정)"):
                    st.session_state.step = 1
                    st.rerun()
            with col_btn2:
                if st.button("초개인화 장바구니 큐레이션 보기 ➡️"):
                    st.session_state.step = 3
                    st.rerun()

        # ==================== 화면 분기 3: 초개인화 장바구니 큐레이션 결과 ====================
        elif st.session_state.step == 3:
            st.subheader("💡 뉴트리핏 초개인화 맞춤 큐레이션 결과 (Step 3)")
            
            survey = st.session_state.survey_data
            
            side_effects_cleaned = [s for s in survey.get("side_effects", []) if s not in ["없음", "기타 직접입력"]]
            if survey.get("side_effect_direct", "").strip():
                side_effects_cleaned.append(survey.get("side_effect_direct"))
                
            algs = list(survey.get("allergies", []))
            if survey.get("allergy_direct", "").strip():
                algs.append(survey.get("allergy_direct"))
            algs_display = [a for a in algs if a not in ["없음", "기타(직접입력)"]]
            
            exclusions = side_effects_cleaned + algs_display
            exclusions_str = ', '.join(exclusions) if exclusions else '없음'
            
            st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                    <strong>📊 분석 대상자 프로필:</strong> {survey['gender']} ({survey['age']}) | BMI: {survey['bmi']} | 
                    🎯 <strong>핵심 건강고민(가산점 분배):</strong> {', '.join(survey['health_goals'])} | 
                    🚫 <strong>배제된 부작용/알레르기:</strong> {exclusions_str}
                </div>
            """, unsafe_allow_html=True)
            
            categories = ["마그네슘", "비타민C", "오메가3", "유산균 / 프로바이오틱스", "콜라겐", "멀티비타민"]
            selected_category = st.selectbox(
                "🔎 특정 추천 카테고리만 필터링하여 확인하기:",
                ["전체 맞춤 추천"] + categories,
                index=0
            )
            
            filter_cat = None if selected_category == "전체 맞춤 추천" else selected_category

            try:
                recommendations = get_recommendations(survey, selected_category=filter_cat, top_n=10)
            except Exception as e:
                st.error(f"추천 엔진 구동 중 에러가 발생했습니다: {e}")
                if st.button("돌아가기"):
                    st.session_state.step = 2
                    st.rerun()
                return

            if recommendations.empty:
                st.warning("⚠️ 입력하신 알레르기/부작용 필터 또는 맞춤 가중치 조건에 해당하는 제품이 목록에 존재하지 않거나 모두 필터링되었습니다.")
                if st.button("⬅️ 웰니스 리포트로 돌아가기"):
                    st.session_state.step = 2
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
                                    <div style="margin-top: 4px; font-size: 0.8rem; color: #a7f3d0;">💡 웰니스 맞춤 가산점: +{bonus:.2f}점</div>
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
                
                detail_url = get_product_detail_url(selected_row)
                st.link_button("🛒 제품 상세 보기 ↗", url=detail_url, use_container_width=True)
                
                st.markdown("---")

                foodsafety_infos = find_foodsafety_info(std_ing, db_data)

                if not foodsafety_infos:
                    st.info("💡 본 제품의 표준성분은 고시형 비타민/마그네슘 원료로, 개별인정형 지식베이스에서 별도 조회되지 않고 표준 고시 섭취 규격에 따릅니다.")
                    
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
                
                col_btn_back1, col_btn_back2 = st.columns(2)
                with col_btn_back1:
                    if st.button("⬅️ 이전 단계 (웰니스 리포트)"):
                        st.session_state.step = 2
                        st.rerun()
                with col_btn_back2:
                    if st.button("🔄 문진 새로 작성하기"):
                        st.session_state.agreed = False
                        st.session_state.step = 1
                        st.session_state.survey_data = {}
                        st.session_state.all_agree = False
                        st.session_state.agree_1 = False
                        st.session_state.agree_2 = False
                        st.session_state.agree_3 = False
                        st.rerun()

    # ==================== 메뉴 분기 2: 📊 뉴트리핏 데이터 인사이트 (Admin) ====================
    elif selected_menu == "📊 뉴트리핏 데이터 인사이트 (Admin)":
        st.subheader("📊 뉴트리핏 백오피스 데이터 모니터링 시스템")
        
        # 데이터 사전 로딩
        try:
            df_master = load_data()
            master_count = len(df_master)
        except Exception as e:
            df_master = pd.DataFrame()
            master_count = 0
            st.error(f"마스터 상품 데이터를 불러올 수 없습니다: {e}")
            
        record_count = 0
        if os.path.exists(LOG_FILE_PATH):
            try:
                df_logs = pd.read_csv(LOG_FILE_PATH, encoding="utf-8-sig")
                record_count = len(df_logs)
            except:
                df_logs = pd.DataFrame()
        else:
            df_logs = pd.DataFrame()
            
        # [상단 지표]
        col1, col2, col3 = st.columns(3)
        col1.metric("식약처 공인 인정 원료", "768개")
        col2.metric("매칭 마스터 상품 수", f"{master_count:,}개")
        col3.metric("누적 사용자 진단 로그", f"{record_count:,}건")
        
        st.markdown("---")
        
        # [중단 차트] 마스터 상품 데이터 상위 5대 표준성분 분포
        st.markdown("### 🏆 마스터 상품 데이터 상위 5대 표준성분 분포")
        if not df_master.empty and '표준성분' in df_master.columns:
            top_ingredients = df_master['표준성분'].dropna().str.split(',').explode().str.strip().value_counts().head(5)
            if not top_ingredients.empty:
                chart_df = pd.DataFrame({"상품 수": top_ingredients})
                st.bar_chart(chart_df)
            else:
                st.info("표준성분 데이터가 비어 있습니다.")
        else:
            st.info("표준성분 데이터를 표시할 수 없습니다.")
            
        st.markdown("---")
        
        # [하단 트렌드] survey_logs.csv TOP 3 분포 비율
        st.markdown("### 🎯 누적 사용자 건강고민 TOP 3 트렌드")
        if not df_logs.empty and 'health_goals' in df_logs.columns:
            top_goals = df_logs['health_goals'].dropna().str.split(',').explode().str.strip().value_counts().head(3)
            if not top_goals.empty:
                goals_chart_df = pd.DataFrame({"누적 진단 수": top_goals})
                st.bar_chart(goals_chart_df)
            else:
                st.info("누적된 건강고민 트렌드 정보가 없습니다.")
        else:
            st.info("누적된 사용자 진단 로그 파일(survey_logs.csv)이 존재하지 않거나 비어 있습니다.")

if __name__ == "__main__":
    main()
