"""
iHerb 스포츠 카테고리 상품 정보 다중 페이지 스크래핑 및 SQLite 저장 스크립트

이 스크립트는 iHerb의 스포츠 상품 카테고리 API를 통해 1페이지부터 10페이지까지의
상품 정보를 동적으로 수집하고, 수집된 데이터를 매 페이지마다 SQLite 데이터베이스에
저장하는 역할을 합니다.

주요 기능:
- catalog.app.iherb.com API(POST)를 활용한 1~10페이지 순회 수집
- SQLite 데이터베이스(sports_products.db) 연결 및 테이블 생성
- 수집된 상품 데이터를 INSERT OR REPLACE 방식을 사용하여 매 페이지마다 즉시 DB에 저장/업데이트
- 완료 후 DB 저장 현황 확인 및 총 적재 레코드 수 출력

생성일: 2026-06-20
"""

import requests
import sqlite3
import os
import sys
import time

# Windows 콘솔 출력 인코딩 오류 방지
sys.stdout.reconfigure(encoding='utf-8')

# DB 파일 경로 및 설정
db_dir = os.path.join("iherb", "data")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "sports_products.db")

# SQLite 연결 및 테이블 정의
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    productId INTEGER PRIMARY KEY,
    displayName TEXT,
    url TEXT,
    partNumber TEXT,
    listPrice TEXT,
    discountPrice TEXT,
    discountPriceValue REAL,
    rating REAL,
    ratingCount INTEGER,
    brandCode TEXT,
    brandName TEXT,
    name TEXT,
    productName TEXT,
    packageQuantity TEXT,
    productForm TEXT,
    pricePerServing TEXT,
    recentActivityMessage TEXT,
    isOutOfStock INTEGER
)
""")
conn.commit()

url = "https://catalog.app.iherb.com/category/sports/products"
headers = {
    "origin": "https://kr.iherb.com",
    "referer": "https://kr.iherb.com/c/sports",
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

total_inserted = 0

print("iHerb 스포츠 상품 1~10페이지 수집 및 SQLite 저장을 시작합니다...")

for page in range(1, 11):
    payload = {
        "isMobile": False,
        "page": page,
        "pageSize": 24
    }
    
    print(f"페이지 {page} 요청 중...", end=" ", flush=True)
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"오류 발생: {e}")
        break
        
    if response.status_code != 200:
        print(f"실패 (상태 코드: {response.status_code})")
        break
        
    data = response.json()
    products = data.get("products", [])
    
    if not products:
        print("상품 데이터 없음 (수집 종료)")
        break
        
    print(f"성공 (상품 수: {len(products)}) -> DB 저장 중...", end=" ", flush=True)
    
    # 매 페이지마다 SQLite DB에 저장
    page_inserted = 0
    for p in products:
        # 데이터 정제 및 타입 변환
        product_id = p.get("productId")
        if not product_id:
            continue
            
        display_name = p.get("displayName")
        product_url = p.get("url")
        part_number = p.get("partNumber")
        list_price = p.get("listPrice")
        discount_price = p.get("discountPrice")
        
        try:
            discount_price_val = float(p.get("discountPriceValue")) if p.get("discountPriceValue") is not None else None
        except ValueError:
            discount_price_val = None
            
        try:
            rating = float(p.get("rating")) if p.get("rating") is not None else None
        except ValueError:
            rating = None
            
        try:
            rating_count = int(p.get("ratingCount")) if p.get("ratingCount") is not None else None
        except ValueError:
            rating_count = None
            
        brand_code = p.get("brandCode")
        brand_name = p.get("brandName")
        name = p.get("name")
        product_name = p.get("productName")
        package_quantity = p.get("packageQuantity")
        product_form = p.get("productForm")
        price_per_serving = p.get("pricePerServing")
        recent_activity_msg = p.get("recentActivityMessage")
        is_out_of_stock = 1 if p.get("isOutOfStock") else 0
        
        cursor.execute("""
        INSERT OR REPLACE INTO products (
            productId, displayName, url, partNumber, listPrice, discountPrice, 
            discountPriceValue, rating, ratingCount, brandCode, brandName, 
            name, productName, packageQuantity, productForm, pricePerServing, 
            recentActivityMessage, isOutOfStock
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id, display_name, product_url, part_number, list_price, discount_price,
            discount_price_val, rating, rating_count, brand_code, brand_name,
            name, product_name, package_quantity, product_form, price_per_serving,
            recent_activity_msg, is_out_of_stock
        ))
        page_inserted += 1
        
    conn.commit()
    print(f"완료 ({page_inserted}개 저장됨)")
    total_inserted += page_inserted
    
    # 정중한 간격을 위해 1초 대기
    time.sleep(1)

# 전체 저장된 레코드 수 확인
cursor.execute("SELECT COUNT(*) FROM products")
db_count = cursor.fetchone()[0]

conn.close()

print(f"\n수집 완료! DB 파일 경로: {db_path}")
print(f"수집 과정 중 처리된 총 상품 수: {total_inserted}")
print(f"현재 SQLite DB에 누적된 총 상품 수: {db_count}")
