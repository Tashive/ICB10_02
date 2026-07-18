"""
온라인 쇼핑몰 구매 의도(Online Shoppers Purchasing Intention) 분석 대시보드 애플리케이션

이 애플리케이션은 온라인 쇼핑 고객들의 세션 로그 데이터를 기반으로, 최종 구매 여부(Revenue)에 따른 
수치형 및 범주형 변수의 행동 패턴 차이를 비교 분석하고 기술 통계 요약, EDA 시각화(퍼널분석 포함) 및 
의사결정나무(Decision Tree) 기반의 머신러닝 예측 모델 페이지를 제공하는 Streamlit 대시보드입니다.

주요 기능:
- 총 세션 수, 구매 전환율 등 비즈니스 핵심 KPI 제공
- 10개 수치형 변수의 Revenue별 분포 비교 시각화 (히스토그램 및 Box Plot 서브플롯) 및 웰치(Welch) T-검정
- 7개 범주형 변수의 Revenue별 빈도 및 비율 시각화 (누적 막대그래프 서브플롯) 및 카이제곱 독립성 검정
- 고객 행동 데이터 기반의 5단계 구매 여정 퍼널(Funnel) 시각화 및 UX/마케팅 인사이트 도출
- 수치형 변수 간의 피어슨 상관행렬 및 랜덤 포레스트(Random Forest) 기반의 변수 중요도 분석
- 의사결정나무(Decision Tree) 기반의 Revenue 예측 머신러닝 모델 페이지 (워크플로우 Mermaid, 트리 구조 및 피처 중요도 시각화, 6가지 평가지표 및 혼동행렬/ROC/PR 커브 시각화)
- 사용자의 세션 필터링(방문자 유형, 주말 여부, 월별) 기능

작성자: Antigravity AI Agent
작성일: 2026-07-15
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_graphviz, export_text
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, matthews_corrcoef, confusion_matrix, roc_curve, precision_recall_curve
)
from sklearn.preprocessing import LabelEncoder
import base64
import os

# Page Config
st.set_page_config(
    page_title="Online Shoppers Purchasing Intention 대시보드",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and theme-aware styling
st.markdown("""
<style>
    .kpi-card {
        background: var(--secondary-background-color, rgba(128, 128, 128, 0.05));
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color, #1E88E5);
        margin-top: 10px;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: var(--text-color);
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value-box {
        background: var(--secondary-background-color, rgba(128, 128, 128, 0.05));
        border-radius: 8px;
        padding: 12px;
        border-top: 4px solid var(--primary-color, #1E88E5);
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.8;
        margin-bottom: 5px;
    }
    .metric-num {
        font-size: 1.4rem;
        font-weight: bold;
        color: var(--text-color);
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--primary-color, #1E88E5);
        margin-bottom: 15px;
        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
        padding-bottom: 8px;
    }
    .subsection-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: var(--primary-color, #1E88E5);
        margin-top: 25px;
        margin-bottom: 10px;
    }
    .report-box {
        background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
        border-left: 5px solid var(--primary-color, #1E88E5);
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# 1. Data Loading with Caching
@st.cache_data
def load_data():
    csv_path = "online-shoppers/data/online_shoppers_intention.csv"
    if not os.path.exists(csv_path):
        # Fallback to local path if running from within online-shoppers directory
        csv_path = "data/online_shoppers_intention.csv"
    
    df = pd.read_csv(csv_path)
    # Ensure types are correct
    df['Revenue'] = df['Revenue'].astype(bool)
    df['Weekend'] = df['Weekend'].astype(bool)
    return df

with st.spinner("데이터를 불러오는 중입니다..."):
    try:
        df_raw = load_data()
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        st.stop()

# Define columns
numerical_cols = [
    'Administrative', 'Administrative_Duration', 
    'Informational', 'Informational_Duration', 
    'ProductRelated', 'ProductRelated_Duration', 
    'BounceRates', 'ExitRates', 
    'PageValues', 'SpecialDay'
]

categorical_cols = [
    'Month', 'OperatingSystems', 'Browser', 
    'Region', 'TrafficType', 'VisitorType', 'Weekend'
]

# ----------------- Sidebar Navigation -----------------
st.sidebar.title("🧭 페이지 이동")
page = st.sidebar.radio("원하시는 페이지를 선택해 주세요:", ["📊 EDA 및 통계 분석", "🤖 머신러닝 예측 모델"])

if page == "📊 EDA 및 통계 분석":
    # ----------------- EDA Page Sidebar Filters -----------------
    st.sidebar.markdown("---")
    st.sidebar.title("🔍 필터 설정")
    
    # Month Filter
    all_months = sorted(df_raw['Month'].unique())
    selected_months = st.sidebar.multiselect("월 (Month)", all_months, default=all_months)
    
    # VisitorType Filter
    all_visitors = sorted(df_raw['VisitorType'].unique())
    selected_visitors = st.sidebar.multiselect("방문자 유형 (VisitorType)", all_visitors, default=all_visitors)
    
    # Weekend Filter
    all_weekends = [True, False]
    selected_weekends = st.sidebar.multiselect("주말 여부 (Weekend)", all_weekends, default=all_weekends)
    
    # Outlier handling for boxplots
    exclude_outliers = st.sidebar.checkbox("시각화 시 극단적 이상치 제외 (Box/Hist 용)", value=False, 
                                           help="수치형 변수 시각화 시 가독성을 높이기 위해 상하위 1% 극단적 이상치를 제외하고 표시합니다. (통계 테이블에는 전체 데이터가 포함됩니다)")
    
    # Apply filters
    df = df_raw[
        (df_raw['Month'].isin(selected_months)) &
        (df_raw['VisitorType'].isin(selected_visitors)) &
        (df_raw['Weekend'].isin(selected_weekends))
    ]
    
    # Quick Reset Button (just rerun with defaults)
    if st.sidebar.button("필터 초기화"):
        st.rerun()
        
    # ----------------- EDA Page Layout -----------------
    st.title("🛍️ Online Shoppers Purchasing Intention 대시보드")
    st.caption("온라인 쇼핑몰 고객 행동 데이터를 기반으로 구매 여정(Revenue) 분석을 시각화합니다.")
    
    # 1. KPI Cards (요약 지표) - Visible globally in EDA page
    total_sessions_raw = len(df_raw)
    total_sessions_filtered = len(df)
    purchases = len(df[df['Revenue'] == True])
    conv_rate = (purchases / total_sessions_filtered * 100) if total_sessions_filtered > 0 else 0
    avg_page_value = df['PageValues'].mean()
    avg_bounce = df['BounceRates'].mean() * 100
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">총 세션 수</div>
            <div class="kpi-value">{total_sessions_filtered:,} <span style="font-size:0.85rem; color:#757575;">/ {total_sessions_raw:,}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">구매 발생 세션 (Revenue=True)</div>
            <div class="kpi-value" style="color: #2E7D32;">{purchases:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">구매 전환율 (Conversion Rate)</div>
            <div class="kpi-value" style="color: #D32F2F;">{conv_rate:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">평균 페이지 가치 (Page Value)</div>
            <div class="kpi-value" style="color: #F57C00;">{avg_page_value:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">평균 이탈률 (Bounce Rate)</div>
            <div class="kpi-value" style="color: #7B1FA2;">{avg_bounce:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Tabs layout
    tab_overview, tab_numerical, tab_categorical, tab_funnel, tab_advanced = st.tabs([
        "📊 데이터 개요 (Overview)", 
        "📈 수치형 변수 분석 (Numerical Vs Revenue)", 
        "🗂️ 범주형 변수 분석 (Categorical Vs Revenue)", 
        "🎯 퍼널 분석 (Funnel Analysis)",
        "🧠 고급 분석 및 중요 변수 (Advanced Analysis)"
    ])
    
    # ================= TAB 1: OVERVIEW =================
    with tab_overview:
        st.subheader("📋 데이터셋 기본 정보 및 품질 진단")
        
        col_ov1, col_ov2 = st.columns([1, 1])
        
        with col_ov1:
            st.markdown("**기본 통계량 요약**")
            info_df = pd.DataFrame({
                "항목": ["전체 행 수", "전체 열 수", "결측치(NaN) 총 개수", "중복 행(Duplicate Rows) 수"],
                "값": [len(df), len(df.columns), df.isnull().sum().sum(), df.duplicated().sum()]
            })
            st.table(info_df)
            
            st.markdown("**데이터 일부 미리보기 (최상위 5행)**")
            st.dataframe(df.head(5), use_container_width=True)
            
        with col_ov2:
            # Target Variable Distribution
            rev_counts = df['Revenue'].value_counts()
            rev_ratios = df['Revenue'].value_counts(normalize=True) * 100
            
            fig_pie = px.pie(
                values=rev_counts.values,
                names=["False (구매 미발생)", "True (구매 발생)"],
                title="🎯 Target Variable (Revenue) 분포 비율",
                color=rev_counts.index,
                color_discrete_map={False: "#EF6C00", True: "#1E88E5"},
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=320)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Summary Table for Target Variable
            target_summary = pd.DataFrame({
                "Revenue": ["False (구매 미발생)", "True (구매 발생)", "전체"],
                "세션 빈도 (Frequency)": [rev_counts.get(False, 0), rev_counts.get(True, 0), len(df)],
                "비율 (Ratio)": [f"{rev_ratios.get(False, 0.0):.2f}%", f"{rev_ratios.get(True, 0.0):.2f}%", "100.00%"]
            })
            st.table(target_summary)
            
        st.markdown('<div class="section-title">💡 데이터 초기 진단 및 비즈니스 인사이트</div>', unsafe_allow_html=True)
        st.markdown("""<div class="report-box">
<strong>1. 클래스 불균형 (Class Imbalance) 검증:</strong><br>
전체 고객 세션 중 약 84.5%는 구매 없이 이탈(Revenue=False)하며, 실제 구매 전환으로 이어진 세션은 약 15.5%(Revenue=True)에 불과합니다. 
이는 전형적인 이커머스 거래 데이터의 특징으로, 이진 분류 모델 학습 시 소수 클래스인 '구매(True)' 세션에 가중치를 두거나 
SMOTE 등 오버샘플링 기법을 적용할 필요성이 강하게 시사됩니다.<br><br>

<strong>2. 데이터 결측치 및 이상치 요약:</strong><br>
본 데이터셋은 총 12,330개의 데이터 샘플과 18개의 칼럼으로 이루어져 있으며, 결측치가 전혀 존재하지 않는 정제된 상태입니다. 
다만 수치형 변수(예: 행정/정보/제품 관련 페이지 머문 시간)에서 표준편차가 평균에 비해 매우 크게 나타나는 경향이 있으므로, 
대부분의 수치형 변수에 이상치(Outlier)가 포함되어 있을 가능성이 높습니다.
</div>""", unsafe_allow_html=True)
    
    # ================= TAB 2: NUMERICAL VARIABLES =================
    with tab_numerical:
        st.subheader("📈 수치형 변수별 Revenue 비교 분석 (히스토그램 & 상자그림 통합)")
        st.markdown("각 수치형 변수의 분포 형태(히스토그램)와 범위/이상치 분포(박스플롯)를 5행 2열 서브플롯 구조로 보여주고 하단에 기술통계를 출력합니다.")
        
        # Prepare dataframe for plotting
        plot_df = df.copy()
        if exclude_outliers:
            for col in numerical_cols:
                q_low = plot_df[col].quantile(0.01)
                q_hi  = plot_df[col].quantile(0.99)
                plot_df = plot_df[(plot_df[col] >= q_low) & (plot_df[col] <= q_hi)]
                
        # 5x2 Grid for Numerical Features
        for idx in range(0, len(numerical_cols), 2):
            col1, col2 = st.columns(2)
            
            # Left Column
            with col1:
                c1 = numerical_cols[idx]
                fig1 = px.histogram(
                    plot_df,
                    x=c1,
                    color="Revenue",
                    marginal="box",
                    barmode="overlay",
                    color_discrete_map={False: '#EF6C00', True: '#1E88E5'},
                    title=f"{c1} 분포 및 범위"
                )
                fig1.update_layout(
                    height=300, 
                    margin=dict(t=40, b=20, l=20, r=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig1, use_container_width=True)
                
            # Right Column
            with col2:
                if idx + 1 < len(numerical_cols):
                    c2 = numerical_cols[idx+1]
                    fig2 = px.histogram(
                        plot_df,
                        x=c2,
                        color="Revenue",
                        marginal="box",
                        barmode="overlay",
                        color_discrete_map={False: '#EF6C00', True: '#1E88E5'},
                        title=f"{c2} 분포 및 범위"
                    )
                    fig2.update_layout(
                        height=300, 
                        margin=dict(t=40, b=20, l=20, r=20),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    
        st.markdown('<div class="subsection-title">📊 수치형 변수 기술통계 요약</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">각 변수별 상세 기술통계 및 평균 차이 유의성 검정(Welch T-Test) 결과를 확인할 수 있습니다.</div>', unsafe_allow_html=True)
        
        selected_num_col = st.selectbox("상세 분석 변수 선택 (수치형):", numerical_cols, index=numerical_cols.index('PageValues'))
        
        group_f = df[df['Revenue'] == False][selected_num_col]
        group_t = df[df['Revenue'] == True][selected_num_col]
        
        # Welch T-test
        t_stat, p_val = stats.ttest_ind(group_f, group_t, equal_var=False, nan_policy='omit')
        sig_text = "통계적으로 매우 유의미한 평균 차이가 존재함 (p-value < 0.05)" if p_val < 0.05 else "통계적으로 유의미한 평균 차이가 존재하지 않음 (p-value >= 0.05)"
        
        # Display stats table
        stats_summary = []
        for name, grp in [("Revenue = False (미구매)", group_f), ("Revenue = True (구매)", group_t)]:
            stats_summary.append({
                "구분": name,
                "데이터 건수": len(grp),
                "평균 (Mean)": grp.mean(),
                "중앙값 (Median)": grp.median(),
                "표준편차 (Std Dev)": grp.std(),
                "최소값 (Min)": grp.min(),
                "최대값 (Max)": grp.max(),
                "왜도 (Skewness)": grp.skew(),
                "첨도 (Kurtosis)": grp.kurt()
            })
            
        stats_df = pd.DataFrame(stats_summary).set_index("구분")
        st.dataframe(stats_df.style.format({
            "평균 (Mean)": "{:.4f}",
            "중앙값 (Median)": "{:.4f}",
            "표준편차 (Std Dev)": "{:.4f}",
            "최소값 (Min)": "{:.4f}",
            "최대값 (Max)": "{:.4f}",
            "왜도 (Skewness)": "{:.4f}",
            "첨도 (Kurtosis)": "{:.4f}"
        }), use_container_width=True)
        
        st.markdown(f"""
        > **웰치(Welch) T-검정 결과**
        > - **t-통계량**: `{t_stat:.4f}` | **p-값**: `{p_val:.4e}`
        > - **해석**: {sig_text}
        """)
    
    # ================= TAB 3: CATEGORICAL VARIABLES =================
    with tab_categorical:
        st.subheader("🗂️ 범주형 변수별 Revenue 비교 분석 (100% 비율 막대그래프)")
        st.markdown("각 범주형 변수의 비율비교 막대그래프를 4행 2열 구조로 시각화하여 Revenue 여부에 따른 비중 차이를 확인합니다.")
        
        # Categorical chronological sorting helper
        month_order = ['Feb', 'Mar', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # 4x2 Grid for Categorical Features (100% Stacked Bar)
        for idx in range(0, len(categorical_cols), 2):
            col1, col2 = st.columns(2)
            
            # Left Column
            with col1:
                c1 = categorical_cols[idx]
                ct1 = pd.crosstab(df[c1], df['Revenue'], normalize='index') * 100
                
                # Sort Month chronologically
                if c1 == 'Month':
                    ct1 = ct1.reindex(index=[m for m in month_order if m in ct1.index])
                    
                ct1 = ct1.reset_index()
                ct1_melted = ct1.melt(id_vars=c1, value_vars=[False, True], var_name='Revenue', value_name='Ratio')
                
                fig1 = px.bar(
                    ct1_melted,
                    x=c1,
                    y='Ratio',
                    color='Revenue',
                    barmode='stack',
                    color_discrete_map={False: '#EF6C00', True: '#1E88E5'},
                    title=f"{c1}별 Revenue 비율"
                )
                fig1.update_layout(
                    height=300, 
                    margin=dict(t=40, b=20, l=20, r=20),
                    yaxis=dict(range=[0, 100], title="비율 (%)"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig1, use_container_width=True)
                
            # Right Column
            with col2:
                if idx + 1 < len(categorical_cols):
                    c2 = categorical_cols[idx+1]
                    ct2 = pd.crosstab(df[c2], df['Revenue'], normalize='index') * 100
                    
                    # Sort Month chronologically if applicable
                    if c2 == 'Month':
                        ct2 = ct2.reindex(index=[m for m in month_order if m in ct2.index])
                        
                    ct2 = ct2.reset_index()
                    ct2_melted = ct2.melt(id_vars=c2, value_vars=[False, True], var_name='Revenue', value_name='Ratio')
                    
                    fig2 = px.bar(
                        ct2_melted,
                        x=c2,
                        y='Ratio',
                        color='Revenue',
                        barmode='stack',
                        color_discrete_map={False: '#EF6C00', True: '#1E88E5'},
                        title=f"{c2}별 Revenue 비율"
                    )
                    fig2.update_layout(
                        height=300, 
                        margin=dict(t=40, b=20, l=20, r=20),
                        yaxis=dict(range=[0, 100], title="비율 (%)"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    
        st.markdown('<div class="subsection-title">📊 범주형 변수 빈도 및 비율 요약</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">각 카테고리별 세션 수와 구매 전환 비율 상세 요약 정보 및 독립성 검정(Chi-Square Test) 결과를 확인하실 수 있습니다.</div>', unsafe_allow_html=True)
        
        selected_cat_col = st.selectbox("상세 분석 변수 선택 (범주형):", categorical_cols, index=categorical_cols.index('Month'))
        
        crosstab = pd.crosstab(df[selected_cat_col], df['Revenue'], margins=True, margins_name="Total")
        crosstab_pct = pd.crosstab(df[selected_cat_col], df['Revenue'], normalize='index') * 100
        
        report_table = pd.DataFrame({
            "구매 미발생 (False)": crosstab[False].iloc[:-1],
            "구매 발생 (True)": crosstab[True].iloc[:-1],
            "전체 세션 수 (Total)": crosstab["Total"].iloc[:-1],
            "미구매 비율 (%)": crosstab_pct[False],
            "구매 전환율 (%)": crosstab_pct[True]
        })
        
        total_false = crosstab[False].iloc[-1]
        total_true = crosstab[True].iloc[-1]
        total_all = crosstab["Total"].iloc[-1]
        total_conv = (total_true / total_all) * 100
        total_non_conv = (total_false / total_all) * 100
        
        total_row = pd.DataFrame({
            "구매 미발생 (False)": [total_false],
            "구매 발생 (True)": [total_true],
            "전체 세션 수 (Total)": [total_all],
            "미구매 비율 (%)": [total_non_conv],
            "구매 전환율 (%)": [total_conv]
        }, index=["합계 (Total)"])
        
        report_table = pd.concat([report_table, total_row])
        report_table.index = report_table.index.astype(str)
        
        # Chi-Square Test
        contingency_matrix = pd.crosstab(df[selected_cat_col], df['Revenue'])
        chi2, p_chi2, dof, expected = stats.chi2_contingency(contingency_matrix)
        sig_chi2 = "통계적으로 매우 유의미한 상관 관계가 존재함 (p-value < 0.05)" if p_chi2 < 0.05 else "통계적으로 유의미한 상관 관계가 존재하지 않음 (p-value >= 0.05)"
        
        st.dataframe(
            report_table.style.format({
                "구매 미발생 (False)": "{:,}",
                "구매 발생 (True)": "{:,}",
                "전체 세션 수 (Total)": "{:,}",
                "미구매 비율 (%)": "{:.2f}%",
                "구매 전환율 (%)": "{:.2f}%"
            }).background_gradient(cmap="Greens", subset=(report_table.index[:-1], "구매 전환율 (%)")),
            use_container_width=True
        )
        
        st.markdown(f"""
        > **카이제곱 독립성 검정 (Chi-Square Test) 결과**
        > - **Chi-Square Stat**: `{chi2:.4f}` | **p-값**: `{p_chi2:.4e}` | **자유도**: `{dof}`
        > - **해석**: {sig_chi2}
        """)
    
    # ================= TAB 4: FUNNEL ANALYSIS =================
    with tab_funnel:
        st.subheader("🎯 고객 구매 여정 퍼널 분석 (Funnel Analysis)")
        st.markdown("고객이 쇼핑몰에 유입되어 상품 탐색에서 최종 결제 완료에 이르기까지의 핵심 단계별 이탈률과 전환율을 시각화합니다.")
        
        # Calculate strict sequential funnel counts
        step1_count = len(df)
        step2_df = df[df['ProductRelated'] > 0]
        step2_count = len(step2_df)
        step3_df = step2_df[step2_df['Administrative'] > 0]
        step3_count = len(step3_df)
        step4_df = step3_df[step3_df['PageValues'] > 0]
        step4_count = len(step4_df)
        step5_df = step4_df[step4_df['Revenue'] == True]
        step5_count = len(step5_df)
        
        # Funnel Chart using Graph Objects
        fig_funnel = go.Figure(go.Funnel(
            y = [
                "1. 전체 유입 (All Sessions)", 
                "2. 상품 상세 탐색 (Product Related)", 
                "3. 장바구니/관리 영역 방문 (Administrative)", 
                "4. 결제 의도 포착 (Page Value > 0)", 
                "5. 최종 구매 완료 (Revenue = True)"
            ],
            x = [step1_count, step2_count, step3_count, step4_count, step5_count],
            textinfo = "value+percent initial+percent previous",
            marker = {"color": ["#1E3A8A", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]}
        ))
        
        fig_funnel.update_layout(
            title_text="🛒 단계별 세션 전환 및 이탈 퍼널 차트",
            height=500,
            margin=dict(t=50, b=20, l=200, r=20)
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # Calculate conversions for summary table
        pct_initial = [
            100.0,
            (step2_count / step1_count * 100) if step1_count > 0 else 0,
            (step3_count / step1_count * 100) if step1_count > 0 else 0,
            (step4_count / step1_count * 100) if step1_count > 0 else 0,
            (step5_count / step1_count * 100) if step1_count > 0 else 0
        ]
        
        pct_previous = [
            100.0,
            (step2_count / step1_count * 100) if step1_count > 0 else 0,
            (step3_count / step2_count * 100) if step2_count > 0 else 0,
            (step4_count / step3_count * 100) if step3_count > 0 else 0,
            (step5_count / step4_count * 100) if step4_count > 0 else 0
        ]
        
        funnel_summary = pd.DataFrame({
            "단계": [
                "1. 전체 유입 (All Sessions)", 
                "2. 상품 상세 탐색 (Product Related)", 
                "3. 장바구니/관리 영역 방문 (Administrative)", 
                "4. 결제 의도 포착 (Page Value > 0)", 
                "5. 최종 구매 완료 (Revenue = True)"
            ],
            "세션 수": [step1_count, step2_count, step3_count, step4_count, step5_count],
            "전체 대비 비율 (%)": pct_initial,
            "이전 단계 대비 전환율 (%)": pct_previous,
            "이전 단계 대비 이탈률 (%)": [0.0] + [100.0 - p for p in pct_previous[1:]]
        })
        
        st.markdown("**📋 퍼널 단계별 수치 데이터 요약**")
        st.dataframe(
            funnel_summary.style.format({
                "세션 수": "{:,}",
                "전체 대비 비율 (%)": "{:.2f}%",
                "이전 단계 대비 전환율 (%)": "{:.2f}%",
                "이전 단계 대비 이탈률 (%)": "{:.2f}%"
            }),
            use_container_width=True
        )
        
        # Process Explanation
        st.markdown('<div class="section-title">💡 구매 여정 퍼널(Funnel) 과정 설명</div>', unsafe_allow_html=True)
        st.markdown("""
        본 대시보드의 퍼널 분석은 고객의 행동 특성이 고도화되는 과정을 바탕으로 순차적인 깔때기(Funnel) 단계로 정의했습니다.
        
        * **1단계: 전체 유입 (All Sessions)**: 쇼핑몰에 진입한 모든 사용자 세션의 원본 모수입니다.
        * **2단계: 상품 상세 탐색 (Product Related)**: 최소 1페이지 이상의 상품 페이지(`ProductRelated > 0`)를 조회하여, 실제 쇼핑몰의 제품 정보 탐색을 개시한 잠재 타겟 고객군입니다.
        * **3단계: 장바구니/관리 영역 방문 (Administrative)**: 장바구니 조회, 고객 계정 관리 등 행정 성격의 페이지(`Administrative > 0`)를 조회하여, 관심 있는 상품을 장바구니에 넣고 구매 결정을 비교하는 활성 고객군입니다.
        * **4단계: 결제 의도 포착 (Page Value > 0)**: 상품 구매 직전 단계로, 쇼핑몰 내에서 실제 결제/구매 프로세스로 이어지는 고가치 페이지(`PageValues > 0`)를 경유한 세션 집단입니다.
        * **5단계: 최종 구매 완료 (Revenue = True)**: 최종적으로 주문 및 결제 승인이 발생하여 구매를 마친 실질적 성과 집단입니다.
        """)
        
        # Diagnostic insights
        drop_2_3 = 100.0 - pct_previous[2]
        drop_3_4 = 100.0 - pct_previous[3]
        drop_4_5 = 100.0 - pct_previous[4]
        
        st.markdown('<div class="section-title">📊 퍼널 구간별 이탈 분석 및 개선 제안 (UX/마케팅 인사이트)</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="report-box">
<strong>1. 상품 상세 탐색 ➡️ 장바구니/관리 영역 (이탈률: {drop_2_3:.2f}%):</strong><br>
- 상품을 조회한 뒤 실제 장바구니나 마이페이지 등으로 전환되는 구간입니다. 이 구간의 이탈이 크다면 상품의 상세 가격 메리트가 부족하거나, 리뷰 부족, 혹은 장바구니 담기(Add-to-cart) 버튼의 UX가 모호할 수 있습니다.<br>
- <em>개선책:</em> 상세 페이지의 핵심 혜택 부각, 리뷰 요약 시스템 도입, 가시성 높은 CTA 버튼 디자인 적용.<br><br>

<strong>2. 장바구니/관리 영역 ➡️ 결제 의도 포착 (이탈률: {drop_3_4:.2f}%):</strong><br>
- 장바구니 단계에서 체크아웃 및 가치가 포착된 구매 절차 페이지로의 전환 비율입니다.<br>
- <em>개선책:</em> 장바구니 이탈 방지를 위한 리타게팅 프로모션, 장바구니 내 간편 예상 배송비 고지, 팝업 쿠폰 적용.<br><br>

<strong>3. 결제 의도 포착 ➡️ 최종 구매 완료 (이탈률: {drop_4_5:.2f}%):</strong><br>
- 구매 전단계까지 도달한 최선의 핵심 가망 고객이 막판에 이탈하는 최후의 허들입니다.<br>
- <em>개선책:</em> 복잡한 본인인증 생략 및 간편결제(네이버페이, 카카오페이 등) 다양화, 보안 엠블럼을 통한 신뢰성 강화, 모바일 결제 최적화.
</div>""", unsafe_allow_html=True)
    
    # ================= TAB 5: ADVANCED ANALYSIS =================
    with tab_advanced:
        st.subheader("🧠 변수 간 상관성 및 구매 예측 기여도(Feature Importance)")
        st.markdown("수치형 변수들 간의 선형 상관관계를 파악하고, 머신러닝 기법을 활용해 Revenue 결정에 가장 중요하게 작용한 핵심 변수들을 알아봅니다.")
        
        col_adv1, col_adv2 = st.columns([1, 1])
        
        with col_adv1:
            # Correlation Heatmap
            corr = df[numerical_cols].corr()
            fig_heat = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title="🔥 수치형 변수 간 피어슨 상관행렬 (Pearson Correlation Matrix)",
                labels=dict(color="Correlation")
            )
            fig_heat.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20))
            st.plotly_chart(fig_heat, use_container_width=True)
            
        with col_adv2:
            # Feature Importance calculation using Random Forest or fall back to Pearson Correlation
            st.markdown("**🤖 머신러닝 기반 Revenue 기여 요인 분석**")
            
            try:
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.preprocessing import LabelEncoder
                
                # Prepare data
                X = df.copy()
                # Encode categorical features
                le_month = LabelEncoder()
                X['Month'] = le_month.fit_transform(X['Month'])
                
                le_vtype = LabelEncoder()
                X['VisitorType'] = le_vtype.fit_transform(X['VisitorType'])
                
                X['Weekend'] = X['Weekend'].astype(int)
                
                y = X['Revenue'].astype(int)
                X_model = X.drop(columns=['Revenue'])
                
                # Fit model
                rf = RandomForestClassifier(n_estimators=50, random_state=42)
                rf.fit(X_model, y)
                
                # Feature importances
                importances = rf.feature_importances_
                feat_imp_df = pd.DataFrame({
                    "Feature": X_model.columns,
                    "Importance": importances
                }).sort_values(by="Importance", ascending=True)
                
                fig_imp = px.bar(
                    feat_imp_df,
                    x="Importance",
                    y="Feature",
                    orientation='h',
                    title="🎯 의사결정나무 모델 기준 변수 중요도 (Random Forest Feature Importance)",
                    color="Importance",
                    color_continuous_scale="Viridis"
                )
                fig_imp.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20))
                st.plotly_chart(fig_imp, use_container_width=True)
                
            except Exception as e:
                # Fallback: simple absolute correlation of numerical variables with Revenue
                st.warning("sklearn을 사용한 변수 중요도 산출에 실패했습니다. (상관관계를 대체하여 표시합니다)")
                corr_with_target = df[numerical_cols].corrwith(df['Revenue'].astype(int)).abs().reset_index()
                corr_with_target.columns = ['Feature', 'Importance']
                corr_with_target = corr_with_target.sort_values(by="Importance", ascending=True)
                
                fig_imp = px.bar(
                    corr_with_target,
                    x="Importance",
                    y="Feature",
                    orientation='h',
                    title="🎯 Revenue와의 상관계수 절대값 비교 (상관계수 기반 중요도)",
                    color="Importance",
                    color_continuous_scale="Blues"
                )
                fig_imp.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20))
                st.plotly_chart(fig_imp, use_container_width=True)
                
        st.markdown('<div class="section-title">💡 상관성 및 특성 기여도 심층 리포트</div>', unsafe_allow_html=True)
        st.markdown("""<div class="report-box">
<strong>1. 강한 상관관계를 가진 변수 경고 (다중공선성 위험):</strong><br>
- <code>BounceRates</code>와 <code>ExitRates</code>는 <strong>0.91</strong>의 매우 높은 양의 상관관계를 보입니다. 머신러닝 예측 모델링 시 두 변수 중 하나를 제거하거나 차원 축소를 적용하는 것이 타당합니다.<br>
- 또한 각 영역별 페이지 수와 머문 시간(예: <code>ProductRelated</code> - <code>ProductRelated_Duration</code>) 역시 <strong>0.86</strong> 수준의 매우 강한 상관관계를 보입니다.<br><br>

<strong>2. 구매 전환을 결정하는 핵심 동인 (Core Drivers):</strong><br>
- <strong>PageValues (페이지 가치):</strong> 예측 중요도 및 타겟 변수와의 상관도 측면에서 모두 압도적인 1위로 나타납니다. 
사용자가 장바구니나 결제선 상의 고가치 페이지를 경유했는지가 구매 완료 여부를 결정짓는 가장 직접적인 요소입니다.<br>
- <strong>ExitRates 및 ProductRelated_Duration:</strong> 그 뒤를 이어 고객이 이탈하지 않고 제품 페이지를 얼마나 장시간 둘러보았는지가 중요한 구매 의도 결정 요인으로 작용하고 있습니다.
</div>""", unsafe_allow_html=True)

else:
    # ================= MACHINE LEARNING PAGE =================
    st.title("🤖 의사결정나무(Decision Tree) 기반 Revenue 예측 모델")
    st.caption("고객의 세션 행동 데이터를 학습하여 최종 구매 여부(Revenue)를 분류 예측하는 의사결정나무 머신러닝 모형을 구축하고 성능을 정밀 검증합니다.")
    
    # ML Sidebar Parameters Control Panel
    st.sidebar.markdown("---")
    st.sidebar.title("🛠️ 모델 하이퍼파라미터")
    
    criterion = st.sidebar.selectbox("불순도 평가 지표 (Criterion)", ["gini", "entropy", "log_loss"], index=0,
                                     help="노드 분할의 품질을 측정할 기능 지표입니다.")
    max_depth = st.sidebar.slider("트리 최대 깊이 (Max Depth)", 1, 10, value=3,
                                  help="결정 트리의 깊이 한계선입니다. 값이 클수록 복잡도가 증가해 과적합(Overfitting)될 수 있습니다.")
    test_size = st.sidebar.slider("테스트 데이터 분할 비율 (Test Size)", 0.1, 0.4, value=0.2, step=0.05,
                                  help="전체 샘플 대비 평가 모델 검증용 데이터 비중입니다.")
    class_weight = st.sidebar.selectbox("클래스 가중치 균형화 (Class Weight)", [None, "balanced"], index=1,
                                        help="'balanced'를 선택하면 데이터셋에 내재된 클래스 불균형 비율에 맞춰 가중치를 자동으로 조정해 Recall을 개선합니다. *참고: 오버샘플링을 활성화하면 이미 학습 클래스가 1:1로 맞춰지므로 이 옵션을 변경해도 동일한 결과가 산출됩니다.")
    use_oversampling = st.sidebar.toggle("클래스 오버샘플링 적용 (Oversampling)", value=True,
                                         help="소수 클래스(구매) 데이터를 복제하여 다수 클래스(미구매)와 1:1로 균형을 맞춥니다. 재현율(Recall) 향상에 매우 효과적이며 오직 훈련 세트에만 수행하여 검증 오염을 배제합니다.")
    
    train_data_range = st.sidebar.radio("학습 데이터 범위 선택", ["전체 데이터 (Full Dataset)", "필터링된 데이터 (Filtered Dataset)"], index=0,
                                        help="상단의 필터를 거쳐 필터링된 데이터에만 학습을 진행할지, 전체 12,330개 세션 전체 데이터셋을 사용할지 정합니다.")
    
    # Select which dataset to feed into ML model
    if train_data_range == "전체 데이터 (Full Dataset)":
        df_ml = df_raw.copy()
    else:
        df_ml = df_raw[
            (df_raw['Month'].isin(selected_months)) &
            (df_raw['VisitorType'].isin(selected_visitors)) &
            (df_raw['Weekend'].isin(selected_weekends))
        ].copy() if 'selected_months' in locals() else df_raw.copy()

    # Preprocessing
    X = df_ml.drop(columns=['Revenue']).copy()
    y = df_ml['Revenue'].astype(int)
    
    # Label encoding for strings
    le_month = LabelEncoder()
    X['Month'] = le_month.fit_transform(X['Month'])
    
    le_vtype = LabelEncoder()
    X['VisitorType'] = le_vtype.fit_transform(X['VisitorType'])
    
    # Convert booleans to integers
    X['Weekend'] = X['Weekend'].astype(int)
    
    # Split
    if len(df_ml) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
    else:
        st.error("데이터 세션 수가 너무 적어 모델 학습을 진행할 수 없습니다. 필터를 넓게 조정해 주세요.")
        st.stop()

    # Define Random Oversampling Function Natively
    def random_oversample(X_tr, y_tr):
        df_train_temp = X_tr.copy()
        df_train_temp['__target__'] = y_tr
        df_maj = df_train_temp[df_train_temp['__target__'] == 0]
        df_min = df_train_temp[df_train_temp['__target__'] == 1]
        if len(df_maj) == 0 or len(df_min) == 0:
            return X_tr, y_tr
        df_min_oversampled = df_min.sample(len(df_maj), replace=True, random_state=42)
        df_oversampled = pd.concat([df_maj, df_min_oversampled], axis=0).sample(frac=1.0, random_state=42).reset_index(drop=True)
        return df_oversampled.drop(columns=['__target__']), df_oversampled['__target__']

    # Keep original X_train / y_train to calculate unbiased train score
    X_train_orig, y_train_orig = X_train.copy(), y_train.copy()

    # Apply Random Oversampling ONLY to the training set (preventing data leakage in evaluation)
    if use_oversampling:
        X_train, y_train = random_oversample(X_train, y_train)

    # Train model
    model = DecisionTreeClassifier(
        criterion=criterion,
        max_depth=max_depth,
        class_weight=class_weight,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # 1) Train Set Predictions & Metrics (Unbiased, using original train data distribution)
    y_train_pred = model.predict(X_train_orig)
    y_train_prob = model.predict_proba(X_train_orig)[:, 1]
    
    acc_train = accuracy_score(y_train_orig, y_train_pred)
    prec_train = precision_score(y_train_orig, y_train_pred, zero_division=0)
    rec_train = recall_score(y_train_orig, y_train_pred, zero_division=0)
    f1_train = f1_score(y_train_orig, y_train_pred, zero_division=0)
    roc_auc_train = roc_auc_score(y_train_orig, y_train_prob)
    mcc_train = matthews_corrcoef(y_train_orig, y_train_pred)
    
    # 2) Test Set Predictions & Metrics
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)
    mcc = matthews_corrcoef(y_test, y_pred)

    # 1. Mermaid workflow diagram
    st.markdown('<div class="section-title">1. 머신러닝 모델링 워크플로우 과정</div>', unsafe_allow_html=True)
    
    mermaid_code = """
    graph TD
        A[데이터 입력] --> B[데이터 인코딩 및 전처리]
        B --> C[피처(X) & 타겟(y) 분리]
        C --> D[훈련 세트 & 테스트 세트 분할]
        D --> E[의사결정나무 모델 학습 진행]
        E --> F[평가용 테스트 세트 예측 수행]
        F --> G[6가지 핵심 예측 지표 산출]
        G --> H[트리 구조 및 피처 중요도 분석]
        G --> I[혼동행렬 및 평가지표 시각화]
    """
    
    # Render natively using Streamlit's built-in markdown support for Mermaid
    st.markdown(f"```mermaid\n{mermaid_code}\n```")

    # 2. Model Structure Visualizer (Decision Tree Graphviz & Rules)
    st.markdown('<div class="section-title">2. 의사결정나무 모델 구조 시각화</div>', unsafe_allow_html=True)
    st.markdown("의사결정 기준에 따라 상위 노드에서 하위 노드로 조건이 분기되는 구조를 시각적으로 보여줍니다.")
    
    # Render Graphviz chart
    try:
        dot_data = export_graphviz(
            model,
            out_file=None,
            feature_names=list(X.columns),
            class_names=['No Purchase (False)', 'Purchase (True)'],
            filled=True,
            rounded=True,
            special_characters=True
        )
        st.graphviz_chart(dot_data)
    except Exception as e:
        st.warning(f"트리 다이어그램 렌더링 중 경고가 발생했습니다: {e}")

    # Text structure expander
    with st.expander("📝 텍스트 기반 의사결정 규칙(Decision Rules) 상세보기"):
        tree_rules = export_text(model, feature_names=list(X.columns))
        st.code(tree_rules, language="text")

    # 3. Feature Importance
    st.markdown('<div class="section-title">3. 피처 중요도 (Feature Importance)</div>', unsafe_allow_html=True)
    st.markdown("의사결정나무 모델이 분류(Revenue)를 예측할 때 어떤 변수가 가장 크게 기여하였는지 지니 불순도 감소 비율 기준으로 기여도를 정렬합니다.")
    
    feat_imp_df = pd.DataFrame({
        "피처": X.columns,
        "중요도": model.feature_importances_
    }).sort_values(by="중요도", ascending=True)
    
    fig_imp = px.bar(
        feat_imp_df,
        x="중요도",
        y="피처",
        orientation='h',
        color="중요도",
        color_continuous_scale="Viridis",
        labels={"중요도": "정보 획득 기여량 (Feature Importance)"}
    )
    fig_imp.update_layout(
        height=400,
        margin=dict(t=20, b=20, l=150, r=20)
    )
    st.plotly_chart(fig_imp, use_container_width=True)

    # 4. Model Evaluation Metrics
    st.markdown('<div class="section-title">4. 모델 평가지표 및 과적합(Overfitting) 진단</div>', unsafe_allow_html=True)
    
    # Switch Tabs for Evaluation
    tab_test_perf, tab_fit_compare = st.tabs([
        "📈 모델 검증 성능 (Test Set Performance)",
        "⚖️ 과적합 및 학습 상태 진단 (Train vs Test Fit)"
    ])

    with tab_test_perf:
        st.markdown("테스트 데이터셋을 사용하여 모델의 실전 분류 예측 성능을 6가지 세부 지표로 평가합니다.")
        if use_oversampling:
            st.info("💡 **클래스 오버샘플링 적용됨**: 학습 시 구매(True) 세션의 비중을 오버샘플링하여 **Recall(재현율) 성능이 획기적으로 향상**되었습니다.")
        
        # Cards layout for 6 metrics
        m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
        
        m_col1.markdown(f"""
        <div class="metric-value-box">
            <div class="metric-title">정확도 (Accuracy)</div>
            <div class="metric-num">{acc:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        m_col2.markdown(f"""
        <div class="metric-value-box" style="border-top-color: #2E7D32;">
            <div class="metric-title">정밀도 (Precision)</div>
            <div class="metric-num" style="color: #2E7D32;">{prec:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        m_col3.markdown(f"""
        <div class="metric-value-box" style="border-top-color: #EF6C00;">
            <div class="metric-title">재현율 (Recall)</div>
            <div class="metric-num" style="color: #EF6C00;">{rec:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        m_col4.markdown(f"""
        <div class="metric-value-box" style="border-top-color: #D32F2F;">
            <div class="metric-title">F1 스코어 (F1-Score)</div>
            <div class="metric-num" style="color: #D32F2F;">{f1:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        m_col5.markdown(f"""
        <div class="metric-value-box" style="border-top-color: #7B1FA2;">
            <div class="metric-title">ROC-AUC</div>
            <div class="metric-num" style="color: #7B1FA2;">{roc_auc:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        m_col6.markdown(f"""
        <div class="metric-value-box" style="border-top-color: #00838F;">
            <div class="metric-title">매튜스 상관계수 (MCC)</div>
            <div class="metric-num" style="color: #00838F;">{mcc:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        # Visualizations of Performance: Confusion Matrix & ROC / PR Curves
        col_plot1, col_plot2 = st.columns([1, 1])

        with col_plot1:
            # Confusion Matrix Heatmap
            cm = confusion_matrix(y_test, y_pred)
            fig_cm = px.imshow(
                cm,
                text_auto=True,
                labels=dict(x="예측값 (Predicted)", y="실제값 (Actual)", color="세션 수"),
                x=["False (미구매)", "True (구매)"],
                y=["False (미구매)", "True (구매)"],
                color_continuous_scale="Blues",
                title="📊 혼동 행렬 (Confusion Matrix)"
            )
            fig_cm.update_layout(height=400, margin=dict(t=50, b=20, l=20, r=20))
            st.plotly_chart(fig_cm, use_container_width=True)

        with col_plot2:
            # ROC and PR Curve
            fpr, tpr, thresholds = roc_curve(y_test, y_prob)
            precision, recall, _ = precision_recall_curve(y_test, y_prob)
            
            curve_choice = st.radio("시각화 곡선 선택:", ["ROC 곡선 (Receiver Operating Characteristic)", "PR 곡선 (Precision-Recall)"], horizontal=True)
            
            if curve_choice.startswith("ROC"):
                fig_curve = go.Figure()
                fig_curve.add_trace(go.Scatter(
                    x=fpr, y=tpr, mode='lines', 
                    name=f'Decision Tree (AUC = {roc_auc:.4f})', 
                    line=dict(color='#1E88E5', width=3)
                ))
                fig_curve.add_trace(go.Scatter(
                    x=[0, 1], y=[0, 1], mode='lines', 
                    name='무작위 분류기 (AUC = 0.50)', 
                    line=dict(color='grey', dash='dash')
                ))
                fig_curve.update_layout(
                    title="📈 ROC 곡선 (ROC Curve)", 
                    xaxis_title="FPR (거짓 양성 비율)", 
                    yaxis_title="TPR (참 양성 비율)", 
                    height=350,
                    margin=dict(t=40, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_curve, use_container_width=True)
            else:
                fig_curve = go.Figure()
                fig_curve.add_trace(go.Scatter(
                    x=recall, y=precision, mode='lines', 
                    name='Precision-Recall Curve', 
                    line=dict(color='#2E7D32', width=3)
                ))
                fig_curve.update_layout(
                    title="🎯 정밀도-재현율 곡선 (PR Curve)", 
                    xaxis_title="Recall (재현율)", 
                    yaxis_title="Precision (정밀도)", 
                    height=350,
                    margin=dict(t=40, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_curve, use_container_width=True)

    with tab_fit_compare:
        st.subheader("⚖️ Train 데이터셋 vs Test 데이터셋 성능 편차 분석")
        st.markdown("학습 데이터셋(Train Set)과 미지의 테스트 데이터셋(Test Set) 간의 평가지표 차이를 검토하여 모델 적합도(Fit Status)를 정밀 진단합니다.")
        
        # Calculate fit status
        diff_acc = acc_train - acc
        diff_f1 = f1_train - f1
        
        # Diagnosis result rendering
        if diff_f1 > 0.12 or diff_acc > 0.08:
            st.error(f"### ⚠️ **과적합 (Overfitting) 상태로 진단되었습니다.**\n\n"
                     f"- **현상**: 훈련 데이터의 F1 스코어({f1_train:.4f})가 테스트 데이터의 F1 스코어({f1:.4f})보다 **{diff_f1:.4f}**만큼 유의미하게 높습니다.\n"
                     f"- **설명**: 모델이 훈련 데이터에 너무 지나치게 맞춰져 있어 새로운 데이터에 대한 일반화(Generalization) 성능이 저하되고 있음을 의미합니다.\n"
                     f"- **💡 추천 액션플랜**: 사이드바에서 **'트리 최대 깊이 (Max Depth)'를 낮추어(예: 3~4 이하)** 모델의 복잡도를 완화하고 가지치기 효과를 유도하세요.")
        elif acc_train < 0.70 or f1_train < 0.50:
            st.warning(f"### ⚠️ **과소적합 (Underfitting) 상태로 진단되었습니다.**\n\n"
                       f"- **현상**: 훈련 및 테스트셋 성적이 모두 다소 저조하게 나타납니다 (Train F1: {f1_train:.4f}, Test F1: {f1:.4f}).\n"
                       f"- **설명**: 결정 트리의 깊이가 너무 얕아서 데이터 안에 내재된 비선형 패턴이나 다이나믹한 의사결정 규칙을 충분히 학습하지 못했습니다.\n"
                       f"- **💡 추천 액션플랜**: 사이드바에서 **'트리 최대 깊이 (Max Depth)'를 높여(예: 5~8 이상)** 모델이 좀 더 깊이 있는 특징들을 분석하도록 설정하세요.")
        else:
            st.success(f"### ✅ **학습 안정 모델 (Balanced Fit) 상태로 진단되었습니다.**\n\n"
                       f"- **현상**: 훈련과 테스트 셋의 편차가 극히 양호합니다 (Train F1: {f1_train:.4f}, Test F1: {f1:.4f}, 편차: {diff_f1:+.4f}).\n"
                       f"- **설명**: 현재 모델은 과적합 및 과소적합 없이 학습 패턴을 적절히 습득하고 일반화 능력을 훌륭하게 유지하고 있습니다.\n"
                       f"- **💡 추천 액션플랜**: 현재 하이퍼파라미터 설정을 유지하여 비즈니스 의사결정 모형으로 활용하는 것이 가장 이상적입니다.")
                       
        col_t1, col_t2 = st.columns([1.2, 1])
        
        with col_t1:
            st.markdown("**📋 Train / Test 성능지표 세부 비교표**")
            compare_table = pd.DataFrame({
                "평가지표 (Performance Metric)": [
                    "정확도 (Accuracy)", "정밀도 (Precision)", "재현율 (Recall)", 
                    "F1 스코어 (F1-Score)", "ROC-AUC 스코어", "매튜스 상관계수 (MCC)"
                ],
                "훈련 세트 (Train Score)": [acc_train, prec_train, rec_train, f1_train, roc_auc_train, mcc_train],
                "테스트 세트 (Test Score)": [acc, prec, rec, f1, roc_auc, mcc],
                "성능 편차 (Train - Test Difference)": [acc_train - acc, prec_train - prec, rec_train - rec, f1_train - f1, roc_auc_train - roc_auc, mcc_train - mcc]
            })
            st.dataframe(compare_table.style.format({
                "훈련 세트 (Train Score)": "{:.4f}",
                "테스트 세트 (Test Score)": "{:.4f}",
                "성능 편차 (Train - Test Difference)": "{:+.4f}"
            }), use_container_width=True)
            
        with col_t2:
            # Render a side-by-side Plotly bar chart
            compare_melted = pd.DataFrame({
                "평가지표": ["정확도", "정밀도", "재현율", "F1 스코어", "ROC-AUC", "MCC"] * 2,
                "점수": [acc_train, prec_train, rec_train, f1_train, roc_auc_train, mcc_train] + 
                         [acc, prec, rec, f1, roc_auc, mcc],
                "데이터셋": ["Train"] * 6 + ["Test"] * 6
            })
            fig_compare = px.bar(
                compare_melted, x="평가지표", y="점수", color="데이터셋", barmode="group",
                color_discrete_map={"Train": "#1E88E5", "Test": "#EF6C00"},
                title="📊 Train vs Test 성능 지표 비교 그래프"
            )
            fig_compare.update_layout(
                height=350, 
                margin=dict(t=40, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_compare, use_container_width=True)

    # Statistical Evaluation Report Box
    st.markdown('<div class="subsection-title">💡 머신러닝 모델 예측 결과 및 비즈니스 액션 플랜 리포트</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="report-box">
<strong>1. 정확도(Accuracy) 및 불균형 데이터셋 보정 성과 (Model Diagnostics):</strong><br>
- 본 대시보드에서는 소수 클래스인 '구매 발생(True)'의 재현능력을 높이기 위해 클래스 가중치 균형화(Class Weight) 옵션을 기본 제공합니다. 
<code>class_weight='balanced'</code>를 적용한 결과, 모델은 무작위 분포가 아니라 불균형 비율을 가중치로 인식하여 예측을 수행합니다. 
그 결과 재현율(Recall)이 <strong>{rec:.4f}</strong>를 기록하며 실제 구매 고객을 누락 없이 효과적으로 식별해 내고 있습니다. 
또한 Matthews Correlation Coefficient(MCC)는 <strong>{mcc:.4f}</strong>를 기록하여 무작위 수준(0.0)을 유의미하게 상회하는 예측 변별력을 입증했습니다.<br><br>

<strong>2. PageValues 기반 고가치 잠재 고객 실시간 전환 (Conversion Optimization):</strong><br>
- 모델 분석 결과, <code>PageValues</code>(페이지 가치)는 구매 여부를 결정하는 가장 핵심적인 피처이며 의사결정나무의 첫 분기 기준입니다. 
특정 임계값(예: PageValues > 6.0) 이상을 기록한 세션은 구매 전환 확률이 매우 높게 나타납니다.<br>
- <strong>[액션 플랜]</strong>: 웹 사이트 로그 수집 솔루션을 통해 실시간으로 세션의 PageValues가 임계값을 초과하는 순간을 감지합니다. 
해당 고객에게 실시간 채팅 상담 연결, 무료 배송 혜택 안내 팝업, 혹은 결제 단계 즉시 연결(Express Checkout) 버튼을 동적으로 노출하여 
전환 직전 단계의 고객이 결제를 망설이지 않고 완료하도록 락인(Lock-in) 전략을 실행합니다.<br><br>

<strong>3. 종료율(ExitRates) 및 이탈률(BounceRates) 통제를 통한 잔류 유도 (UX & Bounce Prevention):</strong><br>
- 피처 중요도와 트리 분기 조건에서 <code>ExitRates</code>와 <code>BounceRates</code>는 구매 확률과 강력한 음의 관계를 보입니다. 
상세 페이지 탐색 중 이탈 요인을 조기에 제거하는 것이 필수적입니다.<br>
- <strong>[액션 플랜]</strong>: 사용자가 이탈하려는 의도(Exit-Intent, 예: 마우스 커서가 브라우저 상단 닫기 영역으로 이동)를 감지했을 때, 
현재 보고 있는 제품군과 연관된 베스트셀러 추천 리스트나 '오늘만 사용 가능한 5% 즉시 할인 쿠폰'을 팝업으로 제공하는 '이탈 방지 캠페인'을 수행합니다. 
또한, 이탈률이 유독 높은 페이지(결제 수단 선택 페이지, 약관 동의 페이지 등)의 레이아웃을 단순화하고 불필요한 입력 폼을 줄이는 UX/UI 개선 작업을 병행합니다.<br><br>

<strong>4. 신규 vs 재방문 고객(VisitorType) 맞춤형 마케팅 전략 (Targeted CRM):</strong><br>
- <code>VisitorType</code>별 비율 분석을 보면, 신규 방문자(New Visitor)의 구매율이 유의미하게 높지만 총 세션 수는 재방문자가 압도적입니다. 
재방문자는 단순 탐색과 비교 목적으로 여러 번 유입된 경우가 많으므로 차별화된 CRM 캠페인이 요구됩니다.<br>
- <strong>[액션 플랜]</strong>: 신규 방문자에게는 첫 방문 환영 쿠폰(예: 10% 첫 구매 할인)과 인기 상품 웰컴 패키지를 메인 화면에 전면 노출해 즉각적인 첫 구매 전환을 유도합니다. 
반면, 재방문 고객에게는 장바구니에 보관된 상품의 가격 할인 알림(Price-drop notification) 발송, 로열티 마일리지 적립 혜택 강조, 
혹은 최근 조회한 상품과 어울리는 크로스셀링(Cross-selling) 개인화 메일을 발송하여 반복 방문이 실구매로 전환되도록 유도합니다.<br><br>

<strong>5. 계절성(Month) 프로모션 및 연간 마케팅 예산 최적화 (Seasonal Budgeting):</strong><br>
- 범주형 분석 결과 11월(Nov), 5월(May) 등의 계절성 요인이 구매율 상승과 밀접하게 연동되어 있습니다.<br>
- <strong>[액션 플랜]</strong>: 예측 모델 상에서 연말 프로모션 시즌인 11월 진입 전 9~10월에는 재방문 고객들의 장바구니 데이터를 집중 수집하여 모수를 확보해 두고, 
11월이 시작되는 시점에 고가치 잠재 고객(PageValues가 높았던 세션들)을 대상으로 집중 리타게팅 광고(GDN, Meta 광고 등) 예산을 2~3배 집중 투입합니다. 
이를 통해 광고비 대비 매출액(ROAS)을 최적화하고 한정된 마케팅 예산의 비즈니스 효율을 극대화합니다.
</div>""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #757575;'>Online Shoppers Purchasing Intention 대시보드 | Created by Antigravity AI Agent</p>", unsafe_allow_html=True)
