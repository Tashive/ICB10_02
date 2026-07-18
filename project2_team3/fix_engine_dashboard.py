"""
app.py landing_col2 블록(538~596행)을 엔진 상태 대시보드로 교체하는 스크립트.
줄 번호 기반으로 직접 슬라이싱하여 인코딩 문제를 우회합니다.
"""

with open('app.py', encoding='utf-8') as f:
    lines = f.readlines()

print(f"총 {len(lines)} 줄")
print(f"538: {repr(lines[537][:80])}")
print(f"596: {repr(lines[595][:80])}")

# 538행 ~ 596행을 새 블록으로 교체 (0-indexed: 537~595)
new_lines = [
    '            with landing_col2:\n',
    '                # 우측: 3대 핵심 엔진 가동 상태 대시보드 (개인 데이터 완전 제거)\n',
    '                engine_status_html = (\n',
    '                    \'<div style="background: rgba(15, 23, 42, 0.6); border: 2px solid rgba(59, 130, 246, 0.3);\'\n',
    '                    \' border-radius: 20px; padding: 24px; box-shadow: 0 15px 40px rgba(0,0,0,0.5);\'\n',
    '                    \' min-height: 480px; backdrop-filter: blur(12px);">\'\n',
    '\n',
    '                    \'<div style="margin-bottom: 8px;">\'\n',
    '                    \'<span style="font-size: 1rem; color: #f1f5f9; font-weight: 800; font-family: Outfit, sans-serif;">\'\n',
    '                    \'&#128187; NutriFit Core Engine Status</span></div>\'\n',
    '\n',
    '                    \'<div style="display: flex; align-items: center; gap: 7px; margin-bottom: 22px;\'\n',
    '                    \' padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.07);">\'\n',
    '                    \'<span style="display:inline-block; width:8px; height:8px; background:#10b981;\'\n',
    '                    \' border-radius:50%; box-shadow:0 0 6px #10b981;"></span>\'\n',
    '                    \'<span style="font-size:0.78rem; color:#34d399; font-weight:700;">\'\n',
    '                    \'&#9679; Core Kernel Active &#129001;</span></div>\'\n',
    '\n',
    '                    \'<div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2);\'\n',
    '                    \' border-radius:12px; padding:16px; margin-bottom:14px;">\'\n',
    '                    \'<div style="display:flex; align-items:flex-start; gap:12px;">\'\n',
    '                    \'<span style="font-size:1.5rem; line-height:1;">&#128737;&#65039;</span>\'\n',
    '                    \'<div style="flex:1;">\'\n',
    '                    \'<div style="font-size:0.82rem; font-weight:700; color:#e2e8f0; margin-bottom:5px;">\'\n',
    '                    \'알레르기 및 부작용 Hard Filter Engine</div>\'\n',
    '                    \'<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:8px;">\'\n',
    '                    \'23개 변수 스캐닝 준비 완료</div>\'\n',
    '                    \'<div style="display:flex; align-items:center; gap:6px;">\'\n',
    '                    \'<span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%;"></span>\'\n',
    '                    \'<span style="font-size:0.72rem; color:#34d399; font-weight:600;">\'\n',
    '                    \'READY &mdash; 확산 필터 가동 대기 중 &#129001;</span>\'\n',
    '                    \'</div></div></div></div>\'\n',
    '\n',
    '                    \'<div style="background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.2);\'\n',
    '                    \' border-radius:12px; padding:16px; margin-bottom:14px;">\'\n',
    '                    \'<div style="display:flex; align-items:flex-start; gap:12px;">\'\n',
    '                    \'<span style="font-size:1.5rem; line-height:1;">&#128138;</span>\'\n',
    '                    \'<div style="flex:1;">\'\n',
    '                    \'<div style="font-size:0.82rem; font-weight:700; color:#e2e8f0; margin-bottom:5px;">\'\n',
    '                    \'영양소 오버도즈 디옵티마이저</div>\'\n',
    '                    \'<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:8px;">\'\n',
    '                    \'식약처 상한 섭취량 실시간 동기화 완료</div>\'\n',
    '                    \'<div style="display:flex; align-items:center; gap:6px;">\'\n',
    '                    \'<span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%;"></span>\'\n',
    '                    \'<span style="font-size:0.72rem; color:#34d399; font-weight:600;">\'\n',
    '                    \'SYNCED &mdash; 식약처 DB 연동 정상 &#129001;</span>\'\n',
    '                    \'</div></div></div></div>\'\n',
    '\n',
    '                    \'<div style="background:rgba(167,139,250,0.06); border:1px solid rgba(167,139,250,0.2);\'\n',
    '                    \' border-radius:12px; padding:16px;">\'\n',
    '                    \'<div style="display:flex; align-items:flex-start; gap:12px;">\'\n',
    '                    \'<span style="font-size:1.5rem; line-height:1;">&#129302;</span>\'\n',
    '                    \'<div style="flex:1;">\'\n',
    '                    \'<div style="font-size:0.82rem; font-weight:700; color:#e2e8f0; margin-bottom:5px;">\'\n',
    '                    \'Scikit-Learn ML 가중치 연산 커널</div>\'\n',
    '                    \'<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:8px;">\'\n',
    '                    \'독립변수 다차원 추론 대기 중</div>\'\n',
    '                    \'<div style="display:flex; align-items:center; gap:6px;">\'\n',
    '                    \'<span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%;"></span>\'\n',
    '                    \'<span style="font-size:0.72rem; color:#34d399; font-weight:600;">\'\n',
    '                    \'STANDBY &mdash; ML 테크놀로지 실시간 가동 중 &#129001;</span>\'\n',
    '                    \'</div></div></div></div>\'\n',
    '\n',
    '                    \'</div>\'\n',
    '                )\n',
    '                st.markdown(engine_status_html, unsafe_allow_html=True)\n',
    '\n',
]

result = lines[:537] + new_lines + lines[596:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(result)

print(f"완료: {len(result)} 줄로 저장")
# 검증
with open('app.py', encoding='utf-8') as f:
    verify = f.readlines()
print(f"검증 줄수: {len(verify)}")
print(f"538: {repr(verify[537][:80])}")
