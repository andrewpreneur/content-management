#!/usr/bin/env python3
"""Build manifest.csv + the outputs table in README from specs.json and the QA results."""
import json, csv, os, sys
H = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(f'{H}/specs.json')); qa = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
rows = []
for a in S['ads']:
    h = a['hook']
    hook = (h['card'] if h['type'] == 'card' else (h['text'] + (' / ' + h['sub'] if h.get('sub') else ''))).replace('*', '')
    for asp in a['aspect']:
        n = f"{a['id']}-{asp}"; q = qa.get(n, {})
        src = {'mark': 'mark (1DO6aV…)', 'lee': 'lee (1lYYpK…)', 'ben': 'ben (1yf2DD…)', 'jessica': 'jessica (1xBZ3x…)',
               'tania': 'taniatestimonial.mp4 (1FfSs6…)'}.get(a['person']) or ('supercut: ' + ' + '.join(dict.fromkeys(x[0] for x in a['segs'])))
        rows.append({'file': f'{a["id"]}/{n}.mp4', 'id': a['id'], 'person': a['person'], 'format': '9:16' if asp == '916' else '4:5',
                     'class': a['class'], 'length_s': q.get('dur', ''), 'hook_type': h['type'], 'hook': hook,
                     'topline': a.get('topline', ''), 'moments': a['moments'], 'source': src,
                     'segments': ' '.join((f'{x[0]}@' if len(x) == 3 else '') + f'{x[-2]:.2f}-{x[-1]:.2f}' for x in a['segs']),
                     'music': S['music'][a['music']]['credit'], 'lufs': q.get('lufs', ''), 'peak_dbfs': q.get('peak', '')})
with open(f'{H}/manifest.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
md = ['| id | format | length | hook type | hook | source |', '|---|---|---|---|---|---|']
for r in rows:
    md.append(f"| `{r['file']}` | {r['format']} | {r['length_s']}s ({r['class']}) | {r['hook_type']} | {r['hook']} | {r['source']} |")
open(f'{H}/outputs-table.md', 'w').write('\n'.join(md) + '\n')
print(len(rows), 'rows')
