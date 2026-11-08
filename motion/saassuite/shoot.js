const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file:///home/user/work/ss15/index.html');await p.evaluate(()=>document.fonts.ready);
const FPS=30,N=15*FPS;const fs=require('fs');fs.mkdirSync('/home/user/work/ss15/fr',{recursive:true});
const only=process.argv[2]?process.argv[2].split(',').map(Number):null;
for(let i=0;i<N;i++){const t=i/FPS;if(only&&!only.includes(i))continue;await p.evaluate(t=>render(t),t);await p.screenshot({path:`/home/user/work/ss15/fr/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close();})();
