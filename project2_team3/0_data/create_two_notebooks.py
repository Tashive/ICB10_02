"""
Jupyter Notebook 개별 생성 및 EDA 분석 스크립트

이 스크립트는 `NutriFit-Dashboard-Data-file.csv` 및 `성분_수작업입력_초안.xlsx` 데이터를 분석하여,
사용자 요청에 따라 두 개의 개별 Jupyter Notebook 파일로 생성합니다:
1. `eda_report_전체데이터.ipynb`: 전체 27,779건 기준 플랫폼별 분석 및 가격 통계
2. `eda_report_카테고리분석.ipynb`: 수작업 샘플 데이터 중 유효 카테고리(24건) 기준 개수 및 교차표 분석
각 코드 셀에는 분석 목적을 명시하는 마크다운 설명과 실행 결과가 사전 렌더링되어 저장됩니다.
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

# 노트북 저장 경로
NB_TOTAL_PATH = os.path.join(DATA_DIR, "eda_report_전체데이터.ipynb")
NB_CAT_PATH = os.path.join(DATA_DIR, "eda_report_카테고리분석.ipynb")

def clean_price_val(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if '.' in val_str:
        val_str = val_str.split('.')[0]
    cleaned = ''.join([c for c in val_str if c.isdigit()])
    return float(cleaned) if cleaned else np.nan

def generate_total_outputs():
    df_csv = pd.read_csv(CSV_PATH, low_memory=False)
    
    # 1. 플랫폼별 건수
    p_counts = df_csv['platform'].value_counts()
    out_counts = "=== 플랫폼별 전체 데이터 건수 ===\n" + p_counts.to_string() + "\n"
    
    # 2. 결측치 비율
    out_nulls = "\n=== 플랫폼별 주요 컬럼 결측치 비율 (%) ===\n"
    for platform, group in df_csv.groupby('platform'):
        out_nulls += f"\n[ {platform} ] (총 {len(group)}건)\n"
        null_ratios = group.isnull().mean() * 100
        active_nulls = null_ratios[null_ratios < 100].round(2)
        out_nulls += active_nulls.to_string() + "\n"
        
    out_section1 = out_counts + out_nulls
    
    # 3. 가격 통계
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
        
    return out_section1, out_prices

def generate_cat_outputs():
    df_excel = pd.read_excel(EXCEL_PATH, skiprows=3)
    df_filtered = df_excel[df_excel['카테고리'].notna() & (df_excel['카테고리'] != '확인필요')]
    
    # 1. 카테고리별 집계
    cat_counts = df_filtered['카테고리'].value_counts()
    out_cats = "=== 카테고리별 상품 개수 집계 ===\n" + cat_counts.to_string() + "\n"
    
    # 2. 교차표
    pivot_table = pd.crosstab(df_filtered['플랫폼'], df_filtered['카테고리'], margins=True, margins_name='합계')
    out_pivot = "=== 플랫폼별 x 카테고리별 교차표 ===\n" + pivot_table.to_string() + "\n"
    
    return out_cats, out_pivot, len(df_excel), len(df_filtered)

def main():
    if not os.path.exists(CSV_PATH) or not os.path.exists(EXCEL_PATH):
        print("분석 데이터 파일이 누락되었습니다.")
        return

    # 연산 결과 생성
    out_s1, out_s2 = generate_total_outputs()
    out_s3, out_s4, total_sample, valid_sample = generate_cat_outputs()
    
    # [파일 1] 전체 데이터 노트북 빌드
    notebook_total = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# NutriFit 전체 상품 데이터 탐색적 분석 (EDA)\n",
                    "\n",
                    "이 보고서는 NutriFit 전체 상품 수집 데이터(`NutriFit-Dashboard-Data-file.csv`, 전체 27,779건)를 분석한 보고서입니다."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 1. 플랫폼별(Coupang/OliveYoung/iHerb) 건수 및 주요 컬럼 결측치 비율(%)\n",
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
                    "\n",
                    "# 데이터 파일 로드\n",
                    "df_csv = pd.read_csv('NutriFit-Dashboard-Data-file.csv', low_memory=False)\n",
                    "\n",
                    "print('=== 플랫폼별 전체 데이터 건수 ===')\n",
                    "print(df_csv['platform'].value_counts().to_string())\n",
                    "\n",
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
                    "### 2. 플랫폼별 가격 컬럼 기초 통계(최소/최대/평균/중앙값)\n",
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
    
    # [파일 2] 카테고리 분석 노트북 빌드
    notebook_cat = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# NutriFit 성분 수작업 분류 샘플 데이터 카테고리 분석\n",
                    "\n",
                    f"**이 분석은 전체 27,779건 중 수작업으로 성분을 확인한 {total_sample}건 중, 카테고리 분류가 완료된 {valid_sample}건만을 대상으로 합니다.**"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3. 카테고리별(멀티비타민/비타민C/오메가3/유산균/콜라겐/마그네슘) 상품 개수 집계\n",
                    "**이 분석을 왜 하는지**: 수작업으로 1차 분류한 샘플 데이터에서 핵심 성분 카테고리별 제품 분포가 어떻게 구성되어 있는지 파악하기 위함입니다."
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
                        "text": [line + "\n" for line in out_s3.split("\n")]
                    }
                ],
                "source": [
                    "import pandas as pd\n",
                    "\n",
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
                    "### 4. 플랫폼 x 카테고리 교차표(피벗 테이블, 합계 포함)\n",
                    "**이 분석을 왜 하는지**: 1차 분류 완료된 제품들이 플랫폼별로 각 카테고리에 어떻게 교차 분포하고 있는지 파악하여 플랫폼별 강점 카테고리를 비교하기 위함입니다."
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
    
    # 두 노트북 파일 쓰기
    with open(NB_TOTAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(notebook_total, f, ensure_ascii=False, indent=1)
    print(f"저장 성공: {NB_TOTAL_PATH}")
        
    with open(NB_CAT_PATH, 'w', encoding='utf-8') as f:
        json.dump(notebook_cat, f, ensure_ascii=False, indent=1)
    print(f"저장 성공: {NB_CAT_PATH}")

if __name__ == "__main__":
    main()
