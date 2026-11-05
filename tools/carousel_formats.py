#!/usr/bin/env python3
"""Carousels modelled on Andrew's competitor references (research/carousels/, docs/carousel-formats.md). One video → many carousels.

Andrew's rules (Nov 5 review):
- Slide 1 is the hook: in one second it must say what this is and why to swipe (who, what, the payoff). Every carousel gets a hero.
- Podcast stack: slide 1 = Andrew on top, the speaker below, the hook in the middle band; then the speaker alone for a few slides.
- Quote cards always say whose words and where from ("From my podcast with Andy Griffith, SoloLink"). Avatar = research/brand/pfp_andrew.png.
- Lessons: name the guest; hero slide (breaking-news style, both people); each lesson image = Andrew left + guest right, middle cut out.
- Event recaps use the real photos (RAWFROMPHOTOS), not video grabs; the caption explains the event.
- Text cards ("A lesson from a SaaS-preneur award winner") for Threads / LinkedIn image posts.
Usage:
  python3 tools/carousel_formats.py clip BANK.json CLIP_ID OUT_DIR      # podcast stack, quotes, sticker, headline, text cards
  python3 tools/carousel_formats.py hybrid BANK.json CLIP_ID OUT_DIR    # images + a video slide (needs formats/<id>/<id>-v7.mp4)
  python3 tools/carousel_formats.py lessons BANK.json OUT_DIR           # "5 lessons from <guest>"
  python3 tools/carousel_formats.py photos SPEC.json OUT_DIR            # photo dump: {"hero": {"img","title","sub"}, "photos": [paths]}
Bank-level fields: guest_name, guest_org, guest_title (e.g. "SaaS-preneur award winner"). Andrew (host) sits on the left.
"""
import argparse, html, json, os, re, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent; FONTS = ROOT / 'tools/fonts'
PROFILE = dict(name='Andrew George', handle='@andrewpreneurship', avatar=str(ROOT / 'research/brand/pfp_andrew.png'))
W, H = 1080, 1350
CSS = f"""
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-Regular.woff');font-weight:400}}
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-SemiBold.woff');font-weight:600}}
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-Bold.woff');font-weight:700}}
@font-face{{font-family:Tight;src:url('file://{FONTS}/InterTight-ExtraBold.ttf');font-weight:800}}
@font-face{{font-family:Oswald;src:url('file://{FONTS}/Oswald-SemiBold.woff');font-weight:600}}
*{{box-sizing:border-box;margin:0}} body{{width:{W}px;height:{H}px;overflow:hidden;font-family:Inter,sans-serif;background:#000}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:center}}
.cap{{text-align:center;font:700 54px/1.14 Inter;-webkit-text-stroke:3px #000;paint-order:stroke fill;text-shadow:0 3px 10px rgba(0,0,0,.6)}}
.lbl{{position:absolute;left:28px;font:700 26px Inter;color:#fff;background:rgba(0,0,0,.55);padding:6px 14px;border-radius:10px}}
"""


def esc(s):
    return html.escape(s or '').replace('\n', '<br>')


def U(p):
    return 'file://' + str(Path(p).resolve())


