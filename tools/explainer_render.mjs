// explainer_render.mjs: turn a seek(t) page (the explainer skills' page.html) into an MP4 with motion blur and its own audio.
// Based on the render script in the explainer skills; adds splitting one render across many machines (Supercomputers).
//   node explainer_render.mjs page.html out.mp4 [fps=60] [subframes=4] [workers=cores]        whole video on this machine
//   node explainer_render.mjs page.html sheet.png --stills 0.5,1.2,3                          contact sheet for checking
//   node explainer_render.mjs page.html part.mp4 [fps] [subframes] [workers] --slice I/N       only slice I of N (silent), for machine I
//   node explainer_render.mjs page.html out.mp4 --join partsDir [fps]                         join the slices (in order) + add the audio
// page.html may be a local path or an https URL. Optional: window.buildAudio(ctx) schedules the soundtrack.
import { createRequire } from 'node:module';
// Playwright installed next to the kit (explainer_setup.sh), else one the machine already has (NODE_PATH / global)
let chromium;
try { ({ chromium } = await import('playwright')); } catch { ({ chromium } = createRequire(import.meta.url)('playwright')); }
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync, readdirSync, existsSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const flag = (n) => { const i = argv.indexOf(n); if (i < 0) return null; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const slice = flag('--slice'), joinDir = flag('--join');
const [html, out, a3 = '60', a4 = '4', a5 = String(Math.max(1, os.cpus().length))] = argv;
if (!html || !out) { console.log('usage: node render.mjs page.html out.mp4 [fps] [subframes] [workers]'); process.exit(1); }
const run = (args) => new Promise((res, rej) => { const p = spawn('ffmpeg', args, { stdio: 'inherit' }); p.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()); });
if (out) mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
const url = /^https?:\/\//.test(html) ? html + (html.includes('?') ? '&' : '?') + 'render' : pathToFileURL(path.resolve(html)).href + '?render';
const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'], ...(proxy ? { proxy: { server: proxy } } : {}) });

// Read the size first, then open every page at exactly that size (pages that measure themselves on load stay correct).
const probe = await browser.newPage();
await probe.goto(url);
await probe.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
const V = await probe.evaluate(() => window.VIDEO);
await probe.close();

