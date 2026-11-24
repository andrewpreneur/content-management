#!/usr/bin/env python3
"""Pack the job toolkits and publish them to the app's private Storage bucket "toolkit". Each job gets a 24 h link, so any
runner (Your Software Agent's Supercomputers, a customer's Claude Code, their own computer) can do it without this repo.
  longform.tar.gz  : long-form editing scripts + fonts + sound effects + SOP 12
  explainer.tar.gz : explainer render (split across machines) + setup + the three explainer skills + SOP 13
Run after changing any of these files:  python3 tools/publish_toolkit.py [pack.tar.gz ...]
"""
import importlib.util, io, tarfile, requests
from pathlib import Path
R = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ycs', R / 'tools/ycs_sync.py'); ycs = importlib.util.module_from_spec(spec); spec.loader.exec_module(ycs)
FILES = ['tools/longform_layout.py', 'tools/montage_intro.py', 'tools/drive_range_proxy.py', 'tools/drive_upload.py', 'tools/transcribe.py',
         'tools/sound_mix.py', 'docs/sops/12-longform-edits.md', 'vendor/motion-graphics/skills/sound-effects/MUSIC.md']
DIRS = ['tools/fonts', 'vendor/motion-graphics/skills/sound-effects/sfx/kit']

PACKS = {
    'longform.tar.gz': (FILES, DIRS, b"Your Content System job toolkit. Follow docs/sops/12-longform-edits.md. Needs ffmpeg, python3, numpy, requests, faster-whisper.\n"),
    'explainer.tar.gz': (['tools/explainer_render.mjs', 'tools/explainer_setup.sh', 'tools/explainer_measure.py', 'tools/explainer_qa.mjs', 'tools/explainer_data.py', 'tools/explainer_selftest.sh', 'tools/drive_upload.py', 'docs/sops/13-explainer-from-zip.md', 'styles/README.md'],
                         [], b"Your Content System explainer kit. Follow docs/sops/13-explainer-from-zip.md. Needs node 18+, ffmpeg, python3 + numpy/scipy/pillow (bash tools/explainer_setup.sh installs Playwright + Chromium).\n"),
}
# Style packs: one download each (styles/<id>/ -> style-<id>.tar.gz, unpacked as style/). Every video job links exactly one.
STYLES = sorted(p.name for p in (R / 'styles').iterdir() if p.is_dir()) if (R / 'styles').exists() else []
for _id in STYLES:
    PACKS[f'style-{_id}.tar.gz'] = ([], [], f"Style pack '{_id}'. Read STYLE.md, look at reference/, copy example/. See styles/README.md in the explainer kit.\n".encode())
SKILLS = ['explainer-default', 'explainer-engaging', 'explainer-high-energy']

def pack(name, files, dirs, readme):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as t:
        for f in files: t.add(R / f, arcname=f)
        for d in dirs: t.add(R / d, arcname=d)
        if name.startswith('style-'):
            t.add(R / 'styles' / name[len('style-'):-len('.tar.gz')], arcname='style')
        if name == 'explainer.tar.gz':
            for sk in SKILLS: t.add(R / 'vendor/motion-graphics/skills' / sk, arcname=f'skills/{sk}')
        ti = tarfile.TarInfo('README.txt'); ti.size = len(readme); t.addfile(ti, io.BytesIO(readme))
    return buf.getvalue()

if __name__ == '__main__':
    import sys
    only = sys.argv[1:] or list(PACKS)
    for name in only:
        data = pack(name, *PACKS[name])
        up = ycs.call('mutation', 'toolkitUploadUrl', {'name': name})
        r = requests.put(up['url'], data=data, headers={'Content-Type': 'application/gzip', 'x-upsert': 'true'}, timeout=300)
        r.raise_for_status()
        print(f'published {name} ({len(data) // 1024} KB)')
    # the list Chat shows (name + what it's for, from styles/README.md's table)
    import re, json
    rows = re.findall(r'^\| `([a-z0-9-]+)` \| ([^|]+) \| ([^|]+) \|', (R / 'styles' / 'README.md').read_text(), re.M)
    listing = json.dumps([{'id': i, 'name': n.strip(), 'useFor': u.strip(), 'file': f'style-{i}.tar.gz'} for i, n, u in rows if i in STYLES]).encode()
    up = ycs.call('mutation', 'toolkitUploadUrl', {'name': 'styles.json'})
    requests.put(up['url'], data=listing, headers={'Content-Type': 'application/json', 'x-upsert': 'true'}, timeout=60).raise_for_status()
    print('published styles.json:', ', '.join(i for i, _, _ in rows))
