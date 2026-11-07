#!/usr/bin/env python3
"""Cut standalone testimonial ads from long raw client testimonials (Nov 7, 2026, testimonials-a worker).

Each ad = real client footage (never AI), cut from word-timed transcript ranges, with:
hook (quote / headline / question / stat / pre-roll text card), animated word captions (active word yellow),
name + business lower third, light punch-ins, low music bed ducked under speech, end card with CTA.
Audio: voice gain-matched, music ducked, integrated loudness -14 LUFS, limiter (true peak ~ -1.5 dBFS).

Usage:
  python3 tools/testimonial_ads.py SPECS.json OUT_DIR [--only id1,id2] [--aspect 916|45] [--jobs 3]
SPECS.json: {"people": {...}, "music": [...], "ads": [{"id", "person", "segs": [[a0,a1],...], "hook": {...},
             "topline": "...", "aspect": ["916","45"]}, ...]}
"""
import argparse, json, os, re, subprocess, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import brand_look as B

FPS = 30
END = 2.8          # end card seconds
HOOK = 3.0         # hook overlay seconds (after any pre-roll card)
PRE_CARD = 1.3     # pre-roll text card seconds (hook type "card")
ZOOM = 1.12
ROOT = Path(__file__).resolve().parent.parent
PFP = ROOT / 'research/brand/pfp_andrew.png'


def F(path, size):
    return _font(path, size)


@lru_cache(None)
def _font(path, size):
    return ImageFont.truetype(path, size)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(' '.join(map(str, cmd))[:400] + '\n' + r.stderr[-1500:])
    return r


# ---------------------------------------------------------------- words / captions
FIXES = {'gonna': 'going to'}


def load_words(tx_path):
    d = json.load(open(tx_path))
    out = []
    for s in d['segments']:
        for w in s['words']:
            t = w['w'].strip()
            if out and t.startswith('-'):
                out[-1]['w'] += t; out[-1]['e'] = w['e']; continue
            out.append({'w': t, 's': w['s'], 'e': w['e']})
    # GoHighLevel / HighLevel
    i, res = 0, []
    while i < len(out):
        w = out[i]; lw = [x['w'].lower().strip('.,!?') for x in out[i:i + 3]]
        if lw[:3] == ['go', 'high', 'level']:
            res.append({'w': 'GoHighLevel' + out[i + 2]['w'][5:], 's': w['s'], 'e': out[i + 2]['e']}); i += 3; continue
        if lw[:2] == ['high', 'level']:
            res.append({'w': 'HighLevel' + out[i + 1]['w'][5:], 's': w['s'], 'e': out[i + 1]['e']}); i += 2; continue
        if lw[:2] in (['sassweet', '.ai'], ['saas', 'suite']):   # whisper splits the product name
            res.append({'w': 'SaaSSuite' + re.sub(r'^\.?\w+', '', out[i + 1]['w']), 's': w['s'], 'e': out[i + 1]['e']}); i += 2; continue
        res.append(w); i += 1
    return res


def retime(words, segs, offset):
    res, off = [], offset
    for a0, a1 in segs:
        for w in words:
            mid = (w['s'] + w['e']) / 2
            if a0 - 0.02 <= mid < a1:
                res.append({'w': w['w'], 's': off + max(0, w['s'] - a0), 'e': off + min(a1, w['e']) - a0})
        off += a1 - a0
    return res


