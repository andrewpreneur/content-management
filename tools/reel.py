#!/usr/bin/env python3
"""Cut a 9:16 reel from a long source using an edit list (EDL) + word-level transcript.

Layout (1080×1920): header (series pill + hook / title) on top, screen footage as a 1080×1080
square in the middle, word-by-word captions (active word in accent yellow), CTA card at the end.

Usage:
  python3 tools/reel.py EDL.json OUT.mp4 [--clean] [--lang es --translations es.json] [--srt OUT.srt]

EDL.json:
{
  "source": "/path/source.mp4",          # 16:9 screen recording (any res)
  "transcript": "/path/transcript.json", # from tools/transcribe.py
  "hook": "HighLevel just turned every funnel into a *store*",   # first 3.5s; *word* = accent
  "title": "Stores inside *funnels*",    # header after the hook
  "cta": "Comment *STORE* and I'll send you the setup",          # last 4s
  "series": "ONE FEATURE YOU CAN SELL",  # optional pill text (translate for language pages)
  "segments": [ {"a": [0.0, 13.05], "v": null, "cx": 0.35, "cy": 0.5, "zoom": 1.0, "layout": "screen"}, ... ],
  # optional camera (talking head) on the same timeline as the screen recording:
  "cam": "/path/camera.mp4", "cam_offset": 0, "fcx": 0.45, "fcy": 0.4, "fzoom": 1.0, "audio": "/path/camera.mp4"
}
  layout = screen (square screen crop) | split (screen 1080×720 over face 1080×680) | face (face 1080×1400 under the header)
  a    = audio (spoken) range in source seconds; the cut follows the voice
  v    = optional different start time for the picture (b-roll from elsewhere in the source)
  cx/cy= screen crop centre (fractions); fcx/fcy/fzoom = face crop (per segment or EDL-wide)
--clean   no captions/hook/CTA (base for tools/variants.py Trial Reels, which add their own)
--translations  JSON {"<transcript segment start>": "translated text"}; words spread evenly over each line
"""
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import brand_look as B

W, H, VID_Y, VID = 1080, 1920, 520, 1080
FIXES = [(r'(?i)^high-?level', 'HighLevel'), (r'(?i)^e-?comm$', 'e-comm'), (r'^gonna$', 'going to')]


def probe(src):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                        '-of', 'csv=p=0', src], capture_output=True, text=True, check=True).stdout.strip()
    w, h = o.split(',')
    return int(w), int(h)


def merged_words(transcript):
    """Flatten words, merge whisper fragments ('e' + '-commerce'), apply brand spelling fixes."""
    out = []
    for seg in transcript['segments']:
        for w in seg['words']:
            if out and w['w'].startswith('-'):
                out[-1]['w'] += w['w']; out[-1]['e'] = w['e']
            else:
                out.append(dict(w, seg=seg['start']))
    for w in out:
        core = w['w'].strip('.,!?')
        for pat, rep in FIXES:
            core = re.sub(pat, rep, core)
        w['cap'] = core
    return out


def retime(words, segs):
    res, off = [], 0.0
    for s in segs:
        a0, a1 = s['a']
        for w in words:
            if a0 - 0.05 <= w['s'] < a1:
                res.append({'cap': w['cap'], 's': off + max(0, w['s'] - a0), 'e': off + min(a1, w['e']) - a0, 'seg': w['seg']})
        off += a1 - a0
    return res, off


def translated_words(words_rt, translations):
    """Replace English words with translated ones, spread evenly across each original line's span."""
    out, groups = [], {}
    for w in words_rt:
        groups.setdefault(w['seg'], []).append(w)
    for seg, ws in groups.items():
        tr = translations.get(f"{seg}") or translations.get(f"{seg:.2f}") or translations.get(str(seg))
        if not tr:
            continue
        tw = tr.split()
        # only the share of the line that is inside the cut
        span0, span1 = ws[0]['s'], ws[-1]['e']
        step = (span1 - span0) / max(1, len(tw))
        for i, t in enumerate(tw):
            out.append({'cap': t.strip('.,!?¿¡'), 's': span0 + i * step, 'e': span0 + (i + 1) * step})
    return sorted(out, key=lambda w: w['s'])


