"""
scraper.py

trip.com 호텔 리뷰 API를 호출하여 리뷰 데이터를 수집하고, SQLite 데이터베이스에 저장하는 스크립트입니다.
첫 페이지 데이터 수집 검증 후 전체 리뷰 데이터를 루프 돌며 저장합니다.
작성일: 2026-06-22
"""

import os
import sys
import time
import json
import sqlite3
from scrapling import Fetcher

# 윈도우 콘솔 인코딩 에러 방지 (일본어 등 특수문자 출력 대비)
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = "trip_com/data/reviews.db"
HOTEL_ID = 58635410

# API 요청 정보 설정
URL = "https://kr.trip.com/restapi/soa2/34308/getHotelCommentInfo"

HEADERS = {
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

def create_payload(page_index):
    return {
        "hotelId": HOTEL_ID,
        "commentFilterOptions": {
            "pageIndex": page_index,
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

def init_db():
    """SQLite 데이터베이스 및 테이블을 생성하고 연결을 반환합니다."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            username TEXT,
            rating INTEGER,
            comment_level TEXT,
            room_name TEXT,
            raw_content TEXT,
            translated_content TEXT,
            create_date TEXT,
            checkin_date TEXT
        )
    """)
    conn.commit()
    return conn

def parse_comments(data):
    """API 응답 데이터에서 리뷰 목록을 파싱합니다."""
    comments = []
    try:
        group_list = data.get("data", {}).get("groupList", [])
        for group in group_list:
            if group.get("dataType") == 7: # dataType이 7인 항목에 리뷰 목록이 있음
                comment_list = group.get("commentList", [])
                for item in comment_list:
                    # 필요한 필드 추출
                    review_id = item.get("id")
                    username = item.get("userInfo", {}).get("nickName")
                    rating = item.get("rating")
                    comment_level = item.get("ratingInfo", {}).get("commentLevel")
                    room_name = item.get("roomName")
                    raw_content = item.get("content")
                    translated_content = item.get("translatedContent")
                    create_date = item.get("createDate")
                    checkin_date = item.get("checkinDate")
                    
                    comments.append({
                        "id": review_id,
                        "username": username,
                        "rating": rating,
                        "comment_level": comment_level,
                        "room_name": room_name,
                        "raw_content": raw_content,
                        "translated_content": translated_content,
                        "create_date": create_date,
                        "checkin_date": checkin_date
                    })
    except Exception as e:
        print(f"Error parsing comments: {e}")
    return comments

def save_comments_to_db(conn, comments):
    """리뷰 리스트를 SQLite DB에 저장합니다."""
    cursor = conn.cursor()
    saved_count = 0
    for comment in comments:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO reviews (
                    id, username, rating, comment_level, room_name, 
                    raw_content, translated_content, create_date, checkin_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comment["id"],
                comment["username"],
                comment["rating"],
                comment["comment_level"],
                comment["room_name"],
                comment["raw_content"],
                comment["translated_content"],
                comment["create_date"],
                comment["checkin_date"]
            ))
            saved_count += 1
        except Exception as e:
            print(f"Error inserting review {comment['id']}: {e}")
    conn.commit()
    return saved_count

def fetch_page(fetcher, page_index):
    """특정 페이지의 리뷰 데이터를 가져옵니다."""
    payload = create_payload(page_index)
    response = fetcher.post(URL, json=payload, headers=HEADERS)
    if response.status == 200:
        return response.json()
    else:
        print(f"Failed to fetch page {page_index}. Status: {response.status}")
        return None

def main():
    fetcher = Fetcher()
    conn = init_db()
    
    print("=== [1단계] 첫 페이지 수집 및 검증 ===")
    first_page_data = fetch_page(fetcher, 1)
    if not first_page_data:
        print("첫 페이지 요청 실패로 작업을 중단합니다.")
        conn.close()
        return

    comments = parse_comments(first_page_data)
    if not comments:
        print("첫 페이지에서 수집된 리뷰가 없습니다. 파싱 방식을 확인해 주세요.")
        conn.close()
        return

    # 첫 페이지 정상 수집 여부 검증 (내용, 별점 등 확인)
    print(f"첫 페이지에서 {len(comments)}개의 리뷰를 파싱했습니다.")
    first_comment = comments[0]
    print("\n[첫 번째 리뷰 샘플 검증]")
    print(f"ID: {first_comment['id']}")
    print(f"작성자: {first_comment['username']}")
    print(f"별점: {first_comment['rating']}")
    print(f"평가요약: {first_comment['comment_level']}")
    print(f"객실타입: {first_comment['room_name']}")
    
    # 윈도우 인코딩 안전 출력
    try:
        raw_text_print = first_comment['raw_content'][:100] if first_comment['raw_content'] else '없음'
        print(f"내용(일부): {raw_text_print}")
    except Exception:
        print("내용(일부): [출력 인코딩 오류로 본문 생략]")

    try:
        trans_text_print = first_comment['translated_content'][:100] if first_comment['translated_content'] else '없음'
        print(f"번역내용(일부): {trans_text_print}")
    except Exception:
        print("번역내용(일부): [출력 인코딩 오류로 본문 생략]")
    
    # 필수적인 데이터(내용, 별점 등)가 정상적으로 존재하는지 체크
    if first_comment['raw_content'] and first_comment['rating'] is not None:
        print("\n-> 첫 페이지 데이터 검증 완료 (성공)!")
    else:
        print("\n-> 첫 페이지 데이터 검증 실패 (내용 또는 별점 없음). 작업을 중단합니다.")
        conn.close()
        return

    # 첫 페이지 데이터를 먼저 저장
    saved = save_comments_to_db(conn, comments)
    print(f"첫 페이지 {saved}개 리뷰 DB 저장 완료.")

    # 전체 페이지 정보 획득
    total_count = first_page_data.get("data", {}).get("totalCountForPage", 0)
    print(f"\n=== [2단계] 전체 리뷰 수집 시작 (총 {total_count}개 리뷰 예상) ===")
    
    # 1페이지당 10개이므로 전체 페이지 수 계산
    page_size = 10
    total_pages = (total_count + page_size - 1) // page_size
    print(f"총 {total_pages} 페이지를 수집해야 합니다.")

    all_saved_count = saved
    
    # 2페이지부터 루프 시작 (1페이지는 이미 완료)
    for page in range(2, total_pages + 1):
        print(f"페이지 {page}/{total_pages} 수집 중...")
        page_data = fetch_page(fetcher, page)
        if not page_data:
            print(f"페이지 {page} 가져오기 실패. 다음 페이지로 넘어갑니다.")
            continue
        
        page_comments = parse_comments(page_data)
        if page_comments:
            saved_count = save_comments_to_db(conn, page_comments)
            all_saved_count += saved_count
            print(f"페이지 {page} 저장 성공 ({saved_count}개 저장 완료, 누적: {all_saved_count}개)")
        
        # IP 차단 및 부하 방지를 위해 딜레이 추가
        time.sleep(1.2)

    print(f"\n=== 수집 완료 ===")
    print(f"DB 저장 완료: 총 {all_saved_count}개 리뷰가 '{DB_PATH}'에 저장되었습니다.")
    
    # SQLite에 실제로 저장된 건수 최종 확인
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reviews")
    db_count = cursor.fetchone()[0]
    print(f"SQLite DB 내 최종 데이터 건수: {db_count}개")
    
    conn.close()

if __name__ == "__main__":
    main()
