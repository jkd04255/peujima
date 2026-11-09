"""PJM-014 UI cleanup regression: visible functional UI, not presentation copy.

Uses only synthetic location results. No live reservations, GPS collection or
insurance provider connection. Chromium responsive + mobile WebKit screenshot QA.
"""
from __future__ import annotations

import functools
import http.server
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright
from test_pjm_012 import MOCK_SDK

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa-screenshots"
OUT.mkdir(exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def navigate(page, slug, mobile):
    nav = ".pjm013-bottom-nav" if mobile else ".pjm013-desktop-nav"
    page.locator(f'{nav} [data-act="nav-page"][data-val="{slug}"]').click()
    require(page.evaluate("state.page") == slug, f"route failed: {slug}")

def check_all(page, width, mobile):
    page.goto(page._przima_url, wait_until="load")
    require(page.locator(".hero-pet").count() >= 2, "pet photography lost")
    require(page.locator(".pjm013-home-legacy .hero-v4 h1").inner_text() == "함께하는 모든 날이 건강하기를.", "photo headline changed")
    require(page.locator("#pjm013RegionForm").is_visible(), "home search missing")
    require(page.locator(".pjm013-service-card").count() == 3, "home service actions lost")
    require(page.locator(".pjm013-desktop-nav small").count() == 0, "desktop presentation subtitles remain")
    require(page.locator(".pjm013-page-heading").count() == 0, "intro slide remains on home")

    navigate(page, "nearby", mobile)
    require(page.locator(".pjm013-page-heading").count() == 0, "nearby intro presentation still rendered")
    require(page.locator("h1#pjm013PageTitle.pjm014-sr-only").count() == 1, "nearby screen reader title missing")
    require(page.locator(".nearby-head").count() == 0, "duplicate nearby heading still present")
    require(page.locator("#nearby-hospitals").get_attribute("aria-label") == "주변 동물병원 검색", "accessible nearby landmark missing")
    require(page.locator(".nearby-eyebrow").count() == 0, "nearby English section label remains")
    require(page.locator(".nearby-region-form").is_visible(), "region search missing")
    require(page.locator(".nearby-geo").is_visible(), "GPS search missing")
    require(page.locator("#nearbyKakaoMap").count() == 1, "Kakao map container missing")
    require(page.locator(".nearby-endnote").is_visible(), "real place caution missing")
    require("실제 예약" in page.locator(".nearby-endnote").inner_text(), "booking limitation hidden")
    require("저장하지 않습니다" in page.locator(".nearby-endnote").inner_text(), "location privacy notice hidden")
    if width == 390:
        page.screenshot(path=str(OUT / "pjm-014-390-nearby.png"), full_page=True)

    navigate(page, "clinics", mobile)
    require(page.locator(".pjm013-page-heading").count() == 0, "clinics intro presentation still rendered")
    require(page.locator(".virtual-clinic-notice").is_visible(), "synthetic data caution missing")
    require(page.locator("#specialties").is_visible(), "specialty selection missing")
    require(page.locator(".specialties .section-side").is_visible() is False, "redundant explanatory paragraph remains")
    require(page.locator(".clinic-explore-card").count() == 5, "clinic catalog lost")
    page.locator(".clinic-explore-card").first.click()
    require(page.locator(".clinic-profile-card h2").is_visible(), "clinic detail missing")
    require(page.locator(".clinic-detail-overline").is_visible() is False, "English clinic profile label remains")
    require(page.locator(".clinic-profile-caution").is_visible(), "virtual clinic caution hidden")
    require(page.locator(".clinic-visit-note").is_visible(), "virtual booking caution hidden")
    page.locator(".clinic-reserve-button").click()
    require(page.locator(".cal-date").count() == 7, "calendar not available")
    require(page.locator(".clinic-booking-heading>span").is_visible() is False, "English booking label remains")
    if width == 390:
        page.screenshot(path=str(OUT / "pjm-014-390-clinics.png"), full_page=True)

    navigate(page, "insurance", mobile)
    require(page.locator(".pjm013-page-heading").count() == 0, "insurance intro presentation still rendered")
    require(page.locator("#insurerSelect").is_visible(), "insurance selection missing")
    require(page.locator("#careSelect").is_visible(), "care selection missing")
    require(page.locator(".insurance-intro").is_visible() is False, "redundant insurance introduction remains")
    require(page.locator(".insurance-card .form-head").is_visible() is False, "English pre-check label remains")
    require(page.locator(".insurance-disclaimer").is_visible(), "insurance non-guarantee notice missing")
    require(page.locator(".insurance-button").is_visible(), "insurance evaluation button missing")
    page.locator(".insurance-button").click()
    require(page.locator(".insurance-result").is_visible(), "insurance example result missing")
    if width == 390:
        page.screenshot(path=str(OUT / "pjm-014-390-insurance.png"), full_page=True)

    require(not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"), "horizontal overflow")
    print(f"PASS PJM-014 {width}px: concise pages, live/demo cautions, calendar, insurance")

def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
        functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        origin = f"http://127.0.0.1:{server.server_port}/"
        with sync_playwright() as p:
            for name, browser, sizes in [
                ("Chromium", p.chromium.launch(headless=True, args=["--no-sandbox"]), [320, 390, 768, 1440]),
                ("WebKit", p.webkit.launch(headless=True), [390])
            ]:
                try:
                    for width in sizes:
                        mobile = width <= 850
                        context = browser.new_context(viewport={"width":width,"height":844},
                            locale="ko-KR", reduced_motion="reduce",
                            is_mobile=(name=="WebKit"), has_touch=(name=="WebKit"))
                        page = context.new_page()
                        page._przima_url = origin
                        page.add_init_script("window.PRZIMA_KAKAO_JS_KEY='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'")
                        page.route("**/v2/maps/sdk.js?**", lambda route: route.fulfill(
                            status=200, content_type="application/javascript", body=MOCK_SDK))
                        try:
                            check_all(page, width, mobile)
                        finally:
                            context.close()
                finally:
                    browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print("ALL PJM-014 FUNCTIONAL-FIRST UI QA PASSED")

if __name__ == "__main__":
    main()
