#!/usr/bin/env python3
"""Cut a standalone testimonial ad from a raw client testimonial (real person on screen, no AI).

Usage:  python3 tools/testimonial_ad.py SPEC.json OUT.mp4 [--preview OUT_540.mp4]

SPEC.json
{
  "id": "rob-01",
  "source": "/path/rob.mov", "transcript": "/path/transcript.json",   # tools/transcribe.py output
  "aspect": "916" | "45",
  "crop": {"cx": 0.5, "cy": 0.45, "zoom": 1.0},     # base crop of the source (fractions)
  "segments": [[3.9, 11.3], [16.0, 23.0]],           # source seconds, snapped to word edges
  "hook": {"style": "card" | "bar" | "none", "text": "Real *humans* answer your clients", "dur": 2.2,
           "kicker": "REAL CLIENT"},
  "name": "Rob", "biz": "SaaSSuite customer",
  "end": {"line": "Want this for *your* clients?", "cta": "Tap Learn More", "sub": "..."},
  "music": "/path/bed.mp3", "punch": true
}
Pipeline: trim/crop/punch-in pieces -> concat + end card -> PNG overlays (hook, lower third) -> ASS word
captions (active word yellow, pop-in) -> music bed ducked under speech -> loudness to -14 LUFS, limiter -1 dBTP.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import brand_look as B

FPS = 30
END_DUR = 2.6
LAYOUT = {
    '916': dict(W=1080, H=1920, cap_y=1250, lt_y=1415, bar_y=250, safe=(64, 1016)),
    '45': dict(W=1080, H=1350, cap_y=930, lt_y=1075, bar_y=70, safe=(64, 1016)),
    # 'frame' mode: landscape call footage in a 16:9 window on navy, title header above, captions below
    '916f': dict(W=1080, H=1920, cap_y=1500, lt_y=1235, bar_y=250, frame_y=590, safe=(64, 1016)),
    '45f': dict(W=1080, H=1350, cap_y=1240, lt_y=1000, bar_y=50, frame_y=350, safe=(64, 1016)),
}


def title_png(path, L, title, kicker):
    W, H = L['W'], L['H']
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = L['bar_y']
    if kicker:
        y = B.pill(d, kicker, W // 2, y, B.font(B.FONT_BOLD, 30), fill=(220, 38, 38)) + 28
    f = B.font(B.FONT_BLACK, 66 if len(title) < 40 else 56)
    B.draw_rich(d, title, f, 80, y, W - 160)
    im.save(path)
FIXES = [(r'(?i)^sas+weet(\.ai)?$', 'SaaSSuite'), (r'(?i)^saas$', 'SaaS'), (r'(?i)^high-?level$', 'HighLevel'),
         (r'(?i)^ai$', 'AI'), (r'(?i)^gohighlevel$', 'GoHighLevel')]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-3000:]); raise SystemExit(f'failed: {cmd[0]}')
    return r


def probe(src):
    o = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:stream_side_data=rotation',
             '-of', 'json', src]).stdout
    s = json.loads(o)['streams'][0]
    w, h = s['width'], s['height']
    rot = abs(int(next((d.get('rotation', 0) for d in s.get('side_data_list', []) if 'rotation' in d), 0)))
    return (h, w) if rot in (90, 270) else (w, h)


def words_of(tr):
    out = []
    for seg in tr['segments']:
        for w in seg['words']:
            if out and w['w'].startswith('-'):
                out[-1]['w'] += w['w']; out[-1]['e'] = w['e']; continue
            out.append(dict(w))
    for w in out:
        core = w['w'].strip(' .,!?')
        for pat, rep in FIXES:
            core = re.sub(pat, rep, core)
        w['cap'] = core
    # merge '.ai' fragments into the previous word, and multi-word brand names
    merged = []
    for w in out:
        if merged and w['w'].strip().lower().startswith('.ai'):
            merged[-1]['e'] = w['e']; continue
        merged.append(w)
    out = merged
    def lw(i): return out[i]['cap'].lower() if i < len(out) else ''
    for i in range(len(out)):
        if lw(i) == 'go' and lw(i + 1) == 'high' and lw(i + 2).startswith('level'):
            out[i]['cap'] = 'GoHighLevel' + out[i + 2]['cap'][5:]; out[i]['e'] = out[i + 2]['e']; out[i + 1]['cap'] = out[i + 2]['cap'] = ''
        elif lw(i) == 'high' and lw(i + 1).startswith('level'):
            out[i]['cap'] = 'HighLevel' + out[i + 1]['cap'][5:]; out[i]['e'] = out[i + 1]['e']; out[i + 1]['cap'] = ''
    out = [w for w in out if w['cap']]
    # 'SaaS suite' -> 'SaaSSuite'
    for i in range(len(out) - 1):
        if out[i]['cap'].lower() == 'saas' and out[i + 1]['cap'].lower().startswith('suite'):
            out[i]['cap'] = 'SaaSSuite' + out[i + 1]['cap'][5:]; out[i]['e'] = out[i + 1]['e']; out[i + 1]['cap'] = ''
    return [w for w in out if w['cap']]


def snap(words, a, b):
    inside = [w for w in words if w['s'] >= a - 0.12 and w['e'] <= b + 0.12]
    if not inside:
        raise SystemExit(f'no words in {a}-{b}')
    return max(0, inside[0]['s'] - 0.08), inside[-1]['e'] + 0.14, inside


def pieces_for(s, e, ws, first, punch):
    """Split a segment at word gaps into 2.5-4.5 s pieces; zoom alternates for punch-ins."""
    if not punch:
        return [(s, e, 1.0)]
    cuts, last = [], s
    for i in range(1, len(ws)):
        gap_t = (ws[i - 1]['e'] + ws[i]['s']) / 2
        if gap_t - last >= 2.5 and e - gap_t >= 1.5 and (ws[i]['s'] - ws[i - 1]['e'] > 0.08 or gap_t - last > 4.5):
            cuts.append(gap_t); last = gap_t
    bounds = [s] + cuts + [e]
    z0 = 1.0 if first else 1.12
    return [(bounds[i], bounds[i + 1], z0 if i % 2 == 0 else (1.12 if z0 == 1.0 else 1.0)) for i in range(len(bounds) - 1)]


def crop_box(sw, sh, aspect, zoom, cx, cy):
    h = sh if sw / sh >= aspect else sw / aspect
    h /= zoom; w = h * aspect
    w, h = int(w) // 2 * 2, int(h) // 2 * 2
    x = int(min(max(0, cx * sw - w / 2), sw - w)); y = int(min(max(0, cy * sh - h / 2), sh - h))
    return w, h, x, y


# ---------- overlays (PIL) ----------
def rgba(c, a):
    return (c[0], c[1], c[2], a)


def hook_png(path, L, hook):
    W, H = L['W'], L['H']
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    text = hook['text']
    if hook['style'] == 'card':
        d.rectangle([0, 0, W, H], fill=rgba(B.BG, 205))
        f = B.font(B.FONT_BLACK, 104 if len(text) < 40 else 88)
        lines = B.rich_lines(d, text, f, W - 160)
        asc, desc = f.getmetrics(); lh = int((asc + desc) * 1.1)
        y0 = H // 2 - len(lines) * lh // 2 - 40
        if hook.get('kicker'):
            B.pill(d, hook['kicker'], W // 2, y0 - 120, B.font(B.FONT_BOLD, 34))
        B.draw_rich(d, text, f, 80, y0, W - 160)
    else:  # bar
        f = B.font(B.FONT_BLACK, 70 if len(text) < 44 else 60)
        lines = B.rich_lines(d, text, f, W - 200)
        asc, desc = f.getmetrics(); lh = int((asc + desc) * 1.12)
        y = L['bar_y']; bh = len(lines) * lh + 70
        if hook.get('kicker'):
            kf = B.font(B.FONT_BOLD, 30)
            B.pill(d, hook['kicker'], W // 2, y, kf); y += 82
        d.rounded_rectangle([60, y, W - 60, y + bh], radius=34, fill=rgba(B.BG, 232))
        B.draw_rich(d, text, f, 100, y + 32, W - 200)
    im.save(path)


def star(d, cx, cy, r, fill):
    import math
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def lower_third_png(path, L, name, biz, stars=True):
    W, H = L['W'], L['H']
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fn, fb = B.font(B.FONT_BLACK, 64), B.font(B.FONT_MED, 40)
    tw = max(d.textlength(name, font=fn) + 250, d.textlength(biz, font=fb)) + 70
    x0, y0 = 64, L['lt_y']; x1, y1 = x0 + tw, y0 + 164
    d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=rgba(B.BG, 228))
    d.rounded_rectangle([x0, y0, x0 + 12, y1], radius=6, fill=B.ACCENT)
    d.text((x0 + 38, y0 + 14), name, font=fn, fill=B.WHITE)
    sx = x0 + 38 + d.textlength(name, font=fn) + 34
    for k in range(5 if stars else 0):
        star(d, sx + k * 42, y0 + 56, 17, B.ACCENT)
    d.text((x0 + 38, y0 + 100), biz, font=fb, fill=B.MUTED)
    im.save(path)


def end_card_png(path, L, bg_frame, end, name):
    W, H = L['W'], L['H']
    bg = Image.open(bg_frame).convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(28))
    ov = Image.new('RGBA', (W, H), rgba(B.BG, 214))
    im = Image.alpha_composite(bg.convert('RGBA'), ov); d = ImageDraw.Draw(im)
    tall = H > 1500
    y = int(H * (0.30 if tall else 0.22))
    y = B.pill(d, 'SAASSUITE', W // 2, y, B.font(B.FONT_BOLD, 34)) + 50
    y = B.draw_rich(d, end.get('line', f'Want results like *{name}*?'), B.font(B.FONT_BLACK, 92), 90, y, W - 180) + 30
    if end.get('sub'):
        y = B.draw_rich(d, end['sub'], B.font(B.FONT_MED, 42), 110, y, W - 220, color=B.MUTED) + 40
    fc = B.font(B.FONT_BLACK, 56); cta = end.get('cta', 'Tap Learn More')
    cw = d.textlength(cta, font=fc) + 120
    d.rounded_rectangle([W / 2 - cw / 2, y + 20, W / 2 + cw / 2, y + 140], radius=26, fill=B.ACCENT)
    d.text((W / 2 - d.textlength(cta, font=fc) / 2, y + 44), cta, font=fc, fill=B.BG)
    ff = B.font(B.FONT_MED, 34); foot = 'Andrew George  ·  SaaSSuite'
    d.text((W / 2 - d.textlength(foot, font=ff) / 2, H - (330 if tall else 140)), foot, font=ff, fill=B.MUTED)
    im.convert('RGB').save(path)


# ---------- captions (ASS) ----------
def ass_time(t):
    h, r = divmod(max(0, t), 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def chunks(words, max_words=3, max_gap=0.35, max_chars=16):
    cur = []
    for w in words:
        if cur and (len(cur) >= max_words or w['s'] - cur[-1]['e'] > max_gap
                    or len(' '.join(x['cap'] for x in cur + [w])) > max_chars):
            yield cur; cur = []
        cur.append(w)
    if cur:
        yield cur


def write_ass(words, path, L, t_from):
    W, H = L['W'], L['H']
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,7,4,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    acc = '&H003FD2FF&'
    ev = []
    chs = list(chunks([w for w in words if w['s'] >= t_from - 0.05]))
    for ci, ch in enumerate(chs):
        nxt = chs[ci + 1][0]['s'] if ci + 1 < len(chs) else 1e9
        for i, w in enumerate(ch):
            st = w['s']; en = ch[i + 1]['s'] if i + 1 < len(ch) else min(w['e'] + 0.18, nxt - 0.01)
            parts = [(f"{{\\c{acc}}}{x['cap'].upper()}{{\\c&H00FFFFFF&}}" if j == i else x['cap'].upper()) for j, x in enumerate(ch)]
            pop = '\\fscx82\\fscy82\\t(0,90,\\fscx100\\fscy100)' if i == 0 else ''
            ev.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{{\\pos({W // 2},{L['cap_y']}){pop}}}{' '.join(parts)}")
    Path(path).write_text(hdr + '\n'.join(ev) + '\n')


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec'); ap.add_argument('out'); ap.add_argument('--preview')
    a = ap.parse_args()
    S = json.load(open(a.spec))
    frame = S.get('mode') == 'frame'
    L = LAYOUT[S.get('aspect', '916') + ('f' if frame else '')]; W, H = L['W'], L['H']
    FW, FH = (W, W * 3 // 4 // 2 * 2) if frame else (W, H)
    # multi-client compilations: segments are [a, b, clip_key] and S['clips'][key] = {source, transcript, crop, name, biz}
    clips = S.get('clips') or {'_': {k: S[k] for k in ('source', 'transcript') if k in S} | {'crop': S.get('crop', {})}}
    multi = 'clips' in S
    WORDS = {k: words_of(json.load(open(c['transcript']))) for k, c in clips.items()}
    if multi:
        sw, sh, cx, cy, bz = FW, FH, 0.5, 0.5, 1.0   # every segment is pre-cropped to the output frame
    else:
        sw, sh = probe(S['source'])
        cr = S.get('crop', {}); cx, cy, bz = cr.get('cx', 0.5), cr.get('cy', 0.45), cr.get('zoom', 1.0)
    hook = S.get('hook', {'style': 'none'})
    punch = S.get('punch', True)

    segs, pieces, out_words, t = [], [], [], 0.0
    seg_clip = []
    for k, sg in enumerate(S['segments']):
        ck = sg[2] if multi else '_'
        s, e, ws = snap(WORDS[ck], sg[0], sg[1])
        segs.append((s, e)); seg_clip.append(ck)
        for (ps, pe, z) in pieces_for(s, e, ws, k == 0, punch):
            pieces.append((ps, pe, z, k))
        for w in ws:
            out_words.append(dict(w, s=w['s'] - s + t, e=w['e'] - s + t))
        t += e - s
    speech_dur = t
    total = speech_dur + END_DUR

    with tempfile.TemporaryDirectory() as td:
        # cut each segment with input seeking (fast on long sources), join into one mezzanine on the output timeline
        parts, off, remap = [], 0.0, []
        for k, (s0, e0) in enumerate(segs):
            pk = os.path.join(td, f'seg{k}.mkv')
            c = clips[seg_clip[k]]; vf = []
            if multi:
                csw, csh = probe(c['source']); cc = c.get('crop', {})
                w_, h_, x_, y_ = crop_box(csw, csh, FW / FH, cc.get('zoom', 1.0), cc.get('cx', 0.5), cc.get('cy', 0.45))
                vf = ['-vf', f'crop={w_}:{h_}:{x_}:{y_},scale={FW}:{FH}:flags=lanczos,setsar=1']
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{s0:.3f}', '-t', f'{e0 - s0:.3f}', '-i', c['source'], '-map', '0:v:0', '-map', '0:a:0', *vf,
                 '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '12', '-r', str(FPS), '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '1', pk])
            parts.append(pk); remap.append((s0, e0, off)); off += e0 - s0
        lst = os.path.join(td, 'list.txt'); Path(lst).write_text(''.join(f"file '{x}'\n" for x in parts))
        src = os.path.join(td, 'src.mkv')
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', src])
        pieces = [(ps - remap[k][0] + remap[k][2], pe - remap[k][0] + remap[k][2], z) for ps, pe, z, k in pieces]
        segs = [(o, o + e0 - s0) for s0, e0, o in remap]
        # last frame for end card
        lf = os.path.join(td, 'last.png')
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{segs[-1][1] - 0.3:.2f}', '-i', src, '-frames:v', '1', lf])
        endp = os.path.join(td, 'end.png'); end_card_png(endp, L, lf, S.get('end', {}), S.get('first', S.get('name', 'them').split()[0]))
        ltp = os.path.join(td, 'lt.png')
        LTS = []   # (t_in, png) for each person change after the first
        if multi:
            c0 = clips[seg_clip[0]]; lower_third_png(ltp, L, c0['name'], c0['biz'], True)
            for k in range(1, len(segs)):
                if seg_clip[k] != seg_clip[k - 1]:
                    pth = os.path.join(td, f'lt{k}.png'); cc = clips[seg_clip[k]]
                    lower_third_png(pth, L, cc['name'], cc['biz'], True); LTS.append((segs[k][0] + 0.2, pth))
        else:
            lower_third_png(ltp, L, S['name'], S['biz'], S.get('stars', True))
        hdur = hook.get('dur', 2.2) if hook['style'] != 'none' else 0
        hkp = os.path.join(td, 'hook.png')
        if hdur:
            hook_png(hkp, L, hook)
        ass = os.path.join(td, 'cap.ass')
        write_ass(out_words, ass, L, hdur - 0.3 if hook['style'] == 'card' else 0)

        inputs = ['-i', src, '-loop', '1', '-t', f'{END_DUR}', '-framerate', str(FPS), '-i', endp,
                  '-loop', '1', '-t', f'{total}', '-framerate', str(FPS), '-i', ltp]
        if hdur:
            inputs += ['-loop', '1', '-t', f'{hdur + 0.3}', '-framerate', str(FPS), '-i', hkp]
        ttp = os.path.join(td, 'title.png')
        if frame:
            title_png(ttp, L, S.get('title', ''), S.get('kicker', 'REAL 1:1 CALL'))
            inputs += ['-loop', '1', '-t', f'{total}', '-framerate', str(FPS), '-i', ttp]
        n_in = 3 + (1 if hdur else 0) + (1 if frame else 0)
        for t_in, pth in LTS:
            inputs += ['-loop', '1', '-t', f'{total}', '-framerate', str(FPS), '-i', pth]
        fc = []
        for i, (ps, pe, z) in enumerate(pieces):
            zz = (1 + (z - 1) * 0.8) if frame else z
            w, h, x, y = crop_box(sw, sh, FW / FH, bz * zz, cx, cy - (0.03 if z > 1 and not frame else 0))
            pad = f",pad={W}:{H}:0:{L['frame_y']}:color=0x0B0F1A" if frame else ''
            fc.append(f"[0:v]trim={ps:.3f}:{pe:.3f},setpts=PTS-STARTPTS,fps={FPS},crop={w}:{h}:{x}:{y},"
                      f"scale={FW}:{FH}:flags=lanczos,setsar=1{pad},format=yuv420p[p{i}]")
        fc.append(f"[1:v]scale={W}:{H},setsar=1,format=yuv420p,fade=t=in:st=0:d=0.25[endv]")
        fc.append(''.join(f'[p{i}]' for i in range(len(pieces))) + f"[endv]concat=n={len(pieces) + 1}:v=1:a=0[base]")
        lt_in, lt_out = (hdur + 0.2 if hook['style'] == 'card' else 0.4), None
        lt_out = min(lt_in + 3.6, speech_dur - 0.3, (LTS[0][0] - 0.3) if LTS else 1e9)
        fc.append(f"[2:v]format=rgba,fade=t=in:st={lt_in:.2f}:d=0.25:alpha=1,fade=t=out:st={lt_out - 0.25:.2f}:d=0.25:alpha=1[lt]")
        fc.append(f"[base][lt]overlay=0:0:enable='between(t,{lt_in:.2f},{lt_out:.2f})'[b1]")
        last = 'b1'
        if hdur:
            fc.append(f"[3:v]format=rgba,fade=t=out:st={hdur - 0.2:.2f}:d=0.2:alpha=1[hk]")
            fc.append(f"[b1][hk]overlay=0:0:enable='lte(t,{hdur:.2f})'[b2]"); last = 'b2'
        if frame:
            ti = 4 if hdur else 3
            fc.append(f"[{ti}:v]format=rgba[tt]")
            fc.append(f"[{last}][tt]overlay=0:0:enable='between(t,{max(0, hdur - 0.05):.2f},{speech_dur:.2f})'[b3]"); last = 'b3'
        for j, (t_in, pth) in enumerate(LTS):
            t_out = min(t_in + 3.0, speech_dur - 0.3)
            fc.append(f"[{n_in + j}:v]format=rgba,fade=t=in:st={t_in:.2f}:d=0.25:alpha=1,fade=t=out:st={t_out - 0.25:.2f}:d=0.25:alpha=1[lx{j}]")
            fc.append(f"[{last}][lx{j}]overlay=0:0:enable='between(t,{t_in:.2f},{t_out:.2f})'[bx{j}]"); last = f'bx{j}'
        fc.append(f"[{last}]ass={ass}[vo]")
        vid = os.path.join(td, 'v.mp4')
        run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', '[vo]', '-t', f'{total:.3f}',
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '4M', '-bufsize', '8M', '-pix_fmt', 'yuv420p',
             '-r', str(FPS), vid])

        # audio: speech segments + ducked music bed
        af = []
        for j, (s, e) in enumerate(segs):
            af.append(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=mono,"
                      f"afade=t=in:d=0.02,afade=t=out:st={e - s - 0.04:.3f}:d=0.04[s{j}]")
        af.append(''.join(f'[s{j}]' for j in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,highpass=f=70,"
                  f"acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4dB,apad=whole_dur={total:.3f},asplit=2[sp][key]")
        af.append(f"[1:a]aformat=sample_rates=48000:channel_layouts=mono,atrim=0:{total:.3f},volume=-19dB,"
                  f"afade=t=in:d=0.4,afade=t=out:st={total - 0.8:.3f}:d=0.8[mus]")
        af.append("[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck]")
        af.append("[sp][duck]amix=inputs=2:duration=first:normalize=0[mix]")
        wav = os.path.join(td, 'a.wav')
        run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-stream_loop', '-1', '-i', S['music'],
             '-filter_complex', ';'.join(af), '-map', '[mix]', '-t', f'{total:.3f}', '-ac', '2', '-ar', '48000', wav])
        import soundfile as sf, pyloudnorm as pyln
        data, rate = sf.read(wav)
        lufs = pyln.Meter(rate).integrated_loudness(data)
        gain = -14.0 - lufs
        run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-filter_complex',
             f"[1:a]volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=60:level=disabled[a]",
             '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', a.out])
        if a.preview:
            run(['ffmpeg', '-v', 'error', '-y', '-i', a.out, '-vf', f'scale=-2:{960 if H > 1500 else 676}', '-c:v', 'libx264',
                 '-crf', '27', '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', a.preview])
    print(json.dumps({'id': S.get('id'), 'out': a.out, 'dur': round(total, 2), 'pieces': len(pieces)}))


if __name__ == '__main__':
    main()
