// 26-codepilot recreation — shared scene for both segments.
// Global time T (s) = reference time - 13.5. Segment "ask" renders T in [0,5), "say-it" renders T in [5,9.5).
// Pure function of time: window.render(t) -> renderScene(T0 + t). No CSS transitions, no timers.
(function(){
const $=id=>document.getElementById(id);
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const lerp=(a,b,p)=>a+(b-a)*p;
const eoC=x=>1-Math.pow(1-cl(x),3);
const eoQ=x=>1-Math.pow(1-cl(x),4);
const eiQ=x=>Math.pow(cl(x),2);
const eioS=x=>(1-Math.cos(Math.PI*cl(x)))/2;
function bez(x1,y1,x2,y2){return function(x){x=cl(x);let lo=0,hi=1,u=.5;for(let i=0;i<30;i++){u=(lo+hi)/2;const bx=3*(1-u)*(1-u)*u*x1+3*(1-u)*u*u*x2+u*u*u;if(bx<x)lo=u;else hi=u;}u=(lo+hi)/2;return 3*(1-u)*(1-u)*u*y1+3*(1-u)*u*u*y2+u*u*u;};}
const camEase=bez(0.626,0.279,0.251,0.907);   // measured camera move B->A
const F=f=>(f-1)/30;                            // ref frame (1-based, seg B) -> T
const FA=f=>5+(f-1)/30;                         // ref frame (1-based, seg A) -> T
function rng(seed){let s=seed>>>0;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};}

// ---------------- constants measured from the reference ----------------
const BG=[10,8,6];
const WIN_W=1683, WIN_H=1112;
const PERSP=4732;
const CAM0={tx:118,ty:-404,s:1,ry:0,rx:0};
const CAM1={tx:376.2,ty:-16.5,s:0.81,ry:-10.76,rx:3.7};
// planet (ellipse horizon) fitted on ref f45: rmse 2.4/255
const PL={cx:959.1,a:1066.1,b:547.0,top:830.5,A:70.8,s:59.3,
  col:[[0.790,0.241,-0.060],[1.067,0.242,-0.350],[1.256,-0.074,-0.060]],
  rim:120,rimSig:1.907,rimU4:2.373,rimCol:[0.634,0.530,0.508],inner:106.2,innerS:6.49,body:[3,3,3]};

// ---------------- planet: precomputed glow image ----------------
let planetCanvas=null;
function buildPlanet(){
  const PAD=0, w=1920, h=1080+260; // drawn with top at PL.top in reference frame, extra rows for when it rises from below
  const c=document.createElement('canvas'); c.width=w; c.height=h; const g=c.getContext('2d');
  const img=g.createImageData(w,h); const D=img.data;
  const cy=PL.top+PL.b;
  for(let y=0;y<h;y++){for(let x=0;x<w;x++){
    const X=(x-PL.cx)/PL.a, Y=(y-cy)/PL.b; const gg=Math.sqrt(X*X+Y*Y);
    const gx=X/(PL.a*gg), gy=Y/(PL.b*gg); const d=(gg-1)/Math.sqrt(gx*gx+gy*gy);
    const u=cl((x-PL.cx)/PL.a,-1.2,1.2);
    let r,gc,b,al;
    const rimW=PL.rim*Math.max(0,1-PL.rimU4*u*u*u*u)*Math.exp(-(d/PL.rimSig)*(d/PL.rimSig));
    if(d<0){ // planet body + inner rim light
      const k=PL.inner*Math.exp(d/PL.innerS);
      r=PL.body[0]+k*0.85; gc=PL.body[1]+k; b=PL.body[2]+k*1.05;
    } else {
      const hal=PL.A*Math.exp(-d/PL.s);
      r=BG[0]+hal*(PL.col[0][0]+PL.col[0][1]*u+PL.col[0][2]*u*u);
      gc=BG[1]+hal*(PL.col[1][0]+PL.col[1][1]*u+PL.col[1][2]*u*u);
      b=BG[2]+hal*(PL.col[2][0]+PL.col[2][1]*u+PL.col[2][2]*u*u);
    }
    r+=rimW*PL.rimCol[0]; gc+=rimW*PL.rimCol[1]; b+=rimW*PL.rimCol[2];
    const i=(y*w+x)*4; D[i]=r; D[i+1]=gc; D[i+2]=b; D[i+3]=255;
  }}
  g.putImageData(img,0,0); planetCanvas=c;
}

// ---------------- text canvas helpers ----------------
const ASK_FONT='200 316px In';
// final letter left edges (ink) at f50 and the converge offsets measured f25->f50
const ASK_LET=[{ch:'A',x:728,off:-9,dx:-7,sx:1},{ch:'s',x:944,off:-2,dx:-26,sx:1},{ch:'k',x:1063,off:5,dx:-8,sx:1.13}];
const ASK_BASE=547; // ink bottom (baseline) y
let askCanvas=null, askInk=[];
function buildAsk(){
  const c=document.createElement('canvas'); c.width=1920; c.height=1080; askCanvas=c;
  const g=c.getContext('2d'); g.font=ASK_FONT; askInk=ASK_LET.map(L=>{const m=g.measureText(L.ch);return m.actualBoundingBoxLeft;});
}
function drawAskLetters(g,p,alpha){ // p = converge progress 0..1
  g.font=ASK_FONT; g.fillStyle=`rgba(255,255,255,${alpha})`; g.textBaseline='alphabetic';
  g.strokeStyle=g.fillStyle; g.lineWidth=1.6; g.lineJoin='miter';
  ASK_LET.forEach((L,i)=>{const bl=g.measureText(L.ch).actualBoundingBoxLeft; const x=L.x+L.off*(1-p)+bl+L.dx;
    g.save(); g.translate(x,ASK_BASE); g.scale(L.sx,1); g.fillText(L.ch,0,0); g.strokeText(L.ch,0,0); g.restore();});
}

// ---------------- DOM refs ----------------
let built=false;
function build(){
  buildPlanet(); buildAsk(); built=true;
}

// streaks (anamorphic flares) measured f17-f27: y, start frame (head at x=0), peak alpha, fade start/end frames, thickness
const STREAKS=[
  {y:435.5,f0:16.0,a:0.95,fo:[22.6,25.6],th:4,band:[22,24,417,17]},
  {y:640,f0:16.75,a:0.95,fo:[23.6,27.2],th:7,band:[22,27,641,17]},
  {y:662.5,f0:17.5,a:0.9,fo:[22.6,25.2],th:4},
  {y:709,f0:19.0,a:0.9,fo:[23.2,26.2],th:6},
  {y:740,f0:19.75,a:0.92,fo:[23.6,27.4],th:4.5},
];
const STREAK_V=525; // px per frame
// colour along x sampled on ref f23 (row 433), normalised to full intensity
const SG=[[0,9,9,6],[80,18,17,22],[160,31,29,41],[240,48,43,70],[320,59,54,83],[400,74,69,108],[480,85,80,121],[560,99,91,149],[640,107,105,156],[720,122,118,168],[800,136,135,166],[880,143,142,159],[960,159,158,173],[1040,175,173,174],[1120,255,253,248],[1200,163,159,142],[1280,157,152,122],[1360,150,145,104],[1440,139,136,81],[1520,135,120,57],[1600,130,101,38],[1680,106,76,30],[1760,79,54,26],[1840,40,32,19],[1920,10,8,6]];
function streakGrad(g,a){
  const gr=g.createLinearGradient(0,0,1920,0);
  SG.forEach(([x,r,gg,b])=>gr.addColorStop(x/1920,`rgba(${Math.min(255,r*1.25)|0},${Math.min(255,gg*1.25)|0},${Math.min(255,b*1.25)|0},${a})`));
  return gr;
}
function renderAskScene(T){
  const cv=$('askcv'); const g=cv.getContext('2d');
  g.setTransform(1,0,0,1,0,0); g.globalAlpha=1; g.filter='none';
  g.fillStyle=`rgb(${BG})`; g.fillRect(0,0,1920,1080);
  const f=T*30+1; // fractional ref frame
  // --- dissolve (f56.5..f63): whole Ask scene pushes in and fades
  const dz=cl((f-56.6)/7);
  // planet
  const po=eoC((T-0.51)/0.7)*(1-cl((f-56.3)/4.6));
  let top=PL.top+120*Math.exp(-Math.max(0,T-0.5)*5.7);
  top+=f>56?Math.min(400,3*Math.exp((f-57)*0.86)):0;
  const psc=1+0.07*Math.pow(dz,2);
  if(po>0){
    g.save(); g.globalAlpha=po;
    g.translate(PL.cx,top); g.scale(psc,psc); g.translate(-PL.cx,-PL.top);
    g.drawImage(planetCanvas,0,0);
    g.restore();
  }
  // streaks
  STREAKS.forEach(S=>{
    const head=(f-S.f0)*STREAK_V; if(head<=0) return;
    const fade=1-cl((f-S.fo[0])/(S.fo[1]-S.fo[0]));
    const tail=Math.max(0,(f-S.fo[0]+1.5)*180);
    if(fade<=0) return;
    const x0=tail,x1=Math.min(1920,head); if(x1<=x0) return;
    g.save();
    g.fillStyle=streakGrad(g,S.a*fade);
    g.fillRect(x0,S.y-S.th/2,x1-x0,S.th);
    // glitch band: hard-edged slab that jumps on for some frames (measured: S1 417-434 at f22-23, S2 641-657 at f21-27)
    if(S.band && f>=S.band[0] && f<S.band[1]){ g.globalAlpha=0.62; g.fillRect(x0,S.band[2],x1-x0,S.band[3]); }
    g.restore();
  });
  // Ask word (own canvas above the UI window: the word dissolves over the rising UI)
  const wc=$('askw').getContext('2d'); wc.setTransform(1,0,0,1,0,0); wc.filter='none'; wc.globalAlpha=1; wc.clearRect(0,0,1920,1080);
  const conv=eioS((f-22)/30);
  if(f>=16.5 && dz<1){
    const glitch=1-cl((f-17)/9);       // 1 -> 0 by f26
    const alpha=cl((f-16.3)/3.2)*(dz>0?Math.exp(-dz*2.1)*(1-cl((dz-0.85)/0.15)):1);
    const sA=1+0.6*Math.pow(dz,1.4);
    const cyA=432-37*Math.pow(dz,1.5);
    const bl=4*dz;
    const ac=askCanvas.getContext('2d'); ac.setTransform(1,0,0,1,0,0); ac.clearRect(0,0,1920,1080); ac.filter='none';
    drawAskLetters(ac,conv,1);
    wc.save();
    if(glitch>0.02){
      const R=rng(Math.floor(f)*7919+13);
      let y=300; const sl=[];
      while(y<560){const h=6+Math.floor(R()*22); sl.push([y,h]); y+=h;}
      sl.forEach(([y0,h])=>{
        const r=R(); const dx=(r<0.35?0:(R()-0.5)*2*140*glitch*glitch); const keep=R()>0.25*glitch;
        if(!keep) return;
        wc.globalAlpha=alpha*(0.8+0.2*R());
        wc.drawImage(askCanvas,0,y0,1920,h,dx,y0,1920,h);
      });
    } else {
      wc.globalAlpha=alpha;
      if(bl>0.2) wc.filter=`blur(${bl}px)`;
      wc.translate(965,cyA); wc.scale(sA,sA); wc.translate(-965,-432);
      wc.drawImage(askCanvas,0,0);
    }
    wc.restore();
  }
  // subtitle 说出需求: per-char blur-in from f27.5, step 1.4 frames, 0.3s each; in dissolve slides down + fades
  const sub=$('sub');
  const sp=sub.children;
  for(let i=0;i<sp.length;i++){
    const p=eoC((f-27.5-i*1.4)/8);
    sp[i].style.opacity=p; sp[i].style.filter=`blur(${(1-p)*8}px)`;
  }
  sub.style.transform=`translateY(${100*Math.pow(dz,1.4)}px)`;
  sub.style.opacity=(1-cl(dz/0.85));
  sub.style.display=(f>=27&&dz<1)?'block':'none';
}

// ---------------- greeting scene (f1-f15) ----------------
function renderGreet(T){
  const z=1+0.0128*(1-Math.exp(-T/0.11))-0.0128; // =1 at end, 1/1.0128 at T=0 (approx)
  const s=1-0.0128*Math.exp(-(T+0.0)/0.11);
  $('greet').style.transform=`translate(1046px,1132px) scale(${s}) translate(-1046px,-1132px)`;
}

// ---------------- window / UI ----------------
function camAt(T){
  // B: settle-in after dissolve (scale about top-left), then the B->A camera move, then slow drift in A
  let c={...CAM0};
  const f=T*30+1;
  if(T<4.452){
    const x=cl((f-57)/26); const sc=1+0.074*Math.pow(1-x,2.2);
    c.s=sc; c.tx=118+WIN_W*(sc-1)/2; c.ty=-404+WIN_H*(sc-1)/2;
  } else {
    const p=camEase((T-4.452)/0.696);
    for(const k in c) c[k]=lerp(CAM0[k],CAM1[k],p);
    // slow orbit in A (measured ry -10.76 -> -6.04 from A f30 to f130)
    const d=cl((T-FA(30))/(FA(130)-FA(30)))*1.05;
    c.ry+=4.72*d; c.tx+=4.6*d; c.s-=0.01*d;
  }
  return c;
}
function setWin(T){
  const c=camAt(T);
  $('win').style.transform=`translate3d(${c.tx}px,${c.ty}px,0) rotateY(${c.ry}deg) rotateX(${c.rx}deg) scale(${c.s})`;
}

const TYPED='把登录页改成深色主题，再跑一遍测试';
function typedCount(f){ // measured: 把 at f73, then every 2 frames; comma at f94; 再 f96 ...
  if(f<73) return 0;
  let n=0; const times=[73,75,77,79,81,83,85,87,89,91,94,96,98,100,102,104,106];
  times.forEach(t=>{if(f>=t) n++;}); return n;
}
const ANSWER='登录页已改为深色主题，24 项测试全部通过。';

function spin(el,T){el.style.transform=`rotate(${(T*360*1.2)%360}deg)`;}

function renderUI(T){
  const f=T*30+1;
  const fa=(T-5)*30+1; // A frame
  // window visibility & dissolve fade-in (f57 -> f63)
  const wo=cl((f-56.8)/6.2);
  $('win').style.opacity=T>=5?1:eoC(wo)*1;
  $('win').style.display=(f>=56.8)?'block':'none';
  // window fill stays see-through while the chapter word dissolves behind it (composer is opaque)
  $('win').style.background=`rgba(11,9,7,${cl((f-56.8)/1.5)})`;
  setWin(T);
  // composer typing
  const n=(f>=124)?0:typedCount(f);
  $('ctext').textContent=TYPED.slice(0,n);
  $('cph').style.display=n>0?'none':'block';
  // send button: grey idle, white while text, dark flash on send f122-123, back to grey by f127
  let bc=[136,134,132];
  if(n>0) bc=[250,248,246];
  if(f>=121.6&&f<124) bc=[30,28,26];
  if(f>=124&&f<127.5){const p=cl((f-124)/3.5);bc=[lerp(30,136,p),lerp(28,134,p),lerp(26,132,p)];}
  $('send').style.background=`rgb(${bc.map(Math.round)})`;
  $('send').style.color=n>0?'#1a1816':'#24221f';
  // chat content (present after send)
  const chat=f>=124;
  $('chat').style.display=chat?'block':'none';
  if(chat){
    // Read row: spinner until A f10, then check. Edit row appears A f10, check at A f40.
    const readDone=fa>=10, editOn=fa>=25, editDone=fa>=40;
    $('r1ck').style.display=readDone?'block':'none'; $('r1sp').style.display=readDone?'none':'block'; spin($('r1sp'),T);
    $('r2').style.display=editOn?'flex':'none';
    $('r2ck').style.display=editDone?'block':'none'; $('r2sp').style.display=editDone?'none':'block'; spin($('r2sp'),T);
    // Bash permission card A f55 -> f79
    const card=fa>=55&&fa<79; $('card').style.display=card?'block':'none'; $('sep').style.display=(fa>=55&&fa<79)?'block':'none';
    // after allow: npm row (spinner until f100), output box, tests line f100
    const run=fa>=79; $('r3').style.display=run?'flex':'none'; $('out').style.display=run?'block':'none';
    $('r3ck').style.display=fa>=100?'block':'none'; $('r3sp').style.display=fa>=100?'none':'block'; spin($('r3sp'),T);
    $('tests').style.display=fa>=100?'block':'none'; $('out').style.height=(fa>=100?107:56)+'px';
    $('thread').style.height=(run?285:(editOn?110:52))+'px';
    // answer typing from A f113, ~1.31 frames per char
    const AT=[113,114,115,116,117,119,120,121,122,124,125,126,128,129,130,131,132,134,135,137,138,139]; let an=0; AT.forEach(x=>{if(fa>=x)an++;});
    $('answer').textContent=ANSWER.slice(0,an);
  }
  // cursor (A f65-f101), local coords of tip
  const cur=$('cursor'); let cx=null,cy=null;
  if(fa>=65&&fa<101){
    if(fa<93){const p=1-Math.pow(0.4,Math.max(0,fa-65.6)); cx=lerp(1760,1461,p); cy=lerp(800,586,p);}
    else {const p=Math.pow(cl((fa-95.5)/5),2.2); cx=lerp(1461,1700,p); cy=lerp(586,940,p);}
  }
  cur.style.display=cx===null?'none':'block';
  if(cx!==null) cur.style.transform=`translate(${cx}px,${cy}px) scale(1.5)`;
  // press highlight f76-79 and ripple f79-88
  const rp=$('ripple');
  if(fa>=75.5&&fa<88){
    let r,o;
    if(fa<79){r=14;o=0.35;} else {const p=(fa-79)/9; r=lerp(16,52,eoC(p)); o=0.38*Math.sqrt(1-p);}
    rp.style.display='block'; rp.style.transform=`translate(${1461-r}px,${586-r}px)`; rp.style.width=rp.style.height=2*r+'px'; rp.style.opacity=o;
  } else rp.style.display='none';
}

// claim (screen space, left): per-char blur-in sweep, ~1230 px/s, each char 0.4 s
function renderClaim(T){
  const lines=[['cl1',4.89],['cl2',5.19],['cl3',5.54]];
  lines.forEach(([id,t0])=>{
    const el=$(id); const ch=el.children;
    for(let i=0;i<ch.length;i++){
      const x=+ch[i].dataset.x;
      const p=eoC((T-t0-x/1230)/0.6);
      ch[i].style.opacity=p; ch[i].style.filter=p<0.999?`blur(${(1-p)*10}px)`:'none';
    }
  });
}

function splitChars(el){
  const txt=el.textContent; el.textContent='';
  [...txt].forEach(c=>{const s=document.createElement('span'); s.textContent=c; s.style.display='inline-block'; if(c===' ') s.style.whiteSpace='pre'; el.appendChild(s);});
  [...el.children].forEach(s=>s.dataset.x=s.offsetLeft);
}

window.renderScene=function(T){
  if(!built){build(); ['cl1','cl2','cl3','sub'].forEach(id=>splitChars($(id)));}
  const f=T*30+1;
  $('greet').style.display=f<16?'block':'none';
  if(f<16) renderGreet(T);
  $('askcv').style.display=(f>=16&&f<64)?'block':'none'; $('askw').style.display=(f>=16&&f<64)?'block':'none';
  if(f>=16&&f<64) renderAskScene(T); else $('sub').style.display='none';
  renderUI(T);
  $('claim').style.display=T>=4.8?'block':'none';
  if(T>=4.8) renderClaim(T);
};
})();
