# SOP 13: Explainer video from a zip (Your Content System chat → any runner)

A person (or a SaaS platform) attaches a zip with **screenshots and a script** and asks for an explainer. You make one
self-contained page that renders any frame from a time value, check it, render it (on Supercomputers when you are Your
Software Agent, else on this machine), put the MP4 in the customer's Google Drive and report back.

Everything you need is in `input.json` (download it first, see "Report back" in the job): `request`, `options`
(format, seconds, style, music), `files` (24 h links), `brand` (name, styles), `conversation` (earlier messages if this is
a follow-up), `skills` (the workspace's own rules: they win), `drive` (url + secret for uploads), `toolkit` (this kit).

Post a progress line at each step (see the job text: `&progress=1`). Keep them short: "Reading the zip", "Writing the
script", "Building scene 3 of 6", "Checking stills", "Rendering on 6 Supercomputers", "Uploading to Drive".

## 1. Read the zip

```bash
mkdir -p ~/job/src && cd ~/job
python3 - <<'PY'
import json, urllib.request, os
I = json.load(open(os.path.expanduser('~/input.json')) if os.path.exists(os.path.expanduser('~/input.json')) else open('input.json'))
for f in I['files']:
    urllib.request.urlretrieve(f['url'], 'src/' + f['name'])
PY
for z in src/*.zip; do unzip -oq "$z" -d src/unzipped; done
find src -type f | head -100
```

Sort what you find: **script** (txt / md / json / docx / srt), **screenshots** (png / jpg / webp: product screens, in
order if named 01, 02…), **brand** (logo, colours, fonts, if any). If there's a manifest (json), follow it.
No script? Write one from the screenshots and the request: one short line per screen, the product's own words.

## 2. Plan

- Read the chosen skill fully: `skills/<style>/SKILL.md` (`explainer-default`, `explainer-engaging` or
  `explainer-high-energy`, from `options.style`). Its rules (pacing, camera, restraint, never invent facts) apply.
- Length = `options.seconds` (±10 %). Format = `options.format` (16:9 = 1920×1080, 9:16 = 1080×1920).
- Beat sheet first: every line of on-screen text, which screenshot / UI moment follows, its time. Use the script's
  wording. No made-up numbers, customers, ratings or claims.
- Brand: colours / fonts / logo from the zip, else `input.brand.styles`, else the skill's default palette.

## 3. Build page.html (one file, self-contained)

- Follow the skill's page contract: `window.VIDEO = {w, h, duration}`, `window.seek(t)` as a pure function of time,
  `?render` mode, optional `window.buildAudio(ctx)` for the soundtrack (synthesised, if `options.music`).
- **Screenshots:** rebuild the key UI moments cleanly where the skill asks for it; where the real screen matters, show
  the screenshot itself in a clean browser/device frame and let the camera push in on the part that matters (crop,
  zoom, highlight, cursor). Never show tiny full screens nobody can read.
- **Embed everything** as base64 (images, fonts, logo) so the single file renders on any machine. Keep it under 50 MB
  (compress screenshots to JPEG q85, max 2400 px wide).

## 4. Check

```bash
bash ~/kit/tools/explainer_setup.sh
node ~/kit/tools/explainer_render.mjs page.html check.png --stills 0.5,3,8,15,25,40,55   # one time per beat
```
Look at check.png. Fix anything clipped, overlapping, unreadable, off-brand or empty. Check again.
Optional quick draft: `node ~/kit/tools/explainer_render.mjs page.html draft.mp4 30 1`.

## 5. Render

### On Supercomputers (you are Your Software Agent)

1. Upload the page so every machine can download it:
   `curl -sS -X POST '<report url>&file=page.html' -H 'x-ycs-run-key: <key>' --data-binary @page.html` → `{"url": …}`
2. Run your **supercomputer_job** tool, kind `script`, size `power` (CPU; Chromium doesn't use the GPU here):
   - machines: `min(8, max(2, ceil(seconds / 10)))`
   - inputs: `[{"name": "page.html", "url": <page url>}, {"name": "toolkit.tar.gz", "url": <input.json toolkit>}]`
   - script (each machine renders its slice):
     ```bash
     set -e
     mkdir -p /work/kit && tar xzf "$IN_DIR/toolkit.tar.gz" -C /work/kit
     bash /work/kit/tools/explainer_setup.sh
     node /work/kit/tools/explainer_render.mjs "$IN_DIR/page.html" "$OUT_DIR/part_${MACHINE_INDEX}.mp4" 60 4 "$(nproc)" --slice "${MACHINE_INDEX}/${MACHINE_COUNT}"
     ```
   - join (one machine, with the parts):
     ```bash
     set -e
     mkdir -p /work/kit && tar xzf "$IN_DIR/toolkit.tar.gz" -C /work/kit
     bash /work/kit/tools/explainer_setup.sh
     node /work/kit/tools/explainer_render.mjs "$IN_DIR/page.html" "$OUT_DIR/explainer.mp4" --join "$IN_DIR,$OUT_DIR,/work"
     ```
3. Follow it with supercomputer_status; post its progress as progress lines. Download `explainer.mp4` from the result.

### On this machine (Claude Code in the cloud or on the person's computer)

`node ~/kit/tools/explainer_render.mjs page.html explainer.mp4 30 2` (uses every CPU core). For a 60 s video expect
several minutes in the cloud; say so in a progress line.

## 6. Deliver

```bash
export DRIVE_UPLOAD_URL="$(python3 -c 'import json;print(json.load(open("input.json"))["drive"]["url"])')"
export DRIVE_UPLOAD_SECRET="$(python3 -c 'import json;print(json.load(open("input.json"))["drive"]["secret"])')"
python3 ~/kit/tools/drive_upload.py put "Explainers" explainer.mp4     # prints the Drive link; the id is after /d/
```
Optionally also upload page.html (file=…) and put its link in `data.html.url` so the person can scrub it live.

Report (once): `status`, a two-sentence `summary` (what it shows, how long, where it rendered), and
`data: {output: {driveId, name}, seconds, format, html: {url}, usage: {runner, machines, minutes}}`.
If something blocks you (no script and no screenshots, an unreadable zip), report `failed` with what's missing in plain words.
