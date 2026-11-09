# mix.py src.mp4 music.mp3 DUR cues.json out.m4a  -- voice + ducked music bed + sfx, loudnorm -14 LUFS / TP -1.5
import sys,json,subprocess
src,mus,dur,cues,out=sys.argv[1:6];dur=float(dur);C=json.load(open(cues))
SFX='/home/user/content-management/vendor/motion-graphics/skills/sound-effects/sfx/'
K={'whoosh':(SFX+'kit/whoosh.ogg',-16),'pop':(SFX+'pop/fs-824189-pop-in-sfx.ogg',-18),'click':(SFX+'click/kenney-interface-click-001.ogg',-14),
   'ding':(SFX+'ding/kenney-interface-confirmation-002.ogg',-16),'tick':(SFX+'click/kenney-interface-tick-001.ogg',-14),'riser':(SFX+'kit/riser.ogg',-24)}
ins=['-i',src,'-i',mus];fc=[];lab=[]
for j,(k,t) in enumerate(C):
  f,g=K[k];ins+=['-i',f];n=j+2
  fc.append(f'[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={int(t*1000)}|{int(t*1000)}[s{j}]');lab.append(f'[s{j}]')
fc.append(f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={dur},asplit=2[v][key]')
fc.append(f'[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{dur},afade=t=in:d=1.2,afade=t=out:st={dur-1.8}:d=1.8,volume=-17dB[m0]')
fc.append('[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[m]')
fc.append(f'[v][m]{"".join(lab)}amix=inputs={2+len(lab)}:normalize=0:duration=first[o]')
tmp=out+'.wav';subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fc),'-map','[o]','-t',str(dur),tmp],check=True)
m=subprocess.run(['ffmpeg','-hide_banner','-i',tmp,'-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(m[m.rfind('{'):m.rfind('}')+1])
ln=f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000"
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-af',ln,'-c:a','aac','-b:a','192k',out],check=True)
r=subprocess.run(['ffmpeg','-hide_banner','-i',out,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
print(out,[l.strip() for l in r.splitlines()[-12:] if 'I:' in l or 'Peak:' in l])
