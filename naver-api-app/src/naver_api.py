"""
네이버 오픈 API 연동을 위한 클라이언트 라이브러리 모듈입니다.
이 모듈은 네이버 검색어 트렌드, 쇼핑인사이트(카테고리 트렌드), 블로그 검색, 카페글 검색, 뉴스 검색, 쇼핑 검색 API의
호출을 처리하고 결과를 파싱하여 반환하는 기능을 제공합니다.
"""

import requests
import json

def get_headers(client_id, client_secret):
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

def handle_response(response):
    if response.status_code == 200:
        return response.json()
    else:
        try:
            err_json = response.json()
            err_msg = err_json.get("errorMessage", response.text)
            err_code = err_json.get("errorCode", "Unknown")
            raise ValueError(f"API Error ({err_code}): {err_msg}")
        except Exception:
            raise ValueError(f"HTTP Error {response.status_code}: {response.text}")

def fetch_search_trend(client_id, client_secret, keywords, start_date, end_date, time_unit="date", device="", gender="", ages=[]):
    """
    Naver Datalab Search Trend API
    - keywords: list of strings or list of dicts (for grouping)
    """
    url = "https://openapi.naver.com/v1/datalab/search"
    
    # Format keywords. If it's a simple list, we group each keyword individually.
    keyword_groups = []
    if isinstance(keywords, list):
        for kw in keywords:
            if isinstance(kw, dict):
                keyword_groups.append(kw)
            else:
                keyword_groups.append({
                    "groupName": kw,
                    "keywords": [kw]
                })
    else:
         keyword_groups.append({
             "groupName": str(keywords),
             "keywords": [str(keywords)]
         })

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages

    response = requests.post(url, headers=get_headers(client_id, client_secret), data=json.dumps(body))
    return handle_response(response)

def fetch_shopping_insight(client_id, client_secret, category_id, category_name, start_date, end_date, time_unit="date", device="", gender="", ages=[]):
    """
    Naver Datalab Shopping Insight (Category Trend) API
    """
    url = "https://openapi.naver.com/v1/datalab/shopping/categories"
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": [
            {
                "name": category_name,
                "param": [category_id]
            }
        ]
    }
    
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages

    response = requests.post(url, headers=get_headers(client_id, client_secret), data=json.dumps(body))
    return handle_response(response)

def fetch_blog_search(client_id, client_secret, query, display=10, start=1, sort="sim"):
    url = "https://openapi.naver.com/v1/search/blog.json"
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, headers=get_headers(client_id, client_secret), params=params)
    return handle_response(response)

def fetch_cafe_search(client_id, client_secret, query, display=10, start=1, sort="sim"):
    url = "https://openapi.naver.com/v1/search/cafearticle.json"
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, headers=get_headers(client_id, client_secret), params=params)
    return handle_response(response)

def fetch_news_search(client_id, client_secret, query, display=10, start=1, sort="sim"):
    url = "https://openapi.naver.com/v1/search/news.json"
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, headers=get_headers(client_id, client_secret), params=params)
    return handle_response(response)

def fetch_shopping_search(client_id, client_secret, query, display=10, start=1, sort="sim", filter_pay="", exclude_types=""):
    url = "https://openapi.naver.com/v1/search/shop.json"
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    if filter_pay:
        params["filter"] = filter_pay
    if exclude_types:
        params["exclude"] = exclude_types
        
    response = requests.get(url, headers=get_headers(client_id, client_secret), params=params)
    return handle_response(response)
