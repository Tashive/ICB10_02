"""
이 스크립트는 중복 제거 후 데이터 행 수가 2570에서 2595 사이로 나오는 모든 컬럼 조합을 탐색하여,
사용자가 언급한 2584건에 도달할 수 있는 정확한 전처리 기준을 식별하는 역할을 합니다.
"""

import os
import pandas as pd
from itertools import combinations

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    df = pd.read_csv(csv_path)
    
    # We want to test different subsets of standard columns
    columns_to_test = ['상가업소번호', '상호명', '지점명', '브랜드명', '상권업종대분류명', '상권업종중분류명', '상권업종소분류명', '시도명', '시군구명', '도로명주소', '지번주소', '건물관리번호', '경도', '위도']
    
    datasets = {
        "With '케이에프씨' (3082 rows)": df,
        "Filtered to 음식/소매 (3072 rows)": df[df['상권업종대분류명'].isin(['음식', '소매'])],
        "Without '케이에프씨' (3044 rows)": df[df.apply(lambda r: not ('케이에프씨' in str(r['상호명']).lower() and 'kfc' not in str(r['상호명']).lower()), axis=1)],
        "Without '케이에프씨' + Filtered (3041 rows)": df[df['상권업종대분류명'].isin(['음식', '소매'])].copy()
    }
    
    datasets["Without '케이에프씨' + Filtered (3041 rows)"] = datasets["Without '케이에프씨' + Filtered (3041 rows)"][
        datasets["Without '케이에프씨' + Filtered (3041 rows)"].apply(
            lambda r: not ('케이에프씨' in str(r['상호명']).lower() and 'kfc' not in str(r['상호명']).lower()), axis=1
        )
    ]

    print("Searching for combinations yielding between 2570 and 2595 rows...\n")
    
    for ds_name, ds in datasets.items():
        print(f"\n--- Testing on dataset: {ds_name} (size: {len(ds)}) ---")
        found_for_ds = False
        for r in range(1, 6):
            for cols in combinations(columns_to_test, r):
                cols_list = list(cols)
                if not all(c in ds.columns for c in cols_list):
                    continue
                
                res = ds.drop_duplicates(subset=cols_list)
                count = len(res)
                if 2570 <= count <= 2595:
                    print(f"  Count: {count} | Subset: {cols_list}")
                    found_for_ds = True
        if not found_for_ds:
            print("  No combinations in this range.")

if __name__ == '__main__':
    main()
