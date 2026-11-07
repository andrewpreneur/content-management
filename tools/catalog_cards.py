#!/usr/bin/env python3
"""Catalog cards (Nov 7 overnight): single images, thread carousels and story frames built from real frames.

Lessons from the Nov 4 feature carousels Andrew didn't like (see outputs/2026-11-07-catalog/README.md):
every slide here is either a real face (big) or big type on a plain card. No tiny screenshots, no slide-deck chrome.

Formats (render(slides, out_dir, w, h) -> list of files; slides are dicts with 'format'):
  quote      cream card, big quote, speaker face + name + where it's from         (1080x1350 or 1200x627)
  stat       navy card, giant yellow number, one-line label, face + attribution  (1080x1350 or 1200x627)
  tweet      black card, Andrew avatar/name/handle, big plain text               (1080x1350 or 1200x627)
  facehook   full-bleed photo of the speaker, hook in big type over a dark fade  (1080x1350) — thread cover
  cta        navy card with one action                                           (1080x1350)
  story      1080x1920 story frame: photo/thumbnail, text, optional link-sticker placeholder
"""
import html, json, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent; FONTS = ROOT / 'tools/fonts'
AV = ROOT / 'research/brand/pfp_andrew.png'
NAVY, YEL, BLUE = '#0B0F1A', '#FFD23F', '#2E7DFF'
CSS = f"""
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-Regular.woff');font-weight:400}}
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-SemiBold.woff');font-weight:600}}
@font-face{{font-family:Inter;src:url('file://{FONTS}/Inter-Bold.woff');font-weight:700}}
@font-face{{font-family:Tight;src:url('file://{FONTS}/InterTight-ExtraBold.ttf');font-weight:800}}
@font-face{{font-family:Oswald;src:url('file://{FONTS}/Oswald-SemiBold.woff');font-weight:600}}
*{{box-sizing:border-box;margin:0}} body{{overflow:hidden;font-family:Inter,sans-serif}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:center}}
.av{{border-radius:50%;object-fit:cover;flex:none}}
.hl{{color:{YEL}}}
.cap{{text-align:center;font:700 54px/1.14 Inter;-webkit-text-stroke:3px #000;paint-order:stroke fill;text-shadow:0 3px 10px rgba(0,0,0,.6)}}
.lbl{{position:absolute;left:28px;font:700 26px Inter;color:#fff;background:rgba(0,0,0,.55);padding:6px 14px;border-radius:10px}}
"""


def esc(s):
    s = html.escape(s or '').replace('\n', '<br>')
    return s.replace('[[', "<span class='hl'>").replace(']]', '</span>')  # [[word]] = yellow accent


def U(p):
    return 'file://' + str(Path(p).resolve())


def fit(text, big, small, n=90):
    return big if len(text) <= n else small if len(text) <= n * 1.8 else int(small * 0.82)


def byline(s, size, color, sub_color):
    av = s.get('avatar') or AV
    return (f"<div style='display:flex;gap:{size // 2}px;align-items:center'><img class='av' src='{U(av)}' style='width:{size * 2.4:.0f}px;height:{size * 2.4:.0f}px'>"
            f"<div style='font:700 {size}px/1.25 Inter;color:{color}'>{esc(s.get('by', 'Andrew George'))}<br><span style='font-weight:400;color:{sub_color}'>{esc(s.get('by2', '@andrewpreneurship'))}</span></div></div>")


