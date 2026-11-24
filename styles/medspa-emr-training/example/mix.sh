#!/usr/bin/env bash
# Voice lines at the page's cues + music bed ≈ −24 LUFS under the voice (fades out under the outro); final −16 LUFS.
#   ./mix.sh h|v   (after: node tools/explainer_render.mjs "index.html?fmt=<f>" out/<f>.mp4 30 2 3)
set -e; cd "$(dirname "$0")"; F=${1:-h}
MUSIC=${MUSIC:-/home/user/work/medspa/music.mp3}
node -e "
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage();
await p.goto('file://'+process.cwd()+'/index.html?fmt=$F');const r=await p.evaluate(()=>({cues:window.CUES,dur:window.VIDEO.duration}));
require('fs').writeFileSync('cues-$F.json',JSON.stringify(r));await b.close();})()"
python3 - "$MUSIC" "$F" <<'PY'
import json,subprocess,sys
music,f=sys.argv[1],sys.argv[2]; c=json.load(open(f'cues-{f}.json')); dur=c['dur']
ins=[]; fl=[]
for i,(k,t) in enumerate(c['cues']):
    ins+=['-i',f'audio/{k}.mp3']; ms=int(t*1000); fl.append(f'[{i}:a]aresample=48000,adelay={ms}|{ms}[v{i}]')
n=len(c['cues']); out0=[t for k,t in c['cues'] if k=='outro'][0]
fl.append(''.join(f'[v{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0,apad,atrim=0:{dur},loudnorm=I=-16:TP=-2:LRA=7[voice]')
fl.append(f'[{n}:a]aresample=48000,atrim=0:{dur},volume=0.13,afade=t=in:d=0.8,afade=t=out:st={out0+0.6}:d=1.2[bed]')
fl.append('[voice][bed]amix=inputs=2:normalize=0,alimiter=limit=0.89[a]')
name={'h':'desktop','v':'mobile'}[f]
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-stream_loop','-1','-i',music,'-i',f'out/{f}_silent.mp4','-filter_complex',';'.join(fl),
  '-map',f'{n+1}:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(dur),f'out/emr-in-room-{name}.mp4'],check=True)
print(f'mixed -> out/emr-in-room-{name}.mp4 ({dur}s)')
PY
