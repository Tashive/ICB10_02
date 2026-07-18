"""
쿠팡의 건강식품 카테고리(305798)에서 영양제 관련 상품 정보를 수집하는 스크립트입니다.
scrapling 라이브러리의 Fetcher.get()을 사용하여 페이지 단위로 상품 목록을 수집하며,
봇 차단 감지 시 대기 후 재시도(Retry) 메커니즘을 적용하여 카테고리 내의 전체 데이터를 끝까지 안전하게 수집합니다.
"""

import os
import re
import time
import random
import pandas as pd
from datetime import datetime
from scrapling import Fetcher

# 수집 대상 카테고리 번호 및 기본 URL
CATEGORY_ID = 305798
BASE_URL = "https://www.coupang.com/np/categories/305798"

# 제공된 HTTP 헤더 및 쿠키 정보 설정 (ASCII 문자만 포함)
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "ko,en-US;q=0.9,en;q=0.8,ar;q=0.7",
    "cache-control": "max-age=0",
    "cookie": "PCID=17813117138244692856770; MARKETID=17813117138244692856770; x-coupang-target-market=KR; x-coupang-accept-language=ko-KR; sid=cf049040937640949e766943f08286f8f9856f9a; gd1=Y; bm_ss=ab8e18ef4e; bm_so=7948F108742C477B65959921581461BE50D8BA5A28BD34F5E76AB9F4F8342EEF~YAAQLmHKF5wn/dmeAQAAl64vEwhx5bpLQ/R5QMa5GyJtMJrLpA76MMHqbXLqxZX2Z0HaD7SgyoX+egl6R37nmk14EZDZO6SpR6SkofycPv/305xNYI4rGWsq03MrqtkuWBMTnNbwurFHIzhhpQFqSjjOk3btA8Y4nF3gKD4hPSPHLfj7rZ2AsLMBm8KOjX+NcX+3EM+3K3lO6uZnwQ14IRhGcfhdG/Q+O/lmiZE3/+lux2o5Ui+jTsNJ1lC8oB6FDgNUYfj/iAxac90wGJPphusV7w9hM8UbA3tREBuCpGM/t8WRITqW8TTTF45dGsbtEzMcPBFtLDz3Xas/XTJz7dUEZXz3CFF0j3OkBgKjuKL/Z7CpeTOiOyQa1j4rgfJ9unFZgkI5XK",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "referrer": "https://www.coupang.com/",
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

def extract_brand(product_name):
    """
    상품명에서 브랜드 정보를 정교하게 추출합니다.
    """
    matches = re.findall(r'\[([^\]]+)\]', product_name)
    exclude_keywords = {
        '정품', '해외직구', '쿠팡직수입', '본사직영', '1+1', '2+1', '3+1', '4+1', '단품', 
        '공식', '공식수입', '한정수량', '특가', '기획', '무료배송', '국내배송', '특별기획', '대용량'
    }
    for match in matches:
        clean_match = match.strip()
        if not any(ek in clean_match for ek in exclude_keywords) and len(clean_match) <= 15:
            if not re.search(r'\d+(정|캡슐|포|g|ml|병|개)', clean_match):
                return clean_match
    
    matches_parentheses = re.findall(r'\(([^)]+)\)', product_name)
    for match in matches_parentheses:
        clean_match = match.strip()
        if not any(ek in clean_match for ek in exclude_keywords) and len(clean_match) <= 15:
            if not re.search(r'\d+(정|캡슐|포|g|ml|병|개)', clean_match):
                return clean_match
            
    words = product_name.split()
    if words:
        first_word = words[0]
        first_word_clean = re.sub(r'[\[\]\(\)]', '', first_word).strip()
        if not any(ek in first_word_clean for ek in exclude_keywords) and len(first_word_clean) > 1:
            return first_word_clean
            
    return "기타"

def classify_category(product_name):
    """
    상품명 기준으로 카테고리를 분류하고 수집 대상 여부를 필터링합니다.
    """
    name_lower = product_name.lower()
    
    exclude_keywords = ['단백질', '프로틴', '헬스보충제', '다이어트', '체중감량', '지방연소', '한약', '홍삼', '녹용']
    if any(ek in name_lower for ek in exclude_keywords):
        return None
        
    categories_keywords = {
        '멀티비타민/종합비타민/멀티미네랄': ['멀티비타민', '종합비타민', '멀티미네랄'],
        '비타민C': ['비타민c', '비타민 c', '비타민씨', '아스코르브산'],
        '오메가3': ['오메가3', '오메가-3', 'epa', 'dha', '피쉬오일', '어유'],
        '유산균': ['유산균', '프로바이오틱스', '락토바실러스'],
        '콜라겐': ['콜라겐', 'collagen'],
        '마그네슘': ['마그네슘', 'magnesium']
    }
    
    matched_categories = []
    for cat, keywords in categories_keywords.items():
        if any(kw in name_lower for kw in keywords):
            matched_categories.append(cat)
            
    if not matched_categories:
        return None
        
    return matched_categories[0]

