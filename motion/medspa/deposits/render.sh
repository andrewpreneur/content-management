cd /home/user/content-management/motion/medspa/deposits
R=/home/user/work/medspa/frames; N=1170; q=$(( (N+3)/4 ))
for f in h v; do for k in 0 1 2 3; do node shoot.js $f $R/$f $((k*q)) $(( (k+1)*q<N ? (k+1)*q : N )) & done; wait
r=$([ $f = h ] && echo 16x9 || echo 9x16)
ffmpeg -loglevel error -y -framerate 30 -i $R/$f/%05d.jpg -i /home/user/work/medspa/mix.wav -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest /home/user/work/medspa/medspa-deposits-$r.mp4 && rm -rf "${R:?}/$f" && echo made $f; done; echo ALLDONE
