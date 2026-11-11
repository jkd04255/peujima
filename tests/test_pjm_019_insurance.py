"""PJM-020 insurance summary UX regression.
The screen now asks only for product and care type, not expense/dates/medical history.
Official-public-info summaries are not policy adjudication; unknown contract details stay unknown.
"""
from __future__ import annotations
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def require(value,msg):
    if not value: raise AssertionError(msg)

def verify_summary_engine(page):
    q=lambda ins,care: page.evaluate("(x)=>PJM019.summarize(x.ins,x.care)",{"ins":ins,"care":care})
    x=q("meritz-dog","illness")
    require(x["status"]=="보장 검토 가능" and "30일" in " ".join(x["points"]),"Meritz disease waiting period")
    require("50~70%" in x["description"] and x["showPlans"],"published tier-range disclosure")
    x=q("meritz-dog","patella")
    require("1년" in x["description"] and x["status"]=="면책기간 확인 필수","patella timing warning")
    x=q("meritz-dog","mri")
    require("최초 연 1회" in x["description"],"scan annual one-time cap")
    x=q("meritz-dog","dental")
    require("확인" in x["status"],"dental should not assert guaranteed payout")
    for c in ["vaccine","groom"]:
        x=q("meritz-dog",c)
        require(x["status"]=="일반적으로 보장 제외","preventive / cosmetic coverage caution")
    for ins in ["meritz-cat","hyundai-dog","hyundai-cat","db-dog","db-cat"]:
        x=q(ins,"illness")
        require(x["showPlans"] is False,"must not carry Meritz dog amounts over to other products")
        require("50~70%" not in x["description"],"must not show unverified percentages")
    x=q("hyundai-dog","mri")
    require(x["status"]=="특약 가입 여부 확인","Hyundai add-on caveat")
    require(q("hyundai-cat","mri")["showPlans"] is False,"cat policy is not dog rider")
    require(q("missing","unknown")["status"]=="추가 확인 필요","invalid selection must fail closed")

def reveal_notes(page):
    """Open the new single footer disclosure for legacy policy-detail checks."""
    panel=page.locator(".pjm030-fineprint")
    assert panel.count()==1, "bottom evidence disclosure must exist"
    if panel.get_attribute("open") is None:
        page.locator(".pjm030-fineprint > summary").click()

