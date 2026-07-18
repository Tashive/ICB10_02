"""
Jupyter Notebook 생성 및 EDA 분석 스크립트

이 스크립트는 `NutriFit-Dashboard-Data-file.csv` 및 `성분_수작업입력_초안.xlsx` 데이터를 분석하고,
분석 과정과 결과를 사전 실행된 형태의 Jupyter Notebook 파일(`eda_report.ipynb`)로 생성합니다.
각 코드 셀 위에는 해당 분석의 목적을 담은 마크다운 셀이 배치됩니다.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"c:\\Users\\tasha\\OneDrive\\바탕 화면\\ICB10_02\\project2_team3\\0_data"
CSV_PATH = os.path.join(DATA_DIR, "NutriFit-Dashboard-Data-file.csv")
EXCEL_PATH = os.path.join(DATA_DIR, "성분_수작업입력_초안.xlsx")
NOTEBOOK_PATH = os.path.join(DATA_DIR, "eda_report.ipynb")

# 가격 정제 함수
def clean_price_val(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if '.' in val_str:
        val_str = val_str.split('.')[0]
    cleaned = ''.join([c for c in val_str if c.isdigit()])
    return float(cleaned) if cleaned else np.nan

def generate_data_outputs():
    # 1. CSV 로드
    df_csv = pd.read_csv(CSV_PATH, low_memory=False)
    
    # 1-1. 플랫폼별 건수
    p_counts = df_csv['platform'].value_counts()
    out_counts = "=== 플랫폼별 전체 데이터 건수 ===\n" + p_counts.to_string() + "\n"
    
    # 1-2. 결측치 비율
    out_nulls = "\n=== 플랫폼별 주요 컬럼 결측치 비율 (%) ===\n"
    for platform, group in df_csv.groupby('platform'):
        out_nulls += f"\n[ {platform} ] (총 {len(group)}건)\n"
        null_ratios = group.isnull().mean() * 100
        active_nulls = null_ratios[null_ratios < 100].round(2)
        out_nulls += active_nulls.to_string() + "\n"
        
    out_section1 = out_counts + out_nulls
    
    # 2. 가격 통계
    out_prices = "=== 플랫폼별 가격 기초 통계량 ===\n"
    for platform in ['Coupang', 'OliveYoung', 'iHerb']:
        group = df_csv[df_csv['platform'] == platform]
        if platform == 'Coupang':
            price_col = 'price'
        elif platform == 'OliveYoung':
            price_col = 'price_cur'
        else:
            price_col = 'discountPrice'
            
        prices = group[price_col].apply(clean_price_val).dropna()
        out_prices += f"\n[ {platform} ] ({price_col} 컬럼 기준)\n"
        out_prices += f"  - 최소값: {prices.min():,.0f}원\n"
        out_prices += f"  - 최대값: {prices.max():,.0f}원\n"
        out_prices += f"  - 평균값: {prices.mean():,.2f}원\n"
        out_prices += f"  - 중앙값: {prices.median():,.0f}원\n"
        
    # 3. 엑셀 분석
    df_excel = pd.read_excel(EXCEL_PATH, skiprows=3)
    df_filtered = df_excel[df_excel['카테고리'].notna() & (df_excel['카테고리'] != '확인필요')]
    
    # 3-1. 카테고리별 집계
    cat_counts = df_filtered['카테고리'].value_counts()
    out_cats = "=== 카테고리별 상품 개수 집계 ===\n" + cat_counts.to_string() + "\n"
    
    # 4. 교차표
    pivot_table = pd.crosstab(df_filtered['플랫폼'], df_filtered['카테고리'], margins=True, margins_name='합계')
    out_pivot = "=== 플랫폼별 x 카테고리별 교차표 ===\n" + pivot_table.to_string() + "\n"
    
    return out_section1, out_prices, out_cats, out_pivot

def main():
    if not os.path.exists(CSV_PATH) or not os.path.exists(EXCEL_PATH):
        print("필요한 데이터 파일이 존재하지 않습니다.")
        return

    # 파이썬 연산 실행하여 실제 출력값 가져오기 (노트북 프리렌더링용)
    out_s1, out_s2, out_s3, out_s4 = generate_data_outputs()
    
    # 노트북 구조 정의
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# NutriFit 상품 데이터 및 수작업 성분 분류 초안 EDA 보고서\n",
                    "\n",
                    "이 노트북은 통합 상품 데이터(`NutriFit-Dashboard-Data-file.csv`)와 수작업 성분 분류 초안 데이터(`성분_수작업입력_초안.xlsx`)를 활용하여 탐색적 데이터 분석(EDA)을 수행한 결과 보고서입니다."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 1. 플랫폼별 데이터 건수 및 결측치 비율 분석\n",
                    "**이 분석을 왜 하는지**: 전체 데이터셋에서 수집된 플랫폼별 데이터의 분포와 각 컬럼의 누락율(결측치 비율)을 파악하여 데이터의 품질을 검증하고 전처리 방향을 설정하기 위함입니다."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": [line + "\n" for line in out_s1.split("\n")]
                    }
                ],
                "source": [
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import os\n",
                    "\n",
                    "# 데이터 로드\n",
                    "df_csv = pd.read_csv('NutriFit-Dashboard-Data-file.csv', low_memory=False)\n",
                    "\n",
                    "# 플랫폼별 건수 계산\n",
                    "print('=== 플랫폼별 전체 데이터 건수 ===')\n",
                    "print(df_csv['platform'].value_counts().to_string())\n",
                    "\n",
                    "# 플랫폼별 결측치 비율\n",
                    "print('\\n=== 플랫폼별 주요 컬럼 결측치 비율 (%) ===')\n",
                    "for platform, group in df_csv.groupby('platform'):\n",
                    "    print(f'\\n[ {platform} ] (총 {len(group)}건)')\n",
                    "    null_ratios = group.isnull().mean() * 100\n",
                    "    active_nulls = null_ratios[null_ratios < 100].round(2)\n",
                    "    print(active_nulls.to_string())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2. 플랫폼별 가격 컬럼 기초 통계량 분석\n",
                    "**이 분석을 왜 하는지**: 각 플랫폼별 제품의 가격 범주(최소값, 최대값, 평균, 중앙값)를 계산하여 가격대의 분포와 특징을 비교 분석하기 위함입니다."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": [line + "\n" for line in out_s2.split("\n")]
                    }
                ],
                "source": [
                    "# 가격 정제 함수 정의\n",
                    "def clean_price_val(val):\n",
                    "    if pd.isna(val):\n",
                    "        return np.nan\n",
                    "    val_str = str(val).strip()\n",
                    "    if '.' in val_str:\n",
                    "        val_str = val_str.split('.')[0]\n",
                    "    cleaned = ''.join([c for c in val_str if c.isdigit()])\n",
                    "    return float(cleaned) if cleaned else np.nan\n",
                    "\n",
                    "print('=== 플랫폼별 가격 기초 통계량 ===')\n",
                    "for platform in ['Coupang', 'OliveYoung', 'iHerb']:\n",
                    "    group = df_csv[df_csv['platform'] == platform]\n",
                    "    if platform == 'Coupang':\n",
                    "        price_col = 'price'\n",
                    "    elif platform == 'OliveYoung':\n",
                    "        price_col = 'price_cur'\n",
                    "    else:\n",
                    "        price_col = 'discountPrice'\n",
                    "        \n",
                    "    prices = group[price_col].apply(clean_price_val).dropna()\n",
                    "    print(f'\\n[ {platform} ] ({price_col} 컬럼 기준)')\n",
                    "    print(f'  - 최소값: {prices.min():,.0f}원')\n",
                    "    print(f'  - 최대값: {prices.max():,.0f}원')\n",
                    "    print(f'  - 평균값: {prices.mean():,.2f}원')\n",
                    "    print(f'  - 중앙값: {prices.median():,.0f}원')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3. 성분 수작업 입력 초안의 카테고리별 상품 개수 집계\n",
                    "**이 분석을 왜 하는지**: 수작업으로 1차 분류한 샘플 데이터에서 핵심 성분 카테고리별 제품 분포가 어떻게 구성되어 있는지 파악하기 위함입니다."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": [line + "\n" for line in out_s3.split("\n")]
                    }
                ],
                "source": [
                    "# 엑셀 로드 및 필터링\n",
                    "df_excel = pd.read_excel('성분_수작업입력_초안.xlsx', skiprows=3)\n",
                    "df_filtered = df_excel[df_excel['카테고리'].notna() & (df_excel['카테고리'] != '확인필요')]\n",
                    "\n",
                    "print('=== 카테고리별 상품 개수 집계 ===')\n",
                    "category_counts = df_filtered['카테고리'].value_counts()\n",
                    "print(category_counts.to_string())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 4. 플랫폼별 x 카테고리별 상품 교차표(피벗 테이블) 분석\n",
                    "**이 분석을 왜 하는지**: 1차 분류 완료된 제품들이 플랫폼별로 각 카테고리에 어떻게 교차 분포하고 있는지 파악하여 플랫폼별 강점 카테고리를 비교하기 위함입니다."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 4,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": [line + "\n" for line in out_s4.split("\n")]
                    }
                ],
                "source": [
                    "# 교차표 생성\n",
                    "pivot_table = pd.crosstab(df_filtered['플랫폼'], df_filtered['카테고리'], margins=True, margins_name='합계')\n",
                    "print('=== 플랫폼별 x 카테고리별 교차표 ===')\n",
                    "print(pivot_table.to_string())"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    # ipynb 저장
    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)
        
    print("--- Jupyter Notebook 생성 완료 ---")
    print(f"저장 경로: {NOTEBOOK_PATH}")

if __name__ == "__main__":
    main()
