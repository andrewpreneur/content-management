import sys,json,subprocess,numpy as np
from faster_whisper import WhisperModel
src,out=sys.argv[1],sys.argv[2]
raw=subprocess.run(['ffmpeg','-v','error','-i',src,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
a=np.frombuffer(raw,np.float32)
m=WhisperModel('small.en',device='cpu',compute_type='int8')
segs,_=m.transcribe(a,word_timestamps=True,language='en')
W=[]
for s in segs:
  for w in s.words: W.append([w.word.strip(),round(w.start,2),round(w.end,2)])
json.dump(W,open(out,'w'))
print(' '.join(w[0] for w in W)); print('last',W[-1])
