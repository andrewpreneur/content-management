#!/usr/bin/env python3
"""Tighten the silence at every cut of a finished ad so the lines almost touch (Andrew, Nov 27: ads only, never long form).

  python3 tools/tighten_cuts.py IN.mp4 OUT.mp4 [--keep 0.025] [--thr -33] [--all-pauses 0]

Finds quiet stretches (10 ms windows under --thr dBFS, >= 60 ms) that contain a picture cut, and removes all of the quiet
except --keep seconds on each side (so words never clip). Natural pauses inside one take are left alone unless
--all-pauses N (then any quiet stretch longer than N s is tightened too). Spans are snapped to whole frames so sound and
picture stay in sync; a 5 ms fade at each join stops clicks. Prints the removed spans as JSON.
"""
import argparse, json, subprocess, numpy as np

def probe(v):
    s = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                                   "-of", "json", v], capture_output=True, text=True).stdout)["streams"][0]
    n, d = s["r_frame_rate"].split("/"); return s["width"], s["height"], float(n) / float(d)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--keep", type=float, default=0.025); ap.add_argument("--thr", type=float, default=-33)
    ap.add_argument("--all-pauses", type=float, default=0)
    a = ap.parse_args(); W, H, fps = probe(a.inp)
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.inp, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(float) / 32768; w = 160; n = len(x) // w
    q = 20 * np.log10(np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1)) + 1e-9) < a.thr
    sw, sh = 64, max(2, int(64 * H / W) // 2 * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.inp, "-vf", f"scale={sw}:{sh},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, sh, sw).astype(float); d = np.abs(np.diff(f, axis=0)).mean((1, 2))
    cuts = [(i + 1) / fps for i in range(len(d)) if d[i] > max(6, 4 * np.median(d))]
    spans, i = [], 0
    while i < n:
        if not q[i]: i += 1; continue
        j = i
        while j < n and q[j]: j += 1
        s, e = i / 100, j / 100; i = j
        if e - s < 0.06: continue
        has_cut = any(s - 0.05 <= c <= e + 0.05 for c in cuts)
        if not has_cut and not (a.all_pauses and e - s > a.all_pauses): continue
        rs, re_ = np.round((s + a.keep) * fps) / fps, np.round((e - a.keep) * fps) / fps
        if re_ - rs >= 1 / fps: spans.append((round(rs, 4), round(re_, 4)))
    if not spans:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-c", "copy", a.out], check=True); print("[]"); return
    keep, t = [], 0.0
    for s, e in spans: keep.append((t, s)); t = e
    keep.append((t, None))
    parts, labels = [], []
    for k, (s, e) in enumerate(keep):
        tr = f"start={s}" + (f":end={e}" if e is not None else "")
        dur = (e - s) if e is not None else None
        fade = f",afade=t=in:d=0.005" + (f",afade=t=out:st={dur - 0.005:.4f}:d=0.005" if dur else "")
        parts.append(f"[0:v]trim={tr},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={tr},asetpts=PTS-STARTPTS{fade}[a{k}]")
        labels.append(f"[v{k}][a{k}]")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                    "-movflags", "+faststart", a.out], check=True)
    print(json.dumps({"removed": spans, "seconds": round(sum(e - s for s, e in spans), 2)}))

if __name__ == "__main__":
    main()
