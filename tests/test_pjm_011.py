"""PJM-011 browser regression checks on the feature branch only."""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[1] / "index.html"
OUT = Path(__file__).resolve().parents[1] / "qa-screenshots"
OUT.mkdir(exist_ok=True)
KST = timezone(timedelta(hours=9))
ISSUES = []

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def run_case(browser, width, height):
    context = browser.new_context(viewport={"width":width,"height":height}, timezone_id="Asia/Seoul", locale="ko-KR", reduced_motion="reduce")
    page = context.new_page()
    page.clock.install(time=datetime(2026,11,7,15,0,tzinfo=KST))
    errors=[]
    page.on("pageerror", lambda e: errors.append(str(e)))
    try:
        page.goto(APP.as_uri()+"#clinics", wait_until="load")
        page.locator(".clinic-explore-card").first.wait_for(timeout=15000)
        require(page.locator(".clinic-explore-card").count()==5, f"{width}: all-mode catalog should show five synthetic clinics")
        require(page.locator(".cal-date").count()==0, f"{width}: catalog unexpectedly includes calendar")
        require(page.locator(".doctor-choice").count()==0, f"{width}: catalog unexpectedly includes doctor selector")
        if width==390:page.screenshot(path=str(OUT/"390-catalog.png"),full_page=True)

        page.locator(".clinic-explore-card").first.click()
        page.locator(".clinic-profile-card h2").wait_for()
        require(page.locator(".clinic-profile-card h2").inner_text()=="포근한 동물메디컬센터", f"{width}: wrong clinic opened")
        require(page.locator(".cal-date").count()==0, f"{width}: clinic profile should hide calendar before reservation")
        require(page.locator(".doctor-choice").count()==0, f"{width}: doctor selector visible before reservation")
        if width==390:page.screenshot(path=str(OUT/"390-detail.png"),full_page=True)

        page.locator('[data-act="clinic-reserve"]').click()
        require(page.locator(".cal-date").count()==7, f"{width}: 7-day timeline missing after booking")
        require(page.locator(".doctor-choice").count()==2, f"{width}: multi-doctor clinic should require doctor selection")
        require(page.locator(".cal-slot").count()==0, f"{width}: doctor not selected but time slots visible")
        if width==390:page.screenshot(path=str(OUT/"390-booking-open.png"),full_page=True)

        page.locator(".doctor-choice").first.click()
        require(page.locator(".cal-date").count()==7, f"{width}: dates disappeared after selecting doctor")
        require(page.locator(".cal-slot").count()>0, f"{width}: no future synthetic slots after selecting doctor")
        page.locator(".cal-slot").first.click()
        require(page.locator(".cal-next").is_enabled(), f"{width}: choosing time should enable confirmation")
        page.locator(".cal-next").click()
        require(page.locator(".booking-modal").is_visible(), f"{width}: booking modal missing")
        page.locator("#reasonSelect").select_option("other")
        page.locator('[data-act="book-done"]').click()
        require(page.locator("#bookingValidation").is_visible(), f"{width}: missing required other-text validation")
        page.locator("#otherReasonInput").fill("식욕이 줄고 기침을 합니다")
        page.locator('[data-act="book-done"]').click()
        require(page.locator(".booking-modal-done").count()==1, f"{width}: completion preview missing")
        require("포근한 동물메디컬센터" in page.locator(".booking-receipt").inner_text(), f"{width}: booking receipt points at wrong clinic")
        page.locator('[data-act="booking-insurance"]').click()
        require(not page.locator(".booking-modal").count(), f"{width}: insurance transition left modal open")
        require(page.locator("#insurance").count()==1, f"{width}: insurance page missing after booking transition")
        page.locator('[data-act="nav-page"][data-val="clinics"]:visible').first.click()

        page.locator('[data-act="clinic-collapse"]').click()
        require(page.locator(".cal-date").count()==0, f"{width}: calendar remained visible after collapse")
        page.locator('[data-act="clinic-back"]').click()
        require(page.locator(".clinic-explore-card").count()==5, f"{width}: back did not restore listing")
        require(not errors, f"{width}: JS errors: {errors}")
        overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
        require(not overflow, f"{width}: horizontal overflow")
        print(f"PASS {width}x{height}: list > detail > booking > confirmation > insurance > collapse > list")
    finally:
        context.close()

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        try:
            for width,height in [(320,700),(390,844),(768,1024),(1440,900)]:
                run_case(browser,width,height)
        finally:
            browser.close()
    print("ALL PJM-011 browser cases passed")

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(f"PJM-011 QA FAILURE: {exc}",file=sys.stderr)
        raise
