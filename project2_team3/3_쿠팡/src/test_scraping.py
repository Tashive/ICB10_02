"""
쿠팡 건강식품 카테고리 상품 목록 수집을 위한 테스트 스크립트입니다.
제공된 쿠키와 헤더를 기반으로 scrapling 라이브러리를 사용하여 쿠팡 데이터를 정상적으로 조회할 수 있는지 검증합니다.
"""
import os
import sys
import json
from scrapling import Fetcher, DynamicFetcher


# 쿠팡 카테고리 URL
url = "https://www.coupang.com/np/categories/305798?page=1&per_page=72"

# 제공된 HTTP 헤더 및 쿠키 정보 설정
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "ko,en-US;q=0.9,en;q=0.8,ar;q=0.7",
    "cache-control": "max-age=0",
    "cookie": "PCID=17813117138244692856770; MARKETID=17813117138244692856770; x-coupang-target-market=KR; x-coupang-accept-language=ko-KR; sid=cf049040937640949e766943f08286f8f9856f9a; gd1=Y; bm_ss=ab8e18ef4e; bm_mi=09B18AB664073C9A3EC904CA636B5D0C~YAAQsjpvPXdPIgOfAQAACDxUBwA0CQsmlvoEyTeBwujnzNx2GX3tzk+uFSJC578f7SlcxBcsPsFrKUuJg2JXltlvRI/b6pDnmAf9Ox4zCUaBDGtPAQ+HRYP9L67wsSdiRyxekrZ/xi6IJ/a9S1wJEOFGhj0JsAnP3pX8t5ehdRFHiYFfanh9+GRKw4XQyOGF0MI09dWXsGuwuyOSwhkKp2m6723wg7PMFJUcKd89KOwzi4NPavQd8YWLKJE/3ul9UIrXeQSq8nQjd7Got88VwYv3FsZJ7L17FU2BY9x6pHWAjkNadIvLmOZMtieWa2yTjqpli+VV4YNFFYsS3EbbgFksGQ==~1; bm_sz=C86F315858B46E1E5A9DCFA070EF7187~YAAQsjpvPXtPIgOfAQAACDxUBwBhDwWcHOQZVjJyptFqt01MkCkMfjh1I/PQOSZVC6WJhQMsPX1sJVbt1Yr2SmFDRY2/jPmGHJ4Y8z6PmryZSDb/2BNrL1LiwEMShrBPWp8jdi9GZC02RapmXe6VJ/CC+86iYIud2j4AwMkFcQbsiRC28D0LxDddyaYSHTzQ2d1cTY7Jya6iBmyM9xQvsFG2ujONgoLLpydD9qsk/ky4Zq+mICFUwGFODCdEgbbSsA352cchNvGfvF8gn1wKLOhizRGpJA/bOip/EHMtwNQ5/jKshQ9DxdwVe6x+4hQ7iREzceIjLdYb2BlHsMxtdnDxJLbWxyOUzR1qbh1hNVkoOy5hVQIpQPsAlhKoF094aAsFMVUWzOazC0Mc0WZ+PqA=~4469556~3556403; _abck=6435AFF5EA2D5D8997C1F951924CCCD9~0~YAAQsjpvPf9PIgOfAQAAbzxUBxCAL7qXMJMy+DVfxmI9gzW21WCM0e43GUUNC5WEbYsVsAlycT2A9cukFqQpD4H+f5YcoPGXiFGXPbilOEQP5RgKGqt7WGQAx2JfQmyrqjrgZdJL3aPtHXIanqAedfCTkNTYM636Fnkp4zxOz3A9xPDQ/hZDj+xm7PMinSvIjLZxndpjYzE42h/vAfVTGygO+JaStMOuJl94Ox5PxfuAJuI2oQt71phSLlg3mxt0jiKcmpx3pVx/0JbRPLvxDmqVXDRvtYqsAQpfTvh6t7cJUILNrtWI5oSg+lWlWw86sh7xnq4UJcqCq6S5wIc1yP57YpxRkjqAg00sVzI1CxkCqHCjrI8C9KoZrwXLP03+cTCU2DkHbOTG/+tFV0Kx+LUxTsXlN2EEhBicYw7l7mu6TAk+3GRj85Vso7wG8vIBwZ/+E34yGCEaWOliwCc0y4g7SKbSzi/VOkzYnUois2HxRSwBv0jPzeMVdCsmJgJa1yn4RkmFauIe/2WrTzsrz4er/ekNgrSWklgi47BaMfczXNrAufpkMOMSG6P30/R0Dq0PhV2Js5AEfjunKGAAY4Szdzwvd/O/IgGrLN8kiZUNRc8ceFxBGhMiZkAywx8G6FqZFhfq70zkF9o4Ty5GzqZTsA==~-1~-1~1782537975~AAQAAAAF%2f%2f%2f%2f%2f+2Cnbr01DWoErtZrkHvHlM4KqKMqujTb%2fWASw3cIi9k%2f3i9+e3jluY+Sap7UqSZ%2fIww74jm2GIF6i2rslig1iLrdsHbEo64mmAa~-1; ak_bmsc=8F98803A1E5088653526ACCC43BA9DFE~000000000000000000000000000000~YAAQsjpvPSpYIgOfAQAABEJUBwD6gWicxTTorinaY6ZpAo8bgtTaCMF2KzZBKZSZsKDAHsxmdHw25ex/tKYG2mH0M1q4e0998xVqUHd0HkzQiK3VgNN3ReHhZpZZmyIxsuR0Bz93hJsUGlS7OjdFms9j+F64My8yDIzMbF4N/ujwj2aIoRm84IWLa8QRi0LnZVkAuCovrTW0mT1Yrrwou7LGBitGXqmzR1jIT32hZoLcI2FS9vVXPo38XhCNGCme17cpE7i8jYv4AAvXS0LZvQRk9lMXRoZHwTw3RWbEF1o/S1WiiQBaEkuizHFaRtW9/xU6LfP6nGi4LR/k/FM5GEiNfax39Edwqyjq/1DqMoZgeZ609v86hR1Ciekkp2hNMrqodi7i2h90WkS1ef1+oSHqjkPMR5n13slYfHeEsXDRBSIovkHeFyr9cKfH0HEoZOnDxdOOwi0BHUBhry3GrCMHfVDWQ/RbytWutAcSZNNkMrvmbOnWVpuRu3IyLRwgRcsP+oos; bm_so=9DAB7E3AA2CCCE55225A20AD90D839A6061EB921BF00FBDC81B628E4046D3DF0~YAAQjIj+eRM2oNOeAQAAU+Z1BwhClQYoBL2tUnCMlKkYyXSqChI2Mu36+Ip09tU9JVNnA6HJMcoFKMVavJiqQL2jSiS4y167Nz5BvdsavCmWDukLopJPk0PpmF3cZMhuq8jX0N0pO4IV/xc8u2wKI+QBjqgCFbtSKZ9/F4tCieSnsxRM1nlL0eCnJpZPnbYqJaCPgB2F31rkvydp9Yi0PPxv+KPDTNCvT9xPoRECUEmIHiqKGSvQARvFsF1BV2C44C0OgzkftBOQhzZpGCiDDnqs2yAjJMxKuSKMKXkRFfquMvsR0eQTQC6wky+L+CZc4nFn+uWqmu+MI5WRNNhhqLX6PoZ1Z8p019j6rveh2iBkLblLRm/AZRGXz5s55uF8u8GUTcef57GRCRgNfF/BczDa6t+oFdwoOXxkgyPTBAXyxSzKEcLOWPD9cHxUB3rkPUbqjnFnF1m/to93QHkfV9ZLiw==; bm_sv=322C4E20F3E7BF3499488BA7F865248B~YAAQjIj+eRQ2oNOeAQAAU+Z1BwDBWzv6tNeqbi1flDRqfaEocpQlB9flqRxA8hXfnXSe6/sL18XmL/qCosMGQhkrEmjpg3BPcMN9HvmFChoTP06UQ6UK+biM2WDlB3SHIqeBF6Wexbjp6TJxuukE8I8re/bYWozZKUfTFcbrKo2jZV08mbdegmHjvoiUPba6AUNlejNgmsQ63mZ0gq+DZ67lYmKjAftIgpYUM7w+7Y4w/GktxfkUBAAglan5f7cR7A==~1; bm_lso=9DAB7E3AA2CCCE55225A20AD90D839A6061EB921BF00FBDC81B628E4046D3DF0~YAAQjIj+eRM2oNOeAQAAU+Z1BwhClQYoBL2tUnCMlKkYyXSqChI2Mu36+Ip09tU9JVNnA6HJMcoFKMVavJiqQL2jSiS4y167Nz5BvdsavCmWDukLopJPk0PpmF3cZMhuq8jX0N0pO4IV/xc8u2wKI+QBjqgCFbtSKZ9/F4tCieSnsxRM1nlL0eCnJpZPnbYqJaCPgB2F31rkvydp9Yi0PPxv+KPDTNCvT9xPoRECUEmIHiqKGSvQARvFsF1BV2C44C0OgzkftBOQhzZpGCiDDnqs2yAjJMxKuSKMKXkRFfquMvsR0eQTQC6wky+L~-1; bm_s=YAAQfIj+ee3iTtSeAQAA3ct4BwXNAOnmG1hkImIQc+l/o8yrkKYMX9WYC3S9qPnyBQIDkM+8gw/1ZuHWo5gf/C/xS//7cM9lsHeeT0I4pu68Xw/8BH4qyNQbI8xUNkcsySEsboW0Zs4rqJ+YBKHRQTTK5k5Gyk78yHiq6yIn7IWWJ8NQ6pM9xdc28mt+MLtHhOGENo+K4Cqs/jWa+8msiNIV9I/ix7RvAhodufKCH+bDaSjfeBHbrkU/lAl+fMQVzVmfIM4Kpg1bq1h4ib1WmSPVRCDggWls9nF0W6C3UulgUWe4lGw97d/CPzZq3spFktVGFW/+DTLWlLO/kN1GVZCUs9XeX4Bxmn3zWCp/UPxpKxstq9REvAIDUXA1RwhRhuejUlsn3tLulVZvBPRp19KQC/v5zFJ6bcLIYZZDh03uKxV4hj4S+28jVSzjFo/bNEiBGOv4Xah9CiBwFjgbi6RdBDIilLqQrUfz43nsXbO/ihxUA3+DDthbttb9JqSZR+FYKvqSxV03/xxDlHgMfcf5M3wcB6nFGLMy6JnUJyW5vB6QPbbScKxA9QQ0lSgliKEOlNRkhv+yaOHcIEODylwk9tYOR558cMe6hYInIGWuu2rSGoMsRrTsPQ/NSE3Qwpd61lt178IySQqTCGATXSAQcDWzNiXn/vl/ubE2Rva2X2c3CMvZ7j+1iVJTPD/AKyrRu6ydieoNHvUNbP91cDnILyqtrAheeZXFHqYy2SOVlomDKMCEQj4MrA9suzQLhEQxZZplg0WB4Cly0KPfr5Vj6uYpF/NPvtfq8BhS4Wr1WIBR2B/kQmSemUv49ICIsH+k6+do3Zx009hbDR6cfkqj3T3mTUra/9wqr3KSYx2uu01DbAQq/FkHSxoowV+lewkH1A82P3gbPRAy9x1EwWkLFwQAHfgeVPurBubzT9+B5igG73wa33WUkGpFUBJ8Y9BK0qxf/Z54xrTT2ytL0sqbOKX8ULpzues=; x-cp-s=YzE9MyZjMj0xLjAuMCZjMz0xNzgyNTM2Nzg5MzkyJmM0PVJFNW9LMmhKY1VWNGJVSXdiM05UUlRGSU4zazViMkpKY210RU5uQkthWGRYUm5vMmVFWnFjWEZ1UzBsdWFqUm5TME54SzJ0TmNXZHVhbW80YTA5SksydHlZbFYxUVZOUFRuTTJkVVZ6VVVVeVREWnBhMFozZVVOR1FXMUZhVXBwUmtKWlJVMVFRVVZpYlc5dFEwUnZNSHB1V21kaGFYaHhZa0kwT0RKb1VqaGFUV2M5JmM1PWNvbS5jb3VwYW5nLndlYiZjNj0mYzc9JmM4PTlhMTExMGY4MGEwMDA0MTdjYWNiM2U0MGZlZmJhY2I2MCZjOT00NCZzMT1ac0EyUHMyOFJWVDJDWkJMcVpQNDdMeEVHOHNSeDNiRkFaNmpqZG5jOHV3PSZzMj0xLjAgLjA=",
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

