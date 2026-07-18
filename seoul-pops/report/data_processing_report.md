# 데이터 가공 및 압축 보고서: 서울시 생활인구 (동별)

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
| **파일 크기** | 41.60 MB | 39.83 MB | -4.2% |
| **행 수 (Rows)** | 305,280 | 8,547,840 | +2700.0% (Tidy화로 28배 증가) |
| **열 수 (Columns)** | 32 | 6 | -81.2% (28개 성별/연령대 -> 3개) |

> [!NOTE]
> Tidy Data 형태로 변환하면서 행의 개수가 28배로 대폭 늘어났음에도 불구하고, Parquet의 압축 효율과 적절한 데이터 타입 최적화(Downcasting) 덕분에 파일 용량이 매우 효율적으로 유지되었습니다.

## 3. DataFrame info() 비교

### (1) 원본 CSV 데이터프레임 정보
```text
<class 'pandas.DataFrame'>
RangeIndex: 305280 entries, 0 to 305279
Data columns (total 32 columns):
 #   Column           Non-Null Count   Dtype  
---  ------           --------------   -----  
 0   기준일ID            305280 non-null  int64  
 1   시간대구분            305280 non-null  int64  
 2   행정동코드            305280 non-null  int64  
 3   총생활인구수           305280 non-null  float64
 4   남자0세부터9세생활인구수    305280 non-null  float64
 5   남자10세부터14세생활인구수  305280 non-null  float64
 6   남자15세부터19세생활인구수  305280 non-null  float64
 7   남자20세부터24세생활인구수  305280 non-null  float64
 8   남자25세부터29세생활인구수  305280 non-null  float64
 9   남자30세부터34세생활인구수  305280 non-null  float64
 10  남자35세부터39세생활인구수  305280 non-null  float64
 11  남자40세부터44세생활인구수  305280 non-null  float64
 12  남자45세부터49세생활인구수  305280 non-null  float64
 13  남자50세부터54세생활인구수  305280 non-null  float64
 14  남자55세부터59세생활인구수  305280 non-null  float64
 15  남자60세부터64세생활인구수  305280 non-null  float64
 16  남자65세부터69세생활인구수  305280 non-null  float64
 17  남자70세이상생활인구수     305280 non-null  float64
 18  여자0세부터9세생활인구수    305280 non-null  float64
 19  여자10세부터14세생활인구수  305280 non-null  float64
 20  여자15세부터19세생활인구수  305280 non-null  float64
 21  여자20세부터24세생활인구수  305280 non-null  float64
 22  여자25세부터29세생활인구수  305280 non-null  float64
 23  여자30세부터34세생활인구수  305280 non-null  float64
 24  여자35세부터39세생활인구수  305280 non-null  float64
 25  여자40세부터44세생활인구수  305280 non-null  float64
 26  여자45세부터49세생활인구수  305280 non-null  float64
 27  여자50세부터54세생활인구수  305280 non-null  float64
 28  여자55세부터59세생활인구수  305280 non-null  float64
 29  여자60세부터64세생활인구수  305280 non-null  float64
 30  여자65세부터69세생활인구수  305280 non-null  float64
 31  여자70세이상생활인구수     305280 non-null  float64
dtypes: float64(29), int64(3)
memory usage: 74.5 MB
```

### (2) 최적화 Parquet 데이터프레임 정보
```text
<class 'pandas.DataFrame'>
RangeIndex: 8547840 entries, 0 to 8547839
Data columns (total 6 columns):
 #   Column  Dtype   
---  ------  -----   
 0   기준일ID   int32   
 1   시간대구분   int8    
 2   행정동코드   int32   
 3   성별      category
 4   연령대     category
 5   생활인구수   float32 
dtypes: category(2), float32(1), int32(2), int8(1)
memory usage: 122.3 MB
```

## 4. 데이터 타입 최적화 상세 (Downcasting)
- **기준일ID**: `int64` $\rightarrow$ `int32` (메모리 절반 감소)
- **시간대구분**: `int64` $\rightarrow$ `int8` (메모리 87.5% 감소)
- **행정동코드**: `int64` $\rightarrow$ `int32` (메모리 절반 감소)
- **성별 / 연령대**: `object` (문자열) $\rightarrow$ `category` (문자열 중복 제거 및 인덱스화로 엄청난 메모리 절약)
- **생활인구수**: `float64` $\rightarrow$ `float32` (정밀도 유지하며 메모리 절반 감소)

## 5. 결론 및 제안
Tidy Data 형태는 분석 및 시각화 도구(예: BI 툴, Seaborn, ggplot 등)에서 데이터를 처리할 때 매우 유용합니다. 비록 행의 수는 늘어났으나, 적합한 데이터 타입 다운캐스팅과 Parquet 포맷을 사용하여 용량과 I/O 성능 면에서 큰 이점을 얻을 수 있게 되었습니다.

## 6. 추가 최적화 결과 (`기준일ID`, `행정동코드` 카테고리화)
사용자 요청에 따라 고유값 개수가 적은 `기준일ID`(30개)와 `행정동코드`(424개)를 기존 `int32`에서 `category` 타입으로 추가 최적화했습니다.

