# PJM-023 · 펫보험 상품 선택/진료 항목/보장 근거 확대 (2026-11-10)

## 문제
PJM-022까지 3개 보험사 × 반려견/반려묘 6개 선택지, 진료 10개에 한정됨. 실제 진료 항목과 보장 내용의 차이를 한눈에 이해하기 어려움. 특히 원문 약관 확인 없이 각 질병 치료가 무조건 보장될 것처럼 표시하는 위험을 줄여야 함.

## 변경 범위
- 6개 보험사 12개 반려견·반려묘 선택지: 메리츠/현대/DB + 삼성/KB/NH (신규 6)
- 진료 항목: 기존 10개 + 35개 = **45개**. 소화기·내과·만성질환·피부/귀/눈·뼈/관절·검사/처치·고양이 질환·예방/일상 그룹.
- 반려견 보험 선택 시 고양이 전용 5종은 표시하지 않음. 선택 보험 변경 시 기존 결론 초기화.
- 사용자 필수 입력 **보험 상품 + 진료 항목 2개 유지**. 서버 및 업로드 없음.
- 선택 보험/진료에 따라 **상품 안내 버전**, 보상 대상, 보상비율, 자기부담금, 진료별 주의점 표시. 지급 한도/면책/확장특약은 인앱 상세 펼치기.
- 2025년 전국 진료비 항목별 공개 중간값만 표시. 새롭게 세분화된 35개 질환에는 임의 치료비 합계/보험금 지급액 없음.
- 기존 PJM-021 메리츠 시연 계산, PJM-022 DB **일일·연간 한도 적용 전** 가상 계산만 유지. 나머지 상품은 공식 상품 소개 정보만 요약.
- NH 펫앤미든든 2604는 판매 안내에서 확인했지만 **공식 약관 원문 미검증**으로 명시. KB 반려묘 26.07 역시 상품 존재 공시 확인만으로 보상금 계산을 허용하지 않음.

## 보험사별 근거 / 검증 수준
| 보험사 | 반려견/묘 공식 상품 출처 | 검증 내용 | 제한 |
| --- | --- | --- | --- |
| 메리츠 | https://www.meritzdirect.com/pet/product.do · https://www.meritzdirect.com/pet/product-cat.do | 반려견/묘 플랜별 보상비율·한도·공제금·영상검사 안내 | 개별 증권·약관 전문 미대조 |
| DB | https://www.directdb.co.kr/ltm/prd/cpnm/custInfoView.do?pdcDvcd=l_pet_dog&searchPdcCd=31119&searchPdcTrtHistCd=00 · https://m.directdb.co.kr/ltm/prd/cpnmcat/custInfoView.do?pdcDvcd=l_pet_cat&searchPdcCd=31121&searchPdcTrtHistCd=00 | 반려견 2610 보상비율·공제금·관절 대기, 반려묘 공개 상품 | 2607↔2610 버전 혼용 금지, 실제 플랜 미확정 |
| 현대해상 | https://m.hi.co.kr/serviceAction.do?menuId=202853 · https://mdirect.hi.co.kr/service.do?m=e9b3d5b6c3&petType=C | Hi2601 및 다이렉트 강아지/고양이 치료와 특약 소개 | 플랜별 실제 가입 정보 미확인 |
| 삼성화재 | https://direct.samsungfire.com/m/fp/pet.html | 강아지/고양이 특약, 50/70/80% 선택형 소개 | 공제·가입 한도·대기기간 미검증 |
| KB | https://insight.kbinsure.co.kr/pet-insurance-coverage/ · https://www.kbinsure.co.kr/CG803000012.ec | 2026.01 개정 발표, 26.07 반려견·반려묘 상품 공시 | 개정 발표 최대 한도는 모든 가입 플랜 공통 아님 |
| NH | https://nh-insure.co.kr/pet/ · https://mobile.newsis.com/view/NISX20241204_0002983874 | NH펫앤미든든 2604 판매 안내 및 출시 보도 | **보험사 공식 원문 약관 미검증**, 수치 계산 금지 |

### 진료비
- 농림축산식품부 2025 전국 진료비 현황, 개별 항목 중간값.
- https://www.mafra.go.kr/bbs/home/792/592824/download.do
- 기존 근거 표 및 가정 시나리오: [PJM-021_INSURANCE_EVIDENCE.md](PJM-021_INSURANCE_EVIDENCE.md)
- **개별 항목별 전국 중간값을 질병 평균 치료비로 말하지 않는다.**
- 진단·시술 추천이나 실제 청구 지원 기능이 아니다.

## 구현
- `pjm023-catalog.js`: 공식 확인 상품의 버전·보상 개요·검증 단계와 35개 세분화 진료 항목.
- `pjm019-insurance.js/.css`: 기존 2개 필수 선택 UX 유지, 그룹별 진료, 12개 상품 안내, 간결한 펼치기 조건.
- `index.html`, `scripts/build_pages.py`, `tests/test_pjm_012_build.py`: 신규 자산 로딩 및 승인형 Pages 배포 산출물 반영.
- `tests/test_pjm_023_catalog.py`: Chromium(320, 390, 768, 1440), WebKit(390) 신규 QA. 12개/45개 항목, 강아지↔고양이 분리, 출처·세부 조건, 한도 미검증 상품 지급액 표시 금지, 기존 지도/홈/보험 회귀 검증.
- 기존 전체 PJM-011~022 및 axe QA도 `.github/workflows/pjm-014-qa.yml`에서 실행.

## 남은 한계
1. 전 상품의 **모든 가입 연도별 실제 약관 PDF**를 판독한 것은 아니므로, 입원·통원·수술 횟수/세부 진료별 지급 심사는 제공하지 않는다.
2. 세분화 진료 종류는 보호자가 선택하기 쉽게 만들기 위한 탐색 항목이며, 질환이 실제로 진단되었다거나 모든 검사가 필요하다는 의미가 아니다.
3. 모든 상품 보험금을 단일 계산식으로 추측하지 않는다. 근거가 확보되는 보험사 한 곳씩 계산 범위를 확대한다.
4. 실제 iPhone Safari 실기기 검증 미실시. G2 전체 Gate HOLD, 실예약·실보험 API·유료 API·개인정보 수집 금지 유지.
5. PR 병합/Pages 공개 배포는 QA 및 승인 게이트를 따라 진행. **수동 Pages 워크플로는 사용자가 직접 실행한다. TinyFish는 사용하지 않는다.**
