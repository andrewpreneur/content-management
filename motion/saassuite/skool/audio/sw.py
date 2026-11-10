import json,sys
def words(v):
    d=json.load(open(f'scribe-{v}.json'));return [w for w in d['words'] if w['type']=='word']
if __name__=='__main__':
    W=words(sys.argv[1]);a,b=float(sys.argv[2]),float(sys.argv[3])
    for i,w in enumerate(W):
        if a<=w['start']<=b: print(i,w['text'],round(w['start'],2),round(w['end'],2))
