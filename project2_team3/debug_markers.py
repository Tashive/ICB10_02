"""
app.py 마커 탐색 디버그 스크립트.
"""
with open('app.py', encoding='utf-8') as f:
    content = f.read()

START_MARKER = '            with landing_col2:'
idx_start = content.find(START_MARKER)
print(f'START at: {idx_start}')
if idx_start >= 0:
    snippet = content[idx_start:idx_start+3000]
    print(repr(snippet[:500]))
    print('---')
    # 끝 마커 후보 탐색
    for marker in ['st.markdown("---")', "st.markdown('---')", 'st.markdown("""---')", 'st.markdown(\"---\")', '\n            st.markdown']:
        idx = content.find(marker, idx_start)
        print(f'  [{marker[:30]}] at {idx}')
