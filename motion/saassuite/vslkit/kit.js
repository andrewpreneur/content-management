// VSL overlay kit: layout from face_zone, karaoke captions, dark end card, SFX cue export.
// Page sets KIT.init({...}) then defines render(t) calling KIT.caption(t) and KIT.endCard(t).
const KIT = (() => {
  const V = new URLSearchParams(location.search).get('v') || '169', is169 = V === '169';
  const W = is169 ? 1920 : 1080, H = is169 ? 1080 : 1920;
  const $ = id => document.getElementById(id);
  let O, phrases = [], cap, end, cues = [];
  function init(o) {
    O = Object.assign({ accent: '#9B83FF', pill: '#7B5CFF', capY: is169 ? 940 : 1650, capSize: is169 ? 62 : 84, cta: 'See the full training', endDur: 3 }, o);
    document.body.style.width = W + 'px'; document.body.style.height = H + 'px';
    const st = document.createElement('style');
    st.textContent = `#kcap{position:absolute;left:0;right:0;text-align:center;color:#fff;white-space:nowrap;font-family:ID;font-weight:800;font-variation-settings:'opsz' 32;letter-spacing:-0.037em}
#kcap span{display:inline-block;margin:0 .12em;text-shadow:4px 4px 0 rgba(0,0,0,.6),0 0 24px rgba(0,0,0,.35)}
#kend{position:absolute;inset:0;background:#0B0B10;display:none;overflow:hidden}
#kend .glow{position:absolute;left:50%;top:62%;width:140%;height:70%;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(closest-side,${O.pill}55,${O.pill}11 60%,transparent)}
#kend .wm{position:absolute;left:0;right:0;text-align:center;color:#fff;font-family:ID;font-weight:800;font-variation-settings:'opsz' 32;letter-spacing:-0.037em}
#kend .pl{position:absolute;left:50%;background:${O.pill};color:#fff;font:600 ${is169 ? 34 : 40}px IN;padding:${is169 ? '16px 34px' : '20px 40px'};border-radius:999px;white-space:nowrap;box-shadow:0 18px 50px ${O.pill}66}`;
    document.head.appendChild(st);
    cap = document.createElement('div'); cap.id = 'kcap'; cap.style.top = O.capY + 'px'; cap.style.fontSize = O.capSize + 'px'; document.body.appendChild(cap);
    end = document.createElement('div'); end.id = 'kend';
    end.innerHTML = `<div class="glow"></div><div class="wm" style="top:${is169 ? 390 : 780}px;font-size:${is169 ? 150 : 140}px">SaaSSuite<span style="color:${O.accent}">.</span></div><div class="pl" style="top:${is169 ? 600 : 1000}px">${O.cta} →</div>`;
    document.body.appendChild(end);
    let cur = [];
    for (const w of O.words) { const l = cur[cur.length - 1]; if (cur.length && (cur.length >= 3 || w[1] - l[2] > 0.35 || /[,.?!]$/.test(l[0]))) phrases.push(cur), cur = []; cur.push(w); }
    phrases.push(cur);
    O.tEnd = O.words[O.words.length - 1][2] + 0.25;
    window.DURATION = O.tEnd + O.endDur;
    cue(O.tEnd - 0.05, 'whoosh', -4); cue(O.tEnd + 0.45, 'pop', -6);
  }
  function caption(t) {
    if (t >= O.tEnd) { cap.innerHTML = ''; return; }
    const P = phrases.find(p => p[0][1] - 0.05 <= t && t <= p[p.length - 1][2] + 0.15);
    if (!P) { cap.innerHTML = ''; return; }
    let ai = -1; P.forEach((w, i) => { if (w[1] <= t) ai = i; });
    cap.innerHTML = P.map((w, i) => `<span style="color:${i === ai ? O.accent : '#fff'}">${w[0].replace(/,$/, '')}</span>`).join('');
    const p = SS.ease.outQuart((t - P[0][1] + 0.05) / 0.18); cap.style.opacity = p; cap.style.transform = `translateY(${(1 - p) * 14}px)`;
  }
  function endCard(t) {
    const u = t - O.tEnd; end.style.display = u >= 0 ? 'block' : 'none'; if (u < 0) return true;
    end.style.opacity = 0.996 * SS.cl(u / 0.25); // keep <1 so Playwright keeps writing RGBA PNGs (an RGB frame breaks the ffmpeg overlay)
    const wm = end.querySelector('.wm'), r = SS.wordRise(t, O.tEnd + 0.1, 0, { dy: 30 }); wm.style.opacity = r.op; wm.style.transform = `translateY(${r.y}px)`; wm.style.filter = `blur(${r.blur}px)`;
    const s = SS.stamp(t, O.tEnd + 0.45), pl = end.querySelector('.pl'); pl.style.opacity = s.op; pl.style.transform = `translateX(-50%) scale(${s.s}) rotate(${s.rot}deg)`;
    return false;
  }
  // Visibility window helper: returns {on, inP, outP} for an element shown t0..t1 (in 0.35 s, out 0.3 s).
  function win(t, t0, t1, din = 0.35, dout = 0.3) { return { on: t >= t0 - 0.01 && t <= t1 + dout, inP: SS.cl((t - t0) / din), outP: SS.cl((t - t1) / dout) }; }
  function cue(t, kind, gain = 0) { cues.push([+t.toFixed(3), kind, gain]); }
  window.getCues = () => cues;
  return { V, is169, W, H, $, init, caption, endCard, win, cue, get O() { return O; } };
})();
