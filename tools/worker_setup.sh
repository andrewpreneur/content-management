#!/bin/bash
# Set up a cloud render worker and start it. Usage: WORKER=w1 PODS="pod1" CLIPS="pod1-01,pod1-02" bash tools/worker_setup.sh
# Kit (branch render-kit): transcripts, ElevenLabs-cleaned voices (flac), speaker maps, music beds, dfenv requirements.
set -e; R=/home/user/content-management; X=/home/user/work; mkdir -p $X/bank $X/formats $X/motion/audio; cd $X
[ -d kit ] || git clone -q --depth 1 -b render-kit "$(git -C $R remote get-url origin)" kit
pip install -q librosa soundfile numpy scipy pillow 2>&1 | tail -2
if [ ! -x dfenv/bin/python ]; then python3 -m venv dfenv; dfenv/bin/pip install -q --extra-index-url https://download.pytorch.org/whl/cpu -r kit/requirements-dfenv.txt 2>&1 | tail -2; fi
for p in kit/bank/*/; do pn=$(basename $p); mkdir -p bank/$pn; cp $p/*.words.json bank/$pn/
  cp -n $p/*.src.mp4 bank/$pn/ 2>/dev/null || true
  for f in $p/*.voice.flac; do c=$(basename $f .voice.flac); [ -f bank/$pn/$c.voice.wav ] || ffmpeg -v error -y -i $f bank/$pn/$c.voice.wav; done; done
cp -rn kit/formats/* formats/ 2>/dev/null || true; cp -rn kit/audio/* motion/audio/
declare -A ID=([pod1]=1o16B2yPjlANHRT6xhp6hvU0dh32pJefg [pod2]=19oDJJJ-NDbI9FCOE6XBZTuyPGvXiEln0 [pod3]=1sfvECkswOzt0svNs3O-rOQDRGFGyH4qw)
for p in $PODS; do mkdir -p $p; [ -s $p/$p.mp4 ] || curl -sL --retry 4 -o $p/$p.mp4 "https://drive.usercontent.google.com/download?id=${ID[$p]}&export=download&confirm=t"; ls -la $p/$p.mp4; done
cd $R; for L in 0 1; do RQ_CLIPS="$CLIPS" RQ_DROP=1 WORKER="$WORKER" setsid nohup python3 tools/render_queue.py video $L 2 >> $X/rq_v$L.log 2>&1 < /dev/null & disown; done
echo "worker $WORKER started: $CLIPS"
