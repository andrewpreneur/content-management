#!/usr/bin/env bash
# One-time setup for tools/explainer_render.mjs on a fresh machine (Supercomputer, cloud session or your computer).
# Needs: node 18+, ffmpeg. Installs Playwright + Chromium next to the kit (no global changes beyond the browser).
set -e
KIT="$(cd "$(dirname "$0")/.." && pwd)"
command -v ffmpeg >/dev/null || { (sudo -n apt-get install -y ffmpeg || apt-get install -y ffmpeg) >/dev/null 2>&1 || { echo "ffmpeg is missing"; exit 1; }; }
command -v node >/dev/null || { echo "node 18+ is missing"; exit 1; }
cd "$KIT"
if ! node -e "require.resolve('playwright')" >/dev/null 2>&1; then
  [ -f package.json ] || echo '{"name":"ycs-kit","private":true,"type":"module"}' > package.json
  npm i --silent --no-audit --no-fund playwright@1 >/dev/null
fi
# use a Chromium that's already there (e.g. /opt/pw-browsers), else download one
node -e "const {chromium}=require('playwright');chromium.launch().then(b=>b.close()).catch(()=>process.exit(1))" 2>/dev/null \
  || npx playwright install --with-deps chromium >/dev/null 2>&1 || npx playwright install chromium >/dev/null
echo "explainer kit ready ($(node -v), $(ffmpeg -version | head -1 | cut -d' ' -f1-3))"
