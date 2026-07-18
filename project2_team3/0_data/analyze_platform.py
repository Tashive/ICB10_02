"""
제품명 내 성분 키워드 추출 테스트 스크립트

이 스크립트는 `NutriFit-Dashboard-Data-file.csv` 파일의 각 플랫폼별 제품명 컬럼에서
자주 등장하는 주요 성분 키워드(마그네슘, 엽산, 비타민 등)를 매칭하여
성분 추출 성공률과 샘플 데이터를 확인합니다.
"""

import os
import sys
import pandas as pd

# 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"c:\\Users\\tasha\\OneDrive\\바탕 화면\\ICB10_02\\project2_team3\\0_data"
CSV_PATH = os.path.join(DATA_DIR, "NutriFit-Dashboard-Data-file.csv")

df = pd.read_csv(CSV_PATH, low_memory=False)

# 자주 나오는 성분 키워드 목록
ingredient_keywords = [
    "마그네슘", "엽산", "비타민", "칼륨", "칼슘", "아연", "철분",
    "오메가3", "프로바이오틱", "유산균", "콜라겐", "루테인", "코엔자임"
]

def extract_ingredient(name):
    if pd.isna(name):
        return None
    found = [kw for kw in ingredient_keywords if kw in name]
    return ", ".join(found) if found else None

name_col_map = {"Coupang": "product_name", "OliveYoung": "name", "iHerb": "displayName"}

for platform, group in df.groupby("platform"):
    name_col = name_col_map[platform]
    extracted = group[name_col].apply(extract_ingredient)
    matched_ratio = extracted.notna().mean()
    print(f"{platform}: 성분 추출 성공률 {matched_ratio:.1%}")
    sample_df = pd.DataFrame({
        "제품명": group[name_col],
        "추출_성분": extracted
    }).dropna().head(3)
    for idx, row in sample_df.iterrows():
        print(f"  - 제품명: {row['제품명']} -> 추출: {row['추출_성분']}")
    print()
