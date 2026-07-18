"""
이 스크립트는 burger.csv 데이터에서 중복된 행이 있는지 검사하고,
전체 열 기준 중복 및 상가업소번호 기준 중복 내역을 추출하여 분석 보고서를 작성합니다.
"""

import os
import pandas as pd

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    report_path = os.path.join(script_dir, '..', 'report', 'duplicates_report.txt')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    df = pd.read_csv(csv_path)
    
    # 1. Check exact duplicates (all columns)
    exact_dup = df[df.duplicated(keep=False)]
    exact_dup_count = len(df[df.duplicated(keep='first')])
    
    # 2. Check duplicates based on 상가업소번호 (which should be unique)
    id_dup = df[df.duplicated(subset=['상가업소번호'], keep=False)]
    id_dup_count = len(df[df.duplicated(subset=['상가업소번호'], keep='first')])
    
    # Save report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== 중복 데이터 분석 보고서 ===\n\n")
        f.write(f"1. 전체 열 기준 완전 중복 데이터 수: {exact_dup_count}개 행 (총 {len(exact_dup)}개 행이 연관됨)\n")
        f.write(f"2. 상가업소번호 기준 중복 데이터 수: {id_dup_count}개 행 (총 {len(id_dup)}개 행이 연관됨)\n\n")
        
        if len(exact_dup) > 0:
            f.write("--- [내역] 전체 열 기준 완전 중복 데이터 상세 ---\n")
            cols_to_show = ['상가업소번호', '상호명', '지점명', '시도명', '시군구명', '도로명주소']
            exact_dup_sorted = exact_dup.sort_values(by=['상가업소번호'])
            f.write(exact_dup_sorted[cols_to_show].to_string())
            f.write("\n\n")
        else:
            f.write("전체 열 기준 완전 중복 데이터가 존재하지 않습니다.\n\n")
            
        if len(id_dup) > 0:
            f.write("--- [내역] 상가업소번호 기준 중복 데이터 상세 (완전 중복 제외) ---\n")
            cols_to_show = ['상가업소번호', '상호명', '지점명', '시도명', '시군구명', '도로명주소', '상권업종대분류명']
            exact_dup_indices = exact_dup.index
            non_exact_id_dup = id_dup[~id_dup.index.isin(exact_dup_indices)]
            if len(non_exact_id_dup) > 0:
                non_exact_id_dup_sorted = non_exact_id_dup.sort_values(by=['상가업소번호'])
                f.write(non_exact_id_dup_sorted[cols_to_show].to_string())
            else:
                f.write("상가업소번호 기준 중복 데이터는 모두 완전 중복 데이터입니다.\n")
            f.write("\n")
            
    print(f"Duplicate check complete. Summary saved to {report_path}")
    print(f"Exact duplicates (all columns): {exact_dup_count}")
    print(f"Store ID duplicates: {id_dup_count}")

if __name__ == '__main__':
    main()
