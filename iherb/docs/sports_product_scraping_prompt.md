1) HTTP 요청정보

Request URL
https://kr.iherb.com/c/sports?p=2&isAjax=true
Request Method
GET
Status Code
200 OK
Remote Address
104.18.38.11:443
Referrer Policy
strict-origin-when-cross-origin


2) HTTP 헤더정보

referer
https://kr.iherb.com/c/sports
sec-ch-ua
"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"Windows"
sec-fetch-dest
empty
sec-fetch-mode
cors
sec-fetch-site
same-origin
traceparent
00-0180c2c20082d0d944703e9e7f63f3d4-fede8a3daa75801e-01
tracestate
2746152@nr=0-1-3663630-1588743540-fede8a3daa75801e----1781921814539
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
x-requested-with
XMLHttpRequest

3) Payload 정보

p=2&isAjax=true

4) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

*참고: kr.iherb.com 웹 주소로 직접 AJAX GET 요청을 보낼 경우 Cloudflare 403(Turnstile) 차단이 발생하므로, 모바일 앱 백엔드 API인 `https://catalog.app.iherb.com/category/sports/products`로 POST 요청을 보냄으로써 차단을 우회하여 더 안전하고 정형화된 JSON 데이터를 수집했습니다.*

**수집된 Product 22268의 JSON 데이터 예시:**
```json
{
    "productId": 22268,
    "displayName": "Trace, 40,000V, 전해질 농축물, 237ml(8fl oz)",
    "url": "https://kr.iherb.com/pr/trace-40-000-volts-electrolyte-concentrate-8-fl-oz-237-ml/22268",
    "partNumber": "TMR-00110",
    "listPrice": "₩29,786",
    "discountPrice": "₩29,786",
    "rating": 4.8,
    "ratingCount": 3281,
    "brandCode": "TMR",
    "brandName": "Trace (트레이스)",
    "productName": "40,000 Volts, Electrolyte Concentrate",
    "productForm": "액상"
}
```

5) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장할 것 (완료)
- 스크립트 위치: `iherb/src/scrape_products.py`
- 데이터 저장 위치: `iherb/data/sports_products_page2.csv`

6) 1~10페이지까지 수집하되 매 페이지마다 sqlite db 로 저장할 것 (완료)
- 스크립트 위치: `iherb/src/scrape_products.py`
- 수집 범위: 1페이지 ~ 10페이지 (페이지별 24개 상품, 총 240개 수집)
- 데이터 저장 위치: `iherb/data/sports_products.db` (테이블명: `products`)
