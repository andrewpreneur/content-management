// render.mjs — seek(t) page -> silent MP4 + cues.json (adapted from the explainer skills' renderer).
//   node render.mjs page.html timing.json fmt(h|v) out_silent.mp4 [fps=30] [subframes=1] [workers=4]
//   node render.mjs page.html timing.json fmt sheet.jpg --stills 0.5,1.2,...   (contact sheet)
//   node render.mjs page.html timing.json fmt framesdir --every 1                (one JPG per second, for review)
import { createRequire } from 'node:module'; const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const [, , html, timing, fmt, out, a5 = '30', a6 = '1', a7 = '4'] = process.argv;
const run = (args) => new Promise((res, rej) => { const p = spawn('ffmpeg', args, { stdio: 'inherit' }); p.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()); });
const url = pathToFileURL(path.resolve(html)).href + '?render&fmt=' + fmt;
const TIM = readFileSync(timing, 'utf8');
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const W = fmt === 'v' ? 1080 : 1920, H = fmt === 'v' ? 1920 : 1080;
async function openPage() {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.addInitScript(`window.TIMING = ${TIM}; window.FMT = '${fmt}';`);
  await page.goto(url);
  await page.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
  const bad = await page.evaluate(async () => { await Promise.all([...document.fonts].map(f => f.load().catch(() => {}))); await document.fonts.ready; return [...document.fonts].filter(f => f.status !== 'loaded').map(f => f.family); });
  if (bad.length) console.warn('WARNING fonts not loaded:', [...new Set(bad)].join(', '));
  return page;
}
const shot = async (page, t) => { await page.evaluate(t => window.seek(t), t); return page.screenshot({ type: 'jpeg', quality: 92 }); };
const p0 = await openPage();
const V = await p0.evaluate(() => ({ ...window.VIDEO, cues: window.CUES, scenes: window.SCENES.map(s => ({ kind: s.kind, t0: s.t0, t1: s.t1, at: s.at })) }));
if (a5 === '--stills' || a5 === '--every') {
  const times = a5 === '--stills' ? a6.split(',').map(Number) : Array.from({ length: Math.floor(V.duration / +a6) }, (_, i) => +(i * +a6 + 0.5).toFixed(2));
  const dir = a5 === '--every' ? out : out + '.frames'; mkdirSync(dir, { recursive: true });
  for (let i = 0; i < times.length; i++) writeFileSync(`${dir}/${String(i).padStart(3, '0')}.jpg`, await shot(p0, times[i]));
  if (a5 === '--stills') {
    const cols = Math.min(4, times.length), rows = Math.ceil(times.length / cols);
    await run(['-v', 'error', '-y', '-framerate', '1', '-i', `${dir}/%03d.jpg`, '-vf', `scale=${fmt === 'v' ? 360 : 640}:-1,tile=${cols}x${rows}:padding=6:color=gray`, '-frames:v', '1', out]);
    rmSync(dir, { recursive: true });
  }
  await browser.close(); console.log('ok', times.length, 'frames'); process.exit(0);
}
writeFileSync(out.replace(/\.mp4$/, '.cues.json'), JSON.stringify({ duration: V.duration, cues: V.cues, scenes: V.scenes }, null, 1));
await p0.close();
const fps = +a5, sub = Math.max(1, +a6), workers = Math.max(1, +a7), N = Math.round(V.duration * fps);
const base = out.replace(/\.mp4$/, '');
const vf = sub > 1 ? ['-vf', `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB)`] : [];
const t0 = Date.now(); let done = 0; const per = Math.ceil(N / workers), segs = [];
await Promise.all(Array.from({ length: workers }, async (_, w) => {
  const a = w * per, b = Math.min(N, a + per); if (a >= b) return;
  const seg = `${base}_seg${w}.mp4`; segs[w] = seg;
  const page = await openPage();
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps * sub), '-i', '-', ...vf, '-r', String(fps), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'veryfast', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const closed = new Promise(r => ff.on('close', r));
  for (let f = a; f < b; f++) {
    for (let s = 0; s < sub; s++) { const buf = await shot(page, (f + (sub > 1 ? (s / sub) * 0.5 : 0)) / fps); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
    if (++done % 150 === 0) process.stdout.write(`\r${done}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await closed; await page.close();
}));
const list = base + '_segs.txt';
writeFileSync(list, segs.filter(Boolean).map(s => `file '${path.resolve(s)}'`).join('\n'));
await run(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', out]);
segs.filter(Boolean).forEach(s => rmSync(s)); rmSync(list);
console.log(`\nvideo -> ${out} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
await browser.close();
