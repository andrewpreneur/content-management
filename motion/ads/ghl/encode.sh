cd /home/user/work/ads
declare -A N=([ag1]=yourghlagent-hands-off [ag2]=yourghlagent-one-prompt [sp1]=yourghlsupport-60-minute-race [sp2]=yourghlsupport-hold-music)
for c in ag1 ag2 sp1 sp2; do for f in h v; do
  until grep -q "done $c $f" render.log; do sleep 15; done
  r=$([ $f = h ] && echo 16x9 || echo 9x16)
  ffmpeg -loglevel error -y -framerate 30 -i frames/$c-$f/%05d.jpg -i ${c}_mix.wav -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest out/${N[$c]}-$r.mp4 && rm -rf frames/$c-$f && echo encoded $c $f
done; done
