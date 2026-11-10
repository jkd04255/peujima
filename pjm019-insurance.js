/* PJM-020 · Readable policy-summary experience, grounded in public product information.
 * No personal data, money inputs, insurance login, network calls, paid API or claims adjudication.
 * This page NEVER substitutes a signed contract or its full insurance terms.
 */
(function(){
  "use strict";
  const MERITZ="https://www.meritzdirect.com/pet/product.do";
  const HYUNDAI="https://m.hi.co.kr/serviceAction.do?menuId=202853";
  const DB="https://www.dongbuinsurance.com/FWMALV6783.do";
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
    {id:"injury",label:"사고·상해 치료"},
    {id:"patella",label:"슬개골·고관절"},
    {id:"mri",label:"MRI·CT 검사"},
    {id:"dental",label:"치과·구강질환"},
    {id:"vaccine",label:"예방접종·정기검진"},
    {id:"groom",label:"미용·발톱 관리"}
  ];
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
  const planDetails='<details class="pjm020-details"><summary>플랜별 보장 한도 자세히 보기</summary>'+
    '<div class="pjm020-table-wrap"><table><thead><tr>'+
    '<th scope="col">플랜</th><th scope="col">비율</th><th scope="col">통원·입원 1일</th>'+
    '<th scope="col">수술 당일</th><th scope="col">연간</th><th scope="col">영상검사</th>'+
    '</tr></thead><tbody>'+PLAN_LIMITS.map(p=>'<tr>'+p.map(x=>'<td>'+esc(x)+'</td>').join("")+'</tr>').join("")+
    '</tbody></table></div><p>공개 상품 안내의 플랜별 예시 한도입니다. 가입 시점·특약·자기부담금에 따라 달라질 수 있습니다.</p></details>';
  function summarize(insurerId,careId){
    const insurer=INSURERS.find(i=>i.id===insurerId);
    if(!insurer||!CARES.find(c=>c.id===careId))return {status:"추가 확인 필요",title:"선택한 상품을 확인해 주세요",description:"상품과 진료 항목을 다시 선택해 주세요.",points:[],source:null,showPlans:false};
    const meritzDog=insurerId==="meritz-dog", meritzCat=insurerId==="meritz-cat";
    const hyundaiDog=insurerId==="hyundai-dog";
    const base={status:"가입 계약 확인 필요",title:"계약별 보장 조건을 확인해야 합니다",
      description:"보험사 이름만으로 보장 금액이나 지급 여부를 확정할 수 없습니다.",
      points:["가입 시점의 상품 약관과 의료비 특약을 확인하세요.","보장비율·공제금·회당 및 연간 한도는 계약마다 다를 수 있습니다."],
      source:insurer.source,showPlans:false};
    if(careId==="vaccine"||careId==="groom"){
      return {...base,status:"일반적으로 보장 제외",title:careId==="vaccine"?"예방 목적의 진료는 대부분 제외됩니다":"단순 미용·일상 관리는 대부분 제외됩니다",
        description:careId==="vaccine"?"예방접종과 증상이 없는 정기검진은 일반적으로 의료비 보장 대상이 아닙니다.":"미용·발톱 정리처럼 치료 목적이 아닌 관리는 일반적으로 의료비 보장 대상이 아닙니다.",
        points:["치료를 위한 처치라면 진단명과 특약에 따라 달라질 수 있습니다.","최종 제외 여부는 가입 약관의 면책 조항을 확인해야 합니다."]};
    }
    if(meritzDog){
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
  function output(){
    if(!state.showResult)return '<p class="pjm020-instruction">보험과 치료 항목을 선택한 뒤 결과를 확인하세요.</p>';
    const x=summarize(state.insurer,state.care);
    const pts=x.points.map(s=>'<li>'+esc(s)+'</li>').join("");
    return '<article class="insurance-result pjm020-result" role="status" aria-live="polite">'+
      '<span class="pjm020-status">'+esc(x.status)+'</span><h3>'+esc(x.title)+'</h3>'+
      '<p>'+esc(x.description)+'</p>'+(pts?'<ul>'+pts+'</ul>':"")+
      (x.showPlans?planDetails:"")+
      '<p class="pjm020-note">해당 상품의 공개 안내를 요약한 내용이며, 가입 계약에 따라 결과가 달라질 수 있습니다.</p>'+
      (x.source?'<a href="'+esc(x.source)+'" target="_blank" rel="noopener noreferrer">공식 상품 안내 확인 ↗</a>':"")+
      '</article>';
  }
  function section(mode,legacyCare){
    if(mode!==state.mode){state.mode=mode;state.insurer=mode==="cat"?"meritz-cat":"meritz-dog";state.showResult=false;}
    if(legacyCare&&state.previousCare!==legacyCare&&CARES.some(i=>i.id===legacyCare)){
      state.previousCare=legacyCare;state.care=legacyCare;state.showResult=false;
    }
    return '<section class="section insurance pjm020-insurance" id="insurance">'+
      '<div class="site-width pjm020-wrap">'+
      '<div class="pjm020-heading"><h2>내 보험,<br><em>어디까지 보장될까요?</em></h2>'+
      '<p>가입 보험과 진료 항목을 선택하면 필요한 내용만 정리해 드립니다.</p></div>'+
      '<div class="insurance-card pjm020-card">'+
      '<label for="insurerSelect">가입 보험·상품<select id="insurerSelect">'+
      options(INSURERS,state.insurer)+'</select></label>'+
      '<label for="careSelect">궁금한 치료·검사<select id="careSelect">'+
      options(CARES,state.care)+'</select></label>'+
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
    state[event.target.id==="insurerSelect"?"insurer":"care"]=event.target.value;
    state.showResult=false;
    const out=document.getElementById("pjm020Output");if(out)out.innerHTML=output();
  },true);
  document.addEventListener("click",event=>{
    if(!event.target.closest("#insurance .insurance-button"))return;
    event.preventDefault();event.stopImmediatePropagation();
    state.showResult=true;
    const out=document.getElementById("pjm020Output");if(out){out.innerHTML=output();out.scrollIntoView({behavior:"smooth",block:"nearest"});}
  },true);
  window.PJM019=Object.freeze({section,summarize,insurers:INSURERS,careTypes:CARES});
})();