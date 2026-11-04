#!/usr/bin/env python3
"""Build the "One → Twenty" review page (Artifact) from one or more multiplier runs.

Usage:
  python3 tools/review_page.py OUT_DIR RUN_DIR [RUN_DIR ...] [--note "line"]...

Each RUN_DIR (outputs/YYYY-MM-DD-<source>/) needs manifest_spec.json (see tools/manifest.py).
Writes OUT_DIR/index.html + OUT_DIR/m/<run>/... (videos re-encoded to 720p so each is well under 15 MB,
images as JPEG). Publish with the Artifact tool: file_path=OUT_DIR/index.html, files={all of m/}, and
capabilities {db:{}, user:{}} so Andrew's Approve / Change / Reject taps land in the page's `reviews`
collection (doc id "<run>__<key>": {status, note, at}), which Claude reads back with ArtifactData.
"""
import argparse, html, json, os, shutil, subprocess
from pathlib import Path
from PIL import Image

GROUPS = [
    ('reel', 'Main-feed reels', 'Each opens on a different real line, so each is a new post.'),
    ('reel_variant', 'IG Trial Reels', 'Speed, zoom, hook and caption tweaks. Trial Reels only (shown to non-followers).'),
    ('translation', 'Spanish', 'Translated captions, hook and CTA. Dub waits for ElevenLabs.'),
    ('carousel', 'Carousel', '1080×1350 slides for IG / LinkedIn (PDF) / FB.'),
    ('story_sequence', 'Story sequence', '1080×1920 frames. Dashed boxes = where the real IG sticker goes.'),
    ('podcast', 'Podcast', 'Cleaned audio, audiogram and an extended-segment script.'),
    ('long_video', 'YouTube long-form', 'Outline, titles and thumbnail concepts. Andrew films this.'),
    ('email', 'Email & essay', ''),
    ('substack', 'Email & essay', ''),
    ('linkedin_post', 'Social text', ''),
    ('threads_post', 'Social text', ''),
    ('x_thread', 'Social text', ''),
]
LABEL = {'reel': 'Reel', 'reel_variant': 'Trial Reel', 'translation': 'Spanish', 'carousel': 'Carousel',
         'story_sequence': 'Stories', 'podcast': 'Podcast', 'long_video': 'YouTube', 'email': 'Email',
         'substack': 'Essay', 'linkedin_post': 'LinkedIn', 'threads_post': 'Threads', 'x_thread': 'X thread'}


def enc_video(src, dst, square=False):
    vf = 'scale=720:720' if square else 'scale=720:-2'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-vf', vf, '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', '28', '-maxrate', '1800k', '-bufsize', '3600k', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                    '-b:a', '96k', '-movflags', '+faststart', dst], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '1.5', '-i', dst, '-frames:v', '1', '-q:v', '4',
                    dst.replace('.mp4', '.jpg')], check=True)


def to_jpg(src, dst, maxw=1080):
    im = Image.open(src).convert('RGB')
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(dst, quality=84, optimize=True)


def build(out, runs, notes):
    out = Path(out); (out / 'm').mkdir(parents=True, exist_ok=True)
    data = {'runs': [], 'notes': notes}
    for rd in runs:
        rd = Path(rd); spec = json.loads((rd / 'manifest_spec.json').read_text())
        run = rd.name; md = out / 'm' / run; md.mkdir(parents=True, exist_ok=True)
        items = []
        for o in spec['outputs']:
            f = o.get('file'); it = {'key': o['key'], 'type': o['output_type'], 'label': LABEL.get(o['output_type'], o['output_type']),
                                     'platforms': o.get('platforms', []), 'notes': o.get('notes'), 'changes': o.get('variant_changes', []),
                                     'lang': o.get('language', 'en')}
            if not f or not os.path.exists(f):
                it['missing'] = True; items.append(it); continue
            ext = Path(f).suffix
            if ext == '.mp4':
                dst = md / f"{o['key']}.mp4"
                if not dst.exists():
                    enc_video(f, str(dst), square='audiogram' in o['key'])
                it['video'] = f"m/{run}/{dst.name}"; it['poster'] = f"m/{run}/{dst.stem}.jpg"
            elif ext == '.mp3':
                shutil.copy(f, md / f"{o['key']}.mp3"); it['audio'] = f"m/{run}/{o['key']}.mp3"
            elif ext in ('.md', '.srt'):
                it['text'] = Path(f).read_text()
            if o['output_type'] in ('carousel', 'story_sequence'):
                d = Path(f).parent; pat = 'slide-*.png' if o['output_type'] == 'carousel' else 'frame-*.png'
                it['images'] = []
                for p in sorted(d.glob(pat)):
                    dst = md / f"{o['key']}-{p.stem}.jpg"; to_jpg(p, dst); it['images'].append(f"m/{run}/{dst.name}")
                it.pop('text', None)
            items.append(it)
        data['runs'].append({'id': run, 'title': spec['source'].get('label', run), 'source': spec['source'], 'items': items})
    tpl = (Path(__file__).parent / 'review_page_template.html').read_text()
    page = tpl.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    (out / 'index.html').write_text(page)
    files = sorted(str(p.relative_to(out)) for p in (out / 'm').rglob('*') if p.is_file())
    (out / 'files.json').write_text(json.dumps(files, indent=1))
    total = sum((out / f).stat().st_size for f in files)
    print(f"{len(files)} media files, {total/1e6:.1f} MB → {out}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('runs', nargs='+'); ap.add_argument('--note', action='append', default=[])
    a = ap.parse_args(); build(a.out, a.runs, a.note)
