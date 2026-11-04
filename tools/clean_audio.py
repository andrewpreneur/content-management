#!/usr/bin/env python3
"""Clean speech audio: remove echo/room reverb and background noise, then a light voice EQ.

Usage:
  python3 tools/clean_audio.py SRC(.mp4|.wav|.m4a) OUT.wav [--engine local|elevenlabs] [--start S --dur D] [--atten 24]

Engines
- elevenlabs: ElevenLabs Voice Isolator (POST /v1/audio-isolation). Best at echo/reverb. Needs the API key working
  (header xi-api-key; see docs/sops/07-ai-clients.md). Costs credits per minute of audio.
- local (default): DeepFilterNet3 (open-source speech enhancement, runs on CPU) in its own venv, then EQ:
  high-pass 80 Hz, -3 dB at 300 Hz (boxy room), +2 dB at 3.5 kHz (clarity). No compressor: it pulls the echo tail back up (measured); sound_mix.py sets loudness.
  --atten caps how much noise/reverb is removed (dB); lower = more natural, higher = drier.
  Setup once: python3 -m venv work/dfenv && work/dfenv/bin/pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
              && work/dfenv/bin/pip install deepfilternet safetensors soundfile ; weights from huggingface.co/fal/DeepFilterNet3
  (env DF_PY = venv python, DF_MODEL = model dir with config.ini + checkpoints/).
Use the cleaned WAV as the "source" in a voice ranges file for tools/sound_mix.py.
"""
import argparse, os, subprocess, sys, tempfile
from pathlib import Path

DF_PY = os.environ.get('DF_PY', '/home/user/work/dfenv/bin/python')
DF_MODEL = os.environ.get('DF_MODEL', '/home/user/work/dfmodel/DeepFilterNet3')
EQ = "highpass=f=80,equalizer=f=300:t=q:w=1.2:g=-3,equalizer=f=3500:t=q:w=1.0:g=2"

DF_SCRIPT = r'''
import sys, torch, soundfile as sf
from df.enhance import init_df, enhance
model, st, _ = init_df(sys.argv[3])
a, sr = sf.read(sys.argv[1], dtype='float32')          # 48 kHz mono from ffmpeg
x = torch.from_numpy(a).unsqueeze(0)
lim = float(sys.argv[4]); out = enhance(model, st, x, atten_lim_db=lim if lim > 0 else None)
sf.write(sys.argv[2], out.squeeze(0).numpy(), st.sr())
'''


def run(c):
    subprocess.run(c, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--engine', default='local', choices=['local', 'elevenlabs'])
    ap.add_argument('--start', type=float); ap.add_argument('--dur', type=float)
    ap.add_argument('--atten', type=float, default=24.0); ap.add_argument('--no-eq', action='store_true')
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, 'raw.wav')
        cut = (['-ss', str(a.start)] if a.start is not None else []) + (['-t', str(a.dur)] if a.dur else [])
        run(['ffmpeg', '-y', '-v', 'error', *cut, '-i', a.src, '-vn', '-ac', '1', '-ar', '48000', raw])
        clean = os.path.join(td, 'clean.wav')
        if a.engine == 'elevenlabs':
            import requests
            with open(raw, 'rb') as f:
                r = requests.post('https://api.elevenlabs.io/v1/audio-isolation', headers={'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'dummy')},
                                  files={'audio': ('audio.wav', f, 'audio/wav')}, timeout=900)
            if r.status_code >= 400:
                raise SystemExit(f'ElevenLabs Voice Isolator {r.status_code}: {r.text[:300]}  (fallback: --engine local)')
            iso = os.path.join(td, 'iso.mp3'); Path(iso).write_bytes(r.content)
            run(['ffmpeg', '-y', '-v', 'error', '-i', iso, '-ac', '1', '-ar', '48000', clean])
        else:
            sp = os.path.join(td, 'dfn_run.py'); Path(sp).write_text(DF_SCRIPT)
            run([DF_PY, sp, raw, clean, DF_MODEL, str(a.atten)])
        af = 'anull' if a.no_eq else EQ
        run(['ffmpeg', '-y', '-v', 'error', '-i', clean, '-af', af, '-ac', '1', '-ar', '48000', a.out])
    print('cleaned →', a.out)


if __name__ == '__main__':
    main()
