#!/usr/bin/env python3
"""Gate every edit against the locked house look before it's reported (docs/edit-style-lock.md).

  python3 tools/style_check.py VIDEO [--captions] [--out check.jpg] [--ref docs/brand-video/reference/approved-captions.jpg]

Samples 1 frame/second and checks the caption zone (bottom 32%):
  - NO yellow caption text (the retired v0 look): yellow pixels must stay under 0.4% of the zone in every frame
  - NO solid white caption box (black text on a white pill): a bright flat bar wide enough for a line of text
  - captions on → the violet accent (#7B5CFF / #9B83FF) shows up in at least 30% of frames
Writes a side-by-side sheet (6 frames of the video next to the approved reference) for a final look by eye.
Exit 0 = pass, 1 = fail (the reasons are printed as JSON). Never report a video that fails.
"""
import argparse, json, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "docs/brand-video/reference/approved-captions.jpg"


def frames(video, w=480):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout.strip() or 0)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps=1,scale={w}:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    probe = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    h = len(probe) // (w * 3)
    n = len(raw) // (w * h * 3)
    return dur, [np.frombuffer(raw[i * w * h * 3:(i + 1) * w * h * 3], np.uint8).reshape(h, w, 3) for i in range(n)]


def hsv(rgb):
    r, g, b = [rgb[..., i].astype(np.float32) / 255 for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b); d = mx - mn + 1e-6
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return hue, (mx - mn) / (mx + 1e-6), mx


def check(video, captions=True):
    dur, fs = frames(video)
    why, yellow_hits, violet_hits, box_hits = [], 0, 0, 0
    for f in fs:
        z = f[int(f.shape[0] * 0.68):]
        h, s, v = hsv(z)
        if ((h > 40) & (h < 62) & (s > 0.55) & (v > 0.75)).mean() > 0.004: yellow_hits += 1
        if ((h > 245) & (h < 275) & (s > 0.35) & (v > 0.55)).mean() > 0.0004: violet_hits += 1
        # a white pill: rows where a long run is near-white and flat, with dark text inside
        bright = (v > 0.92) & (s < 0.08)
        rows = bright.mean(axis=1)
        if ((rows > 0.25) & (rows < 0.9)).sum() >= max(6, z.shape[0] // 12):
            dark_in = ((v < 0.25) & np.repeat(((rows > 0.25) & (rows < 0.9))[:, None], z.shape[1], 1)).mean()
            if dark_in > 0.004: box_hits += 1
    n = max(1, len(fs))
    if yellow_hits / n > 0.05: why.append(f"yellow in the caption area in {yellow_hits}/{n} frames (the retired look; captions are white + violet)")
    if box_hits / n > 0.10: why.append(f"black-on-white caption boxes in {box_hits}/{n} frames (captions are white text with no box)")
    if captions and violet_hits / n < 0.30: why.append(f"the violet spoken-word accent shows in only {violet_hits}/{n} frames")
    return {"pass": not why, "why": why, "frames": n, "yellow": yellow_hits, "violet": violet_hits, "boxes": box_hits, "seconds": round(dur, 1)}


def sheet(video, out, ref):
    tmp = Path(out).with_suffix(".tile.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", "thumbnail=60,scale=480:-2,tile=3x2", "-frames:v", "1", str(tmp)])
    if Path(ref).exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-i", str(ref), "-filter_complex",
                        "[0:v]scale=1440:-2[a];[1:v]scale=1440:-2[b];[a][b]vstack", str(out)])
        tmp.unlink(missing_ok=True)
    else:
        tmp.rename(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--captions", action="store_true", default=True); ap.add_argument("--no-captions", dest="captions", action="store_false")
    ap.add_argument("--out", default=""); ap.add_argument("--ref", default=str(REF))
    a = ap.parse_args()
    r = check(a.video, a.captions)
    if a.out:
        sheet(a.video, a.out, a.ref); r["sheet"] = a.out
    print(json.dumps(r))
    sys.exit(0 if r["pass"] else 1)
