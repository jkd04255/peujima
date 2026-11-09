"""PJM-013: service IA/browser navigation regression (synthetic locations only).

Validates home -> real nearby -> demo appointment -> insurance, hash history,
direct links, category shortcuts, mobile bottom tabs, actual-service disclosures,
home region search, photo preservation, keyboard and responsive overflow.
"""
from __future__ import annotations
import functools
import http.server
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from test_pjm_012 import MOCK_SDK

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-screenshots"
OUT.mkdir(exist_ok=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def check(ok,msg):
    if not ok:raise AssertionError(msg)

def tab(page,name,mobile):
    selector=(".pjm013-bottom-nav " if mobile else ".pjm013-desktop-nav ")+f'[data-act="nav-page"][data-val="{name}"]'
    page.locator(selector).click()

def check_page(page,slug):
    check(page.evaluate("state.page")==slug,f"wrong page state: expected {slug}")
    check(page.evaluate("location.hash")=="#"+slug,f"wrong route URL: {slug}")
    check(page.locator(".pjm013-page--"+slug).count()==1,f"no main for {slug}")
    check(page.locator(".pjm013-page--"+slug+" .pjm013-page-heading").count()==(slug!="home"),"page heading mismatch")

def verify(browser,origin,width,height):
    mobile=width<=850
    context=browser.new_context(
        viewport={"width":width,"height":height},locale="ko-KR",
        timezone_id="Asia/Seoul",reduced_motion="reduce",
        geolocation={"latitude":37.5,"longitude":127.0},permissions=["geolocation"]
    )
    page=context.new_page()
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.add_init_script("window.PRZIMA_KAKAO_JS_KEY='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'")
    page.route("**/v2/maps/sdk.js?**",lambda route:route.fulfill(
        status=200,content_type="application/javascript",body=MOCK_SDK))
    try:
        page.goto(origin,wait_until="load")
        check(page.locator(".pjm013-home h1").count()==1,f"{width}: no hub headline")
        check(page.locator("#pjm013RegionForm").is_visible(),f"{width}: primary search missing")
        check(page.locator(".pjm013-home-services .pjm013-service-card").count()==3,f"{width}: service choices missing")
        check(page.locator(".hero-pet").count()>=2,f"{width}: pet images lost")
        check(page.locator(".nearby-geo").count()==0,f"{width}: nearby should be its own page")
        check(page.locator(".clinic-explore-card").count()==0,f"{width}: demo clinics leaked into homepage")
        check(page.locator('[data-act="nav-page"][data-val="home"][aria-current="page"]').count()==2,
              f"{width}: nav active indicator missing")
        check(page.evaluate("window.__kakaoCalls===undefined"),f"{width}: SDK loaded before user request")
        check(page.locator(".pjm013-bottom-nav").is_visible()==mobile,f"{width}: mobile nav visibility")
        check(not page.evaluate("document.documentElement.scrollWidth>window.innerWidth+2"),f"{width}: home overflow")
        page.evaluate("window.scrollTo(0, 700)")
        check(abs(page.evaluate("document.querySelector('.pjm013-header').getBoundingClientRect().top"))<3,
              f"{width}: sticky service header is not retained on scroll")
        if mobile:
            check(page.evaluate("document.querySelector('.pjm013-bottom-nav').getBoundingClientRect().bottom <= window.innerHeight + 1"),
                  f"{width}: persistent bottom tab bar not at viewport foot")
        page.evaluate("window.scrollTo(0, 0)")
        if width==390:page.screenshot(path=str(OUT/"pjm-013-390-home.png"),full_page=True)

        tab(page,"nearby",mobile)
        check_page(page,"nearby")
        check(page.locator("#nearbyTitle").is_visible(),f"{width}: nearby screen missing")
        check(page.locator(".clinic-explore-card").count()==0,f"{width}: live and demo mixed")

        tab(page,"clinics",mobile)
        check_page(page,"clinics")
        check(page.locator(".clinic-explore-card").count()==5,f"{width}: demo booking catalog missing")
        check("가상" in page.locator(".virtual-clinic-notice").inner_text(),f"{width}: demo warning missing")
        check(page.locator("#specialties").count()==1,f"{width}: specialty grid absent")
        if width==390:page.screenshot(path=str(OUT/"pjm-013-390-clinics.png"),full_page=True)

        tab(page,"insurance",mobile)
        check_page(page,"insurance")
        check(page.locator("#insurerSelect").is_visible(),f"{width}: insurance tool not available")
        page.go_back(wait_until="domcontentloaded")
        check_page(page,"clinics")
        page.go_back(wait_until="domcontentloaded")
        check_page(page,"nearby")
        tab(page,"home",mobile)
        check_page(page,"home")
        page.locator("#pjm013RegionInput").fill("수원역")
        page.locator("#pjm013RegionForm button").click()
        check_page(page,"nearby")
        page.locator(".nearby-place").first.wait_for(timeout=10000)
        check("수원역 기준" in page.locator(".nearby-status").inner_text(),
              f"{width}: home region search did not open real Kakao search")
        check(page.locator(".nearby-place").count()==2,f"{width}: home region search wrong places")
        check(page.locator(".nearby-place [data-act='clinic-reserve']").count()==0,
              f"{width}: real listing must never offer mock booking")
        if width==390:page.screenshot(path=str(OUT/"pjm-013-390-nearby-mock.png"),full_page=True)

        tab(page,"home",mobile)
        page.locator('[data-act="nav-specialty"][data-val="내과"]').click()
        check_page(page,"clinics")
        check(page.locator("#specialtySelect").input_value()=="내과",f"{width}: specialty shortcut lost")
        check(not page.evaluate("document.documentElement.scrollWidth>window.innerWidth+2"),f"{width}: clinic overflow")
        check(not errors,f"{width}: page JS runtime errors {errors}")
        print(f"PASS PJM-013 Chromium {width}x{height}: home/navigation/history/real-vs-demo/category/search/no overflow")
    finally:context.close()

def check_webkit(browser,origin):
    context=browser.new_context(**{
        "viewport":{"width":390,"height":844},"is_mobile":True,"has_touch":True,"device_scale_factor":3,
        "locale":"ko-KR","reduced_motion":"reduce"
    })
    page=context.new_page()
    try:
        page.goto(origin,wait_until="domcontentloaded")
        check(page.locator(".pjm013-bottom-nav").is_visible(),"WebKit: missing mobile bottom nav")
        page.locator('.pjm013-bottom-nav [data-val="nearby"]').tap()
        check_page(page,"nearby")
        page.locator('.pjm013-bottom-nav [data-val="clinics"]').tap()
        check(page.locator(".clinic-explore-card").count()==5,"WebKit: mock booking catalog absent")
        page.locator('.pjm013-bottom-nav [data-val="insurance"]').tap()
        check(page.locator("#insurerSelect").count()==1,"WebKit: insurance destination missing")
        page.locator('.pjm013-bottom-nav [data-val="home"]').tap()
        check_page(page,"home")
        print("PASS PJM-013 WebKit mobile touch bottom navigation: all four destinations")
    finally:context.close()

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
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    verify(chromium,origin,w,h)
                check_webkit(webkit,origin)
            finally:
                chromium.close();webkit.close()
    finally:server.shutdown();server.server_close()
    print("ALL PJM-013 SERVICE NAVIGATION QA PASSED (mock Kakao/real hardware not used)")

if __name__=="__main__":main()
