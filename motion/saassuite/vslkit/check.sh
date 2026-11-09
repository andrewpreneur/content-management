#!/bin/bash
# check.sh overlay.html WORKDIR 169|916 "t1,t2,..." -> WORKDIR/check<V>.jpg : overlay stills composited on base frames, with head box drawn
H=$1; D=$2; V=$3; TS=$4; K=$(dirname "$0"); mkdir -p $D/chk; rm -f $D/chk/*
node $K/stills.js $H $V $D/chk/o.png "$TS"
hb=$(tail -1 $D/face$V.json | python3 -c "import json,sys;h=json.load(sys.stdin)['head'];print(f'{h[0]}:{h[1]}:{h[2]-h[0]}:{h[3]-h[1]}')")
IFS=: read x y w h <<< "$hb"; i=0
for t in ${TS//,/ }; do ffmpeg -v error -y -ss $t -i $D/b$V.mp4 -i $D/chk/o_$t.png -filter_complex "[0:v]drawbox=x=$x:y=$y:w=$w:h=$h:color=red@0.8:t=4[b];[b][1:v]overlay,drawtext=text='$t':x=10:y=10:fontsize=48:fontcolor=yellow:box=1:boxcolor=black" -frames:v 1 $D/chk/c_$(printf %02d $i).jpg; i=$((i+1)); done
n=$(ls $D/chk/c_*.jpg | wc -l); if [ $V = 169 ]; then sc=640:360; c=4; else sc=270:480; c=8; fi
ffmpeg -v error -y -pattern_type glob -i "$D/chk/c_*.jpg" -vf "scale=$sc,tile=${c}x$(( (n+c-1)/c ))" -frames:v 1 $D/check$V.jpg
