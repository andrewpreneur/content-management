// YourGHLAgent + YourGHLSupport motion ads. index.html?c=ag1|ag2|sp1|sp2&fmt=h|v
// All art is authored on a 1080x1080 stage; 16:9 centres it, 9:16 puts it inside the middle 4:5 band.
const Q = new URLSearchParams(location.search), C = Q.get('c') || 'ag1', V = Q.get('fmt') === 'v';
const FW = V ? 1080 : 1920, FH = V ? 1920 : 1080;
document.documentElement.style.cssText = document.body.style.cssText = `width:${FW}px;height:${FH}px`;
const { cl, lerp, ease, spring } = SS; const E3 = ease.outCubic, E4 = ease.outQuart, IO = ease.inOutCubic;
const sp = (x, w = 14, z = 0.6) => spring(x, w, z), pos = x => Math.max(0, x);
const S = document.getElementById('stage'), BG = document.getElementById('bgx');
S.style.left = (FW - 1080) / 2 + 'px'; S.style.top = (FH - 1080) / 2 + 'px';
function el(p, css = '', html = '') { const d = document.createElement('div'); d.className = 'a'; d.style.cssText = css; d.innerHTML = html; p.appendChild(d); return d; }
const tf = (e, s) => e.style.transform = s, op = (e, o) => e.style.opacity = o, bl = (e, b) => e.style.filter = b > .3 ? `blur(${b}px)` : 'none';
function pop(e, t, t0, base = '') { const k = sp(t - t0, 15, 0.55); op(e, cl((t - t0) / 0.08)); tf(e, `${base} scale(${t < t0 ? 0 : k})`); }
function rise(e, t, t0, dy = 40, base = '') { const k = E4((t - t0) / 0.45); op(e, k); bl(e, (1 - k) * 8); tf(e, `${base} translateY(${(1 - k) * dy}px)`); }
function outAt(e, t, t1, d = 0.25) { const k = cl((t - t1) / d); if (k > 0) { op(e, (+e.style.opacity || 1) * (1 - k)); bl(e, k * 10); } }
function win(t, a, b) { return t >= a && t < b; }
const typed = (s, t, t0, cps = 26) => s.slice(0, Math.max(0, Math.min(s.length, Math.floor((t - t0) * cps))));
const caret = (t, c) => `<span style="display:inline-block;width:.5em;height:1em;vertical-align:-.12em;background:${c};opacity:${Math.floor(t * 2.4) % 2 ? 0 : 1}"></span>`;
function shout(p, txt, size, color, css = '') { return el(p, `left:0;right:0;text-align:center;${css}`, `<div class="anton" style="font-size:${size}px;color:${color}">${[...txt].map((c, i) => `<span data-l="${i}" style="display:inline-block;white-space:pre">${c}</span>`).join('')}</div>`); }
function letters(e, t, t0, st = 0.03) { e.querySelectorAll('[data-l]').forEach(s => { const r = SS.letterRise(t, t0, +s.dataset.l, { stagger: st }); tf(s, `translateY(${r.y}px) rotate(${r.rot}deg)`); bl(s, r.blur); op(s, r.op); }); }
const CK = c => `<svg width="1em" height="1em" viewBox="0 0 24 24" style="vertical-align:-.15em"><path d="M5 12.5l4.5 4.5L19 7.5" stroke="${c}" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const CURSOR = '<svg width="46" height="46" viewBox="0 0 24 24"><path d="M4 2l16 9-7 2-3 7z" fill="#fff" stroke="#111" stroke-width="1.5" stroke-linejoin="round"/></svg>';

const AG = { bg: '#0A0B0D', fg: '#FFFFFF', lime: '#C8FF2E', dim: '#8C9099', card: '#14161A', line: '#24272E' };
const SPT = { bg: '#FFF7EC', ink: '#111111', or: '#FF5A1F', red: '#E11D48', green: '#16A34A', card: '#FFFFFF', line: '#EADFCF', mute: '#6B6258' };
const CUES = []; // [time, sfx] for the mixer
const cue = (t, k) => CUES.push([+t.toFixed(3), k]);

function agentBG() {
  BG.style.background = `radial-gradient(900px 700px at 50% 45%, rgba(200,255,46,.07), transparent 70%), ${AG.bg}`;
  const g = el(BG, 'inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:60px 60px');
  return t => { g.style.backgroundPosition = `${t * 8}px ${t * 14}px`; };
}
function supportBG() {
  BG.style.background = SPT.bg;
  const g = el(BG, 'inset:0;background-image:radial-gradient(rgba(17,17,17,.08) 1.5px,transparent 1.5px);background-size:44px 44px');
  return t => { g.style.backgroundPosition = `${t * 6}px ${t * 4}px`; };
}
function endCard(p, th, t0, name, domain, cta, mark) {
  const W = el(p, 'left:0;right:0;top:330px;text-align:center', `<div style="display:inline-flex;align-items:center;gap:20px;font:900 92px Inter;letter-spacing:-.04em;color:${th.fg || th.ink}">${mark}${name}</div>`);
  const D = el(p, `left:0;right:0;top:470px;text-align:center;font:600 40px Inter;color:${th.dim || th.mute}`, domain);
  const B = el(p, `left:540px;top:580px;padding:30px 56px;border-radius:999px;background:${th.lime || th.or};color:${th.lime ? '#0A0B0D' : '#fff'};font:800 44px Inter;white-space:nowrap`, cta);
  const cur = el(p, 'left:0;top:0;z-index:9', CURSOR);
  cue(t0, 'whoosh'); cue(t0 + 0.7, 'pop'); cue(t0 + 1.7, 'click');
  return t => {
    const on = t >= t0; [W, D, B, cur].forEach(e => e.style.display = on ? 'block' : 'none'); if (!on) return;
    rise(W, t, t0, 50); rise(D, t, t0 + 0.25, 30);
    const s = SS.stamp(t, t0 + 0.7); op(B, s.op); tf(B, `translateX(-50%) scale(${(t < t0 + 0.7 ? 0 : s.s) * SS.press(t, t0 + 1.7)})`);
    const k = E3((t - t0 - 1.0) / 0.7); op(cur, t > t0 + 1.0 ? 1 : 0); tf(cur, `translate(${lerp(900, 600, k)}px,${lerp(980, 640, k)}px) scale(${SS.cursorSquish(t, t0 + 1.7)})`);
  };
}
const AGMARK = `<span style="width:84px;height:84px;border-radius:22px;background:${AG.lime};display:grid;place-items:center;font:900 46px Inter;color:#0A0B0D">A</span>`;
const SPMARK = `<span style="width:84px;height:84px;border-radius:50%;background:${SPT.or};display:grid;place-items:center;color:#fff;font:900 40px Inter">60</span>`;

// a generic CRM window (deliberately not HighLevel's UI or logo)
function crmWindow(p, css, th) {
  return el(p, `${css};background:${th.card};border:1px solid ${th.line};border-radius:22px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.5)`,
    `<div style="height:56px;border-bottom:1px solid ${th.line};display:flex;align-items:center;gap:10px;padding:0 20px">${'<i style="width:12px;height:12px;border-radius:50%;background:#2E3138;display:block"></i>'.repeat(3)}<span style="margin-left:14px;font:600 18px Inter;color:${th.dim}">Your GHL account</span></div>
     <div data-side style="position:absolute;left:0;top:56px;bottom:0;width:150px;border-right:1px solid ${th.line};padding:18px 14px;display:grid;gap:8px;align-content:start">${['Contacts', 'Pipeline', 'Workflows', 'Calendar'].map(n => `<div data-nav="${n}" style="font:600 18px Inter;color:${th.dim};padding:10px 12px;border-radius:10px">${n}</div>`).join('')}</div>
     <div data-body style="position:absolute;left:150px;right:0;top:56px;bottom:0;overflow:hidden"></div>`);
}

const CONCEPTS = {
  // ---------------- AGENT 1: Hands off ----------------
  ag1: { dur: 20.5, music: 'agent', build() {
    const bgu = agentBG(); const th = AG;
    const sh1 = shout(S, 'Give it a login.', 120, th.fg, 'top:70px');
    const login = el(S, `left:240px;top:300px;width:600px;background:${th.card};border:1px solid ${th.line};border-radius:26px;padding:40px;box-shadow:0 30px 80px rgba(0,0,0,.6)`,
      `<div style="font:800 34px Inter;color:#fff">Connect your account</div><div style="margin-top:8px;font:500 20px Inter;color:${th.dim}">YourGHLAgent needs a login. That's it.</div>
       <div style="margin-top:30px;font:600 16px Inter;color:${th.dim}">Email</div><div data-e class="mono" style="margin-top:8px;height:64px;border-radius:12px;border:1px solid ${th.line};padding:0 18px;display:flex;align-items:center;font-size:24px;color:#fff"></div>
       <div style="margin-top:18px;font:600 16px Inter;color:${th.dim}">Password</div><div data-p class="mono" style="margin-top:8px;height:64px;border-radius:12px;border:1px solid ${th.line};padding:0 18px;display:flex;align-items:center;font-size:30px;color:#fff;letter-spacing:4px"></div>
       <div data-b style="margin-top:28px;height:72px;border-radius:14px;background:${th.lime};color:#0A0B0D;display:grid;place-items:center;font:800 26px Inter">Give it a login</div>`);
    const ok = el(S, `left:500px;top:240px;width:110px;height:110px;border-radius:50%;background:${th.lime};display:grid;place-items:center;font-size:64px`, CK('#0A0B0D'));
    cue(1.95, 'click'); cue(2.15, 'ding');
    // dashboard + log
    const W = crmWindow(S, 'left:40px;top:40px;width:1000px;height:600px', th); const body = W.querySelector('[data-body]');
    const panes = {
      Contacts: el(body, 'inset:0;padding:22px', `<div style="font:800 26px Inter;color:#fff;margin-bottom:14px">Contacts</div>${['Maria Lopez · Roof quote', 'James Carter · Booked call', 'Priya Shah · New lead', 'Tom Becker · Follow up', 'Ana Ruiz · New lead', 'Kevin Moore · Quote sent', 'Lena Park · New lead'].map(r => `<div data-r style="display:flex;gap:14px;align-items:center;padding:12px 10px;border-bottom:1px solid ${th.line};font:600 20px Inter;color:#d7d9de"><span style="width:34px;height:34px;border-radius:50%;background:#262A31"></span>${r}</div>`).join('')}`),
      Pipeline: el(body, 'inset:0;padding:22px', `<div style="font:800 26px Inter;color:#fff;margin-bottom:14px">Pipeline</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px">${['New lead', 'Quoted', 'Won'].map(c => `<div data-col style="position:relative;background:#101216;border:1px solid ${th.line};border-radius:14px;height:440px;padding:12px"><div style="font:700 18px Inter;color:${th.dim};margin-bottom:10px">${c}</div></div>`).join('')}</div>`),
      Workflows: el(body, 'inset:0;padding:22px', `<div style="font:800 26px Inter;color:#fff;margin-bottom:14px">Missed-call text back</div><svg width="820" height="440" style="position:absolute;left:22px;top:70px;overflow:visible"><path data-wl d="M140 70 V170 M140 230 V330 M140 230 H520 V330" stroke="${th.lime}" stroke-width="4" fill="none"/></svg>${[['Missed call', 40, 70], ['Wait 1 min', 40, 230], ['Send SMS', 40, 390], ['Tag: hot lead', 420, 390]].map((n, i) => `<div data-node style="position:absolute;left:${n[1] + 22}px;top:${n[2] + 40}px;width:240px;height:64px;border-radius:14px;background:#101216;border:2px solid ${i ? th.line : th.lime};display:grid;place-items:center;font:700 20px Inter;color:#fff">${n[0]}</div>`).join('')}`),
      Calendar: el(body, 'inset:0;padding:22px', `<div style="font:800 26px Inter;color:#fff;margin-bottom:14px">Discovery call · this week</div><div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px">${['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].map(d => `<div style="background:#101216;border:1px solid ${th.line};border-radius:12px;height:420px;padding:10px;position:relative"><div style="font:700 16px Inter;color:${th.dim}">${d}</div></div>`).join('')}</div>`),
    };
    const cards = []; const cols = panes.Pipeline.querySelectorAll('[data-col]');
    ['Maria L.', 'James C.', 'Priya S.', 'Tom B.', 'Ana R.'].forEach((n, i) => { const c = document.createElement('div'); c.style.cssText = `position:absolute;left:12px;right:12px;height:64px;border-radius:12px;background:#1B1E24;border:1px solid ${th.line};font:700 18px Inter;color:#fff;display:flex;align-items:center;padding:0 14px`; c.textContent = n; cols[0].appendChild(c); cards.push(c); });
    const slots = []; panes.Calendar.querySelectorAll('div[style*="height:420px"]').forEach((d, i) => { [0, 1].forEach(j => { if ((i + j) % 2) return; const s = document.createElement('div'); s.style.cssText = `position:absolute;left:8px;right:8px;top:${60 + j * 150 + i * 20}px;height:90px;border-radius:10px;background:${th.lime};color:#0A0B0D;font:800 16px Inter;padding:10px`; s.innerHTML = 'Booked'; d.appendChild(s); slots.push(s); }); });
    const LOG = [[3.0, '> logged in to your GHL'], [3.5, '> importing contacts'], [5.0, '✓ 7 contacts added'], [5.5, '> building pipeline'], [7.6, '✓ pipeline: New lead → Quoted → Won'], [8.0, '> workflow: missed-call text back'], [10.1, '✓ workflow live'], [10.4, '> booking discovery calls'], [12.0, '✓ calendar filled'], [12.8, '✓ tagged hot leads'], [13.6, '✓ follow-ups sent'], [14.4, '✓ report ready']];
    const log = el(S, `left:40px;top:665px;width:1000px;height:270px;background:#08090B;border:1px solid ${th.line};border-radius:22px;padding:20px 26px;overflow:hidden`, `<div class="mono" style="font-size:16px;color:${th.dim};margin-bottom:8px">agent log</div><div data-lines class="mono" style="font-size:24px;line-height:1.55"></div>`);
    LOG.forEach(l => cue(l[0], l[1].startsWith('✓') ? 'tick' : 'key'));
    const cur = el(S, 'left:0;top:0;z-index:5;display:none', CURSOR);
    const phases = [['Contacts', 3.4, 5.4], ['Pipeline', 5.4, 7.9], ['Workflows', 7.9, 10.3], ['Calendar', 10.3, 12.6]];
    phases.forEach(p => cue(p[1], 'click'));
    const kb = el(S, `left:140px;top:740px;width:800px;height:230px;border-radius:24px;background:#121418;border:1px solid ${th.line};display:grid;grid-template-columns:repeat(12,1fr);gap:8px;padding:22px`, [...'QWERTYUIOPASDFGHJKL;ZXCVBNM,./ '].slice(0,36).map(k => `<i style="display:grid;place-items:center;height:44px;border-radius:8px;background:#1D2026;font:700 16px Inter;color:#5A5F69;font-style:normal">${k.trim()}</i>`).join(''));
    const sh2 = shout(S, 'Hands off.', 190, th.lime, 'top:500px'); const sh3 = shout(S, 'It does the work.', 130, th.fg, 'top:380px');
    cue(12.6, 'whoosh'); cue(12.8, 'impact'); cue(15.6, 'impact');
    const end = endCard(S, th, 17.8, 'YourGHLAgent', 'yourghlagent.com', 'Try YourGHLAgent', AGMARK);
    return t => {
      bgu(t);
      const L1 = t < 2.7; sh1.style.display = login.style.display = L1 ? 'block' : 'none'; ok.style.display = t > 2.0 && t < 2.8 ? 'block' : 'none';
      if (L1) { letters(sh1, t, 0.1); rise(login, t, 0.15, 60); login.querySelector('[data-e]').innerHTML = typed('you@youragency.com', t, 0.6, 30) + (t < 1.3 ? caret(t, '#fff') : ''); login.querySelector('[data-p]').textContent = '•'.repeat(Math.max(0, Math.min(10, Math.floor((t - 1.3) * 22)))); login.querySelector('[data-b]').style.transform = `scale(${SS.press(t, 1.95)})`; outAt(login, t, 2.4); outAt(sh1, t, 2.4); }
      if (t > 2.0) pop(ok, t, 2.05);
      const D = win(t, 2.6, 17.8); W.style.display = log.style.display = D ? 'block' : 'none';
      if (D) {
        const g = sp(t - 2.6, 9, 0.8); const z = t > 12.6 ? E3((t - 12.6) / 0.6) : 0;
        tf(W, `perspective(2400px) translateY(${(1 - g) * 80 - z * 60}px) rotateX(${(1 - g) * 12 + z * 18}deg) scale(${lerp(0.92, 1, g) - z * 0.12})`); op(W, cl((t - 2.6) / 0.2) * (1 - cl((t - 12.6) / 0.3)));
        tf(log, `translateY(${(1 - g) * 120 - z * 470}px)`); op(log, cl((t - 2.7) / 0.2) * (1 - cl((t - 15.3) / 0.25)));
        let cur_p = phases.find(p => t >= p[1] && t < p[2]) || (t < 3.4 ? phases[0] : phases[3]);
        Object.entries(panes).forEach(([k, e]) => { const on = k === cur_p[0]; e.style.display = on ? 'block' : 'none'; if (on) { const k2 = E4((t - cur_p[1]) / 0.4); tf(e, `translateX(${(1 - k2) * 60}px)`); op(e, k2); } });
        W.querySelectorAll('[data-nav]').forEach(n => { const on = n.dataset.nav === cur_p[0]; n.style.background = on ? 'rgba(200,255,46,.12)' : 'transparent'; n.style.color = on ? th.lime : th.dim; });
        panes.Contacts.querySelectorAll('[data-r]').forEach((r, i) => pop(r, t, 3.7 + i * 0.18));
        cards.forEach((c, i) => { const t0 = 5.7 + i * 0.12; const mv = i < 3 ? E3((t - 6.6 - i * 0.25) / 0.5) * (i === 0 ? 2 : 1) : 0; const col = Math.round(mv); const fx = mv * 262; op(c, cl((t - t0) / 0.1)); c.style.top = (40 + (i % 5) * 76 - (i < 3 ? mv * 0 : 0)) + 'px'; tf(c, `translateX(${fx}px) translateY(${i < 3 ? -Math.min(i, 2) * 0 : 0}px) scale(${t < t0 ? 0 : sp(t - t0, 16, 0.6)})`); });
        const wl = panes.Workflows.querySelector('[data-wl]'); if (wl.getTotalLength) { const Ln = wl.getTotalLength(); wl.style.strokeDasharray = Ln; wl.style.strokeDashoffset = Ln * (1 - E3((t - 8.3) / 1.4)); }
        panes.Workflows.querySelectorAll('[data-node]').forEach((n, i) => pop(n, t, 8.1 + i * 0.4));
        slots.forEach((s, i) => pop(s, t, 10.6 + i * 0.14));
        // cursor visits nav item then content
        const targets = [[95, 140], [95, 190], [95, 240], [95, 290]]; const pi = phases.indexOf(cur_p); const tg = targets[pi];
        const prev = targets[Math.max(0, pi - 1)]; const k3 = E3((t - cur_p[1] + 0.35) / 0.35);
        const cx = 40 + lerp(prev[0], tg[0], k3) + (t > cur_p[1] + 0.3 ? Math.sin(t * 2) * 160 + 420 : 0) * E3((t - cur_p[1] - 0.3) / 0.6), cy = 40 + lerp(prev[1], tg[1], k3) + (t > cur_p[1] + 0.3 ? 140 + Math.cos(t * 1.7) * 80 : 0) * E3((t - cur_p[1] - 0.3) / 0.6);
        cur.style.display = t > 3.0 && t < 12.6 ? 'block' : 'none'; tf(cur, `translate(${cx}px,${cy}px) scale(${SS.cursorSquish(t, cur_p[1])})`);
        const lines = LOG.filter(l => t >= l[0]).slice(-6); log.querySelector('[data-lines]').innerHTML = lines.map((l, i) => { const ok2 = l[1].startsWith('✓'); const txt = i === lines.length - 1 ? typed(l[1], t, l[0], 40) : l[1]; return `<div style="color:${ok2 ? th.lime : '#d7d9de'}">${txt}</div>`; }).join('');
      }
      const H = win(t, 12.6, 15.5); kb.style.display = H ? 'grid' : 'none'; sh2.style.display = H ? 'block' : 'none';
      if (H) { letters(sh2, t, 12.75, 0.04); rise(kb, t, 12.6, 120); const lift = E3((t - 13.2) / 0.5); tf(sh2, `translateY(${-lift * 0}px)`); outAt(sh2, t, 15.2); outAt(kb, t, 15.2); }
      const I = win(t, 15.5, 17.9); sh3.style.display = I ? 'block' : 'none'; if (I) { letters(sh3, t, 15.55, 0.03); outAt(sh3, t, 17.6); }
      end(t);
    };
  }, caps: [[2.8, 6.0, 'It goes to work inside your GHL.'], [6.0, 10.3, 'Pipelines. Workflows. Calendars.'], [10.3, 12.6, 'Whatever you tell it.']] },

  // ---------------- AGENT 2: One prompt, whole build ----------------
  ag2: { dur: 18.5, music: 'agent', build() {
    const bgu = agentBG(); const th = AG;
    const PROMPT = 'Build a pipeline, a booking calendar and a follow-up workflow for my roofing clients.';
    const bar = el(S, `left:80px;top:430px;width:920px;min-height:150px;background:${th.card};border:2px solid ${th.lime};border-radius:28px;padding:30px 34px;box-shadow:0 0 0 10px rgba(200,255,46,.06),0 30px 80px rgba(0,0,0,.6)`, `<div data-t class="mono" style="font-size:34px;line-height:1.35;color:#fff"></div>`);
    const lbl = el(S, `left:80px;top:370px;font:700 22px Inter;color:${th.dim}`, 'YourGHLAgent');
    const T = [['Pipeline', 'New → Quoted → Won'], ['Calendar', 'Booking page live'], ['Workflow', 'Follow-up in 5 min'], ['Contacts', 'Leads tagged'], ['Email', 'Quote template'], ['Form', 'Roof quote form']];
    const tiles = T.map((x, i) => el(S, `left:0;top:0;width:300px;height:210px;border-radius:22px;background:${th.card};border:1px solid ${th.line};padding:22px;box-shadow:0 24px 60px rgba(0,0,0,.55)`,
      `<div style="font:800 28px Inter;color:#fff">${x[0]}</div><div data-viz style="margin-top:14px;height:90px;position:relative"></div><div style="font:600 18px Inter;color:${th.dim};margin-top:6px">${x[1]}</div><div data-ck style="position:absolute;right:16px;top:16px;width:48px;height:48px;border-radius:50%;background:${th.lime};display:grid;place-items:center;font-size:28px">${CK('#0A0B0D')}</div>`));
    // mini visuals
    tiles.forEach((tl, i) => { const v = tl.querySelector('[data-viz]'); v.innerHTML = i === 0 ? [0, 1, 2].map(k => `<i data-b style="position:absolute;left:${k * 88}px;bottom:0;width:76px;height:20px;border-radius:6px;background:#22262D;display:block"></i>`).join('') : i === 1 ? [...Array(10)].map((_, k) => `<i data-s style="position:absolute;left:${(k % 5) * 52}px;top:${Math.floor(k / 5) * 46}px;width:44px;height:38px;border-radius:8px;background:#22262D;display:block"></i>`).join('') : i === 2 ? `<svg width="256" height="90"><path data-p d="M10 45 H90 M130 45 H210" stroke="${th.lime}" stroke-width="4"/><circle cx="110" cy="45" r="16" fill="none" stroke="${th.lime}" stroke-width="4"/><circle cx="230" cy="45" r="16" fill="${th.lime}"/></svg>` : [...Array(3)].map((_, k) => `<i data-ln style="position:absolute;left:0;top:${k * 30}px;height:16px;border-radius:8px;background:#22262D;display:block;width:0"></i>`).join(''); });
    const acct = crmWindow(S, 'left:70px;top:150px;width:940px;height:640px', th);
    acct.querySelector('[data-body]').innerHTML = `<div style="padding:24px;font:800 28px Inter;color:#fff">Roofing clients · built</div><div data-grid style="position:absolute;left:24px;right:24px;top:84px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px">${T.map(x => `<div style="height:220px;border-radius:16px;background:#101216;border:1px solid ${th.line};padding:16px;font:700 20px Inter;color:#fff">${x[0]}<div style="margin-top:8px;font:600 16px Inter;color:${th.lime}">${CK(th.lime)} ${x[1]}</div></div>`).join('')}</div>`;
    const sh1 = shout(S, 'One prompt.', 170, th.fg, 'top:810px'); const sh2 = shout(S, 'Whole build.', 170, th.lime, 'top:810px');
    const flash = el(S, `left:-500px;top:-500px;width:2080px;height:2080px;background:${th.lime};opacity:0`);
    cue(0.2, 'whoosh'); for (let k = 0; k < 12; k++) cue(0.6 + k * 0.2, 'key'); cue(3.1, 'click'); cue(3.25, 'impact'); [4.8, 5.6, 6.4, 7.2, 8.0, 8.8].forEach(x => cue(x, 'tick')); cue(10.3, 'whoosh'); cue(10.9, 'impact'); cue(14.0, 'impact');
    const end = endCard(S, th, 16.2, 'YourGHLAgent', 'yourghlagent.com', 'Try YourGHLAgent', AGMARK);
    return t => {
      bgu(t);
      const P = t < 3.3; bar.style.display = lbl.style.display = P ? 'block' : 'none';
      if (P) { rise(bar, t, 0.1, 50); rise(lbl, t, 0.1, 20); bar.querySelector('[data-t]').innerHTML = (t < 0.6 ? `<span style="color:${th.dim}">Tell it what to do</span>` : typed(PROMPT, t, 0.6, 36)) + caret(t, th.lime); tf(bar, `scale(${SS.press(t, 3.1)})`); }
      op(flash, t > 3.2 && t < 3.6 ? (1 - (t - 3.2) / 0.4) * 0.5 : 0);
      const X = win(t, 3.2, 11.2); const shake = t > 3.2 && t < 3.7 ? Math.sin(t * 90) * 10 * (1 - (t - 3.2) / 0.5) : 0; S.style.translate = `${shake}px ${-shake * 0.6}px`;
      tiles.forEach((tl, i) => {
        tl.style.display = X ? 'block' : 'none'; if (!X) return;
        const a = i / 6 * Math.PI * 2 - Math.PI / 2 + (t - 3.2) * 0.12; const ex = sp(t - 3.2, 9, 0.55); const back = E3((t - 10.3) / 0.7);
        const R = 330 * ex; const gx = 70 + 150 + 24 + (i % 3) * 302, gy = 150 + 56 + 84 + Math.floor(i / 3) * 234;
        const x = lerp(540 + Math.cos(a) * R * 1.15 - 150, gx, back), y = lerp(500 + Math.sin(a) * R * 0.95 - 105, gy, back);
        const focus = Math.exp(-Math.pow((t - (4.4 + i * 0.8)) / 0.35, 2));
        op(tl, cl((t - 3.2) / 0.1) * (1 - cl((t - 10.9) / 0.2))); tf(tl, `translate(${x}px,${y}px) rotate(${(1 - ex) * (i - 2.5) * 40 + Math.sin(t + i) * 2 * (1 - back)}deg) scale(${(0.86 + 0.22 * focus) * lerp(1, 0.9, back)})`); tl.style.zIndex = focus > 0.5 ? 5 : 1; tl.style.borderColor = focus > 0.3 ? th.lime : th.line;
        const ck = tl.querySelector('[data-ck]'); const st = SS.stamp(t, 4.8 + i * 0.8); op(ck, st.op); tf(ck, `scale(${t < 4.8 + i * 0.8 ? 0 : st.s})`);
        const lt = t - (4.2 + i * 0.8);
        tl.querySelectorAll('[data-b]').forEach((b, k) => b.style.height = (20 + 60 * E3((lt - k * 0.15) / 0.5) * [0.5, 0.8, 1][k]) + 'px');
        tl.querySelectorAll('[data-s]').forEach((s, k) => s.style.background = lt > k * 0.06 && k % 3 !== 1 ? th.lime : '#22262D');
        tl.querySelectorAll('[data-ln]').forEach((l, k) => l.style.width = 220 * E3((lt - k * 0.15) / 0.4) * [1, 0.8, 0.6][k] + 'px');
        const pth = tl.querySelector('[data-p]'); if (pth) { pth.style.strokeDasharray = 200; pth.style.strokeDashoffset = 200 * (1 - E3(lt / 0.6)); }
      });
      const A = win(t, 10.8, 16.3); acct.style.display = A ? 'block' : 'none'; if (A) { const k = sp(t - 10.8, 12, 0.6); op(acct, cl((t - 10.8) / 0.15) * (1 - cl((t - 16.0) / 0.25))); tf(acct, `scale(${lerp(1.06, 1, k)})`); acct.style.boxShadow = `0 0 0 ${3 + 3 * Math.sin(t * 4)}px rgba(200,255,46,.5),0 30px 80px rgba(0,0,0,.5)`; }
      sh1.style.display = win(t, 11.4, 14.0) ? 'block' : 'none'; letters(sh1, t, 11.45); sh2.style.display = win(t, 14.0, 16.1) ? 'block' : 'none'; letters(sh2, t, 14.05);
      end(t);
    };
  }, caps: [[0.2, 3.2, 'Tell it what to do.'], [3.6, 10.6, 'It builds every piece inside your GHL.']] },

  // ---------------- SUPPORT 1: The 60-minute race ----------------
  sp1: { dur: 22.5, music: 'support', build() {
    const bgu = supportBG(); const th = SPT;
    const sh = shout(S, 'GHL support sucks.', 118, th.ink, 'top:420px'); const scr = el(S, 'left:180px;top:560px', `<svg width="720" height="40"><path data-u d="M10 26 C 160 6, 320 36, 480 16 S 660 30, 710 14" stroke="${th.red}" stroke-width="10" fill="none" stroke-linecap="round"/></svg>`);
    const L = el(S, `left:30px;top:110px;width:500px;height:720px;background:${th.card};border:2px solid ${th.line};border-radius:26px;padding:26px;overflow:hidden`, `<div style="font:800 30px Inter;color:${th.ink}">Support queue</div><div data-days style="margin-top:6px;font:700 22px Inter;color:${th.red}"></div><div data-rows style="margin-top:18px;display:grid;gap:10px"></div>`);
    const R = el(S, `left:550px;top:110px;width:500px;height:720px;background:${th.card};border:2px solid ${th.or};border-radius:26px;padding:26px;overflow:hidden`, `<div style="font:800 30px Inter;color:${th.ink}">YourGHLSupport</div><div data-clock class="mono" style="margin-top:10px;font:700 110px 'JetBrains Mono';color:${th.or};letter-spacing:-.04em">60:00</div><div data-chat style="margin-top:10px;display:grid;gap:10px"></div>`);
    const stamp = el(S, `left:600px;top:560px;padding:16px 34px;border:8px solid ${th.green};border-radius:18px;color:${th.green};font:900 70px Inter;letter-spacing:-.02em;background:#fff`, 'SOLVED');
    const ROWS = ['Ticket #48213 · Waiting', 'Reply: "We\'re looking into it"', 'Ticket #48213 · Waiting', 'Escalated · No update', 'Ticket #48213 · Still waiting', 'Reply: "Can you send a video?"'];
    const CHAT = [[3.2, 'u', 'My SMS workflow stopped sending.'], [4.2, 'us', 'On it.'], [6.6, 'us', 'Found it. The trigger filter was off.'], [8.4, 'us', 'Fixed and tested.']];
    const hard = el(S, `left:60px;top:200px;width:960px;background:${th.card};border:2px solid ${th.line};border-radius:26px;padding:34px`, `<div style="font:800 40px Inter;color:${th.ink}">Needs a fix only GHL can make?</div><div style="margin-top:8px;font:600 26px Inter;color:${th.mute}">We open the ticket and chase it for you.</div><div style="position:relative;margin-top:60px;height:200px"><svg width="892" height="40" style="position:absolute;top:44px;left:0"><path data-tl d="M60 20 H832" stroke="${th.or}" stroke-width="6"/></svg>${['Ticket opened', 'Followed up', 'Followed up again', 'SOLVED'].map((s, i) => `<div data-st style="position:absolute;left:${i * 257}px;top:0;width:120px;text-align:center"><div style="width:120px;height:120px;border-radius:50%;background:${i === 3 ? th.green : th.or};display:grid;place-items:center;color:#fff;font-size:54px">${i === 3 ? CK('#fff') : i + 1}</div><div style="margin-top:14px;font:800 ${i === 3 ? 28 : 22}px Inter;color:${i === 3 ? th.green : th.ink};width:220px;margin-left:-50px">${s}</div></div>`).join('')}</div>`);
    const line1 = el(S, `left:0;right:0;top:360px;text-align:center;font:900 84px Inter;letter-spacing:-.04em;color:${th.ink};line-height:1.02`, `Any GHL issue.<br><span style="color:${th.or}">Solved in 60 minutes.</span>`);
    cue(0.15, 'impact'); ROWS.forEach((r, i) => cue(2.6 + i * 1.3, 'pop')); CHAT.forEach(c => cue(c[0], 'pop')); cue(9.2, 'impact'); cue(11.0, 'whoosh'); [11.8, 12.9, 14.0, 15.1].forEach(x => cue(x, 'tick')); cue(15.1, 'ding'); cue(16.6, 'whoosh');
    const end = endCard(S, th, 19.8, 'YourGHLSupport', 'yourghlsupport.com', 'Get 60-Minute GHL Support', SPMARK);
    return t => {
      bgu(t);
      const H = t < 2.3; sh.style.display = scr.style.display = H ? 'block' : 'none'; if (H) { letters(sh, t, 0.05, 0.025); const u = scr.querySelector('[data-u]'); u.style.strokeDasharray = 760; u.style.strokeDashoffset = 760 * (1 - E3((t - 0.8) / 0.5)); outAt(sh, t, 2.0); outAt(scr, t, 2.0); }
      const Sp = win(t, 2.2, 10.9); L.style.display = R.style.display = Sp ? 'block' : 'none';
      if (Sp) {
        const k = sp(t - 2.2, 11, 0.7); tf(L, `translateX(${(1 - k) * -300}px)`); tf(R, `translateX(${(1 - k) * 300}px)`); op(L, k); op(R, k); outAt(L, t, 10.6); outAt(R, t, 10.6);
        const days = Math.min(6, Math.floor(pos(t - 2.4) / 1.2) + 1); L.querySelector('[data-days]').textContent = `Waiting ${days} day${days > 1 ? 's' : ''}`;
        L.querySelector('[data-rows]').innerHTML = ROWS.map((r, i) => { const t0 = 2.6 + i * 1.3; if (t < t0) return ''; const kk = E3((t - t0) / 0.3); return `<div style="padding:16px 18px;border-radius:14px;background:#FFF1F2;border:1px solid #FBCFD9;font:700 20px Inter;color:${th.ink};opacity:${kk};transform:translateY(${(1 - kk) * -30}px)"><span style="color:${th.red}">Day ${Math.min(i + 1, 6)}</span> · ${r}</div>`; }).join('');
        const solvedAt = 9.2; const tc = Math.min(t, solvedAt); const sec = Math.round(3600 - E3(pos(tc - 2.6) / (solvedAt - 2.6)) * (3600 - 1104)); const mm = String(Math.floor(sec / 60)).padStart(2, '0'), ss = String(sec % 60).padStart(2, '0');
        R.querySelector('[data-clock]').textContent = `${mm}:${ss}`; R.querySelector('[data-clock]').style.color = t > solvedAt ? th.green : th.or;
        R.querySelector('[data-chat]').innerHTML = CHAT.map(c => { if (t < c[0]) return ''; const kk = sp(t - c[0], 15, 0.6); const me = c[1] === 'us'; return `<div style="justify-self:${me ? 'end' : 'start'};max-width:400px;padding:14px 18px;border-radius:18px;background:${me ? th.or : '#F3EBDF'};color:${me ? '#fff' : th.ink};font:700 22px Inter;transform:scale(${kk});transform-origin:${me ? 'right' : 'left'} bottom">${c[2]}</div>`; }).join('');
      }
      stamp.style.display = win(t, 9.2, 10.9) ? 'block' : 'none'; if (t > 9.2) { const st = SS.stamp(t, 9.2); op(stamp, st.op); tf(stamp, `scale(${st.s}) rotate(${-8 + st.rot}deg)`); outAt(stamp, t, 10.6); }
      const Hd = win(t, 10.9, 16.6); hard.style.display = Hd ? 'block' : 'none';
      if (Hd) { rise(hard, t, 10.95, 60); outAt(hard, t, 16.3); const tl = hard.querySelector('[data-tl]'); tl.style.strokeDasharray = 772; tl.style.strokeDashoffset = 772 * (1 - E3((t - 11.8) / 3.3)); hard.querySelectorAll('[data-st]').forEach((s, i) => pop(s, t, 11.8 + i * 1.1)); }
      const Ln = win(t, 16.6, 19.9); line1.style.display = Ln ? 'block' : 'none'; if (Ln) { rise(line1, t, 16.65, 50); outAt(line1, t, 19.6); }
      end(t);
    };
  }, caps: [[2.4, 9.2, 'They take days. We take minutes.'], [9.3, 10.9, 'Solved.']] },

  // ---------------- SUPPORT 2: Hold music ----------------
  sp2: { dur: 18.5, music: 'hold+support', build() {
    const bgu = supportBG(); const th = SPT; const HOLD = 5.0;
    const holdBg = el(BG, 'inset:0;background:#2A2A2E');
    const card = el(S, `left:190px;top:200px;width:700px;height:640px;border-radius:40px;background:#3A3A40;padding:46px;text-align:center;color:#D8D8DC`, `<div style="font:700 26px Inter;color:#A5A5AD">GHL support line</div><div style="margin-top:14px;font:900 64px Inter;letter-spacing:-.03em;color:#fff">You're on hold</div><div style="margin-top:10px;font:600 26px Inter;color:#A5A5AD">Your call is important to us.</div><div data-eq style="margin:46px auto 0;height:120px;display:flex;gap:10px;justify-content:center;align-items:flex-end">${'<i style="width:22px;border-radius:6px;background:#8E8E96;display:block"></i>'.repeat(9)}</div><div data-pos style="margin-top:36px;font:800 34px Inter;color:#fff"></div><div data-w class="mono" style="margin-top:10px;font:700 30px 'JetBrains Mono';color:#A5A5AD"></div>`);
    const notes = [...Array(6)].map((_, i) => el(S, `left:${200 + i * 130}px;top:860px;font:900 54px Inter;color:#8E8E96`, i % 2 ? '♪' : '♫'));
    const flash = el(BG, `inset:0;background:${th.or};opacity:0`);
    const typing = el(S, `left:300px;top:380px;padding:22px 30px;border-radius:26px;background:#F3EBDF;font:900 40px Inter;color:${th.mute}`, '•••');
    const bub = el(S, `left:300px;top:330px;padding:34px 56px;border-radius:40px 40px 40px 10px;background:${th.or};color:#fff;font:900 120px Inter;letter-spacing:-.04em`, 'On it.');
    const who = el(S, `left:300px;top:270px;font:700 26px Inter;color:${th.ink};display:flex;gap:10px;align-items:center`, `<span style="width:16px;height:16px;border-radius:50%;background:${th.green}"></span>YourGHLSupport · online`);
    const clock = el(S, `left:0;right:0;top:220px;text-align:center;font:700 200px 'JetBrains Mono';letter-spacing:-.05em;color:${th.or}`, '60:00');
    const steps = el(S, 'left:300px;top:500px;display:grid;gap:14px', ['Found the issue', 'Fixed it', 'Tested it'].map(s => `<div data-sx style="font:800 40px Inter;color:${th.ink};display:flex;gap:16px;align-items:center"><span style="color:${th.green}">${CK(th.green)}</span>${s}</div>`).join(''));
    const stamp = el(S, `left:540px;top:740px;padding:18px 44px;border:10px solid ${th.green};border-radius:22px;color:${th.green};font:900 96px Inter;background:#fff`, 'SOLVED');
    const l1 = el(S, `left:0;right:0;top:300px;text-align:center;font:900 96px Inter;letter-spacing:-.04em;color:${th.ink};line-height:1`, `No hold music.`);
    const l2 = el(S, `left:0;right:0;top:440px;text-align:center;font:800 54px Inter;letter-spacing:-.02em;color:${th.ink};line-height:1.15`, `Any issue <span style="color:${th.or}">solved in 60 minutes.</span><br><span style="color:${th.mute};font-size:42px">Or we open the ticket and chase it for you.</span>`);
    cue(HOLD, 'impact'); cue(5.6, 'pop'); cue(6.1, 'pop'); [7.6, 8.3, 9.0].forEach(x => cue(x, 'tick')); cue(9.6, 'impact'); cue(10.6, 'whoosh');
    const end = endCard(S, th, 15.8, 'YourGHLSupport', 'yourghlsupport.com', 'Get 60-Minute GHL Support', SPMARK);
    return t => {
      bgu(t); const h = t < HOLD; holdBg.style.display = card.style.display = h ? 'block' : 'none'; notes.forEach(n => n.style.display = h ? 'block' : 'none');
      if (h) { rise(card, t, 0, 40); card.querySelectorAll('[data-eq] i').forEach((b, i) => b.style.height = (20 + 90 * Math.abs(Math.sin(t * 3 + i * 0.8))) + 'px'); card.querySelector('[data-pos]').textContent = `You are caller #${47 + Math.floor(t * 1.4)}`; const w = 41 * 60 + 12 + Math.floor(t * 211); card.querySelector('[data-w]').textContent = `Waiting ${String(Math.floor(w / 3600)).padStart(2, '0')}:${String(Math.floor(w / 60) % 60).padStart(2, '0')}:${String(w % 60).padStart(2, '0')}`; notes.forEach((n, i) => { const f = ((t * 0.5 + i * 0.17) % 1); op(n, Math.sin(f * Math.PI) * 0.8); tf(n, `translateY(${-f * 260}px) rotate(${Math.sin(t + i) * 20}deg)`); }); }
      op(flash, t > HOLD && t < HOLD + 0.35 ? 1 - (t - HOLD) / 0.35 : 0);
      typing.style.display = win(t, 5.3, 5.95) ? 'block' : 'none'; if (t < 5.95) { pop(typing, t, 5.3); typing.style.opacity = 0.5 + 0.5 * Math.sin(t * 14); }
      const B = win(t, 5.95, 7.2); bub.style.display = who.style.display = B ? 'block' : 'none'; if (B) { pop(bub, t, 6.0); rise(who, t, 5.95, 20); outAt(bub, t, 6.95); outAt(who, t, 6.95); }
      const K = win(t, 7.1, 10.6); clock.style.display = steps.style.display = K ? 'block' : 'none';
      if (K) { rise(clock, t, 7.1, 30); const sec = Math.round(3600 - E3(pos(Math.min(t, 9.6) - 7.1) / 2.5) * (3600 - 1330)); clock.textContent = `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`; clock.style.color = t > 9.6 ? th.green : th.or; steps.querySelectorAll('[data-sx]').forEach((s, i) => rise(s, t, 7.6 + i * 0.7, 30)); outAt(clock, t, 10.3); outAt(steps, t, 10.3); }
      stamp.style.display = win(t, 9.6, 10.6) ? 'block' : 'none'; if (t > 9.6) { const st = SS.stamp(t, 9.6); op(stamp, st.op); tf(stamp, `translateX(-50%) scale(${st.s}) rotate(${-8 + st.rot}deg)`); outAt(stamp, t, 10.35); }
      const Lw = win(t, 10.6, 15.9); l1.style.display = l2.style.display = Lw ? 'block' : 'none'; if (Lw) { rise(l1, t, 10.65, 40); rise(l2, t, 11.6, 40); outAt(l1, t, 15.6); outAt(l2, t, 15.6); }
      end(t);
    };
  }, caps: [[0.3, 4.9, 'Still on hold with GHL support?']] },
};

const CON = CONCEPTS[C]; const upd = CON.build();
const cap = document.createElement('div'); cap.id = 'cap'; document.getElementById('frame').appendChild(cap);
const capY = V ? (FH - 1080) / 2 + 1080 + 40 : 980; cap.style.top = capY + 'px';
const darkC = C.startsWith('ag');
window.DUR = CON.dur; window.CUES = CUES; window.MUSIC = CON.music;
window.render = t => {
  upd(t);
  const c = CON.caps.find(x => t >= x[0] && t < x[1]); const dark = darkC || (C === 'sp2' && t < 5);
  if (!c) { cap.style.opacity = 0; } else {
    if (cap._k !== c[2] + dark) { cap._k = c[2] + dark; cap.innerHTML = `<span style="background:${dark ? 'rgba(255,255,255,.08)' : 'rgba(17,17,17,.06)'};color:${dark ? '#fff' : '#111'}">${c[2]}</span>`; }
    const k = E4((t - c[0]) / 0.3) * (1 - cl((t - c[1] + 0.25) / 0.25)); cap.style.opacity = k; cap.style.transform = `translateY(${(1 - k) * 14}px)`;
  }
};
