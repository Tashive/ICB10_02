"""
이 스크립트는 burger.csv 데이터에서 '시도명'과 '시군구명'을 공백 기준으로 합쳐
'시도시군구명' 파생변수를 생성하고, 이를 burger.csv에 저장합니다.
또한, '시도시군구명'과 '브랜드명' 간의 빈도수 교차표를 생성하여 별도의 CSV 파일로 저장합니다.
"""

import os
import pandas as pd

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    output_crosstab_path = os.path.join(script_dir, '..', 'report', 'brand_region_crosstab.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    # Load burger data
    df = pd.read_csv(csv_path)
    
    # 1. Concatenate 시도명 and 시군구명 with a space to create '시도시군구명'
    df['시도시군구명'] = df['시도명'].astype(str).str.strip() + ' ' + df['시군구명'].astype(str).str.strip()
    
    # Save the updated DataFrame back to burger.csv
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("Successfully added '시도시군구명' column and updated burger.csv.")
    
    # 2. Generate crosstab between '시도시군구명' and '브랜드명'
    # margins=True can be helpful, but for clean CSV data we can save the table directly.
    # Let's save it with margins for a complete overview.
    crosstab = pd.crosstab(df['시도시군구명'], df['브랜드명'], margins=True, margins_name='합계')
    
    # Ensure the report directory exists
    os.makedirs(os.path.dirname(output_crosstab_path), exist_ok=True)
    
    # Save the crosstab to brand_region_crosstab.csv
    crosstab.to_csv(output_crosstab_path, encoding='utf-8-sig')
    print(f"Successfully saved crosstab to {output_crosstab_path}.")
    
    # Print a preview of the crosstab (first 10 rows)
    print("\n=== 교차표 미리보기 (상위 10개 지역) ===")
    print(crosstab.head(10).to_string())

if __name__ == '__main__':
    main()
