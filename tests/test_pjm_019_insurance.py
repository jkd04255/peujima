"""PJM-019: verified-product, fail-closed benefit scenarios and full UI/browser regression.

Only mocks existing official-information links, no real insurer, login, policy PDF,
paid API, personal location or insurance claim. Real iPhone Safari is separate.
"""
from __future__ import annotations
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def evaluate(page, **changes):
    base={
      "insurer":"meritz-dog","plan":"premium","care":"illness","deductible":"30000",
      "visit":"out","start":"2025-01-01","onset":"2026-03-05",
      "expense":"200000","annualPaid":"0","dailyPaid":"0","existing":"no",
      "scanUsed":"no","policyMatch":True
    }
    base.update(changes)
    return page.evaluate("(q)=>window.PJM019.estimate(q)",base)

def check_engine(page):
    good=evaluate(page)
    require(good["kind"]=="scenario" and good["amount"]==119000,
       "70% 200000 minus 30000 deductible example should be 119000")
    require(evaluate(page,plan="standard",expense="1000000")["amount"]==150000,
       "basic plan daily cap")
    require(evaluate(page,plan="economy",expense="1000000")["amount"]==100000,
       "economy plan daily cap")
    require(evaluate(page,annualPaid="14950000")["amount"]==50000,
       "annual remaining cap")
    require(evaluate(page,visit="surgery-out",expense="8000000")["amount"]==2500000,
       "surgery-day cap")
    require(evaluate(page,care="mri",scanUsed="no",expense="4000000")["amount"]==300000,
       "MRI first annual scan constrained by non-surgery daily cap")
    require(evaluate(page,care="patella",start="2026-01-01",onset="2026-06-01")["kind"]=="excluded",
       "first-year patella exclusion")
    require(evaluate(page,care="illness",start="2026-01-01",onset="2026-01-20")["kind"]=="excluded",
       "first 30 days illness exclusion")
    require(evaluate(page,care="injury",start="2026-01-01",onset="2026-01-05")["kind"]=="scenario",
       "injury should not be treated as new-disease waiting period")
    require(evaluate(page,care="vaccine")["kind"]=="excluded","preventive care exclusion")
    require(evaluate(page,care="groom")["kind"]=="excluded","grooming exclusion")
    require(evaluate(page,care="dental")["kind"]=="hold","dental needs contract conditions")
    require(evaluate(page,care="mri",scanUsed="yes")["kind"]=="hold","repeat imaging must be held")
    require(evaluate(page,insurer="hyundai-dog")["kind"]=="hold","other insurer must not estimate")
    require(evaluate(page,insurer="meritz-cat")["kind"]=="hold","dog rules cannot be reused for cats")
    require(evaluate(page,policyMatch=False)["kind"]=="hold","unknown signed terms must block")
    require(evaluate(page,existing="unknown")["kind"]=="hold","unknown pre-existing condition blocks")
    require(evaluate(page,existing="yes")["kind"]=="excluded","documented pre-existing condition")
    require(evaluate(page,expense="-1")["kind"]=="hold","negative cost blocks")
    require(evaluate(page,expense="abc")["kind"]=="hold","invalid currency blocks")
    require(evaluate(page,annualPaid="")["kind"]=="hold","unknown annual remainder blocks")
    require(evaluate(page,onset="2023-01-01")["kind"]=="hold","pre-policy illness blocks")
    require(evaluate(page,start="2026-02-31")["kind"]=="hold","invalid start date blocks")

def run_case(browser, origin, width, height, engine="Chromium"):
    ctx=browser.new_context(viewport={"width":width,"height":height},locale="ko-KR",
        reduced_motion="reduce",has_touch=engine=="WebKit",is_mobile=engine=="WebKit")
    page=ctx.new_page()
    exceptions=[]
    page.on("pageerror",lambda e:exceptions.append(str(e)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
        lambda route:route.fulfill(status=200,content_type="text/css",body="/* no external font in test */"))
    try:
        page.goto(origin+"#insurance",wait_until="load")
        require(page.locator("#insurance").count()==1,"insurance route not mounted")
        require(page.locator("#insurerSelect").is_visible(),"insurance company selection lost")
        require(page.locator("#careSelect").is_visible(),"care selection lost")
        require(page.locator(".insurance-button").is_visible(),"analysis button missing")
        require(page.locator(".insurance-disclaimer").is_visible(),"insurance non-guarantee notice lost")
        require(page.locator(".insurance-intro").count()==0,"redundant intro returned")
        require(page.locator(".insurance-card .form-head").count()==0,"decorative English heading returned")
        require(page.locator("a[href='https://www.meritzdirect.com/pet/product.do']").count()>0,
                "official source link missing")
        require("PJM019" in page.evaluate("() => ({PJM019:!!window.PJM019})") and page.evaluate("!!window.PJM019"),
                "engine not loaded")
        check_engine(page)
        page.locator(".insurance-button").click()
        require(page.locator(".insurance-result").is_visible(),"initial hold result missing")
        require("추가 확인" in page.locator(".insurance-result").inner_text(),"missing fields should not estimate")
        page.locator("#pjm019Start").fill("2025-01-01")
        page.locator("#pjm019Start").dispatch_event("change")
        page.locator("#pjm019Onset").fill("2026-03-05")
        page.locator("#pjm019Onset").dispatch_event("change")
        page.locator("#pjm019Expense").fill("200000")
        page.locator("#pjm019Expense").dispatch_event("change")
        page.locator("#pjm019AnnualPaid").fill("0")
        page.locator("#pjm019AnnualPaid").dispatch_event("change")
        page.locator("#pjm019DailyPaid").fill("0")
        page.locator("#pjm019DailyPaid").dispatch_event("change")
        page.locator("#pjm019Existing").select_option("no")
        page.locator("#pjm019PolicyMatch").check()
        page.locator(".insurance-button").click()
        require("119,000원" in page.locator(".pjm019-amount").inner_text(),
                "UI result should use assumed rule and cite amount as hypothetical")
        require("확정" in page.locator(".pjm019-result").inner_text(),"uncertainty notice disappeared")
        page.locator("#insurerSelect").select_option("hyundai-dog")
        require(page.locator(".pjm019-amount").count()==0,
                "stale Meritz amount visible after unsupported insurer switch")
        page.locator(".insurance-button").click()
        require("추가 확인" in page.locator(".insurance-result").inner_text(),
                "unsupported insurer must not produce claims")
        require(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),
                f"{engine} {width}: insurance overflow")
        page.goto(origin+"#home",wait_until="load")
        require(page.locator(".pjm013-service-card").count()==3,"home services changed")
        page.goto(origin+"#nearby",wait_until="load")
        require(page.locator(".nearby-geo").is_visible(),"Kakao search missing after insurance")
        require(not exceptions,f"{engine} {width}: JS errors: {exceptions}")
        print(f"PASS PJM-019 {engine} {width}px: terms scenarios, fail-closed checks, UI, routes, overflow")
    finally:
        ctx.close()

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
                for w,h in [(320,700),(390,844),(1440,900)]:
                    run_case(chromium,origin,w,h)
                run_case(webkit,origin,390,844,"WebKit")
            finally:
                chromium.close()
                webkit.close()
    finally:
        server.shutdown()
        server.server_close()
    print("ALL PJM-019 POLICY SCENARIO QA PASSED")

if __name__=="__main__":
    main()
