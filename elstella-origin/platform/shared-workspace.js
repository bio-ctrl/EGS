/* Optional Supabase sync adapter. Requires a Supabase project configured by the owner.
 * Uses the public anon key and authenticated user JWT; row-level security is mandatory.
 * Never place a service_role key in browser code.
 */
(function(root,factory){
 const api=factory();
 if(typeof module==="object"&&module.exports)module.exports=api;
 if(root)root.ElstellaSharedWorkspace=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 "use strict";
 const TABLE="origin_workspaces";
 function normalizeUrl(v){return String(v||"").trim().replace(/\/$/,"");}
 function headers(key,token){return {apikey:key,Authorization:"Bearer "+token,"Content-Type":"application/json"};}
 async function request(url,options,fetchImpl){
   const r=await fetchImpl(url,options); const body=await r.text();
   let data=null;try{data=body?JSON.parse(body):null;}catch(_){}
   if(!r.ok)throw new Error((data&&data.message)||("Database request failed: HTTP "+r.status));
   return data;
 }
 function createClient({url,anonKey,fetchImpl=fetch}){
   const base=normalizeUrl(url), key=String(anonKey||"").trim();
   if(!/^https:\/\/[a-z0-9-]+\.supabase\.co$/i.test(base)||!key)throw new Error("Enter a valid Supabase project URL and public anon key.");
   async function auth(path,payload){
     return request(base+"/auth/v1/"+path,{method:"POST",headers:{apikey:key,"Content-Type":"application/json"},body:JSON.stringify(payload)},fetchImpl);
   }
   async function save(accessToken,workspace){
     return request(base+"/rest/v1/"+TABLE,{method:"POST",headers:{...headers(key,accessToken),Prefer:"resolution=merge-duplicates,return=representation"},body:JSON.stringify({payload:workspace,updated_at:new Date().toISOString()})},fetchImpl);
   }
   async function load(accessToken){
     const rows=await request(base+"/rest/v1/"+TABLE+"?select=payload,updated_at&limit=1",{headers:headers(key,accessToken)},fetchImpl);
     return rows&&rows[0]?rows[0]:null;
   }
   return {
     signUp:(email,password)=>auth("signup",{email,password}),
     signIn:(email,password)=>auth("token?grant_type=password",{email,password}),
     save,load
   };
 }
 return {createClient,TABLE};
});
