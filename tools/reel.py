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
  "segments": [ {"a": [0.0, 13.05], "v": null, "cx": 0.35, "cy": 0.5, "zoom": 1.0}, ... ]
}
  a    = audio (spoken) range in source seconds; the cut follows the voice
  v    = optional different start time for the picture (b-roll from elsewhere in the source)
  cx/cy= crop centre as a fraction of the frame; zoom 1.0 = square crop of full height
--clean   no captions/hook/CTA (base for tools/variants.py Trial Reels, which add their own)
--translations  JSON {"<transcript segment start>": "translated text"}; words spread evenly over each line
"""
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

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


def write_ass(words, path, y=1440):
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
            ev.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{{\\pos({W//2},{y})}}{' '.join(parts)}")
    Path(path).write_text(hdr + '\n'.join(ev) + '\n')


def write_srt(words, path):
    def t(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    lines = []
    for i, ch in enumerate(chunks(words, max_words=6), 1):
        lines.append(f"{i}\n{t(ch[0]['s'])} --> {t(ch[-1]['e'])}\n{' '.join(w['cap'] for w in ch)}\n")
    Path(path).write_text('\n'.join(lines))


def overlay_png(path, *, hook=None, title=None, cta=None, series=B.SERIES):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = B.pill(d, series, W // 2, 250, B.font(B.FONT_BOLD, 30))
    if hook:
        B.draw_rich(d, hook, B.font(B.FONT_BLACK, 70), 60, y + 30, W - 120)
    if cta:  # CTA replaces the title in the header so it never collides with captions
        d.rounded_rectangle([50, y + 20, W - 50, VID_Y - 12], radius=32, fill=B.ACCENT)
        B.draw_rich(d, cta, B.font(B.FONT_BLACK, 56), 90, y + 42, W - 180, color=B.BG, accent=B.BLUE)
    elif title:
        B.draw_rich(d, title, B.font(B.FONT_BLACK, 62), 60, y + 50, W - 120)
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('edl'); ap.add_argument('out')
    ap.add_argument('--clean', action='store_true')
    ap.add_argument('--translations'); ap.add_argument('--srt')
    a = ap.parse_args()
    edl = json.loads(Path(a.edl).read_text())
    src, segs = edl['source'], edl['segments']
    sw, sh = probe(src)
    words = merged_words(json.loads(Path(edl['transcript']).read_text()))
    wrt, total = retime(words, segs)
    if a.translations:
        wrt = translated_words(wrt, json.loads(Path(a.translations).read_text()))

    with tempfile.TemporaryDirectory() as td:
        inputs, fc, cat = [], [], ''
        for i, s in enumerate(segs):
            a0, a1 = s['a']; dur = a1 - a0; v0 = s.get('v') if s.get('v') is not None else a0
            side = int(min(sh, sw) / s.get('zoom', 1.0)) // 2 * 2
            x = int(min(max(0, s.get('cx', 0.5) * sw - side / 2), sw - side))
            y = int(min(max(0, s.get('cy', 0.5) * sh - side / 2), sh - side))
            inputs += ['-ss', f'{v0}', '-t', f'{dur}', '-i', src, '-ss', f'{a0}', '-t', f'{dur}', '-i', src]
            fc.append(f"[{2*i}:v]crop={side}:{side}:{x}:{y},scale={VID}:{VID}:flags=lanczos,fps=30,setsar=1,trim=duration={dur},setpts=PTS-STARTPTS[v{i}]")
            fc.append(f"[{2*i+1}:a]aresample=48000,atrim=duration={dur},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={max(0,dur-0.05)}:d=0.05[a{i}]")
            cat += f"[v{i}][a{i}]"
        fc.append(f"{cat}concat=n={len(segs)}:v=1:a=1[vc][ac]")
        n = 2 * len(segs)
        hook_png, title_png, cta_png = (os.path.join(td, f) for f in ('hook.png', 'title.png', 'cta.png'))
        if a.clean:
            overlay_png(title_png)
            inputs += ['-loop', '1', '-t', f'{total}', '-i', title_png]
            fc.append(f"color=c=0x{'%02X%02X%02X' % B.BG}:s={W}x{H}:d={total}:r=30[bg];[bg][vc]overlay=0:{VID_Y}[b1];[b1][{n}:v]overlay=0:0[vo]")
        else:
            ser = edl.get('series', B.SERIES)
            overlay_png(hook_png, hook=edl['hook'], series=ser); overlay_png(title_png, title=edl.get('title', edl['hook']), series=ser)
            overlay_png(cta_png, cta=edl['cta'], series=ser)
            ass = os.path.join(td, 'cap.ass'); write_ass(wrt, ass)
            inputs += ['-loop', '1', '-t', f'{total}', '-i', hook_png, '-loop', '1', '-t', f'{total}', '-i', title_png,
                       '-loop', '1', '-t', f'{total}', '-i', cta_png]
            cta_t = max(3.5, total - 4)
            fc.append(f"color=c=0x{'%02X%02X%02X' % B.BG}:s={W}x{H}:d={total}:r=30[bg];[bg][vc]overlay=0:{VID_Y}[b1];"
                      f"[b1][{n}:v]overlay=0:0:enable='lt(t,3.5)'[b2];[b2][{n+1}:v]overlay=0:0:enable='between(t,3.5,{cta_t})'[b3];"
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
