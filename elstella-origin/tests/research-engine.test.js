const test=require("node:test");
const assert=require("node:assert/strict");
const engine=require("../platform/research-engine.js");
test("article metadata becomes an explicitly unreviewed record",()=>{
 const r=engine.articleToRecord({id:"123",pmid:"123",doi:"10.1/example",title:"A study",abstractText:"Abstract",authorString:"A Author",pubYear:2025});
 assert.equal(r.title,"A study"); assert.equal(r.identifier,"10.1/example"); assert.equal(r.status,"Unreviewed"); assert.equal(r.claim,"");
 assert.match(r.limitations,/Verify publication identity/);
});
test("abstract extraction returns traceable candidates without calling them verified",()=>{
 const c=engine.extractCandidates("We investigated cardiac fibrosis in a cohort. The study used single-cell sequencing. We found distinct cell populations. However, the sample was small.");
 assert.ok(c.length>=3); assert.ok(c.every(x=>x.reviewStatus==="Candidate only"));
 assert.ok(c.some(x=>x.kind==="Reported result")); assert.ok(c.some(x=>x.kind==="Limitation / uncertainty"));
});
test("empty abstracts return no candidate claims",()=>assert.deepEqual(engine.extractCandidates(""),[]));
test("summary reports counts without inventing evidence quality",()=>{
 const s=engine.summarize([{program:"CARDIA",status:"Unreviewed",claim:""},{program:"CARDIA",status:"Verified by second reviewer",claim:"A paraphrase"}]);
 assert.equal(s.total,2);assert.equal(s.unreviewed,1);assert.equal(s.claimCount,1);assert.match(s.warning,/not evidence quality/);
});
