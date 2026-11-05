#!/usr/bin/env python3
"""Carousel formats modelled on Andrew's competitor references (research/carousels/README.md): one video → many carousels.

Formats (1080×1350 slides):
  convo      Hormozi podcast stack: two video frames stacked, a caption on each (yellow top, white bottom)
  tweet      Hormozi/Martell quote card: black, avatar + name + handle, big plain text (**bold** allowed). No fake verified badge.
  notes      Josh Snow notes card: white, small avatar row, plain step-by-step text
  lesson     GaryVee "LESSON #1": video still on top, white panel with yellow label, bold title, quote, footer
  sticker    Mila Markson story: photo with white rounded sticker lines + "Here's what … 👉"
  headline   Josh Snow news cover: photo, condensed caps headline over a dark fade
  bigword    Dan Martell event recap: photo, huge word ("DAY 1"), small subline, SWIPE →
Usage:
  python3 tools/carousel_formats.py render SPEC.json OUT_DIR        # explicit slides
  python3 tools/carousel_formats.py clip BANK.json CLIP_ID OUT_DIR  # convo + tweet + sticker + headline from one clip
  python3 tools/carousel_formats.py lessons BANK.json OUT_DIR       # "N lessons from <guest>" from a whole podcast
  python3 tools/carousel_formats.py event VIDEO.mp4 OUT_DIR --word "LEVEL UP" --sub "..."   # photo-dump recap from an event video
"""
import argparse, html, json, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent; FONTS = ROOT / 'tools/fonts'
PROFILE = dict(name='Andrew George', handle='@andrewpreneurship', avatar=str(ROOT / 'research/carousels/avatar_andrew.jpg'))
W, H = 1080, 1350
CSS = f"""
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-Regular.woff');font-weight:400}}
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-SemiBold.woff');font-weight:600}}
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-Bold.woff');font-weight:700}}
@font-face{{font-family:Tight;src:url('file://{FONTS}/InterTight-ExtraBold.ttf');font-weight:800}}
@font-face{{font-family:Oswald;src:url('file://{FONTS}/Oswald-SemiBold.woff');font-weight:600}}
*{{box-sizing:border-box;margin:0}} body{{width:{W}px;height:{H}px;overflow:hidden;font-family:Inter,sans-serif}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:center}}
"""


def esc(s):
    return html.escape(s or '').replace('\n', '<br>')


def rich(s):
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', esc(s))


def img_url(p):
    return 'file://' + str(Path(p).resolve())


