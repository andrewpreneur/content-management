#!/usr/bin/env python3
"""Build outputs/2026-11-07-vsl-a/manifest.json + README table from rendered files and specs."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import specs_vsla as S
OUT = S.OUT
DESC = {'A': ('Clean brand-kit edit: captions, punch-ins, lower third, motion cards', '16:9'),
        'V916': ('Clean edit, vertical (cards on top, face below)', '9:16'), 'V45': ('Clean edit, feed (cards on top, face below)', '4:5'),
        'H1': ('Hook test 1: cold open', '4:5'), 'H2': ('Hook test 2: cold open', '4:5'), 'H3': ('Hook test 3: cold open', '4:5'),
        'H1V': ('Hook test 1: cold open', '9:16'), 'H2V': ('Hook test 2: cold open', '9:16'), 'H3V': ('Hook test 3: cold open', '9:16'),
        'S916': ('Short ad cut', '9:16'), 'S45': ('Short ad cut', '4:5'),
        'M916': ('No face: original voice + motion graphics', '9:16'), 'M169': ('No face: original voice + motion graphics', '16:9'), 'M45': ('No face: original voice + motion graphics', '4:5'),
        'T45': ('No face, no voice: text + motion graphics + music', '4:5'), 'T916': ('No face, no voice: text + motion graphics + music', '9:16')}
SRCID = {'V1': '13qkVrK33SXyYZVcphpAlj9s0XOF3mLpT', 'V2': '1ZMXGDpYSC_yT2SHdfJC53KBvSWttjUmg', 'V3': '1-atbjEUHm2ctbPv9dR45pw-0tUvUKT1p', 'V4': '1SR6zSYC8bB84Bhgc-eG5S4oJmhcEKi_N'}
rows = []
for vid in ('V1', 'V2', 'V3', 'V4'):
    for f in sorted((OUT / vid).glob('*.mp4')):
        if '.prev' in f.name: continue
        var = f.stem.split('-', 1)[1].upper()
        try: d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout)
        except ValueError: continue  # still rendering
        desc, fmt = DESC.get(var, (var, ''))
        hook = ''
        if var[:2] in ('H1', 'H2', 'H3'):
            r, t = S.V[vid]['hooks'][var[:2]]; hook = t.replace('*', '')
            ws = [w['w'] for w in S.words_of(vid) if r[0] - 0.02 <= w['s'] < r[1]]
            desc += f' ("{" ".join(ws)}")'
        elif var.startswith('T'):
            c = S.TEXT[vid][0][1]; hook = ' '.join(c.get('lines') or [c.get('title', '')]).replace('*', '')
        else:
            hook = ' '.join(w['w'] for w in S.words_of(vid)[:9 if not var.startswith('S') else 9]) + '…'
        rows.append(dict(id=f.stem, video=vid, variant=var, desc=desc, format=fmt, length=round(d, 1), hook=hook,
                         source=f'VSL VIDEO {vid[1]} (Drive {SRCID[vid]})', file=f'render-drop/vsl-a:{vid}/{f.name}'))
json.dump(rows, open(sys.argv[1], 'w'), indent=1)
print(len(rows), 'rows')
