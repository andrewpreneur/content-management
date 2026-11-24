#!/usr/bin/env python3
"""remix.py: make the final video from a video project's layers, without re-rendering the picture.

  python3 tools/remix.py input.json out.mp4 [--work DIR]

input.json = what the app hands an export job: {"manifest": {...}, "urls": {"<file name>": "https://…"}}  (or a bare manifest
with files next to it). The manifest format is content-hq backend/supabase/functions/_shared/projectpure.ts:
  video (silent, caption-free render) · lines [{text, t, dur, file, words, muted, volume}] · music {src, volume, fadeIn, fadeOut}
  · sfx [{t, file, volume}] · captions {on, color, active, size, bottom, font, weight, maxWords} · mix {lufs, duckDb}
Voice lines are placed at their times and normalised; the music bed sits under them and ducks while anyone speaks; sound
effects ride on top; captions are burned from the word timings (active word in the accent colour); final loudness = mix.lufs.
"""
import json, os, subprocess, sys, tempfile, urllib.request
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
FONTS = KIT / 'tools' / 'fonts'


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'ffmpeg failed: {" ".join(cmd[:6])}…\n{p.stderr[-1500:]}')
    return p


def fetch(name, urls, base, work):
    """A layer's file: a link from urls, an https src, or a file next to input.json."""
    if not name:
        return None
    dst = work / ('dl_' + Path(name.split('?')[0]).name.replace(' ', '_'))
    if dst.exists():
        return dst
    src = urls.get(name) or (name if name.startswith('https://') else None)
    if src:
        urllib.request.urlretrieve(src, dst)
        return dst
    local = base / name
    if local.exists():
        return local
    sys.exit(f'missing layer file: {name}')


def ass_color(hexs):
    h = hexs.lstrip('#')
    return f'&H00{h[4:6]}{h[2:4]}{h[0:2]}&'.upper()


def ass_time(t):
    t = max(0.0, t); return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def phrases(m):
    out = []
    cap = m['captions']
    for l in sorted([x for x in m['lines'] if not x.get('muted')], key=lambda x: x['t']):
        cur = []
        for w in l.get('words', []):
            cur.append({'w': w['w'], 's': l['t'] + w['s'], 'e': l['t'] + w['e']})
            if len(cur) >= cap.get('maxWords', 6) or (w['w'][-1:] in '.,:!?' and len(cur) >= 2):
                out.append(cur); cur = []
        if cur:
            out.append(cur)
    res = [{'t0': p[0]['s'] - 0.08, 't1': p[-1]['e'] + 0.3, 'words': p} for p in out]
    for a, b in zip(res, res[1:]):
        a['t1'] = min(a['t1'], b['t0'])
    return res


