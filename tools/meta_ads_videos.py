#!/usr/bin/env python3
"""Meta video ads, Nov 7 2026. Two kinds:
  motion  = a static template (tools/meta_ads_render.py) animated in-browser (seek(t)) + music bed + end card
  footage = real footage (Andrew VSL / customer testimonials), 4:5 crop, word-by-word captions, headline, end card
python3 tools/meta_ads_videos.py [--only V01,V02]   -> /home/user/work/ma/videos/<id>.mp4 (+ list in videos.json)
No AI faces anywhere: motion ads are UI/text only, footage ads are 100% real people.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import meta_ads_render as R
import meta_ads_batch_1107 as B

ROOT = Path(__file__).resolve().parent.parent
W = Path('/home/user/work/ma')
OUTV = W / 'videos'
FPS = 30
ENV = dict(os.environ, NODE_PATH=os.environ.get('NODE_PATH', '/opt/node-tools/node_modules'))
MUSIC = W / 'music/music-1168.mp3'

END = {
    'A': ('I sell ONE GHL feature<br>for <span class="acc">$99/month</span>', 'Watch the free breakdown →'),
    'B': ('Onboarding, training and support.<br><span class="acc">Done for you.</span>', 'Start free with SaaSSuite →'),
}

ANIM_JS = r"""
<script>
function E(x){x=Math.min(1,Math.max(0,x));return 1-Math.pow(1-x,3)}
function apply(e,ty,p){
 if(ty==='pop'){e.style.opacity=p;e.style.transform=`translateY(${(1-p)*24}px) scale(${.9+.1*p})`;e.style.transformOrigin=e.classList.contains('r')&&e.parentNode.classList.contains('th')?'right bottom':'left bottom'}
 else if(ty==='up'){e.style.opacity=p;e.style.transform=`translateY(${(1-p)*70}px)`}
 else if(ty==='fade'){e.style.opacity=p}
 else if(ty==='drop'){e.style.opacity=Math.min(1,p*2);e.style.transform=`translateY(${(1-p)*-160}px) rotate(${(e.dataset.rot||-2.5)*p + (1-p)*-9}deg)`}
 else if(ty==='strike'){e.style.textDecorationLine=p>0.5?'line-through':'none'; e.style.color=p>0.5?'':'#222'}
 else if(ty==='check'){e.classList.toggle('ok',p>0.5);e.textContent=p>0.5?'✓':''}
 else if(ty==='slam'){e.style.opacity=p>0?1:0;const s=1+(1-p)*0.6;e.style.transform=`scale(${s})`}
}
window.seek=function(t){
 for(const it of PLAN){const els=[...document.querySelectorAll(it.sel)];
  els.forEach((e,i)=>apply(e,it.ty,E((t-(it.t0+i*(it.step||0)))/(it.d||.35))));}
 const ec=document.getElementById('endcard'); if(ec){const p=E((t-ENDT)/.45);ec.style.opacity=p;ec.firstElementChild.style.transform=`translateY(${(1-p)*40}px)`}
};
</script>"""

ENDCARD_CSS = """
#endcard{position:absolute;inset:0;z-index:50;opacity:0;background:radial-gradient(90% 60% at 50% 40%,#1B2A55,#0B0F1A 75%);display:flex;align-items:center;justify-content:center;text-align:center}
#endcard>div{display:flex;flex-direction:column;align-items:center;gap:34px;padding:0 70px}
#endcard img{width:150px;height:150px;border-radius:50%;object-fit:cover;border:5px solid #FFD23F}
#endcard h2{font:900 76px/1.05 Inter;color:#fff;letter-spacing:-2px}
#endcard h2 .acc{color:#FFD23F}
#endcard .b{background:#FFD23F;color:#0B0F1A;font:800 40px Inter;padding:24px 44px;border-radius:999px}
#endcard .n{font:600 28px Inter;color:#AAB3C8}
"""


def endcard_html(kind):
    h, b = END[kind]
    who = 'Andrew George · The One Feature guy' if kind == 'A' else 'SaaSSuite · by Andrew George'
    return (f'<div id="endcard"><div><img src="file://{B.AV}"><h2>{h}</h2><div class="b">{b}</div>'
            f'<div class="n">{who}</div></div></div>')


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        print(r.stderr[-2000:]); raise SystemExit(f'failed: {cmd[:3]}')
    return r


def encode(frames_dir, ext, audio_args, out, dur):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{frames_dir}/f_%05d.{ext}'] + audio_args + [
        '-t', f'{dur:.3f}', '-c:v', 'libx264', '-crf', '21', '-maxrate', '4M', '-bufsize', '8M', '-pix_fmt', 'yuv420p',
        '-preset', 'medium', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-movflags', '+faststart', '-shortest', str(out)]
    run(cmd)


# ------------------------------------------------------------------ motion ads
MOTION = [
    # id, static spec id, plan, endcard kind, end time, duration, hook, primary/headline borrowed from static
    ('V01', 'C10a', [dict(sel='.th .m,.th .card', t0=0.3, step=1.05, ty='pop')], 'A', 7.6, 10.0, 'Text thread: vibe coding'),
    ('V02', 'C10b', [dict(sel='.th .m,.th .card', t0=0.3, step=1.3, ty='pop')], 'A', 6.2, 8.5, 'Text thread: which one?'),
    ('V03', 'C10c', [dict(sel='.th .m', t0=0.3, step=1.25, ty='pop')], 'B', 7.4, 9.8, 'Text thread: midnight support'),
    ('V04', 'C10d', [dict(sel='.th .m,.th .card', t0=0.3, step=1.1, ty='pop')], 'A', 6.6, 9.0, 'Text thread: show me'),
    ('V05', 'C08a', [dict(sel='h1', t0=0.1, ty='fade', d=.4), dict(sel='.r', t0=0.7, step=0.55, ty='up'),
                     dict(sel='.r s', t0=3.6, step=0.6, ty='strike', d=.1), dict(sel='.cb[data-ck]', t0=4.9, step=0.45, ty='check', d=.1)], 'A', 7.4, 9.6, 'Notes: cross out, check off'),
    ('V06', 'C06a', [dict(sel='h1', t0=0.1, ty='up'), dict(sel='.rc', t0=0.5, ty='up'), dict(sel='.rw', t0=1.1, step=0.75, ty='pop'),
                     dict(sel='.nt', t0=4.4, ty='fade')], 'A', 6.6, 8.8, 'Receipt: the one-feature math'),
    ('V07', 'C05a', [dict(sel='h1', t0=0.1, ty='up'), dict(sel='.a h2', t0=0.6, ty='fade'), dict(sel='.a li', t0=0.9, step=0.45, ty='pop'),
                     dict(sel='.b h2', t0=2.9, ty='fade'), dict(sel='.b li', t0=3.2, step=0.45, ty='pop')], 'A', 7.2, 9.4, 'Split: all of GHL vs one feature'),
    ('V08', 'C11d', [dict(sel='.n', t0=0.15, ty='drop', d=.6)], 'A', 4.6, 6.8, 'Sticky note drop: 3 steps'),
    ('V09', 'C16d', [dict(sel='.w', t0=0.3, ty='slam', d=.25), dict(sel='.bt div', t0=1.6, step=0.35, ty='pop')], 'A', 4.4, 6.6, 'Retro error pop-up'),
    ('V10', 'C09a', [dict(sel='.hd', t0=0.2, ty='fade'), dict(sel='.tx', t0=0.6, ty='up', d=.6), dict(sel='.mt,.st', t0=1.6, ty='fade')], 'A', 4.6, 6.8, 'Tweet card'),
    ('V11', 'C16c', [dict(sel='.k,h1', t0=0.1, step=0.25, ty='up'), dict(sel='.it', t0=1.0, step=0.9, ty='up', d=.5)], 'B', 5.6, 7.8, 'List: after the client signs'),
    ('V12', 'C07a', [dict(sel='h1', t0=0.1, ty='up'), dict(sel='.sc', t0=0.6, ty='up', d=.5), dict(sel='.it', t0=1.5, step=0.7, ty='pop')], 'B', 6.0, 8.2, 'Feature callouts on real UI'),
]


def build_motion(vid, sid, plan, ek, endt, dur, hook, H=1350):
    spec = next(s for s in B.S if s['id'] == sid)
    html = R.TEMPLATES[spec['tpl']](spec, H)
    # notes: start every row un-checked so the check-off can animate
    if spec['tpl'] == 'notes':
        html = html.replace('<span class="cb ok">✓</span>', '<span class="cb ok" data-ck></span>')
    inject = f'<style>{ENDCARD_CSS}</style>{endcard_html(ek)}<script>const PLAN={json.dumps(plan)};const ENDT={endt};</script>{ANIM_JS}'
    html = html.replace('</div></body>', '</div>' + inject + '</body>')
    tmp = Path(tempfile.mkdtemp(prefix=f'{vid}_'))
    (tmp / 'p.html').write_text(html)
    (tmp / 'f').mkdir()
    run(['node', str(ROOT / 'tools/shoot_frames.js'), str(tmp / 'p.html'), str(tmp / 'f'), '1080', str(H), str(FPS), str(dur)], env=ENV)
    out = OUTV / f'{vid}.mp4'
    ss = {'V01': 8, 'V02': 30, 'V03': 50, 'V04': 70}.get(vid, 15 + int(vid[1:]) * 5)
    audio = ['-ss', str(ss), '-i', str(MUSIC), '-filter_complex',
             f'[1:a]volume=0.55,afade=t=in:d=0.3,afade=t=out:st={dur-0.8}:d=0.8[a]', '-map', '0:v', '-map', '[a]']
    encode(tmp / 'f', 'jpg', audio, out, dur)
    shutil.rmtree(tmp)
    return dict(id=vid, kind='motion', source_static=sid, hook=hook, dur=dur, endcard=ek, file=str(out))


# ------------------------------------------------------------------ footage ads
OVERLAY_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;background:transparent;overflow:hidden;font-family:Inter}
.hl{position:absolute;top:0;left:0;right:0;padding:56px 60px 120px;background:linear-gradient(rgba(0,0,0,.78),rgba(0,0,0,.45) 65%,transparent);
 font:900 64px/1.05 Inter;color:#fff;letter-spacing:-1.5px;text-align:center}
.hl .acc{color:#FFD23F}
.tg{display:inline-block;background:#FFD23F;color:#0B0F1A;font:800 24px Inter;letter-spacing:1px;border-radius:999px;padding:8px 20px;margin-bottom:18px}
.cap{position:absolute;left:60px;right:60px;top:1010px;text-align:center}
.cap span{display:inline-block;background:rgba(0,0,0,.82);color:#fff;font:900 54px/1.15 Inter;padding:10px 22px;border-radius:14px;letter-spacing:-.5px}
.cap b{color:#FFD23F}
.foot{position:absolute;left:0;right:0;bottom:44px;text-align:center;font:700 26px Inter;color:#fff;text-shadow:0 2px 8px rgba(0,0,0,.8)}
"""

