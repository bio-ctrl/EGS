const test=require("node:test");
const assert=require("node:assert/strict");
const contract=require("../platform/ai-contract.js");
test("AI request requires a question",()=>assert.throws(()=>contract.validateRequest({question:" "}),/required/));
test("AI request limits evidence count",()=>assert.throws(()=>contract.validateRequest({question:"Compare",records:Array.from({length:31},(_,i)=>({id:String(i)}))}),/30/));
test("AI prompt requires source IDs and uncertainty",()=>{
 const m=contract.buildMessages({question:"What differs?",records:[{id:"C-1",title:"Example",claim:""}]});
 assert.match(m[0].content,/Never invent papers/);assert.match(m[0].content,/contradictory/);assert.match(m[1].content,/C-1/);
});
