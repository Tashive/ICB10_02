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
            <div style="font-size: 28px; margin-bottom: 10px;">🔍</div>
            <div style="color: #3b82f6; font-weight: 700; font-size: 16px; margin-bottom: 6px;">검색 데이터 다차원 분석</div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">쇼핑, 블로그, 카페, 뉴스 검색 데이터를 수집하고 다각도로 분석합니다.</div>
        </div>
        """, unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 28px; margin-bottom: 10px;">📊</div>
            <div style="color: #8b5cf6; font-weight: 700; font-size: 16px; margin-bottom: 6px;">인터랙티브 시각화</div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">모든 차트는 Plotly 기반으로 인터랙티브하게 제공됩니다.</div>
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
if not client_id or not client_secret:
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

    st.markdown("#### 📂 실제 스마트스토어 실적 데이터 분석 연동 (선택사항)")
    uploaded_file = st.file_uploader(
        "스마트스토어에서 다운로드한 상품/판매 실적 엑셀 또는 CSV 파일을 업로드해 주세요. 업로드 시 실제 데이터와 네이버 쇼핑 트렌드를 연동하여 정밀 분석합니다.", 
        type=["xlsx", "xls", "csv"], 
        help="스마트스토어의 상품별 실적분석 엑셀 보고서 포맷을 자동으로 인식해 컬럼을 파싱합니다."
    )

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
                    else:
                        df_all = pd.concat(df_list, ignore_index=True)
                        
                        # 스마트스토어 파일 업로드 확인 및 파싱
                        store_df = None
                        if uploaded_file is not None:
                            try:
                                store_df = parse_smartstore_data(uploaded_file)
                                # 각 상품의 소속 카테고리를 추정하는 컬럼 추가 (키워드 기반 자동 매핑)
                                store_df["매핑 카테고리"] = "미분류"
                                for idx, row in store_df.iterrows():
                                    prod_name = row["상품명"]
                                    for cat in st.session_state["selected_shopping_categories"]:
                                        cat_name = cat["name"]
                                        # 상품명에 카테고리명이 포함되는지 지능형 체크
                                        if cat_name in prod_name or prod_name.replace(" ", "") in cat_name or any(part in prod_name for part in cat_name.split("/")) or (len(cat_name) >= 3 and cat_name[:3] in prod_name):
                                            store_df.at[idx, "매핑 카테고리"] = cat_name
                                            break
                            except Exception as e:
                                st.error(f"❌ 스마트스토어 데이터 파싱 실패: {str(e)}")
                                store_df = None
                        
                        # 탭 인터페이스 구성
                        tab1, tab2, tab3 = st.tabs(["📈 클릭 트렌드 & 기본 통계", "👥 성별/연령 및 매출액 추이", "🏆 개별 상품 랭킹 보드"])
                        
                        with tab1:
                            # KPI 카드 배치
                            st.markdown("### 🛍️ 카테고리별 트렌드 지표 요약")
                            kpi_cols = st.columns(len(df_list))
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
                            st.markdown("### 💰 카테고리별 일일 추정/실제 매출액 추이")
                            sales_list = []
                            for cat in st.session_state["selected_shopping_categories"]:
                                cat_name = cat["name"]
                                cat_id = cat["id"]
                                cat_df = df_all[df_all["category"] == cat_name]
                                
                                # 스마트스토어 업로드 시 실제 데이터와 네이버 트렌드 지수 융합 배분
                                if store_df is not None:
                                    mapped_products = store_df[store_df["매핑 카테고리"] == cat_name]
                                    total_revenue = mapped_products["매출액"].sum()
                                    
                                    if total_revenue > 0:
                                        total_ratio = cat_df["ratio"].sum()
                                        df_sales = cat_df.copy()
                                        if total_ratio > 0:
                                            # 트렌드 지수에 비례하여 누적 결제금액을 일일 매출로 안분 배분
                                            df_sales["추정 매출액"] = ((df_sales["ratio"] / total_ratio) * total_revenue).astype(int)
                                        else:
                                            df_sales["추정 매출액"] = 0
                                        sales_list.append(df_sales[["period", "추정 매출액", "category"]])
                                    else:
                                        # 매핑 상품은 없으나 카테고리 기본 추이 렌더링
                                        avg_price = 120000 if "가구" in cat_name or "수납" in cat_name else (450000 if "디지털" in cat_name else 55000)
                                        df_sales = generate_mock_sales_trend(cat_df, avg_price)
                                        sales_list.append(df_sales)
                                else:
                                    # 가상 데이터 렌더링
                                    avg_price = 120000 if "가구" in cat_name or "수납" in cat_name else (450000 if "디지털" in cat_name else 55000)
                                    df_sales = generate_mock_sales_trend(cat_df, avg_price)
                                    sales_list.append(df_sales)
                                
                            if sales_list:
                                df_sales_all = pd.concat(sales_list, ignore_index=True)
                                fig_sales = px.line(
                                    df_sales_all, x="period", y="추정 매출액", color="category",
                                    labels={"period": "날짜", "추정 매출액": "추정 매출액 (원)", "category": "카테고리"},
                                    title="일일 매출액 변동 추이 (요일별 가중치 또는 안분 배분 반영)",
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
                            selected_rank_cat_name = st.selectbox("랭킹 보드를 조회할 카테고리를 선택하세요:", cat_names, key="rank_cat_selector")
                            
                            selected_cat_info = next(c for c in st.session_state["selected_shopping_categories"] if c["name"] == selected_rank_cat_name)
                            selected_cat_id = selected_cat_info["id"]
                            
                            # 스마트스토어 업로드 시 카테고리 매핑 관리 아코디언 제공
                            if store_df is not None:
                                with st.expander("🔗 스마트스토어 상품 - 네이버 쇼핑 카테고리 매핑 관리"):
                                    st.markdown("스마트스토어 상품명 분석을 통해 자동으로 소속 카테고리가 분류되었습니다. 오분류가 있는 경우 아래에서 카테고리를 수정해 주세요.")
                                    cat_options = ["미분류"] + [c["name"] for c in st.session_state["selected_shopping_categories"]]
                                    
                                    if "manual_mappings" not in st.session_state:
                                        st.session_state["manual_mappings"] = {}
                                        
                                    for idx, row in store_df.iterrows():
                                        p_id = row["상품ID"]
                                        p_name = row["상품명"]
                                        auto_cat = row["매핑 카테고리"]
                                        
                                        current_cat = st.session_state["manual_mappings"].get(p_id, auto_cat)
                                        
                                        col_p1, col_p2 = st.columns([3, 1])
                                        with col_p1:
                                            st.markdown(f"📦 **{p_name}** `(ID: {p_id})`")
                                        with col_p2:
                                            new_cat = st.selectbox(
                                                "소속 카테고리", 
                                                options=cat_options, 
                                                index=cat_options.index(current_cat) if current_cat in cat_options else 0,
                                                key=f"map_{p_id}"
                                            )
                                            if new_cat != current_cat:
                                                st.session_state["manual_mappings"][p_id] = new_cat
                                                st.rerun()
                                                
                                    for idx, row in store_df.iterrows():
                                        p_id = row["상품ID"]
                                        if p_id in st.session_state["manual_mappings"]:
                                            store_df.at[idx, "매핑 카테고리"] = st.session_state["manual_mappings"][p_id]

                            # 매핑된 상품이 있을 경우 실제 데이터 사용, 없을 경우 가상 데이터 시뮬레이션
                            actual_products_in_cat = pd.DataFrame()
                            if store_df is not None:
                                actual_products_in_cat = store_df[store_df["매핑 카테고리"] == selected_rank_cat_name]
                                
                            if not actual_products_in_cat.empty:
                                st.success(f"✅ 스마트스토어의 실제 등록 상품 {len(actual_products_in_cat)}개의 실적을 기반으로 랭킹 보드를 렌더링했습니다.")
                                df_products = actual_products_in_cat[[
                                    "상품명", "클릭수", "구매전환율", "구매수", "평균 단가 (원)", "매출액"
                                ]].rename(columns={
                                    "구매전환율": "구매전환율 (%)", 
                                    "구매수": "추정 구매수", 
                                    "평균 단가 (원)": "평균 단가 (원)",
                                    "매출액": "추정 매출액 (원)"
                                })
                            else:
                                if store_df is not None:
                                    st.info(f"💡 현재 카테고리('{selected_rank_cat_name}')에 매핑된 실제 스마트스토어 상품이 없어 가상 시뮬레이션 데이터를 제공합니다. 위 매핑 관리 아코디언에서 상품을 매핑하시면 반영됩니다.")
                                df_products = generate_mock_products(selected_rank_cat_name, selected_cat_id)
                            
                            st.markdown(f"#### 🥇 {selected_rank_cat_name} 상품별 실적 순위 (클릭수 및 전환율)")
                            
                            # 랭킹 정렬 기준 선택
                            sort_by = st.radio("랭킹 기준 설정", ["추정 매출액 순", "클릭수 순", "구매전환율 순"], horizontal=True, key="rank_sort_criteria")
                            
                            if sort_by == "추정 매출액 순":
                                df_sorted = df_products.sort_values(by="추정 매출액 (원)", ascending=False).reset_index(drop=True)
                            elif sort_by == "클릭수 순":
                                df_sorted = df_products.sort_values(by="클릭수", ascending=False).reset_index(drop=True)
                            else:
                                df_sorted = df_products.sort_values(by="구매전환율 (%)", ascending=False).reset_index(drop=True)
                                
                            df_sorted.index = df_sorted.index + 1
                            df_sorted.index.name = "순위"
                            
                            st.dataframe(
                                df_sorted.style.background_gradient(cmap="Oranges", subset=["클릭수", "추정 매출액 (원)"])
                                .format({"구매전환율 (%)": "{:.2f}%", "평균 단가 (원)": "{:,.0f}원", "추정 매출액 (원)": "{:,.0f}원", "클릭수": "{:,.0f}", "추정 구매수": "{:,.0f}"}),
                                use_container_width=True
                            )
                            
                            # 2차원 산점도를 통한 포트폴리오 분석 (BCG 매트릭스 타입)
                            st.markdown("#### 📊 상품 포트폴리오 분석 (클릭수 vs 구매전환율)")
                            st.markdown("""
                            * **스타 (우측 상단)**: 클릭수(유입량)와 구매전환율(선호도)이 모두 높은 핵심 상품입니다.
                            * **성장 기회 (좌측 상단)**: 구매전환율은 높으나 유입(클릭수)이 부족해 마케팅 노출 증대가 필요한 상품입니다.
                            * **노출 과다 (우측 하단)**: 클릭수는 높으나 구매전환율이 낮아 상세페이지나 가격 경쟁력 개선이 필요한 상품입니다.
                            """)
                            
                            # 중위수 기준값 산출
                            median_clicks = float(df_products["클릭수"].median())
                            median_conv = float(df_products["구매전환율 (%)"].median())
                            
                            if pd.isna(median_clicks) or median_clicks <= 0:
                                median_clicks = 1.0
                            if pd.isna(median_conv) or median_conv <= 0:
                                median_conv = 1.0
                                
                            def get_position(row, med_c, med_v):
                                if row["클릭수"] >= med_c and row["구매전환율 (%)"] >= med_v:
                                    return "스타 (우측 상단)"
                                elif row["클릭수"] < med_c and row["구매전환율 (%)"] >= med_v:
                                    return "성장 기회 (좌측 상단)"
                                elif row["클릭수"] >= med_c and row["구매전환율 (%)"] < med_v:
                                    return "노출 과다 (우측 하단)"
                                else:
                                    return "개선 필요 (좌측 하단)"
                                    
                            df_products["포지셔닝"] = df_products.apply(lambda r: get_position(r, median_clicks, median_conv), axis=1)
                            
                            fig_scatter = px.scatter(
                                df_products, x="클릭수", y="구매전환율 (%)",
                                size="추정 매출액 (원)", color="포지셔닝",
                                text="상품명",
                                color_discrete_map={
                                    "스타 (우측 상단)": "#10b981",
                                    "성장 기회 (좌측 상단)": "#3b82f6",
                                    "노출 과다 (우측 하단)": "#f59e0b",
                                    "개선 필요 (좌측 하단)": "#ef4444"
                                },
                                title=f"{selected_rank_cat_name} 상품별 마케팅 포지셔닝 맵 (원 크기 = 매출액)",
                                labels={"클릭수": "클릭수 (유입량)", "구매전환율 (%)": "구매전환율 (%)", "포지셔닝": "4사분면 포지션"},
                                template="plotly_dark"
                            )
                            fig_scatter.update_traces(textposition='top center')
                            fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                            
                            # 중위수 기준 가이드라인 추가
                            fig_scatter.add_vline(x=median_clicks, line_dash="dash", line_color="#94a3b8", 
                                                 annotation_text=f"클릭 중위수 ({int(median_clicks)})", annotation_position="top left")
                            fig_scatter.add_hline(y=median_conv, line_dash="dash", line_color="#94a3b8", 
                                                 annotation_text=f"전환율 중위수 ({median_conv:.2f}%)", annotation_position="bottom right")
                            
                            st.plotly_chart(fig_scatter, use_container_width=True)
                            
                            # --- 4사분면 진단 및 마케팅 가이드라인 보고서 렌더링 ---
                            st.markdown("### 💡 맞춤형 상품 포트폴리오 진단 및 마케팅 가이드라인")
                            
                            quadrants = {
                                "스타 (Star - 핵심 주력)": [],
                                "성장 기회 (Growth - 노출 부족)": [],
                                "노출 과다 (Exposure - 전환율 개선 필요)": [],
                                "개선 필요 (Underperforming - 유입/설득 부족)": []
                            }
                            
                            for _, row in df_products.iterrows():
                                p_name = row["상품명"]
                                clicks = row["클릭수"]
                                conv = row["구매전환율 (%)"]
                                rev = row["추정 매출액 (원)"]
                                pos = row["포지셔닝"]
                                
                                item_info = (p_name, clicks, conv, rev)
                                if pos == "스타 (우측 상단)":
                                    quadrants["스타 (Star - 핵심 주력)"].append(item_info)
                                elif pos == "성장 기회 (좌측 상단)":
                                    quadrants["성장 기회 (Growth - 노출 부족)"].append(item_info)
                                elif pos == "노출 과다 (우측 하단)":
                                    quadrants["노출 과다 (Exposure - 전환율 개선 필요)"].append(item_info)
                                else:
                                    quadrants["개선 필요 (Underperforming - 유입/설득 부족)"].append(item_info)
                                    
                            # 상단에 요약 2x2 메트릭스 카드 배치
                            st.markdown("#### 📊 포지셔닝 현황판")
                            grid_col1, grid_col2 = st.columns(2)
                            with grid_col1:
                                make_card(
                                    "🌟 스타 상품군",
                                    f"{len(quadrants['스타 (Star - 핵심 주력)'])}개 상품",
                                    "클릭수 높음 & 전환율 높음",
                                    color_class="text-green"
                                )
                                make_card(
                                    "⚠️ 노출 과다 상품군",
                                    f"{len(quadrants['노출 과다 (Exposure - 전환율 개선 필요)'])}개 상품",
                                    "클릭수 높음 & 전환율 낮음",
                                    color_class="text-blue"
                                )
                            with grid_col2:
                                make_card(
                                    "📈 성장 기회 상품군",
                                    f"{len(quadrants['성장 기회 (Growth - 노출 부족)'])}개 상품",
                                    "클릭수 낮음 & 전환율 높음",
                                    color_class="text-blue"
                                )
                                make_card(
                                    "🔍 개선 필요 상품군",
                                    f"{len(quadrants['개선 필요 (Underperforming - 유입/설득 부족)'])}개 상품",
                                    "클릭수 낮음 & 전환율 낮음",
                                    color_class="text-purple"
                                )
                                
                            # 상세 탭 구성
                            detail_tabs = st.tabs([
                                "🌟 스타", 
                                "📈 성장 기회", 
                                "⚠️ 노출 과다", 
                                "🔍 개선 필요"
                            ])
                            
                            with detail_tabs[0]:
                                st.markdown("#### 🌟 스타 (Star - 핵심 주력) 마케팅 액션")
                                if quadrants["스타 (Star - 핵심 주력)"]:
                                    st.markdown("**대상 상품:**")
                                    for p in quadrants["스타 (Star - 핵심 주력)"]:
                                        st.markdown(f"- 📦 `{p[0]}` (클릭: {p[1]:,}회 | 전환율: {p[2]:.2f}% | 매출: {p[3]:,}원)")
                                else:
                                    st.info("이 카테고리에 해당하는 상품이 없습니다.")
                                st.markdown("""
                                **현 상태:** 유입량과 구매 전환 매력이 모두 높은 가장 이상적인 핵심 상품군입니다.
                                **추천 액션:**
                                1. **재고 확보 및 배송 관리:** 품절로 인한 판매 기회 유실을 최우선적으로 방지합니다.
                                2. **리뷰 관리 및 평점 최적화:** 구매 고객의 긍정 리뷰를 전면에 배치하고 부정 피드백에 신속 대응합니다.
                                3. **노출 시너지 확보:** 네이버 쇼핑 검색 광고의 키워드 순위를 상위권으로 유지하며 브랜드 키워드 광고를 병행합니다.
                                """)
                                
                            with detail_tabs[1]:
                                st.markdown("#### 📈 성장 기회 (Growth - 노출 부족) 마케팅 액션")
                                if quadrants["성장 기회 (Growth - 노출 부족)"]:
                                    st.markdown("**대상 상품:**")
                                    for p in quadrants["성장 기회 (Growth - 노출 부족)"]:
                                        st.markdown(f"- 📦 `{p[0]}` (클릭: {p[1]:,}회 | 전환율: {p[2]:.2f}% | 매출: {p[3]:,}원)")
                                else:
                                    st.info("이 카테고리에 해당하는 상품이 없습니다.")
                                st.markdown("""
                                **현 상태:** 상품의 가격, 혜택, 상세페이지 등 설득력은 우수하나 유입되는 고객 수(노출)가 현저히 부족합니다.
                                **추천 액션:**
                                1. **검색 노출 최적화 (SEO):** 상품명에 네이버 쇼핑 트렌드 인기 키워드를 반영하고 태그 설정을 고도화합니다.
                                2. **광고 예산 증액:** 저평가된 해당 상품군에 네이버 쇼핑 검색 광고나 성과형 디스플레이 광고(GFA) 예산을 늘려 유입을 강제로 유도합니다.
                                3. **외부 채널 활용:** 블로그, SNS(인스타그램 등) 공동구매나 체험단을 진행하여 트래픽 유입 경로를 다각화합니다.
                                """)
                                
                            with detail_tabs[2]:
                                st.markdown("#### ⚠️ 노출 과다 (Exposure - 전환율 개선 필요) 마케팅 액션")
                                if quadrants["노출 과다 (Exposure - 전환율 개선 필요)"]:
                                    st.markdown("**대상 상품:**")
                                    for p in quadrants["노출 과다 (Exposure - 전환율 개선 필요)"]:
                                        st.markdown(f"- 📦 `{p[0]}` (클릭: {p[1]:,}회 | 전환율: {p[2]:.2f}% | 매출: {p[3]:,}원)")
                                else:
                                    st.info("이 카테고리에 해당하는 상품이 없습니다.")
                                st.markdown("""
                                **현 상태:** 광고나 상위 노출 등으로 유입은 충분히 발생하고 있으나, 상세페이지나 혜택 등이 매력적이지 않아 구매 결정을 내리지 못하고 이탈하고 있습니다.
                                **추천 액션:**
                                1. **상세페이지 개편:** 도입부의 후킹(Hooking) 소구점을 재점검하고, 로딩 속도가 느린 이미지나 가독성 떨어지는 텍스트를 개선합니다.
                                2. **구매 장벽 제거:** 즉시 사용 가능한 할인 쿠폰 지급, 복수 구매 할인(1+1 등), 무료 배송 혜택을 일시적으로 추가해 구매를 유도합니다.
                                3. **리뷰 및 신뢰 장치 보완:** 실구매 고객의 고화질 리뷰나 만족도 높은 후기를 상세페이지 상단에 삽입하여 구매 안심감을 부여합니다.
                                """)
                                
                            with detail_tabs[3]:
                                st.markdown("#### 🔍 개선 필요 (Underperforming - 유입/설득 부족) 마케팅 액션")
                                if quadrants["개선 필요 (Underperforming - 유입/설득 부족)"]:
                                    st.markdown("**대상 상품:**")
                                    for p in quadrants["개선 필요 (Underperforming - 유입/설득 부족)"]:
                                        st.markdown(f"- 📦 `{p[0]}` (클릭: {p[1]:,}회 | 전환율: {p[2]:.2f}% | 매출: {p[3]:,}원)")
                                else:
                                    st.info("이 카테고리에 해당하는 상품이 없습니다.")
                                st.markdown("""
                                **현 상태:** 노출과 매력도가 모두 평균 이하로 떨어져 방치되고 있거나 리뉴얼이 필요한 상품군입니다.
                                **추천 액션:**
                                1. **상품 전면 개편:** 썸네일(대표 이미지)을 최신 트렌드에 맞게 재촬영하고 상품명을 완전 리뉴얼합니다.
                                2. **패키지 및 묶음 판매:** 단독 상품 판매가 어려우므로, '스타' 상품군의 보조 제품으로 묶거나 기획전 번들 상품으로 구성하여 강제 노출 기회를 만듭니다.
                                3. **가격 포지셔닝 재조정:** 유사 경쟁 상품들과의 가격 분포를 확인하고 일시적인 파격 특가 행사를 통해 지수 상승을 꾀합니다.
                                """)
                                
                            # 마크다운 리포트 생성 및 다운로드 버튼 제공
                            report_content = f"""# 📊 [스마트스토어 상품 포트폴리오 마케팅 진단 보고서]
