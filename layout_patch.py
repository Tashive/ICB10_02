import os

if os.path.exists('app.py'):
    with open('app.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 1. 최상단 브랜드 GNB 헤더 주입 정의
    gnb_html = '''
    st.markdown("""
    <div style='position: fixed; top: 0; left: 0; width: 100%; background: #ffffff; padding: 15px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e5e7eb; z-index: 9999;'>
        <div style='font-size: 22px; font-weight: bold; color: #10B981;'>🥗 NutriFit</div>
        <div style='display: flex; gap: 30px; font-size: 15px; font-weight: 500; color: #4B5563;'>
            <span>소개</span><span>AI 맞춤 추천</span><span style='color: #EF4444;'>⚠️ 내 영양제 초과 진단</span><span>🔒 백오피스</span>
        </div>
    </div>
    <div style='margin-top: 80px;'></div>
    """, unsafe_allow_html=True)
    '''
    
    # 2. 전면 프리미엄 CSS 테이밍 디자인 스킨 선언
    premium_css = '''
    st.markdown("""
    <style>
    .stButton>button {
        border-radius: 20px !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.1) !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    '''
    
    # 3. 하단 엔터프라이즈 공식 푸터 아키텍처 정의
    footer_html = '''
    st.markdown("""
    <div style='width: 100%; background: #111827; padding: 40px 50px; margin-top: 60px; border-top: 4px solid #10B981; color: #9CA3AF; font-size: 13px;'>
        <p style='margin: 0; text-align: center; line-height: 1.6;'>
            © 2026 NutriFit Inc. All rights reserved. <br>
            본 서비스는 식약처 권장 가이드 및 공공데이터를 준수하며 의학적 진단을 대체하지 않습니다. | 고객지원센터: 1644-2026
        </p>
    </div>
    """, unsafe_allow_html=True)
    '''

    # 코드 상단에 GNB와 CSS 인젝션 배치
    if '🥗 NutriFit' not in code:
        lines = code.split('\n')
        # import 구문 아래 또는 설정 아래 적절히 주입
        insert_idx = 0
        for i, line in enumerate(lines):
            if 'set_page_config' in line:
                insert_idx = i + 1
                break
        
        lines.insert(insert_idx, premium_css)
        lines.insert(insert_idx, gnb_html)
        code = '\n'.join(lines)

    # 4. 레이아웃 구조 개편 (비대칭 st.columns 할당 자동화)
    if 'st.columns' in code and '2.3' not in code:
        code = code.replace('st.columns(2)', 'st.columns([2.3, 1.0])')
        code = code.replace('st.columns([2, 1])', 'st.columns([2.3, 1.0])')
        
    # 최하단 푸터 결합
    if '© 2026 NutriFit Inc.' not in code:
        code += '\n' + footer_html

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print('[OK] app.py 대형 브랜드사급 GNB, 푸터, 2.3:1 레이아웃 구조 다이렉트 개편 완료')

# 깃허브 원격 동기화
os.system('git add .')
os.system('git commit -m "design: 대형 웰니스 브랜드사급 하이엔드 UI/UX 레이아웃 개편 및 디자인 스킨 적용"')
os.system('git push origin main')
print('[🚀 SUCCESS] 하이엔드 D2C 플랫폼 리팩토링 스펙 최종 배포 완료!')