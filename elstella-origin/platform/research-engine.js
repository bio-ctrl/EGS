/* ORIGIN ATLAS research engine — deterministic, provenance-first utilities.
 * This module does not generate scientific conclusions or replace expert review.
 * Browser global: window.ElstellaResearch; CommonJS export for tests.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports) module.exports=api;
  if(root) root.ElstellaResearch=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const API="https://www.ebi.ac.uk/europepmc/webservices/rest/search";
  const clean=v=>String(v??"").replace(/\s+/g," ").trim();
  function articleToRecord(a){
    const pmid=a.pmid? "PMID: "+a.pmid : "";
    const doi=clean(a.doi);
    const url=doi?"https://doi.org/"+doi:(a.pmid?"https://pubmed.ncbi.nlm.nih.gov/"+a.pmid+"/":"");
    return {
      id:"EPMC-"+(a.id||a.pmid||doi||Date.now()),
      program:"CARDIA", title:clean(a.title)||"Untitled source",
      url, identifier:doi||pmid, context:"Not extracted — review source",
      evidenceClass:(a.pubTypeList&&a.pubTypeList.pubType||[]).join("; ")||"Not classified",
      model:"Not extracted", cell:"Not extracted", claim:"",
      location:"Abstract metadata imported; full source review required",
      status:"Unreviewed", limitations:"Automatically imported metadata. Verify publication identity, study design, methods, findings and limitations against the source.",
      abstractText:clean(a.abstractText), publicationYear:a.firstPublicationDate||String(a.pubYear||""),
      authors:(a.authorString||"").trim(), journalTitle:clean(a.journalTitle),
      sourceDatabase:"Europe PMC", importedAt:new Date().toISOString()
    };
  }
  function extractCandidates(abstractText){
    const text=clean(abstractText);
    if(!text)return [];
    const sentences=text.split(/(?<=[.!?])\s+(?=[A-Z0-9])/);
    const patterns=[
      {kind:"Objective / rationale",re:/\b(aim\w*|objective\w*|investigat\w*|evaluat\w*|assess\w*|sought to|we hypothesi\w*)\b/i},
      {kind:"Methods / model",re:/\b(method\w*|cohort|patient\w*|mouse|mice|rat\w*|animal model|in vitro|single.cell|sequenc\w*|transcriptom\w*|proteom\w*|randomi[sz]\w*)\b/i},
      {kind:"Reported result",re:/\b(found|observ\w*|demonstrat\w*|showed|reveal\w*|associated with|increased|decreased|reduced|improved|identified|resulted in)\b/i},
      {kind:"Limitation / uncertainty",re:/\b(limit\w*|however|although|caution|small sample|not powered|further studies|remain unclear|did not)\b/i}
    ];
    const out=[];
    for(const sentence of sentences){
      const s=clean(sentence); if(s.length<20)continue;
      const match=patterns.find(p=>p.re.test(s));
      if(match && !out.some(x=>x.text===s))out.push({kind:match.kind,text:s,sourceLocation:"Abstract — exact sentence; confirm against publisher/PubMed record",reviewStatus:"Candidate only"});
      if(out.length>=12)break;
    }
    return out;
  }
  async function searchEuropePmc(query,{pageSize=15,fetchImpl=fetch}={}){
    const q=clean(query); if(!q)throw new Error("Enter a literature search query.");
    const url=API+"?query="+encodeURIComponent(q)+"&format=json&pageSize="+Math.min(50,Math.max(1,pageSize))+"&resultType=core";
    const response=await fetchImpl(url,{headers:{Accept:"application/json"}});
    if(!response.ok)throw new Error("Europe PMC returned HTTP "+response.status);
    const data=await response.json();
    return (data.resultList&&data.resultList.result||[]).map(articleToRecord);
  }
  function summarize(records){
    const rows=Array.isArray(records)?records:[];
    const byProgram={}, byClass={}, unreviewed=rows.filter(r=>!/^verified by second reviewer$/i.test(r.status||"")).length;
    rows.forEach(r=>{byProgram[r.program||"Unassigned"]=(byProgram[r.program||"Unassigned"]||0)+1;byClass[r.evidenceClass||"Not classified"]=(byClass[r.evidenceClass||"Not classified"]||0)+1;});
    return {total:rows.length,unreviewed,byProgram,byClass,claimCount:rows.filter(r=>clean(r.claim)).length,
      warning:"Counts describe entered records only. They are not evidence quality, certainty, efficacy or scientific consensus."};
  }
  return {articleToRecord,extractCandidates,searchEuropePmc,summarize};
});
