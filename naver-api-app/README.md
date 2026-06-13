# 📊 Naver API Insight Dashboard

네이버 오픈 API를 활용하여 검색어 트렌드, 쇼핑 트렌드, 블로그/카페/뉴스/쇼핑 검색 데이터를 수집, 분석 및 시각화하는 Streamlit 대시보드 애플리케이션입니다.

## 🔗 Streamlit 서비스 접속 주소
* **배포 URL**: [https://icb1002-l6oj3njr57og9w4vj69rnn.streamlit.app/](https://icb1002-l6oj3njr57og9w4vj69rnn.streamlit.app/)

---

## 🛠️ 최근 작업 내역

### 1. API 인증 정보 관리 체계 개선 (보안 강화)
* **로컬/배포 하이브리드 로드 지원**: 로컬 환경에서는 `.env` 및 `.streamlit/secrets.toml`을 통해 API 인증 키(`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`)를 관리하고, 배포 후에는 Streamlit Cloud의 **Secrets**에서 자동으로 가져오도록 코드를 수정했습니다.
* **수동 입력 지원**: 인증 키가 세팅되지 않은 경우, 사이드바에서 사용자가 직접 키를 수동 입력하여 대시보드를 사용할 수 있게 폴백 기능을 구현했습니다.

### 2. 자동 커밋 및 푸시 훅(Hook) 시스템 구축
* **Git Post-Commit Hook 설정**: 로컬에서 커밋 성공 시 자동으로 원격 저장소에 `push`하도록 `.git/hooks/post-commit`을 작성했습니다.
* **실시간 변경사항 감시 데몬**: 로컬 파일 시스템 변경을 감시하여 변경사항이 저장되는 즉시 자동으로 커밋 및 푸시를 수행하는 `auto_git_sync.py` 스크립트를 가동했습니다.

### 3. 통계 분석 및 시각화 기능 오류 수정
* **Pandas Styler 의존성 해결**: EDA 요약본 제공 시 테이블 내 그라데이션(`Styler.background_gradient`)이 `matplotlib` 라이브러리 부재로 인해 로드되지 않던 에러를 해결했습니다.
* **의존성 업데이트**: `requirements.txt`에 `matplotlib`를 추가하여 로컬 및 배포 서버 환경에서 오류 없이 렌더링되도록 조치했습니다.
