# SOP 12: Long-form intro, outro and montage edits (jobs from Your Content System)

The app's **Long form** page sends these as Claude Code jobs. The job's `input.json` says which video and which options.
Never edit RAW footage: work on the finished edit (V+S master or the clean-audio version) the job names. Never post anything.
Put every output in the brand's Drive (`tools/drive_upload.py`, folder `_ENGINE/02-review/Long form edits/<video name>`), never in git.

## Getting the video
- Read it through the Drive script: `python3 tools/drive_range_proxy.py &` then use `http://127.0.0.1:8765/<driveId>` as the
  source (works for any size, any owner). The public download link (`drive.usercontent.google.com/download?id=…&confirm=t`)
  is faster but Google sometimes refuses it for big files; fall back to the proxy.
- Needs `DRIVE_UPLOAD_URL` / `DRIVE_UPLOAD_SECRET` in the environment (same as uploads).

## kind `longform.analyze`
`python3 tools/longform_layout.py SRC --json layout.json` → report `data: {intro, outro, duration, timeline}` (the JSON as is).
Intro = start until the first switch from full-screen speaker to speaker + screen (V+S / picture in picture), or the first
40 s if it never switches (podcasts). Outro = the last switch back to full screen until the end (includes the end card).

## kind `longform.intro_outro` (options: `parts` intro|outro|both, `introMode` layout|first40, `style`, `captions`, `music`)
1. Run the analyzer (or use `input.layout`). Intro range = 0 → intro.end (or 0 → 40 s for `first40`). Outro = outro.start → end.
2. Edit only those ranges, in the chosen style (brand style palette/fonts from `input.style`, or the editing style key
   V1–V8 from `docs/brand-video/`): tighten pauses and filler (`tools/clip_finder.py` word timings), punch-in zooms on emphasis,
   captions if `captions` is true (same caption look as the montage tool), sound pass with `tools/sound_mix.py`
   (music ducked under voice if a track is given), one clear title line in the intro. Keep the speaker's words; don't add AI people
   (docs/ai-video-rules.md).
3. Assemble: edited intro + untouched middle + edited outro, same size and frame rate as the source. Re-encode once
   (libx264 CRF 18, preset medium, AAC 256k); check the joins by eye at each boundary (±2 s).
4. Upload `<name> - edited intro.mp4` (and the full assembled video `<name> - edited.mp4`) to Drive.
5. Report `data: {output: {driveId, name}, parts: {intro: driveId, outro: driveId}, introSeconds, outroSeconds, notes}`.

## kind `longform.montage` (options: `length` s, `intensity` 1-5, `captions`, `music` Drive id | mixkit id | null, `style`, `reference`, `title`, `prepend`)
1. Transcript: `python3 tools/transcribe.py SRC tx/` (or the episode's existing transcript if the job gives one and it matches the length).
2. `python3 tools/montage_intro.py --video SRC --transcript tx/transcript.json --out montage.mp4 --length L --intensity I
   [--no-captions] [--music music.mp3 | --mixkit N] [--style style.json] --title "TITLE" --avoid 0-<intro end>`
   With `prepend` true also pass `--prepend-to SRC --full full.mp4` (montage + whole video, one file).
   No music given: pick from `vendor/motion-graphics/skills/sound-effects/MUSIC.md` by mood (high energy for intensity ≥ 4).
   `reference` (a video URL): watch it first and match its pacing (adjust intensity/length), say what you matched in the notes.
3. Review `montage.mp4.picks.json`: drop any bite that needs context, is a mid-word cut, or is said by a non-speaker; rerun if needed.
4. Upload `<name> - montage intro.mp4` (+ `<name> - with montage.mp4` when prepended) to Drive.
5. Report `data: {output: {driveId, name}, full: {driveId, name} | null, seconds, bites: [...from picks.json]}`.

## Report
Use the job's report command. `images` are not used for these jobs; files go to Drive and their ids go in `data`.
