"""PJM-032 explicit approximate cost ranges vs 2025 government medians.
Never confuse service-planning estimates with verified national prices or insurer payouts.
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

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def set_care(page,care):
    page.locator("#careSelect").select_option(care)
    page.locator(".insurance-button").click()
    panel=page.locator(".pjm031-procedures")
    need(panel.is_visible(),f"missing selected subprocedure panel: {care}")
    disclosure=panel.locator(".pjm035-procedure-disclosure")
    need(disclosure.count()==1 and disclosure.get_attribute("open") is None,
         f"procedure details should start collapsed: {care}")
    disclosure.locator("summary").click()
    need(disclosure.get_attribute("open") is not None,
         f"procedure details should expand: {care}")
    return panel

def run_case(browser,url,w,h,engine,full):
    ctx=browser.new_context(viewport={"width":w,"height":h},locale="ko-KR",
        reduced_motion="reduce",has_touch=engine=="WebKit",
        is_mobile=engine=="WebKit")
    page=ctx.new_page();errs=[]
    page.on("pageerror",lambda error:errs.append(str(error)))
    try:
        page.goto(url+"#insurance",wait_until="load")
        need(page.locator("#insurance select").count()==2,"two required selections must stay")
        if full:
            matrix=page.evaluate("""() => {
              let estimate=0,nonPrice=0,unknown=0,invalid=0,missing=[];
              const careTypes=PJM019.careTypes;
              for(const care of careTypes){
                const rows=PJM031.entries[care.id];
                if(!rows){missing.push(care.id);continue;}
                for(const row of rows){
                  const result=PJM032.estimate(care.id,row,"dog");
                  if(result.kind==="estimate"){
                    estimate++;
                    if(!(result.low>0&&result.high>=result.low&&
                       Number.isFinite(result.low)&&Number.isFinite(result.high)))invalid++;
                    if(result.basis==="published-case"&&!PJM032.anchors[result.source])invalid++;
                  }else if(result.kind==="not-applicable")nonPrice++;
                  else unknown++;
                }
              }
              const dog=PJM032.estimate("neuter",PJM031.entries.neuter[0],"dog");
              const cat=PJM032.estimate("neuter",PJM031.entries.neuter[0],"cat");
              return {topicCount:careTypes.length,entries:Object.values(PJM031.entries).reduce((n,v)=>n+v.length,0),
                estimate,nonPrice,unknown,invalid,missing,
                dog:[dog.low,dog.high],cat:[cat.low,cat.high],
                sampleAmounts:PJM019.sample("meritz-dog","illness")?.plans?.map(x=>x.amount)};
            }""")
            need(matrix["topicCount"]==52 and matrix["entries"]==261 and
                 matrix["estimate"]==235 and matrix["nonPrice"]==26 and
                 matrix["unknown"]==0 and matrix["invalid"]==0 and
                 not matrix["missing"],"incomplete cost coverage: "+str(matrix))
            need(matrix["dog"]==[200000,350000] and
                 matrix["cat"]==[100000,250000],"dog/cat neuter estimates leaked")
            need(matrix["sampleAmounts"]==[65800,65800,47000],
                 "original Meritz illustrative insurer math changed")

        page.locator("#insurerSelect").select_option("meritz-dog")
        p=set_care(page,"patella")
        pat=p.locator(".pjm031-procedure-item").filter(has_text="슬개골 교정수술비")
        need(pat.count()==1 and "약 80만~300만원" in pat.inner_text() and
             "공개 사례 참고" in pat.inner_text(),
             "patella surgery approx cost should be shown prominently")
        need(not pat.locator(".pjm031-published").count(),
             "approx surgery price must not be styled as government statistic")
        need("병원별 비용 확인" not in p.inner_text(),
             "old generic hospital-only price label must be removed")
        need(page.locator(".pjm021-fee-guide").count()==1,
             "the applicable published fee must remain in its own guide")
        p=set_care(page,"cancer")
        for title,band in [("종양 절제·암수술비","약 30만~500만원"),
                           ("항암약물치료비","약 20만~70만원"),
                           ("방사선치료비","약 50만~150만원")]:
            item=p.locator(".pjm031-procedure-item").filter(has_text=title)
            need(item.count()==1 and band in item.inner_text(),
                 f"cancer reference estimate missing {title}: {band}")
            need(item.locator(".pjm031-published").count()==0,
                 "cancer procedure estimate must not be official statistic")
        need(page.locator(".pjm021-plan-amounts").count()==0,
             "cancer treatment cost must never become automatic insurer payout")
        need(page.locator(".pjm021-fee-guide").count()==1 and
             "공식 공개 진료비 참고" in page.locator(".pjm021-fee-guide").inner_text() and
             "10,000원" in page.locator(".pjm021-fee-guide").inner_text(),
             "cancer may show the separate 2025 first-visit median, not a blank guide")
        need("신뢰할 수 있는 공개 진료비 자료가 없습니다." not in
             page.locator(".pjm020-result").inner_text(),
             "cancer estimate must not be confused with missing national surgery statistics")
        footer=page.locator(".pjm030-fineprint")
        need(footer.count()==1 and not page.locator(".pjm032-sources").is_visible(),
             "source links should stay in the single collapsed footer")
        page.locator(".pjm030-fineprint > summary").click()
        need(page.locator(".pjm032-sources").is_visible() and
             page.locator(".pjm032-sources a").count()>=2,
             "reference sources should be optional, accessible, and tied to selected topic")
        need(page.locator(".pjm031-procedure-caution").is_visible() and
             "합산" in page.locator(".pjm031-procedure-caution").inner_text(),
             "do not imply adding all individual treatment estimates")
        need(page.locator(".pjm021-unpriced").count()>0 and
             page.locator(".pjm021-policy-details").count()==1,
             "cost-only page must keep supplemental caveats and policy source")
        need(page.locator(".pjm020-result a[target='_blank']").count()==0,
             "do not trigger external browsing by default")

        p=set_care(page,"mri")
        need(p.locator(".pjm031-published").count()==2 and
             "791,500원" in p.inner_text() and "600,000원" in p.inner_text(),
             "real 2025 government single-item MRI/CT medians must remain exact")
        need(page.locator(".pjm021-fee-guide").count()==1,
             "exact published MRI/CT figures require the official fee guide")
        page.locator("#insurerSelect").select_option("meritz-cat")
        p=set_care(page,"neuter")
        need("약 10만~25만원" in p.inner_text() and
             "약 15만~35만원" in p.inner_text(),
             "cat neuter planning amounts should not copy dog prices")
        need(page.locator(".pjm021-fee-guide").count()==0,
             "neuter has no official fee median and must not show an empty official card")
        p=set_care(page,"fip")
        need(page.locator(".pjm021-fee-guide").count()==1,
             "FIP may show the 2025 first-visit median without mislabeling antiviral course price")
        need("약 100만~1,500만원" in p.inner_text() and
             "전체 치료 과정" in p.inner_text(),
             "FIP course estimate must specify longer unit")
        p=set_care(page,"hospital")
        need("반려견 1일 입원비" not in p.inner_text(),
             "dog-specific publication must not appear for cats")
        page.locator("#insurerSelect").select_option("nh-dog")
        p=set_care(page,"funeral")
        need("약 20만~35만원" in p.inner_text(),
             "actual public cremation service fee should provide a planning range")
        p=set_care(page,"liability")
        # '계약 확인' includes the characters '약 ': check price labels only.
        need("보험 보장·청구 조건" in p.inner_text() and
             all("약 " not in label for label in
                 p.locator(".pjm031-price").all_inner_texts()),
             "non-medical indemnity paperwork must not show invented fees")
        need(not page.evaluate("document.documentElement.scrollWidth>innerWidth+2"),
             f"{engine} {w} horizontal scrolling from price labels")
        need(not errs,f"{engine} {w} JavaScript errors: {errs}")
        print(f"PASS PJM-032 {engine} {w}: price estimates separate from public medians and insurance benefits")
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
                for w,h in [(320,700),(390,844),(768,1024),(1440,900)]:
                    run_case(chromium,url,w,h,"Chromium",full=w==390)
                run_case(webkit,url,390,844,"WebKit",full=True)
            finally:chromium.close();webkit.close()
    finally:server.shutdown();server.server_close()
    print("ALL PJM-032 APPROX COST QA PASSED")

if __name__=="__main__":main()
