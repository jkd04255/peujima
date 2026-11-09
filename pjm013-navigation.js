/* PJM-013 — navigation & service architecture
 * The editorial pet photography and existing PJM-012 Kakao / PJM-011 booking
 * features are preserved; this layer controls WHERE each service lives.
 * No server, login, paid API, external dependency, or user-data persistence.
 */
(function () {
  "use strict";
  const pages = ["home", "nearby", "clinics", "insurance"];
  const route = () => {
    const page = decodeURIComponent((window.location.hash || "").replace(/^#/, ""));
    return pages.includes(page) ? page : "home";
  };
  const arrow = '<svg width="19" height="19" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>';
  const pin = '<svg width="19" height="19" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 21s7-6.3 7-11a7 7 0 1 0-14 0c0 4.7 7 11 7 11Z"/><circle cx="12" cy="10" r="2.4"/></svg>';
  const search = '<svg width="19" height="19" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="10.5" cy="10.5" r="7"/><path d="m16 16 5 5"/></svg>';
  const calendar = '<svg width="19" height="19" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18"/></svg>';
  const shield = '<svg width="19" height="19" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/></svg>';
  const homeIcon = '<svg width="19" height="19" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><path d="m3 11 9-8 9 8v10H3V11Z"/><path d="M9 21v-7h6v7"/></svg>';
  const entries = [
    ["home", "홈", "처음으로", homeIcon],
    ["nearby", "병원 찾기", "실제 장소", pin],
    ["clinics", "진료과·예약", "가상 체험", calendar],
    ["insurance", "펫보험", "안내", shield]
  ];
  function links(current, mobile = false) {
    return entries.map(([key, name, sub, ic]) =>
      '<button type="button" data-act="nav-page" data-val="' + key + '"' +
      ' class="pjm013-nav-item' + (current === key ? ' is-current' : '') + '"' +
      ' aria-current="' + (current === key ? 'page' : 'false') + '">' +
      '<span class="pjm013-nav-icon">' + ic + '</span><span class="pjm013-nav-name">' +
      name + '</span>' + (!mobile ? '<small>' + sub + '</small>' : '') + '</button>'
    ).join("");
  }
  function modeSwitch(mode) {
    return '<div class="pjm013-mode-switch" role="group" aria-label="반려동물 종류 선택">' +
      [["all","전체"],["dog","강아지"],["cat","고양이"]].map(([key,label]) =>
        '<button type="button" data-act="mode" data-val="' + key +
        '" aria-pressed="' + (mode === key) + '"' + (mode === key ? ' class="is-selected"' : '') +
        '>' + label + '</button>').join("") + '</div>';
  }
  function header(brand, state) {
    return '<a href="#main-content" class="pjm013-skip">본문으로 건너뛰기</a>' +
      '<header class="header header-v4 pjm013-header"><div class="site-width pjm013-header-grid">' +
      '<div class="pjm013-brand">' + brand + '</div>' +
      '<nav class="pjm013-desktop-nav" aria-label="주요 서비스">' + links(state.page) + '</nav>' +
      modeSwitch(state.mode) + '</div></header>';
  }
  function bottom(page) {
    return '<nav class="pjm013-bottom-nav" aria-label="모바일 주요 서비스">' + links(page, true) + '</nav>';
  }
  function home() {
    return '<section class="pjm013-home" aria-labelledby="pjm013HomeTitle">' +
      '<div class="site-width">' +
        '<div class="pjm013-home-top"><div class="pjm013-home-title">' +
          '<span class="pjm013-eyebrow"><span class="pjm013-dot"></span> FIND THE RIGHT CARE</span>' +
          '<h1 id="pjm013HomeTitle">우리 아이의 오늘,<br><em>어디서부터 알아볼까요?</em></h1>' +
          '<p>가까운 병원을 찾고, 진료 분야를 살펴보고,<br class="pjm013-desktop-only"> 예약 과정과 보험 조건까지 차근차근 알아보세요.</p>' +
        '</div>' +
        '<div class="pjm013-search-panel">' +
          '<div class="pjm013-panel-heading"><span>01 / REAL LOCATION</span><strong>먼저, 가까운 병원부터.</strong></div>' +
          '<form id="pjm013RegionForm" class="pjm013-search-form" role="search">' +
            '<label for="pjm013RegionInput">찾고 싶은 지역을 입력해 주세요</label>' +
            '<div class="pjm013-search-row">' + search +
              '<input id="pjm013RegionInput" type="search" maxlength="80" placeholder="지역명 또는 역 이름 · 예: 수원역" autocomplete="off" />' +
              '<button type="submit" aria-label="입력한 지역으로 실제 동물병원 검색">' + arrow + '</button>' +
            '</div>' +
          '</form>' +
          '<button type="button" class="pjm013-locate" data-act="nav-nearby-locate">' + pin + ' 내 위치로 가까운 병원 찾기 ' + arrow + '</button>' +
          '<p class="pjm013-panel-note">카카오맵에 등록된 실제 장소를 검색합니다. 위치는 버튼을 누른 뒤에만 요청합니다.</p>' +
        '</div></div>' +
        '<div class="pjm013-home-divider"><span>OUR SERVICES</span><span>필요한 서비스로 바로 이동하세요.</span></div>' +
        '<div class="pjm013-home-services">' +
          '<button class="pjm013-service-card is-real" type="button" data-act="nav-page" data-val="nearby">' +
            '<span class="pjm013-card-num">01 / 실제 장소</span><span class="pjm013-card-arrow">' + arrow + '</span>' +
            '<strong>내 주변<br>동물병원 찾기</strong><span>위치 또는 지역 검색 · 지도와 거리순 목록</span>' +
            '<span class="pjm013-card-foot">병원 찾기 →</span></button>' +
          '<button class="pjm013-service-card is-demo" type="button" data-act="nav-page" data-val="clinics">' +
            '<span class="pjm013-card-num">02 / 체험 전용</span><span class="pjm013-card-arrow">' + arrow + '</span>' +
            '<strong>진료과부터<br>예약 과정까지</strong><span>증상별 진료 분야 · 7일 예약 시연</span>' +
            '<span class="pjm013-card-foot">가상 예약 체험 →</span></button>' +
          '<button class="pjm013-service-card is-guide" type="button" data-act="nav-page" data-val="insurance">' +
            '<span class="pjm013-card-num">03 / 정보 안내</span><span class="pjm013-card-arrow">' + arrow + '</span>' +
            '<strong>펫보험,<br>가기 전에 확인</strong><span>상품별 확인 항목 · 보장 조건 안내</span>' +
            '<span class="pjm013-card-foot">보험 안내 →</span></button>' +
        '</div>' +
        '<div class="pjm013-condition-row"><div><span class="pjm013-eyebrow">DISCOVER BY CARE</span>' +
          '<h2>어떤 진료가 필요하신가요?</h2></div>' +
          '<div class="pjm013-condition-chips">' +
            [["내과","내과"],["외과·정형","외과·정형"],["피부·알레르기","피부·알레르기"],["치과","치과"]].map(([key,label]) =>
              '<button type="button" data-act="nav-specialty" data-val="' + key + '">' + label + arrow + '</button>'
            ).join("") +
          '</div>' +
          '<p>진료 분야별 병원·예약 정보는 현재 가상 데이터로 체험할 수 있습니다.</p>' +
        '</div>' +
      '</div></section>';
  }
  const headings = {
    nearby: ["FIND / 01", "주변 동물병원", "정말 가까운 병원부터 찾아보세요.", "카카오맵 실제 장소 정보 · 이 페이지에서 예약하지 않습니다."],
    clinics: ["EXPLORE / 02", "진료과·예약 체험", "필요한 진료부터, 예약 과정까지.", "가상 병원 5곳의 시연용 정보이며 실제 예약은 접수되지 않습니다."],
    insurance: ["GUIDE / 03", "펫보험 안내", "진료 전에 챙겨볼 보장 조건.", "참고용 조건 안내이며 실제 지급 여부를 보장하지 않습니다."]
  };
  function pageHeading(page) {
    const h = headings[page];
    if (!h) return "";
    return '<section class="pjm013-page-heading" aria-labelledby="pjm013PageTitle"><div class="site-width">' +
      '<span class="pjm013-eyebrow"><span class="pjm013-dot"></span> ' + h[0] + '</span>' +
      '<h1 id="pjm013PageTitle" tabindex="-1">' + h[1] + '</h1><p>' + h[2] + '</p>' +
      '<span class="pjm013-heading-disclosure">' + h[3] + '</span>' +
      '</div></section>';
  }
  window.PJM013 = {pages, route, header, bottom, home, pageHeading};
})();
