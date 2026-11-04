#!/usr/bin/env python3
"""Clip bank: turn hand-picked moments into exact clips with cleaned voice and a review preview.

Usage:
  python3 tools/clip_bank.py outputs/clip-bank/pod3.json [--preview] [--only ID ...]
Spec (JSON): {"source": "/path/video.mp4", "transcript": "/path/transcript.json", "work": "/path/workdir",
              "clips": [{"id": "pod3-02", "start": "first words of the clip", "end": "last words of the clip",
                         "after": 230.0, "title": "2-line story title", "hook_q": "Question hook?", "hook_plain": "...",
                         "speaker": "who talks", "topic": "...", "notes": "..."}]}
`start`/`end` are matched against the transcript words (case/punctuation-insensitive), so in/out points land on word
boundaries. `after` (seconds) disambiguates repeated phrases. Writes the resolved times back into the spec, the
cleaned voice to WORK/<id>.voice.wav (tools/clean_audio.py --gate strong, Andrew-approved), the words with clip-relative
times to WORK/<id>.words.json, and with --preview a 1080x1920 letterbox preview WORK/<id>.preview.mp4
(16:9 band, title on top, one-word captions — the S4/V2 story layout, fast ffmpeg-only).
"""
import argparse, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / 'tools/fonts/InterTight-ExtraBold.ttf'
PRE, POST = 0.08, 0.30  # breathing room around the first/last word


def norm(w):
    return re.sub(r"[^a-z0-9]", '', w.lower().replace('’', "'"))


def find(words, phrase, after=0.0, last=False):
    toks = [norm(t) for t in phrase.split() if norm(t)]
    nw = [norm(w['w']) for w in words]
    for i in range(len(words) - len(toks) + 1):
        if words[i]['s'] < after: continue
        if nw[i:i + len(toks)] == toks:
            return (i + len(toks) - 1) if last else i
    raise SystemExit(f'phrase not found after {after}s: "{phrase}"')


def ass_time(t):
    h, r = divmod(max(0, t), 3600); m, s = divmod(r, 60); return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--preview', action='store_true'); ap.add_argument('--only', nargs='*')
    a = ap.parse_args(); sp = Path(a.spec); S = json.loads(sp.read_text())
    words = [w for s in json.loads(Path(S['transcript']).read_text())['segments'] for w in s['words']]
    work = Path(S['work']); work.mkdir(parents=True, exist_ok=True)
    for c in S['clips']:
        i = find(words, c['start'], c.get('after', 0.0)); j = find(words, c['end'], words[i]['s'], last=True)
        t0 = round(max(0, words[i]['s'] - PRE), 2); t1 = round(words[j]['e'] + POST, 2)
        c['t0'], c['t1'], c['dur'] = t0, t1, round(t1 - t0, 2)
        c['text'] = ' '.join(w['w'] for w in words[i:j + 1])
        if a.only and c['id'] not in a.only: continue
        cw = [[w['w'], round(w['s'] - t0, 2), round(w['e'] - t0, 2)] for w in words[i:j + 1]]
        (work / f"{c['id']}.words.json").write_text(json.dumps(cw, ensure_ascii=False))
        voice = work / f"{c['id']}.voice.wav"
        if not voice.exists():
            subprocess.run(['python3', str(ROOT / 'tools/clean_audio.py'), S['source'], str(voice), '--start', str(t0), '--dur', str(c['dur']),
                            '--gate', 'strong'], check=True, capture_output=True)
        if a.preview:
            ass = work / f"{c['id']}.ass"
            ev = [f"Dialogue: 0,{ass_time(w[1])},{ass_time(cw[k + 1][1] if k + 1 < len(cw) else w[2] + 0.3)},W,,0,0,0,,{w[0]}" for k, w in enumerate(cw)]
            ass.write_text('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n'
                           'Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Alignment, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow\n'
                           'Style: W,Inter Tight ExtraBold,44,&H00FFFFFF,&H00000000,&H80000000,0,7,70,0,930,1,0,2\n\n'
                           '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n' + '\n'.join(ev) + '\n')
            title = work / f"{c['id']}.title.txt"; title.write_text(c.get('title', ''))
            vf = (f"scale=1080:-2,pad=1080:1920:0:656:black,drawtext=fontfile={FONT}:textfile={title}:fontsize=46:fontcolor=white:"
                  f"line_spacing=12:x=(w-text_w)/2:y=470,subtitles={ass}:fontsdir={FONT.parent}")
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t0), '-t', str(c['dur']), '-i', S['source'], '-i', str(voice),
                            '-map', '0:v', '-map', '1:a', '-vf', vf, '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                            '-af', 'loudnorm=I=-16:TP=-2', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                            str(work / f"{c['id']}.preview.mp4")], check=True)
        print(f"{c['id']}: {t0:.2f}-{t1:.2f} ({c['dur']} s) {c['text'][:70]}…")
    sp.write_text(json.dumps(S, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
