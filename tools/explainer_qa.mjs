// explainer_qa.mjs: the required check before any estimate, test or render. Pass/fail rules, plus a contact sheet that
// the agent (or a person) must look at. Exit 0 = pass, 1 = fail (fix and run again), 2 = the page can't be checked.
//   node tools/explainer_qa.mjs page.html [--out qa/] [--tol 6] [--pad 8]
// The page follows the explainer contract (window.VIDEO {w,h,duration}, window.seek(t)) and adds:
//   window.STORYBOARD = { safe: {top,right,bottom,left}, steps: [{ id, title, t0, t1, click, target: {x,y,w,h} }] }
//     target = the element in SCREENSHOT pixels (from targets.json, made by tools/explainer_measure.py)
//   data-qa="shot-<id>"   the <img> of that step's screenshot (any transform; its on-screen box is measured)
//   data-qa="cursor"      the cursor; its hotspot is the element's top-left unless data-hot="x,y" (px inside it)
//   data-qa="box-<id>"    optional highlight you drew; it must hug the target (pad ± tol)
//   data-qa="caption"     caption box; data-qa="read" on anything else that must be read (titles, pills, logos)
// Rules (every one must pass):
//   cursor   at step.click the cursor hotspot is inside the target (in frame pixels), and the target is on screen
//   box      every edge of box-<id> within tol px of target ± pad, from t0+0.3 to t1-0.3
//   safe     captions and data-qa="read" stay inside the safe area at every checked moment
//   lines    captions are at most 2 lines
//   fonts    every declared font loaded
//   hold     the step holds ≥ STORYBOARD.minHold s (default 3; the style sets it) after its click, unless the step says hold:false
//   clear    with STORYBOARD.clear, captions and data-qa="read" never overlap data-qa="app" (the screenshot's frame)
// Writes qa.json (every check, with numbers) and contact.png (one still per step at its click and its middle, the
// expected target in magenta, the cursor hotspot in green, failures in red).
import { createRequire } from 'node:module';
let chromium;
try { ({ chromium } = await import('playwright')); } catch { ({ chromium } = createRequire(import.meta.url)('playwright')); }
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const opt = (n, d) => { const i = argv.indexOf(n); if (i < 0) return d; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const outDir = opt('--out', 'qa'), TOL = +opt('--tol', 6), PAD = +opt('--pad', 8);
const html = argv[0];
if (!html) { console.log('usage: node explainer_qa.mjs page.html [--out qa/] [--tol 6] [--pad 8]'); process.exit(2); }
mkdirSync(outDir, { recursive: true });
const url = /^https?:\/\//.test(html) ? html + (html.includes('?') ? '&' : '?') + 'render' : pathToFileURL(path.resolve(html.split('?')[0])).href + '?' + (html.includes('?') ? html.split('?')[1] + '&' : '') + 'render';
const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'], ...(proxy ? { proxy: { server: proxy } } : {}) });
const probe = await browser.newPage();
await probe.goto(url);
await probe.waitForFunction(() => window.VIDEO && typeof window.seek === 'function', null, { timeout: 30000 });
const V = await probe.evaluate(() => window.VIDEO);
await probe.close();
const page = await browser.newPage({ viewport: { width: V.w, height: V.h }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', (e) => errors.push(String(e.message).slice(0, 300)));
await page.goto(url);
await page.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
const SB = await page.evaluate(() => window.STORYBOARD || null);
if (!SB || !Array.isArray(SB.steps) || !SB.steps.length) {
  console.error('FAIL: window.STORYBOARD with steps is missing. Write the storyboard first (SOP 13, step 3).');
  await browser.close(); process.exit(2);
}
const fonts = await page.evaluate(async () => {
  await Promise.all([...document.fonts].map((f) => f.load().catch(() => {})));
  await document.fonts.ready;
  return [...document.fonts].filter((f) => f.status !== 'loaded').map((f) => f.family);
});
const safe = typeof SB.safe === "number" ? { top: SB.safe, right: SB.safe, bottom: SB.safe, left: SB.safe } : SB.safe || { top: 0, right: 0, bottom: 0, left: 0 };   // a number = the same margin on every side
const checks = [];
const add = (rule, step, ok, detail) => checks.push({ rule, step, ok: !!ok, detail });
add('fonts', null, !fonts.length, fonts.length ? `not loaded: ${[...new Set(fonts)].join(', ')}` : 'all loaded');

/** Seek, then read where everything is on screen (getBoundingClientRect includes every transform). */
async function measureAt(t, id) {
  await page.evaluate(async (t) => { await window.seek(t); await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))); }, t);
  return page.evaluate((id) => {
    const seen = (e) => { let o = 1; for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const cs = getComputedStyle(n); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +cs.opacity; } return o; };
    const box = (e) => { if (!e) return null; const r = e.getBoundingClientRect(); const vis = seen(e) > 0.05 && r.width > 0; return { x: r.x, y: r.y, w: r.width, h: r.height, vis }; };
    const img = document.querySelector(`[data-qa="shot-${id}"]`);
    const cur = document.querySelector('[data-qa="cursor"]');
    const hot = (cur?.dataset.hot || '0,0').split(',').map(Number);
    const caps = [...document.querySelectorAll('[data-qa="caption"]')].map((e) => {
      const r = box(e); const lh = parseFloat(getComputedStyle(e).lineHeight) || parseFloat(getComputedStyle(e).fontSize) * 1.2;
      const pad = parseFloat(getComputedStyle(e).paddingTop) + parseFloat(getComputedStyle(e).paddingBottom);
      return { ...r, lines: Math.round((r.h - pad) / lh), text: e.textContent.trim().slice(0, 80) };
    });
    const reads = [...document.querySelectorAll('[data-qa="read"]')].map((e) => ({ ...box(e), text: (e.textContent || e.getAttribute('alt') || '').trim().slice(0, 40) }));
    return { img: box(img), nat: img ? { w: img.naturalWidth, h: img.naturalHeight } : null, cursor: box(cur), hot,
      drawn: box(document.querySelector(`[data-qa="box-${id}"]`)), caps, reads, app: box(document.querySelector('[data-qa="app"]')) };
  }, id);
}
const toFrame = (m, tg) => {
  const s = m.img.w / m.nat.w;
  return { x: m.img.x + tg.x * s, y: m.img.y + tg.y * (m.img.h / m.nat.h), w: tg.w * s, h: tg.h * (m.img.h / m.nat.h) };
};
// two boxes overlap by more than 2 px (the app = [data-qa="app"], the screenshot's frame)
const hits = (a, b) => Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x) > 2 && Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y) > 2;
const inside = (r) => r.x >= safe.left - 0.5 && r.y >= safe.top - 0.5 && r.x + r.w <= V.w - safe.right + 0.5 && r.y + r.h <= V.h - safe.bottom + 0.5;
const fmt = (r) => r ? `${Math.round(r.x)},${Math.round(r.y)} ${Math.round(r.w)}×${Math.round(r.h)}` : 'none';
const shots = [];

