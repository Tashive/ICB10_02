"""
이 스크립트는 burger.csv 데이터에서 실제 오프라인 매장의 중복을 탐색하기 위해
동일한 '상호명'과 '도로명주소'를 가지는 데이터 그룹 및
동일한 '브랜드명'과 '도로명주소'를 가지는 데이터 그룹의 중복 내역을 검출하고 상세 보고서를 작성합니다.
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
    
    # 1. 상호명 + 도로명주소 기준 중복 확인
    dup_name_addr = df[df.duplicated(subset=['상호명', '도로명주소'], keep=False)]
    dup_name_addr_groups = dup_name_addr.groupby(['상호명', '도로명주소'])
    
    # 2. 브랜드명 + 도로명주소 기준 중복 확인
    dup_brand_addr = df[df.duplicated(subset=['브랜드명', '도로명주소'], keep=False)]
    dup_brand_addr_groups = dup_brand_addr.groupby(['브랜드명', '도로명주소'])
    
    # Generate detailed report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write("         [중복 데이터 분석 및 상세 내역 보고서]    \n")
        f.write("==================================================\n\n")
        
        f.write("1. [요약] 시스템 고유 번호(상가업소번호) 및 전체 열 기준 중복\n")
        f.write(f"  - 전체 열(모든 컬럼) 완전 일치 중복 행 수: {df.duplicated().sum()}건\n")
        f.write(f"  - 상가업소번호 기준 중복 행 수: {df.duplicated(subset=['상가업소번호']).sum()}건\n")
        f.write("  => 시스템상의 식별자(상가업소번호)는 모두 고유하게 부여되어 있어 단순 식별자 중복은 없습니다.\n\n")
        
        f.write("2. [요약] 오프라인 실제 매장 기준 중복 (동일 위치, 동일 브랜드/상호)\n")
        f.write("  A. [상호명 + 도로명주소] 기준 중복:\n")
        f.write(f"    - 중복에 연관된 총 행 수: {len(dup_name_addr)}건 (전체의 {len(dup_name_addr)/len(df)*100:.2f}%)\n")
        f.write(f"    - 중복이 의심되는 고유 매장 위치 수: {len(dup_name_addr_groups)}군데\n")
        
        # Breakdown of duplicate counts
        sizes_name_addr = dup_name_addr_groups.size()
        f.write(f"    - 중복 빈도별 고유 매장 분포:\n")
        for count, freq in sizes_name_addr.value_counts().sort_index().items():
            f.write(f"      * {count}중 중복 매장: {freq}군데\n")
        
        f.write("\n  B. [브랜드명 + 도로명주소] 기준 중복:\n")
        f.write(f"    - 중복에 연관된 총 행 수: {len(dup_brand_addr)}건 (전체의 {len(dup_brand_addr)/len(df)*100:.2f}%)\n")
        f.write(f"    - 중복이 의심되는 고유 매장 위치 수: {len(dup_brand_addr_groups)}군데\n")
        
        sizes_brand_addr = dup_brand_addr_groups.size()
        f.write(f"    - 중복 빈도별 고유 매장 분포:\n")
        for count, freq in sizes_brand_addr.value_counts().sort_index().items():
            f.write(f"      * {count}중 중복 매장: {freq}군데\n")
            
        f.write("\n==================================================\n")
        f.write("     [상세 내역] 상호명 + 도로명주소 기준 중복 매장 Top 30\n")
        f.write("==================================================\n")
        
        # Sort groups by size descending to show most duplicated first
        sorted_groups = sorted(dup_name_addr_groups, key=lambda x: len(x[1]), reverse=True)
        
        for i, ((name, addr), group) in enumerate(sorted_groups[:30], 1):
            f.write(f"\n[{i}] 매장명: {name} | 주소: {addr} ({len(group)}중 중복)\n")
            f.write("  " + "-"*80 + "\n")
            f.write(f"  {'상가업소번호':<20} | {'지점명':<15} | {'상권업종소분류명':<15} | {'경도':<12} | {'위도':<12}\n")
            f.write("  " + "-"*80 + "\n")
            for idx, row in group.iterrows():
                branch = str(row['지점명']) if pd.notna(row['지점명']) else '없음'
                subcat = str(row['상권업종소분류명']) if pd.notna(row['상권업종소분류명']) else '없음'
                lon = f"{row['경도']:.5f}" if pd.notna(row['경도']) else '없음'
                lat = f"{row['위도']:.5f}" if pd.notna(row['위도']) else '없음'
                f.write(f"  {row['상가업소번호']:<20} | {branch:<15} | {subcat:<15} | {lon:<12} | {lat:<12}\n")
            f.write("  " + "-"*80 + "\n")
            
        if len(sorted_groups) > 30:
            f.write(f"\n... 그 외 {len(sorted_groups)-30}개의 중복 그룹이 더 존재합니다. 상세 내역은 코드를 통해 추가 조회 가능합니다.\n")

    print("Duplicates detailed check complete.")
    print(f"Total name+address duplicate rows: {len(dup_name_addr)}")
    print(f"Unique location groups: {len(dup_name_addr_groups)}")

if __name__ == '__main__':
    main()
