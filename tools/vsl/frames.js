// Stream frames of a seekable HTML page as PNG to stdout.
// node tools/vsl/frames.js page.html W H FPS DUR ALPHA(0|1) [FROM_FRAME TO_FRAME]
// The page must define window.seek(t) (sync) and window.READY (promise, optional).
const {chromium}=require('playwright');const path=require('path');
(async()=>{
 const [html,W,H,FPS,DUR,ALPHA,F0,F1]=process.argv.slice(2);
 const b=await chromium.launch({args:['--disable-gpu','--force-color-profile=srgb']});
 const p=await b.newPage({viewport:{width:+W,height:+H},deviceScaleFactor:1});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text());});
 await p.goto('file://'+path.resolve(html));await p.evaluate(()=>document.fonts.ready);
 await p.evaluate(()=>window.READY||null);
 const cdp=await p.context().newCDPSession(p);
 if(+ALPHA) await cdp.send('Emulation.setDefaultBackgroundColorOverride',{color:{r:0,g:0,b:0,a:0}});
 const N=Math.round(+DUR*+FPS); const a=F0?+F0:0, z=F1?Math.min(N,+F1):N;
 for(let f=a;f<z;f++){
  await p.evaluate(t=>window.seek(t),f/(+FPS));
  const r=await cdp.send('Page.captureScreenshot',{format:'png',optimizeForSpeed:true,captureBeyondViewport:false});
  const buf=Buffer.from(r.data,'base64');
  if(!process.stdout.write(buf)) await new Promise(res=>process.stdout.once('drain',res));
 }
 await b.close();
 if(errs.length){console.error('PAGE ERRORS:\n'+errs.join('\n'));process.exit(2);}
})().catch(e=>{console.error(e);process.exit(1);});
