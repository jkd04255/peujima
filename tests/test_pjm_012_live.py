"""PJM-012 REAL Kakao Web SDK smoke: browser uses auto-injected public JS key.

Runs only on approved feature-branch push checks with the GitHub secret configured.
No user GPS used, no preview hosting, and no actual Pages deployment.
"""
from __future__ import annotations
import functools
import http.server
import os
from pathlib import Path
import sys
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_pages import build_site


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def main():
    key=os.getenv("PJM012_KAKAO_JS_KEY","").strip()
    if not key:
        print("SKIP LIVE KAKAO QA: repository secret PJM012_KAKAO_JS_KEY is not configured")
        return

    lat,lng=37.5662952,126.9779451  # FIXED Seoul City Hall, never personal GPS

    with tempfile.TemporaryDirectory(prefix="przima-live-") as tmp:
        # Simulate the eventual real static site: key is auto-injected by the build,
        # never supplied via the visitor's sessionStorage or Playwright init_script.
        dist=Path(tmp)/"site"
        build_site(dist,key)
        handler=functools.partial(QuietHandler,directory=str(dist))
        server=http.server.ThreadingHTTPServer(("127.0.0.1",8000),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
                try:
                    context=browser.new_context(
                        viewport={"width":390,"height":844},
                        locale="ko-KR",timezone_id="Asia/Seoul",
                        geolocation={"latitude":lat,"longitude":lng,"accuracy":100},
                        permissions=["geolocation"],reduced_motion="reduce",
                    )
                    page=context.new_page()
                    errors=[]
                    page.on("pageerror",lambda exc:errors.append(str(exc)))
                    page.goto("http://localhost:8000/",wait_until="domcontentloaded")
                    page.locator("#nearbyTitle").wait_for(timeout=15000)

                    if not page.evaluate("Boolean(window.PRZIMA_KAKAO_JS_KEY)"):
                        raise AssertionError("Public JS key was not auto-configured by the release build")
                    if page.locator("#nearbyKeyForm").count():
                        raise AssertionError("Visitors must not be prompted for a development key")
                    if page.locator(".nearby-place").count():
                        raise AssertionError("Places appeared before GPS permission request")

                    page.get_by_role("button",name="내 위치로 동물병원 찾기").click()
                    page.wait_for_function(
                        "() => ['ready','error','key-required','empty'].includes(state.nearby.status)",
                        timeout=45000,
                    )
                    status=page.evaluate("state.nearby.status")
                    if status!="ready":
                        description=page.locator("#nearby-hospitals .nearby-status").inner_text()
                        raise AssertionError(f"Real Kakao search failed: {status} / {description}")

                    count=page.locator(".nearby-place").count()
                    if count < 1:
                        raise AssertionError("Real Kakao query returned no veterinary place cards")
                    if page.locator(".nearby-place a[href^='https://place.map.kakao.com/']").count()!=count:
                        raise AssertionError("Some real Kakao places have no detail link")
                    if not page.evaluate("Boolean(window.kakao?.maps?.Map)"):
                        raise AssertionError("Real Kakao map SDK did not load")
                    if page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2"):
                        raise AssertionError("Live search caused horizontal overflow")
                    if errors:
                        raise AssertionError("JavaScript runtime error(s) in real SDK test")
                    print(f"PASS REAL KAKAO API: auto-built public key works without visitor entry, "
                          f"localhost:8000 authorized, {count} veterinary place(s) from fixed Seoul coordinate")
                    print("Live browser map initialized; no public deploy or personal geolocation used")
                    context.close()
                finally:browser.close()
        finally:server.shutdown();server.server_close()


if __name__=="__main__":main()