def chunks(words, max_words=3, max_chars=18):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        txt = ' '.join(x['w'] for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = (len(cur) >= max_words or len(txt) >= max_chars or re.search(r'[.,!?]$', w['w'])
               or (nxt and nxt['s'] - w['e'] > 0.3) or nxt is None)
        if brk:
            out.append(cur); cur = []
    res = []
    for i, c in enumerate(out):
        s, e = c[0]['s'], c[-1]['e']
        if i + 1 < len(out) and out[i + 1][0]['s'] - e < 0.5:
            e = out[i + 1][0]['s']
        else:
            e += 0.25
        res.append({'s': s, 'e': e, 'words': c})
    return res


def clean_word(w):
    w = FIXES.get(w.lower(), w)
    return w.strip(',.;:').upper() if w not in ('...',) else w


# ---------------------------------------------------------------- overlay drawing
def stroke_text(d, xy, text, fnt, fill, sw=6):
    d.text(xy, text, font=fnt, fill=fill, stroke_width=sw, stroke_fill=(0, 0, 0))


@lru_cache(4096)
def caption_img(words_key, active, scale_step, width):
    """words_key: tuple of words; active: index; scale_step 0..3 pop animation."""
    size = 84 if width >= 1080 else 70
    size = int(size * (0.86, 0.93, 0.98, 1.0)[scale_step])
    fnt = F(B.FONT_BLACK, size)
    words = [clean_word(w) for w in words_key]
    tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    space = tmp.textlength(' ', font=fnt)
    # wrap into max 2 lines of 940px
    lines, cur = [], []
    for i, w in enumerate(words):
        trial = ' '.join(words[j] for j in cur + [i])
        if cur and tmp.textlength(trial, font=fnt) > 940:
            lines.append(cur); cur = [i]
        else:
            cur.append(i)
    lines.append(cur)
    asc, desc = fnt.getmetrics(); lh = int((asc + desc) * 1.05)
    H = lh * len(lines) + 30
    im = Image.new('RGBA', (width, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 12
    for ln in lines:
        lw = sum(tmp.textlength(words[i], font=fnt) for i in ln) + space * (len(ln) - 1)
        x = (width - lw) / 2
        for i in ln:
            stroke_text(d, (x, y), words[i], fnt, B.ACCENT if i == active else B.WHITE, sw=7)
            x += tmp.textlength(words[i], font=fnt) + space
        y += lh
    return im


def rich_wrap(d, text, fnt, max_w):
    return B.rich_lines(d, text, fnt, max_w)


def draw_rich_block(text, fnt, max_w, color, accent, line_gap=1.08, align='center'):
    tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    lines = rich_wrap(tmp, text, fnt, max_w)
    asc, desc = fnt.getmetrics(); lh = int((asc + desc) * line_gap)
    im = Image.new('RGBA', (max_w, lh * len(lines) + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    space = tmp.textlength(' ', font=fnt); y = 0
    for line in lines:
        lw = sum(tmp.textlength(w, font=fnt) for w, _ in line) + space * (len(line) - 1)
        x = (max_w - lw) / 2 if align == 'center' else 0
        for w, acc in line:
            d.text((x, y), w, font=fnt, fill=accent if acc else color)
            x += tmp.textlength(w, font=fnt) + space
        y += lh
    return im


@lru_cache(64)
def hook_img(kind, text, sub, width):
    """Returns RGBA hook block (to be placed at top). kind: quote|headline|question|stat|card-top"""
    if kind == 'headline':
        blk = draw_rich_block(text, F(B.FONT_BLACK, 70), 900, (0, 0, 0), (20, 70, 200))
        im = Image.new('RGBA', (width, blk.height + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([(width - 980) // 2, 0, (width + 980) // 2, blk.height + 56], 28, fill=B.ACCENT + (255,))
        im.alpha_composite(blk, ((width - 900) // 2, 30)); return im
    if kind == 'question':
        blk = draw_rich_block(text, F(B.FONT_BLACK, 68), 880, (12, 12, 12), (220, 40, 40))
        im = Image.new('RGBA', (width, blk.height + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([(width - 960) // 2, 0, (width + 960) // 2, blk.height + 56], 28, fill=(255, 255, 255, 255))
        im.alpha_composite(blk, ((width - 880) // 2, 30)); return im
    if kind == 'quote':
        blk = draw_rich_block(text, F(B.FONT_BLACK, 66), 880, B.WHITE, B.ACCENT)
        im = Image.new('RGBA', (width, blk.height + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([(width - 980) // 2, 0, (width + 980) // 2, blk.height + 100], 30, fill=(11, 15, 26, 215))
        d.text(((width - 980) // 2 + 30, -40), '“', font=F(B.FONT_BLACK, 170), fill=B.ACCENT)
        im.alpha_composite(blk, ((width - 880) // 2, 64)); return im
    if kind == 'stat':
        big = F(B.FONT_BLACK, 230 if len(text) <= 4 else 170)
        tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
        bw = tmp.textlength(text, font=big); asc, desc = big.getmetrics()
        lab = draw_rich_block(sub or '', F(B.FONT_BLACK, 62), 900, B.WHITE, B.ACCENT)
        H = asc + desc + lab.height + 40
        im = Image.new('RGBA', (width, H + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([(width - 980) // 2, 0, (width + 980) // 2, H + 20], 30, fill=(11, 15, 26, 215))
        stroke_text(d, ((width - bw) / 2, -10), text, big, B.ACCENT, sw=0)
        im.alpha_composite(lab, ((width - 900) // 2, asc + desc - 10)); return im
    if kind == 'topline':
        tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
        sz = 40
        while sz > 24 and tmp.textlength(text, font=F(B.FONT_BLACK, sz)) > width - 160:
            sz -= 2
        fnt = F(B.FONT_BLACK, sz); tw = tmp.textlength(text, font=fnt)
        im = Image.new('RGBA', (width, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        x0 = (width - tw) / 2 - 30
        d.rounded_rectangle([x0, 0, x0 + tw + 60, 80], 40, fill=(11, 15, 26, 205))
        d.text((x0 + 30, 40 - sz * 0.6), text, font=fnt, fill=B.WHITE)
        return im
    raise ValueError(kind)


@lru_cache(8)
def lower_third(name, role, width):
    nf, rf = F(B.FONT_BLACK, 50), F(B.FONT_MED, 34)
    tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    w = int(max(tmp.textlength(name, font=nf), tmp.textlength(role, font=rf))) + 90
    im = Image.new('RGBA', (w, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, 140], 22, fill=(11, 15, 26, 230))
    d.rectangle([0, 0, 14, 140], fill=B.ACCENT)
    d.text((44, 18), name, font=nf, fill=B.WHITE)
    d.text((44, 84), role, font=rf, fill=B.ACCENT)
    return im


@lru_cache(4)
def pfp_circle(size):
    im = Image.open(PFP).convert('RGB').resize((size, size), Image.LANCZOS)
    m = Image.new('L', (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    im = im.convert('RGBA'); im.putalpha(m); return im


def end_card(bg_frame, first, cta, W, H):
    bg = bg_frame.filter(ImageFilter.GaussianBlur(28)).convert('RGBA')
    bg.alpha_composite(Image.new('RGBA', (W, H), (11, 15, 26, 190)))
    d = ImageDraw.Draw(bg)
    cy = H // 2 - (330 if H > 1500 else 250)
    p = pfp_circle(260 if H > 1500 else 210)
    d.ellipse([W // 2 - p.width // 2 - 8, cy - 8, W // 2 + p.width // 2 + 8, cy + p.width + 8], fill=B.ACCENT)
    bg.alpha_composite(p, (W // 2 - p.width // 2, cy))
    y = cy + p.width + 50
    blk = draw_rich_block(f'Want results like *{first}?*', F(B.FONT_BLACK, 80), 940, B.WHITE, B.ACCENT)
    bg.alpha_composite(blk, ((W - 940) // 2, y)); y += blk.height + 30
    bf = F(B.FONT_BLACK, 52); tw = d.textlength(cta, font=bf)
    d.rounded_rectangle([(W - tw) / 2 - 50, y, (W + tw) / 2 + 50, y + 120], 60, fill=B.ACCENT)
    d.text(((W - tw) / 2, y + 30), cta, font=bf, fill=(0, 0, 0))
    y += 170
    sf = F(B.FONT_BOLD, 38); s = 'Andrew George  ·  Andrewpreneurship'
    d.text(((W - d.textlength(s, font=sf)) / 2, y), s, font=sf, fill=B.MUTED)
    return bg.convert('RGB')


def card_frame(bg_frame, text, W, H):
    bg = bg_frame.filter(ImageFilter.GaussianBlur(24)).convert('RGBA')
    bg.alpha_composite(Image.new('RGBA', (W, H), (11, 15, 26, 205)))
    blk = draw_rich_block(text, F(B.FONT_BLACK, 96), 960, B.WHITE, B.ACCENT, line_gap=1.1)
    bg.alpha_composite(blk, ((W - 960) // 2, (H - blk.height) // 2))
    d = ImageDraw.Draw(bg); f = F(B.FONT_BLACK, 34); t = 'REAL CLIENT  ·  REAL FOOTAGE'
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([(W - tw) / 2 - 28, (H - blk.height) // 2 - 120, (W + tw) / 2 + 28, (H - blk.height) // 2 - 50], 35, fill=B.BLUE)
    d.text(((W - tw) / 2, (H - blk.height) // 2 - 110), t, font=f, fill=B.WHITE)
    return bg.convert('RGB')


# ---------------------------------------------------------------- plates (ffmpeg)
def person_crop(P, aspect):
    x, y, w, h = P['crop']
    if aspect == '45':
        h2 = int(w * 1.25 / 2) * 2
        fy = P.get('face', [0.5, 0.4])[1]
        y2 = int(min(max(fy * h - 0.42 * h2, 0), h - h2))
        return x, y + y2, w, h2
    return x, y, w, h


def geo_for(P, aspect, W, H):
    if P.get('layout') == 'call':
        cx, cy, cw, ch = P['screen']
        return f'crop={cw}:{ch}:{cx}:{cy},scale=-2:{H},crop={W}:{H},boxblur=24:2,eq=brightness=-0.18:saturation=0.7'
    x, y, w, h = person_crop(P, aspect)
    return f'crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos'


def build_plate(P, segs, aspect, pre, W, H, out_v, out_a, tmp, seg_people=None):
    seg_people = seg_people or [P] * len(segs)
    vf, af, n = [], [], len(segs)
    for i, (a0, a1) in enumerate(segs):
        geo = geo_for(seg_people[i], aspect, W, H)
        vf.append(f'[{i}:v]trim=duration={a1 - a0:.3f},setpts=PTS-STARTPTS,fps={FPS},{geo},setsar=1[v{i}]')
        af.append(f'[{i}:a]atrim=duration={a1 - a0:.3f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=mono,'
                  f'afade=t=in:d=0.015,areverse,afade=t=in:d=0.02,areverse[a{i}]')
    vc = ''.join(f'[v{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0,tpad=start_mode=clone:start_duration={pre}:stop_mode=clone:stop_duration={END}[vo]'
    ac = ''.join(f'[a{i}]' for i in range(n)) + f'concat=n={n}:v=0:a=1,adelay={int(pre * 1000)},apad=pad_dur={END + 0.5}[ao]'
    fc = ';'.join(vf + af + [vc, ac])
    total = pre + sum(b - a for a, b in segs) + END
    ins = []
    for (a0, a1), sp in zip(segs, seg_people):
        ins += ['-ss', f'{a0:.3f}', '-t', f'{a1 - a0 + 0.2:.3f}', '-i', sp['src']]
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[vo]', '-c:v', 'libx264', '-preset',
         'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-t', f'{total:.3f}', out_v,
         '-map', '[ao]', '-t', f'{total:.3f}', '-c:a', 'pcm_s16le', out_a])
    return total


# ---------------------------------------------------------------- audio
def movavg(x, k):
    c = np.cumsum(np.concatenate([np.zeros(k // 2 + 1), x, np.zeros(k)]))
    return (c[k:k + len(x)] - c[:len(x)]) / k


def mix_audio(voice_wav, music, music_off, out_wav, total, pre):
    import soundfile as sf, pyloudnorm as pyln
    v, sr = sf.read(voice_wav)
    if v.ndim > 1: v = v.mean(1)
    n = int(total * sr); v = np.pad(v, (0, max(0, n - len(v))))[:n]
    meter = pyln.Meter(sr)
    lv = meter.integrated_loudness(v[int(pre * sr):int((total - END) * sr)])
    v = v * 10 ** ((-16 - lv) / 20)
    with tempfile.NamedTemporaryFile(suffix='.wav') as t:
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(music_off), '-stream_loop', '-1', '-i', music, '-t', f'{total + 1:.2f}',
             '-ac', '1', '-ar', str(sr), t.name])
        m, _ = sf.read(t.name)
    m = np.pad(m, (0, max(0, n - len(m))))[:n]
    lm = meter.integrated_loudness(m)
    m = m * 10 ** ((-34 - lm) / 20)        # bed ~18 LU under the voice
    # ducking envelope from voice energy (20 ms windows, smoothed)
    hop = int(0.02 * sr); e = np.sqrt(movavg(v ** 2, hop))
    speech = (e > 10 ** (-42 / 20)).astype(float)
    k = int(0.35 * sr); speech = movavg(speech, k).clip(0, 1)
    gain = 1.0 - 0.45 * speech             # extra -5 dB while talking
    t = np.arange(n) / sr
    gain = gain * np.where(t >= total - END - 0.3, 10 ** (8 / 20), 1.0)  # music up under the end card
    gain = gain * np.where(t < pre, 10 ** (8 / 20), 1.0)                 # and under a pre-roll card
    fade = np.clip((total - t) / 0.8, 0, 1)
    mix = v + m * gain * fade
    lmix = meter.integrated_loudness(mix)
    mix = mix * 10 ** ((-14 - lmix) / 20)
    st = np.stack([mix, mix], 1)
    for _ in range(4):   # limiter, then re-measure the stereo result and correct the gain (ends ~ -14 LUFS, TP < -1)
        sf.write(out_wav + '.pre.wav', st.astype(np.float32), sr, subtype='FLOAT')
        run(['ffmpeg', '-v', 'error', '-y', '-i', out_wav + '.pre.wav', '-af',
             'alimiter=limit=0.80:attack=2:release=50:level=disabled:asc=0', '-ar', '48000', '-c:a', 'pcm_f32le', out_wav])
        o, _ = sf.read(out_wav)
        lo = meter.integrated_loudness(o)
        if abs(lo + 14) < 0.3: break
        st = st * 10 ** ((-14 - lo) / 20)
    os.remove(out_wav + '.pre.wav')


# ---------------------------------------------------------------- per-frame compositing
def shots(segs, words_rt, pre, total):
    """punch-in timeline: list of (t0, zoom). New zoom at each cut and every ~4 s at a word gap."""
    marks, off = [(0.0, 1.0)], pre
    z = 1.0
    for i, (a0, a1) in enumerate(segs):
        if i:
            z = ZOOM if z == 1.0 else 1.0; marks.append((off, z))
        d = a1 - a0; last = off
        gaps = [w['s'] for w in words_rt if off + 0.5 < w['s'] < off + d - 1.2]
        for g in gaps:
            if g - last >= 3.8:
                z = ZOOM if z == 1.0 else 1.0; marks.append((g, z)); last = g
        off += d
    marks.append((total - END, 1.0))
    return marks


def zoom_at(marks, t):
    z = 1.0
    for t0, zz in marks:
        if t >= t0: z = zz
    return z


def render(ad, people, music_list, out_dir, aspect, tmpdir):
    W, H = (1080, 1920) if aspect == '916' else (1080, 1350)
    hk = ad['hook']; pre = PRE_CARD if hk['type'] == 'card' else 0.0
    if ad['person'] == 'multi':          # supercut: segs = [[person, a0, a1], ...]
        seg_people = [people[x[0]] for x in ad['segs']]; segs = [x[1:] for x in ad['segs']]
    else:
        seg_people = [people[ad['person']]] * len(ad['segs']); segs = ad['segs']
    P = seg_people[0]
    pv, pa = f'{tmpdir}/plate.mp4', f'{tmpdir}/voice.wav'
    total = build_plate(P, segs, aspect, pre, W, H, pv, pa, tmpdir, seg_people)
    words, off, seg_t = [], pre, []
    for (a0, a1), sp in zip(segs, seg_people):
        words += retime(load_words(sp['tx']), [[a0, a1]], off); seg_t.append((off, off + a1 - a0, sp)); off += a1 - a0
    # lower third windows: first appearance of each person (single person: after the hook)
    lts, seen = [], set()
    multi = ad['person'] == 'multi'
    for i, (t0, t1, sp) in enumerate(seg_t):
        if sp['name'] not in seen:
            seen.add(sp['name'])
            if multi:
                run_end = t1
                for u0, u1, up in seg_t[i + 1:]:
                    if up is not sp: break
                    run_end = u1
                lts.append((t0, min(2.6, run_end - t0), sp))
            else:
                lts.append((pre + ad.get('lt_at', HOOK + 0.2), ad.get('lt_dur', 4.2), sp))
    caps = chunks(words)
    mus = music_list[ad.get('music', 0) % len(music_list)]
    mix = f'{tmpdir}/mix.wav'
    mix_audio(pa, mus['file'], mus.get('offset', 0), mix, total, pre)
    nfr = int(round(total * FPS))
    out = f"{out_dir}/{ad['id']}-{aspect}.mp4"
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', pv, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium',
                            '-crf', '21', '-maxrate', '4M', '-bufsize', '8M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                            '-movflags', '+faststart', '-t', f'{total:.3f}', out], stdin=subprocess.PIPE)
    marks = shots(segs, words, pre, total)
    call = P.get('layout') == 'call'
    cap_y = {'916': 1300 if not call else 1330, '45': 1000}[aspect]
    lt_y = {'916': 1460, '45': 1160}[aspect]
    hook_y = 230 if aspect == '916' else 70
    first = 'these' if multi else P['first']; cta = ad.get('cta', 'BOOK A CALL WITH ANDREW')
    endc = card = None
    voice = None
    if call:
        import soundfile as sf
        voice, vsr = sf.read(pa)
        if voice.ndim > 1: voice = voice.mean(1)
        face = Image.open(P['face_img']).convert('RGBA'); andrew = Image.open(P['andrew_img']).convert('RGBA')
    fsz = W * H * 3
    for fi in range(nfr):
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            buf = last_buf
        last_buf = buf
        t = fi / FPS
        base = Image.frombytes('RGB', (W, H), buf)
        if t >= total - END:
            if endc is None:
                endc = end_card(base, first, cta, W, H)
            a = min(1.0, (t - (total - END)) / 0.25)
            frame = Image.blend(base, endc, a) if a < 1 else endc
            enc.stdin.write(frame.tobytes()); continue
        if pre and t < pre:
            if card is None:
                card = card_frame(base, hk['card'], W, H)
            enc.stdin.write(card.tobytes()); continue
        if not call:
            cur = next((sp for t0, t1, sp in seg_t if t0 <= t < t1), seg_t[-1][2])
            fx, fy = cur.get('face', [0.5, 0.4])
            z = zoom_at(marks, t)
            if z != 1.0:
                cw, ch = W / z, H / z
                x0 = min(max(fx * W - cw / 2, 0), W - cw); y0 = min(max(fy * H - ch / 2, 0), H - ch)
                base = base.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
            frame = base.convert('RGBA')
            # soft dark gradient top + bottom for legibility
            frame.alpha_composite(grad(W, H))
        else:
            frame = base.convert('RGBA')
            i0 = int(t * vsr); seg = voice[i0:i0 + vsr // FPS]
            lvl = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0
            pulse = min(1.0, lvl * 9)
            fs = 500 if aspect == '916' else 380
            fcy = 560 if aspect == '916' else 330
            d = ImageDraw.Draw(frame)
            ring = int(10 + 26 * pulse)
            d.ellipse([W // 2 - fs // 2 - ring, fcy - ring, W // 2 + fs // 2 + ring, fcy + fs + ring], fill=B.ACCENT + (int(120 + 135 * pulse),))
            frame.alpha_composite(face.resize((fs, fs), Image.LANCZOS), (W // 2 - fs // 2, fcy))
            asz = fs * 2 // 5
            ax, ay = W // 2 + fs // 2 - asz // 2, fcy + fs - asz + 10
            d.ellipse([ax - 8, ay - 8, ax + asz + 8, ay + asz + 8], fill=B.WHITE)
            frame.alpha_composite(andrew.resize((asz, asz), Image.LANCZOS), (ax, ay))
            pf = F(B.FONT_BLACK, 34); pt = '●  RECORDED CLIENT CALL'
            ptw = d.textlength(pt, font=pf); py = fcy + fs + 50
            d.rounded_rectangle([(W - ptw) / 2 - 26, py, (W + ptw) / 2 + 26, py + 66], 33, fill=(200, 30, 45, 235))
            d.text(((W - ptw) / 2, py + 13), pt, font=pf, fill=B.WHITE)
        tt = t - pre
        # hook / topline
        if tt < HOOK and hk['type'] != 'card':
            kind = hk['type']
            hi = hook_img(kind, hk['text'], hk.get('sub', ''), W)
            a = min(1.0, tt / 0.2)
            dy = int((1 - a) * -40)
            if a < 1:
                hi = hi.copy(); hi.putalpha(Image.eval(hi.getchannel('A'), lambda v: int(v * a)))
            frame.alpha_composite(hi, (0, max(0, hook_y + dy)))
        elif ad.get('topline') or hk['type'] == 'card':
            frame.alpha_composite(hook_img('topline', ad.get('topline') or hk['card'].replace('*', ''), '', W), (0, hook_y))
        # lower third
        for lt0, dur_lt, sp in lts:
            if lt0 <= t < lt0 + dur_lt:
                lt = lower_third(sp['name'], sp['role'], W)
                k = min(1.0, (t - lt0) / 0.25, (lt0 + dur_lt - t) / 0.25)
                x = int(60 - (1 - k) * (lt.width + 60))
                frame.alpha_composite(lt, (x, lt_y))
        # captions
        for c in caps:
            if c['s'] <= t < c['e']:
                act = max([i for i, w in enumerate(c['words']) if w['s'] <= t] or [0])
                step = min(3, int((t - c['s']) * FPS))
                ci = caption_img(tuple(w['w'] for w in c['words']), act, step, W)
                frame.alpha_composite(ci, (0, cap_y - ci.height // 2))
                break
        enc.stdin.write(frame.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); dec.stdout.close(); dec.wait()
    return out, total


@lru_cache(4)
def grad(W, H):
    g = np.zeros((H, 1), np.float32)
    top = int(H * 0.22); bot = int(H * 0.45)
    g[:top, 0] = np.linspace(0.55, 0, top)
    g[H - bot:, 0] = np.linspace(0, 0.6, bot)
    a = (np.repeat(g, W, 1) * 255).astype(np.uint8)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); im.putalpha(Image.fromarray(a)); return im


def job(args):
    ad, people, music, out_dir, aspect = args
    with tempfile.TemporaryDirectory(dir=os.environ.get('TA_TMP')) as td:
        try:
            out, total = render(ad, people, music, out_dir, aspect, td)
            return ad['id'], aspect, round(total, 2), None
        except Exception as e:
            return ad['id'], aspect, 0, str(e)[-800:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('specs'); ap.add_argument('out')
    ap.add_argument('--only', default=''); ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--skip-existing', action='store_true')
    a = ap.parse_args()
    S = json.load(open(a.specs)); os.makedirs(a.out, exist_ok=True)
    only = set(filter(None, a.only.split(',')))
    jobs = []
    for ad in S['ads']:
        if only and ad['id'] not in only: continue
        for asp in ad.get('aspect', ['916']):
            if a.skip_existing and os.path.exists(f"{a.out}/{ad['id']}-{asp}.mp4"): continue
            jobs.append((ad, S['people'], S['music'], a.out, asp))
    with ProcessPoolExecutor(a.jobs) as ex:
        for r in ex.map(job, jobs):
            print(*r, flush=True)


if __name__ == '__main__':
    main()
