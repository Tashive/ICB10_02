"""
올리브영 온라인몰 건강식품(비타민, 영양제, 유산균, 슬리밍/이너뷰티) 카테고리 수집 및 SQLite DB 저장 프로그램.

이 스크립트는 올리브영 온라인몰 건강식품 상품을 페이지 단위로 수집하는 즉시 SQLite 데이터베이스에 실시간 적재합니다.
이를 통해 수집 중간 차단이나 비정상 종료가 발생해도 데이터 유실을 차단하며, 수집 완료 후 DB로부터 최신 데이터를 쿼리해 CSV로도 자동 갱신합니다.
또한, 실행 시 기존의 CSV 수집 파일들이 있다면 이를 SQLite DB에 먼저 마이그레이션(초기화)하여 데이터의 연속성을 유지합니다.
"""

import os
import re
import time
import random
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from curl_cffi import requests

DB_PATH = r"project2_team3/4_올리브영 온라인몰/data/oliveyoung_health.db"
DATA_DIR = r"project2_team3/4_올리브영 온라인몰/data"

def init_db():
    """SQLite 데이터베이스 및 테이블을 초기화합니다."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # products 테이블 생성 (goods_no UNIQUE 제약 조건을 활용하여 중복 방지)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            goods_no TEXT UNIQUE,
            brand TEXT,
            name TEXT,
            price_org INTEGER,
            price_cur INTEGER,
            score REAL,
            review_count TEXT,
            tags TEXT,
            link TEXT,
            img_url TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("SQLite 데이터베이스 초기화 완료.")

def migrate_existing_csv_to_db():
    """기존 수집 데이터 CSV 파일이 존재하는 경우 SQLite DB에 최초 1회 마이그레이션합니다."""
    files = {
        "비타민": "올리브영_비타민_수집데이터.csv",
        "유산균": "올리브영_유산균_수집데이터.csv",
        "슬리밍_이너뷰티": "올리브영_슬리밍_이너뷰티_수집데이터.csv",
        "영양제": "올리브영_영양제_수집데이터.csv"
    }
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 현재 DB에 적재된 행의 수 확인
    cursor.execute("SELECT COUNT(*) FROM products")
    db_count = cursor.fetchone()[0]
    
    # DB가 비어있는 경우에만 CSV 마이그레이션 진행
    if db_count == 0:
        print("SQLite DB가 비어있습니다. 기존 CSV 파일을 데이터베이스로 마이그레이션합니다...")
        for cat_name, file_name in files.items():
            csv_path = os.path.join(DATA_DIR, file_name)
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    print(f"  마이그레이션 중: {file_name} ({len(df)}개 상품)")
                    
                    for _, row in df.iterrows():
                        # 정상가/판매가 데이터 형변환 처리
                        def to_int(val):
                            if pd.isna(val) or val == "":
                                return None
                            try:
                                return int(float(str(val).replace(",", "")))
                            except ValueError:
                                return None
                        
                        price_org = to_int(row.get("price_org"))
                        price_cur = to_int(row.get("price_cur"))
                        
                        # 평점 변환
                        score_val = row.get("score")
                        score = float(score_val) if not pd.isna(score_val) and score_val != "" else None
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO products 
                            (category, goods_no, brand, name, price_org, price_cur, score, review_count, tags, link, img_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row.get("카테고리", cat_name),
                            row.get("goods_no"),
                            row.get("brand"),
                            row.get("name"),
                            price_org,
                            price_cur,
                            score,
                            row.get("review_count"),
                            row.get("tags"),
                            row.get("link"),
                            row.get("img_url")
                        ))
                    conn.commit()
                except Exception as e:
                    print(f"  CSV 마이그레이션 오류 ({file_name}): {e}")
        
        cursor.execute("SELECT COUNT(*) FROM products")
        new_count = cursor.fetchone()[0]
        print(f"마이그레이션 완료. 현재 DB 총 적재 수: {new_count}개 상품.")
    else:
        print(f"SQLite DB에 이미 {db_count}개의 상품 데이터가 존재하여 초기 CSV 마이그레이션을 건너뜁니다.")
        
    conn.close()

def save_page_products_to_db(products_list):
    """한 페이지의 상품 목록을 SQLite DB에 저장(Upsert)합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for p in products_list:
        # 가격 정수형 변환 처리
        price_org = int(p["price_org"]) if p["price_org"] else None
        price_cur = int(p["price_cur"]) if p["price_cur"] else None
        score = float(p["score"]) if p["score"] else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (category, goods_no, brand, name, price_org, price_cur, score, review_count, tags, link, img_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["카테고리"],
            p["goods_no"],
            p["brand"],
            p["name"],
            price_org,
            price_cur,
            score,
            p["review_count"],
            p["tags"],
            p["link"],
            p["img_url"]
        ))
        
    conn.commit()
    conn.close()

def export_db_to_csv(cat_name):
    """수집 완료 후 SQLite DB에서 특정 카테고리 전체 데이터를 조회하여 CSV로 덮어씁니다."""
    safe_cat_name = cat_name.replace("/", "_")
    output_file = os.path.join(DATA_DIR, f"올리브영_{safe_cat_name}_수집데이터.csv")
    
    conn = sqlite3.connect(DB_PATH)
    # 데이터 조회
    query = "SELECT category AS 카테고리, goods_no, brand, name, price_org, price_cur, score, review_count, tags, link, img_url FROM products WHERE category = ?"
    df = pd.read_sql_query(query, conn, params=(cat_name,))
    conn.close()
    
    if not df.empty:
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"[{cat_name}] CSV 백업 완료: 총 {len(df)}개 상품이 '{output_file}'에 업데이트되었습니다.")
    else:
        print(f"[{cat_name}] DB 내에 해당하는 데이터가 없어 CSV 파일 업데이트를 생략합니다.")

