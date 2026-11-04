#!/usr/bin/env python3
"""Render a carousel (1080×1350 PNG slides) from a JSON spec.

Usage: python3 tools/carousel.py SPEC.json OUT_DIR [--pdf]

SPEC = {"handle": "Andrew George · The One Feature guy",
        "slides": [ {"kicker": "STEP 1", "title": "Add a *store* element", "body": "Short line.",
                     "image": "/path/shot.png", "crop": [x0, y0, x1, y1],   # px in the image, optional
                     "bullets": ["a", "b"], "big": false, "photo_bg": "/path/photo.jpg"} ]}
*word* = accent colour. "big": true = hook/CTA slide (huge title, no image).
--pdf also writes carousel.pdf (LinkedIn document post).
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
import brand_look as B

W, H, M = 1080, 1350, 72


def fit_image(path, crop, box_w, box_h):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    if crop:
        im = im.crop(tuple(crop))
    scale = min(box_w / im.width, box_h / im.height)
    if scale != 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    return im


def cover(path, w, h):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    return ImageOps.fit(im, (w, h), Image.LANCZOS)


def render(slide, idx, total, handle):
    if slide.get('photo_bg'):
        im = cover(slide['photo_bg'], W, H)
        shade = Image.new('RGB', (W, H), B.BG)
        im = Image.blend(im, shade, 0.78)
    else:
        im = Image.new('RGB', (W, H), B.BG)
    d = ImageDraw.Draw(im)
    y = M + 10
    if slide.get('kicker'):
        y = B.pill(d, slide['kicker'], M + d.textlength(slide['kicker'], font=B.font(B.FONT_BOLD, 30)) / 2 + 28, y,
                   B.font(B.FONT_BOLD, 30)) + 34
    big = slide.get('big')
    tf = B.font(B.FONT_BLACK, 104 if big else 68)
    if big:
        y = max(y, 300)
    y = B.draw_rich(d, slide['title'], tf, M, y, W - 2 * M, align='left') + 18
    if slide.get('body'):
        y = B.draw_rich(d, slide['body'], B.font(B.FONT_MED, 40 if not big else 46), M, y, W - 2 * M,
                        align='left', color=B.MUTED if not big else B.WHITE) + 24
    for b in slide.get('bullets', []):
        d.ellipse([M, y + 18, M + 16, y + 34], fill=B.ACCENT)
        y = B.draw_rich(d, b, B.font(B.FONT_BOLD, 44), M + 40, y, W - 2 * M - 40, align='left') + 10
    if slide.get('image'):
        box_top = y + 16
        box_h = H - box_top - 130
        if box_h > 200:
            pic = fit_image(slide['image'], slide.get('crop'), W - 2 * M, box_h)
            x = (W - pic.width) // 2
            mask = Image.new('L', pic.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, pic.width - 1, pic.height - 1], radius=24, fill=255)
            d.rounded_rectangle([x - 6, box_top - 6, x + pic.width + 6, box_top + pic.height + 6], radius=28, fill=B.PANEL)
            im.paste(pic, (x, box_top), mask)
    # footer
    ff = B.font(B.FONT_BOLD, 28)
    d.text((M, H - 80), handle, font=ff, fill=B.MUTED)
    pg = f"{idx}/{total}" + ("  →" if idx < total else "")
    d.text((W - M - d.textlength(pg, font=ff), H - 80), pg, font=ff, fill=B.ACCENT if idx < total else B.MUTED)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec'); ap.add_argument('out'); ap.add_argument('--pdf', action='store_true')
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    slides = spec['slides']; ims = []
    for i, s in enumerate(slides, 1):
        im = render(s, i, len(slides), spec.get('handle', f"{B.NAME} · {B.TAGLINE}"))
        im.save(out / f"slide-{i:02d}.png", optimize=True); ims.append(im)
    if a.pdf:
        ims[0].save(out / 'carousel.pdf', save_all=True, append_images=ims[1:], resolution=150)
    print(f"{len(slides)} slides → {out}")


if __name__ == '__main__':
    main()