def slide_html(s, prof):
    f = s['format']; av = lambda n: f"<img src='{U(prof['avatar'])}' style='width:{n}px;height:{n}px;border-radius:50%;object-fit:cover'>"
    if f == 'split':  # Andrew top, speaker bottom, hook in the middle band
        return (f"<div style='position:absolute;left:0;top:0;width:{W}px;height:600px;background:url({U(s['top'])}) center/cover'></div>"
                f"<div style='position:absolute;left:0;top:750px;width:{W}px;height:600px;background:url({U(s['bot'])}) center/cover'></div>"
                f"<div style='position:absolute;left:0;top:600px;width:{W}px;height:150px;background:#0B0B0B;display:flex;align-items:center;justify-content:center;padding:0 50px'>"
                f"<div style='font:800 {s.get('size', 52)}px/1.08 Tight;color:#fff;text-align:center;letter-spacing:-.01em'>{esc(s['text'])}</div></div>"
                + (f"<div class='lbl' style='top:28px'>{esc(s['top_label'])}</div>" if s.get('top_label') else '')
                + (f"<div class='lbl' style='bottom:28px'>{esc(s['bot_label'])}</div>" if s.get('bot_label') else ''))
    if f == 'single':
        return (f"<div class='bg' style='background-image:url({U(s['img'])})'></div>"
                f"<div class='cap' style='position:absolute;left:60px;right:60px;bottom:90px;color:{s.get('color', '#fff')}'>{esc(s['text'])}</div>")
    if f == 'hero':  # breaking-news cover: both people + headline
        return (f"<div class='bg' style='background-image:url({U(s['img'])})'></div><div class='bg' style='background:linear-gradient(180deg,rgba(0,0,0,0) 38%,rgba(0,0,0,.88) 74%)'></div>"
                f"<div style='position:absolute;left:56px;right:56px;bottom:84px;color:#fff'>"
                f"<span style='display:inline-block;background:{s.get('tag_bg', '#E32B2B')};color:#fff;font:600 34px Oswald;letter-spacing:.06em;padding:4px 16px;margin-bottom:22px'>{esc(s.get('tag', 'NEW EPISODE'))}</span>"
                f"<div style='font:600 {s.get('size', 98)}px/1.02 Oswald;text-transform:uppercase;text-shadow:0 4px 18px rgba(0,0,0,.5)'>{esc(s['title'])}</div>"
                f"<div style='font:600 38px/1.3 Inter;margin-top:18px;color:#E8E8E8'>{esc(s.get('sub', ''))}</div></div>")
    if f == 'tweet':
        big = s.get('size', 58 if len(s['text']) < 200 else 46)
        foot = f"<div style='font:400 30px/1.35 Inter;color:#8B98A5;margin-top:40px'>{esc(s['foot'])}</div>" if s.get('foot') else ''
        return (f"<div class='bg' style='background:#000'></div><div style='position:absolute;left:84px;right:84px;top:50%;transform:translateY(-50%);color:#fff'>"
                f"<div style='display:flex;gap:26px;align-items:center;margin-bottom:44px'>{av(128)}<div><div style='font:700 52px Inter'>{esc(prof['name'])}</div>"
                f"<div style='font:400 40px Inter;color:#8B98A5'>{esc(prof['handle'])}</div></div></div>"
                f"<div style='font:400 {big}px/1.24 Inter;letter-spacing:-.01em'>{esc(s['text'])}</div>{foot}</div>")
    if f == 'textcard':
        return (f"<div class='bg' style='background:{s.get('bg', '#F4F1EA')}'></div><div style='position:absolute;left:96px;right:96px;top:50%;transform:translateY(-50%);color:#151515'>"
                f"<div style='font:600 34px Inter;letter-spacing:.04em;text-transform:uppercase;color:#7A6F5D;margin-bottom:34px'>{esc(s['label'])}</div>"
                f"<div style='font:800 {s.get('size', 74)}px/1.1 Tight;letter-spacing:-.015em'>“{esc(s['text'])}”</div>"
                f"<div style='display:flex;gap:18px;align-items:center;margin-top:52px'>{(f"<img src='{U(s['avatar'])}' style='width:84px;height:84px;border-radius:50%;object-fit:cover'>" if s.get('avatar') else av(84))}<div style='font:600 32px/1.3 Inter'>{esc(s['by'])}<br><span style='font-weight:400;color:#6B6458'>{esc(s.get('by2', ''))}</span></div></div></div>")
    if f == 'lesson':
        return (f"<div style='position:absolute;left:0;top:0;width:{W}px;height:760px;background:url({U(s['img'])}) center/cover'></div>"
                f"<div style='position:absolute;left:0;top:760px;width:{W}px;height:590px;background:#fff;text-align:center;padding:52px 80px 0'>"
                f"<span style='display:inline-block;background:#FFD400;color:#111;font:600 64px Oswald;letter-spacing:.02em;padding:4px 26px'>{esc(s['label'])}</span>"
                f"<div style='font:800 {76 if len(s['title']) <= 32 else 62}px/1.08 Tight;color:#111;margin-top:28px;letter-spacing:-.01em'>{esc(s['title'])}</div>"
                f"<div style='font:400 32px/1.35 Inter;color:#333;margin-top:20px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden'>“{esc(s['quote'])}”</div>"
                f"<div style='position:absolute;left:0;right:0;bottom:48px;font:700 32px Inter;color:#111'>{esc(s.get('footer', ''))}</div></div>")
    if f == 'sticker':
        lines = ''.join(f"<div style='display:inline-block;background:#fff;color:#111;font:700 52px/1.18 Inter;padding:12px 26px;border-radius:18px;margin:6px 0;max-width:900px'>{esc(l)}</div><br>" for l in s['lines'])
        cta = f"<div style='display:inline-block;background:#fff;color:#111;font:700 46px Inter;padding:10px 24px;border-radius:16px;margin-top:22px'>{esc(s['cta'])}</div>" if s.get('cta') else ''
        return f"<div class='bg' style='background-image:url({U(s['img'])})'></div><div style='position:absolute;left:0;right:0;top:{s.get('y', 640)}px;text-align:center'>{lines}{cta}</div>"
    if f == 'headline':
        return (f"<div class='bg' style='background-image:url({U(s['img'])})'></div><div class='bg' style='background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.82) 88%)'></div>"
                f"<div style='position:absolute;left:60px;right:60px;bottom:110px;text-align:center;font:600 {s.get('size', 104)}px/1.06 Oswald;color:#fff;text-transform:uppercase;text-shadow:0 4px 18px rgba(0,0,0,.6)'>{esc(s['text'])}</div>")
    if f == 'photohero':
        return (f"<div class='bg' style='background-image:url({U(s['img'])})'></div><div class='bg' style='background:linear-gradient(180deg,rgba(0,0,0,0) 50%,rgba(0,0,0,.78) 90%)'></div>"
                f"<div style='position:absolute;left:60px;right:60px;bottom:96px;color:#fff'><div style='font:800 {s.get('size', 96)}px/1.02 Tight;letter-spacing:-.02em'>{esc(s['title'])}</div>"
                f"<div style='font:600 40px/1.3 Inter;margin-top:16px'>{esc(s.get('sub', ''))}</div></div>")
    if f == 'photo':
        return f"<div class='bg' style='background-image:url({U(s['img'])})'></div>"
    raise SystemExit('unknown format ' + f)


