# SOP 13: Explainer video from a zip (Your Content System chat → any runner)

A person (or a SaaS platform) attaches a zip with **screenshots and a script** and asks for an explainer. You make one
self-contained page that renders any frame from a time value, check it, render it (on Supercomputers when you are Your
Software Agent, else on this machine), put the MP4 in the customer's Google Drive and report back.

Everything you need is in `input.json` (download it first, see "Report back" in the job): `request`, `options`
(format, seconds, style, music), `files` (24 h links), `brand` (name, styles), `conversation` (earlier messages if this is
a follow-up), `skills` (the workspace's own rules: they win), `drive` (url + secret for uploads), `toolkit` (this kit).

Post a progress line at each step (see the job text: `&progress=1`). Keep them short: "Reading the zip", "Writing the
script", "Building scene 3 of 6", "Checking stills", "Rendering on 6 Supercomputers", "Uploading to Drive".

## 0. Self-test (once per machine / new setup, ~1 min, no cost)

`bash ~/kit/tools/explainer_selftest.sh src/unzipped ~/job/style` checks node, ffmpeg, python libs, the ElevenLabs key,
measures the screenshots and runs the QA on the style's example. It must print SELF-TEST PASSED, and you must be able to
open `selftest/qa/contact.png` as an image. If you can't look at images, say so in your first progress line.

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

**The zip's own instructions win.** If it has a `SKILL.md` (or `brand/design-system.md`, `brand/colors.json`, fonts, a logo,
`script.md`, `screenshots/manifest.json`), that is the customer's house style: follow it exactly (structure, colours, fonts, captions,
safe areas, words to avoid). The style pack (step 2) supplies motion, captions and the example; never let it override their look.
If it asks for two cuts (desktop + mobile), make the one the person asked for first (default: desktop 16:9); mention the other.

Sort what you find: **script** (txt / md / json / docx / srt), **screenshots** (png / jpg / webp: product screens, in
order if named 01, 02…), **brand** (logo, colours, fonts, if any). If there's a manifest (json), follow it.
No script? Write one from the screenshots and the request: one short line per screen, the product's own words.

## 2. Open the style pack (required)

Every job carries exactly one style pack: `input.style` = `{id, name, url}` (a `style-<id>.tar.gz`). No pack = stop and
report `failed` with "Pick a style for this video (or Make a new style)"; never invent a look.

```bash
mkdir -p ~/job/style && curl -sSL "$(python3 -c 'import json;print(json.load(open("input.json"))["style"]["url"])')" | tar xz -C ~/job
```
Read `style/STYLE.md`, open every image in `style/reference/` **and look at it**, and read `style/example/` (the source of
an approved video). Build by copying the example's patterns (layout, motion helpers, captions, timing): don't start from
a blank page. If the zip has its own `brand/design-system.md`, its colours/fonts/layout win over the pack's; the pack
still gives motion, captions and the example. `styles/README.md` (in this kit) explains packs.

## 3. Measure, then storyboard (before any code)

**Measure every screenshot** (no guessing positions):
```bash
python3 ~/kit/tools/explainer_measure.py src/unzipped --preview measured/      # → src/unzipped/targets.json
```
It finds the highlight already drawn on each screenshot (ring, numbered badge, arrow) and writes the element's exact box
(`target`) and click point (`click`) in screenshot pixels. Look at `measured/*.png`: the magenta box must sit exactly on
the element the script names. A step marked NOT FOUND: measure it yourself (open the image, read the pixel box) and write it
into the storyboard by hand. Screenshots that already show a highlight: **don't draw a second box**; zoom toward it and click it.

