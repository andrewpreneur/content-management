// Med spa staff training: "How to collect payments and deposits through the platform". index.html?fmt=h|v
// Art on a 1080x1080 stage (centred in 16:9, middle band in 9:16). Timed to ElevenLabs VO word stamps (words.js).
const Q = new URLSearchParams(location.search), V = Q.get('fmt') === 'v';
const FW = V ? 1080 : 1920, FH = V ? 1920 : 1080;
document.documentElement.style.cssText = document.body.style.cssText = `width:${FW}px;height:${FH}px`;
const { cl, lerp, ease, spring } = SS; const E3 = ease.outCubic, E4 = ease.outQuart;
const sp = (x, w = 14, z = 0.6) => spring(x, w, z);
const S = document.getElementById('stage'), BG = document.getElementById('bgx');
if (V) { S.style.left = '0px'; S.style.top = '330px'; } else { const z = 1.18; S.style.zoom = z; S.style.left = (960 - 540 * z) / z + 'px'; S.style.top = (470 - 480 * z) / z + 'px'; } // 16:9: stage zoomed so the cards fill the frame
const C = { bg: '#FBF6F2', ink: '#241F1D', rose: '#C2657A', roseL: '#F6E3E6', sage: '#3F8B65', sageL: '#E2F0E8', mute: '#8B817B', card: '#FFFFFF', line: '#EDE3DC', red: '#D64545' };
function el(p, css = '', html = '') { const d = document.createElement('div'); d.className = 'a'; d.style.cssText = css; d.innerHTML = html; p.appendChild(d); return d; }
const tf = (e, s) => e.style.transform = s, op = (e, o) => e.style.opacity = o, bl = (e, b) => e.style.filter = b > .3 ? `blur(${b}px)` : 'none';
function pop(e, t, t0, base = '') { const k = sp(t - t0, 15, 0.55); op(e, cl((t - t0) / 0.08)); tf(e, `${base} scale(${t < t0 ? 0 : k})`); }
function rise(e, t, t0, dy = 40, base = '') { const k = E4((t - t0) / 0.45); op(e, k); bl(e, (1 - k) * 8); tf(e, `${base} translateY(${(1 - k) * dy}px)`); }
function outAt(e, t, t1, d = 0.25) { const k = cl((t - t1) / d); if (k > 0) { op(e, (+e.style.opacity || 1) * (1 - k)); bl(e, k * 10); } }
const win = (t, a, b) => t >= a && t < b;
const CUES = []; const cue = (t, k) => CUES.push([+t.toFixed(3), k]);
const CK = (c, s = '1em') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" style="vertical-align:-.15em"><path d="M5 12.5l4.5 4.5L19 7.5" stroke="${c}" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ICON = {
  link: c => `<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.4" stroke-linecap="round"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/></svg>`,
  phone: c => `<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.2" stroke-linejoin="round"><path d="M5 3h3l2 5-2.5 1.5a11 11 0 0 0 7 7L16 14l5 2v3a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>`,
  card: c => `<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.2"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6 15h4"/></svg>`,
  user: c => `<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>`,
  globe: c => `<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>`,
  spark: c => `<svg width="1em" height="1em" viewBox="0 0 24 24" fill="${c}"><path d="M12 2l2.2 6.8L21 11l-6.8 2.2L12 20l-2.2-6.8L3 11l6.8-2.2z"/></svg>`,
  cal: c => `<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2.2"><rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>`,
};
const card = (p, css, html = '') => el(p, `background:${C.card};border:1px solid ${C.line};border-radius:28px;box-shadow:0 2px 2px rgba(36,31,29,.04),0 24px 60px rgba(36,31,29,.10);${css}`, html);
const kick = (p, txt, y, color = C.rose) => el(p, `left:0;right:0;top:${y}px;text-align:center;font:800 22px Inter;letter-spacing:.22em;color:${color}`, txt);
const pill = (p, html, css, bg, fg) => el(p, `padding:16px 30px;border-radius:999px;background:${bg};color:${fg};font:800 34px Inter;white-space:nowrap;${css}`, html);
function strike(p, css) { return el(p, `height:7px;border-radius:4px;background:${C.red};transform-origin:0 50%;${css}`); }

BG.style.background = C.bg;
const dots = el(BG, `inset:0;background-image:radial-gradient(rgba(36,31,29,.06) 1.5px,transparent 1.5px);background-size:46px 46px`);
const glow = el(BG, `inset:0;background:radial-gradient(900px 600px at 50% 40%, rgba(194,101,122,.10), transparent 70%)`);

