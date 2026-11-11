/* PJM-045 / G2-INS-01 — auditable, scenario-only insurance settlement previews.
 * Never use another insurer's terms, or silently assume a contract version.
 * No personal data persistence, real claim API, diagnosis, or payout guarantee.
 */
(function () {
  "use strict";
  const meritzSource = "https://www.meritzdirect.com/pet/product.do";
  const meritzCatSource = "https://www.meritzdirect.com/pet/product-cat.do";
  const dbDogSource = "https://www.directdb.co.kr/ltm/prd/cpnm/custInfoView.do?pdcDvcd=l_pet_dog&searchPdcCd=31119&searchPdcTrtHistCd=00";
  const dbCatSource = "https://www.directdb.co.kr/ltm/prd/cpnmcat/custInfoView.do?pdcDvcd=l_pet_cat&searchPdcCd=31121&searchPdcTrtHistCd=00";
  const samsungSource = "https://d.samsungfire.com/m/mall/MP030706_001.html";
  const samsungCatSource = "https://direct.samsungfire.com/m/mall/MP030705_001.html";
  const kakaoSource = "https://kakaopayinscorp.co.kr/blog/kang-hyungwook-pet-insurance-must-check";
  const plan = (key, name, ratio, daily, annual, surgery, scan, provenance, verified) =>
    Object.freeze({key, name, ratio, daily, annual, surgery, scan, provenance, verified});
  const meritz = Object.freeze([
    plan("premium", "고급형 70%", .7, 300000, 15000000, 2500000, 1000000, "2026 공식 상품 안내", true),
    plan("standard", "기본형 70%", .7, 150000, 10000000, 2500000, 500000, "2026 공식 상품 안내", true),
    plan("economy", "실속형 50%", .5, 100000, 7000000, 2000000, 300000, "2026 공식 상품 안내", true)
  ]);
  const dbDog2607 = Object.freeze([
    plan("db2607-economy", "2607 50% · 일 10만원", .5, 100000, 7000000, 1500000, null, "2607 가입안내 (2610 계약 아님)", false),
    plan("db2607-standard", "2607 70% · 일 15만원", .7, 150000, 20000000, 2500000, null, "2607 가입안내 (2610 계약 아님)", false),
    plan("db2607-premium", "2607 70% · 일 30만원", .7, 300000, 20000000, 2500000, null, "2607 가입안내 (2610 계약 아님)", false)
  ]);
  // 2610 public product introductions (dog and cat) verify rates and deductions,
  // but NOT a complete 2610 plan-specific daily/surgery/annual table.
  // The rate choices below are NOT named or capped insurance plans.
  const db2610Rates = Object.freeze([
    plan("db2610-50", "2610 공개 비율 50% · 한도 미확인", .5, null, null, null, null, "2610 공식 상품 소개 · 한도 미확인", false),
    plan("db2610-70", "2610 공개 비율 70% · 한도 미확인", .7, null, null, null, null, "2610 공식 상품 소개 · 한도 미확인", false)
  ]);
  // Samsung's 2026 specific dog/cat pages list 50/70%, NOT generic 80%.
  // Deductible and payout caps are not verified: selecting a rate opens manual terms.
  const samsungRates = Object.freeze([
    plan("samsung-50", "2026 공개 비율 50% · 공제금 미확인", .5, null, null, null, null, "2026 공식 반려견/묘 상품 상세 · 50%", false),
    plan("samsung-70", "2026 공개 비율 70% · 공제금 미확인", .7, null, null, null, null, "2026 공식 반려견/묘 상품 상세 · 70%", false)
  ]);
  // Do NOT map DB cat's 2607 benefit tiers to a particular ratio without the signed schedule.
  // Unknown insurer contract details never receive automatically invented deductible/cap.
  const specs = Object.freeze({
    "meritz-dog": {source:meritzSource, description:"메리츠 2026 반려견 의료비Ⅲ · 통원/입원 각각 특약 필요", plans:meritz, defaultKey:"premium", deductible:30000},
    "meritz-cat": {source:meritzCatSource, description:"메리츠 2026 반려묘 의료비Ⅲ · 통원/입원 각각 특약 필요", plans:meritz, defaultKey:"premium", deductible:30000},
    "db-dog": {source:dbDogSource, description:"DB 반려견 2610은 50/70% 및 공제금 3/5만원까지 공식 소개로 확인했습니다. 일·연간·수술 한도는 2610 가입증권을 확인해야 합니다. 구버전 2607 플랜은 2610에 적용하지 않습니다.", plans:[...db2610Rates,...dbDog2607], defaultKey:null, deductible:30000},
    "db-cat": {source:dbCatSource, description:"DB 반려묘 2610 공식 소개에 50/70% 및 공제 3/5만원이 명시되어 있습니다. 2607 가입안내·상단 보장예시와 플랜별 한도는 직접 대응시키지 않았습니다.", plans:db2610Rates, defaultKey:null, deductible:null},
    "samsung-dog": {source:samsungSource, description:"삼성화재 착한펫 반려견 2026 공식 상세의 의료비 비율은 50/70%입니다. 공제금·가입금액은 미확인으로, 해당 비율을 고르고 증권의 공제금을 직접 입력해야 가상 계산할 수 있습니다.", plans:samsungRates, defaultKey:null, deductible:null},
    "samsung-cat": {source:samsungCatSource, description:"삼성화재 반려묘 2026 공식 상세의 의료비 비율은 50/70%입니다. 공제금·가입금액은 미확인으로, 해당 비율을 고르고 증권의 공제금을 직접 입력해야 가상 계산할 수 있습니다.", plans:samsungRates, defaultKey:null, deductible:null},
    "hyundai-dog": {source:null, description:"현대해상 Hi2601 계약별 보상비율·자기부담금·특약별 한도는 이 계산에서 확정하지 않았습니다.", plans:[], defaultKey:null},
    "hyundai-cat": {source:null, description:"현대해상 반려묘 보험의 계약별 지급비율·공제금·한도 자료가 부족합니다.", plans:[], defaultKey:null},
    "kb-dog": {source:null, description:"KB 26.01 약관 일부와 26.07 상품은 서로 다른 버전입니다. 계약의 보상 조건 확인이 필요합니다.", plans:[], defaultKey:null},
    "kb-cat": {source:null, description:"KB 반려묘 26.07 실제 가입약관의 의료비 산식·공제금·한도는 확인되지 않았습니다.", plans:[], defaultKey:null},
    "nh-dog": {source:null, description:"NH 반려견 2604 공식 의료비 약관 원문을 확인하지 못해 임의 지급률을 적용하지 않습니다.", plans:[], defaultKey:null},
    "nh-cat": {source:null, description:"NH 반려묘 2604 공식 의료비 약관 원문을 확인하지 못해 임의 지급률을 적용하지 않습니다.", plans:[], defaultKey:null},
    "kakao-dog": {source:kakaoSource, description:"카카오페이손보 2026 반려견 공식 소개: 70%, 일 자기부담금 3만원. 입통원 보장 범위·최종 한도는 가입 플랜마다 다릅니다.", plans:[plan("kakao-precap", "70% · 한도 적용 전", .7, null, null, null, null, "2026 공식 소개(플랜·한도 미확인)", false)], defaultKey:"kakao-precap", deductible:30000},
    "kakao-cat": {source:null, description:"카카오페이손보 반려묘 계약에 반려견 70%·3만원 조건을 복사하지 않습니다.", plans:[], defaultKey:null}
  });
  const fmt = n => Number(n).toLocaleString("ko-KR") + "원";
  const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  let selection = {scope:null, index:-1, planKey:null, deductible:30000, manual:false, custom:null};
  function medicalRow(insurer, care, row, index) {
    const cat = insurer.endsWith("-cat");
    const medians = window.PJM019?.medianCosts || {};
    if(cat && ["inpatient","vaccine"].includes(row[3]))return null;
    const exact = medians[row[3]];
    const band = exact ? null : window.PJM032?.estimate(care,row,cat?"cat":"dog");
    if(band?.kind==="not-applicable")return null;
    const lower = exact?.won ?? (band?.kind==="estimate" ? band.low : null);
    const upper = exact?.won ?? (band?.kind==="estimate" ? band.high : null);
    if(!Number.isFinite(lower) || !Number.isFinite(upper))return null;
    const stage=row[0],title=row[1];
    const span = exact ? "단일 항목 공식 중간값" : band.basis==="published-case" ? "공개 사례 참고" : "예산 추정";
    const unit = exact ? "단일 검사·처치 1회" : band.unit;
    const multiDay = /전체 치료 과정|30일|과정|장기|회차 묶음/.test(unit);
    const type = /수술/.test(stage+" "+title) ? "surgery" : /MRI|CT|내시경/.test(title) ? "scan" : "visit";
    return {index,stage,title,low:lower,high:upper,span,unit,type,multiDay};
  }
  function rowsFor(insurer,care) {
    const benefit = window.PJM023?.cares?.some(x=>x.id===care && x.group==="기타 보장");
    if(benefit)return [];
    return (window.PJM031?.entries?.[care]||[]).map((row,i)=>medicalRow(insurer,care,row,i)).filter(Boolean);
  }
  const blockedTopics = new Set(["vaccine","groom","healthcheck","neuter"]);
  function calculate(bill, terms, row) {
    if(!Number.isFinite(bill)||bill<0||!terms||!Number.isFinite(terms.ratio)||
       terms.ratio<=0||terms.ratio>1||!Number.isFinite(terms.deductible)||
       terms.deductible<0||row.multiDay)return null;
    // One eligible service on one day. No stacking of riders, no other claims.
    // Integer micro-ratio avoids 0.7 floating-point rounding a payable won down to 118,999.
    const numerator = Math.round(terms.ratio * 1000000);
    const beforeCap = Math.floor(Math.max(0,bill-terms.deductible) * numerator / 1000000);
    const cap = row.type==="surgery" && terms.surgery!=null ? terms.surgery : terms.daily;
    const limits = [bill, beforeCap];
    if(Number.isFinite(cap))limits.push(cap);
    if(Number.isFinite(terms.annual))limits.push(terms.annual);
    if(row.type==="scan" && Number.isFinite(terms.scan))limits.push(terms.scan);
    const paid = Math.max(0,Math.min(...limits));
    return {bill,payout:paid,selfPay:bill-paid,beforeCap};
  }
  function activeData(insurer,care) {
    const scope=insurer+":"+care, spec=specs[insurer]||{description:"선택한 상품의 계약 조건 미확인",plans:[]};
    if(scope!==selection.scope) {
      selection={scope,index:-1,planKey:spec.defaultKey||null,deductible:spec.deductible??null,manual:false,custom:null};
    }
    const rows=rowsFor(insurer,care);
    if(!rows.some(r=>r.index===selection.index)) {
      const preferred=care==="patella"?"슬개골 교정수술비":
        care==="cancer"?"종양 절제·암수술비":
        care==="chemo"?"항암약제비":
        care==="mri"?"MRI 촬영":
        care==="cruciate"?"십자인대 안정화 수술비":null;
      selection.index=(rows.find(r=>r.title===preferred)||rows[0]||{}).index??0;
    }
    return {spec,rows,row:rows.find(r=>r.index===selection.index)||null,
      preset:spec.plans.find(p=>p.key===selection.planKey)||null};
  }
  function termsFor(data) {
    if(selection.manual)return selection.custom;
    if(!data.preset)return null;
    return {...data.preset,deductible:selection.deductible};
  }
  function numberField(name,label,value,placeholder,required=false) {
    const shown=value==null?"":String(value);
    return '<label>'+label+'<input data-pjm045-input="'+name+'" type="number" inputmode="decimal" min="0" max="100000000" step="1"'+
      (required?' required':'')+' value="'+esc(shown)+'" placeholder="'+esc(placeholder)+'"></label>';
  }
  function render(insurer,care) {
    const data=activeData(insurer,care),{spec,rows,row}=data;
    const isPreventive=blockedTopics.has(care);
    const isBenefit=window.PJM023?.cares?.some(x=>x.id===care&&x.group==="기타 보장");
    if(isBenefit)return '<section class="pjm045-settlement"><h4>보험금·본인부담금</h4>'+
      '<p>이 항목은 일반 동물병원 의료비가 아닌 별도 특약·청구조건입니다. 일반 진료비 실손 산식을 적용하지 않습니다.</p></section>';
    if(!row)return '<section class="pjm045-settlement"><h4>보험금·본인부담금</h4><p>선택한 주제의 단일 진료비 근거가 없어 지급액을 계산하지 않습니다.</p></section>';
    const terms=termsFor(data);
    const low=!isPreventive?calculate(row.low,terms,row):null;
    const high=!isPreventive?calculate(row.high,terms,row):null;
    const valid=!!low&&!!high;
    const bounded=!!terms&&data.preset?.verified===true&&Number.isFinite(terms.daily)&&Number.isFinite(terms.annual)&&
      (row.type!=="scan"||Number.isFinite(terms.scan))&&!selection.manual;
    const mode=selection.manual?"사용자가 입력한 계약 조건으로 계산한 가상 예시":bounded?"공식 공개 플랜 조건을 적용한 가상 예시":data.preset?.provenance?.includes("2607")?"구버전 2607 참고 플랜 · 2610 계약에 적용 불가":"한도 일부 미확인 · 지급액 확정 불가";
    const ranges=valid?'<div class="pjm045-totals" aria-label="예상 진료비와 가정 보험금 및 부담금">'+
      '<div><span>선택한 처치의 참고 비용</span><strong>'+fmt(row.low)+(row.low!==row.high?' ~ '+fmt(row.high):"")+'</strong></div>'+
      '<div><span>'+(bounded?"가정상 보험금":"한도 적용 전·조건부 보험금")+'</span><strong>'+fmt(low.payout)+(low.payout!==high.payout?' ~ '+fmt(high.payout):"")+'</strong></div>'+
      '<div class="pjm045-pay"><span>'+(bounded?"가정상 본인부담금":"조건부 본인부담금")+'</span><strong>'+fmt(low.selfPay)+(low.selfPay!==high.selfPay?' ~ '+fmt(high.selfPay):"")+'</strong></div>'+
      '</div><p class="pjm045-assumption">보장 대상인 <b>동일한 1일의 단일 처치</b>, 관련 특약 가입, 면책기간 경과, 다른 보험금·기지급액 없음 등을 가정했습니다. 보장 제외·남은 한도 부족 시 보험금 0원·본인부담 전액도 가능합니다.</p>':
      '<p class="pjm045-unknown">'+(isPreventive?"예방·미용 등은 일반 의료비에서 제외될 수 있어 자동 보험금 계산을 하지 않습니다.":
        row.multiDay?"여러 날에 걸친 치료 과정은 한 건의 1일 한도 산식으로 계산할 수 없습니다.":
        "이 보험상품의 보상비율·자기부담금·선택 플랜이 확인되지 않아 지급액을 임의로 표시하지 않습니다. 아래에서 증권의 조건을 직접 입력하면 가상 계산할 수 있습니다.")+'</p>';
    const options=rows.map(r=>'<button type="button" class="pjm045-choice'+(r.index===selection.index?' is-selected':'')+
      '" aria-pressed="'+(r.index===selection.index)+'" data-pjm045-row="'+r.index+'">'+esc(r.title)+'</button>').join("");
    const plans=(spec.plans||[]).map(p=>'<button type="button" class="pjm045-choice'+(!selection.manual&&p.key===selection.planKey?' is-selected':'')+
      '" aria-pressed="'+(!selection.manual&&p.key===selection.planKey)+'" data-pjm045-plan="'+esc(p.key)+'">'+esc(p.name)+'</button>').join("");
    const premiumChoice=(!selection.manual&&data.preset&&["meritz-dog","meritz-cat","db-dog","db-cat"].includes(insurer))?
      '<div class="pjm045-deduct"><span>공제금 가정</span>'+
      [30000,50000].map(d=>'<button type="button" data-pjm045-deduct="'+d+'" aria-pressed="'+(selection.deductible===d)+
        '" class="pjm045-choice'+(selection.deductible===d?' is-selected':'')+'">'+(d/10000)+'만원</button>').join("")+'</div>':"";
    const manual=selection.custom||{};
    const manualFields='<div class="pjm045-manual-fields">'+
      numberField("percent","가입 증권의 보상비율 (%)",manual.percent,"예: 70",true)+
      numberField("deductible","1일 자기부담금 (원)",manual.deductible,"예: 30000",true)+
      numberField("daily","1일 보상한도 (원, 선택)",manual.daily,"미확인 시 비워두기")+
      numberField("annual","남은 연간 한도 (원, 선택)",manual.annual,"미확인 시 비워두기")+
      '<button type="button" class="pjm045-apply" data-pjm045-apply>직접 입력한 조건으로 계산</button></div>';
    const source=spec.source?'<span class="pjm045-source">보험사 공개 상품 안내 확인 기준</span>':"";
    return '<section class="pjm045-settlement" aria-label="보험금 및 본인부담금 가상 계산">'+
      '<h4>진료비에서 얼마를 부담할까요?</h4>'+
      '<p class="pjm045-summary">대표 처치 <b>한 가지</b>를 선택해 보험금과 직접 부담할 금액을 함께 확인합니다.</p>'+
      '<p class="pjm045-subtitle">비용을 계산할 검사·치료</p>'+
      '<div class="pjm045-choices" role="group" aria-label="계산할 세부 처치 선택">'+options+'</div>'+
      '<p class="pjm045-cost-source">'+esc(row.span)+' · '+esc(row.unit)+' · 이 비용은 병원 견적이나 질병 전체 비용이 아닙니다.</p>'+
      '<p class="pjm045-subtitle">보험 플랜·계약 조건</p>'+
      (plans?'<div class="pjm045-choices" role="group" aria-label="보험 플랜 선택">'+plans+'</div>':"")+
      premiumChoice+
      '<p class="pjm045-conditions">'+esc(spec.description)+'</p>'+
      '<button type="button" class="pjm045-manual-toggle" data-pjm045-manual aria-expanded="'+selection.manual+'">증권 조건 직접 입력'+(selection.manual?" 닫기":"")+'</button>'+
      (selection.manual?manualFields:"")+
      '<p class="pjm045-mode">'+esc(mode)+'</p>'+ranges+
      '<p class="pjm045-fine-note">임의로 여러 치료비를 합산하지 않으며, 동일일 여러 항목의 공제·합산 및 MRI/CT·관절·치과·항암 특약 중복지급은 계산하지 않습니다. 실제 지급액과 자기부담액은 가입 증권·면책·특약·잔여한도·청구 심사에 따라 다릅니다. '+source+'</p>'+
      '</section>';
  }
  function update(root) {
    const insurer=document.querySelector("#insurerSelect")?.value||"";
    const care=document.querySelector("#careSelect")?.value||"";
    const template=document.createElement("template");template.innerHTML=render(insurer,care);
    root.replaceWith(template.content.firstElementChild);
  }
  document.addEventListener("click",e=>{
    const b=e.target.closest?.("[data-pjm045-row],[data-pjm045-plan],[data-pjm045-deduct],[data-pjm045-manual],[data-pjm045-apply]");
    if(!b)return;
    const root=b.closest(".pjm045-settlement");if(!root)return;
    e.preventDefault();e.stopPropagation();
    if(b.hasAttribute("data-pjm045-row"))selection.index=Number(b.dataset.pjm045Row);
    if(b.hasAttribute("data-pjm045-plan")){
      selection.planKey=b.dataset.pjm045Plan;
      selection.manual=false;
      const insurer=document.querySelector("#insurerSelect")?.value||"";
      const selected=specs[insurer]?.plans?.find(p=>p.key===selection.planKey);
      if(selected?.key.startsWith("db2610"))selection.deductible=null;
      if(selected?.key.startsWith("samsung")){
        // A public ratio alone is not enough to estimate money. Require the
        // owner's explicit contract deductible instead of inventing 30,000.
        selection.manual=true;
        selection.custom={percent:Math.round(selected.ratio*100),
          ratio:selected.ratio,deductible:null,daily:null,annual:null,surgery:null,scan:null};
      }
    }
    if(b.hasAttribute("data-pjm045-deduct"))selection.deductible=Number(b.dataset.pjm045Deduct);
    if(b.hasAttribute("data-pjm045-manual"))selection.manual=!selection.manual;
    if(b.hasAttribute("data-pjm045-apply")){
      const fields=Object.fromEntries(Array.from(root.querySelectorAll("[data-pjm045-input]")).map(el=>[el.dataset.pjm045Input,el.value.trim()]));
      const percent=Number(fields.percent),deduct=Number(fields.deductible);
      if(fields.percent===""||fields.deductible===""||!Number.isFinite(percent)||percent<=0||percent>100||
        !Number.isFinite(deduct)||deduct<0||deduct>10000000){
        const input=root.querySelector('[data-pjm045-input="percent"]');if(input)input.focus();
        return;
      }
      const cap=v=>v===""?null:Number(v);
      if(["daily","annual"].some(k=>fields[k]!=="" && (!Number.isFinite(cap(fields[k]))||cap(fields[k])<=0||cap(fields[k])>100000000)))return;
      selection.custom={percent,ratio:percent/100,deductible:deduct,daily:cap(fields.daily),annual:cap(fields.annual),surgery:null,scan:null};
    }
    update(root);
  },true);
  window.PJM045=Object.freeze({render,calculate,rowsFor,specs});
})();