for (const st of SB.steps) {
  const id = st.id;
  // motion-graphics step (no screenshot, no click: prompt/script/website videos): it must hold long enough, keep its cards and
  // headline inside the safe area, and the caption must not cover any of them (checked at the middle of the step)
  if (st.click == null && !st.target) {
    const MINm = Number(SB.minHold ?? 3);
    add('hold', id, st.t1 - st.t0 >= MINm - 1e-6, `on screen ${(st.t1 - st.t0).toFixed(2)} s (style minimum ${MINm} s)`);
    const mid = (st.t0 + st.t1) / 2;
    await page.evaluate((t) => window.seek(t), mid); await page.waitForTimeout(60);
    const r = await page.evaluate((id) => {
      const sh = document.querySelector(`[data-qa="shot-${id}"]`); if (!sh) return null;
      const vis = (e) => { const s = getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) > 0.05; };
      const box = (e) => { const b = e.getBoundingClientRect(); return { x: b.x, y: b.y, w: b.width, h: b.height }; };
      const els = [...sh.querySelectorAll('.card, .row, .h, [data-qa="box"]')].filter((e) => vis(e) && e.getBoundingClientRect().width > 4);
      const cap = document.querySelector('[data-qa="caption"]');
      return { els: els.map((e) => ({ b: box(e), what: (e.className || e.tagName).toString().slice(0, 30) })), cap: cap && vis(cap) ? box(cap) : null };
    }, id);
    if (!r) { add('safe', id, false, `no [data-qa="shot-${id}"] on screen at ${mid.toFixed(2)}s`); continue; }
    const out = r.els.filter((e) => !inside(e.b));
    add('safe', id, !out.length, out.length ? `outside the safe area: ${out.map((e) => `${e.what} ${fmt(e.b)}`).join('; ')}` : `${r.els.length} elements inside`);
    const under = r.cap ? r.els.filter((e) => hits(e.b, r.cap)) : [];
    add('caption', id, !under.length, under.length ? `caption covers ${under.map((e) => e.what).join(', ')}` : 'clear');
    continue;
  }
  if (!st.target) { add('cursor', id, false, 'step has no target (measure it: tools/explainer_measure.py)'); continue; }
  const MIN = Number(SB.minHold ?? 3);
  if (st.hold !== false) add('hold', id, st.t1 - st.click >= MIN - 1e-6, `holds ${(st.t1 - st.click).toFixed(2)} s after the click (style minimum ${MIN} s)`);
  // 1. cursor at the click
  const m = await measureAt(st.click, id);
  if (!m.img || !m.nat?.w) { add('cursor', id, false, `no visible [data-qa="shot-${id}"] image at ${st.click}s`); continue; }
  const T = toFrame(m, st.target);
  const onScreen = T.x >= 0 && T.y >= 0 && T.x + T.w <= V.w && T.y + T.h <= V.h;
  add('target-on-screen', id, onScreen, `target in frame ${fmt(T)}`);
  let hx = null, hy = null;
  if (m.cursor?.vis) { hx = m.cursor.x + m.hot[0]; hy = m.cursor.y + m.hot[1]; }
  const hit = hx !== null && hx >= T.x && hx <= T.x + T.w && hy >= T.y && hy <= T.y + T.h;
  add('cursor', id, hit, hx === null ? `no visible cursor at the click (${st.click}s)` : `cursor ${Math.round(hx)},${Math.round(hy)} vs target ${fmt(T)}`);
  const buf1 = await page.screenshot({ type: 'png' });
  shots.push({ id, t: st.click, label: `${id} · click ${st.click}s`, buf: buf1, T, hot: hx !== null ? [hx, hy] : null, ok: hit && onScreen });
  // 2. a drawn box hugs the target, across the step
  const mid = (st.t0 + st.t1) / 2;
  for (const t of [st.t0 + 0.3, mid, st.t1 - 0.3].filter((t) => t > st.t0 && t < st.t1)) {
    const k = await measureAt(t, id);
    if (k.drawn?.vis && k.img) {
      const E = toFrame(k, st.target), want = { x: E.x - PAD, y: E.y - PAD, w: E.w + 2 * PAD, h: E.h + 2 * PAD };
      const off = Math.max(Math.abs(k.drawn.x - want.x), Math.abs(k.drawn.y - want.y), Math.abs(k.drawn.x + k.drawn.w - want.x - want.w), Math.abs(k.drawn.y + k.drawn.h - want.y - want.h));
      add('box', id, off <= TOL, `at ${t.toFixed(2)}s the box is ${off.toFixed(1)} px off (allowed ${TOL})`);
    }
    for (const c of k.caps.filter((c) => c.vis)) {
      if (SB.clear && k.app?.vis) add('clear', id, !hits(c, k.app), `caption “${c.text}” ${hits(c, k.app) ? 'covers' : 'stays off'} the app (${t.toFixed(2)}s)`);
      add('safe', id, inside(c), `caption “${c.text}” at ${fmt(c)} (${t.toFixed(2)}s)`);
      add('lines', id, c.lines <= 2, `caption “${c.text}” has ${c.lines} lines`);
    }
    for (const r of k.reads.filter((r) => r.vis)) {
      add('safe', id, inside(r), `“${r.text}” at ${fmt(r)} (${t.toFixed(2)}s)`);
      if (SB.clear && k.app?.vis) add('clear', id, !hits(r, k.app), `“${r.text}” ${hits(r, k.app) ? 'covers' : 'stays off'} the app (${t.toFixed(2)}s)`);
    }
  }
  const k = await measureAt(mid, id);
  shots.push({ id, t: mid, label: `${id} · middle ${mid.toFixed(1)}s`, buf: await page.screenshot({ type: 'png' }), T: k.img ? toFrame(k, st.target) : null, hot: null, ok: true });
}
// also the intro / outro and anything between steps: safe area for text
for (const t of [0.5, V.duration - 0.5]) {
  const k = await measureAt(t, '__none__');
  for (const c of k.caps.filter((c) => c.vis)) add('safe', null, inside(c), `caption “${c.text}” at ${fmt(c)} (${t}s)`);
  for (const r of k.reads.filter((r) => r.vis)) add('safe', null, inside(r), `“${r.text}” at ${fmt(r)} (${t}s)`);
  shots.push({ id: t < 1 ? 'intro' : 'outro', t, label: `${t < 1 ? 'intro' : 'outro'} ${t.toFixed(1)}s`, buf: await page.screenshot({ type: 'png' }), T: null, hot: null, ok: true });
}
if (errors.length) add('page-errors', null, false, errors.slice(0, 3).join(' | '));

