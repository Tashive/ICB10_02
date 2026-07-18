"""
iHerb 유산균 키워드 매칭 분석 및 디버깅 스크립트

이 스크립트는 `NutriFit-Dashboard-Data-file.csv` 전체 데이터에서 platform이 'iHerb'인 상품 중
대소문자 구분 없이 `probiotic`, `lacto`, `bifidobacterium` 키워드가 들어간 상품의 개수를 세고,
각 플랫폼별 매칭 제품의 총 개수를 분석하여 이전 추출 스크립트의 편향 원인을 진단합니다.
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
    
    # iHerb의 유산균 상품 수 확인
    iherb_df = df[df["platform"] == "iHerb"]
    iherb_names = iherb_df["displayName"].dropna().astype(str)
    
    keywords = ["probiotic", "lacto", "bifidobacterium"]
    
    matched_counts = {kw: 0 for kw in keywords}
    total_matched = 0
    matched_samples = []
    
    for name in iherb_names:
        name_lower = name.lower()
        matched = False
        for kw in keywords:
            if kw in name_lower:
                matched_counts[kw] += 1
                matched = True
        if matched:
            total_matched += 1
            if len(matched_samples) < 5:
                matched_samples.append(name)
                
    print(f"=== iHerb 내 유산균 관련 키워드 검색 결과 (총 {len(iherb_df)}건 중) ===")
    print(f"총 매칭 건수: {total_matched}건")
    for kw, count in matched_counts.items():
        print(f" - '{kw}' 매칭: {count}건")
    print("\niHerb 매칭 샘플 5개:")
    for sample in matched_samples:
        print(f" - {sample}")
        
    # 전체 플랫폼별 유산균 키워드 매칭 현황 분석
    print("\n=== 전체 플랫폼별 유산균 관련 매칭 현황 ===")
    name_cols = {"Coupang": "product_name", "OliveYoung": "name", "iHerb": "displayName"}
    probiotic_kws = ["유산균", "프로바이오틱", "probiotic", "프로바이오틱스", "락토", "lacto", "비피더스", "bifidobacterium"]
    
    for platform, col in name_cols.items():
        group = df[df["platform"] == platform]
        names = group[col].dropna().astype(str)
        matched_cnt = 0
        for name in names:
            name_lower = name.lower()
            if any(kw in name_lower for kw in probiotic_kws):
                matched_cnt += 1
        print(f" - {platform}: 전체 {len(group)}건 중 매칭 {matched_cnt}건")

if __name__ == "__main__":
    main()