def captions_ass(m, W, H):
    c = m['captions']
    scale = H / 1080
    fs = round(c.get('size', 30) * scale * 1.18); mv = round(c.get('bottom', 62) * scale)
    bold = -1 if c.get('weight', 500) >= 650 else 0
    font = c.get('font', 'Inter Display') + (' Medium' if 450 <= c.get('weight', 500) < 600 and 'Medium' not in c.get('font', '') else '')
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{fs},{ass_color(c.get('color', '#4b5563'))},&H00FFFFFF,&H00000000,&H00000000,{bold},0,0,0,100,100,0,0,1,0,0,2,{W // 10},{W // 10},{mv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    act, base = ass_color(c.get('active', '#175892')), ass_color(c.get('color', '#4b5563'))
    ev = []
    for p in phrases(m):
        ws = p['words']
        # one event per active word (plus the gaps), so the highlight follows the voice
        marks = [p['t0']] + [w['s'] for w in ws[1:]] + [p['t1']]
        for k in range(len(ws)):
            a, b = marks[k], marks[k + 1]
            if b - a < 0.02:
                continue
            txt = ' '.join((f'{{\\c{act}}}{x["w"]}{{\\c{base}}}' if j == k else x['w']) for j, x in enumerate(ws))
            ev.append(f'Dialogue: 1,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{txt}')
    return head + '\n'.join(ev) + '\n'


def main():
    args = sys.argv[1:]
    work_dir = None
    if '--work' in args:
        i = args.index('--work'); work_dir = args[i + 1]; del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    inp, out = Path(args[0]), Path(args[1])
    d = json.loads(inp.read_text())
    m, urls = (d['manifest'], d.get('urls', {})) if 'manifest' in d else (d, {})
    work = Path(work_dir or tempfile.mkdtemp(prefix='remix_')); work.mkdir(parents=True, exist_ok=True)
    base = inp.resolve().parent
    dur = float(m['duration'])

    video = fetch(m['video'], urls, base, work)
    probe = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', str(video)]).stdout)['streams'][0]
    W, H = int(probe['width']), int(probe['height'])

    ins, fl, n = [], [], 0
    def add(path, t, vol, tag):
        nonlocal n
        ins.extend(['-i', str(path)]); ms = int(max(0, t) * 1000)
        fl.append(f'[{n}:a]aresample=48000,volume={vol:.3f},adelay={ms}|{ms}[{tag}{n}]'); n += 1
        return f'[{tag}{n - 1}]'
    voice = [add(fetch(l['file'], urls, base, work), l['t'], float(l.get('volume', 1)), 'v') for l in m['lines'] if not l.get('muted')]
    fx = [add(fetch(s['file'], urls, base, work), s['t'], float(s['volume']), 'x') for s in m.get('sfx', [])]
    mu = m.get('music')
    lufs = float(m.get('mix', {}).get('lufs', -16))
    parts = []
    if voice:
        fl.append(''.join(voice) + f'amix=inputs={len(voice)}:normalize=0,apad,atrim=0:{dur},loudnorm=I={lufs}:TP=-2:LRA=7,asplit=2[voice][vkey]')
        parts.append('[voice]')
    if fx:
        fl.append(''.join(fx) + f'amix=inputs={len(fx)}:normalize=0,apad,atrim=0:{dur}[fx]'); parts.append('[fx]')
    if mu:
        ins.extend(['-stream_loop', '-1', '-i', str(fetch(mu['src'], urls, base, work))]); mi = n; n += 1
        fo = max(0.0, dur - float(mu.get('fadeOut', 2)))
        fl.append(f'[{mi}:a]aresample=48000,atrim=0:{dur},volume={float(mu["volume"]):.3f},afade=t=in:d={float(mu.get("fadeIn", 1))},afade=t=out:st={fo}:d={float(mu.get("fadeOut", 2))}[bed]')
        if voice:
            ratio = max(1.5, float(m.get('mix', {}).get('duckDb', 10)) / 2.5)
            fl.append(f'[bed][vkey]sidechaincompress=threshold=0.04:ratio={ratio:.1f}:attack=30:release=400[duck]'); parts.insert(0, '[duck]')
        else:
            parts.insert(0, '[bed]')
    elif voice:
        fl.append('[vkey]anullsink')
    if not parts:
        fl.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{dur}[a]')
    else:
        fl.append(''.join(parts) + f'amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.89,loudnorm=I={lufs}:TP=-1.5:LRA=9[a]')
    ins.extend(['-i', str(video)]); vi = n

    vf = 'null'
    if m.get('captions', {}).get('on', True) and any(l.get('words') for l in m['lines']):
        ass = work / 'captions.ass'; ass.write_text(captions_ass(m, W, H))
        vf = f"ass={ass}:fontsdir={FONTS}"
    fl.append(f'[{vi}:v]{vf}[v]')
    out.parent.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[v]', '-map', '[a]',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
         '-movflags', '+faststart', '-t', f'{dur}', str(out)])
    print('wrote', out, f'({dur:.1f} s, {len(voice)} voice lines, {len(fx)} sound effects, music: {mu["title"] if mu else "none"})')


if __name__ == '__main__':
    main()
