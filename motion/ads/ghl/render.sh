cd /home/user/content-management/motion/ads/ghl
R=/home/user/work/ads/frames
run(){ c=$1; f=$2; n=$3; q=$(( (n+3)/4 )); for k in 0 1 2 3; do node shoot.js $c $f $R/$c-$f $((k*q)) $(( (k+1)*q<n ? (k+1)*q : n )) & done; wait; echo done $c $f; }
for c in "ag1 615" "ag2 555" "sp1 675" "sp2 555"; do set -- $c; run $1 h $2; run $1 v $2; done
