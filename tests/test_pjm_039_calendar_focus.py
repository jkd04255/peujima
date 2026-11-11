"""PJM-039 keyboard focus visibility checks for the booking calendar."""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[1] / "index.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_case(browser, engine: str, width: int, height: int) -> None:
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
        page.locator(".doctor-choice").first.click()
        require(page.locator(".cal-slot").count() > 0,
                f"{engine} {width}px: time slots missing")

        selectors = [
            ".cal-date:not(:disabled)",
            ".cal-slot",
            ".cal-week-nav button:not(:disabled)",
        ]
        for selector in selectors:
            target = page.locator(selector).first
            target.evaluate("(el) => el.focus({focusVisible:true})")
            actual = target.evaluate("""(el) => ({
                visible: el.matches(':focus-visible'),
                width: getComputedStyle(el).outlineWidth,
                color: getComputedStyle(el).outlineColor,
                offset: getComputedStyle(el).outlineOffset
            })""")
            require(actual == {
                "visible": True,
                "width": "3px",
                "color": "rgb(53, 92, 64)",
                "offset": "3px",
            }, f"{engine} {width}px: focus indicator mismatch for {selector}: {actual}")

        require(not page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2"),
                f"{engine} {width}px: horizontal overflow")
        require(not errors, f"{engine} {width}px: JavaScript errors: {errors}")
        print(f"PASS {engine} {width}px: date/time/week controls have high-contrast keyboard focus")
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
    print("ALL PJM-039 keyboard focus checks passed")


if __name__ == "__main__":
    main()
