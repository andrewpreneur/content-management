#!/usr/bin/env python3
"""project_push.py: save a finished video as an editable project in Your Content System (the video editor).

  python3 tools/project_push.py DIR [--root UUID]      # DIR holds manifest.json + every file it names

manifest.json = content-hq _shared/projectpure.ts format: video (silent, caption-free render), page, scenes, voice, lines (+ word
timings), music, sfx, captions, mix, pronounce. Brand = env YCS_BRAND (default andrewpreneurship). --root adds a new version to an
existing project. Prints the project id.
"""
import json, sys, uuid, importlib.util, requests
from pathlib import Path

R = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ycs', R / 'tools/ycs_sync.py'); ycs = importlib.util.module_from_spec(spec); spec.loader.exec_module(ycs)

def main():
    a = sys.argv[1:]
    root = None
    if '--root' in a: i = a.index('--root'); root = a[i + 1]; del a[i:i + 2]
    d = Path(a[0]); m = json.loads((d / 'manifest.json').read_text())
    root = root or str(uuid.uuid4())
    names = [m.get('video'), m.get('page'), (m.get('music') or {}).get('src')] + [l['file'] for l in m.get('lines', [])] + [s['file'] for s in m.get('sfx', [])]
    names = [n for n in dict.fromkeys(names) if n and not n.startswith('https://')]
    for n in names:
        up = ycs.call('mutation', 'projectUploadUrl', {'root': root, 'name': n})
        requests.put(up['url'], data=(d / n).read_bytes(), headers={'x-upsert': 'true'}, timeout=300).raise_for_status()
    # the page's own files (scripts, fonts, logos) go along so a scene change can re-render it
    extra = [p for p in d.iterdir() if p.is_file() and p.name not in names and p.name != 'manifest.json' and p.suffix in ('.js', '.png', '.jpg', '.svg', '.ttf', '.woff', '.woff2', '.json', '.css', '.ogg', '.mp3', '.wav')]
    for p in extra:
        up = ycs.call('mutation', 'projectUploadUrl', {'root': root, 'name': p.name})
        requests.put(up['url'], data=p.read_bytes(), headers={'x-upsert': 'true'}, timeout=300).raise_for_status()
    row = ycs.call('mutation', 'projectCreate', {'brandKey': ycs.BRAND if hasattr(ycs, 'BRAND') else 'andrewpreneurship', 'root': root, 'manifest': m})
    print('project', row['id'], 'version', row['version'], f'({len(names)} layers + {len(extra)} page files)')

if __name__ == '__main__':
    main()
