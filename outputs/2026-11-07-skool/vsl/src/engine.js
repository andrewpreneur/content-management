// Skool VSL motion engine. A page = engine.js + a VSL file that calls VSL({theme, scenes}).
// Contract (explainer skills): window.VIDEO = {w,h,duration}, window.seek(t) is a pure function of time.
// Timing comes from ElevenLabs word timestamps: window.TIMING = {duration, words:[{w,s,e,p}], paras}.
// Scenes are anchored to spoken phrases, so the same scene list fits every voice and the short cuts
// (a scene whose anchor phrase is not in the script is skipped).
// window.CUES (built at load) lists every sound cue {t, type} for the Python mixer.

/* ---------- helpers (from the explainer skills) ---------- */
function spring(t, w = 14, z = 0.82) {
  if (t <= 0) return 0;
  if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
}
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => (x = clamp(x), x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const kf = keys => t => { if (t <= keys[0][0]) return keys[0][1]; for (let i = 1; i < keys.length; i++) { const [a, va] = keys[i - 1], [b, vb, e = ease] = keys[i]; if (t <= b) return lerp(va, vb, e((t - a) / (b - a))); } return keys[keys.length - 1][1]; };
const rng = s => () => (s = (s + 0x6D2B79F5) | 0, s = Math.imul(s ^ (s >>> 15), 1 | s), s ^= s + Math.imul(s ^ (s >>> 7), 61 | s), ((s ^ (s >>> 14)) >>> 0) / 4294967296);
const pop = (t, at, w = 18, z = 0.62) => spring(t - at, w, z);           // 0 -> 1 with a little overshoot
const soft = (t, at, w = 12) => spring(t - at, w, 1);                     // 0 -> 1 no overshoot

/* ---------- setup ---------- */
const QS = new URLSearchParams(location.search);
const FMT = window.FMT || QS.get('fmt') || 'h';
const IS_V = FMT === 'v';
const W = IS_V ? 1080 : 1920, H = IS_V ? 1920 : 1080;
if (!window.TIMING) {   // preview: ?timing=../timing/vsl1-pro.json
  const x = new XMLHttpRequest(); x.open('GET', QS.get('timing') || '../timing/vsl1-pro.json', false); x.send();
  window.TIMING = JSON.parse(x.responseText);
}
const TIM = window.TIMING;
const OUTRO = 3.4;
window.VIDEO = { w: W, h: H, duration: +(TIM.duration + OUTRO).toFixed(3), fps: 30 };
const DUR = window.VIDEO.duration;
const WORDS = TIM.words.map((w, i) => ({ ...w, i, n: w.w.toLowerCase().replace(/[’']/g, "'").replace(/[^a-z0-9']/g, '') }));
const CUES = window.CUES = [];
const cue = (t, type, gain = 1) => { if (t >= 0 && t < DUR) CUES.push({ t: +t.toFixed(3), type, gain }); };
// layout regions: visual box + caption line
const R = IS_V ? { x: 50, y: 250, w: 980, h: 1060 } : { x: 120, y: 60, w: 1680, h: 740 };
const CAP_Y = IS_V ? 1440 : 905;

const norm = s => s.toLowerCase().replace(/[’']/g, "'").replace(/[^a-z0-9' ]/g, ' ').split(/\s+/).filter(Boolean);
function findPhrase(phrase, from = 0, to = WORDS.length) {
  const p = norm(phrase);
  for (let i = from; i <= to - p.length; i++) {
    let ok = true;
    for (let j = 0; j < p.length; j++) { const w = WORDS[i + j].n.replace(/'/g, ''), q = p[j].replace(/'/g, ''); if (!(w === q || (q.endsWith('*') && w.startsWith(q.slice(0, -1))))) { ok = false; break; } }
    if (ok) return i;
  }
  return -1;
}

/* ---------- DOM ---------- */
const el = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; };
const css = (e, o) => { for (const k in o) e.style[k] = o[k]; return e; };
const stage = el('div', 'stage', document.body);
css(stage, { width: W + 'px', height: H + 'px' });
document.body.classList.add(IS_V ? 'fmt-v' : 'fmt-h');
const bgCanvas = el('canvas', 'bg', stage); bgCanvas.width = W; bgCanvas.height = H;
const scenesLayer = el('div', 'layer', stage);
const capLayer = el('div', 'layer caps', stage);
const fxLayer = el('div', 'layer', stage);

/* ---------- icons (simple line icons, 24 grid) ---------- */
const IC = {
  bolt: '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>', users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5"/><circle cx="17" cy="9" r="2.6"/><path d="M16.5 14.6c2.6.2 4.4 1.9 5 4.9"/>',
  cal: '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>', book: '<path d="M4 5.5C4 4.1 5.1 3 6.5 3H20v15H6.5C5.1 18 4 19.1 4 20.5z"/><path d="M4 20.5C4 21.9 5.1 23 6.5 23H20v-5"/>',
  chat: '<path d="M4 5h16v11H9l-5 4z"/>', gear: '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
  rocket: '<path d="M12 2c4 2.5 6 6.5 5.5 12l-2.5 3h-6l-2.5-3C6 8.5 8 4.5 12 2z"/><circle cx="12" cy="9.5" r="2"/><path d="M9 17l-2 5 5-2.5L17 22l-2-5"/>',
  check: '<path d="M4.5 12.5l5 5L19.5 7"/>', play: '<path d="M7 4.5v15l12-7.5z"/>', down: '<path d="M12 3v13M6 10.5l6 6 6-6M4 21h16"/>',
  bulb: '<path d="M9 18h6M10 21.5h4M12 2.5a6.5 6.5 0 0 0-4 11.6c.8.7 1.2 1.6 1.2 2.6v.3h5.6v-.3c0-1 .4-1.9 1.2-2.6A6.5 6.5 0 0 0 12 2.5z"/>',
  dollar: '<path d="M12 2v20M17 6.5c-1-1.3-2.8-2-5-2-2.8 0-4.5 1.4-4.5 3.4 0 4.6 10 2.4 10 7.4 0 2-1.9 3.6-5 3.6-2.4 0-4.4-.9-5.5-2.4"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>', star: '<path d="M12 2.8l2.8 5.9 6.4.8-4.7 4.4 1.2 6.3L12 17.1l-5.7 3.1 1.2-6.3L2.8 9.5l6.4-.8z"/>',
  gift: '<rect x="3" y="8" width="18" height="5" rx="1"/><path d="M5 13v8h14v-8M12 8v13M12 8c-1.5-4-6-4.5-6-2s4 2 6 2c2 0 6 .5 6-2s-4.5-2-6 2"/>',
  layers: '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12.5l9 5 9-5M3 17l9 5 9-5"/>', clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l3.5 2"/>',
  zap: '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>', file: '<path d="M6 2.5h8l5 5V21.5H6z"/><path d="M14 2.5v5h5"/>', inbox: '<path d="M3 13l3-9h12l3 9v7H3z"/><path d="M3 13h5l1.5 3h5L16 13h5"/>',
  arrowR: '<path d="M4 12h15M13 6l6 6-6 6"/>', home: '<path d="M3 11l9-8 9 8"/><path d="M5 9.5V21h14V9.5"/>', pin: '<path d="M12 22s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.6"/>',
  spark: '<path d="M12 2v6M12 16v6M2 12h6M16 12h6M5 5l3.5 3.5M15.5 15.5L19 19M5 19l3.5-3.5M15.5 8.5L19 5"/>', code: '<path d="M8 6l-6 6 6 6M16 6l6 6-6 6"/>',
  chart: '<path d="M3 21h18M6 17v-5M11 17V8M16 17v-7M21 17V4"/>', msg: '<rect x="3" y="4" width="18" height="13" rx="3"/><path d="M8 21l4-4"/>', search: '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/>',
  heart: '<path d="M12 20.5s-8-4.8-8-11A4.5 4.5 0 0 1 12 6a4.5 4.5 0 0 1 8 3.5c0 6.2-8 11-8 11z"/>', puzzle: '<path d="M4 8h4a2 2 0 1 1 4 0h4v4a2 2 0 1 1 0 4v4H4v-4a2 2 0 1 0 0-4z"/>',
  door: '<path d="M5 21V3h11v18M3 21h18"/><circle cx="13" cy="12" r="1"/>', flow: '<rect x="3" y="3" width="7" height="6" rx="1.5"/><rect x="14" y="15" width="7" height="6" rx="1.5"/><path d="M6.5 9v4.5a2 2 0 0 0 2 2H14"/>',
  phone: '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10.5 18.5h3"/>', send: '<path d="M3 11l18-8-8 18-2-8z"/>', video: '<rect x="2.5" y="5" width="14" height="14" rx="3"/><path d="M16.5 10l5-3v10l-5-3"/>',
};
const icon = (name, size = 40, stroke = 'currentColor', sw = 2) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${stroke}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${IC[name] || IC.star}</svg>`;
const CURSOR = '<svg width="34" height="44" viewBox="0 0 17 22"><path d="M1 1v17.5l4.6-4.3 3.1 6.8 2.8-1.3-3-6.6H15z" fill="#111" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>';

/* ---------- jigsaw piece path ---------- */
function piecePath(s, [t, r, b, l]) {     // tabs: 1 out, -1 in, 0 flat; square of side s
  const k = s / 100;
  const edge = (x0, y0, dx, dy, nx, ny, tab) => {
    if (!tab) return `L${x0 + dx * 100 * k},${y0 + dy * 100 * k}`;
    const P = (u, v) => `${x0 + (dx * u + nx * v * tab) * k},${y0 + (dy * u + ny * v * tab) * k}`;
    return `L${P(35, 0)} C${P(40, 0)} ${P(42, -4)} ${P(38, -10)} C${P(32, -20)} ${P(40, -30)} ${P(50, -30)} C${P(60, -30)} ${P(68, -20)} ${P(62, -10)} C${P(58, -4)} ${P(60, 0)} ${P(65, 0)} L${P(100, 0)}`;
  };
  return `M0,0 ${edge(0, 0, 1, 0, 0, 1, t)} ${edge(s, 0, 0, 1, -1, 0, r)} ${edge(s, s, -1, 0, 0, -1, b)} ${edge(0, s, 0, -1, 1, 0, l)} Z`;
}

/* ---------- scene machinery ---------- */
const COMP = {};           // component builders: COMP.name = (s, E) => update(t)
const E = { W, H, IS_V, R, el, css, icon, cue, spring, pop, soft, seg, ease, easeOut, lerp, clamp, kf, rng, piecePath, CURSOR };
// a centred box of design size dw x dh scaled to fit the visual region (or the full frame)
E.box = (s, dw, dh, region = R, maxScale = s.maxScale || 1.75) => {
  const sc = Math.min(region.w / dw, region.h / dh, maxScale);
  const b = el('div', 'box', s.root);
  css(b, { width: dw + 'px', height: dh + 'px', left: (region.x + (region.w - dw * sc) / 2) + 'px', top: (region.y + (region.h - dh * sc) / 2) + 'px', transform: `scale(${sc})`, transformOrigin: '0 0' });
  b.sc = sc; return b;
};
E.full = { x: 0, y: 0, w: W, h: H };
E.at = (e, x, y, extra = '') => { e.style.transform = `translate(${x}px,${y}px) ${extra}`; };
E.show = (e, k, dy = 24, sc0 = 0.86) => { e.style.opacity = clamp(k * 1.6); e.style.transform = `translateY(${(1 - k) * dy}px) scale(${lerp(sc0, 1, k)})`; };

function VSL(cfg) {
  const T = cfg.theme;
  document.documentElement.style.cssText += Object.entries(T.vars).map(([k, v]) => `--${k}:${v};`).join('');
  document.body.classList.add('theme-' + T.name);
  T.drawBg && T.drawBg(bgCanvas.getContext('2d'), W, H, E);
  // resolve scene anchors in order
  let cursor = 0; const S = [];
  for (const sc of cfg.scenes) {
    const alts = Array.isArray(sc.at) ? sc.at : [sc.at];
    let idx = -1;
    for (const a of alts) { idx = findPhrase(a, cursor, Math.min(WORDS.length, cursor + (sc.within || 60))); if (idx >= 0) break; }
    if (idx < 0) continue;
    S.push({ ...sc, wi: idx, t0: Math.max(0, WORDS[idx].s - (sc.lead ?? 0.12)) }); cursor = idx + 1;
  }
  S[0].t0 = 0;
  S.forEach((s, i) => { s.t1 = i + 1 < S.length ? S[i + 1].t0 : TIM.duration + 0.15; s.wj = i + 1 < S.length ? S[i + 1].wi : WORDS.length; s.idx = i; });
  S.push({ kind: T.outro || 'outro', t0: TIM.duration + 0.15, t1: DUR + 1, wi: WORDS.length, wj: WORDS.length, idx: S.length, cap: false, outro: true });
  // build
  for (const s of S) {
    s.words = WORDS.slice(s.wi, s.wj);
    s.wt = (ph, fb = 0) => { const i = findPhrase(ph, s.wi, s.wj); return i >= 0 ? WORDS[i].s : s.t0 + 0.3 + fb; };
    s.wte = (ph) => { const p = norm(ph); const i = findPhrase(ph, s.wi, s.wj); return i >= 0 ? WORDS[i + p.length - 1].e : s.t1 - 0.3; };
    s.root = el('div', 'scene', scenesLayer); s.root.style.zIndex = s.idx + 1;
    s.wrap = s.root;
    if (s.bg) css(s.root, { background: s.bg });
    if (s.tone) s.root.classList.add('tone-' + s.tone);
    s.update = (COMP[s.kind] || COMP.big)(s, E, T) || (() => {});
    if (s.idx > 0) cue(s.t0 - 0.06, s.sfx || T.sceneSfx || 'whoosh', s.sfxGain || 0.8);
  }
  window.SCENES = S;
  // captions: chunk words into short lines
  const maxC = IS_V ? (T.capCharsV || 16) : (T.capChars || 24);
  const chunks = []; let cur = [];
  const capOff = new Set(); S.forEach(s => { if (s.cap === false) for (let i = s.wi; i < s.wj; i++) capOff.add(i); });
  WORDS.forEach((w, i) => {
    if (capOff.has(i)) { if (cur.length) { chunks.push(cur); cur = []; } return; }
    const len = cur.reduce((a, x) => a + x.w.length + 1, 0) + w.w.length;
    const newScene = S.some(s => s.wi === i);
    if (cur.length && (len > maxC || newScene || w.s - cur[cur.length - 1].e > 0.45)) { chunks.push(cur); cur = []; }
    cur.push(w);
    if (/[.,?!;:]$/.test(w.w) && cur.length >= 2) { chunks.push(cur); cur = []; }
  });
  if (cur.length) chunks.push(cur);
  // merge 1-word orphans into previous chunk when short enough
  const capEls = chunks.map((c, ci) => {
    const line = el('div', 'cap', capLayer);
    const spans = c.map(w => { const sp = el('span', 'cw' + (T.hl && T.hl.some(h => w.n.startsWith(h)) ? ' hl' : ''), line); sp.textContent = (T.capUpper ? w.w.toUpperCase() : w.w).replace(/[,;:]$/, '').replace(/\.$/, T.keepDots ? '.' : ''); return sp; });
    const next = chunks[ci + 1];
    const t0 = c[0].s - 0.08, t1 = next ? Math.min(next[0].s - 0.08, c[c.length - 1].e + 1.0) : c[c.length - 1].e + 0.8;
    return { line, spans, c, t0, t1, gapAfter: !next || next[0].s - 0.08 - t1 > 0.15 };
  });
  // outro overlay & preview controls
  window.seek = t => {
    t = clamp(t, 0, DUR - 1e-4);
    T.bgUpdate && T.bgUpdate(bgCanvas, t, E);
    for (const s of S) {
      const vis = t >= s.t0 - 0.02 && t < s.t1 + (T.outDur || 0.32);
      s.root.style.display = vis ? 'block' : 'none';
      if (!vis) continue;
      const kIn = T.inK ? T.inK(t - s.t0) : spring(t - s.t0, 16, 0.86), kOut = seg(t, s.t1, s.t1 + (T.outDur || 0.32));
      (T.transition || defaultTransition)(s, kIn, kOut, t);
      s.update(t);
    }
    { let act = null; for (const s of S) if (t >= s.t0 + (T.toneDelay || 0)) act = s; const tone = act && (act.tone || T.tone) || 'base'; if (capLayer.dataset.tone !== tone) capLayer.dataset.tone = tone; }
    for (const c of capEls) {
      const vis = t >= c.t0 && t < c.t1 + (c.gapAfter ? 0.12 : 0);
      c.line.style.display = vis ? 'flex' : 'none';
      if (!vis) continue;
      const out = c.gapAfter ? seg(t, c.t1, c.t1 + 0.12) : 0;
      const ki = spring(t - c.t0, 22, 0.8); c.line.style.opacity = (1 - out) * clamp(ki * 2); c.line.style.transform = `translateY(calc(-50% + ${(1 - ki) * 24}px))`;
      c.spans.forEach((sp, j) => {
        const w = c.c[j], k = pop(t, w.s - 0.06, 22, 0.65);
        sp.style.opacity = lerp(T.ghost ?? 0.28, 1, clamp(k * 1.5));
        sp.style.transform = `translateY(${(1 - clamp(k, 0, 1.3)) * 8}px) scale(${lerp(0.92, 1, clamp(k, 0, 1.25))})`;
        sp.classList.toggle('on', t >= w.s - 0.03 && t < w.e + 0.08);
      });
    }
  };
  function defaultTransition(s, kIn, kOut) {
    s.root.style.opacity = clamp(kIn * 1.5) * (1 - kOut);
    s.root.style.transform = `translateY(${(1 - kIn) * 40}px) scale(${lerp(0.94, 1, kIn) + kOut * 0.04})`;
  }
  CUES.sort((a, b) => a.t - b.t);
  if (!QS.has('render')) previewControls();
  window.seek(0);
}

function previewControls() {
  const sc = Math.min(innerWidth / W, (innerHeight - 60) / H);
  css(stage, { transform: `scale(${sc})`, transformOrigin: '0 0' });
  const bar = el('div', 'ctl', document.body); const r = el('input', '', bar); r.type = 'range'; r.min = 0; r.max = DUR; r.step = 0.01; r.style.width = '80vw';
  const lab = el('span', '', bar); r.oninput = () => { window.seek(+r.value); lab.textContent = (+r.value).toFixed(2); };
  css(bar, { position: 'fixed', bottom: '10px', left: '10px', zIndex: 99 });
}
