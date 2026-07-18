"""
iHerb 영양제 상품 데이터 SQLite 저장 스크립트.
이 스크립트는 iHerb 카테고리 v2 supplements API를 호출하여
1페이지부터 마지막 페이지까지 전체 상품 데이터를 수집하고, 
각 페이지별 원본 JSON 응답과 파싱된 상품 상세 정보를 SQLite 데이터베이스(data/iHerb_supplements.db)에 저장합니다.
"""
import requests
import sqlite3
import json
import os
import sys
import time

# Windows 환경 한글 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

def main():
    url = "https://catalog.app.iherb.com/category/v2/supplements"
    headers = {
        "origin": "https://kr.iherb.com",
        "referer": "https://kr.iherb.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "content-type": "application/json"
    }
    
    # DB 폴더 및 경로 설정
    os.makedirs("data", exist_ok=True)
    db_path = os.path.join("data", "iHerb_supplements.db")
    
    # SQLite 연결 및 테이블 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 페이지별 원본 JSON 데이터 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages_raw (
            page INTEGER PRIMARY KEY,
            response_json TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. 파싱된 개별 상품 정보 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            productId INTEGER PRIMARY KEY,
            displayName TEXT,
            brandName TEXT,
            partNumber TEXT,
            listPrice TEXT,
            discountPrice TEXT,
            rating REAL,
            ratingCount INTEGER,
            url TEXT,
            packageQuantity TEXT,
            productForm TEXT,
            pricePerServing TEXT,
            page INTEGER
        )
    """)
    conn.commit()
    
    page = 1
    page_size = 24  # 기본 24개씩 수집
    total_products_scraped = 0
    consecutive_empty_pages = 0
    max_retries = 3
    
    print("SQLite DB로 데이터 수집 및 저장을 시작합니다...")
    
    while True:
        payload = {
            "categoryIds": [],
            "healthTopicIds": [],
            "attributeValueIds": [],
            "brandCodes": [],
            "priceRanges": [],
            "ratings": [],
            "weights": [],
            "specials": "",
            "sort": None,
            "showShippingSaver": False,
            "showITested": False,
            "searchWithinKeyWord": "",
            "programs": [],
            "showOnlyAvailable": False,
            "page": page,
            "pageSize": page_size
        }
        
        raw_response_text = ""
        products = []
        
        # API 요청 및 재시도 루프
        for attempt in range(1, max_retries + 1):
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=15)
                if res.status_code == 200:
                    raw_response_text = res.text
                    data = res.json()
                    products = data.get("products", [])
                    break
                else:
                    print(f"[페이지 {page}] API 에러 - HTTP {res.status_code} (시도 {attempt}/{max_retries})")
            except Exception as e:
                print(f"[페이지 {page}] 네트워크 에러: {e} (시도 {attempt}/{max_retries})")
            
            if attempt < max_retries:
                time.sleep(2)
        
        # 수집 중단 조건
        if not products:
            consecutive_empty_pages += 1
            print(f"[페이지 {page}] 빈 페이지 반환 (연속 빈 페이지: {consecutive_empty_pages})")
            if consecutive_empty_pages >= 3:
                print("더 이상 수집할 데이터가 없어 수집을 마칩니다.")
                break
        else:
            consecutive_empty_pages = 0
            
            # SQLite DB 저장
            try:
                # 1. raw response 저장 (이미 있는 페이지인 경우 대체)
                cursor.execute(
                    "INSERT OR REPLACE INTO pages_raw (page, response_json) VALUES (?, ?)",
                    (page, raw_response_text)
                )
                
                # 2. 상품 정보 저장
                for p in products:
                    cursor.execute("""
                        INSERT OR REPLACE INTO products (
                            productId, displayName, brandName, partNumber,
                            listPrice, discountPrice, rating, ratingCount,
                            url, packageQuantity, productForm, pricePerServing, page
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        p.get("productId"),
                        p.get("displayName"),
                        p.get("brandName"),
                        p.get("partNumber"),
                        p.get("listPrice"),
                        p.get("discountPrice"),
                        p.get("rating"),
                        p.get("ratingCount"),
                        p.get("url"),
                        p.get("packageQuantity"),
                        p.get("productForm"),
                        p.get("pricePerServing"),
                        page
                    ))
                
                conn.commit()
                total_products_scraped += len(products)
                print(f"[진행] 페이지 {page} 저장 완료 - 상품 {len(products)}개 추가 (누적: {total_products_scraped}개)")
                
            except Exception as e:
                print(f"[페이지 {page}] DB 저장 중 오류 발생: {e}")
                conn.rollback()
        
        page += 1
        # 서버 부하 방지를 위해 0.15초 대기
        time.sleep(0.15)
        
    conn.close()
    print(f"\n수집 완료! 총 {total_products_scraped}개의 상품 정보와 각 페이지별 원본 응답이 '{db_path}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
