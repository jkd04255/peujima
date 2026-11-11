"""PJM-042: skip-to-content preserves the active SPA route and browser history."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[1] / "index.html"


def run_case(browser, engine: str, width: int, height: int) -> None:
    mobile = width <= 850
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
        page.goto(APP.as_uri() + "#insurance", wait_until="load")
        assert page.evaluate("state.page") == "insurance"
        assert page.locator(".pjm013-skip").get_attribute("href") == "#main-content"
        page.evaluate("window.scrollTo(0, 700)")
        page.locator(".pjm013-skip").focus()
        page.keyboard.press("Enter")

        assert page.evaluate("location.hash") == "#insurance", (
            f"{engine} {width}: skip link changed route hash"
        )
        assert page.evaluate("state.page") == "insurance", (
            f"{engine} {width}: skip link changed the active page"
        )
        assert page.evaluate("document.activeElement?.id") == "main-content", (
            f"{engine} {width}: skip link did not focus main"
        )
        aligned = page.evaluate("""() => {
          const main = document.getElementById('main-content').getBoundingClientRect();
          const header = document.querySelector('.pjm013-header').getBoundingClientRect();
          return main.top >= header.height - 3 && main.top <= header.height + 8;
        }""")
        assert aligned, f"{engine} {width}: main is hidden behind sticky header"

        nav = ".pjm013-bottom-nav" if mobile else ".pjm013-desktop-nav"
        page.locator(nav + ' [data-act="nav-page"][data-val="clinics"]').click()
        assert page.evaluate("location.hash") == "#clinics"
        page.go_back(wait_until="load")
        assert page.evaluate("location.hash") == "#insurance", (
            f"{engine} {width}: skip link polluted history"
        )
        assert page.evaluate("state.page") == "insurance"
        assert not errors, f"{engine} {width}: JS errors: {errors}"
        print(f"PASS PJM-042 {engine} {width}: skip focus/route/history/sticky header")
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
    print("ALL PJM-042 skip-link route and history checks passed")


if __name__ == "__main__":
    main()
