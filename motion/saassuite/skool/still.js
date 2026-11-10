const {chromium}=require('playwright');(async()=>{const [v,fmt,out,...ts]=process.argv.slice(2);const W=fmt=='v'?1080:1920,H=fmt=='v'?1920:1080;
const b=await chromium.launch();const p=await b.newPage({viewport:{width:W,height:H}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()=='error')errs.push(m.text())});
await p.goto('file://'+__dirname+'/index.html?v='+v+'&fmt='+fmt);await p.evaluate(()=>document.fonts.ready);
if(errs.length){console.log(errs);process.exit(1)}
let list=ts; if(ts[0]=='scenes'){list=await p.evaluate(()=>{return [...document.querySelectorAll('.scene')].length})}
console.log('DUR',await p.evaluate(()=>window.DUR));
for(const t of ts){await p.evaluate(t=>window.render(+t),t);await p.screenshot({path:`${out}/${v}-${fmt}-${t}.png`});}
console.log(errs);await b.close();})();
