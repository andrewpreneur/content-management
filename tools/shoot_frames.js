// Render an HTML animation frame by frame: node tools/shoot_frames.js page.html outdir W H fps dur [transparent]
// The page must define window.seek(t). Frames -> outdir/f_00001.(jpg|png). NODE_PATH=/opt/node-tools/node_modules
const {chromium} = require('playwright');
(async () => {
  const [html, out, w, h, fps, dur, transp] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: +w, height: +h}});
  await p.goto('file://' + html, {waitUntil: 'networkidle'});
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(200);
  const n = Math.round(+fps * +dur);
  const png = transp === '1';
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.seek(t), i / +fps);
    const f = `${out}/f_${String(i + 1).padStart(5, '0')}.${png ? 'png' : 'jpg'}`;
    await p.screenshot(png ? {path: f, omitBackground: true} : {path: f, type: 'jpeg', quality: 92});
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