def slide_html(fmt, s, prof):
    av = f"<img src='{img_url(prof['avatar'])}' style='width:{s.get('av', 128)}px;height:{s.get('av', 128)}px;border-radius:50%;object-fit:cover'>"
    if fmt == 'convo':
        cap = lambda t, c: f"<div style='position:absolute;left:60px;right:60px;bottom:46px;text-align:center;font:700 54px/1.12 Inter;color:{c};-webkit-text-stroke:3px #000;paint-order:stroke fill;text-shadow:0 3px 10px rgba(0,0,0,.6)'>{esc(t)}</div>"
        return (f"<div style='position:absolute;left:0;top:0;width:{W}px;height:675px;background:url({img_url(s['top_img'])}) center/cover'>{cap(s.get('top_text', ''), '#FFE14D')}</div>"
                f"<div style='position:absolute;left:0;top:675px;width:{W}px;height:675px;background:url({img_url(s['bot_img'])}) center/cover'>{cap(s.get('bot_text', ''), '#FFFFFF')}</div>")
    if fmt == 'tweet':
        big = s.get('size', 64 if len(s['text']) < 230 else 50)
        return (f"<div class='bg' style='background:#000'></div><div style='position:absolute;left:84px;right:84px;top:50%;transform:translateY(-50%);color:#fff'>"
                f"<div style='display:flex;gap:26px;align-items:center;margin-bottom:44px'>{av}<div><div style='font:700 52px Inter'>{esc(prof['name'])}</div>"
                f"<div style='font:400 40px Inter;color:#8B98A5'>{esc(prof['handle'])}</div></div></div>"
                f"<div style='font:400 {big}px/1.22 Inter;letter-spacing:-.01em'>{rich(s['text'])}</div></div>")
    if fmt == 'notes':
        return (f"<div class='bg' style='background:#fff'></div><div style='position:absolute;left:96px;right:96px;top:150px;color:#1F2328'>"
                f"<div style='display:flex;gap:20px;align-items:center;margin-bottom:56px'>{av.replace('128px', '92px')}<div><div style='font:700 36px Inter'>{esc(prof['name'])}</div>"
                f"<div style='font:400 30px Inter;color:#6B7280'>{esc(prof['handle'])}</div></div></div>"
                f"<div style='font:400 44px/1.5 Inter'>{rich(s['text']).replace('<br><br>', '</div><div style=\"height:40px\"></div><div>')}</div></div>")
    if fmt == 'lesson':
        return (f"<div style='position:absolute;left:0;top:0;width:{W}px;height:760px;background:url({img_url(s['img'])}) center/cover'></div>"
                f"<div style='position:absolute;left:0;top:760px;width:{W}px;height:590px;background:#fff;text-align:center;padding:56px 80px 0'>"
                f"<span style='display:inline-block;background:#FFD400;color:#111;font:600 64px Oswald;letter-spacing:.02em;padding:4px 26px'>{esc(s['label'])}</span>"
                f"<div style='font:800 {76 if len(s['title']) <= 32 else 62}px/1.08 Tight;color:#111;margin-top:30px;letter-spacing:-.01em'>{esc(s['title'])}</div>"
                f"<div style='font:400 32px/1.35 Inter;color:#333;margin-top:22px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden'>“{esc(s['quote'])}”</div>"
                f"<div style='position:absolute;left:0;right:0;bottom:52px;font:700 34px Inter;color:#111'>{esc(s.get('footer', ''))}</div></div>")
    if fmt == 'sticker':
        lines = ''.join(f"<div style='display:inline-block;background:#fff;color:#111;font:700 52px/1.18 Inter;padding:12px 26px;border-radius:18px;margin:6px 0;max-width:900px'>{esc(l)}</div><br>" for l in s['lines'])
        cta = f"<div style='display:inline-block;background:#fff;color:#111;font:700 46px Inter;padding:10px 24px;border-radius:16px;margin-top:22px'>{esc(s['cta'])}</div>" if s.get('cta') else ''
        return (f"<div class='bg' style='background-image:url({img_url(s['img'])})'></div>"
                f"<div style='position:absolute;left:0;right:0;top:{s.get('y', 640)}px;text-align:center'>{lines}{cta}</div>")
    if fmt == 'headline':
        return (f"<div class='bg' style='background-image:url({img_url(s['img'])})'></div><div class='bg' style='background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.82) 88%)'></div>"
                f"<div style='position:absolute;left:60px;right:60px;bottom:110px;text-align:center;font:600 {s.get('size', 104)}px/1.06 Oswald;color:#fff;text-transform:uppercase;text-shadow:0 4px 18px rgba(0,0,0,.6)'>{esc(s['text'])}</div>")
    if fmt == 'bigword':
        sw = "<div style='position:absolute;right:60px;bottom:52px;font:600 26px Inter;letter-spacing:.2em;color:#fff'>SWIPE →</div>" if s.get('swipe') else ''
        return (f"<div class='bg' style='background-image:url({img_url(s['img'])})'></div><div class='bg' style='background:linear-gradient(180deg,rgba(0,0,0,0) 45%,rgba(0,0,0,.75) 85%)'></div>"
                f"<div style='position:absolute;left:40px;right:40px;bottom:170px;text-align:center;color:#fff'><div style='font:800 {s.get('size', 210)}px/1 Tight;letter-spacing:-.02em;text-shadow:0 6px 24px rgba(0,0,0,.5)'>{esc(s['word'])}</div>"
                f"<div style='font:600 44px/1.3 Inter;margin-top:14px'>{esc(s.get('sub', ''))}</div></div>{sw}")
    if fmt == 'photo':
        return f"<div class='bg' style='background-image:url({img_url(s['img'])})'></div>"
    raise SystemExit('unknown format ' + fmt)


def render(spec, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); prof = {**PROFILE, **spec.get('profile', {})}
    hd = out / '_html'; hd.mkdir(exist_ok=True); pairs, files = [], []
    for i, s in enumerate(spec['slides']):
        fmt = s.get('format', spec['format'])
        h = hd / f'slide-{i + 1:02d}.html'; h.write_text(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{slide_html(fmt, s, prof)}</body></html>")
        f = out / f'slide-{i + 1:02d}.png'; pairs.append(f'{h}:{f}'); files.append(str(f))
    subprocess.run(['node', str(ROOT / 'tools/shoot.js'), str(W), str(H), *pairs], check=True, env={**__import__('os').environ, 'NODE_PATH': '/opt/node-tools/node_modules'})
    (out / 'carousel.json').write_text(json.dumps(spec, indent=1, ensure_ascii=False)); return files


# ---------- building carousels from a podcast clip ----------
def frame(src, t, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', src, '-frames:v', '1', '-q:v', '2', out], check=True); return out


def crop(img, person, ratio, out, mult=5.0, top=0.36):
    im = Image.open(img); IW, IH = im.size; f = person['face']; cw = min(IW, mult * f); ch = cw * ratio
    if ch > IH: ch = IH; cw = ch / ratio
    cx = min(max(person['x'], cw / 2), IW - cw / 2); cy = min(max(person['y'] + (0.5 - top) * ch, ch / 2), IH - ch / 2)
    im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, int(W * ratio)), Image.LANCZOS).save(out, quality=92); return out


