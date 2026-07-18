"""
플랫폼별 콜라겐 키워드 매칭 분석 스크립트

이 스크립트는 `NutriFit-Dashboard-Data-file.csv` 전체 데이터에서 플랫폼별로
`콜라겐`, `collagen`, `이너뷰티` 키워드가 매칭되는 상품의 개수를 세어 출력합니다.
"""

import os
import sys
import pandas as pd

# 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"c:\\Users\\tasha\\OneDrive\\바탕 화면\\ICB10_02\\project2_team3\\0_data"
CSV_PATH = os.path.join(DATA_DIR, "NutriFit-Dashboard-Data-file.csv")

def main():
    if not os.path.exists(CSV_PATH):
        print("데이터 파일이 없습니다.")
        return

    df = pd.read_csv(CSV_PATH, low_memory=False)
    name_cols = {"Coupang": "product_name", "OliveYoung": "name", "iHerb": "displayName"}
    collagen_kws = ["콜라겐", "collagen", "이너뷰티"]
    
    print("=== 전체 플랫폼별 콜라겐 관련 매칭 현황 ===")
    for platform, col in name_cols.items():
        group = df[df["platform"] == platform]
        names = group[col].dropna().astype(str)
        matched_cnt = 0
        for name in names:
            name_lower = name.lower()
            if any(kw in name_lower for kw in collagen_kws):
                matched_cnt += 1
        print(f" - {platform}: 전체 {len(group)}건 중 매칭 {matched_cnt}건")

if __name__ == "__main__":
    main()
