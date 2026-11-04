#!/usr/bin/env python3
"""Minimal ElevenLabs client: auth test, find Andrew's cloned voice, text-to-speech, dubbing. Dry-run + char cap.

Auth: header `xi-api-key: <key>`.  Env: ELEVENLABS_API_KEY. (In a Claude cloud session the proxy may inject it;
then a dummy works — but the proxy must send it as `xi-api-key`, not `Authorization`.)

Usage:
  python3 tools/elevenlabs_client.py test                    # auth check + plan/character balance
  python3 tools/elevenlabs_client.py voices                  # list voices; cloned ones marked
  python3 tools/elevenlabs_client.py tts VOICE_ID script.md out.mp3 [--dry-run] [--model eleven_multilingual_v2]
  python3 tools/elevenlabs_client.py dub in.mp4 es out_es.mp4 [--dry-run]
Rules: never create a new voice clone without Andrew's approval and a clone on file (overnight brief).
Cap: ELEVENLABS_MAX_CHARS per tts call (default 12000).
"""
import argparse, json, os, sys, time
from pathlib import Path

HOST = 'https://api.elevenlabs.io'


def hdr(json_ct=True):
    h = {'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'dummy')}
    if json_ct:
        h['Content-Type'] = 'application/json'
    return h


def get(path):
    import requests
    r = requests.get(HOST + path, headers=hdr(), timeout=60)
    if r.status_code >= 400:
        raise SystemExit(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    return r.json()


def clean_script(text):
    """Strip markdown, stage directions in [brackets] and **bold** headers so only spoken words remain."""
    import re
    lines = []
    for ln in text.splitlines():
        if ln.startswith('#') or ln.startswith('_'):
            continue
        ln = re.sub(r'\*\*\[.*?\]\*\*', '', ln); ln = re.sub(r'\[.*?\]', '', ln)
        ln = ln.replace('**', '').strip()
        if ln:
            lines.append(ln)
    return '\n'.join(lines)


def cmd_test(_):
    import requests
    r = requests.get(HOST + '/v1/user/subscription', headers=hdr(), timeout=30)
    if r.status_code >= 400:
        print(f"AUTH FAILED — HTTP {r.status_code} — {r.text[:200]}"); sys.exit(1)
    d = r.json()
    print(f"OK — tier {d.get('tier')}, characters {d.get('character_count')}/{d.get('character_limit')}")


def cmd_voices(_):
    d = get('/v2/voices?page_size=100')
    for v in d.get('voices', []):
        tag = 'CLONE' if v.get('category') in ('cloned', 'professional') else ''
        print(f"{v['voice_id']}  {tag:5}  {v['name']}  ({v.get('category')})")


def cmd_tts(a):
    text = clean_script(Path(a.script).read_text())
    cap = int(os.environ.get('ELEVENLABS_MAX_CHARS', '12000'))
    body = {'text': text, 'model_id': a.model, 'voice_settings': {'stability': 0.45, 'similarity_boost': 0.85, 'style': 0.2}}
    if a.dry_run or len(text) > cap:
        print(json.dumps({'DRY_RUN': True, 'url': f'{HOST}/v1/text-to-speech/{a.voice}', 'chars': len(text), 'cap': cap,
                          'preview': text[:300]}, indent=1))
        if len(text) > cap:
            raise SystemExit('Over character cap; raise ELEVENLABS_MAX_CHARS deliberately.')
        return
    import requests
    r = requests.post(f'{HOST}/v1/text-to-speech/{a.voice}?output_format=mp3_44100_128', headers=hdr(), json=body, timeout=300)
    if r.status_code >= 400:
        raise SystemExit(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    Path(a.out).write_bytes(r.content); print('saved', a.out, f'({len(text)} chars)')


def cmd_dub(a):
    if a.dry_run:
        print(json.dumps({'DRY_RUN': True, 'url': f'{HOST}/v1/dubbing', 'file': a.src, 'target_lang': a.lang,
                          'note': 'dubbing keeps Andrew\'s voice timbre; check result before posting'}, indent=1)); return
    import requests
    with open(a.src, 'rb') as f:
        r = requests.post(f'{HOST}/v1/dubbing', headers=hdr(False), files={'file': f},
                          data={'target_lang': a.lang, 'source_lang': 'en', 'num_speakers': 1, 'watermark': 'false'}, timeout=600)
    if r.status_code >= 400:
        raise SystemExit(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    did = r.json()['dubbing_id']; print('dubbing_id', did)
    for _ in range(180):
        s = get(f'/v1/dubbing/{did}')
        print('status:', s.get('status'))
        if s.get('status') == 'dubbed':
            r = requests.get(f'{HOST}/v1/dubbing/{did}/audio/{a.lang}', headers=hdr(False), timeout=600)
            Path(a.out).write_bytes(r.content); print('saved', a.out); return
        if s.get('status') == 'failed':
            raise SystemExit(f'Dubbing failed: {s}')
        time.sleep(10)
    raise SystemExit('Timed out waiting for dubbing')


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('test'); sub.add_parser('voices')
    t = sub.add_parser('tts'); t.add_argument('voice'); t.add_argument('script'); t.add_argument('out')
    t.add_argument('--model', default='eleven_multilingual_v2'); t.add_argument('--dry-run', action='store_true')
    d = sub.add_parser('dub'); d.add_argument('src'); d.add_argument('lang'); d.add_argument('out'); d.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    {'test': cmd_test, 'voices': cmd_voices, 'tts': cmd_tts, 'dub': cmd_dub}[a.cmd](a)


if __name__ == '__main__':
    main()
