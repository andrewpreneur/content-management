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
    'explainer.tar.gz': (['tools/explainer_render.mjs', 'tools/explainer_setup.sh', 'tools/drive_upload.py', 'docs/sops/13-explainer-from-zip.md'],
                         [], b"Your Content System explainer kit. Follow docs/sops/13-explainer-from-zip.md. Needs node 18+, ffmpeg (bash tools/explainer_setup.sh installs Playwright + Chromium).\n"),
}
SKILLS = ['explainer-default', 'explainer-engaging', 'explainer-high-energy']

def pack(name, files, dirs, readme):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as t:
        for f in files: t.add(R / f, arcname=f)
        for d in dirs: t.add(R / d, arcname=d)
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