def chunks(words, max_words=3, max_gap=0.35):
    cur = []
    for w in words:
        if cur and (len(cur) >= max_words or w['s'] - cur[-1]['e'] > max_gap):
            yield cur; cur = []
        cur.append(w)
    if cur:
        yield cur


def ass_time(t):
    h, r = divmod(max(0, t), 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def box(sw, sh, aspect, zoom, cx, cy):
    """Largest crop of the given aspect (w/h) inside sw×sh, shrunk by zoom, centred at (cx, cy) fractions."""
    h = sh if sw / sh >= aspect else sw / aspect
    h = h / zoom; w = h * aspect
    w, h = int(w) // 2 * 2, int(h) // 2 * 2
    x = int(min(max(0, cx * sw - w / 2), sw - w)); y = int(min(max(0, cy * sh - h / 2), sh - h))
    return w, h, x, y


LOOK = {'name': 'house'}   # set from the EDL: "look": "ig" (Instagram basic) or "house" (default)


def write_ass(words, path, y_at=lambda t: 1440):
    if LOOK['name'] == 'ig':
        from house_captions import ig_captions_ass
        Path(path).write_text(ig_captions_ass([{'w': w['cap'], 't0': w['s'], 't1': w['e']} for w in words], W, H)); return
    """Captions in THE house look (tools/house_captions.py): white Inter Display, soft shadow, no box, the spoken word
    violet, sentence case. The old yellow-on-navy "v0" look is retired; it only comes back with REEL_LOOK=v0."""
    if os.environ.get('REEL_LOOK') == 'v0':
        return write_ass_v0(words, path, y_at)
    from house_captions import captions_ass, words_to_phrases
    ws = [{'w': w['cap'], 't0': w['s'], 't1': w['e']} for w in words]
    Path(path).write_text(captions_ass(words_to_phrases(ws), W, H, out_y_frac=0.80))


def write_ass_v0(words, path, y_at=lambda t: 1440):
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,74,&H00FFFFFF,&H00FFFFFF,&H30000000,&H30000000,-1,0,0,0,100,100,0,0,3,14,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    acc = '&H003FD2FF&'  # BGR of #FFD23F
    for ch in chunks(words):
        for i, w in enumerate(ch):
            st = w['s']; en = ch[i + 1]['s'] if i + 1 < len(ch) else w['e'] + 0.15
            parts = [(f"{{\\c{acc}}}{x['cap'].upper()}{{\\c&H00FFFFFF&}}" if j == i else x['cap'].upper()) for j, x in enumerate(ch)]
            ev.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{{\\pos({W//2},{y_at(st)})}}{' '.join(parts)}")
    Path(path).write_text(hdr + '\n'.join(ev) + '\n')


def write_srt(words, path):
    def t(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    lines = []
    for i, ch in enumerate(chunks(words, max_words=6), 1):
        lines.append(f"{i}\n{t(ch[0]['s'])} --> {t(ch[-1]['e'])}\n{' '.join(w['cap'] for w in ch)}\n")
    Path(path).write_text('\n'.join(lines))


HOUSE_ACCENT = (255, 255, 255)   # white: Andrew wants clean white text only (no violet/yellow accent words)


def overlay_png(path, *, hook=None, title=None, cta=None, series=B.SERIES):
    if LOOK['name'] == 'ig':
        return overlay_png_ig(path, LOOK.get('headline') or hook or title or '')
    if os.environ.get('REEL_LOOK') != 'v0':
        return overlay_png_house(path, hook=hook, title=title, cta=cta)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if hook or title:  # translucent band so the header reads over a face shot too (invisible on the brand background)
        band = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(band).rectangle([0, 200, W, VID_Y], fill=B.BG + (170,))
        im.alpha_composite(band)
    y = B.pill(d, series, W // 2, 250, B.font(B.FONT_BOLD, 30))
    if hook:
        B.draw_rich(d, hook, B.font(B.FONT_BLACK, 70), 60, y + 30, W - 120)
    if cta:  # CTA replaces the title in the header so it never collides with captions
        d.rounded_rectangle([50, y + 20, W - 50, VID_Y - 12], radius=32, fill=B.ACCENT)
        B.draw_rich(d, cta, B.font(B.FONT_BLACK, 56), 90, y + 42, W - 180, color=B.BG, accent=B.BLUE)
    elif title:
        B.draw_rich(d, title, B.font(B.FONT_BLACK, 62), 60, y + 50, W - 120)
    im.save(path)


def overlay_png_ig(path, headline):
    """"Instagram basic" headline (Andrew's Nov 25 reference): ONE headline for the whole video, black condensed text on a
    white rounded card near the top. Emoji are dropped (fonts can't draw them reliably)."""
    fd = Path(__file__).resolve().parent / 'fonts'
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    text = re.sub(r'[*\[\]]', '', headline).strip()
    text = ''.join(ch for ch in text if ord(ch) < 0x2190).strip()
    if not text:
        im.save(path); return
    size = 96
    while True:
        f = ImageFont.truetype(str(fd / 'BarlowCondensed-Medium.ttf'), size)
        words, lines, cur = text.split(), [], ''
        for w in words:   # wrap to the card width, at most 2 lines
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=f) <= W * 0.72 or not cur: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 2 or size <= 64: break
        size -= 6
    asc, desc = f.getmetrics(); lh = asc + desc
    tw = max(d.textlength(l, font=f) for l in lines)
    pw, ph = round(W * 0.04), round(lh * 0.32)
    bw, bh = tw + pw * 2, lh * len(lines) + ph * 2
    x0, y0 = (W - bw) / 2, round(H * 0.155)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=round(W * 0.03), fill=(255, 255, 255, 255))
    for i, l in enumerate(lines):
        d.text(((W - d.textlength(l, font=f)) / 2, y0 + ph + i * lh - round(desc * 0.25)), l, font=f, fill=(12, 12, 14, 255))
    im.save(path)


def overlay_png_house(path, *, hook=None, title=None, cta=None):
    """Header in the house look: clean white Inter Display with a soft shadow straight on the video. No colour, no pills,
    no bands, no series pill."""
    from PIL import ImageFilter
    fd = Path(__file__).resolve().parent / 'fonts'
    big = lambda n: ImageFont.truetype(str(fd / 'InterDisplay-Bold.ttf'), n)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    text = cta or hook or title
    if not text:
        im.save(path); return
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    B.draw_rich(sd, text, big(76 if not cta else 64), 70, 250, W - 140, color=(0, 0, 0, 150), accent=(0, 0, 0, 150))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
    y = B.draw_rich(d, text, big(76 if not cta else 64), 70, 246, W - 140, color=(255, 255, 255), accent=HOUSE_ACCENT)
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('edl'); ap.add_argument('out')
    ap.add_argument('--clean', action='store_true')
    ap.add_argument('--translations'); ap.add_argument('--srt')
    a = ap.parse_args()
    edl = json.loads(Path(a.edl).read_text())
    LOOK['name'] = edl.get('look', 'house'); LOOK['headline'] = edl.get('headline') or edl.get('hook')
    src, segs = edl['source'], edl['segments']
    sw, sh = probe(src)
    words = merged_words(json.loads(Path(edl['transcript']).read_text()))
    wrt, total = retime(words, segs)
    if a.translations:
        wrt = translated_words(wrt, json.loads(Path(a.translations).read_text()))

    cam = edl.get('cam'); cw, ch = probe(cam) if cam else (0, 0)
    audio_src = edl.get('audio', cam or src)
    bgc = '0x%02X%02X%02X' % B.BG
    seg_spans, off = [], 0.0
    for s in segs:
        seg_spans.append((off, off + s['a'][1] - s['a'][0], s.get('layout', 'screen'))); off += s['a'][1] - s['a'][0]
    cap_y = {'screen': 1440, 'split': 1240, 'face': 1360}

    def y_at(t):
        for t0, t1, lay in seg_spans:
            if t0 <= t < t1:
                return cap_y[lay]
        return cap_y[seg_spans[-1][2]]

    with tempfile.TemporaryDirectory() as td:
        inputs, fc, cat = [], [], ''

        def add_input(start, dur, path):
            inputs.extend(['-ss', f'{start}', '-t', f'{dur}', '-i', path])
            return len(inputs) // 6 - 1

        for i, s in enumerate(segs):
            a0, a1 = s['a']; dur = a1 - a0; v0 = s.get('v') if s.get('v') is not None else a0
            lay = s.get('layout', 'screen')
            tail = f"fps=30,setsar=1,trim=duration={dur},setpts=PTS-STARTPTS"
            if lay in ('screen', 'split'):
                si = add_input(v0, dur, src)
                asp = 1.0 if lay == 'screen' else 1.5
                w, h, x, y = box(sw, sh, asp, s.get('zoom', 1.0), s.get('cx', 0.5), s.get('cy', 0.5))
                ow, oh = (VID, VID) if lay == 'screen' else (W, 720)
                fc.append(f"[{si}:v]crop={w}:{h}:{x}:{y},scale={ow}:{oh}:flags=lanczos,{tail}[s{i}]")
            if lay in ('split', 'face', 'full'):
                ci = add_input(v0 + edl.get('cam_offset', 0), dur, cam)
                asp = W / 680 if lay == 'split' else W / H if lay == 'full' else W / (H - VID_Y)
                w, h, x, y = box(cw, ch, asp, s.get('fzoom', edl.get('fzoom', 1.0)), s.get('fcx', edl.get('fcx', 0.5)), s.get('fcy', edl.get('fcy', 0.5)))
                ow, oh = (W, 680) if lay == 'split' else (W, H) if lay == 'full' else (W, H - VID_Y)
                fc.append(f"[{ci}:v]crop={w}:{h}:{x}:{y},scale={ow}:{oh}:flags=lanczos,{tail}[c{i}]")
            if lay == 'screen':
                fc.append(f"[s{i}]pad={W}:{H}:0:{VID_Y}:color={bgc}[v{i}]")
            elif lay == 'split':
                fc.append(f"[s{i}]pad={W}:1240:0:{VID_Y}:color={bgc}[t{i}];[t{i}][c{i}]vstack[v{i}]")
            elif lay == 'full':   # vertical talking head (ads, speaker reels): the face fills the frame, no bands
                fc.append(f"[c{i}]null[v{i}]")
            else:
                fc.append(f"[c{i}]pad={W}:{H}:0:{VID_Y}:color={bgc}[v{i}]")  # face sits under the header
            ai = add_input(a0, dur, audio_src)
            fc.append(f"[{ai}:a]aresample=48000,atrim=duration={dur},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={max(0,dur-0.05)}:d=0.05[a{i}]")
            cat += f"[v{i}][a{i}]"
        fc.append(f"{cat}concat=n={len(segs)}:v=1:a=1[vc][ac]")
        n = len(inputs) // 6
        hook_png, title_png, cta_png = (os.path.join(td, f) for f in ('hook.png', 'title.png', 'cta.png'))
        if a.clean:
            fc.append("[vc]null[vo]")  # no header: variants.py draws its own hook at the top
        else:
            ser = edl.get('series', B.SERIES)
            overlay_png(hook_png, hook=edl['hook'], series=ser); overlay_png(title_png, title=edl.get('title', edl['hook']), series=ser)
            overlay_png(cta_png, cta=edl['cta'], series=ser)
            ass = os.path.join(td, 'cap.ass'); write_ass(wrt, ass, y_at)
            inputs += ['-loop', '1', '-t', f'{total}', '-i', hook_png, '-loop', '1', '-t', f'{total}', '-i', title_png,
                       '-loop', '1', '-t', f'{total}', '-i', cta_png]
            cta_t = max(3.5, total - 4)
            fc.append(f"[vc][{n}:v]overlay=0:0:enable='lt(t,3.5)'[b2];[b2][{n+1}:v]overlay=0:0:enable='between(t,3.5,{cta_t})'[b3];"
                      f"[b3][{n+2}:v]overlay=0:0:enable='gte(t,{cta_t})'[b4];[b4]subtitles={ass}[vo]")
        fc.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ao]")
        cmd = ['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '[vo]', '-map', '[ao]',
               '-t', f'{total}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p',
               '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', a.out]
        subprocess.run(cmd, check=True)
    if a.srt:
        write_srt(wrt, a.srt)
    print(f"{a.out}  {total:.1f}s")


if __name__ == '__main__':
    main()
