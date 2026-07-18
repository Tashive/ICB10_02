"""
test_fetch.py

Klook 검색 API를 호출하여 데이터 수집 가능 여부 및 응답 JSON 구조를 테스트하는 스크립트입니다.
작성자: Antigravity
작성일: 2026-06-24
"""

import json
from scrapling import Fetcher

def test_fetch():
    url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ko_KR",
        "x-platform": "desktop",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "cookie": "_cfuvid=fja5dP87aG5yCEK99qcoVWbQHK8FDHxGQP0mtPdVXB0-1782301580.363879-1.0.1.1-_a8QOMy_peRGV48pE6zeaElgIKvJ80FndALr8d.dwyc; kepler_id=f06f995a-86ee-4d88-b6e6-a646d44ecd44; klk_currency=KRW; klk_rdc=KR; klk_ps=1; _fwb=113kHs6JoZ2bnnRdprVA4ZO.1782301582742; _cq_duid=1.1782301583.ds96YjUoD0ks60qB; _cq_suid=1.1782301583.v3W9DmgBy0CcpE7o; _gcl_au=1.1.1689593517.1782301583; dable_uid=13770955.1782301583590; _twpid=tw.1782301583302.882812328840822403; _yjsu_yjad=1782301583.0b7acdad-639d-4353-bfc3-76d5f8c6dc23; _tguatd=eyJzYyI6IihkaXJlY3QpIiwiZnRzIjoiKGRpcmVjdCkifQ==; _tgpc=e171b6dc-9091-471d-9a94-e1d775e01af3; _tgidts=eyJzaCI6ImQ0MWQ4Y2Q5OGYwMGIyMDRlOTgwMDk5OGVjZjg0MjdlIiwiY2kiOiI1M2RlOTMzMi1mOWZmLTQ3NmMtOGNmNC03NzkxZDUwN2FlYzMiLCJzaSI6IjY4MTFhZTYxLWEyY2EtNDE3My1iODhlLThiNjc1MzIzM2UxYiJ9; __lt__cid=a963f75c-5137-4367-bd48-39a31fb3cab8; __lt__cid.c83939be=a963f75c-5137-4367-bd48-39a31fb3cab8; __lt__sid=16633b19-0f938787; __lt__sid.c83939be=16633b19-0f938787; klk_sessionid=MQ.2634ff99ab4c4bc176d315514734d031; _tt_enable_cookie=1; _ttp=01KVWQ7T1TH0FKJCDSQY75AFPX_.tt.1; _ga=GA1.1.506805387.1782301584; JSESSIONID=0B2827610B5A02EB825427BDAB3C8A71; KOUNT_SESSION_ID=0B2827610B5A02EB825427BDAB3C8A71; clientside-cookie=cc7bb24adf3200dc18b834ebe99c7b27c6c141a1f85e3bf02b71d3fbcc200783652169a83df5c04d198eadd7b54b66caab7cfe1f921fd8ac46040a073574fbca4774f9a204493ece809cfe1e0c912f379eb16bbdaadf3f08b8c0c68a95a5416df1141ffeea6db70bbe13b540b253b49182b6791abce69f2a1ace71034da00ceb81386afc892284cbb7c861d99323d15bf8dbcc62cb5351c0d31c26; forterToken=868e1673e0f742968ec92f9b6387b338_1782301584171__UDF43-m4_21ck_; klk_i_sn=9794830693..1782301973850; klk_ga_sn=5946836999..1782301973853; wcs_bt=s_2cb388a4aa34:1782301974; _cq_session=1.1782301583043.TRqAkdLikbcHAnzS.1782301974745; _tglksd=eyJzIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiIiwic3QiOjE3ODIzMDE1ODMzMTcsInNvZCI6IihkaXJlY3QpIiwic29kdCI6MTc4MjMwMTU4MzMxNywic29kcyI6ImMiLCJzb2RzdCI6MTc4MjMwMTk3NDc5OH0=; _uetsid=531bb1d06fc211f1ab9effddb3553dac; _uetvid=531bcb206fc211f1afcd8dc9c9cb3510; _cq_s=DiID57CMsh640vCy:7aEaYB8Lvr+TjdqdGO2E+uDcn1a6kHbwKLH55aTaqZSXGaIroN4EWrl3TPK2/xX0xMvu5kwCsGR/X+YoT0b9ahFmMiR+OqJ2CF8Dc6wmmNk4GnTcNoPUC5gMZPsVFtcaO4BE4sI7N59PJW0v28dXanYcPB+nAmIRtbtoFYfCO6lRfnF0QRlDt6jVipceyBDfU/LVzN8o2vZWWn45kw==:IafL0pvqMF/X3kGcjWCS2A==; _tgsid=eyJscGQiOiJ7XCJscHVcIjpcImh0dHBzOi8vd3d3Lmtsb29rLmNvbSUyRmtvJTJGc2VhcmNoJTJGcmVzdWx0JTJGXCIsXCJscHRcIjpcIktsb29rJTIwVHJhdmVsXCIsXCJscHJcIjpcIlwifSIsInBzIjoiOGUwNzhlYTAtZDQyMS00ZTc1LWJiYzItYzAyYjYzMTJkZWE3IiwicHZjIjoiMiIsInNjIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiOi0xIiwiZWMiOiI0IiwicHYiOiIxIiwidGltIjoiNjgxMWFlNjEtYTJjYS00MTczLWI4OGUtOGI2NzUzMjMzZTFiOjE3ODIzMDE1ODY2ODU6LTEifQ==; _ga_HSY7KJ18X2=GS2.1.s1782301583$o1$g1$t1782301974$j59$l0$h0; _ga_FW3CMDM313=GS2.1.s1782301583$o1$g1$t1782301974$j6$l0$h0; _ga_V8S4KC8ZXR=GS2.1.s1782301583$o1$g1$t1782301975$j5$l0$h519304495; datadome=c7c0zBzlRr65X1EcGbV7U~PVY7dD4fFI7I~9xJlHKLnIhRAjMDV495WtMZ0PQmUyKWP5IqXMmZnPlwCGC~YpFSiuwj~7d2~6w2dB74byzFl6uETD7jnAeYK1db_0UxlB; ttcsid=1782301583422::3pgCndZv_JWfXAoKzC1C.1.1782301975389.0::1.390006.391674::335283.6.579.253::337455.28.0; ttcsid_C1SIFQUHLSU5AAHCT7H0=1782301583421::FjAXqkX7p9LIZXoVITU-.1.1782301975389.1; klk_gl_sess=08379a7c895a..1782301583906..1782301975499"
    }

    params_1 = {
        "query": "대한민국",
        "search_scope": "main_search",
        "sort": "most_relevant",
        "tab_key": "0",
        "start": "1",
        "spm": "SearchResult.SearchResultTab_LIST",
        "clickId": "1cd71660fb",
        "dd_referrer": "",
        "size": "15",
        "k_lang": "ko_KR",
        "k_currency": "KRW"
    }

    fetcher = Fetcher()

    # 1. start=1 호출
    response1 = fetcher.get(url, params=params_1, headers=headers)
    cards1 = response1.json().get("result", {}).get("search_result", {}).get("cards", [])
    titles1 = [c.get("data", {}).get("title") for c in cards1]

    # 2. start=2 호출
    params_2 = params_1.copy()
    params_2["start"] = "2"
    response2 = fetcher.get(url, params=params_2, headers=headers)
    cards2 = response2.json().get("result", {}).get("search_result", {}).get("cards", [])
    titles2 = [c.get("data", {}).get("title") for c in cards2]

    # 3. start=16 호출
    params_16 = params_1.copy()
    params_16["start"] = "16"
    response16 = fetcher.get(url, params=params_16, headers=headers)
    cards16 = response16.json().get("result", {}).get("search_result", {}).get("cards", [])
    titles16 = [c.get("data", {}).get("title") for c in cards16]

    print("--- Titles (start=1) ---")
    for idx, t in enumerate(titles1, 1):
        print(f"{idx}: {t}")

    print("\n--- Titles (start=2) ---")
    for idx, t in enumerate(titles2, 1):
        print(f"{idx}: {t}")

    print("\n--- Titles (start=16) ---")
    for idx, t in enumerate(titles16, 1):
        print(f"{idx}: {t}")

if __name__ == "__main__":
    test_fetch()
