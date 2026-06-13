"""
네이버 오픈 API를 활용하여 다양한 트렌드 및 검색 데이터를 수집, 분석 및 시각화하는 Streamlit 대시보드 애플리케이션입니다.
본 대시보드는 네이버 검색어 트렌드, 쇼핑 트렌드, 쇼핑 검색, 블로그 검색, 카페글 검색, 뉴스 검색 서비스를 제공합니다.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import naver_api
import shopping_categories

# 1. 페이지 설정 및 디자인 시스템 정의
st.set_page_config(
    page_title="Naver API Insight Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS를 통한 Glassmorphism 및 프리미엄 테마 적용
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    /* 글꼴 적용 */
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    }
    
    /* 카드 디자인 */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 12px 40px 0 rgba(16, 185, 129, 0.15);
    }
    
    /* 텍스트 색상 및 강조 */
    .text-green {
        color: #10b981 !important;
        font-weight: 800;
    }
    .text-blue {
        color: #3b82f6 !important;
        font-weight: 800;
    }
    .text-purple {
        color: #8b5cf6 !important;
        font-weight: 800;
    }
    .text-red {
        color: #ef4444 !important;
        font-weight: 800;
    }
    .text-orange {
        color: #f97316 !important;
        font-weight: 800;
    }
    
    /* 헤더 스타일 */
    .dashboard-title {
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.6rem;
        margin-bottom: 5px;
    }
    
    /* 구분선 */
    .glow-divider {
        height: 3px;
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.6) 0%, rgba(57, 130, 246, 0.6) 50%, rgba(139, 92, 246, 0.6) 100%);
        margin-bottom: 25px;
        border-radius: 2px;
    }
    
    /* 안내 문구 스타일 */
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    }
    
    /* 초록색 스코어카드 */
    .green-metric-card {
        background: rgba(16, 185, 129, 0.08);
        border: 1.5px solid rgba(16, 185, 129, 0.25);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    .green-metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(16, 185, 129, 0.6);
        box-shadow: 0 12px 40px 0 rgba(16, 185, 129, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# 2. 캐싱 지원 API 호출 함수 래퍼 정의
@st.cache_data(ttl=600)
def cached_search_trend(client_id, client_secret, keywords, start_date, end_date, time_unit, device, gender, ages):
    return naver_api.fetch_search_trend(client_id, client_secret, keywords, start_date, end_date, time_unit, device, gender, ages)

@st.cache_data(ttl=600)
def cached_shopping_insight(client_id, client_secret, category_id, category_name, start_date, end_date, time_unit, device, gender, ages):
    return naver_api.fetch_shopping_insight(client_id, client_secret, category_id, category_name, start_date, end_date, time_unit, device, gender, ages)

@st.cache_data(ttl=300)
def cached_blog_search(client_id, client_secret, query, display, start, sort):
    return naver_api.fetch_blog_search(client_id, client_secret, query, display, start, sort)

@st.cache_data(ttl=300)
def cached_cafe_search(client_id, client_secret, query, display, start, sort):
    return naver_api.fetch_cafe_search(client_id, client_secret, query, display, start, sort)

@st.cache_data(ttl=300)
def cached_news_search(client_id, client_secret, query, display, start, sort):
    return naver_api.fetch_news_search(client_id, client_secret, query, display, start, sort)

@st.cache_data(ttl=300)
def cached_shopping_search(client_id, client_secret, query, display, start, sort, filter_pay, exclude_types):
    return naver_api.fetch_shopping_search(client_id, client_secret, query, display, start, sort, filter_pay, exclude_types)

# --- 쇼핑 트렌드 고도화 분석을 위한 가상/시뮬레이션 데이터 생성 도우미 함수 ---
def generate_mock_products(cat_name, cat_id):
    """
    카테고리 이름을 기반으로 난수 시드를 생성하여 개별 상품의 가상 클릭수, 전환율, 가격, 매출 정보를 모델링해 랭킹 보드용 데이터를 반환합니다.
    """
    seed = int(cat_id) if str(cat_id).isdigit() else hash(cat_name) % (10**8)
    np.random.seed(seed)
    
    adjectives = ["친환경", "북유럽풍", "모던", "프리미엄", "에센셜", "미니멀", "스마트", "럭셔리", "내추럴", "심플", "컴팩트", "가성비갑"]
    types = ["클래식", "시그니처", "베이직", "플러스", "디럭스", "울트라", "이지", "컴포트"]
    
    product_names = []
    num_products = 10
    
    for i in range(num_products):
        adj = np.random.choice(adjectives)
        tp = np.random.choice(types)
        num = np.random.randint(1, 100)
        
        prod_name = f"{adj} {cat_name} {tp} {num:02d}"
        clicks = int(np.random.lognormal(mean=7, sigma=0.8))
        conversion_rate = float(np.random.beta(a=3, b=100) * 100)
        
        # 카테고리별 합리적 평균 단가 책정
        if "패션" in cat_name or "의류" in cat_name:
            avg_price = int(np.random.normal(loc=55000, scale=15000))
        elif "디지털" in cat_name or "가전" in cat_name:
            avg_price = int(np.random.normal(loc=450000, scale=120000))
        elif "가구" in cat_name or "인테리어" in cat_name or "수납" in cat_name:
            avg_price = int(np.random.normal(loc=120000, scale=35000))
        else:
            avg_price = int(np.random.normal(loc=35000, scale=10000))
            
        avg_price = max(5000, (avg_price // 1000) * 1000)
        purchases = max(1, int(clicks * (conversion_rate / 100)))
        revenue = purchases * avg_price
        
        product_names.append({
            "상품명": prod_name,
            "클릭수": clicks,
            "구매전환율 (%)": round(conversion_rate, 2),
            "추정 구매수": purchases,
            "평균 단가 (원)": avg_price,
            "추정 매출액 (원)": revenue
        })
        
    return pd.DataFrame(product_names)

def generate_mock_demographics(cat_name, cat_id):
    """
    카테고리명에 맞게 성별 및 연령대별 가중치가 적용된 데모 데이터를 시드 고정 방식으로 생성합니다.
    """
    seed = int(cat_id) if str(cat_id).isdigit() else hash(cat_name) % (10**8)
    np.random.seed(seed)
    
    # 성비 편향 설정
    female_ratio = 0.5
    if any(k in cat_name for k in ["여성", "화장품", "뷰티", "육아", "식품", "주방", "수납"]):
        female_ratio = np.random.uniform(0.70, 0.92)
    elif any(k in cat_name for k in ["남성", "디지털", "가전", "IT", "게임", "자동차"]):
        female_ratio = np.random.uniform(0.15, 0.35)
    else:
        female_ratio = np.random.uniform(0.40, 0.60)
        
    male_ratio = 1.0 - female_ratio
    
    # 연령 분포 설정
    if "가전" in cat_name or "디지털" in cat_name or "IT" in cat_name:
        age_distribution = np.random.dirichlet([2, 8, 8, 4, 2, 1])
    elif "의류" in cat_name or "패션" in cat_name:
        age_distribution = np.random.dirichlet([3, 7, 9, 6, 3, 1])
    elif "육아" in cat_name:
        age_distribution = np.random.dirichlet([1, 2, 12, 3, 1, 0.5])
    else:
        age_distribution = np.random.dirichlet([3, 5, 7, 7, 5, 3])
        
    ages = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
    age_ratios = {ages[i]: round(age_distribution[i] * 100, 1) for i in range(len(ages))}
    
    return {
        "gender": {"여성": round(female_ratio * 100, 1), "남성": round(male_ratio * 100, 1)},
        "age": age_ratios
    }

def generate_mock_sales_trend(df_cat, avg_price_unit):
    """
    클릭수 지표(ratio)와 요일별 온라인 쇼핑 가중치, 카테고리별 단가를 조합하여 시계열 매출 추이를 유도합니다.
    """
    np.random.seed(42)
    df_sales = df_cat.copy()
    
    # 요일별 쇼핑 가중치
    df_sales["dayofweek"] = df_sales["period"].dt.dayofweek
    weekday_weights = {0: 1.15, 1: 1.20, 2: 1.15, 3: 1.05, 4: 0.95, 5: 0.80, 6: 0.85}
    df_sales["weight"] = df_sales["dayofweek"].map(weekday_weights)
    
    traffic_factor = 250
    df_sales["추정 매출액"] = (df_sales["ratio"] * traffic_factor * df_sales["weight"] * avg_price_unit).astype(int)
    
    return df_sales[["period", "추정 매출액", "category"]]

def parse_smartstore_data(file):
    """
    스마트스토어 상품/판매 실적 엑셀 또는 CSV 파일을 파싱하여 표준 칼럼 구조로 변환합니다.
    """
    try:
        # 파일 확장자에 따라 판다스로 읽음
        if file.name.endswith('.csv'):
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding='cp949')
        else:
            df = pd.read_excel(file)
            
        # 컬럼 표준화 매핑 딕셔너리
        column_mappings = {
            "상품명": ["상품명", "물품명", "상품 이름", "Product Name"],
            "상품ID": ["상품번호", "상품ID", "상품 번호", "Product ID"],
            "클릭수": ["유입수", "클릭수", "조회수", "클릭", "Clicks", "Views"],
            "구매수": ["결제수량", "구매수량", "구매수", "판매수량", "Sales Qty", "Purchases"],
            "매출액": ["결제금액", "매출액", "판매금액", "매출", "Revenue", "Sales Amount"],
            "구매전환율": ["구매전환율", "전환율", "구매전환율 (%)", "Conversion Rate"]
        }
        
        standard_df = pd.DataFrame()
        
        for std_col, syn_list in column_mappings.items():
            matched_col = None
            for col in df.columns:
                clean_col = str(col).strip().replace(" ", "").lower()
                clean_syns = [str(syn).strip().replace(" ", "").lower() for syn in syn_list]
                if clean_col in clean_syns or any(clean_syn in clean_col for clean_syn in clean_syns):
                    matched_col = col
                    break
            
            if matched_col is not None:
                standard_df[std_col] = df[matched_col]
            else:
                if std_col == "상품명":
                    raise ValueError("엑셀 파일 내에서 '상품명' 컬럼을 찾을 수 없습니다.")
                elif std_col == "클릭수":
                    standard_df["클릭수"] = 0
                elif std_col == "구매수":
                    standard_df["구매수"] = 0
                elif std_col == "매출액":
                    standard_df["매출액"] = 0
                elif std_col == "구매전환율":
                    standard_df["구매전환율"] = 0.0
                    
        standard_df["상품명"] = standard_df["상품명"].astype(str)
        if "상품ID" in standard_df.columns:
            standard_df["상품ID"] = standard_df["상품ID"].astype(str)
        else:
            standard_df["상품ID"] = [f"MOCK_{i}" for i in range(len(standard_df))]
            
        standard_df["클릭수"] = pd.to_numeric(standard_df["클릭수"], errors='coerce').fillna(0).astype(int)
        standard_df["구매수"] = pd.to_numeric(standard_df["구매수"], errors='coerce').fillna(0).astype(int)
        standard_df["매출액"] = pd.to_numeric(standard_df["매출액"], errors='coerce').fillna(0).astype(int)
        standard_df["구매전환율"] = pd.to_numeric(standard_df["구매전환율"], errors='coerce').fillna(0.0).astype(float)
        
        mask = (standard_df["구매전환율"] == 0.0) & (standard_df["클릭수"] > 0)
        standard_df.loc[mask, "구매전환율"] = (standard_df.loc[mask, "구매수"] / standard_df.loc[mask, "클릭수"] * 100).round(2)
        
        standard_df["평균 단가 (원)"] = 0
        price_mask = standard_df["구매수"] > 0
        standard_df.loc[price_mask, "평균 단가 (원)"] = (standard_df.loc[price_mask, "매출액"] / standard_df.loc[price_mask, "구매수"]).astype(int)
        
        zero_price_mask = standard_df["평균 단가 (원)"] == 0
        standard_df.loc[zero_price_mask, "평균 단가 (원)"] = 35000
        
        return standard_df
    except Exception as e:
        raise ValueError(f"파일 파싱 중 에러 발생: {str(e)}")

# UI 헬퍼 함수
def make_card(title, value, subtitle="", color_class=""):
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>
        <div style="font-size: 26px; font-weight: 800; margin-top: 8px;" class="{color_class}">{value}</div>
        {f'<div style="color: #64748b; font-size: 11px; margin-top: 6px;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

# 3. 사이드바 - 네비게이션 메뉴 (상단) + API 설정 (하단)

# API 키 로드 (환경변수 → Streamlit Secrets → 세션 상태 순)
env_client_id = os.getenv("NAVER_CLIENT_ID", "")
env_client_secret = os.getenv("NAVER_CLIENT_SECRET", "")

secrets_client_id = env_client_id
secrets_client_secret = env_client_secret

if not secrets_client_id or not secrets_client_secret:
    try:
        secrets_client_id = st.secrets.get("NAVER_CLIENT_ID", "")
        secrets_client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
    except Exception:
        secrets_client_id = ""
        secrets_client_secret = ""

default_client_id = secrets_client_id if secrets_client_id else st.session_state.get("client_id", "")
default_client_secret = secrets_client_secret if secrets_client_secret else st.session_state.get("client_secret", "")

# 사이드바 스타일 추가
st.sidebar.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #1e293b;
}
.sidebar-section-header {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 10px 0 6px 0;
    margin-top: 4px;
}
.sidebar-api-header {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 700;
    padding: 6px 0 10px 0;
}
div[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── 안내 섹션 ──
st.sidebar.markdown('<div class="sidebar-section-header">안내</div>', unsafe_allow_html=True)

menu_all = [
    "🏠 대시보드 소개",
    "📈 검색어 트렌드 분석",
    "🛍️ 쇼핑 트렌드 분석",
    "📦 내 쇼핑몰 상품 진단",
    "🛒 쇼핑 검색 분석",
    "📝 블로그 검색 분석",
    "👥 카페글 검색 분석",
    "📰 뉴스 검색 분석",
]

# 세션 상태에서 현재 선택된 메뉴 가져오기
if "current_menu" not in st.session_state:
    st.session_state["current_menu"] = "🏠 대시보드 소개"

def set_menu(selected):
    """메뉴 선택 콜백 함수"""
    st.session_state["current_menu"] = selected

# 안내 섹션
for item in ["🏠 대시보드 소개"]:
    is_active = st.session_state["current_menu"] == item
    btn_style = "primary" if is_active else "secondary"
    if st.sidebar.button(item, key=f"menu_{item}", use_container_width=True, type=btn_style):
        set_menu(item)
        st.rerun()

# 데이터랩 트렌드 분석 섹션
st.sidebar.markdown('<div class="sidebar-section-header">데이터랩 트렌드 분석</div>', unsafe_allow_html=True)
for item in ["📈 검색어 트렌드 분석", "🛍️ 쇼핑 트렌드 분석"]:
    is_active = st.session_state["current_menu"] == item
    btn_style = "primary" if is_active else "secondary"
    if st.sidebar.button(item, key=f"menu_{item}", use_container_width=True, type=btn_style):
        set_menu(item)
        st.rerun()

# 쇼핑몰 매출 실적 분석 섹션
st.sidebar.markdown('<div class="sidebar-section-header">쇼핑몰 매출 실적 분석</div>', unsafe_allow_html=True)
for item in ["📦 내 쇼핑몰 상품 진단"]:
    is_active = st.session_state["current_menu"] == item
    btn_style = "primary" if is_active else "secondary"
    if st.sidebar.button(item, key=f"menu_{item}", use_container_width=True, type=btn_style):
        set_menu(item)
        st.rerun()

# 검색 데이터 다차원 분석 섹션
st.sidebar.markdown('<div class="sidebar-section-header">검색 데이터 다차원 분석</div>', unsafe_allow_html=True)
for item in ["🛒 쇼핑 검색 분석", "📝 블로그 검색 분석", "👥 카페글 검색 분석", "📰 뉴스 검색 분석"]:
    is_active = st.session_state["current_menu"] == item
    btn_style = "primary" if is_active else "secondary"
    if st.sidebar.button(item, key=f"menu_{item}", use_container_width=True, type=btn_style):
        set_menu(item)
        st.rerun()

menu = st.session_state["current_menu"]

# ── 구분선 ──
st.sidebar.markdown("---")

# ── 하단: NAVER API 설정 섹션 ──
st.sidebar.markdown('<div class="sidebar-api-header">🔑 NAVER API 설정</div>', unsafe_allow_html=True)

client_id_input = st.sidebar.text_input("Naver Client ID", value=default_client_id, type="password", help="네이버 개발자 센터에서 발급받은 Client ID를 입력하세요.")
client_secret_input = st.sidebar.text_input("Naver Client Secret", value=default_client_secret, type="password", help="네이버 개발자 센터에서 발급받은 Client Secret을 입력하세요.")

client_id = client_id_input.strip() if client_id_input else ""
client_secret = client_secret_input.strip() if client_secret_input else ""

if client_id: st.session_state["client_id"] = client_id
if client_secret: st.session_state["client_secret"] = client_secret

# API 연결 상태 표시
if client_id and client_secret:
    st.sidebar.markdown(
        """
        <div style="background-color: #10b981; color: white; padding: 12px 14px; border-radius: 10px; font-weight: 600; display: flex; align-items: center; gap: 10px; margin-top: 8px; font-size: 14px;">
            <span>&#9989;</span>
            <span>API 인증 키를 성공적으로 로드했습니다.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        """
        <div style="background-color: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4); color: #fca5a5; padding: 12px 14px; border-radius: 10px; font-weight: 600; display: flex; align-items: center; gap: 10px; margin-top: 8px; font-size: 14px;">
            <span>&#9888;</span>
            <span>API Key를 입력해 주세요.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# 4. 공통 검색 조건 입력 컴포넌트 (메인 화면 상단)
# 메뉴명 → 타이틀 매핑
menu_title_map = {
    "🏠 대시보드 소개": "대시보드 소개",
    "📈 검색어 트렌드 분석": "검색어 트렌드",
    "🛍️ 쇼핑 트렌드 분석": "쇼핑 트렌드 (인사이트)",
    "📦 내 쇼핑몰 상품 진단": "내 쇼핑몰 상품 진단",
    "🛒 쇼핑 검색 분석": "쇼핑 검색",
    "📝 블로그 검색 분석": "블로그 검색",
    "👥 카페글 검색 분석": "카페글 검색",
    "📰 뉴스 검색 분석": "뉴스 검색",
}
display_title = menu_title_map.get(menu, menu)
st.markdown(f'<div class="dashboard-title">네이버 {display_title} 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

# 대시보드 소개 페이지
if menu == "🏠 대시보드 소개":
    st.markdown("""
    <div style="background: rgba(30,41,59,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 30px; margin-bottom: 24px;">
        <h2 style="color: #10b981; margin-top: 0;">📊 Naver API Insight Dashboard 소개</h2>
        <p style="color: #cbd5e1; font-size: 15px; line-height: 1.8;">
            본 대시보드는 <b>네이버 오픈 API</b>를 활용하여 다양한 트렌드 및 검색 데이터를 수집, 분석, 시각화하는 도구입니다.
            왼쪽 사이드바에서 원하는 분석 메뉴를 선택하여 시작하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 28px; margin-bottom: 10px;">📈</div>
            <div style="color: #10b981; font-weight: 700; font-size: 16px; margin-bottom: 6px;">데이터랩 트렌드 분석</div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">검색어 트렌드 및 쇼핑 카테고리별 클릭 트렌드를 시계열로 분석합니다.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 28px; margin-bottom: 10px;">📦</div>
            <div style="color: #8b5cf6; font-weight: 700; font-size: 16px; margin-bottom: 6px;">내 쇼핑몰 상품 진단</div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">쇼핑몰 판매/실적 리포트를 업로드하여 BCG 분석과 맞춤형 액션 플랜을 제안합니다.</div>
        </div>
        """, unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 28px; margin-bottom: 10px;">🔍</div>
            <div style="color: #3b82f6; font-weight: 700; font-size: 16px; margin-bottom: 6px;">검색 데이터 다차원 분석</div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">쇼핑, 블로그, 카페, 뉴스 검색 데이터를 수집하고 다각도로 분석합니다.</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 28px; margin-bottom: 10px;">🔑</div>
            <div style="color: #f59e0b; font-weight: 700; font-size: 16px; margin-bottom: 6px;">API 설정 방법</div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">왼쪽 사이드바 하단의 NAVER API 설정에 Client ID와 Secret을 입력하세요.</div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# API 키 누락 예외 처리
if menu != "📦 내 쇼핑몰 상품 진단" and (not client_id or not client_secret):
    st.info("👈 왼쪽 사이드바 하단의 **NAVER API 설정**에서 Client ID와 Client Secret을 먼저 입력해 주세요.")
    st.stop()

# 5. 각 페이지별 대시보드 구현
if menu == "📈 검색어 트렌드 분석":
    st.markdown("### 🔍 검색어 트렌드 조건 설정")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        keywords_input = st.text_input("검색어 입력 (쉼표 ','로 여러 개 구분)", value="삼성전자, SK하이닉스, 현대자동차", help="트렌드를 비교 분석할 검색어들을 쉼표로 구분하여 최대 5개까지 입력하세요.")
    with col2:
        time_unit = st.selectbox("구간 단위", ["date", "week", "month"], index=0, format_func=lambda x: {"date": "일간", "week": "주간", "month": "월간"}[x])
        
    col3, col4, col5 = st.columns(3)
    with col3:
        start_date = st.date_input("시작일", value=datetime.now() - timedelta(days=90), min_value=datetime(2016, 1, 1))
    with col4:
        end_date = st.date_input("종료일", value=datetime.now())
    with col5:
        device = st.selectbox("기기 필터", ["", "pc", "mo"], format_func=lambda x: {"": "전체 기기", "pc": "PC", "mo": "모바일"}[x])
        
    col6, col7 = st.columns(2)
    with col6:
        gender = st.selectbox("성별 필터", ["", "f", "m"], format_func=lambda x: {"": "전체 성별", "f": "여성", "m": "남성"}[x])
    with col7:
        ages_options = {
            "1": "0~12세", "2": "13~18세", "3": "19~24세", "4": "25~29세", "5": "30~34세",
            "6": "35~39세", "7": "40~44세", "8": "45~49세", "9": "50~54세", "10": "55~59세", "11": "60세 이상"
        }
        ages = st.multiselect("연령대 필터 (선택 안 하면 전체)", options=list(ages_options.keys()), format_func=lambda x: ages_options[x])

    keywords_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
    
    if len(keywords_list) > 5:
        st.error("⚠️ 검색어는 최대 5개까지만 비교 가능합니다. 입력 개수를 줄여주세요.")
        st.stop()
        
    if st.button("트렌드 데이터 수집 및 분석 실행", type="primary"):
        if not keywords_list:
            st.warning("검색어를 입력해 주세요.")
        else:
            with st.spinner("네이버 데이터랩 트렌드 데이터 수집 중..."):
                try:
                    data = cached_search_trend(
                        client_id, client_secret, keywords_list,
                        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
                        time_unit, device, gender, ages
                    )
                    
                    results = data.get("results", [])
                    if not results or not results[0].get("data"):
                        st.warning("조회된 결과가 없습니다. 조건을 확인해 주세요.")
                    else:
                        df_list = []
                        for group in results:
                            title = group.get("title")
                            g_data = group.get("data", [])
                            temp_df = pd.DataFrame(g_data)
                            if not temp_df.empty:
                                temp_df["ratio"] = temp_df["ratio"].astype(float)
                                temp_df["period"] = pd.to_datetime(temp_df["period"])
                                temp_df["keyword"] = title
                                df_list.append(temp_df)
                        
                        df_all = pd.concat(df_list, ignore_index=True)
                        
                        # 1. 기술 통계치 산출 및 KPI 카드 배치
                        st.markdown("### 📊 주요 지표 요약 (KPI)")
                        kpi_cols = st.columns(len(results))
                        
                        for i, group in enumerate(results):
                            title = group.get("title")
                            group_df = df_all[df_all["keyword"] == title]
                            
                            if not group_df.empty:
                                mean_val = group_df["ratio"].mean()
                                max_val = group_df["ratio"].max()
                                max_date = group_df.loc[group_df["ratio"].idxmax(), "period"].strftime("%Y-%m-%d")
                                
                                colors = ["text-green", "text-blue", "text-purple", "text-green", "text-blue"]
                                with kpi_cols[i]:
                                    make_card(
                                        f"✨ {title} 평균지표", 
                                        f"{mean_val:.2f}%", 
                                        f"최대치: {max_val:.2f}% ({max_date})",
                                        color_class=colors[i % len(colors)]
                                    )
                        
                        # 2. 트렌드 차트 시각화
                        st.markdown("### 📈 기간별 검색 트렌드 추이")
                        fig = px.line(
                            df_all, x="period", y="ratio", color="keyword",
                            labels={"period": "날짜", "ratio": "상대적 검색량 (%)", "keyword": "검색어"},
                            title="네이버 통합검색 내 검색어 트렌드 추이 (가장 높은 날을 100으로 기준)",
                            template="plotly_dark"
                        )
                        fig.update_layout(
                            hovermode="x unified",
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font_family="Outfit, Noto Sans KR"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 3. 분포 요약 분석 (기술통계 고도화: 중앙값, 왜도, 첨도, 변동계수 추가)
                        st.markdown("### 📊 검색량 분포 요약 및 통계적 비대칭성 분석 (EDA)")
                        stat_df = df_all.groupby("keyword")["ratio"].describe().reset_index()
                        
                        # 왜도, 첨도, 변동계수(CV) 계산
                        stats_extra = df_all.groupby("keyword")["ratio"].agg(
                            skew="skew",
                            kurtosis=lambda x: x.kurtosis(),
                            cv=lambda x: x.std() / x.mean() if x.mean() != 0 else 0
                        ).reset_index()
                        
                        stat_df = stat_df.merge(stats_extra, on="keyword")
                        stat_df.columns = ["검색어", "데이터 수", "평균", "표준편차", "최소값", "25%", "중앙값(50%)", "75%", "최대값", "왜도 (Skewness)", "첨도 (Kurtosis)", "변동계수 (CV)"]
                        
                        st.dataframe(
                            stat_df.style.background_gradient(cmap="Blues", subset=["평균", "최대값"])
                            .format({"평균": "{:.2f}", "표준편차": "{:.2f}", "왜도 (Skewness)": "{:.2f}", "첨도 (Kurtosis)": "{:.2f}", "변동계수 (CV)": "{:.2f}"}),
                            use_container_width=True
                        )
                        
                        # 통계 설명 가이드 추가
                        with st.expander("💡 통계 지표 해석 가이드"):
                            st.markdown("""
                            - **왜도 (Skewness)**: 분포의 비대칭 정도를 나타냅니다. 0에 가까울수록 좌우 대칭이며, 양수(+) 값이 크면 왼쪽으로 치우치고 오른쪽 꼬리가 긴 형태(급격한 일시적 검색 폭증 현상)를 의미합니다.
                            - **첨도 (Kurtosis)**: 분포의 뾰족한 정도를 나타냅니다. 값이 클수록 분포가 중앙에 몰려 있고 이상치(검색 급증일)가 빈번히 발생했음을 의미합니다.
                            - **변동계수 (CV)**: 표준편차를 평균으로 나눈 값으로, 값이 클수록 기간 내 검색 강도의 기복이 심하고 작을수록 꾸준한 검색 흐름을 보였음을 뜻합니다.
                            """)
                        
                        # 데이터 다운로드
                        csv = df_all.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 CSV 파일로 검색 트렌드 데이터 다운로드",
                            data=csv,
                            file_name=f"naver_search_trend_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"데이터 수집 중 오류가 발생했습니다: {e}")

elif menu == "🛍️ 쇼핑 트렌드 분석":
    st.markdown("### 🛍️ 쇼핑 카테고리 클릭 트렌드 설정")
    
    # 세션 상태에 선택된 카테고리 목록 초기화
    if "selected_shopping_categories" not in st.session_state:
        st.session_state["selected_shopping_categories"] = [
            {"name": "패션의류", "id": "50000000"},
            {"name": "디지털/가전", "id": "50000003"}
        ]
        
    st.markdown("#### 🔍 비교할 카테고리 추가")
    
    input_mode = st.radio("카테고리 선택 방식", ["트리 구조 선택", "카테고리 ID 직접 입력"], horizontal=True)
    
    target_name = ""
    target_id = ""
    
    if input_mode == "트리 구조 선택":
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        
        # 1차 카테고리
        with col_c1:
            cat1_list = list(shopping_categories.SHOPPING_CATEGORIES.keys())
            selected_cat1 = st.selectbox("1차 카테고리", cat1_list)
            cat1_data = shopping_categories.SHOPPING_CATEGORIES[selected_cat1]
            target_name = selected_cat1
            target_id = cat1_data["id"]
            
        # 2차 카테고리
        with col_c2:
            cat2_data = cat1_data.get("sub", {})
            if cat2_data:
                cat2_list = ["선택 안 함"] + list(cat2_data.keys())
                selected_cat2 = st.selectbox("2차 카테고리", cat2_list)
                if selected_cat2 != "선택 안 함":
                    cat2_info = cat2_data[selected_cat2]
                    target_name = selected_cat2
                    target_id = cat2_info["id"]
                    
                    # 3차 카테고리
                    with col_c3:
                        cat3_data = cat2_info.get("sub", {})
                        if cat3_data:
                            cat3_list = ["선택 안 함"] + list(cat3_data.keys())
                            selected_cat3 = st.selectbox("3차 카테고리", cat3_list)
                            if selected_cat3 != "선택 안 함":
                                cat3_info = cat3_data[selected_cat3]
                                if isinstance(cat3_info, dict):
                                    target_name = selected_cat3
                                    target_id = cat3_info["id"]
                                    
                                    # 4차 카테고리
                                    with col_c4:
                                        cat4_data = cat3_info.get("sub", {})
                                        if cat4_data:
                                            cat4_list = ["선택 안 함"] + list(cat4_data.keys())
                                            selected_cat4 = st.selectbox("4차 카테고리", cat4_list)
                                            if selected_cat4 != "선택 안 함":
                                                cat4_info = cat4_data[selected_cat4]
                                                target_name = selected_cat4
                                                target_id = cat4_info
                                        else:
                                            st.selectbox("4차 카테고리", ["하위 없음"], disabled=True)
                                else:
                                    target_name = selected_cat3
                                    target_id = cat3_info
                                    with col_c4:
                                        st.selectbox("4차 카테고리", ["하위 없음"], disabled=True)
                        else:
                            st.selectbox("3차 카테고리", ["하위 없음"], disabled=True)
                            with col_c4:
                                st.selectbox("4차 카테고리", ["하위 없음"], disabled=True)
            else:
                st.selectbox("2차 카테고리", ["하위 없음"], disabled=True)
                with col_c3:
                    st.selectbox("3차 카테고리", ["하위 없음"], disabled=True)
                with col_c4:
                    st.selectbox("4차 카테고리", ["하위 없음"], disabled=True)
                    
    else:  # 직접 입력
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            custom_name = st.text_input("카테고리명 입력 (예: 여성 재킷)", placeholder="비교할 카테고리 이름을 입력하세요.")
        with col_in2:
            custom_id = st.text_input("카테고리 ID 입력 (예: 50000813)", placeholder="네이버 쇼핑 카테고리 ID 8자리를 입력하세요.")
            
        if custom_name and custom_id:
            target_name = custom_name.strip()
            target_id = custom_id.strip()

    # 카테고리 추가 버튼
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("➕ 비교 목록에 추가", use_container_width=True):
            if not target_name or not target_id:
                st.warning("추가할 카테고리를 선택하거나 입력해 주세요.")
            else:
                exists = any(c["id"] == target_id for c in st.session_state["selected_shopping_categories"])
                if exists:
                    st.warning("이미 추가된 카테고리입니다.")
                else:
                    st.session_state["selected_shopping_categories"].append({
                        "name": target_name,
                        "id": target_id
                    })
                    st.success(f"'{target_name}'({target_id}) 카테고리가 추가되었습니다.")
                    st.rerun()

    # 현재 추가된 카테고리 리스트 표시 및 삭제 기능
    st.markdown("#### 📋 현재 선택된 비교 대상")
    if not st.session_state["selected_shopping_categories"]:
        st.info("비교 대상 카테고리가 없습니다. 상단에서 카테고리를 선택해 추가해 주세요.")
    else:
        for idx, cat in enumerate(st.session_state["selected_shopping_categories"]):
            c_name, c_id = cat["name"], cat["id"]
            col_label, col_del = st.columns([5, 1])
            with col_label:
                st.markdown(f"🏷️ **{c_name}** `(ID: {c_id})`")
            with col_del:
                if st.button("삭제", key=f"del_{idx}_{c_id}", type="secondary"):
                    st.session_state["selected_shopping_categories"].pop(idx)
                    st.rerun()

    st.markdown("---")
    st.markdown("#### 📅 기타 검색 조건")

    col1, col2, col3 = st.columns(3)
    with col1:
        time_unit = st.selectbox("구간 단위", ["date", "week", "month"], index=0, format_func=lambda x: {"date": "일간", "week": "주간", "month": "월간"}[x])
    with col2:
        start_date = st.date_input("시작일", value=datetime.now() - timedelta(days=90))
    with col3:
        end_date = st.date_input("종료일", value=datetime.now())
        
    col4, col5, col6 = st.columns(3)
    with col4:
        device = st.selectbox("기기 필터", ["", "pc", "mo"], format_func=lambda x: {"": "전체 기기", "pc": "PC", "mo": "모바일"}[x])
    with col5:
        gender = st.selectbox("성별 필터", ["", "f", "m"], format_func=lambda x: {"": "전체 성별", "f": "여성", "m": "남성"}[x])
    with col6:
        ages = st.multiselect("연령대 필터 (선택 안 하면 전체)", options=["10", "20", "30", "40", "50", "60"])

    # Initialize session state for shopping trends if they do not exist
    if "shopping_run" not in st.session_state:
        st.session_state["shopping_run"] = False
    if "shopping_df_all" not in st.session_state:
        st.session_state["shopping_df_all"] = None
    if "completed_actions" not in st.session_state:
        st.session_state["completed_actions"] = {}

    if st.button("쇼핑 트렌드 분석 실행", type="primary"):
        if not st.session_state["selected_shopping_categories"]:
            st.warning("최소 하나의 쇼핑 카테고리를 비교 목록에 추가해 주세요.")
        else:
            with st.spinner("네이버 쇼핑인사이트 데이터 조회 중..."):
                try:
                    df_list = []
                    ages_mapped = []
                    ages_map = {"10": "2", "20": "3", "30": "5", "40": "7", "50": "9", "60": "11"}
                    for a in ages:
                        if a in ages_map:
                            ages_mapped.append(ages_map[a])
                            
                    for cat in st.session_state["selected_shopping_categories"]:
                        cat_name = cat["name"]
                        cat_id = cat["id"]
                        data = cached_shopping_insight(
                            client_id, client_secret, cat_id, cat_name,
                            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
                            time_unit, device, gender, ages_mapped
                        )
                        
                        results = data.get("results", [])
                        if results and results[0].get("data"):
                            g_data = results[0].get("data", [])
                            df = pd.DataFrame(g_data)
                            df["ratio"] = df["ratio"].astype(float)
                            df["period"] = pd.to_datetime(df["period"])
                            df["category"] = cat_name
                            df_list.append(df)
                    
                    if not df_list:
                        st.warning("조회된 데이터가 없습니다. 카테고리 또는 기간 설정을 확인해 주세요.")
                        st.session_state["shopping_df_all"] = None
                        st.session_state["shopping_run"] = False
                    else:
                        df_all = pd.concat(df_list, ignore_index=True)
                        st.session_state["shopping_df_all"] = df_all
                        st.session_state["shopping_run"] = True
                        st.rerun()
                except Exception as e:
                    err_msg = str(e)
                    st.error(f"🚨 쇼핑 트렌드 데이터를 불러오지 못했습니다: {err_msg}")
                    st.session_state["shopping_df_all"] = None
                    st.session_state["shopping_run"] = False

    if st.session_state.get("shopping_run", False) and st.session_state.get("shopping_df_all") is not None:
        df_all = st.session_state["shopping_df_all"]
        try:
            # 탭 인터페이스 구성
            tab1, tab2, tab3 = st.tabs(["📈 클릭 트렌드 & 기본 통계", "👥 성별/연령 및 매출액 추이", "🏆 개별 상품 랭킹 보드"])
            
            with tab1:
                # KPI 카드 배치
                st.markdown("### 🛍️ 카테고리별 트렌드 지표 요약")
                kpi_cols = st.columns(len(st.session_state["selected_shopping_categories"]))
                for i, cat in enumerate(st.session_state["selected_shopping_categories"]):
                    cat_name = cat["name"]
                    cat_df = df_all[df_all["category"] == cat_name]
                    if not cat_df.empty:
                        mean_val = cat_df["ratio"].mean()
                        max_row = cat_df.loc[cat_df["ratio"].idxmax()]
                        colors = ["text-green", "text-blue", "text-purple", "text-green", "text-blue"]
                        with kpi_cols[i]:
                            make_card(
                                f"🛍️ {cat_name} 평균 클릭지표", 
                                f"{mean_val:.2f}%", 
                                f"최대치: {max_row['ratio']:.2f}% ({max_row['period'].strftime('%Y-%m-%d')})",
                                color_class=colors[i % len(colors)]
                            )
                    
                # 트렌드 시각화
                st.markdown("### 📈 카테고리별 쇼핑 클릭 트렌드 추이 비교")
                fig = px.line(
                    df_all, x="period", y="ratio", color="category",
                    labels={"period": "날짜", "ratio": "클릭 비율 (%)", "category": "카테고리"},
                    title="선택한 쇼핑 분야별 상대적 클릭량 추이 (가장 높은 시점 = 100)",
                    template="plotly_dark"
                )
                fig.update_layout(
                    hovermode="x unified",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 상세 기술통계 테이블
                st.markdown("### 📊 카테고리별 세부 기술통계 및 분석")
                stat_df = df_all.groupby("category")["ratio"].describe().reset_index()
                
                # 왜도, 첨도, 변동계수 계산
                stats_extra = df_all.groupby("category")["ratio"].agg(
                    skew="skew",
                    kurtosis=lambda x: x.kurtosis(),
                    cv=lambda x: x.std() / x.mean() if x.mean() != 0 else 0
                ).reset_index()
                
                stat_df = stat_df.merge(stats_extra, on="category")
                stat_df.columns = ["카테고리명", "데이터 수", "평균", "표준편차", "최소값", "25%", "중앙값(50%)", "75%", "최대값", "왜도 (Skewness)", "첨도 (Kurtosis)", "변동계수 (CV)"]
                
                st.dataframe(
                    stat_df.style.background_gradient(cmap="BuGn", subset=["평균", "최대값"])
                    .format({"평균": "{:.2f}", "표준편차": "{:.2f}", "왜도 (Skewness)": "{:.2f}", "첨도 (Kurtosis)": "{:.2f}", "변동계수 (CV)": "{:.2f}"}),
                    use_container_width=True
                )
                
                # CSV 다운로드
                csv = df_all.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 CSV 파일로 쇼핑 트렌드 데이터 다운로드",
                    data=csv,
                    file_name=f"naver_shopping_trend_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
            with tab2:
                st.markdown("### 👥 카테고리별 성별 및 연령대 클릭 분포 분석")
                
                for cat in st.session_state["selected_shopping_categories"]:
                    cat_name = cat["name"]
                    cat_id = cat["id"]
                    
                    st.markdown(f"#### 🏷️ {cat_name} 인구통계학적 특성")
                    demo = generate_mock_demographics(cat_name, cat_id)
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        # 성별 분포 파이 차트
                        df_gender = pd.DataFrame(list(demo["gender"].items()), columns=["성별", "비율"])
                        fig_gender = px.pie(
                            df_gender, values="비율", names="성별",
                            title=f"{cat_name} 성별 관심도 분포",
                            color="성별",
                            color_discrete_map={"여성": "#ec4899", "남성": "#3b82f6"},
                            hole=0.4,
                            template="plotly_dark"
                        )
                        fig_gender.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_gender, use_container_width=True)
                        
                    with col_d2:
                        # 연령대 분포 바 차트
                        df_age = pd.DataFrame(list(demo["age"].items()), columns=["연령대", "비율"])
                        fig_age = px.bar(
                            df_age, x="연령대", y="비율",
                            title=f"{cat_name} 연령대별 관심도 분포",
                            color="연령대",
                            color_discrete_sequence=px.colors.sequential.Sunsetdark,
                            template="plotly_dark"
                        )
                        fig_age.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                        st.plotly_chart(fig_age, use_container_width=True)
                        
                # 매출 추이 시각화
                st.markdown("### 💰 카테고리별 일일 추정 매출액 추이")
                sales_list = []
                for cat in st.session_state["selected_shopping_categories"]:
                    cat_name = cat["name"]
                    cat_id = cat["id"]
                    cat_df = df_all[df_all["category"] == cat_name]
                    
                    # 가상의 평균단가 설정
                    if "패션" in cat_name or "의류" in cat_name:
                        avg_price = 55000
                    elif "디지털" in cat_name or "가전" in cat_name:
                        avg_price = 450000
                    elif "가구" in cat_name or "인테리어" in cat_name or "수납" in cat_name:
                        avg_price = 120000
                    else:
                        avg_price = 35000
                        
                    df_sales = generate_mock_sales_trend(cat_df, avg_price)
                    sales_list.append(df_sales)
                    
                if sales_list:
                    df_sales_all = pd.concat(sales_list, ignore_index=True)
                    fig_sales = px.line(
                        df_sales_all, x="period", y="추정 매출액", color="category",
                        labels={"period": "날짜", "추정 매출액": "추정 매출액 (원)", "category": "카테고리"},
                        title="일일 추정 매출액 변동 추이 (요일별 가중치 및 단가 반영)",
                        template="plotly_dark"
                    )
                    fig_sales.update_layout(
                        hovermode="x unified",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                    fig_sales.update_yaxes(tickformat=",d")
                    st.plotly_chart(fig_sales, use_container_width=True)
                    
            with tab3:
                st.markdown("### 🏆 카테고리별 개별 상품 랭킹 보드")
                
                # 비교 대상 카테고리 중 하나 선택
                cat_names = [cat["name"] for cat in st.session_state["selected_shopping_categories"]]
                selected_rank_cat_name = st.selectbox("랭킹 보드를 조회할 카테고리를 선택하세요:", cat_names, key="rank_cat_select")
                
                # 선택한 카테고리의 정보 찾기
                selected_cat_info = next(c for c in st.session_state["selected_shopping_categories"] if c["name"] == selected_rank_cat_name)
                selected_cat_id = selected_cat_info["id"]
                
                # 상품 데이터 로드 (시뮬레이션 데이터)
                df_products = generate_mock_products(selected_rank_cat_name, selected_cat_id)
                
                # 1. 포지셔닝 진단 연산 (상위/하위 백분위 및 평균 비교)
                q85_clicks = df_products["클릭수"].quantile(0.85)
                q80_clicks = df_products["클릭수"].quantile(0.80)
                q30_cvr = df_products["구매전환율 (%)"].quantile(0.30)
                avg_cvr = df_products["구매전환율 (%)"].mean()
                median_clicks = df_products["클릭수"].median()
                median_cvr = df_products["구매전환율 (%)"].median()
                
                def get_positioning(row):
                    clicks = row["클릭수"]
                    cvr = row["구매전환율 (%)"]
                    if clicks >= q85_clicks and cvr < avg_cvr:
                        return "노출 과다"
                    elif clicks >= q80_clicks and cvr < q30_cvr:
                        return "개선 필요"
                    elif clicks >= median_clicks and cvr >= median_cvr:
                        return "스타"
                    elif clicks < median_clicks and cvr >= median_cvr:
                        return "성장 기회"
                    else:
                        return "유지 관리"
                
                df_products["포지셔닝"] = df_products.apply(get_positioning, axis=1)
                
                over_exposed_count = int((df_products["포지셔닝"] == "노출 과다").sum())
                underperforming_count = int((df_products["포지셔닝"] == "개선 필요").sum())
                star_growth_count = int(((df_products["포지셔닝"] == "스타") | (df_products["포지셔닝"] == "성장 기회")).sum())
                
                # 액션 플랜 정의 및 상태 트래킹
                action_items = [
                    f"[{selected_rank_cat_name}] 노출 과다 상품 상세 페이지 이미지 고도화 및 후기 상단 배치",
                    f"[{selected_rank_cat_name}] 개선 필요 상품 가격 할인 프로모션 또는 쿠폰 발행",
                    f"[{selected_rank_cat_name}] 스타 상품 광고 입찰가 상향 및 노출 지면 확대",
                    f"[{selected_rank_cat_name}] 성장 기회 상품 SNS 체험단 모집 및 인플루언서 협찬 진행",
                    f"[{selected_rank_cat_name}] 경쟁사 가격 동향 분석 및 스마트스토어 즉시 할인 설정"
                ]
                
                checked_count = sum(1 for item in action_items if st.session_state["completed_actions"].get(item, False))
                total_count = len(action_items)
                pending_count = total_count - checked_count
                completion_rate = (checked_count / total_count) * 100
                
                # 독립된 상단 메트릭스 카드 배치
                col_score1, col_score2, col_score3, col_score4 = st.columns(4)
                with col_score1:
                    make_card("🚨 노출 과다 상품 수", f"{over_exposed_count}개", "클릭수 상위 15% & CVR 평균 미만", "text-red")
                with col_score2:
                    make_card("⚠️ 개선 필요 상품 수", f"{underperforming_count}개", "클릭수 상위 20% & CVR 하위 30%", "text-orange")
                with col_score3:
                    make_card("📋 주간 보류 액션", f"{pending_count}개", f"진행률: {completion_rate:.0f}% ({checked_count}/{total_count})", "text-blue")
                with col_score4:
                    make_card("🏆 스타 & 성장 상품 수", f"{star_growth_count}개", "성장성 양호 및 핵심 주력 상품", "text-green")
                
                st.markdown("---")
                
                # 반도넛 게이지 차트 & 액션 플랜 체크리스트 배치
                col_gauge, col_checklist = st.columns([2, 3])
                
                with col_gauge:
                    st.markdown("#### 📈 액션 플랜 달성률")
                    fig_gauge = go.Figure(data=[go.Pie(
                        values=[completion_rate, 100 - completion_rate, 100],
                        labels=["완료", "미완료", "hidden"],
                        hole=0.7,
                        marker=dict(colors=["#10b981", "#374151", "rgba(0,0,0,0)"]),
                        hoverinfo="label+value" if completion_rate > 0 else "none",
                        textinfo="none",
                        sort=False,
                        rotation=270
                    )])
                    fig_gauge.update_layout(
                        showlegend=False,
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=240,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        annotations=[
                            dict(
                                text=f"<span style='font-size:26px; font-weight:bold; color:#10b981;'>{completion_rate:.0f}%</span><br><span style='font-size:12px; color:#9ca3af;'>달성률</span>",
                                x=0.5, y=0.55,
                                showarrow=False,
                                align="center"
                            )
                        ]
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                with col_checklist:
                    st.markdown("#### 🎯 주간 마케팅 권장 액션 플랜")
                    for idx, item in enumerate(action_items):
                        is_checked = st.checkbox(
                            item,
                            value=st.session_state["completed_actions"].get(item, False),
                            key=f"chk_{selected_cat_id}_{idx}"
                        )
                        if is_checked != st.session_state["completed_actions"].get(item, False):
                            st.session_state["completed_actions"][item] = is_checked
                            st.rerun()
                            
                st.markdown("---")
                
                st.markdown(f"#### 🥇 {selected_rank_cat_name} 상품별 실적 및 진단 순위")
                
                # 랭킹 정렬 기준 선택
                sort_by = st.radio("랭킹 기준 설정", ["추정 매출액 순", "클릭수 순", "구매전환율 순"], horizontal=True, key="rank_sort_by")
                
                if sort_by == "추정 매출액 순":
                    df_sorted = df_products.sort_values(by="추정 매출액 (원)", ascending=False).reset_index(drop=True)
                elif sort_by == "클릭수 순":
                    df_sorted = df_products.sort_values(by="클릭수", ascending=False).reset_index(drop=True)
                else:
                    df_sorted = df_products.sort_values(by="구매전환율 (%)", ascending=False).reset_index(drop=True)
                    
                df_sorted.index = df_sorted.index + 1
                df_sorted.index.name = "순위"
                
                # 테이블 컬럼 순서 재배치 및 출력
                df_display_sorted = df_sorted[["상품명", "포지셔닝", "클릭수", "구매전환율 (%)", "추정 구매수", "평균 단가 (원)", "추정 매출액 (원)"]]
                st.dataframe(
                    df_display_sorted.style.background_gradient(cmap="Oranges", subset=["클릭수", "추정 매출액 (원)"])
                    .format({"구매전환율 (%)": "{:.2f}%", "평균 단가 (원)": "{:,.0f}원", "추정 매출액 (원)": "{:,.0f}원", "클릭수": "{:,.0f}", "추정 구매수": "{:,.0f}"}),
                    use_container_width=True
                )
                
                # 시각화 차트 배치 (가로 배치)
                col_bar, col_scatter = st.columns(2)
                
                with col_bar:
                    df_sorted_for_bar = df_products.copy().sort_values(by="클릭수", ascending=False)
                    fig_bar = px.bar(
                        df_sorted_for_bar, x="상품명", y="클릭수", color="포지셔닝",
                        color_discrete_map={
                            "개선 필요": "#ef4444",
                            "노출 과다": "#f97316",
                            "스타": "#10b981",
                            "성장 기회": "#3b82f6",
                            "유지 관리": "#6b7280"
                        },
                        category_orders={"포지셔닝": ["스타", "성장 기회", "노출 과다", "개선 필요", "유지 관리"]},
                        title=f"📊 {selected_rank_cat_name} 상품별 유입(클릭수) 및 포지셔닝 비교",
                        labels={"클릭수": "클릭수 (회)", "상품명": "상품명", "포지셔닝": "상태 포지셔닝"},
                        template="plotly_dark"
                    )
                    fig_bar.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_tickangle=-45
                    )
                    fig_bar.update_traces(marker_cornerradius=12)
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                with col_scatter:
                    fig_scatter = px.scatter(
                        df_products, x="클릭수", y="구매전환율 (%)",
                        size="추정 매출액 (원)", color="포지셔닝",
                        color_discrete_map={
                            "개선 필요": "#ef4444",
                            "노출 과다": "#f97316",
                            "스타": "#10b981",
                            "성장 기회": "#3b82f6",
                            "유지 관리": "#6b7280"
                        },
                        text="상품명",
                        title=f"🎯 {selected_rank_cat_name} 상품별 마케팅 포지셔닝 맵 (원 크기 = 매출액)",
                        labels={"클릭수": "클릭수 (유입량)", "구매전환율 (%)": "구매전환율 (%)", "포지셔닝": "포지셔닝"},
                        template="plotly_dark"
                    )
                    fig_scatter.update_traces(textposition='top center')
                    fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
                # 보고서 내보내기 다운로드 버튼
                st.markdown("### 📥 맞춤형 종합 진단 보고서 내보내기")
                
                report_md = f"""# 🛍️ 네이버 쇼핑 트렌드 상품 진단 보고서

