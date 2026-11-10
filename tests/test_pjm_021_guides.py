"""PJM-021 official vet-cost and Meritz 2026 illustrative insurance guide.

No personal information or live insurer requests. The example is NOT actual
insurance adjudication, average disease bill, or price quote.
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

def check(x,msg):
    if not x:raise AssertionError(msg)

def inspect_engine(page):
    values=page.evaluate("""() => {
      const x=PJM019, med=x.medianCosts;
      const s=(name)=>x.sample("meritz-dog",name);
      return {
        med:{first:med.first.won,cbc:med.cbc.won,chem:med.chem.won,
          xray:med.xray.won,ct:med.ct.won,mri:med.mri.won},
        illness:s("illness"),digestive:s("digestive"),
        injury:s("injury"),patella:s("patella"),
        noEstimate:["skin","ear","dental","mri","vaccine","groom"].every(k=>s(k)===null),
        otherInsurer:x.sample("meritz-cat","illness"),
        onsite:Object.keys(med).every(k=>med[k].won>0) &&
          !x.guidance("meritz-dog","illness").includes("href="),
        careIds:x.careTypes.map(y=>y.id)
      };
    }""")
    check(values["med"]=={"first":10000,"cbc":34000,"chem":80000,"xray":45000,"ct":600000,"mri":791500},
          "official median dataset mismatch")
    for name,total,high,eco in [
        ("illness",124000,65800,47000),
        ("digestive",147000,81900,58500),
        ("injury",55000,17500,12500),
        ("patella",55000,17500,12500)
    ]:
        v=values[name]
        check(v["total"]==total and v["plans"][0]["amount"]==high and
              v["plans"][2]["amount"]==eco,name+" assumption mismatch")
    check(values["noEstimate"],"unverified medical procedures produced false payment")
    check(values["otherInsurer"] is None,"Meritz dog benefits reused on another product")
    check(values["onsite"],"internal explanation must not force insurer website")
    check({"digestive","skin","ear"}.issubset(values["careIds"]),"common conditions not available")

def reveal_notes(page):
    """Open the new single footer disclosure for legacy policy-detail checks."""
    panel=page.locator(".pjm030-fineprint")
    assert panel.count()==1, "bottom evidence disclosure must exist"
    if panel.get_attribute("open") is None:
        page.locator(".pjm030-fineprint > summary").click()

def run_case(browser,origin,w,h,engine):
    ctx=browser.new_context(viewport={"width":w,"height":h},locale="ko-KR",
        reduced_motion="reduce",has_touch=engine=="WebKit",is_mobile=engine=="WebKit")
    page=ctx.new_page()
    errs=[]
    page.on("pageerror",lambda err:errs.append(str(err)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
        lambda route:route.fulfill(status=200,content_type="text/css",body="/* fonts stubbed in CI */"))
    try:
        page.goto(origin+"#insurance",wait_until="load")
        check(page.locator("#insurance select").count()==2,"must ask only 2 questions")
        inspect_engine(page)
        page.locator(".insurance-button").click()
        reveal_notes(page)
        result=page.locator(".pjm020-result")
        check(result.is_visible(),"summary result missing")
        check(page.locator(".pjm021-fee-row").count()==3,"illness itemized fees missing")
        check("10,000원" in result.inner_text() and "34,000원" in result.inner_text()
              and "80,000원" in result.inner_text(),"official fee medians absent")
        check("65,800원" in result.inner_text() and "47,000원" in result.inner_text(),
              "illustrative plan payments missing")
        check("가상" in result.inner_text() and "중간값" in result.inner_text(),
              "price and payout uncertainty disclaimers missing")
        # Optional research links in the collapsed cost-source footer are fine;
        # insurance explanation must not send the user to an insurer's website.
        check(result.locator("a[href]").count()==
              result.locator(".pjm030-fineprint .pjm032-sources a[href]").count() and
              result.locator("a[target='_blank']").count()==0,
              "only voluntary fee-source links in the bottom disclosure are allowed")
        check(page.locator(".pjm021-policy-details").count()==1,"in-app details missing")
        check(not page.locator(".pjm021-policy-details").get_attribute("open"),
              "explanatory details should be collapsed by default")
        page.locator(".pjm021-policy-details summary").click()
        check(page.locator(".pjm021-policy-details[open]").is_visible(),
              "in-app policy disclosure failed")
        check("30일" in page.locator(".pjm021-policy-details").inner_text(),
              "policy exemption details missing")

        page.locator("#careSelect").select_option("digestive")
        check(page.locator(".pjm021-fee-guide").count()==0,"stale plan from prior treatment")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        check("81,900원" in page.locator(".pjm020-result").inner_text(),
              "digestive reference scenario wrong")

        page.locator("#careSelect").select_option("mri")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        check("791,500원" in page.locator(".pjm020-result").inner_text(),
              "2025 median MRI price missing")
        check("600,000원" in page.locator(".pjm020-result").inner_text(),
              "2025 median CT price missing")
        check(page.locator(".pjm021-plan-amounts").count()==0,
              "imaging payment must not be guessed under unclear combined caps")

        page.locator("#careSelect").select_option("skin")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        check("피부" in page.locator(".pjm020-result").inner_text(),
              "skin-specific explanation missing")
        check(page.locator(".pjm021-plan-amounts").count()==0,
              "skin treatment cost unsupported: no fabricated payout")

        page.locator("#insurerSelect").select_option("hyundai-dog")
        check(page.locator(".pjm020-result").count()==0,"stale Meritz conclusion")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        check(page.locator(".pjm021-plan-amounts").count()==0,
              "unreviewed insurer must not show Meritz payouts")
        check("가입 계약" in page.locator(".pjm020-result").inner_text(),
              "no caveat for not-yet-reviewed company")

        page.goto(origin+"#home",wait_until="load")
        check(page.locator(".pjm013-service-card").count()==3,"home services regressed")
        page.goto(origin+"#nearby",wait_until="load")
        check(page.locator(".nearby-geo").is_visible(),"map services regressed")
        page.goto(origin+"#insurance",wait_until="load")
        check(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),
              f"{engine} {w} insurance horizontal overflow")
        check(not errs,f"{engine} {w} JavaScript errors {errs}")
        print(f"PASS PJM-021 {engine} {w}: itemized published medians, hypothetical payout, caveats, responsive")
    finally:ctx.close()

def main():
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                origin=f"http://127.0.0.1:{server.server_port}/"
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_case(chromium,origin,w,h,"Chromium")
                run_case(webkit,origin,390,844,"WebKit")
            finally:
                chromium.close();webkit.close()
    finally:
        server.shutdown();server.server_close()
    print("ALL PJM-021 INSURANCE GUIDES QA PASSED")

if __name__=="__main__":main()
