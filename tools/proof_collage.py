#!/usr/bin/env python3
"""Proof collage: screenshots pop in scattered over the video, slow then faster (Andrew, Nov 26 Black Friday ad).

  python3 tools/proof_collage.py IN.mp4 OUT.mp4 --shots DIR --start 12.3 [--end 16.0] [--build 2.4] [--seed 7]

--start = when the line starts ("I run my agency that pays my bills..."). The N screenshots arrive at
t_i = build * (i/N)^(1/2.6) after start (exponential feel: first ones slow, last ones rapid), each pops in
(scale 0.82 -> 1, fade, ~120 ms), scattered over a jittered grid so together they cover nearly the full frame,
random sizes (28-62 % of the width), slight tilt, no border (images straight on, faint shadow), later ones on top.
--sfx adds a pop on each landing (Andrew: "pop, pop, pop" as each one comes in).
They hold until --end (default start+build+0.6) then fade out in 0.2 s. Audio is copied untouched.
"""
import argparse, glob, math, random, subprocess, json
from PIL import Image, ImageFilter, ImageDraw

def probe(v):
    s = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,r_frame_rate", "-of", "json", v], capture_output=True, text=True).stdout)["streams"][0]
    n, d = s["r_frame_rate"].split("/"); return s["width"], s["height"], float(n) / float(d)

def card(path, w, rot):
    """The screenshot straight on (no border, no frame; Andrew Nov 27), with a faint shadow so overlaps read."""
    im = Image.open(path).convert("RGBA")
    scale = w / im.width
    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    pad = w // 14; sh = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", sh.size, 0); a.paste(im.getchannel("A").point(lambda x: x * 0.35), (pad, pad + pad // 4))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(pad / 3))); sh.alpha_composite(im, (pad, pad))
    return sh.rotate(rot, Image.BICUBIC, expand=True)

def pop_track(sfx, times, start, sr=48000, seed=7):
    """One pop per screenshot, landing on its frame; pitch varies a little so it reads pop-pop-pop, not a loop."""
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", sfx, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    p = np.frombuffer(pcm, np.float32).reshape(-1, 2); rnd = random.Random(seed)
    out = np.zeros((int((start + times[-1] + 1) * sr), 2), np.float32)
    for i, t in enumerate(times):
        r = rnd.uniform(0.9, 1.18); idx = np.arange(0, len(p) - 1, r)
        q = np.stack([np.interp(idx, np.arange(len(p)), p[:, c]) for c in (0, 1)], 1).astype(np.float32)
        g = 0.55 * (0.85 + 0.15 * (i % 3) / 2)
        o = int((start + t) * sr); out[o:o + len(q)] += q[: len(out) - o] * g
    path = "/tmp/_pops.f32"; out.tofile(path); return path, sr

def comp(fr, im, x, y):
    """alpha_composite that allows cards to hang off the edges."""
    l, t = max(0, -x), max(0, -y); r, b = min(im.width, fr.width - x), min(im.height, fr.height - y)
    if r > l and b > t: fr.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

def plan(shots, W, H, seed):
    rnd = random.Random(seed); n = len(shots)
    cols = 3 if W < H else 5; rows = math.ceil(n / cols)
    cells = [(c, r) for r in range(rows) for c in range(cols)]; rnd.shuffle(cells)
    items = []
    # bigger cards first-ish so small ones land on top late in the build
    sizes = sorted([rnd.uniform(0.28, 0.62) for _ in shots], reverse=True)
    for i, (p, frac) in enumerate(zip(shots, sizes)):
        c, r = cells[i % len(cells)]
        cx = (c + 0.5 + rnd.uniform(-0.35, 0.35)) / cols * W
        cy = (r + 0.5 + rnd.uniform(-0.35, 0.35)) / rows * H
        im = Image.open(p); ar = im.width / im.height
        w = frac * W
        if w / ar > 0.42 * H: w = 0.42 * H * ar          # tall cards don't eat the whole frame
        w = min(w, im.width * 2.6)                          # tiny screenshots don't get blurry
        w = max(w, 0.24 * W)
        img = card(p, int(w), rnd.uniform(-7, 7))
        # keep each card (nearly) inside the frame: at most 6 % of a card may hang off an edge
        hx, hy = img.width / 2 * 0.88, img.height / 2 * 0.88
        cx = min(max(cx, hx), W - hx) if 2 * hx < W else W / 2
        cy = min(max(cy, hy), H - hy) if 2 * hy < H else H / 2
        items.append({"img": img, "cx": cx, "cy": cy})
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--shots", required=True)
    ap.add_argument("--start", type=float, required=True); ap.add_argument("--end", type=float)
    ap.add_argument("--build", type=float, default=2.4); ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--k", type=float, default=2.6)
    ap.add_argument("--sfx", default="", help="pop sound played as each screenshot lands (mixed under the voice)")
    a = ap.parse_args()
    W, H, fps = probe(a.inp)
    shots = sorted(glob.glob(f"{a.shots}/*.png") + glob.glob(f"{a.shots}/*.jpg"))
    items = plan(shots, W, H, a.seed); n = len(items)
    times = [a.build * (i / n) ** (1 / a.k) for i in range(n)]
    end = (a.end if a.end else a.start + a.build + 0.6) - a.start
    end = max(end, a.build + 0.4); fade = 0.2; pop = 0.12
    nfr = int(math.ceil((end + fade) * fps)) + 1
    fc = f"[1:v]setpts=PTS-STARTPTS+{a.start}/TB[o];[0:v][o]overlay=eof_action=pass:format=auto[v]"
    extra, amap, acodec = [], ["-map", "0:a?"], ["-c:a", "copy"]
    if a.sfx:   # voice stays as is; pops are added on top (limiter only touches a pop that would clip)
        pth, sr = pop_track(a.sfx, times, a.start)
        extra = ["-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", pth]
        fc += ";[0:a][2:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.97:level=false[a]"
        amap, acodec = ["-map", "[a]"], ["-c:a", "aac", "-b:a", "256k"]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", a.inp,
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", *extra,
        "-filter_complex", fc, "-map", "[v]", *amap, "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        *acodec, "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    for f in range(nfr):
        t = f / fps; fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out_a = 1.0 if t < end else max(0.0, 1 - (t - end) / fade)
        for it, t0 in zip(items, times):
            if t < t0: break
            p = min(1.0, (t - t0) / pop); e = 1 - (1 - p) ** 3
            im = it["img"]; s = 0.82 + 0.18 * e
            if s < 0.999: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
            al = e * out_a
            if al < 0.999:
                im = im.copy(); im.putalpha(im.getchannel("A").point(lambda x: int(x * al)))
            comp(fr, im, int(it["cx"] - im.width / 2), int(it["cy"] - im.height / 2))
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()
    if ff.returncode: raise SystemExit("ffmpeg failed")

if __name__ == "__main__":
    main()
