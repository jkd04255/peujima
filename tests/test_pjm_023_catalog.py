"""PJM-023 expanded insurance product and condition taxonomy.
Public product guides only; do not infer real policy acceptance or reimbursements.
"""
from __future__ import annotations
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class Silent(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def need(x,msg):
    if not x:raise AssertionError(msg)

def reveal_notes(page):
    """Open the new single footer disclosure for legacy policy-detail checks."""
    panel=page.locator(".pjm030-fineprint")
    assert panel.count()==1, "bottom evidence disclosure must exist"
    if panel.get_attribute("open") is None:
        page.locator(".pjm030-fineprint > summary").click()

def run_case(browser,url,w,h,engine):
    context=browser.new_context(viewport={"width":w,"height":h},locale="ko-KR",
       reduced_motion="reduce",has_touch=(engine=="WebKit"),is_mobile=(engine=="WebKit"))
    page=context.new_page();errors=[]
    page.on("pageerror",lambda err:errors.append(str(err)))
    page.route("https://cdn.jsdelivr.net/gh/sun-typeface/**",
       lambda route:route.fulfill(status=200,content_type="text/css",body="/* test font offline */"))
    try:
        page.goto(url+"#insurance",wait_until="load")
        need(page.locator("#insurance select").count()==2,"must require exactly 2 selections")
        stats=page.evaluate("""() => ({
          c:window.PJM023?.cares.length,i:PJM019.insurers.length,
          care:PJM019.careTypes.length,
          catalog:!!window.PJM023,
          species:!!PJM019.insurers.find(x=>x.id==="nh-cat"),
          official:!!PJM019.insurers.find(x=>x.id==="samsung-dog")
        })""")
        need(stats["catalog"] and stats["i"]==14 and stats["c"]==42 and
             stats["care"]==52 and stats["species"] and stats["official"],
             f"catalog counts or data failed: {stats}")
        need(page.locator("#careSelect optgroup").count()>=7,"grouped care taxonomy absent")
        need(page.locator("#careSelect option").count()==47,
             "dog should display 10 base, 30 shared conditions and 7 extra-benefit/claims topics")
        policyFacts=page.evaluate("""() => {
          const p=PJM023;
          return {
            hyundaiForeign:p.focus["hyundai-dog"].foreignbody,
            hyundaiMedicine:p.focus["hyundai-dog"].allergy,
            hyundaiMRI:p.focus["hyundai-dog"].mri,
            kbChemo:p.focus["kb-dog"].chemo,
            kbMRI:p.focus["kb-dog"].mri,
            samsungKidney:p.focus["samsung-dog"].kidney,
            samsungRatio:p.products["samsung-dog"][2],
            meritzFIP:p.focus["meritz-cat"].fip,
            catVaccine:p.focus["samsung-cat"].feline_herpes
          };
        }""")
        need("2회" in policyFacts["hyundaiForeign"],"Hi2601 foreign-body rider annual 2 not shown")
        need("12회" in policyFacts["hyundaiMedicine"] and "90일" in policyFacts["hyundaiMedicine"],
             "Hi2601 special-drug benefit annual 12 / 90-day rule missing")
        need("1회" in policyFacts["hyundaiMRI"],"Hi2601 MRI/CT annual 1 missing")
        need("90일" in policyFacts["kbChemo"] and "1종" in policyFacts["kbMRI"],
             "KB 26.01 major-treatment waiting or same-day restriction missing")
        need("90일" in policyFacts["samsungKidney"] and "50%" in policyFacts["samsungRatio"],
             "Samsung specific disease waiting or actual selectable ratio mismatch")
        need("90일" in policyFacts["meritzFIP"],"Meritz feline FIP exclusion not shown")
        need("예방접종" in policyFacts["catVaccine"],"Samsung cat prior vaccination condition missing")

        # PJM-026: policy dates and provenance must not get silently generalized.
        evidence=page.evaluate("""() => ({
            db:PJM023.evidence["db-dog"],
            kb:PJM023.evidence["kb-dog"],
            nh:PJM023.evidence["nh-cat"],
            hy:PJM023.evidence["hyundai-dog"],
            insurerNH:PJM023.insurers.find(x=>x.id==="nh-dog").source
        })""")
        need(evidence["db"]["grade"]=="B" and "2607" in evidence["db"]["warning"],
             "DB 2610 vs 2607 product-page conflict unreported")
        need(evidence["kb"]["grade"]=="A" and "26.07" in evidence["kb"]["warning"],
             "KB 26.01 proof must not be claimed for 26.07")
        need(evidence["nh"]["grade"]=="D" and "nhfire.co.kr" in evidence["insurerNH"],
             "NH original unverified or wrong official company domain")
        need(evidence["hy"]["grade"]=="A","Hyundai Hi2601 original policy status lost")
        page.locator("#insurerSelect").select_option("db-dog")
        page.locator("#careSelect").select_option("chemo")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("2610" in page.locator(".pjm026-source-meta").inner_text()
             and "2607" in page.locator(".pjm026-version-warning").inner_text(),
             "DB version conflict not visible in simplified in-app answer")
        need("상품 안내 확인" in page.locator(".pjm030-evidence-note").inner_text(),
             "B grade wrongly presented as original policy PDF")
        page.locator("#insurerSelect").select_option("kb-dog")
        page.locator("#careSelect").select_option("chemo")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("26.01" in page.locator(".pjm026-version-warning").inner_text()
             and "26.07" in page.locator(".pjm026-version-warning").inner_text(),
             "KB original policy mismatch not communicated on screen")
        need("A · 일부 약관 원문 확인" in page.locator(".pjm030-evidence-note").inner_text(),
             "KB policy PDF audit badge missing")
        need(page.locator(".pjm020-result a[target='_blank']").count()==0,
             "in-app policy explanation must not redirect to insurer")
        page.locator("#insurerSelect").select_option("kb-dog")
        page.locator("#careSelect").select_option("chemo")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        result=page.locator(".pjm020-result")
        need(result.is_visible(),"new policy guidance missing")
        need("금쪽같은" in result.inner_text(),"KB-specific official summary not shown")
        need("30만원" in page.locator(".pjm023-focus").inner_text(),
             "KB antitumor drug published cap missing")
        need(page.locator(".pjm023-fact").count()>=3,"coverage facts missing")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "unverified KB benefits must never be calculated")
        need(page.locator(".pjm023-more").count()==1,"terms details not in-app")
        page.locator(".pjm023-more summary").click()
        need(page.locator(".pjm023-more[open]").is_visible(),"cannot expand conditions")
        need("면책" in page.locator(".pjm023-more").inner_text(),"exclusions omitted")

        # PJM-029: insurer-issued disclosure vs unreviewed official PDF body
        # and third-party 26.07 interpretations must remain distinguishable.
        snapshot=page.evaluate("""() => ({
            products:PJM023.kb2607.products.map(x=>({
                code:x.code,species:x.species,channel:x.channel,
                sourceType:x.sourceType,policyFile:x.policyFile
            })),
            dog:PJM023.kb2607.secondary["kb-dog"],
            cat:PJM023.kb2607.secondary["kb-cat"],
            gradeDog:PJM023.evidence["kb-dog"].grade,
            gradeCat:PJM023.evidence["kb-cat"].grade
        })""")
        need({x["code"] for x in snapshot["products"]}==
             {"25343","25344","25345","25346","25357","25358"},
             "KB 26.07 officially listed product identity matrix changed")
        need(sorted(x["channel"] for x in snapshot["products"] if x["species"]=="dog")==
             ["다이렉트형","일반형","일반형(추가 공시 코드)"],"dog general and direct policy must be distinct")
        need(sorted(x["channel"] for x in snapshot["products"] if x["species"]=="cat")==
             ["다이렉트형","일반형","일반형(추가 공시 코드)"],"cat general and direct policy must be distinct")
        need(snapshot["gradeDog"]=="A" and snapshot["gradeCat"]=="D",
             "KB verified 26.01 PDF must not become a verified 26.07 cat policy")
        need(all(x["sourceType"].startswith("official_listing") for x in snapshot["products"]),
             "never classify undecoded KB 26.07 PDF as read original")
        need("30일" in snapshot["cat"]["illness"] and
             "원문" in snapshot["cat"]["illness"],
             "secondary 26.07 cat guidance must be explicitly unverified")
        page.locator("#insurerSelect").select_option("kb-dog")
        page.locator("#careSelect").select_option("mri")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("25343" in page.locator(".pjm029-kb-editions").inner_text() and
             "25357" in page.locator(".pjm029-kb-editions").inner_text() and
             "25344" in page.locator(".pjm029-kb-editions").inner_text(),
             "KB dog general and direct product codes not displayed")
        need(not page.locator(".pjm029-kb-details").is_visible(),
             "secondary 26.07 notes should not clutter default result")
        page.locator(".pjm023-more summary").click()
        need("2차 해설" in page.locator(".pjm029-kb-details").inner_text() and
             "원문" in page.locator(".pjm029-kb-details").inner_text(),
             "26.07 secondary and original document status incorrectly conflated")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "unverified 26.07 MRI claim amount cannot be calculated")
        page.locator("#insurerSelect").select_option("kb-cat")
        page.locator("#careSelect").select_option("feline_cystitis")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("25345" in page.locator(".pjm029-kb-editions").inner_text() and
             "25358" in page.locator(".pjm029-kb-editions").inner_text() and
             "25346" in page.locator(".pjm029-kb-editions").inner_text() and
             "25343" not in page.locator(".pjm029-kb-editions").inner_text(),
             "KB dog product codes leaked into cat result")
        page.locator(".pjm023-more summary").click()
        need("비뇨기" in page.locator(".pjm029-kb-details").inner_text() and
             "원문" in page.locator(".pjm029-kb-details").inner_text(),
             "cat 26.07 urinary caveat missing")
        need(page.locator(".pjm027-clause-origin").count()==0,
             "KB dog 26.01 source must never be displayed for KB cat")
        need(page.locator(".pjm020-result a[target='_blank']").count()==0,
             "KB 26.07 in-app explanation must not redirect")
        page.locator("#insurerSelect").select_option("nh-dog")
        page.locator("#careSelect").select_option("mri")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need(page.locator(".pjm029-kb-editions").count()==0,
             "KB 26.07 label must not leak into another insurer")
        
        # PJM-027: only KB dog 26.01 signed original clauses can be explained.
        page.locator("#insurerSelect").select_option("kb-dog")
        for care,words in [
            ("funeral",("30일","동물장묘업체","보상비율")),
            ("boarding",("상해","180일","추가 식대")),
            ("liability",("1,000만원","사고당","법률상"))
        ]:
            page.locator("#careSelect").select_option(care)
            page.locator(".insurance-button").click()
            reveal_notes(page)
            detail=page.locator(".pjm023-focus").inner_text()
            for word in words:
                need(word in detail,f"KB 26.01 {care} term {word} missing")
            origin=page.locator(".pjm027-clause-origin")
            need(origin.is_visible() and "26.01" in origin.inner_text(),
                 f"KB 26.01 {care} exact policy edition and location absent")
            need("26.07" in page.locator(".pjm026-version-warning").inner_text(),
                 "old KB policy must not be assigned to the 26.07 contract")
            need(page.locator(".pjm021-plan-amounts").count()==0,
                 "extra KB benefits must not result in invented payment")
            need(page.locator(".pjm020-result a[target='_blank']").count()==0,
                 "the result should remain inside PRZIMA")
            # PJM-028: show original exclusions only on explicit expansion,
            # keeping the default two-selection result concise.
            need(page.locator(".pjm028-clause-details").count()==1,
                 "KB 26.01 supplement must be available in details")
            need(not page.locator(".pjm028-clause-details").is_visible(),
                 "policy exclusions should stay collapsed by default")
            page.locator(".pjm023-more summary").click()
            details=page.locator(".pjm028-clause-details").inner_text()
            must={"funeral":("장례확인서","임시 안치"),
                  "boarding":("위탁비용 영수증","질병입원"),
                  "liability":("3만원","동거","질병 전염")}
            for word in must[care]:
                need(word in details or word in detail,
                     f"KB 26.01 {care} missing verified claim exclusion: {word}")
            if care=="liability":
                need("타인 소유 반려동물" in detail,
                     "KB liability must not be overclaimed as all property damage")
                need("사고당 자기부담금 3만원" in detail,
                     "KB accident-level deductible lost")
        page.locator("#insurerSelect").select_option("kb-cat")
        page.locator("#careSelect").select_option("boarding")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need(page.locator(".pjm027-clause-origin").count()==0 and
             page.locator(".pjm028-clause-details").count()==0,
             "KB 26.01 dog boarding terms must never be copied to KB cat")
        page.locator("#insurerSelect").select_option("samsung-dog")
        page.locator("#careSelect").select_option("funeral")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need(page.locator(".pjm027-clause-origin").count()==0,
             "KB 26.01 clause must not appear in other insurers")

        page.locator("#insurerSelect").select_option("nh-cat")
        need(page.locator(".pjm020-result").count()==0,"stale KB result after insurer change")
        need(page.locator("#careSelect option").count()==49,"cat topic choices and shared benefits not present")
        page.locator("#careSelect").select_option("hospital")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need(page.locator(".pjm021-fee-guide").count()==0 and
             page.locator(".pjm031-published").count()==0,
             "cat admission must hide the dog-only median without an empty fee panel")
        page.locator("#careSelect").select_option("feline_cystitis")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        txt=page.locator(".pjm020-result").inner_text()
        need("원문" in txt and "미검증" in txt,"NH unverified contract must be labeled")
        need("비뇨기" in txt,"cat urinary treatment-specific note missing")
        need(page.locator(".pjm021-plan-amounts").count()==0,"unverified NH must have no payout")

        page.locator("#insurerSelect").select_option("samsung-dog")
        need(page.locator("#careSelect").input_value()=="illness","cat-only care must reset for dog")
        need(page.locator("#careSelect option").count()==47,"cat-only care leaked to dog")
        page.locator("#careSelect").select_option("allergy")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("삼성화재" in page.locator(".pjm020-result").inner_text(),
             "new insurer missing in-app facts")
        need("50%" in page.locator(".pjm023-coverage").inner_text() and
             "70%" in page.locator(".pjm023-coverage").inner_text(),
             "Samsung detailed product 50/70 percentage missing")
        need("NH펫앤미든든" not in page.locator(".pjm023-coverage").inner_text(),
             "old insurer's source leaked into Samsung result")

        page.locator("#insurerSelect").select_option("kakao-dog")
        page.locator("#careSelect").select_option("surgery")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("수술당일형" in page.locator(".pjm023-coverage").inner_text(),
             "KakaoPay surgery-only vs inpatient/outpatient plans not shown")
        need("카카오페이손해보험" in page.locator(".pjm023-coverage").inner_text(),
             "KakaoPay official coverage profile not shown")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "KakaoPay must not reuse Meritz/DB payout examples")

        # PJM-025: optional nonmedical benefit choices do not fabricate a claim or
        # assume a dog-only coverage applies to cats or unrelated insurers.
        page.locator("#insurerSelect").select_option("db-dog")
        page.locator("#careSelect").select_option("dog_bite_training")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        txt=page.locator(".pjm020-result").inner_text()
        need("15만원" in txt and "10회" in txt and "2주" in txt,
             "DB dog bite training rider public conditions missing")
        need(page.locator(".pjm023-extra-warning").is_visible(),
             "separately insured benefit not visually separated from medical")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "no non-medical benefit payout without actual contract")
        need(page.locator(".pjm021-fee-guide").count()==0,
             "non-medical benefits must not show vet fee medians")
        page.locator("#careSelect").select_option("dog_large")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("10회" in page.locator(".pjm023-focus").inner_text(),
             "DB dog large-dog rider annual limit missing")
        page.locator("#careSelect").select_option("mri")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("30일" in page.locator(".pjm023-focus").inner_text() and
             "90일" in page.locator(".pjm023-focus").inner_text(),
             "DB 2610 MRI 30-day wait must be distinguished from chemo 90-day wait")
        page.locator("#careSelect").select_option("chemo")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("90일" in page.locator(".pjm023-focus").inner_text() and
             "6회" in page.locator(".pjm023-focus").inner_text(),
             "DB 2610 oncology 90-day waiting / six treatments omitted")
        page.locator("#careSelect").select_option("surgery")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("30일" in page.locator(".pjm023-focus").inner_text() and
             "연 1회" in page.locator(".pjm023-focus").inner_text(),
             "DB 2610 specific high-cost surgery waiting / frequency omitted")
        page.locator("#insurerSelect").select_option("kb-dog")
        page.locator("#careSelect").select_option("claim_docs")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("30만원" in page.locator(".pjm023-focus").inner_text(),
             "KB 30만원 claim documentation threshold omitted")
        need("업로드" in page.locator(".pjm020-result").inner_text(),
             "user must not be prompted to upload personal claim records")
        page.locator("#insurerSelect").select_option("nh-cat")
        page.locator("#careSelect").select_option("boarding")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need("판매 대리점" in page.locator(".pjm023-focus").inner_text(),
             "NH seller evidence must not be called official terms")
        page.locator("#insurerSelect").select_option("meritz-cat")
        need(page.locator("#careSelect option[value='dog_bite_training']").count()==0,
             "dog-only bite benefit leaked to cat")
        page.locator("#insurerSelect").select_option("meritz-dog")

        page.locator("#careSelect").select_option("illness")
        page.locator(".insurance-button").click()
        reveal_notes(page)
        need(page.locator(".pjm021-plan-amounts > div").count()==3,
             "Meritz payout simulation changed")
        need("메리츠" in page.locator(".pjm023-coverage").inner_text(),
             "Meritz official product overview missing")
        need(not page.evaluate("document.documentElement.scrollWidth > innerWidth+2"),
             f"{engine} {w} horizontal overflow")
        page.goto(url+"#home",wait_until="load")
        need(page.locator(".pjm013-service-card").count()==3,"home routes changed")
        page.goto(url+"#nearby",wait_until="load")
        need(page.locator(".nearby-geo").is_visible(),"map entry changed")
        need(not errors,f"JavaScript exceptions {engine} {w}: {errors}")
        print(f"PASS PJM-025 {engine} {w}px 14 products / 52 care and supplemental benefit topics / sourced details")
    finally:
        context.close()

def main():
    srv=http.server.ThreadingHTTPServer(("127.0.0.1",0),
       functools.partial(Silent,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                url=f"http://127.0.0.1:{srv.server_port}/"
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_case(chromium,url,w,h,"Chromium")
                run_case(webkit,url,390,844,"WebKit")
            finally:chromium.close();webkit.close()
    finally:srv.shutdown();srv.server_close()
    print("PJM-025 extended insurance benefits and QA passed")

if __name__=="__main__":main()
