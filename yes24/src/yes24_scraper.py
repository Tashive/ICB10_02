"""
YES24 베스트셀러 도서 정보 수집 스크립트

이 스크립트는 YES24 베스트셀러 페이지의 HTML 응답 및 내재된 JSON 데이터를 파싱하여
도서 상세 정보(순위, 제목, 저자, 출판사, 가격, 평점, 판매지수 등)를 수집하고 CSV 파일로 저장합니다.
1페이지부터 데이터가 없을 때까지 자동으로 모든 페이지를 순회하며 수집을 진행합니다.
"""

import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 설정 정보
TARGET_URL = "https://www.yes24.com/product/category/BestSellerContents"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
PARAMS = {
    "categoryNumber": "001001003",
    "sumGb": "06",
    "sex": "A",
    "age": "255",
    "goodsTp": "0",
    "addOptionTp": "0",
    "excludeTp": "2",
    "pageNumber": 1,
    "pageSize": 24,
    "goodsStatGb": "06",
    "eBookTp": "0",
    "bestType": "YES24_BESTSELLER",
    "type": "",
    "saleYear": "0",
    "saleMonth": "0",
    "weekNo": "0",
    "saleDts": "",
    "viewMode": "",
    "freeYn": ""
}

def parse_number(text):
    if not text:
        return 0
    # 숫자와 소수점만 추출
    num_str = re.sub(r'[^\d.]', '', text)
    if not num_str:
        return 0
    try:
        return float(num_str) if '.' in num_str else int(num_str)
    except ValueError:
        return 0

