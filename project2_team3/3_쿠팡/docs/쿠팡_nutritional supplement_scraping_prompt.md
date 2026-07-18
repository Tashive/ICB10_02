쿠팡 헬스/건강식품 카테고리에서 프로젝트 대상 상품만 수집하고 저장

https://scrapling.readthedocs.io/en/latest/
을 사용해서 아래 카테고리 페이지의 상품 목록을 수집할 것.
이때 첫 페이지 데이터를 수집하고 수집 항목이 제대로 나오면
전체 페이지를 순회하여 수집하는 방법으로 진행할 것.

https://www.coupang.com/np/categories/305798?page=1&per_page=72


### 수집 대상 필터 조건 (반드시 준수)
아래 6개 카테고리에 해당하는 상품만 수집하고 나머지는 제외할 것.

포함 키워드 (상품명에 하나라도 포함되면 수집):
- 멀티비타민 / 종합비타민 / 멀티미네랄
- 비타민C / 비타민 C / 비타민씨 / 아스코르브산
- 오메가3 / 오메가-3 / EPA / DHA / 피쉬오일 / 어유
- 유산균 / 프로바이오틱스 / 락토바실러스
- 콜라겐 / collagen
- 마그네슘 / magnesium

제외 키워드 (상품명에 포함되면 수집 제외+포함키워드가 없을 경우 수집 제외):
- 단백질 / 프로틴 / 헬스보충제
- 다이어트 / 체중감량 / 지방연소
- 한약 / 홍삼 / 녹용


### 수집 항목
플랫폼, 브랜드, 상품명, 카테고리, 가격, 할인율,
평점, 리뷰수, 로켓배송여부, 상품URL, 수집일


1) HTTP 요청정보
Request URL
https://www.coupang.com/np/categories/305798
Request Method
GET
Status Code
200 OK
Remote Address
23.35.218.121:443
Referrer Policy
strict-origin-when-cross-origin


