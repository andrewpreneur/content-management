# prep.sh N PY CAPY : copy overlay + assets into /home/user/work/vN/r and fill placeholders
N=$1; R=/home/user/content-management; D=/home/user/work/v$N/r; mkdir -p $D
cp $R/tools/fonts/InterVariable-opsz-wght-latin.woff2 $R/tools/fonts/Inter-Regular.woff $R/tools/fonts/Inter-SemiBold.woff $R/.claude/skills/saassuite-motion/lib.js $R/motion/saassuite/vsl-kit.js $D/
python3 - "$N" "$2" "$3" <<'PY'
import sys,json;N,py,capy=sys.argv[1:]
R='/home/user/content-management/motion/saassuite/vsl%s/overlay.html'%N;h=open(R).read()
W=json.load(open('/home/user/work/v%s/words.json'%N))
h=h.replace('__WORDS__',json.dumps(W)).replace('__PY__',py).replace('__CAPY__',capy)
open('/home/user/work/v%s/r/overlay.html'%N,'w').write(h)
PY
