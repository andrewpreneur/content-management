# SOP 14: Save every video as an editable project (Your Content System → Video editor)

Every video we make keeps its layers, so later changes (a voice line, the music, a sound effect, captions) are a quick
remix (tools/remix.py, ~20 s) instead of a new render. The app's editor reads a **manifest** plus the files it names.

## When you finish any explainer / motion video
1. Render the picture once more **without captions and without sound**: hide the page's caption element (our pages: add
   `?nocap` to the page URL; otherwise set the caption element's `visibility:hidden`). This is `silent.mp4`.
2. Keep every layer as its own file:
   - each voice line: `line-00.mp3`, `line-01.mp3`, … (the ElevenLabs files, untrimmed)
   - music: the file (`music.mp3`) or its https link (Mixkit links are fine)
   - each sound effect file you used (`whoosh.ogg`, `click.ogg`, …)
   - the page: `page.html` plus what it loads next to it (scripts, logos, fonts). Put fonts in the same folder (no sub-folders: change `url(fonts/x.ttf)` to `url(x.ttf)`).
3. Write `manifest.json` (format below). Word timings come from ElevenLabs `/with-timestamps` (seconds from the start of the line).
4. Hand it over:
   - **Job from the app (YSA / Claude Code):** upload every file with `&file=<name>` (≤50 MB each) and put the manifest in your
     final report as `data.project`. The app turns it into a project automatically.
   - **From the engine repo:** `python3 tools/project_push.py <folder>` (folder = manifest.json + files).
5. Check: `python3 tools/remix.py manifest.json check.mp4` must make the same video you delivered (voice, music, captions).

## Manifest (content-hq `backend/supabase/functions/_shared/projectpure.ts` is the source of truth)
```json
{ "v": 1, "title": "LumeClick - Starter explainer", "duration": 54.3, "fps": 30, "width": 1920, "height": 1080,
  "video": "silent.mp4", "page": "page.html",
  "scenes": [{ "id": "hook", "label": "Missed calls", "t0": 0.25, "t1": 3.4 }],
  "voice": { "id": "<elevenlabs voice id>", "name": "Adam", "model": "eleven_multilingual_v2", "stability": 0.5, "style": 0.1 },
  "lines": [{ "id": "l00", "text": "Every missed call is a job going to your competitor.", "t": 0.6, "dur": 2.65, "file": "line-00.mp3",
              "words": [{ "w": "Every", "s": 0.0, "e": 0.28 }] }],
  "music": { "src": "https://assets.mixkit.co/music/634/634.mp3", "title": "Your Breath (Mixkit #634)", "volume": 0.12, "fadeIn": 1, "fadeOut": 2.2 },
  "sfx": [{ "id": "s1", "kind": "whoosh", "file": "whoosh.ogg", "t": 3.28, "volume": 0.2 }],
  "captions": { "on": true, "color": "#4b5563", "active": "#175892", "size": 30, "bottom": 62, "font": "Inter Display", "weight": 500, "maxWords": 6 },
  "mix": { "lufs": -16, "duckDb": 10 },
  "pronounce": [{ "word": "LumeClick", "say": "Loom Click" }] }
```
- `t` = when the line starts in the video; `words[].s/e` are relative to the line. Caption text = the words (write brand names
  the way they're spelled; `pronounce` makes the voice say them right when a line is re-recorded).
- `scenes` = the page's scenes (STORYBOARD steps) with readable labels: they're the scene lane in the editor and where change notes point.
- `size` / `bottom` are in frame pixels at 1080p.

## Jobs the editor sends
- `video.remix` (Export): `python3 tools/remix.py input.json out.mp4` (input.json = {manifest, urls}), upload to Drive, report `data.output`.
- `video.revise` (scene change note): edit `page.html` for that scene only, re-render `silent.mp4` without captions, upload both
  with `&file=`, report `data.project` = the manifest with the new files. The app saves it as a new version.
