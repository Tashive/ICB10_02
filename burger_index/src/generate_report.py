"""
이 스크립트는 burger.csv 데이터를 바탕으로 브랜드명과 상권업종대분류명 간의
교차표(Crosstab)를 작성하고, 한글 인코딩 깨짐 없이 파일로 저장하여 보고서를 생성합니다.
"""

import os
import pandas as pd

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    report_path = os.path.join(script_dir, '..', 'report', 'crosstab_report.txt')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    df = pd.read_csv(csv_path)
    
    # Generate Crosstab
    crosstab = pd.read_csv(csv_path)
    ct = pd.crosstab(df['브랜드명'], df['상권업종대분류명'], margins=True, margins_name='합계')
    
    # Ensure report folder exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    # Save report to a text file in UTF-8
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== 브랜드별 상권업종대분류명 교차표 빈도수 분석 ===\n\n")
        f.write(ct.to_string())
        f.write("\n\n=== 상세 데이터 (딕셔너리 형태) ===\n")
        f.write(f"INDEX: {ct.index.tolist()}\n")
        f.write(f"COLUMNS: {ct.columns.tolist()}\n")
        f.write(f"VALUES: {ct.values.tolist()}\n")
        
    print(f"Report saved successfully to {report_path}")

if __name__ == '__main__':
    main()
