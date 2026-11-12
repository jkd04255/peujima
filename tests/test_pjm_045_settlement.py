"""PJM-045 G2: 14-product payout/self-payment previews with evidence gates."""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[1] / "index.html"
OUTPUT = APP.parent / "qa-screenshots"
ALL = [
    "meritz-dog","meritz-cat","hyundai-dog","hyundai-cat",
    "db-dog","db-cat","samsung-dog","samsung-cat",
    "kb-dog","kb-cat","nh-dog","nh-cat","kakao-dog","kakao-cat"
]


def require(value, label):
    if not value:
        raise AssertionError(label)


def activate(page, insurer, care="illness"):
    page.locator("#insurerSelect").select_option(insurer)
    page.locator("#careSelect").select_option(care)
    page.locator(".insurance-button").click()
    require(page.locator(".pjm045-settlement").is_visible(),
            f"{insurer}/{care}: settlement panel missing")
    require(page.locator("#insurance select").count() == 2,
            "required entry remains exactly two dropdowns")


def numeric_model(page):
    result = page.evaluate("""() => {
        const P = window.PJM045;
        const row = {type:"visit", multiDay:false};
        const premium = {ratio:.7,deductible:30000,daily:300000,annual:15000000};
        const surgery = {type:"surgery", multiDay:false};
        const cheap = P.calculate(200000,premium,row);
        const surgeryAmount = P.calculate(2000000,
          {...premium,surgery:2500000},surgery);
        const capped = P.calculate(500000,
          {ratio:.5,deductible:30000,daily:100000,annual:7000000},row);
        const noPay = P.calculate(25000,premium,row);
        return {
          products:Object.keys(P.specs),cheap,surgeryAmount,capped,noPay,
          unknown:P.calculate(200000,null,row),
          invalid:P.calculate(200000,{ratio:1.2,deductible:0},row),
          course:P.calculate(1500000,premium,{type:"visit",multiDay:true})
        };
    }""")
    require(set(result["products"]) == set(ALL), "all fourteen insurer/species variants required")
    require(result["cheap"] == {"bill":200000,"payout":119000,
                "selfPay":81000,"beforeCap":119000}, "70% minus 30k calculation")
    require(result["surgeryAmount"]["payout"] == 1379000, "surgery-day cap not handled")
    require(result["capped"]["payout"] == 100000, "per-day cap missing")
    require(result["capped"]["selfPay"] == 400000, "capped personal amount wrong")
    require(result["noPay"]["payout"] == 0 and
            result["noPay"]["selfPay"] == 25000, "deductible floor wrong")
    require(all(result[k] is None for k in ("unknown","invalid","course")),
            "unknown ratio, invalid percentage, or multi-day case must fail closed")


