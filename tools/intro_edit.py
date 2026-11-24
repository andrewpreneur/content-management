#!/usr/bin/env python3
"""Edit a long video's intro the way we do by hand: tighten it, reframe, punch in, caption, title, clean sound.

  python3 tools/intro_edit.py --video SRC --transcript tx/transcript.json --start 0 --end 95 --out intro.mp4 \
      [--crop x,y,w,h] [--title "…"] [--sub "…"] [--style styles/saassuite/tokens.json] [--height 1080] \
      [--pause 0.30] [--zoom 1.12] [--keep-fillers] [--no-captions] [--plan plan.json]

SRC: a local file or URL (e.g. http://127.0.0.1:8765/<driveId> from tools/drive_range_proxy.py). The transcript must have
word timings in SOURCE seconds (tools/transcribe.py; transcribe just the range you edit, then pass --tx-offset if its
times start at 0).
What it does (all of it is the house editing style, see styles/saassuite/STYLE.md + SCRIPT.md):
  1. keeps only the spoken words in [start, end]: drops filler words (um, uh, erm, "you know" when alone) and closes every
     silence longer than --pause (default 0.30 s), with 60 ms of air at each cut so nothing sounds clipped;
  2. --crop reframes to a region of the source (e.g. the speaker's tile in a call recording), scaled to the output;
  3. punch-in: each sentence alternates between a wide and a --zoom (default 1.12×) framing, so every cut is motivated;
  4. captions (default on): 2–4 word phrases, white, the spoken word in the accent colour, lower third, inside the safe area;
  5. a title line (--title, optional --sub) over the first 3 seconds;
  6. sound: 12 ms fades at every cut, loudness −14 LUFS (true peak −1 dB).
Writes OUT (H.264 CRF 18, AAC 256k, same fps as the source) and OUT.plan.json (every kept range, what was removed, timing map).
--plan FILE reuses a saved plan (hand-edited is fine) instead of computing one. --dry-run writes the plan only.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

FILLERS = {"um", "uh", "erm", "uhm", "hmm", "mm", "ah", "eh"}
ROOT = Path(__file__).resolve().parent.parent


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"command failed: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}")
    return r.stdout


def probe(src):
    j = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate", "-of", "json", src]))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    n, d = v["r_frame_rate"].split("/")
    return int(v["width"]), int(v["height"]), float(n) / float(d)


def _word(w, offset):
    """One word from any of our transcript shapes: {w,s,e} (engine) or {word|text,start,end} (whisper)."""
    t = str(w.get("w", w.get("word", w.get("text", "")))).strip()
    s, e = w.get("s", w.get("start")), w.get("e", w.get("end"))
    if not t or s is None or e is None:
        return None
    return {"w": t, "s": float(s) + offset, "e": float(e) + offset}


def words_of(tx, offset):
    raw = [w for s in tx.get("segments", []) for w in s.get("words", [])] or tx.get("words", [])
    return [x for x in (_word(w, offset) for w in raw) if x]


def parse_tiles(spec):
    """--tiles "x,y,w,h,faceX;x,y,w,h,faceX": the people on a call grid, left to right, with each face's centre x."""
    if not spec:
        return []
    out = []
    for part in spec.split(";"):
        x, y, w, h, fx = (int(float(v)) for v in part.split(","))
        out.append((x, y, w, h, fx))
    return out


