"""PJM-016: map marker must visibly identify the exact selected hospital.

Synthetic Kakao SDK only. Chromium and WebKit, no live API or user locations.
"""
from __future__ import annotations

import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from test_pjm_012 import MOCK_SDK

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa-screenshots"
OUT.mkdir(exist_ok=True)

# Extend the established mock to expose registered Kakao marker click callbacks.
# This tests the real PJM012.paint() marker listener, not a substitute UI path.
MOCK_CLICKABLE = MOCK_SDK.replace(
    "function Marker(opts){this.options=opts;}",
    "function Marker(opts){this.options=opts;(window.__testMarkers ||= []).push(this);}"
).replace(
    "event:{addListener:function(){}}",
    "event:{addListener:function(marker,type,callback){if(type==='click')marker.__click=callback;}}"
)
assert MOCK_CLICKABLE != MOCK_SDK
assert "__testMarkers" in MOCK_CLICKABLE and "marker.__click" in MOCK_CLICKABLE


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


def must(condition, message):
    if not condition:
        raise AssertionError(message)


def run_case(browser, origin, width, height, name):
    context = browser.new_context(
        viewport={"width": width, "height": height}, locale="ko-KR",
        reduced_motion="reduce", geolocation={"latitude":37.5,"longitude":127.0},
        permissions=["geolocation"], is_mobile=(name=="WebKit"), has_touch=(name=="WebKit"),
    )
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.add_init_script("window.PRZIMA_KAKAO_JS_KEY='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'")
    page.route("**/v2/maps/sdk.js?**", lambda route: route.fulfill(
        status=200, content_type="application/javascript", body=MOCK_CLICKABLE))
    try:
        page.goto(origin + "#nearby", wait_until="load")
        count_status=page.locator("#nearby-hospitals .nearby-results-title [role='status']")
        must(count_status.count()==1 and count_status.get_attribute("aria-live")=="polite" and
             count_status.get_attribute("aria-atomic")=="true",
             "result count should be announced politely and as one complete message")
        must(page.locator("#nearby-hospitals .nearby-results").get_attribute("aria-live") is None,
             "screen reader should not announce every hospital card as a live update")
        page.locator(".nearby-geo").click()
        page.locator(".nearby-place").first.wait_for(timeout=10000)
        must(count_status.inner_text()=="2곳 · 가까운 순",
             "result count announcement missing or stale")
        must(page.locator(".nearby-place").count()==2, "two synthetic hospitals not rendered")
        must(page.evaluate("window.__testMarkers?.length")==2, "two clickable markers not created")
        must(page.locator(".nearby-place.is-selected").count()==0, "premature selection before marker click")
        must(page.locator(".nearby-place-selected").count()==0, "visible selection-label markup should be removed completely")
        # Results are sorted by distance; first marker belongs to id=1001.
        page.evaluate("window.__testMarkers[0].__click()")
        selected = page.locator('.nearby-place[data-place-id="1001"]')
        must(selected.get_attribute("class").find("is-selected")!=-1, "first marker did not select first hospital")
        must(selected.locator(".nearby-place-selected").count()==0, "selection text badge should not render")
        must("선택한 병원" in selected.get_attribute("aria-label"), "accessibility label lacks selection")
        must(page.evaluate("document.activeElement?.dataset.placeId")== "1001", "selection did not focus result")
        must(page.locator(".nearby-place.is-selected").count()==1, "multiple selected cards")
        must(page.locator(".nearby-place-selected").count()==0, "text badge unexpectedly rendered")
        must(page.evaluate("""() => getComputedStyle(document.querySelector('.nearby-place.is-selected')).outlineStyle""") == "solid",
             "selected card missing strong highlight outline")
        if width==390:
            page.screenshot(path=str(OUT / f"pjm-016-{name.lower()}-390-selected.png"), full_page=True)

        page.evaluate("window.__testMarkers[1].__click()")
        second=page.locator('.nearby-place[data-place-id="1002"]')
        must(second.locator(".nearby-place-selected").count()==0, "second selected card must also have no text badge")
        must(second.get_attribute("class").find("is-selected")!=-1, "second clicked marker not highlighted")
        must(page.locator('.nearby-place[data-place-id="1001"].is-selected').count()==0, "old card remains selected")
        must(page.locator(".nearby-place.is-selected").count()==1, "selection not exclusive")
        must(page.evaluate("document.activeElement?.dataset.placeId")=="1002", "second selection not focused")
        must(page.locator(".nearby-place [href^='https://place.map.kakao.com/']").count()==2,
             "Kakao detail links lost")

        page.locator("#nearbyRegionInput").fill("수원역")
        page.locator("#nearbyRegionForm button").click()
        page.locator(".nearby-place").first.wait_for(timeout=10000)
        must(page.locator(".nearby-place.is-selected").count()==0, "stale highlight after region search")
        must(page.locator(".nearby-place-selected").count()==0, "selection badge should remain removed after searching")
        must(not page.evaluate("document.documentElement.scrollWidth > window.innerWidth+2"),
             "horizontal overflow on selected-card layout")
        must(not errors, f"JavaScript page errors: {errors}")
        print(f"PASS PJM-017 {name} {width}px: marker click, badge-free outline, focus, exclusive selection, reset")
    finally:
        context.close()


def main():
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),
        functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        origin=f"http://127.0.0.1:{server.server_port}/"
        with sync_playwright() as p:
            chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                run_case(chromium,origin,320,700,"Chromium")
                run_case(chromium,origin,390,844,"Chromium")
                run_case(chromium,origin,1440,900,"Chromium")
                run_case(webkit,origin,390,844,"WebKit")
            finally:
                chromium.close()
                webkit.close()
    finally:
        server.shutdown()
        server.server_close()
    print("PJM-017 BADGE-FREE MARKER SELECTION QA PASSED (mock Kakao, no physical iPhone)")

if __name__=="__main__":
    main()
