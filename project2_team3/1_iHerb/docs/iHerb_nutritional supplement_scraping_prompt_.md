1) HTTP 요청정보

Request URL
https://catalog.app.iherb.com/category/v2/supplements/filters
Request Method
POST
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

{"categoryIds":[],"healthTopicIds":[],"attributeValueIds":[],"brandCodes":[],"priceRanges":[],"ratings":[],"weights":[],"specials":"","sort":null,"showShippingSaver":false,"showITested":false,"searchWithinKeyWord":"","programs":[],"showOnlyAvailable":false}


4) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

```json
{
  "displayName": "보충제",
  "totalSize": 25171,
  "filters": [
    {
      "filterName": "Sort",
      "displayName": "정렬 기준",
      "key": "Sort",
      "options": [
        {
          "displayName": "추천순",
          "value": "13",
          "count": 0,
          "groupKey": null,
          "priority": 0,
          "options": []
        }
      ]
    }
  ],
  "products": [
    {
      "productId": 64009,
      "displayName": "California Gold Nutrition, LactoBif® 30 프로바이오틱, 300억CFU, 베지 캡슐 60정",
      "url": "https://kr.iherb.com/pr/california-gold-nutrition-lactobif-30-probiotics-30-billion-cfu-60-veggie-capsules/64009",
      "partNumber": "CGN-00965",
      "listPrice": "₩35,140",
      "discountPrice": "₩26,355",
      "rating": 4.7,
      "ratingCount": 165873,
      "brandName": "California Gold Nutrition (캘리포니아 골드 뉴트리션)",
      "name": "LactoBif® 30 프로바이오틱, 300억CFU, 베지 캡슐 60정",
      "productName": "LactoBif® 30 Probiotics",
      "potency": "30 Billion CFU",
      "packageQuantity": "60 개",
      "productForm": "베지 캡슐",
      "pricePerServing": "₩439/제공량"
    }
  ]
}
```

5) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장할 것
- **수집 확인 완료**: 전체 페이지(1~525페이지, 총 25,171개 상품)의 데이터가 성공적으로 수집되었습니다.
- **저장 위치**: [iHerb_supplements.csv](file:///c:/Users/tasha/OneDrive/바탕 화면/ICB10_02/project2_team3/1_iHerb/data/iHerb_supplements.csv) 파일로 저장되었습니다.