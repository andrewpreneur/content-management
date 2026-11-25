# SOP 15: Get a long video ready for YouTube (intro + thumbnail + title) — job `longform.produce` / `longform.opening`

The app sends this to Your Software Agent first (Supercomputers), Claude Code otherwise. One job takes a finished long video
in Drive to: an edited intro, 2-3 thumbnails, 3 titles, a description with chapters, all uploaded/reported. **The person
approves in the app (YouTube Studio → Ready) before anything goes to YouTube. Never upload to YouTube yourself.**
Never edit RAW footage or the source file's audio: everything happens on your copy, in the output. Keep the speaker's
words; no AI people (docs/ai-video-rules.md).

`input.json`: `video {driveId, name}`, `options {intro: montage|opening|none, style, title, montage{…} | opening{…}, notes}`,
`style` (brand style: palette, fonts, pack), `stylePack` (link to `style-<pack>.tar.gz`; saassuite = the Skool explainer look),
`toolkit`, `drive {url, secret}`. Send progress as you go (`&progress=1`, `{text, percent}`): it shows in the app.
**Pre-approved: no estimate or preview checkpoint.** Go straight through and report once.

## 0. Get the video (fast)
```
export DRIVE_UPLOAD_URL=… DRIVE_UPLOAD_SECRET=…          # from input.json drive
python3 tools/drive_fetch.py <driveId> source.mp4          # 24 parallel reads, ~10 MB/s (2 GB in ~3 min)
ffprobe source.mp4                                          # size, fps, duration
```
4K source: make a 1080p work copy for analysis (`ffmpeg -i source.mp4 -vf scale=-2:1080 -c:v libx264 -preset veryfast -crf 20 -c:a copy work.mp4`)
but cut the final from `source.mp4` at its own size and frame rate.

## 1. Transcript and layout
`python3 tools/transcribe.py work.mp4 tx/` (word timings). `python3 tools/longform_layout.py work.mp4 --json layout.json`
(where the full-screen opening switches to speaker + screen).

## 2a. intro = `montage` (podcast style, e.g. a coaching call)
**A montage is NOT an edit of the video's beginning.** It is a cold open of the best 6-10 hooks found anywhere in the
WHOLE video (spread across the runtime, at most one from the first 5 minutes), cut tight with music and sound, then a
transition, then the ORIGINAL video from 0:00, untouched. Final = [montage] + [transition] + [full original].
- Pick moments that are **hooky, dramatic and positive**: a bold claim, a result with a number, an "aha", a laugh, a
  question that makes you want the answer. No moment that needs context, no complaints about a client, no mid-word cuts.
  Mix speakers if it's a call (the guest's wins are great hooks).
