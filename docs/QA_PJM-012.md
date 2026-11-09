# PJM-012 QA · 카카오맵 주변 동물병원 검색

- 기준선: 프지마 v0.7.0 `main` `4b21e8ba7abc4fd6c6c50542f2e8b9f086098f4b`
- 기능 브랜치: `feature/pjm-012-kakao-nearby`
- 상태: **G1/G2 승인, 기능 브랜치 구현 및 모의 브라우저 QA 통과, G3 미승인**
- 첫 자동검사: https://github.com/jkd04255/peujima/actions/runs/42401745694 — FAIL; 기존 필터가 '동물병원'을 포함하는 카페명을 잘못 허용함
- 수정 커밋: `17ff9bdcfb8ac99eb76219980468ae5fd4b96bb9` — 카카오 category_name이 있으면 동물병원 분류로 제한
- 수정 후 검사: https://github.com/jkd04255/peujima/actions/runs/42401838778 — **SUCCESS**
- 실행: GitHub Actions ubuntu-latest / Chromium / Playwright 1.56.0
- 테스트 데이터: **모의 Kakao SDK/고정 GPS·가상 결과**로 4개 화면 회귀 QA + 별도의 **실제 Kakao 서버 응답 시험** (2026-11-09, 서울시청 고정 좌표)

## 확인 항목
| 화면 | PJM-012 모의 GPS + Kakao | PJM-011 가상예약 회귀 |
|---|---|---|
| 320×700 | PASS | PASS |
| 390×844 | PASS | PASS |
| 768×1024 | PASS | PASS |
| 1440×900 | PASS | PASS |

검증 내용:
- 로드 시 자동 GPS 권한 요청 / 카카오 API 호출 없음
- 사용자가 클릭한 뒤 GPS 좌표가 카카오 `keywordSearch('동물병원')`에 전달됨
- 카카오 장소 검색 옵션 `radius=3000`, `sort=DISTANCE`, `location` 확인
- 지도 객체 및 마커 생성, 가까운 순 목록, 카카오맵 상세 링크 확인
- '동물병원'을 이름에 포함한 카페는 카카오 카테고리 기준으로 제외
- 1km 반경 재검색, 주소/지역 수동 검색, 결과 0건에서 이전 검색 결과 제거
- JavaScript 키가 없을 때 실제 데이터 가공하지 않고 설정 안내
- GPS 거부 시 지역 직접입력 가능
- 가상 병원 5곳 및 7일 캘린더/의료진/예약 완료/보험 안내 정상 동작
- 4가지 화면 너비에서 페이지 가로 넘침/JS pageerror 없음
- QA 스크린샷은 모의 결과임을 명확히 표시 (`pjm-012-390-mock-results.png`)

## 테스트하지 못한 사항 / 후속 검증
- **실제 Kakao API JavaScript 키가 GitHub Actions Secret에 등록되어 인증·장소 검색·지도 SDK 로드 검증 성공.** 카카오 사용량/실제 과금은 개발자 콘솔에서 별도 확인 필요.
- 사용자 제공 카카오 콘솔 스크린샷에서 **프지마 앱 ID 1642725의 일간 무료 쿼터 제공** 문구 확인(2026-11-09).
- 실제 GPS 좌표 접근/사용자 위치를 통한 현장 병원 결과, iPhone Safari/Android 실기기 확인 미수행
- 모든 동물병원 명칭·카테고리 사례 및 키보드/스크린리더 조합 전체를 독립적으로 검증하지 않음
- `main` 공개 Pages는 **기존 v0.7.0** 그대로; PJM-012는 아직 공개되지 않음
- QA는 작성한 팀과 동일 AI가 작성/수정했으므로 독립 QA를 대체하지 않음

## 승인/배포 게이트
- [x] G1: 카카오맵 무료 API 기반 주변 병원 검색 기획 동의 (병원 비교 제외)
- [x] G2: 위치/지도/거리순/수동 검색 및 가상 예약 분리 UX 사용자 명시 승인
- [x] 브랜치 구현 및 4개 화면의 모의 QA 성공
- [x] JavaScript 키 GitHub Actions Secret 등록 및 `http://localhost:8000` 허용 도메인 등록 결과 검증
- [x] 실제 카카오 API 연동 테스트: 서울시청 고정 좌표에서 **실제 동물병원 14곳 검색** 및 지도 로드 성공
- [ ] iPhone Safari 실제 GPS 및 위치 권한/지역 검색 실기기 확인
- [ ] **G3 공개 배포 승인**
- [ ] `main` 병합 및 GitHub Pages 배포

