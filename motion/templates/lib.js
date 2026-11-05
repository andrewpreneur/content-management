// Generic podcast-clip template library. Every template gets CLIP (built by tools/formats.py):
// {id, T, FR, NF, IW, IH, W:[[word,start,flag]], people:[{id,x,y,face}], segs:[[t0,t1,pid]], Th (hook end), title:[l1,l2],
//  hook_q, hook_plain, brand, shots:{fmt:[[t,cx,cy,sw],...]}, beats:[...], cutFrames:[...]}
const $=id=>document.getElementById(id); const stage=$('stage');
const {FR,NF,T,IW,IH,W}=CLIP; const LAST=W.length?W[W.length-1][1]+0.6:T;
const clean=s=>s.replace(/[.,?!]/g,'');
const views=[];
function View(z,parent,cut){
  const d=document.createElement('div'); d.style.cssText=`position:absolute;overflow:hidden;z-index:${z}`;
  const im=document.createElement('img'); im.style.cssText=`position:absolute;left:0;top:0;transform-origin:0 0;width:${IW}px;height:${IH}px`;
  d.appendChild(im); (parent||stage).appendChild(d);
  const v={d,im,cut,set(r,win,filter){
    const [X,Y,w,h]=r; let [cx,cy,sw]=win; let sh=sw*h/w; if(sh>IH){sh=IH;sw=sh*w/h;} if(sw>IW){sw=IW;sh=sw*h/w;}
    cx=M.clamp(cx,sw/2,IW-sw/2); cy=M.clamp(cy,sh/2,IH-sh/2); const sc=w/sw;
    Object.assign(d.style,{left:X.toFixed(2)+'px',top:Y.toFixed(2)+'px',width:w.toFixed(2)+'px',height:h.toFixed(2)+'px'});
    im.style.transform=`translate(${(-(cx-sw/2)*sc).toFixed(2)}px,${(-(cy-sh/2)*sc).toFixed(2)}px) scale(${sc.toFixed(5)})`;
    if(filter!==undefined) im.style.filter=filter;
  }}; views.push(v); return v;
}
// hard-cut shot list with a slow push-in inside each shot
function shots(list,push=0.014){ return t=>{let k=list[0]; for(const s of list) if(t>=s[0]) k=s; const z=1-push*Math.min(5,t-k[0]); return [k[1],k[2],k[3]*z,k[0]];}; }
// spring camera through keys [[t,cx,cy,sw],...]
function springs(list,sp=M.CAM){ const tr=i=>M.track(list[0][i],list.slice(1).map(k=>[k[0],k[i],sp])); const a=tr(1),b=tr(2),c=tr(3); return t=>[a(t),b(t),c(t)]; }
function phrases(n=3,maxGap=0.6){
  const out=[]; let cur=[]; const sw=CLIP.segs.map(s=>s[0]).slice(1);
  W.forEach((w,i)=>{cur.push(w); const nx=W[i+1];
    const brk=/[.,?!]$/.test(w[0])||cur.length>=n||!nx||(nx[1]-w[1]>maxGap)||sw.some(t=>w[1]<t&&nx&&nx[1]>=t);
    if(brk){out.push({w:cur,s:cur[0][1],e:nx?nx[1]:LAST}); cur=[];}});
  return out;
}
const at=(list,t)=>{let c=null; for(const x of list) if(t>=x.s) c=x; return c;};
const wordAt=t=>{let c=null; for(const w of W) if(t>=w[1]) c=w; return c;};
const segAt=t=>{let c=CLIP.segs[0]; for(const s of CLIP.segs) if(t>=s[0]) c=s; return c;};
const second=t=>segAt(t)!==CLIP.segs[0]&&segAt(t)[2]!==CLIP.segs[0][2]; // a different voice than the opener
function el(tag,css,html,parent){const d=document.createElement(tag); d.style.cssText=css; if(html!=null) d.innerHTML=html; (parent||stage).appendChild(d); return d;}
const FONTS=`@font-face{font-family:'Inter Tight';src:url('../../tools/fonts/InterTight-ExtraBold.ttf');font-weight:800}
@font-face{font-family:'Playfair';src:url('../../tools/fonts/PlayfairDisplay-BoldItalic.ttf');font-style:italic;font-weight:700}`;
{const st=document.createElement('style'); st.textContent=FONTS; document.head.appendChild(st);}
function scene(extra,bg='#000'){
  const seek0=M.scene({W:1080,H:1920,T:T,bg,intro:null,SH:{n:{w:1,h:1,r:0,bg,cam:1}},start:'n',SEQ:[],layers:[],extra});
  const CF=CLIP.cutFrames||[];
  window.seek=async t=>{ seek0(t); const n=Math.min(NF-1,Math.max(0,Math.floor(t*FR+1e-6))); const id=String(n).padStart(4,'0'); const waits=[];
    let cn=null; if(CF.length){ for(const f of CF){ if(f<=n) cn=f; else break; } }
    for(const v of views){ let src;
      if(v.cut){ if(cn===null){v.d.style.visibility='hidden'; continue;} v.d.style.visibility=''; src=`../frames/${CLIP.id}/c${String(cn).padStart(4,'0')}.webp`; }
      else src=`../frames/${CLIP.id}/f${id}.jpg`;
      if(v.im._s!==src){v.im._s=src; v.im.src=src; waits.push(v.im.decode().catch(()=>{}));} }
    await Promise.all(waits); };
}
