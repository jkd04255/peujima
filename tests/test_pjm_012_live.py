"""PJM-012 optional REAL Kakao Web SDK smoke test (not a simulated Kakao response).

Needs PJM012_KAKAO_JS_KEY GitHub Actions secret and
JavaScript SDK domain http://localhost:8000 registered in Kakao Developers.
No user GPS collected: test browser grants a fixed Seoul coordinate.
No public Pages deployment. Never print or screenshot the key.
"""
from __future__ import annotations

import functools
import http.server
import json
import os
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
KEY = os.getenv("PJM012_KAKAO_JS_KEY", "").strip()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        return


def main():
    if not KEY:
        print("SKIP LIVE KAKAO QA: repository secret PJM012_KAKAO_JS_KEY is not configured")
        return

    if not KEY.isalnum() or not 20 <= len(KEY) <= 64:
        raise AssertionError("LIVE KAKAO QA: JavaScript key format is invalid (key value not printed)")

    # Fixed synthetic test coordinate; never use any user's actual GPS.
    lat, lng = 37.5662952, 126.9779451  # Seoul City Hall area
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                context = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    locale="ko-KR",
                    timezone_id="Asia/Seoul",
                    geolocation={"latitude": lat, "longitude": lng, "accuracy": 100},
                    permissions=["geolocation"],
                    reduced_motion="reduce",
                )
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                # Inject key in browser memory only, never in repo files or log output.
                page.add_init_script(script="window.PRZIMA_KAKAO_JS_KEY=" + json.dumps(KEY) + ";")
                page.goto("http://localhost:8000/", wait_until="domcontentloaded")
                page.locator("#nearbyTitle").wait_for(timeout=15000)
                if page.locator(".nearby-place").count() != 0:
                    raise AssertionError("Live places appeared before location request")

                page.get_by_role("button", name="내 위치로 동물병원 찾기").click()
                page.wait_for_function(
                    "() => ['ready','error','key-required','empty'].includes(state.nearby.status)",
                    timeout=45000,
                )
                status = page.evaluate("state.nearby.status")
                if status != "ready":
                    # No sensitive key or URL in diagnostics.
                    desc = page.locator("#nearby-hospitals .nearby-status").inner_text()
                    raise AssertionError(f"Live Kakao search did not finish with results: {status}; {desc}")

                count = page.locator(".nearby-place").count()
                if count < 1:
                    raise AssertionError("Live Kakao search returned no veterinary clinic cards")
                if page.locator(".nearby-place a[href^='https://place.map.kakao.com/']").count() != count:
                    raise AssertionError("Live search places have missing Kakao location links")
                if not page.evaluate("!!window.kakao?.maps?.Map"):
                    raise AssertionError("Kakao real map SDK did not load")
                if page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2"):
                    raise AssertionError("Live search produced horizontal overflow")
                if errors:
                    raise AssertionError("Live browser JS error(s) while searching")

                print(f"PASS REAL KAKAO API: localhost:8000 authorized, JS SDK loaded, "
                      f"nearby veterinary query returned {count} place(s), map rendered")
                print("No user GPS, production changes, paid API toggles, or public deployments made")
                context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