def split_filter(tiles, zoom, W, H, fps, gap=4):
    """Each person cropped tall around their face, side by side, filling the 16:9 frame (podcast split)."""
    n = len(tiles); tw = (W - gap * (n - 1)) // n // 2 * 2
    chains, labels = [f"[0:v]split={n}" + "".join(f"[s{i}]" for i in range(n))], []
    for i, (x, y, w, h, fx) in enumerate(tiles):
        ch = round(h / zoom / 2) * 2; cw = min(w, round(ch * tw / H / 2) * 2)
        cx = min(max(x, fx - cw // 2), x + w - cw); cy = y + max(0, round((h - ch) * 0.1))   # keep the top of the head in
        chains.append(f"[s{i}]crop={cw}:{ch}:{cx}:{cy},scale={tw}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                      f"crop={tw}:{H},setsar=1[t{i}]")
        labels.append(f"[t{i}]")
    stack = "".join(labels) + f"hstack=inputs={n}" if n > 1 else labels[0] + "null"
    return ";".join(chains) + f";{stack},pad={W}:{H}:(ow-iw)/2:0:color=0x0B0B10,fps={fps}"


def plan_cuts(words, start, end, pause, keep_fillers, air=0.06):
    """Kept source ranges + the words in each (fillers dropped, long silences closed)."""
    ws = [w for w in words if w["s"] >= start - 0.05 and w["e"] <= end + 0.05]
    removed = []
    if not keep_fillers:
        kept = []
        for w in ws:
            bare = re.sub(r"[^a-z]", "", w["w"].lower())
            (removed if bare in FILLERS else kept).append(w)
        ws = kept
    ranges = []
    for w in ws:
        if ranges and w["s"] - ranges[-1]["e"] <= pause:
            ranges[-1]["e"] = w["e"]; ranges[-1]["words"].append(w)
        else:
            ranges.append({"s": w["s"], "e": w["e"], "words": [w]})
    for r in ranges:
        r["s"] = max(start, r["s"] - air); r["e"] = min(end, r["e"] + air)
    # never let padded ranges overlap
    for a, b in zip(ranges, ranges[1:]):
        if a["e"] > b["s"]:
            a["e"] = b["s"] = (a["e"] + b["s"]) / 2
    # split at sentence ends inside a range, so a tight speaker still gets a punch-in change per sentence (a jump on the
    # sentence boundary reads as an edit, not a glitch)
    split = []
    for r in ranges:
        cur = {"s": r["s"], "words": []}
        for k, w in enumerate(r["words"]):
            cur["words"].append(w)
            nxt = r["words"][k + 1] if k + 1 < len(r["words"]) else None
            if nxt and re.search(r"[.!?]$", w["w"]) and len(cur["words"]) >= 3:
                cut = (w["e"] + nxt["s"]) / 2
                cur["e"] = cut; split.append(cur); cur = {"s": cut, "words": []}
        cur["e"] = r["e"]; split.append(cur)
    return split, removed


def sentence_starts(ranges):
    """Index of the range where each new sentence begins (for punch-in alternation)."""
    marks, prev_end = [], True
    for i, r in enumerate(ranges):
        if prev_end:
            marks.append(i)
        prev_end = bool(re.search(r"[.!?]$", r["words"][-1]["w"]))
    return set(marks)


def ass_time(t):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def hex_ass(h, alpha=0):
    h = h.lstrip("#"); return f"&H{alpha:02X}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def captions_ass(phrases, W, H, style, title, sub, title_at="left"):
    accent = style.get("color", {}).get("accent", "#7B5CFF")
    fs = round(H * 0.052); out_y = round(H * 0.86)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display,{fs},&H00FFFFFF,&H00FFFFFF,&H64000000,&H96000000,1,0,0,0,100,100,-1,0,1,{max(2, fs // 18)},{max(1, fs // 22)},2,{W // 10},{W // 10},{H - out_y},1
Style: Title,Inter Display,{round(H * 0.072)},&H00FFFFFF,&H00FFFFFF,&H50000000,&H64000000,1,0,0,0,100,100,-1.5,0,1,{max(2, H // 300)},{max(1, H // 360)},7,{W // 14},{W // 14},{H // 9},1
Style: Sub,Inter Display,{round(H * 0.042)},&H00FFFFFF,&H00FFFFFF,&H50000000,&H64000000,0,0,0,0,100,100,0,0,1,{max(1, H // 400)},1,7,{W // 14},{W // 14},{H // 9 + round(H * 0.09)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if title:
        # left third, two short lines, mid-height: the speaker sits in the middle, so the title never covers a face
        def two(t):
            if len(t) <= 18: return t
            sp = [k for k, ch in enumerate(t) if ch == " "]
            k = min(sp, key=lambda k: abs(k - len(t) / 2)) if sp else 0
            return t[:k] + "\\N" + t[k + 1:] if k else t
        x0, ym = W // 14, round(H * 0.47)
        bw, bh = round(W * 0.46), round(H * 0.56)
        bx, al1, al7 = 0, "an1", "an7"
        if title_at == "bottom":   # split screen: faces on both sides, so centre it on the chests above the captions
            x0, ym = W // 2, round(H * 0.64); bw, bh = W, round(H * 0.40); al1, al7 = "an2", "an8"
            two = lambda t: t
        ev.append(f"Dialogue: 0,{ass_time(0.1)},{ass_time(3.4)},Title,,0,0,0,,{{\\an7\\pos({bx},{ym - bh // 2})\\p1\\bord0\\shad0"
                  f"\\blur{H // 14}\\c&H000000&\\alpha&H60&\\fad(220,260)}}m 0 0 l {bw} 0 {bw} {bh} 0 {bh}{{\\p0}}")
        ev.append(f"Dialogue: 2,{ass_time(0.15)},{ass_time(3.3)},Title,,0,0,0,,{{\\{al1}\\pos({x0},{ym})\\fad(220,260)}}{two(title)}")
        if sub:
            ev.append(f"Dialogue: 2,{ass_time(0.35)},{ass_time(3.3)},Sub,,0,0,0,,{{\\{al7}\\pos({x0},{ym + H // 40})"
                      f"\\fad(220,260)\\alpha&H20&}}{two(sub) if len(sub) > 34 else sub}")
    acc = hex_ass(accent)
    for ph in phrases:
        for k, w in enumerate(ph["words"]):
            a = w["t0"]; b = ph["words"][k + 1]["t0"] if k + 1 < len(ph["words"]) else ph["t1"]
            if b - a < 0.02:
                continue
            txt = " ".join((f"{{\\c{acc}}}{x['w']}{{\\c&H00FFFFFF&}}" if j == k else x["w"]) for j, x in enumerate(ph["words"]))
            ev.append(f"Dialogue: 1,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{txt}")
    return head + "\n".join(ev) + "\n"


def phrases_of(ranges, tmap):
    """2–4 word caption phrases on the OUTPUT timeline, broken at punctuation."""
    out, cur = [], []
    for r in ranges:
        for w in r["words"]:
            cur.append({"w": w["w"], "t0": tmap(w["s"]), "t1": tmap(w["e"])})
            if len(cur) >= 4 or re.search(r"[,.!?;:]$", w["w"]) and len(cur) >= 2:
                out.append(cur); cur = []
        if cur and len(cur) >= 2:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    res = [{"words": p, "t1": p[-1]["t1"] + 0.12} for p in out]
    for a, b in zip(res, res[1:]):   # overlapping phrases stack in ASS (the next line jumps ABOVE): end each where the next starts
        a["t1"] = min(a["t1"], b["words"][0]["t0"])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True); ap.add_argument("--transcript", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--tx-offset", type=float, default=0, help="add to transcript times (when it was made from a cut-out range)")
    ap.add_argument("--crop", help="x,y,w,h in source pixels")
    ap.add_argument("--tiles", help='call grid split: "x,y,w,h,faceX;x,y,w,h,faceX" (each person cropped tall around the face, side by side)')
    ap.add_argument("--title", default=""); ap.add_argument("--sub", default="")
    ap.add_argument("--style", default=str(ROOT / "styles/saassuite/tokens.json"))
    ap.add_argument("--height", type=int, default=1080); ap.add_argument("--pause", type=float, default=0.30)
    ap.add_argument("--zoom", type=float, default=1.12); ap.add_argument("--keep-fillers", action="store_true")
    ap.add_argument("--no-captions", dest="captions", action="store_false", default=True)
    ap.add_argument("--plan"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    SW, SH, fps = probe(a.video)
    cx, cy, cw, ch = [int(v) for v in a.crop.split(",")] if a.crop else (0, 0, SW, SH)
    tiles = parse_tiles(a.tiles)
    H = a.height; W = round(H * 16 / 9 / 2) * 2
    style = json.loads(Path(a.style).read_text()) if a.style and Path(a.style).exists() else {}

    if a.plan:
        plan = json.loads(Path(a.plan).read_text()); ranges = plan["ranges"]
    else:
        words = words_of(json.loads(Path(a.transcript).read_text()), a.tx_offset)
        if not words:
            sys.exit(f"no words found in {a.transcript} (expected segments[].words[] with w/s/e or word/start/end)")
        ranges, removed = plan_cuts(words, a.start, a.end, a.pause, a.keep_fillers)
        if not ranges:
            sys.exit(f"no speech between {a.start} s and {a.end} s (check --start/--end and --tx-offset)")
        starts = sentence_starts(ranges)
        z = True   # first sentence wide (the establishing shot), then alternate
        for i, r in enumerate(ranges):
            if i in starts:
                z = not z
            r["zoom"] = a.zoom if z else 1.0
        plan = {"source": a.video, "start": a.start, "end": a.end, "pause": a.pause, "crop": [cx, cy, cw, ch], "ranges": ranges,
                "removed_fillers": [w["w"] for w in removed]}
    # output timeline map
    acc, offs = 0.0, []
    for r in ranges:
        offs.append(acc); acc += r["e"] - r["s"]
    def tmap(t):
        for r, o in zip(ranges, offs):
            if r["s"] - 0.001 <= t <= r["e"] + 0.001:
                return o + (t - r["s"])
        return min(offs[-1] + ranges[-1]["e"] - ranges[-1]["s"], max(0, next((o for r, o in zip(ranges, offs) if r["s"] > t), acc)))
    plan["output_seconds"] = round(acc, 2); plan["source_seconds"] = round(a.end - a.start, 2)
    Path(a.out + ".plan.json").write_text(json.dumps(plan, indent=1))
    print(f"intro: {plan['source_seconds']} s of source -> {plan['output_seconds']} s ({len(ranges)} pieces, "
          f"{len(plan.get('removed_fillers', []))} fillers out)")
    if a.dry_run:
        return

    tmp = Path(tempfile.mkdtemp(prefix=".intro_", dir=str(Path(a.out).resolve().parent)))   # next to the output (some sandboxes block /tmp)
    parts = []
    for i, r in enumerate(ranges):
        zf = float(r.get("zoom", 1.0))
        # crop region, then punch in around its centre, then scale to the output frame (16:9, letterboxed if the crop isn't)
        zw, zh = round(cw / zf / 2) * 2, round(ch / zf / 2) * 2
        zx, zy = cx + (cw - zw) // 2, cy + max(0, round((ch - zh) * 0.15))   # punch in but keep the top of the head
        vf = (f"crop={zw}:{zh}:{zx}:{zy},scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0B0B10,setsar=1,fps={fps}")
        if tiles:
            vf = split_filter(tiles, zf, W, H, fps)
        d = r["e"] - r["s"]
        af = f"afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012,aresample=48000"
        p = tmp / f"p{i:04d}.mkv"   # mkv: PCM audio keeps cuts sample-exact (mp4 refuses PCM)
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{r['s']:.3f}", "-i", a.video, "-t", f"{d:.3f}",
             "-filter_complex" if tiles else "-vf", vf, "-af", af,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(p)])
        parts.append(p)
    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = tmp / "joined.mkv"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    vf = "null"
    if a.captions or a.title:
        ass = tmp / "caps.ass"
        ass.write_text(captions_ass(phrases_of(ranges, tmap) if a.captions else [], W, H, style, a.title, a.sub,
                                   "bottom" if tiles else "left"))
        fonts = ROOT / "styles/saassuite/fonts"
        vf = f"ass={ass}:fontsdir={fonts}"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-vf", vf, "-af", "loudnorm=I=-14:TP=-1:LRA=9",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", f"{fps}",
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", a.out])
    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
