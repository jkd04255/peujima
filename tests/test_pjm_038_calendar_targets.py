"""PJM-038 calendar week-navigation touch-target regression.

Checks the existing booking preview calendar in Chromium and WebKit viewport
profiles. This is browser automation, not a physical iPhone Safari test.
"""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[1] / "index.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_case(browser, width: int, height: int, engine: str) -> None:
    context = browser.new_context(
        viewport={"width": width, "height": height},
        locale="ko-KR",
        timezone_id="Asia/Seoul",
        reduced_motion="reduce",
        is_mobile=engine == "WebKit",
        has_touch=engine == "WebKit",
    )
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(APP.as_uri() + "#clinics", wait_until="load")
        page.locator(".clinic-explore-card").first.wait_for(timeout=15000)
        page.locator(".clinic-explore-card").first.click()
        page.locator("[data-act='clinic-reserve']").click()

        require(page.locator(".cal-date").count() == 7,
                f"{engine} {width}px: seven-day calendar missing")
        controls = page.locator(".cal-week-nav button")
        require(controls.count() == 2,
                f"{engine} {width}px: previous/next week controls missing")
        for control in controls.all():
            box = control.bounding_box()
            require(box is not None, f"{engine} {width}px: week control not rendered")
            if width <= 620:
                require(box["width"] >= 44 and box["height"] >= 44,
                        f"{engine} {width}px: mobile week target below 44px: {box}")
            else:
                require(box["width"] == 34 and box["height"] == 34,
                        f"{engine} {width}px: desktop control dimensions changed: {box}")

        require(not page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2"),
                f"{engine} {width}px: horizontal overflow")
        require(not errors, f"{engine} {width}px: JavaScript errors: {errors}")
        print(f"PASS {engine} {width}x{height}: calendar arrows, seven-day strip, no overflow")
    finally:
        context.close()


def main() -> None:
    with sync_playwright() as playwright:
        cases = [
            (playwright.chromium.launch(headless=True, args=["--no-sandbox"]), "Chromium",
             [(320, 700), (390, 844), (768, 1024), (1440, 900)]),
            (playwright.webkit.launch(headless=True), "WebKit", [(320, 700), (390, 844)]),
        ]
        for browser, engine, sizes in cases:
            try:
                for width, height in sizes:
                    run_case(browser, width, height, engine)
            finally:
                browser.close()
    print("ALL PJM-038 calendar touch-target checks passed")


if __name__ == "__main__":
    main()
