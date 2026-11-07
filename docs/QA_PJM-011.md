# PJM-011 QA — 병원 상세 화면 및 예약 진입 분리

- 날짜: 2026-11-07 (KST)
- 기준선: 공개 v0.6.0
- 기능 브랜치: `feature/pjm-011-clinic-detail-flow`
- 검토 PR: https://github.com/jkd04255/peujima/pull/5 (G3 승인 후 main squash 병합 완료)
- 브라우저 테스트 실행: https://github.com/jkd04255/peujima/actions/runs/42346388537 (최신 브랜치 커밋 PASS), https://github.com/jkd04255/peujima/actions/runs/42346395046 (PR 재검증 PASS)
- 테스트 대상 구현 커밋: `f81504d3cfe6b088bbd38fd454dd057c91b1f370`
- 테스트 워크플로 커밋: `ee5f30d6bf9bc32f17011ed45016b0d122b910c7`
- 테스트 소스: `tests/test_pjm_011.py`
- 실행 환경: GitHub Actions / ubuntu-latest / Playwright 1.56.0 / Chromium
- 테스트 시간: 2026-11-07T06:17Z (KST 15:17)
- 테스트 기준 시각: 2026-11-07 15:00 KST (Playwright clock)
- 결과: **PASS 4/4**

## 테스트 항목
| 화면 | 결과 | 검증 내용 |
| --- | --- | --- |
| 320×700 | PASS | 목록→상세→예약→완료→보험→예약 접기→목록 복귀 |
| 390×844 | PASS | 동일 회귀 시나리오 + 3장 스크린샷 아티팩트 저장 |
| 768×1024 | PASS | 동일 회귀 시나리오 |
| 1440×900 | PASS | 동일 회귀 시나리오 |

모든 브라우저 시나리오는 다음을 추가 확인:
- 초기 병원 5곳 표시, 최초 목록에 캘린더/의료진 선택 UI가 없음
- 첫 병원 상세 정보 정확함, 예약하기 전 캘린더 숨김
- 예약하기 후 7일 캘린더/복수 의료진 표시, 의료진 선택 전 슬롯 없음
- 의료진 선택 후 가상 슬롯 선택 및 확인 버튼 활성화
- 기존 예약 모달 및 '기타' 입력 공란 경고
- 시연 완료 화면에서 병원명 보존, 보험 안내 진입
- 예약 접기 시 캘린더 제거, 목록 복귀 성공
- 가로 오버플로와 포착된 JS pageerror 없음

GitHub Actions 로그:
```text
PASS 320x700: list > detail > booking > confirmation > insurance > collapse > list
PASS 390x844: list > detail > booking > confirmation > insurance > collapse > list
PASS 768x1024: list > detail > booking > confirmation > insurance > collapse > list
PASS 1440x900: list > detail > booking > confirmation > insurance > collapse > list
ALL PJM-011 browser cases passed
```

## 남은 위험
- 실제 iPhone Safari/Android WebView 실기기 검증하지 않음.
- 키보드/스크린리더 전체 조합과 모든 필터/병원/휴진일 조합에 대한 완전 회귀 테스트는 아님.
- GitHub Pages 배포 워크플로 https://github.com/jkd04255/peujima/actions/runs/42354599119 는 성공, 단 공개 URL을 직접 HTTP 요청하여 최신 버전을 수신했는지 검증하는 작업은 접속 제약으로 미완료.
- 실제 예약/의료진/보험 자료는 합성 예시이며 진료 가능 정보가 아님.
- 제공된 레퍼런스 스크린샷은 예약 캘린더만 보여주는 이미지이며, 병원 상세 페이지는 승인된 색·레이아웃 방향을 기반으로 구현. 실제 병원 사진은 사용하지 않음.

## 승인 및 배포
- [x] G1 요구사항 승인
- [x] G2 디자인 승인
- [x] 브랜치 구현
- [x] Playwright 자동 QA 4/4
- [x] 사용자 G3 배포 승인 — 2026-11-07 17:13 KST
- [x] main 병합 — `6b66d1b9af4c2664ab6a7502ca5b735e5605b332`
- [x] GitHub Pages build/deploy/report 워크플로 성공 — 실행 #42354599119
- [ ] 공개 사이트 HTTP 본문 최신 여부 직접 확인
- [ ] 실제 iPhone Safari 실기기 최종 QA

**배포 작업 성공과 실기기 검증 완료는 별개이다.**
