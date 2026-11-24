#!/usr/bin/env bash
# Self-test for any machine or agent that will make explainers (Your Software Agent, Claude Code, a custom session).
# Cheap (no voice, no render): checks the tools, measures the zip's screenshots, builds the style's example page on them
# and runs the required QA. Exit 0 = ready; anything else says what's missing.
#   bash tools/explainer_selftest.sh KIT_ZIP_DIR STYLE_DIR [OUT_DIR=selftest]
# KIT_ZIP_DIR = the unzipped feature kit (screenshots/, script.md, brand/); STYLE_DIR = an unpacked style pack (style/).
set -u
KITTOOLS="$(cd "$(dirname "$0")/.." && pwd)"; ZIP="$(cd "$1" && pwd)"; STYLE="$(cd "$2" && pwd)"; OUT="${3:-selftest}"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
ok() { echo "ok    $*"; }; bad() { echo "FAIL  $*"; FAILED=1; }; FAILED=0

bash "$KITTOOLS/tools/explainer_setup.sh" >/dev/null 2>&1 || bad "setup script (node / ffmpeg / Playwright / python libs)"
[ -f "$KITTOOLS/.node/env.sh" ] && . "$KITTOOLS/.node/env.sh"
command -v node >/dev/null && ok "node $(node -v)" || bad "node 18+"
command -v ffmpeg >/dev/null && ok "ffmpeg" || bad "ffmpeg"
python3 -c "import numpy, scipy, PIL" 2>/dev/null && ok "python numpy/scipy/pillow" || bad "python numpy/scipy/pillow"
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user)
  [ "$code" = 200 ] && ok "ElevenLabs key works" || bad "ElevenLabs key answered $code"
else echo "warn  no ELEVENLABS_API_KEY on this machine (the voiceover needs it)"; fi
[ -f "$STYLE/STYLE.md" ] && ok "style pack: $(head -1 "$STYLE/STYLE.md")" || bad "no STYLE.md in $STYLE"
n=$(ls "$STYLE"/reference/* 2>/dev/null | wc -l); [ "$n" -gt 0 ] && ok "$n reference stills (LOOK at them: $STYLE/reference/)" || bad "no reference stills"

python3 "$KITTOOLS/tools/explainer_measure.py" "$ZIP" --preview "$OUT/measured" > "$OUT/measure.txt" 2>&1 \
  && ok "measured every screenshot ($(grep -c ': ring\|: spotlight' "$OUT/measure.txt") found; look at $OUT/measured/)" \
  || { bad "measure: $(grep 'NOT FOUND' "$OUT/measure.txt" | head -3 | tr '\n' ' ')"; }

if [ -f "$STYLE/example/index.html" ] && grep -q "STORYBOARD" "$STYLE/example/index.html"; then
  W="$OUT/page"; mkdir -p "$W"; cp "$STYLE/example/index.html" "$W/"; ln -sfn "$ZIP" "$W/kit"
  python3 "$KITTOOLS/tools/explainer_data.py" "$ZIP" --placeholder "$W/data.js" >/dev/null && ok "data.js (stand-in voice timing)"
  if node "$KITTOOLS/tools/explainer_qa.mjs" "$W/index.html" --out "$OUT/qa" > "$OUT/qa.txt" 2>&1; then ok "$(grep -o "QA PASSED ([0-9]* checks)" "$OUT/qa.txt")"
  else bad "QA: $(grep FAIL "$OUT/qa.txt" | head -3 | tr '\n' ' ')"; fi
  echo "      contact sheet: $OUT/qa/contact.png (an agent must be able to LOOK at this image)"
else echo "warn  this style's example isn't a screenshot walkthrough: QA runs on the page you build"; fi

[ "$FAILED" = 0 ] && echo "SELF-TEST PASSED" || echo "SELF-TEST FAILED"
exit "$FAILED"
