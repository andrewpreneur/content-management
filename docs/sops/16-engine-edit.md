# SOP 16: Engine edit (a new video in the drop folder → edited short-form set)
Job kind `longform.multiply`. Started by the platform when a new video lands in `_ENGINE` or `_ENGINE/01-inbox`
(Drive watch, every 30 min) or by hand. Same toolkit as SOP 15 (`input.json` → `toolkit`).
Read `docs/edit-style-lock.md` FIRST (the locked look: white + violet captions, no boxes, no yellow), then `docs/brand.md`
(voice, **But/Therefore**) and `docs/ai-video-rules.md`. Never edit the original file.

## 1. Get it
- `python3 tools/drive_fetch.py <driveId> src.<ext>` (export DRIVE_UPLOAD_URL / DRIVE_UPLOAD_SECRET from input.json `drive`).
- `ffprobe` length, size, rotation. iPhone `.MOV` is often HEVC + a rotation flag: transcode once to
  `src.mp4` (`ffmpeg -i src.MOV -c:v libx264 -crf 17 -preset fast -c:a aac -b:a 192k src.mp4`); ffmpeg applies the rotation.
- `python3 tools/transcribe.py src.mp4 work/` → word timings.

## 2. Decide what it is (say it in `data.notes`)
- **Ad / promo** (name has "ad", an offer, a deadline like Black Friday, under ~3 min): the job is an ad set.
- **Talking-head lesson / story**: the SOP 02 multiplier set.

## 3. Ad set (most drops)
1. **Master** 9:16, 20–60 s: strongest hook first (a result, a number, the offer), then problem → **but** → solution →
   **therefore** → offer + one CTA. Cut every dead pause and false start. EDL with `"layout": "full"` on every segment (vertical talking head) → `python3 tools/reel.py edl/master.json master.mp4 --srt master.srt` (house look is the default).
2. **3 hook re-edits**: same body, each opens on a different real spoken line + its own on-screen hook text.
3. **Trial variants**: `python3 tools/variants.py clean.mp4 trial/ --hook "A" --hook "B" --srt clean.srt --no-mirror`.
4. **Feed + wide**: a 4:5 (1080×1350) of the master, and a 16:9 if the source is wide.
5. **Copy** (`ad-copy.md`): 3 primary texts, 5 headlines, 3 descriptions, 3 captions, CTA keyword. Prices, dates and offer
   terms only as said in the video; anything missing = `[Andrew: …]`.
Captions + hook/CTA text: the LOCK only (`docs/edit-style-lock.md`): white, spoken word violet, no boxes, never yellow.
Every output must pass `python3 tools/style_check.py <file>` before it's uploaded; put the JSON in `data.styleCheck`.
Sound: voice -16 LUFS, music bed well under the voice, no music if the source already has some.

## 4. Lesson / story
SOP 02 steps 1–4 and 6 (master, 3 re-edits, trial reels, text pack). Skip carousel/stories/Spanish unless asked.

## 5. Check, upload, report
- `python3 tools/style_check.py master.mp4 --baseline clean.mp4 --out check.jpg` for EVERY output (must pass; look at check.jpg against the
  approved reference). Then watch the master end to end. Contact sheet of every output (one frame per 2 s): no black frames, captions inside the
  safe zone, faces not cut.
- Upload each file to `_ENGINE/02-review/<YYYY-MM-DD>-<source name>/` (`tools/drive_upload.py`).
- Progress POST (`&progress=1`) at least every 10 minutes. Report:
  `{"status":"done","summary":"…","data":{"type":"ad|lesson","notes":"…","seconds":<master length>,
  "outputs":[{"driveId":"","name":"","kind":"master|reedit|trial|feed|wide","ratio":"9:16","seconds":0}],
  "copy":"<ad-copy.md text>","minutes":<wall-clock minutes>,"styleCheck":{"pass":true,"why":[]}}}` plus `"images":[{"base64":"<contact sheet JPG>"}]`.
- Nothing is posted. Outputs go to the review queue in the app.
