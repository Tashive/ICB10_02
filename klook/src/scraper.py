"""
scraper.py

Klook 검색 API를 호출하여 대한민국의 액티비티 상품 데이터를 전체 수집하고,
수집된 데이터를 CSV 파일로 저장하는 스크립트입니다.
작성자: Antigravity
작성일: 2026-06-24
"""

import os
import sys
import time
import pandas as pd
from scrapling import Fetcher

# 윈도우 콘솔 인코딩 에러 방지
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

OUTPUT_DIR = "klook/data"
CSV_PATH = os.path.join(OUTPUT_DIR, "klook_activities.csv")

URL = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ko_KR",
    "x-platform": "desktop",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "cookie": "_cfuvid=fja5dP87aG5yCEK99qcoVWbQHK8FDHxGQP0mtPdVXB0-1782301580.363879-1.0.1.1-_a8QOMy_peRGV48pE6zeaElgIKvJ80FndALr8d.dwyc; kepler_id=f06f995a-86ee-4d88-b6e6-a646d44ecd44; klk_currency=KRW; klk_rdc=KR; klk_ps=1; _fwb=113kHs6JoZ2bnnRdprVA4ZO.1782301582742; _cq_duid=1.1782301583.ds96YjUoD0ks60qB; _cq_suid=1.1782301583.v3W9DmgBy0CcpE7o; _gcl_au=1.1.1689593517.1782301583; dable_uid=13770955.1782301583590; _twpid=tw.1782301583302.882812328840822403; _yjsu_yjad=1782301583.0b7acdad-639d-4353-bfc3-76d5f8c6dc23; _tguatd=eyJzYyI6IihkaXJlY3QpIiwiZnRzIjoiKGRpcmVjdCkifQ==; _tgpc=e171b6dc-9091-471d-9a94-e1d775e01af3; _tgidts=eyJzaCI6ImQ0MWQ4Y2Q5OGYwMGIyMDRlOTgwMDk5OGVjZjg0MjdlIiwiY2kiOiI1M2RlOTMzMi1mOWZmLTQ3NmMtOGNmNC03NzkxZDUwN2FlYzMiLCJzaSI6IjY4MTFhZTYxLWEyY2EtNDE3My1iODhlLThiNjc1MzIzM2UxYiJ9; __lt__cid=a963f75c-5137-4367-bd48-39a31fb3cab8; __lt__cid.c83939be=a963f75c-5137-4367-bd48-39a31fb3cab8; __lt__sid=16633b19-0f938787; __lt__sid.c83939be=16633b19-0f938787; klk_sessionid=MQ.2634ff99ab4c4bc176d315514734d031; _tt_enable_cookie=1; _ttp=01KVWQ7T1TH0FKJCDSQY75AFPX_.tt.1; _ga=GA1.1.506805387.1782301584; JSESSIONID=0B2827610B5A02EB825427BDAB3C8A71; KOUNT_SESSION_ID=0B2827610B5A02EB825427BDAB3C8A71; clientside-cookie=cc7bb24adf3200dc18b834ebe99c7b27c6c141a1f85e3bf02b71d3fbcc200783652169a83df5c04d198eadd7b54b66caab7cfe1f921fd8ac46040a073574fbca4774f9a204493ece809cfe1e0c912f379eb16bbdaadf3f08b8c0c68a95a5416df1141ffeea6db70bbe13b540b253b49182b6791abce69f2a1ace71034da00ceb81386afc892284cbb7c861d99323d15bf8dbcc62cb5351c0d31c26; forterToken=868e1673e0f742968ec92f9b6387b338_1782301584171__UDF43-m4_21ck_; klk_i_sn=9794830693..1782301973850; klk_ga_sn=5946836999..1782301973853; wcs_bt=s_2cb388a4aa34:1782301974; _cq_session=1.1782301583043.TRqAkdLikbcHAnzS.1782301974745; _tglksd=eyJzIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiIiwic3QiOjE3ODIzMDE1ODMzMTcsInNvZCI6IihkaXJlY3QpIiwic29kdCI6MTc4MjMwMTU4MzMxNywic29kcyI6ImMiLCJzb2RzdCI6MTc4MjMwMTk3NDc5OH0=; _uetsid=531bb1d06fc211f1ab9effddb3553dac; _uetvid=531bcb206fc211f1afcd8dc9c9cb3510; _cq_s=DiID57CMsh640vCy:7aEaYB8Lvr+TjdqdGO2E+uDcn1a6kHbwKLH55aTaqZSXGaIroN4EWrl3TPK2/xX0xMvu5kwCsGR/X+YoT0b9ahFmMiR+OqJ2CF8Dc6wmmNk4GnTcNoPUC5gMZPsVFtcaO4BE4sI7N59PJW0v28dXanYcPB+nAmIRtbtoFYfCO6lRfnF0QRlDt6jVipceyBDfU/LVzN8o2vZWWn45kw==:IafL0pvqMF/X3kGcjWCS2A==; _tgsid=eyJscGQiOiJ7XCJscHVcIjpcImh0dHBzOi8vd3d3Lmtsb29rLmNvbSUyRmtvJTJGc2VhcmNoJTJGcmVzdWx0JTJGXCIsXCJscHRcIjpcIktsb29rJTIwVHJhdmVsXCIsXCJscHJcIjpcIlwifSIsInBzIjoiOGUwNzhlYTAtZDQyMS00ZTc1LWJiYzItYzAyYjYzMTJkZWE3IiwicHZjIjoiMiIsInNjIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiOi0xIiwiZWMiOiI0IiwicHYiOiIxIiwidGltIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiOjE3ODIzMDE1ODY2ODU6LTEifQ==; _ga_HSY7KJ18X2=GS2.1.s1782301583$o1$g1$t1782301974$j59$l0$h0; _ga_FW3CMDM313=GS2.1.s1782301583$o1$g1$t1782301974$j6$l0$h0; _ga_V8S4KC8ZXR=GS2.1.s1782301583$o1$g1$t1782301975$j5$l0$h519304495; datadome=c7c0zBzlRr65X1EcGbV7U~PVY7dD4fFI7I~9xJlHKLnIhRAjMDV495WtMZ0PQmUyKWP5IqXMmZnPlwCGC~YpFSiuwj~7d2~6w2dB74byzFl6uETD7jnAeYK1db_0UxlB; ttcsid=1782301583422::3pgCndZv_JWfXAoKzC1C.1.1782301975389.0::1.390006.391674::335283.6.579.253::337455.28.0; ttcsid_C1SIFQUHLSU5AAHCT7H0=1782301583421::FjAXqkX7p9LIZXoVITU-.1.1782301975389.1; klk_gl_sess=08379a7c895a..1782301583906..1782301975499"
}

