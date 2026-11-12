// node shoot.js <overlay.html> <169|916> <out.mov | stills-dir> [t1,t2,... for stills]
// Renders the transparent overlay frame by frame (window.render(t), 30 fps) and pipes PNGs into ffmpeg (PNG-in-MOV keeps alpha).
// Also writes <out>.cues.json (SFX cue list from the page).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
(async () => {
  const [html, v, out, stills] = process.argv.slice(2); const W = v === '169' ? 1920 : 1080, H = { '169': 1080, '916': 1920, '45': 1350, '34': 1440 }[v];
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto('file://' + path.resolve(html) + '?v=' + v + (process.env.END ? '&end=' + process.env.END : '')); await p.evaluate(() => document.fonts.ready);
  const dur = await p.evaluate(() => window.DUR);
  if (stills) {
    fs.mkdirSync(out, { recursive: true });
    for (const t of stills.split(',').map(Number)) { await p.evaluate(t => render(t), t); await p.screenshot({ path: `${out}/${v}-${t.toFixed(2)}.png`, omitBackground: true }); }
  } else {
    fs.writeFileSync(out + '.cues.json', JSON.stringify(await p.evaluate(() => window.CUES)));
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', '-c:v', 'png', '-pix_fmt', 'rgba', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(dur * 30);
    for (let i = 0; i < N; i++) { await p.evaluate(t => render(t), i / 30); const buf = await p.screenshot({ omitBackground: true }); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); if (i % 300 === 0) console.log(v, i, '/', N); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();
