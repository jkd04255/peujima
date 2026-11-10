"""PJM-023 expanded insurance product and condition taxonomy.
Public product guides only; do not infer real policy acceptance or reimbursements.
"""
from __future__ import annotations
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class Silent(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def need(x,msg):
    if not x:raise AssertionError(msg)

def run_case(browser,url,w,h,engine):
    context=browser.new_context(viewport={"width":w,"height":h},locale="ko-KR",
       reduced_motion="reduce",has_touch=(engine=="WebKit"),is_mobile=(engine=="WebKit"))
    page=context.new_page();errors=[]
    page.on("pageerror",lambda err:errors.append(str(err)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
       lambda route:route.fulfill(status=200,content_type="text/css",body="/* test font offline */"))
    try:
        page.goto(url+"#insurance",wait_until="load")
        need(page.locator("#insurance select").count()==2,"must require exactly 2 selections")
        stats=page.evaluate("""() => ({
          c:window.PJM023?.cares.length,i:PJM019.insurers.length,
          care:PJM019.careTypes.length,
          catalog:!!window.PJM023,
          species:!!PJM019.insurers.find(x=>x.id==="nh-cat"),
          official:!!PJM019.insurers.find(x=>x.id==="samsung-dog")
        })""")
        need(stats["catalog"] and stats["i"]==14 and stats["c"]==35 and
             stats["care"]==45 and stats["species"] and stats["official"],
             f"catalog counts or data failed: {stats}")
        need(page.locator("#careSelect optgroup").count()>=7,"grouped care taxonomy absent")
        need(page.locator("#careSelect option").count()==40,
             "dog should show 10 base and 30 non-cat-specific conditions")
        page.locator("#insurerSelect").select_option("kb-dog")
        page.locator("#careSelect").select_option("chemo")
        page.locator(".insurance-button").click()
        result=page.locator(".pjm020-result")
        need(result.is_visible(),"new policy guidance missing")
        need("금쪽같은" in result.inner_text(),"KB-specific official summary not shown")
        need("30만원" in page.locator(".pjm023-focus").inner_text(),
             "KB antitumor drug published cap missing")
        need(page.locator(".pjm023-fact").count()>=3,"coverage facts missing")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "unverified KB benefits must never be calculated")
        need(page.locator(".pjm023-more").count()==1,"terms details not in-app")
        page.locator(".pjm023-more summary").click()
        need(page.locator(".pjm023-more[open]").is_visible(),"cannot expand conditions")
        need("면책" in page.locator(".pjm023-more").inner_text(),"exclusions omitted")

        page.locator("#insurerSelect").select_option("nh-cat")
        need(page.locator(".pjm020-result").count()==0,"stale KB result after insurer change")
        need(page.locator("#careSelect option").count()==45,"cat topic choices not present")
        page.locator("#careSelect").select_option("hospital")
        page.locator(".insurance-button").click()
        need("반려견 입원비" not in page.locator(".pjm021-fee-guide").inner_text(),
             "dog-only published admission price must not be offered for a cat")
        page.locator("#careSelect").select_option("feline_cystitis")
        page.locator(".insurance-button").click()
        txt=page.locator(".pjm020-result").inner_text()
        need("원문" in txt and "미검증" in txt,"NH unverified contract must be labeled")
        need("비뇨기" in txt,"cat urinary treatment-specific note missing")
        need(page.locator(".pjm021-plan-amounts").count()==0,"unverified NH must have no payout")

        page.locator("#insurerSelect").select_option("samsung-dog")
        need(page.locator("#careSelect").input_value()=="illness","cat-only care must reset for dog")
        need(page.locator("#careSelect option").count()==40,"cat-only care leaked to dog")
        page.locator("#careSelect").select_option("allergy")
        page.locator(".insurance-button").click()
        need("삼성화재" in page.locator(".pjm020-result").inner_text(),
             "new insurer missing in-app facts")
        need("80%" in page.locator(".pjm023-coverage").inner_text(),
             "official Samsung selectable ratio missing")
        need("NH펫앤미든든" not in page.locator(".pjm023-coverage").inner_text(),
             "old insurer's source leaked into Samsung result")

        page.locator("#insurerSelect").select_option("kakao-dog")
        page.locator("#careSelect").select_option("surgery")
        page.locator(".insurance-button").click()
        need("수술당일형" in page.locator(".pjm023-coverage").inner_text(),
             "KakaoPay surgery-only vs inpatient/outpatient plans not shown")
        need("카카오페이손해보험" in page.locator(".pjm023-coverage").inner_text(),
             "KakaoPay official coverage profile not shown")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "KakaoPay must not reuse Meritz/DB payout examples")

        page.locator("#insurerSelect").select_option("meritz-dog")
        page.locator("#careSelect").select_option("illness")
        page.locator(".insurance-button").click()
        need(page.locator(".pjm021-plan-amounts > div").count()==3,
             "Meritz payout simulation changed")
        need("메리츠" in page.locator(".pjm023-coverage").inner_text(),
             "Meritz official product overview missing")
        need(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),
             f"{engine} {w} horizontal overflow")
        page.goto(url+"#home",wait_until="load")
        need(page.locator(".pjm013-service-card").count()==3,"home routes changed")
        page.goto(url+"#nearby",wait_until="load")
        need(page.locator(".nearby-geo").is_visible(),"map entry changed")
        need(not errors,f"JavaScript exceptions {engine} {w}: {errors}")
        print(f"PASS PJM-023 {engine} {w}px 12 products / 45 care topics / sourced details")
    finally:
        context.close()

def main():
    srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),
       functools.partial(Silent,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                url=f"http://127.0.0.1:{srv.server_port}/"
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_case(chromium,url,w,h,"Chromium")
                run_case(webkit,url,390,844,"WebKit")
            finally:chromium.close();webkit.close()
    finally:srv.shutdown();srv.server_close()
    print("PJM-023 full insurance catalog QA passed")

if __name__=="__main__":main()
