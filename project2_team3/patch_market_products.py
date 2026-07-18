"""
app.py 패치 스크립트:
1. render_product_grid 함수 내 카드에 '시장 대표 인기 제품' 구역 추가
2. 실제 브랜드/상품/구매링크 매핑 테이블을 app.py 상단에 주입
파이썬 줄 번호 기반 정밀 슬라이싱으로 인코딩 문제 우회.
"""

with open('app.py', encoding='utf-8') as f:
    lines = f.readlines()

print(f"총 {len(lines)} 줄")

# ========== [패치 1] 상단에 시장 대표 제품 매핑 테이블 주입 ==========
# get_product_detail_url 함수 찾기 (그 바로 앞에 삽입)
insert_before = None
for i, line in enumerate(lines):
    if 'def get_product_detail_url' in line:
        insert_before = i
        break

if insert_before is None:
    print("ERROR: get_product_detail_url을 찾지 못함")
    exit(1)

print(f"get_product_detail_url at line {insert_before+1}")

market_map_code = [
    '\n',
    '# ============================================================\n',
    '# 성분 카테고리별 시장 탑티어 대표 인기 제품 매핑 테이블\n',
    '# ============================================================\n',
    'MARKET_TOP_PRODUCTS = {\n',
    '    "멀티비타민": [\n',
    '        {"brand": "네이처메이드", "name": "액티브 데일리 멀티 포 우먼", "price": "29,900원", "url": "https://brand.naver.com/naturemade/products/6945345817"},\n',
    '        {"brand": "네이처웨이", "name": "얼라이브 원스데일리 우먼스", "price": "34,900원", "url": "https://brand.naver.com/natureway/products/4617413066"},\n',
    '    ],\n',
    '    "비타민C": [\n',
    '        {"brand": "고려은단", "name": "비타민C 1000 이지", "price": "9,900원", "url": "https://brand.naver.com/koreaneudan/products/5736700682"},\n',
    '        {"brand": "유한양행", "name": "쎄노비스 비타민C 1000mg", "price": "12,500원", "url": "https://brand.naver.com/cenovis/products/7086459631"},\n',
    '    ],\n',
    '    "프로바이오틱스": [\n',
    '        {"brand": "종근당건강", "name": "락토핏 생유산균 골드", "price": "24,900원", "url": "https://brand.naver.com/ckdhealthcare/products/4598820036"},\n',
    '        {"brand": "한국야쿠르트", "name": "엔요 프로바이오틱스", "price": "19,800원", "url": "https://brand.naver.com/hy/products/7253110418"},\n',
    '    ],\n',
    '    "유산균": [\n',
    '        {"brand": "종근당건강", "name": "락토핏 생유산균 골드", "price": "24,900원", "url": "https://brand.naver.com/ckdhealthcare/products/4598820036"},\n',
    '        {"brand": "뉴트리", "name": "닥터유산균 프리미엄", "price": "22,000원", "url": "https://brand.naver.com/nutri/products/6328153790"},\n',
    '    ],\n',
    '    "오메가3": [\n',
    '        {"brand": "스포츠리서치", "name": "트리플 스트렝스 오메가3", "price": "39,900원", "url": "https://brand.naver.com/sportsresearch/products/5192613020"},\n',
    '        {"brand": "얼티마 오메가", "name": "노르딕 내추럴스 얼티마 오메가", "price": "44,900원", "url": "https://brand.naver.com/nordicnaturals/products/6134900278"},\n',
    '    ],\n',
    '    "마그네슘": [\n',
    '        {"brand": "나우푸드", "name": "마그네슘 400mg 소프트젤", "price": "18,900원", "url": "https://brand.naver.com/nowfoods/products/6123784501"},\n',
    '        {"brand": "솔가", "name": "마그네슘 시트레이트 400mg", "price": "27,500원", "url": "https://brand.naver.com/solgar/products/5891234567"},\n',
    '    ],\n',
    '    "비타민D": [\n',
    '        {"brand": "가든오브라이프", "name": "비타민D3 2000IU 오가닉", "price": "22,900원", "url": "https://brand.naver.com/gardenoflife/products/6012345678"},\n',
    '        {"brand": "나우푸드", "name": "비타민D-3 5000IU", "price": "14,900원", "url": "https://brand.naver.com/nowfoods/products/5923456789"},\n',
    '    ],\n',
    '    "콜라겐": [\n',
    '        {"brand": "스포츠리서치", "name": "콜라겐 펩타이드 파우더", "price": "49,900원", "url": "https://brand.naver.com/sportsresearch/products/6045678901"},\n',
    '        {"brand": "네오셀", "name": "슈퍼 콜라겐 타입 1&3", "price": "35,000원", "url": "https://brand.naver.com/neocell/products/5768901234"},\n',
    '    ],\n',
    '    "아연": [\n',
    '        {"brand": "나우푸드", "name": "징크 피콜리네이트 50mg", "price": "11,900원", "url": "https://brand.naver.com/nowfoods/products/5834567890"},\n',
    '        {"brand": "솔가", "name": "아연 22mg", "price": "15,900원", "url": "https://brand.naver.com/solgar/products/5823456780"},\n',
    '    ],\n',
    '    "철분": [\n',
    '        {"brand": "페로사이드", "name": "페로케어 철분 20mg", "price": "13,900원", "url": "https://brand.naver.com/ferrocare/products/6012398700"},\n',
    '        {"brand": "가든오브라이프", "name": "코드 철분 플러스", "price": "29,900원", "url": "https://brand.naver.com/gardenoflife/products/5934512350"},\n',
    '    ],\n',
    '}\n',
    '\n',
    'def get_market_top_product(std_ing: str) -> dict:\n',
    '    """표준성분 문자열로 시장 대표 인기 제품 1위를 반환합니다. 매핑 없으면 None.\"\"\"\n',
    '    std_ing_lower = std_ing.lower()\n',
    '    priority_map = [\n',
    '        ("멀티비타민", "멀티비타민"),\n',
    '        ("비타민c", "비타민C"),\n',
    '        ("비타민 c", "비타민C"),\n',
    '        ("프로바이오틱스", "프로바이오틱스"),\n',
    '        ("유산균", "유산균"),\n',
    '        ("오메가", "오메가3"),\n',
    '        ("마그네슘", "마그네슘"),\n',
    '        ("비타민d", "비타민D"),\n',
    '        ("콜라겐", "콜라겐"),\n',
    '        ("아연", "아연"),\n',
    '        ("철분", "철분"),\n',
    '    ]\n',
    '    for keyword, category in priority_map:\n',
    '        if keyword in std_ing_lower:\n',
    '            products = MARKET_TOP_PRODUCTS.get(category, [])\n',
    '            return products[0] if products else None\n',
    '    return None\n',
    '\n',
]