def sentences(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.!?]$', w[0]): out.append(cur); cur = []
    if cur: out.append(cur)
    res = []
    for s in out:  # split long sentences at a natural break so each slide reads as one line
        parts, cur = [], []
        for k, w in enumerate(s):
            cur.append(w); nxt = s[k + 1][0].lower() if k + 1 < len(s) else ''
            if len(cur) >= 8 and w[0].endswith(',') and nxt in ('but', 'and', 'so', 'because', 'if', 'then') and len(s) - k > 5: parts.append(cur); cur = []
        if cur: parts.append(cur)
        for pp in parts:
            t = ' '.join(x[0] for x in pp).replace(' -', '-').rstrip(',')
            res.append(dict(text=t[0].upper() + t[1:] + ('' if re.search(r'[.!?]$', t) else '.'), s=pp[0][1], e=pp[-1][2]))
    return res


def speaker_at(segs, t):
    for a, b, l in segs:
        if a <= t < b: return l
    return segs[-1][2]


def from_clip(bank, cid, out):
    S = json.loads(Path(bank).read_text()); c = next(x for x in S['clips'] if x['id'] == cid); work = Path(S['work']); src = c.get('src', S['source'])
    words = json.loads((work / f'{cid}.words.json').read_text()); spk_p = Path('/home/user/work/formats') / cid / 'speakers.json'
    if not spk_p.exists():
        spk_p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['/home/user/work/dfenv/bin/python', str(ROOT / 'tools/speakers.py'), src, str(spk_p), '--start', str(c['t0']), '--dur', str(c['dur']),
                        '--words', str(work / f'{cid}.words.json')], check=True, capture_output=True)
    spk = json.loads(spk_p.read_text()); P = {p['id']: p for p in spk['people']}; segs = spk['segments']
    DEP = {'and', 'but', 'so', 'because', 'which', 'that', "that's", 'it', "it's", 'they', 'this', 'yeah', 'yes', 'um', 'uh', 'like', 'right', 'okay', 'oh', 'well', 'or', 'then', 'also'}
    FILL = re.compile(r"\b(you know|i mean|kind of|sort of|in my mind's eye|like,)\b", re.I)
    def good(x): w = x['text'].split(); return 5 <= len(w) <= 24 and re.sub(r'[^a-z\']', '', w[0].lower()) not in DEP and not FILL.search(x['text'])
    allS = sentences(words); sents = [x for x in allS if good(x)]
    if len(sents) < 4: sents = [x for x in allS if 4 <= len(x['text'].split()) <= 26] or allS
    who = c.get('speaker', ''); attrib = '' if who.startswith('Andrew') and '+' not in who and '→' not in who else f"\n\n— {who.split(' →')[-1].split(' +')[0].strip()}"
    if '→' in who: attrib = f"\n\n— {who.split('→')[-1].strip()}"
    elif '+' in who and not who.startswith('Andrew'): attrib = f"\n\n— {who.split('+')[0].strip()}"
    out = Path(out); tmp = out / '_frames'; tmp.mkdir(parents=True, exist_ok=True); made = {}
    def shot(t, ratio, pid=None, mult=5.0):
        pid = speaker_at(segs, t) if pid is None else pid; raw = frame(src, c['t0'] + t, str(tmp / f'raw_{t:.2f}.jpg'))
        return crop(raw, P[pid], ratio, str(tmp / f'c_{t:.2f}_{ratio:.2f}_{pid}.jpg'), mult)
    other = lambda pid: next((q for q in P if q != pid), pid)
    # 1) convo stack — line by line, current speaker on top, the other person (or the next beat) below
    sl = []
    for k in range(0, min(len(sents), 10) - 1, 2):
        a, b_ = sents[k], sents[k + 1]; pa, pb = speaker_at(segs, (a['s'] + a['e']) / 2), speaker_at(segs, (b_['s'] + b_['e']) / 2)
        # each caption sits on the person who says it (same speaker twice → a tighter second angle)
        sl.append(dict(top_img=shot((a['s'] + a['e']) / 2, 0.625, pa, 4.6), top_text=a['text'], bot_img=shot((b_['s'] + b_['e']) / 2, 0.625, pb, 3.6 if pb == pa else 4.6), bot_text=b_['text']))
    made['convo'] = render(dict(format='convo', slides=sl[:5]), out / 'convo')
    # 2) tweet quotes — the lines that read best on their own
    quotes = sorted(sents, key=lambda s: -len(re.findall(r'\b(\d+|never|always|best|worst|fail\w*|money|clients?|customers?|simple|hard)\b', s['text'], re.I)))[:5]
    quotes = sorted(quotes, key=lambda s: s['s'])
    made['tweet'] = render(dict(format='tweet', slides=[dict(text=(f"“{q['text']}”" if attrib else q['text']) + attrib) for q in quotes] + [dict(text=f"From my conversation with {S.get('guest', 'a guest')}.\n\nFull clip on my page.", size=48)]), out / 'tweet')
    # 3) sticker story — title as stickers on the speaker, then the beats
    p0 = speaker_at(segs, sents[0]['s'] + 0.3); st = [dict(img=shot(sents[0]['s'] + 0.3, 1.25, p0, 5.5), lines=c['title'].split('\n'), cta="Here's what they said 👉")]
    for s in sents[1:5]: st.append(dict(img=shot((s['s'] + s['e']) / 2, 1.25, None, 5.5), lines=[s['text']], y=820))
    made['sticker'] = render(dict(format='sticker', slides=st), out / 'sticker')
    # 4) news headline cover + photo slides
    hl = [dict(format='headline', img=shot(sents[0]['s'] + 0.5, 1.25, p0, 6.5), text=c.get('hook_plain') or c['title'].replace('\n', ' '))]
    hl += [dict(format='tweet', text=(f"“{s['text']}”" if attrib else s['text']) + attrib) for s in sents[:3]]
    made['headline'] = render(dict(format='headline', slides=hl), out / 'headline')
    return made