def run_case(browser,origin,width,height,name):
    context=browser.new_context(viewport={"width":width,"height":height},locale="ko-KR",
        reduced_motion="reduce",has_touch=name=="WebKit",is_mobile=name=="WebKit")
    page=context.new_page()
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
        lambda route:route.fulfill(status=200,content_type="text/css",body="/* no external font in test */"))
    try:
        page.goto(origin+"#insurance",wait_until="load")
        require(page.locator("#insurance").is_visible(),"insurance view missing")
        require(page.locator("#insurerSelect").is_visible(),"insurer selector missing")
        require(page.locator("#careSelect").is_visible(),"treatment selector missing")
        require(page.locator(".insurance-button").is_visible(),"summary button missing")
        require(page.locator(".insurance-disclaimer").is_visible(),"policy disclaimer missing")
        require(page.locator(".insurance-intro").count()==0,"old redundant intro returned")
        require(page.locator(".insurance-card .form-head").count()==0,"old non-functional English metadata returned")
        require(page.locator("#pjm019Expense").count()==0,"old expense input still displayed")
        require(page.locator("#pjm019Start").count()==0,"old insurance date still required")
        require(page.locator("#pjm019AnnualPaid").count()==0,"old paid amount field still required")
        require(page.locator("#pjm019PolicyMatch").count()==0,"old checkbox still required")
        require(page.locator("#insurance select").count()==2,"expected exactly two product and care selects")
        require(page.locator(".pjm020-result").count()==0,"result visible before user chooses")
        require(page.locator(".insurance-button").evaluate("(b)=>b.tagName")== "BUTTON","summary is not a link")
        require("PJM019" in page.evaluate("() => ({PJM019:!!window.PJM019})"),"analyzer JS unavailable")
        verify_summary_engine(page)

        page.locator(".insurance-button").click()
        # PJM-034: explicitly opening a long summary must announce its heading
        # and show the top of the result below the sticky mobile header.
        require(page.evaluate("""() => {
            const result=document.querySelector(".pjm020-result");
            return !!result && document.activeElement===result.querySelector("h3") &&
                result.querySelector("h3").tabIndex===-1;
        }"""),f"{name} {width}: result heading did not receive accessible focus")
        if width<=850:
            page.wait_for_function("""() => {
                const result=document.querySelector("#pjm020Output");
                const header=document.querySelector(".pjm013-header");
                if(!result || !header)return false;
                const top=result.getBoundingClientRect().top;
                const headerBottom=header.getBoundingClientRect().bottom;
                return top>=headerBottom+2 && top<=headerBottom+45;
            }""",timeout=4000)
        reveal_notes(page)
        require(page.locator(".insurance-result").is_visible(),"summary not rendered after click")
        result=page.locator(".insurance-result").inner_text()
        require("질병 통원·입원 의료비" in result,"wrong first default summary")
        require("50~70%" in result,"range should be concise and labeled")
        require("30일" in result,"waiting period not included")
        require(page.locator(".pjm020-details").count()==1,"optional detailed plan info missing")
        require(page.locator(".pjm020-details").is_visible(),"plan detail disclosure inaccessible")
        require(not page.locator(".pjm020-details").get_attribute("open"),"plans should start collapsed")
        page.locator(".pjm020-details summary").click()
        require(page.locator(".pjm020-details[open] table").is_visible(),"plan comparison did not expand")
        require(page.locator(".pjm020-details tbody tr").count()==3,"plan rows missing")
        require(page.locator(".pjm020-result a[target='_blank']").count()==0,"insurance explanation should remain inside PRZIMA")
        require(page.locator(".pjm021-policy-details").count()==1,"source and exclusions must be explained in-app")

        page.locator("#careSelect").select_option("patella")
        require(page.locator(".pjm020-result").count()==0,"stale result after changing treatment")
        require(page.locator("#insurerSelect").input_value()=="meritz-dog","selection lost after care change")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        require("1년" in page.locator(".pjm020-result").inner_text(),"patella summary missing")
        page.locator("#insurerSelect").select_option("hyundai-dog")
        require(page.locator(".pjm020-result").count()==0,"stale Meritz result after insurer change")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        require("특약" in page.locator(".pjm020-result").inner_text(),"Hyundai optional clause missing")
        require(page.locator(".pjm020-details").count()==0,"unverified insurer has plan comparison")

        page.locator("#insurerSelect").select_option("meritz-cat")
        page.locator("#careSelect").select_option("illness")
        page.locator(".insurance-button").focus()
        page.locator(".insurance-button").press("Enter")
        require(page.evaluate("""() => {
            const result=document.querySelector(".pjm020-result");
            return !!result && document.activeElement===result.querySelector("h3");
        }"""),f"{name} {width}: keyboard submit did not focus the answer heading")
        reveal_notes(page)
        require("반려묘" in page.locator(".pjm020-result").inner_text(),"cat warning missing")
        # A cat estimate may legitimately include 30만원; verify species-specific
        # official fee entries, not an arbitrary numeral in medical price bands.
        require("반려견 1일 입원비" not in page.locator(".pjm031-procedures").inner_text() and
                "반려견 종합백신 접종" not in page.locator(".pjm031-procedures").inner_text(),
                "dog-only published medical cost copied to cat")
        require(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),f"{name} {width}px horizontal overflow")
        page.goto(origin+"#home",wait_until="load")
        require(page.locator(".pjm013-service-card").count()==3,"home services broken")
        page.goto(origin+"#nearby",wait_until="load")
        require(page.locator(".nearby-geo").is_visible(),"Kakao place search missing")
        require(not errors,f"{name} {width}px JS errors {errors}")
        print(f"PASS PJM-020 {name} {width}px simple insurance summaries / controls / routes")
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
    print("PJM-020 SIMPLE INSURANCE QA PASSED")

if __name__=="__main__": main()