async function openPage() {
  const page = await browser.newPage({ viewport: { width: V.w, height: V.h }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.waitForFunction(() => window.VIDEO && typeof window.seek === 'function');
  // load every declared font, even ones only used by scenes hidden at t=0
  const bad = await page.evaluate(async () => {
    await Promise.all([...document.fonts].map(f => f.load().catch(() => {})));
    await document.fonts.ready;
    return [...document.fonts].filter(f => f.status !== 'loaded').map(f => f.family);
  });
  if (bad.length) console.warn('WARNING: fonts did not load (fallback in use):', [...new Set(bad)].join(', '), '- embed them as base64.');
  return page;
}
const shot = async (page, t) => { await page.evaluate(t => window.seek(t), t); return page.screenshot({ type: 'jpeg', quality: 95 }); };

if (a3 === '--stills') {
  const page = await openPage();
  const times = a4.split(',').map(Number), dir = out + '.frames';
  mkdirSync(dir, { recursive: true });
  for (let i = 0; i < times.length; i++) writeFileSync(`${dir}/${String(i).padStart(3, '0')}.jpg`, await shot(page, times[i]));
  await browser.close();
  const cols = Math.min(3, times.length), rows = Math.ceil(times.length / cols);
  await run(['-v', 'error', '-y', '-framerate', '1', '-i', `${dir}/%03d.jpg`, '-vf', `scale=${Math.min(960, V.w)}:-1,tile=${cols}x${rows}:padding=6:color=gray`, '-frames:v', '1', out]);
  rmSync(dir, { recursive: true });
  console.log('stills ->', out); process.exit(0);
}

async function addAudio(silent, out) {
  const page = await openPage();
  const hasAudio = await page.evaluate(() => typeof window.buildAudio === 'function');
  if (!hasAudio) { await run(['-v', 'error', '-y', '-i', silent, '-c', 'copy', '-movflags', '+faststart', out]); return; }
  const b64 = await page.evaluate(async (dur) => {
    const sr = 48000, ctx = new OfflineAudioContext(2, Math.ceil(sr * dur), sr);
    await window.buildAudio(ctx);
    const b = await ctx.startRendering(), L = b.getChannelData(0), R = b.getChannelData(b.numberOfChannels > 1 ? 1 : 0);
    const i16 = new Int16Array(L.length * 2);
    for (let i = 0; i < L.length; i++) { i16[2 * i] = Math.max(-1, Math.min(1, L[i])) * 32767; i16[2 * i + 1] = Math.max(-1, Math.min(1, R[i])) * 32767; }
    const u8 = new Uint8Array(i16.buffer); let s = '';
    for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    return btoa(s);
  }, V.duration);
  const pcm = out.replace(/\.mp4$/, '') + '.pcm'; writeFileSync(pcm, Buffer.from(b64, 'base64'));
  await run(['-v', 'error', '-y', '-i', silent, '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', pcm,
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out]);
  rmSync(pcm);
}

if (joinDir) {
  // parts are named part_<I>.mp4 (any folder layout under joinDir); join them in order without re-encoding, then add the sound once
  const found = [];
  const walk = (d) => { for (const f of readdirSync(d, { withFileTypes: true })) { const p = path.join(d, f.name); if (f.isDirectory()) walk(p); else if (/^part_\d+\.mp4$/.test(f.name)) found.push(p); } };
  for (const d of joinDir.split(',')) if (existsSync(d)) walk(d);
  const byIndex = new Map(found.map((p) => [Number(path.basename(p).match(/\d+/)[0]), p]));
  const parts = [...byIndex.keys()].sort((a, b) => a - b).map((k) => byIndex.get(k));
  if (!parts.length) { console.error('no part_<I>.mp4 files found in', joinDir); process.exit(1); }
  const list = out.replace(/\.mp4$/, '') + '_parts.txt', silent = out.replace(/\.mp4$/, '') + '_silent.mp4';
  writeFileSync(list, parts.map((p) => `file '${path.resolve(p)}'`).join('\n'));
  await run(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', silent]);
  rmSync(list);
  await addAudio(silent, out);
  const err = await new Promise((res) => { let e = ''; const p = spawn('ffmpeg', ['-v', 'error', '-i', out, '-f', 'null', '-']); p.stderr.on('data', (d) => (e += d)); p.on('close', () => res(e.trim())); });
  if (err) { console.error('decode check failed:', err.slice(0, 400)); process.exit(1); }
  console.log(`joined ${parts.length} parts -> ${out}`);
  await browser.close(); process.exit(0);
}

const fps = +a3, sub = Math.max(1, +a4), workers = Math.max(1, +a5), N = Math.round(V.duration * fps);
const base = out.replace(/\.mp4$/, ''), silent = base + '_silent.mp4';
const vf = sub > 1 ? ['-vf', `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB)`] : [];
const t0 = Date.now(); let doneFrames = 0;
let F0 = 0, F1 = N;
if (slice) { const [I, n] = slice.split('/').map(Number); const per0 = Math.ceil(N / n); F0 = Math.min(N, I * per0); F1 = Math.min(N, F0 + per0); }
const per = Math.ceil((F1 - F0) / workers), segs = [];
const progress = process.env.PROGRESS_FILE;
await Promise.all(Array.from({ length: workers }, async (_, w) => {
  const a = F0 + w * per, b = Math.min(F1, a + per); if (a >= b) return;
  const seg = `${base}_seg${w}.mp4`; segs[w] = seg;
  const page = await openPage();
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps * sub), '-i', '-', ...vf,
    '-r', String(fps), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'medium', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const closed = new Promise(r => ff.on('close', r));
  for (let f = a; f < b; f++) {
    for (let s = 0; s < sub; s++) {             // 180-degree shutter: sub-frames spread over half a frame
      const buf = await shot(page, (f + (sub > 1 ? (s / sub) * 0.5 : 0)) / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    if (++doneFrames % 30 === 0) { process.stdout.write(`\r${doneFrames}/${F1 - F0} frames  ${((Date.now() - t0) / 1000).toFixed(0)}s`); if (progress) writeFileSync(progress, `${Math.round(100 * doneFrames / (F1 - F0))}% Rendering frames\n`); }
  }
  ff.stdin.end(); await closed; await page.close();
}));
const list = base + '_segs.txt';
writeFileSync(list, segs.filter(Boolean).map(s => `file '${path.resolve(s)}'`).join('\n'));
await run(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', silent]);
segs.filter(Boolean).forEach(s => rmSync(s)); rmSync(list);
console.log(`\nvideo -> ${silent}  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
if (slice) { const { renameSync } = await import('node:fs'); renameSync(silent, out); console.log('slice ->', out); await browser.close(); process.exit(0); }

await addAudio(silent, out);
console.log('with audio ->', out);
await browser.close();
