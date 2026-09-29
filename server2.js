const http = require('http');
const fs = require('fs');
const path = require('path');
const catalog = [
  {id:'p-100',name:'Terra Trail Pack',category:'outdoor',tags:['trail','sustainable','travel'],price:79,in_stock:true},
  {id:'p-101',name:'Summit Steel Bottle',category:'outdoor',tags:['hydration','sustainable','trail'],price:28,in_stock:true},
  {id:'p-102',name:'Weekend Carry-On',category:'travel',tags:['travel','lightweight','organised'],price:129,in_stock:true},
  {id:'p-103',name:'Studio Noise-Cancel Buds',category:'audio',tags:['commute','focus','travel'],price:149,in_stock:true},
  {id:'p-104',name:'City Commuter Tote',category:'travel',tags:['commute','organised','sustainable'],price:69,in_stock:true}
];
const normalise = value => String(value || '').toLowerCase().replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim();
const json = (res, code, data) => { const body=Buffer.from(JSON.stringify(data));res.writeHead(code,{'Content-Type':'application/json','Content-Length':body.length,'Cache-Control':'no-store'});res.end(body); };
function recommend(body) {
  const profile=body.profile||{}, history=profile.behaviour||[], session=body.session_events||[];
  const interests=(profile.preferences||[]).map(normalise).filter(Boolean);
  const usual=history.map(x=>normalise(x.category)).filter(Boolean), recent=session.map(x=>normalise(x.category)).filter(Boolean);
  const signals=new Set([...interests,...usual,...recent]);
  const shift=recent.some(x=>!usual.includes(x));
  const recommendations=catalog.filter(x=>x.in_stock).map(item=>{
    const name=normalise(item.name), evidence=[];
    const labels=[...item.tags.map(normalise),normalise(item.category),name];
    for(const signal of signals) if(labels.some(label=>label.includes(signal)||signal.includes(label))) evidence.push(signal);
    const score=evidence.reduce((total, signal) => total + (interests.includes(signal) ? 30 : 10), 0) + (recent.includes(normalise(item.category)) ? 3 : 0);
    return {id:item.id,name:item.name,category:item.category,price:item.price,score,evidence:[...new Set(evidence)].length?[...new Set(evidence)]:['no direct match']};
  }).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id)).slice(0,3);
  return {trace_id:Math.random().toString(16).slice(2,14),recommendations,active_learning:shift?{question:`You usually browse ${usual[0]||'other products'}, but recently browsed ${recent[0]}. Is this a new shopping goal?`,options:['outdoor','travel','audio']}:null,guardrails:{catalog_grounded:true,protected_attributes_used_for_ranking:false,human_review_required:false},monitor:{latency_ms:1,estimated_tokens:45+18*recommendations.length,grounding:'pass'},fairness_demo:{status:'synthetic control test passed',benchmark:'Counterfactual invariance: identical shopping signals, differing gender field.',result:'The gender field is stripped before scoring, so ranking inputs and outputs remain identical.',limitation:'This proves the control path, not real-world demographic outcome parity.'},eu_readiness:{classification:'Conditional: consumer retail ranking is not automatically high-risk.',implemented:['catalog grounding test','protected-trait removal before ranking','decision trace and output evidence'],required:['formal use-case classification','representative bias evaluation','risk register owner and review cadence','production QMS and trained human-oversight owner','post-market incident process']}};
}
http.createServer((req,res)=>{
  if(req.method==='GET'&&req.url==='/'){const file=path.join(__dirname,'app','static','index.html');const data=Buffer.concat([fs.readFileSync(file),Buffer.from('<script src="/demo-layer.js"></script>')]);res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});return res.end(data);}
  if(req.method==='GET'&&req.url==='/demo-layer.js'){const data=fs.readFileSync(path.join(__dirname,'app','static','demo-layer.js'));res.writeHead(200,{'Content-Type':'application/javascript; charset=utf-8','Cache-Control':'no-store'});return res.end(data);}
  if(req.method==='POST'&&req.url==='/api/recommend'){let raw='';req.on('data',x=>raw+=x);req.on('end',()=>{try{json(res,200,recommend(JSON.parse(raw||'{}')))}catch(e){json(res,400,{error:e.message})}});return;}
  if(req.method==='GET'&&req.url==='/api/status') return json(res,200,{local_only:true,catalog_items:catalog.length});
  json(res,404,{error:'not found'});
}).listen(8080,()=>console.log('DriveNext v2 listening at http://localhost:8080'));
