"""
이 스크립트는 다양한 컬럼 조합을 통해 중복 제거를 시도하여,
정확히 2584건이 나오는 중복 제거 기준(subset)을 자동으로 탐색하는 유틸리티입니다.
"""

import os
import sys
import pandas as pd
from itertools import combinations

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    df = pd.read_csv(csv_path)
    
    # We want to test different subsets of columns to see if any combination yields 2584.
    columns_to_test = ['상호명', '지점명', '브랜드명', '도로명주소', '지번주소', '건물관리번호', '경도', '위도']
    
    # Filtered and Unfiltered versions
    datasets = {
        "Unfiltered (3082 rows)": df,
        "Filtered to 음식/소매 (3072 rows)": df[df['상권업종대분류명'].isin(['음식', '소매'])],
        # Simulator without '케이에프씨' (3044 rows)
        "Original Unfiltered (3044 rows)": df[df.apply(lambda r: not ('케이에프씨' in str(r['상호명']).lower() and 'kfc' not in str(r['상호명']).lower()), axis=1)],
        "Original Filtered (3041 rows)": df[df['상권업종대분류명'].isin(['음식', '소매'])].copy()
    }
    
    # We will adjust Original Filtered
    datasets["Original Filtered (3041 rows)"] = datasets["Original Filtered (3041 rows)"][
        datasets["Original Filtered (3041 rows)"].apply(
            lambda r: not ('케이에프씨' in str(r['상호명']).lower() and 'kfc' not in str(r['상호명']).lower()), axis=1
        )
    ]

    print("Searching for combinations that yield exactly 2584 rows...\n")
    
    found = False
    for ds_name, ds in datasets.items():
        print(f"Testing on dataset: {ds_name} (size: {len(ds)})")
        
        # Test all column combinations of size 1 to 5
        for r in range(1, 6):
            for cols in combinations(columns_to_test, r):
                cols_list = list(cols)
                # Check if all columns exist in the dataset
                if not all(c in ds.columns for c in cols_list):
                    continue
                
                # Try dropping duplicates
                res = ds.drop_duplicates(subset=cols_list)
                count = len(res)
                if count == 2584:
                    print(f"  [FOUND!] Subset: {cols_list} -> {count} rows")
                    found = True
                    
    if not found:
        print("No exact combinations of standard columns yielded 2584 rows.")

if __name__ == '__main__':
    main()
