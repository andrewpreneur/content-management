#!/usr/bin/env python3
"""Paragraph-by-paragraph ElevenLabs TTS with word timestamps.

  python3 tts.py <script.txt> <voice_id> <out_dir> [--model eleven_multilingual_v2] [--only 3,5] [--style 0.3]

For each paragraph: POST /v1/text-to-speech/{voice}/with-timestamps with previous_text/next_text,
save p01.mp3 + p01.json (character alignment). Then build.py stitches them into one timeline.
Spoken text can differ from display text through SAY (pronunciation fixes); display words stay as written.
"""
import argparse, base64, json, os, sys, time
from pathlib import Path
import requests

HOST = 'https://api.elevenlabs.io'
# pronunciation fixes: display -> spoken (applied only to the TTS text)
SAY = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script'); ap.add_argument('voice'); ap.add_argument('out')
    ap.add_argument('--model', default='eleven_multilingual_v2')
    ap.add_argument('--only', default='')
    ap.add_argument('--stability', type=float, default=0.42)
    ap.add_argument('--similarity', type=float, default=0.8)
    ap.add_argument('--style', type=float, default=0.25)
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args()
    paras = [l.strip() for l in Path(a.script).read_text().splitlines() if l.strip()]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    only = {int(x) for x in a.only.split(',') if x}
    for i, p in enumerate(paras, 1):
        if only and i not in only:
            continue
        spoken = p
        for k, v in SAY.items():
            spoken = spoken.replace(k, v)
        body = {
            'text': spoken, 'model_id': a.model,
            'voice_settings': {'stability': a.stability, 'similarity_boost': a.similarity, 'style': a.style,
                               'use_speaker_boost': True, 'speed': a.speed},
            'previous_text': ' '.join(paras[max(0, i - 3):i - 1]) or None,
            'next_text': ' '.join(paras[i:i + 2]) or None,
            'seed': a.seed + i,
        }
        for attempt in range(4):
            r = requests.post(f'{HOST}/v1/text-to-speech/{a.voice}/with-timestamps?output_format=mp3_44100_192',
                              headers={'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'dummy'),
                                       'Content-Type': 'application/json'}, json=body, timeout=300)
            if r.status_code < 400:
                break
            print('retry', r.status_code, r.text[:200], file=sys.stderr); time.sleep(3 * (attempt + 1))
        else:
            raise SystemExit(f'failed paragraph {i}')
        d = r.json()
        (out / f'p{i:02d}.mp3').write_bytes(base64.b64decode(d['audio_base64']))
        json.dump({'text': p, 'spoken': spoken, 'alignment': d.get('alignment'),
                   'settings': body['voice_settings'], 'model': a.model, 'voice': a.voice},
                  open(out / f'p{i:02d}.json', 'w'))
        print('ok', i, len(spoken), 'chars')


if __name__ == '__main__':
    main()
