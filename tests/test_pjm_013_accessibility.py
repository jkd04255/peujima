"""PJM-013: new home navigation accessibility and keyboard smoke (axe WCAG A/AA).

Focus on the NEW service hub, header and mobile bottom tab bar. Existing
legacy sections have separate regressions and are NOT covered by this scan.
"""
from __future__ import annotations
import functools
import http.server
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
AXE=ROOT/"node_modules/axe-core/axe.min.js"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def audit(page,selector,width):
    result=page.evaluate("""async selector => {
      const root=document.querySelector(selector);
      if(!root) throw new Error('new navigation audit scope missing: '+selector);
      return axe.run(root,{
        runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']},
        resultTypes:['violations']
      });
    }""",selector)
    if result["violations"]:
        problems=[]
        for issue in result["violations"]:
            problems.append(f"{issue['id']} impact={issue.get('impact')} nodes=" +
                repr([n.get("target") for n in issue.get("nodes",[])[:5]]))
        raise AssertionError(f"axe {width}px {selector}: "+" / ".join(problems))
    print(f"PASS PJM-013 axe WCAG A/AA {width}px {selector}: zero automated findings")

def main():
    if not AXE.is_file():
        raise FileNotFoundError("Install axe-core@4.10.3 for QA")
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),
      functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        origin=f"http://127.0.0.1:{server.server_port}/"
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    context=browser.new_context(
                        viewport={"width":w,"height":h},locale="ko-KR",reduced_motion="reduce"
                    )
                    page=context.new_page()
                    try:
                        page.goto(origin,wait_until="load")
                        page.add_script_tag(path=str(AXE))
                        for scope in (".pjm013-home",".pjm013-header"):
                            audit(page,scope,w)
                        if w<=850:audit(page,".pjm013-bottom-nav",w)
                        page.locator("#pjm013RegionInput").focus()
                        page.keyboard.press("Tab")
                        if page.evaluate("document.activeElement?.closest('#pjm013RegionForm')") is None:
                            raise AssertionError(f"{w}px: keyboard can't reach home search submit")
                        print(f"PASS PJM-013 {w}px: home search keyboard navigation")
                    finally:context.close()
            finally:browser.close()
    finally:server.shutdown();server.server_close()
    print("ALL PJM-013 NEW NAVIGATION ACCESSIBILITY QA PASSED")

if __name__=="__main__":main()
