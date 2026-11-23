#!/usr/bin/env python3
"""Find a long-form video's intro and outro from its layout.

Andrew's long-form edits open with him full screen (the intro), switch to "V+S" (him in a small window + the screen
recording, picture-in-picture) for the body, then go back to full screen (the outro, often ending on a brand card).
This samples 1 frame a second from the start and the end, labels each frame and finds the switches.

  python3 tools/longform_layout.py VIDEO_OR_URL [--window 300] [--fallback 40] [--json out.json]

VIDEO_OR_URL can be a local file or an http(s) URL with range support (e.g. tools/drive_range_proxy.py).
Prints JSON: {duration, intro: {start, end, seconds, method}, outro: {start, end, seconds, method}, timeline: {head, tail}}
method: "layout" (found the switch), "fallback" (no switch in the window: first --fallback seconds / no outro).

Frame label (192x108 gray, right three quarters of the frame): "screen" when most 6x6 blocks are flat (UI, screen
recordings), "card" when flat but dark (end/title cards, counted with the outro), else "speaker" (camera). Calibrated on V+S edits: speaker ≈ 0.13–0.20 flat, screen ≥ 0.39.
A layout change only counts when it lasts 3+ seconds.
"""
import argparse, json, subprocess, sys
import numpy as np

W, H, FLAT = 192, 108, 0.30


def duration(src):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip())


def labels(src, start, length):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(start), '-i', src, '-t', str(length), '-vf', f'fps=1,scale={W}:{H}',
                          '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
    out = []
    while True:
        b = p.stdout.read(W * H)
        if len(b) < W * H: break
        g = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.int16)[:, W // 4:]
        blk = g[:H // 6 * 6, :g.shape[1] // 6 * 6].reshape(H // 6, 6, -1, 6).std(axis=(1, 3))
        flat = (blk < 2.5).mean()
        # end cards / title cards: flat but dark with almost no bright pixels (screen recordings always have bright text/UI)
        out.append('speaker' if flat <= FLAT else 'card' if (g > 200).mean() < 0.03 and g.mean() < 100 else 'screen')
    p.wait()
    return out


def runs(lab, t0):
    """[(label, start, end)] with runs shorter than 3 s merged into the previous run."""
    r = []
    for i, l in enumerate(lab):
        if r and r[-1][0] == l: r[-1][2] = t0 + i + 1
        else: r.append([l, t0 + i, t0 + i + 1])
    m = []
    for x in r:
        if m and (x[2] - x[1] < 3 or x[0] == m[-1][0]): m[-1][2] = x[2]
        else: m.append(x)
    return [tuple(x) for x in m]


def analyze(src, window=300, fallback=40):
    d = duration(src); win = min(window, d)
    # a dark flat frame is an end card only in the last 20 s; anywhere else it's a dark-mode screen recording
    fix = lambda lab, t0: [('screen' if l == 'card' and t0 + i < d - 20 else l) for i, l in enumerate(lab)]
    head = runs(fix(labels(src, 0, win), 0), 0)
    tail_start = max(0, d - win)
    tail = head if tail_start == 0 else runs(fix(labels(src, tail_start, win), int(tail_start)), int(tail_start))
    first_screen = next((s for l, s, e in head if l == 'screen' and s > 0), None)
    intro = ({'start': 0, 'end': first_screen, 'seconds': first_screen, 'method': 'layout'} if first_screen
             else {'start': 0, 'end': min(fallback, d), 'seconds': min(fallback, d), 'method': 'fallback'})
    last_screen_end = max((e for l, s, e in tail if l == 'screen'), default=None)
    outro = ({'start': last_screen_end, 'end': round(d, 2), 'seconds': round(d - last_screen_end, 2), 'method': 'layout'}
             if last_screen_end and d - last_screen_end >= 2 else {'start': None, 'end': None, 'seconds': 0, 'method': 'none'})
    return {'duration': round(d, 2), 'intro': intro, 'outro': outro,
            'timeline': {'head': [list(x) for x in head], 'tail': [list(x) for x in tail]}}


if __name__ == '__main__':
    a = argparse.ArgumentParser(); a.add_argument('src'); a.add_argument('--window', type=float, default=300)
    a.add_argument('--fallback', type=float, default=40); a.add_argument('--json')
    o = a.parse_args(); r = analyze(o.src, o.window, o.fallback)
    s = json.dumps(r, indent=1); print(s)
    if o.json: open(o.json, 'w').write(s)