def scrape_page(page_num):
    print(f"[Info] Scrapes page {page_num}...")
    params = PARAMS.copy()
    params["pageNumber"] = page_num
    
    # referer도 페이지 번호에 맞게 업데이트
    headers = HEADERS.copy()
    headers["Referer"] = f"https://www.yes24.com/product/category/bestseller?categoryNumber=001001003&pageNumber={page_num}&pageSize=24"
    
    try:
        response = requests.get(TARGET_URL, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            print(f"[Error] Failed to fetch page {page_num}. Status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "lxml")
        # 각 도서 항목 li 태그를 찾음
        book_lis = soup.find_all("li", attrs={"data-goods-no": True})
        
        if not book_lis:
            print(f"[Info] No book items found on page {page_num}.")
            return []
        
        books = []
        for li in book_lis:
            goods_no = li.get("data-goods-no")
            
            # 랭킹 추출
            rank_el = li.find("em", class_="rank")
            rank = parse_number(rank_el.text) if rank_el else None
            
            # 도서 정보 영역
            item_info = li.find("div", class_="item_info")
            if not item_info:
                continue
            
            # 도서명
            title_el = item_info.find("a", class_="gd_name")
            title = title_el.text.strip() if title_el else ""
            
            # 부제목
            subtitle_el = item_info.find("span", class_="gd_nameE")
            subtitle = subtitle_el.text.strip() if subtitle_el else ""
            
            # 저자
            auth_el = item_info.find("span", class_="info_auth")
            author = ""
            if auth_el:
                auth_a = auth_el.find("a")
                if auth_a:
                    author = auth_a.text.strip()
                else:
                    author = auth_el.text.replace("저", "").strip()
            
            # 출판사
            pub_el = item_info.find("span", class_="info_pub")
            publisher = ""
            if pub_el:
                pub_a = pub_el.find("a")
                publisher = pub_a.text.strip() if pub_a else pub_el.text.strip()
                
            # 출판일
            date_el = item_info.find("span", class_="info_date")
            publish_date = date_el.text.strip() if date_el else ""
            
            # 가격 정보
            price_div = item_info.find("div", class_="info_price")
            shop_price = 0
            sale_price = 0
            discount_rate = 0
            point = 0
            
            if price_div:
                # 할인율
                sale_rate_el = price_div.find("span", class_="txt_sale")
                if sale_rate_el:
                    sale_rate_num_el = sale_rate_el.find("em", class_="num")
                    discount_rate = parse_number(sale_rate_num_el.text) if sale_rate_num_el else 0
                
                # 판매가
                sale_price_el = price_div.find("strong", class_="txt_num")
                if sale_price_el:
                    sale_price_num_el = sale_price_el.find("em", class_="yes_b")
                    sale_price = parse_number(sale_price_num_el.text) if sale_price_num_el else 0
                
                # 정가
                shop_price_el = price_div.find("span", class_="txt_num dash")
                if shop_price_el:
                    shop_price_num_el = shop_price_el.find("em", class_="yes_m")
                    shop_price = parse_number(shop_price_num_el.text) if shop_price_num_el else 0
                
                # 포인트적립
                point_el = price_div.find("span", class_="yPoint")
                if point_el:
                    point = parse_number(point_el.text)
            
            # 평가 정보
            rating_div = item_info.find("div", class_="info_rating")
            sale_index = 0
            review_count = 0
            rating = 0.0
            
            if rating_div:
                # 판매지수
                sale_num_el = rating_div.find("span", class_="saleNum")
                if sale_num_el:
                    sale_index = parse_number(sale_num_el.text)
                
                # 리뷰 개수
                rv_count_el = rating_div.find("span", class_="rating_rvCount")
                if rv_count_el:
                    rv_count_num_el = rv_count_el.find("em", class_="txC_blue")
                    review_count = parse_number(rv_count_num_el.text) if rv_count_num_el else 0
                
                # 리뷰 평점
                rating_el = rating_div.find("span", class_="rating_grade")
                if rating_el:
                    rating_num_el = rating_el.find("em", class_="yes_b")
                    rating = parse_number(rating_num_el.text) if rating_num_el else 0.0
            
            # JSON 데이터 파싱 (ORD_GOODS_OPT)
            opt_input = li.find("input", attrs={"name": "ORD_GOODS_OPT"})
            sort_no = ""
            sort_name = ""
            if opt_input and opt_input.get("value"):
                try:
                    opt_data = json.loads(opt_input.get("value"))
                    sort_no = opt_data.get("goodsSortNo", "")
                    sort_name = opt_data.get("goodsSortNm", "")
                    # 혹시 HTML 파싱에서 누락된 가격이나 저자가 있다면 JSON에서 보완
                    if not shop_price:
                        shop_price = opt_data.get("shopPrice", 0)
                    if not sale_price:
                        sale_price = opt_data.get("salePrice", 0)
                    if not author and opt_data.get("goodsAuth"):
                        author = opt_data.get("goodsAuth").replace("<", "").replace(">", "").replace(" 저", "").strip()
                except Exception as e:
                    print(f"[Warning] Failed to parse JSON for goods_no {goods_no}: {e}")
            
            book_data = {
                "순위": rank,
                "상품번호": goods_no,
                "도서명": title,
                "부제목": subtitle,
                "저자": author,
                "출판사": publisher,
                "출판일": publish_date,
                "정가": shop_price,
                "판매가": sale_price,
                "할인율(%)": discount_rate,
                "포인트": point,
                "판매지수": sale_index,
                "리뷰개수": review_count,
                "평점": rating,
                "분야코드": sort_no,
                "분야명": sort_name
            }
            books.append(book_data)
            
        return books
    except Exception as e:
        print(f"[Error] Exception occurred while scraping page {page_num}: {e}")
        return []

def main():
    print("=== YES24 Bestseller Scraper Started ===")
    all_books = []
    page = 1
    
    while True:
        books = scrape_page(page)
        if not books:
            print(f"[Info] Scraped finished. No more data on page {page}.")
            break
            
        all_books.extend(books)
        print(f"[Info] Successfully scraped page {page}. (Current total: {len(all_books)} books)")
        page += 1
        time.sleep(1.0)  # 사이트 부하 방지를 위한 딜레이
        
    if all_books:
        # 데이터프레임 변환
        df = pd.DataFrame(all_books)
        
        # 저장 경로 생성
        output_dir = os.path.join("yes24", "data")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "yes24_bestseller.csv")
        
        # CSV 저장
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"[Success] Saved {len(all_books)} books to {output_file}")
    else:
        print("[Error] No books collected.")

if __name__ == "__main__":
    main()