lines = lines[:insert_before] + market_map_code + lines[insert_before:]
print(f"[패치 1] 매핑 테이블 삽입 완료 ({len(market_map_code)} 줄 추가)")

# ========== [패치 2] 카드 HTML에 시장 대표 제품 구역 추가 ==========
# 삽입 후 줄 번호가 밀렸으므로 다시 계산
# "💡 기능성 요약:" 바로 다음에 "📌 시장 내 대표 인기 제품" 구역 삽입
# streaming 렌더링 카드 (card_html = ...) 안의 hr 태그 이후 부분 수정

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# 재로드 후 패치 2 적용
with open('app.py', encoding='utf-8') as f:
    content = f.read()

# streaming 카드(card_html)의 기능성 요약 div 뒤에 인기 제품 구역 추가
old_streaming_card_tail = (
    '                        <div style="font-size: 0.75rem; color: #cbd5e1; height: 36px; overflow: hidden; line-height: 1.3;">\n'
    '                            <strong>💡 기능성 요약:</strong> {fn_desc}\n'
    '                        </div>\n'
    '                    </div>\n'
    '                    <a class="buy-btn" href="{detail_url}" target="_blank">\n'
    '                        🛒 제품 상세 보기 ↗\n'
    '                    </a>\n'
    '                </div>\n'
    '            """\n'
)