def scrape_category(cat_name, cat_no):
    """특정 카테고리의 상품 정보를 스크래핑하고 매 페이지 SQLite DB에 저장합니다."""
    base_url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do"
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        "referer": "https://www.oliveyoung.co.kr/store/main/main.do",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    page = 1
    
    print(f"\n==========================================")
    print(f"카테고리 [{cat_name}] 실시간 DB 저장 스크래핑 시작")
    print(f"==========================================")
    
    while True:
        print(f"[{cat_name}] 페이지 {page} 요청 중...")
        params = {
            "dispCatNo": cat_no,
            "pageIdx": str(page),
        }
        
        response = None
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                response = session.get(base_url, headers=headers, params=params, timeout=15)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    retry_count += 1
                    wait_time = 5 * retry_count + random.uniform(1.0, 3.0)
                    print(f"    [429 차단 감지] {wait_time:.1f}초 대기 후 재시도 합니다. ({retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"    페이지 {page} 요청 실패. 상태 코드: {response.status_code}")
                    break
            except Exception as e:
                retry_count += 1
                wait_time = 5 * retry_count
                print(f"    네트워크 오류 발생: {e}. {wait_time}초 후 재시도 합니다. ({retry_count}/{max_retries})")
                time.sleep(wait_time)
                
        if response is None or response.status_code != 200:
            print(f"[{cat_name}] 페이지 {page} 수집에 최종 실패했습니다. 해당 카테고리 수집을 조기 종료합니다.")
            break
            
        soup = BeautifulSoup(response.text, "html.parser")
        product_elements = soup.select("ul.cate_prd_list li")
        
        if not product_elements:
            print(f"[{cat_name}] 페이지 {page}에 상품이 존재하지 않습니다. 수집 완료.")
            break
            
        print(f"[{cat_name}] 페이지 {page}에서 {len(product_elements)}개 상품 파싱 및 SQLite 실시간 저장 중...")
        
        page_products = []
        for prd in product_elements:
            goods_no = ""
            link_el = prd.select_one("a.prd_thumb")
            if link_el:
                goods_no = link_el.get("data-ref-goodsno", "")
            
            brand_el = prd.select_one("span.tx_brand")
            brand = brand_el.text.strip() if brand_el else ""
            
            name_el = prd.select_one("p.tx_name")
            name = name_el.text.strip() if name_el else ""
            
            price_org = ""
            price_org_el = prd.select_one("span.tx_org span.tx_num")
            if price_org_el:
                price_org = price_org_el.text.strip().replace(",", "")
                
            price_cur = ""
            price_cur_el = prd.select_one("span.tx_cur span.tx_num")
            if price_cur_el:
                price_cur = price_cur_el.text.strip().replace(",", "")
            
            score = ""
            score_el = prd.select_one("span.review_point span.point")
            if score_el and score_el.get("style"):
                style_str = score_el.get("style")
                match = re.search(r"width:\s*([\d\.]+)%", style_str)
                if match:
                    width_val = float(match.group(1))
                    score = f"{width_val / 20:.1f}"
                    
            review_count = ""
            point_area = prd.select_one("p.prd_point_area")
            if point_area:
                match = re.search(r"\(\s*([\d,\+]+)\s*\)", point_area.text)
                if match:
                    review_count = match.group(1).replace(",", "")
                    
            tags_el = prd.select("p.prd_flag span")
            tags = [t.text.strip() for t in tags_el if t.text.strip()]
            tags_str = ", ".join(tags)
            
            link = ""
            if goods_no:
                link = f"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo={goods_no}"
                
            img_url = ""
            img_el = prd.select_one("a.prd_thumb img")
            if img_el:
                img_url = img_el.get("data-original") or img_el.get("src") or ""
            
            page_products.append({
                "카테고리": cat_name,
                "goods_no": goods_no,
                "brand": brand,
                "name": name,
                "price_org": price_org,
                "price_cur": price_cur,
                "score": score,
                "review_count": review_count,
                "tags": tags_str,
                "link": link,
                "img_url": img_url
            })
            
        # 페이지 단위 실시간 SQLite DB Upsert 실행
        save_page_products_to_db(page_products)
        
        page += 1
        delay = random.uniform(2.0, 4.0)
        time.sleep(delay)
        
    # 수집 완료 후 DB의 최신 데이터 상태를 쿼리하여 CSV로 덮어쓰기 백업
    export_db_to_csv(cat_name)

def main():
    # 1. DB 초기화
    init_db()
    
    # 2. 기존 CSV 파일 데이터가 있다면 SQLite DB로 초기 마이그레이션 수행
    migrate_existing_csv_to_db()
    
    # 3. 4대 카테고리 스크래핑 루프 작동
    categories = {
        "비타민": "100000200010015",
        "유산균": "100000200010024",
        "슬리밍_이너뷰티": "100000200010023",
        "영양제": "100000200010025"
    }
    
    for cat_name, cat_no in categories.items():
        scrape_category(cat_name, cat_no)
        rest_time = random.uniform(5.0, 10.0)
        print(f"카테고리 전환 대기 중... ({rest_time:.1f}초)")
        time.sleep(rest_time)

if __name__ == "__main__":
    main()
