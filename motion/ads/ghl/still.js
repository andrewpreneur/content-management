const {chromium}=require('playwright');(async()=>{const [c,fmt,out,...ts]=process.argv.slice(2);const W=fmt=='v'?1080:1920,H=fmt=='v'?1920:1080;
const b=await chromium.launch();const p=await b.newPage({viewport:{width:W,height:H}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+__dirname+'/index.html?c='+c+'&fmt='+fmt);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
for(const t of ts){await p.evaluate(t=>window.render(+t),t);await p.screenshot({path:`${out}/${c}-${fmt}-${t}.png`});}
console.log(c,errs);await b.close();})();