const SC = []; // [t0, t1, update]
const scene = (t0, t1, build) => { const g = el(S, 'inset:0;display:none'); const u = build(g); SC.push([t0, t1, g, u]); };

// 1. Title 0–3.3
scene(0, 3.3, g => {
  const k = kick(g, 'STAFF TRAINING', 300); const h = el(g, `left:0;right:0;top:350px;text-align:center;font:700 96px Fraunces;line-height:1.04;color:${C.ink}`, `How to collect<br>payments <span style="color:${C.rose}">&amp; deposits</span>`);
  const s = el(g, `left:0;right:0;top:580px;text-align:center;font:600 34px Inter;color:${C.mute}`, 'through the platform');
  cue(0.05, 'whoosh');
  return t => { rise(k, t, 0.05, 20); rise(h, t, 0.2, 50); rise(s, t, 2.0, 24); };
});
// 2. The rule 3.3–7.15
scene(3.3, 7.15, g => {
  const k = kick(g, 'THE ONE RULE', 260);
  const c = card(g, 'left:140px;top:330px;width:800px;padding:44px', `<div style="font:700 30px Inter;color:${C.mute}">Deposits only come through</div><div style="margin-top:14px;font:700 64px Fraunces;color:${C.ink}">your live booking links</div>
    <div data-u style="margin-top:30px;display:flex;align-items:center;gap:16px;padding:20px 26px;border-radius:18px;background:${C.roseL};font:700 32px Inter;color:${C.rose}"><span style="font-size:36px">${ICON.link(C.rose)}</span>yourspa.com/book</div>`);
  const b = pill(g, `${ICON.card('#fff')} Deposit collected`, 'left:540px;top:720px;', C.sage, '#fff');
  cue(3.35, 'whoosh'); cue(6.1, 'pop');
  return t => { rise(k, t, 3.35, 20); rise(c, t, 3.5, 60); const st = SS.stamp(t, 6.1); op(b, t < 6.1 ? 0 : st.op); tf(b, `translateX(-50%) scale(${t < 6.1 ? 0 : st.s}) rotate(${st.rot}deg)`); };
});
// phone mock used by scene 3
function phone(p, x, y) {
  return el(p, `left:${x}px;top:${y}px;width:380px;height:720px;border-radius:56px;background:#1E1A19;padding:14px;box-shadow:0 30px 70px rgba(36,31,29,.25)`,
    `<div style="position:relative;width:100%;height:100%;border-radius:44px;background:#fff;overflow:hidden;padding:46px 26px">
      <div style="font:800 15px Inter;letter-spacing:.18em;color:${C.rose}">BOOK ONLINE</div><div style="margin-top:8px;font:700 34px Fraunces;color:${C.ink}">Lip filler consult</div>
      <div style="margin-top:20px;font:700 17px Inter;color:${C.mute}">Choose a time</div>
      <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:10px">${['10:00', '11:30', '1:00', '2:30'].map((s, i) => `<div data-slot="${i}" style="padding:16px 0;text-align:center;border-radius:14px;border:2px solid ${C.line};font:700 22px Inter;color:${C.ink}">${s}</div>`).join('')}</div>
      <div style="margin-top:22px;padding:18px;border-radius:16px;background:${C.bg};display:flex;justify-content:space-between;font:700 20px Inter;color:${C.ink}"><span>Deposit</span><span>Due today</span></div>
      <div data-pay style="margin-top:18px;padding:22px 0;text-align:center;border-radius:16px;background:${C.rose};color:#fff;font:800 24px Inter">Pay deposit &amp; book</div>
      <div data-ok style="position:absolute;inset:0;background:${C.sage};display:grid;place-items:center;align-content:center;gap:16px;color:#fff;font:800 32px Inter;text-align:center;opacity:0"><div style="width:110px;height:110px;border-radius:50%;background:rgba(255,255,255,.2);display:grid;place-items:center;font-size:70px;margin:0 auto">${CK('#fff')}</div>Deposit paid<br><span style="font:600 22px Inter;opacity:.85">You're booked</span></div></div>`);
}
// 3. New patient books online 7.15–11.25
scene(7.15, 11.25, g => {
  const k = el(g, `left:90px;top:300px;font:800 22px Inter;letter-spacing:.2em;color:${C.rose}`, 'NEW PATIENT');
  const h = el(g, `left:90px;top:340px;font:700 76px Fraunces;line-height:1.05;color:${C.ink}`, 'Books on<br>your website');
  const n = el(g, `left:90px;top:560px;font:600 32px Inter;color:${C.mute};line-height:1.4`, `Deposit paid<br>at booking ${CK(C.sage)}`);
  const ph = phone(g, 600, 170);
  cue(7.2, 'whoosh'); cue(8.5, 'click'); cue(9.6, 'click'); cue(10.2, 'ding');
  return t => { rise(k, t, 7.2, 20); rise(h, t, 7.3, 40); rise(n, t, 9.4, 24); const k2 = sp(t - 7.2, 10, 0.75); tf(ph, `translateY(${(1 - k2) * 120}px) rotate(${(1 - k2) * 6}deg)`); op(ph, cl((t - 7.2) / 0.2));
    ph.querySelectorAll('[data-slot]').forEach((s, i) => { const on = i === 1 && t > 8.5; s.style.background = on ? C.roseL : '#fff'; s.style.borderColor = on ? C.rose : C.line; s.style.color = on ? C.rose : C.ink; });
    tf(ph.querySelector('[data-pay]'), `scale(${SS.press(t, 9.6)})`); const ok = ph.querySelector('[data-ok]'); const u = E3((t - 10.0) / 0.35); op(ok, u); tf(ok, `scale(${lerp(1.08, 1, u)})`); };
});
// 4. New patient calls 11.25–20.4
scene(11.25, 20.4, g => {
  const k = kick(g, 'NEW PATIENT CALLS IN', 110);
  const ring = el(g, `left:490px;top:160px;width:100px;height:100px;border-radius:50%;background:${C.roseL};display:grid;place-items:center;font-size:52px`, ICON.phone(C.rose));
  const no = el(g, 'left:0;right:0;top:300px;text-align:center', '');
  const A = card(g, 'left:150px;top:300px;width:360px;height:150px;display:grid;place-items:center;font:800 40px Inter;color:' + C.ink, `Not in the app`);
  const B = card(g, 'left:570px;top:300px;width:360px;height:150px;display:grid;place-items:center;font:800 40px Inter;color:' + C.ink, `Not in the EMR`);
  const sA = strike(g, 'left:205px;top:372px;width:250px'), sB = strike(g, 'left:625px;top:372px;width:250px');
  const xA = el(g, `left:470px;top:280px;width:56px;height:56px;border-radius:50%;background:${C.red};color:#fff;display:grid;place-items:center;font:900 34px Inter`, '×');
  const xB = el(g, `left:890px;top:280px;width:56px;height:56px;border-radius:50%;background:${C.red};color:#fff;display:grid;place-items:center;font:900 34px Inter`, '×');
  // option 1: text the link
  const o1 = card(g, 'left:150px;top:520px;width:360px;height:330px;padding:28px', `<div style="font:800 20px Inter;letter-spacing:.16em;color:${C.rose}">OPTION 1</div><div style="margin-top:8px;font:700 34px Fraunces;color:${C.ink}">Text the live link</div>
    <div data-b style="margin-top:22px;padding:18px 20px;border-radius:22px 22px 22px 6px;background:${C.roseL};font:700 21px Inter;color:${C.ink};line-height:1.35">Here's your booking link:<br><span style="color:${C.rose}">yourspa.com/book</span></div><div data-s style="margin-top:12px;font:700 18px Inter;color:${C.sage}">${CK(C.sage)} Sent</div>`);
  const o2 = card(g, 'left:570px;top:520px;width:360px;height:330px;padding:28px', `<div style="font:800 20px Inter;letter-spacing:.16em;color:${C.rose}">OPTION 2</div><div style="margin-top:8px;font:700 34px Fraunces;color:${C.ink}">Card over the phone?</div>
    <div style="margin-top:18px;font:600 23px Inter;color:${C.mute};line-height:1.4"><span style="font-size:30px">${ICON.card(C.ink)}</span> Book them yourself through the <b style="color:${C.ink}">same live link</b></div><div data-d style="margin-top:20px;display:inline-block;padding:12px 20px;border-radius:999px;background:${C.sage};color:#fff;font:800 21px Inter">${CK('#fff')} Deposit collected</div>`);
  cue(11.3, 'whoosh'); cue(13.0, 'pop'); cue(13.82, 'tick'); cue(14.45, 'tick'); cue(15.35, 'whoosh'); cue(16.6, 'pop'); cue(17.6, 'whoosh'); cue(19.9, 'ding');
  return t => {
    rise(k, t, 11.3, 20); pop(ring, t, 11.35); if (t > 11.35 && t < 12.8) tf(ring, `rotate(${Math.sin(t * 40) * 12 * (1 - cl((t - 12.2) / 0.5))}deg)`);
    rise(A, t, 12.9, 40); rise(B, t, 13.1, 40);
    [[sA, 13.82], [sB, 14.45]].forEach(([s, t0]) => tf(s, `scaleX(${E3((t - t0) / 0.3)})`)); pop(xA, t, 13.85); pop(xB, t, 14.5);
    const dim = E3((t - 15.2) / 0.4); [A, B, sA, sB, xA, xB].forEach(e => e.style.filter = `${dim > 0.01 ? `grayscale(1) opacity(${1 - dim * 0.55})` : 'none'}`);
    rise(o1, t, 15.3, 50); const bb = o1.querySelector('[data-b]'); pop(bb, t, 15.9); op(o1.querySelector('[data-s]'), cl((t - 16.8) / 0.2));
    rise(o2, t, 17.5, 50); const d = o2.querySelector('[data-d]'); const st = SS.stamp(t, 19.85); op(d, t < 19.85 ? 0 : st.op); tf(d, `scale(${t < 19.85 ? 0 : st.s})`);
  };
});
// 5+6. Existing patients 20.45–29.35 (portal card, then manual card); "No deposit" pills
scene(20.45, 29.35, g => {
  const k = kick(g, 'EXISTING PATIENTS', 170, C.ink);
  const P = card(g, 'left:120px;top:250px;width:400px;height:520px;padding:34px', `<div style="font-size:54px">${ICON.user(C.rose)}</div><div style="margin-top:14px;font:700 40px Fraunces;color:${C.ink};line-height:1.1">Book in the<br>patient portal</div>
    <div style="margin-top:22px;display:grid;gap:10px">${['Next visit · Botox', 'Tue · 2:30 PM'].map(s => `<div style="padding:14px 18px;border-radius:14px;background:${C.bg};font:700 21px Inter;color:${C.ink}">${s}</div>`).join('')}</div>`);
  const M = card(g, 'left:560px;top:250px;width:400px;height:520px;padding:34px', `<div style="font-size:54px">${ICON.phone(C.rose)}</div><div style="margin-top:14px;font:700 40px Fraunces;color:${C.ink};line-height:1.1">Call in?<br>Staff books manually</div>
    <div style="margin-top:22px;display:grid;gap:10px">${['Front desk', 'Booked in the calendar'].map(s => `<div style="padding:14px 18px;border-radius:14px;background:${C.bg};font:700 21px Inter;color:${C.ink}">${s}</div>`).join('')}</div>`);
  const n1 = pill(g, 'No deposit', 'left:320px;top:700px;', C.ink, '#fff'), n2 = pill(g, 'No deposit', 'left:760px;top:700px;', C.ink, '#fff');
  cue(20.5, 'whoosh'); cue(23.2, 'pop'); cue(24.7, 'whoosh'); cue(28.3, 'pop');
  return t => { rise(k, t, 20.5, 20); rise(P, t, 20.6, 60); rise(M, t, 24.7, 60);
    [[n1, 23.2], [n2, 28.3]].forEach(([n, t0]) => { const st = SS.stamp(t, t0); op(n, t < t0 ? 0 : st.op); tf(n, `translateX(-50%) scale(${t < t0 ? 0 : st.s}) rotate(${st.rot}deg)`); }); };
});
// 7. Can't find your link 29.4–35.3
scene(29.4, 35.3, g => {
  const h = el(g, `left:0;right:0;top:170px;text-align:center;font:700 80px Fraunces;color:${C.ink}`, `Can't find your link?`);
  const R = [[ICON.globe(C.rose), 'Check your website', 30.95], [ICON.spark(C.rose), 'Ask the AI', 31.84], [ICON.cal(C.rose), `EMR <span data-c>› Calendars</span> <span data-b>› Booking links</span>`, 32.81]].map((r, i) =>
    card(g, `left:150px;top:${330 + i * 150}px;width:780px;height:120px;padding:0 34px;display:flex;align-items:center;gap:24px;font:800 36px Inter;color:${C.ink}`, `<span style="font-size:46px;display:grid">${r[0]}</span><span>${r[1]}</span>`));
  cue(29.45, 'whoosh'); [30.95, 31.84, 32.81].forEach(x => cue(x, 'pop')); cue(33.67, 'tick'); cue(34.38, 'tick');
  return t => { rise(h, t, 29.45, 40); R.forEach((r, i) => rise(r, t, [30.95, 31.84, 32.81][i], 50));
    const c = R[2].querySelector('[data-c]'), b = R[2].querySelector('[data-b]'); c.style.color = t > 33.67 ? C.rose : C.line; b.style.color = t > 34.38 ? C.rose : C.line;
    if (t > 34.38) R[2].style.borderColor = C.rose; };
});
// 8. Summary 35.3–39
scene(35.3, 39.0, g => {
  const L = card(g, 'left:120px;top:300px;width:400px;height:400px;padding:36px', `<div style="font:800 20px Inter;letter-spacing:.18em;color:${C.rose}">NEW PATIENTS</div><div style="margin-top:12px;font:700 50px Fraunces;color:${C.ink};line-height:1.05">Live booking link</div><div style="margin-top:30px;display:inline-block;padding:14px 24px;border-radius:999px;background:${C.sage};color:#fff;font:800 26px Inter">${CK('#fff')} Deposit</div>`);
  const R2 = card(g, 'left:560px;top:300px;width:400px;height:400px;padding:36px', `<div style="font:800 20px Inter;letter-spacing:.18em;color:${C.mute}">EXISTING PATIENTS</div><div style="margin-top:12px;font:700 50px Fraunces;color:${C.ink};line-height:1.05">Portal or manual</div><div style="margin-top:30px;display:inline-block;padding:14px 24px;border-radius:999px;background:${C.ink};color:#fff;font:800 26px Inter">No deposit</div>`);
  const h = el(g, `left:0;right:0;top:190px;text-align:center;font:800 24px Inter;letter-spacing:.22em;color:${C.ink}`, 'REMEMBER');
  cue(35.35, 'whoosh'); cue(35.9, 'pop');
  return t => { rise(h, t, 35.35, 20); rise(L, t, 35.45, 60); rise(R2, t, 35.75, 60); };
});

