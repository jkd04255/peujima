/* PJM-019 | Offline contract-condition guide and explicitly hypothetical benefit estimator.
   2026-11-10 official PRODUCT SUMMARY, not the signed contract/policy PDF.
   Never requests credentials, uploads or saves data; does not contact an insurer. */
(function(){
  "use strict";
  const SOURCE="https://www.meritzdirect.com/pet/product.do";
  const CHECKED="2026-11-10";
  const PLANS={
    premium:{label:"고급형",ratio:0.70,daily:300000,surgery:2500000,annual:15000000,scan:1000000},
    standard:{label:"기본형",ratio:0.70,daily:150000,surgery:2500000,annual:10000000,scan:500000},
    economy:{label:"실속형",ratio:0.50,daily:100000,surgery:2000000,annual:7000000,scan:300000}
  };
  const INSURERS=[
    ["meritz-dog","메리츠화재 · 펫퍼민트 Puppy & Family (반려견)"],
    ["meritz-cat","메리츠화재 · 펫퍼민트 Cat & Family (반려묘)"],
    ["hyundai-dog","현대해상 · 굿앤굿우리펫 (반려견)"],
    ["hyundai-cat","현대해상 · 굿앤굿우리펫 (반려묘)"],
    ["db-dog","DB손해보험 · 펫블리 (반려견)"],
    ["db-cat","DB손해보험 · 펫블리 (반려묘)"]
  ];
  const CARES=[
    ["illness","질병 치료"],["injury","사고·상해 치료"],
    ["patella","슬개골·고관절"],["mri","MRI·CT·내시경"],
    ["dental","치과·구강질환"],["vaccine","예방접종·정기검진"],["groom","미용·발톱 관리"]
  ];
  const VISITS=[
    ["out","통원 (수술 아님)"],["in","입원 (수술 아님)"],
    ["surgery-out","통원 수술 당일"],["surgery-in","입원 수술 당일"]
  ];
  const memory={
    insurer:"meritz-dog",care:"illness",plan:"premium",deductible:"30000",
    visit:"out",start:"",onset:"",expense:"",annualPaid:"",dailyPaid:"",
    existing:"unknown",scanUsed:"unknown",policyMatch:false,
    activated:false,mode:"all",legacyCare:"illness"
  };
  const krw=n=>Math.floor(n).toLocaleString("ko-KR")+"원";
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  function option(value,label,current){return '<option value="'+escape(value)+'"'+(value===current?" selected":"")+'>'+escape(label)+'</option>';}
  function choices(items,selected){return items.map(p=>option(p[0],p[1],selected)).join("");}
  function dateValue(s){if(!/^\d{4}-\d{2}-\d{2}$/.test(String(s)))return null;const d=new Date(s+"T00:00:00Z");return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s?d:null;}
  function nonnegative(s){if(typeof s!=="string"&&typeof s!=="number")return null;const raw=String(s).trim();if(!/^\d+$/.test(raw))return null;const n=Number(raw);return Number.isSafeInteger(n)&&n>=0&&n<=100000000? n:null;}
  function stop(reason,kind="hold"){return {kind,title:kind==="excluded"?"보장 제외 항목에 해당할 수 있습니다":"추가 확인이 필요합니다",reason,amount:null};}
  function estimate(params){
    const q=Object.assign({},memory,params||{});
    const plan=PLANS[q.plan];
    if(q.insurer!=="meritz-dog")return stop("현재 금액 분석은 2026년 메리츠화재 펫퍼민트 반려견 상품 안내만 지원합니다. 다른 상품은 금액을 계산하지 않습니다.");
    if(!plan||!["30000","50000"].includes(String(q.deductible)))return stop("가입 증권의 플랜과 자기부담금을 확인해 주세요.");
    if(q.care==="vaccine"||q.care==="groom")return stop("공식 상품 안내에서 예방 목적의 검사·정기검진과 중성화·미용 등은 보상 제외로 안내합니다. 계약의 별도 특약을 확인해 주세요.","excluded");
    if(q.care==="dental")return stop("구강질환 치료는 상품 안내에 언급되지만, 치료 목적·진단명·면책 조항에 따라 달라집니다. 일반 스케일링 등을 치료비로 임의 분류하지 않습니다.");
    if(!["illness","injury","patella","mri"].includes(q.care))return stop("치료 항목을 선택해 주세요.");
    if(!q.policyMatch)return stop("실제 보험증권과 2026년 공식 상품 안내의 플랜·통원/입원 특약이 일치하는지 확인해 주세요.");
    if(!["out","in","surgery-out","surgery-in"].includes(q.visit))return stop("통원·입원·수술 당일 구분을 확인해 주세요.");
    const start=dateValue(q.start),onset=dateValue(q.onset);
    if(!start||!onset)return stop("보험개시일과 최초 증상 발생일(상해는 사고일)을 입력해야 면책기간을 확인할 수 있습니다.");
    if(onset<start)return stop("보험개시일 이전에 발생한 증상·사고는 계산할 수 없습니다. 기왕증 여부를 확인해 주세요.");
    if(q.existing==="yes")return stop("보험개시 전 이미 발병·감염된 질환은 보장 제외로 안내됩니다. 실제 가입 당시 계약 조건 확인이 필요합니다.","excluded");
    if(q.existing!=="no")return stop("보험개시 전 동일 증상·진료 이력 유무를 확인해 주세요. 알 수 없으면 계산하지 않습니다.");
    const days=Math.round((onset.getTime()-start.getTime())/86400000);
    if(q.care!=="injury"&&days<30)return stop("보험개시일을 포함한 최초 30일 이내 발병한 질병은 보상하지 않는다고 안내되어 있습니다.","excluded");
    if(q.care==="patella"){
      const anniv=new Date(Date.UTC(start.getUTCFullYear()+1,start.getUTCMonth(),start.getUTCDate()));
      if(onset<anniv)return stop("슬관절·고관절 관련 질환·상해는 최초 보장개시 후 1년 이내 발병 시 보상 제외로 안내됩니다(갱신계약 예외 가능).","excluded");
    }
    if(q.care==="mri"&&q.scanUsed!=="no")return stop("MRI·CT·내시경은 별도 연간 최초 1회 한도입니다. 같은 연도에 이미 사용했거나 모르면 계산하지 않습니다.");
    const expense=nonnegative(q.expense),annualPaid=nonnegative(q.annualPaid),dailyPaid=nonnegative(q.dailyPaid);
    if(expense===null||expense===0)return stop("이번 진료의 보장대상 의료비(원)를 입력해 주세요. 전체 결제액에 비보장 항목이 포함되면 따로 분리해야 합니다.");
    if(annualPaid===null||dailyPaid===null)return stop("같은 담보의 올해 이미 지급된 보험금과 같은 날 지급된 보험금을 확인해 입력해 주세요. 없으면 0을 입력합니다.");
    const surgery=q.visit.startsWith("surgery-"),limit=surgery?plan.surgery:plan.daily;
    const annualRemaining=Math.max(0,plan.annual-annualPaid);
    const dailyRemaining=Math.max(0,limit-dailyPaid);
    const scanRemaining=q.care==="mri"?plan.scan:Infinity;
    // EDUCATIONAL ASSUMPTION, not a verified payment formula from the user's signed policy.
    const assumedBeforeLimit=Math.max(0,expense-Number(q.deductible))*plan.ratio;
    const amount=Math.floor(Math.max(0,Math.min(assumedBeforeLimit,annualRemaining,dailyRemaining,scanRemaining)));
    return {
      kind:"scenario",title:"조건을 가정한 계산 예시",reason:"이 금액은 보험금 지급 확정액이 아닙니다. 공제·비례보상 순서와 계약별 면책·실제 잔여 한도 확인 전에는 오차가 있을 수 있습니다.",
      amount,expense,plan,limit,annualRemaining,dailyRemaining,scanRemaining,
      deductible:Number(q.deductible),assumedBeforeLimit,care:q.care
    };
  }
  function get(id){return document.getElementById(id);}
  function read(){const map={
    insurer:"insurerSelect",care:"careSelect",plan:"pjm019Plan",
    deductible:"pjm019Deductible",visit:"pjm019Visit",start:"pjm019Start",
    onset:"pjm019Onset",expense:"pjm019Expense",annualPaid:"pjm019AnnualPaid",
    dailyPaid:"pjm019DailyPaid",existing:"pjm019Existing",scanUsed:"pjm019ScanUsed"
  };Object.entries(map).forEach(([key,id])=>{if(get(id))memory[key]=get(id).value;});
    memory.policyMatch=!!get("pjm019PolicyMatch")?.checked;
  }
  function summary(){
    const p=PLANS[memory.plan]||PLANS.premium;
    return '<div class="pjm019-limits" aria-label="공식 상품 안내의 플랜별 한도">'+
      '<div><span>보장비율</span><strong>'+Math.round(p.ratio*100)+'%</strong></div>'+
      '<div><span>통원·입원 1일</span><strong>'+krw(p.daily)+'</strong></div>'+
      '<div><span>수술 당일</span><strong>'+krw(p.surgery)+'</strong></div>'+
      '<div><span>연간 (담보별)</span><strong>'+krw(p.annual)+'</strong></div>'+
      '<div><span>영상검사 연 1회</span><strong>'+krw(p.scan)+'</strong></div></div>';
  }
  function result(){
    if(!memory.activated)return '<div class="pjm019-empty">가입한 플랜과 진료 조건을 입력한 뒤 <b>보장 조건 분석하기</b>를 눌러 주세요.</div>';
    const x=estimate(memory);
    if(x.kind!=="scenario")return '<div class="insurance-result pjm019-result is-'+x.kind+'" role="status" aria-live="polite">'+
      '<span class="pjm019-status">'+(x.kind==="excluded"?"보장 제외 안내":"추가 확인 필요")+'</span>'+
      '<h3>'+escape(x.title)+'</h3><p>'+escape(x.reason)+'</p>'+
      '<a href="'+SOURCE+'" target="_blank" rel="noopener noreferrer">메리츠화재 공식 상품 안내 원문 확인 ↗</a></div>';
    return '<div class="insurance-result pjm019-result is-scenario" role="status" aria-live="polite">'+
      '<span class="pjm019-status">계산 예시 · 확정 지급액 아님</span>'+
      '<h3>가정에 따른 예상 보장액</h3>'+
      '<div class="pjm019-amount">'+krw(x.amount)+'</div>'+
      '<dl class="pjm019-breakdown"><div><dt>입력한 보장 대상 의료비</dt><dd>'+krw(x.expense)+'</dd></div>'+
      '<div><dt>자기부담금</dt><dd>'+krw(x.deductible)+'</dd></div>'+
      '<div><dt>가정 계산</dt><dd>(진료비 − 자기부담금) × '+Math.round(x.plan.ratio*100)+'%</dd></div>'+
      '<div><dt>적용 한도</dt><dd>1일 '+krw(x.limit)+' / 연간 잔여 '+krw(x.annualRemaining)+'</dd></div>'+
      (Number.isFinite(x.scanRemaining)?'<div><dt>영상검사 한도</dt><dd>'+krw(x.scanRemaining)+'</dd></div>':"")+
      '<div><dt>가정상 본인 부담액</dt><dd>'+krw(x.expense-x.amount)+'</dd></div></dl>'+
      '<p class="pjm019-caution">'+escape(x.reason)+'</p>'+
      '<a href="'+SOURCE+'" target="_blank" rel="noopener noreferrer">공식 상품 안내에서 보장 한도 검증하기 ↗</a></div>';
  }
  function field(id,label,body,small){
    return '<label class="pjm019-field" for="'+id+'"><span>'+label+'</span>'+body+
      (small?'<small>'+small+'</small>':"")+'</label>';
  }
  function makeSelect(id,list,selected){return '<select id="'+id+'">'+choices(list,selected)+'</select>';}
  function txt(id,type,val,placeholder){return '<input id="'+id+'" type="'+type+'" value="'+escape(val)+'"'+(placeholder?' placeholder="'+escape(placeholder)+'"':"")+(type==="number"?' min="0" max="100000000" step="1" inputmode="numeric"':"")+' />';}
  function section(mode,legacyCare){
    if(mode!==memory.mode){memory.mode=mode;memory.insurer=mode==="cat"?"meritz-cat":"meritz-dog";memory.activated=false;}
    if(legacyCare&&legacyCare!==memory.legacyCare&&CARES.some(p=>p[0]===legacyCare)){memory.legacyCare=legacyCare;memory.care=legacyCare;memory.activated=false;}
    const supported=memory.insurer==="meritz-dog";
    return '<section class="section insurance pjm019-insurance" id="insurance" aria-label="내 펫보험 보장 조건 분석">'+
      '<div class="site-width pjm019-layout">'+
      '<div class="pjm019-header"><span class="pjm019-eyebrow">PRZIMA · INSURANCE GUIDE</span>'+
      '<h2>내 보험,<br><em>어디까지 보장될까요?</em></h2>'+
      '<p>가입한 상품과 실제 진료 조건을 선택해 보장 범위와 한도를 살펴보세요.</p>'+
      '<div class="pjm019-source">자료 기준 '+CHECKED+' · 공식 상품 안내 기반 · 보험사와 무관한 비공식 분석</div></div>'+
      '<div class="insurance-card pjm019-card">'+
      '<div class="pjm019-section-head"><b>가입 계약</b><span>01 / 상품 확인</span></div>'+
      '<div class="pjm019-grid">'+
      field("insurerSelect","보험사 · 상품",makeSelect("insurerSelect",INSURERS,memory.insurer))+
      field("pjm019Plan","가입 플랜",makeSelect("pjm019Plan",Object.keys(PLANS).map(k=>[k,PLANS[k].label+" · "+Math.round(PLANS[k].ratio*100)+"%"]),memory.plan))+
      field("pjm019Deductible","1회 자기부담금",makeSelect("pjm019Deductible",[["30000","3만원"],["50000","5만원"]],memory.deductible))+
      field("pjm019Visit","진료 구분",makeSelect("pjm019Visit",VISITS,memory.visit))+
      '</div>'+
      '<div class="pjm019-support" role="note">'+(supported?'현재 메리츠 반려견 상품 안내에 공개된 수치만 적용합니다. 실제 보험증권에서 상품·특약·플랜이 일치하는지 확인하세요.':'이 상품의 계약별 지급 규칙은 아직 검증되지 않아 금액을 계산하지 않습니다. 추후 상품별 공식 약관 검증 후 지원합니다.')+'</div>'+
      '<div id="pjm019Limits">'+(supported?summary():'<p>지원하지 않는 상품의 보장 한도는 표시하지 않습니다.</p>')+'</div>'+
      '<div class="pjm019-section-head"><b>진료 조건</b><span>02 / 지급 가능 조건</span></div>'+
      '<div class="pjm019-grid">'+
      field("careSelect","치료·검사 항목",makeSelect("careSelect",CARES,memory.care))+
      field("pjm019Existing","보험개시 이전 같은 증상·진료 이력",makeSelect("pjm019Existing",[["unknown","모름 / 확인 필요"],["no","없음"],["yes","있음"]],memory.existing))+
      field("pjm019Start","최초 보험개시일",txt("pjm019Start","date",memory.start),"재가입 계약·계약 변경은 별도 확인 필요")+
      field("pjm019Onset","최초 발병일 또는 사고일",txt("pjm019Onset","date",memory.onset),"진료일과 다를 수 있습니다")+
      field("pjm019ScanUsed","이번 보험연도 영상검사 보장 사용 여부",makeSelect("pjm019ScanUsed",[["unknown","모름 / 확인 필요"],["no","미사용"],["yes","사용"]],memory.scanUsed),"MRI·CT·내시경인 경우만 적용")+
      field("pjm019Expense","이번 진료의 보장 대상 비용 (원)",txt("pjm019Expense","number",memory.expense,"예: 200000"),"미용·예방진료 등 제외 금액을 빼고 입력")+
      field("pjm019AnnualPaid","올해 이 담보로 이미 받은 보험금 (원)",txt("pjm019AnnualPaid","number",memory.annualPaid,"없으면 0"),"연간 한도 계산에 필요")+
      field("pjm019DailyPaid","같은 날 이 담보로 이미 받은 보험금 (원)",txt("pjm019DailyPaid","number",memory.dailyPaid,"없으면 0"),"같은 날 수술·통원 합산 여부도 확인")+
      '</div>'+
      '<label class="pjm019-confirm"><input type="checkbox" id="pjm019PolicyMatch"'+(memory.policyMatch?" checked":"")+' /><span>내 보험증권의 플랜·자기부담금·특약이 위 상품 안내와 일치함을 확인했습니다. 이 결과가 최종 지급액이 아닌 <b>가정 계산</b>임을 이해합니다.</span></label>'+
      '<button type="button" class="primary-btn insurance-button pjm019-submit">보장 조건 분석하기 →</button>'+
      '<div id="pjm019Outcome">'+result()+'</div>'+
      '<div class="pjm019-reference"><b>확인한 공식 자료</b><p>메리츠화재 펫퍼민트 Puppy &amp; Family 다이렉트: 반려견 통원·입원의료비Ⅲ 특약, 보장비율, 자기부담금, 수술·영상검사 한도 및 보장개시 제외 기간.</p>'+
      '<a href="'+SOURCE+'" target="_blank" rel="noopener noreferrer">공식 상품 안내 보기 ↗</a><small>실제 약관 및 개별 계약서 전체를 자동 분석한 결과는 아닙니다. 특히 기존 가입 상품·갱신계약에서는 적용 내용이 다를 수 있습니다.</small></div>'+
      '</div>'+
      '<p class="insurance-disclaimer">보험금 지급 여부와 금액은 보험사 심사 및 가입 계약 약관에 따릅니다. 이 기능은 개인 가입정보를 조회·저장하지 않고, 상품을 추천·판매·중개하지 않습니다.</p>'+
      '</div></section>';
  }
  function updateDynamic(){
    const root=get("insurance");if(!root)return;
    const supported=memory.insurer==="meritz-dog";
    const limits=get("pjm019Limits");
    if(limits)limits.innerHTML=supported?summary():'<p>지원하지 않는 상품의 보장 한도는 표시하지 않습니다.</p>';
    const support=root.querySelector(".pjm019-support");
    if(support)support.textContent=supported?'현재 메리츠 반려견 상품 안내에 공개된 수치만 적용합니다. 실제 보험증권에서 상품·특약·플랜이 일치하는지 확인하세요.':'이 상품의 계약별 지급 규칙은 아직 검증되지 않아 금액을 계산하지 않습니다. 추후 상품별 공식 약관 검증 후 지원합니다.';
    const outcome=get("pjm019Outcome");if(outcome)outcome.innerHTML=result();
  }
  document.addEventListener("change",e=>{
    if(!get("insurance")?.contains(e.target))return;
    if(!/^(insurerSelect|careSelect|pjm019)/.test(e.target.id))return;
    // Avoid legacy insurerSelect/careSelect rerender, keep current form inputs and scroll.
    if(e.target.id==="insurerSelect"||e.target.id==="careSelect")e.stopImmediatePropagation();
    read();memory.activated=false;updateDynamic();
  },true);
  document.addEventListener("click",e=>{
    if(!e.target.closest("#insurance .insurance-button"))return;
    e.preventDefault();e.stopImmediatePropagation();read();memory.activated=true;updateDynamic();
    get("pjm019Outcome")?.scrollIntoView({behavior:"smooth",block:"nearest"});
  },true);
  window.PJM019=Object.freeze({section,estimate,plans:PLANS,source:SOURCE});
})();