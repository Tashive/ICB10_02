"""
save_to_db.py

Klook 검색 API를 호출하여 대한민국의 액티비티 상품 데이터를 전체 수집하고,
각 페이지별 원본 JSON 응답과 파싱된 상품 상세 정보를 SQLite 데이터베이스에 실시간으로 저장하는 스크립트입니다.
페이지별로 0.5초의 대기 시간을 가져 부하를 방지하며, 상품 링크(deep_link)를 필수로 수집합니다.

작성자: Antigravity
작성일: 2026-06-24
"""

import os
import sys
import time
import sqlite3
import json
from scrapling import Fetcher

# Windows 콘솔 한글 인코딩 문제 방지
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

OUTPUT_DIR = "klook/data"
DB_PATH = os.path.join(OUTPUT_DIR, "klook_activities.db")
URL = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ko_KR",
    "x-platform": "desktop",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "cookie": "_cfuvid=fja5dP87aG5yCEK99qcoVWbQHK8FDHxGQP0mtPdVXB0-1782301580.363879-1.0.1.1-_a8QOMy_peRGV48pE6zeaElgIKvJ80FndALr8d.dwyc; kepler_id=f06f995a-86ee-4d88-b6e6-a646d44ecd44; klk_currency=KRW; klk_rdc=KR; klk_ps=1; _fwb=113kHs6JoZ2bnnRdprVA4ZO.1782301582742; _cq_duid=1.1782301583.ds96YjUoD0ks60qB; _cq_suid=1.1782301583.v3W9DmgBy0CcpE7o; _gcl_au=1.1.1689593517.1782301583; dable_uid=13770955.1782301583590; _twpid=tw.1782301583302.882812328840822403; _yjsu_yjad=1782301583.0b7acdad-639d-4353-bfc3-76d5f8c6dc23; _tguatd=eyJzYyI6IihkaXJlY3QpIiwiZnRzIjoiKGRpcmVjdCkifQ==; _tgpc=e171b6dc-9091-471d-9a94-e1d775e01af3; _tgidts=eyJzaCI6ImQ0MWQ4Y2Q5OGYwMGIyMDRlOTgwMDk5OGVjZjg0MjdlIiwiY2kiOiI1M2RlOTMzMi1mOWZmLTQ3NmMtOGNmNC03NzkxZDUwN2FlYzMiLCJzaSI6IjY4MTFhZTYxLWEyY2EtNDE3My1iODhlLThiNjc1MzIzM2UxYiJ9; __lt__cid=a963f75c-5137-4367-bd48-39a31fb3cab8; __lt__cid.c83939be=a963f75c-5137-4367-bd48-39a31fb3cab8; __lt__sid=16633b19-0f938787; __lt__sid.c83939be=16633b19-0f938787; klk_sessionid=MQ.2634ff99ab4c4bc176d315514734d031; _tt_enable_cookie=1; _ttp=01KVWQ7T1TH0FKJCDSQY75AFPX_.tt.1; _ga=GA1.1.506805387.1782301584; JSESSIONID=0B2827610B5A02EB825427BDAB3C8A71; KOUNT_SESSION_ID=0B2827610B5A02EB825427BDAB3C8A71; clientside-cookie=cc7bb24adf3200dc18b834ebe99c7b27c6c141a1f85e3bf02b71d3fbcc200783652169a83df5c04d198eadd7b54b66caab7cfe1f921fd8ac46040a073574fbca4774f9a204493ece809cfe1e0c912f379eb16bbdaadf3f08b8c0c68a95a5416df1141ffeea6db70bbe13b540b253b49182b6791abce69f2a1ace71034da00ceb81386afc892284cbb7c861d99323d15bf8dbcc62cb5351c0d31c26; forterToken=868e1673e0f742968ec92f9b6387b338_1782301584171__UDF43-m4_21ck_; klk_i_sn=9794830693..1782301973850; klk_ga_sn=5946836999..1782301973853; wcs_bt=s_2cb388a4aa34:1782301974; _cq_session=1.1782301583043.TRqAkdLikbcHAnzS.1782301974745; _tglksd=eyJzIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiIiwic3QiOjE3ODIzMDE1ODMzMTcsInNvZCI6IihkaXJlY3QpIiwic29kdCI6MTc4MjMwMTU4MzMxNywic29kcyI6ImMiLCJzb2RzdCI6MTc4MjMwMTk3NDc5OH0=; _uetsid=531bb1d06fc211f1ab9effddb3553dac; _uetvid=531bcb206fc211f1afcd8dc9c9cb3510; _cq_s=DiID57CMsh640vCy:7aEaYB8Lvr+TjdqdGO2E+uDcn1a6kHbwKLH55aTaqZSXGaIroN4EWrl3TPK2/xX0xMvu5kwCsGR/X+YoT0b9ahFmMiR+OqJ2CF8Dc6wmmNk4GnTcNoPUC5gMZPsVFtcaO4BE4sI7N59PJW0v28dXanYcPB+nAmIRtbtoFYfCO6lRfnF0QRlDt6jVipceyBDfU/LVzN8o2vZWWn45kw==:IafL0pvqMF/X3kGcjWCS2A==; _tgsid=eyJscGQiOiJ7XCJscHVcIjpcImh0dHBzOi8vd3d3Lmtsb29rLmNvbSUyRmtvJTJGc2VhcmNoJTJGcmVzdWx0JTJGXCIsXCJscHRcIjpcIktsb29rJTIwVHJhdmVsXCIsXCJscHJcIjpcIlwifSIsInBzIjoiOGUwNzhlYTAtZDQyMS00ZTc1LWJiYzItYzAyYjYzMTJkZWE3IiwicHZjIjoiMiIsInNjIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiOi0xIiwiZWMiOiI0IiwicHYiOiIxIiwidGltIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiOjE3ODIzMDE1ODY2ODU6LTEifQ==; _ga_HSY7KJ18X2=GS2.1.s1782301583$o1$g1$t1782301974$j59$l0$h0; _ga_FW3CMDM313=GS2.1.s1782301583$o1$g1$t1782301974$j6$l0$h0; _ga_V8S4KC8ZXR=GS2.1.s1782301583$o1$g1$t1782301975$j5$l0$h519304495; datadome=c7c0zBzlRr65X1EcGbV7U~PVY7dD4fFI7I~9xJlHKLnIhRAjMDV495WtMZ0PQmUyKWP5IqXMmZnPlwCGC~YpFSiuwj~7d2~6w2dB74byzFl6uETD7jnAeYK1db_0UxlB; ttcsid=1782301583422::3pgCndZv_JWfXAoKzC1C.1.1782301975389.0::1.390006.391674::335283.6.579.253::337455.28.0; ttcsid_C1SIFQUHLSU5AAHCT7H0=1782301583421::FjAXqkX7p9LIZXoVITU-.1.1782301975389.1; klk_gl_sess=08379a7c895a..1782301583906..1782301975499"
}

