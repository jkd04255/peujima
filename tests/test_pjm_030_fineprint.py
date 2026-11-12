"""PJM-030 one small-print footer for insurance supporting notes.
Keeps clinical/coverage facts visible and preserves all original safety text.
"""
from __future__ import annotations
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def run_case(browser,url,width,height,engine):
    ctx=browser.new_context(viewport={"width":width,"height":height},
        locale="ko-KR",reduced_motion="reduce",
        has_touch=(engine=="WebKit"),is_mobile=(engine=="WebKit"))
    page=ctx.new_page()
    errors=[]
    page.on("pageerror",lambda error:errors.append(str(error)))
    try:
        page.goto(url+"#insurance",wait_until="load")
        need(page.locator("#insurance select").count()==2,
             "PJM-030 must not add inputs")
        page.locator("#insurerSelect").select_option("meritz-dog")
        page.locator("#careSelect").select_option("illness")
        page.locator(".insurance-button").click()
        result=page.locator(".pjm020-result")
        footer=page.locator(".pjm030-fineprint")
        need(result.is_visible() and footer.count()==1,
             "result or one unified disclosure missing")
        need(footer.get_attribute("open") is None,
             "fine print must start collapsed")
        need(page.locator(".pjm021-fees").is_visible() and
             "10,000원" in page.locator(".pjm021-fees").inner_text(),
             "actual cost item must stay visible")
        need(page.locator(".pjm045-totals").is_visible(),
             "new conditional payout / self-payment must be visible")
        need(page.locator(".pjm021-plan-amounts").count()==1 and
             not page.locator(".pjm021-plan-amounts").is_visible(),
             "legacy hypothetical payout should be preserved in optional fine print")
        for sel in [".pjm021-cost-notice",".pjm021-example .pjm021-calc-note",
                    ".pjm026-source-meta",".pjm026-version-warning"]:
            # The entire old scenario and its calculation note now live in fine print.
            check=".pjm021-calc-note" if "calc-note" in sel else sel
            need(page.locator(check).count()==1 and
                 not page.locator(check).is_visible(),
                 "secondary notice must be out of default reading flow: "+check)
        positions=page.evaluate("""() => {
            const root=document.querySelector(".pjm020-result");
            const footer=root?.querySelector(":scope > .pjm030-fineprint");
            const moved=[".pjm021-cost-notice",".pjm021-calc-note",
              ".pjm026-source-meta",".pjm026-version-warning",
              ".pjm021-policy-details",".pjm023-more",".pjm021-conditions"];
            return {
              last:root?.lastElementChild===footer,
              within:moved.every(sel=>Array.from(root.querySelectorAll(sel))
                .every(el=>footer.contains(el))),
              unique:root?.querySelectorAll(".pjm021-cost-notice").length===1,
              xOverflow:document.documentElement.scrollWidth>innerWidth+2
            };
        }""")
        need(positions["last"] and positions["within"] and positions["unique"],
             "not all caveats moved once to last footer: "+str(positions))
        need(not positions["xOverflow"],
             "horizontal overflow from footer on "+engine)
        footer.locator(":scope > summary").click()
        need(page.locator(".pjm021-cost-notice").is_visible(),
             "cost median caution inaccessible")
        need("2025년" in page.locator(".pjm021-cost-notice").inner_text(),
             "source year must be preserved")
        need(page.locator(".pjm021-plan-amounts").is_visible(),
             "legacy payout illustration must remain readable when expanded")
        need(page.locator(".pjm030-evidence-note").is_visible(),
             "policy evidence grade inaccessible")
        need(page.locator(".pjm021-policy-details").count()==1,
             "detailed medical source lost")
        footer.locator(":scope > summary").click()
        need(not page.locator(".pjm021-cost-notice").is_visible(),
             "fine print cannot collapse again")

        page.locator("#insurerSelect").select_option("kb-dog")
        page.locator("#careSelect").select_option("liability")
        page.locator(".insurance-button").click()
        need(page.locator(".pjm023-focus").is_visible() and
             "3만원" in page.locator(".pjm023-focus").inner_text(),
             "essential liability deductible moved into fine print")
        need(not page.locator(".pjm023-extra-warning").is_visible(),
             "secondary rider caveat must start collapsed")
        page.locator(".pjm030-fineprint > summary").click()
        need(page.locator(".pjm023-extra-warning").is_visible() and
             page.locator(".pjm029-kb-editions").is_visible(),
             "rider and product edition warnings not available")
        page.locator(".pjm023-more summary").click()
        need(page.locator(".pjm028-clause-details").is_visible(),
             "KB rider exclusions lost")
        need(page.locator(".pjm020-result a[target='_blank']").count()==0,
             "no forced external source redirects")
        page.locator("#insurerSelect").select_option("nh-cat")
        need(page.locator(".pjm020-result").count()==0,
             "stale insurer result survived selection change")
        page.locator("#careSelect").select_option("feline_cystitis")
        page.locator(".insurance-button").click()
        need(page.locator(".pjm029-kb-editions").count()==0,
             "KB product codes leaked into NH result")
        need(page.locator(".pjm030-fineprint").get_attribute("open") is None,
             "new result fine print should start closed")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "unverified insurer must not show a payout")
        need(not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"),
             "result overflow on "+engine)
        need(not errors,f"JavaScript errors ({engine} {width}): {errors}")
        print(f"PASS PJM-030 {engine} {width}: concise main answer, collapsed fine print, no leaked policy data")
    finally:ctx.close()

def main():
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),
        functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                url=f"http://127.0.0.1:{server.server_port}/"
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_case(chromium,url,w,h,"Chromium")
                run_case(webkit,url,390,844,"WebKit")
            finally:
                chromium.close();webkit.close()
    finally:server.shutdown();server.server_close()
    print("ALL PJM-030 FOOTNOTE UX QA PASSED")

if __name__=="__main__":main()
