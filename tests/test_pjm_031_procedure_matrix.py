"""PJM-031 all 52 care topics have real subprocedure-level names.
The 2025 official price registry does not contain surgery or chemotherapy charges:
no invented procedure price, automatic insurance benefit, or extra input.
"""
from __future__ import annotations

import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def need(condition,message):
    if not condition:raise AssertionError(message)

def start_page(browser,url,w,h,engine):
    ctx=browser.new_context(viewport={"width":w,"height":h},locale="ko-KR",
        reduced_motion="reduce",has_touch=(engine=="WebKit"),
        is_mobile=(engine=="WebKit"))
    page=ctx.new_page()
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.goto(url+"#insurance",wait_until="load")
    return ctx,page,errors

def result_for(page,care):
    page.locator("#careSelect").select_option(care)
    page.locator(".insurance-button").click()
    need(page.locator(".pjm020-result").is_visible(),
         "insurance result failed for "+care)
    return page.locator(".pjm031-procedures")

def check_examples(page):
    page.locator("#insurerSelect").select_option("meritz-dog")
    p=result_for(page,"patella")
    txt=p.inner_text()
    need("슬개골 교정수술비" in txt and
         "수술 후 재활" in txt and "X-ray" in txt,
         "patella should include surgery, imaging and rehabilitation")
    surgery=p.locator(".pjm031-procedure-item").filter(has_text="슬개골 교정수술비")
    need(surgery.count()==1 and
         "수술·시술비 별도 확인" in surgery.inner_text(),
         "patella surgery cost must not be fabricated")
    need(page.locator(".pjm031-procedure-caution").count()==1 and
         not page.locator(".pjm031-procedure-caution").is_visible(),
         "extra explanation must remain inside compact bottom fine print")

    p=result_for(page,"cancer")
    txt=p.inner_text()
    for label in ["종양 절제·암수술비","항암약물치료비",
                  "방사선치료비","세포검사·조직검사비","암 병기 평가"]:
        need(label in txt,"oncology missing "+label)
    for label in ["암수술비","항암약물치료비","방사선치료비"]:
        row=p.locator(".pjm031-procedure-item").filter(has_text=label)
        need(row.count()==1 and
             ("비용 확인" in row.locator(".pjm031-price").inner_text() or
              "별도 확인" in row.locator(".pjm031-price").inner_text()),
             "unverified cancer treatment price misrepresented: "+label)
        need(not row.locator(".pjm031-published").count(),
             "no nationwide median for "+label)
    need(page.locator(".pjm021-plan-amounts").count()==0,
         "surgery and cancer diagnosis must not imply a payout")
    p=result_for(page,"mri")
    txt=p.inner_text()
    need("791,500원" in txt and "600,000원" in txt,
         "only existing published MRI/CT single-fee medians should be reused")
    need(p.locator(".pjm031-published").count()==2,
         "MRI and CT should be separate published price rows")
    p=result_for(page,"foreignbody")
    need("내시경 이물 제거비" in p.inner_text() and
         "장절개·위절개 수술비" in p.inner_text(),
         "foreign-body removal must include intervention and surgery")
    p=result_for(page,"cruciate")
    need("십자인대 안정화 수술비" in p.inner_text(),
         "cruciate ligament surgery omitted")
    p=result_for(page,"heart")
    need("심초음파 검사비" in p.inner_text() and
         "심장 약물치료비" in p.inner_text(),
         "heart examination/treatment omitted")
    p=result_for(page,"surgery")
    need("정형·신경·종양 수술비" in p.inner_text(),
         "surgery topic needs distinct techniques")

    page.locator("#insurerSelect").select_option("meritz-cat")
    p=result_for(page,"feline_block")
    need("회음부 요도루조성술비" in p.inner_text() and
         "도뇨비" in p.inner_text(),
         "feline blockage should include surgery and catheterization")
    p=result_for(page,"hospital")
    need("반려견 1일 입원비" not in p.inner_text(),
         "dog-only national fee leaked into cat procedures")
    p=result_for(page,"vaccine")
    need("반려견 종합백신 접종" not in p.inner_text(),
         "dog-only vaccine fee leaked into cat procedures")
    p=result_for(page,"fip")
    need("항바이러스 치료비" in p.inner_text(),
         "feline FIP treatment omitted")
    page.locator("#insurerSelect").select_option("nh-dog")
    need(page.locator(".pjm020-result").count()==0,
         "stale previous insurer procedures remained")
    p=result_for(page,"boarding")
    need("보호자 입원 사유" in p.inner_text(),
         "nonclinical benefit rows must be covered")
    need("계약·특약별 확인" in p.inner_text(),
         "benefit items must not carry invented treatment fees")

