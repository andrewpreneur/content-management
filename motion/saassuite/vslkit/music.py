#!/usr/bin/env python3
"""ElevenLabs music: python3 music.py OUT.mp3 SECONDS "prompt"  (chunks of <=180 s are joined later by mix.sh)."""
import os, sys, time, requests
out, secs, prompt = sys.argv[1], float(sys.argv[2]), sys.argv[3]
t = time.time()
r = requests.post('https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192',
                  headers={'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'dummy'), 'Content-Type': 'application/json'},
                  json={'prompt': prompt, 'music_length_ms': int(secs * 1000), 'force_instrumental': True}, timeout=900)
print(out, r.status_code, len(r.content), f'{time.time() - t:.0f}s')
if r.status_code >= 400: sys.exit(r.text[:400])
open(out, 'wb').write(r.content)