- **기준 카테고리**: {selected_rank_cat_name}
- **진단 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **분류 임계치**: 클릭수 중위수 {int(median_clicks)}회 | 구매전환율 중위수 {median_conv:.2f}%

---

## 1. 포지셔닝 요약
- **🌟 스타 (Star - 핵심 주력)**: {len(quadrants["스타 (Star - 핵심 주력)"])}개 상품
- **📈 성장 기회 (Growth - 노출 부족)**: {len(quadrants["성장 기회 (Growth - 노출 부족)"])}개 상품
- **⚠️ 노출 과다 (Exposure - 전환율 개선 필요)**: {len(quadrants["노출 과다 (Exposure - 전환율 개선 필요)"])}개 상품
- **🔍 개선 필요 (Underperforming - 유입/설득 부족)**: {len(quadrants["개선 필요 (Underperforming - 유입/설득 부족)"])}개 상품

---

## 2. 그룹별 진단 및 마케팅 추천 액션

### 🌟 스타 (Star - 핵심 주력)
- **대상 상품**: {', '.join([f"'{p[0]}'" for p in quadrants["스타 (Star - 핵심 주력)"]]) if quadrants["스타 (Star - 핵심 주력)"] else '없음'}
- **현 상태**: 유입량과 구매 전환 매력이 모두 높은 가장 이상적인 핵심 상품군입니다.
- **추천 액션**:
  1. **재고 확보 및 배송 관리**: 품절로 인한 판매 기회 유실을 최우선적으로 방지합니다.
  2. **리뷰 관리 및 평점 최적화**: 구매 고객의 긍정 리뷰를 전면에 배치하고 부정 피드백에 신속 대응합니다.
  3. **노출 시너지 확보**: 네이버 쇼핑 검색 광고의 키워드 순위를 상위권으로 유지하며 브랜드 키워드 광고를 병행합니다.