**Storyboard** = `window.STORYBOARD` in the page (the checker reads it):
`{ safe: {top,right,bottom,left}, steps: [{ id, title, t0, t1, click, target }] }`, one step per script step, `target`
copied from targets.json, times built from the voiceover lengths (each line's clip length, measured). One target per
step: the cursor, the zoom and any box all point at the same element.

### Every explainer has (unless the kit or pack says otherwise)
- **A short intro** (≈3 s): logo + feature name + one-line promise. **An outro** with where to find it.
- **A voiceover**: one calm voice, **ElevenLabs** (eleven_multilingual_v2 or newer) with word timestamps
  (`/v1/text-to-speech/<voice>/with-timestamps`), one clip per line; captions come from the word timings, burned in.
- **A cursor on the screenshots**: zoom toward the target, the cursor glides to the click point (its position computed from the
  same camera every frame), presses, accent ripple, holds ≥ 3 s after the click.
- **Light music** ≈ −24 LUFS under the voice, fading out under the outro; final mix −16 LUFS.
- Nothing that must be read outside the safe area; nothing drawn over the app except the cursor and ripple.

## 4. Build page.html, then the required check

- Page contract: `window.VIDEO = {w, h, fps, duration}`, `window.seek(t)` (pure function of time), `?render` mode.
- QA hooks: `data-qa="shot-<id>"` on each step's screenshot `<img>`, `data-qa="cursor"` (+ `data-hot="x,y"` = the tip inside it),
  `data-qa="caption"` on the caption box, `data-qa="read"` on titles / pills / logos, optional `data-qa="box-<id>"` on a drawn box.
- Copy `style/example/index.html` when the pack has a walkthrough example (medspa-emr-training does): it already meets
  every rule below.
- Embed or ship everything the page loads (images, fonts, logo) next to it; keep it under 50 MB.

**The check (must pass before any estimate, test or render):**
```bash
bash ~/kit/tools/explainer_setup.sh && { . ~/kit/.node/env.sh 2>/dev/null || true; }
node ~/kit/tools/explainer_qa.mjs page.html --out qa      # exit 0 = pass
```
Rules: the cursor is inside the target at every click; any drawn box is within 6 px of target ± 8 px; captions and every
`data-qa="read"` stay inside the safe area; captions ≤ 2 lines; fonts loaded; each step holds ≥ 3 s after its click; no page
errors. It writes `qa/qa.json` and `qa/contact.png`. **Then look at `qa/contact.png`** next to `style/reference/` (open both
images): same family? anything covered, cramped, off-brand, unreadable? Fix and run the check again until it passes and looks
right. Say "QA passed (N checks)" in a progress line and attach `qa/contact.png` (`&file=contact.png`) to the estimate text.

### A test version first
After the check passes: render only the **first ~10 s** (intro + the first step with its voice and cursor), in the final look, on
ONE machine (it's 300 frames), send it with `&preview=1` (upload with `&file=test.mp4`). Wait for **Approve full project** or
**Needs revision** (apply the notes, re-run the check, send a new test). Design and checking happen once, carefully; only the
approved page goes to many machines.

## 5. Render

### On Supercomputers (you are Your Software Agent)

1. Only the page that passed the check and whose test was approved. Upload it (and its files) so every machine can download it:
   `curl -sS -X POST '<report url>&file=page.html' -H 'x-ycs-run-key: <key>' --data-binary @page.html` → `{"url": …}`
2. Run your **supercomputer_job** tool, kind `script`, size `power` (CPU; Chromium doesn't use the GPU here):
   - machines: `min(8, max(2, ceil(seconds / 10)))`
   - inputs: `[{"name": "page.html", "url": <page url>}, {"name": "toolkit.tar.gz", "url": <input.json toolkit>}]`
   - script (each machine renders its slice):
     ```bash
     set -e
     mkdir -p /work/kit && tar xzf "$IN_DIR/toolkit.tar.gz" -C /work/kit
     bash /work/kit/tools/explainer_setup.sh && { . /work/kit/.node/env.sh 2>/dev/null || true; }
     node /work/kit/tools/explainer_render.mjs "$IN_DIR/page.html" "$OUT_DIR/part_${MACHINE_INDEX}.mp4" 30 2 "$(nproc)" --slice "${MACHINE_INDEX}/${MACHINE_COUNT}"
     ```
   - join (one machine, with the parts):
     ```bash
     set -e
     mkdir -p /work/kit && tar xzf "$IN_DIR/toolkit.tar.gz" -C /work/kit
     bash /work/kit/tools/explainer_setup.sh && { . /work/kit/.node/env.sh 2>/dev/null || true; }
     node /work/kit/tools/explainer_render.mjs "$IN_DIR/page.html" "$OUT_DIR/explainer.mp4" --join "$IN_DIR,$OUT_DIR,/work"
     ```
3. Follow it with supercomputer_status; post its progress as progress lines. Download `explainer.mp4` from the result.

### On this machine (Claude Code in the cloud or on the person's computer)

`node ~/kit/tools/explainer_render.mjs page.html explainer.mp4 30 2 3` (3 browser pages: big screenshots use a lot of memory). For a 60 s video expect
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
