import json,subprocess,glob
D=39.0; SF='/home/user/content-management/vendor/motion-graphics/skills/sound-effects/sfx/'
ding=sorted(glob.glob(SF+'ding/*'))[0]
K={'whoosh':(SF+'kit/whoosh.ogg',0.18),'click':(SF+'kit/click.ogg',0.35),'pop':(SF+'kit/pop.ogg',0.25),'tick':(SF+'kit/tick.ogg',0.25),'ding':(ding,0.25)}
C=json.load(open('cues.json')); ins=['-i','vo.mp3','-i','music.mp3']; fl=[]
for i,(t,k) in enumerate(C):
    f,v=K[k]; ins+=['-i',f]; ms=int(t*1000); fl.append(f"[{i+2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[s{i}]")
fl.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={D},asplit=2[v][sc]")
fl.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{D},afade=t=in:d=0.5,afade=t=out:st={D-2}:d=2,volume=0.28[m0]")
fl.append("[m0][sc]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=350[m]")
fl.append("[v][m]"+''.join(f'[s{i}]' for i in range(len(C)))+f"amix=inputs={2+len(C)}:normalize=0:duration=first,atrim=0:{D},loudnorm=I=-14:TP=-1.5:LRA=11[o]")
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[o]','-ar','48000','mix.wav'],check=True)