def check_matrix(page):
    total=page.evaluate("""() => {
      const ids=PJM019.careTypes.map(x=>x.id);
      const entries=PJM031.entries;
      return {
        expected:ids.length,
        actual:Object.keys(entries).length,
        missing:ids.filter(id=>!entries[id]),
        extras:Object.keys(entries).filter(id=>!ids.includes(id)),
        incomplete:Object.entries(entries).filter(([id,rows])=>
            rows.length<4 || rows.some(row=>row.length<3 ||
              row.length>4 || !row[0] || !row[1] || !row[2])).map(x=>x[0]),
        count:Object.values(entries).reduce((n,v)=>n+v.length,0),
        selects:document.querySelectorAll("#insurance select").length
      };
    }""")
    need(total["expected"]==52 and total["actual"]==52 and
         not total["missing"] and not total["extras"] and
         not total["incomplete"] and total["count"]>=250 and
         total["selects"]==2,
         "52-care taxonomy is incomplete or changed inputs: "+str(total))
    seen=set()
    # All selectable entries are checked in their correct animal context.
    for insurer in ("meritz-dog","meritz-cat"):
        page.locator("#insurerSelect").select_option(insurer)
        opts=page.locator("#careSelect option").evaluate_all(
           "(nodes)=>nodes.map(n=>n.value).filter(Boolean)")
        for care in opts:
            result=result_for(page,care)
            expected=page.evaluate("(id)=>PJM031.entries[id].length",care)
            n=result.locator(".pjm031-procedure-item").count()
            need(n>=4 and n<=expected,
                 f"missing clinical breakdown for {insurer}:{care}: {n}/{expected}")
            need(result.locator(".pjm031-procedure-title strong").count()==n,
                 f"unlabeled procedure for {care}")
            need(result.locator(".pjm031-price").count()==n,
                 f"missing price evidence status for {care}")
            need(not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"),
                 f"horizontal overflow with topic {care}")
            seen.add(care)
    need(len(seen)==52,"not all 52 topics were accessible: "+str(total["expected"]-len(seen)))

def run_case(browser,url,w,h,engine,full):
    ctx,page,errors=start_page(browser,url,w,h,engine)
    try:
        check_matrix(page) if full else None
        check_examples(page)
        need(not page.evaluate("document.documentElement.scrollWidth>innerWidth+2"),
             f"{engine} {w} insurance overflow")
        need(not errors,f"{engine} {w} script failures: {errors}")
        print(f"PASS PJM-031 {engine} {w} detailed all-care procedures, evidence and mobile")
    finally:ctx.close()

def main():
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),
        functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            chromium=p.chromium.launch(headless=True,args=["--no-sandbox"])
            webkit=p.webkit.launch(headless=True)
            try:
                url=f"http://127.0.0.1:{server.server_port}/"
                for w,h in ((320,700),(390,844),(768,1024),(1440,900)):
                    run_case(chromium,url,w,h,"Chromium",full=w==390)
                run_case(webkit,url,390,844,"WebKit",full=True)
            finally:chromium.close();webkit.close()
    finally:server.shutdown();server.server_close()
    print("ALL PJM-031 SUBPROCEDURE QA PASSED")

if __name__=="__main__":main()
