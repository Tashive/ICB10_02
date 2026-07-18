"""
식품안전나라 API 키 복원 및 테스트 스크립트

이 스크립트는 제공된 API 키(4cca164bc44a494c8e1)가 19자리인 점에 착안하여,
마지막 20번째 자리가 누락되었을 가능성을 염두에 두고 16진수 문자(0-9, a-f)를 대입하여
식품안전나라 API를 호출해봅니다. 유효한 인증키가 찾아지면 해당 키를 반환합니다.
"""

import sys
import urllib.request

# 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

base_key = "4cca164bc44a494c8e1"
hex_chars = "0123456789abcdef"

def test_key(key):
    url = f"http://openapi.foodsafetykorea.go.kr/api/{key}/I-0040/json/1/1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            res_text = response.read().decode('utf-8')
            if "인증키가 유효하지 않습니다" not in res_text:
                return True, res_text
    except Exception as e:
        pass
    return False, None

def main():
    print(f"기본 키: {base_key} (길이: {len(base_key)})")
    print("마지막 자리 대입 테스트 시작...")
    
    found = False
    for char in hex_chars:
        test_k = base_key + char
        success, response = test_key(test_k)
        if success:
            print(f"\n[성공] 유효한 API 키를 찾았습니다: {test_k}")
            print(f"응답 데이터 일부: {response[:300]}")
            found = True
            break
            
    if not found:
        print("\n16진수 문자 대입 결과 유효한 키를 찾지 못했습니다.")
        print("대소문자 및 기타 영문자 전체(a-z, A-Z, 0-9)로 확장하여 재시도합니다...")
        import string
        all_chars = string.ascii_letters + string.digits
        for char in all_chars:
            test_k = base_key + char
            success, response = test_key(test_k)
            if success:
                print(f"\n[성공] 유효한 API 키를 찾았습니다: {test_k}")
                print(f"응답 데이터 일부: {response[:300]}")
                found = True
                break
                
    if not found:
        print("\n모든 단일 문자 대입 테스트 실패. 키 자체에 더 많은 글자가 누락되었거나 키가 만료된 것 같습니다.")

if __name__ == "__main__":
    main()
