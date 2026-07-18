"""
서울시 생활인구 데이터에서 회현동의 데이터만 추출하여
ydata-profiling을 사용한 상세 데이터 프로파일링 리포트(HTML)를 생성하고,
이를 기본 웹 브라우저로 열어주는 스크립트입니다.
"""
# 0. pkg_resources 런타임 패치
import sys
import subprocess
import importlib

try:
    import pkg_resources
except ImportError:
    print("pkg_resources not found. Installing setuptools<70 dynamically...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools<70"])
        importlib.invalidate_caches()
        import pkg_resources
        print("Successfully installed setuptools<70.")
    except Exception as e:
        print(f"Failed to install setuptools dynamically: {e}")

import os
import pandas as pd
import glob
import webbrowser
from ydata_profiling import ProfileReport

# 1. 행정동 코드 가져오기
data_dir = 'seoul-pops/data'
excel_files = glob.glob(os.path.join(data_dir, '*20241218.xlsx'))
if not excel_files:
    raise FileNotFoundError("행정동코드 매핑 엑셀 파일을 찾을 수 없습니다.")
excel_path = excel_files[0]

df_map = pd.read_excel(excel_path, header=1)
df_map['H_DNG_NM'] = df_map['H_DNG_NM'].astype(str)

# 회현동 행정동코드 추출
hoehyun_codes = df_map[df_map['H_DNG_NM'].str.contains('회현')]['H_DNG_CD'].tolist()
print(f"Hoehyun Dong Codes: {hoehyun_codes}")

# 2. Parquet 파일 로드 및 필터링
parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
if not os.path.exists(parquet_path):
    parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized.parquet'

print(f"Reading dataset: {parquet_path}")
df_pop = pd.read_parquet(parquet_path, engine='pyarrow')
df_pop.columns = ['기준일ID', '시간대구분', '행정동코드', '성별', '연령대', '생활인구수']

# 필터링
df_pop['행정동코드'] = df_pop['행정동코드'].astype(int)
df_hoehyun = df_pop[df_pop['행정동코드'].isin(hoehyun_codes)].copy()

# 데이터 타입 설정
df_hoehyun['기준일ID'] = df_hoehyun['기준일ID'].astype('category')
df_hoehyun['행정동코드'] = df_hoehyun['행정동코드'].astype('category')
df_hoehyun['성별'] = df_hoehyun['성별'].astype('category')
df_hoehyun['연령대'] = df_hoehyun['연령대'].astype('category')
df_hoehyun['시간대구분'] = df_hoehyun['시간대구분'].astype('int8')
df_hoehyun['생활인구수'] = df_hoehyun['생활인구수'].astype('float32')

print(f"Hoehyun data shape: {df_hoehyun.shape}")

# 3. 프로파일링 리포트 생성 (데이터가 작으므로 minimal=False로 상세 분석)
print("Generating Profile Report for Hoehyun-dong...")
profile = ProfileReport(
    df_hoehyun,
    title="서울시 회현동 생활인구 데이터 프로파일링 리포트",
    explorative=True,
    minimal=False
)

output_html = 'seoul-pops/report/hoehyun_EDA_Report.html'
os.makedirs(os.path.dirname(output_html), exist_ok=True)

profile.to_file(output_html)
print(f"Hoehyun profiling report saved to: {output_html}")

# 4. 브라우저로 리포트 열기
abs_html_path = os.path.abspath(output_html)
print(f"Opening report in browser: {abs_html_path}")
webbrowser.open('file://' + abs_html_path)
