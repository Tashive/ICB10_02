"""
식품안전나라 건강기능식품 기능성 원료인정현황 API(서비스명 I-0040) 호출 및 데이터 저장 스크립트

이 스크립트는 `project2_team3/.env` 파일에서 식품안전나라 API 키(FOODSAFETY_API_KEY_BOMI)를 읽어
건강기능식품 기능성 원료인정현황 API(I-0040)를 호출하고 전체 데이터를 100건씩 나누어 수집합니다.
수집된 데이터는 `project2_team3/0_data/functional_ingredient_db.json` 파일에 저장됩니다.
"""

import os
import sys
import json
import urllib.request
import time

# 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

ENV_PATH = r"c:\Users\tasha\OneDrive\바탕 화면\ICB10_02\project2_team3\.env"
OUTPUT_PATH = r"c:\Users\tasha\OneDrive\바탕 화면\ICB10_02\project2_team3\0_data\functional_ingredient_db.json"

def load_api_key():
    if not os.path.exists(ENV_PATH):
        print(f"Error: {ENV_PATH} 파일이 없습니다.")
        sys.exit(1)
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("FOODSAFETY_API_KEY_BOMI="):
                return line.strip().split("=")[1]
    return None

def fetch_data(api_key, start_idx, end_idx):
    url = f"http://openapi.foodsafetykorea.go.kr/api/{api_key}/I-0040/json/{start_idx}/{end_idx}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    # API 요청 실패 시 재시도 로직 추가 (네트워크 불안정 대비)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data_bytes = response.read()
                raw_text = data_bytes.decode('utf-8')
                data_json = json.loads(raw_text)
                return data_json
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return None

def main():
    api_key = load_api_key()
    if not api_key:
        print("Error: FOODSAFETY_API_KEY_BOMI 키를 찾을 수 없습니다.")
        sys.exit(1)
        
    start_idx = 1
    end_idx = 100
    all_rows = []
    total_count = None
    
    print("API 호출 시작...")
    
    while True:
        print(f"호출 범위: {start_idx} ~ {end_idx}...")
        res = fetch_data(api_key, start_idx, end_idx)
        
        if not res:
            print(f"Error: {start_idx} ~ {end_idx} 데이터를 가져오는데 실패했습니다.")
            break
            
        service_data = res.get("I-0040")
        if not service_data:
            # API 키 오류나 다른 문제의 응답이 있는지 확인
            # 예: {"RESULT": {"MSG": "인증키가 유효하지 않습니다.", "CODE": "INFO-200"}}
            if "RESULT" in res:
                print(f"API Error Response: {res['RESULT'].get('MSG')} ({res['RESULT'].get('CODE')})")
            else:
                print("Error: Unexpected response format", res)
            break
            
        # 총 건수 설정
        if total_count is None:
            total_count_str = service_data.get("total_count")
            if total_count_str:
                total_count = int(total_count_str)
                print(f"전체 데이터 건수: {total_count}건")
            else:
                # total_count가 없으면 결과의 row 개수로만 파악
                total_count = 0
                
        rows = service_data.get("row")
        if not rows:
            print("더 이상 데이터가 없습니다.")
            break
            
        all_rows.extend(rows)
        print(f"현재까지 수집된 건수: {len(all_rows)} / {total_count if total_count else 'Unknown'}")
        
        if total_count and len(all_rows) >= total_count:
            print("전체 데이터를 성공적으로 수집했습니다.")
            break
            
        # 다음 페이지
        start_idx += 100
        end_idx += 100
        # 과도한 요청 방지를 위해 살짝 대기
        time.sleep(0.5)
        
    # 결과 저장
    output_dir = os.path.dirname(OUTPUT_PATH)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=4)
        
    print(f"\n최종 수집 완료: {len(all_rows)} 건")
    print(f"결과 파일 저장 완료: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
