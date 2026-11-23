#!/usr/bin/env python3
"""Pack the job toolkit (long-form editing scripts + the fonts and sound effects they use + SOP 12) and publish it to the
app's private Storage bucket "toolkit" as longform.tar.gz. Each long-form job gets a 24 h link to it, so any customer's
Claude Code can run the edits without this repository. Run after changing any of these files:
  python3 tools/publish_toolkit.py
"""
import importlib.util, io, tarfile, requests
from pathlib import Path
R = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ycs', R / 'tools/ycs_sync.py'); ycs = importlib.util.module_from_spec(spec); spec.loader.exec_module(ycs)
FILES = ['tools/longform_layout.py', 'tools/montage_intro.py', 'tools/drive_range_proxy.py', 'tools/drive_upload.py', 'tools/transcribe.py',
         'tools/sound_mix.py', 'docs/sops/12-longform-edits.md', 'vendor/motion-graphics/skills/sound-effects/MUSIC.md']
DIRS = ['tools/fonts', 'vendor/motion-graphics/skills/sound-effects/sfx/kit']

buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode='w:gz') as t:
    for f in FILES: t.add(R / f, arcname=f)
    for d in DIRS: t.add(R / d, arcname=d)
    readme = b"Your Content System job toolkit. Follow docs/sops/12-longform-edits.md. Needs ffmpeg, python3, numpy, requests, faster-whisper.\n"
    ti = tarfile.TarInfo('README.txt'); ti.size = len(readme); t.addfile(ti, io.BytesIO(readme))
up = ycs.call('mutation', 'toolkitUploadUrl', {'name': 'longform.tar.gz'})
r = requests.put(up['url'], data=buf.getvalue(), headers={'Content-Type': 'application/gzip', 'x-upsert': 'true'}, timeout=300)
r.raise_for_status()
print(f'published longform.tar.gz ({len(buf.getvalue()) // 1024} KB)')
