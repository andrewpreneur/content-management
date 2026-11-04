#!/usr/bin/env python3
"""Styled reel renderer — approved editing styles from docs/editing-styles.md.

  python3 tools/stylekit.py EDL.json OUT.mp4 --style s1|s2|s3-green|s3-warm|s4 [--srt OUT.srt]
  python3 tools/stylekit.py --raw-vs-edited RAW.mp4 EDITED.mp4 OUT.mp4 [--title "..."]     (S6)

EDL = tools/reel.py EDL (source = screen recording, cam = face camera on the same timeline, transcript, segments with
"a" audio ranges, optional "v", "cx"/"cy"/"zoom" screen crop) plus:
  "accent": ["layout", "HighLevel", ...]   words shown in the style's accent treatment
  segment "head": "Hide what they *don't use*"   headline / visual text for that beat (*word* = accent)
  "title": persistent title for s4, "cta": "LAYOUT" keyword for the end card
Audio is the concatenation of the "a" ranges (continuous). Video is cut into sub-shots at the style's pace:
layout alternation (split / face / visual), screen punch-ins, slow push-ins on the face — so something changes every 1.5–2.5 s.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import reel as R

W, H = 1080, 1920
FD = Path(__file__).parent / 'fonts'
F_SANS = str(FD / 'InterTight-ExtraBold.ttf')
F_SANS_I = str(FD / 'InterTight-ExtraBoldItalic.ttf')
F_SERIF = str(FD / 'InstrumentSerif-Regular.ttf')
F_SERIF_I = str(FD / 'InstrumentSerif-Italic.ttf')
F_PLAY_I = str(FD / 'PlayfairDisplay-BoldItalic.ttf')

STYLES = {
    # pace = sub-shot seconds; pattern = layout cycle; split geometry = (visual_top, seam_y, face card box)
    's1': dict(bg=('#F4F8FC', '#DCE9F5'), ink='#0E1116', accent='#2F7BF6', pace=2.2, pattern=['split', 'split', 'face', 'split', 'visual'],
               seam=1010, face_box=(40, 1050, 1040, 1920), radius=70, round_bottom=False, vis_box=(70, 150, 1010, 960),
               cap='s1', head_font=F_SANS, head_size=58, head_color='#0E1116'),
    's2': dict(bg=('#EADFCE', '#DED0BB'), ink='#1B1712', accent='#C2502F', pace=1.6, pattern=['split', 'visual', 'split', 'face', 'split', 'card'],
               seam=1000, face_box=(36, 1040, 1044, 1884), radius=64, round_bottom=True, vis_box=(60, 140, 1020, 950),
               cap='s2', head_font=F_SERIF, head_size=92, head_color='#1B1712'),
    's3-green': dict(bg=('#0B110C', '#122015'), ink='#FFFFFF', accent='#B6F36A', pace=2.0, pattern=['split'],
                     seam=900, face_box=(0, 790, 1080, 1920), radius=0, round_bottom=False, vis_box=(60, 250, 1020, 840),
                     cap='s3-green', head_font=F_SANS, head_size=60, head_color='#FFFFFF', fade_face=True),
    's3-warm': dict(bg=('#1E1410', '#2B1C15'), ink='#FFFFFF', accent='#F0A27A', pace=2.0, pattern=['split'],
                    seam=900, face_box=(0, 790, 1080, 1920), radius=0, round_bottom=False, vis_box=(60, 250, 1020, 840),
                    cap='s3-warm', head_font=F_SERIF, head_size=78, head_color='#F6EDE6', fade_face=True),
    's4': dict(bg=('#000000', '#000000'), ink='#FFFFFF', accent='#FFFFFF', pace=4.5, pattern=['wide', 'tight'],
               cap='s4'),
}


def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ass_color(h):
    r, g, b = hexrgb(h); return f'&H00{b:02X}{g:02X}{r:02X}&'


def rich(draw, text, fnt, fnt_acc, x0, y, maxw, color, accent, align='center', gap=1.1):
    """*word* -> accent font+color. Returns bottom y."""
    toks, acc = [], False
    for raw in text.split():
        st = raw.startswith('*'); en = raw.endswith('*') and len(raw) > 1
        if st: acc = True
        toks.append((raw.replace('*', ''), acc))
        if en: acc = False
    lines, cur = [], []
    for t in toks:
        trial = cur + [t]
        wdt = sum(draw.textlength(w + ' ', font=fnt_acc if a else fnt) for w, a in trial)
        if cur and wdt > maxw:
            lines.append(cur); cur = [t]
        else:
            cur = trial
    if cur: lines.append(cur)
    asc, desc = fnt.getmetrics(); lh = int((asc + desc) * gap)
    for line in lines:
        lw = sum(draw.textlength(w, font=fnt_acc if a else fnt) for w, a in line) + draw.textlength(' ', font=fnt) * (len(line) - 1)
        x = x0 + (maxw - lw) / 2 if align == 'center' else x0
        for w, a in line:
            f = fnt_acc if a else fnt
            draw.text((x, y), w, font=f, fill=accent if a else color)
            x += draw.textlength(w, font=f) + draw.textlength(' ', font=fnt)
        y += lh
    return y


def gradient(c1, c2):
    a, b = hexrgb(c1), hexrgb(c2)
    g = Image.new('RGB', (1, H))
    for y in range(H):
        t = y / (H - 1); g.putpixel((0, y), tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return g.resize((W, H))


def round_mask(w, h, r, bottom=True):
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, w - 1, h - 1 + (0 if bottom else r)], radius=r, fill=255)
    return m


def fade_mask(w, h, fade=160):
    m = Image.new('L', (w, h), 255); d = ImageDraw.Draw(m)
    for y in range(fade):
        d.line([(0, y), (w, y)], fill=int(255 * y / fade))
    return m


# ---------------- per-shot background / card images ----------------
def bg_png(st, path, head=None, layout='split'):
    im = gradient(*st['bg']).convert('RGBA'); d = ImageDraw.Draw(im)
    if head and layout in ('split', 'visual') and st['cap'] in ('s3-green', 's3-warm'):
        f = ImageFont.truetype(st['head_font'], st['head_size'])
        fa = ImageFont.truetype(F_SERIF_I if st['cap'] == 's3-warm' else st['head_font'], st['head_size'])
        rich(d, head, f, fa, 70, 130, W - 140, st['head_color'], st['accent'])
    if head and layout == 'visual' and st['cap'] == 's1':
        f = ImageFont.truetype(F_SANS, 64); fa = ImageFont.truetype(F_PLAY_I, 70)
        rich(d, head, f, fa, 70, 170, W - 140, st['ink'], st['accent'])
    im.save(path)


def card_png(st, path, text):
    """Full-frame section card (S2 chapter beat / S1 kinetic title)."""
    im = gradient(*st['bg']).convert('RGB'); d = ImageDraw.Draw(im)
    if st['cap'] == 's2':
        f = ImageFont.truetype(F_SERIF, 120); fa = ImageFont.truetype(F_SERIF_I, 120)
        bottom = rich(d, text, f, fa, 80, 0, W - 160, st['ink'], st['accent'])
        im2 = gradient(*st['bg']).convert('RGB'); d2 = ImageDraw.Draw(im2)
        rich(d2, text, f, fa, 80, (H - bottom) // 2 - 60, W - 160, st['ink'], st['accent']); im2.save(path); return
    f = ImageFont.truetype(F_SANS, 96); fa = ImageFont.truetype(F_PLAY_I, 104)
    rich(d, text, f, fa, 80, 760, W - 160, st['ink'], st['accent']); im.save(path)


def end_png(st, path, keyword):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    small = ImageFont.truetype(F_SERIF_I, 64); big = ImageFont.truetype(F_PLAY_I, 150)
    kw = f'“{keyword}”'
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    tw = d.textlength(kw, font=big)
    acc = hexrgb(st['accent']) if st['cap'] != 's1' else (255, 236, 140)
    gd.text(((W - tw) / 2, 1380), kw, font=big, fill=acc + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(18)); im.alpha_composite(glow)
    cw = d.textlength('comment', font=small)
    d.text(((W - cw) / 2, 1300), 'comment', font=small, fill=(255, 255, 255, 230))
    d.text(((W - tw) / 2, 1380), kw, font=big, fill=(255, 250, 225, 255))
    im.save(path)


# ---------------- captions ----------------
def write_styled_ass(words, path, st, layout_at, accent, shot_end=lambda t: 1e9, end_t=None):
    acc = set(a.lower() for a in accent)
    cap = st['cap']
    styles = {
        's1': [('Seam', 'Inter Tight ExtraBold', 70, st['ink'], 0, 0, 2), ('Face', 'Inter Tight ExtraBold', 76, '#FFFFFF', 3, 2, 2)],
        's2': [('Seam', 'Inter Tight ExtraBold', 46, '#FFFFFF', 0, 0, 3), ('Face', 'Instrument Serif', 120, '#FFFFFF', 2, 0, 1)],
        's3-green': [('Seam', 'Inter Tight ExtraBold', 74, '#FFFFFF', 3, 3, 1), ('Face', 'Inter Tight ExtraBold', 74, '#FFFFFF', 3, 3, 1)],
        's3-warm': [('Seam', 'Inter Tight ExtraBold', 50, '#FFFFFF', 0, 0, 3), ('Face', 'Inter Tight ExtraBold', 50, '#FFFFFF', 0, 0, 3)],
        's4': [('Seam', 'Inter Tight ExtraBold', 40, '#FFFFFF', 2, 1, 1), ('Face', 'Inter Tight ExtraBold', 40, '#FFFFFF', 2, 1, 1)],
    }[cap]
    box_col = {'s2': st['accent'], 's3-warm': st['accent']}.get(cap)
    lines = []
    for name, font, size, col, outline, shadow, border in styles:
        if border == 3:  # opaque box ("pill")
            lines.append(f"Style: {name},{font},{size},{ass_color(col)},{ass_color(col)},{ass_color(box_col or '#000000')},{ass_color(box_col or '#000000')},0,0,0,0,100,100,0,0,3,14,0,5,40,40,0,1")
        else:
            lines.append(f"Style: {name},{font},{size},{ass_color(col)},{ass_color(col)},&H64000000&,&H96000000&,0,0,0,0,100,100,0,0,1,{outline},{shadow},5,40,40,0,1")
    hdr = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           + '\n'.join(lines) + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    # group: one word per event (join a <=3-letter word with the next, like the refs); s3-green shows up to 3 words
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if cap == 's3-green':
            if len(cur) >= 3:
                groups.append(cur); cur = []
        elif not (len(w['cap']) <= 3 and len(cur) == 1):
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    ev = []
    acc_col = ass_color(st['accent'])
    for i, g in enumerate(groups):
        t0 = g[0]['s']; t1 = groups[i + 1][0]['s'] if i + 1 < len(groups) else g[-1]['e'] + 0.3
        t1 = min(t1, t0 + 1.2) if cap != 's3-green' else t1
        lay = layout_at(t0)
        if end_t is not None and t0 >= end_t:
            continue
        t1 = min(t1, shot_end(t0))
        style = 'Face' if lay in ('face', 'card') else 'Seam'
        if lay == 'card':
            continue  # chapter card carries its own text
        txt_parts = []
        for w in g:
            word = w['cap'] if cap not in ('s2',) else w['cap'].lower()
            if w['cap'].lower().strip('.,!?') in acc and cap in ('s1', 's3-green'):
                f = 'Playfair Display' if cap == 's1' else 'Inter Tight ExtraBold'
                word = f"{{\\fn{f}\\i1\\c{acc_col}}}{word}{{\\r}}"
            txt_parts.append(word)
        if cap == 's4':
            pos = (300, 905)
        elif cap in ('s3-green', 's3-warm'):
            pos = (W // 2, st['seam'])
        elif style == 'Face':
            pos = (W // 2, 1420)
        elif lay == 'visual':
            pos = (W // 2, 1590)
        else:
            pos = (W // 2, st['seam'] + (10 if cap == 's1' else 0))
        ev.append(f"Dialogue: 0,{R.ass_time(t0)},{R.ass_time(t1)},{style},,0,0,0,,{{\\pos({pos[0]},{pos[1]})}}{' '.join(txt_parts)}")
    Path(path).write_text(hdr + '\n'.join(ev) + '\n')


# ---------------- shot planning ----------------
def plan_shots(segs, st):
    shots, t, k = [], 0.0, 0
    for si, s in enumerate(segs):
        a0, a1 = s['a']; dur = a1 - a0; v0 = s.get('v', a0) if s.get('v') is not None else a0
        forced = s.get('layout_force')
        n = max(1, round(dur / st['pace']))
        step = dur / n
        for j in range(n):
            lay = forced or st['pattern'][k % len(st['pattern'])]
            if lay == 'card' and not s.get('head'):
                lay = 'split'
            if lay == 'card' and j > 0:
                lay = 'split'
            shots.append(dict(seg=si, t=t + j * step, dur=step, src=v0 + j * step, layout=lay, zoom=s.get('zoom', 1.6) * (1.0 if k % 2 == 0 else 1.25),
                              cx=s.get('cx', 0.5), cy=s.get('cy', 0.5), head=s.get('head'), push=(k % 3 == 1)))
            k += 1
        t += dur
    return shots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('edl', nargs='?'); ap.add_argument('out', nargs='?')
    ap.add_argument('--style', default='s1', choices=list(STYLES)); ap.add_argument('--srt')
    ap.add_argument('--raw-vs-edited', nargs=3, metavar=('RAW', 'EDITED', 'OUT')); ap.add_argument('--title', default='HOW THE ENGINE EDITS MY VIDEOS')
    a = ap.parse_args()
    if a.raw_vs_edited:
        return raw_vs_edited(*a.raw_vs_edited, a.title)
    st = STYLES[a.style]; edl = json.loads(Path(a.edl).read_text())
    src, cam, segs = edl['source'], edl.get('cam'), edl['segments']
    sw, sh = R.probe(src); cw, ch = R.probe(cam) if cam else (0, 0)
    words = R.merged_words(json.loads(Path(edl['transcript']).read_text()))
    wrt, total = R.retime(words, segs)
    shots = plan_shots(segs, st)
    if edl.get('cta'):
        # end card: last ~2.5 s go full-face
        for sh_ in shots:
            if sh_['t'] + sh_['dur'] > total - 2.6 and a.style != 's4':
                sh_['layout'] = 'face'

    def shot_end(t):
        for s_ in shots:
            if s_['t'] <= t < s_['t'] + s_['dur']:
                return s_['t'] + s_['dur']
        return 1e9

    def layout_at(t):
        for s in shots:
            if s['t'] <= t < s['t'] + s['dur']:
                return s['layout']
        return shots[-1]['layout']

    with tempfile.TemporaryDirectory() as td:
        clips = []
        for i, s in enumerate(shots):
            out = os.path.join(td, f'v{i:03d}.mp4'); lay = s['layout']
            inputs, fc = [], []
            if a.style == 's4':
                # letterbox: 16:9 cam full width, wide/tight alternate + slow push
                z = 1.0 if lay == 'wide' else 1.35
                cwid, chei = int(cw / z) // 2 * 2, int(ch / z) // 2 * 2
                cx0 = int(min(max(0, edl.get('fcx', 0.5) * cw - cwid / 2), cw - cwid)); cy0 = int(min(max(0, 0.42 * ch - chei / 2), ch - chei))
                inputs = ['-ss', f"{s['src'] + edl.get('cam_offset', 0)}", '-t', f"{s['dur']}", '-i', cam]
                titlep = os.path.join(td, 'title.png')
                if not os.path.exists(titlep):
                    im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
                    f = ImageFont.truetype(F_SANS, 46)
                    y = 430
                    for line in edl.get('title', 'Title').split('\n'):
                        lw = d.textlength(line, font=f); d.text(((W - lw) / 2, y), line, font=f, fill=(255, 255, 255)); y += 66
                    im.save(titlep)
                inputs += ['-loop', '1', '-t', f"{s['dur']}", '-i', titlep]
                fc.append(f"[0:v]crop={cwid}:{chei}:{cx0}:{cy0},scale={W}:608,setsar=1,fps=30[v];[1:v][v]overlay=0:620[o]")
            elif lay in ('face',):
                z = 1.0 if not s['push'] else 1.0
                fw, fh = R.box(cw, ch, W / H, 1.0, edl.get('fcx', 0.5), 0.5)[:2]
                x0 = int(min(max(0, edl.get('fcx', 0.5) * cw - fw / 2), cw - fw))
                inputs = ['-ss', f"{s['src'] + edl.get('cam_offset', 0)}", '-t', f"{s['dur']}", '-i', cam]
                push = f",zoompan=z='min(1.0+on*0.0012,1.08)':x='iw/2-(iw/zoom/2)':y='ih/3-(ih/zoom/3)':d=1:s={W}x{H}:fps=30" if s['push'] else ''
                fc.append(f"[0:v]crop={fw}:{fh}:{x0}:0,scale={W}:{H},setsar=1,fps=30{push}[o]")
            elif lay == 'card':
                cp = os.path.join(td, f'card{i}.png'); card_png(st, cp, s['head'])
                inputs = ['-loop', '1', '-t', f"{s['dur']}", '-i', cp]
                fc.append(f"[0:v]scale={W}:{H},setsar=1,fps=30[o]")
            else:  # split / visual
                bgp = os.path.join(td, f'bg{i}.png'); bg_png(st, bgp, s['head'], lay)
                vx0, vy0, vx1, vy1 = st['vis_box']
                if lay == 'visual':
                    vx0, vy0, vx1, vy1 = (60, 420, 1020, 1500) if a.style != 's1' else (60, 420, 1020, 1500)
                vw, vh = vx1 - vx0, vy1 - vy0
                cwid, chei, cx0, cy0 = R.box(sw, sh, vw / vh, s['zoom'], s['cx'], s['cy'])
                inputs = ['-loop', '1', '-t', f"{s['dur']}", '-i', bgp, '-ss', f"{s['src']}", '-t', f"{s['dur']}", '-i', src]
                vm = os.path.join(td, f'vm{i}.png'); round_mask(vw, vh, 28).save(vm)
                inputs += ['-loop', '1', '-t', f"{s['dur']}", '-i', vm]
                fc.append(f"[1:v]crop={cwid}:{chei}:{cx0}:{cy0},scale={vw}:{vh},setsar=1,fps=30,format=rgba[sc];[2:v]format=gray[vmk];[sc][vmk]alphamerge[scr]")
                shadow = '' if a.style.startswith('s3') else ''
                fc.append(f"[0:v]scale={W}:{H},fps=30,format=rgba[bg];[bg][scr]overlay={vx0}:{vy0}[b1]")
                last = 'b1'
                if lay == 'split' and cam:
                    fx0, fy0, fx1, fy1 = st['face_box']; fw_, fh_ = fx1 - fx0, fy1 - fy0
                    ccw, cch, ccx, ccy = R.box(cw, ch, fw_ / fh_, 1.55 if a.style.startswith('s3') else 1.75, edl.get('fcx', 0.5), 0.32)
                    fmk = os.path.join(td, f'fm{i}.png')
                    (fade_mask(fw_, fh_) if st.get('fade_face') else round_mask(fw_, fh_, st['radius'], st['round_bottom'])).save(fmk)
                    inputs += ['-ss', f"{s['src'] + edl.get('cam_offset', 0)}", '-t', f"{s['dur']}", '-i', cam, '-loop', '1', '-t', f"{s['dur']}", '-i', fmk]
                    fc.append(f"[3:v]crop={ccw}:{cch}:{ccx}:{ccy},scale={fw_}:{fh_},setsar=1,fps=30,format=rgba[fc];[4:v]format=gray[fmk];[fc][fmk]alphamerge[face];[{last}][face]overlay={fx0}:{fy0}[b2]")
                    last = 'b2'
                fc.append(f"[{last}]format=yuv420p[o]")
            subprocess.run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '[o]', '-t', f"{s['dur']}",
                            '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-an', out], check=True)
            clips.append(out)
        lst = os.path.join(td, 'list.txt'); Path(lst).write_text(''.join(f"file '{c}'\n" for c in clips))
        vcat = os.path.join(td, 'v.mp4')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vcat], check=True)
        # audio: continuous concat of "a" ranges
        ain, afc, acat = [], [], ''
        asrc = edl.get('audio', cam or src)
        for j, sg in enumerate(segs):
            ain += ['-ss', f"{sg['a'][0]}", '-t', f"{sg['a'][1] - sg['a'][0]}", '-i', asrc]
            afc.append(f"[{j}:a]aresample=48000,afade=t=in:d=0.02,afade=t=out:st={max(0, sg['a'][1] - sg['a'][0] - 0.03)}:d=0.03[a{j}]"); acat += f'[a{j}]'
        afc.append(f"{acat}concat=n={len(segs)}:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
        aout = os.path.join(td, 'a.m4a')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', *ain, '-filter_complex', ';'.join(afc), '-map', '[ao]', '-c:a', 'aac', '-b:a', '160k', aout], check=True)
        ass = os.path.join(td, 'c.ass'); write_styled_ass(wrt, ass, st, layout_at, edl.get('accent', []), shot_end, (total - 2.4) if edl.get('cta') else None)
        vf = f"subtitles={ass}:fontsdir={FD}"
        inputs = ['-i', vcat, '-i', aout]
        if edl.get('cta'):
            ep = os.path.join(td, 'end.png'); end_png(st, ep, edl['cta'])
            inputs += ['-loop', '1', '-t', f'{total}', '-i', ep]
            fcx = f"[0:v]{vf}[s];[s][2:v]overlay=0:0:enable='gte(t,{total - 2.4})'[o]"
        else:
            fcx = f"[0:v]{vf}[o]"
        subprocess.run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', fcx, '-map', '[o]', '-map', '1:a', '-t', f'{total}',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', a.out], check=True)
    if a.srt:
        R.write_srt(wrt, a.srt)
    print(f"{a.out}  {total:.1f}s  {len(shots)} shots  style {a.style}")


def raw_vs_edited(raw, edited, out, title):
    with tempfile.TemporaryDirectory() as td:
        bg = os.path.join(td, 'bg.png')
        im = gradient('#3A2618', '#160E09').convert('RGB')
        noise = Image.effect_noise((W, H), 18).convert('RGB'); im = Image.blend(im, noise, 0.06)
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(str(FD / 'InterTight-ExtraBold.ttf'), 40); fs = ImageFont.truetype(F_SANS, 22)
        y = 330
        for line in title.upper().split('\n') if '\n' in title else [title.upper()]:
            lw = d.textlength(line, font=f); d.text(((W - lw) / 2, y), line, font=f, fill=(236, 226, 214)); y += 56
        for x, lab, fill, ink in ((70, 'RAW', (20, 20, 20), (255, 255, 255)), (560, 'EDITED BY THE ENGINE', (244, 205, 72), (20, 20, 20))):
            tw = d.textlength(lab, font=fs); d.rounded_rectangle([x, 540, x + tw + 30, 580], radius=6, fill=fill); d.text((x + 15, 547), lab, font=fs, fill=ink)
        im.save(bg)
        fc = ("[1:v]scale=450:800,setsar=1[r];[2:v]scale=450:800,setsar=1[e];"
              "[0:v][r]overlay=70:600:shortest=1[b1];[b1][e]overlay=560:600:shortest=1[o]")
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', bg, '-i', raw, '-i', edited, '-filter_complex', fc,
                        '-map', '[o]', '-map', '2:a?', '-shortest', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], check=True)
    print(out)


if __name__ == '__main__':
    main()
