"""PJM-012 axe-core WCAG 2.2 static section checks in Chromium with MOCK Kakao SDK.

Only the newly added location discovery section is scanned, to keep this
review's scope separate from legacy v0.7.0 accessibility debt.
"""
from __future__ import annotations
import functools
import http.server
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from test_pjm_012 import MOCK_SDK

ROOT=Path(__file__).resolve().parents[1]
AXE=ROOT/"node_modules/axe-core/axe.min.js"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def scan(page,stage,width):
    page.add_script_tag(path=str(AXE))
    data=page.evaluate("""async () => {
      const root=document.getElementById('nearby-hospitals');
      return await axe.run(root,{
        runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']},
        resultTypes:['violations']
      });
    }""")
    problems=data["violations"]
    if problems:
        fragments=[]
        for issue in problems:
            targets=[str(node.get("target")) for node in issue.get("nodes",[])[:3]]
            fragments.append(f"{issue['id']} / {issue['impact']} / {targets}")
        raise AssertionError(f"axe {width}px {stage} WCAG issues: "+"; ".join(fragments))
    print(f"PASS axe WCAG 2.2 A/AA {width}px {stage}: no automated violations in PJM-012 section")


def main():
    if not AXE.is_file():
        raise FileNotFoundError("Install axe-core first: npm install --no-save --no-package-lock axe-core@4.10.3")
    server=http.server.ThreadingHTTPServer(
        ("127.0.0.1",0),functools.partial(QuietHandler,directory=str(ROOT))
    )
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        origin=f"http://127.0.0.1:{server.server_address[1]}/"
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for width,height in [(320,700),(390,844),(768,1024),(1440,900)]:
                    context=browser.new_context(viewport={"width":width,"height":height},
                                                locale="ko-KR",reduced_motion="reduce",
                                                geolocation={"latitude":37.5,"longitude":127.0},
                                                permissions=["geolocation"])
                    page=context.new_page()
                    page.add_init_script("window.PRZIMA_KAKAO_JS_KEY='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'")
                    page.route("**/v2/maps/sdk.js?**",
                               lambda route:route.fulfill(status=200,content_type="application/javascript",body=MOCK_SDK))
                    try:
                        page.goto(origin,wait_until="load")
                        scan(page,"initial",width)
                        page.locator('[data-act="nearby-locate"]').click()
                        page.locator(".nearby-place").first.wait_for(timeout=10000)
                        scan(page,"results",width)
                        page.locator("#nearbyRegionInput").focus()
                        page.keyboard.press("Tab")
                        focused=page.evaluate("document.activeElement?.closest('#nearbyRegionForm')?.tagName")
                        if focused != "FORM":
                            raise AssertionError(f"{width}px: keyboard navigation failed near regional search")
                        print(f"PASS {width}px keyboard focus: region input to search action")
                    finally:context.close()
            finally:browser.close()
    finally:server.shutdown();server.server_close()
    print("ALL PJM-012 axe NEW-SECTION QA PASSED (full site and real screen readers not covered)")


if __name__=="__main__":main()
