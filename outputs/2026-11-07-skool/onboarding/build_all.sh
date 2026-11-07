#!/bin/bash
# Render + mix + check every video in both voices. Usage: ./build_all.sh [id:voice ...]
set -e
cd "$(dirname "$0")"
[ -f build/fonts.css ] || python3 make_fonts.py
JOBS=${@:-onb1:andrew onb1:jessica onb2:andrew onb2:briggs onb3:andrew onb3:savvy intro:andrew intro:ash ask:andrew ask:alex}
for j in $JOBS; do
  id=${j%%:*}; v=${j##*:}
  [ -f build/${id}_${v}/timing.json ] || python3 voice.py $id $v
  FPS=${FPS:-60} node render.mjs $id $v | tail -1
  python3 mix.py $id $v 2>&1 | grep -v Warn | tail -1
  python3 check_final.py $id $v 2>&1 | tail -1
done