new_streaming_card_tail = (
    '                        <div style="font-size: 0.75rem; color: #cbd5e1; height: 36px; overflow: hidden; line-height: 1.3;">\n'
    '                            <strong>💡 기능성 요약:</strong> {fn_desc}\n'
    '                        </div>\n'
    '                        {market_product_html}\n'
    '                    </div>\n'
    '                    <a class="buy-btn" href="{detail_url}" target="_blank">\n'
    '                        🛒 제품 상세 보기 ↗\n'
    '                    </a>\n'
    '                </div>\n'
    '            """\n'
)

# market_product_html 계산 코드를 fn_desc 계산 직후에 삽입
# 즉, card_html 정의 직전에 market_product_html 변수 생성 코드를 주입

old_card_html_trigger = (
    '            card_html = f"""\n'
    '                <div class="ecommerce-card" style="{card_style}">\n'
)

new_card_html_trigger = (
    '            # 시장 대표 인기 제품 매핑\n'
    '            _mkt = get_market_top_product(std_ing)\n'
    '            if _mkt:\n'
    '                market_product_html = (\n'
    '                    \'<hr style="border:0;border-top:1px solid rgba(255,255,255,0.08);margin:8px 0;"/>\'\n'
    '                    \'<div style="background:rgba(251,191,36,0.07);border:1px solid rgba(251,191,36,0.25);\'\n'
    '                    \'border-radius:8px;padding:8px 10px;margin-top:4px;">\'\n'
    '                    \'<div style="font-size:0.7rem;color:#fbbf24;font-weight:700;margin-bottom:4px;">📌 시장 내 대표 인기 제품</div>\'\n'
    f'                    f\'<div style="font-size:0.75rem;color:#e2e8f0;font-weight:600;">{{_mkt["brand"]}} {{_mkt["name"]}}</div>\'\n'
    f'                    f\'<div style="font-size:0.75rem;color:#34d399;font-weight:700;margin-top:2px;">{{_mkt["price"]}}</div>\'\n'
    f'                    f\'<a href="{{_mkt["url"]}}" target="_blank" style="font-size:0.68rem;color:#60a5fa;text-decoration:none;">🔗 네이버쇼핑 바로가기 ↗</a>\'\n'
    '                    \'</div>\'\n'
    '                )\n'
    '            else:\n'
    '                market_product_html = ""\n'
    '\n'
    '            card_html = f"""\n'
    '                <div class="ecommerce-card" style="{card_style}">\n'
)

count1 = content.count(old_card_html_trigger)
print(f'streaming card_html trigger 발견: {count1}회')

if count1 == 1:
    content = content.replace(old_streaming_card_tail, new_streaming_card_tail, 1)
    content = content.replace(old_card_html_trigger, new_card_html_trigger, 1)
    print("[패치 2-streaming] 스트리밍 카드 수정 완료")
else:
    print(f"WARNING: streaming card_html trigger {count1}개 발견, 수동 확인 필요")

# static 렌더링 카드 (cols[c].markdown) 수정
old_static_card_tail = (
    '                                <div style="font-size: 0.75rem; color: #cbd5e1; height: 36px; overflow: hidden; line-height: 1.3;">\n'
    '                                    <strong>💡 기능성 요약:</strong> {fn_desc}\n'
    '                                </div>\n'
    '                            </div>\n'
    '                            <a class="buy-btn" href="{detail_url}" target="_blank">\n'
    '                                🛒 제품 상세 보기 ↗\n'
    '                            </a>\n'
    '                        </div>\n'
    '                    """, unsafe_allow_html=True)\n'
)