def fetch_klook_page(fetcher, page):
    """특정 페이지 번호에 대한 Klook 검색 API 결과를 가져옵니다."""
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
            return response.json()
        else:
            print(f"페이지 {page} 호출 실패. Status Code: {response.status}")
            return None
    except Exception as e:
        print(f"페이지 {page} 호출 중 오류 발생: {e}")
        return None

def parse_cards(data):
    """API 응답 JSON에서 액티비티 상품 데이터를 추출합니다."""
    parsed_items = []
    
    if not data or not data.get("success"):
        return parsed_items
        
    try:
        result = data.get("result", {})
        search_result = result.get("search_result", {})
        cards = search_result.get("cards", [])
        
        for card in cards:
            card_data = card.get("data", {})
            track_info = card.get("track_info", {})
            
            # 필드 추출 및 가공
            product_id = card_data.get("vertical_id") or track_info.get("object_id")
            title = card_data.get("title")
            category = card_data.get("category")
            city_name = card_data.get("city_name")
            cover_url = card_data.get("cover_url")
            deep_link = card_data.get("deep_link")
            sold_out = card_data.get("sold_out")
            location = card_data.get("location")
            
            price_info = card_data.get("price", {})
            selling_price = price_info.get("selling_price")
            market_price = price_info.get("market_price")
            
            review_obj = card_data.get("review_obj", {}) or {}
            rating = review_obj.get("star") or track_info.get("review_rating")
            review_count = track_info.get("review_count") or review_obj.get("number")
            booked_count = review_obj.get("booked")
            
            parsed_items.append({
                "product_id": product_id,
                "title": title,
                "category": category,
                "city_name": city_name,
                "cover_url": cover_url,
                "deep_link": deep_link,
                "sold_out": sold_out,
                "location": location,
                "selling_price": selling_price,
                "market_price": market_price,
                "rating": rating,
                "review_count": review_count,
                "booked_count": booked_count
            })
    except Exception as e:
        print(f"데이터 파싱 중 오류 발생: {e}")
        
    return parsed_items