def init_db():
    """SQLite 데이터베이스 및 테이블을 초기화합니다."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 페이지별 원본 JSON 저장 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages_raw (
            page INTEGER PRIMARY KEY,
            response_json TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. 파싱된 개별 액티비티 상품 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            city_name TEXT,
            cover_url TEXT,
            deep_link TEXT,
            sold_out INTEGER,
            location TEXT,
            selling_price TEXT,
            market_price TEXT,
            rating REAL,
            review_count INTEGER,
            booked_count TEXT,
            page INTEGER,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def fetch_page(fetcher, page):
    """특정 페이지 번호에 대한 Klook 검색 API 결과를 요청합니다."""
    params = {
        "query": "대한민국",
        "search_scope": "main_search",
        "sort": "most_relevant",
        "tab_key": "0",
        "start": str(page),
        "spm": "SearchResult.SearchResultTab_LIST",
        "clickId": "1cd71660fb",
        "dd_referrer": "",
        "size": "15",
        "k_lang": "ko_KR",
        "k_currency": "KRW"
    }
    
    try:
        response = fetcher.get(URL, params=params, headers=HEADERS)
        if response.status == 200:
            return response
        else:
            print(f"[페이지 {page}] API 호출 실패. 상태 코드: {response.status}")
            return None
    except Exception as e:
        print(f"[페이지 {page}] 요청 에러 발생: {e}")
        return None

def parse_and_save(conn, page, response_data, response_text):
    """응답 데이터를 파싱하여 SQLite DB에 저장합니다."""
    cursor = conn.cursor()
    
    # 1. raw json 저장
    cursor.execute(
        "INSERT OR REPLACE INTO pages_raw (page, response_json) VALUES (?, ?)",
        (page, response_text)
    )
    
    # 2. 상품 정보 파싱 및 저장
    result = response_data.get("result", {})
    search_result = result.get("search_result", {})
    cards = search_result.get("cards", [])
    
    saved_count = 0
    for card in cards:
        card_data = card.get("data", {})
        track_info = card.get("track_info", {})
        
        product_id = card_data.get("vertical_id") or track_info.get("object_id")
        if not product_id:
            continue
            
        product_id = str(product_id)
        title = card_data.get("title")
        category = card_data.get("category")
        city_name = card_data.get("city_name")
        cover_url = card_data.get("cover_url")
        deep_link = card_data.get("deep_link") # 상품 링크 정보 필수 포함
        sold_out = 1 if card_data.get("sold_out") else 0
        location = card_data.get("location")
        
        price_info = card_data.get("price", {}) or {}
        selling_price = price_info.get("selling_price")
        market_price = price_info.get("market_price")
        
        review_obj = card_data.get("review_obj", {}) or {}
        rating = review_obj.get("star") or track_info.get("review_rating")
        if rating:
            try:
                rating = float(rating)
            except ValueError:
                rating = None
                
        review_count = track_info.get("review_count") or review_obj.get("number")
        if review_count:
            if isinstance(review_count, str):
                # 숫자만 남기고 제거
                clean_count = "".join([c for c in review_count if c.isdigit()])
                if clean_count:
                    review_count = int(clean_count)
                else:
                    review_count = None
            else:
                review_count = int(review_count)
                
        booked_count = review_obj.get("booked")
        
        cursor.execute("""
            INSERT OR REPLACE INTO products (
                product_id, title, category, city_name, cover_url, deep_link,
                sold_out, location, selling_price, market_price, rating,
                review_count, booked_count, page
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id, title, category, city_name, cover_url, deep_link,
            sold_out, location, selling_price, market_price, rating,
            review_count, booked_count, page
        ))
        saved_count += 1
        
    conn.commit()
    return saved_count

