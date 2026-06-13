# 📊 Naver API Insight Dashboard 배포 가이드

본 문서는 `naver-api-app` Streamlit 애플리케이션을 로컬 실행 및 **Streamlit Community Cloud**에 배포하는 방법을 설명합니다.

---

## 1. 로컬 환경에서 실행 및 테스트

배포 전 로컬 환경에서 대시보드가 정상 동작하는지 테스트합니다.

### 1-1. 필요한 패키지 설치
`naver-api-app` 폴더 내에 생성된 `requirements.txt` 파일을 이용하여 필요한 라이브러리를 설치합니다.
```bash
pip install -r requirements.txt
```

### 1-2. Streamlit 실행
가장 상위 폴더(워크스페이스 루트)가 아닌, `naver-api-app` 디렉토리로 이동하여 실행하거나, 해당 경로를 명시하여 실행합니다.
```bash
# naver-api-app 폴더 내에서 실행할 경우
streamlit run src/app.py
```

---

## 2. Streamlit Community Cloud 배포 방법

Streamlit Community Cloud를 사용하면 무료로 웹에 대시보드를 배포할 수 있습니다.

### 2-1. GitHub 저장소 준비
1. 현재 소스코드가 GitHub 저장소에 올라가 있는지 확인합니다. (이미 `https://github.com/Tashive/ICB10_02` 에 최신 작업본이 업로드되어 있습니다.)
2. 배포하려는 브랜치가 `main`인지 확인합니다.

### 2-2. Streamlit Cloud 설정 및 배포
1. [Streamlit Community Cloud](https://share.streamlit.io/)에 접속하여 로그인합니다 (GitHub 계정 연동 권장).
2. 우측 상단의 **"New app"** 버튼을 클릭합니다.
3. 아래 정보를 입력합니다:
   * **Repository**: `Tashive/ICB10_02`
   * **Branch**: `main`
   * **Main file path**: `naver-api-app/src/app.py`  *(경로 중요: 하위 폴더 형식이므로 앞에 `naver-api-app/`을 반드시 붙여야 합니다.)*
   * **App URL**: 사용자가 원하는 도메인명 설정 (예: `naver-api-insight`)
4. **"Deploy!"** 버튼을 누르기 전, 아래의 **API Key 설정(Secrets)**을 먼저 진행하거나 배포 후 진행해야 작동합니다.

---

## 3. 🔑 환경변수 및 Secrets 설정 (보안)

네이버 OpenAPI를 사용하기 위해서는 발급받은 Client ID와 Client Secret이 필요합니다. 배포된 웹 앱에서 매번 입력하지 않고 자동으로 로드되도록 Secrets 설정을 적용할 수 있습니다.

### 3-1. Streamlit Cloud에 Secrets 등록하기
1. 배포 중이거나 배포 완료된 대시보드 화면 우측 하단의 **"Settings"** (톱니바퀴 아이콘)을 클릭합니다.
2. 설정 팝업창에서 **"Secrets"** 메뉴로 이동합니다.
3. 텍스트 박스에 아래와 같이 네이버 개발자 센터에서 발급받은 키 정보를 입력하고 **Save**를 누릅니다:

```toml
NAVER_CLIENT_ID = "발급받은_네이버_Client_ID"
NAVER_CLIENT_SECRET = "발급받은_네이버_Client_Secret"
```

4. 이제 대시보드를 새로고침하면 왼쪽 사이드바에 자동으로 네이버 API 인증 정보가 채워져 바로 분석을 시작할 수 있습니다.
