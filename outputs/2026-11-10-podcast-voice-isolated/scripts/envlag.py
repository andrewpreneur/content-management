# envelope cross-correlation: robust lag (ms) between original channel and isolated channel
import sys, subprocess, numpy as np
def env(p, ss, t, ch):
    cmd=["ffmpeg","-v","error","-ss",str(ss),"-t",str(t),"-i",p,"-af",f"pan=mono|c0=c{ch}","-ar","16000","-f","f32le","-"]
    x=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,dtype=np.float32)
    h=16  # 1 ms hops
    x=np.abs(x[:len(x)//h*h]).reshape(-1,h).mean(1)
    k=np.ones(10)/10; x=np.convolve(x,k,'same')
    return np.log(x+1e-4)
a_p,b_p,ss,t,ch=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4]),int(sys.argv[5])
a=env(a_p,ss,t,ch); b=env(b_p,ss,t,ch); n=min(len(a),len(b)); a=a[:n]-a[:n].mean(); b=b[:n]-b[:n].mean()
L=200; best=None
for lag in range(-L,L+1):
    if lag>=0: r=np.dot(a[lag:],b[:n-lag])
    else: r=np.dot(a[:n+lag],b[-lag:])
    if best is None or r>best[1]: best=(lag,r)
print(f"lag_ms={best[0]} (positive = cleaned is early) corr={best[1]/np.sqrt((a*a).sum()*(b*b).sum()):.3f}")
