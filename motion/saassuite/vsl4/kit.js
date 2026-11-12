// VSL overlay kit (worker B, Nov 9). Pure render(t) components on a 720x420 design "panel" that is placed
// beside Andrew (16:9) or under his head (9:16). All motion comes from SS (saassuite-motion/lib.js).
// Usage: const K = Kit({accent, ...}); K.scene(t0, t1, root => [...components]); K.render(t).
function Kit(o) {
  const { cl, lerp, ease } = SS;
  const A = o.accent, CARD = o.card || '#FBF8F4', INK = o.ink || '#101010', MUTED = o.muted || '#6F6E72', TRACK = o.track || '#EFEEF3';
  const V = new URLSearchParams(location.search).get('v') || '169';
  // 45 = 4:5 1080x1350 and 34 = 3:4 1080x1440 (Meta feed): crop of the 4K source centred on Andrew (head y ≈ 140–690 / 150–735).
  const L = { '169': { W: 1920, H: 1080, px: 1196, py: 210, ps: 0.94, cap: 932, cs: 62, endS: 170 },
    '916': { W: 1080, H: 1920, px: 205, py: 1198, ps: 0.93, cap: 1636, cs: 84, endS: 150 },
    '45': { W: 1080, H: 1350, px: 205, py: 735, ps: 0.93, cap: 1150, cs: 72, endS: 140 },
    '34': { W: 1080, H: 1440, px: 205, py: 780, ps: 0.93, cap: 1205, cs: 76, endS: 145 } }[V];
  document.body.style.width = L.W + 'px'; document.body.style.height = L.H + 'px';
  const el = (tag, css, parent, html) => { const e = document.createElement(tag); if (css) e.style.cssText = css; if (html != null) e.innerHTML = html; (parent || document.body).appendChild(e); return e; };
  const panel = el('div', `position:absolute;left:${L.px}px;top:${L.py}px;width:720px;height:420px;transform-origin:0 0`);
  const scenes = [], CUES = [];
  const cue = (t, k) => CUES.push({ t: +t.toFixed(3), k });
  const shadowTxt = '0 8px 30px rgba(0,0,0,.45),0 2px 6px rgba(0,0,0,.35)';

  // ---------- components (each returns {draw(t)}) ----------
  // Mono kicker: letters rise 9px easeOutCubic 0.12s, stagger 0.03s (ClimbX kicker).
  function kicker(p, text, t0, x, y, c = {}) {
    const e = el('div', `position:absolute;left:${x}px;top:${y}px;font:700 ${c.size || 22}px JB;letter-spacing:${c.ls || 4}px;color:${c.color || A};white-space:nowrap;text-shadow:${c.shadow === false ? 'none' : '0 2px 10px rgba(0,0,0,.5)'}`, p);
    const sp = [...text].map(ch => el('span', 'display:inline-block', e, ch === ' ' ? '&nbsp;' : ch));
    return { draw: t => sp.forEach((s, j) => { const u = ease.outCubic((t - t0 - j * 0.03) / 0.12); s.style.opacity = cl((t - t0 - j * 0.03) / 0.07); s.style.transform = `translateY(${(1 - u) * 9}px)`; }) };
  }
  // Headline: letter spring-rise (ClimbX measured). lines = ['vibe coding.'], acc = words in accent.
  function headline(p, lines, acc, t0, x, y, c = {}) {
    const size = c.size || 84, lh = c.lh || Math.round(size * 1.08), color = c.color || '#fff';
    const e = el('div', `position:absolute;left:${x}px;top:${y}px;font-family:ID;font-weight:800;font-variation-settings:'opsz' 32;letter-spacing:-0.037em;font-size:${size}px;line-height:${lh}px;color:${color};white-space:nowrap;text-shadow:${c.shadow === false ? 'none' : shadowTxt};${c.align ? 'text-align:' + c.align + ';width:' + c.w + 'px' : ''}`, p);
    const L2 = []; let i = 0;
    lines.forEach(line => { const d = el('div', '', e); line.split(' ').forEach((w, wi) => { if (wi) el('span', '', d, '&nbsp;'); const isA = acc.includes(w); [...w].forEach(ch => L2.push({ s: el('span', `display:inline-block;will-change:transform;${isA ? 'color:' + A : ''}`, d, ch), i: i++ })); }); });
    cue(t0, 'whoosh');
    return { el: e, draw: t => L2.forEach(({ s, i }) => { const r = SS.letterRise(t, t0, i); s.style.transform = `translateY(${r.y}px) rotate(${r.rot}deg)`; s.style.filter = r.blur > 0.2 ? `blur(${r.blur}px)` : 'none'; s.style.opacity = r.op; }) };
  }
  // Floating card sliding in on the ClimbX spring.
  function card(p, t0, x, y, w, h, c = {}) {
    const e = el('div', `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;border-radius:${c.r || 22}px;background:${c.bg || CARD};box-shadow:0 1px 1px rgba(0,0,0,.05),0 6px 6px -2px rgba(0,0,0,.08),0 30px 70px rgba(0,0,0,.35);overflow:hidden`, p);
    cue(t0, 'whoosh');
    return { el: e, draw: t => { const s = SS.cardSlide(t, t0, c.dx || 358); e.style.opacity = s.op; e.style.transform = `translateX(${s.x}px)`; e.style.filter = s.blurX > 0.3 ? `blur(${Math.min(8, s.blurX)}px)` : 'none'; } };
  }
  // Pill stamp (ClimbX "Ready to post"): slam + overshoot + shock ring.
  function pill(p, html, t0, cx, cy, c = {}) {
    const wrap = el('div', `position:absolute;left:${cx}px;top:${cy}px;width:0;height:0`, p);
    const ring = el('div', `position:absolute;border-radius:50%;border:2.5px solid ${c.ring || A};left:0;top:0`, wrap);
    const e = el('div', `position:absolute;left:0;top:0;transform-origin:50% 50%;white-space:nowrap;background:${c.bg || A};color:${c.color || '#fff'};font:700 ${c.size || 34}px IN;padding:${c.pad || '14px 30px'};border-radius:999px;box-shadow:0 14px 34px ${c.glow || 'rgba(255,105,47,.35)'}`, wrap, html);
    cue(t0, 'pop');
    return { el: e, draw: t => { const st = SS.stamp(t, t0); e.style.opacity = st.op; e.style.transform = `translate(-50%,-50%) scale(${st.s}) rotate(${st.rot * (c.rotK ?? 1)}deg)`; const f = (t - t0) * 30 - 6.5; const r = f > 0 ? 150 * (1 - Math.exp(-f / 3.2)) : 0; ring.style.width = ring.style.height = 2 * r + 'px'; ring.style.transform = `translate(-50%,-50%)`; ring.style.opacity = f > 0 ? 0.9 * cl(1 - f / 13) : 0; } };
  }
  // Card row: blur-dissolve + 16px rise (MakerMap rows); optional strike-through after ts.
  function row(p, html, t0, x, y, w, h, c = {}) {
    const e = el('div', `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;border-radius:14px;background:${c.bg || '#F1EEE9'};display:flex;align-items:center;gap:16px;padding:0 20px;font:600 ${c.size || 27}px IN;color:${c.color || INK};white-space:nowrap`, p, html);
    let sk = null; if (c.strike != null) { sk = el('div', `position:absolute;left:${c.skx || 70}px;top:${h / 2 - 2}px;height:4px;border-radius:2px;background:${INK}`, e); cue(c.strike, 'tick'); }
    cue(t0, 'click');
    return { el: e, draw: t => { const u = cl((t - t0) / 0.12); e.style.opacity = u; e.style.filter = u < 1 ? `blur(${10 * (1 - u)}px)` : 'none'; e.style.transform = `translateY(${16 * (1 - SS.spring(t - t0, 14, 1))}px)`; if (sk) { const k = ease.outCubic((t - c.strike) / 0.35); sk.style.width = k * (c.skw || w - 110) + 'px'; e.style.color = k > 0.5 ? '#A3A2A8' : (c.color || INK); } } };
  }
  const icon = (txt, bg = 'rgba(255,105,47,.14)', col = A) => `<div style="width:40px;height:40px;border-radius:11px;background:${bg};display:grid;place-items:center;color:${col};font:700 20px IN;flex:none">${txt}</div>`;
  const check = (col = '#fff') => `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="${col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>`;
  // Typing (Tessel): new char born in accent, fades to ink over 5 frames; solid caret.
  function typer(p, text, t0, x, y, c = {}) {
    const e = el('div', `position:absolute;left:${x}px;top:${y}px;font:${c.weight || 500} ${c.size || 30}px IN;color:${INK};white-space:nowrap`, p);
    const caret = `<span style="display:inline-block;width:3px;height:${(c.size || 30) * 1.1}px;background:${A};vertical-align:-6px;margin-left:3px"></span>`;
    for (let i = 0; i < text.length; i += 3) cue(t0 + i / (c.cps || 22), 'type');
    return { draw: t => { const ty = SS.typing(t, t0, text, c.cps || 22); let h = ''; [...ty.shown].forEach((ch, i) => { const a = cl(ty.ageOf(i) / 5); h += `<span style="color:${a < 1 ? `color-mix(in srgb, ${A} ${(1 - a) * 100}%, ${INK})` : INK}">${ch === ' ' ? '&nbsp;' : ch}</span>`; }); e.innerHTML = (ty.n === 0 && c.ph ? `<span style="color:#A3A2A8">${c.ph}</span>` : h) + (t < (c.caretOff || 1e9) ? caret : ''); } };
  }
  // Skeleton "website" that builds: bars fill with the ClimbX bar curve, rows 0.133s apart.
  function site(p, t0, x, y, w, h) {
    const e = el('div', `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;border-radius:14px;background:#fff;border:1px solid #ECEAE6;overflow:hidden`, p);
    const nav = el('div', `position:absolute;left:0;top:0;right:0;height:30px;background:#F4F2EE;display:flex;gap:6px;align-items:center;padding-left:12px`, e, '<i style="width:9px;height:9px;border-radius:50%;background:#E2DED8"></i><i style="width:9px;height:9px;border-radius:50%;background:#E2DED8"></i><i style="width:9px;height:9px;border-radius:50%;background:#E2DED8"></i>');
    const H = h - 30, parts = [
      [0.06, 0.18, 0.55, 0.16, INK], [0.06, 0.40, 0.38, 0.07, '#CFCBC4'], [0.06, 0.53, 0.18, 0.12, A],
      [0.06, 0.74, 0.27, 0.2, '#EFEBE5'], [0.365, 0.74, 0.27, 0.2, '#EFEBE5'], [0.67, 0.74, 0.27, 0.2, '#EFEBE5'], [0.67, 0.14, 0.27, 0.5, '#F3E4DA']];
    const B = parts.map(([px, py, pw, ph, col]) => el('div', `position:absolute;left:${px * w}px;top:${30 + py * H}px;height:${ph * H}px;border-radius:8px;background:${col}`, e));
    cue(t0, 'riser');
    return { draw: t => B.forEach((b, r) => { const f = SS.barFill(t, t0, r); b.style.width = f * parts[r][2] * w + 'px'; b.style.opacity = cl((t - t0 - r * 0.133) / 0.06); }) };
  }
  // Button press (MakerMap press curve) that flips to a done state.
  function button(p, html, doneHtml, tp, x, y, c = {}) {
    const e = el('div', `position:absolute;left:${x}px;top:${y}px;height:${c.h || 56}px;padding:0 ${c.padx || 24}px;border-radius:999px;background:#2B2E40;color:#fff;font:700 ${c.size || 22}px IN;display:flex;align-items:center;gap:8px;white-space:nowrap;transform-origin:50% 50%`, p, html);
    cue(tp, 'click'); cue(tp + 0.12, 'ding');
    return { draw: t => { e.style.transform = `scale(${SS.press(t, tp)})`; const k = cl((t - tp - 0.09) / 0.07); e.style.background = k > 0.5 ? A : '#2B2E40'; e.innerHTML = k > 0.5 ? doneHtml : html; } };
  }
  // Seeded confetti burst (ClimbX): radial d = sp(1-e^-7t), gravity, fade after 0.45s.
  function confetti(p, t0, cx, cy, n = 18) {
    let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    const cols = [A, '#FFB38F', '#FFFFFF', '#2B2E40', '#FFD2BD'];
    const P = Array.from({ length: n }, (_, i) => ({ a: rnd() * Math.PI * 2, sp: 60 + rnd() * 120, g: 30 + rnd() * 50, spin: (rnd() - .5) * 600, bar: rnd() > .5, e: el('div', `position:absolute;left:${cx}px;top:${cy}px;background:${cols[i % 5]};border-radius:2px`, p) }));
    return { draw: t => P.forEach(q => { const u = t - t0; if (u < 0) { q.e.style.opacity = 0; return; } const d = q.sp * (1 - Math.exp(-7 * u)); q.e.style.width = (q.bar ? 5 : 7) + 'px'; q.e.style.height = (q.bar ? 13 : 7) + 'px'; q.e.style.transform = `translate(${Math.cos(q.a) * d * 1.25}px,${Math.sin(q.a) * d + q.g * u * u}px) rotate(${q.spin * u}deg)`; q.e.style.opacity = 1 - cl((u - 0.45) / 0.45); }) };
  }
  // Generic: a fixed element fading in/out with blur (for labels).
  function fadeIn(p, html, t0, css) { const e = el('div', 'position:absolute;' + css, p, html); return { el: e, draw: t => { const u = ease.outQuart((t - t0) / 0.4); e.style.opacity = u; e.style.transform = `translateY(${(1 - u) * 14}px)`; e.style.filter = u < 1 ? `blur(${6 * (1 - u)}px)` : 'none'; } }; }

  function scene(t0, t1, build) { const root = el('div', 'position:absolute;inset:0;display:none', panel); scenes.push({ t0, t1, root, parts: build(root) }); }

  // ---------- captions (karaoke, 2-3 words, break on >0.35s pause or punctuation) ----------
  const cap = el('div', `position:absolute;left:0;right:0;top:${L.cap}px;text-align:center;color:#fff;white-space:nowrap;font-family:ID;font-weight:800;font-variation-settings:'opsz' 32;letter-spacing:-0.037em;font-size:${L.cs}px`);
  const ph = []; let cur = []; for (const w of WORDS) { if (cur.length && (cur.length >= 3 || w[1] - cur[cur.length - 1][2] > 0.35 || /[,.?!]$/.test(cur[cur.length - 1][0]))) ph.push(cur), cur = []; cur.push(w); } ph.push(cur);
  ph.forEach((p, i) => { const nx = ph[i + 1]; p.end = nx ? Math.min(p[p.length - 1][2] + 0.3, nx[0][1] - 0.04) : p[p.length - 1][2] + 0.3; });

  // ---------- HUD (ClimbX): brackets + mono labels; 9:16 bottom row only (top is Andrew's head) ----------
  const hud = el('div', 'position:absolute;inset:0;font:500 15px JB;letter-spacing:3.4px;color:rgba(235,232,228,.72)');
  const hl = (css, txt) => el('div', 'position:absolute;white-space:nowrap;' + css, hud, txt);
  const brk = (css) => el('div', 'position:absolute;width:14px;height:14px;' + css, hud);
  let tc = { textContent: '' };
  if (o.hud === false) {}
  else if (V === '169') { hl('left:42px;top:30px', 'SAASSUITE'); hl('right:42px;top:30px', o.hud); tc = hl('left:42px;bottom:30px', ''); hl('right:42px;bottom:30px', 'ONE FEATURE');
    brk('left:20px;top:20px;border-left:2px solid;border-top:2px solid'); brk('right:20px;top:20px;border-right:2px solid;border-top:2px solid'); brk('left:20px;bottom:20px;border-left:2px solid;border-bottom:2px solid'); brk('right:20px;bottom:20px;border-right:2px solid;border-bottom:2px solid'); }
  else { tc = hl('left:42px;bottom:34px', ''); hl('right:42px;bottom:34px', o.hud); brk('left:20px;bottom:22px;border-left:2px solid;border-bottom:2px solid'); brk('right:20px;bottom:22px;border-right:2px solid;border-bottom:2px solid'); }

  // ---------- dark end card ----------
  const end = el('div', `position:absolute;inset:0;display:none;background:radial-gradient(ellipse 60% 50% at 50% 55%, ${o.glow || 'rgba(255,105,47,.16)'}, rgba(0,0,0,0) 70%),#0B0B10`);
  const endW = { draw: () => {} }; let endParts = [];
  function endCard(t0, cta) {
    o.endT = t0; cue(t0, 'whoosh');
    const midY = L.H / 2;
    const hw = headline(end, ['SaaSSuite.'], [], t0 + 0.15, 0, midY - L.endS * 0.75, { size: L.endS, align: 'center', w: L.W, shadow: false });
    const dot = hw.el.querySelectorAll('span'); dot[dot.length - 1].style.color = A;
    endParts = [hw, pill(end, cta, t0 + 0.75, L.W / 2, midY + L.endS * 0.62, { size: V === '169' ? 38 : 40, pad: '18px 40px' })];
  }

  function render(t) {
    const pulse = o.pulse === false ? 1 : SS.beatPulse(t, 90);
    panel.style.transform = `scale(${L.ps * pulse})`;
    for (const s of scenes) {
      const on = t >= s.t0 - 0.05 && t <= s.t1; s.root.style.display = on ? 'block' : 'none'; if (!on) continue;
      const out = cl((t - (s.t1 - 0.25)) / 0.25); s.root.style.opacity = 1 - out; s.root.style.transform = `translateY(${-out * 26}px)`; s.root.style.filter = out > 0 ? `blur(${out * 10}px)` : 'none';
      s.parts.forEach(c => c.draw(t));
    }
    const isEnd = o.endT != null && t >= o.endT;
    end.style.display = isEnd ? 'block' : 'none';
    if (isEnd) { end.style.opacity = cl((t - o.endT) / 0.25); endParts.forEach(c => c.draw(t)); }
    hud.style.opacity = isEnd ? 0 : 1;
    const f = Math.floor(t * 30 + 1e-6); tc.textContent = `00:00:${String(Math.floor(f / 30)).padStart(2, '0')}:${String(f % 30).padStart(2, '0')}`;
    const P = !isEnd && ph.find(p => p[0][1] - 0.05 <= t && t <= p.end);
    if (P) { let ai = -1; P.forEach((w, i) => { if (w[1] <= t) ai = i; }); cap.innerHTML = P.map((w, i) => `<span style="display:inline-block;margin:0 .12em;text-shadow:4px 4px 0 rgba(0,0,0,.55),0 0 24px rgba(0,0,0,.35);color:${i === ai ? A : '#fff'}">${w[0].replace(/,$/, '')}</span>`).join(''); const u = ease.outQuart((t - P[0][1] + 0.05) / 0.18); cap.style.opacity = u; cap.style.transform = `translateY(${(1 - u) * 14}px)`; }
    else cap.innerHTML = '';
  }
  return { V, L, el, panel, scene, kicker, headline, card, pill, row, icon, check, typer, site, button, confetti, fadeIn, endCard, render, CUES, cue, INK, MUTED, TRACK, A };
}
