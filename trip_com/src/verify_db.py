"""
verify_db.py

수집된 리뷰 데이터가 SQLite DB에 정상적으로 저장되었는지 레코드를 조회하여 검증하는 스크립트입니다.
작성일: 2026-06-22
"""

import sys
import sqlite3

# 콘솔 인코딩 에러 방지
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = "trip_com/data/reviews.db"

def verify():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 전체 개수 확인
    c.execute("SELECT COUNT(*) FROM reviews")
    total = c.fetchone()[0]
    print(f"Total reviews in DB: {total}")
    
    # 3개 레코드 샘플 확인
    c.execute("SELECT id, username, rating, comment_level, room_name, SUBSTR(raw_content, 1, 40) FROM reviews LIMIT 3")
    rows = c.fetchall()
    
    print("\n--- SAMPLE RECORDS ---")
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"User: {row[1]}")
        print(f"Rating: {row[2]} ({row[3]})")
        print(f"Room: {row[4]}")
        print(f"Content Sample: {row[5]}...")
        print("-" * 30)
        
    conn.close()

if __name__ == "__main__":
    verify()
