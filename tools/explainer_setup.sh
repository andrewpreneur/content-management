#!/usr/bin/env bash
# One-time setup for tools/explainer_render.mjs on a fresh machine (Supercomputer, cloud session or your computer).
# Needs: node 18+, ffmpeg. Installs Playwright + Chromium next to the kit (no global changes beyond the browser).
set -e
KIT="$(cd "$(dirname "$0")/.." && pwd)"
command -v ffmpeg >/dev/null || { (sudo -n apt-get install -y ffmpeg || apt-get install -y ffmpeg) >/dev/null 2>&1 || { echo "ffmpeg is missing"; exit 1; }; }
cd "$KIT"
# Node 18+: use the machine's, else a portable copy inside the kit (bare Supercomputers have none). No root needed.
NODE_OK() { command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ]; }
if ! NODE_OK; then
  ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=x64;; aarch64|arm64) ARCH=arm64;; esac
  V=v20.18.1; D="$KIT/.node/node-$V-linux-$ARCH"
  if [ ! -x "$D/bin/node" ]; then
    mkdir -p "$KIT/.node"
    (curl -fsSL "https://nodejs.org/dist/$V/node-$V-linux-$ARCH.tar.xz" || wget -qO- "https://nodejs.org/dist/$V/node-$V-linux-$ARCH.tar.xz") | tar -xJ -C "$KIT/.node" \
      || { echo "node 18+ is missing and couldn't be downloaded"; exit 1; }
  fi
  export PATH="$D/bin:$PATH"
  echo "export PATH=\"$D/bin:\$PATH\"" > "$KIT/.node/env.sh"   # later steps: source .node/env.sh
fi
if ! node -e "require.resolve('playwright')" >/dev/null 2>&1; then
  [ -f package.json ] || echo '{"name":"ycs-kit","private":true,"type":"module"}' > package.json
  npm i --silent --no-audit --no-fund playwright@1 >/dev/null
fi
# use a Chromium that's already there (e.g. /opt/pw-browsers), else download one
node -e "const {chromium}=require('playwright');chromium.launch().then(b=>b.close()).catch(()=>process.exit(1))" 2>/dev/null \
  || npx playwright install --with-deps chromium >/dev/null 2>&1 || npx playwright install chromium >/dev/null
echo "explainer kit ready ($(node -v), $(ffmpeg -version | head -1 | cut -d' ' -f1-3))"