def is_bot_detected(html_content, products_count):
    """
    HTML 콘텐츠 및 파싱된 상품 수를 기준으로 봇 감지 여부를 확인합니다.
    """
    if not html_content:
        return True
    html_lower = html_content.lower()
    bot_keywords = ["captcha", "denied", "robot", "ip block", "접속이 제한", "보안"]
    if any(keyword in html_lower for keyword in bot_keywords):
        return True
    # 상품 수가 0개인 경우도 봇 디텍션 화면일 가능성을 고려
    if products_count == 0:
        return True
    return False

def scrape_coupang():
    """
    쿠팡 영양제 카테고리 목록을 순회하여 필터 조건에 부합하는 상품 데이터를 수집합니다.
    봇 차단 발생 시 자동으로 대기 후 재시도하며 끝까지 모든 데이터를 가져옵니다.
    """
    # 기존에 수집된 데이터 로드 (이어서 수집하기 위함)
    output_dir = "project2_team3/3_쿠팡/data"
    if not os.path.exists(output_dir):
        output_dir = "data"
    output_path = os.path.join(output_dir, "coupang_nutritional_supplements.csv")
    
    existing_df = None
    existing_urls = set()
    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path, encoding="utf-8-sig")
            if "상품URL" in existing_df.columns:
                existing_urls = set(existing_df["상품URL"].dropna().tolist())
            print(f"기존 수집 데이터를 로드했습니다: {len(existing_df)}건 (고유 URL 수: {len(existing_urls)}개)")
        except Exception as e:
            print(f"기존 수집 데이터 로드 중 오류 발생 (처음부터 새로 수집합니다): {e}")

    all_products_data = []
    page = 8
    max_empty_pages = 2  # 연속으로 진짜 빈 페이지가 2번 이상 나오면 수집을 마침
    empty_consecutive = 0
    
    print("쿠팡 영양제 카테고리 전체 상품 수집을 시작합니다. (Fetcher.get + 재시도 로직)")
    
    while True:
        url = f"{BASE_URL}?page={page}&per_page=72"
        print(f"\n[Page {page}] 요청 중... (현재 누적 수집 건수: {len(all_products_data)}개)")
        
        # 재시도 루프
        max_retries = 5
        retry_delay = 20  # 차단 시 대기할 기본 초 (차단당할 때마다 점진적으로 늘어남)
        success = False
        products = []
        response_html = ""
        
        for retry in range(1, max_retries + 1):
            try:
                response = Fetcher.get(url, headers=HEADERS, impersonate="chrome")
                response_html = response.html_content if response.html_content else ""
                
                if response.status == 200:
                    products = response.css('li[class*="ProductUnit_productUnit"]')
                    
                    # 봇 차단 여부 검사
                    if is_bot_detected(response_html, len(products)):
                        if "접속이 제한" in response_html or "captcha" in response_html.lower() or "denied" in response_html.lower():
                            print(f"  -> [경고] 봇 차단 감지됨 (시도 {retry}/{max_retries}). {retry_delay}초간 대기 후 다시 시도합니다...")
                            time.sleep(retry_delay)
                            retry_delay += 10  # 대기 시간 점증
                            continue
                        else:
                            # 봇 차단 키워드가 없고 진짜 상품이 0개인 경우 (끝 페이지 도달 가능성)
                            # 일단 한 번 더 검증해보기 위해 15초 쉬고 1회는 무조건 재시도
                            if retry == 1:
                                print(f"  -> [알림] 상품이 0개입니다. 혹시 모를 차단을 대비하여 15초 대기 후 1회 재시도합니다...")
                                time.sleep(15)
                                continue
                            else:
                                # 재시도했는데도 차단 키워드 없이 계속 0개면 진짜 빈 페이지로 판단
                                success = True
                                break
                    else:
                        # 봇 감지 안 됨 & 상품이 정상적으로 1개 이상 존재
                        success = True
                        break
                else:
                    print(f"  -> [에러] HTTP 상태코드 {response.status} (시도 {retry}/{max_retries}). {retry_delay}초간 대기합니다...")
                    time.sleep(retry_delay)
                    retry_delay += 10
                    
            except Exception as e:
                print(f"  -> [예외] 요청 중 오류 발생: {e} (시도 {retry}/{max_retries}). {retry_delay}초간 대기합니다...")
                time.sleep(retry_delay)
                retry_delay += 10
        
        # 재시도 루프 후 처리
        if not success:
            print(f"[Page {page}] 최종 요청 실패로 수집을 안전하게 중단합니다.")
            break
            
        # 상품 목록 파싱
        if not products:
            print(f"[Page {page}] 진짜 빈 페이지로 확인되었습니다.")
            empty_consecutive += 1
            if empty_consecutive >= max_empty_pages:
                print("더 이상 수집할 상품 페이지가 없습니다. 순회를 정상 종료합니다.")
                break
        else:
            empty_consecutive = 0
            print(f"[Page {page}] 검색된 상품 수: {len(products)}개")
            
            page_parsed_count = 0
            for product in products:
                name_el = product.css('[class*="productName"]')
                product_name = name_el[0].text.strip() if name_el else ""
                
                if not product_name:
                    continue
                    
                category = classify_category(product_name)
                if not category:
                    continue
                    
                brand = extract_brand(product_name)
                
                price_el = product.css('[class*="priceValue"]')
                price_str = price_el[0].text.strip() if price_el else ""
                price = int(re.sub(r'[^0-9]', '', price_str)) if price_str else 0
                
                discount_el = product.css('[class*="discountRate"]')
                discount = discount_el[0].text.strip() if discount_el else "0%"
                
                rating_el = product.css('[class*="star"], [class*="Rating_star"]')
                rating_str = rating_el[0].text.strip() if rating_el else "0.0"
                try:
                    rating = float(rating_str)
                except ValueError:
                    rating = 0.0
                    
                reviews_el = product.css('[class*="ratingCount"]')
                reviews_str = reviews_el[0].text.strip() if reviews_el else ""
                reviews = int(re.sub(r'[^0-9]', '', reviews_str)) if reviews_str else 0
                
                is_rocket = False
                delivery_badge = product.css('[class*="delivery"], [class*="Badge"]')
                for badge in delivery_badge:
                    badge_text = badge.text.strip()
                    if '로켓' in badge_text or badge.attrib.get('data-badge-type') == 'delivery':
                        is_rocket = True
                        break
                        
                rocket_imgs = product.css('img[src*="rocket"], img[alt*="로켓배송"]')
                if rocket_imgs:
                    is_rocket = True
                    
                rocket_delivery = "Y" if is_rocket else "N"
                
                a_el = product.css('a')
                href = a_el[0].attrib.get('href', '') if a_el else ""
                product_url = f"https://www.coupang.com{href}" if href else ""
                
                # 기존 수집 데이터에 존재하는 URL인 경우 수집 제외
                if product_url in existing_urls:
                    continue
                    
                collect_date = datetime.now().strftime("%Y-%m-%d")
                
                all_products_data.append({
                    "플랫폼": "쿠팡",
                    "브랜드": brand,
                    "상품명": product_name,
                    "카테고리": category,
                    "가격": price,
                    "할인율": discount,
                    "평점": rating,
                    "리뷰수": reviews,
                    "로켓배송여부": rocket_delivery,
                    "상품URL": product_url,
                    "수집일": collect_date
                })
                page_parsed_count += 1
                
            print(f"[Page {page}] 필터 통과 상품 수: {page_parsed_count}개")
            
        page += 1
        # 페이지별 정상 딜레이 (봇 탐지 회피용: 2.5 ~ 4.5초)
        time.sleep(random.uniform(2.5, 4.5))
        
    print(f"\n수집 완료! 필터를 통과한 총 상품 수: {len(all_products_data)}개")
    
    if all_products_data or existing_df is not None:
        new_df = pd.DataFrame(all_products_data) if all_products_data else pd.DataFrame()
        if existing_df is not None:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.drop_duplicates(subset=["상품URL"], keep="first", inplace=True)
        else:
            combined_df = new_df
            
        os.makedirs(output_dir, exist_ok=True)
        combined_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"데이터가 업데이트되어 저장되었습니다: {output_path} (총 {len(combined_df)}건, 신규 수집 {len(all_products_data)}건)")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_coupang()
