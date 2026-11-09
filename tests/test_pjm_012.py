"""PJM-012: Chromium mock-Kakao/GPS browser QA, never a live API verification."""
from __future__ import annotations
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-screenshots"
OUT.mkdir(exist_ok=True)
TEST_KEY="a"*32
MOCK_SDK=r"""
window.__kakaoCalls=[];
window.__mapInstances=0;
(function(){
  const Status={OK:"OK",ZERO_RESULT:"ZERO_RESULT",ERROR:"ERROR"};
  const SortBy={DISTANCE:"DISTANCE"};
  function LatLng(lat,lng){this.lat=lat;this.lng=lng;}
  function Map(el,opts){window.__mapInstances++;this.target=el;this.setBounds=function(){};}
  function Marker(opts){this.options=opts;}
  function LatLngBounds(){this.extend=function(){};}
  function Places(){}
  Places.prototype.keywordSearch=function(keyword,callback,options){
    window.__kakaoCalls.push({keyword,options:options||{}});
    if(keyword==="동물병원"){
      if(window.__mockEmpty){callback([],Status.ZERO_RESULT,{});return;}
      if(window.__mockFailure){callback([],Status.ERROR,{});return;}
      callback([
        {id:"1002",place_name:"나중 동물병원",category_name:"의료 > 동물병원",x:"127.03",y:"37.60",road_address_name:"가상 시뮬레이션 도로 2",phone:"02-111-2222"},
        {id:"1001",place_name:"가까운 동물병원",category_name:"의료 > 동물병원",x:"127.001",y:"37.501",road_address_name:"가상 시뮬레이션 도로 1",phone:"02-1234-5678"},
        {id:"1003",place_name:"동물병원 찾는 카페",category_name:"음식점 > 카페",x:"127.0001",y:"37.5001"}
      ],Status.OK,{});
    }else if(keyword==="없는지역"){callback([],Status.ZERO_RESULT,{});}
    else{callback([{id:"region",x:"127.0",y:"37.5"}],Status.OK,{});}
  };
  function Geocoder(){}
  Geocoder.prototype.addressSearch=function(q,callback){
    if(q==="없는지역")callback([],Status.ZERO_RESULT);
    else callback([{x:"127.0",y:"37.5"}],Status.OK);
  };
  window.kakao={maps:{load:function(cb){cb();},LatLng,Map,Marker,LatLngBounds,event:{addListener:function(){}},services:{Status,SortBy,Places,Geocoder}}};
})();
"""

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def assert_true(value,msg):
    if not value:raise AssertionError(msg)

