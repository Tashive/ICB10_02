"""
이 스크립트는 다양한 컬럼들의 조합(지번주소, 건물관리번호 등 포함)으로 중복을 제거할 때
각각의 결과 행 수를 계산하여 2584건이 나오는 정확한 조건이 있는지 확인하기 위한 것입니다.
"""

import os
import pandas as pd

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    df = pd.read_csv(csv_path)
    
    print(f"Total raw rows: {len(df)}")
    
    # We will test various combinations and print the results
    combinations_to_test = [
        ['상호명', '도로명주소'],
        ['상호명', '지번주소'],
        ['상호명', '건물관리번호'],
        ['상호명', '건물명'],
        ['상호명', '경도', '위도'],
        ['상호명', '지점명', '도로명주소'],
        ['상호명', '지점명', '지번주소'],
        ['상호명', '지점명', '건물관리번호'],
        ['상호명', '지점명', '건물명'],
        ['상호명', '지점명', '경도', '위도'],
    ]
    
    print("\n--- Unfiltered (3082 rows) ---")
    for cols in combinations_to_test:
        count = len(df.drop_duplicates(subset=cols))
        print(f"Dedup on {cols}: {count}")
        
    df_filt = df[df['상권업종대분류명'].isin(['음식', '소매'])]
    print("\n--- Filtered to 음식/소매 (3072 rows) ---")
    for cols in combinations_to_test:
        count = len(df_filt.drop_duplicates(subset=cols))
        print(f"Dedup on {cols}: {count}")

if __name__ == '__main__':
    main()
