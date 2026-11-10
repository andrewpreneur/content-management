import subprocess,re,json,sys
v=sys.argv[1]; src=f'out4/skool-{"sales-about" if v=="sales" else "onboarding"}-16x9-v4.mp4'
o=subprocess.run(['ffmpeg','-hide_banner','-i',f'{v}_v2.wav','-af','silencedetect=n=-35dB:d=0.36','-f','null','-'],capture_output=True,text=True).stderr
S=list(zip([float(x) for x in re.findall(r'silence_start: ([0-9.]+)',o)],[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',o)]))
cuts=[]
for a,b in S:
    g=b-a
    if a<0.5: continue
    new=0.12 if (v=='sales' and 23.6<a<24.0) else max(0.25,g*0.55)
    rm=g-new
    if rm<0.08: continue
    rm=round(rm*30)/30; m=(a+b)/2; cuts.append((round(m-rm/2,3),round(m+rm/2,3)))
print(v,len(cuts),'removed',round(sum(b-a for a,b in cuts),2),'s');json.dump(cuts,open(f'{v}_cuts.json','w'))
expr='+'.join(f'between(t,{a},{b})' for a,b in cuts)
# voice only, re-cut (for remix)
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f'{v}_v2.wav','-af',f"aselect='not({expr})',asetpts=N/SR/TB",f'{v}_v3.wav'],check=True)
# video only, frames removed at same spans
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',src,'-an','-vf',f"select='not({expr})',setpts=N/30/TB",'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',f'{v}_v5video.mp4'],check=True)
