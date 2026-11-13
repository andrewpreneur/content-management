const {chromium}=require('playwright');(async()=>{const [fmt,out,a,b]=process.argv.slice(2);const W=fmt=='v'?1080:1920,H=fmt=='v'?1920:1080;
const br=await chromium.launch();const p=await br.newPage({viewport:{width:W,height:H}});
await p.goto('file://'+__dirname+'/index.html?fmt='+fmt);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
require('fs').mkdirSync(out,{recursive:true});
for(let i=+a;i<+b;i++){await p.evaluate(t=>window.render(t),i/30);await p.screenshot({path:`${out}/${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:93});}
await br.close();})();
