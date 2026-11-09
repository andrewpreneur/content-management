// node stills.js overlay.html 169|916 OUT.png t1,t2,...  -> one tiled check image over a base frame grabbed separately (transparent tiles)
const { chromium } = require('playwright'); const path = require('path');
(async () => { const [html, v, out, ts] = process.argv.slice(2); const W = v === '169' ? 1920 : 1080, H = v === '169' ? 1080 : 1920;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto('file://' + path.resolve(html) + '?v=' + v); await p.evaluate(() => document.fonts.ready);
  for (const t of ts.split(',')) { await p.evaluate(t => window.render(t), +t); await p.screenshot({ path: out.replace('.png', `_${t}.png`), omitBackground: true }); }
  await b.close(); })();
