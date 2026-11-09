# PJM-012 · G3 HOLD · 배포 없는 실제 iPhone Safari 사전 QA

2026-11-09 · **G3 보류, PR #7 Draft, 공개/스테이징 배포 금지.**

## 목적과 안전 조건

개인 Windows 11 PC와 iPhone을 **같은 신뢰할 수 있는 Wi-Fi**에 연결하고 PC의 사설 IP에서 HTTPS 서버를 실행합니다. 인터넷에 공개하거나 터널·포트 포워딩을 사용하지 않습니다.

- PC의 명시적 사설 IPv4에만 서버 바인딩. 0.0.0.0, 공인 IP, 127.0.0.1 등은 실제 실행 시 거부.
- 서버 실행마다 생성되는 임시 토큰 경로 외 요청은 404. HTML, 주변병원 JS/CSS만 제공. 인증서·키·프로젝트 내부 파일은 제공하지 않음.
- Kakao **JavaScript 키만** 터미널에 숨김 입력. 로컬 서버 RAM에만 유지하고 키·GPS·접속 IP·토큰을 로그/파일/PR에 기록하지 않음. **REST/Admin 키 입력 금지.**
- 키는 지도 SDK 사용을 위해 iPhone에 제공되는 HTML에서 확인 가능한 웹용 공개 키입니다. 카카오 SDK 도메인 제한을 유지하세요.
- GPS를 사용자가 허용한 경우 좌표는 **카카오 장소 검색 API에 전송**됩니다. 프지마 서버에는 저장되지 않지만 카카오 정책이 적용됩니다.
- **mkcert 루트 CA를 iPhone에서 일시적으로 신뢰**해야 HTTPS 위치 API를 사용할 수 있습니다. 직접 소유한 PC의 공개 루트 인증서만 설치하고 시험이 끝나면 프로파일/신뢰를 제거합니다. rootCA-key.pem 절대 공유 금지.

## 준비

- Windows 11 / Python 3 / Git, 사유 Wi-Fi, iPhone Safari.
- 카카오 개발자에서 발급받은 **JavaScript 키** (대화에 보내지 않음).
- 기숙사/학교/게스트 Wi-Fi의 클라이언트 격리 설정 때문에 기기 간 접속이 안 될 수 있음. 개인 공유기 권장.
- 서버 가동 중 Windows 방화벽은 **개인 네트워크만 허용**, 공용 네트워크·포트포워딩 금지.

## 1. 기능 브랜치 내려받기 (Windows PowerShell)

~~~powershell
git clone --single-branch --branch feature/pjm-012-kakao-nearby https://github.com/jkd04255/peujima.git
cd peujima
py --version
~~~

이미 Git 저장소를 가지고 있다면 현재 변경내용을 보존하고 별도 폴더로 clone합니다.

## 2. PC의 Wi-Fi IPv4 확인

~~~powershell
ipconfig
~~~

Wi-Fi 어댑터의 IPv4 주소를 확인합니다. 예시는 **192.168.0.23**이지만 실제 주소를 넣어야 합니다. 10.x.x.x, 172.16–31.x.x, 192.168.x.x 사설 IP만 지원합니다.

## 3. PC 개발용 HTTPS 인증서 생성

~~~powershell
winget install -e --id FiloSottile.mkcert
mkcert -install
mkcert -cert-file .local-qa-cert.pem -key-file .local-qa-key.pem 192.168.0.23
mkcert -CAROOT
~~~

192.168.0.23을 실제 IP로 변경하세요. 인증서 발급에는 본인의 Windows 관리자 권한이 필요할 수 있습니다.

**중요:** mkcert -CAROOT 폴더의 **rootCA.pem만** iPhone으로 전달합니다. **rootCA-key.pem**은 절대 전송하지 마세요. .local-qa-key.pem도 개인키이므로 다른 기기로 보내거나 Git에 올리지 마세요. 이 파일들은 .gitignore에서 제외합니다.

mkcert 공식: https://github.com/FiloSottile/mkcert

## 4. iPhone에 공개 루트 CA 임시 설치

1. PC의 mkcert -CAROOT 폴더에 있는 **rootCA.pem만** 개인 iPhone으로 전달합니다.
2. iPhone에서 파일을 열어 인증서 프로파일 설치 안내를 따릅니다. **설정 → 일반 → VPN 및 기기 관리**에서 설치합니다.
3. **설정 → 일반 → 정보 → 인증서 신뢰 설정**에서 해당 인증서에 대해 전체 신뢰를 활성화합니다.
4. 신뢰 경고를 우회하여 진행하지 마세요. 테스트를 마치면 이 설정을 해제하고 테스트용 프로파일을 제거합니다.

Apple 공식 안내: https://support.apple.com/ko-kr/102390

## 5. 카카오 JavaScript SDK에 사설 IP 임시 등록

https://developers.kakao.com/console/app → 프지마 → **앱 → 플랫폼 키 → JavaScript 키 → JavaScript SDK 도메인**에 다음 값을 추가합니다.

~~~text
https://192.168.0.23:8443
~~~

