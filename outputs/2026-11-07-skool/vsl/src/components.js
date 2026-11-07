// Scene components. Each: COMP.name = (s, E, T) => update(t). Props come from the scene object.
// Times inside a scene come from the voice: s.wt('phrase') = when that phrase starts.

const tm = (s, it, k, n) => it.at ? s.wt(it.at, k * 0.5) : lerp(s.t0 + 0.25, Math.max(s.t0 + 0.4, s.t1 - 0.6), n > 1 ? k / (n - 1) : 0);

/* Big kinetic type over the full frame. s.text overrides the spoken words. s.hl = words to colour. */
COMP.big = (s, E, T) => {
  s.cap = false;
  const sz = s.size || (E.IS_V ? 128 : 138);
  const box = E.el('div', 'abs', s.root);
  E.css(box, { left: E.IS_V ? '70px' : '160px', right: E.IS_V ? '70px' : '160px', top: '0', bottom: '0', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '28px' });
  let ic;
  if (s.icon) { ic = E.el('div', 'ico', box, E.icon(s.icon, sz * 0.62, 'currentColor', 2.2)); E.css(ic, { width: sz * 1.2 + 'px', height: sz * 1.2 + 'px', borderRadius: sz * 0.32 + 'px' }); }
  const line = E.el('div', 'h', box);
  E.css(line, { fontSize: sz + 'px', textAlign: 'center', display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 0.24em', lineHeight: 1.04, color: s.ink || 'var(--bigink)' });
  const toks = s.text ? s.text.split(' ').map(w => ({ w, n: w.toLowerCase().replace(/[^a-z0-9']/g, '') })) : s.words.map(w => ({ w: w.w, n: w.n, s: w.s }));
  // map text tokens to spoken word times when possible
  let wi = 0; const sw = s.words;
  toks.forEach((t, k) => { if (t.s == null) { const j = sw.findIndex((w, q) => q >= wi && w.n.replace(/'/g, '') === t.n.replace(/'/g, '')); if (j >= 0) { t.s = sw[j].s; wi = j + 1; } else t.s = (toks[k - 1]?.s ?? s.t0 + 0.1) + 0.12; } });
  const hl = (s.hl || []).map(x => x.toLowerCase());
  const spans = toks.map(t => { const sp = E.el('span', 'nowrap', line); sp.textContent = T.capUpper || s.upper ? t.w.toUpperCase() : t.w; if (hl.some(h => t.n.startsWith(h))) sp.classList.add('bighl'); E.css(sp, { display: 'inline-block' }); return sp; });
  let sub; if (s.sub) { sub = E.el('div', 'serif sub', box, s.sub); E.css(sub, { fontSize: sz * 0.45 + 'px' }); }
  return t => {
    spans.forEach((sp, k) => { const q = E.pop(t, toks[k].s - 0.07, 20, 0.6), g0 = s.ghost != null ? s.ghost : E.soft(t, s.t0, 14) * 0.14; sp.style.opacity = Math.max(g0, E.clamp(q * 2)); sp.style.transform = `translateY(${(1 - E.clamp(q, 0, 1.3)) * 30}px) scale(${E.lerp(0.85, 1, q)})`; });
    if (ic) E.show(ic, E.pop(t, s.t0, 14, 0.6), 30, 0.5);
    if (sub) E.show(sub, E.soft(t, toks[toks.length - 1].s + 0.2));
    const push = E.lerp(1, 1.06, E.seg(t, s.t0, s.t1 + 0.3));
    box.style.transform = `scale(${push})`;
  };
};

/* Tiles that pop in on their word. items [{t, i, at, d}]; variant 'tile' | 'card' | 'q' */
COMP.chips = (s, E) => {
  const items = s.items, n = items.length, V = E.IS_V, card = s.variant === 'card' || s.variant === 'q';
  const cols = V ? (card ? 1 : (n > 3 ? 2 : 1)) : Math.min(n, s.cols || n);
  const rows = Math.ceil(n / cols);
  const tw = V ? (cols === 1 ? 820 : 420) : (card ? 470 : 330), th = card ? (V ? 220 : 340) : (V && cols === 1 ? 170 : 230), gap = 34;
  const dw = cols * tw + (cols - 1) * gap, dh = rows * th + (rows - 1) * gap + (s.title ? 120 : 0);
  const b = E.box(s, dw, dh);
  let title; if (s.title) { title = E.el('div', 'h abs nowrap', b, s.title); E.css(title, { left: 0, right: 0, top: 0, textAlign: 'center', fontSize: '64px' }); }
  const els = items.map((it, k) => {
    const c = E.el('div', 'card abs', b), r = Math.floor(k / cols), q = k % cols;
    const lastRow = r === rows - 1 && n % cols ? (cols - n % cols) * (tw + gap) / 2 : 0;
    E.css(c, { width: tw + 'px', height: th + 'px', left: q * (tw + gap) + lastRow + 'px', top: (s.title ? 120 : 0) + r * (th + gap) + 'px', display: 'flex', flexDirection: (card && V) || (!card && V && cols === 1) ? 'row' : 'column', alignItems: card && !V ? 'flex-start' : 'center', justifyContent: 'center', gap: '22px', padding: '30px 34px' });
    const ic = E.el('div', 'ico', c, s.variant === 'q' ? '<span class="h" style="font-size:64px">?</span>' : E.icon(it.i || 'star', card ? 50 : 56));
    E.css(ic, { width: (card ? 92 : 104) + 'px', height: (card ? 92 : 104) + 'px', borderRadius: '26px' });
    const tx = E.el('div', '', c);
    const lab = E.el('div', 'h', tx, it.t); E.css(lab, { fontSize: (card ? 44 : (it.t.length > 11 ? 40 : 46)) + 'px', textAlign: card && !V ? 'left' : (V && card ? 'left' : 'center'), lineHeight: 1.08 });
    if (it.d) { const d = E.el('div', 'sub', tx, it.d); E.css(d, { fontSize: '26px', marginTop: '10px', fontWeight: 600, lineHeight: 1.25 }); }
    const at = tm(s, it, k, n); E.cue(at - 0.02, 'pop', 0.55);
    return { c, at };
  });
  return t => {
    if (title) E.show(title, E.soft(t, s.t0));
    els.forEach(({ c, at }, k) => { const q = E.pop(t, at - 0.08, 17, 0.6); c.style.opacity = E.clamp(q * 2); c.style.transform = `translateY(${(1 - q) * 60}px) scale(${E.lerp(0.75, 1, q)})`; c.classList.toggle('lit', t > at - 0.05); });
  };
};

/* Notification toasts stacking up. items [{t, d, i, at}] */
COMP.toasts = (s, E) => {
  const n = s.items.length, tw = E.IS_V ? 900 : 940, th = 150, gap = 26;
  const b = E.box(s, tw, n * th + (n - 1) * gap + 40);
  const els = s.items.map((it, k) => {
    const c = E.el('div', 'card abs', b);
    E.css(c, { width: tw + 'px', height: th + 'px', left: 0, top: k * (th + gap) + 'px', display: 'flex', alignItems: 'center', gap: '28px', padding: '0 34px', borderRadius: '30px' });
    const ic = E.el('div', 'ico', c, E.icon(it.i || 'bolt', 48)); E.css(ic, { width: '88px', height: '88px', borderRadius: '24px' });
    const tx = E.el('div', '', c); const a = E.el('div', 'h', tx, it.t); E.css(a, { fontSize: '42px' });
    if (it.d) { const d = E.el('div', 'sub', tx, it.d); E.css(d, { fontSize: '27px', fontWeight: 600, marginTop: '8px' }); }
    const tag = E.el('div', 'sub abs', c, it.tag || 'now'); E.css(tag, { right: '34px', top: '26px', fontSize: '22px', fontWeight: 600 });
    const at = tm(s, it, k, n); E.cue(at - 0.02, s.sfxItem || 'pop', 0.6);
    return { c, at };
  });
  return t => els.forEach(({ c, at }) => { const q = E.pop(t, at - 0.08, 16, 0.66); c.style.opacity = E.clamp(q * 2); c.style.transform = `translateX(${(1 - q) * 120}px) scale(${E.lerp(0.9, 1, q)})`; });
};

/* Jigsaw. mode: 'assemble' | 'chaos' | 'labels' | 'solve'. */
COMP.puzzle = (s, E) => {
  const V = E.IS_V, cols = s.cols || 3, rows = s.rows || 2, ps = s.ps || (V ? 280 : 250);
  const dw = cols * ps + 160, dh = rows * ps + 160;
  const b = E.box(s, dw, dh, s.region || E.R);
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg'); svg.setAttribute('width', dw); svg.setAttribute('height', dh); svg.style.overflow = 'visible'; b.appendChild(svg);
  const r = E.rng(s.seed || 3), hT = [], vT = [];
  for (let y = 0; y < rows; y++) for (let x = 0; x < cols - 1; x++) hT[y * cols + x] = r() > .5 ? 1 : -1;
  for (let y = 0; y < rows - 1; y++) for (let x = 0; x < cols; x++) vT[y * cols + x] = r() > .5 ? 1 : -1;
  const colors = s.colors || ['var(--acc)', 'var(--acc2)', 'var(--pz3)', 'var(--pz4)'];
  const labels = s.labels || [];
  const pieces = [], labelLayer = [];
  for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
    const k = y * cols + x;
    const tabs = [y > 0 ? -vT[(y - 1) * cols + x] : 0, x < cols - 1 ? hT[k] : 0, y < rows - 1 ? vT[k] : 0, x > 0 ? -hT[k - 1] : 0];
    const g = document.createElementNS(svgNS, 'g'); svg.appendChild(g);
    const p = document.createElementNS(svgNS, 'path'); p.setAttribute('d', E.piecePath(ps, tabs));
    const col = colors[(x + y * 2) % colors.length];
    p.setAttribute('style', `fill:${col};stroke:var(--pzline);stroke-width:5;stroke-linejoin:round`); g.appendChild(p);
    const L = labels[k];
    let tx; const LBL = 1;
    if (L) {
      const lg = document.createElementNS(svgNS, 'g'); labelLayer.push(lg); g._lg = lg;
      const fo = document.createElementNS(svgNS, 'foreignObject'); fo.setAttribute('x', -20); fo.setAttribute('y', 0); fo.setAttribute('width', ps + 40); fo.setAttribute('height', ps); lg.appendChild(fo);
      tx = E.el('div', 'h', null, L.t); E.css(tx, { width: ps + 40 + 'px', height: ps + 'px', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontSize: (L.t.length > 10 ? 40 : 46) + 'px', color: 'var(--pzink)', padding: '20px', lineHeight: 1.05 }); fo.appendChild(tx);
    }
    const ang = r() * Math.PI * 2, dist = 900 + r() * 400;
    const tx0 = 80 + x * ps, ty0 = 80 + y * ps;
    const at = L && L.at ? s.wt(L.at, k * 0.4) : s.t0 + 0.1 + k * (s.stagger || 0.16);
    pieces.push({ g, tx0, ty0, sx: tx0 + Math.cos(ang) * dist, sy: ty0 + Math.sin(ang) * dist, rot0: (r() - .5) * 140, at, k, x, y, miss: s.missing === k });
    E.cue(at + 0.28, s.mode === 'labels' ? 'pop' : 'click', 0.5);
  }
  labelLayer.forEach(lg => svg.appendChild(lg));
  // chaos: extra loose pieces raining in
  const extra = [];
  if (s.mode === 'chaos') for (let i = 0; i < (s.extra || 9); i++) {
    const g = document.createElementNS(svgNS, 'g'); svg.appendChild(g);
    const p = document.createElementNS(svgNS, 'path'); p.setAttribute('d', E.piecePath(ps * 0.8, [r() > .5 ? 1 : -1, r() > .5 ? 1 : -1, r() > .5 ? 1 : -1, r() > .5 ? 1 : -1]));
    p.setAttribute('style', `fill:${colors[i % colors.length]};stroke:var(--pzline);stroke-width:5;opacity:.95`); g.appendChild(p);
    const side = i % 4, at = s.t0 + 0.2 + i * ((s.t1 - s.t0 - 0.8) / (s.extra || 9));
    const ex = [-300, dw + 100, r() * dw, r() * dw][side], ey = [r() * dh, r() * dh, -300, dh + 100][side];
    extra.push({ g, at, sx: ex, sy: ey, tx: -120 + r() * (dw + 40), ty: -120 + r() * (dh + 40), rot: (r() - .5) * 120 });
    E.cue(at + 0.2, 'pop', 0.4);
  }
  if (s.missing != null && s.missAt && findPhrase(s.missAt, s.wi, s.wj) >= 0) E.cue(WORDS[findPhrase(s.missAt, s.wi, s.wj)].s + 0.25, 'impact', 0.8);
  if (s.mode === 'solve') E.cue(s.t0 + 0.1 + pieces.length * (s.stagger || 0.16) + 0.25, 'impact', 0.8);
  let badge, tB;
  if (s.badge) { badge = E.el('div', 'pill h abs nowrap', b, E.icon('check', 44, 'currentColor', 3) + ' ' + s.badge); tB = s.wt(s.badgeAt || 'community', 1); E.css(badge, { left: dw / 2 + 'px', top: dh / 2 + 'px', fontSize: '54px', padding: '22px 40px', background: 'var(--acc)', color: 'var(--accink)', borderColor: 'transparent', boxShadow: '0 20px 60px rgba(0,0,0,.45)', zIndex: 5 }); E.cue(tB, 'impact', .7); }
  return t => {
    if (badge) { const q = E.pop(t, tB - .05, 15, .55); badge.style.opacity = E.clamp(q * 2); badge.style.transform = `translate(-50%,-50%) scale(${E.lerp(.4, 1, q)}) rotate(${(1 - E.clamp(q)) * -8}deg)`; }
    for (const p of pieces) {
      let k;
      if (s.mode === 'chaos') k = 1 - 0.25 * E.easeOut(E.seg(t, s.t0 + 0.3 + p.k * 0.1, s.t1));
      else k = E.spring(t - p.at, 13, 0.78);
      if (p.miss) { const mi = findPhrase(s.missAt || 'zzzz', s.wi, s.wj); k = mi >= 0 ? E.spring(t - WORDS[mi].s, 12, 0.75) : 0; }
      const x = E.lerp(p.sx, p.tx0, k), y = E.lerp(p.sy, p.ty0, k), rot = (1 - k) * p.rot0;
      let wob = s.mode === 'chaos' ? Math.sin(t * 9 + p.k) * 4 * E.seg(t, s.t0 + 0.5, s.t1) : 0;
      const sc = s.mode === 'solve' ? 1 + 0.06 * Math.max(0, Math.sin(E.clamp((t - s.t0 - 0.35 - pieces.length * (s.stagger || 0.16)) * 3) * Math.PI)) : 1;
      p.g.setAttribute('transform', `translate(${x},${y}) rotate(${rot + wob} ${dw / 2 - x} ${dh / 2 - y}) translate(${ps / 2},${ps / 2}) scale(${sc}) translate(${-ps / 2},${-ps / 2})`);
      p.g.style.opacity = E.clamp(k * 3);
      if (p.g._lg) { p.g._lg.setAttribute('transform', p.g.getAttribute('transform')); p.g._lg.style.opacity = p.g.style.opacity; }
    }
    for (const p of extra) {
      const k = E.spring(t - p.at, 10, 0.7);
      p.g.setAttribute('transform', `translate(${E.lerp(p.sx, p.tx, k)},${E.lerp(p.sy, p.ty, k)}) rotate(${p.rot * (1 - k * 0.4) + Math.sin(t * 6 + p.rot) * 6})`);
      p.g.style.opacity = E.clamp(k * 3);
    }
  };
};

/* A tangle of wires between labelled nodes (things getting complicated). */
COMP.tangle = (s, E) => {
  const dw = E.IS_V ? 940 : 1500, dh = E.IS_V ? 940 : 700, b = E.box(s, dw, dh), r = E.rng(11);
  const names = s.nodes || ['GoHighLevel', 'Claude', 'App builder', 'AI agents', 'Automations', 'Offer', 'Customers', 'Pricing'];
  const pts = names.map((nm, k) => { const a = k / names.length * Math.PI * 2 + 0.3; return { x: dw / 2 + Math.cos(a) * dw * 0.38, y: dh / 2 + Math.sin(a) * dh * 0.38, nm }; });
  const svgNS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(svgNS, 'svg'); svg.setAttribute('width', dw); svg.setAttribute('height', dh); svg.style.position = 'absolute'; b.appendChild(svg);
  const lines = [];
  for (let i = 0; i < 16; i++) {
    const A = pts[Math.floor(r() * pts.length)], B = pts[Math.floor(r() * pts.length)]; if (A === B) continue;
    const p = document.createElementNS(svgNS, 'path');
    const c1x = r() * dw, c1y = r() * dh, c2x = r() * dw, c2y = r() * dh;
    p.setAttribute('d', `M${A.x},${A.y} C${c1x},${c1y} ${c2x},${c2y} ${B.x},${B.y}`);
    p.setAttribute('style', `fill:none;stroke:${i % 3 ? 'var(--line2)' : 'var(--acc)'};stroke-width:5;stroke-linecap:round`);
    svg.appendChild(p); const L = p.getTotalLength ? 2600 : 2600; p.style.strokeDasharray = L; lines.push({ p, L, at: s.t0 + 0.15 + i * 0.12 });
  }
  const nodes = pts.map((pt, k) => { const c = E.el('div', 'pill abs h', b, pt.nm); E.css(c, { left: pt.x + 'px', top: pt.y + 'px', fontSize: '34px', padding: '16px 26px' }); return { c, at: s.t0 + k * 0.08 }; });
  E.cue(s.t0 + 0.3, 'glitch', 0.35);
  return t => {
    lines.forEach(l => { l.p.style.strokeDashoffset = l.L * (1 - E.easeOut(E.seg(t, l.at, l.at + 0.9))); });
    nodes.forEach(({ c, at }, k) => { const q = E.pop(t, at, 16, 0.6); c.style.opacity = E.clamp(q * 2); c.style.transform = `translate(-50%,-50%) scale(${q}) rotate(${Math.sin(t * 7 + k) * 2.5 * E.seg(t, s.t0 + 1, s.t1)}deg)`; });
  };
};

/* Skool-style community page mockup. tab: community | classroom | calendar | about */
COMP.skool = (s, E) => {
  const V = E.IS_V, dw = V ? 860 : 1240, dh = V ? 1000 : 680, b = E.box(s, dw, dh);
  const w = E.el('div', 'win', b); E.css(w, { width: dw + 'px', height: dh + 'px', left: 0, top: 0 });
  const head = E.el('div', '', w); E.css(head, { height: '84px', display: 'flex', alignItems: 'center', gap: '18px', padding: '0 32px', borderBottom: '1.5px solid var(--line)' });
  const logo = E.el('div', 'ico', head, E.icon('users', 30)); E.css(logo, { width: '52px', height: '52px', borderRadius: '14px' });
  E.css(E.el('div', 'h nowrap', head, s.name || 'AI + SaaS Builders'), { fontSize: '30px' });
  const sr = E.el('div', 'pill sub', head, E.icon('search', 22) + (V ? '' : ' Search')); E.css(sr, { marginLeft: 'auto', fontSize: '20px', padding: '10px 18px' });
  const tabs = ['Community', 'Classroom', 'Calendar', 'Members', 'About'].slice(0, V ? 3 : 5);
  const tb = E.el('div', '', w); E.css(tb, { display: 'flex', gap: V ? '34px' : '44px', padding: '0 32px', height: '70px', alignItems: 'center', borderBottom: '1.5px solid var(--line)', fontSize: '25px', fontWeight: 600 });
  const tabEls = tabs.map(x => { const e = E.el('div', 'nowrap', tb, x); E.css(e, { padding: '20px 0', borderBottom: '4px solid transparent', color: 'var(--sub)' }); return e; });
  const tab = s.tab || 'community', ti = Math.max(0, tabs.findIndex(x => x.toLowerCase() === tab));
  tabEls[ti].style.color = 'var(--ink)'; tabEls[ti].style.borderBottomColor = 'var(--acc2)';
  const body = E.el('div', 'abs', w); E.css(body, { left: '32px', right: '32px', top: '186px', bottom: '28px' });
  const bw = dw - 64, bh = dh - 214; const items = [];
  const add = (e, at) => { e._at = at; items.push({ e, at }); return e; };
  if (tab === 'community') {
    const posts = s.posts || [
      { a: 'AG', n: 'Andrew', t: 'New drop: my GoHighLevel onboarding skill', tag: 'Announcement' },
      { a: 'JM', n: 'Member', t: 'Working on my first demo with Claude', tag: 'Wins' },
      { a: 'RS', n: 'Member', t: 'How do I price a SaaS offer for dentists?', tag: 'Questions' },
    ];
    posts.forEach((p, k) => {
      const c = add(E.el('div', 'card abs', body), p.at ? s.wt(p.at, k) : s.t0 + 0.35 + k * 0.45);
      const ph = (bh - 2 * 22) / 3;
      E.css(c, { left: 0, width: bw + 'px', top: k * (ph + 22) + 'px', height: ph + 'px', padding: '24px 28px', display: 'flex', gap: '22px', alignItems: 'center', borderRadius: '18px' });
      const av = E.el('div', 'ico h', c, p.a); E.css(av, { width: '74px', height: '74px', borderRadius: '50%', fontSize: '26px' });
      const tx = E.el('div', '', c); E.css(tx, { minWidth: 0, flex: 1 });
      E.css(E.el('div', 'sub', tx, `${p.n} · <b style="color:var(--acc2)">${p.tag}</b>`), { fontSize: '21px', fontWeight: 600 });
      E.css(E.el('div', 'h', tx, p.t), { fontSize: V ? '31px' : '33px', marginTop: '8px', lineHeight: 1.12 });
      const lk = E.el('div', 'sub', tx, `${E.icon('heart', 20)} &nbsp;${12 + k * 7} &nbsp;&nbsp; ${E.icon('chat', 20)} &nbsp;${4 + k * 3}`); E.css(lk, { fontSize: '20px', marginTop: '10px', display: 'flex', alignItems: 'center' });
      E.cue(c._at, 'pop', 0.4);
    });
  } else if (tab === 'classroom') {
    const courses = s.courses || [{ t: 'Start here', p: 1, i: 'rocket' }, { t: 'GoHighLevel foundations', p: .7, i: 'layers' }, { t: 'Build with AI', p: .45, i: 'spark' }, { t: 'Package your offer', p: .25, i: 'gift' }, { t: 'Get customers', p: .1, i: 'target' }, { t: 'Skills + prompts', p: 0, i: 'file' }];
    const cols = V ? 2 : 3, rows = Math.ceil(courses.length / cols), g = 22, cw = (bw - (cols - 1) * g) / cols, ch = (bh - (rows - 1) * g) / rows;
    courses.forEach((c0, k) => {
      const c = add(E.el('div', 'card abs', body), c0.at ? s.wt(c0.at, k) : s.t0 + 0.3 + k * 0.18);
      E.css(c, { left: (k % cols) * (cw + g) + 'px', top: Math.floor(k / cols) * (ch + g) + 'px', width: cw + 'px', height: ch + 'px', overflow: 'hidden', borderRadius: '18px' });
      const th = E.el('div', '', c, E.icon(c0.i, 60, 'currentColor', 1.8)); E.css(th, { height: '45%', background: k % 2 ? 'var(--thumb2)' : 'var(--thumb1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--thumbink)' });
      E.css(E.el('div', 'h', c, c0.t), { fontSize: '29px', padding: '18px 22px 0', lineHeight: 1.1 });
      const pb = E.el('div', 'abs', c); E.css(pb, { left: '22px', right: '22px', bottom: '22px', height: '12px', borderRadius: '6px', background: 'var(--line)' });
      const fill = E.el('div', '', pb); E.css(fill, { height: '100%', borderRadius: '6px', background: 'var(--acc2)', width: '0%' }); c._fill = fill; c._p = c0.p;
    });
  } else if (tab === 'calendar') {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], cw = bw / 7, rows = 4, ch = (bh - 44) / rows;
    days.forEach((d, k) => E.css(E.el('div', 'sub abs', body, d), { left: k * cw + 10 + 'px', top: 0, fontSize: '21px', fontWeight: 700 }));
    for (let r = 0; r < rows; r++) for (let c = 0; c < 7; c++) { const cell = E.el('div', 'abs', body); E.css(cell, { left: c * cw + 'px', top: 44 + r * ch + 'px', width: cw - 8 + 'px', height: ch - 8 + 'px', borderRadius: '12px', border: '1.5px solid var(--line)' }); E.css(E.el('div', 'sub', cell, String(r * 7 + c + 1)), { fontSize: '18px', padding: '8px 10px', fontWeight: 600 }); }
    const evs = s.events || [{ d: 1, r: 0, t: 'Coaching call' }, { d: 3, r: 1, t: 'Q&A' }, { d: 1, r: 2, t: 'Coaching call' }, { d: 4, r: 2, t: 'New drop' }, { d: 3, r: 3, t: 'Q&A' }];
    evs.forEach((ev, k) => { const e = add(E.el('div', 'abs h nowrap', body, ev.t), ev.at ? s.wt(ev.at, k) : s.t0 + 0.4 + k * 0.3); E.css(e, { left: ev.d * cw + 4 + 'px', top: 44 + ev.r * ch + ch * 0.42 + 'px', width: (V ? cw * 1.9 : cw * 1.6) + 'px', fontSize: V ? '19px' : '21px', padding: '9px 12px', borderRadius: '10px', background: k % 2 ? 'var(--acc)' : 'var(--acc2)', color: k % 2 ? 'var(--accink)' : '#fff', overflow: 'hidden' }); E.cue(e._at, 'pop', 0.4); });
  }
  // camera: start zoomed into the active tab, pull back
  const zoom = s.zoom ?? 1.12;
  return t => {
    const k = E.ease(E.seg(t, s.t0, s.t0 + 1.0));
    w.style.transform = `scale(${E.lerp(zoom, 1, k)})`; w.style.transformOrigin = '30% 20%';
    items.forEach(({ e, at }) => { const q = E.pop(t, at - 0.06, 16, 0.7); e.style.opacity = E.clamp(q * 2); e.style.transform = `translateY(${(1 - q) * 40}px) scale(${E.lerp(0.92, 1, q)})`; if (e._fill) e._fill.style.width = (e._p * 100 * E.easeOut(E.seg(t, at + 0.2, at + 1.2))) + '%'; });
  };
};

/* Steps along a path, each lights on its word. items [{t, i, at}] */
COMP.steps = (s, E) => {
  const V = E.IS_V, n = s.items.length;
  const dw = V ? 860 : 1560, dh = V ? 1000 : 420, b = E.box(s, dw, dh);
  const line = E.el('div', 'abs', b), fill = E.el('div', 'abs', b);
  if (V) { E.css(line, { left: '70px', top: '70px', width: '8px', height: dh - 140 + 'px', background: 'var(--line)', borderRadius: '4px' }); E.css(fill, { left: '70px', top: '70px', width: '8px', background: 'var(--acc)', borderRadius: '4px' }); }
  else { E.css(line, { left: dw / (2 * n) + 'px', right: dw / (2 * n) + 'px', top: '100px', height: '8px', background: 'var(--line)', borderRadius: '4px' }); E.css(fill, { left: dw / (2 * n) + 'px', top: '100px', height: '8px', background: 'var(--acc)', borderRadius: '4px' }); }
  const els = s.items.map((it, k) => {
    const x = V ? 74 : dw / n * (k + 0.5), y = V ? 70 + (dh - 140) * (n > 1 ? k / (n - 1) : 0) : 104;
    const dot = E.el('div', 'ico abs', b, E.icon(it.i || 'check', 54)); E.css(dot, { width: '128px', height: '128px', borderRadius: '50%', left: x - 64 + 'px', top: y - 64 + 'px', border: '6px solid var(--bg)' });
    const lab = E.el('div', 'h abs nowrap', b, it.t);
    if (V) E.css(lab, { left: '180px', top: y - 30 + 'px', fontSize: '54px' }); else E.css(lab, { left: x + 'px', top: '200px', fontSize: '46px', transform: 'translateX(-50%)', textAlign: 'center' });
    if (it.d) { const d = E.el('div', 'sub abs nowrap', b, it.d); if (V) E.css(d, { left: '180px', top: y + 34 + 'px', fontSize: '28px', fontWeight: 600 }); else E.css(d, { left: x + 'px', top: '262px', fontSize: '28px', transform: 'translateX(-50%)', fontWeight: 600 }); lab._d = d; }
    const at = tm(s, it, k, n); E.cue(at - 0.02, 'tick', 0.7);
    return { dot, lab, at, k };
  });
  return t => {
    let prog = 0;
    els.forEach(({ dot, lab, at, k }) => {
      const q = E.pop(t, at - 0.08, 16, 0.55), on = t > at - 0.05;
      dot.style.transform = `scale(${E.lerp(0.4, 1, E.clamp(q, 0, 1.3))})`; dot.style.opacity = E.clamp(0.35 + q);
      dot.classList.toggle('on', on);
      lab.style.opacity = E.clamp(q * 2) * 1; if (lab._d) lab._d.style.opacity = E.clamp(q * 2);
      if (!V) lab.style.transform = `translateX(-50%) translateY(${(1 - q) * 30}px)`; else lab.style.transform = `translateX(${(1 - q) * 40}px)`;
      if (on) prog = Math.max(prog, k + E.easeOut(E.seg(t, at, at + 0.5)) * 0);
      if (t > at) prog = Math.max(prog, k);
    });
    const total = n - 1;
    const last = els.findIndex(e => t < e.at); const cur = last < 0 ? total : Math.max(0, last - 1);
    const nextAt = last < 0 ? 0 : els[last].at, prevAt = els[cur].at;
    const frac = last < 0 ? 0 : E.easeOut(E.seg(t, prevAt + 0.2, nextAt - 0.05)) * 0.0;
    const p = (cur + frac) / Math.max(1, total);
    if (V) fill.style.height = (dh - 140) * p + 'px'; else fill.style.width = (dw - dw / n) * p + 'px';
  };
};

/* File cards downloading. items [{t, at, ext}] */
COMP.files = (s, E) => {
  const n = s.items.length, V = E.IS_V, fw = V ? 820 : 430, fh = V ? 210 : 470, g = 34;
  const dw = V ? fw : n * fw + (n - 1) * g, dh = V ? n * fh + (n - 1) * g : fh, b = E.box(s, dw, dh);
  const els = s.items.map((it, k) => {
    const c = E.el('div', 'card abs', b);
    E.css(c, { width: fw + 'px', height: fh + 'px', left: V ? 0 : k * (fw + g) + 'px', top: V ? k * (fh + g) + 'px' : 0, padding: '34px', display: 'flex', flexDirection: V ? 'row' : 'column', gap: '26px', alignItems: V ? 'center' : 'flex-start' });
    const ic = E.el('div', 'ico', c, E.icon(it.i || 'file', 58)); E.css(ic, { width: '110px', height: '110px', borderRadius: '26px' });
    const tx = E.el('div', '', c); E.css(tx, { flex: 1, width: '100%' });
    E.css(E.el('div', 'h', tx, it.t), { fontSize: '42px' });
    E.css(E.el('div', 'sub', tx, it.d || ''), { fontSize: '25px', fontWeight: 600, marginTop: '8px' });
    const pb = E.el('div', '', tx); E.css(pb, { height: '14px', borderRadius: '7px', background: 'var(--line)', marginTop: '24px', overflow: 'hidden' });
    const fl = E.el('div', '', pb); E.css(fl, { height: '100%', background: 'var(--acc2)', width: '0' });
    const dn = E.el('div', 'ico', c, E.icon('down', 40)); E.css(dn, { width: '80px', height: '80px', borderRadius: '50%', marginLeft: V ? '0' : 'auto', alignSelf: V ? 'center' : 'flex-end' });
    const at = tm(s, it, k, n); E.cue(at, 'pop', 0.5); E.cue(at + 1.0, 'tick', 0.5);
    return { c, fl, dn, at };
  });
  return t => els.forEach(({ c, fl, dn, at }) => {
    const q = E.pop(t, at - 0.08, 16, 0.65); c.style.opacity = E.clamp(q * 2); c.style.transform = `translateY(${(1 - q) * 70}px) scale(${E.lerp(0.85, 1, q)})`;
    const p = E.easeOut(E.seg(t, at + 0.15, at + 1.0)); fl.style.width = p * 100 + '%';
    dn.innerHTML = E.icon(p >= 1 ? 'check' : 'down', 40); dn.classList.toggle('on', p >= 1);
  });
};

/* Line chart rising with a label. */
COMP.growth = (s, E) => {
  const dw = E.IS_V ? 940 : 1400, dh = E.IS_V ? 800 : 640, b = E.box(s, dw, dh);
  const c = E.el('div', 'card abs', b); E.css(c, { inset: 0, padding: '40px' });
  E.css(E.el('div', 'h', c, s.title || 'Online business'), { fontSize: '50px' });
  E.css(E.el('div', 'sub', c, s.sub || 'Growing'), { fontSize: '27px', fontWeight: 600, marginTop: '8px' });
  const svgNS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(svgNS, 'svg'); const gw = dw - 80, gh = dh - 220; svg.setAttribute('width', gw); svg.setAttribute('height', gh); E.css(svg, { position: 'absolute', left: '40px', bottom: '40px', overflow: 'visible' }); c.appendChild(svg);
  const N = 9, r = E.rng(5), pts = Array.from({ length: N }, (_, i) => [i / (N - 1) * gw, gh - (0.08 + 0.84 * Math.pow(i / (N - 1), 1.6) + (r() - .5) * 0.08) * gh]);
  for (let i = 1; i < 4; i++) { const l = document.createElementNS(svgNS, 'line'); l.setAttribute('x1', 0); l.setAttribute('x2', gw); l.setAttribute('y1', gh * i / 4); l.setAttribute('y2', gh * i / 4); l.setAttribute('style', 'stroke:var(--line);stroke-width:2;stroke-dasharray:6 10'); svg.appendChild(l); }
  const area = document.createElementNS(svgNS, 'path'); area.setAttribute('style', 'fill:var(--acc2);opacity:.14'); svg.appendChild(area);
  const p = document.createElementNS(svgNS, 'path'); p.setAttribute('d', 'M' + pts.map(q => q.join(',')).join(' L')); p.setAttribute('style', 'fill:none;stroke:var(--acc2);stroke-width:9;stroke-linecap:round;stroke-linejoin:round'); svg.appendChild(p);
  const L = 3000; p.style.strokeDasharray = L;
  const dot = document.createElementNS(svgNS, 'circle'); dot.setAttribute('r', 16); dot.setAttribute('style', 'fill:var(--acc);stroke:var(--card);stroke-width:6'); svg.appendChild(dot);
  const badges = (s.badges || []).map((bd, k) => { const e = E.el('div', 'pill abs h', c, bd.t); E.css(e, { right: '40px', top: 40 + k * 76 + 'px', fontSize: '30px', background: 'var(--acc2)', color: '#fff', borderColor: 'transparent' }); const at = bd.at ? s.wt(bd.at, k) : s.t0 + 1 + k * .4; E.cue(at, 'pop', .5); return { e, at }; });
  return t => {
    const k = E.ease(E.seg(t, s.t0 + 0.2, s.t1 - 0.2));
    p.style.strokeDashoffset = L * (1 - k);
    const m = k * (N - 1), i = Math.min(N - 2, Math.floor(m)), f = m - i;
    const x = E.lerp(pts[i][0], pts[i + 1][0], f), y = E.lerp(pts[i][1], pts[i + 1][1], f);
    dot.setAttribute('cx', x); dot.setAttribute('cy', y);
    area.setAttribute('d', 'M0,' + gh + ' L' + pts.slice(0, i + 1).map(q => q.join(',')).join(' L') + ` L${x},${y} L${x},${gh} Z`);
    badges.forEach(({ e, at }) => { const q = E.pop(t, at - .06, 16, .6); e.style.opacity = E.clamp(q * 2); e.style.transform = `scale(${E.lerp(.6, 1, q)})`; });
  };
};

/* You-are-here map: pin, three branches, one gets picked. */
COMP.map = (s, E) => {
  const V = E.IS_V, dw = V ? 940 : 1400, dh = V ? 940 : 640, b = E.box(s, dw, dh);
  const svgNS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(svgNS, 'svg'); svg.setAttribute('width', dw); svg.setAttribute('height', dh); svg.style.position = 'absolute'; b.appendChild(svg);
  const o = V ? [dw / 2, dh - 110] : [170, dh / 2];
  const ends = (s.options || ['Option A', 'Option B', 'Option C']).map((nm, k) => V ? [dw * (0.18 + k * 0.32), 130, nm] : [dw - 260, dh * (0.16 + k * 0.34), nm]);
  const paths = ends.map(([x, y], k) => { const p = document.createElementNS(svgNS, 'path'); const d = V ? `M${o[0]},${o[1]} C${o[0]},${o[1] - 300} ${x},${y + 340} ${x},${y + 60}` : `M${o[0]},${o[1]} C${o[0] + 380},${o[1]} ${x - 420},${y} ${x - 140},${y}`; p.setAttribute('d', d); p.setAttribute('style', 'fill:none;stroke:var(--line2);stroke-width:8;stroke-linecap:round;stroke-dasharray:2 20'); svg.appendChild(p); return p; });
  const pick = s.pick ?? 1;
  const hp = document.createElementNS(svgNS, 'path'); hp.setAttribute('d', paths[pick].getAttribute('d')); hp.setAttribute('style', 'fill:none;stroke:var(--acc);stroke-width:12;stroke-linecap:round'); svg.appendChild(hp); hp.style.strokeDasharray = 2000;
  const pin = E.el('div', 'ico abs', b, E.icon('pin', 56)); E.css(pin, { width: '110px', height: '110px', borderRadius: '50%', left: o[0] - 55 + 'px', top: o[1] - 55 + 'px' });
  const yl = E.el('div', 'h abs nowrap', b, s.here || 'You are here'); E.css(yl, V ? { left: o[0] + 'px', top: o[1] + 70 + 'px', transform: 'translateX(-50%)', fontSize: '36px' } : { left: o[0] - 70 + 'px', top: o[1] + 76 + 'px', fontSize: '34px' });
  const labs = ends.map(([x, y, nm], k) => { const e = E.el('div', 'pill abs h', b, nm); E.css(e, V ? { left: x + 'px', top: y + 'px', transform: 'translate(-50%,-50%)', fontSize: '30px', padding: '14px 20px' } : { left: x - 130 + 'px', top: y + 'px', transform: 'translateY(-50%)', fontSize: '34px' }); return e; });
  const tPick = s.wt(s.pickAt || 'next step', 1.5); E.cue(tPick, 'click', .7); E.cue(tPick + .5, 'pop', .5);
  return t => {
    paths.forEach((p, k) => { p.style.opacity = E.clamp((t - s.t0 - 0.2 - k * .15) * 3); });
    labs.forEach((e, k) => { const q = E.pop(t, s.t0 + 0.4 + k * .2, 15, .6); e.style.opacity = E.clamp(q * 2) * (t > tPick && k !== pick ? 0.45 : 1); e.classList.toggle('lit', t > tPick + .4 && k === pick); });
    hp.style.strokeDashoffset = 2000 * (1 - E.ease(E.seg(t, tPick, tPick + 0.8)));
    E.show(pin, E.pop(t, s.t0, 14, .55), 30, .4);
  };
};

/* GoHighLevel-style pipeline mockup: cards slide across stages. */
COMP.ghl = (s, E) => {
  const V = E.IS_V, dw = V ? 860 : 1280, dh = V ? 980 : 680, b = E.box(s, dw, dh);
  const w = E.el('div', 'win', b); E.css(w, { inset: 0, width: dw + 'px', height: dh + 'px' });
  const side = E.el('div', 'abs', w); const sw = V ? 0 : 250; E.css(side, { left: 0, top: 0, bottom: 0, width: sw + 'px', background: 'var(--side)', padding: '26px 18px', display: V ? 'none' : 'block' });
  ['Dashboard', 'Conversations', 'Calendars', 'Contacts', 'Opportunities', 'Automation', 'Sites'].forEach((x, k) => { const e = E.el('div', 'nowrap', side, x); E.css(e, { padding: '13px 16px', borderRadius: '10px', fontSize: '20px', fontWeight: 600, color: k === 4 ? '#fff' : 'var(--sideink)', background: k === 4 ? 'var(--acc2)' : 'transparent', marginBottom: '6px' }); });
  const main = E.el('div', 'abs', w); E.css(main, { left: sw + 30 + 'px', right: '30px', top: '24px', bottom: '24px' });
  E.css(E.el('div', 'h nowrap', main, s.title || 'Opportunities · Pipeline'), { fontSize: '34px' });
  const cols = s.cols || ['New lead', 'Contacted', 'Booked', 'Won'], mw = dw - sw - 60, cw = (mw - (cols.length - 1) * 16) / cols.length, top = 74;
  cols.forEach((c, k) => { const col = E.el('div', 'abs', main); E.css(col, { left: k * (cw + 16) + 'px', top: top + 'px', width: cw + 'px', bottom: 0, background: 'var(--colbg)', borderRadius: '14px' }); E.css(E.el('div', 'sub nowrap', col, c), { fontSize: V ? '20px' : '21px', fontWeight: 700, padding: '14px 14px' }); });
  const names = s.cards || ['Bright Smiles Dental', 'Peak Roofing', 'Glow Med Spa', 'Coastal Realty', 'Iron Gym'];
  const r = E.rng(9);
  const cards = names.map((nm, k) => {
    const c = E.el('div', 'card abs', main); E.css(c, { width: cw - 20 + 'px', height: (V ? 128 : 110) + 'px', padding: '14px 16px', borderRadius: '12px', boxShadow: 'none' });
    E.css(E.el('div', 'h', c, nm), { fontSize: V ? '22px' : '23px', lineHeight: 1.1 }); E.css(E.el('div', 'skel', c), { width: '60%', marginTop: '12px', height: '10px' });
    const moves = [0, Math.min(cols.length - 1, 1 + (k % 3)), Math.min(cols.length - 1, 2 + (k % 2))];
    return { c, k, moves, row: k % 3, at: s.t0 + 0.3 + k * 0.25 };
  });
  const span = s.t1 - s.t0;
  cards.forEach(cd => { E.cue(cd.at + span * 0.35 + cd.k * 0.2, 'click', 0.35); });
  return t => {
    const k0 = E.ease(E.seg(t, s.t0, s.t0 + 1.1)); w.style.transform = `scale(${E.lerp(1.08, 1, k0)})`;
    cards.forEach(cd => {
      const a = E.pop(t, cd.at, 15, .7);
      const st = E.ease(E.seg(t, cd.at + span * 0.35 + cd.k * 0.2, cd.at + span * 0.35 + cd.k * 0.2 + 0.5)), st2 = E.ease(E.seg(t, cd.at + span * 0.6 + cd.k * 0.15, cd.at + span * 0.6 + cd.k * 0.15 + 0.5));
      const colx = E.lerp(E.lerp(cd.moves[0], cd.moves[1], st), cd.moves[2], st2);
      const rowsUsed = cd.row;
      cd.c.style.left = colx * (cw + 16) + 10 + 'px'; cd.c.style.top = top + 54 + rowsUsed * (V ? 142 : 124) + 'px';
      cd.c.style.opacity = E.clamp(a * 2); cd.c.style.transform = `scale(${E.lerp(.8, 1, a) + 0.04 * Math.sin(Math.PI * Math.max(st * (1 - st2), 0))}) rotate(${(st > 0 && st < 1) || (st2 > 0 && st2 < 1) ? 2 : 0}deg)`;
    });
  };
};

/* Automation workflow: nodes connected top to bottom. items [{t, d, i, at}] */
COMP.workflow = (s, E) => {
  const V = E.IS_V, n = s.items.length, nw = V ? 760 : 560, nh = 130, g = V ? 70 : 60;
  const horiz = !V && s.horiz !== false;
  const dw = horiz ? n * nw * 0.62 + (n - 1) * 50 : nw, dh = horiz ? 360 : n * nh + (n - 1) * g;
  const b = E.box(s, dw, dh);
  const els = s.items.map((it, k) => {
    const c = E.el('div', 'card abs', b); const x = horiz ? k * (nw * 0.62 + 50) : 0, y = horiz ? (k % 2 ? 190 : 40) : k * (nh + g);
    E.css(c, { left: x + 'px', top: y + 'px', width: (horiz ? nw * 0.62 : nw) + 'px', height: nh + 'px', display: 'flex', alignItems: 'center', gap: '20px', padding: '0 24px', borderRadius: '20px' });
    const ic = E.el('div', 'ico', c, E.icon(it.i || 'bolt', 40)); E.css(ic, { width: '76px', height: '76px', borderRadius: '20px' });
    const tx = E.el('div', '', c); E.css(E.el('div', 'sub nowrap', tx, it.d || (k ? 'Action' : 'Trigger')), { fontSize: '20px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em' }); E.css(E.el('div', 'h nowrap', tx, it.t), { fontSize: '33px', marginTop: '4px' });
    let con; if (k) { con = E.el('div', 'abs', b); if (horiz) E.css(con, { left: x - 50 + 'px', top: (k % 2 ? 190 : 40) + (k % 2 ? 0 : nh) - (k % 2 ? 0 : 0) + 'px', width: '50px', height: '6px', background: 'var(--acc)', borderRadius: '3px', top: 40 + nh / 2 + (k % 2 ? 75 : 75) + 'px' }); else E.css(con, { left: nw / 2 - 3 + 'px', top: y - g + 'px', width: '6px', height: g + 'px', background: 'var(--acc)', borderRadius: '3px', transformOrigin: 'top' }); }
    const at = tm(s, it, k, n); E.cue(at - .02, 'pop', .5);
    return { c, con, at };
  });
  let done; if (s.done) { done = E.el('div', 'pill abs h', b, E.icon('check', 30) + ' ' + s.done); E.css(done, horiz ? { left: dw / 2 + 'px', top: dh + 30 + 'px', fontSize: '32px', background: 'var(--acc)', color: 'var(--accink)', borderColor: 'transparent' } : { left: nw / 2 + 'px', top: dh + 30 + 'px', fontSize: '32px', background: 'var(--acc)', color: 'var(--accink)', borderColor: 'transparent' }); }
  const tDone = s.done ? s.wt(s.doneAt || 'zzzz', 99) : 0; const tD = Math.min(tDone, s.t1 - 0.7); if (done) E.cue(tD, 'pop', .7);
  return t => {
    els.forEach(({ c, con, at }) => { const q = E.pop(t, at - .08, 16, .65); c.style.opacity = E.clamp(q * 2); c.style.transform = `translateY(${(1 - q) * 40}px) scale(${E.lerp(.85, 1, q)})`; if (con) { const p = E.easeOut(E.seg(t, at - .25, at)); con.style.transform = horiz ? `scaleX(${p})` : `scaleY(${p})`; con.style.transformOrigin = horiz ? 'left' : 'top'; } });
    if (done) { const q = E.pop(t, tD, 14, .55); done.style.opacity = E.clamp(q * 2); done.style.transform = `translateX(-50%) scale(${E.lerp(.5, 1, q)})`; }
  };
};

/* Claude-style chat: prompt types, answer streams. */
COMP.claude = (s, E) => {
  const V = E.IS_V, dw = V ? 940 : 1300, dh = V ? 980 : 700, b = E.box(s, dw, dh);
  const w = E.el('div', 'win', b); E.css(w, { width: dw + 'px', height: dh + 'px' });
  const bar = E.el('div', 'bar', w, '<i></i><i></i><i></i>'); E.css(E.el('span', 'h', bar, 'Claude'), { marginLeft: '12px', color: 'var(--ink)', fontSize: '22px' });
  const msg = E.el('div', 'abs', w); E.css(msg, { right: '36px', top: '84px', maxWidth: '78%', background: 'var(--colbg)', borderRadius: '20px', padding: '22px 26px', fontSize: V ? '32px' : '31px', fontWeight: 600, lineHeight: 1.3 });
  const full = s.prompt || 'Help me turn this idea into an offer';
  const ans = E.el('div', 'abs', w); E.css(ans, { left: '36px', right: '36px', top: V ? '330px' : '280px' });
  const aIc = E.el('div', 'ico', ans, E.icon('spark', 34)); E.css(aIc, { width: '62px', height: '62px', borderRadius: '50%', marginBottom: '20px' });
  const lines = (s.answer || ['1. Pick one customer', '2. Name the problem you solve', '3. Build the smallest version', '4. Price it and test it']).map((l, k) => { const e = E.el('div', 'h', ans, l); E.css(e, { fontSize: V ? '38px' : '40px', marginBottom: '20px', lineHeight: 1.15 }); return e; });
  const t0 = s.t0 + 0.2, tType = t0 + full.length / 28;
  E.cue(t0, 'typing', 0.5); E.cue(tType + 0.15, 'click', 0.5);
  return t => {
    const n = Math.floor(E.clamp((t - t0) * 28, 0, full.length));
    msg.innerHTML = full.slice(0, n) + (t < tType + 0.3 && Math.floor(t * 3) % 2 === 0 ? '<span style="opacity:.6">|</span>' : '');
    msg.style.opacity = t > t0 - 0.05 ? 1 : 0;
    E.show(aIc, E.pop(t, tType + 0.2, 16, .6), 10, .5);
    lines.forEach((l, k) => { const q = E.soft(t, tType + 0.45 + k * 0.38, 16); l.style.opacity = q; l.style.transform = `translateY(${(1 - q) * 20}px)`; l.style.clipPath = `inset(0 ${100 - q * 100}% 0 0)`; });
  };
};

/* App builder: wireframe blocks snap together into an app. */
COMP.appbuild = (s, E) => {
  const V = E.IS_V, dw = V ? 860 : 1300, dh = V ? 1000 : 720, b = E.box(s, dw, dh);
  const w = E.el('div', 'win', b); E.css(w, { width: dw + 'px', height: dh + 'px' });
  E.el('div', 'bar', w, '<i></i><i></i><i></i><span style="margin-left:14px">' + (s.title || 'my-app.preview') + '</span>');
  const blocks = V ? [[30, 80, 800, 90, 'nav'], [30, 200, 800, 300, 'hero'], [30, 530, 385, 200, 'c'], [445, 530, 385, 200, 'c'], [30, 760, 800, 180, 'btn']]
    : [[30, 80, 1240, 80, 'nav'], [30, 190, 760, 300, 'hero'], [820, 190, 450, 300, 'img'], [30, 520, 390, 170, 'c'], [455, 520, 390, 170, 'c'], [880, 520, 390, 170, 'c']];
  const r = E.rng(4);
  const els = blocks.map(([x, y, bw, bh, kind], k) => {
    const e = E.el('div', 'abs', w); E.css(e, { left: x + 'px', top: y + 'px', width: bw + 'px', height: bh + 'px', borderRadius: '16px', background: kind === 'hero' ? 'var(--acc2)' : kind === 'img' ? 'var(--acc)' : kind === 'btn' ? 'var(--acc)' : 'var(--colbg)', padding: '26px', color: kind === 'hero' ? '#fff' : 'var(--ink)' });
    if (kind === 'hero') { E.css(E.el('div', 'h', e, s.hero || 'Your idea, live'), { fontSize: V ? '60px' : '64px' }); E.css(E.el('div', 'skel', e), { width: '70%', marginTop: '26px', background: 'rgba(255,255,255,.45)' }); E.css(E.el('div', 'skel', e), { width: '50%', marginTop: '14px', background: 'rgba(255,255,255,.45)' }); }
    if (kind === 'c') { E.css(E.el('div', 'ico', e, E.icon(['bolt', 'users', 'chart'][k % 3], 34)), { width: '64px', height: '64px' }); E.css(E.el('div', 'skel', e), { width: '70%', marginTop: '22px' }); }
    if (kind === 'btn') { E.css(e, { display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accink)' }); E.css(E.el('div', 'h', e, s.btn || 'Get started'), { fontSize: '46px' }); }
    if (kind === 'nav') { E.css(e, { display: 'flex', alignItems: 'center', gap: '20px', padding: '0 26px' }); E.css(E.el('div', 'skel', e), { width: '140px', height: '18px', background: 'var(--ink)' }); for (let i = 0; i < 3; i++) E.css(E.el('div', 'skel', e), { width: '90px' }); }
    const at = s.t0 + 0.2 + k * ((s.t1 - s.t0 - 0.8) / blocks.length);
    E.cue(at + 0.15, 'click', 0.4);
    return { e, at, dx: (r() - .5) * 500, dy: (r() - .5) * 400, rot: (r() - .5) * 30 };
  });
  return t => els.forEach(({ e, at, dx, dy, rot }) => { const q = E.spring(t - at, 14, .72); e.style.opacity = E.clamp(q * 2.5); e.style.transform = `translate(${dx * (1 - q)}px,${dy * (1 - q)}px) rotate(${rot * (1 - q)}deg) scale(${E.lerp(.6, 1, q)})`; });
};

/* Hub: centre node, spokes draw to labelled nodes. */
COMP.hub = (s, E) => {
  const V = E.IS_V, dw = V ? 940 : 1400, dh = V ? 940 : 700, b = E.box(s, dw, dh);
  const names = s.nodes || ['GoHighLevel', 'Claude', 'AI agents', 'Automations'];
  const cx = dw / 2, cy = dh / 2, rx = dw * 0.36, ry = dh * 0.36;
  const svgNS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(svgNS, 'svg'); svg.setAttribute('width', dw); svg.setAttribute('height', dh); svg.style.position = 'absolute'; b.appendChild(svg);
  const nodes = names.map((nm, k) => {
    const a = -Math.PI / 2 + k / names.length * Math.PI * 2 + (s.rot || Math.PI / names.length), x = cx + Math.cos(a) * rx, y = cy + Math.sin(a) * ry;
    const l = document.createElementNS(svgNS, 'line'); l.setAttribute('x1', cx); l.setAttribute('y1', cy); l.setAttribute('x2', x); l.setAttribute('y2', y); l.setAttribute('style', 'stroke:var(--acc);stroke-width:7;stroke-linecap:round'); svg.appendChild(l);
    const e = E.el('div', 'pill abs h', b, nm); E.css(e, { left: x + 'px', top: y + 'px', fontSize: '36px', padding: '18px 28px' });
    const at = s.items && s.items[k] && s.items[k].at ? s.wt(s.items[k].at, k) : s.t0 + 0.3 + k * 0.3; E.cue(at, 'pop', .45);
    return { l, e, x, y, at };
  });
  const c = E.el('div', 'ico abs', b, s.center ? `<span class="h" style="font-size:40px;text-align:center;line-height:1.05">${s.center}</span>` : E.icon(s.icon || 'users', 90)); E.css(c, { width: '240px', height: '240px', borderRadius: '50%', left: cx - 120 + 'px', top: cy - 120 + 'px', background: 'var(--acc)', color: 'var(--accink)' });
  const tJoin = s.t1 - 0.9; E.cue(tJoin, 'impact', .5);
  return t => {
    E.show(c, E.pop(t, s.t0 + 0.05, 14, .6), 0, .4);
    nodes.forEach(({ l, e, x, y, at }) => {
      const q = E.pop(t, at, 15, .6); e.style.opacity = E.clamp(q * 2); e.style.transform = `translate(-50%,-50%) scale(${E.lerp(.5, 1, q)})`;
      const p = E.easeOut(E.seg(t, at + 0.1, at + 0.5)); l.setAttribute('x2', E.lerp(cx, x, p)); l.setAttribute('y2', E.lerp(cy, y, p));
    });
    const pulse = E.seg(t, tJoin, tJoin + 0.6); c.style.boxShadow = `0 0 0 ${pulse * 60}px rgba(255,210,63,${0.35 * (1 - pulse)})`;
  };
};

/* Coaching call window (no faces: initials tiles + waveform). */
COMP.call = (s, E) => {
  const V = E.IS_V, dw = V ? 940 : 1300, dh = V ? 980 : 700, b = E.box(s, dw, dh);
  const w = E.el('div', 'win', b); E.css(w, { width: dw + 'px', height: dh + 'px' });
  const bar = E.el('div', 'bar', w, '<i></i><i></i><i></i>'); E.css(E.el('span', 'h', bar, s.title || 'Weekly coaching call'), { marginLeft: '12px', color: 'var(--ink)', fontSize: '22px' });
  const live = E.el('div', 'pill h', bar, '● LIVE'); E.css(live, { marginLeft: 'auto', background: '#E5484D', color: '#fff', borderColor: 'transparent', fontSize: '18px', padding: '6px 14px' });
  const ini = s.people || ['AG', 'JM', 'RS', 'TK', 'LB', 'MC'], cols = V ? 2 : 3, rows = Math.ceil(ini.length / cols), g = 18, gw = dw - 60, gh = dh - 50 - 60 - 120;
  const tw = (gw - (cols - 1) * g) / cols, th = (gh - (rows - 1) * g) / rows;
  const tiles = ini.map((x, k) => {
    const tl = E.el('div', 'abs', w); E.css(tl, { left: 30 + (k % cols) * (tw + g) + 'px', top: 80 + Math.floor(k / cols) * (th + g) + 'px', width: tw + 'px', height: th + 'px', borderRadius: '18px', background: k ? 'var(--colbg)' : 'var(--acc2)', display: 'flex', alignItems: 'center', justifyContent: 'center' });
    const av = E.el('div', 'h', tl, x); E.css(av, { width: '110px', height: '110px', borderRadius: '50%', background: k ? 'var(--card)' : 'rgba(255,255,255,.2)', color: k ? 'var(--ink)' : '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '38px' });
    return { tl, at: s.t0 + 0.2 + k * 0.15 };
  });
  const wave = E.el('div', 'abs', w); E.css(wave, { left: '30px', right: '30px', bottom: '30px', height: '90px', display: 'flex', alignItems: 'center', gap: '6px' });
  const bars = Array.from({ length: 60 }, () => { const x = E.el('div', '', wave); E.css(x, { flex: 1, background: 'var(--acc)', borderRadius: '4px' }); return x; });
  const words = s.words;
  return t => {
    tiles.forEach(({ tl, at }, k) => { const q = E.pop(t, at, 15, .65); tl.style.opacity = E.clamp(q * 2); tl.style.transform = `scale(${E.lerp(.7, 1, q)})`; tl.style.outline = k === 0 ? `${4 + 3 * Math.abs(Math.sin(t * 8))}px solid var(--acc)` : 'none'; });
    const speaking = words.some(w => t >= w.s && t <= w.e + 0.05);
    bars.forEach((x, i) => { const h = speaking ? 20 + 70 * Math.abs(Math.sin(t * 11 + i * 0.7) * Math.sin(t * 5.3 + i * 0.31)) : 10; x.style.height = h + 'px'; });
  };
};

/* Video player (watching someone build). */
COMP.video = (s, E) => {
  const V = E.IS_V, dw = V ? 940 : 1300, dh = V ? 760 : 700, b = E.box(s, dw, dh);
  const w = E.el('div', 'win', b); E.css(w, { width: dw + 'px', height: dh + 'px', background: 'var(--player)' });
  const scr = E.el('div', 'abs', w); E.css(scr, { left: '40px', top: '40px', right: '40px', bottom: '140px', borderRadius: '14px', background: 'var(--card)', overflow: 'hidden' });
  for (let i = 0; i < 6; i++) E.css(E.el('div', 'skel abs', scr), { left: '40px', top: 40 + i * 56 + 'px', width: (30 + (i * 37) % 55) + '%', height: '20px' });
  const play = E.el('div', 'ico abs', w, E.icon('play', 70)); E.css(play, { width: '160px', height: '160px', borderRadius: '50%', left: dw / 2 - 80 + 'px', top: (dh - 100) / 2 - 80 + 'px', background: 'var(--acc)', color: 'var(--accink)' });
  const pb = E.el('div', 'abs', w); E.css(pb, { left: '40px', right: '40px', bottom: '70px', height: '14px', borderRadius: '7px', background: 'rgba(255,255,255,.2)' });
  const fl = E.el('div', '', pb); E.css(fl, { height: '100%', borderRadius: '7px', background: 'var(--acc)' });
  const lab = E.el('div', 'h abs nowrap', w, s.title || 'Watch the build'); E.css(lab, { left: '40px', bottom: '20px', color: '#fff', fontSize: '28px' });
  E.cue(s.t0 + .4, 'click', .6);
  return t => { const k = E.pop(t, s.t0 + 0.4, 18, .5); play.style.transform = `scale(${t < s.t0 + .4 ? 1 : E.lerp(1, 0, E.seg(t, s.t0 + .4, s.t0 + .7))})`; fl.style.width = E.seg(t, s.t0 + .4, s.t1 + 2) * 100 + '%'; };
};

/* Post composer: types a post, publishes, likes pop. */
COMP.composer = (s, E) => {
  const V = E.IS_V, dw = V ? 940 : 1200, dh = V ? 860 : 640, b = E.box(s, dw, dh);
  const c = E.el('div', 'card abs', b); E.css(c, { inset: 0, padding: '40px' });
  const hd = E.el('div', '', c); E.css(hd, { display: 'flex', alignItems: 'center', gap: '20px' });
  E.css(E.el('div', 'ico h', hd, 'You'), { width: '84px', height: '84px', borderRadius: '50%', fontSize: '26px' });
  E.css(E.el('div', 'sub', hd, s.where || 'Post in <b>Community</b>'), { fontSize: '26px', fontWeight: 600 });
  const tx = E.el('div', 'h', c); E.css(tx, { fontSize: V ? '50px' : '50px', marginTop: '40px', lineHeight: 1.2, minHeight: '200px' });
  const full = s.text || "Here's what I'm working on this week...";
  const btn = E.el('div', 'pill h abs', c, E.icon('send', 28) + ' Post'); E.css(btn, { right: '40px', bottom: '40px', fontSize: '32px', background: 'var(--acc2)', color: '#fff', borderColor: 'transparent', padding: '18px 34px' });
  const re = E.el('div', 'abs', c); E.css(re, { left: '40px', bottom: '46px', display: 'flex', gap: '16px' });
  const pills = (s.reacts || ['12', '5 replies', 'Nice work']).map((x, k) => { const e = E.el('div', 'pill h', re, (k === 0 ? E.icon('heart', 24) + ' ' : k === 1 ? E.icon('chat', 24) + ' ' : '') + x); E.css(e, { fontSize: '26px' }); return e; });
  const t0 = s.t0 + 0.25, tEnd = t0 + full.length / 26, tPost = tEnd + 0.35;
  E.cue(t0, 'typing', .45); E.cue(tPost, 'click', .7);
  pills.forEach((_, k) => E.cue(tPost + 0.45 + k * 0.3, 'pop', .45));
  const cur = E.el('div', 'abs', b, E.CURSOR);
  return t => {
    const n = Math.floor(E.clamp((t - t0) * 26, 0, full.length)); tx.textContent = full.slice(0, n);
    const k = E.ease(E.seg(t, tEnd - 0.4, tPost)); E.at(cur, E.lerp(dw * 0.55, dw - 120, k), E.lerp(dh * 0.4, dh - 80, k), `scale(${t > tPost && t < tPost + .12 ? .85 : 1})`);
    btn.style.transform = `scale(${t > tPost && t < tPost + 0.15 ? .92 : 1})`;
    if (t > tPost) { btn.innerHTML = E.icon('check', 28) + ' Posted'; } else btn.innerHTML = E.icon('send', 28) + ' Post';
    pills.forEach((p, k) => { const q = E.pop(t, tPost + 0.45 + k * 0.3, 18, .55); p.style.opacity = E.clamp(q * 2); p.style.transform = `scale(${E.lerp(.4, 1, q)})`; });
  };
};

/* Inbox of ignored leads. */
COMP.inbox = (s, E) => {
  const V = E.IS_V, dw = V ? 940 : 1200, dh = V ? 980 : 720, b = E.box(s, dw, dh);
  const w = E.el('div', 'win', b); E.css(w, { width: dw + 'px', height: dh + 'px' });
  const bar = E.el('div', 'bar', w, '<i></i><i></i><i></i>'); E.css(E.el('span', 'h', bar, 'Inbox'), { marginLeft: '12px', color: 'var(--ink)', fontSize: '22px' });
  const badge = E.el('div', 'pill h', bar, '0'); E.css(badge, { marginLeft: 'auto', background: '#E5484D', color: '#fff', borderColor: 'transparent', fontSize: '20px', padding: '6px 16px' });
  const leads = s.leads || ['New lead: wants a quote', 'Missed call', 'Form fill: "call me back"', 'New lead: booking request', 'Missed call', 'DM: "are you open?"'];
  const rh = (dh - 80) / leads.length;
  const rows = leads.map((x, k) => {
    const r = E.el('div', 'abs', w); E.css(r, { left: '24px', right: '24px', top: 60 + k * rh + 'px', height: rh - 12 + 'px', display: 'flex', alignItems: 'center', gap: '20px', padding: '0 20px', borderBottom: '1.5px solid var(--line)' });
    E.css(E.el('div', '', r), { width: '18px', height: '18px', borderRadius: '50%', background: '#E5484D', flex: 'none' });
    E.css(E.el('div', 'h nowrap', r, x), { fontSize: V ? '30px' : '32px', flex: 1, overflow: 'hidden' });
    const tmr = E.el('div', 'sub nowrap', r, ''); E.css(tmr, { fontSize: '24px', fontWeight: 700 });
    const at = s.t0 + 0.2 + k * ((s.t1 - s.t0 - 0.6) / leads.length); E.cue(at, 'tick', .55);
    return { r, tmr, at, k };
  });
  return t => {
    let cnt = 0;
    rows.forEach(({ r, tmr, at, k }) => { const q = E.pop(t, at, 16, .7); r.style.opacity = E.clamp(q * 2); r.style.transform = `translateX(${(1 - q) * -60}px)`; if (t > at) cnt++; const hrs = Math.max(0, Math.floor((t - at) * 3)); tmr.textContent = t > at ? `no reply · ${hrs + 1 + k}h` : ''; });
    badge.textContent = cnt;
  };
};

/* Clock spinning + repetitive task bars, then an Automated toggle. */
COMP.clock = (s, E) => {
  const V = E.IS_V, dw = V ? 900 : 1300, dh = V ? 980 : 620, b = E.box(s, dw, dh);
  const cs = V ? 420 : 460;
  const cl = E.el('div', 'card abs', b); E.css(cl, { width: cs + 'px', height: cs + 'px', borderRadius: '50%', left: V ? (dw - cs) / 2 + 'px' : '40px', top: V ? '0' : (dh - cs) / 2 + 'px' });
  const hand1 = E.el('div', 'abs', cl), hand2 = E.el('div', 'abs', cl);
  E.css(hand1, { left: cs / 2 - 5 + 'px', top: cs * 0.18 + 'px', width: '10px', height: cs * 0.32 + 'px', background: 'var(--ink)', borderRadius: '5px', transformOrigin: '50% 100%' });
  E.css(hand2, { left: cs / 2 - 4 + 'px', top: cs * 0.1 + 'px', width: '8px', height: cs * 0.4 + 'px', background: 'var(--acc2)', borderRadius: '4px', transformOrigin: '50% 100%' });
  for (let i = 0; i < 12; i++) { const tk = E.el('div', 'abs', cl); E.css(tk, { left: cs / 2 - 3 + 'px', top: '18px', width: '6px', height: '24px', background: 'var(--line2)', borderRadius: '3px', transformOrigin: `50% ${cs / 2 - 18}px`, transform: `rotate(${i * 30}deg)` }); }
  const list = E.el('div', 'abs', b); E.css(list, V ? { left: '0', right: '0', top: cs + 50 + 'px' } : { left: cs + 120 + 'px', right: '0', top: '40px' });
  const tasks = s.tasks || ['Copy data by hand', 'Send the same follow-up', 'Update the spreadsheet'];
  const rows = tasks.map((x, k) => { const r = E.el('div', 'card', list); E.css(r, { display: 'flex', alignItems: 'center', gap: '18px', padding: '22px 26px', marginBottom: '20px', borderRadius: '18px' }); const ic = E.el('div', 'ico', r, E.icon('clock', 32)); E.css(ic, { width: '60px', height: '60px' }); E.css(E.el('div', 'h nowrap', r, x), { fontSize: '34px' }); return { r, ic, at: s.t0 + 0.3 + k * 0.35 }; });
  const tog = E.el('div', 'pill h', list); E.css(tog, { fontSize: '34px', padding: '18px 28px', marginTop: '10px' });
  const tAuto = s.wt(s.autoAt || 'automated', 1.6); E.cue(tAuto, 'click', .7); E.cue(tAuto + .1, 'pop', .5);
  return t => {
    const spin = t < tAuto ? (t - s.t0) * 900 : (tAuto - s.t0) * 900; hand2.style.transform = `rotate(${spin}deg)`; hand1.style.transform = `rotate(${spin / 12}deg)`;
    rows.forEach(({ r, ic, at }) => { const q = E.pop(t, at, 16, .7); r.style.opacity = E.clamp(q * 2); r.style.transform = `translateY(${(1 - q) * 30}px)`; ic.innerHTML = E.icon(t > tAuto + 0.2 ? 'check' : 'clock', 32); ic.classList.toggle('on', t > tAuto + 0.2); });
    const on = t > tAuto; tog.innerHTML = `<span style="display:inline-block;width:76px;height:42px;border-radius:21px;background:${on ? 'var(--acc)' : 'var(--line)'};position:relative"><span style="position:absolute;top:5px;left:${on ? 39 : 5}px;width:32px;height:32px;border-radius:50%;background:#fff"></span></span> Automated`;
    E.show(tog, E.soft(t, s.t0 + 1.0));
  };
};

/* Stack of blocks building up (foundation -> top). items bottom-first. */
COMP.stack = (s, E) => {
  const V = E.IS_V, n = s.items.length, bw = V ? 820 : 900, bh = V ? 170 : 150, g = 14;
  const dw = bw, dh = n * bh + (n - 1) * g, b = E.box(s, dw, dh);
  const els = s.items.map((it, k) => {
    const c = E.el('div', 'abs', b); const wk = bw * (1 - k * 0.08);
    E.css(c, { left: (bw - wk) / 2 + 'px', width: wk + 'px', top: dh - (k + 1) * bh - k * g + 'px', height: bh + 'px', borderRadius: '22px', background: ['var(--acc2)', 'var(--acc)', 'var(--card)', 'var(--pz3)'][k % 4], color: k % 4 === 0 ? '#fff' : 'var(--ink2)', display: 'flex', alignItems: 'center', gap: '26px', padding: '0 40px', border: '1.5px solid var(--line)' });
    E.css(E.el('div', '', c, E.icon(it.i || 'layers', 58)), { display: 'flex' });
    const tx = E.el('div', '', c); E.css(E.el('div', 'h nowrap', tx, it.t), { fontSize: '50px' }); if (it.d) E.css(E.el('div', 'nowrap', tx, it.d), { fontSize: '26px', fontWeight: 600, opacity: .75, marginTop: '4px' });
    const at = tm(s, it, k, n); E.cue(at + 0.2, 'impact', .45);
    return { c, at };
  });
  return t => els.forEach(({ c, at }) => { const q = E.spring(t - at, 15, .6); c.style.opacity = E.clamp(q * 3); c.style.transform = `translateY(${(1 - q) * -500}px)`; });
};

/* Pie: tools are one slice. */
COMP.pie = (s, E) => {
  const V = E.IS_V, dw = V ? 900 : 1300, dh = V ? 900 : 600, b = E.box(s, dw, dh), R0 = V ? 300 : 260;
  const svgNS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(svgNS, 'svg'); svg.setAttribute('width', 2 * R0 + 40); svg.setAttribute('height', 2 * R0 + 40); E.css(svg, { position: 'absolute', left: V ? (dw - 2 * R0 - 40) / 2 + 'px' : '0', top: V ? '0' : (dh - 2 * R0 - 40) / 2 + 'px', overflow: 'visible' }); b.appendChild(svg);
  const arc = (a0, a1, r) => { const p = a => [R0 + 20 + r * Math.cos(a), R0 + 20 + r * Math.sin(a)]; const [x0, y0] = p(a0), [x1, y1] = p(a1); return `M${R0 + 20},${R0 + 20} L${x0},${y0} A${r},${r} 0 ${a1 - a0 > Math.PI ? 1 : 0} 1 ${x1},${y1} Z`; };
  const rest = document.createElementNS(svgNS, 'path'); rest.setAttribute('style', 'fill:var(--card);stroke:var(--line);stroke-width:3'); svg.appendChild(rest);
  const tool = document.createElementNS(svgNS, 'path'); tool.setAttribute('style', 'fill:var(--acc)'); svg.appendChild(tool);
  const lab = E.el('div', 'abs', b); E.css(lab, V ? { left: 0, right: 0, top: 2 * R0 + 80 + 'px', textAlign: 'center' } : { left: 2 * R0 + 120 + 'px', top: '110px' });
  const L = (s.labels || [['Tools', 'var(--acc)'], ['Customer · Offer · Selling · Delivery', 'var(--sub)']]).map(([x, c], k) => { const e = E.el('div', 'h', lab, `<span style="display:inline-block;width:30px;height:30px;border-radius:8px;background:${c};margin-right:16px;vertical-align:-3px"></span>${x}`); E.css(e, { fontSize: k ? '38px' : '50px', marginBottom: '26px', maxWidth: V ? 'none' : '520px', lineHeight: 1.15 }); return e; });
  E.cue(s.t0 + .2, 'pop', .5);
  return t => {
    const k = E.ease(E.seg(t, s.t0 + 0.1, s.t0 + 0.9)); rest.setAttribute('d', arc(-Math.PI / 2 + 0.0001, -Math.PI / 2 + Math.PI * 2 * k - 0.0001, R0));
    const k2 = E.pop(t, s.t0 + 0.7, 14, .6); tool.setAttribute('d', arc(-Math.PI / 2, -Math.PI / 2 + Math.PI * 0.45, R0 * E.lerp(0.7, 1.08, E.clamp(k2, 0, 1.2))));
    L.forEach((e, q) => E.show(e, E.soft(t, s.t0 + 0.8 + q * 0.5), 20, .95));
  };
};

/* End card with a pulsing join button and a cursor click. */
COMP.outro = (s, E, T) => {
  s.cap = false;
  const V = E.IS_V, box = E.el('div', 'abs', s.root); E.css(box, { inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '40px' });
  const top = E.el('div', 'serif', box, T.outroKicker || 'Come build with us'); E.css(top, { fontSize: V ? '96px' : '80px', textAlign: 'center', padding: '0 60px', color: 'var(--outroink)' });
  const btn = E.el('div', 'h nowrap', box, (T.outroBtn || 'Join the community') + ' ' + E.icon('arrowR', 52, 'currentColor', 2.6)); E.css(btn, { fontSize: V ? '70px' : '72px', padding: '34px 56px', borderRadius: '999px', background: 'var(--btn)', color: 'var(--btnink)', display: 'flex', alignItems: 'center', gap: '18px' });
  const nm = E.el('div', 'h nowrap', box, T.outroName || 'Andrew George'); E.css(nm, { fontSize: '34px', letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--outrosub)' });
  if (T.outroPlaceholder) E.css(nm, { letterSpacing: '0.06em', fontSize: V ? '44px' : '40px', padding: '18px 30px', border: '3px dashed var(--outrosub)', borderRadius: '16px', textTransform: 'none' });
  const cur = E.el('div', 'abs', s.root, E.CURSOR);
  const tClick = s.t0 + 1.6; E.cue(tClick, 'click', .9); E.cue(s.t0 + 0.35, 'impact', .55);
  return t => {
    E.show(top, E.soft(t, s.t0 + 0.05), 20, .95); E.show(nm, E.soft(t, s.t0 + 0.5), 10, .95);
    const q = E.pop(t, s.t0 + 0.25, 14, .55), press = t > tClick && t < tClick + 0.14 ? 0.94 : 1;
    btn.style.opacity = E.clamp(q * 2); btn.style.transform = `scale(${E.lerp(.6, 1, q) * press * (1 + 0.025 * Math.sin(Math.max(0, t - tClick - .2) * 6))})`;
    const r = btn.getBoundingClientRect(), sr = btn.offsetParent ? 1 : 1;
    const k = E.ease(E.seg(t, s.t0 + 0.6, tClick - 0.05));
    const sr2 = s.root.getBoundingClientRect(), scl = sr2.width / E.W || 1; const bx = (r.right - sr2.left) / scl - (V ? 90 : 110), by = (r.top - sr2.top) / scl + r.height / scl * 0.55;
    E.at(cur, E.lerp(E.W * 0.82, bx, k), E.lerp(E.H * 0.92, by, k), `scale(${press < 1 ? .85 : 1})`); cur.style.opacity = E.clamp((t - s.t0 - 0.5) * 4);
  };
};
