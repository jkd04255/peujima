"""G2-INS-02: only official, version-scoped rate choices; no invented policy caps."""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
INSURANCE = ROOT / "index.html"


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def select(page, insurer, care):
    page.locator("#insurerSelect").select_option(insurer)
    page.locator("#careSelect").select_option(care)
    page.locator(".insurance-button").click()
    need(page.locator(".pjm045-settlement").is_visible(),
         f"{insurer} {care} missing settlement panel")


def run_case(browser, engine, width, height):
    ctx = browser.new_context(
        viewport={"width": width, "height": height},
        locale="ko-KR", reduced_motion="reduce",
        is_mobile=(engine == "WebKit"),
        has_touch=(engine == "WebKit")
    )
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    try:
        page.goto(INSURANCE.as_uri()+"#insurance", wait_until="load")
        model = page.evaluate("""() => {
          const a=window.PJM045.specs;
          const mini=id=>a[id].plans.map(p=>({
            key:p.key,ratio:p.ratio,daily:p.daily,annual:p.annual,
            surgery:p.surgery,scan:p.scan,verified:p.verified
          }));
          return {dbDog:mini("db-dog"),dbCat:mini("db-cat"),
            samsungDog:mini("samsung-dog"),samsungCat:mini("samsung-cat"),
            other:["hyundai-dog","hyundai-cat","kb-dog","kb-cat",
                   "nh-dog","nh-cat","kakao-cat"].map(id=>mini(id).length),
            catSource:a["samsung-cat"].source,
            dogSource:a["samsung-dog"].source};
        }""")
        need({p["key"] for p in model["dbDog"]} >=
             {"db2610-50","db2610-70","db2607-economy",
              "db2607-standard","db2607-premium"},
             "DB dog 2610 official rates or existing 2607 old plans missing")
        need({p["key"] for p in model["dbCat"]} ==
             {"db2610-50","db2610-70"},
             "DB cat 2610 rate choices mismatched (do not copy 2607 caps)")
        for insurer in ("dbDog", "dbCat", "samsungDog", "samsungCat"):
            for plan in model[insurer]:
                if plan["key"].startswith("db2610") or plan["key"].startswith("samsung"):
                    need(plan["ratio"] in (.5,.7), f"{insurer}: unsupported ratio")
                    need(all(plan[k] is None for k in ("daily","annual","surgery","scan")),
                         f"{insurer}: undocumented policy caps copied")
                    need(not plan["verified"], f"{insurer}: partial rate is not a verified full plan")
        need(model["other"] == [0]*7, "unverified insurer acquired fabricated default plan")
        need("MP030705" in model["catSource"] and "MP030706" in model["dogSource"],
             "Samsung dog and cat official pages must have different sources")

        for insurer, care in (("db-dog","patella"),("db-cat","feline_block")):
            select(page, insurer, care)
            need(page.locator(".pjm045-totals").count() == 0,
                 f"{insurer}: must fail closed until 2610 ratio and deductible explicitly selected")
            page.locator('[data-pjm045-plan="db2610-70"]').click()
            need(page.locator(".pjm045-totals").count() == 0,
                 f"{insurer}: choosing a public ratio must not invent the deductible")
            need(page.locator(".pjm045-deduct [data-pjm045-deduct]").count() == 2,
                 f"{insurer}: confirmed deductible 30k/50k options not shown")
            page.locator('[data-pjm045-deduct="30000"]').click()
            need(page.locator(".pjm045-totals").is_visible(),
                 f"{insurer}: explicit public ratio + deductible fails to calculate")
            need("한도 일부 미확인" in page.locator(".pjm045-mode").inner_text(),
                 f"{insurer}: 2610 payout must say final caps are unverified")
            need("조건부 본인부담금" in page.locator(".pjm045-pay").inner_text(),
                 f"{insurer}: unverified result must not claim confirmed reimbursement")
            page.locator('[data-pjm045-plan="db2610-50"]').click()
            need(page.locator(".pjm045-totals").count() == 0,
                 f"{insurer}: new rate selection must require renewed deduction selection")
            page.locator('[data-pjm045-deduct="50000"]').click()
            need(page.locator(".pjm045-totals").is_visible(),
                 f"{insurer}: 50%, 5만원 case missing")
            need(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),
                 f"{insurer} {engine} {width}: horizontal overflow")

        for insurer, care in (("samsung-dog","cancer"),
                              ("samsung-cat","feline_block")):
            select(page,insurer,care)
            need(page.locator(".pjm045-totals").count() == 0,
                 f"{insurer}: Samsung without signed deductible must have no payout")
            need("50/70%" in page.locator(".pjm045-conditions").inner_text(),
                 f"{insurer}: official 2026 rates missing")
            need("80%" not in page.locator(".pjm045-conditions").inner_text(),
                 f"{insurer}: unrelated Samsung generic marketing rate leaked")
            page.locator('[data-pjm045-plan="samsung-70"]').click()
            need(page.locator(".pjm045-manual-fields").is_visible(),
                 f"{insurer}: official ratio must require manual deductible")
            need(page.locator('[data-pjm045-input="percent"]').input_value() == "70",
                 f"{insurer}: official ratio selection not prefilled")
            need(page.locator('[data-pjm045-input="deductible"]').input_value() == "",
                 f"{insurer}: contract deductible was silently invented")
            need(page.locator(".pjm045-totals").count() == 0,
                 f"{insurer}: payout appeared without deductible")
            page.locator('[data-pjm045-input="deductible"]').fill("30000")
            page.locator("[data-pjm045-apply]").click()
            need(page.locator(".pjm045-totals").is_visible(),
                 f"{insurer}: user-provided deductible not applied")
            need("사용자가 입력한" in page.locator(".pjm045-mode").inner_text(),
                 f"{insurer}: must distinguish owner assumptions from official policy")
            need(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),
                 f"{insurer} {engine} {width}: horizontal overflow")

        select(page,"nh-cat","fip")
        need(page.locator(".pjm045-totals").count() == 0,
             "NH without official original policy may not auto-calculate")
        need(not errors, f"{engine} {width}: JavaScript exceptions {errors}")
        print(f"PASS G2-INS-02 {engine} {width}: DB 2610 source-only rates, Samsung contract gate, 14 insurer safety")
    finally:
        ctx.close()


def main():
    with sync_playwright() as p:
        chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
        webkit=p.webkit.launch(headless=True)
        try:
            for width,height in ((320,700),(390,844),(1440,900)):
                run_case(chromium,"Chromium",width,height)
            run_case(webkit,"WebKit",390,844)
        finally:
            chromium.close()
            webkit.close()
    print("ALL G2-INS-02 OFFICIAL-RATE REGRESSION PASSED")


if __name__ == "__main__":
    main()
