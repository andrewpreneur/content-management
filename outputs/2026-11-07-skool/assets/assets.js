// Skool launch assets in the onboarding look. One page draws any asset: assets.html?a=<id>.
// Uses engine.js helpers (div, icon, avatar, skel, esc). Community name stays {{COMMUNITY_NAME}}.
'use strict';
const NAME = '{{COMMUNITY_NAME}}';

function bgCanvas(S, w, h, color, opts = {}) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  cv.style.cssText = 'position:absolute;left:0;top:0'; S.appendChild(cv);
  const g = cv.getContext('2d');
  g.fillStyle = opts.base || '#0B0F1A'; g.fillRect(0, 0, w, h);
  const gl = g.createRadialGradient(w * (opts.gx ?? .85), h * (opts.gy ?? .2), 0, w * (opts.gx ?? .85), h * (opts.gy ?? .2), Math.max(w, h) * .9);
  gl.addColorStop(0, color + 'CC'); gl.addColorStop(.45, color + '33'); gl.addColorStop(1, color + '00');
  g.fillStyle = gl; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(255,255,255,.06)';
  for (let y = 18; y < h; y += 30) for (let x = 18; x < w; x += 30) { g.beginPath(); g.arc(x, y, 1.4, 0, 7); g.fill(); }
}
function lightBg(S, w, h) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; cv.style.cssText = 'position:absolute;left:0;top:0'; S.appendChild(cv);
  const g = cv.getContext('2d'); g.fillStyle = '#F4F5F9'; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(15,20,45,.07)'; for (let y = 20; y < h; y += 36) for (let x = 20; x < w; x += 36) { g.beginPath(); g.arc(x, y, 1.6, 0, 7); g.fill(); }
}
const mark = (S, x, y, s = 56) => div(S, `left:${x}px;top:${y}px;width:${s}px;height:${s}px;border-radius:${s * .28}px;background:var(--yel);display:flex;align-items:center;justify-content:center;font:800 ${s * .54}px 'Inter Tight';color:#0B0F1A`, 'A', 'abs');
const chip = (P, x, y, t, ic, o = {}) => div(P, `left:${x}px;top:${y}px;height:${o.h || 56}px;padding:0 ${o.px || 22}px;border-radius:999px;background:${o.bg || 'rgba(255,255,255,.1)'};border:1px solid ${o.bd || 'rgba(255,255,255,.18)'};color:${o.fg || '#fff'};display:flex;align-items:center;gap:10px;font-weight:700;font-size:${o.fs || 22}px`, (ic ? icon(ic, (o.fs || 22) + 2, o.ic || o.fg || '#fff') : '') + esc(t), 'abs');
const num = (P, x, y, s, n, bg = 'var(--acc)') => div(P, `left:${x}px;top:${y}px;width:${s}px;height:${s}px;border-radius:50%;background:${bg};color:#fff;display:flex;align-items:center;justify-content:center;font:800 ${s * .46}px 'Inter Tight'`, String(n), 'abs');

// ---------- course covers (1460x752) ----------
const COURSES = [
  { id: 'course-01-start-here', n: 1, t: 'Start Here', sub: 'Find your starting point', c: '#2E7DFF', icon: 'flag', motif: 'paths' },
  { id: 'course-02-foundations', n: 2, t: 'Foundations', sub: 'The tools, and who you want to help', c: '#F59E0B', icon: 'layers', motif: 'tools' },
  { id: 'course-03-build-with-ai', n: 3, t: 'Build with AI', sub: 'Turn your idea into something people can use', c: '#7C5CFF', icon: 'spark', motif: 'prompt' },
  { id: 'course-04-saas-offers', n: 4, t: 'SaaS Offers', sub: 'Package what you build into an offer', c: '#EC4899', icon: 'tag', motif: 'offer' },
  { id: 'course-05-getting-clients', n: 5, t: 'Getting Clients', sub: 'Reach customers and win your first clients', c: '#10B981', icon: 'trend', motif: 'pipeline' },
  { id: 'course-06-follow-up-delivery', n: 6, t: 'Follow-up & Delivery', sub: 'Follow up, then improve how you deliver', c: '#06B6D4', icon: 'mail', motif: 'sequence' },
  { id: 'course-07-skills-prompts', n: 7, t: 'Skills & Prompts', sub: 'Downloadable skills and prompts library', c: '#F97316', icon: 'download', motif: 'files' },
  { id: 'course-08-coaching-replays', n: 8, t: 'Coaching Replays', sub: 'Work through it on a coaching call', c: '#6366F1', icon: 'users', motif: 'replay' },
];