실제 IP로 바꾸세요. 콘솔에서 포트 포함 형식을 허용하지 않으면 포트를 제외한 **https://192.168.0.23**으로 등록하고 실제 SDK 인증 여부를 확인합니다. 기존 GitHub Pages/localhost 도메인은 그대로 둡니다.

공식 데브톡의 사설 IP 설정 사례:
- https://devtalk.kakao.com/t/pwa-sdk/133158
- https://devtalk.kakao.com/t/topic/147528

## 6. 로컬 HTTPS 서버 실행

저장소 루트 PowerShell에서:

~~~powershell
py scripts/ios_safari_lan.py --host 192.168.0.23 --port 8443 --cert .local-qa-cert.pem --key .local-qa-key.pem
~~~

IP를 변경하세요. 터미널에 **Kakao JavaScript 키를 입력**하라는 메시지가 나타나면 붙여넣고 Enter. 키가 화면에 표시되거나 파일에 저장되지 않습니다.

서버가 다음 형식의 **임시 접속 URL**을 출력합니다.

~~~text
https://192.168.0.23:8443/t/임시무작위토큰/
~~~

PC와 동일 Wi-Fi에 연결된 iPhone Safari의 주소창에 해당 URL을 직접 입력합니다. **토큰·키·실제 좌표가 포함된 화면을 타인에게 보내지 마세요.**

서버를 중단하려면 PC 터미널에서 **Ctrl+C**. URL 토큰은 다음 실행 때 변경됩니다. 이 단계에는 GitHub Pages 설정 변경·PR 병합·배포가 전혀 없습니다.

## 7. 실제 iPhone Safari QA 체크리스트

**첫 화면**
- [ ] 사설 IP의 HTTPS URL이 인증서 경고 없이 정상적으로 열림
- [ ] 기존 프지마 사진·브랜드·강아지/고양이/전체 모드 유지
- [ ] 사이트 진입만으로 GPS 권한 요청이 나타나지 않음
- [ ] JavaScript 키 입력칸이 보이지 않음

**GPS 허용**
- [ ] 내 위치로 동물병원 찾기 버튼을 눌렀을 때만 위치 권한 요청
- [ ] 허용 후 주변 실제 동물병원 목록과 지도 마커 표시
- [ ] 1/3/5km 반경 변경, 거리순 목록 갱신
- [ ] 마커 터치 시 목록 탐색 가능, 상세링크/전화 버튼 반응

**GPS 거부·지역 검색**
- [ ] 위치 권한 거부 시 정상 오류 안내 + 수동 지역 검색 가능
- [ ] 수원역 등 지역명 검색 시 실제 결과 표시
- [ ] 키보드 입력 중 비의도적 자동 확대 없음
- [ ] 세로/가로 전환·지도 드래그·스크롤 중 가로 넘침 없음

**기존 기능**
- [ ] 실제 병원 검색 결과에 예약 체험 버튼 없음
- [ ] 가상 병원 5곳 → 상세 → 7일 캘린더/의료진/시간 선택 → 가상 예약 완료 → 보험 안내 유지
- [ ] 실제 장소 데이터와 가상 예약이 혼동되지 않음

**결과 기록**
- 항목별 PASS/FAIL/미확인만 PR에 기재. 실제 위치 좌표·실주소·URL 토큰·키는 기록하지 않음.
- 스크린샷 공유 시 Safari 주소창/토큰/실사용자의 위치를 가림.
- 사용자가 직접 시험한 결과를 확인하기 전까지 **iPhone Safari 실기기 QA는 미확인 상태**.

## 8. 안전하게 종료

1. Ctrl+C로 PC HTTPS 서버 종료.
2. 카카오 JS SDK 도메인 목록에서 **추가한 사설 IP만 제거**. 기존 GitHub Pages/localhost 값은 보존.
3. iPhone에서 **설정 → 일반 → 정보 → 인증서 신뢰 설정**의 테스트 CA 신뢰 해제, **설정 → 일반 → VPN 및 기기 관리**에서 프로파일 삭제.
4. PC의 .local-qa-cert.pem / .local-qa-key.pem 삭제. mkcert의 다른 CA 파일은 임의 삭제하지 않음.
5. Windows 방화벽에 별도 8443 규칙을 만들었다면 삭제.
6. **G3 HOLD, main·Pages 미변경 유지**.

## 오류별 대응

| 현상 | 원인 후보와 대처 |
| --- | --- |
| iPhone 연결 불가 | 서로 다른 Wi-Fi, 사설 IP 변경, AP 격리, 방화벽. 공용 네트워크 방화벽 무력화 금지 |
| 인증서 경고 | 발급 IP 불일치, 루트 CA 미설치/미신뢰. 경고 무시하지 말고 인증서 재확인 |
| 위치 권한 미표시 | HTTPS 신뢰·Safari 위치 서비스 설정 확인 |
| Kakao SDK 오류 | JavaScript 키 하위 SDK 도메인에 정확한 사설 IP가 등록됐는지 확인 |
| 지도만 비어 있음 | Kakao 응답/쿼터/네트워크. 실제 장소를 임의 생성하지 않음 |

참고:
- https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API
- https://support.apple.com/ko-kr/102390

**상태: 로컬 테스트 준비 문서. 아직 실제 iPhone Safari에서 실행·검증하지 않았음.**
