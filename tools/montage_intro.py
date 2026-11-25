#!/usr/bin/env python3
"""Montage-style intro for a long-form video (podcasts first, works for any talking video).

Picks the most "clippable" short moments from the transcript (questions, bold claims, numbers, stakes, punchy lines),
cuts them into a fast hook montage with punch-in zooms and sound hits, lays your music under the voice (ducked),
optionally burns captions in your style, and ends on a title card. Intensity (1-5) sets how short and fast the cuts are.

  python3 tools/montage_intro.py --video SRC.mp4 --transcript tx.json --out intro.mp4 \
      [--length 45] [--intensity 3] [--captions | --no-captions] [--music track.mp3 | --mixkit 130] \
      [--style style.json] [--title "Video title"] [--avoid 0-40] [--height 1080] [--prepend-to SRC.mp4 --full out_full.mp4]

transcript.json: tools/transcribe.py output (segments with word timings 's'/'e' or 'start'/'end').
style.json (optional, from the app's brand styles): {"palette": {"background": "#0B0B0F", "ink": "#FFFFFF", "accent": "#7C5CFF"},
  "fonts": {"display": "InterTight-ExtraBold"}}. Default: dark background, white text, violet accent, Inter Tight ExtraBold.
--avoid start-end: skip moments in that range (e.g. the intro you're replacing).
Writes OUT, OUT.picks.json (the moments used, with times and why) and, with --prepend-to, the full video (montage + video).
Music: your file, or a Mixkit track id (downloaded at run time, Mixkit Stock Music Free License; never committed).
"""
import argparse, json, os, re, subprocess, tempfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SFX = ROOT / 'vendor/motion-graphics/skills/sound-effects/sfx'
FONTS = ROOT / 'tools/fonts'
STAKES = re.compile(r"\b(fail\w*|lost|lose|never|always|first|best|worst|biggest|mistake\w*|secret|truth|why|how|money|\$\d[\d,.]*\w*|"
                    r"\d[\d,.]*\s?(k|m|million|thousand|percent|%)|quit|fired|scared|afraid|hard|insane|crazy|changed|wish|regret|"
                    r"nobody|everyone|problem|wrong|right now|actually|honestly|real(ly)?|biggest|only|stop|start)\b", re.I)
DEPENDENT = {'and', 'but', 'so', 'because', 'which', 'that', 'it', "it's", 'they', 'he', 'she', 'this', 'these', 'those', 'yeah',
             'yes', 'um', 'uh', 'also', 'then', 'or', 'like', 'right', 'exactly', 'oh', 'okay', 'mm', 'well'}
FILLER = re.compile(r"\b(um+|uh+|like|you know|kind of|sort of|i mean)\b", re.I)
# intensity → (target bite seconds, zoom amount, sound on every cut)
LEVEL = {1: (6.5, 1.00, False), 2: (5.0, 1.04, False), 3: (3.8, 1.07, True), 4: (3.0, 1.10, True), 5: (2.4, 1.14, True)}


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode: raise SystemExit('ffmpeg failed: ' + r.stderr[-1500:])


def probe(src):
    o = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate:format=duration',
                                   '-of', 'json', src], capture_output=True, text=True).stdout)
    s = o['streams'][0]; n, d = s['r_frame_rate'].split('/')
    return int(s['width']), int(s['height']), float(n) / float(d), float(o['format']['duration'])


def words_of(tx):
    out = []
    for seg in tx['segments']:
        for w in seg.get('words') or []:
            out.append({'w': w.get('w') or w.get('word', ''), 's': float(w.get('s', w.get('start', 0))), 'e': float(w.get('e', w.get('end', 0)))})
    return out


def sentences(words):
    """Split into sentences on . ? ! and long pauses."""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        gap = words[i + 1]['s'] - w['e'] if i + 1 < len(words) else 9
        if re.search(r'[.?!]["”]?$', w['w'].strip()) or gap > 0.8:
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out


def score(sent):
    text = ' '.join(w['w'] for w in sent).strip()
    n = len(sent); dur = sent[-1]['e'] - sent[0]['s']
    first = re.sub(r'[^\w\']', '', sent[0]['w'].lower())
    s = 0.0; why = []
    if text.endswith('?'): s += 3; why.append('question')
    if text.endswith('!'): s += 1.5; why.append('exclaims')
    k = len(STAKES.findall(text));  s += min(k, 3) * 1.2
    if k: why.append('stakes')
    if re.search(r'\d', text): s += 1; why.append('numbers')
    if 4 <= n <= 14: s += 1.5; why.append('punchy')
    if first in DEPENDENT: s -= 2.5
    s -= len(FILLER.findall(text)) * 1.2
    if dur < 1.2 or dur > 9: s -= 4
    return s, text, why


