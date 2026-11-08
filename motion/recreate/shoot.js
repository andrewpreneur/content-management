// Render an HTML file that defines window.render(t) (pure function of time, seconds) to frames.
// node motion/recreate/shoot.js page.html OUT_DIR DURATION_S FPS WIDTH HEIGHT [frame,frame,...]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const [html,out,dur,fps,w,h,only]=process.argv.slice(2);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:+w,height:+h}});
await p.goto('file://'+path.resolve(html));await p.evaluate(()=>document.fonts.ready);
fs.mkdirSync(out,{recursive:true});const N=Math.round(+dur*+fps);const pick=only?only.split(',').map(Number):null;
for(let i=0;i<N;i++){if(pick&&!pick.includes(i))continue;await p.evaluate(t=>window.render(t),i/+fps);
 await p.screenshot({path:`${out}/${String(i).padStart(4,'0')}.png`});}
await b.close();})();
