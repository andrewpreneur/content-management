"""Shared brand look for rendered assets (proposed Nov 4, 2026 — Andrew to confirm; see docs/brand-kit.md).

Imported by reel.py, carousel.py, story.py.
"""
from PIL import Image, ImageDraw, ImageFont

BG = (11, 15, 26)          # #0B0F1A  near-black navy
PANEL = (22, 28, 44)       # #161C2C  card panels
ACCENT = (255, 210, 63)    # #FFD23F  highlight yellow (one or two words per line, never whole sentences)
BLUE = (46, 125, 255)      # #2E7DFF  pills / series tag
WHITE = (255, 255, 255)
MUTED = (160, 170, 190)

FONT_BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
FONT_BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONT_MED = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
FONT_REG = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'

NAME = 'Andrew George'
TAGLINE = 'The One Feature guy'
SERIES = 'ONE FEATURE YOU CAN SELL'


def font(path, size):
    return ImageFont.truetype(path, size)


def rich_lines(draw, text, fnt, max_w):
    """Wrap text where *word* marks accent words. Returns list of lines; each line = list of (word, accent)."""
    out, inacc = [], False  # supports multi-word accents: *two words*
    for raw in text.split():
        start, end = raw.startswith('*'), raw.endswith('*') and len(raw) > 1
        w = raw.replace('*', '')
        if start:
            inacc = True
        out.append((w, inacc))
        if end:
            inacc = False
    words = out
    lines, cur = [], []
    for w in words:
        trial = ' '.join(x[0] for x in cur + [w])
        if cur and draw.textlength(trial, font=fnt) > max_w:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def draw_rich(draw, text, fnt, box_x, y, max_w, align='center', color=WHITE, accent=ACCENT, line_gap=1.12):
    """Draw wrapped rich text; returns bottom y."""
    lines = rich_lines(draw, text, fnt, max_w)
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * line_gap)
    space = draw.textlength(' ', font=fnt)
    for line in lines:
        lw = sum(draw.textlength(w, font=fnt) for w, _ in line) + space * (len(line) - 1)
        x = box_x + (max_w - lw) / 2 if align == 'center' else box_x
        for w, acc in line:
            draw.text((x, y), w, font=fnt, fill=accent if acc else color)
            x += draw.textlength(w, font=fnt) + space
        y += lh
    return y


def pill(draw, text, cx, y, fnt, fill=BLUE, color=WHITE, pad=(28, 14)):
    w = draw.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    h = asc + desc
    x0 = cx - w / 2 - pad[0]
    draw.rounded_rectangle([x0, y, cx + w / 2 + pad[0], y + h + pad[1] * 2], radius=(h + pad[1] * 2) // 2, fill=fill)
    draw.text((cx - w / 2, y + pad[1]), text, font=fnt, fill=color)
    return y + h + pad[1] * 2
