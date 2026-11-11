"""PJM-041 route-change focus continuity regression."""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[1] / "index.html"


def run_case(browser, engine: str, width: int, height: int) -> None:
    context = browser.new_context(
        viewport={"width": width, "height": height},
        locale="ko-KR",
        reduced_motion="reduce",
        is_mobile=engine == "WebKit",
        has_touch=engine == "WebKit",
    )
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
               lambda route: route.fulfill(status=200, content_type="text/css", body=""))
    try:
        page.goto(APP.as_uri() + "#home", wait_until="load")
        nav = page.locator(".pjm013-bottom-nav" if engine == "WebKit" or width <= 850
                           else ".pjm013-desktop-nav")
        target = nav.locator('[data-act="nav-page"][data-val="clinics"]')
        target.wait_for(state="visible")
        target.focus()
        page.keyboard.press("Enter")

        main = page.locator("#main-content")
        assert page.evaluate("document.activeElement?.id") == "main-content", (
            f"{engine} {width}px: route change did not move focus to main"
        )
        assert page.locator("#pjm013PageTitle").inner_text() == "진료과·예약 체험"
        assert nav.locator('[aria-current="page"]').get_attribute("data-val") == "clinics"

        page.go_back(wait_until="load")
        assert page.evaluate("document.activeElement?.id") == "main-content", (
            f"{engine} {width}px: browser history change did not move focus to main"
        )
        assert nav.locator('[aria-current="page"]').get_attribute("data-val") == "home"
        assert page.evaluate("location.hash") == "#home"
        assert not errors, f"{engine} {width}px: JavaScript errors: {errors}"
        print(f"PASS {engine} {width}px: keyboard route and browser history focus continuity")
    finally:
        context.close()


def main() -> None:
    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        webkit = playwright.webkit.launch(headless=True)
        try:
            for width, height in [(320, 700), (390, 844), (1440, 900)]:
                run_case(chromium, "Chromium", width, height)
            run_case(webkit, "WebKit", 390, 844)
        finally:
            chromium.close()
            webkit.close()
    print("ALL PJM-041 route focus checks passed")


if __name__ == "__main__":
    main()
