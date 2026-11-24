#!/usr/bin/env bash
# Voice lines at their cues (cues.json, from the page) + music bed ≈ −24 LUFS under the voice, fading out at the outro.
set -e; cd "$(dirname "$0")"
MUSIC=${MUSIC:-/home/user/work/medspa/music.mp3}
python3 - "$MUSIC" <<'PY'
import json,subprocess,sys
c=json.load(open('cues.json')); dur=c['dur']; music=sys.argv[1]
ins=[]; f=[]
for i,(k,t) in enumerate(c['cues']):
    ins+=['-i',f'audio/{k}.mp3']; ms=int(t*1000); f.append(f'[{i}:a]aresample=48000,adelay={ms}|{ms}[v{i}]')
n=len(c['cues']); out0=[t for k,t in c['cues'] if k=='outro'][0]
f.append(''.join(f'[v{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,apad,atrim=0:{dur},loudnorm=I=-16:TP=-2:LRA=7[voice]')
f.append(f'[{n}:a]aresample=48000,atrim=0:{dur},volume=0.13,afade=t=in:d=1.0,afade=t=out:st={out0+0.6}:d=1.2[bed]')
f.append('[voice][bed]amix=inputs=2:normalize=0,alimiter=limit=0.89[a]')
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-stream_loop','-1','-i',music,'-i','out/silent_silent.mp4','-filter_complex',';'.join(f),
  '-map',f'{n+1}:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(dur),'out/emr-in-room-desktop.mp4'],check=True)
print('mixed -> out/emr-in-room-desktop.mp4')
PY
