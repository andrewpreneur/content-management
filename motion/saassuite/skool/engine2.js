// Skool v3 "showreel" engine. 1920x1080. window.render(t) pure function of time.
// Brief (Andrew + prompt-motion showreel prompt): something moves every second, real camera moves, no slow fades,
// less text (captions carry the words), more graphics, real photos of Andrew.
const Q = new URLSearchParams(location.search), V = Q.get('v') || 'sales';
const WD = 1920, HT = 1080;
const { cl, lerp, ease, spring } = SS;
const W = TIMING[V], SCN = SCENES2[V];
const $ = id => document.getElementById(id);
const norm = s => s.toLowerCase().replace(/[^a-z0-9']/g, '').replace(/'/g, '');
function T(phrase, after = 0, end = false) {
  const p = phrase.split(/\s+/).map(norm);
  for (let i = 0; i < W.length; i++) {
    if (W[i].s < after - 0.01) continue;
    let ok = true; for (let k = 0; k < p.length; k++) if (!W[i + k] || norm(W[i + k].w).replace(/-/g, '') !== p[k].replace(/-/g, '')) { ok = false; break; }
    if (ok) return end ? W[i + p.length - 1].e : W[i].s;
  }
  throw new Error('phrase not found: ' + phrase + ' after ' + after.toFixed(2));
}
const DUR = W[W.length - 1].e + 3.0; window.DUR = DUR;
const E3 = ease.outCubic, E4 = ease.outQuart, EX = ease.outExpo, IO = ease.inOutCubic;
const sp = (x, w = 14, z = 0.62) => spring(x, w, z);
const pos = x => Math.max(0, x);
function el(parent, css = '', html = '', cls = '') { const d = document.createElement('div'); if (cls) d.className = cls; d.style.cssText = 'position:absolute;' + css; d.innerHTML = html; parent.appendChild(d); return d; }
function tf(e, s) { e.style.transform = s; }
function op(e, o) { e.style.opacity = o; }
function blur(e, b) { e.style.filter = b > 0.25 ? `blur(${b}px)` : 'none'; }
function popIn(e, lt, t0, base = '') { const k = sp(lt - t0, 15, 0.55); op(e, cl((lt - t0) / 0.08)); tf(e, `${base} scale(${lt < t0 ? 0 : k})`); }
function riseIn(e, lt, t0, dy = 50, base = '') { const k = E4((lt - t0) / 0.5); op(e, k); blur(e, (1 - k) * 10); tf(e, `${base} translateY(${(1 - k) * dy}px)`); }
const VIO = '#7B5CFF', VIO2 = '#9B83FF', INK = '#141418';
// ---------- icons (24 grid, stroke) ----------
const IC = {
  chat: '<path d="M4 5h16v11H9l-5 4z"/>', play: '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9l5 3-5 3z" fill="currentColor"/>',
  video: '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3"/>', box: '<path d="M3 8l9-5 9 5v8l-9 5-9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
  building: '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2M11 21v-3h2v3"/>',
  megaphone: '<path d="M3 10v4h4l8 5V5L7 10z"/><path d="M18 9a4 4 0 010 6"/>', store: '<path d="M3 9l2-5h14l2 5"/><path d="M4 9v11h16V9"/><path d="M3 9h18M9 20v-6h6v6"/>',
  tag: '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.5"/>', code: '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>', knot: '<path d="M4 12c4-8 12 8 16 0M4 12c4 8 12-8 16 0"/>',
  gear: '<circle cx="12" cy="12" r="3.2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/>', lock: '<rect x="5" y="11" width="14" height="10" rx="2"/>',
  clock: '<circle cx="12" cy="12" r="9"/>', cal: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>', plane: '<path d="M3 11l18-8-7 18-3-7z"/><path d="M11 14l10-11"/>',
  chart: '<path d="M4 20V4M4 20h16"/><path d="M7 15l4-4 3 3 5-6"/>', check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>', heart: '<path d="M12 20s-7-4.5-7-10a4 4 0 017-2.5A4 4 0 0119 10c0 5.5-7 10-7 10z"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 5-7 8-7s7 2 8 7"/>', bolt: '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>', search: '<circle cx="11" cy="11" r="7"/><path d="M16 16l5 5"/>',
  star: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>', dollar: '<path d="M12 2v20M17 6.5c-1-1.5-3-2.5-5-2.5-3 0-5 1.5-5 3.8 0 5 10 2.6 10 8 0 2.4-2.3 4.2-5 4.2-2.3 0-4.3-1-5.3-2.8"/>',
  pin: '<path d="M12 22s-7-7-7-12a7 7 0 0114 0c0 5-7 12-7 12z"/><circle cx="12" cy="10" r="2.5"/>', mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
  gift: '<rect x="3" y="9" width="18" height="12" rx="1"/><path d="M3 13h18M12 9v12M12 9c-2-4-6-4-6-1.5S12 9 12 9zM12 9c2-4 6-4 6-1.5S12 9 12 9z"/>', home: '<path d="M3 11l9-8 9 8v10H3z"/>',
};
const icon = (k, s = 48, c = 'currentColor', w = 2) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round">${IC[k] || ''}</svg>`;
const IMG = n => `assets/${n}.jpg`;
const photo = (n, w, h, r = 28, pos = 'center') => `<div style="width:${w}px;height:${h}px;border-radius:${r}px;overflow:hidden;position:relative;box-shadow:0 40px 90px rgba(20,20,40,.25)"><img src="${IMG(n)}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:${pos}" data-kb></div>`;
const card = (w, h, inner = '', extra = '') => `<div style="width:${w}px;height:${h}px;background:#fff;border:1px solid #E6E4EF;border-radius:26px;box-shadow:0 30px 80px rgba(20,20,40,.12);position:relative;overflow:hidden;${extra}">${inner}</div>`;
const avatar = (s, img, ini, bg) => img ? `<div style="width:${s}px;height:${s}px;border-radius:50%;overflow:hidden;border:4px solid #fff;box-shadow:0 10px 30px rgba(20,20,40,.18)"><img src="${IMG(img)}" style="width:100%;height:100%;object-fit:cover"></div>` : `<div style="width:${s}px;height:${s}px;border-radius:50%;background:${bg || 'linear-gradient(135deg,#7B5CFF,#B9A8FF)'};color:#fff;display:grid;place-items:center;font:800 ${s * 0.36}px ID;border:4px solid #fff;box-shadow:0 10px 30px rgba(20,20,40,.18)">${ini || ''}</div>`;
const GR = ['linear-gradient(135deg,#7B5CFF,#B9A8FF)', 'linear-gradient(135deg,#2E90FA,#9ACBFF)', 'linear-gradient(135deg,#F79009,#FEC84B)', 'linear-gradient(135deg,#12B76A,#7CE0B0)', 'linear-gradient(135deg,#EE46BC,#F9A8D4)', 'linear-gradient(135deg,#141418,#555)'];
const word = (txt, size, color = INK) => `<div style="font:800 ${size}px ID;letter-spacing:-.04em;line-height:.95;color:${color};white-space:nowrap">${[...txt].map((c, i) => `<span data-l="${i}" style="display:inline-block;white-space:pre">${c}</span>`).join('')}</div>`;
function letters(root, lt, t0, st = 0.035) { root.querySelectorAll('[data-l]').forEach(s => { const r = SS.letterRise(lt + 100, t0 + 100, +s.dataset.l, { stagger: st }); tf(s, `translateY(${r.y}px) rotate(${r.rot}deg)`); blur(s, r.blur); op(s, r.op); }); }
function kenburns(root, lt, dur, a = 1.14, b = 1.0) { root.querySelectorAll('[data-kb]').forEach(i => tf(i, `scale(${lerp(a, b, E3(lt / Math.max(1, dur)))})`)); }
function svg(w, h, inner, css = '') { return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible;${css}">${inner}</svg>`; }
function drawPath(p, k) { const L = p._L || (p._L = p.getTotalLength()); p.style.strokeDasharray = L; p.style.strokeDashoffset = L * (1 - cl(k)); }
// ---------- scene renderers: (root, p, at) -> update(lt, dur) ----------
const R = {
  // giant single word, rings + orbiting icons
  hook(root, p, at) {
    const rings = [0, 1, 2].map(i => el(root, `left:960px;top:520px;width:10px;height:10px;border-radius:50%;border:3px solid ${VIO};`));
    const w = el(root, 'left:0;right:0;top:390px;display:flex;justify-content:center', word(p.word, p.size || 250));
    const ics = (p.icons || ['cart', 'chart', 'mail', 'bolt', 'store', 'search']).map((k, i) => el(root, `left:0;top:0;width:120px;height:120px;border-radius:34px;background:#fff;box-shadow:0 18px 40px rgba(20,20,40,.12);display:grid;place-items:center;color:${VIO}`, icon(k, 58)));
    w.style.zIndex = 4;
    return lt => {
      rings.forEach((r, i) => { const k = ((lt - i * 0.45) % 1.6) / 1.6; const s = lt < i * 0.45 ? 0 : 20 + k * 130; tf(r, `translate(-50%,-50%) scale(${s})`); op(r, lt < i * 0.45 ? 0 : (1 - k) * 0.35); r.style.borderWidth = (3 / Math.max(1, s / 10)) + 'px'; });
      letters(w, lt, 0.05, 0.04); tf(w, `scale(${1 + 0.03 * E3(lt / 3)})`);
      ics.forEach((d, i) => { const a = i / ics.length * Math.PI * 2 + lt * 0.35; const R0 = 720 + 40 * Math.sin(lt + i); const x = 960 + Math.cos(a) * R0 - 60, y = 520 + Math.sin(a) * R0 * 0.55 - 60; const k = sp(lt - 0.3 - i * 0.08, 13, 0.5); op(d, cl((lt - 0.3 - i * 0.08) / 0.1)); tf(d, `translate(${x}px,${y}px) scale(${k * (0.8 + 0.25 * Math.sin(a))}) rotate(${Math.sin(lt + i) * 8}deg)`); d.style.zIndex = Math.sin(a) > 0 ? 3 : 0; });
    };
  },
  // revenue line chart fed by "AI" + "Software" chips
  growth(root, p, at) {
    const C = el(root, 'left:640px;top:200px', card(1040, 620, `<div style="position:absolute;left:44px;top:36px;font:600 26px ID;color:#6B6F7B">Revenue</div><div data-n style="position:absolute;left:44px;top:72px;font:800 84px ID;letter-spacing:-.04em;color:${INK}">$0</div>` +
      svg(1040, 620, `<defs><linearGradient id="gf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${VIO}" stop-opacity=".35"/><stop offset="1" stop-color="${VIO}" stop-opacity="0"/></linearGradient></defs>${[0, 1, 2, 3].map(i => `<line x1="44" x2="996" y1="${250 + i * 90}" y2="${250 + i * 90}" stroke="#EEECF4" stroke-width="2"/>`).join('')}<path data-a d="" fill="url(#gf)"/><path data-p d="M44 540 C 200 530, 300 520, 420 470 S 640 380, 760 300 S 920 170, 996 130" fill="none" stroke="${VIO}" stroke-width="7" stroke-linecap="round"/><circle data-d r="12" fill="${VIO}"/><circle data-r r="12" fill="none" stroke="${VIO}" stroke-width="3"/>`, 'position:absolute;left:0;top:0')));
    const chips = ['AI', 'Software'].map((t, i) => el(root, `left:150px;top:${360 + i * 170}px;padding:26px 40px;border-radius:22px;background:${i ? INK : VIO};color:#fff;font:800 54px ID;letter-spacing:-.03em;box-shadow:0 20px 50px rgba(20,20,40,.2)`, t));
    const dots = [...Array(14)].map(() => el(root, `left:0;top:0;width:14px;height:14px;border-radius:50%;background:${VIO}`));
    const path = C.querySelector('[data-p]'), area = C.querySelector('[data-a]'), dot = C.querySelector('[data-d]'), ring = C.querySelector('[data-r]'), num = C.querySelector('[data-n]');
    const tm = p.moneyAt ? at(p.moneyAt) : 1.5;
    return lt => {
      riseIn(C, lt, 0.1, 80); chips.forEach((c, i) => { const k = sp(lt - (i ? at(p.swAt || 'software') : 0.15), 13, 0.55); op(c, cl(k * 3)); tf(c, `translateX(${(1 - k) * -300}px) rotate(${(1 - k) * -10}deg)`); });
      const k = E3((lt - 0.6) / Math.max(1.2, tm - 0.2)); drawPath(path, k); const L = path._L; const pt = path.getPointAtLength(L * cl(k));
      dot.setAttribute('cx', pt.x); dot.setAttribute('cy', pt.y); ring.setAttribute('cx', pt.x); ring.setAttribute('cy', pt.y); const rk = (lt % 0.9) / 0.9; ring.setAttribute('r', 12 + rk * 30); ring.style.opacity = 1 - rk;
      area.setAttribute('d', `M44 580 L44 540 ${[...Array(30)].map((_, i) => { const q = path.getPointAtLength(L * cl(k) * i / 29); return `L${q.x} ${q.y}`; }).join(' ')} L${pt.x} 580 Z`);
      num.textContent = '$' + Math.round(48000 * Math.pow(cl(k), 1.6)).toLocaleString('en-US');
      dots.forEach((d, i) => { const ph = ((lt * 0.8 + i / dots.length) % 1); const from = i % 2 ? [420, 600] : [380, 430]; const to = [700, 520]; const x = lerp(from[0], to[0], ph), y = lerp(from[1], to[1], ph) - Math.sin(ph * Math.PI) * 60; op(d, lt < 0.8 ? 0 : Math.sin(ph * Math.PI) * 0.8); tf(d, `translate(${x}px,${y}px) scale(${0.6 + 0.6 * Math.sin(ph * Math.PI)})`); });
    };
  },
  // community network: center node + ring of members, edges draw, pulses travel
  network(root, p, at) {
    const N = p.n || 10, cx = 960, cy = 500, Rr = p.r || 360;
    const nodes = [...Array(N)].map((_, i) => { const a = -Math.PI / 2 + i / N * Math.PI * 2; return { x: cx + Math.cos(a) * Rr * 1.35, y: cy + Math.sin(a) * Rr * 0.82, img: (p.imgs || [])[i] }; });
    const S = el(root, 'left:0;top:0', svg(1920, 1080, nodes.map((n, i) => `<path data-e="${i}" d="M${cx} ${cy} Q ${(cx + n.x) / 2 + (i % 2 ? 60 : -60)} ${(cy + n.y) / 2} ${n.x} ${n.y}" fill="none" stroke="${VIO}" stroke-opacity=".35" stroke-width="3"/>`).join('') + nodes.map((n, i) => `<path data-x="${i}" d="M${n.x} ${n.y} L ${nodes[(i + 1) % N].x} ${nodes[(i + 1) % N].y}" stroke="#D9D2FA" stroke-width="2" fill="none"/>`).join('')));
    const pulses = nodes.map(() => el(root, `left:0;top:0;width:16px;height:16px;border-radius:50%;background:${VIO};box-shadow:0 0 18px ${VIO}`));
    const av = nodes.map((n, i) => el(root, `left:${n.x - 54}px;top:${n.y - 54}px`, avatar(108, n.img, ['JM', 'KT', 'RS', 'AL', 'DP', 'MB', 'CW', 'NV', 'LH', 'SO', 'EB', 'TG'][i], GR[i % 5])));
    const C = el(root, `left:${cx - 110}px;top:${cy - 110}px`, p.center ? avatar(220, p.center) : `<div style="width:220px;height:220px;border-radius:50%;background:${VIO};display:grid;place-items:center;color:#fff;font:800 56px ID;box-shadow:0 0 0 18px rgba(123,92,255,.15),0 30px 70px rgba(123,92,255,.45)">${p.label || 'You'}</div>`);
    const halo = el(root, `left:${cx}px;top:${cy}px;width:10px;height:10px;border-radius:50%;border:2px solid ${VIO}`);
    const E = S.querySelectorAll('[data-e]'), X = S.querySelectorAll('[data-x]');
    return lt => {
      popIn(C, lt, 0.05); const hk = (lt % 1.4) / 1.4; tf(halo, `translate(-50%,-50%) scale(${24 + hk * 30})`); op(halo, (1 - hk) * 0.5); halo.style.borderWidth = (2 / (2.4 + hk * 3)) + 'px';
      av.forEach((a, i) => popIn(a, lt, 0.35 + i * 0.07));
      E.forEach((e, i) => drawPath(e, E3((lt - 0.3 - i * 0.07) / 0.5))); X.forEach((e, i) => drawPath(e, E3((lt - 1.1 - i * 0.05) / 0.4)));
      pulses.forEach((d, i) => { const e = E[i]; if (!e._L) { op(d, 0); return; } const ph = ((lt * 0.7 + i * 0.37) % 1); const out = i % 2; const q = e.getPointAtLength(e._L * (out ? ph : 1 - ph)); op(d, lt < 1.0 ? 0 : Math.sin(ph * Math.PI)); tf(d, `translate(${q.x - 8}px,${q.y - 8}px)`); });
      tf(root.firstChild, `none`);
    };
  },
  // tools orbit around an AI core; more keep appearing ("every week")
  orbit(root, p, at) {
    const names = p.names; const core = el(root, 'left:860px;top:400px;width:200px;height:200px;border-radius:50%;display:grid;place-items:center;color:#fff;font:800 64px ID;background:radial-gradient(circle at 35% 30%,#B9A8FF,#7B5CFF 55%,#4B2FD6);box-shadow:0 0 0 20px rgba(123,92,255,.12),0 0 120px rgba(123,92,255,.55)', 'AI');
    const orbs = el(root, 'left:0;top:0', svg(1920, 1080, [0, 1, 2].map(i => `<ellipse cx="960" cy="500" rx="${360 + i * 170}" ry="${120 + i * 60}" fill="none" stroke="#D9D2FA" stroke-width="2" stroke-dasharray="6 10" transform="rotate(${-8 + i * 8} 960 500)"/>`).join('')));
    const chips = names.map((n, i) => el(root, 'left:0;top:0;padding:16px 26px;border-radius:16px;background:#fff;border:1px solid #E6E4EF;font:700 30px ID;color:#2b2e38;white-space:nowrap;box-shadow:0 14px 34px rgba(20,20,40,.12)', n));
    const wk = el(root, `left:1500px;top:150px;padding:14px 24px;border-radius:999px;background:${INK};color:#fff;font:700 28px ID`, '');
    return lt => {
      const k = sp(lt, 10, 0.5); tf(core, `scale(${k * (1 + 0.04 * Math.sin(lt * 6))})`); op(orbs, cl(lt / 0.3)); tf(orbs, `rotate(${lt * 2}deg)`); orbs.style.transformOrigin = '960px 500px';
      chips.forEach((c, i) => { const ring = i % 3, a = i * 2.39 + lt * (0.55 - ring * 0.12); const rx = 360 + ring * 170, ry = 120 + ring * 60, rot = (-8 + ring * 8) * Math.PI / 180; let x = Math.cos(a) * rx, y = Math.sin(a) * ry; const X = 960 + x * Math.cos(rot) - y * Math.sin(rot), Y = 500 + x * Math.sin(rot) + y * Math.cos(rot); const d = (Math.sin(a) + 1) / 2; const t0 = 0.3 + i * (p.every || 0.22); const s = SS.stamp(lt, t0); op(c, s.op * (0.55 + 0.45 * d)); tf(c, `translate(${X}px,${Y}px) translate(-50%,-50%) scale(${lt < t0 ? 0 : Math.min(1.1, s.s) * (0.75 + 0.35 * d)})`); c.style.zIndex = d > 0.5 ? 5 : 1; blur(c, (1 - d) * 2.5); });
      const n = Math.max(1, Math.min(52, Math.floor((lt - 0.2) / 0.22) + 1)); wk.textContent = `Week ${n}`; popIn(wk, lt, 0.2);
    };
  },
  // chips fall through a funnel into one coin
  filter(root, p, at) {
    const F = el(root, 'left:660px;top:330px', svg(600, 420, `<path d="M0 0 H600 L370 300 V420 H230 V300 Z" fill="#fff" stroke="#E6E4EF" stroke-width="3"/><path d="M0 0 H600" stroke="${VIO}" stroke-width="6"/>`, 'filter:drop-shadow(0 30px 60px rgba(20,20,40,.12))'));
    const chips = p.names.map(n => el(root, 'left:0;top:0;padding:14px 22px;border-radius:14px;background:#fff;border:1px solid #E6E4EF;font:700 26px ID;color:#2b2e38;white-space:nowrap;box-shadow:0 10px 26px rgba(20,20,40,.1)', n));
    const coin = el(root, `left:860px;top:760px;width:200px;height:200px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 35% 30%,#B9A8FF,#7B5CFF 60%,#4B2FD6);color:#fff;box-shadow:0 0 0 16px rgba(123,92,255,.14),0 0 100px rgba(123,92,255,.6)`, icon('dollar', 96, '#fff', 2.4));
    const gear = el(root, `left:1300px;top:700px;width:150px;height:150px;border-radius:40px;background:${INK};display:grid;place-items:center`, icon('gear', 84, '#fff', 2));
    const tc = at(p.coinAt), tg = p.gearAt ? at(p.gearAt) : 99;
    return lt => {
      riseIn(F, lt, 0, 60);
      chips.forEach((c, i) => { const x0 = 300 + (i % 6) * 230 + (i > 5 ? 110 : 0), y0 = 90 + Math.floor(i / 6) * 90; const t0 = 0.2 + i * 0.12; const f = pos(lt - t0 - 0.5); const fall = Math.min(1, f * f * 1.2); const x = lerp(x0, 960, E3(fall)), y = lerp(y0, 640, fall); op(c, cl((lt - t0) / 0.15) * (1 - cl((fall - 0.85) / 0.15))); tf(c, `translate(${x}px,${y}px) translate(-50%,-50%) rotate(${(i * 23 % 30 - 15) * (1 - fall)}deg) scale(${1 - 0.5 * fall})`); });
      const s = SS.stamp(lt, tc); op(coin, s.op); tf(coin, `scale(${lt < tc ? 0 : s.s}) rotate(${lt * 30 * (lt > tc)}deg)`);
      op(gear, cl((lt - tg) / 0.15)); tf(gear, `scale(${lt < tg ? 0 : sp(lt - tg, 14, 0.55)}) rotate(${(lt - tg) * 120}deg)`);
    };
  },
  // photo reveal: iris opens, Ken Burns, floating tags
  photoHero(root, p, at) {
    const big = p.wide ? [980, 620] : [600, 780]; const x = p.x ?? (p.wide ? 470 : 660), y = p.y ?? (p.wide ? 210 : 140);
    const glow = el(root, `left:${x + big[0] / 2 - 420}px;top:${y + big[1] / 2 - 420}px;width:840px;height:840px;border-radius:50%;background:radial-gradient(circle,rgba(123,92,255,.28),transparent 65%)`);
    const P = el(root, `left:${x}px;top:${y}px`, photo(p.img, big[0], big[1], 34, p.pos || 'center'));
    const tags = (p.tags || []).map((t, i) => el(root, `left:${t.x}px;top:${t.y}px;padding:18px 28px;border-radius:999px;background:${t.dark ? INK : '#fff'};color:${t.dark ? '#fff' : INK};font:700 30px ID;display:flex;align-items:center;gap:14px;white-space:nowrap;box-shadow:0 20px 50px rgba(20,20,40,.16)`, (t.icon ? `<span style="color:${t.dark ? VIO2 : VIO}">${icon(t.icon, 34)}</span>` : '') + t.t));
    const sparks = [...Array(10)].map((_, i) => el(root, `left:0;top:0;width:${8 + i % 3 * 4}px;height:${8 + i % 3 * 4}px;border-radius:50%;background:${i % 2 ? VIO : '#B9A8FF'}`));
    return (lt, dur) => {
      const k = E4((lt - 0.05) / 0.7); P.firstChild.style.clipPath = `circle(${k * 75}% at 50% 50%)`; tf(P, `translateY(${(1 - k) * 40}px) rotate(${(1 - k) * (p.rot ?? -4)}deg)`); kenburns(P, lt, dur);
      op(glow, k); tf(glow, `scale(${0.8 + 0.2 * k + 0.03 * Math.sin(lt * 2)})`);
      tags.forEach((g, i) => { const t0 = p.tags[i].at ? at(p.tags[i].at) : 0.6 + i * 0.35; popIn(g, lt, t0, `translateY(${Math.sin(lt * 1.6 + i) * 8}px)`); });
      sparks.forEach((s, i) => { const a = i / 10 * Math.PI * 2 + lt * 0.4; const r = 470 + 40 * Math.sin(lt * 2 + i); op(s, cl((lt - 0.6) / 0.3) * 0.7); tf(s, `translate(${x + big[0] / 2 + Math.cos(a) * r}px,${y + big[1] / 2 + Math.sin(a) * r * 0.75}px)`); });
    };
  },
  // deck of photos flies in and fans out; optional stamped chip
  fan(root, p, at) {
    const imgs = p.imgs; const cards = imgs.map((n, i) => el(root, 'left:810px;top:230px', photo(n, 420, 560, 24, 'center')));
    const chip = p.chip ? el(root, `left:960px;top:850px;padding:22px 38px;border-radius:999px;background:${VIO};color:#fff;font:800 44px ID;letter-spacing:-.02em;white-space:nowrap;box-shadow:0 24px 60px rgba(123,92,255,.4)`, p.chip) : null;
    return (lt, dur) => {
      const n = cards.length; cards.forEach((c, i) => { const t0 = 0.1 + i * 0.16; const k = sp(lt - t0, 11, 0.62); const f = sp(lt - 0.9 - i * 0.05, 9, 0.7); const ang = (i - (n - 1) / 2) * 13 * f; const dx = (i - (n - 1) / 2) * 250 * f; const lift = Math.sin(lt * 1.2 + i) * 6;
        op(c, cl((lt - t0) / 0.1)); tf(c, `translate(${dx}px,${(1 - k) * 700 + Math.abs(i - (n - 1) / 2) * 30 * f + lift}px) rotate(${ang + (1 - k) * 30}deg) scale(${0.9 + 0.1 * k})`); c.style.zIndex = 10 - Math.abs(i - (n - 1) / 2) | 0; kenburns(c, lt, dur, 1.1, 1); });
      if (chip) { const t0 = p.chipAt ? at(p.chipAt) : 1.4; const s = SS.stamp(lt, t0); op(chip, s.op); tf(chip, `translate(-50%,0) scale(${lt < t0 ? 0 : s.s}) rotate(${s.rot}deg)`); chip.style.zIndex = 20; }
    };
  },
  // 3D app window: community post + reply from Andrew (photo avatar)
  chat3D(root, p, at) {
    const C = el(root, 'left:430px;top:150px', card(1060, 720, `
      ${navbar("Community", 0.9)}
      <div data-q style="position:absolute;left:40px;top:150px;right:40px;display:flex;gap:22px">${avatar(84, null, 'JM', GR[1])}<div style="flex:1"><div style="font:800 28px ID">Jordan M.</div><div style="margin-top:12px;background:#F4F2FB;border-radius:20px;padding:22px 26px;font:500 30px ID;line-height:1.35;color:#2b2e38">${p.q}</div></div></div>
      <div data-a style="position:absolute;left:150px;top:${p.aTop || 420}px;right:40px;display:flex;gap:22px">${avatar(84, 'pfp')}<div style="flex:1"><div style="font:800 28px ID">Andrew George <span style="font:600 20px ID;color:#fff;background:${VIO};padding:4px 12px;border-radius:999px;margin-left:8px">Founder</span></div><div data-b style="margin-top:12px;background:${VIO};border-radius:20px;padding:22px 26px;font:500 30px ID;line-height:1.35;color:#fff;min-height:84px"></div></div></div>
      <div data-team style="position:absolute;left:40px;bottom:34px;display:flex;align-items:center;gap:-10px">${[0, 1, 2].map(i => `<div style="margin-left:${i ? -18 : 0}px">${avatar(64, null, ['SR', 'KT', 'DM'][i], GR[i + 2])}</div>`).join('')}<span style="margin-left:18px;font:700 24px ID;color:#6B6F7B">+ the team</span></div>`));
    const ping = el(root, `left:1430px;top:120px;width:84px;height:84px;border-radius:50%;background:#F04438;color:#fff;font:800 38px ID;display:grid;place-items:center;box-shadow:0 14px 30px rgba(240,68,56,.4)`, '1');
    const q = C.querySelector('[data-q]'), a = C.querySelector('[data-a]'), b = C.querySelector('[data-b]'), team = C.querySelector('[data-team]');
    const ta = p.aAt ? at(p.aAt) : 1.2, tt = p.teamAt ? at(p.teamAt) : ta + 1;
    return lt => {
      const cam = SS.keynoteCam(lt + 0.0, 0.0); const g = sp(lt, 9, 0.8); tf(C, `perspective(2400px) rotateY(${lerp(-24, -8, g) + Math.sin(lt * 0.6) * 2}deg) rotateX(${lerp(14, 5, g)}deg) translateY(${(1 - g) * 120}px) scale(${lerp(0.85, 1, g)})`); op(C, cl(lt / 0.15));
      riseIn(q, lt, 0.3, 30); riseIn(a, lt, ta - 0.4, 30);
      const typ = Math.max(0, Math.floor((lt - ta) * 42)); b.innerHTML = lt < ta ? `<span style="letter-spacing:6px;opacity:${0.5 + 0.5 * Math.sin(lt * 12)}">•••</span>` : p.a.slice(0, typ);
      riseIn(team, lt, tt, 20); popIn(ping, lt, ta + 0.1);
    };
  },
  // course tiles flip in on a tilted 3D grid, progress ring, pin drops
  classroom(root, p, at) {
    const names = p.items; const NB = el(root, 'left:260px;top:40px;width:1400px;border-radius:22px;overflow:hidden;box-shadow:0 20px 50px rgba(20,20,40,.1)', navbar('Classroom'));
    const G = el(root, 'left:260px;top:250px;width:1400px;height:760px;transform-style:preserve-3d');
    const tiles = names.map((n, i) => el(G, `left:${(i % 3) * 470}px;top:${Math.floor(i / 3) * 350}px;width:440px;height:330px;border-radius:20px;overflow:hidden;background:#fff;border:1px solid #E6E4EF;box-shadow:0 26px 60px rgba(20,20,40,.12)`,
      `<img src="${IMG('course' + n[1])}" style="width:440px;height:236px;object-fit:cover;display:block"><div style="padding:14px 20px;font:800 26px ID;letter-spacing:-.01em;white-space:nowrap">${COURSES[n[1]]}</div><div style="position:absolute;left:20px;right:20px;bottom:16px;height:14px;border-radius:7px;background:#E5E5E5"><i data-bar style="display:block;height:100%;width:0;border-radius:7px;background:${VIO}"></i></div>`));
    const pin = el(root, `left:0;top:0;color:${VIO}`, `<div style="filter:drop-shadow(0 10px 20px rgba(123,92,255,.5))">${icon('pin', 110, VIO, 2.4)}</div>`);
    return lt => {
      riseIn(NB, lt, 0, -40); const g = sp(lt, 8, 0.85); tf(G, `perspective(2600px) rotateX(${lerp(26, 8, g)}deg) translateY(${(1 - g) * 100}px)`);
      tiles.forEach((d, i) => { const t0 = names[i][2] ? Math.min(at(names[i][2]), 0.3 + i * 0.12) : 0.2 + i * 0.12; const k = sp(lt - t0, 12, 0.6); op(d, cl((lt - t0) / 0.1)); tf(d, `rotateY(${(1 - k) * 90}deg) translateZ(${(1 - k) * 120}px)`); d.querySelector('[data-bar]').style.width = 100 * SS.barFill(lt, t0 + 0.4) * (0.2 + 0.6 * ((i * 37) % 10) / 10) + '%'; });
      if (p.pinAt) { const tp = at(p.pinAt); const k = sp(lt - tp, 13, 0.45); op(pin, cl((lt - tp) / 0.1)); tf(pin, `translate(${260 + 470 * (p.pinTile % 3) + 165}px,${lerp(0, 160 + Math.floor(p.pinTile / 3) * 350, k)}px)`); } else op(pin, 0);
    };
  },
  // vault unlocks, software windows rise (dark)
  vault(root, p, at) {
    const V = el(root, 'left:710px;top:330px', `<div style="width:500px;height:440px;border-radius:40px;background:linear-gradient(160deg,#1E1E2A,#121219);border:2px solid #2E2E40;box-shadow:0 0 0 1px rgba(155,131,255,.2),0 40px 120px rgba(123,92,255,.35);position:relative"><div data-door style="position:absolute;inset:0;border-radius:40px;background:linear-gradient(160deg,#2A2A3A,#17171F);display:grid;place-items:center;transform-origin:left center"><div style="width:170px;height:170px;border-radius:50%;border:10px solid ${VIO2};display:grid;place-items:center"><div data-wheel style="width:90px;height:12px;background:${VIO2};border-radius:6px"></div></div></div></div>`);
    const sh = el(root, 'left:880px;top:180px', svg(160, 170, `<path d="M20 170 V70 a60 60 0 0 1 120 0 V170" fill="none" stroke="${VIO2}" stroke-width="22" stroke-linecap="round"/>`));
    const wins = (p.items || ['New software', 'New system', 'Early access']).map((n, i) => el(root, `left:0;top:0;width:360px;height:220px;border-radius:22px;background:#15151D;border:1px solid #2E2E40;box-shadow:0 30px 80px rgba(0,0,0,.5),0 0 60px rgba(123,92,255,.25);overflow:hidden`, `<div style="height:44px;border-bottom:1px solid #2A2A38;display:flex;gap:8px;align-items:center;padding:0 16px">${'<i style="width:10px;height:10px;border-radius:50%;background:#3a3a4c;display:block"></i>'.repeat(3)}</div><div style="padding:22px;display:flex;gap:16px;align-items:center;color:#fff;font:800 30px ID">${icon(['box', 'bolt', 'star'][i], 44, VIO2)}${n}</div><div style="margin:0 22px;height:12px;border-radius:6px;background:#262634"><i style="display:block;height:100%;width:${60 + i * 15}%;background:${VIO};border-radius:6px"></i></div>`));
    const tu = at(p.unlockAt);
    return lt => {
      riseIn(V, lt, 0, 60); const u = sp(lt - tu, 12, 0.5); tf(sh, `translateY(${-u * 60}px) rotate(${-u * 18}deg)`); sh.style.transformOrigin = '140px 170px'; op(sh, cl(lt / 0.2) * (1 - cl((lt - tu - 0.8) / 0.3)));
      V.querySelector('[data-wheel]').style.transform = `rotate(${E3((lt - tu + 0.4) / 0.6) * 270}deg)`;
      const d = E3((lt - tu - 0.35) / 0.6); V.querySelector('[data-door]').style.transform = `perspective(1200px) rotateY(${-d * 105}deg)`;
      wins.forEach((w, i) => { const t0 = tu + 0.7 + i * (p.gap || 0.45); const k = sp(lt - t0, 11, 0.6); const X = [380, 780, 1180][i], Y = [210, 120, 210][i]; op(w, cl((lt - t0) / 0.12)); tf(w, `translate(${lerp(785, X, k)}px,${lerp(470, Y, k) + Math.sin(lt * 1.4 + i) * 8}px) scale(${lerp(0.3, 1, k)}) rotate(${(1 - k) * (i - 1) * 20}deg)`); });
    };
  },
  // three line-drawn industry icons + counter
  industries(root, p, at) {
    const items = p.items; const boxes = items.map((it, i) => el(root, `left:${330 + i * 450}px;top:300px;width:360px;text-align:center`, `<div style="width:300px;height:300px;margin:0 auto;border-radius:50%;background:#fff;box-shadow:0 30px 70px rgba(20,20,40,.12);display:grid;place-items:center;position:relative"><svg width="160" height="160" viewBox="0 0 24 24" fill="none" stroke="${VIO}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">${IC[it.icon].replace(/<(path|rect|circle)/g, '<$1 data-s')}</svg><svg width="300" height="300" style="position:absolute;inset:0"><circle data-ring cx="150" cy="150" r="140" fill="none" stroke="${VIO}" stroke-width="6" stroke-linecap="round" transform="rotate(-90 150 150)"/></svg></div><div style="margin-top:30px;font:800 34px ID;letter-spacing:-.02em;color:${INK}">${it.label}</div>`));
    const cnt = el(root, `left:0;right:0;top:110px;text-align:center;font:800 110px ID;letter-spacing:-.05em;color:${VIO}`, '0');
    return lt => {
      const tc = Math.min(p.countAt ? at(p.countAt) : 0.2, 0.2); op(cnt, cl((lt - tc) / 0.2)); cnt.textContent = Math.round(1000 * E3((lt - tc) / 1.6)).toLocaleString('en-US') + (lt - tc > 1.6 ? '+' : '');
      boxes.forEach((b, i) => { const t0 = Math.min(at(items[i].at) - 0.15, 0.25 + i * 0.35); popIn(b.firstChild, lt, t0); riseIn(b.lastChild, lt, t0 + 0.15, 20); b.querySelectorAll('[data-s]').forEach(s => { if (!s.getTotalLength) return; drawPath(s, E3((lt - t0) / 0.8)); }); drawPath(b.querySelector('[data-ring]'), E3((lt - t0 - 0.2) / 0.9)); });
    };
  },
  // needle gauges
  gauges(root, p, at) {
    const items = p.items; const G = items.map((it, i) => el(root, `left:${200 + i * 540}px;top:330px;width:480px;text-align:center`, svg(480, 280, `<path d="M40 260 A200 200 0 0 1 440 260" fill="none" stroke="#EEECF4" stroke-width="34" stroke-linecap="round"/><path data-arc d="M40 260 A200 200 0 0 1 440 260" fill="none" stroke="${it.dir === 'down' ? '#B9A8FF' : VIO}" stroke-width="34" stroke-linecap="round"/><g data-nd transform="rotate(0 240 260)"><line x1="240" y1="260" x2="240" y2="90" stroke="${INK}" stroke-width="10" stroke-linecap="round"/></g><circle cx="240" cy="260" r="22" fill="${INK}"/>`) + `<div style="margin-top:26px;font:800 40px ID;letter-spacing:-.02em">${it.label} <span style="color:${VIO}">${it.dir === 'down' ? '↓' : '↑'}</span></div>`));
    return lt => G.forEach((g, i) => { const it = items[i], t0 = at(it.at) - 0.2; riseIn(g, lt, Math.min(0.1 + i * 0.12, t0), 40); const from = it.dir === 'down' ? 0.88 : 0.15, to = it.dir === 'down' ? 0.12 : 0.9; const k = lerp(from, to, SS.spring(lt - t0, 9, 0.35)); g.querySelector('[data-nd]').setAttribute('transform', `rotate(${(k - 0.5) * 180} 240 260)`); drawPath(g.querySelector('[data-arc]'), k); });
  },
  // four pillars dock into a hub
  hub(root, p, at) {
    const P4 = [['chat', 'Me'], ['play', 'Training'], ['video', 'Calls'], ['box', 'Software']];
    const ring = el(root, 'left:0;top:0', svg(1920, 1080, `<circle data-c cx="960" cy="500" r="290" fill="none" stroke="${VIO}" stroke-width="4" stroke-dasharray="4 14"/>` + P4.map((_, i) => `<path data-l="${i}" d="M960 500 L${960 + Math.cos(-Math.PI / 2 + i * Math.PI / 2 + Math.PI / 4) * 290} ${500 + Math.sin(-Math.PI / 2 + i * Math.PI / 2 + Math.PI / 4) * 290}" stroke="${VIO}" stroke-width="4"/>`).join('')));
    const core = el(root, 'left:830px;top:370px', p.center ? avatar(260, p.center) : `<div style="width:260px;height:260px;border-radius:50%;background:${INK};display:grid;place-items:center;color:#fff">${icon('home', 110, '#fff', 1.8)}</div>`);
    const sat = P4.map((q, i) => el(root, 'left:0;top:0;width:210px;text-align:center', `<div style="width:170px;height:170px;margin:0 auto;border-radius:44px;background:${i % 2 ? '#fff' : VIO};color:${i % 2 ? VIO : '#fff'};display:grid;place-items:center;box-shadow:0 26px 60px rgba(20,20,40,.16)">${icon(q[0], 80, 'currentColor', 1.8)}</div><div style="margin-top:16px;font:800 30px ID">${q[1]}</div>`));
    return lt => {
      popIn(core, lt, 0.05); const rc = ring.querySelector('[data-c]'); drawPath(rc, E3((lt - 0.1) / 0.8)); ring.querySelector('svg').style.transform = 'none';
      sat.forEach((s, i) => { const t0 = p.dock ? at(p.dock[i]) - 0.1 : 0.4 + i * 0.25; const a = -Math.PI / 2 + i * Math.PI / 2 + Math.PI / 4; const k = sp(lt - t0, 10, 0.62); const r = lerp(900, 330, k); const aa = a - (1 - k) * 1.2; op(s, cl((lt - t0) / 0.1)); tf(s, `translate(${960 + Math.cos(aa) * r - 105}px,${500 + Math.sin(aa) * r * 0.95 - 100}px) scale(${0.6 + 0.4 * k})`); drawPath(ring.querySelector(`[data-l="${i}"]`), E3((lt - t0 - 0.3) / 0.4)); });
    };
  },
  // brand wordmark build (dark)
  brand(root, p, at) {
    const dot = el(root, `left:960px;top:470px;width:40px;height:40px;border-radius:50%;background:${VIO};box-shadow:0 0 80px ${VIO}`);
    const l1 = el(root, 'left:0;right:0;top:360px;display:flex;justify-content:center', word('SaaS and AI', 150, '#fff')), l2 = el(root, 'left:0;right:0;top:520px;display:flex;justify-content:center', word('Business Mastery.', 150, VIO2));
    const parts = [...Array(26)].map((_, i) => el(root, `left:960px;top:490px;width:${6 + i % 4 * 3}px;height:${6 + i % 4 * 3}px;border-radius:50%;background:${i % 3 ? VIO2 : '#fff'}`));
    return lt => {
      const k = E3(lt / 0.5); tf(dot, `translate(-50%,-50%) scale(${lt < 0.5 ? 1 + 8 * k : Math.max(0, 9 - (lt - 0.5) * 30)})`); op(dot, lt < 0.8 ? 1 : 0);
      letters(l1, lt, 0.55, 0.03); letters(l2, lt, 0.8, 0.03);
      parts.forEach((d, i) => { const a = i * 2.4, v = 300 + (i * 53 % 400); const tt = pos(lt - 0.5); op(d, tt > 0 ? cl(1 - tt / 1.6) : 0); tf(d, `translate(${Math.cos(a) * v * E3(tt / 1.2)}px,${Math.sin(a) * v * 0.6 * E3(tt / 1.2) + tt * tt * 40}px)`); });
    };
  },
  // huge outlined numeral fills with violet, 1-3 word label, side photo/icon
  bigNum(root, p, at) {
    const dark = p.dark; const N = el(root, 'left:150px;top:90px', `<div style="position:relative;font:800 820px ID;letter-spacing:-.07em;line-height:1"><span style="color:transparent;-webkit-text-stroke:5px ${dark ? '#3a3a52' : '#D9D2FA'}">${p.n}</span><span data-fill style="position:absolute;left:0;top:0;color:${dark ? VIO2 : VIO}">${p.n}</span></div>`);
    const L = el(root, 'left:820px;top:330px', word(p.label, 140, dark ? '#fff' : INK)); const L2 = p.label2 ? el(root, 'left:820px;top:480px', word(p.label2, 140, dark ? VIO2 : VIO)) : null;
    const S = p.img ? el(root, 'left:1420px;top:620px', avatar(260, p.img)) : (p.icon ? el(root, `left:1420px;top:640px;width:220px;height:220px;border-radius:60px;background:${dark ? '#1C1C26' : '#fff'};color:${VIO};display:grid;place-items:center;box-shadow:0 30px 70px rgba(20,20,40,.18)`, icon(p.icon, 110, dark ? VIO2 : VIO, 1.8)) : null);
    return lt => {
      const k = sp(lt, 9, 0.7); tf(N, `translateX(${(1 - k) * -500}px) skewX(${(1 - k) * 12}deg)`); op(N, cl(lt / 0.1));
      const f = E3((lt - 0.25) / 0.7); N.querySelector('[data-fill]').style.clipPath = `inset(${(1 - f) * 100}% 0 0 0)`;
      letters(L, lt, 0.35, 0.03); if (L2) letters(L2, lt, 0.5, 0.03); if (S) popIn(S, lt, 0.7, `translateY(${Math.sin(lt * 2) * 8}px)`);
    };
  },
  // DM: message types, send, paper plane flies to Andrew
  dm(root, p, at) {
    const B = el(root, 'left:240px;top:300px', card(760, 420, `<div style="padding:30px 36px;font:800 32px ID;display:flex;align-items:center;gap:16px">${avatar(64, 'pfp')}Message Andrew</div><div data-t style="margin:0 36px;min-height:150px;border:2px solid #E6E4EF;border-radius:20px;padding:22px;font:500 32px ID;line-height:1.35;color:#2b2e38"></div><div data-s style="position:absolute;right:36px;bottom:30px;padding:16px 34px;border-radius:999px;background:${VIO};color:#fff;font:700 28px ID">Send</div>`));
    const pl = el(root, `left:0;top:0;color:${VIO}`, icon('plane', 90, VIO, 2));
    const A = el(root, 'left:1360px;top:330px', avatar(260, 'pfp')); const badge = el(root, `left:1580px;top:320px;width:80px;height:80px;border-radius:50%;background:#F04438;color:#fff;font:800 36px ID;display:grid;place-items:center`, '1');
    const txt = p.text, ts = 0.5, tsend = ts + txt.length / 40 + 0.25;
    return lt => {
      riseIn(B, lt, 0, 60); B.querySelector('[data-t]').innerHTML = txt.slice(0, Math.max(0, Math.floor((lt - ts) * 40))) + (lt < tsend ? `<span style="display:inline-block;width:3px;height:32px;background:${VIO};vertical-align:-5px"></span>` : '');
      const s = B.querySelector('[data-s]'); s.style.transform = `scale(${SS.press(lt, tsend)})`;
      const f = E3((lt - tsend) / 0.9); op(pl, lt > tsend && f < 1 ? 1 : 0); const x = lerp(900, 1440, f), y = lerp(640, 420, f) - Math.sin(f * Math.PI) * 220; tf(pl, `translate(${x}px,${y}px) rotate(${-20 + f * 30}deg) scale(${1 - 0.5 * f})`);
      popIn(A, lt, 0.2); popIn(badge, lt, tsend + 0.9);
    };
  },
  // three icon tiles that light on phrases
  trio(root, p, at) {
    const T3 = p.items.map((it, i) => el(root, `left:${270 + i * 480}px;top:280px;width:420px;height:460px;border-radius:40px;background:#fff;border:1px solid #E6E4EF;box-shadow:0 30px 70px rgba(20,20,40,.1);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px`, `<div data-i style="width:200px;height:200px;border-radius:56px;background:#F1EEFF;color:${VIO};display:grid;place-items:center">${icon(it.icon, 110, 'currentColor', 1.6)}</div><div style="font:800 44px ID;letter-spacing:-.03em">${it.label}</div>`));
    return lt => T3.forEach((d, i) => { const t0 = at(p.items[i].at) - 0.2; const k = sp(lt - Math.min(t0, 0.15 + i * 0.12), 12, 0.6); op(d, cl(k * 3)); const on = cl((lt - t0) / 0.25); tf(d, `translateY(${(1 - k) * 160 - on * 26}px) rotate(${(1 - k) * (i - 1) * 8}deg)`); d.style.boxShadow = `0 ${30 + on * 20}px ${70 + on * 30}px rgba(123,92,255,${0.1 + on * 0.3})`; const ic = d.querySelector('[data-i]'); ic.style.background = on > 0.5 ? VIO : '#F1EEFF'; ic.style.color = on > 0.5 ? '#fff' : VIO; tf(ic, `scale(${1 + 0.12 * Math.sin(Math.min(1, on) * Math.PI)}) rotate(${on * 360 * (i % 2 ? 1 : -1) * 0}deg)`); });
  },
  // clock spinning through days, reply envelope arrives
  clock(root, p, at) {
    const C = el(root, 'left:610px;top:200px', svg(700, 700, `<circle cx="350" cy="350" r="300" fill="#fff" stroke="#E6E4EF" stroke-width="3"/>${[...Array(12)].map((_, i) => `<line x1="350" y1="70" x2="350" y2="${i % 3 ? 95 : 115}" stroke="${i % 3 ? '#D9DDE3' : INK}" stroke-width="${i % 3 ? 4 : 8}" stroke-linecap="round" transform="rotate(${i * 30} 350 350)"/>`).join('')}<circle data-arc cx="350" cy="350" r="300" fill="none" stroke="${VIO}" stroke-width="12" stroke-linecap="round" transform="rotate(-90 350 350)"/><line data-h x1="350" y1="350" x2="350" y2="200" stroke="${INK}" stroke-width="16" stroke-linecap="round"/><line data-m x1="350" y1="350" x2="350" y2="130" stroke="${VIO}" stroke-width="10" stroke-linecap="round"/><circle cx="350" cy="350" r="20" fill="${INK}"/>`, 'filter:drop-shadow(0 30px 60px rgba(20,20,40,.12))'));
    const days = [1, 2].map(i => el(root, `left:${1360}px;top:${330 + i * 0}px;padding:18px 30px;border-radius:999px;background:${i === 2 ? VIO : INK};color:#fff;font:800 40px ID`, `Day ${i}`));
    const env = el(root, `left:1350px;top:560px;width:200px;height:200px;border-radius:50px;background:#fff;box-shadow:0 30px 70px rgba(20,20,40,.18);display:grid;place-items:center;color:${VIO}`, icon('mail', 110, VIO, 1.8) + `<div style="position:absolute;right:-14px;top:-14px;width:70px;height:70px;border-radius:50%;background:#12B76A;display:grid;place-items:center">${icon('check', 40, '#fff', 3)}</div>`);
    return (lt, dur) => {
      popIn(C, lt, 0); const sp2 = E3(lt / Math.max(1.5, dur - 0.5)) * 48; C.querySelector('[data-h]').setAttribute('transform', `rotate(${sp2 * 30 / 12 * 12} 350 350)`); C.querySelector('[data-m]').setAttribute('transform', `rotate(${sp2 * 360} 350 350)`); drawPath(C.querySelector('[data-arc]'), (sp2 % 24) / 24);
      days.forEach((d, i) => { const t0 = 0.5 + i * 0.9; const k = sp(lt - t0, 13, 0.55); op(d, cl((lt - t0) / 0.1) * (i === 0 ? 1 - cl((lt - 1.4) / 0.15) : 1)); tf(d, `translateY(${(1 - k) * 40}px) scale(${k})`); });
      popIn(env, lt, Math.max(1.6, dur - 1.6));
    };
  },
  // question builder: blocks snap onto a card, then answered by avatars
  composer(root, p, at) {
    const C = el(root, 'left:560px;top:150px', card(800, 760, `<div style="padding:34px 40px;font:800 34px ID;display:flex;gap:16px;align-items:center">${icon('search', 40, VIO, 2.2)}Your question</div>`));
    const blocks = p.blocks.map((b, i) => el(root, `left:0;top:0;width:720px;height:120px;border-radius:24px;background:${['#F1EEFF', '#E8F2FF', '#FFF3E6'][i]};display:flex;align-items:center;gap:22px;padding:0 30px;font:800 36px ID;color:${INK}`, `<span style="width:66px;height:66px;border-radius:20px;background:#fff;display:grid;place-items:center;color:${VIO}">${icon(b.icon, 38, VIO, 2)}</span>${b.label}`));
    const ans = el(root, `left:1420px;top:640px;display:flex;align-items:center;gap:0`, [0, 1, 2].map(i => `<div style="margin-left:${i ? -24 : 0}px">${avatar(96, i === 0 ? 'pfp' : null, ['', 'KT', 'RS'][i], GR[i + 1])}</div>`).join('') + `<div style="margin-left:18px;padding:16px 26px;border-radius:999px;background:#12B76A;color:#fff;font:800 30px ID;display:flex;gap:10px;align-items:center">${icon('check', 32, '#fff', 3)}Answered</div>`);
    return lt => {
      riseIn(C, lt, 0, 60); blocks.forEach((b, i) => { const t0 = at(p.blocks[i].at) - 0.15; const k = sp(lt - t0, 12, 0.6); op(b, cl((lt - t0) / 0.08)); tf(b, `translate(${lerp(i % 2 ? 1700 : -700, 600, k)}px,${270 + i * 150}px) rotate(${(1 - k) * (i % 2 ? 12 : -12)}deg)`); });
      riseIn(ans, lt, at(p.ansAt), 40);
    };
  },
  // conveyor of course cards
  courses(root, p, at) {
    const cs = p.items.map((n, i) => el(root, 'left:0;top:300px;width:560px;height:420px;border-radius:24px;overflow:hidden;background:#fff;border:1px solid #E6E4EF;box-shadow:0 30px 70px rgba(20,20,40,.14)', `<img src="${IMG('course' + n.c)}" style="width:560px;height:301px;object-fit:cover;display:block"><div style="padding:18px 24px;font:800 32px ID;letter-spacing:-.02em;white-space:nowrap">${COURSES[n.c]}</div><div style="position:absolute;left:24px;right:24px;bottom:20px;height:14px;border-radius:7px;background:#E5E5E5"></div>`));
    return (lt, dur) => cs.forEach((c, i) => { const t0 = Math.min(at(p.items[i].at) - 0.15, 0.15 + i * 0.6); const k = sp(lt - t0, 12, 0.6); const base = 100 + i * 600 - E3(lt / dur) * Math.max(0, cs.length * 600 - 1750); op(c, cl((lt - t0) / 0.1)); const hl = lt > at(p.items[i].at) - 0.1; tf(c, `translate(${base}px,${(1 - k) * 260 + Math.sin(lt * 1.5 + i) * 6 - (hl ? 20 : 0)}px) rotate(${(1 - k) * -14}deg) scale(${0.85 + 0.15 * k})`); c.style.boxShadow = hl ? `0 0 0 6px ${VIO},0 30px 70px rgba(123,92,255,.3)` : '0 30px 70px rgba(20,20,40,.14)'; });
  },
  // price tag swings, gets struck, "Included" stamp
  priceStrike(root, p, at) {
    const yt = el(root, `left:260px;top:280px;width:300px;height:220px;border-radius:40px;background:#FF0033;display:grid;place-items:center;box-shadow:0 30px 70px rgba(255,0,51,.3)`, icon('play', 140, '#fff', 1.6));
    const pc = el(root, `left:260px;top:560px;width:300px;height:220px;border-radius:40px;background:${INK};display:grid;place-items:center`, icon('star', 120, '#fff', 1.6));
    const tag = el(root, 'left:820px;top:140px', `<div style="position:relative;width:640px;height:420px"><div style="position:absolute;left:300px;top:0;width:4px;height:120px;background:#C9C4DA"></div><div style="position:absolute;left:40px;top:110px;width:560px;height:300px;border-radius:40px;background:#fff;box-shadow:0 40px 90px rgba(20,20,40,.16);display:grid;place-items:center"><div style="font:800 150px ID;letter-spacing:-.05em;color:${INK};position:relative">$1,000s<i data-x style="position:absolute;left:-4%;top:52%;height:18px;width:0;background:#F04438;border-radius:9px;transform:rotate(-6deg)"></i></div></div></div>`);
    const st = el(root, `left:1150px;top:700px;padding:26px 50px;border-radius:24px;border:8px solid #12B76A;color:#12B76A;font:800 72px ID;letter-spacing:-.03em;background:#fff`, 'Included');
    const tx = at(p.strikeAt), ts = at(p.stampAt);
    return lt => {
      popIn(yt, lt, at(p.ytAt) - 0.15); popIn(pc, lt, at(p.pcAt) - 0.15);
      const sw = Math.sin(lt * 3) * 10 * Math.exp(-lt * 0.6); const k = sp(lt - 0.1, 9, 0.5); op(tag, cl(lt / 0.1)); tf(tag, `translateY(${(1 - k) * -500}px) rotate(${sw}deg)`); tag.style.transformOrigin = '302px 0';
      tag.querySelector('[data-x]').style.width = 108 * E3((lt - tx) / 0.35) + '%';
      const s = SS.stamp(lt, ts); op(st, s.op); tf(st, `scale(${lt < ts ? 0 : s.s}) rotate(${-8 + s.rot}deg)`);
    };
  },
  // browser + AI side panel answering
  aiPrompt(root, p, at) {
    const B = el(root, 'left:200px;top:120px', card(1520, 780, `<div style="height:70px;background:#F4F3F8;display:flex;align-items:center;gap:12px;padding:0 24px">${'<i style="width:14px;height:14px;border-radius:50%;background:#D9D7E3;display:block"></i>'.repeat(3)}<div style="margin-left:24px;width:520px;height:40px;border-radius:20px;background:#fff;font:500 20px ID;color:#8a8d99;display:flex;align-items:center;padding:0 20px">skool.com / classroom</div></div><div style="width:960px">${navbar('Classroom', 0.85)}</div>
      <div style="position:absolute;left:30px;top:230px;width:880px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px">${[...Array(6)].map((_, i) => `<div data-c style="height:158px;border-radius:14px;overflow:hidden;opacity:.9"><img src="${IMG('course' + i)}" style="width:100%;height:100%;object-fit:cover"></div>`).join('')}</div>
      <div data-side style="position:absolute;right:0;top:70px;bottom:0;width:560px;border-left:1px solid #EEECF4;background:#FCFBFF;padding:30px"><div style="font:800 28px ID;display:flex;gap:12px;align-items:center;color:${VIO}">${icon('bolt', 34, VIO, 2.2)}${p.tag}</div><div data-q style="margin-top:24px;background:#fff;border:2px solid #E6E4EF;border-radius:18px;padding:20px;font:500 26px ID;line-height:1.35;min-height:150px"></div><div data-a style="margin-top:22px"></div></div>`));
    const lines = p.answer; const ts = 0.6, tq = ts + p.text.length / 38;
    return lt => {
      const g = sp(lt, 9, 0.8); tf(B, `perspective(2600px) rotateX(${(1 - g) * 18}deg) translateY(${(1 - g) * 120}px) scale(${lerp(0.9, 1, g)})`); op(B, cl(lt / 0.15));
      B.querySelector('[data-q]').innerHTML = p.text.slice(0, Math.max(0, Math.floor((lt - ts) * 38)));
      const A = B.querySelector('[data-a]'); A.innerHTML = lines.map((l, i) => { const t0 = tq + 0.3 + i * 0.45; const k = E3((lt - t0) / 0.4); return `<div style="margin-top:14px;padding:16px 20px;border-radius:14px;background:${i === 0 ? VIO : '#F1EEFF'};color:${i === 0 ? '#fff' : INK};font:700 24px ID;opacity:${k};transform:translateX(${(1 - k) * 40}px)">${l}</div>`; }).join('') + (lt > tq && lt < tq + 0.3 ? `<div style="margin-top:14px;height:24px;width:70%;border-radius:12px;background:linear-gradient(90deg,#EEE,#DDD,#EEE);background-size:200%;background-position:${(lt * 200) % 200}% 0"></div>` : '');
      B.querySelectorAll('[data-c]').forEach((c, i) => { const hl = lt > tq + 0.3 && (i === 1 || i === 0); c.style.outline = hl ? `6px solid ${VIO}` : 'none'; c.style.opacity = lt > tq + 0.3 ? (hl ? 1 : 0.35) : 0.9; });
    };
  },
  // spotlight finds one tile
  spotlight(root, p, at) {
    const tiles = [...Array(12)].map((_, i) => el(root, `left:${300 + (i % 4) * 340}px;top:${170 + Math.floor(i / 4) * 250}px;width:300px;height:210px;border-radius:24px;background:${GR[i % 6]}`, ''));
    const dim = el(root, 'left:0;top:0;width:1920px;height:1080px;pointer-events:none');
    const tf0 = at(p.findAt), target = 5;
    return lt => {
      tiles.forEach((d, i) => popIn(d, lt, 0.05 + i * 0.04));
      const k = E3((lt - tf0 + 0.2) / 0.6); const tx = 300 + (target % 4) * 340 + 150, ty = 170 + Math.floor(target / 4) * 250 + 105; const wx = 960 + Math.cos(lt * 1.7) * 500, wy = 540 + Math.sin(lt * 2.3) * 250;
      const x = lerp(wx, tx, k), y = lerp(wy, ty, k), r = lerp(260, 230, k);
      dim.style.background = `radial-gradient(circle ${r}px at ${x}px ${y}px, transparent 0, transparent ${r - 10}px, rgba(246,245,242,.86) ${r + 30}px)`; op(dim, cl((lt - 0.4) / 0.3));
      const T = tiles[target]; const on = cl((lt - tf0) / 0.3); T.style.zIndex = 5; T.style.transform = `scale(${1 + 0.25 * sp(lt - tf0, 12, 0.5) * (lt > tf0)})`; T.style.boxShadow = on ? `0 0 0 8px ${VIO},0 30px 80px rgba(123,92,255,.5)` : 'none';
    };
  },
  // weekly calendar with recurring events; Friday highlight
  calendar(root, p, at) {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const C = el(root, 'left:260px;top:140px', card(1400, 800, `${navbar('Calendar')}<div style="padding:18px 40px;display:flex;justify-content:flex-end"><div style="font:700 24px ID;color:#fff;background:${VIO};padding:10px 20px;border-radius:999px">Every week</div></div><div style="display:grid;grid-template-columns:repeat(5,1fr);gap:18px;padding:0 40px">${days.map(d => `<div data-d style="height:480px;border-radius:22px;background:#F7F6FB;position:relative"><div style="padding:18px;font:700 26px ID;color:#6B6F7B">${d}</div></div>`).join('')}</div>`));
    const D = C.querySelectorAll('[data-d]'); const evs = p.events.map(e => { const x = document.createElement('div'); x.style.cssText = `position:absolute;left:12px;right:12px;top:${e.top || 80}px;height:${e.h || 130}px;border-radius:16px;padding:16px;font:800 24px ID;line-height:1.15;color:${e.alt ? VIO : '#fff'};background:${e.alt ? '#ECE8FF' : VIO}`; x.innerHTML = (e.live ? `<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#F04438;margin-right:8px" data-live></span>` : '') + e.t; D[e.d].appendChild(x); return x; });
    return lt => {
      riseIn(C, lt, 0, 70); evs.forEach((x, i) => { const e = p.events[i]; const t0 = e.at ? at(e.at) - 0.1 : 0.4 + i * 0.12; const k = sp(lt - t0, 13, 0.45); op(x, cl((lt - t0) / 0.08)); tf(x, `translateY(${(1 - k) * -120}px) scale(${0.8 + 0.2 * k})`); const lv = x.querySelector('[data-live]'); if (lv) lv.style.opacity = 0.4 + 0.6 * Math.abs(Math.sin(lt * 4)); });
      if (p.hl !== undefined) { const th = at(p.hlAt); const on = cl((lt - th) / 0.25); D[p.hl].style.boxShadow = `inset 0 0 0 ${on * 6}px ${VIO}`; D[p.hl].style.background = on ? `rgba(123,92,255,${0.08 * on})` : '#F7F6FB'; tf(D[p.hl], `scale(${1 + 0.04 * sp(lt - th, 12, 0.4) * (lt > th)})`); }
    };
  },
  // live video call grid with Andrew speaking
  callGrid(root, p, at) {
    const C = el(root, 'left:240px;top:120px', card(1440, 800, `<div style="height:74px;display:flex;align-items:center;justify-content:space-between;padding:0 30px;border-bottom:1px solid #EEECF4"><div style="font:800 28px ID">${p.title || 'Coaching call'}</div><div style="display:flex;gap:10px;align-items:center;font:800 24px ID;color:#fff;background:#F04438;padding:8px 18px;border-radius:999px"><i data-lv style="width:12px;height:12px;border-radius:50%;background:#fff;display:block"></i>LIVE</div></div>
      <div style="display:grid;grid-template-columns:2fr 1fr;grid-template-rows:1fr 1fr;gap:16px;padding:20px;height:700px"><div data-main style="grid-row:span 2;border-radius:20px;overflow:hidden;position:relative;box-shadow:0 0 0 0 ${VIO}"><img src="${IMG(p.img || 'hero')}" style="width:100%;height:100%;object-fit:cover;object-position:${p.pos || '30% 25%'}" data-kb><div style="position:absolute;left:18px;bottom:18px;background:rgba(20,20,24,.7);color:#fff;font:700 22px ID;padding:8px 14px;border-radius:10px">Andrew</div><div data-wave style="position:absolute;right:20px;bottom:20px;display:flex;gap:5px;align-items:flex-end;height:40px">${'<i style="width:7px;background:#fff;border-radius:4px;display:block"></i>'.repeat(6)}</div></div>${[0, 1].map(i => `<div data-o style="border-radius:20px;background:${GR[i + 1]};display:grid;place-items:center">${avatar(140, null, ['KT', 'RS'][i], 'rgba(255,255,255,.25)')}</div>`).join('')}</div>`));
    const chip = p.chip ? el(root, `left:1500px;top:70px;padding:20px 34px;border-radius:999px;background:${INK};color:#fff;font:800 40px ID;display:flex;gap:14px;align-items:center`, icon('cal', 40, VIO2, 2) + p.chip) : null;
    return (lt, dur) => {
      const g = sp(lt, 9, 0.8); tf(C, `perspective(2600px) rotateY(${lerp(16, 4, g)}deg) translateX(${(1 - g) * 200}px)`); op(C, cl(lt / 0.12)); kenburns(C, lt, dur, 1.12, 1.0);
      C.querySelectorAll('[data-wave] i').forEach((b, i) => b.style.height = (10 + 30 * Math.abs(Math.sin(lt * 9 + i * 1.3))) + 'px'); C.querySelector('[data-main]').style.boxShadow = `0 0 0 ${4 + 3 * Math.abs(Math.sin(lt * 5))}px ${VIO}`;
      C.querySelectorAll('[data-o]').forEach((o, i) => popIn(o, lt, 0.4 + i * 0.15)); C.querySelector('[data-lv]').style.opacity = 0.4 + 0.6 * Math.abs(Math.sin(lt * 4));
      if (chip) { const t0 = at(p.chipAt); const s = SS.stamp(lt, t0); op(chip, s.op); tf(chip, `scale(${lt < t0 ? 0 : s.s}) rotate(${s.rot}deg)`); }
    };
  },
  // announcement drops falling into a feed (dark)
  feed(root, p, at) {
    const items = p.items; const F = el(root, 'left:560px;top:120px', `<div style="width:800px;height:820px;border-radius:30px;background:#15151D;border:1px solid #2A2A38;box-shadow:0 40px 120px rgba(0,0,0,.5);position:relative;overflow:hidden"><div style="padding:30px 36px;font:800 34px ID;color:#fff;display:flex;gap:14px;align-items:center">${icon('megaphone', 40, VIO2, 2)}Announcements</div></div>`);
    const rows = items.map((it, i) => el(F.firstChild, `left:36px;right:36px;top:${120 + i * 170}px;height:150px;border-radius:22px;background:${i === 0 ? 'linear-gradient(135deg,#7B5CFF,#5A3FE0)' : '#1E1E2A'};display:flex;align-items:center;gap:24px;padding:0 28px;color:#fff;font:800 32px ID`, `<span style="width:90px;height:90px;border-radius:24px;background:${i === 0 ? 'rgba(255,255,255,.2)' : '#2A2A3A'};display:grid;place-items:center">${icon(it.icon, 50, '#fff', 1.8)}</span>${it.t}${i === 0 ? '<span style="margin-left:auto;font:800 22px ID;background:#fff;color:#5A3FE0;padding:8px 16px;border-radius:999px">NEW</span>' : ''}`));
    const gift = el(root, `left:1420px;top:260px;color:${VIO2}`, icon('gift', 200, VIO2, 1.4));
    return lt => {
      riseIn(F, lt, 0, 60); rows.forEach((r, i) => { const t0 = i === 0 ? at(items[0].at) : 0.25 + i * 0.12; const k = sp(lt - t0, 12, 0.5); op(r, cl((lt - t0) / 0.1)); tf(r, `translateY(${(1 - k) * -220}px) scale(${0.85 + 0.15 * k})`); if (i === 0) r.style.boxShadow = `0 0 ${40 + 20 * Math.sin(lt * 4)}px rgba(123,92,255,.6)`; });
      popIn(gift, lt, at(items[0].at) - 0.3, `rotate(${Math.sin(lt * 3) * 8}deg)`);
    };
  },
  // intro post: lines fill, post press, hearts float
  post(root, p, at) {
    const C = el(root, 'left:520px;top:110px', card(880, 840, `<div style="padding:34px 40px;display:flex;gap:20px;align-items:center">${avatar(90, null, 'You', GR[3])}<div><div style="font:800 34px ID">Your intro post</div><div style="font:600 24px ID;color:#6B6F7B">Introductions</div></div></div><div data-ls style="padding:0 40px"></div><div data-btn style="position:absolute;right:40px;bottom:36px;padding:18px 46px;border-radius:999px;background:${VIO};color:#fff;font:800 32px ID">Post</div>`));
    const LS = C.querySelector('[data-ls]'); const rows = p.lines.map((l, i) => { const d = document.createElement('div'); d.style.cssText = 'display:flex;gap:20px;align-items:center;padding:22px 0;border-top:1px solid #EEECF4;font:800 32px ID'; d.innerHTML = `<span style="width:64px;height:64px;border-radius:18px;background:#F1EEFF;display:grid;place-items:center">${icon(l.icon, 36, VIO, 2)}</span>${l.label}<span data-bar style="margin-left:auto;height:14px;border-radius:7px;background:#E6E4EF;width:0"></span>`; LS.appendChild(d); return d; });
    const hearts = [...Array(9)].map((_, i) => el(root, `left:${1250 + (i % 3) * 50}px;top:820px;color:${i % 2 ? '#F04438' : VIO}`, icon(i % 3 ? 'heart' : 'chat', 54, i % 2 ? '#F04438' : VIO, 2.2)));
    const tb = p.btnAt ? at(p.btnAt) : 99;
    const bar = el(root, 'left:460px;top:440px', composerBar(1000)); const cur = el(root, 'left:0;top:0;z-index:9', '<svg viewBox="0 0 24 24" width="52" height="52"><path d="M4 2l16 9-7 2-3 7z" fill="#fff" stroke="#141418" stroke-width="1.5" stroke-linejoin="round"/></svg>');
    const tcl = 0.9;
    return lt => {
      riseIn(bar, lt, 0, 40); op(bar, cl(lt / 0.15) * (1 - cl((lt - tcl - 0.15) / 0.2))); bar.style.transform += ` scale(${SS.press(lt, tcl)})`;
      const ck = E3((lt - 0.2) / 0.7); op(cur, lt < tcl + 0.4 ? cl(lt / 0.1) : 0); tf(cur, `translate(${lerp(1300, 820, ck)}px,${lerp(800, 470, ck)}px) scale(${SS.cursorSquish(lt, tcl)})`);
      riseIn(C, lt, tcl + 0.15, 60); rows.forEach((r, i) => { const t0 = Math.max(tcl + 0.4 + i * 0.1, p.lines[i].at ? at(p.lines[i].at) - 0.15 : 0.3 + i * 0.25); riseIn(r, lt, t0, 30); r.querySelector('[data-bar]').style.width = 180 * E3((lt - t0 - 0.2) / 0.6) + 'px'; });
      C.querySelector('[data-btn]').style.transform = `scale(${SS.press(lt, tb)})`;
      hearts.forEach((h, i) => { const t0 = tb + 0.2 + i * 0.12; const f = pos(lt - t0); op(h, f > 0 ? cl(1 - f / 1.4) : 0); tf(h, `translate(${Math.sin(f * 3 + i) * 40}px,${-f * 420}px) scale(${0.6 + 0.4 * cl(f * 3)})`); });
    };
  },
  // three big circular steps with progress rings
  steps(root, p, at) {
    const S3 = p.items.map((it, i) => el(root, `left:${250 + i * 500}px;top:250px;width:420px;text-align:center`, `<div style="position:relative;width:340px;height:340px;margin:0 auto"><svg width="340" height="340" style="position:absolute;inset:0"><circle cx="170" cy="170" r="154" fill="#fff" stroke="#EEECF4" stroke-width="14"/><circle data-r cx="170" cy="170" r="154" fill="none" stroke="${VIO}" stroke-width="14" stroke-linecap="round" transform="rotate(-90 170 170)"/></svg><div data-i style="position:absolute;inset:0;display:grid;place-items:center;color:${VIO}">${icon(it.icon, 130, VIO, 1.6)}</div><div data-c style="position:absolute;right:6px;top:6px;width:92px;height:92px;border-radius:50%;background:#12B76A;display:grid;place-items:center">${icon('check', 50, '#fff', 3)}</div></div><div style="margin-top:28px;font:800 42px ID;letter-spacing:-.03em">${it.label}</div>`));
    return lt => S3.forEach((s, i) => { const t0 = at(p.items[i].at) - 0.2; const k = sp(lt - Math.min(t0, 0.1 + i * 0.12), 12, 0.6); op(s, cl(k * 3)); tf(s, `translateY(${(1 - k) * 120}px)`); drawPath(s.querySelector('[data-r]'), E3((lt - t0) / 0.7)); const c = s.querySelector('[data-c]'); const st = SS.stamp(lt, t0 + 0.7); op(c, st.op); tf(c, `scale(${lt < t0 + 0.7 ? 0 : st.s})`); });
  },
  // end card (dark): photo ring, wordmark, button + cursor + confetti
  end(root, p, at) {
    const A = el(root, 'left:860px;top:110px', avatar(200, 'pfp')); const ringS = el(root, 'left:840px;top:90px', svg(240, 240, `<circle cx="120" cy="120" r="114" fill="none" stroke="${VIO2}" stroke-width="5" stroke-dasharray="20 14"/>`));
    const l1 = el(root, 'left:0;right:0;top:370px;display:flex;justify-content:center', word('SaaS and AI', 130, '#fff')), l2 = el(root, 'left:0;right:0;top:510px;display:flex;justify-content:center', word('Business Mastery.', 130, VIO2));
    const btn = p.composer ? el(root, 'left:960px;top:710px', composerBar(860)) : el(root, `left:960px;top:720px;padding:30px 64px;border-radius:999px;background:${VIO};color:#fff;font:800 44px ID;white-space:nowrap;box-shadow:0 0 60px rgba(123,92,255,.6)`, p.btn);
    const cur = el(root, 'left:0;top:0', '<svg viewBox="0 0 24 24" width="56" height="56"><path d="M4 2l16 9-7 2-3 7z" fill="#fff" stroke="#141418" stroke-width="1.5" stroke-linejoin="round"/></svg>');
    const conf = [...Array(40)].map((_, i) => el(root, `left:960px;top:770px;width:${10 + i % 3 * 4}px;height:${16 + i % 2 * 8}px;border-radius:3px;background:${['#7B5CFF', '#B9A8FF', '#fff', '#12B76A', '#F79009'][i % 5]}`));
    const tc = p.clickAt ? at(p.clickAt) + 0.15 : 1.8;
    return lt => {
      if (p.composer) { const ph = btn.querySelector('[data-ph]'); const txt = p.typed || ''; const n = Math.max(0, Math.floor((lt - tc - 0.3) * 30)); if (lt > tc + 0.3) { ph.style.color = INK; ph.textContent = txt.slice(0, n) || ' '; } }
      popIn(A, lt, 0.1); op(ringS, cl((lt - 0.2) / 0.2)); tf(ringS, `rotate(${lt * 40}deg)`); letters(l1, lt, 0.2, 0.03); letters(l2, lt, 0.4, 0.03);
      const s = SS.stamp(lt, 0.9); op(btn, s.op); tf(btn, `translate(-50%,0) scale(${(lt < 0.9 ? 0 : s.s) * SS.press(lt, tc)})`);
      const k = E3((lt - tc + 0.7) / 0.7); op(cur, lt > tc - 0.7 ? 1 : 0); tf(cur, `translate(${lerp(1400, p.composer ? 900 : 1050, k)}px,${lerp(1000, p.composer ? 745 : 770, k)}px) scale(${SS.cursorSquish(lt, tc)})`);
      conf.forEach((c, i) => { const f = pos(lt - tc); const a = -Math.PI / 2 + (i / 40 - 0.5) * 2.6; const v = 700 + (i * 37 % 400); op(c, f > 0 ? cl(1 - f / 1.8) : 0); tf(c, `translate(${Math.cos(a) * v * f}px,${Math.sin(a) * v * f + 900 * f * f}px) rotate(${f * (300 + i * 20)}deg)`); });
    };
  },
};

// ---------- Skool chrome (from Andrew's screenshots) ----------
const TABS = ['Community', 'Classroom', 'Calendar', 'Members', 'Map', 'Leaderboards', 'About'];
const COURSES = ['Sell One GHL Feature', '01 • Foundation', '02 • Build', '03 • Market', '04 • Sell', '05 • Agent Prompts'];
const navbar = (active, sc = 1) => `<div style="background:#fff;border-bottom:1px solid #EEECF4;padding:${18 * sc}px ${30 * sc}px 0"><div style="display:flex;align-items:center;gap:${14 * sc}px"><img src="${IMG('pfp')}" style="width:${48 * sc}px;height:${48 * sc}px;border-radius:${12 * sc}px;object-fit:cover"><div style="font:700 ${24 * sc}px ID;white-space:nowrap">SaaS &amp; AI Business Mastery</div><div style="flex:1;margin-left:${18 * sc}px;height:${44 * sc}px;border-radius:${10 * sc}px;background:#ECECEC;display:flex;align-items:center;gap:${10 * sc}px;padding:0 ${16 * sc}px;font:500 ${20 * sc}px ID;color:#8a8a8a">${icon('search', 22 * sc, '#8a8a8a', 2)}Search</div><img src="${IMG('pfp')}" style="width:${44 * sc}px;height:${44 * sc}px;border-radius:50%;object-fit:cover"></div><div style="display:flex;gap:${30 * sc}px;margin-top:${18 * sc}px">${TABS.map(t => `<div style="font:500 ${20 * sc}px ID;color:${t === active ? INK : '#8a8a8a'};padding-bottom:${12 * sc}px;border-bottom:${4 * sc}px solid ${t === active ? INK : 'transparent'}">${t}</div>`).join('')}</div></div>`;
const composerBar = (w, sc = 1) => `<div style="width:${w}px;background:#fff;border-radius:${14 * sc}px;box-shadow:0 ${4 * sc}px ${18 * sc}px rgba(0,0,0,.14);display:flex;align-items:center;gap:${18 * sc}px;padding:${14 * sc}px ${18 * sc}px"><img src="${IMG('pfp')}" style="width:${52 * sc}px;height:${52 * sc}px;border-radius:50%;object-fit:cover"><div data-ph style="flex:1;font:500 ${26 * sc}px ID;color:#8a8a8a;white-space:nowrap;overflow:hidden">Write something</div><div style="display:flex;gap:${10 * sc}px;align-items:center;border:1px solid #D9D9D9;border-radius:${12 * sc}px;padding:${10 * sc}px ${18 * sc}px;font:600 ${22 * sc}px ID;color:#555">${icon('video', 26 * sc, '#555', 2)}Go Live</div></div>`;
Object.assign(R, {
  // Andrew holding the phone; the green screen shows the Skool community
  phoneHero(root, p, at) {
    const S = 0.95, PJ = { w: 1600, h: 900, x0: 987, y0: 463, x1: 1173, y1: 840 };
    const C = el(root, 'left:200px;top:60px;width:1520px;height:855px;border-radius:34px;overflow:hidden;box-shadow:0 40px 90px rgba(20,20,40,.25)');
    const inner = el(C, 'left:0;top:0;width:1520px;height:855px;transform-origin:65% 60%');
    const scr = el(inner, `left:${PJ.x0 * S - 6}px;top:${PJ.y0 * S - 6}px;width:${(PJ.x1 - PJ.x0) * S + 12}px;height:${(PJ.y1 - PJ.y0) * S + 12}px;background:#F6F6F6;overflow:hidden`, `<div data-ui style="width:520px;transform:scale(${((PJ.x1 - PJ.x0) * S + 12) / 520});transform-origin:0 0">${navbar('Community', 0.62)}<div style="padding:14px">${composerBar(492, 0.62)}</div><div data-feed style="padding:0 14px">${[['JM', 'My first offer is drafted. Can you look at the pricing?'], ['KT', 'Just landed my first SaaS client!'], ['RS', 'Which course should I start with?'], ['DP', 'Friday call notes are up']].map((q, i) => `<div style="background:#fff;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,.06)"><div style="display:flex;gap:10px;align-items:center">${avatar(40, null, q[0], GR[i + 1])}<b style="font:700 18px ID">${['Jordan M.', 'Kelly T.', 'Ray S.', 'Dana P.'][i]}</b></div><div style="margin-top:10px;font:500 18px ID;line-height:1.35">${q[1]}</div></div>`).join('')}</div></div>`);
    el(inner, 'left:0;top:0;width:1520px;height:855px', `<img src="assets/phone.png" style="width:100%;height:100%;object-fit:cover">`);
    const tags = (p.tags || []).map(t => el(root, `left:${t.x}px;top:${t.y}px;padding:18px 28px;border-radius:999px;background:${t.dark ? INK : '#fff'};color:${t.dark ? '#fff' : INK};font:700 30px ID;display:flex;gap:12px;align-items:center;white-space:nowrap;box-shadow:0 20px 50px rgba(20,20,40,.18)`, (t.icon ? `<span style="color:${t.dark ? VIO2 : VIO}">${icon(t.icon, 32)}</span>` : '') + t.t));
    return (lt, dur) => {
      const k = E4(lt / 0.6); C.style.clipPath = `inset(${(1 - k) * 50}% ${(1 - k) * 50}% round 34px)`; tf(inner, `scale(${lerp(1.0, 1.32, E3(pos(lt - 0.4) / Math.max(1.5, dur - 0.4)))})`);
      const fd = C.querySelector('[data-feed]'); fd.style.transform = `translateY(${-Math.max(0, lt - 1) * 40}px)`;
      tags.forEach((g, i) => popIn(g, lt, p.tags[i].at ? at(p.tags[i].at) : 0.7 + i * 0.4, `translateY(${Math.sin(lt * 1.6 + i) * 8}px)`));
    };
  },
});
// ---------- build ----------
const world = $('world'); const scenes = []; let prev = 0;
SCN.forEach(s => {
  const st = (typeof s.at === 'number' ? s.at : T(s.at, prev)) - 0.1; prev = st + 0.11;
  const root = el(world, 'left:0;top:0;width:1920px;height:1080px;display:none;transform-origin:50% 50%');
  scenes.push({ s, root, st, upd: null });
});
scenes.forEach((sc, i) => { sc.en = i + 1 < scenes.length ? scenes[i + 1].st : DUR + 1; const at = ph => T(ph, sc.st - 0.3) - sc.st; sc.upd = R[sc.s.type](sc.root, sc.s, at); });
// captions
const cap = $('cap'); const phrases = []; { let cur = []; W.forEach((w, i) => { const p = W[i - 1]; if (cur.length && (w.s - p.e > 0.35 || /[.,?!:]$/.test(p.w) || cur.length >= 5)) { phrases.push(cur); cur = []; } cur.push(w); }); if (cur.length) phrases.push(cur); }
// background layers
const blobs = [0, 1, 2].map(i => el($('bg'), `left:0;top:0;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(123,92,255,${[0.16, 0.10, 0.12][i]}),transparent 65%)`));
function render(t) {
  let dark = 0;
  scenes.forEach((sc, i) => {
    const vis = t >= sc.st && t < sc.en + 0.25; sc.root.style.display = vis ? 'block' : 'none'; if (!vis) return;
    const lt = t - sc.st, dur = sc.en - sc.st, out = cl((t - sc.en) / 0.25);
    if (t < sc.en) dark = sc.s.dark ? cl(lt / 0.18) : (i > 0 && scenes[i - 1].s.dark ? 1 - cl(lt / 0.18) : 0);
    // camera: punch-in on entry, slow push, whip out
    const tr = sc.s.tr || ['zoom', 'left', 'up', 'zoom'][i % 4]; const ink = E4(lt / 0.42);
    let base = '';
    if (tr === 'zoom') base = `scale(${lerp(0.9, 1, ink)})`; else if (tr === 'left') base = `translateX(${(1 - ink) * 260}px)`; else if (tr === 'up') base = `translateY(${(1 - ink) * 160}px)`;
    const push = 1 + 0.035 * E3(lt / Math.max(1, dur)); const drift = `translate(${Math.sin(lt * 0.5 + i) * 10}px,${Math.cos(lt * 0.4 + i) * 6}px)`;
    tf(sc.root, `${base} ${drift} scale(${push * (1 + out * 0.12)})`); op(sc.root, cl(lt / 0.12) * (1 - out)); blur(sc.root, out * 14 + (1 - ink) * (tr === 'zoom' ? 6 : 3));
    sc.upd(lt, dur);
  });
  $('dark').style.opacity = dark;
  blobs.forEach((b, i) => tf(b, `translate(${[200, 1100, 600][i] + Math.sin(t * 0.21 + i * 2) * 220}px,${[-200, 300, 500][i] + Math.cos(t * 0.17 + i) * 160}px)`));
  $('grid').style.backgroundPosition = `${(t * 12) % 48}px ${(t * 8) % 48}px`;
  // captions
  let P = null; for (let i = 0; i < phrases.length; i++) { const a = phrases[i][0].s - 0.05, b = i + 1 < phrases.length ? Math.min(phrases[i + 1][0].s - 0.05, phrases[i].at(-1).e + 0.7) : phrases[i].at(-1).e + 0.7; if (t >= a && t < b) { P = phrases[i]; break; } }
  const cur = scenes.find(sc => t >= sc.st && t < sc.en); const hide = cur && cur.s.type === 'end' && t > cur.st + 0.6;
  if (!P || hide) { cap.style.opacity = 0; } else {
    if (cap._k !== P[0].s) { cap._k = P[0].s; cap.innerHTML = `<span class="pill">${P.map(w => `<span class="w">${w.w}</span>`).join(' ')}</span>`; }
    const act = P.reduce((m, w, i) => t >= w.s - 0.03 ? i : m, -1); const dk = dark > 0.5; cap.className = dk ? 'dk' : '';
    cap.querySelectorAll('.w').forEach((s, i) => { s.style.color = i === act ? (dk ? VIO2 : VIO) : (dk ? '#fff' : INK); s.style.opacity = i <= act ? 1 : 0.4; s.style.transform = i === act ? 'translateY(-2px) scale(1.06)' : 'none'; });
    const e = cl((t - P[0].s + 0.05) / 0.1); cap.style.opacity = e; cap.style.transform = `translateX(-50%) translateY(${(1 - e) * 12}px)`;
  }
}
window.render = render;
window.CUES = { scenes: scenes.map(s => +s.st.toFixed(3)), click: scenes.filter(s => s.s.type === 'end').map(s => +(s.s.clickAt ? T(s.s.clickAt, s.st - 0.3) + 0.15 : s.st + 1.8).toFixed(3)), dark: scenes.map(s => !!s.s.dark) };