def lessons(bank, out, n=5, guest=None):
    S = json.loads(Path(bank).read_text()); out = Path(out); tmp = out / '_frames'; tmp.mkdir(parents=True, exist_ok=True); slides = []
    clips = [c for c in S['clips'] if 'parts' not in c and not c.get('speaker', '').startswith('Andrew')][:n]  # the guest's lessons only; guest = guest or S.get('guest', 'the podcast')
    for i, c in enumerate(clips):
        src = c.get('src', S['source']); raw = frame(src, c['t0'] + min(3, c['dur'] / 2), str(tmp / f'l{i}.jpg'))
        im = Image.open(raw); IW, IH = im.size; r = 760 / 1080; ch = IW * r * 0.62; cw = ch / r
        im.crop((int((IW - cw) / 2), int((IH - ch) / 2), int((IW + cw) / 2), int((IH + ch) / 2))).resize((W, 760)).save(raw)
        first = re.split(r'(?<=[.!?])\s', c.get('text', '').replace(' -', '-'))[0]
        if len(first) > 110: first = first[:110].rsplit(' ', 1)[0] + '…'
        slides.append(dict(img=raw, label=f'LESSON #{i + 1}', title=c['title'].replace('\n', ' '), quote=first, footer=f'{len(clips)} lessons from {guest}'))
    return render(dict(format='lesson', slides=slides), out)


def event(video, out, word, sub, n=8):
    out = Path(out); tmp = out / '_frames'; tmp.mkdir(parents=True, exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video], capture_output=True, text=True).stdout)
    imgs = []
    for k in range(n):
        f = str(tmp / f'e{k}.jpg'); frame(video, dur * (k + 0.5) / n, f); im = Image.open(f); IW, IH = im.size
        ch = min(IH, IW * 1.25); cw = ch / 1.25; im.crop((int((IW - cw) / 2), int((IH - ch) / 2), int((IW + cw) / 2), int((IH + ch) / 2))).resize((W, H)).save(f); imgs.append(f)
    slides = [dict(format='bigword', img=imgs[0], word=word, sub=sub, swipe=True)] + [dict(format='photo', img=x) for x in imgs[1:]]
    return render(dict(format='bigword', slides=slides), out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('args', nargs='+'); ap.add_argument('--word', default='LEVEL UP'); ap.add_argument('--sub', default='')
    ap.add_argument('--guest'); a = ap.parse_args()
    if a.cmd == 'render': print(render(json.loads(Path(a.args[0]).read_text()), a.args[1]))
    elif a.cmd == 'clip': print(json.dumps(from_clip(a.args[0], a.args[1], a.args[2]), indent=1))
    elif a.cmd == 'lessons': print(lessons(a.args[0], a.args[1], guest=a.guest))
    elif a.cmd == 'event': print(event(a.args[0], a.args[1], a.word, a.sub))
