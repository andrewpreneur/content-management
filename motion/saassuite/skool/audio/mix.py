import json,subprocess,sys,re
v=sys.argv[1]; C=json.load(open('/home/user/work/skool/cues.json'))[v]
D=C['dur']; SFX='/home/user/content-management/vendor/motion-graphics/skills/sound-effects/sfx/kit/'
voice=f'/home/user/work/skool/{v}_v2.wav'; music=f'/home/user/work/skool/music-{v}.mp3'
ins=['-i',voice,'-i',music,'-i',SFX+'whoosh.ogg','-i',SFX+'click.ogg']
cues=C['scenes'][1:]
f=[f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0,apad=whole_dur={D}[vo]",
   f"[vo]asplit=2[vo1][vo2]",
   f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{D},afade=t=in:d=1.2,afade=t=out:st={D-2.6}:d=2.6,loudnorm=I=-14:TP=-2:linear=true,volume=0.30[mu]",
   f"[mu][vo2]sidechaincompress=threshold=0.06:ratio=2.5:attack=60:release=600[mud]",
   f"[2:a]aresample=48000,aformat=channel_layouts=stereo,asplit={len(cues)}"+''.join(f'[w{i}]' for i in range(len(cues)))]
for i,t in enumerate(cues): f.append(f"[w{i}]adelay={int(max(0,t-0.12)*1000)}|{int(max(0,t-0.12)*1000)},volume=0.16[wd{i}]")
ck=C['click'][0]; f.append(f"[3:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(ck*1000)}|{int(ck*1000)},volume=0.5[ckd]")
f.append("[vo1][mud]"+''.join(f'[wd{i}]' for i in range(len(cues)))+f"[ckd]amix=inputs={3+len(cues)}:normalize=0:duration=first,atrim=0:{D}[mx]")
fc=';'.join(f)
def run(extra,out):
    return subprocess.run(['ffmpeg','-hide_banner','-y',*ins,'-filter_complex',fc+';[mx]'+extra+'[o]','-map','[o]','-ar','48000',out],capture_output=True,text=True)
r=run('loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','/tmp/claude-0/-home-user-content-management/4429a793-2fa7-5e8d-8b75-1d73799d6b30/scratchpad/m1.wav')
j=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
g=-14-float(j['input_i']); print('gain',round(g,2),'in_tp',j['input_tp'],'-> tp',round(float(j['input_tp'])+g,2))
r=run(f"volume={g:.2f}dB,alimiter=limit=0.84:attack=1:release=50:level=false",f'/home/user/work/skool/{v}_mix.wav')
print(v,'ok' if r.returncode==0 else r.stderr[-800:])
