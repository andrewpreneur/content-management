const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [v,dur,only]=process.argv.slice(2);const W=v==='169'?1920:1080,H=v==='169'?1080:1920;
const b=await chromium.launch();const p=await b.newPage({viewport:{width:W,height:H}});
await p.goto('file:///home/user/work/vsl1/overlay.html?v='+v);await p.evaluate(()=>document.fonts.ready);
const out='/home/user/work/vsl1/ov'+v;fs.mkdirSync(out,{recursive:true});const N=Math.round(+dur*30);const pick=only?only.split(',').map(Number):null;
for(let i=0;i<N;i++){if(pick&&!pick.includes(i))continue;await p.evaluate(t=>render(t),i/30);await p.screenshot({path:`${out}/${String(i).padStart(4,'0')}.png`,omitBackground:true});}
await b.close();})();
