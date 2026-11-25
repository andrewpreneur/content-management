#!/usr/bin/env python3
"""THE caption look for every edit we make (long form, montages, short form). One module, no copies.

Locked from Andrew's approved edits (Fail V+S intro, Nov 24): Inter Display bold, WHITE text with a soft dark outline
and shadow, NO box or pill behind it, 2-4 word phrases broken at punctuation, the word being spoken in violet
(#7B5CFF from styles/saassuite/tokens.json), sentence case (never ALL CAPS), lower third inside the safe area.
Never yellow, never black-on-white boxes, never a different font. tools/style_check.py fails any render that drifts.

  from house_captions import phrases_of, captions_ass, words_to_phrases
"""
import re

ACCENT = "#7B5CFF"


def ass_time(t):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def hex_ass(h, alpha=0):
    h = h.lstrip("#"); return f"&H{alpha:02X}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def captions_ass(phrases, W, H, style=None, title="", sub="", title_at="left", out_y_frac=0.86):
    accent = ((style or {}).get("color", {}) or {}).get("accent", ACCENT)
    fs = round(min(H * 0.052, W * 0.066)); out_y = round(H * out_y_frac)   # vertical: sized by width
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: {0 if H > W else 2}
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



def words_to_phrases(words):
    """[{w, t0, t1}] already on the output timeline → caption phrases (same breaking rules as phrases_of)."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or (re.search(r"[,.!?;:]$", w["w"]) and len(cur) >= 2):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    res = [{"words": p, "t1": p[-1]["t1"] + 0.12} for p in out]
    for a, b in zip(res, res[1:]):
        a["t1"] = min(a["t1"], b["words"][0]["t0"])
    return res