function motif(S, m, c, x, y) {
  const P = div(S, `left:${x}px;top:${y}px;width:560px;height:520px;transform:rotate(-3deg)`, null, 'abs');
  const card = (cx, cy, w, h, css = '') => div(P, `left:${cx}px;top:${cy}px;width:${w}px;height:${h}px;${css}`, null, 'card');
  const tint = c + '22';
  if (m === 'paths') {
    [["I'm new", 'seed'], ['I have an idea', 'bulb'], ['I have an offer', 'tag']].forEach(([t, ic], i) => {
      const k = card(0, i * 170, 560, 148, i === 1 ? `border:4px solid ${c}` : '');
      num(k, 28, 44, 58, i + 1, c);
      div(k, 'left:110px;top:30px;font-size:15px;color:#8A90A0', 'Path ' + (i + 1), 'abs caps');
      div(k, 'left:110px;top:56px;font-size:40px', esc(t), 'abs tight');
      div(k, `position:absolute;right:28px;top:40px;width:68px;height:68px;border-radius:20px;background:${tint};display:flex;align-items:center;justify-content:center`, icon(ic, 34, c));
    });
  } else if (m === 'tools') {
    const k = card(0, 0, 560, 500);
    div(k, `left:36px;top:34px;font-size:16px;color:${c}`, 'Your toolkit', 'abs caps');
    [['GoHighLevel', 'zap'], ['AI', 'spark'], ['SaaS', 'layers'], ['Automations', 'gear']].forEach(([t, ic], i) => {
      const r = div(k, `left:${36 + (i % 2) * 250}px;top:${80 + Math.floor(i / 2) * 150}px;width:230px;height:130px;border-radius:20px;background:#F6F7FA;display:flex;flex-direction:column;justify-content:center;gap:12px;padding-left:22px`, null, 'abs');
      r.innerHTML = `<span style="width:52px;height:52px;border-radius:16px;background:${tint};display:flex;align-items:center;justify-content:center">${icon(ic, 28, c)}</span><b style="font-size:24px">${t}</b>`;
    });
    const w = div(k, `left:36px;top:390px;width:488px;height:80px;border-radius:18px;background:${c};color:#fff;display:flex;align-items:center;gap:14px;padding-left:22px;font-weight:800;font-size:24px`, icon('target', 30, '#fff') + 'Who do you want to help?', 'abs');
  } else if (m === 'prompt') {
    const k = card(0, 30, 560, 440, 'background:#0F1424;border-color:#0F1424');
    div(k, 'left:36px;top:32px;font-size:16px;color:#B7A8FF;display:flex;gap:10px;align-items:center', icon('prompt', 22, '#B7A8FF') + 'Prompt', 'abs caps');
    div(k, 'position:absolute;left:36px;top:84px;width:488px;color:#E5E9F5;font-size:30px;line-height:1.5;white-space:normal;font-weight:500',
      `Build a booking flow for <span style="background:var(--yel);color:#0B0F1A;padding:0 10px;border-radius:8px;font-weight:700">my gym clients</span> that texts every new lead.`);
    div(k, `left:36px;top:340px;height:64px;padding:0 24px;border-radius:14px;background:${c};color:#fff;display:flex;align-items:center;gap:10px;font-weight:800;font-size:22px`, icon('zap', 24, '#fff') + 'Build it', 'abs');
  } else if (m === 'offer') {
    const k = card(0, 0, 560, 500);
    div(k, `position:absolute;left:0;top:0;width:560px;height:130px;border-radius:22px 22px 0 0;background:linear-gradient(135deg,${c},#0B0F1A)`);
    div(k, 'left:36px;top:40px;font-size:40px;color:#fff', 'AI Receptionist', 'abs tight');
    div(k, 'left:36px;top:92px;font-size:18px;color:rgba(255,255,255,.75)', 'For dental offices', 'abs');
    ['Answers every missed call', 'Books into your calendar', 'Follows up by text'].forEach((t, i) => {
      const r = div(k, `left:36px;top:${160 + i * 74}px;display:flex;align-items:center;gap:16px;font-size:24px;font-weight:600`, null, 'abs');
      r.innerHTML = `<span style="width:38px;height:38px;border-radius:50%;background:var(--ok);display:flex;align-items:center;justify-content:center">${icon('check', 22, '#fff', 3)}</span>${t}`;
    });
    div(k, `left:36px;top:400px;width:488px;height:70px;border-radius:16px;background:${c};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:24px`, 'Start monthly plan', 'abs');
  } else if (m === 'pipeline') {
    [['New lead', 3], ['Booked', 2], ['Client', 1]].forEach(([t, n], i) => {
      const col = div(P, `left:${i * 190}px;top:${20 + i * 20}px;width:176px;height:460px;border-radius:20px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2)`, null, 'abs');
      div(col, 'left:18px;top:18px;font-size:15px;color:#fff', t, 'abs caps');
      for (let j = 0; j < n; j++) {
        const cd = div(col, `left:12px;top:${58 + j * 124}px;width:152px;height:110px;border-radius:16px;background:#fff;box-shadow:0 10px 30px rgba(0,0,0,.2)`, null, 'abs');
        avatar(cd, 14, 14, 38, ['JM', 'RS', 'KL', 'AP', 'TB', 'MN'][i * 2 + j], AV_COLORS[(i * 2 + j) % 8]);
        skel(cd, 14, 66, 110, 10); skel(cd, 14, 84, 70, 10);
        if (i === 2) { cd.style.border = `3px solid ${c}`; div(cd, `position:absolute;right:12px;top:16px;width:30px;height:30px;border-radius:50%;background:var(--ok);display:flex;align-items:center;justify-content:center`, icon('check', 18, '#fff', 3)); }
      }
    });
  } else if (m === 'sequence') {
    [['Day 1', 'Thanks for booking! Here is what happens next.'], ['Day 3', 'Quick check-in: any questions so far?'], ['Day 7', 'Your first results are in. Want a walkthrough?']].forEach(([d, t], i) => {
      const k = card(i * 30, i * 165, 500, 140);
      div(k, `left:28px;top:24px;height:36px;padding:0 14px;border-radius:999px;background:${tint};color:${c};font-weight:800;font-size:16px;display:flex;align-items:center;gap:8px`, icon('mail', 18, c) + d, 'abs');
      div(k, 'position:absolute;left:28px;top:74px;width:440px;font-size:22px;font-weight:600;white-space:normal;line-height:1.3', t);
    });
  } else if (m === 'files') {
    const k = card(0, 0, 560, 500);
    div(k, `left:36px;top:32px;font-size:16px;color:${c};display:flex;gap:10px;align-items:center`, icon('download', 20, c) + 'Downloads', 'abs caps');
    [['Skill', 'Offer builder', 'zap'], ['Prompt', 'Ideal client finder', 'prompt'], ['Skill', 'Follow-up writer', 'mail'], ['Prompt', 'Demo script', 'play']].forEach(([kd, t, ic], i) => {
      const r = div(k, `left:28px;top:${80 + i * 100}px;width:504px;height:84px;border-radius:18px;background:#F6F7FA`, null, 'abs');
      div(r, `position:absolute;left:14px;top:12px;width:60px;height:60px;border-radius:18px;background:${tint};display:flex;align-items:center;justify-content:center`, icon(ic, 30, c));
      div(r, `left:90px;top:14px;font-size:14px;color:${c}`, kd, 'abs caps');
      div(r, 'left:90px;top:36px;font-size:24px;font-weight:700', t, 'abs');
      div(r, `position:absolute;right:16px;top:18px;width:48px;height:48px;border-radius:14px;background:${i < 2 ? 'var(--ok)' : '#fff'};border:1px solid var(--line);display:flex;align-items:center;justify-content:center`, icon(i < 2 ? 'check' : 'download', 22, i < 2 ? '#fff' : '#6B7280', i < 2 ? 3 : 2.2));
    });
  } else if (m === 'replay') {
    const k = card(0, 0, 560, 360);
    const v = div(k, 'position:absolute;left:24px;top:24px;width:512px;height:260px;border-radius:16px;background:linear-gradient(135deg,#1B2340,#0B0F1A);display:flex;align-items:center;justify-content:center');
    div(v, 'width:88px;height:88px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center', icon('play', 38, '#0B0F1A'));
    const bar = div(k, 'position:absolute;left:24px;top:306px;width:512px;height:10px;border-radius:5px;background:#ECEEF3;overflow:hidden');
    div(bar, `position:absolute;left:0;top:0;bottom:0;width:38%;background:${c}`);
    const n = card(70, 330, 460, 150, `border:3px solid ${c}`);
    div(n, `left:26px;top:22px;font-size:15px;color:${c};display:flex;gap:8px;align-items:center`, icon('cal', 18, c) + 'Next coaching call', 'abs caps');
    div(n, 'position:absolute;left:26px;top:58px;width:410px;font-size:26px;font-weight:700;white-space:normal;line-height:1.25', 'Bring one specific thing to work through');
  }
}

