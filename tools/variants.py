#!/usr/bin/env python3
"""Render reel variants from one master video (multiplier step 2).

Usage:
  python3 tools/variants.py MASTER.mp4 OUT_DIR --hook "Hook A" --hook "Hook B" \
      [--srt captions.srt] [--alt-open alt_first5s.mp4]

Each variant changes at least two things so no two uploads are identical:
  v1  speed +0.1x            + hook A, font 1
  v2  speed -0.1x            + hook B, font 2
  v3  mirrored               + hook A, font 2, caption style 2
  v4  hook B, font 1         + caption style 2, slight zoom 1.04
  v5  new first 5s (--alt-open)  + hook B, font 2   (skipped if no --alt-open)
  v6  mirrored + speed +0.05x + hook A, font 1, caption style 1
NOTE (Nov 4 research): Instagram says speed changes alone do not make a post original.
These renders are hook/caption test variants (IG Trial Reels, different platforms) — not
repeat uploads to the same account. Real variants need a different first 5s/layout too.
Writes OUT_DIR/manifest.json with the changes per file (goes into outputs.variant_changes).
Mirroring flips on-screen text in the source footage — skip v3/v6 for clips with screen recordings
by passing --no-mirror.
"""
import argparse, json, subprocess, shutil
from pathlib import Path

FONTS = {
    1: '/usr/share/fonts/opentype/inter/Inter-Black.otf',
    2: '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
}
CAPTION_STYLES = {
    1: "FontName=Inter,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=60",
    2: "FontName=DejaVu Sans,FontSize=15,PrimaryColour=&H0000E5FF,OutlineColour=&H00000000,BorderStyle=3,Outline=6,Alignment=2,MarginV=70",
}


def esc(t):
    return t.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')


def hook_filter(text, font, workdir):
    import textwrap, hashlib
    wrapped = '\n'.join(textwrap.wrap(text.upper(), 18))
    tf = Path(workdir) / f".hook_{hashlib.md5((text+str(font)).encode()).hexdigest()[:8]}.txt"
    tf.write_text(wrapped)
    return (f"drawtext=fontfile={FONTS[font]}:textfile={tf}:fontcolor=white:fontsize=h/24:line_spacing=12:"
            f"box=1:boxcolor=black@0.6:boxborderw=28:x=(w-text_w)/2:y=h*0.14:enable='lt(t,3.5)'")


def render(master, out, *, speed=1.0, mirror=False, zoom=1.0, hook=None, font=1, srt=None, cap=1, alt_open=None):
    v = []
    if zoom != 1.0:
        v.append(f"scale=iw*{zoom}:-2,crop=iw/{zoom}:ih/{zoom}")
    if mirror:
        v.append('hflip')
    if srt:
        v.append(f"subtitles={srt}:force_style='{CAPTION_STYLES[cap]}'")
    if hook:
        v.append(hook_filter(hook, font, Path(out).parent))
    if speed != 1.0:
        v.append(f"setpts=PTS/{speed}")
    vf = ','.join(v) or 'null'
    af = f"atempo={speed}" if speed != 1.0 else 'anull'

    if alt_open:
        # replace first 5s of master with alt_open (both scaled to master size), then apply filters
        fc = (f"[1:v]scale=1080:1920,setsar=1,fps=30[av];[1:a]aresample=48000[aa];"
              f"[0:v]trim=start=5,setpts=PTS-STARTPTS,scale=1080:1920,setsar=1,fps=30[mv];"
              f"[0:a]atrim=start=5,asetpts=PTS-STARTPTS,aresample=48000[ma];"
              f"[av][aa][mv][ma]concat=n=2:v=1:a=1[cv][ca];[cv]{vf}[ov];[ca]{af}[oa]")
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', master, '-i', alt_open, '-filter_complex', fc,
               '-map', '[ov]', '-map', '[oa]']
    else:
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', master, '-vf', vf, '-af', af]
    cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '160k',
            '-map_metadata', '-1', '-movflags', '+faststart', str(out)]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('master'); ap.add_argument('out_dir')
    ap.add_argument('--hook', action='append', required=True, help='give 2 hooks: A and B')
    ap.add_argument('--srt'); ap.add_argument('--alt-open'); ap.add_argument('--no-mirror', action='store_true')
    a = ap.parse_args()
    if not shutil.which('ffmpeg'):
        raise SystemExit('ffmpeg not installed')
    hA = a.hook[0]; hB = a.hook[1] if len(a.hook) > 1 else a.hook[0]
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    plan = [
        ('v1', dict(speed=1.1, hook=hA, font=1, cap=1), ['speed+0.1', 'hook_A', 'font_1']),
        ('v2', dict(speed=0.9, hook=hB, font=2, cap=1), ['speed-0.1', 'hook_B', 'font_2']),
        ('v3', dict(mirror=True, hook=hA, font=2, cap=2), ['mirror', 'hook_A', 'font_2', 'captions_2']),
        ('v4', dict(zoom=1.04, hook=hB, font=1, cap=2), ['zoom_1.04', 'hook_B', 'font_1', 'captions_2']),
        ('v5', dict(alt_open=a.alt_open, hook=hB, font=2, cap=1), ['new_first_5s', 'hook_B', 'font_2']),
        ('v6', dict(mirror=True, speed=1.05, hook=hA, font=1, cap=1), ['mirror', 'speed+0.05', 'hook_A', 'font_1']),
    ]
    manifest = []
    for name, kw, changes in plan:
        if name == 'v5' and not a.alt_open:
            continue
        if kw.get('mirror') and a.no_mirror:
            continue
        f = out / f"{Path(a.master).stem}_{name}.mp4"
        render(a.master, f, srt=a.srt, **kw)
        manifest.append({'file': f.name, 'variant_changes': changes})
        print('rendered', f.name)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
