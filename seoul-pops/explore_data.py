"""
행정동코드 매핑정보 엑셀과 Parquet 파일을 로드하여
연남동, 성수동에 해당하는 행정동 코드를 추출하고 데이터를 필터링하는 검증 스크립트입니다.
"""
import os
import pandas as pd
import glob

# 1. 행정동 코드 가져오기
data_dir = 'seoul-pops/data'
excel_files = glob.glob(os.path.join(data_dir, '*20241218.xlsx'))
excel_path = excel_files[0]

df_map = pd.read_excel(excel_path, header=1)
df_map['H_DNG_NM'] = df_map['H_DNG_NM'].astype(str)

yeonnam_codes = df_map[df_map['H_DNG_NM'].str.contains('연남')]['H_DNG_CD'].tolist()
seongsu_codes = df_map[df_map['H_DNG_NM'].str.contains('성수')]['H_DNG_CD'].tolist()
target_codes = yeonnam_codes + seongsu_codes

print("Yeonnam codes:", yeonnam_codes)
print("Seongsu codes:", seongsu_codes)

code_to_name = {}
for _, row in df_map.iterrows():
    try:
        cd = int(row['H_DNG_CD'])
        if cd in target_codes:
            code_to_name[cd] = row['H_DNG_NM']
    except:
        pass

print("Code to Name Mapping:", code_to_name)

# 2. Parquet 파일 로드 및 필터링
parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
if not os.path.exists(parquet_path):
    parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized.parquet'

df_pop = pd.read_parquet(parquet_path, engine='pyarrow')

# 실제 컬럼명 한글로 매핑
df_pop.columns = ['기준일ID', '시간대구분', '행정동코드', '성별', '연령대', '생활인구수']

# 행정동코드 타입 일치화 후 필터링
df_pop['행정동코드'] = df_pop['행정동코드'].astype(int)
df_filtered = df_pop[df_pop['행정동코드'].isin(target_codes)].copy()
df_filtered['행정동명'] = df_filtered['행정동코드'].map(code_to_name)

print("Filtered DataFrame Info:")
print(df_filtered.info())
print("\nUnique Dongs in Filtered Data:", df_filtered['행정동명'].unique())
print(df_filtered.head(10))
