#!/usr/bin/env python3
"""Podcast audio clips: extract the audio of each clip's local render (no processing) and upload it to Drive.

For every /home/user/work/formats/<clip>/<clip>-v1.mp4 (else the lowest vN that exists):
  ffmpeg -vn, audio stream copied when it is AAC, else plain AAC 128k encode. No filters of any kind.
Uploads to _ENGINE / 02-review / podcast-audio-clips (tools/drive_upload.py; skips names already there),
records {clipId: {driveId, name, mimeType, sizeBytes, sourceRender}} in posting/audio_clips.json,
then deletes only the local .m4a it created.

Usage: python3 tools/export_app_audio.py [--tmp DIR] [clipId ...]
"""
import json, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import drive_upload

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMATS = '/home/user/work/formats'
OUT = os.path.join(ROOT, 'posting', 'audio_clips.json')
FOLDER = 'podcast-audio-clips'


def pick_render(clip):
    d = os.path.join(FORMATS, clip)
    vs = sorted((int(m.group(1)), f) for f in os.listdir(d) if (m := re.fullmatch(re.escape(clip) + r'-v(\d+)\.mp4', f)))
    return os.path.join(d, vs[0][1]) if vs else None  # v1 first, else lowest vN


def acodec(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name',
                        '-of', 'csv=p=0', path], capture_output=True, text=True)
    return r.stdout.strip()


def main():
    args = sys.argv[1:]
    tmp = None
    if args[:1] == ['--tmp']:
        tmp, args = args[1], args[2:]
    tmp = tmp or tempfile.mkdtemp(prefix='audioclips-')
    os.makedirs(tmp, exist_ok=True)
    rec = json.load(open(OUT)) if os.path.exists(OUT) else {}
    clips = args or sorted(os.listdir(FORMATS))
    for clip in clips:
        if clip in rec and rec[clip].get('driveId'):
            continue
        src = pick_render(clip)
        if not src:
            print('no render', clip); continue
        c = acodec(src)
        if not c:
            print('no audio stream', clip); continue
        out = os.path.join(tmp, f'{clip}-audio.m4a')
        codec = ['-c:a', 'copy'] if c == 'aac' else ['-c:a', 'aac', '-b:a', '128k']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-map', '0:a:0', *codec, '-movflags', '+faststart', out], check=True)
        size = os.path.getsize(out)
        url = drive_upload.put(FOLDER, out)
        m = re.search(r'/d/([\w-]{20,})', url or '') or re.search(r'[?&]id=([\w-]{20,})', url or '')
        if not m:
            print('upload gave no id, keeping file', out, url); continue
        rec[clip] = dict(driveId=m.group(1), name=os.path.basename(out), mimeType='audio/mp4', sizeBytes=size,
                         sourceRender=os.path.basename(src), audioCodec='copy' if c == 'aac' else 'aac 128k')
        json.dump(rec, open(OUT, 'w'), indent=1, sort_keys=True)
        os.remove(out)  # only the file this script made, after a confirmed upload
    print(len(rec), 'clips recorded in', OUT)


if __name__ == '__main__':
    main()
