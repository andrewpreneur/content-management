#!/usr/bin/env python3
"""Vertical (1080×1920) captioned audiogram from a podcast episode + its transcript.

Usage: python3 tools/audiogram.py AUDIO transcript.json START END OUT.mp4 --title "Hook *line*" [--photo andrew.jpg]
       [--fix "Alex from Ozy=Alex Hormozi"]
Layout: series pill + title (header), round photo of Andrew, yellow waveform, word-by-word captions (same style as reels).
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
import brand_look as B
import reel as R

W, H = 1080, 1920


def card(path, title, photo):
    im = Image.new('RGB', (W, H), B.BG); d = ImageDraw.Draw(im)
    y = B.pill(d, 'GET REAL WITH ANDREW GEORGE', W // 2, 250, B.font(B.FONT_BOLD, 30))
    B.draw_rich(d, title, B.font(B.FONT_BLACK, 72), 70, y + 40, W - 140)
    if photo:
        p = ImageOps.fit(ImageOps.exif_transpose(Image.open(photo)).convert('RGB'), (360, 360), centering=(0.5, 0.3))
        m = Image.new('L', (360, 360), 0); ImageDraw.Draw(m).ellipse([0, 0, 359, 359], fill=255)
        d.ellipse([W // 2 - 186, 714, W // 2 + 186, 1086], fill=B.ACCENT)
        im.paste(p, (W // 2 - 180, 720), m)
    d.text((70, 1700), f"{B.NAME} · {B.TAGLINE}", font=B.font(B.FONT_BOLD, 30), fill=B.MUTED)
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio'); ap.add_argument('transcript'); ap.add_argument('start', type=float); ap.add_argument('end', type=float)
    ap.add_argument('out'); ap.add_argument('--title', required=True); ap.add_argument('--photo'); ap.add_argument('--fix', action='append', default=[])
    a = ap.parse_args()
    words = R.merged_words(json.loads(Path(a.transcript).read_text()))
    wrt, total = R.retime(words, [{'a': [a.start, a.end]}])
    for f in a.fix:  # multi-word caption fixes, e.g. a misheard name
        src, dst = f.split('=', 1); s_words, d_words = src.split(), dst.split()
        i = 0
        while i <= len(wrt) - len(s_words):  # every occurrence
            if [w['cap'] for w in wrt[i:i + len(s_words)]] == s_words:
                t0, t1 = wrt[i]['s'], wrt[i + len(s_words) - 1]['e']; step = (t1 - t0) / len(d_words)
                wrt[i:i + len(s_words)] = [{'cap': dw, 's': t0 + k * step, 'e': t0 + (k + 1) * step} for k, dw in enumerate(d_words)]
                i += len(d_words)
            else:
                i += 1
    with tempfile.TemporaryDirectory() as td:
        bg = os.path.join(td, 'bg.png'); card(bg, a.title, a.photo)
        ass = os.path.join(td, 'c.ass'); R.write_ass(wrt, ass, lambda t: 1480)
        fc = (f"[1:a]atrim={a.start}:{a.end},asetpts=PTS-STARTPTS,highpass=f=80,loudnorm=I=-14:TP=-1.5,asplit[a1][a2];"
              f"[a2]showwaves=s=900x180:mode=cline:colors=0xFFD23F:scale=sqrt:r=30,format=rgba[w];"
              f"[0:v][w]overlay=90:1150,subtitles={ass}[v]")
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-framerate', '30', '-i', bg, '-i', a.audio,
                        '-filter_complex', fc, '-map', '[v]', '-map', '[a1]', '-t', f'{total}', '-c:v', 'libx264',
                        '-preset', 'medium', '-crf', '24', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                        '-movflags', '+faststart', a.out], check=True)
    print(a.out, f'{total:.1f}s')


if __name__ == '__main__':
    main()
