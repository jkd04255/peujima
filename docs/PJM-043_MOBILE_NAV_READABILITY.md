# PJM-043 — 모바일 하단 메뉴 한글 레이블 가독성

- 분류: 기존 디자인 유지형 소규모 UI 타이포그래피 개선
- 기준 main: `55ac5dcec154bf6cd4cc4e8f294e415cbc2004a7` (PJM-042 및 디자인 Skills PR #38 반영)
- 참고: `AGENTS.md`, `docs/OPERATING_PROCESS_v1.md`, `docs/HUMAN_WEB_DESIGN_ADOPTION.md`, Human Web Design 및 Frontend Design Skills
- 상태: 기능 브랜치 구현 / 정확한 PR HEAD 자동 QA와 G3 병합 게이트 확인 필요

## 문제 / 디자인 판단
코드 기준 하단 탭 레이블은 모바일 ≤850px에서 11px, 좁은 화면 ≤380px에서 10px입니다. 반려동물 진료과·병원 탐색·보험으로 이동하는 **반복 사용 경로**인데 한글 글자가 작아서 읽기 부담이 있습니다. 기존의 절제된 네비게이션과 SUIT/ SUITE 타이포그래피, 숲색/크림색 브랜드를 보존하면서 탭 레이블만 한 단계 키웁니다.

## 최소 변경
- 모바일 ≤850px 탭 글자 11 → 12px, line-height 1.25
- 모바일 ≤380px 탭 글자 10 → 11px
- 4개 메뉴, 이름, 아이콘, 활성 상태, 고정 위치, 안전 영역, 기존 focus-visible 링, 컬러, 반응형 배치는 그대로 둡니다.
- 신규 UI 텍스트·카드·버튼·애니메이션·외부 리소스·데이터 연동은 추가하지 않습니다.

## 인수 기준 / 검증
1. Chromium 320px 11px; 390/768px 12px, WebKit 320/390px 동일합니다.
2. 4개 메뉴가 한 줄에 표시되고 각 항목의 실제 터치/클릭 대상은 44×44px 이상이며 수평 넘침이 없습니다.
3. 클릭하여 보험 화면으로 이동한 뒤 현재 탭 `aria-current=page`가 올바르게 유지되고 JS 오류가 없어야 합니다.
4. 기존 전체 PJM-011~042, Chromium/WebKit/axe 및 새로운 PJM-043 검사를 **정확한 PR 최신 HEAD에서 통과**해야 병합할 수 있습니다.
5. QA 스크린샷(320/390px Chromium/WebKit)을 Actions artifact로 보존합니다.

## 보호·운영
- 사진, 그라데이션, 3모드 브랜드, 병원 상세·주변 탐색, 가상 예약/캘린더, 보험·진료비, 필수 고지 및 키보드 라우팅 변경 없음.
- G2 전체 Gate HOLD 유지. 실예약·보험 지급·개인정보/Auth·DB·유료 API 연동 금지.
- Pages 배포는 **사용자가 수동 실행**. main 병합과 실제 Pages 배포를 혼동하지 않습니다.
- 실제 iPhone Safari/Instagram 앱내 브라우저 검증 미확인.
