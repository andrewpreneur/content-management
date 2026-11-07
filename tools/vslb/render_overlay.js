// Render the VSL overlay page frame by frame (transparent PNG) and pipe it into ffmpeg.
// node tools/vslb/render_overlay.js page.html data.json ffargs.json
// ffargs.json = full ffmpeg argv (without "ffmpeg"); the overlay PNG stream is "-f image2pipe -framerate FPS -i -" and
// must appear in it as the literal string "__PIPE__" (it is replaced by those args).
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs'); const path = require('path');
(async () => {
  const [html, dataPath, argsPath] = process.argv.slice(2);
  const D = JSON.parse(fs.readFileSync(dataPath, 'utf8')); const FPS = D.FPS || 30;
  const args = JSON.parse(fs.readFileSync(argsPath, 'utf8'));
  const i = args.indexOf('__PIPE__'); args.splice(i, 1, '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: D.W, height: D.H } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(d => { window.DATA = d; }, D);
  await p.goto('file://' + path.resolve(html)); await p.evaluate(() => document.fonts.ready);
  const cdp = await p.context().newCDPSession(p);
  await cdp.send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', ...args]); ff.stderr.on('data', d => process.stderr.write(d));
  let code = null; const closed = new Promise(r => ff.on('close', c => { code = c; r(); })); ff.stdin.on('error', () => { });
  const N = Math.round(D.T * FPS);
  for (let f = 0; f < N && code === null; f++) {
    await p.evaluate(t => seek(t), f / FPS);
    const r = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true, captureBeyondViewport: false });
    if (!ff.stdin.write(Buffer.from(r.data, 'base64'))) await Promise.race([new Promise(r => ff.stdin.once('drain', r)), closed]);
    if (f % 300 === 0) process.stderr.write(`  frame ${f}/${N}\n`);
  }
  ff.stdin.end(); await closed; await b.close();
  if (code !== 0) { console.error('ffmpeg failed', code); process.exit(1); }
  if (errs.length) { console.error('page errors:\n' + errs.join('\n')); process.exit(1); }
  console.log('overlay rendered', N, 'frames');
})().catch(e => { console.error(e); process.exit(1); });
