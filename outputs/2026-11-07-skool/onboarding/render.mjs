// Render one video + voice to a silent MP4 (H.264 CRF 20) and dump its SFX cue list.
//   node render.mjs onb1 andrew                 -> build/onb1_andrew/silent.mp4 + cues.json
//   node render.mjs onb1 andrew --stills 3,4.5  -> build/onb1_andrew/stills.jpg (contact sheet)
//   node render.mjs onb1 andrew --sheet 1       -> one frame per second, contact sheets in build/onb1_andrew/sheet-*.jpg
// Env: FPS (30), WORKERS (4).
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const [, , id, voice, mode, arg] = process.argv;
const dir = path.join(HERE, 'build', `${id}_${voice}`);
const timing = JSON.parse(readFileSync(path.join(dir, 'timing.json'), 'utf8'));
const DATA = { id, voice, timing };
const url = pathToFileURL(path.join(HERE, 'skool.html')).href + '?render';
const run = args => new Promise((res, rej) => { const p = spawn('ffmpeg', args, { stdio: 'inherit' }); p.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()); });
const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });

async function openPage() {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  await page.addInitScript(d => { window.DATA = d; }, DATA);
  await page.goto(url);
  await page.waitForFunction(() => window.VIDEO && typeof window.seek === 'function', null, { timeout: 20000 });
  await page.evaluate(async () => { await Promise.all([...document.fonts].map(f => f.load().catch(() => {}))); await document.fonts.ready; });
  return page;
}
const shot = async (page, t, q = 92) => { await page.evaluate(t => window.seek(t), t); return page.screenshot({ type: 'jpeg', quality: q }); };

const first = await openPage();
const V = await first.evaluate(() => window.VIDEO);
writeFileSync(path.join(dir, 'cues.json'), JSON.stringify(await first.evaluate(() => window.CUES), null, 0));

if (mode === '--stills' || mode === '--sheet') {
  const times = mode === '--stills' ? arg.split(',').map(Number) : Array.from({ length: Math.floor(V.duration / (+arg || 1)) + 1 }, (_, i) => +(i * (+arg || 1)).toFixed(2));
  const fdir = path.join(dir, 'frames'); rmSync(fdir, { recursive: true, force: true }); mkdirSync(fdir, { recursive: true });
  for (let i = 0; i < times.length; i++) writeFileSync(`${fdir}/${String(i).padStart(3, '0')}.jpg`, await shot(first, times[i], 85));
  await browser.close();
  const per = mode === '--stills' ? times.length : 12, cols = Math.min(4, per);
  for (let s = 0; s * per < times.length; s++) {
    const n = Math.min(per, times.length - s * per), rows = Math.ceil(n / cols);
    await run(['-v', 'error', '-y', '-start_number', String(s * per), '-framerate', '1', '-i', `${fdir}/%03d.jpg`, '-frames:v', String(n),
      '-vf', `scale=640:-1,drawtext=text='%{eif\\:n+${s * per}\\:d}':x=8:y=8:fontsize=26:fontcolor=red:box=1,tile=${cols}x${rows}:padding=4:color=gray`,
      '-frames:v', '1', path.join(dir, mode === '--stills' ? 'stills.jpg' : `sheet-${s}.jpg`)]);
  }
  rmSync(fdir, { recursive: true });
  console.log('times', times.join(',')); process.exit(0);
}

await first.close();
const fps = +(process.env.FPS || 30), workers = +(process.env.WORKERS || 4), N = Math.round(V.duration * fps);
const per = Math.ceil(N / workers), segs = [], t0 = Date.now(); let done = 0;
await Promise.all(Array.from({ length: workers }, async (_, w) => {
  const a = w * per, b = Math.min(N, a + per); if (a >= b) return;
  const seg = path.join(dir, `seg${w}.mp4`); segs[w] = seg;
  const page = await openPage();
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-crf', '20', '-preset', 'medium', '-r', String(fps), seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const closed = new Promise(r => ff.on('close', r));
  for (let f = a; f < b; f++) {
    const buf = await shot(page, f / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (++done % 150 === 0) process.stdout.write(`\r${id}_${voice} ${done}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await closed; await page.close();
}));
const list = path.join(dir, 'segs.txt');
writeFileSync(list, segs.filter(Boolean).map(s => `file '${s}'`).join('\n'));
await run(['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', path.join(dir, 'silent.mp4')]);
segs.filter(Boolean).forEach(s => rmSync(s)); rmSync(list);
console.log(`\n${id}_${voice}: silent.mp4 ${N} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
await browser.close();
