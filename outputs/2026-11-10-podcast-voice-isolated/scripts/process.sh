#!/bin/bash
# usage: process.sh <ep> "<output base name>"
set -euo pipefail
ep=$1; base=$2; d=/home/user/work/podiso/$ep; cd $d
src=src/orig.m4a
sr=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 $src)
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $src)
# exact sample count of the original stream, converted to 48k
ns=$(ffmpeg -v error -i $src -ac 1 -f s16le - | wc -c); ns=$((ns/2))
n48=$(python3 -c "print(round($dur*48000))")
echo "sr=$sr dur=$dur samples=$ns n48=$n48"
for ch in 0 1; do
  [ -s iso_c$ch.mp3 ] && continue
  ffmpeg -v error -y -i $src -af "pan=mono|c0=c$ch" -c:a flac in_c$ch.flac
  for try in 1 2 3; do
    code=$(curl -sS --max-time 1800 -o iso_c$ch.mp3 -w "%{http_code}" -X POST https://api.elevenlabs.io/v1/audio-isolation -H "xi-api-key: $ELEVENLABS_API_KEY" -F "audio=@in_c$ch.flac") || code=ERR
    echo "ch$ch try$try http=$code"; [ "$code" = 200 ] && break; head -c 400 iso_c$ch.mp3; echo; rm -f iso_c$ch.mp3; sleep 10
  done
  [ -s iso_c$ch.mp3 ] || { echo FAIL; exit 1; }
  rm -f in_c$ch.flac
  echo "iso ch$ch dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 iso_c$ch.mp3)"
done
# decode, resample to 48k (high quality), pad/trim to exact length, merge to stereo
ffmpeg -v error -y -i iso_c0.mp3 -i iso_c1.mp3 -filter_complex \
 "[0:a]aresample=48000:resampler=soxr,apad,atrim=end_sample=$n48[l];[1:a]aresample=48000:resampler=soxr,apad,atrim=end_sample=$n48[r];[l][r]join=inputs=2:channel_layout=stereo[a]" \
 -map "[a]" -c:a pcm_s16le "$base.wav"
ffmpeg -v error -y -i "$base.wav" -c:a libmp3lame -b:a 320k "$base.mp3"
od=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$base.wav")
echo "orig=$dur wav=$od diff_ms=$(python3 -c "print(round(($od-$dur)*1000,2))")"
echo "mp3=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$base.mp3")"
for t in 60 $(python3 -c "print(int($dur/2))") $(python3 -c "print(int($dur-90))"); do
  for ch in 0 1; do echo -n "t=$t ch$ch "; python3 -I ../scripts/envlag.py $src "$base.wav" $t 40 $ch; done
done
ls -la; df -h / | tail -1
