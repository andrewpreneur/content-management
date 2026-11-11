import json,subprocess,sys
c=sys.argv[1]; C=json.load(open('/home/user/work/ads/cues.json'))[c]; D=C['dur']
SF='/home/user/content-management/vendor/motion-graphics/skills/sound-effects/sfx/'
import glob
ding=sorted(glob.glob(SF+'ding/*'))[0]
SFX={'whoosh':(SF+'kit/whoosh.ogg',0.35),'click':(SF+'kit/click.ogg',0.5),'pop':(SF+'kit/pop.ogg',0.4),'tick':(SF+'kit/tick.ogg',0.35),'impact':(SF+'kit/impact.ogg',0.55),'ding':(ding,0.4),'key':(SF+'kit/tick.ogg',0.12)}
W='/home/user/work/ads/'
ins=[];fl=[]
if C['music']=='hold+support':
    ins+=['-i',W+'hold.mp3','-i',W+'support.mp3']
    fl.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:5.0,afade=t=in:d=0.3,afade=t=out:st=4.92:d=0.08,volume=0.55,apad=whole_dur={D}[m0]")
    fl.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{D-5.4},afade=t=in:d=0.05,afade=t=out:st={D-5.4-1.5}:d=1.5,volume=0.5,adelay=5400|5400,apad=whole_dur={D}[m1]")
    fl.append("[m0][m1]amix=inputs=2:normalize=0:duration=longest[mu]"); base=2
else:
    ins+=['-i',W+C['music']+'.mp3']
    fl.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{D},afade=t=in:d=0.2,afade=t=out:st={D-1.5}:d=1.5,volume=0.5,apad=whole_dur={D}[mu]"); base=1
labs=[]
for i,(t,k) in enumerate(C['cues']):
    f,v=SFX[k]; ins+=['-i',f]; ms=int(t*1000)
    fl.append(f"[{base+i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[s{i}]"); labs.append(f'[s{i}]')
fl.append('[mu]'+''.join(labs)+f"amix=inputs={1+len(labs)}:normalize=0:duration=first,atrim=0:{D},loudnorm=I=-14:TP=-1.5:LRA=11[o]")
subprocess.run(['ffmpeg','-loglevel','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[o]','-ar','48000',W+c+'_mix.wav'],check=True); print(c,'mixed')
