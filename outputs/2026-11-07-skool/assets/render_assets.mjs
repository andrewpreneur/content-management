// Render every asset in assets.js to PNG master + JPG (<= 400 KB).  node render_assets.mjs [id ...]
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { mkdirSync, statSync, rmSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
const { chromium } = createRequire(import.meta.url)('playwright');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const url = pathToFileURL(path.join(HERE, 'assets.html')).href;
const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const probe = await b.newPage(); await probe.goto(url);
const all = await probe.evaluate(() => Object.fromEntries(Object.entries(window.ASSETS).map(([k, v]) => [k, { w: v.w, h: v.h, scale: v.scale || 1 }])));
await probe.close();
const ids = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(all);
mkdirSync(path.join(HERE, 'png'), { recursive: true }); mkdirSync(path.join(HERE, 'jpg'), { recursive: true });
for (const id of ids) {
  const a = all[id];
  const p = await b.newPage({ viewport: { width: a.w, height: a.h }, deviceScaleFactor: a.scale });
  p.on('pageerror', e => console.error(id, 'PAGE ERROR', e.message));
  await p.goto(url + '?a=' + id);
  await p.evaluate(async () => { await Promise.all([...document.fonts].map(f => f.load().catch(() => {}))); await document.fonts.ready; });
  const png = path.join(HERE, 'png', id + '.png'), jpg = path.join(HERE, 'jpg', id + '.jpg');
  await p.screenshot({ path: png, clip: { x: 0, y: 0, width: a.w, height: a.h } });
  for (const q of [3, 4, 5, 6, 8]) {   // ffmpeg mjpeg q (2 best): first that fits 400 KB
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', png, '-q:v', String(q), jpg]);
    if (statSync(jpg).size <= 400 * 1024) break;
  }
  const ps = statSync(png).size;
  if (ps > 1024 * 1024) rmSync(png);   // keep PNG masters only when small
  console.log(id, `${a.w * a.scale}x${a.h * a.scale}`, 'jpg', Math.round(statSync(jpg).size / 1024) + 'KB', ps > 1024 * 1024 ? 'png dropped (' + Math.round(ps / 1024) + 'KB)' : 'png ' + Math.round(ps / 1024) + 'KB');
  await p.close();
}
await b.close();