def live_search_case(browser,origin,width,height):
    context=browser.new_context(viewport={"width":width,"height":height},locale="ko-KR",timezone_id="Asia/Seoul",reduced_motion="reduce",geolocation={"latitude":37.5,"longitude":127.0},permissions=["geolocation"])
    page=context.new_page()
    errors=[]
    page.on("pageerror",lambda err:errors.append(str(err)))
    page.add_init_script(f"window.PRZIMA_KAKAO_JS_KEY='{TEST_KEY}'")
    page.route("**/v2/maps/sdk.js?**",lambda route:route.fulfill(status=200,content_type="application/javascript",body=MOCK_SDK))
    try:
        page.goto(origin,wait_until="load")
        page.locator("#nearbyTitle").wait_for()
        assert_true(page.locator(".clinic-explore-card").count()==5,f"{width}: synthetic clinic catalog missing")
        assert_true(page.locator(".nearby-place").count()==0,f"{width}: should not invent live places")
        assert_true(page.evaluate("window.__kakaoCalls===undefined"),f"{width}: SDK loaded before explicit user request")
        assert_true(page.locator(".nearby-geo").is_visible(),f"{width}: GPS action missing")
        if width==390:page.screenshot(path=str(OUT/"pjm-012-390-initial.png"),full_page=True)
        page.locator('[data-act="nearby-locate"]').click()
        page.locator(".nearby-place").first.wait_for(timeout=8000)
        assert_true(page.locator(".nearby-place").count()==2,f"{width}: expected 2 actual-vet mock results")
        assert_true(page.locator(".nearby-place").first.locator("b").inner_text()=="가까운 동물병원",f"{width}: not sorted by nearby distance")
        assert_true(page.locator(".nearby-place").locator('[data-act="calendar-continue"]').count()==0,f"{width}: live place must not have demo booking")
        assert_true(page.locator(".nearby-place").locator('a[href^="https://place.map.kakao.com/"]').count()==2,f"{width}: Kakao external links missing")
        data=page.evaluate("window.__kakaoCalls.filter(c=>c.keyword==='동물병원').map(c=>({radius:c.options.radius,sort:c.options.sort,lat:c.options.location.lat}))")
        assert_true(data and data[0]["radius"]==3000 and data[0]["sort"]=="DISTANCE" and data[0]["lat"]==37.5,f"{width}: wrong Kakao query options {data}")
        assert_true(page.evaluate("window.__mapInstances")>=1,f"{width}: map was not instantiated")
        if width==390:page.screenshot(path=str(OUT/"pjm-012-390-mock-results.png"),full_page=True)
        page.locator("#nearbyRadius").select_option("1000")
        page.locator(".nearby-place").first.wait_for(timeout=8000)
        data=page.evaluate("window.__kakaoCalls.filter(c=>c.keyword==='동물병원').map(c=>c.options.radius)")
        assert_true(data[-1]==1000,f"{width}: radius change was not searched")
        page.locator("#nearbyRegionInput").fill("수원역")
        page.locator("#nearbyRegionForm button").click()
        page.locator(".nearby-place").first.wait_for(timeout=8000)
        assert_true("수원역 기준" in page.locator("#nearby-hospitals .nearby-status").inner_text(),f"{width}: region mode not indicated")
        page.evaluate("window.__mockEmpty=true")
        page.locator("#nearbyRadius").select_option("5000")
        page.get_by_text("선택한 반경에서 동물병원 검색 결과가 없습니다.",exact=False).first.wait_for(timeout=8000)
        assert_true(page.locator(".nearby-place").count()==0,f"{width}: empty search retained stale clinics")
        assert_true(page.locator(".clinic-explore-card").count()==5,f"{width}: virtual hospital section disappeared")
        page.locator(".clinic-explore-card").first.click()
        assert_true(page.locator(".cal-date").count()==0,f"{width}: virtual detail calendar shown too soon")
        page.locator('[data-act="clinic-reserve"]').click()
        assert_true(page.locator(".cal-date").count()==7,f"{width}: virtual booking calendar broken")
        assert_true(not page.evaluate("document.documentElement.scrollWidth>window.innerWidth+2"),f"{width}: horizontal overflow")
        assert_true(not errors,f"{width}: JS errors: {errors}")
        print(f"PASS {width}x{height}: no auto GPS; mock Kakao SDK; GPS; radius; manual search; empty; virtual booking; no JS errors/overflow")
    finally:context.close()

def missing_key_and_denial(browser,origin):
    context=browser.new_context(viewport={"width":390,"height":844},reduced_motion="reduce")
    page=context.new_page()
    page.goto(origin,wait_until="load")
    assert_true(page.locator(".nearby-place").count()==0,"missing key must not show fabricated places")
    page.locator('[data-act="nearby-locate"]').click()
    assert_true("키" in page.locator(".nearby-status").inner_text(),"missing-key help missing")
    assert_true(page.locator(".nearby-settings details").get_attribute("open") is not None,"key input should be exposed")
    context.close()

    context=browser.new_context(viewport={"width":390,"height":844},reduced_motion="reduce")
    page=context.new_page()
    page.add_init_script(f"window.PRZIMA_KAKAO_JS_KEY='{TEST_KEY}'")
    page.add_init_script("""Object.defineProperty(navigator,'geolocation',{configurable:true,value:{getCurrentPosition(success,error){error({code:1})}}});""")
    page.goto(origin,wait_until="load")
    page.locator('[data-act="nearby-locate"]').click()
    assert_true("거부" in page.locator(".nearby-status").inner_text(),"GPS denial fallback missing")
    assert_true(page.locator("#nearbyRegionInput").is_visible(),"manual region search missing after denial")
    context.close()
    print("PASS missing Kakao key + refused GPS: explicit error, no fabricated place, manual search available")

def main():
    handler=functools.partial(QuietHandler,directory=str(ROOT))
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    origin=f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for width,height in [(320,700),(390,844),(768,1024),(1440,900)]:
                    live_search_case(browser,origin,width,height)
                missing_key_and_denial(browser,origin)
            finally:browser.close()
    finally:server.shutdown();server.server_close()
    print("ALL PJM-012 MOCK BROWSER QA PASSED (not a live Kakao API test)")

if __name__=="__main__":main()
