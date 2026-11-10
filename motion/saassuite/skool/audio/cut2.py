import json,re,subprocess,sys
def norm(x): return re.sub(r"[^a-z0-9]","",x.lower())
def words(v):
    d=json.load(open(f'scribe-{v}.json'));return [w for w in d['words'] if w['type']=='word']
def find(W,phrase,after=0):
    p=[norm(x) for x in phrase.split()]
    for i in range(after,len(W)):
        if all(i+k<len(W) and norm(W[i+k]['text'])==p[k] for k in range(len(p))): return i
    raise Exception('nf '+phrase)
def seg(W,a,b,after=0):
    i=find(W,a,after); j=find(W,b,i)+len(b.split())-1; return (i,j)
def build(v,src,segs,out,joins):
    W=words(v);pieces=[]
    for n,(i,j) in enumerate(segs):
        pre=W[i]['start']-(W[i-1]['end'] if i>0 else 0); post=(W[j+1]['start'] if j+1<len(W) else W[j]['end']+1)-W[j]['end']
        want=joins[n-1] if n>0 else 0.3
        s=W[i]['start']-min(want/2+0.04,pre*0.5)
        wantn=joins[n] if n<len(joins) else 0.6
        e=W[j]['end']+min(wantn/2+0.04,post*0.5)
        cur=s
        for k in range(i,j):
            g=W[k+1]['start']-W[k]['end']
            if g>0.6:
                pieces.append((cur,W[k]['end']+0.22)); cur=W[k+1]['start']-0.22
        pieces.append((cur,e))
    fl=[]
    for n,(s,e) in enumerate(pieces):
        fl.append(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={e-s-0.008:.3f}:d=0.008[p{n}]")
    fl.append(''.join(f'[p{n}]' for n in range(len(pieces)))+f"concat=n={len(pieces)}:v=0:a=1[o]")
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',src,'-filter_complex',';'.join(fl),'-map','[o]','-c:a','pcm_s24le','-ar','48000',out],check=True)
    print(out,len(pieces),'pieces')
U='/root/.claude/uploads/4429a793-2fa7-5e8d-8b75-1d73799d6b30/'
if sys.argv[1]=='sales':
    W=words('sales')
    S=[seg(W,'if you run a business online','I built this',3),
       seg(W,"Inside you'll get direct access to me and my team who",'offers',100),
       seg(W,"You'll also get access to step-by-step",'trainings',124),
       seg(W,'And other highly','space',139),
       seg(W,'Lastly','Lastly',147),
       seg(W,"You'll also get exclusive access",'personally',156),
       seg(W,"I've worked",'see you inside',171)]
    J=[0.5,0.5,0.15,0.55,0.12,0.6]
    build('sales',U+'7439f9d9-salesaboutaudioraw.m4a',S,'sales_v2.wav',J)
else:
    W=words('onb')
    S=[seg(W,'welcome in to SaaS','Mastery',8),
       seg(W,'You made it. I am glad','out of it',52),
       seg(W,'Number one','stuck on',86),
       seg(W,'And this will be','hold of me',129),
       seg(W,'Responses may','give you answers',142),
       seg(W,'Number two','get started',175),
       seg(W,'And start with the course that matches','build an offer',199),
       seg(W,'And many other things','things',232),
       seg(W,'These are all','YouTube channel',236),
       seg(W,'and from paid courses','paid courses',244),
       seg(W,'that usually I would sell for thousands','community',257),
       seg(W,'Pro tip','watch first',278),
       seg(W,"you won't need all of them so find",'right now',347),
       seg(W,'Number three you get calls and','their family',368),
       seg(W,'Check on the calendar','works for you',412),
       seg(W,'We typically','other successful entrepreneurs',436),
       seg(W,'Number four','run my business',467),
       seg(W,'Now the first','intro post',509),
       seg(W,'This is standard among','goals are',525),
       seg(W,'Make that post','message',556),
       seg(W,"I'm glad you're here",'even better',574)]
    J=[0.6,0.6,0.4,0.55,0.65,0.15,0.4,0.55,0.15,0.12,0.6,0.6,0.7,0.5,0.5,0.7,0.65,0.45,0.5,0.6]
    build('onb',U+'324dc8db-onboardingaudio.m4a',S,'onb_v2.wav',J)
