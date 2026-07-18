"""
iHerb 스포츠 스페셜 상품 전체 정보 스크래핑 스크립트

이 스크립트는 iHerb의 스포츠 스페셜 카테고리 API를 통해 1페이지부터 마지막 페이지까지의 
모든 상품 정보를 동적으로 수집하고, 수집된 데이터를 통합하여 CSV 파일로 저장하는 역할을 합니다.

주요 기능:
- 1페이지부터 데이터가 더 이상 존재하지 않을 때까지 루프를 돌며 API 호출
- 각 페이지별 수집 상태 출력
- 수집된 모든 상품 목록을 pandas DataFrame을 통해 CSV 파일(sports_specials.csv)로 저장

생성일: 2026-06-20
"""

import requests
import json
import pandas as pd
import os
import sys
import time

# Windows 콘솔 출력 인코딩 오류 방지
sys.stdout.reconfigure(encoding='utf-8')

url = "https://catalog.app.iherb.com/category/sports/specials"
headers = {
    "origin": "https://kr.iherb.com",
    "referer": "https://kr.iherb.com/",
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

all_products = []
page = 1
pageSize = 18

print("iHerb 스포츠 스페셜 전체 상품 수집을 시작합니다...")

while True:
    params = {
        "isMobile": "false",
        "page": str(page),
        "pageSize": str(pageSize)
    }
    
    print(f"페이지 {page} 요청 중...", end=" ", flush=True)
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
    except Exception as e:
        print(f"오류 발생: {e}")
        break
        
    if response.status_code != 200:
        print(f"실패 (상태 코드: {response.status_code})")
        break
        
    data = response.json()
    products = data.get("products", [])
    
    if not products:
        print("더 이상 상품이 없습니다. 수집을 종료합니다.")
        break
        
    print(f"성공 (상품 수: {len(products)})")
    all_products.extend(products)
    
    # 페이지 수집 완료 후 딜레이 추가
    page += 1
    time.sleep(1)

print(f"\n총 수집된 상품 수: {len(all_products)}")

if all_products:
    df = pd.json_normalize(all_products)
    output_dir = os.path.join("iherb", "data")
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "sports_specials.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"데이터가 {csv_path} 에 성공적으로 저장되었습니다.")
else:
    print("수집된 상품 데이터가 없습니다.")
