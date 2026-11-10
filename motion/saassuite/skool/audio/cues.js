const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();const o={};
for(const v of ['sales','onb']){await p.goto('file:///home/user/content-management/motion/saassuite/skool/index.html?v='+v);o[v]=await p.evaluate(()=>({...window.CUES,dur:window.DUR}));}
require('fs').writeFileSync('/home/user/work/skool/cues.json',JSON.stringify(o));console.log(o.sales.scenes.length,o.onb.scenes.length,o.sales.click,o.onb.click,o.sales.dur,o.onb.dur);await b.close();})();