CAP_JS = r"""
<script>
function E(x){x=Math.min(1,Math.max(0,x));return 1-Math.pow(1-x,3)}
window.seek=function(t){
 let c=null; for(const ch of CH){ if(t>=ch.s-0.05 && t<ch.e+0.25) c=ch; }
 const el=document.getElementById('cap');
 if(c){ el.innerHTML='<span>'+c.w.map(w=>(t>=w.s-0.03?'<b>'+w.w+'</b>':w.w)).join(' ')+'</span>'; } else el.innerHTML='';
 document.getElementById('hl').style.opacity=E((t-0.05)/.3);
 const ec=document.getElementById('endcard'); const p=E((t-ENDT)/.4); ec.style.opacity=p; ec.firstElementChild.style.transform=`translateY(${(1-p)*40}px)`;
};
</script>"""


def words_for(tx_json, segs):
    """segs: list of (start,end) in source time; returns words re-timed onto the output timeline."""
    d = json.load(open(tx_json))
    allw = [w for s in d['segments'] for w in s.get('words', [])]
    out, off = [], 0.0
    for a, b in segs:
        for w in allw:
            if w['s'] >= a - 0.05 and w['s'] <= b - 0.15 and w['e'] <= b + 0.35:
                out.append(dict(w=w['w'].strip(), s=round(w['s'] - a + off, 3), e=round(min(w['e'], b) - a + off, 3)))
        off += b - a
    fixed = []  # Whisper spelling fixes for names/brands
    for w in out:
        if fixed and fixed[-1]['w'].lower() == 'chat' and w['w'].upper().startswith('GPT'):
            fixed[-1]['w'] = 'ChatGPT' + w['w'][3:]; fixed[-1]['e'] = w['e']; continue
        if len(fixed) >= 2 and fixed[-2]['w'].lower() == 'go' and fixed[-1]['w'].lower() == 'high' and w['w'].lower().startswith('level'):
            fixed.pop(); fixed[-1]['w'] = 'GoHighLevel' + w['w'][5:]; fixed[-1]['e'] = w['e']; continue
        w['w'] = {'sassweet.ai': 'SaaSSuite.ai', 'GHL': 'GHL'}.get(w['w'], w['w'])
        fixed.append(w)
    return fixed


