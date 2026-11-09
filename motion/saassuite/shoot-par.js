// Parallel transparent-overlay shooter: node shoot-par.js page.html outDir DUR W H query [workers=4] [onlyFrames]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const [page,out,dur,W,H,q='',nw='4',only]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const N=Math.round(+dur*30);const pick=only?only.split(',').map(Number):[...Array(N).keys()];const b=await chromium.launch();
const work=async k=>{const p=await b.newPage({viewport:{width:+W,height:+H}});await p.goto('file://'+path.resolve(page)+'?'+q);await p.evaluate(()=>document.fonts.ready);
 for(let j=k;j<pick.length;j+=+nw){const i=pick[j];await p.evaluate(t=>render(t),i/30);await p.screenshot({path:`${out}/${String(i).padStart(4,'0')}.png`,omitBackground:true});}};
await Promise.all([...Array(+nw).keys()].map(work));await b.close();})();
