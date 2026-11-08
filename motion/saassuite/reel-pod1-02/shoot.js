const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file:///home/user/work/ss_reel/overlay.html');await p.evaluate(()=>document.fonts.ready);
fs.mkdirSync('/home/user/work/ss_reel/ov',{recursive:true});const N=Math.round(14.6*30);const only=process.argv[2]?process.argv[2].split(',').map(Number):null;
for(let i=0;i<N;i++){if(only&&!only.includes(i))continue;await p.evaluate(t=>render(t),i/30);await p.screenshot({path:`/home/user/work/ss_reel/ov/${String(i).padStart(4,'0')}.png`,omitBackground:true});}
await b.close();})();