def chunk(words, n=4):
    ch, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= n or re.search(r'[.,?!]$', w['w']):
            ch.append(cur); cur = []
    if cur:
        ch.append(cur)
    return [dict(s=c[0]['s'], e=c[-1]['e'], w=[dict(w=x['w'], s=x['s']) for x in c]) for c in ch]


FOOTAGE = [
    # id, source, transcript, segments, crop (ffmpeg crop on source), headline, tag, endcard, hook
    ('V13', W / 'vsl/v1.mp4', W / 'vsl/tx_v1/transcript.json', [(0.0, 5.3), (35.74, 41.75)], 'crop=1728:2160:1016:0',
     'I sell <span class="acc">ONE</span> GHL feature for $99/month', '', 'A', 'Andrew VSL: greatest advancement + sell one feature'),
    ('V14', W / 'vsl/v1.mp4', W / 'vsl/tx_v1/transcript.json', [(5.3, 15.5)], 'crop=1728:2160:1016:0',
     'Not AI emails. Not AI agents. <span class="acc">Something simpler.</span>', '', 'A', 'Andrew VSL: not emails, not agents'),
    ('V15', W / 'vsl/v1.mp4', W / 'vsl/tx_v1/transcript.json', [(15.54, 20.84), (35.74, 41.75)], 'crop=1728:2160:1016:0',
     'Kept this <span class="acc">behind closed doors</span> for 6 weeks', '', 'A', 'Andrew VSL: behind closed doors'),
    ('V16', W / 'testi/rob.mp4', W / 'testi/tx_rob/transcript.json', [(11.3, 24.1)], 'ROB',
     '<span class="acc">Real humans</span> answer your clients\' questions', 'SAASSUITE CUSTOMER', 'B', 'Rob testimonial: real humans on support'),
    ('V17', W / 'testi/brentney.mp4', W / 'testi/tx_brentney/transcript.json', [(12.5, 18.2), (21.8, 27.6)], 'crop=1080:1350:0:120',
     '“Now I can <span class="acc">scale</span>.”', 'SAASSUITE CUSTOMER', 'B', 'Brentney testimonial: support was slowing growth'),
    ('V18', W / 'testi/ben.mp4', W / 'testi/tx_ben/transcript.json', [(0.0, 11.9)], 'crop=1080:1350:0:200',
     'Agency owner: “super helpful with <span class="acc">everything</span>”', 'REAL CUSTOMER', 'B', 'Ben testimonial: agency builds HighLevel with Andrew'),
]


