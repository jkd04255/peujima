"""PJM-018: SUIT Variable typography, Korean hierarchy and responsive regression.

Browser assertions use a mock Kakao key, never live GPS/reservation data.
Font-family is verified as a CSS stack; local browsers without internet may
render a fallback, so this is not a guarantee of physical iPhone font loading.
"""
from __future__ import annotations

import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa-screenshots"
OUT.mkdir(exist_ok=True)
FONT_CSS_URL = (
    "https://cdn.jsdelivr.net/gh/sun-typeface/SUIT@2/fonts/variable/woff2/SUIT-Variable.css"
)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


def require(condition, message):
    if not condition: raise AssertionError(message)


def computed(page, selector):
    return page.locator(selector).first.evaluate(
        "(el) => {const s=getComputedStyle(el);return {"
        "family:s.fontFamily,weight:s.fontWeight,spacing:s.letterSpacing,"
        "fontSize:s.fontSize,lineHeight:s.lineHeight}}"
    )


def assert_suit(page, selector, label):
    el = page.locator(selector)
    require(el.count()>0, f"{label}: selector not found: {selector}")
    family = computed(page, selector)["family"]
    require("SUIT Variable" in family, f"{label}: unexpected mixed font: {family}")


def no_overflow(page, name, width):
    require(not page.evaluate(
        "document.documentElement.scrollWidth > innerWidth + 2"),
        f"{name}: horizontal overflow at {width}px"
    )


def run_screen(browser, origin, width, height, name):
    mobile = width <= 850
    context = browser.new_context(
        viewport={"width": width, "height": height},
        locale="ko-KR", reduced_motion="reduce"
    )
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    # Deterministic CSS inspection, without loading a third-party font binary:
    # the production CDN declaration is verified below, not replaced in source.
    page.route("**/SUIT-Variable.css", lambda route: route.fulfill(
        status=200, content_type="text/css", body="/* SUIT external font CSS test stub */"))
    try:
        page.goto(origin, wait_until="load")
        require(page.locator(".pjm013-header").is_visible(), "home header missing")
        require(page.locator(".hero-pet").count()>=2, "original pet photographs missing")
        require(page.locator(".pjm013-service-card").count()==3, "service cards missing")
        require(page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--przima-typeface').includes('SUIT Variable')"), "SUIT typography token missing")
        require(page.evaluate("getComputedStyle(document.documentElement).fontSynthesis") == "none", "synthetic font styles enabled")
        for sel in [
            ".pjm013-header .brand-primary",
            ".pjm013-service-card strong",
            ".pjm013-home-legacy .hero-v4-heading",
            ".pjm013-search-row input",
        ]:
            assert_suit(page, sel, "home")
        nav = ".pjm013-bottom-nav" if mobile else ".pjm013-desktop-nav"
        assert_suit(page, nav+" .pjm013-nav-name", "navigation")
        heading = computed(page, ".pjm013-home-legacy .hero-v4-heading")
        require(heading["spacing"].startswith("-"), "headline tracking no longer adjusted")
        no_overflow(page, "home", width)

        page.goto(origin+"#nearby",wait_until="load")
        require(page.locator(".nearby-geo").is_visible(), "nearby GPS button missing")
        require(page.locator(".nearby-region-form").is_visible(), "nearby region search missing")
        assert_suit(page, ".nearby-geo", "nearby button")
        assert_suit(page, ".nearby-region-form input", "nearby input")
        assert_suit(page, ".nearby-results-title h3", "nearby result heading")
        require("실제 예약" in page.locator(".nearby-endnote").inner_text(),
                "real booking unavailable notice missing")
        no_overflow(page, "nearby", width)

        page.goto(origin+"#clinics",wait_until="load")
        require(page.locator(".clinic-explore-card").count()==5, "synthetic clinic cards missing")
        assert_suit(page, ".clinic-explore-main strong", "clinic card")
        page.locator(".clinic-explore-card").first.click()
        assert_suit(page, ".clinic-profile-body h2", "clinic detail title")
        require(page.locator(".clinic-profile-caution").is_visible(),
                "virtual clinic warning missing")
        no_overflow(page, "clinic detail", width)

        page.goto(origin+"#insurance",wait_until="load")
        assert_suit(page, ".insurance h2", "insurance heading")
        assert_suit(page, ".insurance-card select", "insurance select")
        require(page.locator("#insurerSelect").is_visible(), "insurance dropdown missing")
        require(page.locator(".insurance-disclaimer").is_visible(),
                "insurance guidance disclaimer missing")
        no_overflow(page, "insurance", width)

        if width==390:
            page.screenshot(path=str(OUT/f"pjm-018-{name.lower()}-390-insurance.png"),full_page=True)
        require(not errors, f"{name} {width}px JavaScript errors: {errors}")
        print(f"PASS PJM-018 {name} {width}px: SUIT typography across home/nearby/clinics/insurance, no overflow")
    finally:
        context.close()


def main():
    css=(ROOT/"pjm013-navigation.css").read_text(encoding="utf-8")
    require(css.startswith(f'@import url("{FONT_CSS_URL}");'),
            "official SUIT v2 stylesheet URL must be loaded before other CSS")
    require("OFL" in css and "--przima-typeface" in css,
            "font license or fallback token missing")
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1",0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        origin=f"http://127.0.0.1:{server.server_port}/"
        with sync_playwright() as p:
            chrome=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_screen(chrome,origin,w,h,"Chromium")
                run_screen(webkit,origin,390,844,"WebKit")
            finally:
                chrome.close();webkit.close()
    finally:
        server.shutdown();server.server_close()
    print("PJM-018 TYPOGRAPHY AND RESPONSIVE QA PASSED")


if __name__=="__main__":
    main()
