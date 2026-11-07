#!/usr/bin/env python3
"""Re-roll paragraphs that fail QC (wrong words or pause > 0.9s) with new seeds, up to N tries.
  python3 fix.py <voice_dir>...   (reads qc.json + p??.json settings; script = scripts/<name before '-'>.txt)"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import qc_voice
HERE = Path(__file__).parent.parent
for d in map(Path, sys.argv[1:]):
    nm = d.name.split('-')[0]; script = HERE / 'scripts' / (nm + '.txt')
    if not script.exists(): script = HERE / 'scripts/teasers' / (nm + '.txt')
    for k in range(1, 5):
        rows = json.load(open(d / 'qc.json'))
        bad = [int(r['p'][1:]) for r in rows if 'WORDS' in r['flags'] or 'PAUSE' in r['flags']]
        if not bad: break
        meta = json.load(open(d / f'p{bad[0]:02d}.json')); s = meta['settings']
        subprocess.run(['python3', str(HERE / 'src/tts.py'), str(script), meta['voice'], str(d), '--only', ','.join(map(str, bad)),
                        '--stability', str(s['stability']), '--similarity', str(s['similarity_boost']), '--style', str(s['style']),
                        '--speed', str(s['speed']), '--seed', str(100 * k + 3)], check=True, capture_output=True)
        qc_voice.qc_dir(d)
