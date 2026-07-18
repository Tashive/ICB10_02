"""
이 스크립트는 소상공인시장진흥공단 상가업소 정보 데이터에서
버거킹, 맥도날드, KFC, 롯데리아(영문 명칭 포함, 대소문자 구분 없음) 매장 정보를 추출하여
하나의 통합 파일(burger.csv)로 저장하는 역할을 합니다.
"""

import os
import csv
import re
import glob

def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    output_path = os.path.join(data_dir, 'burger.csv')
    
    # Define brand matching function based on user specifications
    def matches_brand(name):
        name = str(name).lower()
        if '버거킹' in name or 'burger king' in name or 'burgerking' in name:
            return True
        elif '맥도날드' in name or 'mcdonald' in name:
            return True
        elif 'kfc' in name or '케이에프씨' in name:
            return True
        elif '롯데리아' in name or 'lotteria' in name:
            return True
        return False

    # Find all source CSV files in data_dir (excluding burger.csv)
    csv_files = glob.glob(os.path.join(data_dir, '소상공인시장진흥공단_상가(상권)정보_*_202603.csv'))
    csv_files = [f for f in csv_files if os.path.basename(f) != 'burger.csv']
    
    if not csv_files:
        print("No CSV files found in:", data_dir)
        return

    print(f"Found {len(csv_files)} source CSV files.")
    
    header = None
    matched_count = 0
    total_processed = 0

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as outfile:
        writer = None
        
        for file_path in csv_files:
            file_name = os.path.basename(file_path)
            print(f"Processing {file_name}...")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                reader = csv.reader(infile)
                
                try:
                    file_header = next(reader)
                except StopIteration:
                    print(f"Empty file: {file_name}")
                    continue
                
                # Check column index for 상호명
                try:
                    name_idx = file_header.index('상호명')
                except ValueError:
                    print(f"Error: '상호명' column not found in {file_name}")
                    continue
                
                if writer is None:
                    header = file_header
                    writer = csv.writer(outfile)
                    writer.writerow(header)
                
                row_count = 0
                file_matched = 0
                for row in reader:
                    row_count += 1
                    if len(row) <= name_idx:
                        continue
                    
                    shop_name = row[name_idx]
                    if matches_brand(shop_name):
                        writer.writerow(row)
                        file_matched += 1
                        matched_count += 1
                
                total_processed += row_count
                print(f"  Processed {row_count} rows, found {file_matched} matches.")

    print(f"\nExtraction complete!")
    print(f"Total rows processed: {total_processed}")
    # Subtract 1 for the header
    print(f"Total matching burger franchises saved to {output_path}: {matched_count}")

if __name__ == '__main__':
    main()