print("Fetching URL with DynamicFetcher...")
page = DynamicFetcher.fetch(url, headless=False)

print(f"Status Code: {page.status}")
print(f"HTML Length: {len(page.html_content) if page.html_content else 0}")

# HTML 내용 일부 저장
with open("test_page.html", "w", encoding="utf-8") as f:
    f.write(page.html_content)

import re
from datetime import datetime

# 브랜드 추출 함수
def extract_brand(product_name):
    matches = re.findall(r'\[([^\]]+)\]', product_name)
    exclude_keywords = {'정품', '해외직구', '쿠팡직수입', '본사직영', '1+1', '2+1', '단품', '공식', '공식수입', '한정수량', '특가', '기획', '무료배송', '국내배송', '특별기획'}
    for match in matches:
        clean_match = match.strip()
        if not any(ek in clean_match for ek in exclude_keywords) and len(clean_match) <= 15:
            return clean_match
    
    matches_parentheses = re.findall(r'\(([^)]+)\)', product_name)
    for match in matches_parentheses:
        clean_match = match.strip()
        if not any(ek in clean_match for ek in exclude_keywords) and len(clean_match) <= 15:
            return clean_match
            
    words = product_name.split()
    if words:
        first_word = words[0]
        if not any(ek in first_word for ek in exclude_keywords) and len(first_word) > 1:
            return first_word
            
    return "기타"

# 카테고리 매칭 및 필터링 함수
def classify_category(product_name):
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

# 18페이지 수집 테스트 (쿠키 없음)
url_18 = "https://www.coupang.com/np/categories/305798?page=18&per_page=72"
print("Fetching page 18 without cookies...")
no_cookie_headers = headers.copy()
if "cookie" in no_cookie_headers:
    del no_cookie_headers["cookie"]

page_18 = DynamicFetcher.fetch(url_18, headless=False)
print(f"Page 18 Status: {page_18.status}")
print(f"Page 18 HTML Length: {len(page_18.html_content) if page_18.html_content else 0}")

# HTML 내용 저장
with open("test_page_18.html", "w", encoding="utf-8") as f:
    f.write(page_18.html_content)

products_18 = page_18.css('li[class*="ProductUnit_productUnit"]')
print(f"Products found on page 18: {len(products_18)}")

# 봇 감지 키워드나 빈 페이지 키워드가 있는지 확인
html_lower = page_18.html_content.lower() if page_18.html_content else ""
if "captcha" in html_lower or "denied" in html_lower or "robot" in html_lower:
    print("WARNING: Bot detection keyword found in page 18 HTML!")
else:
    print("No bot detection keyword found in page 18.")