// contact sheet: draw the overlays in the browser (no extra tools needed)
const cols = 3, cw = 640, ch = Math.round(cw * V.h / V.w);
const sheet = await browser.newPage({ viewport: { width: cols * cw, height: Math.ceil(shots.length / cols) * (ch + 28) } });
await sheet.setContent(`<body style="margin:0;background:#111;font:14px system-ui;color:#fff"><canvas id=c></canvas></body>`);
const b64 = shots.map((s) => ({ ...s, src: 'data:image/png;base64,' + s.buf.toString('base64'), buf: undefined }));
const png = await sheet.evaluate(async ({ b64, cols, cw, ch, VW, safe }) => {
  const c = document.getElementById('c'); c.width = cols * cw; c.height = Math.ceil(b64.length / cols) * (ch + 28);
  const g = c.getContext('2d'); const k = cw / VW;
  for (let i = 0; i < b64.length; i++) {
    const s = b64[i], x = (i % cols) * cw, y = Math.floor(i / cols) * (ch + 28);
    const im = new Image(); im.src = s.src; await im.decode(); g.drawImage(im, x, y + 28, cw, ch);
    g.strokeStyle = 'rgba(255,255,255,.35)'; g.setLineDash([4, 4]); g.strokeRect(x + safe.left * k, y + 28 + safe.top * k, cw - (safe.left + safe.right) * k, ch - (safe.top + safe.bottom) * k); g.setLineDash([]);
    if (s.T) { g.strokeStyle = '#ff00a0'; g.lineWidth = 2; g.strokeRect(x + s.T.x * k, y + 28 + s.T.y * k, s.T.w * k, s.T.h * k); }
    if (s.hot) { g.strokeStyle = '#00e070'; g.lineWidth = 2; g.beginPath(); g.arc(x + s.hot[0] * k, y + 28 + s.hot[1] * k, 7, 0, 7); g.stroke(); }
    g.fillStyle = s.ok ? '#fff' : '#ff4d4d'; g.fillText((s.ok ? '' : 'FAIL · ') + s.label, x + 8, y + 19);
  }
  return c.toDataURL('image/png').split(',')[1];
}, { b64, cols, cw, ch, VW: V.w, safe });
writeFileSync(path.join(outDir, 'contact.png'), Buffer.from(png, 'base64'));
const failed = checks.filter((c) => !c.ok);
writeFileSync(path.join(outDir, 'qa.json'), JSON.stringify({ pass: !failed.length, video: V, tolerance: TOL, pad: PAD, failed, checks }, null, 1));
for (const c of checks) console.log(`${c.ok ? 'ok  ' : 'FAIL'} ${c.rule.padEnd(16)} ${c.step ?? ''} ${c.detail}`);
console.log(failed.length ? `\nQA FAILED: ${failed.length} of ${checks.length} checks. Fix, then run again.` : `\nQA PASSED (${checks.length} checks).`,
  `Now LOOK at ${path.join(outDir, 'contact.png')} before any estimate or render.`);
await browser.close();
process.exit(failed.length ? 1 : 0);
