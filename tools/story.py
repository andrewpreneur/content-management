#!/usr/bin/env python3
"""Render Instagram/Facebook Story frames (1080×1920 PNG) from a JSON spec. See docs/stories.md.

Usage: python3 tools/story.py SPEC.json OUT_DIR

SPEC = {"frames": [
  {"role": "hook", "text": "Your 1-page funnel can be a *6-page store* now.",
   "photo": "/path/andrew.jpg",              # full-bleed background (real photo), or
   "shot": "/path/screen.png", "crop": [x0,y0,x1,y1],   # screenshot card on brand background
   "focus": 0.4,                             # vertical focus of the photo crop (0 top … 1 bottom)
   "text_y": 1150,                           # top of the text box (keep 250–1580)
   "sticker": {"type": "poll", "q": "Would your clients buy this?", "options": ["Yes", "Show me how"]},
   "sticker_y": 1000,                        # optional fixed sticker position
   "keyword": "STORE"}                       # big accent keyword line for the CTA frame
]}
Stickers are drawn as dashed placeholders: Andrew drops the real IG sticker on the same spot.
Safe zone: text stays inside x 64–1016, y 250–1580 (IG UI covers the rest).
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance

sys.path.insert(0, str(Path(__file__).parent))
import brand_look as B

W, H = 1080, 1920
SAFE_TOP, SAFE_BOT, SX = 250, 1580, 64


def bg_photo(path, focus=0.4):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    scale = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * focus)
    im = im.crop((x, y, x + W, y + H))
    if scale > 1.2:  # low-res source: soften upscale artefacts a little
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    # bottom-to-top darkening so text reads
    grad = Image.linear_gradient('L').resize((W, H))
    dark = Image.new('RGB', (W, H), (0, 0, 0))
    return Image.composite(dark, im, grad.point(lambda v: int(v * 0.55)))


def text_box(im, text, y, size=64, keyword=None):
    d = ImageDraw.Draw(im, 'RGBA')
    f = B.font(B.FONT_BLACK, size)
    lines = B.rich_lines(d, text, f, W - 2 * SX - 80)
    asc, desc = f.getmetrics(); lh = int((asc + desc) * 1.12)
    h = lh * len(lines) + 70 + (150 if keyword else 0)
    y = min(y, SAFE_BOT - h)
    d.rounded_rectangle([SX, y, W - SX, y + h], radius=34, fill=(0, 0, 0, 205))
    B.draw_rich(d, text, f, SX + 40, y + 35, W - 2 * SX - 80)
    if keyword:
        kf = B.font(B.FONT_BLACK, 120)
        kw = d.textlength(keyword, font=kf)
        d.text(((W - kw) / 2, y + 35 + lh * len(lines) + 5), keyword, font=kf, fill=B.ACCENT)
    return y + h


def dashed_rect(d, box, color=(255, 255, 255, 230), dash=18, width=4, r=28):
    x0, y0, x1, y1 = box
    for x in range(int(x0 + r), int(x1 - r), dash * 2):
        d.line([(x, y0), (min(x + dash, x1 - r), y0)], fill=color, width=width)
        d.line([(x, y1), (min(x + dash, x1 - r), y1)], fill=color, width=width)
    for y in range(int(y0 + r), int(y1 - r), dash * 2):
        d.line([(x0, y), (x0, min(y + dash, y1 - r))], fill=color, width=width)
        d.line([(x1, y), (x1, min(y + dash, y1 - r))], fill=color, width=width)


def sticker(im, s, y):
    d = ImageDraw.Draw(im, 'RGBA')
    f = B.font(B.FONT_BOLD, 40); fs = B.font(B.FONT_MED, 26)
    x0, x1 = 170, W - 170
    if s['type'] == 'poll':
        h = 110 + 95 * len(s['options'])
        d.rounded_rectangle([x0, y, x1, y + h], radius=28, fill=(255, 255, 255, 235))
        d.text((x0 + 36, y + 30), s['q'], font=f, fill=(20, 20, 20))
        for i, o in enumerate(s['options']):
            yy = y + 100 + i * 95
            d.rounded_rectangle([x0 + 30, yy, x1 - 30, yy + 75], radius=37, fill=(238, 238, 242))
            d.text((x0 + 60, yy + 16), o, font=f, fill=(40, 40, 40))
    else:  # question box
        h = 220
        d.rounded_rectangle([x0, y, x1, y + h], radius=28, fill=(255, 255, 255, 235))
        d.text((x0 + 36, y + 34), s['q'], font=f, fill=(20, 20, 20))
        d.rounded_rectangle([x0 + 30, y + 110, x1 - 30, y + 190], radius=20, fill=(238, 238, 242))
        d.text((x0 + 56, y + 132), 'Type something…', font=f, fill=(150, 150, 155))
    dashed_rect(d, [x0 - 14, y - 14, x1 + 14, y + h + 14])
    d.text((x0 - 10, y + h + 22), 'add the real IG sticker here', font=fs, fill=(255, 255, 255, 200))
    return y + h + 60


def render(fr):
    if fr.get('photo'):
        im = bg_photo(fr['photo'], fr.get('focus', 0.4))
    else:
        im = Image.new('RGB', (W, H), B.BG)
    d = ImageDraw.Draw(im, 'RGBA')
    if fr.get('shot'):
        shot = Image.open(fr['shot']).convert('RGB')
        if fr.get('crop'):
            shot = shot.crop(tuple(fr['crop']))
        maxw, maxh = W - 2 * SX, 820
        sc = min(maxw / shot.width, maxh / shot.height)
        shot = shot.resize((int(shot.width * sc), int(shot.height * sc)), Image.LANCZOS)
        x = (W - shot.width) // 2; y = fr.get('shot_y', 330)
        d.rounded_rectangle([x - 8, y - 8, x + shot.width + 8, y + shot.height + 8], radius=30, fill=B.PANEL)
        mask = Image.new('L', shot.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, shot.width - 1, shot.height - 1], radius=24, fill=255)
        im.paste(shot, (x, y), mask)
    # small name tag top (inside safe zone)
    B.pill(d, f"{B.NAME} · {B.TAGLINE}", W // 2, SAFE_TOP + 10, B.font(B.FONT_BOLD, 28), fill=(0, 0, 0, 170))
    y = fr.get('text_y', 1150)
    if fr.get('sticker'):
        bottom = text_box(im, fr['text'], y, keyword=fr.get('keyword'))
        sticker(im, fr['sticker'], fr.get('sticker_y', min(bottom + 40, SAFE_BOT - 330)))
    else:
        text_box(im, fr['text'], y, keyword=fr.get('keyword'))
    return im


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('out')
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for i, fr in enumerate(spec['frames'], 1):
        render(fr).save(out / f"frame-{i:02d}-{fr.get('role', 'frame')}.png", optimize=True)
    print(f"{len(spec['frames'])} frames → {out}")


if __name__ == '__main__':
    main()
