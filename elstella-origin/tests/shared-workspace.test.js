const test=require("node:test");
const assert=require("node:assert/strict");
const {createClient,TABLE}=require("../platform/shared-workspace.js");
test("shared workspace client rejects invalid configuration",()=>{
 assert.throws(()=>createClient({url:"http://not-supabase.local",anonKey:"",fetchImpl:async()=>({ok:true,text:async()=>"[]"})}),/valid Supabase/);
});
test("table name is stable",()=>assert.equal(TABLE,"origin_workspaces"));