function course(S, w, h, c) {
  bgCanvas(S, w, h, c.c);
  mark(S, 72, 70, 64);
  div(S, 'left:156px;top:84px;font-size:19px;color:rgba(255,255,255,.7)', `Course ${String(c.n).padStart(2, '0')}`, 'abs caps');
  div(S, `left:72px;top:190px;width:110px;height:110px;border-radius:32px;background:${c.c};display:flex;align-items:center;justify-content:center;box-shadow:0 16px 40px ${c.c}66`, icon(c.icon, 56, '#fff'), 'abs');
  const ttl = div(S, `position:absolute;left:72px;top:340px;width:700px;color:#fff;font-size:${c.t.length > 13 ? 92 : 108}px;line-height:1.0;white-space:normal`, esc(c.t), 'tight');
  div(S, 'position:absolute;left:74px;bottom:76px;width:700px;color:rgba(255,255,255,.75);font-size:32px;line-height:1.25;white-space:normal;font-weight:500', esc(c.sub));
  motif(S, c.motif, c.c, 830, 120);
}

// ---------- community banner (1084x576, rendered at 2x) ----------
function banner(S, w, h) {
  bgCanvas(S, w, h, '#2E7DFF', { gx: .9, gy: .1 });
  mark(S, 56, 56, 52);
  div(S, 'left:56px;top:150px;font-size:15px;color:rgba(255,255,255,.65)', 'Community', 'abs caps');
  div(S, 'left:56px;top:182px;font-size:50px;color:#fff', esc(NAME), 'abs tight');
  div(S, 'position:absolute;left:58px;top:270px;width:640px;font-size:27px;line-height:1.3;color:rgba(255,255,255,.85);font-weight:500;white-space:normal',
    'Build and grow an online business using <span style="color:var(--yel);font-weight:700">AI, SaaS, and GoHighLevel.</span>');
  const row = div(S, 'left:56px;top:420px;display:flex;gap:12px', null, 'abs');
  [['Training', 'book'], ['Skills', 'zap'], ['Prompts', 'prompt'], ['Tools', 'wrench'], ['Coaching', 'users']].forEach(([t, ic]) => {
    const c = chip(row, 0, 0, t, ic, { h: 50, fs: 19, px: 18 }); c.style.position = 'relative'; c.style.left = c.style.top = 'auto'; });
  // mini app window, right side
  const k = div(S, 'left:812px;top:110px;width:420px;height:400px;transform:rotate(-4deg)', null, 'card');
  div(k, 'left:24px;top:22px;width:30px;height:30px;border-radius:9px;background:var(--yel)', null, 'abs');
  skel(k, 66, 30, 150, 12);
  ['Community', 'Classroom', 'Calendar'].forEach((t, i) => div(k, `left:${24 + i * 112}px;top:72px;font-size:14px;font-weight:700;color:${i === 1 ? '#0B0F1A' : '#9AA0AE'}`, t, 'abs'));
  div(k, 'position:absolute;left:136px;top:96px;width:84px;height:3px;background:#0B0F1A;border-radius:2px');
  ['#2E7DFF', '#7C5CFF', '#10B981', '#F59E0B'].forEach((col, i) => {
    const cc = div(k, `left:${24 + (i % 2) * 190}px;top:${118 + Math.floor(i / 2) * 136}px;width:176px;height:122px;border-radius:14px;overflow:hidden;border:1px solid var(--line)`, null, 'abs');
    div(cc, `position:absolute;left:0;top:0;right:0;height:62px;background:linear-gradient(135deg,${col},#0B0F1A)`);
    skel(cc, 12, 76, 120, 10); skel(cc, 12, 98, 80, 8);
  });
}

