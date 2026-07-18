"""
이 스크립트는 burger.csv 데이터에서 '브랜드명'과 '도로명주소'를 기준으로 중복 행을 제거하여
동일 매장이 중복 등록된 데이터 오류를 해결하고, 최종 고유 매장 정보만 남긴 뒤
상권업종대분류명과 브랜드명 간의 업데이트된 교차표를 작성합니다.
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
    
    # Drop duplicates based on '브랜드명' and '도로명주소', keeping the first occurrence
    dedup_df = df.drop_duplicates(subset=['브랜드명', '도로명주소'], keep='first')
    final_rows = len(dedup_df)
    removed_rows = initial_rows - final_rows
    
    # Save the deduplicated data back to burger.csv
    dedup_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print("Deduplication Complete!")
    print(f"  Initial rows: {initial_rows}")
    print(f"  Removed duplicate rows: {removed_rows}")
    print(f"  Final unique store rows: {final_rows}")
    
    # Generate and print updated Crosstab
    ct = pd.crosstab(dedup_df['브랜드명'], dedup_df['상권업종대분류명'], margins=True, margins_name='합계')
    print("\n=== [중복 제거 후] 브랜드별 상권업종대분류명 교차표 ===")
    print(ct.to_string())

if __name__ == '__main__':
    main()
