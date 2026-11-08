#!/usr/bin/env python3
"""Cut A/B test clips for the Style Picker from docs/brand-video/library/*.json best_segments.

Usage: python3 tools/style_clips.py OUT_DIR [MIN_FIT]
  - keeps references with saassuite_fit >= MIN_FIT (default 3)
  - cuts each best_segment to OUT_DIR/<ref>__s<k>.mp4 (720px on the long side, H.264 CRF 27, AAC 96k) + .jpg poster
  - writes OUT_DIR/clips.todo.json (clip list without video urls; fill urls after the asset upload)
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB, REFS = ROOT / 'docs/brand-video/library', Path('/home/user/work/refs')


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    min_fit = float(sys.argv[2]) if len(sys.argv) > 2 else 3
    clips = []
    for f in sorted(LIB.glob('*.json')):
        d = json.loads(f.read_text())
        if float(d.get('saassuite_fit', 0)) < min_fit:
            continue
        src = REFS / f'{f.stem}.mp4'
        for k, s in enumerate(d.get('best_segments', [])):
            a, b = float(s['start']), min(float(s['end']), float(s['start']) + 6.5)
            cid = f'{f.stem}__s{k + 1}'
            mp4, jpg = out / f'{cid}.mp4', out / f'{cid}.jpg'
            if not mp4.exists():
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-i', str(src), '-t', str(b - a),
                                '-vf', "scale='if(gt(iw,ih),min(1280,iw),-2)':'if(gt(iw,ih),-2,min(1280,ih))'",
                                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27', '-pix_fmt', 'yuv420p',
                                '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(mp4)], check=True)
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str((b - a) / 2), '-i', str(mp4), '-frames:v', '1',
                                '-vf', 'scale=480:-2', '-q:v', '5', str(jpg)], check=True)
            clips.append(dict(id=cid, ref=f.stem, title=d.get('title', f.stem), category=d.get('category', ''),
                              fit=d.get('saassuite_fit'), what=s.get('what', ''), tests=s.get('tests', []),
                              start=a, end=b, file=mp4.name, poster=f'p/{jpg.name}'))
    (out / 'clips.todo.json').write_text(json.dumps(dict(clips=clips), indent=1))
    print(len(clips), 'clips from', len({c['ref'] for c in clips}), 'references')


if __name__ == '__main__':
    main()