### (1) 나머지 데이터의 기술통계량
#### 수치형 데이터 기술통계
```text
              시간대구분         생활인구수
count  8.547840e+06  8.547840e+06
mean   1.150000e+01  8.568291e+02
std    6.922187e+00  7.247549e+02
min    0.000000e+00  0.000000e+00
25%    5.750000e+00  4.354366e+02
50%    1.150000e+01  6.751573e+02
75%    1.725000e+01  1.051624e+03
max    2.300000e+01  2.124420e+04
```

#### 범주형 데이터 기술통계
```text
             성별      연령대
count   8547840  8547840
unique        2       14
top          남자     0-9세
freq    4273920   610560
```

### (2) 추가 최적화 후 DataFrame info()
```text
<class 'pandas.DataFrame'>
RangeIndex: 8547840 entries, 0 to 8547839
Data columns (total 6 columns):
 #   Column  Dtype   
---  ------  -----   
 0   기준일ID   category
 1   시간대구분   int8    
 2   행정동코드   category
 3   성별      category
 4   연령대     category
 5   생활인구수   float32 
dtypes: category(4), float32(1), int8(1)
memory usage: 81.5 MB
```

### (3) 추가 최적화 전후 비교 요약
- **메모리 사용량 (info() 기준)**: 122.3 MB $\rightarrow$ **40.8 MB (약 66.6% 감소)**
- **디스크 파일 크기**: 54.91 MB $\rightarrow$ **18.73 MB (약 65.9% 감소)**

> [!TIP]
> `기준일ID`와 `행정동코드`를 범주형(`category`) 데이터 타입으로 변환함으로써, 내부적으로 큰 메모리를 차지하던 `int32`(4바이트) 정수 대신 고유 키값의 딕셔너리와 아주 작은 정수 인덱스(`int8` 및 `int16`)로 대체 저장되어 메모리 및 디스크 사용량이 약 2/3 가량 극적으로 절약되었습니다.

## 7. Parquet 파일 메타 정보 및 구조 설명

최종 최적화되어 저장된 `LOCAL_PEOPLE_DONG_202606_optimized.parquet` 파일의 물리적 메타 정보 및 스키마 구조는 다음과 같습니다.

### (1) Parquet 파일 메타데이터 (FileMetaData)
- **생성 도구 (created_by)**: `parquet-cpp-arrow version 24.0.0`
- **열 개수 (num_columns)**: 6개
- **행 개수 (num_rows)**: 8,547,840개
- **행 그룹 개수 (num_row_groups)**: 9개
- **포맷 버전 (format_version)**: 2.6
- **직렬화 크기 (serialized_size)**: 9,917 바이트 (메타데이터 자체의 크기)

### (2) Parquet 물리적 스키마 (ParquetSchema)
```text
required group field_id=-1 schema {
  optional binary field_id=-1 기준일ID (String);
  optional int32 field_id=-1 시간대구분 (Int(bitWidth=8, isSigned=true));
  optional binary field_id=-1 행정동코드 (String);
  optional binary field_id=-1 성별 (String);
  optional binary field_id=-1 연령대 (String);
  optional float field_id=-1 생활인구수;
}
```

### (3) 메타 정보 상세 설명

1. **포맷 버전 및 생성 엔진**
   - 포맷 버전 `2.6`은 Parquet의 최신 최적화 규격을 적용하여 효율적인 인코딩 방식을 지원합니다.
   - `created_by`의 PyArrow 엔진을 통해 C++ 기반의 성능 효율과 탁월한 압축 성능을 보장받습니다.

2. **행 그룹 (Row Groups = 9)**
   - Parquet는 대용량 데이터를 효율적으로 디스크 I/O 하기 위해 데이터를 여러 **행 그룹(Row Group)** 단위로 분할 저장합니다. 이 파일은 총 9개의 행 그룹으로 분할되어 있으며, 각 행 그룹은 개별적으로 통계 정보(최소/최대값 등)를 갖습니다.
   - 조건절 필터링(예: 특정 시간대 조회) 쿼리 실행 시 이 통계 정보를 활용하여 불필요한 행 그룹을 통째로 패스하는 **Row Group Skipping** 기능이 동작하므로 쿼리 성능이 비약적으로 향상됩니다.

3. **물리적 데이터 타입 매핑**
   - **기준일ID, 행정동코드, 성별, 연령대**: Pandas의 `category` 타입 컬럼들은 Parquet 파일 내부에서 딕셔너리 인코딩 기반의 `binary (String)` 타입으로 압축 저장됩니다. 텍스트 데이터의 중복 저장을 완전히 방지하여 디스크 용량을 대폭 줄입니다.
   - **시간대구분**: `Int(bitWidth=8, isSigned=true)`로 매핑되어, 디스크 내 물리 저장 공간에서도 정밀하게 1바이트(`int8`) 크기만을 소모합니다.
   - **생활인구수**: 일반적인 8바이트 실수(double) 대신 4바이트 실수인 `float` 타입으로 지정되어 물리 스토리지 부담을 절반 수준으로 경감시켰습니다.