def src_info(p):
    r = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(p)])
    w, h = r.stdout.strip().split(',')[:2]
    return int(w), int(h)


def build_footage(vid, src, tx, segs, crop, head, tag, ek, hook):
    tmp = Path(tempfile.mkdtemp(prefix=f'{vid}_'))
    sw, sh = src_info(src)
    if crop == 'ROB':  # zoom call 16:9: Rob is on the left half
        cw = int(sh * 0.8); crop = f'crop={cw}:{sh}:{int(sw*0.16)}:0'
    vparts, aparts = [], []
    for i, (a, b) in enumerate(segs):
        part = tmp / f'p{i}.mp4'
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-i', str(src), '-t', f'{b-a:.3f}', '-vf', f'{crop},scale=1080:1350,fps={FPS},format=yuv420p',
             '-af', 'aresample=48000', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-c:a', 'aac', '-b:a', '192k', str(part)])
        vparts.append(part)
    body = sum(b - a for a, b in segs)
    endlen = 2.2
    dur = body + endlen
    # concat + freeze-free end: pad video by cloning last frame, pad audio with silence
    lst = tmp / 'l.txt'; lst.write_text(''.join(f"file '{p}'\n" for p in vparts))
    base = tmp / 'base.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-vf', f'tpad=stop_mode=clone:stop_duration={endlen}',
         '-af', f'apad=pad_dur={endlen},loudnorm=I=-16:TP=-1.5:LRA=11', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-c:a', 'aac', '-b:a', '192k', str(base)])
    words = words_for(tx, segs)
    ch = chunk(words)
    tg = f'<div class="tg">{tag}</div><br>' if tag else ''
    html = (f'<!doctype html><html><head><meta charset="utf-8">{R.FONTS}<style>{OVERLAY_CSS}{ENDCARD_CSS}</style></head><body>'
            f'<div class="hl" id="hl">{tg}{head}</div><div class="cap" id="cap"></div>'
            f'<div class="foot">{"Andrew George · The One Feature guy" if ek == "A" else "Real customer, real words"}</div>'
            f'{endcard_html(ek)}<script>const CH={json.dumps(ch)};const ENDT={body:.3f};</script>{CAP_JS}</body></html>')
    (tmp / 'o.html').write_text(html)
    (tmp / 'f').mkdir()
    run(['node', str(ROOT / 'tools/shoot_frames.js'), str(tmp / 'o.html'), str(tmp / 'f'), '1080', '1350', str(FPS), f'{dur:.3f}', '1'], env=ENV)
    out = OUTV / f'{vid}.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(base), '-framerate', str(FPS), '-i', str(tmp / 'f/f_%05d.png'),
         '-filter_complex', '[0:v][1:v]overlay=0:0:eof_action=pass[v]', '-map', '[v]', '-map', '0:a', '-t', f'{dur:.3f}',
         '-c:v', 'libx264', '-crf', '21', '-maxrate', '4M', '-bufsize', '8M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
         '-movflags', '+faststart', str(out)])
    shutil.rmtree(tmp)
    return dict(id=vid, kind='footage', source=src.name, segments=segs, hook=hook, dur=round(dur, 2), endcard=ek, file=str(out),
                headline_overlay=re.sub('<[^>]+>', '', head), transcript=' '.join(w['w'] for w in words))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only', default='')
    a = ap.parse_args(); only = set(a.only.split(',')) if a.only else None
    OUTV.mkdir(parents=True, exist_ok=True)
    meta_p = OUTV / 'videos.json'
    meta = json.load(open(meta_p)) if meta_p.exists() else {}
    for m in MOTION:
        if only and m[0] not in only: continue
        print('motion', m[0], flush=True); meta[m[0]] = build_motion(*m)
    for f in FOOTAGE:
        if only and f[0] not in only: continue
        print('footage', f[0], flush=True); meta[f[0]] = build_footage(*f)
    json.dump(meta, open(meta_p, 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