def pick(words, total, length, intensity, avoid, ok=None):
    bite = LEVEL[intensity][0]
    want = max(3, round((length - 3) / bite))
    cands = []
    for sent in sentences(words):
        a, b = sent[0]['s'], sent[-1]['e']
        if avoid and a < avoid[1] and b > avoid[0]: continue
        sc, text, why = score(sent)
        # trim long sentences to the first ~bite*1.6 seconds, ending on a word
        if b - a > bite * 1.6:
            keep = [w for w in sent if w['e'] - a <= bite * 1.6]
            if len(keep) < 3: continue
            sent, b = keep, keep[-1]['e']; text = ' '.join(w['w'] for w in keep) + '…'; sc -= 0.5
        cands.append({'start': round(max(0, a - 0.08), 2), 'end': round(min(total, b + 0.12), 2), 'text': text, 'score': round(sc, 2), 'why': why,
                      'words': [{'w': w['w'], 's': round(w['s'] - a + 0.08, 2), 'e': round(w['e'] - a + 0.08, 2)} for w in sent]})
    cands.sort(key=lambda c: -c['score'])
    chosen = []
    for c in cands:
        if c['score'] < 1: break
        if any(abs(c['start'] - x['start']) < max(20, total / 60) for x in chosen): continue  # spread through the video
        if ok and not ok(c): continue  # e.g. a shared screen instead of faces
        chosen.append(c)
        if len(chosen) >= want or sum(x['end'] - x['start'] for x in chosen) >= length - 3: break
    # order: open on a question if there is one, end on the strongest non-question line, the rest by time
    qs = [c for c in chosen if 'question' in c['why']]
    opener = max(qs, key=lambda c: c['score']) if qs else None
    rest = [c for c in chosen if c is not opener]
    closer = max(rest, key=lambda c: c['score']) if rest else None
    middle = sorted([c for c in rest if c is not closer], key=lambda c: c['start'])
    return [c for c in [opener, *middle, closer] if c]


def hexc(h, a=0):
    h = h.lstrip('#'); return f'&H{a:02X}{h[4:6]}{h[2:4]}{h[0:2]}'.upper()


def ass_for(bites, W, H, style, karaoke):
    ink, acc = style['palette'].get('ink', '#FFFFFF'), style['palette'].get('accent', '#7C5CFF')
    font = style['fonts'].get('display', 'Inter Tight ExtraBold').replace('InterTight-ExtraBold', 'Inter Tight ExtraBold')
    size = int(H * 0.075)
    head = ['[Script Info]', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}', '', '[V4+ Styles]',
            'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
            f'Style: Cap,{font},{size},{hexc(ink)},{hexc(acc)},&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{max(3, size // 14)},2,2,80,80,{int(H * 0.09)},1',
            '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    t = lambda x: f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}'
    ev, off = [], 0.0
    for b in bites:
        ws = b['words']
        # 3-5 words per caption line
        for i in range(0, len(ws), 4):
            chunk = ws[i:i + 4]; a = off + chunk[0]['s']; e = off + chunk[-1]['e'] + 0.05
            if karaoke:
                txt = ''.join(f"{{\\kf{max(1, int((w['e'] - w['s']) * 100))}}}{w['w'].upper()} " for w in chunk)
            else:
                txt = ' '.join(w['w'].upper() for w in chunk)
            ev.append(f'Dialogue: 0,{t(a)},{t(e)},Cap,,0,0,0,,{txt.strip()}')
        off += b['end'] - b['start']
    return '\n'.join(head + ev) + '\n'


def house_ass(bites, W, H):
    """Captions in THE house look (tools/house_captions.py): white, no box, spoken word violet, sentence case."""
    from house_captions import captions_ass, words_to_phrases
    words, off = [], 0.0
    for b in bites:
        for w in b["words"]:
            words.append({"w": w["w"], "t0": off + w["s"], "t1": off + w["e"]})
        off += b["end"] - b["start"]
    return captions_ass(words_to_phrases(words), W, H)


