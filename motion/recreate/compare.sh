#!/bin/bash
# compare.sh REF.mp4 START_S DUR_S RECREATION_FRAMES_DIR FPS OUT_PREFIX
# -> OUT_PREFIX-side.mp4 (ref | recreation | diff) and OUT_PREFIX-ssim.txt (per-frame + average SSIM)
ref=$1; ss=$2; d=$3; fr=$4; fps=$5; o=$6
ffmpeg -v error -y -ss $ss -t $d -i "$ref" -vf "fps=$fps,scale=1280:-2,format=yuv420p" -an /tmp/_ref_$$.mp4
ffmpeg -v error -y -framerate $fps -i "$fr/%04d.png" -vf "scale=1280:-2,format=yuv420p" /tmp/_rec_$$.mp4
ffmpeg -v error -y -i /tmp/_ref_$$.mp4 -i /tmp/_rec_$$.mp4 -filter_complex "[0][1]blend=all_mode=difference,eq=brightness=0.05:contrast=3[d];[0][1][d]hstack=3" -c:v libx264 -crf 22 "$o-side.mp4"
ffmpeg -i /tmp/_ref_$$.mp4 -i /tmp/_rec_$$.mp4 -lavfi "ssim=stats_file=$o-ssim.txt" -f null - 2>&1 | grep -o 'All:[0-9.]*' | tail -1
rm -f /tmp/_ref_$$.mp4 /tmp/_rec_$$.mp4
