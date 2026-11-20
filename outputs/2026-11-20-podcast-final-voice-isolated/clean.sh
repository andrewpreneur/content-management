#!/bin/bash
# Clean the FINAL edited audio (per channel, ElevenLabs voice isolator), rejoin to stereo at the source's 44.1 kHz, exact length.
set -uo pipefail
p=$1; cd /home/user/work/podfinal/$p
src=final.m4a
n=$(ffmpeg -v error -i $src -ac 1 -f s16le - | wc -c); n=$((n/2))
for ch in 0 1; do
  [ -s iso_c$ch.mp3 ] && continue
  ffmpeg -v error -y -i $src -af "pan=mono|c0=c$ch" -c:a flac in_c$ch.flac
  for try in 1 2 3; do
    code=$(curl -sS --max-time 1800 -o iso_c$ch.mp3 -w "%{http_code}" -X POST https://api.elevenlabs.io/v1/audio-isolation -H "xi-api-key: $ELEVENLABS_API_KEY" -F "audio=@in_c$ch.flac") || code=ERR
    echo "$p ch$ch try$try http=$code"; [ "$code" = 200 ] && break; head -c 300 iso_c$ch.mp3; echo; rm -f iso_c$ch.mp3; sleep 15
  done
  rm -f in_c$ch.flac
  [ -s iso_c$ch.mp3 ] || { echo "$p FAIL"; exit 1; }
done
ffmpeg -v error -y -i iso_c0.mp3 -i iso_c1.mp3 -filter_complex \
 "[0:a]aresample=44100:resampler=soxr,apad,atrim=end_sample=$n[l];[1:a]aresample=44100:resampler=soxr,apad,atrim=end_sample=$n[r];[l][r]join=inputs=2:channel_layout=stereo[a]" \
 -map "[a]" -c:a pcm_s16le clean.wav
ffmpeg -v error -y -i clean.wav -c:a libmp3lame -b:a 320k clean.mp3
echo "$p done orig=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $src) wav=$(ffprobe -v error -show_entries format=duration -of csv=p=0 clean.wav)"
