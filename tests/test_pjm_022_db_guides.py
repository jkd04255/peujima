"""PJM-022: DB손해보험 2026 다이렉트 펫블리 반려견 2610(CM) public-guide QA.
All DB numbers are PRE-CAP illustrative arithmetic, not claim decisions.
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

def require(condition,message):
    if not condition: raise AssertionError(message)

def inspect_logic(page):
    x=page.evaluate("""() => {
      const calc=(ins,care)=>PJM019.sample(ins,care);
      const desc=(ins,care)=>PJM019.summarize(ins,care);
      return {
        illness:calc("db-dog","illness"),
        digestive:calc("db-dog","digestive"),
        injury:calc("db-dog","injury"),
        noImaging:calc("db-dog","mri")===null,
        noDental:calc("db-dog","dental")===null,
        cats:calc("db-cat","illness"),
        hyundai:calc("hyundai-dog","illness"),
        dbSource:PJM019.guidance("db-dog","illness"),
        unknownSource:PJM019.guidance("hyundai-cat","illness"),
        meritzSource:PJM019.guidance("meritz-dog","illness"),
        illnessSummary:desc("db-dog","illness"),
        jointSummary:desc("db-dog","patella"),
        dentalSummary:desc("db-dog","dental")
      };
    }""")
    require(x["illness"]["total"]==124000 and x["illness"]["beforeCaps"],"DB scenario metadata")
    require([v["amount"] for v in x["illness"]["plans"]]==[65800,47000],"DB 70/50% arithmetic")
    require([v["amount"] for v in x["digestive"]["plans"]]==[81900,58500],"DB digestive arithmetic")
    require([v["amount"] for v in x["injury"]["plans"]]==[17500,12500],"DB injury arithmetic")
    require(x["noImaging"] and x["noDental"],"unknown tests must not produce payouts")
    require(x["cats"] is None and x["hyundai"] is None,"no insurance-plan number crossover")
    require("DB손해보험" in x["dbSource"] and "2610" in x["dbSource"],"DB public product provenance")
    require("메리츠화재" not in x["dbSource"],"Meritz-only terms leaked into DB")
    require("DB손해보험" not in x["unknownSource"] and "메리츠화재" not in x["unknownSource"],
            "unverified insurer incorrectly cites a different insurance contract")
    require("메리츠화재" in x["meritzSource"],"Meritz evidence regressed")
    require(x["illnessSummary"]["status"]=="보장 검토 가능","DB general treatment status")
    require(not x["illnessSummary"]["showPlans"] and x["illnessSummary"]["showDBDetails"],
            "Meritz tier comparison must not be reused for DB")
    require("1년" in x["jointSummary"]["description"],"DB joint coverage waiting period")
    require(x["dentalSummary"]["status"]=="특약 가입 여부 확인","DB dental rider status")

def run_case(browser,base,w,h,kind):
    ctx=browser.new_context(viewport={"width":w,"height":h},
        locale="ko-KR",reduced_motion="reduce",
        has_touch=kind=="WebKit",is_mobile=kind=="WebKit")
    page=ctx.new_page();errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
        lambda route:route.fulfill(status=200,content_type="text/css",body="/* font offline */"))
    try:
        page.goto(base+"#insurance",wait_until="load")
        require(page.locator("#insurance select").count()==2,"must preserve only two inputs")
        inspect_logic(page)
        page.locator("#insurerSelect").select_option("db-dog")
        page.locator(".insurance-button").click()
        result=page.locator(".pjm020-result")
        require(result.is_visible(),"DB coverage result missing")
        require(result.locator(".pjm021-plan-amounts > div").count()==2,"expected two DB ratio variants")
        txt=result.inner_text()
        require("65,800원" in txt and "47,000원" in txt,"DB example payment labels absent")
        require("한도 적용 전" in txt and "가상" in txt,"DB numbers not marked hypothetical/pre-cap")
        require("30일" in txt and "50%" in txt and "70%" in txt,"DB main policy conditions hidden")
        require(result.locator("a[href]").count()==0,"in-app policy explanation cannot force a redirect")
        require(result.locator(".pjm020-details.pjm022-db-details").count()==1,"DB details missing")
        require(result.locator(".pjm020-details:not(.pjm022-db-details)").count()==0,
                "Meritz plan detail erroneously shown for DB")
        page.locator(".pjm022-db-details summary").click()
        require(page.locator(".pjm022-db-details[open]").is_visible(),"DB details cannot expand")
        require("1년" in page.locator(".pjm022-db-details").inner_text(),"DB conditions missing")
        policy=page.locator(".pjm021-policy-details").text_content()
        require("2610" in policy and "메리츠" not in policy,"DB details wrong source")

        for care in ["mri","dental","skin"]:
            page.locator("#careSelect").select_option(care)
            require(page.locator(".pjm020-result").count()==0,"old DB result remained on care change")
            page.locator(".insurance-button").click()
            require(page.locator(".pjm021-plan-amounts").count()==0,
                    "unverified rider cost must not generate benefits")
            require("특약" in page.locator(".pjm020-result").inner_text(),"rider caveat missing")

        page.locator("#careSelect").select_option("patella")
        page.locator(".insurance-button").click()
        require("1년" in page.locator(".pjm020-result").inner_text(),"joint rider waiting period absent")

        page.locator("#insurerSelect").select_option("hyundai-dog")
        require(page.locator(".pjm020-result").count()==0,"DB result leaked after insurer change")
        page.locator(".insurance-button").click()
        require(page.locator(".pjm021-plan-amounts").count()==0,
                "unverified insurer must not calculate a benefit")
        require("DB손해보험" not in page.locator(".pjm021-policy-details").text_content(),
                "DB evidence leaked into Hyundai policy")

        page.locator("#insurerSelect").select_option("meritz-dog")
        page.locator("#careSelect").select_option("illness")
        page.locator(".insurance-button").click()
        require(page.locator(".pjm021-plan-amounts > div").count()==3,
                "existing Meritz examples regressed")
        require(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),
                f"{kind} {w}px insurance overflow")
        page.goto(base+"#home",wait_until="load")
        require(page.locator(".pjm013-service-card").count()==3,"home navigation regressed")
        page.goto(base+"#nearby",wait_until="load")
        require(page.locator(".nearby-geo").is_visible(),"nearby maps entry regressed")
        require(not errors,f"{kind} {w}px JS errors: {errors}")
        print(f"PASS PJM-022 {kind} {w}px DB 2610 official terms, pre-cap examples and regression")
    finally:ctx.close()

def main():
    srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                root=f"http://127.0.0.1:{srv.server_port}/"
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_case(chromium,root,w,h,"Chromium")
                run_case(webkit,root,390,844,"WebKit")
            finally:
                chromium.close();webkit.close()
    finally:
        srv.shutdown();srv.server_close()
    print("PJM-022 DB DOG INSURANCE QA PASSED")

if __name__=="__main__":main()
