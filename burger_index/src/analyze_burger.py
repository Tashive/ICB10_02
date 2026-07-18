"""
이 스크립트는 burger.csv 데이터를 로드하여 상호명을 기반으로 
브랜드명(버거킹, 맥도날드, KFC, 롯데리아) 파생변수를 추가하고,
해당 브랜드와 상권업종대분류명 간의 교차표(Crosstab)를 생성 및 출력하는 분석 도구입니다.
"""

import os
import pandas as pd
import re

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    # Read the burger.csv file
    df = pd.read_csv(csv_path)
    
    # 브랜드명 파생변수 생성 함수
    def get_brand(name):
        name = str(name).lower()
        if '버거킹' in name or 'burger king' in name or 'burgerking' in name:
            return '버거킹'
        elif '맥도날드' in name or 'mcdonald' in name:
            return '맥도날드'
        elif 'kfc' in name or '케이에프씨' in name:
            return 'KFC'
        elif '롯데리아' in name or 'lotteria' in name:
            return '롯데리아'
        else:
            return '기타'
        
    # Create derived variable
    df['브랜드명'] = df['상호명'].apply(get_brand)
    
    # Save the updated DataFrame back to burger.csv
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("Successfully added '브랜드명' derived variable and saved back to burger.csv.")
    
    # Generate Crosstab (교차표)
    crosstab = pd.crosstab(df['브랜드명'], df['상권업종대분류명'], margins=True, margins_name='합계')
    
    print("\n=== 브랜드별 상권업종대분류명 교차표 ===")
    print(crosstab.to_string())

if __name__ == '__main__':
    main()
