/* Local research server. AI credentials stay server-side.
 * Do not expose this development server publicly without authentication, rate limits and TLS.
 */
const http=require("node:http");
const fs=require("node:fs");
const path=require("node:path");
const {buildMessages}=require("./platform/ai-contract.js");
const ROOT=__dirname;
const PORT=Number(process.env.PORT||4173);
const MIME={".html":"text/html; charset=utf-8",".js":"text/javascript; charset=utf-8",".css":"text/css; charset=utf-8",".json":"application/json",".md":"text/markdown; charset=utf-8",".sql":"text/plain; charset=utf-8"};
function send(res,status,body,type="application/json"){res.writeHead(status,{"Content-Type":type,"X-Content-Type-Options":"nosniff","Cache-Control":"no-store"});res.end(typeof body==="string"?body:JSON.stringify(body));}
async function readBody(req,max=65000){let raw="";for await(const chunk of req){raw+=chunk;if(raw.length>max)throw new Error("Request body too large.");}return JSON.parse(raw||"{}");}
async function handleAI(req,res){
 if(!process.env.AI_API_URL||!process.env.AI_API_KEY||!process.env.AI_MODEL)return send(res,503,{error:"AI provider is not configured. Set AI_API_URL, AI_API_KEY and AI_MODEL on the server."});
 let payload;try{payload=await readBody(req);const messages=buildMessages(payload);
 const upstream=await fetch(process.env.AI_API_URL,{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+process.env.AI_API_KEY},body:JSON.stringify({model:process.env.AI_MODEL,messages,temperature:0.2})});
 const data=await upstream.json().catch(()=>({}));
 if(!upstream.ok)return send(res,502,{error:"AI provider request failed.",providerStatus:upstream.status,detail:String(data.error?.message||"No provider detail").slice(0,500)});
 const answer=data.choices?.[0]?.message?.content;
 if(typeof answer!=="string"||!answer.trim())return send(res,502,{error:"AI provider returned no text in the expected compatible response format."});
 return send(res,200,{answer,model:process.env.AI_MODEL,generatedAt:new Date().toISOString(),disclaimer:"AI-generated literature synthesis. Verify every citation and claim against the original publication; this is not scientific validation or medical advice."});
 }catch(e){return send(res,400,{error:e.message||"Invalid request."});}
}
const server=http.createServer(async(req,res)=>{
 const url=new URL(req.url,"http://localhost");
 if(req.method==="POST"&&url.pathname==="/api/research-assist")return handleAI(req,res);
 if(req.method!=="GET"&&req.method!=="HEAD")return send(res,405,{error:"Method not allowed."});
 let pathname=decodeURIComponent(url.pathname==="/" ? "/index.html":url.pathname);
 if(pathname.split("/").some(part=>part===".env"||part===".git"||part==="node_modules"))return send(res,404,{error:"Not found."});
 const file=path.resolve(ROOT,"."+pathname);
 if(!file.startsWith(ROOT+path.sep))return send(res,403,{error:"Forbidden."});
 fs.readFile(file,(err,buf)=>{if(err)return send(res,404,{error:"Not found."});res.writeHead(200,{"Content-Type":MIME[path.extname(file)]||"application/octet-stream","X-Content-Type-Options":"nosniff"});if(req.method==="HEAD")return res.end();res.end(buf);});
});
server.listen(PORT,()=>process.stdout.write("ORIGIN ATLAS running at http://localhost:"+PORT+"\n"));