// ---------- pinned post graphics (1600x900) ----------
function pinned(S, w, h, kind) {
  bgCanvas(S, w, h, kind === 'ask' ? '#6D5DFC' : kind === 'intro' ? '#10A765' : '#2E7DFF', { gx: .92, gy: .05 });
  mark(S, 80, 76, 60);
  div(S, 'left:162px;top:84px;font-size:19px;color:rgba(255,255,255,.7);display:flex;gap:10px;align-items:center', icon('pin', 22, 'rgba(255,255,255,.7)') + 'Pinned', 'abs caps');
  if (kind === 'welcome') {
    div(S, 'left:80px;top:200px;font-size:40px;color:rgba(255,255,255,.75)', 'Welcome to', 'abs serif');
    div(S, 'position:absolute;left:80px;top:260px;width:780px;font-size:62px;color:#fff;line-height:1.02;white-space:normal', esc(NAME), 'tight');
    div(S, 'position:absolute;left:82px;top:470px;width:700px;font-size:30px;line-height:1.35;color:rgba(255,255,255,.8);font-weight:500;white-space:normal',
      'Training, strategies, skills, tools and coaching to build and grow an online business using AI, SaaS, and GoHighLevel.');
    const k = div(S, 'left:900px;top:150px;width:620px;height:620px', null, 'card');
    div(k, 'left:40px;top:38px;font-size:17px;color:var(--acc)', 'Start here', 'abs caps');
    [['Introduce yourself', "Where you're at, what you want to build, your goal this week", 'comment'], ['Pick your path', "New, have an idea, or have an offer", 'flag'], ['Head into the Classroom', 'Find the lesson that gets you to this week\'s goal', 'book']].forEach(([t, s2, ic], i) => {
      const r = div(k, `left:30px;top:${86 + i * 172}px;width:560px;height:152px;border-radius:20px;background:#F6F7FA`, null, 'abs');
      num(r, 24, 24, 56, i + 1);
      div(r, 'left:100px;top:26px;font-size:30px', t, 'abs tight');
      div(r, 'position:absolute;left:100px;top:72px;width:430px;font-size:21px;color:#5B6272;line-height:1.3;white-space:normal', esc(s2));
    });
  } else if (kind === 'intro') {
    div(S, 'position:absolute;left:80px;top:200px;width:700px;font-size:96px;color:#fff;line-height:1.0;white-space:normal', 'Introduce yourself', 'tight');
    div(S, 'position:absolute;left:82px;top:430px;width:640px;font-size:32px;line-height:1.35;color:rgba(255,255,255,.82);font-weight:500;white-space:normal',
      'Your first post can be simple. Copy the three lines on the right and fill them in.');
    chip(S, 80, 600, 'Post in Introductions', 'comment', { h: 64, fs: 24 });
    const k = div(S, 'left:860px;top:150px;width:660px;height:620px', null, 'card');
    avatar(k, 40, 40, 60, 'You', '#334155').style.fontSize = '17px';
    div(k, 'left:118px;top:54px;font-size:34px;font-weight:700', 'Hey everyone!', 'abs');
    [["Where I'm at", 'e.g. running a small agency'], ['What I want to build', 'e.g. a booking app for gyms'], ['My goal this week', 'e.g. finish my offer page']].forEach(([l, ex], i) => {
      const r = div(k, `left:36px;top:${140 + i * 138}px;width:588px;height:118px;border-radius:20px;background:#F6F7FA`, null, 'abs');
      num(r, 22, 30, 56, i + 1, '#10A765');
      div(r, 'left:100px;top:26px;font-size:16px;color:#10A765', l, 'abs caps');
      div(r, 'left:100px;top:56px;font-size:27px;color:#9AA0AE;font-weight:600', esc(ex), 'abs');
    });
    div(k, 'left:466px;top:546px;width:158px;height:54px;border-radius:12px;background:#10A765;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:22px', 'Post', 'abs');
  } else {
    div(S, 'position:absolute;left:80px;top:200px;width:720px;font-size:88px;color:#fff;line-height:1.02;white-space:normal', 'How to ask a question that gets answered', 'tight');
    div(S, 'position:absolute;left:82px;top:520px;width:640px;font-size:30px;line-height:1.35;color:rgba(255,255,255,.82);font-weight:500;white-space:normal',
      'That gives people enough context to help.');
    [['Goal', 'target'], ['Tried', 'wrench'], ['Stuck', 'q']].forEach(([t, ic], i) => chip(S, 80 + i * 170, 640, t, ic, { h: 60, fs: 24 }));
    const k = div(S, 'left:860px;top:130px;width:660px;height:660px', null, 'card');
    div(k, 'left:40px;top:36px;font-size:17px;color:#6D5DFC;display:flex;gap:10px;align-items:center', icon('q', 22, '#6D5DFC') + 'Your question', 'abs caps');
    [['What you want to accomplish', 'Text every new lead within 5 minutes'], ["What you've tried", 'Added a wait step and a tag trigger'], ["Where you're stuck", 'It never sends the second text'], ['The decision you need help making', 'Form trigger or call trigger?']].forEach(([l, ex], i) => {
      const r = div(k, `left:36px;top:${86 + i * 136}px;width:588px;height:118px;border-radius:20px;background:#F6F7FA`, null, 'abs');
      num(r, 22, 30, 56, i + 1, '#6D5DFC');
      div(r, 'left:100px;top:26px;font-size:16px;color:#6D5DFC', l, 'abs caps');
      div(r, 'left:100px;top:56px;font-size:25px;font-weight:600', esc(ex), 'abs');
    });
  }
}

