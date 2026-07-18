1) HTTP 요청정보

https://catalog.app.iherb.com/category/sports/specials?isMobile=false&page=1&pageSize=18
Request Method
GET
Status Code
200 OK
Remote Address
172.64.149.245:443
Referrer Policy
strict-origin-when-cross-origin

2) HTTP 헤더정보

origin
https://kr.iherb.com
priority
u=1, i
referer
https://kr.iherb.com/
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
same-site
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36

3) Payload 정보

isMobile=false&page=1&pageSize=18

4) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

{
    "products": [
        {
            "productId": 85667,
            "displayName": "California Gold Nutrition, CLA, Clarinol, 복합 리놀레산, 1,000mg, 소프트젤 90정",
            "url": "https://kr.iherb.com/pr/california-gold-nutrition-cla-conjugated-linoleic-acid-1-000-mg-90-veggie-softgels/85667",
            "partNumber": "CGN-01264",
            "listPrice": "₩29,668",
            "discountPrice": "₩22,251",
            "tag": null,
            "isOutOfStock": false,
            "hidePrice": false,
            "isDiscontinued": false,
            "isNotAvailable": false,
            "isNoPO": false,
            "showDiscount": true,
            "rating": 4.6,
            "ratingCount": 3087,
            "ratingCountFormatted": null,
            "ratingUrl": "https://kr.iherb.com/pr/california-gold-nutrition-cla-conjugated-linoleic-acid-1-000-mg-90-veggie-softgels/85667#product-reviews",
            "reviewUrl": "https://kr.iherb.com/r/california-gold-nutrition-cla-conjugated-linoleic-acid-1-000-mg-90-veggie-softgels/85667",
            "isShippingSaver": false,
            "isFeaturedBrand": false,
            "productFlags": null,
            "showGroupMessage": false,
            "isProductCompared": false,
            "isSeasonallyUnavailable": false,
            "discountPercentage": null,
            "salesDiscountPercentage": 25.0,
            "brandCode": "CGN",
            "brandName": "California Gold Nutrition (캘리포니아 골드 뉴트리션)",
            "primaryImageIndex": 235,
            "specialDealInfo": {
                "percentageClaimed": 4.0,
                "isCompletelyClaimed": false,
                "countPerCustomer": 0,
                "progressType": 0,
                "progressColor": "",
                "progressMessage": "",
                "isAtRisk": false
            },
            "hasRating": true,
            "hasTag": false,
            "currencySymbol": "₩",
            "isCurrencySymbolOnLeft": true,
            "discountPriceValue": "22251.0",
            "discountMessage": null,
            "bogoDiscountInfo": null,
            "promoCode": null,
            "promoCodeMessage": "",
            "promoCodeApplied": null,
            "isComingSoon": false,
            "discountType": 1,
            "discountDisplayType": 1,
            "isInCartDiscount": false,
            "ratingStarsMap": [
                1.0,
                1.0,
                1.0,
                1.0,
                0.5
            ]
        }
    ]
}

5) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장할 것 (완료)
- 스크립트 위치: `iherb/src/scrape.py`
- 데이터 저장 위치: `iherb/data/sports_specials_page1.csv`

6) 1페이지부터 마지막페이지까지 모든 데이터 수집 (완료)
- 수집 범위: 1페이지 ~ 29페이지 (30페이지에서 데이터 없음 감지하여 자동 종료)
- 전체 수집 상품 수: 507개
- 데이터 저장 위치: `iherb/data/sports_specials.csv`
