"""PJM-044 — concise home geolocation disclosure, without losing safety context."""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[1] / "index.html"
SCREENSHOTS = APP.parent / "qa-screenshots"
NOTE = "‘내 위치로 찾기’를 누를 때 위치 확인을 시작합니다."


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
        for mode in ("all", "dog", "cat"):
            if mode != "all":
                page.locator(f'.pjm013-mode-switch [data-act="mode"][data-val="{mode}"]').click()
                page.wait_for_function("!state.loading", timeout=5000)
            assert page.evaluate("state.mode") == mode, f"{engine} {width}: mode was lost"
            note = page.locator(".pjm013-home .pjm013-search-panel .pjm013-panel-note")
            assert note.count() == 1 and note.is_visible(), f"{engine} {width}: note missing"
            assert note.inner_text() == NOTE, f"{engine} {width}: incorrect disclosure"
            assert "카카오맵 실제 병원 정보" not in note.inner_text(), (
                f"{engine} {width}: redundant platform copy remains"
            )
            assert page.locator(".pjm013-locate").is_visible(), (
                f"{engine} {width}: locate action is missing"
            )
            assert "내 위치로 찾기" in page.locator(".pjm013-locate").inner_text()
            assert page.locator(".pjm013-home-services .pjm013-service-card").count() == 3
            assert page.locator(".pjm013-service-card.is-real .pjm013-card-num").inner_text() == "실제 병원"
            assert page.locator(".pjm013-service-card.is-demo .pjm013-card-num").inner_text() == "가상 체험"
            assert page.locator(".pjm013-service-card.is-guide .pjm013-card-num").inner_text() == "정보 안내"
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"), (
                f"{engine} {width}: horizontal overflow"
            )

        if width in (320, 390):
            SCREENSHOTS.mkdir(exist_ok=True)
            page.screenshot(path=str(SCREENSHOTS / f"pjm-044-{engine.lower()}-{width}-home-note.png"))

        navigation = ".pjm013-bottom-nav" if width <= 850 else ".pjm013-desktop-nav"
        page.locator(navigation + ' [data-act="nav-page"][data-val="insurance"]').click()
        assert page.evaluate("location.hash") == "#insurance"
        assert page.locator(".pjm013-home .pjm013-panel-note").count() == 0
        page.locator(navigation + ' [data-act="nav-page"][data-val="home"]').click()
        assert page.evaluate("location.hash") == "#home"
        assert page.locator(".pjm013-home .pjm013-panel-note").inner_text() == NOTE
        assert not errors, f"{engine} {width}: JavaScript errors: {errors}"
        print(f"PASS PJM-044 {engine} {width}: concise notice, three modes, demo labels, routes")
    finally:
        context.close()


def main() -> None:
    with sync_playwright() as p:
        chromium = p.chromium.launch(headless=True, args=["--no-sandbox"])
        webkit = p.webkit.launch(headless=True)
        try:
            for width, height in [(320, 700), (390, 844), (768, 1024), (1440, 900)]:
                verify(chromium, "Chromium", width, height)
            for width, height in [(320, 700), (390, 844)]:
                verify(webkit, "WebKit", width, height)
        finally:
            chromium.close()
            webkit.close()
    print("ALL PJM-044 HOME LOCATION NOTE REGRESSION PASSED")


if __name__ == "__main__":
    main()
