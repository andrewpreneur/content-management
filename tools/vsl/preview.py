#!/usr/bin/env python3
"""Quick stills of a spec at chosen output times (overlay composited on the real source frame).
python3 tools/vsl/preview.py V1 A out.jpg t1 t2 ...   (renders a contact sheet)"""
import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import vsl, specs_vsla as S
vid, var, out, *ts = sys.argv[1:]
s = S.make(vid, var); W, H = vsl.DIMS[s['aspect']]
dur = s['cut'].dur if s['cut'] else s['plan']['dur']
ts = [float(t) for t in ts] or [dur * (i + 0.5) / 12 for i in range(12)]
td = Path(tempfile.mkdtemp())
plan = dict(s['plan'], W=W, H=H, dur=dur, mode=s['mode'] if s['mode'] != 'text' else 'motion')
html = (vsl.VSL / 'overlay.html').read_text().replace('__FONTS__', 'file://' + str(vsl.ROOT / 'tools/fonts')).replace('__PLAN__', json.dumps(plan))
(td / 'p.html').write_text(html)
js = td / 'shot.js'
js.write_text("""const {chromium}=require('playwright');(async()=>{const [h,W,H,A,...ts]=process.argv.slice(2);const b=await chromium.launch();
const p=await b.newPage({viewport:{width:+W,height:+H}});const e=[];p.on('pageerror',x=>e.push(x.message));await p.goto('file://'+h);await p.evaluate(()=>document.fonts.ready);
const c=await p.context().newCDPSession(p);if(+A)await c.send('Emulation.setDefaultBackgroundColorOverride',{color:{r:0,g:0,b:0,a:0}});
for(const t of ts){await p.evaluate(t=>{window.seek(Math.max(0,t-0.5));window.seek(t)},+t);await p.screenshot({path:h.replace('p.html','o_'+t+'.png'),omitBackground:!!+A});}
await b.close();if(e.length){console.error(e.join('\\n'));process.exit(2);}})();""")
subprocess.run(['node', str(js), str(td / 'p.html'), str(W), str(H), '1' if s['mode'] == 'overlay' else '0', *map(str, ts)], check=True)
tiles = []
for t in ts:
    o = td / f'o_{t}.png'; f = td / f'f_{t}.png'
    if s['mode'] == 'overlay':
        sh = [x for x in s['shots'] if x['out'] <= t + 1e-6][-1]
        (cw, ch, cx, cy), (px, py, pw, ph) = vsl.crop_for(s['aspect'], sh['f'])
        vf = f'crop={cw}:{ch}:{cx}:{cy},scale={pw}:{ph},pad={W}:{H}:{px}:{py}:color=0x0B0F1A'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(sh['src'] + t - sh['out']), '-i', s['src'], '-frames:v', '1', '-vf', vf, str(td / 'bg.png')], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(td / 'bg.png'), '-i', str(o), '-filter_complex', 'overlay', str(f)], check=True)
    else: f = o
    tiles.append(f)
cols = 4 if W >= H else 6
lst = td / 'l.txt'; lst.write_text(''.join(f"file '{t}'\nduration 1\n" for t in tiles))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-vf', f'scale={480 if W >= H else 300}:-2,tile={cols}x{(len(tiles) + cols - 1) // cols}', '-frames:v', '1', '-q:v', '4', out], check=True)
print(out)