- **진단 대상 카테고리**: {selected_rank_cat_name} (ID: {selected_cat_id})
- **진단 기준 일자**: {datetime.now().strftime('%Y-%m-%d')}
- **총 분석 상품 수**: {len(df_products)}개

## 📊 상품 포지셔닝 현황
- 🏆 **스타 상품**: {', '.join(df_products[df_products['포지셔닝'] == '스타']['상품명'].tolist()) or '없음'}
- 📈 **성장 기회 상품**: {', '.join(df_products[df_products['포지셔닝'] == '성장 기회']['상품명'].tolist()) or '없음'}
- 🚨 **노출 과다 상품 (개선 필요)**: {', '.join(df_products[df_products['포지셔닝'] == '노출 과다']['상품명'].tolist()) or '없음'}
- ⚠️ **개선 필요 상품 (전환율 저조)**: {', '.join(df_products[df_products['포지셔닝'] == '개선 필요']['상품명'].tolist()) or '없음'}
- ⚙️ **유지 관리 상품**: {', '.join(df_products[df_products['포지셔닝'] == '유지 관리']['상품명'].tolist()) or '없음'}

## 🔍 상품별 세일즈/마케팅 지표
| 순위 | 상품명 | 포지셔닝 | 클릭수 | 구매전환율 (%) | 추정 매출액 (원) |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
                for i, row in df_display_sorted.iterrows():
                    report_md += f"| {i} | {row['상품명']} | {row['포지셔닝']} | {row['클릭수']:,} | {row['구매전환율 (%)']:.2f}% | {row['추정 매출액 (원)']:,}원 |\n"
                    
                report_md += f"""
## 💡 맞춤형 마케팅 추천 액션
1. **노출 과다 상품 ({over_exposed_count}개)**
   - 상세페이지 이미지 고도화 및 고객 후기(리뷰)를 상단에 노출시켜 CVR을 개선해야 합니다.
   - 경쟁사 상품 대비 가격 경쟁력이 떨어질 수 있으므로, 즉시 할인 또는 쿠폰 혜택 적용을 권장합니다.

2. **개선 필요 상품 ({underperforming_count}개)**
   - 클릭수 대비 구매전환율이 매우 낮으므로 상품 매력도를 대폭 보완해야 합니다.
   - 가격 할인 프로모션을 실행하거나 1+1 구성 등 기획전을 연동하세요.

3. **스타 상품**
   - 검색 광고 및 쇼핑 검색 입찰가를 추가로 상향 조정하여 검색 노출 순위를 상위로 고정하십시오.
   - 외부 마케팅(SNS, 인플루언서 협찬)을 병행하여 유입 극대화를 추진합니다.

4. **성장 기회 상품**
   - 전환율은 매우 훌륭하므로 유입량(클릭수)만 늘려주면 매출이 급성장합니다.
   - 쇼핑 키워드 광고 집행을 적극 검토하십시오.
"""
                st.download_button(
                    label="📥 종합 진단 보고서 다운로드 (.md)",
                    data=report_md,
                    file_name=f"shopping_trend_report_{selected_rank_cat_name}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        except Exception as e:
            err_msg = str(e)
            st.error(f"🚨 쇼핑 트렌드 데이터를 불러오지 못했습니다: {err_msg}")
            if "024" in err_msg or "Authentication failed" in err_msg or "401" in err_msg:
                st.markdown("""
                <div style="background-color: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 20px; border-radius: 0 8px 8px 0; margin-top: 15px;">
                    <h4 style="color: #ef4444; margin-top: 0;">🔑 네이버 API 인증 실패 (오류 코드: 024) 해결 방법</h4>
                    <p style="font-size: 14px; line-height: 1.6;">네이버 오픈 API 설정 상 <b>데이터랩(쇼핑인사이트)</b> API 서비스가 활성화되지 않았을 때 발생하는 오류입니다. 아래 단계를 통해 즉시 해결할 수 있습니다.</p>
                    <ol style="font-size: 13.5px; line-height: 1.6; padding-left: 20px;">
                        <li>네이버 개발자 센터 (<a href="https://developers.naver.com/" target="_blank" style="color: #3b82f6; text-decoration: underline;">Naver Developers</a>)에 로그인합니다.</li>
                        <li>상단 메뉴의 <b>Application &gt; 내 애플리케이션</b>에서 대시보드에 사용 중인 애플리케이션을 선택합니다.</li>
                        <li><b>API 설정</b> 탭으로 이동합니다.</li>
                        <li><b>로그인 오픈 API 서비스 환경 / 비로그인 오픈 API 서비스 권한</b> 목록에서 <b>데이터랩(쇼핑인사이트)</b> 권한이 체크(추가)되어 있는지 확인하고, 추가되지 않았다면 이를 선택하여 <b>저장</b>을 누릅니다.</li>
                        <li>만약 권한이 제대로 들어가 있음에도 문제가 지속된다면, 사이드바에 입력하신 Client ID와 Client Secret 값이 공백 없이 올바르게 입력되었는지 확인해 주시기 바랍니다.</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)

elif menu == "📦 내 쇼핑몰 상품 진단":
    st.markdown("### 📦 내 쇼핑몰 상품 진단")
    st.markdown("""
    스마트스토어, 쿠팡, 카페24, 쇼피파이 등 다양한 쇼핑몰 플랫폼의 매출/성과 실적 엑셀(.xlsx) 또는 CSV 파일을 업로드하여 
    상품 성과 분석(BCG 포트폴리오, CVR 백분위 진단, 마케팅 액션 체크리스트)을 일괄 수행하고 보고서를 발행합니다.
    """)
    
    # 세션 상태 초기화
    if "diagnose_run" not in st.session_state:
        st.session_state["diagnose_run"] = False
    if "diagnose_df" not in st.session_state:
        st.session_state["diagnose_df"] = None
    if "diagnose_warnings" not in st.session_state:
        st.session_state["diagnose_warnings"] = []
    if "diagnose_actions" not in st.session_state:
        st.session_state["diagnose_actions"] = {}
    if "diagnose_last_filename" not in st.session_state:
        st.session_state["diagnose_last_filename"] = ""
        
    uploaded_file = st.file_uploader("쇼핑몰 상품 실적 데이터 파일 업로드 (Excel 또는 CSV)", type=["xlsx", "xls", "csv"])
    
    if uploaded_file is not None:
        # 파일이 변경되면 체크리스트 상태 자동 초기화
        if st.session_state["diagnose_last_filename"] != uploaded_file.name:
            st.session_state["diagnose_actions"] = {}
            st.session_state["diagnose_last_filename"] = uploaded_file.name
        try:
            # 1. 파일 포맷 파싱
            if uploaded_file.name.endswith('.csv'):
                try:
                    df_raw = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    df_raw = pd.read_csv(uploaded_file, encoding='cp949')
            else:
                df_raw = pd.read_excel(uploaded_file)
                
            raw_cols = [str(c).strip() for c in df_raw.columns]
            
            # 2. 플랫폼 프리셋 정의 및 헤더 자동 맵핑
            PLATFORM_PRESETS = {
                "Smartstore": {
                    "상품명": ["상품명", "물품명", "상품 이름", "Product Name"],
                    "상품ID": ["상품번호", "상품ID", "상품 번호", "Product ID"],
                    "클릭수": ["유입수", "클릭수", "조회수", "클릭", "Clicks", "Views"],
                    "구매수": ["결제수량", "구매수량", "구매수", "판매수량", "Sales Qty", "Purchases"],
                    "매출액": ["결제금액", "매출액", "판매금액", "매출", "Revenue", "Sales Amount"],
                    "구매전환율": ["구매전환율", "전환율", "구매전환율 (%)", "Conversion Rate"]
                },
                "Coupang": {
                    "상품명": ["등록상품명", "상품명", "노출상품명", "Coupang Product Name"],
                    "상품ID": ["등록상품ID", "노출상품ID", "옵션ID", "Coupang Product ID"],
                    "클릭수": ["클릭수", "조회수", "상세조회수", "Clicks"],
                    "구매수": ["결제수량", "구매수량", "판매수량", "주문수량", "Sales"],
                    "매출액": ["매출액", "결제금액", "판매금액", "Revenue"],
                    "구매전환율": ["구매전환율", "전환율", "CVR", "Conversion Rate"]
                },
                "Cafe24": {
                    "상품명": ["상품명", "Cafe24 Product Name"],
                    "상품ID": ["상품번호", "상품코드", "Cafe24 Product ID"],
                    "클릭수": ["조회수", "클릭수", "Hits", "Views"],
                    "구매수": ["주문수량", "구매수", "결제수량", "Sales Qty"],
                    "매출액": ["결제금액", "주문금액", "매출액", "Cafe24 Revenue"],
                    "구매전환율": ["구매전환율", "전환율", "Conversion Rate"]
                },
                "Shopify": {
                    "상품명": ["Product Title", "Title", "Product Name"],
                    "상품ID": ["Product ID", "Variant ID", "ID"],
                    "클릭수": ["Sessions", "Clicks", "Pageviews"],
                    "구매수": ["Orders", "Purchases", "Quantity"],
                    "매출액": ["Sales", "Revenue", "Total Sales"],
                    "구매전환율": ["Conversion Rate", "CVR", "Conversion %"]
                }
            }
            
            detected_mappings = {}
            for target_key in ["상품명", "상품ID", "클릭수", "구매수", "매출액", "구매전환율"]:
                matched_col = None
                for platform, preset in PLATFORM_PRESETS.items():
                    for alias in preset[target_key]:
                        for r_col in raw_cols:
                            if r_col.lower() == alias.lower():
                                matched_col = r_col
                                break
                        if matched_col: break
                    if matched_col: break
                    
                if not matched_col:
                    for r_col in raw_cols:
                        if target_key in r_col or r_col in target_key:
                            matched_col = r_col
                            break
                            
                detected_mappings[target_key] = matched_col
                
            missing_keys = [k for k, v in detected_mappings.items() if v is None]
            
            st.markdown("#### 🔍 업로드 파일 헤더 검증")
            user_mappings = detected_mappings.copy()
            
            if missing_keys:
                st.warning(f"⚠️ 일부 필수 컬럼을 자동으로 매핑하지 못했습니다. 아래에서 알맞은 컬럼을 수동 매핑해 주세요: {', '.join(missing_keys)}")
                col_m1, col_m2 = st.columns(2)
                for idx, key in enumerate(missing_keys):
                    target_col = col_m1 if idx % 2 == 0 else col_m2
                    with target_col:
                        user_mappings[key] = st.selectbox(
                            f"'{key}' 지표에 매칭할 열 선택",
                            options=["선택 안 함"] + raw_cols,
                            key=f"select_map_{key}"
                        )
            else:
                st.success("✅ 모든 필수 컬럼이 자동으로 매핑되었습니다.")
                with st.expander("⚙️ 자동 매핑 결과 확인 및 컬럼 매칭 수동 수정"):
                    col_m1, col_m2 = st.columns(2)
                    for idx, key in enumerate(["상품명", "상품ID", "클릭수", "구매수", "매출액", "구매전환율"]):
                        target_col = col_m1 if idx % 2 == 0 else col_m2
                        with target_col:
                            default_idx = raw_cols.index(detected_mappings[key]) if detected_mappings[key] in raw_cols else 0
                            user_mappings[key] = st.selectbox(
                                f"'{key}' 매칭 열",
                                options=raw_cols,
                                index=default_idx,
                                key=f"select_map_edit_{key}"
                            )
                            
            # 3. 데이터 가공 및 클렌징 (결측 컬럼 보정 및 예외 처리)
            df_cleaned = pd.DataFrame()
            warning_triggered = False
            warning_messages = []
            
            # 상품명 보정
            name_col = user_mappings.get("상품명")
            if name_col and name_col != "선택 안 함" and name_col in df_raw.columns:
                df_cleaned["상품명"] = df_raw[name_col].astype(str)
            else:
                df_cleaned["상품명"] = [f"미지정 상품 {i+1}" for i in range(len(df_raw))]
                warning_triggered = True
                warning_messages.append("상품명 컬럼이 지정되지 않아 임의의 상품명으로 대체되었습니다.")
                
            # 상품ID 보정
            id_col = user_mappings.get("상품ID")
            if id_col and id_col != "선택 안 함" and id_col in df_raw.columns:
                df_cleaned["상품ID"] = df_raw[id_col].astype(str)
            else:
                df_cleaned["상품ID"] = [f"P_{10000+i}" for i in range(len(df_raw))]
                warning_triggered = True
                warning_messages.append("상품ID 컬럼이 지정되지 않아 임의의 ID 코드로 대체되었습니다.")
                
            # 매출액 보정
            rev_col = user_mappings.get("매출액")
            if rev_col and rev_col != "선택 안 함" and rev_col in df_raw.columns:
                df_cleaned["추정 매출액 (원)"] = pd.to_numeric(df_raw[rev_col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0).astype(int)
            else:
                df_cleaned["추정 매출액 (원)"] = 0
                
            # 구매수 보정
            buy_col = user_mappings.get("구매수")
            if buy_col and buy_col != "선택 안 함" and buy_col in df_raw.columns:
                df_cleaned["추정 구매수"] = pd.to_numeric(df_raw[buy_col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0).astype(int)
            else:
                df_cleaned["추정 구매수"] = 0
                
            # 단가 산출
            avg_prices = []
            for idx, row in df_cleaned.iterrows():
                rev = row["추정 매출액 (원)"]
                buy = row["추정 구매수"]
                if rev > 0 and buy > 0:
                    avg_prices.append(int(rev / buy))
                elif rev > 0 and buy == 0:
                    avg_prices.append(35000)
                elif rev == 0 and buy > 0:
                    avg_prices.append(35000)
                else:
                    avg_prices.append(np.random.randint(15000, 85000))
            df_cleaned["평균 단가 (원)"] = avg_prices
            
            # 매출액 및 구매수 상호 역산 보완
            for idx, row in df_cleaned.iterrows():
                if row["추정 매출액 (원)"] == 0 and row["추정 구매수"] > 0:
                    df_cleaned.at[idx, "추정 매출액 (원)"] = row["추정 구매수"] * row["평균 단가 (원)"]
                elif row["추정 구매수"] == 0 and row["추정 매출액 (원)"] > 0:
                    df_cleaned.at[idx, "추정 구매수"] = max(1, int(row["추정 매출액 (원)"] / row["평균 단가 (원)"]))
                elif row["추정 매출액 (원)"] == 0 and row["추정 구매수"] == 0:
                    p_buy = np.random.randint(5, 120)
                    df_cleaned.at[idx, "추정 구매수"] = p_buy
                    df_cleaned.at[idx, "추정 매출액 (원)"] = p_buy * row["평균 단가 (원)"]
                    warning_triggered = True
                    
            if rev_col == "선택 안 함" or buy_col == "선택 안 함":
                warning_messages.append("매출액 또는 구매수량이 누락되어 가상 단가(35,000원 기준) 및 구매건수로 보정되었습니다.")
                
            # 클릭수 보정
            click_col = user_mappings.get("클릭수")
            if click_col and click_col != "선택 안 함" and click_col in df_raw.columns:
                df_cleaned["클릭수"] = pd.to_numeric(df_raw[click_col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0).astype(int)
            else:
                df_cleaned["클릭수"] = (df_cleaned["추정 구매수"] / 0.02).astype(int)
                warning_triggered = True
                warning_messages.append("클릭수(유입량) 컬럼이 누락되어 평균 구매전환율(2.0%) 기준으로 역산하여 보정되었습니다.")
                
            # 구매전환율 보정
            cvr_col = user_mappings.get("구매전환율")
            if cvr_col and cvr_col != "선택 안 함" and cvr_col in df_raw.columns:
                df_cleaned["구매전환율 (%)"] = pd.to_numeric(df_raw[cvr_col].astype(str).str.replace(r'[^\d.%]', '', regex=True), errors='coerce').fillna(0.0)
            else:
                cvr_vals = []
                for idx, row in df_cleaned.iterrows():
                    clicks = row["클릭수"]
                    buy = row["추정 구매수"]
                    if clicks > 0:
                        cvr_vals.append(round((buy / clicks) * 100, 2))
                    else:
                        cvr_vals.append(2.0)
                df_cleaned["구매전환율 (%)"] = cvr_vals
                if cvr_col == "선택 안 함":
                    warning_triggered = True
                    warning_messages.append("구매전환율 컬럼이 누락되어 클릭수 대비 구매수의 실제 수치로 자동 계산되었습니다.")
                    
            st.markdown("---")
            if st.button("🚀 내 쇼핑몰 상품 진단 실행", type="primary", use_container_width=True):
                st.session_state["diagnose_df"] = df_cleaned
                st.session_state["diagnose_run"] = True
                st.session_state["diagnose_warnings"] = warning_messages if warning_triggered else []
                st.rerun()
                
        except Exception as e:
            st.error(f"파일을 읽는 중 에러가 발생했습니다. 헤더 규격을 확인하세요: {e}")
            st.session_state["diagnose_run"] = False
            
    if st.session_state.get("diagnose_run", False) and st.session_state.get("diagnose_df") is not None:
        df_cleaned = st.session_state["diagnose_df"]
        warnings = st.session_state.get("diagnose_warnings", [])
        
        if warnings:
            st.warning("⚠️ **분석 모델 경고 (데이터 보정 알림)**\n" + "\n".join([f"- {msg}" for msg in warnings]))
            
        # 4. 3개 탭 구성
        tab_dashboard, tab_actions, tab_details = st.tabs(["🏠 종합 대시보드", "🎯 마케팅 액션 & 상세 진단", "📋 상품 데이터 상세 내역"])
        
        # 임계값 및 포지셔닝 진단 연산
        q85_clicks = df_cleaned["클릭수"].quantile(0.85)
        q80_clicks = df_cleaned["클릭수"].quantile(0.80)
        q30_cvr = df_cleaned["구매전환율 (%)"].quantile(0.30)
        avg_cvr = df_cleaned["구매전환율 (%)"].mean()
        median_clicks = df_cleaned["클릭수"].median()
        median_cvr = df_cleaned["구매전환율 (%)"].median()
        
        def get_positioning(row):
            clicks = row["클릭수"]
            cvr = row["구매전환율 (%)"]
            if clicks >= q85_clicks and cvr < avg_cvr:
                return "노출 과다"
            elif clicks >= q80_clicks and cvr < q30_cvr:
                return "개선 필요"
            elif clicks >= median_clicks and cvr >= median_cvr:
                return "스타"
            elif clicks < median_clicks and cvr >= median_cvr:
                return "성장 기회"
            else:
                return "유지 관리"
                
        df_cleaned["포지셔닝"] = df_cleaned.apply(get_positioning, axis=1)
        
        over_exposed_count = int((df_cleaned["포지셔닝"] == "노출 과다").sum())
        underperforming_count = int((df_cleaned["포지셔닝"] == "개선 필요").sum())
        star_growth_count = int(((df_cleaned["포지셔닝"] == "스타") | (df_cleaned["포지셔닝"] == "성장 기회")).sum())
        
        action_items = [
            "노출 과다 상품 상세 페이지 이미지 고도화 및 후기 상단 배치",
            "개선 필요 상품 가격 할인 프로모션 또는 쿠폰 발행",
            "스타 상품 광고 입찰가 상향 및 노출 지면 확대",
            "성장 기회 상품 SNS 체험단 모집 및 인플루언서 협찬 진행",
            "경쟁사 가격 동향 분석 및 즉시 할인 설정"
        ]
        
        checked_count = sum(1 for item in action_items if st.session_state["diagnose_actions"].get(item, False))
        total_count = len(action_items)
        pending_count = total_count - checked_count
        completion_rate = (checked_count / total_count) * 100
        
        # --- 1. 🏠 종합 대시보드 탭 ---
        with tab_dashboard:
            st.markdown("#### 📊 쇼핑몰 핵심 성과 지표 요약")
            
            # 지표 계산
            total_clicks = int(df_cleaned["클릭수"].sum())
            total_purchases = int(df_cleaned["추정 구매수"].sum())
            total_revenue = int(df_cleaned["추정 매출액 (원)"].sum())
            overall_cvr = (total_purchases / total_clicks) * 100 if total_clicks > 0 else df_cleaned["구매전환율 (%)"].mean()
            
            col_dash1, col_dash2, col_dash3, col_dash4 = st.columns(4)
            with col_dash1:
                make_card("🎯 총 유입수 (클릭)", f"{total_clicks:,}회", "전체 등록 상품 누적 클릭수", "text-blue")
            with col_dash2:
                make_card("🛍️ 총 구매 건수", f"{total_purchases:,}건", "전체 등록 상품 누적 주문건수", "text-purple")
            with col_dash3:
                make_card("💰 총 추정 매출액", f"{total_revenue:,}원", "전체 상품 매출액의 합산", "text-green")
            with col_dash4:
                make_card("📈 종합 구매전환율 (CVR)", f"{overall_cvr:.2f}%", "총 구매수 / 총 클릭수", "text-orange")
                
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                # 포지셔닝 분포 파이 차트
                pos_counts = df_cleaned["포지셔닝"].value_counts().reset_index()
                pos_counts.columns = ["포지셔닝", "상품수"]
                fig_pos_pie = px.pie(
                    pos_counts, values="상품수", names="포지셔닝",
                    title="🎯 내 쇼핑몰 상품 포지셔닝 분포 비중",
                    color="포지셔닝",
                    color_discrete_map={
                        "개선 필요": "#ef4444",
                        "노출 과다": "#f97316",
                        "스타": "#10b981",
                        "성장 기회": "#3b82f6",
                        "유지 관리": "#6b7280"
                    },
                    hole=0.4,
                    template="plotly_dark"
                )
                fig_pos_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_pos_pie, use_container_width=True)
                
            with col_chart2:
                # 매출 상위 10대 상품 가로 막대 그래프
                df_top10 = df_cleaned.sort_values(by="추정 매출액 (원)", ascending=True).tail(10)
                fig_top10 = px.bar(
                    df_top10, x="추정 매출액 (원)", y="상품명", color="포지셔닝",
                    color_discrete_map={
                        "개선 필요": "#ef4444",
                        "노출 과다": "#f97316",
                        "스타": "#10b981",
                        "성장 기회": "#3b82f6",
                        "유지 관리": "#6b7280"
                    },
                    orientation="h",
                    title="💰 상품 매출액 기여도 Top 10 (색상 = 포지셔닝)",
                    labels={"추정 매출액 (원)": "매출액 (원)", "상품명": "상품명"},
                    template="plotly_dark"
                )
                fig_top10.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                fig_top10.update_traces(marker_cornerradius=6)
                st.plotly_chart(fig_top10, use_container_width=True)
                
            st.markdown("---")
            
            # 비즈니스 진단 리포트 요약 카드
            st.markdown("#### 💡 비즈니스 핵심 진단 요약")
            
            star_prods = df_cleaned[df_cleaned["포지셔닝"] == "스타"]["상품명"].tolist()
            over_prods = df_cleaned[df_cleaned["포지셔닝"] == "노출 과다"]["상품명"].tolist()
            under_prods = df_cleaned[df_cleaned["포지셔닝"] == "개선 필요"]["상품명"].tolist()
            growth_prods = df_cleaned[df_cleaned["포지셔닝"] == "성장 기회"]["상품명"].tolist()
            
            def format_prod_list(prods):
                if not prods: return "없음"
                if len(prods) > 3:
                    return f"**{', '.join(prods[:3])}** 외 {len(prods)-3}개"
                return f"**{', '.join(prods)}**"
                
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px; margin-bottom: 15px;">
                <div style="font-size: 16px; line-height: 1.8;">
                    🏆 <b>핵심 캐시카우 (스타 상품)</b>: {format_prod_list(star_prods)}<br>
                    <span style="color: #94a3b8; font-size: 13.5px; margin-left: 20px;">➔ 유입수와 구매전환율이 모두 우수한 효자 상품군입니다. 마케팅 예산을 우선 배정하여 경쟁사 진입을 방지하세요.</span><br><br>
                    🚨 <b>광고 비효율 경보 (노출 과다 상품)</b>: {format_prod_list(over_prods)}<br>
                    <span style="color: #94a3b8; font-size: 13.5px; margin-left: 20px;">➔ 유입은 많으나 전환율이 평균 미만입니다. 상세페이지 개선, 리뷰 최적화 또는 쿠폰 혜택 제공이 시급합니다.</span><br><br>
                    ⚠️ <b>즉시 개선 요망 (개선 필요 상품)</b>: {format_prod_list(under_prods)}<br>
                    <span style="color: #94a3b8; font-size: 13.5px; margin-left: 20px;">➔ 유입 상위 20%에 속하나 전환율은 최하위 30% 미만인 상품입니다. 상품 옵션 구조, 가격 허들, 또는 이탈 요인을 점검하세요.</span><br><br>
                    📈 <b>성장 가능성 잠재주 (성장 기회 상품)</b>: {format_prod_list(growth_prods)}<br>
                    <span style="color: #94a3b8; font-size: 13.5px; margin-left: 20px;">➔ 전환선호도는 높으나 아직 검색 노출이나 유입이 부족합니다. 검색광고나 외부 SNS 홍보를 통해 유입량을 조금만 늘리면 매출이 극대화됩니다.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # --- 2. 🎯 마케팅 액션 & 상세 진단 탭 ---
        with tab_actions:
            # 상단 독자적인 스코어카드 배치
            col_score1, col_score2, col_score3, col_score4 = st.columns(4)
            with col_score1:
                make_card("🚨 노출 과다 상품 수", f"{over_exposed_count}개", "클릭수 상위 15% & CVR 평균 미만", "text-red")
            with col_score2:
                make_card("⚠️ 개선 필요 상품 수", f"{underperforming_count}개", "클릭수 상위 20% & CVR 하위 30%", "text-orange")
            with col_score3:
                make_card("📋 주간 보류 액션", f"{pending_count}개", f"진행률: {completion_rate:.0f}% ({checked_count}/{total_count})", "text-blue")
            with col_score4:
                make_card("🏆 스타 & 성장 상품 수", f"{star_growth_count}개", "고성과 및 핵심 주력 상품군", "text-green")
                
            st.markdown("---")
            
            # 액션 플랜 게이지 차트 & 체크박스 연동
            col_gauge, col_checklist = st.columns([2, 3])
            
            with col_gauge:
                st.markdown("#### 📈 액션 플랜 달성률")
                fig_gauge = go.Figure(data=[go.Pie(
                    values=[completion_rate, 100 - completion_rate, 100],
                    labels=["완료", "미완료", "hidden"],
                    hole=0.7,
                    marker=dict(colors=["#10b981", "#374151", "rgba(0,0,0,0)"]),
                    hoverinfo="label+value" if completion_rate > 0 else "none",
                    textinfo="none",
                    sort=False,
                    rotation=270
                )])
                fig_gauge.update_layout(
                    showlegend=False,
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=240,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    annotations=[
                        dict(
                            text=f"<span style='font-size:26px; font-weight:bold; color:#10b981;'>{completion_rate:.0f}%</span><br><span style='font-size:12px; color:#9ca3af;'>달성률</span>",
                            x=0.5, y=0.55,
                            showarrow=False,
                            align="center"
                        )
                    ]
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
            with col_checklist:
                st.markdown("#### 🎯 주간 마케팅 권장 액션 플랜")
                for idx, item in enumerate(action_items):
                    is_checked = st.checkbox(
                        item,
                        value=st.session_state["diagnose_actions"].get(item, False),
                        key=f"diag_chk_{idx}"
                    )
                    if is_checked != st.session_state["diagnose_actions"].get(item, False):
                        st.session_state["diagnose_actions"][item] = is_checked
                        st.rerun()
                
                st.markdown(" ")
                if st.button("🔄 액션 플랜 체크 상태 초기화", use_container_width=True):
                    st.session_state["diagnose_actions"] = {}
                    st.rerun()
                        
            st.markdown("---")
            
            # 시각화 배치 (Rounded Bar + Scatter 포지셔닝 맵)
            col_bar, col_scatter = st.columns(2)
            
            with col_bar:
                df_sorted_for_bar = df_cleaned.copy().sort_values(by="클릭수", ascending=False)
                fig_bar = px.bar(
                    df_sorted_for_bar, x="상품명", y="클릭수", color="포지셔닝",
                    color_discrete_map={
                        "개선 필요": "#ef4444",
                        "노출 과다": "#f97316",
                        "스타": "#10b981",
                        "성장 기회": "#3b82f6",
                        "유지 관리": "#6b7280"
                    },
                    category_orders={"포지셔닝": ["스타", "성장 기회", "노출 과다", "개선 필요", "유지 관리"]},
                    title="📊 상품별 유입(클릭수) 및 포지셔닝 비교",
                    labels={"클릭수": "클릭수 (회)", "상품명": "상품명", "포지셔닝": "상태 포지셔닝"},
                    template="plotly_dark"
                )
                fig_bar.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_tickangle=-45
                )
                fig_bar.update_traces(marker_cornerradius=12)
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with col_scatter:
                fig_scatter = px.scatter(
                    df_cleaned, x="클릭수", y="구매전환율 (%)",
                    size="추정 매출액 (원)", color="포지셔닝",
                    color_discrete_map={
                        "개선 필요": "#ef4444",
                        "노출 과다": "#f97316",
                        "스타": "#10b981",
                        "성장 기회": "#3b82f6",
                        "유지 관리": "#6b7280"
                    },
                    text="상품명",
                    title="🎯 상품별 마케팅 포지셔닝 맵 (원 크기 = 매출액)",
                    labels={"클릭수": "클릭수 (유입량)", "구매전환율 (%)": "구매전환율 (%)", "포지셔닝": "포지셔닝"},
                    template="plotly_dark"
                )
                fig_scatter.update_traces(textposition='top center')
                fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            # 리포트 내보내기 마크다운 출력
            st.markdown("### 📥 맞춤형 종합 진단 보고서 내보내기")
            
            report_md = f"""# 📦 쇼핑몰 상품 성과 진단 보고서
            
- **진단 기준 일자**: {datetime.now().strftime('%Y-%m-%d')}
- **총 분석 상품 수**: {len(df_cleaned)}개

## 📊 상품 포지셔닝 현황
- 🏆 **스타 상품**: {', '.join(df_cleaned[df_cleaned['포지셔닝'] == '스타']['상품명'].tolist()) or '없음'}
- 📈 **성장 기회 상품**: {', '.join(df_cleaned[df_cleaned['포지셔닝'] == '성장 기회']['상품명'].tolist()) or '없음'}
- 🚨 **노출 과다 상품 (개선 필요)**: {', '.join(df_cleaned[df_cleaned['포지셔닝'] == '노출 과다']['상품명'].tolist()) or '없음'}
- ⚠️ **개선 필요 상품 (전환율 저조)**: {', '.join(df_cleaned[df_cleaned['포지셔닝'] == '개선 필요']['상품명'].tolist()) or '없음'}
- ⚙️ **유지 관리 상품**: {', '.join(df_cleaned[df_cleaned['포지셔닝'] == '유지 관리']['상품명'].tolist()) or '없음'}

## 🔍 상품별 세일즈/마케팅 지표
| 순위 | 상품명 | 상품ID | 포지셔닝 | 클릭수 | 구매전환율 (%) | 추정 매출액 (원) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
            df_sorted = df_cleaned.sort_values(by="추정 매출액 (원)", ascending=False).reset_index(drop=True)
            for idx, row in df_sorted.iterrows():
                report_md += f"| {idx+1} | {row['상품명']} | {row['상품ID']} | {row['포지셔닝']} | {row['클릭수']:,} | {row['구매전환율 (%)']:.2f}% | {row['추정 매출액 (원)']:,}원 |\n"
                
            report_md += f"""
## 💡 맞춤형 마케팅 추천 액션
1. **노출 과다 상품 ({over_exposed_count}개)**
   - 상세페이지 이미지 고도화 및 고객 후기(리뷰)를 상단에 노출시켜 CVR을 개선해야 합니다.
   - 즉시 할인 또는 쿠폰 혜택 적용을 권장합니다.

2. **개선 필요 상품 ({underperforming_count}개)**
   - 클릭수 대비 구매전환율이 매우 낮으므로 상품 매력도를 대폭 보완해야 합니다.
   - 가격 할인 프로모션을 실행하거나 1+1 구성 등 기획전을 연동하세요.

3. **스타 상품**
   - 검색 광고 및 쇼핑 검색 입찰가를 추가로 상향 조정하여 검색 노출 순위를 상위로 고정하십시오.
   - 외부 마케팅(SNS, 인플루언서 협찬)을 병행하여 유입 극대화를 추진합니다.

4. **성장 기회 상품**
   - 전환율은 매우 훌륭하므로 유입량(클릭수)만 늘려주면 매출이 급성장합니다.
   - 쇼핑 키워드 광고 집행을 적극 검토하십시오.
"""
            st.download_button(
                label="📥 종합 진단 보고서 다운로드 (.md)",
                data=report_md,
                file_name=f"shop_diagnose_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        # --- 3. 📋 상품 데이터 상세 내역 탭 ---
        with tab_details:
            st.markdown("#### 📋 상품 데이터 상세 내역 및 다운로드")
            
            search_query = st.text_input("🔍 상품명으로 검색", "", key="diagnose_search")
            df_filtered = df_cleaned.copy()
            if search_query:
                df_filtered = df_filtered[df_filtered["상품명"].str.contains(search_query, case=False)]
                
            df_filtered = df_filtered[["상품ID", "상품명", "포지셔닝", "클릭수", "구매전환율 (%)", "추정 구매수", "평균 단가 (원)", "추정 매출액 (원)"]]
            st.dataframe(
                df_filtered.style.background_gradient(cmap="Blues", subset=["클릭수", "추정 매출액 (원)"])
                .format({"구매전환율 (%)": "{:.2f}%", "평균 단가 (원)": "{:,.0f}원", "추정 매출액 (원)": "{:,.0f}원", "클릭수": "{:,.0f}", "추정 구매수": "{:,.0f}"}),
                use_container_width=True
            )
            
            csv_processed = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 가공 완료된 상품 데이터 CSV 다운로드",
                data=csv_processed,
                file_name=f"processed_shop_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

else:
    # 블로그, 카페, 뉴스, 쇼핑 검색을 위한 검색 조건 템플릿
    st.markdown("### 🔍 검색 조건 및 대상 키워드 설정")
    
    default_keyword = "갤럭시 S24, 아이폰 15"
    if menu == "🛒 쇼핑 검색 분석":
        default_keyword = "기계식 키보드, 게이밍 마우스"
        
    keywords_input = st.text_input("검색 키워드 입력 (쉼표 ','로 구분하여 여러 개 비교 가능)", value=default_keyword, help="비교 분석할 상품/검색어를 쉼표로 구분하여 입력하세요.")
    keywords_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
    
    col1, col2 = st.columns(2)
    with col1:
        display_num = st.slider("수집할 데이터 개수 (검색어당)", min_value=10, max_value=100, value=30, step=10)
    with col2:
        if menu == "🛒 쇼핑 검색":
            sort_type = st.selectbox("정렬 순서", ["sim", "date", "asc", "dsc"], format_func=lambda x: {"sim": "유사도순", "date": "최신등록순", "asc": "가격낮은순", "dsc": "가격높은순"}[x])
        else:
            sort_type = st.selectbox("정렬 순서", ["sim", "date"], format_func=lambda x: {"sim": "유사도순", "date": "최신작성순"}[x])

    # 검색 기간 설정 (블로그, 뉴스에서 사용)
    st.markdown("### 📅 기간 설정 (블로그, 뉴스 검색에만 실시간 적용)")
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("조회 시작일", value=datetime.now() - timedelta(days=30))
    with col_end:
        end_date = st.date_input("조회 종료일", value=datetime.now())

    if menu in ["🛒 쇼핑 검색 분석", "👥 카페글 검색 분석"]:
        st.markdown(f"""
        <div class="info-box">
            ⚠️ <b>안내:</b> 네이버 {display_title} API는 작성일/등록일 메타데이터를 직접 반환하지 않아 날짜 필터링이 적용되지 않으며, 
            지정한 조건(수집 개수, 정렬)에 기반한 최신 수집 데이터로 비교 분석을 제공합니다.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            💡 <b>기간 필터링 작동 방식:</b> 네이버 {display_title} API로 수집한 최신 데이터(최대 {display_num}개) 중 
            설정하신 기간(<b>{start_date} ~ {end_date}</b>)에 해당하는 데이터를 필터링하여 시계열 및 랭킹 요약을 제공합니다.
        </div>
        """, unsafe_allow_html=True)

    if st.button(f"{display_title} 수집 및 통계 분석 실행", type="primary"):
        if not keywords_list:
            st.warning("검색 키워드를 입력해 주세요.")
        else:
            if menu == "🛒 쇼핑 검색 분석":
                with st.spinner("네이버 쇼핑 API 검색 데이터 수집 중..."):
                    try:
                        df_list = []
                        for query in keywords_list:
                            data = cached_shopping_search(client_id, client_secret, query, display_num, 1, sort_type, "", "")
                            items = data.get("items", [])
                            if items:
                                df = pd.DataFrame(items)
                                df["lprice"] = pd.to_numeric(df["lprice"], errors='coerce').fillna(0).astype(int)
                                df["hprice"] = pd.to_numeric(df["hprice"], errors='coerce').fillna(0).astype(int)
                                df["title"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
                                df["keyword"] = query
                                df_list.append(df)
                        
                        if not df_list:
                            st.warning("수집된 상품 정보가 없습니다.")
                        else:
                            df_all = pd.concat(df_list, ignore_index=True)
                            
                            # KPI 요약 카드
                            st.markdown("### 🛍️ 검색어별 가격 및 상품 분포 비교")
                            kpi_cols = st.columns(len(df_list))
                            for i, query in enumerate(keywords_list):
                                df_q = df_all[df_all["keyword"] == query]
                                if not df_q.empty:
                                    avg_price = df_q[df_q["lprice"] > 0]["lprice"].mean()
                                    min_price = df_q[df_q["lprice"] > 0]["lprice"].min()
                                    colors = ["text-green", "text-blue", "text-purple", "text-green", "text-blue"]
                                    with kpi_cols[i]:
                                        make_card(
                                            f"🛒 {query} 평균최저가", 
                                            f"{int(avg_price):,}원", 
                                            f"최저가: {int(min_price):,}원 (수집: {len(df_q)}개)",
                                            color_class=colors[i % len(colors)]
                                        )
                            
                            # 시각화 1: 박스 플롯 가격 비교 (IQR 이상치 식별에 최적)
                            st.markdown("### 💵 키워드별 상품 최저가 분포 비교 (Box Plot)")
                            fig_box = px.box(
                                df_all[df_all["lprice"] > 0], x="keyword", y="lprice", color="keyword",
                                labels={"lprice": "최저 가격 (원)", "keyword": "검색어"},
                                title="검색 키워드별 상품 최저가 분포 현황 및 극단값(Outlier) 시각화",
                                template="plotly_dark"
                            )
                            fig_box.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)"
                            )
                            st.plotly_chart(fig_box, use_container_width=True)
                            
                            # 시각화 2: 쇼핑몰 점유율 & 브랜드 분석
                            col_c1, col_c2 = st.columns(2)
                            with col_c1:
                                st.markdown("#### 🏪 판매 쇼핑몰 비중 비교 (Grouped Bar)")
                                mall_counts = df_all.groupby(["keyword", "mallName"]).size().reset_index(name="상품수")
                                # 각 키워드별 상위 7개 쇼핑몰만 추출
                                mall_counts = mall_counts.sort_values(["keyword", "상품수"], ascending=[True, False]).groupby("keyword").head(7).reset_index(drop=True)
                                fig_mall = px.bar(
                                    mall_counts, x="상품수", y="mallName", color="keyword", barmode="group",
                                    title="검색어별 주요 판매 쇼핑몰 분포",
                                    template="plotly_dark",
                                    orientation="h"
                                )
                                fig_mall.update_layout(
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)"
                                )
                                st.plotly_chart(fig_mall, use_container_width=True)
                            
                            with col_c2:
                                st.markdown("#### 🏷️ 상위 주요 브랜드 분포 비교")
                                brand_counts = df_all[df_all["brand"] != ""].groupby(["keyword", "brand"]).size().reset_index(name="상품수")
                                brand_counts = brand_counts.sort_values(["keyword", "상품수"], ascending=[True, False]).groupby("keyword").head(7).reset_index(drop=True)
                                if not brand_counts.empty:
                                    fig_brand = px.bar(
                                        brand_counts, x="상품수", y="brand", color="keyword", barmode="group",
                                        title="검색어별 상위 브랜드 상품 분포",
                                        template="plotly_dark",
                                        orientation="h"
                                    )
                                    fig_brand.update_layout(
                                        plot_bgcolor="rgba(0,0,0,0)",
                                        paper_bgcolor="rgba(0,0,0,0)"
                                    )
                                    st.plotly_chart(fig_brand, use_container_width=True)
                                else:
                                    st.info("수집된 상품의 브랜드 정보가 부족합니다.")
                                    
                            # 상품 리스트 출력 (필터링 및 정렬)
                            st.markdown("### 📋 수집된 상품 상세 리스트")
                            display_df = df_all[["keyword", "title", "lprice", "mallName", "brand", "maker", "category1", "link"]]
                            display_df.columns = ["검색어", "상품명", "최저가 (원)", "판매몰", "브랜드", "제조사", "카테고리", "상품링크"]
                            st.dataframe(display_df, use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"쇼핑 데이터 수집 실패: {e}")

            elif menu == "📝 블로그 검색 분석":
                with st.spinner("네이버 블로그 검색 데이터 수집 중..."):
                    try:
                        df_list = []
                        for query in keywords_list:
                            data = cached_blog_search(client_id, client_secret, query, display_num, 1, sort_type)
                            items = data.get("items", [])
                            if items:
                                df = pd.DataFrame(items)
                                df["title"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
                                df["description"] = df["description"].str.replace("<b>", "").str.replace("</b>", "")
                                df["keyword"] = query
                                df["postdate_clean"] = pd.to_datetime(df["postdate"], format="%Y%m%d", errors="coerce")
                                df_list.append(df)
                        
                        if not df_list:
                            st.warning("조회 결과가 없습니다.")
                        else:
                            df_all = pd.concat(df_list, ignore_index=True)
                            
                            # 날짜 필터링 적용
                            start_dt = pd.to_datetime(start_date)
                            end_dt = pd.to_datetime(end_date)
                            df_filtered = df_all[(df_all["postdate_clean"] >= start_dt) & (df_all["postdate_clean"] <= end_dt)]
                            
                            if df_filtered.empty:
                                st.warning(f"선택한 기간 ({start_date} ~ {end_date}) 내에 수집된 블로그 글이 없습니다. 수집 개수를 늘리거나 기간을 조정해 보세요.")
                            else:
                                # KPI 요약
                                st.markdown(f"### 📝 설정 기간 내 ({start_date} ~ {end_date}) 블로그 포스팅 통계")
                                kpi_cols = st.columns(len(keywords_list))
                                for i, query in enumerate(keywords_list):
                                    df_q = df_filtered[df_filtered["keyword"] == query]
                                    colors = ["text-green", "text-blue", "text-purple", "text-green", "text-blue"]
                                    if not df_q.empty:
                                        top_blogger = df_q["bloggername"].value_counts().idxmax()
                                        top_count = df_q["bloggername"].value_counts().max()
                                        with kpi_cols[i]:
                                            make_card(
                                                f"📝 {query} 포스트 수", 
                                                f"{len(df_q)}개", 
                                                f"최다 작성: {top_blogger} ({top_count}개)",
                                                color_class=colors[i % len(colors)]
                                            )
                                    else:
                                        with kpi_cols[i]:
                                            make_card(f"📝 {query} 포스트 수", "0개", "기간 내 해당 글 없음", "")
                                            
                                # 시각화: 작성일별 포스팅 수 추이
                                st.markdown("### 📈 기간 내 포스팅 수 시계열 추이 비교")
                                trend_df = df_filtered.groupby(["postdate_clean", "keyword"]).size().reset_index(name="포스트수")
                                fig_trend = px.line(
                                    trend_df, x="postdate_clean", y="포스트수", color="keyword",
                                    labels={"postdate_clean": "작성일", "포스트수": "포스트 수"},
                                    title="날짜별 블로그 기고량 추이 비교",
                                    template="plotly_dark",
                                    markers=True
                                )
                                fig_trend.update_layout(
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)"
                                )
                                st.plotly_chart(fig_trend, use_container_width=True)
                                
                                # 시각화: 블로거 작성 빈도
                                st.markdown("### 📊 키워드별 상위 주요 블로거 비교")
                                blogger_counts = df_filtered.groupby(["keyword", "bloggername"]).size().reset_index(name="포스트수")
                                blogger_counts = blogger_counts.sort_values(["keyword", "포스트수"], ascending=[True, False]).groupby("keyword").head(5).reset_index(drop=True)
                                fig_blogger = px.bar(
                                    blogger_counts, x="포스트수", y="bloggername", color="keyword", barmode="group",
                                    title="수집 데이터 내 상위 다작 블로거 비교",
                                    template="plotly_dark",
                                    orientation="h"
                                )
                                fig_blogger.update_layout(
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)"
                                )
                                st.plotly_chart(fig_blogger, use_container_width=True)
                                
                                # 테이블 출력
                                st.markdown("### 📋 블로그 포스트 리스트 (설정 기간 기준 필터링)")
                                display_df = df_filtered[["keyword", "title", "bloggername", "postdate", "link"]]
                                display_df.columns = ["검색어", "제목", "블로거", "작성일", "링크"]
                                st.dataframe(display_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"블로그 데이터 수집 실패: {e}")

            elif menu == "👥 카페글 검색 분석":
                with st.spinner("네이버 카페글 데이터 수집 중..."):
                    try:
                        df_list = []
                        for query in keywords_list:
                            data = cached_cafe_search(client_id, client_secret, query, display_num, 1, sort_type)
                            items = data.get("items", [])
                            if items:
                                df = pd.DataFrame(items)
                                df["title"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
                                df["description"] = df["description"].str.replace("<b>", "").str.replace("</b>", "")
                                df["keyword"] = query
                                df_list.append(df)
                        
                        if not df_list:
                            st.warning("조회 결과가 없습니다.")
                        else:
                            df_all = pd.concat(df_list, ignore_index=True)
                            
                            # KPI 요약
                            st.markdown("### ☕ 카페글 지표 요약 및 비교")
                            kpi_cols = st.columns(len(df_list))
                            for i, query in enumerate(keywords_list):
                                df_q = df_all[df_all["keyword"] == query]
                                if not df_q.empty:
                                    top_cafe = df_q["cafename"].value_counts().idxmax()
                                    top_count = df_q["cafename"].value_counts().max()
                                    colors = ["text-green", "text-blue", "text-purple", "text-green", "text-blue"]
                                    with kpi_cols[i]:
                                        make_card(
                                            f"☕ {query} 게시글", 
                                            f"{len(df_q)}개", 
                                            f"최다 카페: {top_cafe} ({top_count}개)",
                                            color_class=colors[i % len(colors)]
                                        )
                                
                            # 시각화: 카페별 글 분포
                            st.markdown("### 📊 키워드별 상위 주요 카페 게시글 분포 비교")
                            cafe_counts = df_all.groupby(["keyword", "cafename"]).size().reset_index(name="게시글수")
                            cafe_counts = cafe_counts.sort_values(["keyword", "게시글수"], ascending=[True, False]).groupby("keyword").head(7).reset_index(drop=True)
                            fig_cafe = px.bar(
                                cafe_counts, x="게시글수", y="cafename", color="keyword", barmode="group",
                                title="관련 글이 주로 수집된 네이버 카페 분포 비교",
                                template="plotly_dark",
                                orientation="h"
                            )
                            fig_cafe.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)"
                            )
                            st.plotly_chart(fig_cafe, use_container_width=True)
                            
                            # 테이블 출력
                            st.markdown("### 📋 카페 게시글 리스트")
                            display_df = df_all[["keyword", "title", "cafename", "link"]]
                            display_df.columns = ["검색어", "제목", "카페이름", "링크"]
                            st.dataframe(display_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"카페글 데이터 수집 실패: {e}")

            elif menu == "📰 뉴스 검색 분석":
                with st.spinner("네이버 뉴스 데이터 수집 중..."):
                    try:
                        df_list = []
                        for query in keywords_list:
                            data = cached_news_search(client_id, client_secret, query, display_num, 1, sort_type)
                            items = data.get("items", [])
                            if items:
                                df = pd.DataFrame(items)
                                df["title"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
                                df["description"] = df["description"].str.replace("<b>", "").str.replace("</b>", "")
                                df["keyword"] = query
                                # pubDate parsing (RFC 822 포맷) 및 Naive datetime 처리
                                df["pubDate_clean"] = pd.to_datetime(df["pubDate"], errors='coerce')
                                if not df["pubDate_clean"].empty and df["pubDate_clean"].dt.tz is not None:
                                    df["pubDate_clean"] = df["pubDate_clean"].dt.tz_localize(None)
                                df_list.append(df)
                        
                        if not df_list:
                            st.warning("조회 결과가 없습니다.")
                        else:
                            df_all = pd.concat(df_list, ignore_index=True)
                            
                            # 날짜 필터링 적용
                            start_dt = pd.to_datetime(start_date)
                            end_dt = pd.to_datetime(end_date)
                            df_filtered = df_all[(df_all["pubDate_clean"] >= start_dt) & (df_all["pubDate_clean"] <= end_dt)]
                            
                            if df_filtered.empty:
                                st.warning(f"선택한 기간 ({start_date} ~ {end_date}) 내에 수집된 뉴스 기사가 없습니다. 수집 개수를 늘리거나 기간을 조정해 보세요.")
                            else:
                                # KPI 요약
                                st.markdown(f"### 📰 설정 기간 내 ({start_date} ~ {end_date}) 뉴스 기사 통계")
                                kpi_cols = st.columns(len(keywords_list))
                                for i, query in enumerate(keywords_list):
                                    df_q = df_filtered[df_filtered["keyword"] == query]
                                    colors = ["text-green", "text-blue", "text-purple", "text-green", "text-blue"]
                                    if not df_q.empty:
                                        latest_news = df_q.loc[df_q["pubDate_clean"].idxmax(), "pubDate_clean"].strftime("%Y-%m-%d %H:%M")
                                        with kpi_cols[i]:
                                            make_card(
                                                f"📰 {query} 뉴스 기사", 
                                                f"{len(df_q)}개", 
                                                f"최신 기사: {latest_news}",
                                                color_class=colors[i % len(colors)]
                                            )
                                    else:
                                        with kpi_cols[i]:
                                            make_card(f"📰 {query} 뉴스 기사", "0개", "기간 내 관련 기사 없음", "")
                                
                                # 시각화: 날짜별 뉴스 보도량 추이
                                st.markdown("### 📈 기간 내 뉴스 보도량 시계열 추이 비교")
                                df_filtered["pubDate_only"] = df_filtered["pubDate_clean"].dt.date
                                news_trend = df_filtered.groupby(["pubDate_only", "keyword"]).size().reset_index(name="기사수")
                                fig_news = px.line(
                                    news_trend, x="pubDate_only", y="기사수", color="keyword",
                                    labels={"pubDate_only": "보도일", "기사수": "기사 수"},
                                    title="날짜별 뉴스 보도량 추이 비교",
                                    template="plotly_dark",
                                    markers=True
                                )
                                fig_news.update_layout(
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)"
                                )
                                st.plotly_chart(fig_news, use_container_width=True)
                                
                                # 테이블 출력
                                st.markdown("### 📋 뉴스 기사 리스트 (설정 기간 기준 필터링)")
                                display_df = df_filtered[["keyword", "title", "pubDate", "link", "originallink"]]
                                display_df.columns = ["검색어", "기사제목", "발행시간", "네이버뉴스링크", "원문링크"]
                                st.dataframe(display_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"뉴스 데이터 수집 실패: {e}")
