"""
iHerb 영양제 상품 데이터 전체 수집 스크립트.
이 스크립트는 iHerb 카테고리 v2 supplements API를 사용하여 
1페이지부터 마지막 페이지까지 모든 영양제 상품 정보를 순차적으로 수집하고,
그 결과를 CSV 파일로 실시간 저장(append)합니다.
"""
import requests
import csv
import json
import os
import sys
import time

# Windows 콘솔 한글 인코딩 문제 방지
sys.stdout.reconfigure(encoding='utf-8')

def main():
    url = "https://catalog.app.iherb.com/category/v2/supplements"
    headers = {
        "origin": "https://kr.iherb.com",
        "referer": "https://kr.iherb.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "content-type": "application/json"
    }
    
    # CSV 헤더 정의
    headers_csv = [
        "productId", "displayName", "brandName", "partNumber",
        "listPrice", "discountPrice", "rating", "ratingCount",
        "url", "packageQuantity", "productForm", "pricePerServing"
    ]
    
    # 데이터 폴더 및 파일 경로 설정
    os.makedirs("data", exist_ok=True)
    csv_file_path = os.path.join("data", "iHerb_supplements.csv")
    
    # 기존 파일이 있다면 헤더를 새로 쓰지 않고 새로 만듦
    with open(csv_file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers_csv)
        writer.writeheader()
    
    page = 1
    page_size = 48
    total_scraped = 0
    consecutive_empty_pages = 0
    max_retries = 3
    
    print("전체 데이터 수집을 시작합니다...")
    
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
        
        products = []
        for attempt in range(1, max_retries + 1):
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    products = data.get("products", [])
                    break
                else:
                    print(f"[페이지 {page}] API 오류 - HTTP {res.status_code} (시도 {attempt}/{max_retries})")
            except Exception as e:
                print(f"[페이지 {page}] 네트워크 오류 발생: {e} (시도 {attempt}/{max_retries})")
            
            if attempt < max_retries:
                time.sleep(2)  # 재시도 전 대기
        
        if not products:
            consecutive_empty_pages += 1
            print(f"[페이지 {page}] 상품 데이터를 가져오지 못했습니다. (연속 빈 페이지: {consecutive_empty_pages})")
            # 연속으로 3페이지가 빈 페이지이면 수집 종료
            if consecutive_empty_pages >= 3:
                print("더 이상 수집할 데이터가 없어 종료합니다.")
                break
        else:
            consecutive_empty_pages = 0
            
            # CSV 파일에 데이터 추가 (append)
            try:
                with open(csv_file_path, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=headers_csv)
                    for p in products:
                        row = {
                            "productId": p.get("productId"),
                            "displayName": p.get("displayName"),
                            "brandName": p.get("brandName"),
                            "partNumber": p.get("partNumber"),
                            "listPrice": p.get("listPrice"),
                            "discountPrice": p.get("discountPrice"),
                            "rating": p.get("rating"),
                            "ratingCount": p.get("ratingCount"),
                            "url": p.get("url"),
                            "packageQuantity": p.get("packageQuantity"),
                            "productForm": p.get("productForm"),
                            "pricePerServing": p.get("pricePerServing")
                        }
                        writer.writerow(row)
                
                total_scraped += len(products)
                print(f"[진행] 페이지 {page} 완료 - {len(products)}개 상품 추가 (누적: {total_scraped}개)")
            except Exception as e:
                print(f"[페이지 {page}] CSV 저장 실패: {e}")
        
        # 다음 페이지로
        page += 1
        # 서버 부하 및 차단 방지를 위한 약간의 대기시간
        time.sleep(0.3)
        
    print(f"\n데이터 수집 완료! 총 {total_scraped}개의 상품 데이터가 '{csv_file_path}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