- `python3 tools/montage_intro.py --video source.mp4 --transcript tx/transcript.json --out montage.mp4 --length <L> --intensity <I>
  [--no-captions] --mixkit <track> --style style.json --title "<title>" --avoid 0-<intro end> --prepend-to source.mp4 --full full.mp4`
  - `feel` podcast → intensity 3, dramatic → 4, upbeat → 4. Length default 45 s.
  - Music: options.music, else a dramatic/cinematic bed (Mixkit cinematic or epic tag pages; fallback #140 Cyberpunk City,
    #723 Other World). Check the licence line in MUSIC.md. Bed ducked well under the voice.
  - Sound: a soft whoosh/impact on cuts (the tool does it), a **riser into the title card and a whoosh + quick white dip
    (or zoom-blur) into the first frame of the video** — the transition must land on the video's first word, not mid-sentence.
- Open `montage.mp4.picks.json`, drop weak or context-needing bites, rerun. Watch the montage end to end once.

## 2b. intro = `opening` (the video's own start, edited with motion graphics — the Skool look)
The first part of the video (until the layout switch in layout.json, or `opening.seconds`, ending on a full sentence;
usually 30-60 s) becomes a tight, designed opening; the rest of the video is untouched.
1. Base edit: `python3 tools/intro_edit.py --video source.mp4 --transcript tx/transcript.json --start S --end E [--crop …|--tiles …]
   --title "<title>" --sub "<one line>" --style style/tokens.json --height <source height> --out base.mp4`
   (cuts fillers and long pauses, punch-ins per sentence, captions in the pack's look). Captions: white pill, active word in the accent.
2. Motion graphics: unpack `stylePack` (`curl -sSL "$URL" | tar xz` → `style/`: STYLE.md, lib.js, example/, fonts/). Read
   STYLE.md and look at reference/ first. Pick `opening.graphics` beats (default 5) where the speaker says something concrete:
   a number, a step, a tool, a promise, the "you'll learn" list. For each beat build one scene in the pack (copy a scene type
   from example/scenes2.js: stat card, checklist, floating UI card, logo row, title) 2.5-4 s long, timed to the words.
   - Layout: **half screen** (speaker kept on one side at ≥50% of the frame, the card on the other) or a full-frame cutaway
     ≤3 s while the voice carries on. Never cover the face; never more than one busy moment.
   - Render the scenes with `node tools/explainer_render.mjs page.html graphics.mp4 30 2 3` (`bash tools/explainer_setup.sh`
     once) at the SOURCE height (4K: render 2160 so text is sharp), then composite onto base.mp4 with ffmpeg (overlay at the beat times).
   - Sound: soft whoosh into each graphic, a UI click on card events, a quiet cinematic bed (~90 bpm) under the opening only,
     fading out where the untouched video starts. -14 LUFS on the output.
3. Join: opening + source from E to the end, same size/fps, one re-encode (libx264 CRF 18, AAC 256k). Check the join ±2 s by ear.

## 2c. intro = `none`
Skip to 3; `full` = the source video.

## LOOK before you upload (both intro types)
`ffmpeg -i intro.mp4 -vf fps=1/3,scale=480:-2,tile=4x3 -frames:v 1 sheet.jpg` and actually look at it: faces in frame, no black
bands, captions one line and in reading order, graphics on-brand (pack colours, accent used once per frame), text readable on a
phone. Fix and re-render before uploading. Say in `notes` what you checked.

## 3. Thumbnails (2-3 options)
1280×720 JPG, ≤1.5 MB each. Built as HTML at 1280×720 and screenshotted (Playwright):
- The speaker's most expressive frame from the video (face big, on one third), cut-out or on a clean background in the pack's palette.
- 2-5 words of text that ADD to the title (never repeat it), Inter Display 800, huge; one accent colour.
- Readable at 160 px wide (check by shrinking it). Vary the options (different frame / words / layout), don't make 3 copies.
Send them in the report's `images` (`{base64, note}`); the app saves them and offers them on the approval card.

## 4. Titles, description, tags
- 3 titles ≤ 60 characters: clear payoff + curiosity, true to the video, no ALL CAPS, no emoji spam. They pair with the thumbnails.
- Description: 2-line hook, 3-5 "in this video" bullets, **chapters** from the transcript (first one `00:00`, include the intro),
  then the brand's links if input.style or notes has them. 10-15 tags.

## 5. Upload and report
`python3 tools/drive_upload.py put "_ENGINE/02-review/Ready for YouTube/<video name>" full.mp4 intro.mp4`
Names: `<name> - ready for YouTube.mp4` (full) and `<name> - intro.mp4`. Then report:
`data {full {driveId, name}, output {driveId, name} (the intro alone), introType, seconds (intro length), titles [3], description,
tags, thumbnails [what each shows], notes}` + `images`.

## Kind `longform.opening` (opening only, no thumbnails/titles)
Steps 0, 1, 2b, look, upload; report `data {output, full, seconds, beats [{t, text, graphic}], notes}`.

## Kind `youtube.push` (after the person approves)
The app opened the YouTube upload; you only move bytes: `python3 tools/drive_fetch.py <driveId> video.mp4` (or reuse the file
if you still have it) then `python3 tools/yt_push.py --session "<upload.session>" --file video.mp4` → report `data {videoId}`.
