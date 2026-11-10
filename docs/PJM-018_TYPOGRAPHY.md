# PJM-018 — SUIT Variable 통합 타이포그래피

2026-11-10 사용자 요청: 프지마 전체 글씨체가 마음에 들지 않으므로 트렌디한 사이트의 서체를 조사하고 교체.

## 비교 및 선택
| 후보 | 특징 | 판단 |
| --- | --- | --- |
| Pretendard Variable | 현대적이고 익숙한 화면용 네오 그로테스크, 공식 동적 서브셋 | 우수하지만 기존 범용 인상과 크게 차별화되지 않음 |
| SUIT Variable | 좁은 카드·모바일에서 간결하고 균형 잡힌 UI 본문형 한글 서체 | **채택**. 통일감·모바일 공간 활용에 적합 |

- 서체 배포자: [sun-typeface/SUIT](https://github.com/sun-typeface/SUIT)
- 공식 배포 CSS: `https://cdn.jsdelivr.net/gh/sun-typeface/SUIT@2/fonts/variable/woff2/SUIT-Variable.css`
- 이용 조건: SIL Open Font License 1.1. 기존 배포자가 허용한 상업적 용도 내에서 공식 CDN 이용
- 프리텐다드 비교 출처: https://github.com/orioncactus/pretendard
- 로딩 실패 시 `Apple SD Gothic Neo`, `Noto Sans KR`, `Malgun Gothic`, `system-ui` 순서의 시스템 폰트 사용
- 외부 이미지·계정 정보·결제·실예약 등 별도 데이터 전송 없음. 폰트 요청은 외부 CDN을 사용하므로 해당 CDN으로 접속이 발생할 수 있음

## 구현
- 파일: `pjm013-navigation.css` **1개 코드 수정**. 기존 커다란 `index.html` 인라인 CSS는 보존
- 파일 첫 부분에 공식 SUIT v2 가변 웹폰트 CSS import
- 기존의 `DM Sans / Noto Sans KR / Apple SD Gothic Neo / Noto Serif KR` 등 여러 글꼴 지정이 뒤섞이지 않도록 사용자 화면 텍스트에 동일 글꼴 스택 강제
- 브랜드 타이포그래피 800, 주요 제목 700~750, 메뉴 670~710, 본문은 기존 400~500 수준으로 재조정
- 한글 제목의 지나친 -0.07em~-0.09em 자간을 약 -0.035em~-0.05em으로 보정
- 기존 배경색·사진·카드·버튼·지도·시연 및 안내 문구·모바일 구조 불변
- 가변 굵기 지원으로 Windows·iOS 간 제목 인상이 가능한 한 일관되도록 조정

## QA
- 신설 `tests/test_pjm_018_typography.py`: Chrome 320/390/768/1440 및 WebKit 390 뷰포트에서 브랜드/메뉴/홈/실제 병원 검색/가상 병원/보험의 동일 서체 지정 검증, 선택/폼 보존, 넘침 검사
- 기존 PJM-011/012/013/014/016 Chromium·WebKit·axe 전체 회귀 QA 유지
- 테스트는 가짜 Kakao 결과만 사용하며 실예약 또는 실사용자 위치를 전송하지 않음
- CDN은 실 서비스에서만 실제 로드하고, 자동 테스트에서는 외부 CSS 요청을 대체해 서체 지정/폴백을 결정론적으로 검증함. **실제 iPhone Safari 폰트 로딩은 배포 후 별도 검증**
- QA 성공 시 PR 생성. 사용자 별도 승인 전 main 병합·GitHub Pages 배포 보류


## PR #16 · 충돌 해결 후 SUITE 제목 서체 추가
- PR #15가 SUIT Variable 통일 작업을 먼저 main에 병합했으므로 해당 본문 서체·굵기·기존 테스트를 보존합니다.
- 본 PR은 공식 SUITE Variable을 브랜드·제목·병원명에만 추가합니다. 메뉴·본문·버튼·입력 등은 SUIT를 유지합니다.
- SUITE 공식 배포: https://github.com/sun-typeface/SUITE (SIL OFL 1.1); CSS: https://cdn.jsdelivr.net/gh/sun-typeface/SUITE@2/fonts/variable/woff2/SUITE-Variable.css
- 기존 Chromium·WebKit 테스트에 실제 화면별 계산 서체가 SUITE인지 확인하는 검사만 추가했습니다.
- 사용자 별도 승인 전 main 병합 및 Pages 배포 보류, 실제 iPhone Safari QA 미확인.
