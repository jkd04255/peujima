/* PJM-020 · Readable policy-summary experience, grounded in public product information.
 * No personal data, money inputs, insurance login, network calls, paid API or claims adjudication.
 * This page NEVER substitutes a signed contract or its full insurance terms.
 */
(function(){
  "use strict";
  const MERITZ="https://www.meritzdirect.com/pet/product.do";
  const HYUNDAI="https://m.hi.co.kr/serviceAction.do?menuId=202853";
  const DB="https://www.directdb.co.kr/ltm/prd/cpnm/custInfoView.do?partner_code=L329&pdcDvcd=l_pet_dog&searchPdcCd=31119&searchPdcTrtHistCd=00";
  const INSURERS=[
    {id:"meritz-dog",label:"메리츠화재 · 펫퍼민트 반려견",source:MERITZ},
    {id:"meritz-cat",label:"메리츠화재 · 펫퍼민트 반려묘",source:MERITZ},
    {id:"hyundai-dog",label:"현대해상 · 굿앤굿우리펫 반려견",source:HYUNDAI},
    {id:"hyundai-cat",label:"현대해상 · 굿앤굿우리펫 반려묘",source:HYUNDAI},
    {id:"db-dog",label:"DB손해보험 · 펫블리 반려견",source:DB},
    {id:"db-cat",label:"DB손해보험 · 펫블리 반려묘",source:DB}
  ];
  const CARES=[
    {id:"illness",label:"질병 통원·입원"},
    {id:"digestive",label:"구토·설사·소화기"},
    {id:"skin",label:"피부·알레르기"},
    {id:"ear",label:"외이염·귀 질환"},
    {id:"injury",label:"사고·상해 치료"},
    {id:"patella",label:"슬개골·고관절"},
    {id:"mri",label:"MRI·CT 검사"},
    {id:"dental",label:"치과·구강질환"},
    {id:"vaccine",label:"예방접종·정기검진"},
    {id:"groom",label:"미용·발톱 관리"}
  ];
  const catalog=window.PJM023||{insurers:[],cares:[],products:{},focus:{},groups:[]};
  INSURERS.push(...catalog.insurers);
  CARES.push(...catalog.cares);
  function careOptions(selected){
    const base='<optgroup label="주요 진료 항목">'+options(CARES.filter(c=>!c.group),selected)+'</optgroup>';
    return base+catalog.groups.filter(group=>group!=="고양이 주요질환"||state.insurer.endsWith("-cat")).map(group=>
      '<optgroup label="'+esc(group)+'">'+options(CARES.filter(c=>c.group===group&&(!state.insurer.endsWith('-cat')||!c.id.startsWith('dog_'))),selected)+'</optgroup>'
    ).join("");
  }
  const PLAN_LIMITS=[
    ["고급형","70%","30만원","250만원","1,500만원","100만원"],
    ["기본형","70%","15만원","250만원","1,000만원","50만원"],
    ["실속형","50%","10만원","200만원","700만원","30만원"]
  ];
  const state={mode:"all",insurer:"meritz-dog",care:"illness",previousCare:"illness",showResult:false};
  function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
  function options(items,selected){return items.map(i=>
    '<option value="'+esc(i.id)+'"'+(i.id===selected?" selected":"")+'>'+esc(i.label)+'</option>'
  ).join("");}

  /* 2025 government nationwide MEDIANS of individually published fees, not
     disease-level treatment averages, a standard package, or an actual hospital quote.
     Verified 2025-12-22 MAFRA report / 3,950 veterinary hospitals. */
  const GOV_SOURCE="농림축산식품부 · 2025 전국 동물병원 진료비 현황 (2025.12.22)";
  const POLICY_SOURCE="메리츠화재 · 2026 펫퍼민트 Puppy & Family 다이렉트 보장내용(통원/입원의료비Ⅲ)";
  const DB_POLICY_SOURCE="DB손해보험 · 2026 프로미라이프 다이렉트 펫블리 반려견보험2610(CM) 상품 안내";
  // DB's 2610 official page publishes 50/70%, 3/5만원 and the deduction-first
  // formula, but does not identify the user's daily/annual cap or optional riders.
  const DB_SAMPLE_RULES=[{name:"70% 가정",ratio:.7},{name:"50% 가정",ratio:.5}];
  const MEDIANS={
    first:{name:"초진 진찰료",won:10000},
    cbc:{name:"전혈구 검사",won:34000},
    chem:{name:"혈액화학 검사",won:80000},
    xray:{name:"X-ray 촬영",won:45000},
    ultrasound:{name:"초음파 검사",won:57000},
    ct:{name:"CT 촬영",won:600000},
    mri:{name:"MRI 촬영",won:791500},
    inpatient:{name:"반려견 입원비(1일 공개 항목)",won:60000},
    vaccine:{name:"반려견 종합백신 접종",won:25000}
  };
  /* Combinations are explicitly synthetic: sums of independent medians.
     "common" is a possible presentation, not a frequency ranking, clinical advice,
     a validated treatment bundle or mean disease bill. */
  const CARE_GUIDES={
    illness:{caption:"질병 외래에서 참고할 검사 예시",items:["first","cbc","chem"],
      others:["진단에 따른 처방·주사비 (공개 통계 없음)"],scenario:true,
      caveat:"진찰·전혈구·혈액화학 검사가 모두 시행된 가상의 통원 사례입니다. 실제 질환별 평균 총진료비가 아닙니다."},
    digestive:{caption:"구토·설사 증상 시 고려될 수 있는 검사",items:["first","chem","ultrasound"],
      others:["수액·구토 억제 처치·약값 (공개 통계 없음)"],scenario:true,
      caveat:"진찰·혈액화학·초음파를 모두 시행한 가상의 통원 사례이며, 반드시 필요한 검사 조합이 아닙니다."},
    skin:{caption:"피부 증상에서 살펴볼 비용 항목",items:["first","cbc"],
      others:["피부 도말·스크래핑·약 처방 (전국 공개 통계 없음)"],scenario:false,
      caveat:"전혈구 검사는 모든 피부질환에 실시하지 않습니다. 피부 치료비 총액을 계산할 근거가 부족합니다."},
    ear:{caption:"귀 질환에서 살펴볼 비용 항목",items:["first"],
      others:["이경 검사·귀 세포검사·세척·약 처방 (전국 공개 통계 없음)"],scenario:false,
      caveat:"실제 외이염 치료비는 별도 검사·처치·약값에 따라 달라집니다."},
    injury:{caption:"외상 평가에 사용할 수 있는 항목",items:["first","xray"],
      others:["창상 처치·봉합·마취·입원 (필요 시 별도)"],scenario:true,
      caveat:"진찰과 방사선 촬영만 시행한 가상 통원 사례입니다. 수술·처치비가 포함된 평균 비용이 아닙니다."},
    patella:{caption:"관절 상태 평가에 사용할 수 있는 항목",items:["first","xray"],
      others:["정형외과 수술·마취·재활 치료 (공개 통계 없음)"],scenario:true,
      caveat:"수술비가 아니라 관절 진찰 및 X-ray만 포함한 가상 통원 사례입니다. 첫 보장개시 후 1년 이내 발병은 제외될 수 있습니다."},
    mri:{caption:"고가 영상검사 시 참고 항목",items:["first","mri","ct"],
      others:["마취·진정·판독·추가 처치가 별도로 발생할 수 있음"],scenario:false,
      caveat:"MRI와 CT는 서로 다른 검사이며 둘 다 시행한다고 가정하지 않습니다. 영상검사 특약과 기본 의료비 한도의 적용 관계를 가입 계약에서 확인할 수 없어 지급액은 계산하지 않습니다."},
    dental:{caption:"구강질환 진료 비용 확인 항목",items:["first"],
      others:["치과 방사선·스케일링·발치·마취 (전국 공개 통계 없음)"],scenario:false,
      caveat:"치료 목적과 예방 목적에 따라 담보가 달라질 수 있어 구강치료 총액이나 지급액을 제시하지 않습니다."},
    vaccine:{caption:"예방 진료에서 공개된 항목",items:["vaccine"],
      others:["추가 예방 처치·상담은 별도"],scenario:false,
      caveat:"예방 목적의 접종·정기검진은 일반적인 의료비 특약에서 보장하지 않는 손해로 안내합니다."},
    groom:{caption:"일상 관리 비용",items:[],
      others:["발톱 관리·미용·일반 목욕 (전국 공개 통계 없음)"],scenario:false,
      caveat:"치료 목적이 아닌 관리 비용은 일반적으로 보장되지 않으며 표준 진료비 통계가 없습니다."}
  };
  for(const c of catalog.cares){
    CARE_GUIDES[c.id]={
      caption:c.label+" 관련 공개 비용 항목",items:c.items,
      others:[c.other+" (전국 공개 중간값 확인 불가)"],scenario:false,
      caveat:c.items.length?
        "표시된 항목별 공개 중간값은 "+c.label+" 진료의 평균 총비용이나 필수 검사 목록이 아닙니다.":
        "이 진료 주제의 정부 공개 단일 항목 중간값은 확인되지 않았습니다. 위 세부 금액은 공개 사례 참고 또는 서비스 예산 추정으로, 실제 청구액이 아닙니다."
    };
  }
  const PLAN_RULES=[
    {name:"고급형",ratio:.7,daily:300000,annual:15000000,surgery:2500000,scan:1000000},
    {name:"기본형",ratio:.7,daily:150000,annual:10000000,surgery:2500000,scan:500000},
    {name:"실속형",ratio:.5,daily:100000,annual:7000000,surgery:2000000,scan:300000}
  ];
  const money=n=>Number(n).toLocaleString("ko-KR")+"원";
  function sample(insurerId,careId){
    const guide=CARE_GUIDES[careId];
    const meritz=insurerId==="meritz-dog",db=insurerId==="db-dog";
    if(!guide||(!meritz&&!db)||!guide.scenario)return null;
    const total=guide.items.reduce((n,id)=>n+MEDIANS[id].won,0);
    return {total,deductible:30000,beforeCaps:db,
      plans:(meritz?PLAN_RULES:DB_SAMPLE_RULES).map(p=>{
        const preliminary=Math.floor(Math.max(total-30000,0)*p.ratio);
        // DB 2610: this is only a PRE-CAP, pre-eligibility formula illustration.
        const amount=meritz?Math.min(preliminary,p.daily,p.annual):preliminary;
        return {name:p.name,ratio:p.ratio,amount,selfPay:total-amount};
      })};
  }
  /* PJM-031 — meaningful, per-condition clinical treatment options.
     Price figures reuse only exact single-item nationwide medians; no made-up
     surgery/chemotherapy prices or claim payouts, and no extra required fields. */
  function procedureBreakdown(insurerId,careId){
    const allRows=window.PJM031?.entries?.[careId];
    if(!Array.isArray(allRows)||allRows.length===0)return "";
    const isCat=insurerId.endsWith("-cat");
    // Do not show dog-only vaccination or dog admission procedure as feline care.
    const rows=allRows.filter((row)=>!(isCat&&(row[3]==="vaccine"||row[3]==="inpatient")));
    const care=catalog.cares.find(c=>c.id===careId);
    const isBenefit=!!care&&care.group==="기타 보장";
    const sourceIds=new Set();
    let hasPublicMedian=false;
    let hasBudgetEstimate=false;
    const sum=rows.map(([stage,title,detail,medianKey])=>{
      const median=MEDIANS[medianKey];
      // These two published fee categories are dog-specific; never copy them to cats.
      const published=median&&!((medianKey==="inpatient"||medianKey==="vaccine")&&isCat);
      const band=published?null:window.PJM032?.estimate(careId,[stage,title,detail,medianKey],isCat?"cat":"dog");
      if(published)hasPublicMedian=true;
      if(band?.kind==="estimate")hasBudgetEstimate=true;
      if(band?.source&&window.PJM032?.anchors?.[band.source])sourceIds.add(band.source);
      const wonToUnit=(value)=>(value/10000).toLocaleString("ko-KR",{maximumFractionDigits:1})+"만";
      const price=published?
        "공식 공개 중간값 · "+money(median.won):
        band?.kind==="estimate"?
        "약 "+wonToUnit(band.low)+"~"+wonToUnit(band.high)+"원 / "+band.unit:
        isBenefit?"보험 보장·청구 조건 (진료비 항목 아님)":"참고 비용 산정 대상 아님";
      const grade=published?"":band?.kind==="estimate"?
        (band.basis==="published-case"?" · 공개 사례 참고":" · 예산 추정"):"";
      return '<li class="pjm031-procedure-item">'+
        '<div class="pjm031-procedure-title"><span class="pjm031-stage">'+esc(stage)+'</span>'+
        '<strong>'+esc(title)+'</strong></div>'+
        '<p>'+esc(detail)+'</p>'+
        '<small class="pjm031-price'+(published?' pjm031-published':'')+'">'+esc(price)+'<span class="pjm032-grade">'+esc(grade)+'</span></small>'+
        '</li>';
    }).join("");
    const sourceNames={government:"정부 공개 진료비",hospital:"외과 병원 공개 가격",surgery:"수술비 비교 가이드",
      example:"실제 진료비 보도",patella:"슬개골 수술비 가이드",chemo:"항암치료 경험 사례",
      oncology:"종양 수술비 사례",radiation:"방사선 치료비 자료",fip:"복막염 치료비 자료",
      funeral:"장묘업체 요금표",cruciate:"십자인대 수술비 가이드"};
    if(hasPublicMedian)sourceIds.add("government");
    const cited=Array.from(sourceIds).map(id=>
      '<a href="'+esc(window.PJM032.anchors[id])+'">'+esc(sourceNames[id]||"비용 참고자료")+'</a>').join(" · ");
    const sources='<p class="pjm032-sources"><b>비용 참고자료</b> · '+
      (cited||(hasBudgetEstimate?"세부 공식 통계가 없어 넓은 예산 가정 적용":"보장·서류 항목으로 진료비 산정 대상이 아님"))+
      '. 특정 병원의 청구액이나 전국 평균이 아닙니다.</p>';
    return '<section class="pjm031-procedures" aria-label="선택한 진료의 세부 검사와 치료">'+
      '<div class="pjm031-heading"><h4>'+(isBenefit?'관련 보장·청구 세부 항목':'세부 검사·치료 항목')+'</h4>'+
      '<span>'+rows.length+'개</span></div>'+
      '<ul class="pjm031-procedure-list">'+sum+'</ul>'+sources+
      '<p class="pjm031-procedure-caution">위 금액 중 공식 공개 중간값은 2025년 정부 조사에 포함된 단일 항목에만 해당합니다. 나머지는 일부 병원별 공개 사례·비공식 비용 가이드와 서비스의 넓은 예산 가정을 구분해 표시한 참고 범위로, 전국 통계나 진료 견적이 아닙니다. 체중·질환 정도·수술 부위·마취·입원·약제와 지역에 따라 실제 지불액은 이 범위 밖일 수 있습니다. 수술·항암·방사선 등에는 진찰·검사·마취·입원·퇴원약이 포함되는지 병원에 확인해야 하며, 카드 금액을 합산해 질환별 총액이나 보험금을 계산하면 안 됩니다.</p>'+
      '</section>';
  }
  function guidance(insurerId,careId){
    const g=CARE_GUIDES[careId];if(!g||catalog.cares.some(c=>c.id===careId&&c.group==="기타 보장"))return "";
    const meritz=insurerId==="meritz-dog",db=insurerId==="db-dog";
    const cat=insurerId.endsWith("-cat");
    // Never present a DOG-specific published fee as a feline treatment price.
    const visibleIds=g.items.filter(id=>!cat||!["inpatient","vaccine"].includes(id));
    const unitRows=visibleIds.map(id=>'<div class="pjm021-fee-row"><span>'+esc(MEDIANS[id].name)+'</span><strong>'+money(MEDIANS[id].won)+'</strong></div>').join("");
    const catNotice=cat&&visibleIds.length!==g.items.length?
      '<span class="pjm021-unpriced">반려묘에 직접 적용할 수 있는 공개 중간값을 확인하지 못해 반려견 전용 금액은 표시하지 않습니다.</span>':"";
    const other=g.others.map(x=>'<span class="pjm021-unpriced">'+esc(x)+'</span>').join("")+catNotice;
    const s=sample(insurerId,careId);
    const exampleText=db
      ?"공제 후 보상비율만 적용한 값이며 개인 계약의 1일·연간 한도, 특약, 면책 및 중복보상 조정을 적용하기 전입니다. 실제 지급액은 더 적거나 0원일 수 있습니다."
      :"3만원 공제, 해당 비용 모두 보장 대상, 의료비Ⅲ 담보 가입, 면책기간 경과, 1일·연간 잔여한도 충분, 중복보상 조정 없음 등을 가정한 계산입니다. 실제 지급액은 달라지거나 0원일 수 있습니다.";
    const scenario=s?'<section class="pjm021-example" aria-label="가정 계산 예시">'+
      '<div class="pjm021-example-heading"><strong>'+(db?"공식 산식의 가상 계산":"보험금은 얼마나 나올까요?")+'</strong><span>'+(db?"한도 적용 전 · 지급 확정 아님":"가상 예시 · 지급 확정 아님")+'</span></div>'+
      '<p>위 항목을 같은 날 모두 받고 총 '+money(s.total)+'이 청구됐다고 가정했습니다.</p>'+
      '<div class="pjm021-plan-amounts'+(db?' pjm022-plan-amounts':'')+'">'+s.plans.map(p=>
        '<div><span>'+esc(p.name)+(db?"":' ('+Math.round(p.ratio*100)+'%)')+'</span><strong>'+money(p.amount)+'</strong>'+
        '<small>'+(db?"한도 적용 전 금액":"가정상 본인부담 "+money(p.selfPay))+'</small></div>').join("")+'</div>'+
      '<p class="pjm021-calc-note">'+esc(exampleText)+'</p></section>':"";
    const imaging=meritz&&careId==="mri"?'<div class="pjm021-imaging"><strong>영상검사 연간 최초 1회 특약 한도</strong>'+
      '<p>고급형 최대 100만원 · 기본형 최대 50만원 · 실속형 최대 30만원</p>'+
      '<small>이는 검사비 한도이지, 받을 보험금의 확정액이 아닙니다.</small></div>':"";
    const policyName=meritz?POLICY_SOURCE:db?DB_POLICY_SOURCE:"선택한 보험사의 가입 시점별 상품 약관 확인 필요";
    const policyConditions=meritz
      ?"통원·입원의료비Ⅲ 특약은 각각 가입해야 하며, 플랜에 따라 보장비율 50~70%, 자기부담금 3만/5만원과 일일·연간 한도가 적용됩니다. 질병 최초 30일, 반려견 슬관절·고관절 관련 최초 1년, 이미 발병한 질환 및 예방 목적 진료의 면책 조건을 확인해야 합니다."
      :db
      ?"2026년 2610(CM) 공개 안내의 의료비 특약은 50% 또는 70% 보상비율과 3만/5만원 자기부담금을 제시합니다. 산식은 (부담 의료비 - 적용 자기부담금) × 보상비율, 이후 일일 한도 이내 지급입니다. 질병은 계약일부터 30일 경과 후, 슬관절·고관절 탈구 및 유사 질환·상해는 1년 경과 후 개시합니다. 치과·특정피부 약물·영상검사 확대는 별도 특약 조건을 확인해야 합니다. 개인 계약의 일일·연간 한도 및 다른 지급 제한은 확인되지 않았습니다."
      :"해당 보험사의 반려견·반려묘 가입 계약에 적용되는 지급비율, 특약, 면책기간과 한도는 아직 검증되지 않았습니다. 다른 보험사의 조건을 대신 적용하지 않습니다.";
    const unsupported=!(meritz||db)?
      '<p class="pjm021-pending">이 보험 상품의 가입 버전별 지급 규칙은 아직 검증하지 않아 예상 보험금을 표시하지 않습니다. 공개 진료비와 별도 참고 예산 범위만 안내합니다.</p>':"";
    const specialPending=db&&!s?
      '<p class="pjm021-pending">이 항목은 처치 비용 또는 특약·한도 자료가 부족하여 지급액을 계산하지 않습니다. 가입한 계약의 보장 내용에 따라 달라집니다.</p>':"";
    // If no exact government-published line item applies, show the PJM-032
    // per-procedure estimates above without repeating an empty official-fee card.
    // Supporting references still move to the single optional bottom disclosure.
    const hasPublishedFee=visibleIds.length>0;
    return (hasPublishedFee?
      '<section class="pjm021-fee-guide" aria-label="공식 공개 진료비와 가상 보장 예시">'+
      '<h4>공식 공개 진료비 참고</h4>'+
      '<p class="pjm021-subhead">'+esc(g.caption)+'</p>'+
      '<div class="pjm021-fees">'+unitRows+other+'</div>'+
      '<p class="pjm021-cost-notice">이 금액은 2025년 전국 동물병원 <b>개별 항목 중간값</b>입니다. 질환별 총 치료비·수술비 또는 진료 권장 목록이 아닙니다.</p>':
      other)+scenario+imaging+specialPending+unsupported+
      '<details class="pjm021-policy-details"><summary>근거와 확인할 조건 보기</summary>'+
      '<div><b>보험 보장 자료</b><p>'+esc(policyName)+'</p>'+
      '<p>'+esc(policyConditions)+'</p>'+
      '<b>진료비 자료</b><p>'+esc(GOV_SOURCE)+'</p>'+
      '<p>'+esc(g.caveat)+'</p>'+
      '<small>원문 약관 PDF 전문과 가입한 증권을 자동 판독한 결과는 아닙니다. 가입 시기·특약·진단·잔여 한도에 따라 지급 여부가 달라집니다.</small></div></details>'+
      (hasPublishedFee?'</section>':'');
  }
  const planDetails='<details class="pjm020-details"><summary>플랜별 보장 한도 자세히 보기</summary>'+
    '<div class="pjm020-table-wrap"><table><thead><tr>'+
    '<th scope="col">플랜</th><th scope="col">비율</th><th scope="col">통원·입원 1일</th>'+
    '<th scope="col">수술 당일</th><th scope="col">연간</th><th scope="col">영상검사</th>'+
    '</tr></thead><tbody>'+PLAN_LIMITS.map(p=>'<tr>'+p.map(x=>'<td>'+esc(x)+'</td>').join("")+'</tr>').join("")+
    '</tbody></table></div><p>공개 상품 안내의 플랜별 예시 한도입니다. 가입 시점·특약·자기부담금에 따라 달라질 수 있습니다.</p></details>';
  const dbDetails='<details class="pjm020-details pjm022-db-details"><summary>DB 펫블리 보장 조건 자세히 보기</summary>'+
    '<p>2026년 펫블리 반려견보험2610(CM) 공식 상품 안내 기준입니다. 의료비 특약을 가입했다고 가정하며 50% 또는 70% 보상비율과 3만원 또는 5만원 자기부담금이 선택 가능합니다.</p>'+
    '<p>질병은 최초 30일 경과 후, 슬관절·고관절 탈구 등은 1년 경과 후 보장 개시합니다. 치과·특정피부 약물치료·MRI/CT 검사비 확대는 해당 특약 가입 여부를 확인해야 합니다.</p>'+
    '<p>개별 계약의 일일·연간 한도, 이전 보험금 지급액 및 다른 보험 보유 여부는 확인되지 않습니다. 화면의 DB 가상 계산은 한도 적용 전 금액입니다.</p></details>';
  function coverageInfo(insurerId,careId){
    const p=catalog.products[insurerId];if(!p)return "";
    const ins=INSURERS.find(i=>i.id===insurerId);
    const care=catalog.cares.find(x=>x.id===careId);
    const isExtra=care&&care.group==="기타 보장";
    const clause=(catalog.clauseEvidence?.[insurerId]||{})[careId]||null;
    const note=clause?.summary||(catalog.focus[insurerId]||{})[careId]||
      (isExtra?"이 상품의 해당 부가보장 특약은 확인되지 않았습니다. 다른 보험사의 보장을 이 계약에도 적용하지 않습니다.":
      "이 진료의 검사·약제·처치가 보장되는지는 진단명, 치료 목적, 실제 가입한 특약 및 면책기간에 따라 달라집니다.");
    const [version,scope,ratio,deductible,limit,waiting,riders,source]=p;
    const row=(label,detail)=>'<div class="pjm023-fact"><dt>'+esc(label)+'</dt><dd>'+esc(detail)+'</dd></div>';
    const audit=(catalog.evidence||{})[insurerId]||null;
    const evidence=audit?({A:"A · 일부 약관 원문 확인",B:"B · 상품 안내 확인",C:"C · 공식 소개 자료",D:"D · 약관 원문 미검증·미확보"}[audit.grade]||"근거 확인 필요"):"근거 확인 필요";
    const auditContext=audit?
      '<p class="pjm026-source-meta">검토 기준: '+esc(audit.version)+'</p>'+
      '<p class="pjm026-version-warning">주의 · '+esc(audit.warning)+'</p>':"";
    const clauseContext=clause?
      '<p class="pjm027-clause-origin">약관 출처 · '+esc(clause.version)+' / '+esc(clause.clause)+'</p>':"";
    const kb2607=insurerId.startsWith("kb-")?catalog.kb2607:null;
    const kbSpecies=insurerId==="kb-dog"?"dog":"cat";
    const kbChoices=kb2607?kb2607.products.filter(x=>x.species===kbSpecies):[];
    const kbIdentifier=kbChoices.map(x=>x.channel+" "+x.code).join(" · ");
    const kbNotice=kb2607?
      '<p class="pjm029-kb-editions">26.07 상품 구분 · '+esc(kbIdentifier)+' (공식 공시 확인, 약관 본문 미검증)</p>':"";
    const kbNote=kb2607?((kb2607.secondary[insurerId]||{})[careId]||
      "선택한 항목의 26.07 보장·한도·대기기간은 약관 본문에서 직접 검증하지 못했습니다."):"";
    const kbDetails=kb2607?
      '<div class="pjm029-kb-details"><h5>26.07 자료 확인 범위</h5>'+
      '<p><strong>공식 공시</strong> · '+esc(kbIdentifier)+' 상품 존재 확인. 일반형/다이렉트형은 별개입니다.</p>'+
      '<p><strong>선택 항목의 2차 해설</strong> · '+esc(kbNote)+'</p>'+
      '<p>26.07의 원문 파일 다운로드 주소를 확인했으나 PDF 본문을 직접 대조하지 못했습니다. 26.01 조건 또는 제3자 해설을 실제 26.07 계약의 지급 조건으로 확정하지 않습니다.</p></div>':"";
    const extraContext=isExtra?
      '<p class="pjm023-extra-warning">이 항목은 일반 진료비 실손 담보가 아닌 별도 보장 또는 청구 절차입니다. 관련 특약의 실제 가입 여부가 확인되지 않으면 지급 가능하다고 판단할 수 없습니다.</p>':"";    return '<section class="pjm023-coverage" aria-label="보험 상품의 공개 보장 조건">'+
      '<div class="pjm023-head"><h4>보험 상품 보장 확인</h4><span>'+esc(evidence)+'</span></div>'+
      '<p class="pjm023-version">'+esc((ins?ins.label+' · ':'')+version)+'</p>'+auditContext+kbNotice+
      '<dl class="pjm023-facts">'+row(isExtra?"기본 의료비":"어떤 진료",scope)+row("보상비율",ratio)+row("자기부담금",deductible)+'</dl>'+extraContext+
      '<p class="pjm023-focus"><b>'+(isExtra?'선택한 보장·청구 항목의 확인 사항':'선택한 진료의 확인 사항')+'</b> '+esc(note)+'</p>'+clauseContext+
      '<details class="pjm023-more"><summary>한도·면책기간·특약 자세히 보기</summary><dl>'+
      row("일일·연간 한도",limit)+row("보장개시·면책",waiting)+row("확장보장",riders)+
      '</dl>'+kbDetails+(clause?.details?.length?
        '<div class="pjm028-clause-details"><h5>이 특약의 실제 지급 조건</h5><dl>'+
        clause.details.map(([label,detail])=>row(label,detail)).join("")+'</dl></div>':"")+
      '<p>검토 자료: '+esc(source)+(insurerId.startsWith('nh-')?' (보험사 공식 원문 약관이 아닌 판매 대리점 안내)':'')+'</p>'+
      '<p>가입 시점의 증권·약관 및 진료 영수증을 대조한 결과가 아닙니다. 해당 진료의 보장 여부나 지급액을 확정하지 않습니다.</p></details>'+
      '</section>';
  }
  function summarize(insurerId,careId){
    const insurer=INSURERS.find(i=>i.id===insurerId);
    if(!insurer||!CARES.find(c=>c.id===careId))return {status:"추가 확인 필요",title:"선택한 상품을 확인해 주세요",description:"상품과 진료 항목을 다시 선택해 주세요.",points:[],source:null,showPlans:false};
    const meritzDog=insurerId==="meritz-dog", meritzCat=insurerId==="meritz-cat";
    const hyundaiDog=insurerId==="hyundai-dog";
    const base={status:"가입 계약 확인 필요",title:"계약별 보장 조건을 확인해야 합니다",
      description:"보험사 이름만으로 보장 금액이나 지급 여부를 확정할 수 없습니다.",
      points:["가입 시점의 상품 약관과 의료비 특약을 확인하세요.","보장비율·공제금·회당 및 연간 한도는 계약마다 다를 수 있습니다."],
      source:insurer.source,showPlans:false};
    if(catalog.cares.some(i=>i.id===careId)){
      const term=catalog.cares.find(i=>i.id===careId);
      const preventive=careId==="neuter"||careId==="healthcheck";
      const extra=term.group==="기타 보장";
      const docs=careId==="claim_docs";
      return {...base,status:preventive?"일반적으로 보장 제외":docs?"보험금 청구 준비":extra?"개별 부가특약 확인 필요":"특약·진단 확인 필요",
        title:term.label,
        description:preventive?"예방·일상 관리 목적의 진료는 일반 의료비 특약에서 보장하지 않을 수 있습니다. 치료 목적의 예외는 계약별 확인이 필요합니다.":
          docs?"진료비 영수증·세부내역서·진료기록부 등을 준비할 수 있습니다. 보험사·청구 금액·상병명에 따라 추가 서류가 필요합니다. 개인정보나 파일을 프지마에 제출할 필요는 없습니다.":
          extra?"의료비와 다른 별도 특약입니다. 지급 대상 사고, 제외 사유, 가입 여부 및 실제 지급 금액을 구분해 확인해야 합니다.":
          "이 진료의 검사·처치·약제비가 모두 같은 보장에 포함되는 것은 아닙니다. 아래 상품별 보장 조건과 면책을 확인해 주세요.",
        points:docs?["보험사 공식 보험금 청구 안내에서 서류 목록과 적용 기준을 확인하세요.","진료비 영수증·세부내역서 원본은 이 화면에 업로드하지 마세요."]:
          extra?["실제 계약에 해당 부가특약이 있는지 확인해야 합니다.","사고 요건·서류·공제금·책임 한도 등 확인 전에는 지급액을 계산하지 않습니다."]:
          ["실제 보장 여부는 가입 담보와 진단명·치료 목적에 따라 달라집니다.","개별 영수증 항목과 공제금·한도·기지급금액 등은 확인되지 않았습니다."],
        showPlans:false,showDBDetails:false};
    }
    if(careId==="vaccine"||careId==="groom"){
      return {...base,status:"일반적으로 보장 제외",title:careId==="vaccine"?"예방 목적의 진료는 대부분 제외됩니다":"단순 미용·일상 관리는 대부분 제외됩니다",
        description:careId==="vaccine"?"예방접종과 증상이 없는 정기검진은 일반적으로 의료비 보장 대상이 아닙니다.":"미용·발톱 정리처럼 치료 목적이 아닌 관리는 일반적으로 의료비 보장 대상이 아닙니다.",
        points:["치료를 위한 처치라면 진단명과 특약에 따라 달라질 수 있습니다.","최종 제외 여부는 가입 약관의 면책 조항을 확인해야 합니다."]};
    }
    if(meritzDog){
      if(careId==="digestive"||careId==="skin"||careId==="ear")return {...base,status:"보장 검토 가능",title:careId==="digestive"?"구토·설사 등 소화기 진료":careId==="skin"?"피부·알레르기 진료":"외이염·귀 질환 진료",
        description:"치료 목적의 질병 통원·입원은 의료비Ⅲ 특약을 가입한 경우 보장 검토 대상입니다. 진찰·검사 비용 전체가 항상 보장되는 것은 아닙니다.",
        points:["질병 최초 보장개시 후 30일 및 기존 질환 관련 면책 여부를 확인해야 합니다.","통원·입원 특약, 보장비율·공제금·남은 한도를 적용해야 합니다."],showPlans:true};
      if(careId==="illness")return {...base,status:"보장 검토 가능",title:"질병 통원·입원 의료비",
        description:"의료비Ⅲ 담보가 포함된 계약은 보장비율 50~70%, 통원·입원 1일 최대 10만~30만원 수준의 플랜별 한도를 안내합니다.",
        points:["첫 보험개시 후 30일 이내 발병한 질병은 제외될 수 있습니다.","기왕증, 자기부담금 및 연간 한도를 확인해야 합니다."],showPlans:true};
      if(careId==="injury")return {...base,status:"보장 검토 가능",title:"사고·상해 치료 의료비",
        description:"의료비Ⅲ 담보가 있다면 통원·입원·수술 보장을 검토할 수 있으며, 보장비율 50~70%와 플랜별 지급 한도가 적용됩니다.",
        points:["보험개시 이전 사고나 기왕증은 보장되지 않을 수 있습니다.","수술·통원·입원 구분과 자기부담금, 지급 한도를 확인하세요."],showPlans:true};
      if(careId==="patella")return {...base,status:"면책기간 확인 필수",title:"슬개골·고관절 보장",
        description:"반려견 슬관절·고관절 관련 질환은 최초 보장개시 후 1년 이내 발병하면 보장 제외로 안내됩니다.",
        points:["최초 발병 시점과 갱신계약 여부를 확인하세요.","1년 이후에도 기왕증·특약·계약 조건에 따라 달라집니다."]};
      if(careId==="mri")return {...base,status:"조건부 보장 검토",title:"MRI·CT·내시경 검사",
        description:"의료비Ⅲ 상품 안내에는 영상검사에 대해 최초 연 1회, 플랜별 최대 30만~100만원 한도가 제시돼 있습니다.",
        points:["해당 담보 가입과 올해 검사비 지급 여부를 확인하세요.","수의사의 검사 목적·진단명, 자기부담금 등도 영향을 줍니다."],showPlans:true};
      if(careId==="dental")return {...base,status:"약관 확인 필요",title:"치과·구강질환 치료",
        description:"구강질환 보장 안내가 있지만, 질병 치료인지 예방·미용 목적 처치인지에 따라 다를 수 있습니다.",
        points:["구강질환 관련 담보와 면책 조항을 확인하세요.","일반 스케일링을 자동으로 보장되는 치료로 판단하지 않습니다."]};
    }
    if(insurerId==="db-dog"){
      const dbBase={...base,showDBDetails:true};
      if(careId==="patella")return {...dbBase,status:"면책기간 확인 필수",title:"슬관절·고관절 탈구 관련 진료",
        description:"펫블리 반려견보험2610의 공식 안내에는 슬관절·고관절 탈구와 유사 질환·상해가 가입일부터 1년이 지난 다음 날부터 보장 개시된다고 설명돼 있습니다.",
        points:["의료비 관련 특약 가입과 최초 사고·발병 시점이 중요합니다.","기존 질환, 일일·연간 한도 및 실제 계약의 지급 제한을 확인해야 합니다."]};
      if(careId==="mri"||careId==="dental"||careId==="skin"){
        const titles={mri:"MRI·CT 검사비 확대",dental:"치과·구강질환 확장보장",skin:"특정피부 약물치료 확장보장"};
        return {...dbBase,status:"특약 가입 여부 확인",title:titles[careId],
          description:"DB손해보험 공식 펫블리 2610 안내에서 관련 확장보장 특약을 소개하지만, 가입 여부와 진료비 보장 대상은 별도 확인이 필요합니다.",
          points:["해당 확장보장 특약 가입과 실제 치료 목적을 확인해야 합니다.","검사·처치별 금액과 계약별 한도가 불확실해 보험금 확정 계산은 제공하지 않습니다."]};
      }
      if(careId==="illness"||careId==="digestive"||careId==="ear"||careId==="injury"){
        const titles={illness:"질병 통원·입원 의료비",digestive:"구토·설사 관련 진료",ear:"외이염·귀 질환 치료",injury:"사고·상해 치료"};
        return {...dbBase,status:"보장 검토 가능",title:titles[careId],
          description:"펫블리 반려견보험2610의 공개 안내는 의료비 특약 가입 시 보상비율 50%·70%, 자기부담금 3만·5만원을 소개합니다. 아래 금액은 3만원 공제 시 한도 적용 전 계산 예시입니다.",
          points:["질병은 가입 후 30일 경과와 기존 질환 여부를 확인하세요.","실제 보장액은 계약별 일일·연간 한도와 선택한 자기부담금에 따라 달라집니다."]};
      }
      return dbBase;
    }
    if(hyundaiDog&&(careId==="patella"||careId==="mri"||careId==="dental")){
      const titles={patella:"슬관절·고관절",mri:"MRI·CT 검사",dental:"치과·구강질환"};
      return {...base,status:"특약 가입 여부 확인",title:titles[careId]+" 보장",
        description:"현대해상 상품 안내에는 해당 분야의 추가 보장 특약이 소개돼 있습니다. 특약을 가입하지 않았다면 같은 보장이 적용된다고 볼 수 없습니다.",
        points:["가입 증권에서 해당 보장 특약을 확인하세요.","적용 약관의 지급비율·면책기간·한도를 확인해야 합니다."]};
    }
    if(meritzCat)return {...base,title:"반려묘 가입 상품의 약관 확인이 필요합니다",
      description:"반려견 상품에 표시된 비율과 한도를 반려묘 계약에 그대로 적용하지 않습니다."};
    return base;
  }
  /* PJM-030 — collect non-essential copy into ONE opt-in, small-print
     area at the very end of each result. Existing source/term elements
     retain their classes and interactions for policy traceability. */
  function compactSupplementalNotes(markup){
    const template=document.createElement("template");
    template.innerHTML=markup;
    const result=template.content.querySelector(".pjm020-result");
    if(!result)return markup;
    const groups=[
      {label:"진료비·가상 계산 기준",selectors:[
        ".pjm021-cost-notice",".pjm021-unpriced",
        ".pjm021-example .pjm021-calc-note",
        ".pjm021-imaging small",".pjm021-pending",
        ".pjm031-procedure-caution",".pjm032-sources"
      ]},
      {label:"가입·보장 유의사항",selectors:[
        ".pjm023-extra-warning",".pjm021-conditions",".pjm020-note"
      ]},
      {label:"보험 상품 버전과 출처",selectors:[
        ".pjm023-head > span",".pjm026-source-meta",
        ".pjm026-version-warning",".pjm029-kb-editions",
        ".pjm027-clause-origin"
      ]},
      {label:"약관·한도·청구 조건",selectors:[
        ".pjm023-more",".pjm021-policy-details",".pjm020-details"
      ]}
    ];
    const notes=document.createElement("details");
    notes.className="pjm030-fineprint";
    const summary=document.createElement("summary");
    summary.textContent="추가 안내 · 출처와 계산 기준 보기";
    notes.appendChild(summary);
    const content=document.createElement("div");
    content.className="pjm030-fineprint-content";
    for(const group of groups){
      const block=document.createElement("section");
      block.className="pjm030-note-group";
      let count=0;
      for(const selector of group.selectors){
        // Nodes are moved, never cloned: no duplicate notices or DOM IDs.
        for(const element of Array.from(result.querySelectorAll(selector))){
          if(element.closest(".pjm030-fineprint"))continue;
          if(selector===".pjm023-head > span"){
            const label=document.createElement("p");
            label.className="pjm030-evidence-note";
            label.textContent="근거 확인 수준 · "+element.textContent.trim();
            element.remove();
            block.appendChild(label);
          }else{
            block.appendChild(element);
          }
          count++;
        }
      }
      if(!count)continue;
      const heading=document.createElement("h5");
      heading.textContent=group.label;
      block.prepend(heading);
      content.appendChild(block);
    }
    if(!content.children.length)return markup;
    notes.appendChild(content);
    result.appendChild(notes);
    return template.innerHTML;
  }
  function output(){
    if(!state.showResult)return '<p class="pjm020-instruction">보험과 치료 항목을 선택한 뒤 결과를 확인하세요.</p>';
    const x=summarize(state.insurer,state.care);
    const extra=guidance(state.insurer,state.care);
    const pts=x.points.map(s=>'<li>'+esc(s)+'</li>').join("");
    return compactSupplementalNotes('<article class="insurance-result pjm020-result" role="status" aria-live="polite">'+
      '<span class="pjm020-status">'+esc(x.status)+'</span><h3>'+esc(x.title)+'</h3>'+
      '<p>'+esc(x.description)+'</p>'+coverageInfo(state.insurer,state.care)+procedureBreakdown(state.insurer,state.care)+extra+(pts?'<div class="pjm021-conditions"><strong>보장 판단에서 중요한 조건</strong><ul>'+pts+'</ul></div>':"")+
      (x.showPlans?planDetails:"")+(x.showDBDetails?dbDetails:"")+
      '<p class="pjm020-note">해당 상품의 공개 안내를 요약한 내용이며, 가입 계약에 따라 결과가 달라질 수 있습니다.</p>'+
      ''+
      '</article>');
  }
  function section(mode,legacyCare){
    if(mode!==state.mode){state.mode=mode;state.insurer=mode==="cat"?"meritz-cat":"meritz-dog";if((mode!=="cat"&&state.care.startsWith("feline_"))||(mode==="cat"&&state.care.startsWith("dog_")))state.care="illness";state.showResult=false;}
    if(legacyCare&&state.previousCare!==legacyCare&&CARES.some(i=>i.id===legacyCare)){
      state.previousCare=legacyCare;state.care=legacyCare;state.showResult=false;
    }
    return '<section class="section insurance pjm020-insurance" id="insurance">'+
      '<div class="site-width pjm020-wrap">'+
      '<div class="pjm020-heading"><h2>내 보험,<br><em>어디까지 보장될까요?</em></h2>'+
      '<p>대표 진료 항목의 공개 비용과 보험 보장 예시를 한 번에 확인해 보세요.</p></div>'+
      '<div class="insurance-card pjm020-card">'+
      '<label for="insurerSelect">가입 보험·상품<select id="insurerSelect">'+
      options(INSURERS,state.insurer)+'</select></label>'+
      '<label for="careSelect">궁금한 치료·검사<select id="careSelect">'+
      careOptions(state.care)+'</select></label>'+
      '<button type="button" class="primary-btn insurance-button">보장 내용 확인하기</button>'+
      '<div class="pjm020-output" id="pjm020Output">'+output()+'</div>'+
      '</div>'+
      '<p class="insurance-disclaimer">가입 시점·특약과 실제 진단·청구 조건에 따라 보험금이 달라집니다. 이 요약은 보험금 지급 확정이나 진단이 아니며, 개인 가입정보를 수집하거나 저장하지 않습니다.</p>'+
      '</div></section>';
  }
  document.addEventListener("change",event=>{
    if(!event.target.closest("#insurance"))return;
    if(event.target.id!=="insurerSelect"&&event.target.id!=="careSelect")return;
    // Prevent the legacy change handler from rerendering the entire page and losing focus.
    event.stopImmediatePropagation();
    const insurerChanged=event.target.id==="insurerSelect";
    state[insurerChanged?"insurer":"care"]=event.target.value;
    if(insurerChanged){
      if((!state.insurer.endsWith("-cat")&&state.care.startsWith("feline_"))||(state.insurer.endsWith("-cat")&&state.care.startsWith("dog_")))state.care="illness";
      const careSelect=document.getElementById("careSelect");
      if(careSelect)careSelect.innerHTML=careOptions(state.care);
    }
    state.showResult=false;
    const out=document.getElementById("pjm020Output");if(out)out.innerHTML=output();
  },true);
  document.addEventListener("click",event=>{
    if(!event.target.closest("#insurance .insurance-button"))return;
    event.preventDefault();event.stopImmediatePropagation();
    state.showResult=true;
    const out=document.getElementById("pjm020Output");if(out){out.innerHTML=output();out.scrollIntoView({behavior:"smooth",block:"nearest"});}
  },true);
  window.PJM019=Object.freeze({section,summarize,insurers:INSURERS,careTypes:CARES,sample,guidance,procedureBreakdown,medianCosts:MEDIANS,policyRules:PLAN_RULES});
})();