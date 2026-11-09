# PJM-012 카카오맵 JavaScript 키 발급 및 연결

상태: **G2 승인 기능 브랜치 전용 안내**. 키 미설정 / 실제 카카오 API 실호출 미검증. main/Pages에는 기능이 배포되지 않음.

## 1. 카카오맵 API 설정
1. https://developers.kakao.com/ 에서 로그인 → [앱] → 앱 생성 (이름 프지마 등).
2. 해당 앱에서 [카카오맵] → [사용 설정] → 상태 ON.
3. 무료 쿼터 표시가 있는지 확인. **계정에서 첫 번째 카카오맵 API 활성화 앱에만 무료 쿼터가 제공**됨(2026-07-21 이후 기준). 비즈월렛 연결/유료 API 활성화는 현재 허용되지 않음.
4. [앱] → [플랫폼 키] → **JavaScript 키** 선택 → JavaScript SDK 도메인 등록:
   - `https://jkd04255.github.io` (GitHub Pages origin)
   - `http://localhost:8000` (로컬 개발 origin)
5. 표시된 **JavaScript 키만 사용**. REST API 키, Admin 키, Client Secret 입력 금지.

공식 안내:
- https://developers.kakao.com/docs/ko/kakaomap/common
- https://apis.map.kakao.com/web/guide/
- https://developers.kakao.com/docs/ko/getting-started/app-key-migration
- https://developers.kakao.com/docs/ko/getting-started/quota

## 2. 개발 브랜치에서 실행
현재 기능 코드는 `feature/pjm-012-kakao-nearby` 브랜치에서만 사용 가능. 로컬 체크아웃 후 프로젝트 루트에서:
```bash
python -m http.server 8000
```
`http://localhost:8000/` 접속 → 주변 병원 섹션의 **개발용 JavaScript 키 설정** 펼치기 → 키 입력 → 현재 탭에 적용 → **내 위치로 동물병원 찾기** 또는 지역 검색.

별도 서버·DB·프록시·REST 인증키가 필요하지 않음. 키는 브라우저 sessionStorage에 저장되며 탭 종료 시 사라짐. 추후 G3 공개 운영에서 방문객도 자동으로 검색하도록 하려면 별도의 승인된 JavaScript 키 설정 및 실제 도메인 작동 확인 필요.

## 3. 검색 방식과 범위
- JavaScript SDK `https://dapi.kakao.com/v2/maps/sdk.js?appkey=...&libraries=services&autoload=false`를 **요청 후** 로드함.
- 클릭 시에만 브라우저 geolocation API가 위치 허가를 요청하며, 허용한 좌표에서 카카오 장소 키워드 검색 `동물병원`, 1/3/5km, 거리순(`SortBy.DISTANCE`)을 사용함.
- 지역 검색은 먼저 Geocoder 주소 검색, 실패하면 장소명 검색으로 중심 좌표를 구함.
- 카카오 응답으로 확인된 실제 동물병원만 지도/목록에 표시, 카카오 장소 상세 페이지와 연락처 연결. 실제 예약은 연결되지 않음.
- 허용 도메인·서비스 요금제·쿼터·영업 정보는 카카오 정책 및 정보 최신성에 따라 달라질 수 있음.

## 4. QA 구분
- 완료: GitHub Actions Chromium / 테스트용 모의 카카오 SDK 및 GPS 승인/거부/응답 0건 / 320·390·768·1440px / 기존 가상 예약 기능 회귀.
- 미완료: **실제 발급한 JavaScript 키**, 카카오 서버의 실제 검색 응답, 실제 지도 타일 로드, 실제 iPhone Safari/Android 기기, 사용자 GPS 현장 시험.
- 모의 스크린샷/결과는 실제 주변 동물병원 확인 증거가 아님.

## 5. 공개·유료 사용 보류
PJM-012는 G3 승인 전까지 `main`과 GitHub Pages에 병합/배포하지 않음. 유료 카카오맵 사용 설정, 비즈월렛 연결, 실예약/DB/인증/개인정보 보관 기능 모두 금지.

## 6. 실서비스 배포 없이 실제 카카오맵 SDK 확인 (2026-11-09 추가)
- 카카오 개발자 콘솔의 `JavaScript SDK 도메인`에 `http://localhost:8000` 등록 (GitHub Pages용 `https://jkd04255.github.io`와는 별개).
- GitHub 저장소 `jkd04255/peujima` → **Settings → Secrets and variables → Actions → New repository secret**:
  - Name: `PJM012_KAKAO_JS_KEY`
  - Secret: 카카오 개발자 콘솔에서 발급된 **JavaScript 키** (REST/Admin 키 아님)
- 키는 대화에 게시하지 말 것. GitHub Actions의 비공개 secret에만 저장할 것.
- 비밀값 생성만으로 테스트는 자동 실행되지 않음. 사용자 설정 완료 통지 후 기능 브랜치에 QA용 커밋을 만들어 `push` 테스트를 실행할 수 있음.
- GitHub Actions `PJM-012 GPS nearby hospitals QA` 워크플로의 **기능 브랜치 push 이벤트에 한하여** `tests/test_pjm_012_live.py`를 실제 카카오 SDK로 실행. 키 미등록 시 SKIP 메시지로 종료함.
- 테스트 브라우저는 **고정 시험 위치 서울시청**, `http://localhost:8000`을 사용하며 방문자 또는 사용자의 실제 위치를 취득하지 않음. 지도 로드 + 실제 장소 검색 응답과 근접 결과를 확인함.
- `main` 병합, GitHub Pages 배포, 유료 API 활성화, 키의 공개 소스 코드 삽입은 진행하지 않음.