def render(slides, out, prof=None):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); prof = prof or PROFILE; hd = out / '_html'; hd.mkdir(exist_ok=True); pairs, files = [], []
    for i, s in enumerate(slides):
        if s['format'] == 'video':
            dst = out / f'slide-{i + 1:02d}.mp4'; shutil.copy(s['file'], dst); files.append(str(dst)); continue
        h = hd / f'slide-{i + 1:02d}.html'; h.write_text(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{slide_html(s, prof)}</body></html>")
        f = out / f'slide-{i + 1:02d}.png'; pairs.append(f'{h}:{f}'); files.append(str(f))
    if pairs: subprocess.run(['node', str(ROOT / 'tools/shoot.js'), str(W), str(H), *pairs], check=True, env={**os.environ, 'NODE_PATH': '/opt/node-tools/node_modules'})
    (out / 'carousel.json').write_text(json.dumps(slides, indent=1, ensure_ascii=False)); return files


def grab(src, t, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', src, '-frames:v', '1', '-q:v', '2', out], check=True); return out


def crop_person(img, p, w, h, mult=4.2, top=0.34):
    im = Image.open(img); IW, IH = im.size; r = h / w; cw = min(IW, mult * p['face']); ch = cw * r
    if ch > IH: ch = IH; cw = ch / r
    cx = min(max(p['x'], cw / 2), IW - cw / 2); cy = min(max(p['y'] + (0.5 - top) * ch, ch / 2), IH - ch / 2)
    return im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((w, h), Image.LANCZOS)


def duo(img, left, right, w, h, out, mult=3.4):
    c = Image.new('RGB', (w, h)); c.paste(crop_person(img, left, w // 2, h, mult), (0, 0)); c.paste(crop_person(img, right, w - w // 2, h, mult), (w // 2, 0)); c.save(out, quality=92); return out


def single(img, p, w, h, out, mult=4.2):
    crop_person(img, p, w, h, mult).save(out, quality=92); return out


DEP = {'and', 'but', 'so', 'because', 'which', 'that', "that's", 'it', "it's", 'they', 'this', 'yeah', 'yes', 'um', 'uh', 'like', 'right', 'okay', 'oh', 'well', 'or', 'then', 'also'}
FILL = re.compile(r"\b(you know|i mean|kind of|sort of|in my mind's eye)\b", re.I)


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
            t = ' '.join(x[0] for x in pp).replace(' -', '-').rstrip(','); t = t[0].upper() + t[1:]
            res.append(dict(text=t + ('' if re.search(r'[.!?]$', t) else '.'), s=pp[0][1], e=pp[-1][2]))
    return res


def good(x):
    w = x['text'].split(); return 5 <= len(w) <= 24 and re.sub(r"[^a-z']", '', w[0].lower()) not in DEP and not FILL.search(x['text'])


def context(bank, cid):
    S = json.loads(Path(bank).read_text()); c = next(x for x in S['clips'] if x['id'] == cid); work = Path(S['work']); src = c.get('src', S['source'])
    words = json.loads((work / f'{cid}.words.json').read_text()); spk_p = Path('/home/user/work/formats') / cid / 'speakers.json'
    if not spk_p.exists():
        spk_p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['/home/user/work/dfenv/bin/python', str(ROOT / 'tools/speakers.py'), src, str(spk_p), '--start', str(c['t0']), '--dur', str(c['dur']),
                        '--words', str(work / f'{cid}.words.json')], check=True, capture_output=True)
    spk = json.loads(spk_p.read_text())
    import sys; sys.path.insert(0, str(ROOT / 'tools')); from speakers_guard import check_label
    spk, _ = check_label(spk, c.get('speaker', '')); P = sorted(spk['people'], key=lambda p: p['x'])
    host = P[0]; main = next(p for p in P if p['id'] == spk['main'])
    guest = main if main is not host else (P[-1] if len(P) > 1 else host)
    allS = sentences(words); sents = [x for x in allS if good(x)]
    if len(sents) < 3: sents = [x for x in allS if 4 <= len(x['text'].split()) <= 26] or allS
    g, org, gt = S.get('guest_name', 'my guest'), S.get('guest_org', ''), S.get('guest_title', '')
    sp = c.get('speaker', ''); by_host = sp.startswith('Andrew') and '→' not in sp and '+' not in sp
    who = 'Andrew George' if by_host else (S['speaker_names'].get(sp, sp) if S.get('speaker_names') else g)
    return dict(S=S, c=c, src=src, P=P, host=host, guest=guest, main=main, sents=sents, g=g, org=org, gt=gt, who=who, by_host=by_host,
                where=f"From my podcast with {g}{', ' + org if org else ''}")


def quote_text(X, s):
    return s['text'] if X['by_host'] else f"“{s['text']}”\n— {X['who']}"


def from_clip(bank, cid, out):
    X = context(bank, cid); c, src, sents = X['c'], X['src'], X['sents']; out = Path(out); fr = out / '_frames'; fr.mkdir(parents=True, exist_ok=True); made = {}
    t_of = lambda s: c['t0'] + (s['s'] + s['e']) / 2
    raw = lambda t: grab(src, t, str(fr / f'raw_{t:.2f}.jpg'))
    hook = c.get('hook_q') or c['title'].replace('\n', ' '); r0 = raw(t_of(sents[0]))
    # 1) podcast stack: Andrew top / speaker bottom, hook in the middle → the speaker alone, line by line
    bot_label = '' if X['by_host'] else X['who'] + (f" · {X['org']}" if X['org'] and X['who'] == X['g'] else '')
    other = X['guest'] if X['by_host'] else X['main']
    sl = [dict(format='split', top=single(r0, X['host'], W, 600, str(fr / 'host_top.jpg'), 4.6), bot=single(r0, other, W, 600, str(fr / 'other_bot.jpg'), 4.6),
               text=hook, top_label='Andrew George', bot_label=bot_label)]
    for k, s in enumerate(sents[:5]):
        sl.append(dict(format='single', img=single(raw(t_of(s)), X['main'], W, H, str(fr / f'one_{k}.jpg'), 3.8), text=s['text'], color='#FFE14D' if k % 2 == 0 else '#FFFFFF'))
    made['convo'] = render(sl, out / 'convo')
    # 2) quote cards: hero (both people + title + where it's from), then attributed quotes
    hero_img = duo(r0, X['host'], X['guest'], W, H, str(fr / 'duo_hero.jpg'))
    quotes = sorted(sorted(sents, key=lambda s: -len(re.findall(r'\b(\d+|never|always|best|worst|fail\w*|money|clients?|customers?|simple|hard|learn\w*|paid)\b', s['text'], re.I)))[:4], key=lambda s: s['s'])
    q = [dict(format='hero', img=hero_img, tag='FROM THE PODCAST', title=c['title'].replace('\n', ' '), sub=X['where'], size=92)]
    q += [dict(format='tweet', text=quote_text(X, s), foot=X['where']) for s in quotes]
    q.append(dict(format='tweet', text=f"Full conversation with {X['g']} is on my page.\n\nWhich line hit hardest?", size=50))
    made['tweet'] = render(q, out / 'tweet')
    # 3) sticker story
    st = [dict(format='sticker', img=single(r0, X['main'], W, H, str(fr / 'st0.jpg'), 5.2), lines=c['title'].split('\n'), cta=(f"What I told {X['g']} 👉" if X['by_host'] else f"{X['who']} on my podcast 👉"))]
    for k, s in enumerate(sents[1:5]): st.append(dict(format='sticker', img=single(raw(t_of(s)), X['main'], W, H, str(fr / f'st{k + 1}.jpg'), 5.2), lines=[s['text']], y=820))
    made['sticker'] = render(st, out / 'sticker')
    # 4) news cover + attributed quotes
    hl = [dict(format='headline', img=hero_img, text=c.get('hook_plain') or c['title'].replace('\n', ' '))]
    hl += [dict(format='tweet', text=quote_text(X, s), foot=X['where']) for s in sents[:3]]
    made['headline'] = render(hl, out / 'headline')
    # 5) text cards for Threads / LinkedIn
    label = f"A lesson from a {X['gt']}" if X['gt'] and not X['by_host'] else 'From my podcast'
    face = None if X['by_host'] else str(crop_person(r0, X['main'], 240, 240, 3.0, 0.42).save(fr / 'face.jpg', quality=92) or fr / 'face.jpg')
    tc = [dict(format='textcard', label=label, avatar=face, text=s['text'].rstrip('.'), by=X['who'], by2=(X['org'] + ' · ' if X['org'] and not X['by_host'] else '') + 'on my podcast',
               size=74 if len(s['text']) < 90 else 60) for s in quotes[:3]]
    made['textcards'] = render(tc, out / 'textcards')
    return made


def hybrid(bank, cid, out, video_fmt='v7'):
    X = context(bank, cid); c, src, sents = X['c'], X['src'], X['sents']; out = Path(out); fr = out / '_frames'; fr.mkdir(parents=True, exist_ok=True)
    reel = Path('/home/user/work/formats') / cid / f'{cid}-{video_fmt}.mp4'; vid = fr / 'video45.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(reel), '-vf', 'crop=1080:1350:0:285', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '192k', str(vid)], check=True)
    r0 = grab(src, c['t0'] + (sents[0]['s'] + sents[0]['e']) / 2, str(fr / 'r0.jpg'))
    slides = [dict(format='hero', img=duo(r0, X['host'], X['guest'], W, H, str(fr / 'duo.jpg')), tag='FROM THE PODCAST', title=c['title'].replace('\n', ' '), sub=X['where'] + ' · swipe to watch →', size=92),
              dict(format='video', file=str(vid))]
    slides += [dict(format='tweet', text=quote_text(X, s), foot=X['where']) for s in sents[:3]]
    rl = grab(src, c['t0'] + (sents[-1]['s'] + sents[-1]['e']) / 2, str(fr / 'r1.jpg'))
    slides.append(dict(format='sticker', img=single(rl, X['main'], W, H, str(fr / 'st.jpg'), 5.2), lines=[sents[-1]['text']], y=820))
    face = None if X['by_host'] else str(crop_person(r0, X['main'], 240, 240, 3.0, 0.42).save(fr / 'face.jpg', quality=92) or fr / 'face.jpg')
    slides.append(dict(format='textcard', avatar=face, label=f"A lesson from a {X['gt']}" if X['gt'] and not X['by_host'] else 'Save this', text=c.get('hook_plain') or c['title'].replace('\n', ' '),
                       by=X['who'], by2=(X['org'] + ' · ' if X['org'] and not X['by_host'] else '') + 'on my podcast'))
    return render(slides, out)


def lessons(bank, out, n=5):
    S = json.loads(Path(bank).read_text()); out = Path(out); fr = out / '_frames'; fr.mkdir(parents=True, exist_ok=True)
    g, org, gt = S.get('guest_name', 'my guest'), S.get('guest_org', ''), S.get('guest_title', 'founder')
    clips = [c for c in S['clips'] if 'parts' not in c and not c.get('speaker', '').startswith('Andrew')][:n]; slides = []
    for i, c in enumerate(clips):
        X = context(bank, c['id']); r = grab(X['src'], c['t0'] + min(3, c['dur'] / 2), str(fr / f'l{i}.jpg'))
        if i == 0:
            slides.append(dict(format='hero', img=duo(r, X['host'], X['guest'], W, H, str(fr / 'hero.jpg')), tag='BREAKING', title=S.get('lessons_title', f"{len(clips)} lessons from a {gt}"),
                               sub=f"{g}{', ' + org if org else ''} · on my podcast", size=100))
        first = re.split(r'(?<=[.!?])\s', c.get('text', '').replace(' -', '-'))[0]
        if len(first) > 110: first = first[:110].rsplit(' ', 1)[0] + '…'
        slides.append(dict(format='lesson', img=duo(r, X['host'], X['main'] if X['main'] is not X['host'] else X['guest'], W, 760, str(fr / f'd{i}.jpg')), label=f'LESSON #{i + 1}',
                           title=c['title'].replace('\n', ' '), quote=first, footer=f"{len(clips)} lessons from {g}"))
    return render(slides, out)


def photos(spec, out):
    sp = json.loads(Path(spec).read_text()); out = Path(out); fr = out / '_frames'; fr.mkdir(parents=True, exist_ok=True)
    def fit(p, k, fy=0.3):
        im = ImageOps.exif_transpose(Image.open(p)).convert('RGB'); IW, IH = im.size; r = H / W
        if IH / IW > r: ch = IW * r; y0 = (IH - ch) * fy; box = (0, int(y0), IW, int(y0 + ch))
        else: cw = IH / r; x0 = (IW - cw) / 2; box = (int(x0), 0, int(x0 + cw), IH)
        f = fr / f'p{k}.jpg'; im.crop(box).resize((W, H), Image.LANCZOS).save(f, quality=92); return str(f)
    h = sp['hero']; slides = [dict(format='photohero', img=fit(h['img'], 0, h.get('focus_y', 0.3)), title=h['title'], sub=h.get('sub', ''), size=h.get('size', 96))]
    slides += [dict(format='photo', img=fit(p, k + 1)) for k, p in enumerate(sp['photos'])]
    return render(slides, out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('args', nargs='+'); a = ap.parse_args()
    if a.cmd == 'clip': print(json.dumps(from_clip(a.args[0], a.args[1], a.args[2]), indent=1))
    elif a.cmd == 'hybrid': print(hybrid(a.args[0], a.args[1], a.args[2]))
    elif a.cmd == 'lessons': print(lessons(a.args[0], a.args[1]))
    elif a.cmd == 'photos': print(photos(a.args[0], a.args[1]))