### 📈 성장 기회 (Growth - 노출 부족)
- **대상 상품**: {', '.join([f"'{p[0]}'" for p in quadrants["성장 기회 (Growth - 노출 부족)"]]) if quadrants["성장 기회 (Growth - 노출 부족)"] else '없음'}
- **현 상태**: 상품의 가격, 혜택, 상세페이지 등 설득력은 우수하나 유입되는 고객 수(노출)가 현저히 부족합니다.
- **추천 액션**:
  1. **검색 노출 최적화 (SEO)**: 상품명에 네이버 쇼핑 트렌드 인기 키워드를 반영하고 태그 설정을 고도화합니다.
  2. **광고 예산 증액**: 저평가된 해당 상품군에 네이버 쇼핑 검색 광고나 성과형 디스플레이 광고(GFA) 예산을 늘려 유입을 강제로 유도합니다.
  3. **외부 채널 활용**: 블로그, SNS(인스타그램 등) 공동구매나 체험단을 진행하여 트래픽 유입 경로를 다각화합니다.

### ⚠️ 노출 과다 (Exposure - 전환율 개선 필요)
- **대상 상품**: {', '.join([f"'{p[0]}'" for p in quadrants["노출 과다 (Exposure - 전환율 개선 필요)"]]) if quadrants["노출 과다 (Exposure - 전환율 개선 필요)"] else '없음'}
- **현 상태**: 광고나 상위 노출 등으로 유입은 충분히 발생하고 있으나, 상세페이지나 혜택 등이 매력적이지 않아 구매 결정을 내리지 못하고 이탈하고 있습니다.
- **추천 액션**:
  1. **상세페이지 개편**: 도입부의 후킹(Hooking) 소구점을 재점검하고, 로딩 속도가 느린 이미지나 가독성 떨어지는 텍스트를 개선합니다.
  2. **구매 장벽 제거**: 즉시 사용 가능한 할인 쿠폰 지급, 복수 구매 할인(1+1 등), 무료 배송 혜택을 일시적으로 추가해 구매를 유도합니다.
  3. **리뷰 및 신뢰 장치 보완**: 실구매 고객의 고화질 리뷰나 만족도 높은 후기를 상세페이지 상단에 삽입하여 구매 안심감을 부여합니다.