// ---------- weekly goal / win templates (1080x1080) ----------
const TPL = {
  'template-1-goal-this-week': { c: '#2E7DFF', icon: 'target', kick: 'My goal this week', title: 'This week I will finish', rows: ['The one outcome', 'The lesson or resource I\'ll use', 'Done by (day)'] },
  'template-2-weekly-win': { c: '#10A765', icon: 'flag', kick: 'Weekly win', title: 'I finished it.', rows: ['What I finished', 'What I learned', "What I'm doing next"] },
  'template-3-progress-update': { c: '#6D5DFC', icon: 'trend', kick: 'Progress update', title: "Here's where I'm at", rows: ["What I'm building", 'What moved forward this week', "Where I'm stuck"] },
  'template-4-shipped': { c: '#F97316', icon: 'play', kick: 'Shipped', title: 'It works!', rows: ['What I built', 'Who it\'s for', 'Try it / see the demo'] },
  'template-5-seven-days': { c: '#F59E0B', icon: 'cal', kick: 'My next 7 days', title: 'One thing to accomplish', rows: ['My target', 'First step (today)', 'Check-in day'], days: true },
};
function template(S, w, h, t) {
  bgCanvas(S, w, h, t.c, { gx: .95, gy: 0 });
  mark(S, 64, 64, 54);
  div(S, 'left:136px;top:76px;font-size:17px;color:rgba(255,255,255,.7)', esc(NAME), 'abs caps');
  div(S, `left:64px;top:170px;width:96px;height:96px;border-radius:28px;background:${t.c};display:flex;align-items:center;justify-content:center`, icon(t.icon, 50, '#fff'), 'abs');
  div(S, `left:186px;top:186px;font-size:20px;color:${t.c === '#F59E0B' ? 'var(--yel)' : '#fff'}`, esc(t.kick), 'abs caps');
  div(S, 'left:186px;top:214px;font-size:48px;color:#fff', esc(t.title), 'abs tight');
  const step = t.days ? 160 : 208, rh = t.days ? 140 : 188;
  const k = div(S, `left:64px;top:320px;width:952px;height:${t.days ? 520 : 668}px`, null, 'card');
  t.rows.forEach((l, i) => {
    const r = div(k, `left:36px;top:${36 + i * step}px;width:880px;height:${rh}px;border-radius:22px;background:#F6F7FA`, null, 'abs');
    num(r, 26, (rh - 64) / 2, 64, i + 1, t.c);
    div(r, `left:118px;top:30px;font-size:18px;color:${t.c}`, esc(l), 'abs caps');
    div(r, `position:absolute;left:118px;top:${rh - 52}px;width:720px;height:3px;border-radius:2px;background:#D5D9E3`);
  });
  if (t.days) {
    'MTWTFSS'.split('').forEach((d, i) => {
      const e = div(S, `left:${64 + i * 138}px;top:880px;width:124px;height:130px;border-radius:24px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;font:800 40px 'Inter Tight'`, `<span style="font:700 14px Inter;letter-spacing:.14em;opacity:.7">DAY</span>${i + 1}`, 'abs');
    });
  } else {
    div(S, 'left:64px;top:1020px;font-size:20px;color:rgba(255,255,255,.6);font-weight:600', 'Copy, fill in, post. Tag it so others can cheer you on.', 'abs');
  }
}

const ASSETS = {};
COURSES.forEach(c => ASSETS[c.id] = { w: 1460, h: 752, draw: S => course(S, 1460, 752, c) });
ASSETS['community-banner'] = { w: 1084, h: 576, scale: 2, draw: S => banner(S, 1084, 576) };
ASSETS['pinned-1-welcome'] = { w: 1600, h: 900, draw: S => pinned(S, 1600, 900, 'welcome') };
ASSETS['pinned-2-introduce-yourself'] = { w: 1600, h: 900, draw: S => pinned(S, 1600, 900, 'intro') };
ASSETS['pinned-3-how-to-ask'] = { w: 1600, h: 900, draw: S => pinned(S, 1600, 900, 'ask') };
Object.entries(TPL).forEach(([id, t]) => ASSETS[id] = { w: 1080, h: 1080, draw: S => template(S, 1080, 1080, t) });
window.ASSETS = ASSETS;

(function () {
  const id = new URLSearchParams(location.search).get('a');
  if (!id || !ASSETS[id]) return;
  const a = ASSETS[id], S = document.getElementById('stage');
  S.style.width = a.w + 'px'; S.style.height = a.h + 'px';
  a.draw(S);
  window.READY = true;
})();
