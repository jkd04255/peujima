"""PJM-018 typography regression for Korean UI across routes and viewports.

Checks the computed font system and conservative responsive layout.
CDN CSS is stubbed for deterministic browser CI; the official font import URLs
are validated from source. This is not a physical iPhone Safari font proof.
"""
from __future__ import annotations
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/"pjm013-navigation.css").read_text(encoding="utf-8")
assert CSS.startswith('@import url("https://cdn.jsdelivr.net/gh/sun-typeface/SUIT@2/fonts/variable/woff2/SUIT-Variable.css");')
assert 'SUITE@2/fonts/variable/woff2/SUITE-Variable.css' in CSS

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def require(condition,message):
    if not condition: raise AssertionError(message)

def family(page,selector):
    return page.locator(selector).first.evaluate("(el)=>getComputedStyle(el).fontFamily")

def run_case(browser,origin,width,height,name):
    context=browser.new_context(viewport={"width":width,"height":height},
        locale="ko-KR",reduced_motion="reduce",
        is_mobile=(name=="WebKit"),has_touch=(name=="WebKit"))
    page=context.new_page()
    errors=[]
    page.on("pageerror",lambda error:errors.append(str(error)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
        lambda route:route.fulfill(status=200,content_type="text/css",body="/* font CDN stub: no glyph files in CI */"))
    try:
        page.goto(origin,wait_until="load")
        page.locator(".pjm013-nav-name").first.wait_for(state="attached",timeout=12000)
        require("SUIT Variable" in family(page,".pjm013-nav-name:visible"),f"{name} navigation missing SUIT")
        require("SUITE Variable" in family(page,".brand-primary"),f"{name} brand missing SUITE")
        require("SUITE Variable" in family(page,".hero-v4-heading"),f"{name} photo hero missing SUITE")
        require("SUIT Variable" in family(page,".pjm013-service-card"),f"{name} service card missing SUIT")
        require("SUITE Variable" in family(page,".pjm013-service-card strong"),f"{name} service title missing SUITE")
        require(page.locator(".hero-pet").count()>=2,"pet photographs lost")
        require(page.locator(".pjm013-service-card").count()==3,"service actions changed")
        require(not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"),
            f"{name} {width}: horizontal overflow on home")
        for route in ["nearby","clinics","insurance"]:
            page.goto(origin+"#"+route,wait_until="load")
            require(page.evaluate("state.page")==route,f"{name} route {route} broken")
            require(not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"),
                f"{name} {width}: horizontal overflow on {route}")
        require(page.locator(".insurance-disclaimer").count()>=1,"insurance disclaimer lost")
        require(page.locator(".insurance-button").count()>=1,"insurance action lost")
        page.goto(origin+"#nearby",wait_until="load")
        require(page.locator(".nearby-geo").is_visible(),"Kakao map location control hidden")
        require("SUIT Variable" in family(page,".nearby-geo"),"nearby GPS button wrong font")
        require("SUIT Variable" in family(page,".nearby-region-form input"),"search input wrong font")
        require(page.locator(".nearby-endnote").is_visible(),"real-booking disclaimer hidden")
        if width<=390:
            require(page.locator(".nearby-region-form input").first.evaluate(
                "(el)=>parseFloat(getComputedStyle(el).fontSize)")>=16,"iOS input autozoom risk")
        require(not errors,f"{name} JS console exceptions {errors}")
        print(f"PASS PJM-018 {name} {width}x{height}: typography, routes, no overflow, notices")
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
                for width,height in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_case(chromium,origin,width,height,"Chromium")
                run_case(webkit,origin,390,844,"WebKit")
            finally:
                chromium.close()
                webkit.close()
    finally:
        server.shutdown()
        server.server_close()
    print("ALL PJM-018 TYPOGRAPHY QA PASSED")

if __name__=="__main__":
    main()
