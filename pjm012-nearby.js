
(function(){
  'use strict';
  const memory={sdkPromise:null,map:null,markers:[]};
  function key(){
    try{return String(window.PRZIMA_KAKAO_JS_KEY||sessionStorage.getItem('przima_kakao_js_key')||'').trim()}
    catch(_){return String(window.PRZIMA_KAKAO_JS_KEY||'').trim()}
  }
  function message(txt,status='error'){
    state.nearby.status=status;state.nearby.message=txt;render();
  }
  function sdk(){
    if(window.kakao?.maps?.services?.Places)return Promise.resolve(window.kakao);
    if(memory.sdkPromise)return memory.sdkPromise;
    const k=key();
    if(!/^[A-Za-z0-9]{20,64}$/.test(k))return Promise.reject(new Error('카카오맵 JavaScript 키가 없습니다. 아래 개발용 키 설정을 확인해 주세요.'));
    memory.sdkPromise=new Promise((resolve,reject)=>{
      const script=document.createElement('script');
      let finished=false;
      const fail=()=>{
        if(finished)return;finished=true;clearTimeout(timeout);script.remove();
        reject(new Error('카카오 지도 SDK를 불러올 수 없습니다. 네트워크와 JavaScript SDK 도메인 등록을 확인해 주세요.'));
      };
      const timeout=setTimeout(fail,12000);
      script.src='https://dapi.kakao.com/v2/maps/sdk.js?appkey='+encodeURIComponent(k)+'&libraries=services&autoload=false';
      script.async=true;
      script.onload=()=>{
        try{
          if(!window.kakao?.maps?.load)return fail();
          window.kakao.maps.load(()=>{
            if(finished)return;
            if(!window.kakao?.maps?.services?.Places)return fail();
            finished=true;clearTimeout(timeout);resolve(window.kakao);
          });
        }catch(_){fail()}
      };
      script.onerror=fail;
      document.head.append(script);
    }).catch(err=>{memory.sdkPromise=null;throw err});
    return memory.sdkPromise;
  }
  function distance(a,b,c,d){
    const rad=Math.PI/180,dy=(c-a)*rad,dx=(d-b)*rad;
    const x=Math.sin(dy/2)**2+Math.cos(a*rad)*Math.cos(c*rad)*Math.sin(dx/2)**2;
    return Math.round(12742000*Math.atan2(Math.sqrt(x),Math.sqrt(1-x)));
  }
  function cleanPlaces(items,center){
    const seen=new Set();
    return (Array.isArray(items)?items:[]).filter(p=>{
      const category=String(p?.category_name||''),name=String(p?.place_name||'');
      return category.includes('동물병원')||name.includes('동물병원')||name.includes('동물의료센터')||name.includes('동물메디컬센터')||name.includes('동물클리닉');
    }).map(p=>{
      const lat=Number(p.y),lng=Number(p.x),id=String(p.id||'');
      if(!id||!Number.isFinite(lat)||!Number.isFinite(lng)||seen.has(id))return null;
      seen.add(id);
      return {id,name:String(p.place_name||''),address:String(p.road_address_name||p.address_name||'주소 미등록'),phone:String(p.phone||''),lat,lng,meters:distance(center.lat,center.lng,lat,lng)};
    }).filter(Boolean).sort((a,b)=>a.meters-b.meters).slice(0,15);
  }
  function meters(value){return value>=1000?(value/1000).toFixed(1)+'km':value+'m'}
  function section(){
    const n=state.nearby;
    const busy=['locating','geocoding','loading'].includes(n.status);
    const statusText=n.message||(key()?'위치 정보는 자동 수집하지 않습니다. 버튼을 눌러 검색을 시작하세요.':'현재 지도 API 연결 키가 없습니다. 아래 설정에서 JavaScript 키를 등록한 뒤 검색해 주세요.');
    const list=n.status==='ready'&&n.results.length?n.results.map(p=>`<article class="nearby-place" data-place-id="${escapeHtml(p.id)}">
      <div class="nearby-place-heading"><b>${escapeHtml(p.name)}</b><small>${meters(p.meters)}</small></div>
      <p>${icon('pin',14)} ${escapeHtml(p.address)}${p.phone?'<br>전화 '+escapeHtml(p.phone):''}</p>
      <div class="nearby-place-links"><a href="https://place.map.kakao.com/${encodeURIComponent(p.id)}" target="_blank" rel="noopener noreferrer">카카오맵 상세 보기 ${icon('arrow',13)}</a>
      ${/^[+0-9 -]{7,25}$/.test(p.phone)?`<a href="tel:${p.phone.replace(/[^0-9+]/g,'')}">전화 걸기</a>`:''}</div>
    </article>`).join(''):`<div class="nearby-no-results">${n.status==='empty'?'선택한 반경에서 동물병원 검색 결과가 없습니다. 다른 지역 또는 반경을 선택해 주세요.':'아직 실제 병원 검색 결과가 없습니다. GPS 버튼 또는 지역명 검색을 이용해 주세요.'}</div>`;
    return `<section id="nearby-hospitals" class="nearby-section" aria-labelledby="nearbyTitle"><div class="site-width">
      <div class="nearby-head"><div><div class="nearby-eyebrow">NEARBY / REAL PLACES</div><h2 id="nearbyTitle">내 주변,<br>가까운 동물병원.</h2><p>내 위치 또는 원하는 지역의 카카오맵 등록 동물병원을 찾아보세요.</p></div>
      <span class="nearby-real-badge">카카오맵 · 실제 장소 검색</span></div>
      <div class="nearby-panel"><div class="nearby-actions">
        <button class="nearby-geo" type="button" data-act="nearby-locate" ${busy?'disabled':''}>${icon('pin',17)} 내 위치로 동물병원 찾기</button>
        <form id="nearbyRegionForm" class="nearby-region-form"><input id="nearbyRegionInput" required maxlength="80" aria-label="동물병원 검색할 지역" placeholder="동네 또는 역 이름 · 예: 수원역"><button type="submit" ${busy?'disabled':''}>지역 검색</button></form>
        <label class="nearby-radius">반경 <select id="nearbyRadius" aria-label="주변 동물병원 검색 반경">${[1000,3000,5000].map(d=>`<option value="${d}" ${n.radius===d?'selected':''}>${d/1000}km</option>`).join('')}</select></label>
      </div><p class="nearby-status ${n.status==='error'?'error':''}" role="status" aria-live="polite">${icon('pin',15)} ${escapeHtml(statusText)}${n.originLabel?' · '+escapeHtml(n.originLabel):''}</p>
      <div class="nearby-map-wrap"><div id="nearbyKakaoMap" role="region" aria-label="카카오맵 주변 동물병원 지도"><div class="nearby-map-placeholder">${icon('pin',25)}<strong>주변 동물병원 지도</strong><span>API 연결 및 검색 후 실제 장소 마커가 표시됩니다.</span></div></div></div>
      <div class="nearby-results-title"><h3>검색된 동물병원</h3><span>${n.status==='ready'?n.results.length+'곳 · 가까운 순':'카카오맵 검색 결과'}</span></div>
      <div class="nearby-results" aria-live="polite">${list}</div>
      <div class="nearby-settings"><details ${n.status==='key-required'?'open':''}><summary>개발용 JavaScript 키 설정</summary>
        <p>카카오맵 JavaScript SDK 도메인 등록 후 JavaScript 키만 입력하세요. 이 입력값은 현재 브라우저 탭에만 보관합니다. Admin/REST 키는 입력하지 마세요.</p>
        <form id="nearbyKeyForm" class="nearby-key-form"><input id="nearbyKeyInput" aria-label="카카오맵 JavaScript 키" placeholder="JavaScript 키" pattern="[A-Za-z0-9]{20,64}" autocomplete="off" required><button type="submit">키 적용</button></form>
      </details><a href="https://map.naver.com/p/search/%EB%8F%99%EB%AC%BC%EB%B3%91%EC%9B%90" target="_blank" rel="noopener noreferrer">네이버 지도에서 검색하기</a></div>
      <p class="nearby-endnote">이 구역은 실제 지도에 등록된 장소 정보로, 영업·진료 여부는 병원에 확인해 주세요. <strong>이곳에서는 실제 예약을 지원하지 않습니다.</strong> 기존 예약 기능은 아래의 <strong>가상 병원 체험</strong>을 이용해 주세요. 위치 좌표는 검색에만 이용하며 프지마 서버에 저장하지 않습니다.</p>
      </div></div></section>`;
  }
  function paint(){
    const target=document.getElementById('nearbyKakaoMap'),n=state.nearby;
    if(!target||!n.center||!window.kakao?.maps?.Map||!memory.sdkPromise)return;
    try{
      const km=window.kakao.maps,center=new km.LatLng(n.center.lat,n.center.lng);
      target.replaceChildren();
      const map=new km.Map(target,{center,level:5});memory.map=map;memory.markers=[];
      if(n.results.length){
        const bounds=new km.LatLngBounds();bounds.extend(center);
        n.results.forEach(p=>{
          const pos=new km.LatLng(p.lat,p.lng);bounds.extend(pos);
          const marker=new km.Marker({map,position:pos});memory.markers.push(marker);
          if(km.event?.addListener)km.event.addListener(marker,'click',()=>{
            Array.from(document.querySelectorAll('.nearby-place')).find(x=>x.dataset.placeId===p.id)?.scrollIntoView({block:'center',behavior:'smooth'});
          });
        });
        map.setBounds(bounds);
      }
    }catch(_){target.innerHTML='<div class="nearby-map-placeholder"><strong>지도를 표시하지 못했습니다.</strong><span>동물병원 목록은 이용할 수 있습니다.</span></div>';}
  }
  async function search(lat,lng,label){
    const n=state.nearby,seq=++n.requestId;
    n.center={lat,lng};n.originLabel=label;n.status='loading';n.results=[];n.message='카카오맵에서 주변 동물병원을 검색하고 있습니다.';render();
    try{
      const k=await sdk();if(seq!==n.requestId)return;
      const places=new k.maps.services.Places();
      places.keywordSearch('동물병원',(items,status)=>{
        if(seq!==n.requestId)return;
        if(status===k.maps.services.Status.OK){
          n.results=cleanPlaces(items,{lat,lng});
          n.status=n.results.length?'ready':'empty';
          n.message=n.results.length?'카카오맵 검색이 완료되었습니다.':'검색 결과가 없습니다. 지역이나 반경을 변경해 주세요.';
        }else if(status===k.maps.services.Status.ZERO_RESULT){
          n.status='empty';n.message='이 반경에서 동물병원을 찾지 못했습니다.';n.results=[];
        }else{n.status='error';n.message='장소 검색에 실패했습니다. 네트워크 또는 API 설정을 확인해 주세요.';n.results=[];}
        render();
      },{location:new k.maps.LatLng(lat,lng),radius:n.radius,sort:k.maps.services.SortBy.DISTANCE,size:15,page:1});
    }catch(err){if(seq!==n.requestId)return;message(err.message||'지도 검색 연결에 실패했습니다.',key()?'error':'key-required');}
  }
  function locate(){
    const n=state.nearby;
    if(!key())return message('카카오맵 JavaScript 키를 먼저 연결해 주세요. 아래 개발용 키 설정을 이용할 수 있습니다.','key-required');
    const seq=++n.requestId;n.status='locating';n.originLabel='';n.message='현재 위치 사용 권한을 확인하고 있습니다.';render();
    if(!navigator.geolocation?.getCurrentPosition)return message('현재 브라우저에서 위치 기능을 지원하지 않습니다. 지역 검색을 이용해 주세요.');
    navigator.geolocation.getCurrentPosition(p=>{
      if(seq!==n.requestId)return;
      const lat=p.coords.latitude,lng=p.coords.longitude;
      if(!Number.isFinite(lat)||!Number.isFinite(lng))return message('유효한 위치를 확인하지 못했습니다. 지역 검색을 이용해 주세요.');
      search(lat,lng,'현재 위치 기준');
    },err=>{
      if(seq!==n.requestId)return;
      message(err.code===1?'위치 권한이 거부되었습니다. 지역명을 직접 검색할 수 있습니다.':err.code===3?'위치 확인 시간이 초과되었습니다. 다시 시도하거나 지역을 검색해 주세요.':'현재 위치를 확인하지 못했습니다. 지역 검색을 이용해 주세요.');
    },{enableHighAccuracy:false,timeout:12000,maximumAge:60000});
  }
  async function region(value){
    const q=String(value||'').trim(),n=state.nearby;
    if(!q)return message('지역을 입력해 주세요.');
    const seq=++n.requestId;n.status='geocoding';n.message='지역 좌표를 확인하고 있습니다.';n.originLabel='';n.results=[];render();
    try{
      const k=await sdk();if(seq!==n.requestId)return;
      const places=new k.maps.services.Places();
      const fallback=()=>places.keywordSearch(q,(items,status)=>{
        if(seq!==n.requestId)return;
        if(status!==k.maps.services.Status.OK||!items?.length)return message('지역을 찾지 못했습니다. 동네 또는 역 이름을 더 자세히 입력해 주세요.');
        const lat=Number(items[0].y),lng=Number(items[0].x);
        if(!Number.isFinite(lat)||!Number.isFinite(lng))return message('지역 좌표를 확인하지 못했습니다.');
        search(lat,lng,q+' 기준');
      },{size:5});
      if(k.maps.services.Geocoder){
        new k.maps.services.Geocoder().addressSearch(q,(items,status)=>{
          if(seq!==n.requestId)return;
          if(status!==k.maps.services.Status.OK||!items?.length)return fallback();
          const lat=Number(items[0].y),lng=Number(items[0].x);
          if(!Number.isFinite(lat)||!Number.isFinite(lng))return fallback();
          search(lat,lng,q+' 기준');
        });
      }else fallback();
    }catch(err){if(seq!==n.requestId)return;message(err.message||'지역 검색 연결에 실패했습니다.',key()?'error':'key-required');}
  }
  function radius(value){
    const n=Number(value);
    if(![1000,3000,5000].includes(n))return;
    state.nearby.radius=n;
    const c=state.nearby.center;
    if(c)return search(c.lat,c.lng,state.nearby.originLabel);
    render();
  }
  function saveKey(value){
    const s=String(value||'').trim();
    if(!/^[A-Za-z0-9]{20,64}$/.test(s))return message('JavaScript 키 형식이 올바르지 않습니다.');
    try{sessionStorage.setItem('przima_kakao_js_key',s)}
    catch(_){return message('현재 탭에 키를 저장하지 못했습니다.')}
    message('JavaScript 키를 현재 탭에 적용했습니다. GPS 또는 지역 검색을 시작해 주세요.','idle');
  }
  window.PJM012={section,paint,locate,region,radius,saveKey};
})();
