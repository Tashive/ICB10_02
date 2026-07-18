"""
이 스크립트는 burger.csv 데이터에서 상권업종대분류명이 '음식' 또는 '소매'가 아닌
매장 데이터를 필터링하여 제외하고, 필터링된 최종 데이터를 다시 burger.csv에 덮어쓰는 역할을 합니다.
"""

import os
import pandas as pd

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    df = pd.read_csv(csv_path)
    initial_rows = len(df)
    
    # Keep only '음식' and '소매'
    allowed_categories = ['음식', '소매']
    filtered_df = df[df['상권업종대분류명'].isin(allowed_categories)]
    final_rows = len(filtered_df)
    removed_rows = initial_rows - final_rows
    
    # Save back to burger.csv
    filtered_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"Filtering Complete!")
    print(f"  Initial rows: {initial_rows}")
    print(f"  Removed rows: {removed_rows}")
    print(f"  Final rows kept: {final_rows}")
    
    # Show new crosstab
    ct = pd.crosstab(filtered_df['브랜드명'], filtered_df['상권업종대분류명'], margins=True, margins_name='합계')
    print("\n=== [업데이트] 브랜드별 상권업종대분류명 교차표 ===")
    print(ct.to_string())

if __name__ == '__main__':
    main()
