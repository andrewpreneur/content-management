// node shoot.js overlay.html 169|916 OUT_DIR [workers=3]  -> transparent PNG frames + OUT_DIR/../cues.json + duration
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [html, v, out, wk = '3'] = process.argv.slice(2); const W = v === '169' ? 1920 : 1080, H = v === '169' ? 1080 : 1920;
  fs.mkdirSync(out, { recursive: true }); const b = await chromium.launch(); const url = 'file://' + path.resolve(html) + '?v=' + v;
  const open = async () => { const p = await b.newPage({ viewport: { width: W, height: H } }); await p.goto(url); await p.evaluate(() => document.fonts.ready); return p; };
  const p0 = await open(); const dur = await p0.evaluate(() => window.DURATION); const cues = await p0.evaluate(() => getCues());
  fs.writeFileSync(path.join(out, '..', 'cues.json'), JSON.stringify(cues)); fs.writeFileSync(path.join(out, '..', 'duration.txt'), String(dur));
  const N = Math.ceil(dur * 30), K = +wk; const pages = [p0]; for (let k = 1; k < K; k++) pages.push(await open());
  await Promise.all(pages.map(async (p, k) => { for (let i = k; i < N; i += K) { await p.evaluate(t => window.render(t), i / 30); await p.screenshot({ path: `${out}/${String(i).padStart(5, '0')}.png`, omitBackground: true }); } }));
  await b.close(); console.log('frames', N, 'dur', dur);
})();
