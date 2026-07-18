"""
test_fetch.py

trip.com의 호텔 리뷰 API를 호출하여 데이터 수집 가능 여부를 테스트하는 스크립트입니다.
수정일: 2026-06-22
"""

import json
from scrapling import Fetcher

def test_fetch():
    url = "https://kr.trip.com/restapi/soa2/34308/getHotelCommentInfo"
    
    headers = {
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "w-payload-source": "1.0.9@102!Nudtz1KLhCAbOX4SO6An9PKnG2KLOSqZOlbn+6FaG6OaKSbpKET2OSVbOrK2+ET5+rApbbbpOSknKr42+rG2KlqIbEVbKtb5+rbSOEb2KE4p+rKpOr4nKrq/K5bpOSqL+rk/OSKZKrVpQlVROShDKFO3GVd3hbb=",
        "x-ctx-country": "KR",
        "x-ctx-currency": "KRW",
        "x-ctx-locale": "ko-KR",
        "x-ctx-ubt-pageid": "10320668147",
        "x-ctx-ubt-pvid": "7",
        "x-ctx-ubt-sid": "9",
        "x-ctx-ubt-vid": "1754985737191.9877n1SlbHlt",
        "x-ctx-user-recognize": "NON_EU",
        "x-ctx-wclient-req": "0af33fe7acb74bcfe9f82cf404544b46",
        "content-type": "application/json"
    }

    payload = {
        "hotelId": 58635410,
        "commentFilterOptions": {
            "pageIndex": 1,
            "pageSize": 10,
            "repeatComment": 1
        },
        "sceneTypes": ["CommentList"],
        "head": {
            "platform": "PC",
            "cver": "0",
            "cid": "1754985737191.9877n1SlbHlt",
            "bu": "IBU",
            "group": "trip",
            "aid": "",
            "sid": "",
            "ouid": "",
            "locale": "ko-KR",
            "timezone": "9",
            "currency": "KRW",
            "pageId": "10320668147",
            "vid": "1754985737191.9877n1SlbHlt",
            "guid": "",
            "isSSR": False
        }
    }

    print("Fetching first page of reviews...")
    fetcher = Fetcher()
    response = fetcher.post(url, json=payload, headers=headers)
    
    print("Status Code:", response.status)
    try:
        data = response.json()
        print("Response Keys:", list(data.keys()))
        if "ResponseStatus" in data:
            print("Response Status Info:", data["ResponseStatus"])
        
        # sample_response.json 파일로 저장하여 구조 파악
        with open("trip_com/src/sample_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Saved response to sample_response.json")
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("Response Text (truncated):", response.text[:1000])

if __name__ == "__main__":
    test_fetch()