def run_case(browser, engine: str, width: int, height: int):
    context = browser.new_context(
        viewport={"width": width, "height": height},
        locale="ko-KR",
        reduced_motion="reduce",
        is_mobile=engine == "WebKit",
        has_touch=engine == "WebKit",
    )
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
               lambda route: route.fulfill(status=200, content_type="text/css", body=""))
    try:
        page.goto(APP.as_uri()+"#insurance", wait_until="load")
        numeric_model(page)
        require(page.locator("#insurerSelect option").count() == 14,
                "must keep fourteen product options")
        activate(page,"meritz-dog","patella")
        require(page.locator(".pjm045-settlement .pjm045-totals").is_visible(),
                "Meritz dog approved plan lacks complete result")
        require("슬개골 교정수술비" in page.locator(
            ".pjm045-choices [data-pjm045-row][aria-pressed='true']").inner_text(),
            "patella scenario must use actual surgery, not initial consultation")
        require("가정상 본인부담금" in page.locator(".pjm045-totals").inner_text(),
                "self-payment not labeled")
        require(page.locator(".pjm045-choices [data-pjm045-plan]").count() == 3,
                "three Meritz plans not selectable")
        # Test a documented plan switch and 5만원 deductible variant.
        page.locator('[data-pjm045-plan="economy"]').click()
        page.locator('[data-pjm045-deduct="50000"]').click()
        require("5만원" in page.locator(".pjm045-deduct").inner_text(),
                "deductible options lost")

        activate(page,"meritz-cat","feline_cystitis")
        require(page.locator(".pjm045-totals").is_visible(),
                "Meritz cat official Cat & Family should calculate")
        require("반려묘" in page.locator(".pjm045-conditions").inner_text(),
                "dog terms leaked into cat")

        activate(page,"db-dog","patella")
        require(page.locator(".pjm045-totals").count() == 0,
                "DB 2610 must not auto-apply the older 2607 plan")
        page.locator('[data-pjm045-plan="db2607-standard"]').click()
        require("2607 참고" in page.locator(".pjm045-mode").inner_text(),
                "older DB plan must explicitly identify edition")
        require(page.locator(".pjm045-totals").is_visible(),
                "explicit 2607 example failed")

        for insurer in ALL:
            activate(page,insurer,"illness")
            require(page.locator(".pjm045-settlement").count() == 1,
                    "duplicate result panel")
            if insurer not in ("meritz-dog","meritz-cat","kakao-dog"):
                require(page.locator(".pjm045-totals").count() == 0,
                        f"{insurer}: insurance payout fabricated without active terms")
            else:
                require(page.locator(".pjm045-totals").count() == 1,
                        f"{insurer}: official scenario missing")
            require(page.locator(".pjm045-manual-toggle").is_visible(),
                    f"{insurer}: missing manual contract option")

        activate(page,"nh-cat","feline_block")
        require(page.locator(".pjm045-totals").count() == 0,
                "unverified NH cat must start without numbers")
        page.locator("[data-pjm045-manual]").click()
        page.locator('[data-pjm045-input="percent"]').fill("70")
        page.locator('[data-pjm045-input="deductible"]').fill("30000")
        page.locator('[data-pjm045-input="daily"]').fill("150000")
        page.locator('[data-pjm045-input="annual"]').fill("3000000")
        page.locator("[data-pjm045-apply]").click()
        require(page.locator(".pjm045-totals").count() == 1,
                "user-provided assumptions did not calculate")
        require("사용자가 입력한" in page.locator(".pjm045-mode").inner_text(),
                "manual terms must not masquerade as official")
        require(page.locator(".pjm020-result a[target='_blank']").count() == 0,
                "do not send users to insurer sites from summary")
        activate(page,"nh-dog","funeral")
        require(page.locator(".pjm045-totals").count() == 0,
                "nonmedical benefit cannot use veterinary medical claim formula")
        activate(page,"meritz-dog","neuter")
        require(page.locator(".pjm045-totals").count() == 0,
                "elective care cannot silently be treated as covered")
        require(not page.evaluate("document.documentElement.scrollWidth > window.innerWidth+2"),
                f"{engine} {width}: horizontal overflow")
        require(not errors, f"{engine} {width}: JS errors {errors}")
        if width in (320,390):
            activate(page,"meritz-dog","patella")
            OUTPUT.mkdir(exist_ok=True)
            page.screenshot(path=str(OUTPUT/f"pjm-045-{engine.lower()}-{width}-settlement.png"))
        print(f"PASS PJM-045 {engine} {width}px all 14 insurers, known/unknown premiums, self-payment, manual terms")
    finally:
        context.close()


def main():
    with sync_playwright() as p:
        chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
        webkit=p.webkit.launch(headless=True)
        try:
            for w,h in [(320,700),(390,844),(1440,900)]:
                run_case(chromium,"Chromium",w,h)
            run_case(webkit,"WebKit",390,844)
        finally:
            chromium.close()
            webkit.close()
    print("ALL PJM-045 G2 INSURANCE SETTLEMENT QA PASSED")


if __name__=="__main__":
    main()
