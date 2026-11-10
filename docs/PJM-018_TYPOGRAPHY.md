# PJM-018 — 디자이너 시각의 공통 타이포그래피

## 사용자 요청
모든 페이지의 글씨체가 산만하고 통일되지 않는 문제를 개선. 기존 사진 중심 감성·컬러·콘텐츠·검색 및 예약 체험 유지.

## 디자인 결정
- 공통 UI/입력/리스트/본문: SUIT Variable (기본 400, 메뉴·버튼 650)
- 사진 히어로·섹션 제목·카드 이름·브랜드: SUITE Variable (대체로 700, 브랜드 780)
- 제목 자간 -0.048em, 네비게이션 자간 -0.022em. 기존 과도한 음수 자간·불규칙한 두께 표준화
- 모바일 검색 입력 16px 유지 (사파리 초점 확대 방지). word-break:keep-all 활용
- 폰트 외 기존 레이아웃·애니메이션·원본 동물 사진·필수 안내·서비스 기능 보존
- 공식 CDN: https://cdn.jsdelivr.net/gh/sun-typeface/SUIT@2 와 SUITE@2; 두 서체 모두 SIL OFL
- 서체 파일을 복제·재배포하지 않고 외부 공식 웹폰트 로드. CDN 접속 불가 시 시스템 폰트 fallback

출처: https://github.com/sun-typeface/SUIT 및 https://github.com/sun-typeface/SUITE

## 코드와 검증
- pjm013-navigation.css: 공식 폰트 CSS imports + 기존 개별 CSS font-family를 단일 디자인 토큰으로 통일
- tests/test_pjm_018_typography.py: Chromium 320/390/768/1440 및 WebKit 390에서 계산된 서체 CSS, 가로 넘침, 라우팅과 입력·안내 보존 QA
- CI에서 외부 CDN CSS를 모의하여 스타일 규칙을 검사하므로 실제 iPhone 글꼴 렌더링 검증을 대신하지 않음
- .github/workflows/pjm-014-qa.yml: PJM-018 feature push/PR 전체 회귀 QA 추가

## 운영
- 기준 main: ca71bcbc576e66341b52d2d157775e63a43afd67
- feature: feature/pjm-018-typography-system
- 기존 실예약·개인정보 저장·유료 API/Auth/보험사 API 금지 유지
- 전체 QA 후 PR 생성, 별도 승인 전 main 병합·Pages 배포 금지
- 실제 iPhone Safari 실기기 QA 미확인