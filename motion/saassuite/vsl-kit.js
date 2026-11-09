// Shared helpers for the full-length speaker VSL overlays (VIDEO 6/7). Needs lib.js (SS) loaded first.
// Graphics live in a fixed 760x440 "panel" that is placed/scaled per format, so they stay off the measured head zone.
const K = (() => {
  const {cl} = SS; const $ = id => document.getElementById(id);
  const V = new URLSearchParams(location.search).get('v') || '169';
  function setup(L) { // L = {W,H,px,py,ps,capY,capS}
    document.body.style.width = L.W + 'px'; document.body.style.height = L.H + 'px';
    const P = $('panel'); P.style.left = L.px + 'px'; P.style.top = L.py + 'px'; P.style.transform = `scale(${L.ps})`;
    const c = $('cap'); c.style.top = L.capY + 'px'; c.style.fontSize = L.capS + 'px';
  }
  // Split words into 2-3 word karaoke phrases (break on >0.35s pause or punctuation).
  function phrases(W) { const ph = []; let cur = []; for (const w of W) { if (cur.length && (cur.length >= 3 || w[1] - cur[cur.length - 1][2] > 0.35 || /[,.?!]$/.test(cur[cur.length - 1][0]))) ph.push(cur), cur = []; cur.push(w); } ph.push(cur); return ph; }
  function captions(t, PH, acc, hideAfter) {
    const cap = $('cap'); if (t > hideAfter) { cap.innerHTML = ''; return; }
    const Pz = PH.find((p, k) => p[0][1] - 0.05 <= t && t < (PH[k + 1] ? Math.min(PH[k + 1][0][1] - 0.05, p[p.length - 1][2] + 0.6) : p[p.length - 1][2] + 0.4));
    if (!Pz) { cap.innerHTML = ''; return; }
    let ai = -1; Pz.forEach((w, i) => { if (w[1] <= t) ai = i; });
    cap.innerHTML = Pz.map((w, i) => `<span style="color:${i === ai ? acc : '#fff'}">${w[0].replace(/[,]$/, '')}</span>`).join('');
    const p = SS.ease.outQuart((t - Pz[0][1] + 0.05) / 0.18); cap.style.opacity = p; cap.style.transform = `translateY(${(1 - p) * 14}px)`;
  }
  // Headline letters: lines = [[word, isAccent], ...] per line.
  function headline(el, lines) { let li = 0; el.innerHTML = lines.map(line => '<div>' + line.map(([w, a]) => [...w].map(c => `<span class="l${a ? ' acc' : ''}" data-i="${li++}">${c}</span>`).join('')).join('<span class="l sp">&nbsp;</span>') + '</div>').join(''); }
  function headlineAt(el, t, t0, t1, o = {}) {
    const vis = t > t0 - 0.05 && t < t1 + 0.3; el.style.display = vis ? 'block' : 'none'; if (!vis) return;
    const out = cl((t - t1) / 0.25);
    el.querySelectorAll('.l').forEach(s => { const i = +s.dataset.i; const r = SS.letterRise(t, t0, i, { stagger: o.stagger || 0.03 });
      s.style.transform = `translateY(${r.y - out * 30}px) rotate(${r.rot}deg)`; s.style.filter = `blur(${r.blur + out * 10}px)`; s.style.opacity = r.op * (1 - out); });
  }
  // Card in (cardSlide from the right) and out (blur fade up).
  function cardAt(el, t, t0, t1, dx = 380) {
    const vis = t > t0 - 0.02 && t < t1 + 0.3; el.style.display = vis ? 'block' : 'none'; if (!vis) return 0;
    const cs = SS.cardSlide(t, t0, dx), out = SS.ease.outCubic((t - t1) / 0.28);
    el.style.opacity = cs.op * (1 - out); el.style.transform = `translate(${cs.x}px,${-out * 24}px)`; el.style.filter = `blur(${(cs.blurX > 0.3 ? cs.blurX : 0) + out * 10}px)`; return 1;
  }
  function rowIn(el, t, t0) { const a = SS.spring(t - t0, 14, 1); el.style.opacity = cl((t - t0) / 0.12); el.style.transform = `translateY(${(1 - a) * 16}px)`; return t >= t0; }
  function stampAt(el, t, t0, t1) { const vis = t > t0 - 0.02 && t < t1 + 0.25; el.style.display = vis ? 'block' : 'none'; if (!vis) return; const s = SS.stamp(t, t0), out = cl((t - t1) / 0.22); el.style.opacity = s.op * (1 - out); el.style.transform = `scale(${s.s * (1 - out * 0.2)}) rotate(${s.rot}deg)`; }
  return { V, $, setup, phrases, captions, headline, headlineAt, cardAt, rowIn, stampAt };
})();
