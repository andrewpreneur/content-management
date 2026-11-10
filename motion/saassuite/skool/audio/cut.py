import json,subprocess,sys,re
from find import find,load
def sil(n):
    o=subprocess.run(["ffmpeg","-hide_banner","-i",n+".wav","-af","silencedetect=n=-38dB:d=0.12","-f","null","-"],capture_output=True,text=True).stderr
    a=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",o)];b=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",o)]
    return list(zip(a,b))
def snap_start(t,S):
    for a,b in S:
        if a-0.05<=t<=b+0.35: return b-0.07
    return t-0.05
def snap_end(t,S):
    for a,b in S:
        if a-0.35<=t<=b+0.05: return a+0.10
    return t+0.05
def build(n,plan,out):
    W=load(n);S=sil(n);keep=[]
    for item in plan:
        if isinstance(item,tuple) and isinstance(item[0],float): s,e=item;gap=0.3
        else:
            a,b,gap=item; ra=find(W,*a) if isinstance(a,tuple) else find(W,a); rb=find(W,*b) if isinstance(b,tuple) else find(W,b)
            assert ra and rb,(a,b)
            s=snap_start(ra[0],S); e=snap_end(rb[1],S)
        # compress internal silences
        cur=s
        for x,y in S:
            if x>s and y<e and y-x>0.42:
                keep.append((cur,x+0.14,0)); cur=y-0.14
        keep.append((cur,e,gap))
    fl=[];t=0
    for i,(s,e,g) in enumerate(keep):
        fl.append(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={e-s-0.012:.3f}:d=0.012,apad=pad_dur={g:.3f}[a{i}]")
    fl.append("".join(f"[a{i}]" for i in range(len(keep)))+f"concat=n={len(keep)}:v=0:a=1,highpass=f=80,afftdn=nf=-32,acompressor=threshold=-20dB:ratio=3:attack=5:release=80[o]")
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",n+".wav","-filter_complex",";".join(fl),"-map","[o]","-ar","48000",out],check=True)
    json.dump(keep,open(out+".keep.json","w"))
