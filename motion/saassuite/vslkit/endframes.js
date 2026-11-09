// node endframes.js overlay.html 169|916 OUT_DIR FROM_S : re-shoot only frames from FROM_S to the end
const { chromium } = require('playwright'); const path = require('path');
(async () => { const [html, v, out, from] = process.argv.slice(2); const W = v === '169' ? 1920 : 1080, H = v === '169' ? 1080 : 1920;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto('file://' + path.resolve(html) + '?v=' + v); await p.evaluate(() => document.fonts.ready);
  const N = Math.ceil(await p.evaluate(() => window.DURATION) * 30);
  for (let i = Math.floor(+from * 30); i < N; i++) { await p.evaluate(t => window.render(t), i / 30); await p.screenshot({ path: `${out}/${String(i).padStart(5, '0')}.png`, omitBackground: true }); }
  await b.close(); })();
