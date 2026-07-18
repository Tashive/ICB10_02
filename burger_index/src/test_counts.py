"""
이 스크립트는 다양한 중복 제거 및 필터링 기준에 따라 최종 행 수가 어떻게 변하는지 테스트하여,
사용자가 요청한 2584건이 나오는 조건을 확인하기 위한 유틸리티입니다.
"""

import os
import sys
import pandas as pd

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    df = pd.read_csv(csv_path)
    
    # ----------------------------------------------------
    # Case A: Current data with '케이에프씨' (3082 rows raw)
    # ----------------------------------------------------
    print("=== [Case A] With '케이에프씨' (3082 rows raw) ===")
    print(f"Deduplicate on ['상호명', '도로명주소']: {len(df.drop_duplicates(subset=['상호명', '도로명주소']))}")
    print(f"Deduplicate on ['상호명', '지점명', '도로명주소']: {len(df.drop_duplicates(subset=['상호명', '지점명', '도로명주소']))}")
    print(f"Deduplicate on ['브랜드명', '지점명', '도로명주소']: {len(df.drop_duplicates(subset=['브랜드명', '지점명', '도로명주소']))}")
    print(f"Deduplicate on ['브랜드명', '도로명주소']: {len(df.drop_duplicates(subset=['브랜드명', '도로명주소']))}")
    
    # Filtered to '음식'/'소매'
    df_filt = df[df['상권업종대분류명'].isin(['음식', '소매'])]
    print("\n--- Filtered to 음식/소매 (3072 rows) ---")
    print(f"Filtered + Deduplicate on ['상호명', '도로명주소']: {len(df_filt.drop_duplicates(subset=['상호명', '도로명주소']))}")
    print(f"Filtered + Deduplicate on ['상호명', '지점명', '도로명주소']: {len(df_filt.drop_duplicates(subset=['상호명', '지점명', '도로명주소']))}")
    print(f"Filtered + Deduplicate on ['브랜드명', '지점명', '도로명주소']: {len(df_filt.drop_duplicates(subset=['브랜드명', '지점명', '도로명주소']))}")
    print(f"Filtered + Deduplicate on ['브랜드명', '도로명주소']: {len(df_filt.drop_duplicates(subset=['브랜드명', '도로명주소']))}")
    
    # ----------------------------------------------------
    # Case B: Original data WITHOUT '케이에프씨' (only 'kfc')
    # ----------------------------------------------------
    # We can simulate this by filtering out rows where brand is 'KFC' but 'kfc' is not in the lowercase '상호명'
    def is_original_kfc(row):
        name = str(row['상호명']).lower()
        if '케이에프씨' in name and 'kfc' not in name:
            return False
        return True
        
    df_orig = df[df.apply(is_original_kfc, axis=1)]
    print("\n\n=== [Case B] WITHOUT '케이에프씨' (3044 rows raw) ===")
    print(f"Raw original rows: {len(df_orig)}")
    print(f"Deduplicate on ['상호명', '도로명주소']: {len(df_orig.drop_duplicates(subset=['상호명', '도로명주소']))}")
    print(f"Deduplicate on ['상호명', '지점명', '도로명주소']: {len(df_orig.drop_duplicates(subset=['상호명', '지점명', '도로명주소']))}")
    print(f"Deduplicate on ['브랜드명', '지점명', '도로명주소']: {len(df_orig.drop_duplicates(subset=['브랜드명', '지점명', '도로명주소']))}")
    print(f"Deduplicate on ['브랜드명', '도로명주소']: {len(df_orig.drop_duplicates(subset=['브랜드명', '도로명주소']))}")
    
    df_orig_filt = df_orig[df_orig['상권업종대분류명'].isin(['음식', '소매'])]
    print("\n--- Filtered to 음식/소매 (3041 rows) ---")
    print(f"Filtered + Deduplicate on ['상호명', '도로명주소']: {len(df_orig_filt.drop_duplicates(subset=['상호명', '도로명주소']))}")
    print(f"Filtered + Deduplicate on ['상호명', '지점명', '도로명주소']: {len(df_orig_filt.drop_duplicates(subset=['상호명', '지점명', '도로명주소']))}")
    print(f"Filtered + Deduplicate on ['브랜드명', '지점명', '도로명주소']: {len(df_orig_filt.drop_duplicates(subset=['브랜드명', '지점명', '도로명주소']))}")
    print(f"Filtered + Deduplicate on ['브랜드명', '도로명주소']: {len(df_orig_filt.drop_duplicates(subset=['브랜드명', '도로명주소']))}")

if __name__ == '__main__':
    main()
