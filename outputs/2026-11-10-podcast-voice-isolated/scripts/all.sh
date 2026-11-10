#!/bin/bash
cd /home/user/work/podiso
for pair in "pod1|pod1audio" "pod2|Pod2audio" "pod5|Podcast5" "pod4|Podcast 4"; do
  ep=${pair%%|*}; nm=${pair#*|}; base="$nm - voice isolated"
  echo "##### $ep"
  ./scripts/process.sh $ep "$base" 2>&1 | grep -v "^[-d]rw\|^total" || { echo "$ep PROCESS FAILED"; continue; }
  (cd $ep && python3 /home/user/content-management/tools/drive_upload.py put "Podcast audio - voice isolated/$ep" "$base.wav" "$base.mp3") || echo "$ep UPLOAD FAILED"
  rm -f "$ep/$base.wav" $ep/iso_c*.mp3 "$ep/$base.mp3"
  df -h / | tail -1
done
echo ALLDONE