// captions (2–4 word phrases, active word in rose)
const cap = document.createElement('div'); cap.id = 'cap'; document.getElementById('frame').appendChild(cap);
cap.style.top = (V ? 330 + 1080 + 50 : 960) + 'px';
const PH = []; let cur = []; for (const w of WORDS) { if (cur.length && (cur.length >= 4 || w[1] - cur[cur.length - 1][2] > 0.3 || /[,.?!:]$/.test(cur[cur.length - 1][0]))) PH.push(cur), cur = []; cur.push(w); } PH.push(cur);
PH.forEach((p, i) => { const nx = PH[i + 1]; p.end = nx ? Math.min(p[p.length - 1][2] + 0.35, nx[0][1] - 0.03) : p[p.length - 1][2] + 0.5; });

window.DUR = 39.0; window.CUES = CUES; window.MUSIC = 'medspa';
window.render = t => {
  dots.style.backgroundPosition = `${t * 5}px ${t * 3}px`;
  for (const [t0, t1, g, u] of SC) { const on = t >= t0 && t < t1; g.style.display = on ? 'block' : 'none'; if (!on) continue; u(t); const o = cl((t - (t1 - 0.25)) / 0.25); if (o > 0) { g.style.opacity = 1 - o; g.style.filter = `blur(${o * 8}px)`; } else { g.style.opacity = 1; g.style.filter = 'none'; } }
  const P = PH.find(p => p[0][1] - 0.05 <= t && t <= p.end);
  if (!P) { cap.innerHTML = ''; return; }
  let ai = -1; P.forEach((w, i) => { if (w[1] <= t) ai = i; });
  cap.innerHTML = `<span style="display:inline-block;padding:10px 24px;border-radius:16px;background:rgba(36,31,29,.88)">${P.map((w, i) => `<span class="w" style="color:${i === ai ? '#F2A6B5' : '#fff'}">${w[0].replace(/[,.:]$/, '')}</span>`).join('')}</span>`;
  const u = E4((t - P[0][1] + 0.05) / 0.18); cap.style.opacity = u; cap.style.transform = `translateY(${(1 - u) * 12}px)`;
};