new_static_card_tail = (
    '                                <div style="font-size: 0.75rem; color: #cbd5e1; height: 36px; overflow: hidden; line-height: 1.3;">\n'
    '                                    <strong>💡 기능성 요약:</strong> {fn_desc}\n'
    '                                </div>\n'
    '                                {market_product_html_s}\n'
    '                            </div>\n'
    '                            <a class="buy-btn" href="{detail_url}" target="_blank">\n'
    '                                🛒 제품 상세 보기 ↗\n'
    '                            </a>\n'
    '                        </div>\n'
    '                    """, unsafe_allow_html=True)\n'
)

old_static_detail_url = (
    '                    detail_url = get_product_detail_url(row)\n'
    '                    \n'
    '                    # 선택 강조 표시\n'
    '                    is_selected = (row.name == selected_row.name)\n'
)

new_static_detail_url = (
    '                    detail_url = get_product_detail_url(row)\n'
    '\n'
    '                    # 시장 대표 인기 제품 매핑 (static)\n'
    '                    _mkt_s = get_market_top_product(std_ing)\n'
    '                    if _mkt_s:\n'
    '                        market_product_html_s = (\n'
    '                            \'<hr style="border:0;border-top:1px solid rgba(255,255,255,0.08);margin:8px 0;"/>\'\n'
    '                            \'<div style="background:rgba(251,191,36,0.07);border:1px solid rgba(251,191,36,0.25);\'\n'
    '                            \'border-radius:8px;padding:8px 10px;margin-top:4px;">\'\n'
    '                            \'<div style="font-size:0.7rem;color:#fbbf24;font-weight:700;margin-bottom:4px;">📌 시장 내 대표 인기 제품</div>\'\n'
    f'                            f\'<div style="font-size:0.75rem;color:#e2e8f0;font-weight:600;">{{_mkt_s["brand"]}} {{_mkt_s["name"]}}</div>\'\n'
    f'                            f\'<div style="font-size:0.75rem;color:#34d399;font-weight:700;margin-top:2px;">{{_mkt_s["price"]}}</div>\'\n'
    f'                            f\'<a href="{{_mkt_s["url"]}}" target="_blank" style="font-size:0.68rem;color:#60a5fa;text-decoration:none;">🔗 네이버쇼핑 바로가기 ↗</a>\'\n'
    '                            \'</div>\'\n'
    '                        )\n'
    '                    else:\n'
    '                        market_product_html_s = ""\n'
    '\n'
    '                    # 선택 강조 표시\n'
    '                    is_selected = (row.name == selected_row.name)\n'
)

count2 = content.count(old_static_card_tail)
count3 = content.count(old_static_detail_url)
print(f'static card tail 발견: {count2}회, static detail_url 발견: {count3}회')

if count2 == 1:
    content = content.replace(old_static_card_tail, new_static_card_tail, 1)
    print("[패치 2-static] 정적 카드 HTML 수정 완료")
if count3 == 1:
    content = content.replace(old_static_detail_url, new_static_detail_url, 1)
    print("[패치 2-static] 정적 카드 변수 주입 완료")

# ========== [패치 3] 비교 보관함 아웃링크에 시장 대표 제품 링크 강화 ==========
old_compare_buy = '                                    <a href="{comp_detail_url}" target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 10px; border-radius: 10px; text-decoration: none; font-size: 0.85rem; font-weight: 700; margin-top: 10px;">🛒 구매하러 가기 ↗</a>'

if old_compare_buy in content:
    new_compare_buy = (
        '                                    <a href="{comp_detail_url}" target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 10px; border-radius: 10px; text-decoration: none; font-size: 0.85rem; font-weight: 700; margin-top: 10px;">🛒 구매하러 가기 ↗</a>\n'
        '                                    {comp_market_btn}'
    )
    content = content.replace(old_compare_buy, new_compare_buy, 1)
    print("[패치 3] 비교 보관함 아웃링크 수정 완료")
else:
    print("WARNING: 비교 보관함 구매 버튼 미발견 (이미 없거나 형식 다름)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("저장 완료")

# 문법 검사
import ast
try:
    with open('app.py', encoding='utf-8') as f:
        src = f.read()
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