def main():
    fetcher = Fetcher()
    conn = init_db()
    
    print("=== [1단계] 첫 페이지 수집 및 검증 ===")
    response = fetch_page(fetcher, 1)
    if not response:
        print("첫 페이지 수집에 실패하여 스크립트를 중료합니다.")
        conn.close()
        return
        
    try:
        response_data = response.json()
        response_text = response.text
    except Exception as e:
        print(f"응답 JSON 파싱 실패: {e}")
        conn.close()
        return
        
    saved = parse_and_save(conn, 1, response_data, response_text)
    if saved == 0:
        print("첫 페이지 파싱 결과가 없어 스크립트를 종료합니다.")
        conn.close()
        return
        
    print(f"첫 페이지 수집 및 저장 완료: {saved}개 상품 DB 기록")
    
    # 첫 번째 상품 검증 출력
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, title, deep_link, selling_price FROM products LIMIT 1")
    sample = cursor.fetchone()
    print("\n--- [DB 저장 샘플 데이터 검증] ---")
    print(f"ID: {sample[0]}")
    print(f"제목: {sample[1]}")
    print(f"상품 링크 (필수): {sample[2]}")
    print(f"가격: {sample[3]}")
    
    if sample[1] and sample[2]:
        print("-> 첫 페이지 데이터 검증 완료 (성공)!")
    else:
        print("-> 첫 페이지 데이터 검증 실패 (제목 혹은 링크 누락). 스크립트를 종료합니다.")
        conn.close()
        return
        
    # 전체 수집 설정
    try:
        total_count = response_data.get("result", {}).get("search_result", {}).get("total", 0)
    except Exception:
        total_count = 1000
        
    max_pages = (total_count + 14) // 15
    print(f"\n=== [2단계] 전체 데이터 수집 시작 (총 {total_count}개 상품 예상, {max_pages}개 페이지) ===")
    
    total_saved = saved
    
    for page in range(2, max_pages + 1):
        print(f"페이지 {page}/{max_pages} 수집 중...")
        res = fetch_page(fetcher, page)
        if not res:
            print(f"페이지 {page} 실패. 다음 페이지로 넘어갑니다.")
            continue
            
        try:
            page_data = res.json()
            page_text = res.text
        except Exception as e:
            print(f"페이지 {page} JSON 파싱 에러: {e}")
            continue
            
        page_saved = parse_and_save(conn, page, page_data, page_text)
        total_saved += page_saved
        print(f"페이지 {page} 저장 성공: {page_saved}개 추가 (누적: {total_saved}개)")
        
        # 페이지별 대기시간 0.5초 (0.1~1.0초 준수)
        time.sleep(0.5)
        
    # 최종 검증
    cursor.execute("SELECT COUNT(*) FROM products")
    db_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pages_raw")
    raw_count = cursor.fetchone()[0]
    
    print("\n=== [3단계] 데이터 수집 및 저장 완료 ===")
    print(f"저장된 DB 파일: {DB_PATH}")
    print(f"DB 내 최종 상품 개수: {db_count}개")
    print(f"DB 내 저장된 원본 페이지 수: {raw_count}개")
    
    conn.close()

if __name__ == "__main__":
    main()
