// Shared helpers for the Pod3 clip variants (included with //@include by tools/motion_build.py).
// Footage: motion/podA/fr/f0000-f0719.jpg = 4K frames of the cut (162.88-184.45 + 195.92-198.35 in pod3.mp4).
const $=id=>document.getElementById(id); const stage=$('stage');
const FR=30, NF=720, T=24.0, IW=3840, IH=2160;
// words in output time: [text, start, flag]  flag 1 = key word, 2 = negative (fail/bad)
const W=[['I’ve',0.04],['grown',0.34],['more',0.48],['in',0.76],['these',0.84],['last',1.02],['two',1.24,1],['months',1.78,1],['I',1.94],['was',2.1],['in',2.18],['the',2.32],['internship',2.44],['than',2.74],['I',3.0],['have',3.1],['in',3.28],['four',3.46,1],['years',3.68,1],['in',3.88],['college.',4.02],
 ['This',4.46],['is',4.48],['insane.',4.64,1],['I’ve',5.14],['learned',5.26],['more',5.38],['about',5.72],['how',6.04],['real',6.22],['life',6.46],['works',6.72],['and',7.0],['about',7.18],['failure,',7.40,1],['and',8.0],['you',8.18],
 ['get',8.46],['taught',8.64],['during',8.9],['school,',9.16],['failure',9.98],['is',10.26],['bad.',10.50,2],['If',10.88],['you',10.9],['get',10.96],['that',11.06],['F,',11.20,2],['it’s',11.46],['bad.',11.58,2],['You',11.96],['want',12.0],['to',12.12],['aim',12.22],['for',12.32],['the',12.48],['A.',12.58,1],
 ['But',13.14,1],['what',13.28],['you',13.36],['learn',13.48],['and',13.68],['what',13.94],['I',14.08],['learned',14.22],['from',14.40],['the',14.54],['internship',14.62],['is',14.84],['you',15.06],['fail,',15.54,2],['you',15.96],['keep',15.98],['going.',16.14,1],['You',16.50],
 ['fail,',16.54,2],['you',16.84],['get',16.94],['back',17.24,1],['up.',17.44,1],['Failure',18.06],['is',18.24],['good.',18.50,1],['Failure',18.92],['is',18.94],['a',19.42],['chance',19.70],['to',19.90],['learn,',20.12,1],['and',20.52],['that',20.78],['is',21.06],['life.',21.22,1],
 ['So',21.61],['it',21.69],['looks',21.73],['like',21.81],['you',21.93],['want',22.03],['to',22.13],['fail',22.25,2],['more',22.41],['and',22.67],['fail',22.91,2],['faster.',23.09,1]];
const LAST=23.5, SWITCH=21.57; // second speaker (the blonde intern) from 21.57
// speaker face centres in the 4K frame
const SPK={andrew:[860,700], ohaji:[1700,690], blonde:[2560,760], green:[3330,780]};
const clean=s=>s.replace(/[.,?]/g,'');

// a camera view: a box on stage showing a window of the 4K frame. win = [cx, cy, sourceWidth]
const views=[];
function View(z,parent,mask){
  const d=document.createElement('div'); d.style.cssText=`position:absolute;overflow:hidden;z-index:${z}`;
  const im=document.createElement('img'); im.style.cssText=`position:absolute;left:0;top:0;transform-origin:0 0;width:${IW}px;height:${IH}px`;
  d.appendChild(im); (parent||stage).appendChild(d);
  const v={d,im,mask,set(r,win,filter){
    const [X,Y,w,h]=r; let [cx,cy,sw]=win; let sh=sw*h/w; if(sh>IH){sh=IH;sw=sh*w/h;} if(sw>IW){sw=IW;sh=sw*h/w;}
    cx=M.clamp(cx,sw/2,IW-sw/2); cy=M.clamp(cy,sh/2,IH-sh/2); const sc=w/sw;
    Object.assign(d.style,{left:X.toFixed(2)+'px',top:Y.toFixed(2)+'px',width:w.toFixed(2)+'px',height:h.toFixed(2)+'px'});
    im.style.transform=`translate(${(-(cx-sw/2)*sc).toFixed(2)}px,${(-(cy-sh/2)*sc).toFixed(2)}px) scale(${sc.toFixed(5)})`;
    if(filter!==undefined) im.style.filter=filter;
  }}; views.push(v); return v;
}
// hard-cut shot list: [[t, cx, cy, sw], ...] with a slow push-in inside every shot
function shots(list,push=0.016){
  return t=>{let k=list[0]; for(const s of list) if(t>=s[0]) k=s; const z=1-push*Math.min(5,t-k[0]); return [k[1],k[2],k[3]*z,k[0]];};
}
// phrases of up to n words, breaking on punctuation (for 2-3 word captions)
function phrases(n=3,maxGap=0.6){
  const out=[]; let cur=[];
  W.forEach((w,i)=>{cur.push(w); const nx=W[i+1]; const brk=/[.,?!]$/.test(w[0])||cur.length>=n||!nx||(nx[1]-w[1]>maxGap)||(w[1]<SWITCH&&nx&&nx[1]>=SWITCH);
    if(brk){out.push({w:cur,s:cur[0][1],e:nx?nx[1]:LAST}); cur=[];}});
  return out;
}
const at=(list,t)=>{let c=null; for(const x of list) if(t>=x.s) c=x; return c;};
const wordAt=t=>{let c=null; for(const w of W) if(t>=w[1]) c=w; return c;};
function el(tag,css,html,parent){const d=document.createElement(tag); d.style.cssText=css; if(html!=null) d.innerHTML=html; (parent||stage).appendChild(d); return d;}
// install seek: scene + frame loading for every view
function install(seek0){
  window.seek=async t=>{ seek0(t); const n=Math.min(NF-1,Math.max(0,Math.floor(t*FR+1e-6))); const id=String(n).padStart(4,'0');
    const waits=[];
    for(const v of views){ const src=v.mask?'../podA/cut/c'+id+'.webp':'../podA/fr/f'+id+'.jpg';  // cut = people only, transparent elsewhere
      if(v.im._s!==src){v.im._s=src; v.im.src=src; waits.push(v.im.decode().catch(()=>{}));} }
    await Promise.all(waits); };
}
