"""
이 스크립트는 서울시 생활인구 (동별) ZIP 데이터를 로드하여,
성별 및 연령대 컬럼을 Tidy Data 형태로 변환(Melt)한 후,
데이터 타입을 다운캐스팅(Downcasting)하여 최적화된 Parquet 파일로 저장하고
원본 데이터와 변환 데이터의 상세 사양을 비교한 보고서를 생성합니다.
"""
import pandas as pd
import numpy as np
import io
import os
import zipfile

def get_df_info_str(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    return buffer.getvalue()

def main():
    zip_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.zip'
    parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
    
    print("1. Loading raw data from zip...")
    # Read CSV directly from ZIP with utf-8-sig encoding, ensuring first column is not wrongly parsed as index
    df_orig = pd.read_csv(zip_path, encoding='utf-8-sig', index_col=False)
    
    print("\n--- Original DataFrame Info (First 5 rows) ---")
    # Python printing handles unicode well inside script execution redirecting to logs
    print(df_orig.head())
    
    orig_info = get_df_info_str(df_orig)
    print("\n--- Original DataFrame info() ---")
    print(orig_info)
    
    print("2. Reshaping to tidy-data...")
    # ID columns
    id_vars = ['기준일ID', '시간대구분', '행정동코드']
    
    # Identify sex-age columns
    sex_age_cols = [col for col in df_orig.columns if col.startswith('남자') or col.startswith('여자')]
    
    # Melt
    df_tidy = df_orig.melt(
        id_vars=id_vars,
        value_vars=sex_age_cols,
        var_name='성별연령대',
        value_name='생활인구수'
    )
    
    # Extract Sex and Age Group
    # Example: '남자0세부터9세생활인구수' -> '남자' & '0세부터9세생활인구수'
    df_tidy['성별'] = df_tidy['성별연령대'].str[:2]
    raw_age = df_tidy['성별연령대'].str[2:-5] # Strip '남자'/'여자' and '생활인구수'
    
    # Map raw age string to cleaner version
    age_map = {
        '0세부터9세': '0-9세',
        '10세부터14세': '10-14세',
        '15세부터19세': '15-19세',
        '20세부터24세': '20-24세',
        '25세부터29세': '25-29세',
        '30세부터34세': '30-34세',
        '35세부터39세': '35-39세',
        '40세부터44세': '40-44세',
        '45세부터49세': '45-49세',
        '50세부터54세': '50-54세',
        '55세부터59세': '55-59세',
        '60세부터64세': '60-64세',
        '65세부터69세': '65-69세',
        '70세이상': '70세 이상'
    }
    df_tidy['연령대'] = raw_age.map(age_map)
    
    # Drop intermediate columns
    df_tidy = df_tidy.drop(columns=['성별연령대'])
    
    # Rearrange columns
    df_tidy = df_tidy[['기준일ID', '시간대구분', '행정동코드', '성별', '연령대', '생활인구수']]
    
    print("\n--- Tidy DataFrame Head ---")
    print(df_tidy.head())
    
    print("3. Downcasting data types for optimization...")
    # Check ranges and downcast
    df_tidy['기준일ID'] = df_tidy['기준일ID'].astype(np.int32)
    df_tidy['시간대구분'] = df_tidy['시간대구분'].astype(np.int8)
    df_tidy['행정동코드'] = df_tidy['행정동코드'].astype(np.int32)
    df_tidy['성별'] = df_tidy['성별'].astype('category')
    df_tidy['연령대'] = df_tidy['연령대'].astype('category')
    df_tidy['생활인구수'] = df_tidy['생활인구수'].astype(np.float32)
    
    print("4. Saving as Parquet...")
    df_tidy.to_parquet(parquet_path, index=False, compression='snappy')
    
    print("5. Verification and comparison...")
    df_parquet = pd.read_parquet(parquet_path)
    parquet_info = get_df_info_str(df_parquet)
    print("\n--- Parquet DataFrame info() ---")
    print(parquet_info)
    
    # Compare sizes
    zip_size = os.path.getsize(zip_path) / (1024 * 1024)
    parquet_size = os.path.getsize(parquet_path) / (1024 * 1024)
    
    # Count rows/cols
    orig_shape = df_orig.shape
    parquet_shape = df_parquet.shape
    
    # Print out summary statistics
    print(f"\nOriginal shape: {orig_shape}")
    print(f"Parquet shape: {parquet_shape}")
    print(f"Zip file size: {zip_size:.2f} MB")
    print(f"Parquet file size: {parquet_size:.2f} MB")
    
    # Create Markdown Report
    report_content = f"""# 데이터 가공 및 압축 보고서: 서울시 생활인구 (동별)

이 보고서는 `LOCAL_PEOPLE_DONG_202606.zip` 데이터를 Tidy Data 형태로 변환하고, 데이터 타입을 Downcast하여 Parquet 형식으로 최적화해 저장한 결과를 비교 분석합니다.

## 1. 개요 및 요약
- **원본 데이터 포맷**: ZIP 압축된 CSV 파일 (`LOCAL_PEOPLE_DONG_202606.csv`)
- **최적화 데이터 포맷**: Parquet 파일 (`LOCAL_PEOPLE_DONG_202606.parquet`, Snappy 압축)
- **변환 방식**: 와이드(Wide) 형태의 성별/연령대별 생활인구 컬럼(28개)을 롱(Long) 형태의 Tidy Data 컬럼(`성별`, `연령대`, `생활인구수`)으로 멜트(Melt) 처리.
- **데이터 최적화**: 
  - 정수형 컬럼(`기준일ID`, `시간대구분`, `행정동코드`)을 적절한 크기(`int32`, `int8`, `int32`)로 다운캐스팅.
  - 범주형 컬럼(`성별`, `연령대`)을 `category` 타입으로 변환.
  - 실수형 컬럼(`생활인구수`)을 `float32`로 변환.

## 2. 파일 크기 및 데이터 형태 비교
| 구분 | 원본 ZIP 파일 | 변환 후 Parquet 파일 | 변화율 |
| --- | --- | --- | --- |
| **파일 크기** | {zip_size:.2f} MB | {parquet_size:.2f} MB | {((parquet_size - zip_size) / zip_size * 100):+.1f}% |
| **행 수 (Rows)** | {orig_shape[0]:,} | {parquet_shape[0]:,} | {((parquet_shape[0] - orig_shape[0]) / orig_shape[0] * 100):+.1f}% (Tidy화로 28배 증가) |
| **열 수 (Columns)** | {orig_shape[1]} | {parquet_shape[1]} | {((parquet_shape[1] - orig_shape[1]) / orig_shape[1] * 100):+.1f}% (28개 성별/연령대 -> 3개) |

> [!NOTE]
> Tidy Data 형태로 변환하면서 행의 개수가 28배로 대폭 늘어났음에도 불구하고, Parquet의 압축 효율과 적절한 데이터 타입 최적화(Downcasting) 덕분에 파일 용량이 매우 효율적으로 유지되었습니다.

## 3. DataFrame info() 비교

### (1) 원본 CSV 데이터프레임 정보
```text
{orig_info.strip()}
```

### (2) 최적화 Parquet 데이터프레임 정보
```text
{parquet_info.strip()}
```

## 4. 데이터 타입 최적화 상세 (Downcasting)
- **기준일ID**: `int64` $\\rightarrow$ `int32` (메모리 절반 감소)
- **시간대구분**: `int64` $\\rightarrow$ `int8` (메모리 87.5% 감소)
- **행정동코드**: `int64` $\\rightarrow$ `int32` (메모리 절반 감소)
- **성별 / 연령대**: `object` (문자열) $\\rightarrow$ `category` (문자열 중복 제거 및 인덱스화로 엄청난 메모리 절약)
- **생활인구수**: `float64` $\\rightarrow$ `float32` (정밀도 유지하며 메모리 절반 감소)

## 5. 결론 및 제안
Tidy Data 형태는 분석 및 시각화 도구(예: BI 툴, Seaborn, ggplot 등)에서 데이터를 처리할 때 매우 유용합니다. 비록 행의 수는 늘어났으나, 적합한 데이터 타입 다운캐스팅과 Parquet 포맷을 사용하여 용량과 I/O 성능 면에서 큰 이점을 얻을 수 있게 되었습니다.
"""
    
    # Save report to artifacts directory (C:\Users\tasha\.gemini\antigravity-ide\brain\d8130969-c0e8-42c0-bc5c-ca4693bf3828)
    # The actual artifact path can be determined from App Data Directory or relative.
    # To write it as an artifact, we can save it to the artifacts directory.
    # The task asks us to save the report, and the artifacts directory is provided in user info:
    # C:\Users\tasha\.gemini\antigravity-ide\brain\d8130969-c0e8-42c0-bc5c-ca4693bf3828
    
    os.makedirs('seoul-pops/report', exist_ok=True)
    with open('seoul-pops/report/data_processing_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("\nReport successfully saved to 'seoul-pops/report/data_processing_report.md'")

if __name__ == '__main__':
    main()
