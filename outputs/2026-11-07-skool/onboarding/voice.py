#!/usr/bin/env python3
"""Generate the voice track for one video + voice with ElevenLabs `with-timestamps`.

  python3 voice.py onb1 andrew           # -> build/onb1_andrew/voice.wav + timing.json
  python3 voice.py onb1 jessica --redo 3 # regenerate paragraph 3 only

Paragraph by paragraph (previous_text / next_text for flow), cached in build/<id>_<voice>/pNN.*.
Spoken text uses pronunciation spellings (SAY); words on screen use the script spelling.
"""
import base64, json, os, re, subprocess, sys
from pathlib import Path
import requests

HERE = Path(__file__).parent
HOST = 'https://api.elevenlabs.io'
VOICES = {
    'andrew': ('Om3UwRqy6aVx0QxEw9Dg', dict(stability=0.5, similarity_boost=0.85, style=0.15, use_speaker_boost=True, speed=0.96)),
    'jessica': ('r1KmysJdVYZjJCm4mL3b', dict(stability=0.45, similarity_boost=0.8, style=0.3, use_speaker_boost=True, speed=1.06)),
    'ash': ('m3yAHyFEFKtbCIM5n7GF', dict(stability=0.45, similarity_boost=0.8, style=0.25, use_speaker_boost=True, speed=1.06)),
    'savvy': ('ogwqBH5bbF03DSbNiRNN', dict(stability=0.5, similarity_boost=0.8, style=0.25, use_speaker_boost=True, speed=1.06)),
    'briggs': ('uhfmGpskiOe0s3pNnkP6', dict(stability=0.45, similarity_boost=0.8, style=0.3, use_speaker_boost=True, speed=1.05)),
    'alex': ('yl2ZDV1MzN4HbQJbMihG', dict(stability=0.45, similarity_boost=0.8, style=0.3, use_speaker_boost=True, speed=1.04)),
}
MODEL = 'eleven_multilingual_v2'
# spoken spelling -> on-screen spelling (one word each side so word counts stay aligned)
SAY = {'GoHighLevel': 'Go High Level', 'SaaS': 'sass'}
LEAD_IN = 2.3      # seconds of intro sting before the first word
GAP = 0.38         # pause between paragraphs
TAIL = 3.4         # end card after last word
SR = 44100


def say_map(text):
    """spoken text + owner list (display word index for every spoken word)."""
    out, owners = [], []
    for i, w in enumerate(text.split(' ')):
        core = re.sub(r'[^\w-]', '', w)
        trail = w[len(w.rstrip('.,!?;:')):] if w else ''
        if core in SAY:
            w = SAY[core] + trail
        for sw in w.split(' '):
            out.append(sw); owners.append(i)
    return ' '.join(out), owners


def say(text):
    return say_map(text)[0]


def tts(voice, text, prev, nxt):
    vid, settings = VOICES[voice]
    body = {'text': text, 'model_id': MODEL, 'voice_settings': settings, 'previous_text': prev, 'next_text': nxt}
    for attempt in range(4):
        r = requests.post(f'{HOST}/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128',
                          headers={'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'dummy'), 'Content-Type': 'application/json'},
                          json=body, timeout=300)
        if r.status_code < 400:
            return r.json()
        print('retry', r.status_code, r.text[:200])
    raise SystemExit('tts failed')


def words_from_alignment(al, display):
    """Group characters into words with start/end; map onto display words by index."""
    chars, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    words, cur = [], None
    for c, s, e in zip(chars, st, en):
        if c.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {'w': '', 's': s, 'e': e}
        cur['w'] += c; cur['e'] = e
    if cur: words.append(cur)
    disp = display.split(' ')
    _, owners = say_map(display)
    if len(owners) != len(words):
        print(f'  WARN word count {len(words)} spoken vs {len(owners)} expected')
        return [{'w': w['w'], 's': w['s'], 'e': w['e']} for w in words]
    merged = {}
    for k, w in enumerate(words):
        o = owners[k]
        if o in merged: merged[o]['e'] = w['e']
        else: merged[o] = {'w': disp[o], 's': w['s'], 'e': w['e']}
    return [merged[i] for i in sorted(merged)]


def decode(mp3, wav):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(mp3), '-ac', '1', '-ar', str(SR), str(wav)], check=True)


def main():
    vid_id, voice = sys.argv[1], sys.argv[2]
    redo = {int(x) for x in sys.argv[sys.argv.index('--redo') + 1].split(',')} if '--redo' in sys.argv else set()
    global GAP, TAIL
    paras = json.loads((HERE / 'scripts.json').read_text())[vid_id]['paras']
    if vid_id in ('intro', 'ask'):
        GAP, TAIL = 0.6, 4.5   # shorts: a touch more air so each step lands
    d = HERE / 'build' / f'{vid_id}_{voice}'; d.mkdir(parents=True, exist_ok=True)
    import numpy as np, soundfile as sf
    pieces, timing, t = [np.zeros(int(LEAD_IN * SR), dtype=np.float32)], [], LEAD_IN
    for i, p in enumerate(paras):
        js, mp3, wav = d / f'p{i:02d}.json', d / f'p{i:02d}.mp3', d / f'p{i:02d}.wav'
        if i in redo or not js.exists():
            prev = say(' '.join(paras[max(0, i - 2):i])); nxt = say(paras[i + 1]) if i + 1 < len(paras) else ''
            res = tts(voice, say(p), prev, nxt)
            mp3.write_bytes(base64.b64decode(res['audio_base64']))
            js.write_text(json.dumps(res['alignment'])); decode(mp3, wav)
            print(f'  generated p{i:02d} ({len(p)} chars)')
        al = json.loads(js.read_text())
        a, _ = sf.read(wav, dtype='float32')
        words = words_from_alignment(al, p)
        # trim trailing silence after the last word (keep 60 ms)
        end = min(len(a), int((words[-1]['e'] + 0.06) * SR)); a = a[:end]
        for w in words: w['s'] = round(w['s'] + t, 3); w['e'] = round(w['e'] + t, 3)
        timing.append({'text': p, 'start': words[0]['s'], 'end': words[-1]['e'], 'words': words})
        pieces.append(a); t += len(a) / SR
        pieces.append(np.zeros(int(GAP * SR), dtype=np.float32)); t += GAP
    pieces.append(np.zeros(int((TAIL - GAP) * SR), dtype=np.float32)); t += TAIL - GAP
    audio = np.concatenate(pieces)
    sf.write(d / 'voice.wav', audio, SR)
    (d / 'timing.json').write_text(json.dumps({'id': vid_id, 'voice': voice, 'duration': round(len(audio) / SR, 3), 'paras': timing}, indent=0))
    print(f'{vid_id}_{voice}: {len(audio) / SR:.1f}s')


if __name__ == '__main__':
    main()