def main():
    fetcher = Fetcher()
    
    print("=== [1단계] 첫 페이지 수집 및 검증 ===")
    first_page = fetch_klook_page(fetcher, 1)
    if not first_page:
        print("첫 페이지 수집 실패. 스크립트를 종료합니다.")
        return
        
    items = parse_cards(first_page)
    if not items:
        print("첫 페이지 데이터 파싱 실패. 스크립트를 종료합니다.")
        return
        
    print(f"첫 페이지에서 {len(items)}개의 상품 정보를 성공적으로 수집했습니다.")
    
    # 첫 번째 아이템 샘플 출력 및 검증
    sample = items[0]
    print("\n--- [샘플 데이터 검증] ---")
    print(f"ID: {sample['product_id']}")
    print(f"제목: {sample['title']}")
    print(f"카테고리: {sample['category']}")
    print(f"도시: {sample['city_name']}")
    print(f"가격: {sample['selling_price']}")
    print(f"평점: {sample['rating']}")
    print(f"리뷰수: {sample['review_count']}")
    
    # 필수적인 정보인 제목이 있는지 검증
    if sample['title']:
        print("-> 첫 페이지 데이터 검증 완료 (성공)!")
    else:
        print("-> 첫 페이지 데이터 검증 실패 (제목 누락). 스크립트를 종료합니다.")
        return

    # 전체 개수 확인
    try:
        total_count = first_page.get("result", {}).get("search_result", {}).get("total", 0)
    except Exception:
        total_count = 1000
    
    print(f"\n=== [2단계] 전체 데이터 수집 시작 (총 {total_count}개 상품 예상) ===")
    
    all_items = []
    all_items.extend(items)
    
    # 2페이지부터 순차적으로 수집
    page = 2
    # 최대 75페이지까지 시도 (15개 * 67 = 1005개)
    max_pages = (total_count + 14) // 15
    print(f"총 {max_pages} 페이지를 수집할 계획입니다.")
    
    while page <= max_pages:
        print(f"페이지 {page}/{max_pages} 수집 중...")
        page_data = fetch_klook_page(fetcher, page)
        if not page_data:
            print(f"페이지 {page} 요청 실패. 수집을 조기 중단하거나 다음으로 넘어갑니다.")
            break
            
        page_items = parse_cards(page_data)
        if not page_items:
            print(f"페이지 {page}에 상품 데이터가 없거나 수집 한도에 도달했습니다. 수집을 종료합니다.")
            break
            
        all_items.extend(page_items)
        print(f"페이지 {page} 수집 완료: {len(page_items)}개 추가 (누적: {len(all_items)}개)")
        
        page += 1
        time.sleep(1.0) # 서버 부하 방지용 딜레이
        
    print("\n=== [3단계] 데이터 저장 및 요약 ===")
    df = pd.DataFrame(all_items)
    
    # 중복 제거 (product_id 기준)
    initial_len = len(df)
    df.drop_duplicates(subset=["product_id"], keep="first", inplace=True)
    dedup_len = len(df)
    print(f"총 수집 상품: {initial_len}개, 중복 제거 후 상품: {dedup_len}개")
    
    # 출력 폴더 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # CSV 저장
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"성공적으로 데이터를 CSV 파일로 저장했습니다.")
    print(f"저장 경로: {CSV_PATH}")

if __name__ == "__main__":
    main()
