/* PJM-032: broad KRW budgeting ranges for pet care, not national medians.
 * Published official single-item medians remain owned by PJM019.MEDIANS.
 * Other numbers are conservative illustrative envelopes; referenced cases
 * are NOT statistically representative of all Korean veterinary hospitals.
 * The base unit is one visit/service unless a separate unit is supplied.
 * Never sum these bands to predict full disease bills or insurance payouts.
 */
(function(){
"use strict";
const anchors=Object.freeze({
 government:"https://www.animalclinicfee.or.kr/",
 hospital:"https://www.daangn.com/kr/local-profile/%EB%B3%B8%EC%99%B8%EA%B3%BC%EB%8F%99%EB%AC%BC%EC%9D%98%EB%A3%8C%EC%84%BC%ED%84%B0-bs7o6dobaejz/",
 surgery:"https://www.pethealthplus.kr/cost-search/surgery",
 example:"https://www.asiae.co.kr/article/2026032611095477307",
 patella:"https://isclinic.co.kr/dog-patella-surgery-cost-2026/",
 chemo:"https://carpe616.tistory.com/12?category=979087",
 oncology:"https://mipinol.co.kr/%EA%B0%95%EC%95%84%EC%A7%80-%EC%A2%85%EC%96%91-%EC%88%98%EC%88%A0%EB%B9%84-%EC%8B%A4%EC%A0%9C-%EC%82%AC%EB%A1%80%EC%99%80-%ED%95%A8%EA%BB%98-%EB%8B%A8%EC%B9%BC%EC%97%90-%EC%A0%95%EB%A6%AC/",
 radiation:"https://petcarenote.co.kr/blog/pet-cancer-radiation-therapy-cost/",
 fip:"https://www.petcarenote.co.kr/blog/feline-infectious-peritonitis-treatment-cost/",
 funeral:"https://pet119.net/pricing",
 cruciate:"https://parkdaeri.com/%EA%B0%95%EC%95%84%EC%A7%80-%EC%8B%AD%EC%9E%90%EC%9D%B8%EB%8C%80-%EC%88%98%EC%88%A0-%EB%B9%84%EC%9A%A9-%ED%8F%89%EA%B7%A0-%EA%B2%AC%EC%A0%81%EA%B3%BC-tplo-%EC%9D%B8%EA%B3%B5%EC%9D%B8%EB%8C%80/"
});
function cost(low,high,unit="1회",basis="budget",source=null){
 if(!(Number.isFinite(low)&&Number.isFinite(high)&&low>0&&high>=low))throw Error("invalid estimate");
 if(!["budget","published-case"].includes(basis))throw Error("invalid evidence type");
 return Object.freeze({low,high,unit,basis,source,kind:"estimate"});
}
const R={
 patella: {
  "슬개골 교정수술비":cost(800000,3000000,"편측 1회","published-case","patella"),
  "동반 십자인대·골변형 수술":cost(1500000,5000000,"동반 수술 1회","published-case","cruciate"),
  "수술 후 재활·재진료비":cost(50000,150000,"회","budget")
 },
 limping:{
  "슬개골·인대·고관절 수술비":cost(800000,5000000,"한쪽 수술 1회","published-case","surgery")
 },
 cruciate:{
  "십자인대 안정화 수술비":cost(1500000,3500000,"편측 1회","published-case","cruciate")
 },
 cancer:{
  "세포검사·조직검사비":cost(50000,350000,"검사 1회","budget"),
  "암 병기 평가·영상검사비":cost(100000,1200000,"진단 과정 1회","budget"),
  "종양 절제·암수술비":cost(300000,5000000,"수술 1회","published-case","oncology"),
  "항암약물치료비":cost(200000,700000,"항암 투여 1회","published-case","chemo"),
  "방사선치료비":cost(500000,1500000,"방사선 치료 1회","published-case","radiation"),
  "면역·표적치료비":cost(300000,3000000,"투여/처방 1회","budget"),
  "통증관리·입원·재검사비":cost(100000,1000000,"진료·입원 과정 1회","budget")
 },
 chemo:{
  "항암 전 상태·혈액검사":cost(30000,200000,"진료 1회","budget"),
  "항암약제비":cost(150000,600000,"투여 1회","published-case","chemo"),
  "항암약물 투여·주사비":cost(30000,180000,"투여·처치 1회","budget"),
  "방사선·수술 병행 치료비":cost(500000,5000000,"치료 1회","budget"),
  "이상반응 치료·응급 입원":cost(100000,1200000,"응급 진료 1회","budget"),
  "치료 반응 영상·재진료":cost(30000,1200000,"평가 1회","budget")
 },
 foreignbody:{
  "내시경 이물 제거비":cost(300000,1300000,"시술 1회","budget"),
  "장절개·위절개 수술비":cost(500000,2500000,"수술 1회","published-case","surgery"),
  "마취·수액·입원비":cost(150000,900000,"진료·입원 과정 1회","budget")
 },
 fracture:{"골절 정복·금속 고정 수술비":cost(800000,4500000,"수술 1회","budget")},
 disc:{"디스크 감압 수술비":cost(2000000,5000000,"수술 1회","published-case","surgery")},
 cataract:{
  "백내장 수술비":cost(2000000,5000000,"한쪽 눈 1회","budget"),
  "녹내장 수술·레이저비":cost(500000,3500000,"한쪽 눈 1회","budget")
 },
 heart:{
  "심초음파 검사비":cost(70000,300000,"검사 1회","budget"),
  "심장 약물치료비":cost(20000,200000,"30일 처방","budget"),
  "반복 심초음파·약물 조정":cost(70000,350000,"재검 1회","budget")
 },
 rehab:{
  "물리치료·운동 재활비":cost(30000,150000,"회","budget"),
  "수중 러닝머신·수치료비":cost(40000,150000,"회","budget"),
  "레이저·전기자극 치료비":cost(20000,100000,"회","budget")
 },
 periodontal: {
  "치석 제거·치주 치료비":cost(200000,800000,"마취 포함 치료 1회","published-case","surgery"),
  "발치·치근 수술비":cost(100000,1500000,"수술 1회","budget")
 },
 dental:{
  "치주염 치료·스케일링":cost(200000,800000,"마취 포함 치료 1회","published-case","surgery"),
  "발치·구강 수술비":cost(100000,1500000,"수술 1회","budget")
 },
 feline_dental:{
  "스케일링·치주치료비":cost(200000,800000,"마취 포함 치료 1회","published-case","surgery"),
  "다발성 발치·구내염 수술비":cost(300000,2000000,"수술 1회","budget")
 },
 bladder:{"방광 결석 수술비":cost(500000,2000000,"수술 1회","published-case","surgery")},
 feline_block:{
  "진정·마취·도뇨비":cost(150000,800000,"응급 처치 1회","budget"),
  "회음부 요도루조성술비":cost(1000000,3500000,"수술 1회","budget")
 },
 fip:{
  "항바이러스 치료비":cost(1000000,15000000,"전체 치료 과정","published-case","fip"),
  "혈액·영상·체액검사":cost(150000,900000,"초기 진단 과정","budget")
 },
 respiratory:{"산소치료·응급 입원":cost(100000,800000,"응급 진료 1회","budget")},
 hospital:{"산소·집중치료·모니터링":cost(120000,500000,"1일","budget")},
 surgery:{
  "일반 외과 수술비":cost(300000,2500000,"수술 1회","published-case","surgery"),
  "정형·신경·종양 수술비":cost(800000,5000000,"수술 1회","budget"),
  "전신마취·모니터링비":cost(50000,300000,"수술 1회","published-case","surgery")
 },
 endoscopy:{
  "상·하부 위장관 내시경비":cost(250000,1300000,"검사 1회","budget"),
  "내시경 이물 제거비":cost(300000,1300000,"시술 1회","budget"),
  "내시경 실패 시 개복수술비":cost(500000,2500000,"수술 1회","budget")
 },
 neuter:{
  "수컷 중성화 수술비":cost(200000,350000,"수술 1회","published-case","surgery"),
  "암컷 중성화 수술비":cost(250000,450000,"수술 1회","published-case","surgery")
 },
 funeral:{
  "동물장묘업체 장례비":cost(200000,350000,"5kg 미만 기본 화장 1회","published-case","funeral")
 },
 boarding:{"등록 업체의 위탁 기본비":cost(30000,150000,"1일","budget")},
 dog_bite_training:{"반려견 행동교정훈련비":cost(50000,200000,"회","budget")}
};
// Feline-only elective neutering is not the same price as dog surgery.
const felineNeuter={
 "수컷 중성화 수술비":cost(100000,250000,"수술 1회","published-case","surgery"),
 "암컷 중성화 수술비":cost(150000,350000,"수술 1회","published-case","surgery")
};
function specific(topic,title,species){
 if(topic==="neuter"&&species==="cat"&&felineNeuter[title])return felineNeuter[title];
 return R[topic]?.[title]||null;
}
// Scope of non-price benefit admin entries: not a veterinary expense.
const noCostTopics=new Set(["liability","dog_bite_fine","dog_large","claim_docs"]);
function benefitAdministrative(topic,title,stage){
 if(noCostTopics.has(topic))return true;
 if(topic==="funeral"&&title!=="동물장묘업체 장례비")return true;
 if(topic==="boarding"&&title!=="등록 업체의 위탁 기본비")return true;
 if(topic==="dog_bite_training"&&title!=="반려견 행동교정훈련비")return true;
 return false;
}
function inferred(stage,title,topic){
 const v=title;
 // Ordering is deliberate: diagnoses and specialty surgery before generic checks.
 if(/백내장/.test(v)&&/수술/.test(v))return cost(2000000,5000000,"한쪽 눈 1회");
 if(/외이도|중이 수술/.test(v)&&/수술/.test(v))return cost(800000,3000000,"수술 1회");
 if(/각막.*수술|기도 교정|안과 수술/.test(v)&&/수술/.test(v))return cost(300000,2500000,"수술 1회");
 if(/골절 고정·응급수술|이물 제거·복부수술|외과적 처치/.test(v))return cost(300000,4000000,"처치/수술 1회");
 if(/수술/.test(v)||/수술/.test(stage))return cost(300000,4000000,"수술 1회");
 if(/MRI|뇌 MRI|척추 MRI/.test(v))return cost(500000,2000000,"영상검사 1회");
 if(/CT/.test(v))return cost(300000,1200000,"영상검사 1회");
 if(/심초음파/.test(v))return cost(70000,300000,"검사 1회");
 if(/X-ray|방사선 촬영|엑스레이/.test(v))return cost(30000,150000,"검사 1회");
 if(/초음파/.test(v))return cost(50000,300000,"검사 1회");
 if(/내시경/.test(v))return cost(200000,1500000,"검사/시술 1회");
 if(/조직검사|생검|병리|세포검사/.test(v))return cost(50000,350000,"검사 1회");
 if(/PCR|바이러스|항원|특이검사|호르몬/.test(v)&&/검사/.test(v))return cost(40000,300000,"검사 1회");
 if(/혈액|전해질|요침사|소변|분변|배양|화학|빈혈|혈구|표지자|혈당|심전도/.test(v)&&/검사|평가|촬영/.test(v))return cost(20000,250000,"검사 1회");
 if(/안압|형광염색|눈물|세극등|이경|진균|도말|스크래핑|정형외과.*검사/.test(v))return cost(20000,180000,"검사 1회");
 if(/검사|진단|평가/.test(v))return cost(20000,350000,"검사·평가 1회");
 if(/화장|장례/.test(v))return cost(200000,500000,"기본 서비스 1회");
 if(/재활|수중|물리치료|레이저|전기자극/.test(v))return cost(30000,150000,"치료 1회");
 if(/응급 입원|집중치료|중증|산소/.test(v))return cost(120000,600000,"진료/입원 1일");
 if(/입원/.test(v))return cost(60000,300000,"입원 1일");
 if(/마취/.test(v))return cost(50000,300000,"마취 1회");
 if(/도뇨|카테터|세척|봉합|부목|수술 후/.test(v))return cost(50000,700000,"처치 1회");
 if(/항암|표적치료|면역치료/.test(v))return cost(150000,1000000,"투여/치료 1회");
 if(/약물|항생|진통|점안|귀약|처방약|인슐린|항경련|수액|주사|영양/.test(v))return cost(20000,300000,"처치/처방 1회");
 if(/스케일링|치석|치주/.test(v))return cost(150000,800000,"치료 1회");
 if(/재진|추적|관찰|경과|관리|운동|식이|교정|체중/.test(v))return cost(10000,150000,"재진/관리 1회");
 if(/진찰|상담|검진|확인/.test(v))return cost(10000,100000,"진료 1회");
 if(/미용|목욕|발톱|귀 청소/.test(v))return cost(10000,120000,"서비스 1회");
 if(stage==="예방")return cost(10000,100000,"회");
 // Explicit coarse budget assumption; not a source-backed market quote.
 return cost(20000,350000,"진료 1회");
}
function estimate(topic,row,species){
 if(!Array.isArray(row)||row.length<3)return Object.freeze({kind:"unknown"});
 const stage=row[0],title=row[1],group=window.PJM023?.cares?.find(x=>x.id===topic)?.group;
 if(group==="기타 보장"&&benefitAdministrative(topic,title,stage)){
  return Object.freeze({kind:"not-applicable",label:"보장·서류 확인 항목 (진료비 없음)"});
 }
 return specific(topic,title,species)||inferred(stage,title,topic);
}
window.PJM032=Object.freeze({estimate,anchors,model:"한국 반려동물 진료·서비스 예산 참고 구간. 특정 동물병원 견적·통계적 평균·보험 지급액 아님.",asOf:"2026-11-11"});
})();