# comp.sh dir fmt DUR TOTAL OUT : extend base to TOTAL (clone last frame), overlay PNGs, mux mixed audio
D=$1; F=$2; DUR=$3; TOT=$4; OUT=$5
PAD=$(python3 -c "print(round($TOT-$DUR+0.3,3))")
ffmpeg -v error -y -i $D/b$F.mp4 -vf "fps=30,tpad=stop_mode=clone:stop_duration=$PAD" -an -t $TOT -c:v libx264 -crf 14 -preset veryfast $D/x$F.mp4
ffmpeg -v error -y -i $D/x$F.mp4 -thread_queue_size 512 -framerate 30 -i $D/o$F/%04d.png -i $D/a.m4a -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -t $TOT -c:v libx264 -crf 20 -preset medium -c:a copy -movflags +faststart $OUT
ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 $OUT | tr '\n' ' '; echo
