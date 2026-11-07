// Skool onboarding motion engine. seek(t) is a pure function of time.
// window.DATA = {id, timing:{duration, paras:[{start,end,words:[{w,s,e}]}]}} is injected by render.mjs.
// Scenes come from videos.js (VIDEOS[id]); every scene/element is anchored to word timestamps.
'use strict';
const W = 1920, H = 1080, TR = 0.25;            // half-length of a scene transition (s)
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const ease = x => (x = clamp(x), x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const backOut = x => { x = clamp(x); const c = 1.45; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

let stage, world, D, TM, META, CUES = [];
const cue = (t, type, extra = {}) => CUES.push({ t: +t.toFixed(3), type, ...extra });

// ---------- DOM ----------
function el(tag, css, html, parent) {
  const e = document.createElement(tag);
  if (css) e.style.cssText = css;
  if (html != null) e.innerHTML = html;
  if (parent) parent.appendChild(e);
  return e;
}
const div = (parent, css, html, cls) => { const e = el('div', css, html, parent); if (cls) e.className = cls; return e; };
function appear(e, t, ta, o = {}) {
  const { dy = 34, dx = 0, s0 = .9, dur = .42, rot = 0 } = o;
  const k = clamp((t - ta) / dur), b = backOut(k);
  e.style.opacity = clamp(k * 2.4);
  e.style.transform = `translate(${(1 - b) * dx}px,${(1 - b) * dy}px) scale(${lerp(s0, 1, b)}) rotate(${(1 - b) * rot}deg)`;
}
function typeIn(e, full, t, ta, cps = 30) {
  const n = Math.floor(clamp((t - ta) * cps, 0, full.length));
  const tEnd = ta + full.length / cps;
  const caret = t >= ta && t < tEnd + 0.9 && (t < tEnd || Math.floor((t - tEnd) * 2.2) % 2 === 0);
  e.innerHTML = esc(full.slice(0, n)) + (caret ? '<span class="caret"></span>' : '');
}
const typeDur = (s, cps = 30) => s.length / cps;

// ---------- icons (Lucide-style strokes, ISC) ----------
const IC = {
  check: 'M20 6 9 17l-5-5', pin: 'M12 17v5M9 3h6l-1 7 3 3v2H7v-2l3-3z', heart: 'M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z',
  comment: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z', book: 'M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5v15zM4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5',
  play: 'M7 4l13 8-13 8z', cal: 'M3 6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM16 2v4M8 2v4M3 10h18',
  bulb: 'M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z', wrench: 'M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z',
  users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
  spark: 'M12 3l1.9 5.8L20 10.7l-6.1 1.9L12 18.5l-1.9-5.9L4 10.7l6.1-1.9z', download: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3',
  file: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6', flag: 'M4 22V4M4 4h13l-2.5 4L17 12H4', gift: 'M20 12v10H4V12M2 7h20v5H2zM12 22V7M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7zM12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z',
  tag: 'M12 2H2v10l9.29 9.29a1 1 0 0 0 1.41 0l8.59-8.59a1 1 0 0 0 0-1.41zM7 7h.01', seed: 'M7 20h10M12 20v-8M12 12C12 8 9 6 5 6c0 4 3 6 7 6zM12 12c0-4 3-6 7-6 0 4-3 6-7 6z',
  mail: 'M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zM22 6l-10 7L2 6',
  gear: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z',
  pause: 'M6 4h4v16H6zM14 4h4v16h-4z', arrow: 'M5 12h14M12 5l7 7-7 7', search: 'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.35-4.35',
  bell: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0', brief: 'M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16',
  prompt: 'M4 17l6-6-6-6M12 19h8', q: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01',
  target: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12zM12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
  layers: 'M12 2 2 7l10 5 10-5zM2 17l10 5 10-5M2 12l10 5 10-5', zap: 'M13 2 3 14h9l-1 8 10-12h-9z', eye: 'M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  trend: 'M22 7 13.5 15.5 8.5 10.5 2 17M16 7h6v6', home: 'M3 10l9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM9 22V12h6v10', send: 'M22 2 11 13M22 2l-7 20-4-9-9-4z',
  list: 'M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01', clock: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 6v6l4 2',
};
const icon = (n, size = 28, color = 'currentColor', sw = 2.2) =>
  `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" style="display:block">${(IC[n] || '').split('M').filter(Boolean).map(p => `<path d="M${p}"/>`).join('')}</svg>`;

// ---------- word timing ----------
const norm = s => s.toLowerCase().replace(/’/g, "'").replace(/[^a-z0-9']/g, '');
function findWord(p, phrase, nth = 0) {
  const ws = TM.paras[p].words, ph = phrase.split(' ').map(norm);
  for (let i = 0; i <= ws.length - ph.length; i++) {
    if (ph.every((x, k) => norm(ws[i + k].w) === x)) { if (nth-- === 0) return i; }
  }
  throw new Error(`phrase not found in para ${p}: "${phrase}"`);
}
const A = (p, phrase, nth) => phrase ? TM.paras[p].words[findWord(p, phrase, nth)].s : TM.paras[p].start;
const E = (p, phrase) => {
  if (!phrase) return TM.paras[p].end;
  const i = findWord(p, phrase) + phrase.split(' ').length - 1; return TM.paras[p].words[i].e;
};

// ---------- shared pieces ----------
const AV_COLORS = ['#F97316', '#8B5CF6', '#06B6D4', '#EC4899', '#10B981', '#F59E0B', '#3B82F6', '#EF4444'];
function avatar(parent, x, y, size, initials, color) {
  return div(parent, `left:${x}px;top:${y}px;width:${size}px;height:${size}px;background:${color};font-size:${size * .38}px`, initials, 'av');
}
function skel(parent, x, y, w, h = 12) { return div(parent, `left:${x}px;top:${y}px;width:${w}px;height:${h}px`, null, 'skel'); }
function iconBadge(parent, x, y, size, name, bg = 'var(--accs)', fg = 'var(--acc)') {
  return div(parent, `position:absolute;left:${x}px;top:${y}px;width:${size}px;height:${size}px;border-radius:${size * .3}px;background:${bg};display:flex;align-items:center;justify-content:center;color:${fg}`, icon(name, size * .5, fg));
}
function numBadge(parent, x, y, size, n) {
  return div(parent, `position:absolute;left:${x}px;top:${y}px;width:${size}px;height:${size}px;border-radius:50%;background:var(--acc);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:${size * .46}px;font-family:'Inter Tight'`, String(n));
}
function checkCircle(parent, x, y, size) {
  const c = div(parent, `position:absolute;left:${x}px;top:${y}px;width:${size}px;height:${size}px;border-radius:50%;border:2.5px solid #D5D9E3;display:flex;align-items:center;justify-content:center`);
  const f = div(c, `position:absolute;inset:-2.5px;border-radius:50%;background:var(--ok);display:flex;align-items:center;justify-content:center;opacity:0`, icon('check', size * .6, '#fff', 3));
  return { c, set(t, ta) { const k = backOut(seg(t, ta, ta + .3)); f.style.opacity = clamp(k * 3); f.style.transform = `scale(${lerp(.4, 1, k)})`; } };
}
// title strip shown above a component: small caps kicker + headline
function heading(parent, y, kicker, title, opts = {}) {
  const g = div(parent, `position:absolute;left:0;top:${y}px;width:${W}px;text-align:center`);
  if (kicker) div(g, 'color:var(--acc);margin-bottom:10px', esc(kicker), 'caps');
  if (title) div(g, `font-size:${opts.size || 54}px;line-height:1.1`, title, 'tight');
  return g;
}

// ---------- cursor ----------
function makeCursor(parent, keys) {
  // keys: [[t, x, y, click?], ...] (absolute time, stage coords inside the camera layer)
  const c = div(parent, 'position:absolute;left:0;top:0;width:40px;height:40px;z-index:50;pointer-events:none',
    `<svg width="40" height="40" viewBox="0 0 24 24"><path d="M5 3l14 8.5-6.2 1.3 3.6 7.2-2.6 1.3-3.6-7.2L5 18.5z" fill="#0B0F1A" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/></svg>`);
  const rip = div(parent, 'position:absolute;width:70px;height:70px;border-radius:50%;border:3px solid var(--acc);opacity:0;z-index:49');
  keys.forEach(k => { if (k[3]) cue(k[0], 'click'); });
  return t => {
    let x = keys[0][1], y = keys[0][2];
    for (let i = 1; i < keys.length; i++) {
      const [ta] = keys[i - 1], [tb, xb, yb] = keys[i];
      const mv = Math.min(.7, (tb - ta) * .85), k = ease(seg(t, tb - mv, tb));
      x = lerp(x, xb, k); y = lerp(y, yb, k);
    }
    let press = 0, rk = -1;
    keys.forEach(k => { if (k[3]) { const d = t - k[0]; if (d > -.08 && d < .16) press = 1 - Math.abs(d - .04) / .12; if (d >= 0 && d < .5) rk = d / .5; } });
    c.style.opacity = clamp((t - keys[0][0] + .3) / .3);
    c.style.transform = `translate(${x - 6}px,${y - 4}px) scale(${1 - .14 * clamp(press)})`;
    rip.style.opacity = rk >= 0 ? (1 - rk) * .8 : 0;
    rip.style.transform = `translate(${x - 35}px,${y - 35}px) scale(${lerp(.3, 1.3, easeOut(rk))})`;
  };
}

// ---------- app window (Skool-style community, rebuilt) ----------
const TABS = ['Community', 'Classroom', 'Calendar', 'Members', 'Leaderboards', 'About'];
const WIN = { x: 210, y: 112, w: 1500, h: 800 };
function appWindow(parent, s) {
  const { x, y, w, h } = WIN;
  const win = div(parent, `left:${x}px;top:${y}px;width:${w}px;height:${h}px;overflow:hidden`, null, 'card');
  const top = div(win, `position:absolute;left:0;top:0;width:${w}px;height:78px;border-bottom:1px solid var(--line)`);
  div(top, 'position:absolute;left:32px;top:19px;width:40px;height:40px;border-radius:11px;background:var(--yel);display:flex;align-items:center;justify-content:center;font:800 22px Inter Tight;color:#0B0F1A', 'A');
  div(top, 'left:86px;top:25px;font-weight:700;font-size:22px', "Andrew's Community", 'abs');
  const sb = div(top, `position:absolute;left:${w / 2 - 260}px;top:17px;width:520px;height:44px;border-radius:12px;background:#F1F2F6;display:flex;align-items:center;gap:12px;padding-left:18px;color:#9AA0AE;font-size:17px`, icon('search', 20, '#9AA0AE') + 'Search');
  div(top, `position:absolute;left:${w - 120}px;top:24px;color:#9AA0AE`, icon('bell', 28, '#9AA0AE'));
  avatar(top, w - 72, 17, 44, 'You', '#334155').style.fontSize = '14px';
  const tabs = div(win, `position:absolute;left:0;top:78px;width:${w}px;height:60px;border-bottom:1px solid var(--line)`);
  const tabEls = TABS.map((name, i) => div(tabs, `left:${40 + i * 158}px;top:18px;font-size:18px;font-weight:600;color:#6B7280`, name, 'abs'));
  const ul = div(tabs, 'position:absolute;top:56px;height:4px;border-radius:3px;background:var(--ink)');
  const content = div(win, `position:absolute;left:0;top:138px;width:${w}px;height:${h - 138}px;background:#FAFAFC`);
  const from = TABS.indexOf(s.tabFrom || s.tab), to = TABS.indexOf(s.tab), tabAt = s.tabAt ?? -1;
  if (tabAt > 0) cue(tabAt, 'tick');
  return {
    win, content, update(t) {
      const k = tabAt > 0 ? ease(seg(t, tabAt, tabAt + .35)) : 1;
      const cur = k < .5 ? from : to;
      tabEls.forEach((e, i) => e.style.color = i === cur ? '#0B0F1A' : '#6B7280');
      const a = tabEls[from], b = tabEls[to];
      const ax = a.offsetLeft, aw = a.offsetWidth, bx = b.offsetLeft, bw = b.offsetWidth;
      ul.style.left = lerp(ax, bx, k) + 'px'; ul.style.width = lerp(aw, bw, k) + 'px';
    }
  };
}

function postCard(parent, x, y, w, p) {
  const hgt = p.h || (p.body === false ? 128 : 176);
  const c = div(parent, `left:${x}px;top:${y}px;width:${w}px;height:${hgt}px`, null, 'card');
  c.style.borderRadius = '18px';
  avatar(c, 24, 22, 46, p.initials || 'JM', p.color || AV_COLORS[0]);
  div(c, 'left:84px;top:22px;font-weight:700;font-size:18px', esc(p.name || 'Member'), 'abs');
  div(c, 'left:84px;top:46px;font-size:15px;color:#8A90A0', esc(p.meta || '2h · ' + (p.tag || 'General')), 'abs');
  if (p.pinned) div(c, `position:absolute;right:22px;top:22px;display:flex;gap:6px;align-items:center;color:var(--acc);font-weight:700;font-size:15px`, icon('pin', 18, 'var(--acc)') + 'Pinned');
  if (p.badge) div(c, `position:absolute;right:22px;top:22px;padding:6px 14px;border-radius:999px;background:${p.badgeBg || 'var(--yel)'};font-weight:700;font-size:15px;color:#0B0F1A`, esc(p.badge));
  const title = div(c, `left:24px;top:84px;font-weight:700;font-size:23px;max-width:${w - 48}px;overflow:hidden`, esc(p.title || ''), 'abs');
  if (p.body !== false) { skel(c, 24, 124, w * .78); skel(c, 24, 146, w * .52); }
  const foot = div(c, `position:absolute;left:${w - 190}px;top:${hgt - 46}px;display:flex;gap:22px;color:#8A90A0;font-weight:600;font-size:16px;align-items:center`);
  const likes = el('span', null, '', foot), cm = el('span', null, '', foot);
  return {
    c, title, h: hgt, setCounts(nl, nc) {
      likes.innerHTML = `<span style="display:inline-flex;gap:6px;align-items:center">${icon('heart', 18, '#8A90A0')}${nl}</span>`;
      cm.innerHTML = `<span style="display:inline-flex;gap:6px;align-items:center">${icon('comment', 18, '#8A90A0')}${nc}</span>`;
    }
  };
}
const countUp = (t, ta, n, step = .18) => Math.max(0, Math.min(n, Math.floor((t - ta) / step) + 1)) * (t >= ta ? 1 : 0);

// ---------- components ----------
const C = {};

// Big kinetic text lines. lines: [{t:'text with *highlight*', at, serif?, size?, color?}], icon?, chips?
C.kinetic = (L, s) => {
  const box = div(L, `position:absolute;left:0;top:0;width:${W}px;height:${H}px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:${s.gap ?? 6}px`);
  let ic;
  if (s.icon) { ic = div(box, 'position:relative;width:120px;height:120px;border-radius:34px;background:var(--acc);display:flex;align-items:center;justify-content:center;margin-bottom:26px', icon(s.icon, 62, '#fff')); }
  if (s.kicker) { s._k = div(box, 'position:relative;color:var(--acc);margin-bottom:16px;font-size:20px', esc(s.kicker), 'caps'); }
  const lines = s.lines.map(ln => {
    const size = ln.size || (ln.serif ? 132 : 104);
    const row = div(box, `position:relative;display:flex;gap:${size * .26}px;font-size:${size}px;line-height:1.08;color:${ln.color || 'var(--ink)'};white-space:nowrap`, null, ln.serif ? 'serif' : 'tight');
    if (ln.serif && !ln.color) row.style.color = 'var(--acc)';
    const words = ln.t.split(' ').map((w, i) => {
      const hl = /^\*.*\*[.,!?]?$/.test(w); const txt = w.replace(/\*/g, '');
      const sp = el('span', 'position:relative;display:inline-block', null, row);
      let mark;
      if (hl) mark = el('span', `position:absolute;left:-.08em;right:-.08em;top:.12em;bottom:.02em;background:var(--yel);border-radius:.12em;transform-origin:0 50%;z-index:0`, null, sp);
      el('span', 'position:relative;z-index:1', esc(txt), sp);
      return { sp, mark, at: (ln.wordAt && ln.wordAt[i]) || ln.at + i * .07 };
    });
    return { ln, words };
  });
  let chips = [];
  if (s.chips) {
    const row = div(box, 'position:relative;display:flex;gap:22px;margin-top:40px');
    chips = s.chips.map(cp => {
      const c = div(row, `position:relative;height:74px;font-size:30px;background:#fff;border:1.5px solid var(--line);box-shadow:0 8px 24px rgba(15,20,45,.07)`, (cp.icon ? `<span style="color:var(--acc)">${icon(cp.icon, 30, 'var(--acc)')}</span>` : '') + esc(cp.t), 'chip');
      cue(cp.at, 'pop'); return { c, at: cp.at };
    });
  }
  s.lines.forEach(ln => cue(ln.at, 'pop', { soft: 1 }));
  return t => {
    if (ic) appear(ic, t, s.iconAt ?? s.lines[0].at - .15, { dy: 20, s0: .5 });
    if (s._k) appear(s._k, t, s.lines[0].at - .1, { dy: 10 });
    lines.forEach(({ ln, words }) => words.forEach(w => {
      appear(w.sp, t, w.at, { dy: 40, s0: .85, dur: .38 });
      if (w.mark) { const k = easeOut(seg(t, (ln.hlAt ?? w.at + .25), (ln.hlAt ?? w.at + .25) + .35)); w.mark.style.transform = `scaleX(${k})`; }
    }));
    chips.forEach(c => appear(c.c, t, c.at, { dy: 30, s0: .7 }));
  };
};

// Row of resource tiles that pop on their spoken word. items: [{t, icon, at}]
C.tiles = (L, s) => {
  const n = s.items.length, tw = s.tw || 250, gap = 34, total = n * tw + (n - 1) * gap, x0 = (W - total) / 2, y = s.y ?? 400;
  const hd = s.title ? heading(L, y - 190, s.kicker, s.title) : null;
  const tiles = s.items.map((it, i) => {
    const c = div(L, `left:${x0 + i * (tw + gap)}px;top:${y}px;width:${tw}px;height:${tw}px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px`, null, 'card');
    const b = div(c, 'width:96px;height:96px;border-radius:28px;background:var(--accs);display:flex;align-items:center;justify-content:center', icon(it.icon, 48, 'var(--acc)'));
    div(c, `font-weight:700;font-size:${it.t.length > 10 ? 25 : 30}px;letter-spacing:-.01em`, esc(it.t));
    cue(it.at, 'pop'); return { c, b, at: it.at };
  });
  return t => {
    if (hd) appear(hd, t, s.titleAt ?? s.items[0].at - .3, { dy: 16 });
    let act = -1; tiles.forEach((x, i) => { if (t >= x.at) act = i; });
    tiles.forEach((x, i) => {
      appear(x.c, t, x.at, { dy: 60, s0: .6 });
      const on = i === act && s.follow !== false;
      x.c.style.borderColor = on ? 'var(--acc)' : 'var(--line)'; x.c.style.borderWidth = on ? '3px' : '1px';
      x.b.style.background = on ? 'var(--acc)' : 'var(--accs)';
      x.b.innerHTML = icon(s.items[i].icon, 48, on ? '#fff' : 'var(--acc)');
    });
  };
};

// Three-path chooser. cards: [{t, sub, icon, at, items:[{t, at}]}]
C.chooser = (L, s) => {
  const cw = 500, ch = 560, gap = 44, x0 = (W - (3 * cw + 2 * gap)) / 2, y = 300;
  const hd = heading(L, 120, s.kicker, s.title);
  const cards = s.cards.map((cd, i) => {
    const c = div(L, `left:${x0 + i * (cw + gap)}px;top:${y}px;width:${cw}px;height:${ch}px`, null, 'card');
    numBadge(c, 36, 36, 52, i + 1);
    div(c, 'left:104px;top:44px;color:#8A90A0;font-size:16px', 'Path ' + (i + 1), 'abs caps');
    const ib = iconBadge(c, cw - 112, 30, 76, cd.icon);
    div(c, 'left:36px;top:130px;font-size:46px', esc(cd.t), 'abs tight');
    div(c, 'left:36px;top:192px;font-size:21px;color:#6B7280', esc(cd.sub), 'abs');
    div(c, `position:absolute;left:36px;top:240px;width:${cw - 72}px;height:1px;background:var(--line)`);
    const rows = cd.items.map((it, k) => {
      const r = div(c, `position:absolute;left:36px;top:${272 + k * 86}px;width:${cw - 72}px;height:68px;border-radius:16px;background:#F6F7FA;display:flex;align-items:center;gap:16px;padding-left:18px;font-size:23px;font-weight:600`);
      const cc = checkCircle(r, 18, 18, 32); el('span', 'margin-left:48px', esc(it.t), r);
      cue(it.at, 'tick'); return { r, cc, at: it.at };
    });
    cue(cd.at, 'pop');
    return { c, ib, rows, at: cd.at, end: s.cards[i + 1] ? s.cards[i + 1].at : (s.endAt ?? 1e9) };
  });
  return t => {
    appear(hd, t, (s.titleAt ?? cards[0].at - .4), { dy: 14 });
    cards.forEach((cd, i) => {
      appear(cd.c, t, (s.inAt ?? cards[0].at - .3) + i * .12, { dy: 70, s0: .85 });
      const act = t >= cd.at && t < cd.end, any = t >= cards[0].at && t < (s.endAt ?? 1e9);
      const k = act ? ease(seg(t, cd.at, cd.at + .3)) : (any ? 0 : 0);
      cd.c.style.boxShadow = act ? '0 30px 70px rgba(15,20,45,.16)' : '';
      cd.c.style.border = act ? '3px solid var(--acc)' : '1px solid var(--line)';
      const base = cd.c.style.transform || '';
      cd.c.style.transform = base + ` translateY(${-18 * k}px)`;
      cd.c.style.opacity = (any && !act && t < (s.endAt ?? 1e9)) ? Math.min(+cd.c.style.opacity, .55) : cd.c.style.opacity;
      cd.rows.forEach(r => { appear(r.r, t, r.at - .05, { dy: 16, s0: .96 }); r.cc.set(t, r.at + .15); });
    });
  };
};

// Composer: a post being written. title typed, then numbered rows [{label, text, at}], post button click.
C.composer = (L, s) => {
  const w = s.w || 1180, x = (W - w) / 2, rowsN = s.rows.length, hgt = s.h || (250 + rowsN * 104 + 110), y = s.y ?? (H - hgt) / 2 - 30;
  const c = div(L, `left:${x}px;top:${y}px;width:${w}px;height:${hgt}px`, null, 'card');
  if (s.kicker) { const k = div(c, `position:absolute;left:44px;top:34px;display:flex;align-items:center;gap:12px;color:var(--acc)`, icon(s.kickIcon || 'comment', 24, 'var(--acc)') + `<span class="caps" style="font-size:16px">${esc(s.kicker)}</span>`); }
  avatar(c, 44, 86, 56, 'You', '#334155').style.fontSize = '16px';
  const ph = div(c, 'left:120px;top:96px;font-size:28px;color:#A0A6B4', esc(s.placeholder || 'Write something...'), 'abs');
  const ttl = div(c, 'left:120px;top:92px;font-size:34px;font-weight:700', '', 'abs');
  div(c, `position:absolute;left:44px;top:172px;width:${w - 88}px;height:1px;background:var(--line)`);
  const rows = s.rows.map((r, i) => {
    const g = div(c, `position:absolute;left:44px;top:${200 + i * 104}px;width:${w - 88}px;height:84px;border-radius:18px;background:#F6F7FA`);
    numBadge(g, 20, 18, 48, r.n ?? i + 1);
    div(g, 'left:88px;top:13px;font-size:15px;color:var(--acc)', esc(r.label), 'abs caps');
    const v = div(g, 'left:88px;top:38px;font-size:27px;font-weight:600', '', 'abs');
    cue(r.at, 'pop', { soft: 1 }); if (r.text) cue(r.at + .15, 'typing', { dur: typeDur(r.text, 34) });
    return { g, v, r };
  });
  const tagx = div(c, `position:absolute;left:44px;top:${hgt - 82}px;height:46px;padding:0 20px;border-radius:999px;background:var(--accs);color:var(--acc);font-weight:700;font-size:18px;display:flex;align-items:center`, esc(s.tag || 'Introductions'));
  const btn = div(c, `left:${w - 44 - 170}px;top:${hgt - 88}px;width:170px;height:58px;font-size:22px`, 'Post', 'btn');
  const toast = s.postAt ? div(L, `position:absolute;left:${W / 2 - 230}px;top:${y + hgt + 26}px;width:460px;height:64px;border-radius:999px;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;gap:12px;font-weight:700;font-size:22px`, icon('check', 24, '#4ADE80', 3) + esc(s.toast || 'Posted to the Community')) : null;
  if (s.title) cue(s.titleAt, 'typing', { dur: typeDur(s.title) });
  if (s.postAt) cue(s.postAt + .25, 'ding');
  const cur = s.postAt ? makeCursor(L, [[s.postAt - 1.1, x + w - 60, y + hgt + 120], [s.postAt, x + w - 44 - 85, y + hgt - 59, 1]]) : null;
  return t => {
    appear(c, t, s.inAt ?? s.titleAt - .35, { dy: 60, s0: .94 });
    ph.style.opacity = t < s.titleAt ? 1 : 0;
    if (t >= s.titleAt) typeIn(ttl, s.title, t, s.titleAt); else ttl.innerHTML = '';
    rows.forEach(({ g, v, r }) => { appear(g, t, r.at, { dy: 20, s0: .95 }); if (r.text) typeIn(v, r.text, t, r.at + .15, 34); });
    if (cur) {
      cur(t);
      const k = seg(t, s.postAt, s.postAt + .12); btn.style.transform = `scale(${1 - .06 * Math.sin(k * Math.PI)})`;
      btn.style.background = t >= s.postAt ? 'var(--ok)' : 'var(--acc)'; btn.innerHTML = t >= s.postAt ? icon('check', 26, '#fff', 3) : 'Post';
      appear(toast, t, s.postAt + .2, { dy: 24, s0: .8 });
    }
  };
};

// Community feed inside the app window. posts: [{name, initials, color, tag, title, at, pinned, likes, comments}]
C.feed = (L, s) => {
  const aw = appWindow(L, { tab: 'Community', ...s });
  const ct = aw.content, colW = 900;
  const comp = div(ct, `left:40px;top:28px;width:${colW}px;height:74px`, null, 'card');
  comp.style.borderRadius = '16px';
  avatar(comp, 18, 15, 44, 'You', '#334155').style.fontSize = '13px';
  const cph = div(comp, 'left:80px;top:23px;font-size:21px;color:#A0A6B4', 'Write something...', 'abs');
  const chipsRow = div(ct, `position:absolute;left:40px;top:120px;display:flex;gap:10px`);
  (s.cats || ['All', 'General', 'Introductions', 'Wins', 'Questions']).forEach((n, i) => {
    const on = n === (s.cat || 'All');
    el('div', `height:40px;padding:0 18px;border-radius:999px;display:flex;align-items:center;font-weight:600;font-size:16px;${on ? 'background:var(--ink);color:#fff' : 'background:#fff;border:1px solid var(--line);color:#4B5563'}`, n, chipsRow);
  });
  // sidebar
  const side = div(ct, `left:${40 + colW + 36}px;top:28px;width:${1500 - colW - 116}px;height:330px`, null, 'card');
  div(side, 'position:absolute;left:0;top:0;right:0;height:110px;border-radius:22px 22px 0 0;background:linear-gradient(120deg,var(--acc),#0B0F1A)');
  div(side, 'left:28px;top:132px;font-weight:700;font-size:22px', "Andrew's Community", 'abs');
  skel(side, 28, 178, 330); skel(side, 28, 200, 260); skel(side, 28, 222, 300);
  div(side, `left:28px;top:262px;width:${1500 - colW - 172}px;height:46px;font-size:18px;background:#F1F2F6;color:#0B0F1A`, 'Invite people', 'btn');
  let yy = 180;
  const compact = s.posts.length > 2;
  const posts = s.posts.map(p => { const pc = postCard(ct, 40, yy, colW, compact ? { body: false, h: 128, ...p } : p); yy += pc.h + 18; cue(p.at, 'pop'); return { pc, p }; });
  const cur = s.cursor ? makeCursor(L, s.cursor) : null;
  return t => {
    aw.update(t);
    posts.forEach(({ pc, p }) => {
      appear(pc.c, t, p.at, { dy: -40, s0: .96 });
      pc.setCounts(countUp(t, p.at + .5, p.likes ?? 0, p.likeStep ?? .12), countUp(t, p.at + .8, p.comments ?? 0, .25));
      if (p.glow) { const on = t >= p.glow; pc.c.style.outline = on ? '3px solid var(--acc)' : 'none'; pc.c.style.outlineOffset = '4px'; }
    });
    if (cur) cur(t);
  };
};

// Classroom: course cards. courses: [{t, icon, color, pct, at}], pick:{i, at}, toast
C.classroom = (L, s) => {
  const aw = appWindow(L, { tab: 'Classroom', ...s });
  const ct = aw.content, cw = 440, chh = 300, gx = 36, x0 = 40, y0 = 34;
  const cards = s.courses.map((cs, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const c = div(ct, `left:${x0 + col * (cw + gx)}px;top:${y0 + row * (chh + 28)}px;width:${cw}px;height:${chh}px;overflow:hidden`, null, 'card');
    const cov = div(c, `position:absolute;left:0;top:0;width:${cw}px;height:150px;background:linear-gradient(135deg,${cs.color || 'var(--acc)'},${cs.color2 || '#0B0F1A'})`);
    div(cov, 'position:absolute;left:28px;top:28px;color:#fff;opacity:.95', icon(cs.icon || 'book', 44, '#fff'));
    div(cov, 'position:absolute;right:26px;top:30px;color:rgba(255,255,255,.75);font-size:15px', 'Course', 'caps');
    div(c, `left:28px;top:172px;font-weight:700;font-size:25px;width:${cw - 56}px;white-space:normal;line-height:1.2`, esc(cs.t), 'abs');
    const bar = div(c, `position:absolute;left:28px;top:${chh - 40}px;width:${cw - 120}px;height:10px;border-radius:5px;background:#ECEEF3;overflow:hidden`);
    const fill = div(bar, 'position:absolute;left:0;top:0;bottom:0;border-radius:5px;background:var(--acc)');
    const pct = div(c, `left:${cw - 78}px;top:${chh - 50}px;font-weight:700;font-size:18px;color:#6B7280`, '0%', 'abs');
    cue(cs.at, 'pop', { soft: 1 }); return { c, fill, pct, cs };
  });
  const pk = s.pick, cur = pk ? makeCursor(L, [[pk.at - 1.2, 1500, 980], [pk.at, WIN.x + x0 + (pk.i % 3) * (cw + gx) + cw / 2, WIN.y + 138 + y0 + Math.floor(pk.i / 3) * (chh + 28) + 120, 1]]) : null;
  const toast = s.toast ? div(L, `position:absolute;left:${W / 2 - 260}px;top:${WIN.y + WIN.h - 100}px;width:520px;height:66px;border-radius:999px;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;gap:12px;font-weight:700;font-size:22px;z-index:20`, icon(s.toastIcon || 'check', 24, '#4ADE80', 3) + esc(s.toast.t)) : null;
  if (s.toast) cue(s.toast.at, 'ding');
  return t => {
    aw.update(t);
    cards.forEach(({ c, fill, pct, cs }, i) => {
      appear(c, t, cs.at, { dy: 50, s0: .9 });
      let p = cs.pct || 0;
      if (cs.grow) p = lerp(cs.grow[0], cs.grow[1], ease(seg(t, cs.grow[2], cs.grow[2] + 1.2)));
      fill.style.width = p + '%'; pct.textContent = Math.round(p) + '%';
      const on = (pk && pk.i === i && t >= pk.at) || (cs.hi && t >= cs.hi);
      c.style.outline = on ? '4px solid var(--acc)' : 'none'; c.style.outlineOffset = '5px';
    });
    if (cur) cur(t);
    if (toast) appear(toast, t, s.toast.at, { dy: 30, s0: .85 });
  };
};

// Calendar month view. events: [{day, t, at, hi}], note:{t, at}
C.calendar = (L, s) => {
  const aw = appWindow(L, { tab: 'Calendar', ...s });
  const ct = aw.content, cw = 196, ch = 102, x0 = 64, y0 = 86;
  div(ct, 'left:64px;top:24px;font-size:30px', esc(s.month || 'This month'), 'abs tight');
  ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach((d, i) => div(ct, `left:${x0 + i * cw + 14}px;top:${y0 - 30}px;font-size:15px;color:#8A90A0;font-weight:700`, d, 'abs caps'));
  const off = s.offset ?? 0, cells = {};
  for (let k = 0; k < 35; k++) {
    const day = k - off + 1, col = k % 7, row = Math.floor(k / 7);
    const c = div(ct, `position:absolute;left:${x0 + col * cw}px;top:${y0 + row * ch}px;width:${cw - 8}px;height:${ch - 8}px;border-radius:14px;background:#fff;border:1px solid var(--line)`);
    if (day >= 1 && day <= 30) { div(c, 'left:12px;top:8px;font-size:16px;font-weight:600;color:#6B7280', day, 'abs'); cells[day] = c; } else c.style.opacity = .35;
  }
  const evs = s.events.map(ev => {
    const c = cells[ev.day];
    const e = div(c, `position:absolute;left:8px;right:8px;bottom:10px;height:38px;border-radius:10px;background:var(--accs);color:var(--acc);font-weight:700;font-size:15px;display:flex;align-items:center;gap:6px;padding-left:10px`, icon('users', 16, 'var(--acc)') + esc(ev.t));
    cue(ev.at, 'pop', { soft: 1 }); return { e, ev, c };
  });
  let note;
  if (s.note) {
    const hv = s.events.find(e => e.hi) || s.events[0];
    const k = hv.day + off - 1, col = k % 7, row = Math.floor(k / 7);
    const nx = WIN.x + x0 + col * cw + (col > 3 ? -470 : cw + 10), ny = WIN.y + 138 + y0 + row * ch - 70;
    note = div(L, `left:${nx}px;top:${ny}px;width:460px;height:${s.note.h || 200}px;z-index:15`, null, 'card');
    note.style.border = '3px solid var(--acc)';
    div(note, 'position:absolute;left:28px;top:24px;display:flex;gap:10px;align-items:center;color:var(--acc)', icon(s.note.icon || 'users', 22, 'var(--acc)') + `<span class="caps" style="font-size:15px">${esc(s.note.kicker || 'Coaching call')}</span>`);
    div(note, 'position:absolute;left:28px;top:64px;right:28px;font-size:28px;font-weight:700;line-height:1.25;white-space:normal', esc(s.note.t));
    cue(s.note.at, 'pop');
  }
  return t => {
    aw.update(t);
    evs.forEach(({ e, ev, c }) => {
      appear(e, t, ev.at, { dy: 12, s0: .7 });
      const on = ev.hi && t >= (s.hiAt ?? ev.at);
      e.style.background = on ? 'var(--acc)' : 'var(--accs)'; e.style.color = on ? '#fff' : 'var(--acc)';
      e.innerHTML = icon('users', 16, on ? '#fff' : 'var(--acc)') + esc(ev.t);
    });
    if (note) appear(note, t, s.note.at, { dy: 30, s0: .85 });
  };
};

// Members gallery with badges. members: [{name, initials, color, building, at}], badges: [{i, t, icon, at}]
C.members = (L, s) => {
  const aw = appWindow(L, { tab: 'Members', ...s });
  const ct = aw.content, cw = 440, chh = 290, gx = 36;
  const cards = s.members.map((m, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const c = div(ct, `left:${40 + col * (cw + gx)}px;top:${30 + row * (chh + 26)}px;width:${cw}px;height:${chh}px`, null, 'card');
    avatar(c, 26, 26, 58, m.initials, m.color);
    div(c, 'left:100px;top:30px;font-weight:700;font-size:22px', esc(m.name), 'abs');
    div(c, 'left:100px;top:60px;font-size:16px;color:#8A90A0', 'Member', 'abs');
    div(c, 'left:26px;top:112px;font-size:15px;color:#8A90A0', 'Building', 'abs caps');
    div(c, `left:26px;top:140px;font-size:24px;font-weight:700;width:${cw - 52}px;white-space:normal;line-height:1.2`, esc(m.building), 'abs');
    skel(c, 26, 222, cw * .7); skel(c, 26, 244, cw * .45);
    cue(m.at, 'pop', { soft: 1 }); return { c, m };
  });
  const badges = (s.badges || []).map(b => {
    const col = b.i % 3, row = Math.floor(b.i / 3);
    const e = div(L, `position:absolute;left:${WIN.x + 40 + col * (cw + gx) + cw - 250}px;top:${WIN.y + 138 + 30 + row * (chh + 26) - 22}px;height:54px;padding:0 20px;border-radius:999px;background:var(--yel);display:flex;align-items:center;gap:10px;font-weight:800;font-size:20px;box-shadow:0 10px 24px rgba(0,0,0,.15);z-index:10`, icon(b.icon, 22, '#0B0F1A', 2.6) + esc(b.t));
    cue(b.at, 'pop'); return { e, b };
  });
  return t => {
    aw.update(t);
    cards.forEach(({ c, m }, i) => {
      appear(c, t, m.at, { dy: 40, s0: .9 });
      const on = badges.some(x => x.b.i === i && t >= x.b.at);
      c.style.outline = on ? '3px solid var(--acc)' : 'none'; c.style.outlineOffset = '4px';
    });
    badges.forEach(({ e, b }) => appear(e, t, b.at, { dy: 20, s0: .4, rot: -8 }));
  };
};

// "Your goal this week" card with typed goal + optional 7-day strip
C.goal = (L, s) => {
  const w = 1160, hgt = s.days ? 520 : 400, x = (W - w) / 2, y = (H - hgt) / 2 - 30;
  const c = div(L, `left:${x}px;top:${y}px;width:${w}px;height:${hgt}px`, null, 'card');
  div(c, `position:absolute;left:0;top:0;width:12px;height:100%;border-radius:22px 0 0 22px;background:var(--acc)`);
  div(c, 'position:absolute;left:60px;top:52px;display:flex;align-items:center;gap:14px;color:var(--acc)', icon(s.icon || 'target', 34, 'var(--acc)') + `<span class="caps" style="font-size:20px">${esc(s.kicker || 'Your goal this week')}</span>`);
  const tx = div(c, 'left:60px;top:120px;font-size:62px', '', 'abs tight');
  div(c, `position:absolute;left:60px;top:226px;width:${w - 120}px;height:2px;background:var(--line)`);
  const pills = (s.pills || []).map((p, i) => {
    const e = div(c, `position:absolute;left:${60 + i * 330}px;top:262px;height:60px;padding:0 24px;border-radius:999px;background:#F3F4F8;display:flex;align-items:center;gap:12px;font-weight:700;font-size:22px`, icon(p.icon || 'check', 24, 'var(--acc)') + esc(p.t));
    cue(p.at, 'pop', { soft: 1 }); return { e, p };
  });
  let days = [];
  if (s.days) {
    'MTWTFSS'.split('').forEach((d, i) => {
      const e = div(c, `position:absolute;left:${60 + i * 150}px;top:${hgt - 160}px;width:120px;height:120px;border-radius:26px;background:#F3F4F8;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-weight:800;font-size:30px;font-family:'Inter Tight'`, `<span style="font-size:14px;color:#8A90A0;font-family:Inter" class="caps">Day</span>${i + 1}`);
      days.push(e);
    });
    cue(s.days.at, 'pop');
  }
  cue(s.typeAt, 'typing', { dur: typeDur(s.text, 26) });
  return t => {
    appear(c, t, s.inAt ?? s.typeAt - .4, { dy: 50, s0: .92 });
    typeIn(tx, s.text, t, s.typeAt, 26);
    pills.forEach(({ e, p }) => appear(e, t, p.at, { dy: 20, s0: .8 }));
    days.forEach((e, i) => {
      appear(e, t, s.days.at + i * .07, { dy: 30, s0: .6 });
      const f = s.days.fill && t >= s.days.fill + i * (s.days.step || .18);
      e.style.background = f ? 'var(--acc)' : '#F3F4F8'; e.style.color = f ? '#fff' : 'var(--ink)';
    });
  };
};

// Downloadable skills/prompts list + a prompt card whose placeholder fills with "your business"
C.resources = (L, s) => {
  const lw = 760, x = 150, y = 190;
  const list = div(L, `left:${x}px;top:${y}px;width:${lw}px;height:640px`, null, 'card');
  div(list, 'position:absolute;left:36px;top:34px;display:flex;align-items:center;gap:12px;color:var(--acc)', icon('download', 24, 'var(--acc)') + '<span class="caps" style="font-size:16px">Downloads</span>');
  const rows = s.files.map((f, i) => {
    const r = div(list, `position:absolute;left:30px;top:${96 + i * 104}px;width:${lw - 60}px;height:86px;border-radius:18px;background:#F6F7FA`);
    iconBadge(r, 16, 13, 60, f.icon || 'file');
    div(r, 'left:92px;top:15px;font-size:15px;color:var(--acc)', esc(f.kind), 'abs caps');
    div(r, 'left:92px;top:38px;font-size:25px;font-weight:700', esc(f.t), 'abs');
    const d = div(r, `position:absolute;right:18px;top:19px;width:48px;height:48px;border-radius:14px;background:#fff;border:1px solid var(--line);display:flex;align-items:center;justify-content:center`, icon('download', 22, '#6B7280'));
    cue(f.at, 'pop', { soft: 1 }); return { r, d, f };
  });
  const pw = 760, px = x + lw + 60;
  const pc = div(L, `left:${px}px;top:${y + 60}px;width:${pw}px;height:520px;background:#0F1424;border-color:#0F1424`, null, 'card');
  div(pc, 'position:absolute;left:36px;top:32px;display:flex;align-items:center;gap:12px;color:#9DB8FF', icon('prompt', 24, '#9DB8FF') + '<span class="caps" style="font-size:16px">Prompt</span>');
  const body = div(pc, `position:absolute;left:36px;top:92px;width:${pw - 72}px;color:#E5E9F5;font-size:29px;line-height:1.5;white-space:normal;font-weight:500`);
  body.innerHTML = esc(s.prompt[0]) + ' <span data-v style="display:inline-block;padding:0 12px;border-radius:10px;font-weight:700"></span> ' + esc(s.prompt[1]);
  const v = body.querySelector('[data-v]');
  cue(s.fillAt, 'typing', { dur: typeDur(s.fill, 30) });
  return t => {
    rows.forEach(({ r, d, f }) => { appear(r, t, f.at, { dx: -40, dy: 0, s0: .97 }); const on = t >= f.at + .5; d.style.background = on ? 'var(--acc)' : '#fff'; d.innerHTML = icon(on ? 'check' : 'download', 22, on ? '#fff' : '#6B7280', on ? 3 : 2.2); });
    appear(list, t, s.inAt, { dy: 40, s0: .95 });
    appear(pc, t, s.promptAt, { dy: 40, s0: .95 });
    if (t < s.fillAt) { v.textContent = s.placeholder; v.style.background = 'rgba(255,210,63,.18)'; v.style.color = '#FFD23F'; }
    else { typeIn(v, s.fill, t, s.fillAt, 30); v.style.background = '#FFD23F'; v.style.color = '#0B0F1A'; }
  };
};

// Question post with labelled fields + replies popping in
C.question = (L, s) => {
  const w = s.w || 1180, rowsN = s.rows.length, hgt = 200 + rowsN * 100 + 30, x = s.x ?? (W - w) / 2, y = s.y ?? 150;
  const c = div(L, `left:${x}px;top:${y}px;width:${w}px;height:${hgt}px`, null, 'card');
  div(c, 'position:absolute;left:44px;top:34px;display:flex;align-items:center;gap:12px;color:var(--acc)', icon('q', 26, 'var(--acc)') + `<span class="caps" style="font-size:16px">${esc(s.kicker || 'Question')}</span>`);
  const ttl = div(c, 'left:44px;top:82px;font-size:36px;font-weight:700', '', 'abs');
  const rows = s.rows.map((r, i) => {
    const g = div(c, `position:absolute;left:44px;top:${170 + i * 100}px;width:${w - 88}px;height:84px;border-radius:18px;background:#F6F7FA`);
    numBadge(g, 18, 18, 48, i + 1);
    div(g, 'left:86px;top:12px;font-size:15px;color:var(--acc)', esc(r.label), 'abs caps');
    const v = div(g, 'left:86px;top:37px;font-size:26px;font-weight:600', '', 'abs');
    cue(r.at, 'pop', { soft: 1 }); cue(r.at + .15, 'typing', { dur: typeDur(r.text, 36) });
    return { g, v, r };
  });
  if (s.title) cue(s.titleAt, 'typing', { dur: typeDur(s.title) });
  const reps = (s.replies || []).map((r, i) => {
    const e = div(L, `left:${x + 90}px;top:${y + hgt + 24 + i * 96}px;width:${w - 90}px;height:80px;display:flex;align-items:center;gap:18px;padding-left:20px;border-radius:18px`, null, 'card');
    avatar(e, 18, 16, 48, r.initials, r.color);
    div(e, 'left:84px;top:14px;font-weight:700;font-size:18px', esc(r.name), 'abs');
    div(e, 'left:84px;top:40px;font-size:21px;color:#374151', esc(r.t), 'abs');
    cue(r.at, 'pop'); return { e, r };
  });
  return t => {
    appear(c, t, s.inAt ?? (s.titleAt - .3), { dy: 50, s0: .95 });
    if (s.title) typeIn(ttl, s.title, t, s.titleAt);
    rows.forEach(({ g, v, r }) => {
      appear(g, t, r.at, { dy: 18, s0: .95 }); typeIn(v, r.text, t, r.at + .15, 36);
      const on = t >= r.at && (!rows.find(o => o.r.at > r.at && t >= o.r.at));
      g.style.boxShadow = on ? 'inset 0 0 0 3px var(--acc)' : 'none';
    });
    reps.forEach(({ e, r }) => appear(e, t, r.at, { dy: 30, s0: .9 }));
  };
};

// Grid of option cards (2x2) popping on words; active one highlighted
C.options = (L, s) => {
  const cw = 700, chh = 240, gx = 40, x0 = (W - 2 * cw - gx) / 2, y0 = s.y ?? 250;
  const hd = s.title ? heading(L, y0 - 150, s.kicker, s.title) : null;
  const cards = s.items.map((it, i) => {
    const c = div(L, `left:${x0 + (i % 2) * (cw + gx)}px;top:${y0 + Math.floor(i / 2) * (chh + 34)}px;width:${cw}px;height:${chh}px`, null, 'card');
    const b = iconBadge(c, 44, 44, 100, it.icon);
    div(c, 'left:44px;top:166px;font-size:15px;color:#8A90A0', 'Option ' + (i + 1), 'abs caps');
    div(c, 'left:176px;top:62px;font-size:44px;line-height:1.08;white-space:normal;width:480px', esc(it.t), 'abs tight');
    cue(it.at, 'pop'); return { c, b, it };
  });
  return t => {
    if (hd) appear(hd, t, s.titleAt ?? cards[0].it.at - .3, { dy: 14 });
    let act = -1; cards.forEach((x, i) => { if (t >= x.it.at) act = i; });
    cards.forEach((x, i) => {
      appear(x.c, t, x.it.at, { dy: 50, s0: .8 });
      const on = i === act; x.c.style.border = on ? '3px solid var(--acc)' : '1px solid var(--line)';
      x.b.style.background = on ? 'var(--acc)' : 'var(--accs)'; x.b.innerHTML = icon(x.it.icon, 50, on ? '#fff' : 'var(--acc)');
    });
  };
};

// Target with a dart that lands on the spoken word
C.target = (L, s) => {
  const cx = 600, cy = 560, R = 300;
  const sv = div(L, `left:${cx - R}px;top:${cy - R}px;width:${2 * R}px;height:${2 * R}px`, `<svg width="${2 * R}" height="${2 * R}" viewBox="-1 -1 2 2">${[1, .78, .56, .34, .13].map((r, i) => `<circle r="${r * .98}" fill="${i % 2 ? '#fff' : 'var(--acc)'}" opacity="${i % 2 ? 1 : (.25 + i * .18)}"/>`).join('')}</svg>`, 'abs');
  const dart = div(L, `left:${cx - 10}px;top:${cy - 10}px;width:300px;height:20px;transform-origin:10px 10px`, `<svg width="300" height="20"><line x1="10" y1="10" x2="250" y2="10" stroke="#0B0F1A" stroke-width="7" stroke-linecap="round"/><path d="M250 10 l40 -16 l-12 16 l12 16z" fill="var(--yel)" stroke="#0B0F1A" stroke-width="3"/><circle cx="10" cy="10" r="8" fill="#0B0F1A"/></svg>`, 'abs');
  const txt = div(L, 'left:1020px;top:380px;display:flex;flex-direction:column;gap:6px', null, 'abs');
  const l1 = div(txt, 'font-size:92px;line-height:1.05', esc(s.l1), 'tight'), l2 = div(txt, 'font-size:132px;line-height:1.05;color:var(--acc)', esc(s.l2), 'serif');
  cue(s.hitAt - .35, 'whoosh'); cue(s.hitAt, 'impact');
  return t => {
    appear(sv, t, s.inAt, { dy: 0, s0: .3, dur: .55 });
    const k = easeOut(seg(t, s.hitAt - .35, s.hitAt));
    const wob = t > s.hitAt ? Math.sin((t - s.hitAt) * 40) * Math.exp(-(t - s.hitAt) * 7) * 4 : 0;
    dart.style.opacity = t > s.hitAt - .35 ? 1 : 0;
    dart.style.transform = `translate(${(1 - k) * 900}px,${-(1 - k) * 300}px) rotate(${-18 + wob}deg)`;
    appear(l1, t, s.inAt + .2, { dy: 30 }); appear(l2, t, s.hitAt, { dy: 30, s0: .7 });
  };
};

// Lesson list (a course page) with "Up next" highlight
C.lessons = (L, s) => {
  const aw = appWindow(L, { tab: 'Classroom', ...s });
  const ct = aw.content;
  const side = div(ct, 'left:40px;top:30px;width:520px;height:600px', null, 'card');
  div(side, 'left:30px;top:28px;font-size:28px', esc(s.course), 'abs tight');
  const bar = div(side, 'position:absolute;left:30px;top:80px;width:460px;height:10px;border-radius:5px;background:#ECEEF3;overflow:hidden');
  div(bar, `position:absolute;left:0;top:0;bottom:0;width:${s.pct || 20}%;background:var(--acc)`);
  const rows = s.items.map((it, i) => {
    const r = div(side, `position:absolute;left:18px;top:${116 + i * 78}px;width:484px;height:64px;border-radius:14px;display:flex;align-items:center;gap:14px;padding-left:16px;font-size:21px;font-weight:600`);
    const ic = el('span', 'display:flex', icon(it.done ? 'check' : 'play', 22, it.done ? 'var(--ok)' : '#9AA0AE', 2.6), r);
    el('span', null, esc(it.t), r);
    return { r, it };
  });
  const nx = s.items.findIndex(i => i.next);
  const tag = div(L, `left:${WIN.x + 40 + 520 - 20}px;top:${WIN.y + 138 + 30 + 116 + nx * 78 + 6}px;height:52px;padding:0 20px;border-radius:999px;background:var(--yel);display:flex;align-items:center;gap:10px;font-weight:800;font-size:20px;z-index:10;box-shadow:0 10px 24px rgba(0,0,0,.15)`, icon('arrow', 22, '#0B0F1A', 2.8) + esc(s.nextLabel || 'Up next'), 'abs');
  const main = div(ct, 'left:600px;top:30px;width:860px;height:600px', null, 'card');
  const vid = div(main, 'position:absolute;left:30px;top:30px;width:800px;height:420px;border-radius:16px;background:linear-gradient(135deg,#1B2340,#0B0F1A);display:flex;align-items:center;justify-content:center');
  div(vid, 'width:96px;height:96px;border-radius:50%;background:rgba(255,255,255,.95);display:flex;align-items:center;justify-content:center', icon('play', 40, '#0B0F1A'));
  const mt = div(main, 'left:30px;top:478px;font-size:30px;font-weight:700', esc(s.items[nx].t), 'abs');
  skel(main, 30, 534, 560); skel(main, 30, 558, 380);
  cue(s.nextAt, 'pop');
  return t => {
    aw.update(t);
    rows.forEach(({ r, it }, i) => { appear(r, t, s.inAt + i * .08, { dx: -20, dy: 0 }); r.style.background = it.next && t >= s.nextAt ? 'var(--accs)' : 'transparent'; });
    appear(tag, t, s.nextAt, { dx: -30, dy: 0, s0: .6 });
    appear(main, t, s.nextAt + .1, { dy: 30, s0: .96 });
  };
};

// Lesson player + "your project" side by side: pause, apply the step, see what happens
C.split = (L, s) => {
  const pw = 900, ph = 640, x0 = 90, y0 = 190;
  const p = div(L, `left:${x0}px;top:${y0}px;width:${pw}px;height:${ph}px`, null, 'card');
  div(p, 'position:absolute;left:32px;top:28px;display:flex;align-items:center;gap:10px;color:var(--acc)', icon('play', 20, 'var(--acc)') + '<span class="caps" style="font-size:15px">Lesson</span>');
  const scr = div(p, `position:absolute;left:32px;top:72px;width:${pw - 64}px;height:440px;border-radius:16px;background:linear-gradient(135deg,#1B2340,#0B0F1A);overflow:hidden`);
  for (let i = 0; i < 4; i++) skel(scr, 50, 60 + i * 44, [520, 380, 600, 300][i], 16).style.background = 'rgba(255,255,255,.12)';
  const stepCard = div(scr, 'position:absolute;left:50px;top:270px;height:80px;padding:0 26px;border-radius:16px;background:var(--yel);display:flex;align-items:center;gap:14px;font-weight:800;font-size:28px;color:#0B0F1A', icon('zap', 28, '#0B0F1A', 2.6) + esc(s.step || 'Step 3: Add the follow-up'));
  const pz = div(scr, 'position:absolute;left:50%;top:50%;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;background:rgba(255,255,255,.95);display:flex;align-items:center;justify-content:center', icon('pause', 46, '#0B0F1A'));
  const bar = div(p, `position:absolute;left:32px;top:540px;width:${pw - 64}px;height:10px;border-radius:5px;background:#ECEEF3;overflow:hidden`);
  const fill = div(bar, 'position:absolute;left:0;top:0;bottom:0;background:var(--acc)');
  div(p, 'left:32px;top:572px;font-size:22px;font-weight:700', esc(s.lesson || 'Lesson 3'), 'abs');
  const qx = x0 + pw + 40, qw = W - qx - 90;
  const q = div(L, `left:${qx}px;top:${y0}px;width:${qw}px;height:${ph}px`, null, 'card');
  div(q, 'position:absolute;left:32px;top:28px;display:flex;align-items:center;gap:10px;color:var(--acc)', icon('layers', 20, 'var(--acc)') + '<span class="caps" style="font-size:15px">Your project</span>');
  const blocks = (s.blocks || ['New lead', 'Send text', 'Book call']).map((b, i) => div(q, `position:absolute;left:32px;top:${86 + i * 112}px;width:${qw - 64}px;height:92px;border-radius:18px;background:#F6F7FA;display:flex;align-items:center;gap:16px;padding-left:22px;font-size:25px;font-weight:700`, `<span style="width:44px;height:44px;border-radius:12px;background:#E3E7F0;display:flex;align-items:center;justify-content:center">${icon('zap', 22, '#6B7280')}</span>${esc(b)}`));
  const nb = div(q, `position:absolute;left:32px;top:${86 + blocks.length * 112}px;width:${qw - 64}px;height:92px;border-radius:18px;background:var(--accs);border:3px solid var(--acc);display:flex;align-items:center;gap:16px;padding-left:20px;font-size:25px;font-weight:700;color:var(--acc)`, `<span style="width:44px;height:44px;border-radius:12px;background:var(--acc);display:flex;align-items:center;justify-content:center">${icon('mail', 22, '#fff')}</span>${esc(s.newBlock || 'Follow-up')}`);
  const ok = div(L, `left:${qx + qw - 260}px;top:${y0 + ph - 50}px;height:64px;padding:0 26px;border-radius:999px;background:var(--ok);color:#fff;display:flex;align-items:center;gap:10px;font-weight:800;font-size:24px;z-index:10;box-shadow:0 12px 30px rgba(22,163,74,.35)`, icon('check', 26, '#fff', 3) + 'It works', 'abs');
  cue(s.pauseAt, 'click'); cue(s.applyAt, 'pop'); cue(s.seeAt, 'ding');
  return t => {
    appear(p, t, s.inAt, { dx: -60, dy: 0, s0: .97 }); appear(q, t, s.inAt + .25, { dx: 60, dy: 0, s0: .97 });
    fill.style.width = lerp(18, 64, clamp((Math.min(t, s.pauseAt) - s.inAt) / 6)) + '%';
    const pk = backOut(seg(t, s.pauseAt, s.pauseAt + .3)); pz.style.opacity = t >= s.pauseAt ? clamp(pk * 2) : 0; pz.style.transform = `scale(${lerp(.4, 1, pk)})`;
    appear(stepCard, t, s.inAt + .5, { dy: 20 });
    blocks.forEach((b, i) => appear(b, t, s.inAt + .4 + i * .1, { dy: 16 }));
    appear(nb, t, s.applyAt, { dx: 0, dy: 40, s0: .6 });
    appear(ok, t, s.seeAt, { dy: 20, s0: .5 });
  };
};

// Workflow nodes; one turns into the trouble spot
C.workflow = (L, s) => {
  const n = s.nodes.length, nw = 320, gap = 90, x0 = (W - n * nw - (n - 1) * gap) / 2, y = 470;
  const hd = s.title ? heading(L, 210, s.kicker, s.title) : null;
  const lines = [], nodes = s.nodes.map((nd, i) => {
    if (i) lines.push(div(L, `position:absolute;left:${x0 + i * (nw + gap) - gap}px;top:${y + 78}px;width:${gap}px;height:6px;background:#CBD2DE;transform-origin:0 50%`));
    const c = div(L, `left:${x0 + i * (nw + gap)}px;top:${y}px;width:${nw}px;height:162px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px`, null, 'card');
    const b = div(c, 'width:64px;height:64px;border-radius:18px;background:var(--accs);display:flex;align-items:center;justify-content:center', icon(nd.icon, 32, 'var(--acc)'));
    div(c, 'font-weight:700;font-size:25px', esc(nd.t));
    return { c, b, nd, at: s.inAt + i * .22 };
  });
  nodes.forEach(x => cue(x.at, 'pop', { soft: 1 }));
  const bad = nodes[s.trouble];
  const qb = div(L, `left:${x0 + s.trouble * (nw + gap) + nw - 46}px;top:${y - 34}px;width:76px;height:76px;border-radius:50%;background:var(--yel);display:flex;align-items:center;justify-content:center;font:800 44px Inter Tight;color:#0B0F1A;box-shadow:0 10px 24px rgba(0,0,0,.18);z-index:5`, '?', 'abs');
  cue(s.troubleAt, 'pop');
  return t => {
    if (hd) appear(hd, t, s.inAt - .2, { dy: 14 });
    nodes.forEach(x => appear(x.c, t, x.at, { dy: 40, s0: .8 }));
    lines.forEach((l, i) => { l.style.transform = `scaleX(${easeOut(seg(t, nodes[i + 1].at - .1, nodes[i + 1].at + .2))})`; });
    const on = t >= s.troubleAt;
    const sh = on ? Math.sin((t - s.troubleAt) * 50) * Math.exp(-(t - s.troubleAt) * 6) * 10 : 0;
    bad.c.style.border = on ? '3px solid #F59E0B' : '1px solid var(--line)';
    bad.c.style.background = on ? '#FFFBEB' : '#fff';
    bad.c.style.translate = `${sh}px 0`;
    appear(qb, t, s.troubleAt, { dy: 20, s0: .3 });
  };
};

// Two big path cards (post it / bring it to coaching)
C.twoPath = (L, s) => {
  const cw = 640, chh = 440, gap = 80, x0 = (W - 2 * cw - gap) / 2, y = s.y ?? 300;
  const hd = s.title ? heading(L, 140, s.kicker, s.title) : null;
  const cards = s.items.map((it, i) => {
    const c = div(L, `left:${x0 + i * (cw + gap)}px;top:${y}px;width:${cw}px;height:${chh}px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px`, null, 'card');
    div(c, 'width:140px;height:140px;border-radius:40px;background:var(--acc);display:flex;align-items:center;justify-content:center', icon(it.icon, 70, '#fff'));
    div(c, 'font-size:50px;text-align:center;line-height:1.1;white-space:normal;width:520px', esc(it.t), 'tight');
    cue(it.at, 'pop'); return { c, it };
  });
  const or = div(L, `left:${W / 2 - 40}px;top:${y + chh / 2 - 40}px;width:80px;height:80px;border-radius:50%;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:24px;z-index:4`, 'or', 'abs');
  return t => {
    if (hd) appear(hd, t, s.items[0].at - .3, { dy: 14 });
    cards.forEach(({ c, it }) => appear(c, t, it.at, { dy: 60, s0: .8 }));
    appear(or, t, s.items[1].at - .15, { dy: 0, s0: .3 });
  };
};

// Progress card: bar jumps forward, optional "new" drop cards
C.progress = (L, s) => {
  const w = 1100, x = (W - w) / 2, y = s.y ?? 640;
  const drops = (s.drops || []).map((d, i) => {
    const c = div(L, `left:${x + i * 570}px;top:${200}px;width:530px;height:330px`, null, 'card');
    div(c, `position:absolute;left:0;top:0;right:0;height:150px;border-radius:22px 22px 0 0;background:linear-gradient(135deg,var(--acc),#0B0F1A)`);
    div(c, 'position:absolute;left:28px;top:28px', icon(d.icon || 'gift', 46, '#fff'));
    div(c, 'position:absolute;right:24px;top:24px;padding:6px 16px;border-radius:999px;background:var(--yel);font-weight:800;font-size:17px', 'NEW');
    div(c, 'left:28px;top:176px;font-size:15px;color:var(--acc)', esc(d.kind), 'abs caps');
    div(c, 'left:28px;top:206px;font-size:30px;font-weight:700', esc(d.t), 'abs');
    skel(c, 28, 262, 380); skel(c, 28, 286, 260);
    cue(d.at, 'pop'); return { c, d };
  });
  const c = div(L, `left:${x}px;top:${y}px;width:${w}px;height:180px`, null, 'card');
  div(c, 'position:absolute;left:40px;top:34px;display:flex;align-items:center;gap:12px;color:var(--acc)', icon('trend', 26, 'var(--acc)') + `<span class="caps" style="font-size:16px">${esc(s.label || 'Current project')}</span>`);
  const pct = div(c, `left:${w - 160}px;top:28px;font-size:44px;width:120px;text-align:right`, '', 'abs tight');
  const bar = div(c, `position:absolute;left:40px;top:110px;width:${w - 80}px;height:26px;border-radius:13px;background:#ECEEF3;overflow:hidden`);
  const fill = div(bar, 'position:absolute;left:0;top:0;bottom:0;border-radius:13px;background:linear-gradient(90deg,var(--acc),#7FB0FF)');
  cue(s.barAt, 'whoosh', { soft: 1 }); cue(s.barAt + .9, 'ding');
  return t => {
    drops.forEach(({ c, d }) => appear(c, t, d.at, { dy: 60, s0: .85 }));
    appear(c, t, s.inAt, { dy: 40, s0: .95 });
    const v = lerp(s.from, s.to, ease(seg(t, s.barAt, s.barAt + 1)));
    fill.style.width = v + '%'; pct.textContent = Math.round(v) + '%';
  };
};

// Seven-day strip filling, then check rows (finished / learned / next)
C.week = (L, s) => {
  const dw = 190, gap = 26, x0 = (W - 7 * dw - 6 * gap) / 2, y = s.rows ? 170 : 380;
  const hd = s.title && !s.rows ? heading(L, 200, s.kicker, s.title) : null;
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((d, i) => {
    const c = div(L, `left:${x0 + i * (dw + gap)}px;top:${y}px;width:${dw}px;height:200px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px`, null, 'card');
    div(c, 'font-size:16px;color:#8A90A0', d, 'caps');
    const n = div(c, 'font-size:64px', String(i + 1), 'tight');
    const ck = div(c, 'position:absolute;right:14px;top:14px;width:34px;height:34px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;opacity:0', icon('check', 20, 'var(--acc)', 3.2));
    return { c, n, ck, i };
  });
  for (let i = 0; i < 7; i++) cue(s.fillAt + i * s.step, 'tick');
  const rows = (s.rows || []).map((r, i) => {
    const e = div(L, `left:${x0}px;top:${430 + i * 128}px;width:${7 * dw + 6 * gap}px;height:108px;display:flex;align-items:center;gap:22px;padding-left:34px`, null, 'card');
    const cc = checkCircle(e, 34, 32, 44);
    div(e, 'left:104px;top:20px;font-size:16px;color:var(--acc)', esc(r.label), 'abs caps');
    div(e, 'left:104px;top:46px;font-size:32px;font-weight:700', esc(r.t), 'abs');
    cue(r.at, 'pop'); return { e, cc, r };
  });
  return t => {
    if (hd) appear(hd, t, s.inAt - .1, { dy: 14 });
    days.forEach(d => {
      appear(d.c, t, s.inAt + d.i * .06, { dy: 40, s0: .7 });
      const on = t >= s.fillAt + d.i * s.step;
      d.c.style.background = on ? 'var(--acc)' : '#fff'; d.c.style.color = on ? '#fff' : 'var(--ink)';
      d.c.style.borderColor = on ? 'var(--acc)' : 'var(--line)';
      d.ck.style.opacity = on ? 1 : 0;
    });
    rows.forEach(({ e, cc, r }) => { appear(e, t, r.at, { dy: 30, s0: .95 }); cc.set(t, r.at + .2); });
  };
};

// Puzzle: last piece flies in and snaps into place
C.puzzle = (L, s) => {
  const sz = 230, g = 14, x0 = 330, y0 = 300;
  const cols = ['var(--acc)', '#0B0F1A', '#FFD23F', 'var(--acc)'];
  const pieces = [0, 1, 2, 3].map(i => {
    const c = div(L, `left:${x0 + (i % 2) * (sz + g)}px;top:${y0 + Math.floor(i / 2) * (sz + g)}px;width:${sz}px;height:${sz}px;border-radius:30px;background:${cols[i]};opacity:${i === 3 ? 1 : .95}`, null, 'abs');
    if (i === 3) c.style.boxShadow = '0 30px 60px rgba(0,0,0,.25)';
    return c;
  });
  const slot = div(L, `left:${x0 + sz + g}px;top:${y0 + sz + g}px;width:${sz}px;height:${sz}px;border-radius:30px;border:4px dashed #C3C9D6`, null, 'abs');
  L.insertBefore(slot, pieces[3]);
  const txt = div(L, 'left:960px;top:390px;display:flex;flex-direction:column;gap:4px', null, 'abs');
  const l1 = div(txt, 'font-size:92px;line-height:1.05', esc(s.l1), 'tight'), l2 = div(txt, 'font-size:128px;line-height:1.05;color:var(--acc)', esc(s.l2), 'serif');
  cue(s.snapAt - .4, 'whoosh'); cue(s.snapAt, 'impact');
  return t => {
    pieces.slice(0, 3).forEach((p, i) => appear(p, t, s.inAt + i * .1, { dy: 30, s0: .6 }));
    const k = ease(seg(t, s.snapAt - .45, s.snapAt));
    const p = pieces[3];
    p.style.opacity = t > s.snapAt - .5 ? 1 : 0;
    const sq = t >= s.snapAt ? 1 + .06 * Math.sin(clamp((t - s.snapAt) / .25) * Math.PI) : 1;
    p.style.transform = `translate(${(1 - k) * 700}px,${-(1 - k) * 420}px) rotate(${(1 - k) * 35}deg) scale(${sq})`;
    appear(l1, t, s.inAt + .2, { dy: 30 }); appear(l2, t, s.snapAt, { dy: 30, s0: .7 });
  };
};

// Avatars gathering around a post (people can see what you're working on)
C.seen = (L, s) => {
  const pc = postCard(L, (W - 980) / 2, 520, 980, { name: 'You', initials: 'You', color: '#334155', meta: 'Just now · Wins', title: s.title, ...s.post });
  const avs = AV_COLORS.slice(0, 7).map((c, i) => {
    const a = avatar(L, W / 2 - 7 * 38 + i * 76 - 30, 420, 76, ['JM', 'RS', 'KL', 'AP', 'TB', 'MN', 'DC'][i], c);
    a.style.border = '4px solid var(--bg)'; return a;
  });
  const eye = div(L, `left:${W / 2 + 7 * 38 - 10}px;top:428px;height:60px;padding:0 20px;border-radius:999px;background:var(--ink);color:#fff;display:flex;align-items:center;gap:10px;font-weight:700;font-size:22px`, icon('eye', 24, '#fff') + 'Seen', 'abs');
  const hd = heading(L, 170, null, s.head, { size: 84 });
  cue(s.postAt, 'pop'); for (let i = 0; i < 7; i++) cue(s.seeAt + i * .12, 'pop', { soft: 1 });
  return t => {
    appear(hd, t, s.inAt, { dy: 30 });
    appear(pc.c, t, s.postAt, { dy: 60, s0: .9 });
    pc.setCounts(countUp(t, s.seeAt + .4, s.post?.likes ?? 14, .1), countUp(t, s.seeAt + .7, s.post?.comments ?? 6, .2));
    avs.forEach((a, i) => appear(a, t, s.seeAt + i * .12, { dy: 30, s0: .3 }));
    appear(eye, t, s.seeAt + .9, { dx: -20, dy: 0, s0: .6 });
  };
};

// ---------- intro sting + end card (shared across the series) ----------
function buildSting() {
  const L = div(stage, `left:0;top:0;width:${W}px;height:${H}px;background:var(--navy);z-index:100`, null, 'abs');
  const band = div(L, `position:absolute;left:0;bottom:-90px;width:${W}px;height:90px;background:var(--acc)`);
  const mark = div(L, `left:${W / 2 - 60}px;top:270px;width:120px;height:120px;border-radius:34px;background:var(--yel);display:flex;align-items:center;justify-content:center;font:800 64px Inter Tight;color:#0B0F1A`, 'A', 'abs');
  const k = div(L, `left:0;top:440px;width:${W}px;text-align:center;color:rgba(255,255,255,.6);font-size:20px`, esc(META.kicker), 'abs caps');
  const ttl = div(L, `left:0;top:486px;width:${W}px;text-align:center;color:#fff;font-size:${META.title.length > 26 ? 88 : 108}px`, META.titleHtml || esc(META.title), 'abs tight');
  const pill = div(L, `left:${W / 2 - 170}px;top:660px;width:340px;height:64px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);display:flex;align-items:center;justify-content:center;gap:16px;color:#fff;font-weight:700;font-size:22px`, '', 'abs');
  pill.innerHTML = esc(META.step) + (META.n ? `<span class="dots">${[1, 2, 3].map(i => `<span class="dot" style="background:${i <= META.n ? 'var(--yel)' : 'rgba(255,255,255,.25)'}"></span>`).join('')}</span>` : '');
  const out0 = TM.paras[0].start - .45;
  cue(.12, 'pop'); cue(.55, 'pop', { soft: 1 }); cue(out0 - .05, 'whoosh');
  return t => {
    if (t > out0 + .6) { L.style.display = 'none'; return; }
    L.style.display = 'block';
    appear(mark, t, .0, { dy: 0, s0: .5, rot: -12, dur: .45 });
    appear(k, t, .2, { dy: 16 }); appear(ttl, t, .3, { dy: 40, s0: .92 }); appear(pill, t, .6, { dy: 20, s0: .8 });
    const o = ease(seg(t, out0, out0 + .55));
    L.style.transform = `translateY(${-o * (H + 90)}px)`;
  };
}
function buildEnd() {
  const t0 = TM.paras[TM.paras.length - 1].end + .45;
  const L = div(stage, `left:0;top:0;width:${W}px;height:${H}px;background:var(--navy);z-index:100;overflow:hidden`, null, 'abs');
  const band = div(L, `position:absolute;left:0;top:-90px;width:${W}px;height:90px;background:var(--acc)`);
  const ok = div(L, `left:${W / 2 - 66}px;top:250px;width:132px;height:132px;border-radius:50%;background:var(--yel);display:flex;align-items:center;justify-content:center`, icon('check', 70, '#0B0F1A', 3.2), 'abs');
  const l1 = div(L, `left:0;top:430px;width:${W}px;text-align:center;color:#fff;font-size:100px`, esc(META.endTitle), 'abs tight');
  const l2 = div(L, `left:0;top:570px;width:${W}px;text-align:center;color:rgba(255,255,255,.7);font-size:40px`, META.endSub, 'abs');
  const dots = div(L, `left:${W / 2 - 160}px;top:680px;width:320px;height:64px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);display:flex;align-items:center;justify-content:center;gap:16px;color:#fff;font-weight:700;font-size:22px`, '', 'abs');
  dots.innerHTML = esc(META.step) + (META.n ? `<span class="dots">${[1, 2, 3].map(i => `<span class="dot" style="background:${i <= META.n ? 'var(--yel)' : 'rgba(255,255,255,.25)'}"></span>`).join('')}</span>` : '');
  cue(t0 - .05, 'whoosh'); cue(t0 + .45, 'ding');
  return t => {
    if (t < t0 - .1) { L.style.display = 'none'; return; }
    L.style.display = 'block';
    const o = ease(seg(t, t0, t0 + .55));
    L.style.transform = `translateY(${(1 - o) * (H + 90)}px)`;
    appear(ok, t, t0 + .45, { dy: 0, s0: .2, rot: -30, dur: .5 });
    appear(l1, t, t0 + .6, { dy: 40 }); appear(l2, t, t0 + .8, { dy: 20 }); appear(dots, t, t0 + 1, { dy: 20 });
  };
}

// ---------- captions (karaoke, chunked) ----------
function buildCaptions() {
  const chunks = [];
  TM.paras.forEach(p => {
    let cur = [];
    p.words.forEach((w, i) => {
      cur.push(w);
      const end = /[.!?]$/.test(w.w) || (/[,;:]$/.test(w.w) && cur.length >= 3) || cur.length >= 6 || i === p.words.length - 1;
      if (end) { chunks.push(cur); cur = []; }
    });
  });
  chunks.forEach((c, i) => { c.t0 = c[0].s - .08; c.t1 = i + 1 < chunks.length ? Math.min(chunks[i + 1][0].s - .08, c[c.length - 1].e + .5) : c[c.length - 1].e + .5; });
  const box = div(stage, `left:0;top:968px;width:${W}px;display:flex;justify-content:center;z-index:60`, null, 'abs');
  const pill = div(box, 'display:flex;gap:12px;padding:12px 28px;border-radius:18px;background:rgba(11,15,26,.92);color:#fff;font-weight:700;font-size:38px;letter-spacing:-.01em;box-shadow:0 12px 30px rgba(0,0,0,.18)');
  let shown = -1, spans = [];
  return (t, hide) => {
    const i = chunks.findIndex(c => t >= c.t0 && t < c.t1);
    if (i < 0 || hide) { box.style.opacity = 0; return; }
    if (i !== shown) { pill.innerHTML = ''; spans = chunks[i].map(w => el('span', null, esc(w.w), pill)); shown = i; }
    box.style.opacity = 1;
    const k = backOut(seg(t, chunks[i].t0, chunks[i].t0 + .25));
    pill.style.transform = `translateY(${(1 - k) * 16}px) scale(${lerp(.94, 1, k)})`;
    chunks[i].forEach((w, j) => {
      const on = t >= w.s - .03, cur = on && (j === chunks[i].length - 1 || t < chunks[i][j + 1].s - .03);
      spans[j].style.opacity = on ? 1 : .38;
      spans[j].style.color = cur ? 'var(--yel)' : '#fff';
    });
  };
}

// series chrome: top-left step label
function buildChrome() {
  const c = div(stage, 'left:56px;top:34px;height:48px;padding:0 20px 0 10px;border-radius:999px;background:#fff;border:1px solid var(--line);display:flex;align-items:center;gap:12px;font-weight:700;font-size:17px;z-index:55', null, 'abs');
  c.innerHTML = `<span style="width:30px;height:30px;border-radius:9px;background:var(--yel);display:flex;align-items:center;justify-content:center;font:800 17px Inter Tight;color:#0B0F1A">A</span><span>${esc(META.chrome)}</span>` +
    (META.n ? `<span class="dots">${[1, 2, 3].map(i => `<span class="dot" style="width:9px;height:9px;background:${i <= META.n ? 'var(--acc)' : '#D8DCE5'}"></span>`).join('')}</span>` : '');
  return c;
}

// ---------- boot / seek ----------
let SCENES = [], sting, endc, caps, chrome, bgDots;
function boot() {
  stage = document.getElementById('stage');
  D = window.DATA; TM = D.timing;
  const V = VIDEOS[D.id]; META = V.meta;
  const r = document.documentElement.style;
  r.setProperty('--acc', META.acc); r.setProperty('--accs', META.accs);
  // soft dotted background, drawn once
  const cv = el('canvas', 'position:absolute;left:0;top:0', null, stage); cv.width = W; cv.height = H;
  const g = cv.getContext('2d'); g.fillStyle = '#F4F5F9'; g.fillRect(0, 0, W, H);
  g.fillStyle = 'rgba(15,20,45,.07)'; for (let y = 20; y < H; y += 36) for (let x = 20; x < W; x += 36) { g.beginPath(); g.arc(x, y, 1.6, 0, 7); g.fill(); }
  const grd = g.createRadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 1100); grd.addColorStop(0, 'rgba(244,245,249,0)'); grd.addColorStop(1, 'rgba(225,229,240,.7)'); g.fillStyle = grd; g.fillRect(0, 0, W, H);
  world = div(stage, `left:0;top:0;width:${W}px;height:${H}px`, null, 'abs');
  const list = V.scenes();
  list.sort((a, b) => a.at - b.at);
  const endT = TM.paras[TM.paras.length - 1].end + .45;
  list.forEach((s, i) => {
    s.t0 = s.at; s.t1 = i + 1 < list.length ? list[i + 1].at : endT + .3;
    const layer = div(world, `left:0;top:0;width:${W}px;height:${H}px;display:none`, null, 'abs');
    const cam = div(layer, `left:0;top:0;width:${W}px;height:${H}px;transform-origin:0 0`, null, 'abs');
    const upd = C[s.kind](cam, s);
    if (i > 0) cue(s.t0 - TR - .05, 'whoosh', { soft: 1 });
    SCENES.push({ s, layer, cam, upd });
  });
  chrome = buildChrome(); caps = buildCaptions(); sting = buildSting(); endc = buildEnd();
  CUES.sort((a, b) => a.t - b.t);
  window.CUES = CUES;
  window.VIDEO = { w: W, h: H, duration: TM.duration };
  if (!/render/.test(location.search)) preview();
  seek(0);
}
const WINDOW_KINDS = ['feed', 'classroom', 'calendar', 'members', 'lessons'];
function camAt(s, t) {
  let x = W / 2, y = H / 2, z = 1;
  if (WINDOW_KINDS.includes(s.kind)) { y = 525; z = 1.08; }   // window scenes sit a little closer
  (s.cam || []).forEach(([tk, cx, cy, cz, dur = .9]) => { const k = ease(seg(t, tk, tk + dur)); x = lerp(x, cx, k); y = lerp(y, cy, k); z = lerp(z, cz, k); });
  z *= 1 + .03 * seg(t, s.t0, s.t1 + TR);   // slow drift push for life
  return `translate(${W / 2 - x * z}px,${H / 2 - y * z}px) scale(${z})`;
}
function seek(t) {
  const mode = META.trans;
  let hideCap = false;
  SCENES.forEach(({ s, layer, cam, upd }, i) => {
    const vis = t >= s.t0 - TR && t <= s.t1 + TR;
    layer.style.display = vis ? 'block' : 'none';
    if (!vis) return;
    const e = i === 0 ? 1 : ease(seg(t, s.t0 - TR, s.t0 + TR)), x = ease(seg(t, s.t1 - TR, s.t1 + TR));
    const m = s.trans || mode;
    if (m === 'slide-x') layer.style.transform = `translateX(${(1 - e) * W - x * W}px)`;
    else if (m === 'slide-y') layer.style.transform = `translateY(${(1 - e) * H - x * H}px)`;
    else { const sc = (1 - e) * -.25 + x * .35; layer.style.transform = `scale(${1 + sc})`; layer.style.opacity = Math.min(e, 1 - x); layer.style.transformOrigin = '50% 50%'; }
    cam.style.transform = camAt(s, t);
    upd(t);
    if (s.nocap && t >= s.t0 - .1 && t < s.t1 - .1) hideCap = true;
  });
  caps(t, hideCap);
  sting(t); endc(t);
  chrome.style.opacity = t < TM.paras[0].start - .2 || t > TM.paras[TM.paras.length - 1].end + .4 ? 0 : 1;
}
window.seek = seek;

function preview() {
  const fit = () => { const k = Math.min(innerWidth / W, (innerHeight - 40) / H); stage.style.transform = `scale(${k})`; };
  fit(); addEventListener('resize', fit);
  const bar = el('input', 'position:fixed;left:10px;right:10px;bottom:8px;width:calc(100% - 20px)', null, document.body);
  bar.type = 'range'; bar.min = 0; bar.max = TM.duration; bar.step = .01; bar.value = 0;
  bar.oninput = () => seek(+bar.value);
}