def is_screen(video, t, limit=0.15):
    """True when the frame at t is mostly a shared screen/document: > 15% of it is bright AND flat (pages, app UI).
    Calibrated on the Live Coaching call (Nov 25): face moments 0.03-0.11, shared docs/apps 0.17-0.39."""
    import numpy as np
    W, H = 192, 108
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{max(0, t):.2f}', '-i', video, '-frames:v', '1', '-vf', f'scale={W}:{H}',
                          '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    if len(raw) < W * H: return False
    g = np.frombuffer(raw[:W * H], np.uint8).reshape(H, W).astype(np.int16)
    blk = g[:H // 6 * 6, :W // 6 * 6].reshape(H // 6, 6, -1, 6)
    return float(((blk.std(axis=(1, 3)) < 4) & (blk.mean(axis=(1, 3)) > 170)).mean()) > limit


def mixkit(track_id, dest):
    url = f'https://assets.mixkit.co/music/{int(track_id)}/{int(track_id)}.mp3'
    urllib.request.urlretrieve(url, dest); return dest


def stream_info(src):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', src], capture_output=True, text=True).stdout)
    v = next(x for x in j['streams'] if x['codec_type'] == 'video'); a = next((x for x in j['streams'] if x['codec_type'] == 'audio'), None)
    return v, a


def fast_prepend(montage, video, full):
    v, a = stream_info(video)
    enc = {'hevc': ['libx265', '-x265-params', 'log-level=error', '-tag:v', 'hvc1'], 'h264': ['libx264']}.get(v['codec_name'])
    if not enc or not a: raise RuntimeError(f"can't match codec {v['codec_name']}")
    tmp = Path(tempfile.mkdtemp(prefix='prepend_'))
    m2 = tmp / 'montage_match.mp4'
    run(['ffmpeg', '-y', '-i', montage, '-vf', f"scale={v['width']}:{v['height']}:flags=lanczos,setsar=1,fps={v['r_frame_rate']}",
         '-c:v', *enc, '-preset', 'medium', '-crf', '16', '-pix_fmt', v.get('pix_fmt', 'yuv420p'), '-video_track_timescale', str(int(v.get('time_base', '1/90000').split('/')[1])),
         '-c:a', a['codec_name'] if a['codec_name'] in ('aac',) else 'aac', '-b:a', '320k', '-ar', a.get('sample_rate', '48000'), '-ac', str(a.get('channels', 2)), str(m2)])
    # join as MPEG-TS so each part keeps its own decoder settings in-band, then wrap as MP4 (hev1/avc3 tag = in-band headers)
    bsf = 'hevc_mp4toannexb' if v['codec_name'] == 'hevc' else 'h264_mp4toannexb'
    parts = []
    for i, x in enumerate((str(m2), video)):
        ts = tmp / f'p{i}.ts'
        run(['ffmpeg', '-y', '-i', x, '-map', '0:v:0', '-map', '0:a:0', '-c', 'copy', '-bsf:v', bsf, '-f', 'mpegts', str(ts)]); parts.append(str(ts))
    lst = tmp / 'parts.txt'; lst.write_text(''.join(f"file '{x}'\n" for x in parts))
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', '-tag:v', 'hev1' if v['codec_name'] == 'hevc' else 'avc3',
         '-bsf:a', 'aac_adtstoasc', '-movflags', '+faststart', full])
    # every frame must decode
    err = subprocess.run(['ffmpeg', '-v', 'error', '-i', full, '-f', 'null', '-'], capture_output=True, text=True).stderr.strip()
    if err: raise RuntimeError('decode check failed: ' + err[:300])
    d_full = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', full], capture_output=True, text=True).stdout.strip())
    d_exp = sum(float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', x], capture_output=True, text=True).stdout.strip()) for x in (str(m2), video))
    if abs(d_full - d_exp) > 1.5: raise RuntimeError(f'joined length {d_full:.1f}s, expected {d_exp:.1f}s')


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--video', required=True); a.add_argument('--transcript', required=True); a.add_argument('--out', required=True)
    a.add_argument('--length', type=float, default=45); a.add_argument('--intensity', type=int, default=3, choices=[1, 2, 3, 4, 5])
    a.add_argument('--captions', dest='captions', action='store_true', default=True); a.add_argument('--no-captions', dest='captions', action='store_false')
    a.add_argument('--music'); a.add_argument('--mixkit', type=int); a.add_argument('--music-db', type=float, default=-15)
    a.add_argument('--style'); a.add_argument('--title', default=''); a.add_argument('--avoid', default='')
    a.add_argument('--height', type=int, default=0, help='output height (default: same as the video)')
    a.add_argument('--prepend-to'); a.add_argument('--full')
    a.add_argument('--tiles', help='call grid: "x,y,w,h,faceX;..." each person cropped around the face, side by side (no call UI)')
    a.add_argument('--crops', help='JSON {"<bite start seconds>": "x,y,w,h,faceX;..."}: a face crop per clip when the call layout changes (from --plan-only + one frame per clip)')
    a.add_argument('--plan-only', action='store_true', help='write the picks (montage.picks.json) and one frame per pick, render nothing')
    a.add_argument('--allow-screens', action='store_true', help='keep moments where a screen/document is shown (default: faces only)')
    o = a.parse_args()

    W0, H0, fps, total = probe(o.video)
    H = o.height or H0; W = round(W0 * H / H0 / 2) * 2
    style = {'palette': {'background': '#0B0B0F', 'ink': '#FFFFFF', 'accent': '#7C5CFF'}, 'fonts': {'display': 'InterTight-ExtraBold'}}
    if o.style:
        s = json.loads(Path(o.style).read_text()); style['palette'].update(s.get('palette') or {}); style['fonts'].update(s.get('fonts') or {})
    avoid = tuple(float(x) for x in o.avoid.split('-')) if o.avoid else None
    faces_only = None if o.allow_screens else (lambda c: not is_screen(o.video, (c['start'] + c['end']) / 2))
    bites = pick(words_of(json.loads(Path(o.transcript).read_text())), total, o.length, o.intensity, avoid, faces_only)
    if not bites: raise SystemExit('No strong moments found in the transcript.')
    crops = json.loads(Path(o.crops).read_text()) if o.crops else {}
    if o.plan_only:
        Path(o.out + '.picks.json').write_text(json.dumps(bites, indent=1))
        for b in bites:
            run(['ffmpeg', '-y', '-v', 'error', '-ss', f"{(b['start'] + b['end']) / 2:.2f}", '-i', o.video, '-frames:v', '1', f"{o.out}.pick-{b['start']:.2f}.jpg"])
        print(json.dumps({'picks': len(bites), 'frames': f'{o.out}.pick-<start>.jpg'})); return
    bite_s, zoom, sfx_every = LEVEL[o.intensity]
    tmp = Path(tempfile.mkdtemp(prefix='montage_'))
    enc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', f'{fps:.3f}', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2']

    # 1. cut each bite, alternating a slow punch-in zoom
    parts = []
    for i, b in enumerate(bites):
        d = b['end'] - b['start']; z = zoom if (i % 2 == 1 or o.intensity >= 4) else 1.0
        vf = f'scale={W}:{H}:flags=lanczos,setsar=1'
        if z > 1.0:
            vf = (f"scale={W * 2}:{H * 2}:flags=lanczos,zoompan=z='1+({z - 1:.3f})*on/({max(1, int(d * fps))})':d=1:"
                  f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps:.3f},setsar=1")
        p = tmp / f'b{i:02d}.mp4'
        tl = crops.get(f"{b['start']:.2f}") or crops.get(str(b['start'])) or o.tiles
        if tl:   # a call: faces side by side, the call's own interface never shows
            from intro_edit import parse_tiles, split_filter
            fc = split_filter(parse_tiles(tl), z if z > 1.0 else 1.0, W, H, f'{fps:.3f}')
            run(['ffmpeg', '-y', '-ss', str(b['start']), '-i', o.video, '-t', f'{d:.2f}', '-filter_complex', fc,
                 '-af', 'afade=t=in:d=0.03,afade=t=out:st=%.2f:d=0.06' % max(0, d - 0.06), *enc, str(p)])
            parts.append(p); continue
        run(['ffmpeg', '-y', '-ss', str(b['start']), '-i', o.video, '-t', f'{d:.2f}', '-vf', vf,
             '-af', 'afade=t=in:d=0.03,afade=t=out:st=%.2f:d=0.06' % max(0, d - 0.06), *enc, str(p)])
        parts.append(p)

    # 2. title card (style colours, video title), with a hit
    card_d = 2.6 if o.title else 0
    if o.title:
        font = next((f for f in [FONTS / 'InterDisplay-Bold.ttf', FONTS / 'InterDisplay-SemiBold.ttf'] if f.exists()), FONTS / 'InterTight-ExtraBold.ttf')
        title = o.title.replace("'", '’').replace(':', '\\:')
        fs = int(H * (0.085 if len(o.title) < 28 else 0.06))
        p = tmp / 'card.mp4'
        run(['ffmpeg', '-y', '-f', 'lavfi', '-i', f"color=c={style['palette']['background']}:s={W}x{H}:r={fps:.3f}:d={card_d}",
             '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo', '-t', str(card_d),
             '-vf', (f"drawtext=fontfile={font}:text='{title}':fontcolor=white:fontsize={fs}:x=(w-text_w)/2:y=(h-text_h)/2-h*0.04,"
                     f"fade=t=in:st=0:d=0.25"), *enc, str(p)])
        parts.append(p)

    # 3. join
    lst = tmp / 'list.txt'; lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    joined = tmp / 'joined.mp4'
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(joined)])
    dur = sum(b['end'] - b['start'] for b in bites) + card_d

    # 4. captions
    vchain = 'null'
    if o.captions:
        ass = tmp / 'caps.ass'; ass.write_text(house_ass(bites, W, H))   # locked house look, never the brand style's ink/fonts
        vchain = f"subtitles={ass}:fontsdir={FONTS}"

    # 5. sound: music ducked under the voice, a hit/whoosh on cuts, a riser into the title card
    music = o.music or (mixkit(o.mixkit, str(tmp / 'music.mp3')) if o.mixkit else None)
    ins = ['-i', str(joined)]; fc = []; mix = ['[0:a]']; nin = 1
    cuts = []; t = 0.0
    for b in bites[:-1]:
        t += b['end'] - b['start']; cuts.append(t)
    sfx = []
    if sfx_every: sfx += [(c - 0.05, SFX / 'kit/whoosh.ogg', -14) for c in cuts]
    if o.title: sfx.append((dur - card_d, SFX / 'kit/impact.ogg', -8))
    for j, (at, f, db) in enumerate(sfx):
        if not Path(f).exists(): continue
        ins += ['-i', str(f)]; k = nin; nin += 1
        fc.append(f'[{k}:a]volume={db}dB,adelay={int(max(0, at) * 1000)}|{int(max(0, at) * 1000)},apad=whole_dur={dur:.2f}[s{j}]'); mix.append(f'[s{j}]')
    if music:
        ins += ['-stream_loop', '-1', '-i', music]; k = nin; nin += 1
        fc.append(f'[{k}:a]volume={o.music_db}dB,atrim=0:{dur:.2f},afade=t=out:st={max(0, dur - 1.2):.2f}:d=1.2[mus]')
        fc.append('[0:a]asplit=2[v1][v2]'); mix[0] = '[v1]'
        fc.append('[mus][v2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=250[duck]'); mix.append('[duck]')
    fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,loudnorm=I=-16:TP=-2:LRA=9[aout]")
    fc.append(f'[0:v]{vchain}[vout]')
    run(['ffmpeg', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-t', f'{dur:.2f}', *enc, o.out])

    picks = {'video': o.video, 'length': round(dur, 2), 'intensity': o.intensity, 'captions': o.captions, 'music': o.music or (f'mixkit:{o.mixkit}' if o.mixkit else None),
             'style': style, 'title': o.title, 'bites': [{k: b[k] for k in ('start', 'end', 'text', 'why', 'score')} for b in bites]}
    Path(o.out + '.picks.json').write_text(json.dumps(picks, indent=1))
    print(json.dumps({'out': o.out, 'seconds': round(dur, 2), 'bites': len(bites)}))

    # 6. optional: montage + the full video. Fast path: re-encode only the montage to match the video exactly
    # (codec, size, fps, pixel format, audio rate), then join with stream copy, so the long video is never re-encoded.
    if o.prepend_to and o.full:
        try:
            fast_prepend(o.out, o.prepend_to, o.full)
            print(json.dumps({'full': o.full, 'method': 'stream copy'})); return
        except Exception as e:
            print(json.dumps({'fast_prepend_failed': str(e)[:300]}))
        run(['ffmpeg', '-y', '-i', o.out, '-i', o.prepend_to, '-filter_complex',
             f'[1:v]scale={W}:{H}:flags=lanczos,setsar=1,fps={fps:.3f}[v1];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];'
             f'[0:v][0:a][v1][a1]concat=n=2:v=1:a=1[v][a]', '-map', '[v]', '-map', '[a]', *enc, o.full])
        print(json.dumps({'full': o.full}))


if __name__ == '__main__':
    main()
