"""
이 스크립트는 추출된 burger.csv 파일의 데이터를 브랜드별(버거킹, 맥도날드, KFC, 롯데리아)로
집계하여 데이터의 정합성과 추출 결과를 검증하는 역할을 합니다.
"""

import os
import csv
import re

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '..', 'data', 'burger.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return

    counts = {
        '버거킹/Burger King': 0,
        '맥도날드/McDonald': 0,
        'KFC': 0,
        '롯데리아/Lotteria': 0,
        '기타/Unmatched': 0
    }
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("Empty file")
            return
            
        try:
            name_idx = header.index('상호명')
        except ValueError:
            print("Error: '상호명' column not found.")
            return
            
        for row in reader:
            if len(row) <= name_idx:
                continue
            name = str(row[name_idx]).lower()
            
            if '버거킹' in name or 'burger king' in name or 'burgerking' in name:
                counts['버거킹/Burger King'] += 1
            elif '맥도날드' in name or 'mcdonald' in name:
                counts['맥도날드/McDonald'] += 1
            elif 'kfc' in name or '케이에프씨' in name:
                counts['KFC'] += 1
            elif '롯데리아' in name or 'lotteria' in name:
                counts['롯데리아/Lotteria'] += 1
            else:
                counts['기타/Unmatched'] += 1
                
    print("\n=== Brand Count Summary ===")
    for brand, cnt in counts.items():
        print(f"  {brand}: {cnt}")
    print(f"  Total Rows: {sum(counts.values())}")

if __name__ == '__main__':
    main()
