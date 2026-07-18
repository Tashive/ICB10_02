"""
inspect_scrapling.py

scrapling Response 객체의 json 속성 혹은 메서드 타입과 데이터를 호출하는 방법을 알아보기 위한 스크립트입니다.
작성일: 2026-06-22
"""

from scrapling import Fetcher

fetcher = Fetcher()
response = fetcher.get("https://httpbin.org/get")
print("Response status:", response.status)
print("Response json type:", type(response.json))

# 만약 response.json이 callable이면 호출하고, 아니면 그냥 출력
if callable(response.json):
    print("response.json() output:", response.json())
else:
    print("response.json output:", response.json)
