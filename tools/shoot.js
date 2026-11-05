// Screenshot local HTML files: node tools/shoot.js W H in1.html:out1.png in2.html:out2.png ...   (NODE_PATH=/opt/node-tools/node_modules)
const {chromium}=require('playwright');(async()=>{const [w,h,...pairs]=process.argv.slice(2);const b=await chromium.launch();
const p=await b.newPage({viewport:{width:+w,height:+h}});
for(const pr of pairs){const [i,o]=pr.split(':');await p.goto('file://'+i);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(120);await p.screenshot({path:o});}
await b.close();})().catch(e=>{console.error(e);process.exit(1);});
