"""PJM-012 WebKit + touch/mobile viewport QA using auto-key release build (MOCK SDK).

WebKit on Linux is a Safari-engine approximation, NOT a real iPhone Safari test.
All locations, place names, and Kakao responses in this test are synthetic.
"""
from __future__ import annotations
import functools
import http.server
from pathlib import Path
import sys
import tempfile
import threading
from playwright.sync_api import sync_playwright
from test_pjm_012 import MOCK_SDK

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_pages import build_site


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def check(cond,msg):
    if not cond:raise AssertionError(msg)


def run_device(browser,device,origin,name):
    context=browser.new_context(
        **device,locale="ko-KR",timezone_id="Asia/Seoul",
        geolocation={"latitude":37.5,"longitude":127.0},
        permissions=["geolocation"],reduced_motion="reduce",
    )
    page=context.new_page()
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.route("**/v2/maps/sdk.js?**",lambda route:route.fulfill(status=200,content_type="application/javascript",body=MOCK_SDK))
    try:
        page.goto(origin+"#nearby",wait_until="domcontentloaded")
        page.locator("#nearbyRegionForm").wait_for()
        check(page.evaluate("Boolean(window.PRZIMA_KAKAO_JS_KEY)"),f"{name}: runtime JS key not injected")
        check(page.locator("#nearbyKeyForm").count()==0,f"{name}: unexpected developer key field")
        check(page.locator(".nearby-place").count()==0,f"{name}: unexpected place list before user action")
        check(page.locator(".clinic-explore-card").count()==0,f"{name}: demo bookings leaked into live search")
        page.locator('.pjm013-bottom-nav [data-act="nav-page"][data-val="clinics"]').tap()
        check(page.locator(".clinic-explore-card").count()==5,f"{name}: synthetic booking clinics lost")
        page.locator('.pjm013-bottom-nav [data-act="nav-page"][data-val="nearby"]').tap()

        page.locator('[data-act="nearby-locate"]').tap()
        page.locator(".nearby-place").first.wait_for(timeout=10000)
        check(page.locator(".nearby-place").count()==2,f"{name}: wrong Kakao mock clinic count")
        check(page.locator(".nearby-place").first.locator("b").inner_text()=="가까운 동물병원",f"{name}: unsorted distance")
        check(page.evaluate("window.__mapInstances")>=1,f"{name}: map missing")
        check(not page.evaluate("document.documentElement.scrollWidth > window.innerWidth+2"),f"{name}: horizontal overflow")
        page.locator("#nearbyRadius").select_option("1000")
        page.locator(".nearby-place").first.wait_for()
        check(page.evaluate("window.__kakaoCalls.filter(x=>x.keyword==='동물병원').at(-1).options.radius")==1000,
              f"{name}: radius did not update")
        page.locator("#nearbyRegionInput").fill("수원역")
        check(page.evaluate("getComputedStyle(document.querySelector('#nearbyRegionInput')).fontSize")=="16px" or device["viewport"]["width"]>620,
              f"{name}: iOS keyboard may auto-zoom due to input font smaller than 16px")
        page.locator("#nearbyRegionForm button").tap()
        page.locator(".nearby-place").first.wait_for()
        check("수원역 기준" in page.locator(".nearby-status").inner_text(),f"{name}: typed region search failed")
        check(not errors,f"{name}: JS errors {errors}")
        print(f"PASS WebKit {name}: auto key, touch GPS, mocked markers, radius, region, responsive layout")
    finally:context.close()


def denied(browser,device,origin):
    context=browser.new_context(**device,reduced_motion="reduce")
    page=context.new_page()
    page.add_init_script("""
      Object.defineProperty(navigator,'geolocation',{configurable:true,
        value:{getCurrentPosition(ok,err){err({code:1})}}});
    """)
    try:
        page.goto(origin+"#nearby",wait_until="domcontentloaded")
        page.locator('[data-act="nearby-locate"]').tap()
        check("거부" in page.locator(".nearby-status").inner_text(),"WebKit: geolocation denial fallback broken")
        check(page.locator("#nearbyRegionInput").is_visible(),"WebKit: manual region fallback missing")
        print("PASS WebKit: denied location still offers manual region search")
    finally:context.close()


def main():
    with tempfile.TemporaryDirectory(prefix="przima-webkit-") as tmp:
        dist=Path(tmp)/"site"
        build_site(dist,"a"*32)
        server=http.server.ThreadingHTTPServer(
            ("127.0.0.1",0),functools.partial(QuietHandler,directory=str(dist))
        )
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            origin=f"http://127.0.0.1:{server.server_address[1]}/"
            with sync_playwright() as p:
                browser=p.webkit.launch(headless=True)
                try:
                    run_device(browser,p.devices["iPhone 13"],origin,"iPhone 13 viewport")
                    run_device(browser,p.devices["iPad (gen 7)"],origin,"iPad viewport")
                    denied(browser,p.devices["iPhone 13"],origin)
                finally:browser.close()
        finally:server.shutdown();server.server_close()
    print("ALL PJM-012 WebKit APPROXIMATION QA PASSED (not physical iOS Safari)")


if __name__=="__main__":main()
