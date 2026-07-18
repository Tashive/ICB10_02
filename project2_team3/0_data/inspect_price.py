"""
Excel 생성을 위한 가격 및 제품명 컬럼 데이터 검사 스크립트

이 스크립트는 `NutriFit-Dashboard-Data-file.csv` 파일에서 각 플랫폼별
가격 및 제품명 컬럼의 실제 데이터 타입과 샘플 값을 확인하여,
Excel 생성 시 필요한 전처리 및 포맷팅 방식을 결정하는 데 사용됩니다.
"""

import os
import sys
import pandas as pd

# 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"c:\\Users\\tasha\\OneDrive\\바탕 화면\\ICB10_02\\project2_team3\\0_data"
CSV_PATH = os.path.join(DATA_DIR, "NutriFit-Dashboard-Data-file.csv")

df = pd.read_csv(CSV_PATH, low_memory=False)

name_col_map = {"Coupang": "product_name", "OliveYoung": "name", "iHerb": "displayName"}
price_col_map = {"Coupang": "price", "OliveYoung": "price_cur", "iHerb": "discountPrice"}

for platform, group in df.groupby("platform"):
    name_col = name_col_map[platform]
    price_col = price_col_map[platform]
    print(f"\n===== {platform} =====")
    print("제품명 샘플:", group[name_col].dropna().head(3).tolist())
    print("가격 샘플:", group[price_col].dropna().head(3).tolist())
