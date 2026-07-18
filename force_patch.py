import os

if os.path.exists('app.py'):
    with open('app.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 1. 무조건 최상단에 박힐 GNB 및 프리미엄 CSS
    ui_top = '''
import streamlit as st

# [D2C Brand GNB Header]
st.markdown("""
<div style='position: fixed; top: 0; left: 0; width: 100%; background: #ffffff; padding: 15px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e5e7eb; z-index: 9999;'>
    <div style='font-size: 22px; font-weight: bold; color: #10B981;'>🥗 NutriFit</div>
    <div style='display: flex; gap: 30px; font-size: 15px; font-weight: 500; color: #4B5563;'>
        <span>소개</span><span>AI 맞춤 추천</span><span style='color: #EF4444;'>⚠️ 내 영양제 초과 진단</span><span>🔒 백오피스</span>
    </div>
</div>
<div style='margin-top: 80px;'></div>
""", unsafe_allow_html=True)

# [Premium Component Skin]
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

    # 2. 무조건 최하단에 박힐 푸터
    ui_bottom = '''
# [Enterprise Official Footer]
st.markdown("""
<div style='width: 100%; background: #111827; padding: 40px 50px; margin-top: 60px; border-top: 4px solid #10B981; color: #9CA3AF; font-size: 13px;'>
    <p style='margin: 0; text-align: center; line-height: 1.6;'>
        © 2026 NutriFit Inc. All rights reserved. <br>
        본 서비스는 식약처 권장 가이드 및 공공데이터를 준수하며 의학적 진단을 대체하지 않습니다. | 고객지원센터: 1644-2026
    </p>
</div>
""", unsafe_allow_html=True)
'''
    
    # 중복 주입 방지하면서 강제 결합
    if '🥗 NutriFit' not in code:
        code = ui_top + '\n' + code
    if '© 2026 NutriFit Inc.' not in code:
        code = code + '\n' + ui_bottom
        
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print('[OK] app.py 하이엔드 레이아웃 강제 인젝션 완료')

# 깃 강제 푸시 및 캐시 브레이킹용 더미 파일 가동
os.system('git add .')
os.system('git commit -m "fix: 대시보드 UI/UX 레이아웃 레이어 강제 마운트 및 캐시 갱신"')
os.system('git push origin main')
print('[🚀 SUCCESS] 최종 무조건 반영 스펙 배포 완료!')