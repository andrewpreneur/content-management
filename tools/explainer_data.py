#!/usr/bin/env python3
"""Write data.js for a walkthrough page (the medspa-emr-training example): measured targets + voiceover lines.

  python3 tools/explainer_data.py KIT_DIR LINES.json OUT/data.js
  python3 tools/explainer_data.py KIT_DIR --placeholder OUT/data.js     # no voice yet: timed stand-in lines (self-test)

KIT_DIR has targets.json (tools/explainer_measure.py). LINES.json = {key: {text, dur, words: [[word, start, end], ...]}},
keys intro, why, s1, s2, … outro, made with ElevenLabs /with-timestamps (one clip per line; see SOP 13).
The page reads window.TARGETS (by screenshot path) and window.LINES.
"""
import json, re, sys
from pathlib import Path


def placeholder(kit: Path):
    script = (kit / 'script.md').read_text() if (kit / 'script.md').exists() else ''
    says = re.findall(r'\*\*Say:\*\*\s*[“"](.+?)[”"]', script)
    rows = re.findall(r'^\|\s*(Intro card|Why|Outro card)\s*\|\s*(.+?)\s*\|', script, re.M)
    lines = {'intro': next((t for k, t in rows if k == 'Intro card'), 'Here is how it works.'),
             'why': next((t for k, t in rows if k == 'Why'), 'What this saves you.'),
             'outro': next((t for k, t in rows if k == 'Outro card'), "That's it.")}
    for i, t in enumerate(says or ['Step one.', 'Step two.', 'Step three.'], 1):
        lines[f's{i}'] = t
    out = {}
    for k, t in lines.items():
        ws = t.split(); dur = max(1.5, 0.36 * len(ws) + 0.3); step = (dur - 0.3) / max(1, len(ws))
        out[k] = {'text': t, 'dur': round(dur, 2), 'words': [[w, round(0.1 + i * step, 3), round(0.1 + (i + 1) * step, 3)] for i, w in enumerate(ws)]}
    return out


def main():
    a = sys.argv[1:]
    if len(a) != 3:
        print(__doc__); sys.exit(2)
    kit = Path(a[0])
    targets = json.loads((kit / 'targets.json').read_text())
    lines = placeholder(kit) if a[1] == '--placeholder' else json.loads(Path(a[1]).read_text())
    Path(a[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(a[2]).write_text('window.TARGETS=' + json.dumps(targets) + ';\nwindow.LINES=' + json.dumps(lines) + ';\n')
    print('wrote', a[2], f'({len(targets)} screenshots, {len(lines)} lines)')


if __name__ == '__main__':
    main()
