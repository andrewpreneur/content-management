// node shoot-range.js v fmt OUT startFrame endFrame  (30 fps)
const {chromium}=require('playwright');(async()=>{const [v,fmt,out,a,b]=process.argv.slice(2);const W=fmt=='v'?1080:1920,H=fmt=='v'?1920:1080;
const br=await chromium.launch();const p=await br.newPage({viewport:{width:W,height:H}});
await p.goto('file://'+__dirname+'/index.html?v='+v+'&fmt='+fmt);await p.evaluate(()=>document.fonts.ready);
require('fs').mkdirSync(out,{recursive:true});
for(let i=+a;i<+b;i++){if(require('fs').existsSync(`${out}/${String(i).padStart(5,'0')}.jpg`))continue;await p.evaluate(t=>window.render(t),i/30);await p.screenshot({path:`${out}/${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:95});}
await br.close();})();