def slide_html(s, W, H):
    f = s['format']; land = W > H
    if f in ('split', 'single'):  # pod1-05 "convo" (Hormozi podcast stack) slides, unchanged from tools/carousel_formats.py
        import sys; sys.path.insert(0, str(ROOT / 'tools')); import carousel_formats as CF
        return CF.slide_html(s, CF.PROFILE)
    if f == 'quote':
        t = s['text']
        if land:  # photo left, quote right
            sz = fit(t, 50, 40, 70)
            return (f"<div class='bg' style='background:#F4F1EA'></div>"
                    f"<div style='position:absolute;left:0;top:0;width:430px;height:{H}px;background:url({U(s['photo'])}) center/cover'></div>"
                    f"<div style='position:absolute;left:480px;right:56px;top:50%;transform:translateY(-50%);color:#151515'>"
                    f"<div style='font:600 22px Inter;letter-spacing:.06em;text-transform:uppercase;color:#7A6F5D;margin-bottom:18px'>{esc(s.get('label', ''))}</div>"
                    f"<div style='font:800 {sz}px/1.1 Tight;letter-spacing:-.015em'>“{esc(t)}”</div>"
                    f"<div style='margin-top:26px;font:700 24px/1.3 Inter'>{esc(s['by'])}<br><span style='font-weight:400;color:#6B6458'>{esc(s.get('by2', ''))}</span></div></div>")
        sz = fit(t, 80, 64, 70)
        return (f"<div class='bg' style='background:#F4F1EA'></div><div style='position:absolute;left:96px;right:96px;top:50%;transform:translateY(-50%);color:#151515'>"
                f"<div style='font:600 32px Inter;letter-spacing:.05em;text-transform:uppercase;color:#7A6F5D;margin-bottom:36px'>{esc(s.get('label', ''))}</div>"
                f"<div style='font:800 {sz}px/1.08 Tight;letter-spacing:-.015em'>“{esc(t)}”</div>"
                f"<div style='margin-top:56px'>{byline(s, 34, '#151515', '#6B6458')}</div></div>")
    if f == 'stat':
        n = s['num']; ns = (300 if len(n) <= 3 else 230 if len(n) <= 5 else 170) if not land else (200 if len(n) <= 3 else 150 if len(n) <= 5 else 115)
        if land:
            return (f"<div class='bg' style='background:{NAVY}'></div>"
                    f"<div style='position:absolute;left:64px;top:50%;transform:translateY(-50%);width:560px;font:800 {ns}px/0.95 Tight;color:{YEL};letter-spacing:-.03em'>{esc(n)}</div>"
                    f"<div style='position:absolute;left:640px;right:60px;top:50%;transform:translateY(-50%);color:#fff'>"
                    f"<div style='font:700 40px/1.2 Inter'>{esc(s['label'])}</div><div style='margin-top:30px'>{byline(s, 22, '#fff', '#9AA3B5')}</div></div>")
        return (f"<div class='bg' style='background:{NAVY}'></div><div style='position:absolute;left:90px;right:90px;top:50%;transform:translateY(-50%);color:#fff'>"
                f"<div style='font:800 {ns}px/0.95 Tight;color:{YEL};letter-spacing:-.03em'>{esc(n)}</div>"
                f"<div style='font:700 56px/1.18 Inter;margin-top:40px'>{esc(s['label'])}</div>"
                f"<div style='margin-top:70px'>{byline(s, 32, '#fff', '#9AA3B5')}</div></div>")
    if f == 'tweet':
        t = s['text']
        if land:
            sz = fit(t, 46, 36, 110)
            return (f"<div class='bg' style='background:#000'></div><div style='position:absolute;left:80px;right:80px;top:50%;transform:translateY(-50%);color:#fff'>"
                    f"<div style='margin-bottom:28px'>{byline(dict(s, by='Andrew George', by2='@andrewpreneurship', avatar=AV), 28, '#fff', '#8B98A5')}</div>"
                    f"<div style='font:400 {sz}px/1.25 Inter;letter-spacing:-.01em'>{esc(t)}</div></div>")
        sz = s.get('size') or fit(t, 74, 60, 110)
        foot = f"<div style='font:400 30px/1.35 Inter;color:#8B98A5;margin-top:40px'>{esc(s['foot'])}</div>" if s.get('foot') else ''
        return (f"<div class='bg' style='background:#000'></div><div style='position:absolute;left:84px;right:84px;top:50%;transform:translateY(-50%);color:#fff'>"
                f"<div style='margin-bottom:44px'>{byline(dict(s, by='Andrew George', by2='@andrewpreneurship', avatar=AV), 46, '#fff', '#8B98A5')}</div>"
                f"<div style='font:400 {sz}px/1.24 Inter;letter-spacing:-.01em'>{esc(t)}</div>{foot}</div>"
                + (f"<div style='position:absolute;right:60px;bottom:50px;font:600 28px Inter;color:#5B6570'>{esc(s['num'])}</div>" if s.get('num') else ''))
    if f == 'facehook':
        sz = s.get('size') or fit(s['text'], 110, 88, 30)
        tag = f"<span style='display:inline-block;background:{s.get('tag_bg', YEL)};color:#111;font:600 34px Oswald;letter-spacing:.06em;padding:4px 16px;margin-bottom:24px'>{esc(s['tag'])}</span><br>" if s.get('tag') else ''
        return (f"<div class='bg' style='background-image:url({U(s['photo'])});background-position:{s.get('pos', 'center top')}'></div>"
                f"<div class='bg' style='background:linear-gradient(180deg,rgba(0,0,0,0) 35%,rgba(0,0,0,.9) 78%)'></div>"
                f"<div style='position:absolute;left:64px;right:64px;bottom:96px;color:#fff'>{tag}"
                f"<div style='font:800 {sz}px/1.0 Tight;letter-spacing:-.02em;text-shadow:0 4px 18px rgba(0,0,0,.5)'>{esc(s['text'])}</div>"
                f"<div style='font:600 38px/1.3 Inter;margin-top:22px;color:#E8E8E8'>{esc(s.get('sub', ''))}</div></div>"
                + (f"<div style='position:absolute;right:56px;top:56px;font:700 30px Inter;color:#fff;background:rgba(0,0,0,.5);padding:8px 18px;border-radius:30px'>swipe →</div>" if s.get('swipe', True) else ''))
    if f == 'ytpost':  # 1080x1350: the real thumbnail (a face + a promise), big headline under it
        return (f"<div class='bg' style='background:url({U(s['bg'])}) center/cover'></div>"
                f"<div style='position:absolute;left:40px;right:40px;top:150px;height:562px;border-radius:26px;overflow:hidden;background:url({U(s['thumb'])}) center/cover;box-shadow:0 20px 60px rgba(0,0,0,.6)'></div>"
                f"<div style='position:absolute;left:70px;right:70px;top:780px;color:#fff'>"
                f"<span style='display:inline-block;background:#E32B2B;color:#fff;font:600 34px Oswald;letter-spacing:.06em;padding:4px 16px;margin-bottom:24px'>NEW VIDEO</span>"
                f"<div style='font:800 {fit(s['text'], 76, 62, 50)}px/1.05 Tight;letter-spacing:-.015em'>{esc(s['text'])}</div>"
                f"<div style='font:600 32px Inter;color:#C9CFDA;margin-top:26px'>▶ Watch on YouTube · link in bio</div></div>"
                f"<div style='position:absolute;left:70px;top:56px;display:flex;gap:16px;align-items:center'><img class='av' src='{U(AV)}' style='width:58px;height:58px'><div style='font:700 28px Inter;color:#fff'>Andrew George</div></div>")
    if f == 'ytland':  # LinkedIn 1200x627: YouTube thumbnail left, one line right
        return (f"<div class='bg' style='background:{NAVY}'></div>"
                f"<div style='position:absolute;left:48px;top:50%;transform:translateY(-50%);width:600px;height:338px;border-radius:18px;overflow:hidden;background:url({U(s['thumb'])}) center/cover;box-shadow:0 14px 40px rgba(0,0,0,.5)'></div>"
                f"<div style='position:absolute;left:690px;right:48px;top:50%;transform:translateY(-50%);color:#fff'>"
                f"<span style='display:inline-block;background:#E32B2B;color:#fff;font:600 24px Oswald;letter-spacing:.06em;padding:3px 12px;margin-bottom:18px'>NEW VIDEO</span>"
                f"<div style='font:800 {fit(s['text'], 46, 38, 50)}px/1.08 Tight;letter-spacing:-.01em'>{esc(s['text'])}</div>"
                f"<div style='font:600 22px Inter;color:#9AA3B5;margin-top:18px'>Andrew George · YouTube</div></div>")
    if f == 'cta':
        return (f"<div class='bg' style='background:{NAVY}'></div><div style='position:absolute;left:96px;right:96px;top:50%;transform:translateY(-50%);color:#fff;text-align:center'>"
                f"<img class='av' src='{U(AV)}' style='width:200px;height:200px;border:6px solid {YEL}'>"
                f"<div style='font:800 {fit(s['text'], 76, 60, 50)}px/1.1 Tight;margin-top:50px;letter-spacing:-.01em'>{esc(s['text'])}</div>"
                f"<div style='font:600 36px Inter;color:#9AA3B5;margin-top:40px'>Andrew George · @andrewpreneurship</div></div>")
    if f == 'story':
        img = (f"<div style='position:absolute;left:60px;right:60px;top:{s.get('img_top', 420)}px;height:{s.get('img_h', 540)}px;border-radius:28px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.5);"
               f"background:url({U(s['img'])}) center/cover'></div>") if s.get('img') and not s.get('full') else ''
        full = f"<div class='bg' style='background-image:url({U(s['img'])})'></div><div class='bg' style='background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 55%,rgba(0,0,0,.85) 100%)'></div>" if s.get('full') else ''
        top = f"<div style='position:absolute;left:70px;right:70px;top:{s.get('text_top', 170)}px;font:800 {s.get('size', 76)}px/1.08 Tight;color:#fff;letter-spacing:-.015em'>{esc(s.get('text', ''))}</div>" if s.get('text') else ''
        sub = f"<div style='position:absolute;left:70px;right:70px;top:{s.get('sub_top', 1040)}px;font:600 46px/1.3 Inter;color:#E6E9F0'>{esc(s.get('sub', ''))}</div>" if s.get('sub') else ''
        link = (f"<div style='position:absolute;left:50%;transform:translateX(-50%);top:{s.get('link_top', 1500)}px;background:#fff;color:#1A5BFF;font:700 44px Inter;padding:22px 40px;border-radius:22px;white-space:nowrap;box-shadow:0 8px 30px rgba(0,0,0,.35)'>🔗 {esc(s['link'])}</div>"
                f"<div style='position:absolute;left:0;right:0;top:{s.get('link_top', 1500) + 120}px;text-align:center;font:600 28px Inter;color:rgba(255,255,255,.7)'>[link sticker goes here]</div>") if s.get('link') else ''
        poll = (f"<div style='position:absolute;left:150px;right:150px;top:{s.get('poll_top', 1260)}px;background:#fff;border-radius:28px;padding:30px;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.35)'>"
                f"<div style='font:700 40px/1.2 Inter;color:#111;margin-bottom:22px'>{esc(s['poll'][0])}</div>"
                + ''.join(f"<div style='font:700 38px Inter;color:#1A5BFF;border:3px solid #E3E7EF;border-radius:18px;padding:16px;margin-top:14px'>{esc(o)}</div>" for o in s['poll'][1:])
                + "</div>") if s.get('poll') else ''
        return (f"<div class='bg' style='background:{s.get('bg', 'linear-gradient(180deg,#0B0F1A,#1A2238)')}'></div>{full}{img}{top}{sub}{poll}{link}"
                f"<div style='position:absolute;left:70px;top:80px;display:flex;gap:16px;align-items:center'><img class='av' src='{U(AV)}' style='width:64px;height:64px'><div style='font:700 30px Inter;color:#fff'>andrewpreneurship</div></div>")
    raise SystemExit('unknown format ' + f)


def render(slides, out, W, H, names=None, quality=86):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); hd = Path('/home/user/work/catalog/_html') / out.name; hd.mkdir(parents=True, exist_ok=True); pairs, files = [], []
    for i, s in enumerate(slides):
        nm = names[i] if names else f'slide-{i + 1:02d}'
        h = hd / f'{nm}.html'; h.write_text(f"<html><head><meta charset='utf-8'><style>{CSS} body{{width:{W}px;height:{H}px}}</style></head><body>{slide_html(s, W, H)}</body></html>")
        p = hd / f'{nm}.png'; pairs.append(f'{h}:{p}'); files.append((p, out / f'{nm}.jpg'))
    subprocess.run(['node', str(ROOT / 'tools/shoot.js'), str(W), str(H), *pairs], check=True, env={**os.environ, 'NODE_PATH': '/opt/node-tools/node_modules'})
    return [to_jpg(p, j, quality) for p, j in files]


def to_jpg(png, jpg, q=86):
    from PIL import Image
    im = Image.open(png).convert('RGB')
    while True:
        im.save(jpg, quality=q, optimize=True, progressive=True)
        if os.path.getsize(jpg) <= 400_000 or q <= 60: break
        q -= 6
    os.remove(png); return str(jpg)
