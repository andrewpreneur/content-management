import json,re,sys
def norm(x): return re.sub(r"[^a-z0-9']","",x.lower())
def load(n): return json.load(open(n+'.words.json'))
def find(W,phrase,after=0):
    p=[norm(x) for x in phrase.split()]
    for i in range(len(W)):
        if W[i]['s']<after: continue
        if all(i+k<len(W) and norm(W[i+k]['w']).replace('-','')==p[k] for k in range(len(p))):
            return W[i]['s'],W[i+len(p)-1]['e'],i
    return None
if __name__=='__main__':
    W=load(sys.argv[1])
    for ph in sys.argv[2:]:
        a,_,b=ph.partition('@'); print(ph,find(W,a,float(b or 0)))