### 🔍 개선 필요 (Underperforming - 유입/설득 부족)
- **대상 상품**: {', '.join([f"'{p[0]}'" for p in quadrants["개선 필요 (Underperforming - 유입/설득 부족)"]]) if quadrants["개선 필요 (Underperforming - 유입/설득 부족)"] else '없음'}
- **현 상태**: 노출과 매력도가 모두 평균 이하로 떨어져 방치되고 있거나 리뉴얼이 필요한 상품군입니다.
- **추천 액션**:
  1. **상품 전면 개편**: 썸네일(대표 이미지)을 최신 트렌드에 맞게 재촬영하고 상품명을 완전 리뉴얼합니다.
  2. **패키지 및 묶음 판매**: 단독 상품 판매가 어려우므로, '스타' 상품군의 보조 제품으로 묶거나 기획전 번들 상품으로 구성하여 강제 노출 기회를 만듭니다.
  3. **가격 포지셔닝 재조정**: 유사 경쟁 상품들과의 가격 분포를 확인하고 일시적인 파격 특가 행사를 통해 지수 상승을 꾀합니다.
"""
                            
                            st.markdown("#### 📥 진단 보고서 내보내기")
                            st.download_button(
                                label="📥 마케팅 진단 보고서 마크다운(.md) 파일 다운로드",
                                data=report_content.encode('utf-8'),
                                file_name=f"smartstore_marketing_report_{selected_rank_cat_name}_{datetime.now().strftime('%Y%m%d')}.md",
                                mime="text/markdown",
                                key="download_marketing_report_btn"
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