2) HTTP 헤더정보
:authority
www.coupang.com
:method
GET
:path
/np/categories/305798
:scheme
https
accept
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-encoding
gzip, deflate, br, zstd
accept-language
ko,en-US;q=0.9,en;q=0.8,ar;q=0.7
cache-control
max-age=0
cookie
PCID=17813117138244692856770; MARKETID=17813117138244692856770; x-coupang-target-market=KR; x-coupang-accept-language=ko-KR; sid=cf049040937640949e766943f08286f8f9856f9a; gd1=Y; bm_ss=ab8e18ef4e; bm_sz=5F4F29ED6EF8D9CEA6657AD1539241F5~YAAQNq0sF4gES+WeAQAAC92v+QAF2lxVHQol4hBBWN0xR271gNaKzKgHodalO+7PIOX64ldmHuOGpSF3Mpm8Qcoq8ZECSMpsOZdyJeNDAG67kcvTL1eYe+faBgjoWQj8Ngb1nFvNCwfU8dAlb6oebJImU6JSfz3cGmzRPmmhfcLxeMrJV3L/ooxaS6u+aPQd3aPa2Ww2sbcyHYk/vhqbsQgSliwEr+s21lVDTbZjGbfRwsZ7OPkmpPfmOXWbntLbKjWnC2093ONwzgaQJbKckEVHBe7DD+TldOtLzo0oNRJX80bQHdNhsXKvZcdAPVmaTA6+kmXpvEsdkYl2rXozpf38xKx5dZzKZ2IfXhP0+Gg9XuPbf1IdFfCJ+ynNxhRWzJ6m+8W/cIMc4A3DpsO4~3422529~3163461; _abck=6435AFF5EA2D5D8997C1F951924CCCD9~0~YAAQNq0sF2gGS+WeAQAAfN+v+RAQQiQ/eMHm2aYcCyQifMstpRhuMLff+IN2MFD0qB7WO4hRxyLq7EtxN2Vivmnit6COxOV39vTbre9KQCKUJlilnFVn5+yNWx7mds5DpgaXEmi/wdQLeu7XlSuNpNUYrc1rNO45vuglH96g5/GJ4C5Oev9Y+6L2vNKNyd+Ndpp+AHUChgpvlmp8jy91yuZlSxOXrQ3xsbjkSvtfAsUCP6q2vbQIrScNHvIjYAVOEO0wyhdytiP6v5cmQYVAxs15axGoGC77Gq/daf1HDb37+C98/TVXagFiHzZkf0z2Y7fZ7kVm2jE1EKFY27kkd+8aLCTwde8PAu0F3Py5PSxpJv0yulk4KyA/13ZBilAMgRKchj13rRaQGDKiwh4JZeadD4pZRqCauCPgM1ISs9stF5/YW6dpmIpvhFkZPpJBOpYMoqVxiFHxafZqpezDr4PGzNyEoZtgi6TRuinavpBUc3V/yl2PUu/wS1NdDbb0ZyFRTGZ7nAUuLtLX096YufGVUUPYD4G0JnpJpzzgIRtXEzdc+u2SftLlehuyc4C9cvhe7nLsw4eIG6zgsqh6RtR+mGthH4vifxenQttFyUOFE8yRUWq6cvzZpnGobnOhCkLmycxWbhjj1I5L8xjitACOGg==~-1~-1~1782309113~AAQAAAAF%2f%2f%2f%2f%2f2B7hMJPPjebzEG5OaqVYJfRZDffW5qYzuISJjzSx7loCo2BK9yrNGurTIn0ekig7zcCO%2fUFPOsERhbQBOEmldyCCElPx2ar7cDH~-1; ak_bmsc=E6C652386D0B814FB1B19EBD2E7F3539~000000000000000000000000000000~YAAQNq0sFxUJS+WeAQAA2+Kv+QCVTpQg3hsi/430CwgngT+T9tNN+ooK4lm+DZSBR6Lqazs+UmMkmK7QWGwzsx5TRciGx207yu85vP8obqpJp7ft8LjV7KMfluVy9NdKkkWcIER3zuvsRE1iqypnZDTCOsWXV5gZ15MQkOKyT7PhjUMI2UgVnJsdB1vgj3ycWDKV9SXCdInjWlql6VJjbnE7CzDXcUF2yiNbjcUU8VGGnFGuu6evJgh1Mxk1BZ5GvnmXDjWx/+fbMim+b7fI06ScyEbwErPEURav3cDiO7kXn44aGh7ThnFNxQUTAEzahu1MH8mNqK/G65k6/O+TmTylNa1XNcWJPE3N1orp5m0wMkVu6t5Twzqfm3Vd+zZELSKkdUP6Ku9Ika7GBSoPRT+a6d/SnsKa8RbpTRuY22HEM776h/6NYR/WLX6+o+rc/LJSNa79pIhUsqzoz/wpIg==; bm_so=8F9F3021F575E1EE5571E0AC922BB0216DE8FEB4CA1019EF45D9DBD03A1E9255~YAAQZtojF/TlVLeeAQAA23e0+QjViCXeQQQmZlJLx9u/x3mD0X7xqXj6Jt1aDNPZlVc8F9ZZ2WyzhszD82ub/r+fM2lsrFIndIBGktbS88FjY5Y86W6u2+7t1iZlDhqylMPx+Fsncl9j7xs7e5uJ1tfVH14JcLqQ4ed+E1I+RTve1h4qZY747w7dPE7hMcAO3J6oFa7DbTcnNuoJ0n038BCkJTRCPOedB0MgYhKcuN6rqrVUssgd//wxKScLMyY4xgkg2ljCvZ/EQfSPi+ohsxyn10tPQSiV45xpFowrRUV07S+QO0o2NytyXFLxPh4Wb1jcXuPgjRZHivktnjUczoRPqJ7HBowal32Dbl9mJurPPpJ57kvro/4AJ1v+9lBNyez1vG7AUZPuhVLjRNZeuA4bErtc7eZ7QoPMXAhMg4Q81PM28czksvzK3t2TgtzAEoVf/ZubWzODrXApzIYRVvLX/A==; bm_sv=BFD77E7096DD66590B8B150C09E9700E~YAAQZtojF/XlVLeeAQAA23e0+QCAZHqQot2U8jmGjJJD5UJSA8A1phJ0zp1oHFdXLKbxGFdQTLSZKG9IAdC1biuV/NBWeOiUKuOGw+UPQmIarD5l3uhobsje/swSg7i+o+SgoB9GVGBJI49roastdDrlKiLRYFCIsMxstp6hU8UyzwTGTotw0phXYDJv6eo5xFgCkQa6cioKZke7oli0o6pepiADD/zZslq8Hc1xsVmO8aaETh4+20yas3oQRfbW5A==~1; x-cp-s=YzE9MyZjMj0xLjAuMCZjMz0xNzgyMzA1ODE0MDE3JmM0PVdVNW9LMmhKY1VWNGJVSXdiM05UUlRGSU4zazViMkpKY210RU5uQkthWGRYUm5vMmVFWnFjWEZ1UzBsdWFqUm5TME54SzJ0TmFrbHRkRXhITTA5SksydHlZbFYxUVZOUFRuTTJkVVZ6VVVVeVREWnBhMFozZVVOR1FXMUZhVXBwUmtKWlJVMVFRVVZpYlc5dFEwUnZNSHB1V21kaGFYaHhTa1puTWxOdGVHZERjMmM5JmM1PWNvbS5jb3VwYW5nLndlYiZjNj0mYzc9JmM4PTlhNjg4ODNhYjI0OTRjZTdhZDdhMDk5NTZkYTFjMjVlJmM5PTgmczE9ZitnSVlCRUI2eEo3cHFzWmc1aXFaNEFTT25kMU54U25OUGpZR01wbytNUT0mczI9MS4wLjA=; bm_lso=8F9F3021F575E1EE5571E0AC922BB0216DE8FEB4CA1019EF45D9DBD03A1E9255~YAAQZtojF/TlVLeeAQAA23e0+QjViCXeQQQmZlJLx9u/x3mD0X7xqXj6Jt1aDNPZlVc8F9ZZ2WyzhszD82ub/r+fM2lsrFIndIBGktbS88FjY5Y86W6u2+7t1iZlDhqylMPx+Fsncl9j7xs7e5uJ1tfVH14JcLqQ4ed+E1I+RTve1h4qZY747w7dPE7hMcAO3J6oFa7DbTcnNuoJ0n038BCkJTRCPOedB0MgYhKcuN6rqrVUssgd//wxKScLMyY4xgkg2ljCvZ/EQfSPi+ohsxyn10tPQSiV45xpFowrRUV07S+QO0o2NytyXFLxPh4Wb1jcXuPgjRZHivktnjUczoRPqJ7HBowal32Dbl9mJurPPpJ57kvro/4AJ1v+9lBNyez1vG7AUZPuhVLjRNZeuA4bErtc7eZ7QoPMXAhMg4Q81PM28czksvzK3t2TgtzAEoVf/ZubWzODrXApzIYRVvLX/A==~1782305814046; bm_s=YAAQZtojF13nVLeeAQAAeoC0+QVZ2xB1Vu/uijEZp+iaRA5u1hs9oEQJ6+oH8PTR7oGLQsRHC4SLUipow7iWyB3qguLJu1175S3gu+8whHhJMIx0KXObvV1G3elLrD+7YBj1oaxR7gXezSjIrkwFYxh0l62diK5m9pAP/bxM3WVufBbS/RYoREO4r2fRRgO/DufU3OTgihY4JpxBQdpihhdLqSnekxqK1f5AqE9EpO9hPyT18geOJAWFM/JQ8gEcvm72Op9Tdzoh9d2OuNEnnVmwaQ13tbg8A8nXrQExicVpsrni86ZJZiVMirpmzMkl3cmAhAlJSkG6jYs+u5ce0vbbYGZ0JVCJwFVEWEKnkxR2H4nLSzTI74aIjOZQzoGQ4bG5LNw9jOPfqgcxLIHttwuzfjy7pPB7XXjuoWvQVSeVG3CFEfdJTKSezn4JTpR+9chLvFGejZx3dpo8gaHvass4y583ssk4RnmBcygDtoYmx+xdRxhMHawVeQ/kVHTVG6XbmWLoq9XKbH9Da7JUrDF7XpomTS74KoraAC6wDhTvnpVNtk4CDrTQIdfzKyZw+tIR7y+DlbpjRgThdPSS/ZsUZZ4QaJJdncYysSJhBFX/XkURO7+vJv2p4V5M+lJ2+POGmUf3RH26qZ6YQ3hkHLYOlLIqe9AHm+ly1lOw3944a/EeaJSg63a/z3CZnFWzu8thRa6bqxBwZQrq6jKIAMFCym7ixm+nKaYyjjUBEp5lQ+vcOQlCsNl/A/9Y4Bk4M1MejSv18/O3tMEXnM87O058R3Wadfo4wbXN3jO6XqXN0475ueqZU6IvGgPkfAC5sGTzsaMx1cTz1R1xuC/MIiQ7qTDXG04dk3kxkG37hobvkkSB9A/wFMQnUdba+4PkmieMqhUDcVwpC+o01IPGTM2lzP9jMqprX4IxMyiq/bq0y1ObWKB2WtpGsQHmfSYknhujZxAj5ckYArGwXGLhUGpxJYfPDW4vdP8=
priority
u=0, i
sec-ch-ua
"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"Windows"
sec-fetch-dest
document
sec-fetch-mode
navigate
sec-fetch-site
same-origin
sec-fetch-user
?1
upgrade-insecure-requests
1
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36

3) Payload 정보


4) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)
<li class="ProductUnit_productUnit__Qd6sv" data-id="0">
    <a href="/vp/products/9360717888?itemId=27774354719&vendorItemId=94764769887&sourceType=CATEGORY&categoryId=305698">
        <figure class="ProductUnit_productImage__Mqcg1">
            <img alt="[정품] 자보티카바 정 Jaboticaba, 1개, 120정" .../>
        </figure>
        <div class="ProductUnit_productInfo__1l0il">
            <div class="ProductUnit_productNameV2__cV9cw">[정품] 자보티카바 정 Jaboticaba, 1개, 120정</div>
            <div class="PriceInfo_discountRate__EsQ8I">88%</div>
            <strong class="Price_priceValue__A4KOr">9,900원</strong>
            <div class="ProductRating_star__RGSlV" style="width:90%">4.5</div>
            <span class="ProductRating_ratingCount__R0Vhz">(3512)</span>
        </div>
    </a>
</li>


5) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장할 것