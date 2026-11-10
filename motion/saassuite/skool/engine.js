// Skool About / Onboarding engine. window.render(t) is a pure function of time.
// URL: index.html?v=sales|onb&fmt=h|v
const Q = new URLSearchParams(location.search), V = Q.get('v') || 'sales', FMT = Q.get('fmt') || 'h';
const VERT = FMT === 'v', WD = VERT ? 1080 : 1920, HT = VERT ? 1920 : 1080;
document.documentElement.style.cssText = document.body.style.cssText = `width:${WD}px;height:${HT}px`;
const { cl, lerp, ease, spring } = SS;
const W = TIMING[V], SC = SCENES[V];
const $ = id => document.getElementById(id);
const norm = s => s.toLowerCase().replace(/[^a-z0-9']/g, '');
// first word start of `phrase` at or after `after`
function T(phrase, after = 0, end = false) {
  const p = phrase.split(/\s+/).map(norm);
  for (let i = 0; i < W.length; i++) {
    if (W[i].s < after - 0.01) continue;
    let ok = true; for (let k = 0; k < p.length; k++) if (!W[i + k] || norm(W[i + k].w).replace(/-/g, '') !== p[k].replace(/-/g, '')) { ok = false; break; }
    if (ok) return end ? W[i + p.length - 1].e : W[i].s;
  }
  throw new Error('phrase not found: ' + phrase + ' after ' + after);
}
const DUR = W[W.length - 1].e + 3.2;
window.DUR = DUR;

// ---------- headline builder: '|' = new line, *word* = accent ----------
function buildH(el, str) {
  let li = 0, acc = false;
  el.innerHTML = str.split('|').map(line => '<div>' + line.split(' ').map(word => {
    if (word.startsWith('*')) acc = true; const a = acc; const clean = word.replace(/\*/g, '');
    if (/\*[.,!?]*$/.test(word)) acc = false;
    return `<span class="w">` + [...clean].map(c => `<span class="l${a ? ' v' : ''}" data-i="${li++}">${c}</span>`).join('') + '</span>';
  }).join('<span class="l"> </span>') + '</div>').join('');
  el._n = li;
}
function riseH(el, t, t0, st) {
  el.querySelectorAll('.l').forEach(s => {
    const r = SS.letterRise(t, t0, +(s.dataset.i || 0), { stagger: st });
    s.style.transform = `translateY(${r.y}px) rotate(${r.rot}deg)`; s.style.filter = r.blur > 0.2 ? `blur(${r.blur}px)` : 'none'; s.style.opacity = r.op;
  });
}
const CK = '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" stroke="#fff" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const LOCK = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></svg>';
const check = () => `<span class="ckw"><span class="ck0"></span><span class="ck" style="opacity:0">${CK}</span></span>`;
function stampEl(el, t, t0) { const st = SS.stamp(t, t0); el.style.opacity = st.op; el.style.transform = `scale(${t < t0 ? 0 : st.s}) rotate(${st.rot}deg)`; }
function riseEl(el, t, t0, dy = 40) { const w = SS.wordRise(t, t0, 0, { dy }); el.style.opacity = w.op; el.style.transform = `translateY(${w.y}px)`; el.style.filter = w.blur > 0.2 ? `blur(${w.blur}px)` : 'none'; }
function typeEl(el, t, t0, text, cps = 34) { const n = Math.max(0, Math.min(text.length, Math.floor((t - t0) * cps))); el.innerHTML = text.slice(0, n) + (t >= t0 && n < text.length ? '<span class="caret"></span>' : ''); }

// ---------- cards: each returns {html, upd(t, el, at)} where at(phrase) resolves a time inside the scene ----------
const CARDS = {
  chips(c) { // tool cloud, optional collapse into one pill
    const names = c.names; const w = 780, h = VERT ? 500 : 620;
    return {
      html: `<div style="position:relative;width:${w}px;height:${h}px">${names.map(n => `<div class="chip">${n}</div>`).join('')}<div class="pill" style="position:absolute;left:50%;top:50%;font-size:30px;padding:18px 30px;opacity:0" data-k="one">${c.one || ''}</div></div>`,
      upd(t, el, at, s0) {
        const t1 = c.collapse ? at(c.collapse) : 1e9;
        el.querySelectorAll('.chip').forEach((d, i) => {
          const col = 4, rx = (i % col) / (col - 1), ry = Math.floor(i / col) / Math.max(1, Math.ceil(names.length / col) - 1);
          const x0 = 20 + rx * (w - 230) + (Math.floor(i / col) % 2) * 30, y0 = 30 + ry * (h - 120);
          const ti = s0 + 0.25 + i * (c.every || 0.16); const st = SS.stamp(t, ti); const k = spring(t - t1 - i * 0.012, 16.4, 0.59);
          const fx = Math.sin(t * 0.9 + i) * 7, fy = Math.cos(t * 0.7 + i * 1.3) * 7;
          const x = lerp(x0 + fx, w / 2 - 90, k), y = lerp(y0 + fy, h / 2 - 30, k);
          d.style.opacity = st.op * (1 - cl((t - t1 - 0.45) / 0.2)); d.style.transform = `translate(${x}px,${y}px) rotate(${(((i * 37) % 9) - 4) * (1 - k)}deg) scale(${t < ti ? 0 : Math.min(st.s, 1.15) * (1 - 0.5 * k)})`;
        });
        const o = el.querySelector('[data-k=one]'); const st = SS.stamp(t, t1 + 0.45); o.style.opacity = st.op; o.style.transform = `translate(-50%,-50%) scale(${t < t1 + 0.45 ? 0 : st.s}) rotate(${st.rot}deg)`;
      }
    };
  },
  chat(c) {
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="row" data-k="q"><div class="av">${c.ini || 'JM'}</div><div><div class="ct" style="font-size:27px">${c.name || 'Jordan M.'}</div><div class="cm">Member · just now</div></div></div>
      <div class="bub" data-k="qb">${c.q}</div>
      <div class="row" style="margin-top:24px" data-k="a"><div class="av" style="background:#141418">AG</div><div><div class="ct" style="font-size:27px">Andrew George</div><div class="cm">Founder · replying</div></div></div>
      <div class="bub me" data-k="ab"></div></div>${c.badge ? `<div class="badge" style="left:-50px;bottom:-30px" data-k="bd"><span class="dot"></span>${c.badge}</div>` : ''}`,
      upd(t, el, at, s0) {
        const ta = c.aAt ? at(c.aAt) : s0 + 1.4;
        riseEl(el.querySelector('[data-k=q]'), t, s0 + 0.3); riseEl(el.querySelector('[data-k=qb]'), t, s0 + 0.45);
        riseEl(el.querySelector('[data-k=a]'), t, ta - 0.3); const ab = el.querySelector('[data-k=ab]'); ab.style.opacity = cl((t - ta + 0.2) / 0.2); typeEl(ab, t, ta, c.a, 40);
        const bd = el.querySelector('[data-k=bd]'); if (bd) stampEl(bd, t, ta + c.a.length / 40 + 0.2);
      }
    };
  },
  checks(c) { // list of rows that tick on phrases
    return {
      html: `<div class="card" style="width:var(--cw)">${c.title ? `<div class="row" style="justify-content:space-between;margin-bottom:14px"><div class="ct">${c.title}</div>${c.pill ? `<span class="pill g">${c.pill}</span>` : ''}</div>` : ''}
        ${c.bar ? '<div class="bar" style="margin-bottom:16px"><i></i></div>' : ''}<div>${c.items.map(it => `<div class="li">${check()}<span>${it[0]}</span></div>`).join('')}</div>${c.btn ? `<div style="margin-top:22px"><span class="pill" data-k="btn">${c.btn}</span></div>` : ''}</div>${c.badge ? `<div class="badge" style="left:-50px;bottom:-30px" data-k="bd"><span class="dot"></span>${c.badge}</div>` : ''}`,
      upd(t, el, at, s0) {
        const rows = el.querySelectorAll('.li'); let done = 0;
        c.items.forEach((it, i) => {
          const r = rows[i]; riseEl(r, t, s0 + 0.25 + i * 0.09, 24);
          const ti = it[1] === null ? 1e9 : (it[1] ? at(it[1]) : s0 + 0.8 + i * 0.5); const ck = r.querySelector('.ck'); stampEl(ck, t, ti);
          const on = cl((t - ti) / 0.25); r.style.background = `rgba(123,92,255,${0.08 * on * (c.hl === false ? 0 : 1)})`; done += SS.barFill(t, ti) / c.items.length;
        });
        const b = el.querySelector('.bar i'); if (b) b.style.width = (100 * done) + '%';
        const bt = el.querySelector('[data-k=btn]'); if (bt) stampEl(bt, t, c.btnAt ? at(c.btnAt) : s0 + 1.2);
        const bd = el.querySelector('[data-k=bd]'); if (bd) stampEl(bd, t, c.badgeAt ? at(c.badgeAt) : s0 + 1.0);
      }
    };
  },
  calls(c) {
    const g = ['#E9E5FB,#D9D2FA', '#E3F0FF,#CFE2FA', '#FFF0E6,#FBDDCB', '#E7F7EE,#CDEEDB'];
    return {
      html: `<div class="card" style="width:var(--cw)"><span class="pill" style="position:absolute;top:30px;right:34px" data-k="live"><span class="dot" style="background:#fff"></span>Live</span>
        <div class="ct">${c.title || 'Founder call'}</div><div class="cm">${c.sub || 'Weekly · with successful entrepreneurs'}</div>
        <div class="grid2">${(c.tiles || ['Guest founder', 'Andrew', 'Member', 'Member']).map((n, i) => `<div class="tile" style="background:linear-gradient(160deg,${g[i]})"><span>${n}</span></div>`).join('')}</div></div>${c.badge ? `<div class="badge" style="left:-50px;bottom:-30px" data-k="bd">${c.badge}</div>` : ''}`,
      upd(t, el, at, s0) {
        el.querySelectorAll('.tile').forEach((d, i) => stampEl(d, t, s0 + 0.35 + i * 0.14));
        stampEl(el.querySelector('[data-k=live]'), t, s0 + 1.0); const bd = el.querySelector('[data-k=bd]'); if (bd) stampEl(bd, t, c.badgeAt ? at(c.badgeAt) : s0 + 1.4);
      }
    };
  },
  drop(c) {
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="row"><div style="width:56px;height:56px;border-radius:16px;background:var(--vio);display:grid;place-items:center" data-k="lock">${LOCK}</div><div><div class="ct">${c.title || 'Members-only drop'}</div><div class="cm" style="color:#A9ABB8">${c.sub || 'New software · new system'}</div></div></div>
        <div style="margin-top:16px">${c.items.map(it => `<div class="li">${check()}<span>${it[0]}</span></div>`).join('')}</div><div style="margin-top:22px"><span class="pill" data-k="btn">${c.btn || 'Open the drop'}</span></div></div>`,
      upd(t, el, at, s0) {
        stampEl(el.querySelector('[data-k=lock]'), t, s0 + 0.3);
        el.querySelectorAll('.li').forEach((r, i) => { riseEl(r, t, s0 + 0.3 + i * 0.09, 24); stampEl(r.querySelector('.ck'), t, c.items[i][1] ? at(c.items[i][1]) : s0 + 0.8 + i * 0.4); });
        stampEl(el.querySelector('[data-k=btn]'), t, c.btnAt ? at(c.btnAt) : s0 + 2.0);
      }
    };
  },
  bars(c) { // labelled bars that fill (up) or drain (down) on phrases
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="ct" style="margin-bottom:10px">${c.title || 'Your business'}</div>${c.items.map(it => `<div style="margin-top:26px"><div class="row" style="justify-content:space-between;font-weight:600;font-size:27px"><span>${it[0]}</span><span class="pill ${it[2] === 'down' ? 'g' : ''}" style="opacity:0">${it[2] === 'down' ? '↓ less' : '↑ more'}</span></div><div class="bar" style="height:18px;border-radius:9px;margin-top:12px"><i style="border-radius:9px"></i></div></div>`).join('')}</div>`,
      upd(t, el, at, s0) {
        const bars = el.querySelectorAll('.bar i'), pills = el.querySelectorAll('.pill');
        c.items.forEach((it, i) => { const ti = it[1] ? at(it[1]) : s0 + 0.6 + i * 0.6; const f = SS.barFill(t, ti); const from = it[2] === 'down' ? 0.85 : 0.22, to = it[2] === 'down' ? 0.18 : 0.92; bars[i].style.width = 100 * lerp(from, to, f) + '%'; bars[i].style.background = it[2] === 'down' ? '#B9A8FF' : 'var(--vio)'; stampEl(pills[i], t, ti + 0.1); });
      }
    };
  },
  stat(c) { // big stamped figure + rows
    return {
      html: `<div class="card" style="width:var(--cw);text-align:left"><div class="cm" style="font-size:24px">${c.label}</div>
        <div style="font-weight:800;font-size:${c.size || 120}px;letter-spacing:-.05em;line-height:1.05;margin:10px 0 6px;position:relative;display:inline-block" data-k="big">${c.big}<i data-k="strike" style="position:absolute;left:-4%;top:52%;height:10px;width:0;background:var(--vio);border-radius:5px"></i></div>
        ${c.stamp ? `<div><span class="pill" style="font-size:30px;padding:14px 26px" data-k="st">${c.stamp}</span></div>` : ''}
        <div style="margin-top:14px">${(c.items || []).map(it => `<div class="li">${check()}<span>${it[0]}</span></div>`).join('')}</div></div>`,
      upd(t, el, at, s0) {
        const big = el.querySelector('[data-k=big]'); const b = SS.bigSettle(t, s0 + 0.35); big.style.opacity = b.op; big.style.filter = b.blur > .2 ? `blur(${b.blur}px)` : 'none'; big.style.transform = `scale(${b.s})`;
        if (c.strikeAt) { const p = ease.outCubic((t - at(c.strikeAt)) / 0.35); el.querySelector('[data-k=strike]').style.width = 108 * cl(p) + '%'; big.style.color = p > 0 ? `rgba(20,20,24,${1 - 0.6 * cl(p)})` : ''; }
        const st = el.querySelector('[data-k=st]'); if (st) stampEl(st, t, c.stampAt ? at(c.stampAt) : s0 + 1.0);
        el.querySelectorAll('.li').forEach((r, i) => { riseEl(r, t, s0 + 0.5 + i * 0.09, 24); stampEl(r.querySelector('.ck'), t, c.items[i][1] ? at(c.items[i][1]) : s0 + 0.9 + i * 0.4); });
      }
    };
  },
  calendar(c) {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="row" style="justify-content:space-between"><div class="ct">Calendar</div><span class="pill g">This week</span></div>
        <div class="cal">${days.map(d => `<div class="day">${d}</div>`).join('')}</div></div>`,
      upd(t, el, at, s0) {
        const ds = el.querySelectorAll('.day'); ds.forEach((d, i) => riseEl(d, t, s0 + 0.25 + i * 0.06, 30));
        if (!el._ev) { el._ev = c.events.map(e => { const x = document.createElement('div'); x.className = 'ev' + (e.alt ? ' b' : ''); x.style.top = (e.top || 56) + 'px'; x.innerHTML = e.t; ds[e.d].appendChild(x); return x; }); }
        c.events.forEach((e, i) => { const ti = e.at === undefined ? s0 + 0.7 + i * 0.25 : (typeof e.at === 'number' ? s0 + e.at : at(e.at)); stampEl(el._ev[i], t, ti); });
        if (c.hl !== undefined) { const ti = at(c.hlAt); const on = cl((t - ti) / 0.25); ds[c.hl].style.boxShadow = `inset 0 0 0 ${3 * on}px var(--vio)`; ds[c.hl].style.background = on > 0 ? `rgba(123,92,255,${0.1 * on})` : ''; }
      }
    };
  },
  prompt(c) { // composer/prompt bar that types, then optional answer chip + button
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="row" style="justify-content:space-between;margin-bottom:18px"><div class="ct">${c.title}</div>${c.tag ? `<span class="pill g">${c.tag}</span>` : ''}</div>
        <div class="prompt" data-k="p"></div>${c.answer ? `<div class="bub" data-k="ans" style="margin-top:18px;opacity:0">${c.answer}</div>` : ''}
        ${c.btn ? `<div style="margin-top:20px;text-align:right"><span class="pill" data-k="btn" style="font-size:24px;padding:12px 26px">${c.btn}</span></div>` : ''}</div>`,
      upd(t, el, at, s0) {
        const ts = c.typeAt ? at(c.typeAt) : s0 + 0.5; typeEl(el.querySelector('[data-k=p]'), t, ts, c.text, c.cps || 30);
        const a = el.querySelector('[data-k=ans]'); if (a) riseEl(a, t, c.ansAt ? at(c.ansAt) : ts + c.text.length / (c.cps || 30) + 0.3, 24);
        const b = el.querySelector('[data-k=btn]'); if (b) { const tb = c.btnAt ? at(c.btnAt) : ts + c.text.length / (c.cps || 30) + 0.2; stampEl(b, t, tb); if (t > tb + 0.6) b.style.transform = `scale(${SS.press(t, tb + 0.8)})`; }
      }
    };
  },
  post(c) { // intro post with lines appearing on phrases
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="row"><div class="av">You</div><div><div class="ct" style="font-size:27px">Your intro post</div><div class="cm">Introductions</div></div></div>
        <div style="margin-top:18px">${c.lines.map(l => `<div class="li" style="font-size:25px"><span style="color:var(--vio);font-weight:800">${l[0]}</span><span class="cm" style="font-size:24px">${l[2] || ''}</span></div>`).join('')}</div>
        <div style="margin-top:18px;text-align:right"><span class="pill" data-k="btn" style="font-size:24px;padding:12px 28px">Post</span></div></div>`,
      upd(t, el, at, s0) {
        el.querySelectorAll('.li').forEach((r, i) => riseEl(r, t, c.lines[i][1] ? at(c.lines[i][1]) : s0 + 0.4 + i * 0.3, 24));
        const b = el.querySelector('[data-k=btn]'); stampEl(b, t, c.btnAt ? at(c.btnAt) : s0 + 1.5);
      }
    };
  },
  tiles(c) { // course tiles appearing on phrases
    const g = ['#E9E5FB,#D9D2FA', '#E3F0FF,#CFE2FA', '#FFF0E6,#FBDDCB', '#E7F7EE,#CDEEDB', '#F3E8FF,#E4D2FA', '#FFF7D6,#F7E7A6'];
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="row" style="justify-content:space-between"><div class="ct">${c.title || 'Classroom'}</div>${c.pill ? `<span class="pill g">${c.pill}</span>` : ''}</div>
        <div class="grid2">${c.items.map((n, i) => `<div class="tile" style="aspect-ratio:16/8;background:linear-gradient(160deg,${g[i % 6]})"><span>${n[0]}</span></div>`).join('')}</div></div>`,
      upd(t, el, at, s0) { el.querySelectorAll('.tile').forEach((d, i) => stampEl(d, t, c.items[i][1] ? at(c.items[i][1]) : s0 + 0.35 + i * 0.14)); }
    };
  },
  feed(c) {
    return {
      html: `<div class="card" style="width:var(--cw)"><div class="row" style="justify-content:space-between"><div class="ct">Announcements</div><span class="pill g">Feed</span></div>
        <div style="margin-top:12px" data-k="list">${c.items.map((it, i) => `<div class="li" style="font-size:25px">${i === 0 ? `<span class="pill" style="font-size:18px;padding:6px 12px">New</span>` : '<span class="dot" style="background:#DCD7F0"></span>'}<span>${it[0]}</span></div>`).join('')}</div></div>`,
      upd(t, el, at, s0) { const rows = el.querySelectorAll('.li'); rows.forEach((r, i) => { if (i === 0) { const ti = c.items[0][1] ? at(c.items[0][1]) : s0 + 1.2; const k = spring(t - ti, 14, 0.7); r.style.opacity = cl((t - ti) / 0.15); r.style.transform = `translateY(${-60 * (1 - k)}px) scale(${lerp(0.9, 1, k)})`; r.style.background = `rgba(123,92,255,${0.1 * cl((t - ti) / 0.3)})`; } else riseEl(r, t, s0 + 0.3 + i * 0.09, 24); }); }
    };
  },
  p4(c) { // the four priorities as cards
    const P = [['01', 'Access to me'], ['02', 'The training'], ['03', 'Founder calls'], ['04', 'First access']];
    return {
      html: `<div class="p4" style="width:var(--pw);${VERT ? 'flex-wrap:wrap' : ''}">${P.map(p => `<div class="card" style="${VERT ? 'flex:0 0 calc(50% - 11px)' : ''}"><div class="n">${p[0]}</div><div class="t">${p[1]}</div></div>`).join('')}</div>`,
      upd(t, el, at, s0) { el.querySelectorAll('.card').forEach((d, i) => { const ti = c.at && c.at[i] ? at(c.at[i]) : s0 + 0.4 + i * 0.22; const r = SS.cardSlide(t, ti, 120); d.style.opacity = r.op; d.style.transform = `translateY(${r.x}px)`; }); }
    };
  },
};

// ---------- build scenes ----------
const world = $('world'); const scenes = [];
let prev = 0;
SC.forEach((s, idx) => {
  const st = (typeof s.at === 'number' ? s.at : T(s.at, prev)) - 0.12; prev = st + 0.13;
  const el = document.createElement('div'); el.className = 'scene' + (s.dark ? ' dark' : ''); world.appendChild(el);
  const lay = s.card ? (s.lay || (['p4'].includes(s.card.type) ? 'stack' : 'split')) : 'center';
  const L = document.createElement('div'); L.className = 'L'; el.appendChild(L);
  const hs = VERT ? (s.hsV || 96) : (s.hs || (lay === 'center' ? 128 : 104));
  if (s.num) L.innerHTML += `<div class="num" style="font-size:${VERT ? 220 : 240}px" data-k="num">${s.num}</div>`;
  if (s.k) L.innerHTML += `<div class="kick" style="font-size:${VERT ? 28 : 26}px;margin-bottom:28px;${lay === 'center' ? 'justify-content:center' : ''}" data-k="kick">${s.kn ? `<b style="width:52px;height:52px;font-size:26px">${s.kn}</b>` : ''}${s.k}</div>`;
  const H = document.createElement('div'); H.className = 'h'; H.style.fontSize = hs + 'px'; L.appendChild(H); buildH(H, s.h);
  if (s.sub) L.innerHTML += `<p class="sub" style="font-size:${VERT ? 38 : 34}px;margin-top:30px" data-k="sub">${s.sub}</p>`;
  let card = null, R = null;
  if (s.card) { card = CARDS[s.card.type](s.card); R = document.createElement('div'); R.className = 'R'; R.innerHTML = card.html; el.appendChild(R); }
  // layout
  if (lay === 'center') { L.style.cssText = `left:0;right:0;top:50%;text-align:center;transform:translateY(-58%)`; }
  else if (lay === 'stack') { L.style.cssText = VERT ? `left:80px;right:80px;top:300px;text-align:center` : `left:0;right:0;top:200px;text-align:center`; R.style.cssText = VERT ? `left:80px;top:900px;--pw:780px;zoom:1.18` : `left:150px;top:540px;--pw:1620px`; }
  else if (VERT) { L.style.cssText = `left:80px;right:80px;top:250px`; R.style.cssText = `left:80px;top:${s.rTopV || 800}px;--cw:780px;zoom:1.18`; }
  else { L.style.cssText = `left:130px;width:${s.lw || 860}px;top:50%;transform:translateY(-50%)`; R.style.cssText = `right:120px;top:50%;--cw:${s.cw || 760}px`; }
  scenes.push({ s, el, L, H, R, card, st, lay });
  const hEl = H; hEl._t0 = st + 0.12;
});
scenes.forEach((sc, i) => sc.en = i + 1 < scenes.length ? scenes[i + 1].st : DUR + 1);
// resolve the vertical centring of split cards after layout
function centre(sc) { if (sc.lay === 'split' && !VERT && sc.R) { sc._rh = sc._rh || sc.R.offsetHeight; } }

// ---------- captions ----------
const cap = $('cap'); cap.style.cssText = VERT ? 'bottom:250px;font-size:58px;padding:0 70px' : 'bottom:56px;font-size:44px;padding:0 200px';
const phrases = []; { let cur = []; W.forEach((w, i) => { const p = W[i - 1]; if (cur.length && (w.s - p.e > 0.35 || /[.,?!]$/.test(p.w) || cur.length >= (VERT ? 3 : 5))) { phrases.push(cur); cur = []; } cur.push(w); }); if (cur.length) phrases.push(cur); }

// ---------- cursor for end card ----------
const cursor = document.createElement('div'); cursor.id = 'cursor'; cursor.innerHTML = '<svg viewBox="0 0 24 24" width="40" height="40"><path d="M4 2l16 9-7 2-3 7z" fill="#fff" stroke="#141418" stroke-width="1.5" stroke-linejoin="round"/></svg>'; $('stage').appendChild(cursor);

function render(t) {
  let darkOn = 0;
  scenes.forEach((sc, i) => {
    const vis = t >= sc.st && t < sc.en + 0.3;
    sc.el.style.display = vis ? 'block' : 'none'; if (!vis) return;
    const out = cl((t - sc.en) / 0.28), s0 = sc.st;
    if (t < sc.en) darkOn = sc.s.dark ? cl((t - s0) / 0.2) : (i > 0 && scenes[i - 1].s.dark ? 1 - cl((t - s0) / 0.2) : 0);
    const push = 1 + 0.03 * cl((t - s0) / Math.max(1, sc.en - s0));
    sc.el.style.opacity = 1 - out; sc.el.style.filter = out > 0 ? `blur(${10 * out}px)` : 'none';
    sc.el.style.transform = `translateY(${-24 * out}px) scale(${push})`; sc.el.style.transformOrigin = '50% 45%';
    riseH(sc.H, t, s0 + 0.08 + (sc.s.num ? 0.25 : 0), sc.H._n > 22 ? 0.018 : 0.028);
    const k = sc.L.querySelector('[data-k=kick]'); if (k) riseEl(k, t, s0, 20);
    const nm = sc.L.querySelector('[data-k=num]'); if (nm) { const b = SS.bigSettle(t, s0); nm.style.opacity = b.op; nm.style.filter = b.blur > .2 ? `blur(${b.blur}px)` : 'none'; nm.style.transform = `scale(${b.s})`; }
    const sb = sc.L.querySelector('[data-k=sub]'); if (sb) riseEl(sb, t, s0 + 0.45, 30);
    if (sc.card) {
      const tc = s0 + 0.18; const r = SS.cardSlide(t, tc, VERT ? 240 : 360);
      centre(sc);
      const base = sc.lay === 'split' && !VERT ? `translateY(-50%) ` : '';
      sc.R.style.opacity = r.op; sc.R.style.transform = base + (VERT ? `translateY(${r.x}px)` : (sc.lay === 'stack' ? `translateY(${r.x * 0.4}px)` : `translateX(${r.x}px)`));
      sc.R.style.filter = r.blurX > 0.3 ? `blur(${Math.min(8, r.blurX)}px)` : 'none';
      sc.card.upd(t, sc.R, ph => T(ph, s0 - 0.2), s0);
    }
    if (sc.s.end) endCard(sc, t, s0);
  });
  $('darkbg').style.opacity = darkOn;
  // captions
  let P = null; for (let i = 0; i < phrases.length; i++) { const a = phrases[i][0].s - 0.05, b = i + 1 < phrases.length ? Math.min(phrases[i + 1][0].s - 0.05, phrases[i][phrases[i].length - 1].e + 0.8) : phrases[i][phrases[i].length - 1].e + 0.8; if (t >= a && t < b) { P = phrases[i]; break; } }
  const curScene = scenes.find(sc => t >= sc.st && t < sc.en);
  const hideCap = curScene && curScene.s.end;
  if (!P || hideCap) cap.innerHTML = ''; else {
    const key = P[0].s; if (cap._k !== key) { cap._k = key; cap.innerHTML = P.map(w => `<span>${w.w}</span>`).join(''); }
    const act = P.reduce((m, w, i) => t >= w.s - 0.03 ? i : m, -1);
    const dk = darkOn > 0.5;
    cap.querySelectorAll('span').forEach((s, i) => { s.style.color = i === act ? (dk ? '#9B83FF' : '#7B5CFF') : (dk ? '#fff' : '#141418'); s.style.opacity = i <= act ? 1 : 0.35; });
    const e = cl((t - P[0].s + 0.05) / 0.12); cap.style.opacity = e; cap.style.transform = `translateY(${(1 - e) * 10}px)`;
  }
}
function endCard(sc, t, s0) {
  const btn = sc.L.querySelector('.cta'); if (!btn) return;
  const tb = s0 + 0.9; stampEl(btn, t, tb);
  const tc = sc.s.clickAt ? T(sc.s.clickAt, s0 - 0.3) + 0.15 : s0 + 1.8;
  const r = btn.getBoundingClientRect(); const tx = r.left + r.width * 0.62, ty = r.top + r.height * 0.6;
  const k = ease.outCubic((t - tc + 0.7) / 0.7);
  cursor.style.display = t > tc - 0.7 && t < sc.en ? 'block' : 'none';
  cursor.style.transform = `translate(${lerp(tx + 260, tx, k)}px,${lerp(ty + 200, ty, k)}px) scale(${SS.cursorSquish(t, tc)})`;
  if (t > tc) btn.style.transform = `scale(${SS.press(t, tc)})`;
}
// end-card markup is injected via scene.h/sub; add the button
scenes.forEach(sc => { if (sc.s.end) { sc.L.insertAdjacentHTML('beforeend', `<div style="margin-top:${VERT ? 70 : 56}px"><span class="cta" style="font-size:${VERT ? 40 : 36}px;padding:${VERT ? '26px 54px' : '22px 50px'}">${sc.s.end}</span></div>`); } });
window.render = render;
window.CUES = { scenes: scenes.map(s => +s.st.toFixed(3)), click: scenes.filter(s => s.s.end).map(s => +(s.s.clickAt ? T(s.s.clickAt, s.st - 0.3) + 0.15 : s.st + 1.8).toFixed(3)), dark: scenes.map(s => !!s.s.dark) };