## 실제 API 시험 준비(2026-11-09)
- 추가 시험: `tests/test_pjm_012_live.py`, GitHub Actions **기능 브랜치 push에서만** `PJM012_KAKAO_JS_KEY` 비공개 Secret 주입.
- 2026-11-09 GitHub Actions 기존 push 워크플로 **재실행(시도 #2)**: `https://github.com/jkd04255/peujima/actions/runs/42556519996` → **SUCCESS**. 서울시청 고정 좌표에서 JavaScript SDK 인증, 실제 동물병원 14곳 반환, 지도 객체 생성. 테스트는 프지마 사용자의 GPS 정보를 취득하지 않았고, 키 값은 로그·소스코드에 기록되지 않음.
- 키 미등록 시 live 시험은 **SKIP**이며 합성 QA 결과와 혼동하면 안 됨.

## 실 API QA 결과 (2026-11-09 KST)
- GitHub Actions: https://github.com/jkd04255/peujima/actions/runs/42556519996 (rerun attempt 2, success).
- 실제 SDK 허용 origin: `http://localhost:8000` (GitHub Actions 임시 테스트 서버).
- 고정된 테스트 좌표: 위도 `37.5662952`, 경도 `126.9779451` (서울시청 인근).
- 실제 Kakao 응답: 동물병원 14곳, 지도 로드 성공, 카카오맵 상세보기 링크 및 가로 넘침·JS 오류 확인 통과.
- 기존 320/390/768/1440 모의 API 및 PJM-011 가상 예약 회귀는 동일 재실행에서 통과.
- **실서비스 도메인 `https://jkd04255.github.io`의 실 API, iPhone Safari 현장 GPS 및 배포 사이트 검증은 아직 미실시.** PJM-012는 main 미병합, G3 미승인.

## PJM-012 G3 전 필수 보완 및 모바일/접근성 QA (2026-11-09)

### 구현/릴리스 게이트
- `scripts/build_pages.py`: Actions Secret의 **공개 가능한 Kakao JS 키**를 `dist/index.html`에서만 `pjm012-nearby.js` 로딩 이전에 주입. 저장소 소스는 미변경, 키가 없으면 빌드 실패.
- `.github/workflows/pjm-012-pages-release.yml`: **G3 승인 후 main에서만 수동 실행**. `workflow_dispatch` 외 push/PR 배포 트리거 없음; main + `PJM-012_G3_APPROVED` 입력 두 조건에서만 빌드/배포. 현재 실행되지 않음.
- **중요**: 실제 G3 때 `main` 병합 **전에** Pages 설정을 branch source에서 `GitHub Actions`로 변경해야 함. 그렇지 않으면 branch 자동 게시로 키 없는 화면이 공개될 위험. 이번 단계에서 Pages 설정/배포 전혀 변경 없음.
- 일반 방문자는 승인된 정식 빌드에서 키 입력창을 볼 필요가 없으며, `window.PRZIMA_KAKAO_JS_KEY`가 미리 주입됨. JS 키는 공개 HTML의 웹키로 보이는 것이 정상이며 도메인 제한·무료 쿼터 관리가 중요.

### 실패 및 수정 기록
- axe 첫 실행 https://github.com/jkd04255/peujima/actions/runs/42558477077 — **신규 주변 병원 영역의 낮은 보조 문구 대비** 위반 발견. PJM-012 전용 CSS에서 보조 글자색 대비를 개선하고 재검증.
- 모바일 Safari 유사 환경에서 입력창 자동 확대를 방지하기 위해 620px 이하 입력 글자 크기 `16px` 및 터치 영역 `44px` 조정.

### 최종 자동검사
- **실제 기능 브랜치 push QA 성공**: https://github.com/jkd04255/peujima/actions/runs/42558621988
- 빌드 단위: synthetic 공개 키 사전 주입, key absent fail-closed, 변경 전 소스 보존 — **PASS**.
- Playwright Chromium: 320×700, 390×844, 768×1024, 1440×900, mock Kakao/GPS 승인·거절·지역 검색·반경/결과 0건, 기존 가상 예약 회귀 — **PASS**.
- **Playwright WebKit** (Linux, Safari 엔진 근사): iPhone 13 및 iPad 7세대 viewport, 탭/터치 GPS, 자동 키 제공, 지도 마커·지역 입력·반경, GPS 권한 거부 대안 — **PASS**. *실제 iPhone Safari 기기 검증 아님*.
- **axe-core 4.10.3**, 신규 `#nearby-hospitals` 영역만: WCAG 2.2 A/AA tag 기반 검사, 320/390/768/1440px 각각 초기/결과 상태 **총 8회에서 자동 위반 0건**. 키보드 지역검색 입력→검색 버튼 포커스 이동 확인 — **PASS**. *전체 사이트·실제 스크린리더 모든 접근성 기준 충족으로 간주하지 않음*.
- **실제 카카오 서버 검증**: `http://localhost:8000`에서 Actions Secret을 빌드 주입한 후 별도 방문자 키 입력 없이 **고정 서울시청 위치 기준 동물병원 14곳** 검색, 지도 로드/스크립트 오류 없음 — **PASS**. 실사용자 GPS 미사용. 최종 GitHub Pages 도메인 검증 아님.
- 전체 테스트 로그와 두 모의 모바일 스크린샷은 위 성공 실행에서 확인 가능.

### 계속 보류
- [ ] **실기기 iPhone Safari** 위치 권한 허용/거부·실제 GPS·수동 검색·터치·스크롤·확대/축소 확인.
- [ ] 실제 GitHub Pages `https://jkd04255.github.io` origin의 JavaScript SDK 허용 확인 및 배포 후 내용 확인(아직 미배포).
- [ ] 사용자의 명시적 G3 공개 배포 승인.
- [ ] GitHub Pages Source 변경 → main 병합 → 수동 배포 (승인 전 모두 금지).
- [ ] 실제 무료 쿼터 소진 시 대응 및 카카오 개발자 콘솔 사용량 재확인. 유료 서비스는 미승인.
