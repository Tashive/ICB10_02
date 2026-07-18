"""
NutriFit 데이터에 플랫폼 컬럼 추가 스크립트

이 스크립트는 `NutriFit-Dashboard-Data-file.csv` 파일에 각 행이
어느 플랫폼(쿠팡, 아이허브, 올리브영)에서 온 것인지를 나타내는 `platform`
컬럼을 추가합니다. 플랫폼은 해당 행에 존재하는 고유 컬럼을 기준으로
추론합니다:
- `product_id`   -> Coupang
- `productId`    -> iHerb
- `goods_no`     -> OliveYoung

사용 방법:
    python add_platform.py

필요한 패키지: pandas
"""

import os
import pandas as pd

DATA_DIR = r"c:\\Users\\tasha\\OneDrive\\바탕 화면\\ICB10_02\\project2_team3\\0_data"
OUTPUT_FILE = os.path.join(DATA_DIR, "NutriFit-Dashboard-Data-file.csv")

def infer_platform(row: pd.Series) -> str:
    if 'product_id' in row and pd.notna(row['product_id']):
        return 'Coupang'
    if 'productId' in row and pd.notna(row['productId']):
        return 'iHerb'
    if 'goods_no' in row and pd.notna(row['goods_no']):
        return 'OliveYoung'
    return 'Unknown'

def main():
    if not os.path.exists(OUTPUT_FILE):
        print(f"Error: {OUTPUT_FILE} not found")
        return
    df = pd.read_csv(OUTPUT_FILE, encoding="utf-8-sig")
    if 'platform' not in df.columns:
        df['platform'] = df.apply(infer_platform, axis=1)
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print("--- platform 컬럼 추가 완료 ---")
        print(f"총 행 수: {len(df)}")
        print(f"출력 파일: {OUTPUT_FILE}")
    else:
        print("platform 컬럼이 이미 존재합니다.")

if __name__ == "__main__":
    main()
