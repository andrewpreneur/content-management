const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();const o={};
for(const c of ['ag1','ag2','sp1','sp2']){await p.goto('file://'+__dirname+'/index.html?c='+c+'&fmt=h');o[c]=await p.evaluate(()=>({dur:window.DUR,cues:window.CUES,music:window.MUSIC}));}
require('fs').writeFileSync('/home/user/work/ads/cues.json',JSON.stringify(o));console.log(Object.fromEntries(Object.entries(o).map(([k,v])=>[k,[v.dur,v.cues.length]])));await b.close();})();
