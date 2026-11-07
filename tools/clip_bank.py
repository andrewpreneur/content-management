#!/usr/bin/env python3
"""Clip bank: turn hand-picked moments into exact clips with cleaned voice and a review preview.

Usage:
  python3 tools/clip_bank.py outputs/clip-bank/pod3.json [--preview] [--only ID ...]
Spec (JSON): {"source": "/path/video.mp4", "transcript": "/path/transcript.json", "work": "/path/workdir",
              "clips": [{"id": "pod3-02", "start": "first words of the clip", "end": "last words of the clip",
                         "after": 230.0, "title": "2-line story title", "hook_q": "Question hook?", "hook_plain": "...",
                         "speaker": "who talks", "topic": "...", "notes": "...",
                         "fix": {"misheard": "correct"},
                         "emph": ["lead words|KEY WORDS", ...]}]}
`emph` (optional, used by the V8 "Animated" format): 3–8 short punch phrases, in order, each spoken word for word after the
hook ("you're getting|PAID TO LEARN", "for the next|30 YEARS"). Pick the words a human editor would blow up big: the
payoff noun/verb at the end of a clause, numbers, the contrast word. Without it V8 falls back to a word-score heuristic.
A clip can instead have "parts": [{"start":..., "end":...}, ...] — stitched in order into WORK/<id>.src.mp4 (an intro
montage, a question + answer from different moments). `start`/`end` are matched against the transcript words (case/punctuation-insensitive), so in/out points land on word
boundaries. `after` (seconds) disambiguates repeated phrases. Writes the resolved times back into the spec, the
cleaned voice to WORK/<id>.voice.wav (tools/clean_audio.py: ElevenLabs Voice Isolator when the key works, else local
DeepFilterNet with no gate — Andrew, Nov 5: the strong gate cut words out), the words with clip-relative
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
        src = S['source']
        if 'parts' in c:  # a clip stitched from several moments (e.g. an intro montage) → one stitched 4K source file
            rng, cw, text, off = [], [], [], 0.0; fx = c.get('fix', {})
            for p in c['parts']:
                i = find(words, p['start'], p.get('after', 0.0)); j = find(words, p['end'], words[i]['s'], last=True)
                a0 = round(max(0, words[i]['s'] - PRE), 2); a1 = round(words[j]['e'] + POST, 2); rng.append([a0, a1])
                cw += [[fx.get(w['w'].strip(), w['w']), round(w['s'] - a0 + off, 2), round(w['e'] - a0 + off, 2)] for w in words[i:j + 1]]
                text.append(' '.join(w['w'] for w in words[i:j + 1])); off += a1 - a0
            c['ranges'], c['t0'], c['t1'], c['dur'], c['text'] = rng, 0.0, round(off, 2), round(off, 2), ' … '.join(text)
            src = str(work / f"{c['id']}.src.mp4"); c['src'] = src
            if a.only and c['id'] not in a.only: continue
            if not Path(src).exists():  # cut each piece, then join (one filtergraph over 4K runs out of memory)
                pieces = []
                for k, (x, y) in enumerate(rng):
                    pc = work / f"{c['id']}.part{k}.mp4"; pieces.append(pc)
                    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(x), '-t', str(round(y - x, 3)), '-i', S['source'], '-af', f'afade=t=in:d=0.02,afade=t=out:st={y - x - 0.03:.2f}:d=0.03',
                                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-r', '30', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', str(pc)], check=True)
                lst = work / f"{c['id']}.parts.txt"; lst.write_text(''.join(f"file '{pc}'\n" for pc in pieces))
                subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', src], check=True)
                for pc in pieces: pc.unlink()
            t0 = 0.0; t1 = c['t1']
        else:
            i = find(words, c['start'], c.get('after', 0.0)); j = find(words, c['end'], words[i]['s'], last=True)
            t0 = round(max(0, words[i]['s'] - PRE), 2); t1 = round(words[j]['e'] + POST, 2)
            c['t0'], c['t1'], c['dur'] = t0, t1, round(t1 - t0, 2)
            c['text'] = ' '.join(w['w'] for w in words[i:j + 1])
            if a.only and c['id'] not in a.only: continue
            fx = c.get('fix', {})  # per-clip caption fixes for misheard words: {"TV": "GPT"}
            cw = [[fx.get(w['w'].strip(), w['w']), round(w['s'] - t0, 2), round(w['e'] - t0, 2)] for w in words[i:j + 1]]
        (work / f"{c['id']}.words.json").write_text(json.dumps(cw, ensure_ascii=False))
        voice = work / f"{c['id']}.voice.wav"
        if not voice.exists():
            base = ['python3', str(ROOT / 'tools/clean_audio.py'), src, str(voice), '--start', str(t0), '--dur', str(c['dur'])]
            r = subprocess.run(base + ['--engine', 'elevenlabs'], capture_output=True, text=True)
            if r.returncode != 0:  # ElevenLabs not available → local clean-up, no gate
                print(f"  {c['id']}: ElevenLabs failed ({r.stdout.strip()[-80:] or r.stderr.strip()[-80:]}) → local")
                subprocess.run(base + ['--gate', 'none'], check=True, capture_output=True)
        if a.preview:
            ass = work / f"{c['id']}.ass"
            ev = [f"Dialogue: 0,{ass_time(w[1])},{ass_time(cw[k + 1][1] if k + 1 < len(cw) else w[2] + 0.3)},W,,0,0,0,,{w[0]}" for k, w in enumerate(cw)]
            ass.write_text('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n'
                           'Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Alignment, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow\n'
                           'Style: W,Inter Tight ExtraBold,60,&H00FFFFFF,&H00000000,&H80000000,0,8,0,0,1330,1,0,2\n\n'
                           '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n' + '\n'.join(ev) + '\n')
            lines = c.get('title', '').split('\n')[:2]; dt = ''
            for k, ln in enumerate(lines):  # one drawtext per line so each line is centred
                tf = work / f"{c['id']}.title{k}.txt"; tf.write_text(ln)
                dt += f",drawtext=fontfile={FONT}:textfile={tf}:fontsize=50:fontcolor=white:x=(w-text_w)/2:y={560 - 62 * (len(lines) - k)}"
            vf = f"scale=1080:-2,pad=1080:1920:0:656:black{dt},subtitles={ass}:fontsdir={FONT.parent}"
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t0), '-t', str(c['dur']), '-i', src, '-i', str(voice),
                            '-map', '0:v', '-map', '1:a', '-vf', vf, '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                            '-af', 'loudnorm=I=-16:TP=-2', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                            str(work / f"{c['id']}.preview.mp4")], check=True)
        print(f"{c['id']}: {t0:.2f}-{t1:.2f} ({c['dur']} s) {c['text'][:70]}…")
    sp.write_text(json.dumps(S, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
