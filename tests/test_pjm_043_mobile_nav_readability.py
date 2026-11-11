"""PJM-043: mobile bottom navigation label legibility and layout regression."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "index.html"
OUT = ROOT / "qa-screenshots"


def verify(browser, engine: str, width: int, height: int) -> None:
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
        nav = page.locator(".pjm013-bottom-nav")
        assert nav.is_visible(), f"{engine} {width}: mobile tabs not visible"
        expected_size = 11 if width <= 380 else 12
        labels = nav.locator(".pjm013-nav-name")
        assert labels.count() == 4, f"{engine} {width}: expected four familiar routes"

        for item in nav.locator(".pjm013-nav-item").all():
            geometry = item.evaluate("""element => {
                const box = element.getBoundingClientRect();
                const label = element.querySelector('.pjm013-nav-name');
                const text = label.getBoundingClientRect();
                const size = parseFloat(getComputedStyle(label).fontSize);
                const lineHeight = parseFloat(getComputedStyle(label).lineHeight);
                return {width:box.width, height:box.height, labelWidth:text.width,
                        labelHeight:text.height, size, lineHeight};
            }""")
            assert geometry["size"] == expected_size, (
                f"{engine} {width}: label font is {geometry['size']}px, expected {expected_size}px"
            )
            assert geometry["width"] >= 44 and geometry["height"] >= 44, (
                f"{engine} {width}: mobile hit area is too small: {geometry}"
            )
            assert geometry["labelWidth"] <= geometry["width"] - 3, (
                f"{engine} {width}: tab label overflows its column: {geometry}"
            )
            assert geometry["labelHeight"] <= geometry["lineHeight"] * 1.4, (
                f"{engine} {width}: tab label wraps to another line: {geometry}"
            )

        assert not page.evaluate(
            "document.documentElement.scrollWidth > window.innerWidth + 2"
        ), f"{engine} {width}: horizontal overflow"

        OUT.mkdir(exist_ok=True)
        if width in (320, 390):
            page.screenshot(path=str(OUT / f"pjm-043-{engine.lower()}-{width}-tabs.png"))

        nav.locator('[data-act="nav-page"][data-val="insurance"]').click()
        assert page.evaluate("location.hash") == "#insurance"
        assert nav.locator('[aria-current="page"]').get_attribute("data-val") == "insurance"
        assert not errors, f"{engine} {width}: JS errors: {errors}"
        print(f"PASS PJM-043 {engine} {width}: readable single-line labels, tap targets, routes")
    finally:
        context.close()


def main() -> None:
    with sync_playwright() as p:
        chromium = p.chromium.launch(headless=True, args=["--no-sandbox"])
        webkit = p.webkit.launch(headless=True)
        try:
            for width, height in [(320, 700), (390, 844), (768, 1024)]:
                verify(chromium, "Chromium", width, height)
            for width, height in [(320, 700), (390, 844)]:
                verify(webkit, "WebKit", width, height)
        finally:
            chromium.close()
            webkit.close()
    print("ALL PJM-043 MOBILE NAVIGATION LABEL READABILITY QA PASSED")


if __name__ == "__main__":
    main()
