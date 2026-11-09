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
      name + '</span></button>'
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
        '<div class="pjm013-home-top">' +
          '<div class="pjm013-search-panel">' +
            '<h2 id="pjm013HomeTitle">동물병원 찾기</h2>' +
            '<form id="pjm013RegionForm" class="pjm013-search-form" role="search">' +
              '<label for="pjm013RegionInput">지역 검색</label>' +
              '<div class="pjm013-search-row">' + search +
                '<input id="pjm013RegionInput" type="search" maxlength="80" placeholder="지역명 또는 역 이름 · 예: 수원역" autocomplete="off" />' +
                '<button type="submit" aria-label="입력한 지역으로 실제 동물병원 검색">' + arrow + '</button>' +
              '</div>' +
            '</form>' +
            '<button type="button" class="pjm013-locate" data-act="nav-nearby-locate">' + pin + ' 내 위치로 찾기 ' + arrow + '</button>' +
            '<p class="pjm013-panel-note">카카오맵 실제 병원 정보 · 위치는 버튼을 누를 때만 확인합니다.</p>' +
          '</div>' +
        '</div>' +
        '<div class="pjm013-home-services" aria-label="서비스 바로가기">' +
          '<button class="pjm013-service-card is-real" type="button" data-act="nav-page" data-val="nearby">' +
            '<span class="pjm013-card-num">실제 병원</span><span class="pjm013-card-arrow">' + arrow + '</span>' +
            '<strong>병원 찾기</strong><span>지도·거리순 검색</span></button>' +
          '<button class="pjm013-service-card is-demo" type="button" data-act="nav-page" data-val="clinics">' +
            '<span class="pjm013-card-num">가상 체험</span><span class="pjm013-card-arrow">' + arrow + '</span>' +
            '<strong>예약 체험</strong><span>진료과·날짜 선택</span></button>' +
          '<button class="pjm013-service-card is-guide" type="button" data-act="nav-page" data-val="insurance">' +
            '<span class="pjm013-card-num">정보 안내</span><span class="pjm013-card-arrow">' + arrow + '</span>' +
            '<strong>펫보험</strong><span>보장 조건 확인</span></button>' +
        '</div>' +
        '<div class="pjm013-condition-row">' +
          '<h2>진료 분야 <span>가상 체험</span></h2>' +
          '<div class="pjm013-condition-chips" aria-label="가상 병원 진료과 선택">' +
            [["내과","내과"],["외과·정형","외과·정형"],["피부·알레르기","피부·알레르기"],["치과","치과"]].map(([key,label]) =>
              '<button type="button" data-act="nav-specialty" data-val="' + key + '">' + label + arrow + '</button>'
            ).join("") +
          '</div>' +
        '</div>' +
      '</div></section>';
  }
  // PJM-014: no slide-like introductory sections. Keep one screen-reader
  // heading per route; all visible content begins with the actual tool.
  const accessiblePageTitles = {
    nearby: "주변 동물병원",
    clinics: "진료과·예약 체험",
    insurance: "펫보험 안내"
  };
  function pageHeading(page) {
    const title = accessiblePageTitles[page];
    return title ? '<h1 id="pjm013PageTitle" class="pjm014-sr-only" tabindex="-1">' + title + '</h1>' : "";
  }
  window.PJM013 = {pages, route, header, bottom, home, pageHeading};
})();
