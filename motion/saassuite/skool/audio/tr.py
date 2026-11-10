import sys,json,numpy as np,soundfile as sf
from faster_whisper import WhisperModel
m=WhisperModel("small.en",compute_type="int8")
for n in sys.argv[1:]:
    import subprocess
    a=subprocess.run(["ffmpeg","-loglevel","error","-i",n+".wav","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
    x=np.frombuffer(a,np.float32)
    segs,_=m.transcribe(x,word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
    W=[]
    for s in segs:
        for w in s.words: W.append({"w":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2)})
    json.dump(W,open(n+".words.json","w"))
    # print with gaps
    line=[];
    for i,w in enumerate(W):
        if i and w["s"]-W[i-1]["e"]>0.6: print(f"   [gap {w['s']-W[i-1]['e']:.1f}s]")
        print(f"{w['s']:7.2f} {w['w']}",end="\n")
