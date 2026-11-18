# tools/export_app.py: data for the app "Your Content System"

Builds the JSON the app (repo `content-hq`, Supabase) ingests to replace the old Claude review pages.
Each file is a JSON array of objects; empty / null fields are left out.

```
python3 tools/export_app_audio.py              # only when new clips were rendered (see "Audio clips")
python3 tools/export_app.py outputs/app-export # rebuild the JSON (no network, a few seconds)
```

## Files (outputs/app-export/)
| File | One row per | Fields |
|---|---|---|
| `runs.json` | dated run folder in `outputs/` (skips planner, content-hq, drive-copy, style-quiz, clip-bank, content-bank, carousel-formats, app-export) | runId, title, date, kind (podcast, carousel, ads, vsl, banner, training, catalog, other), source, summary, outputs (count), reviewArtifact (first claude.ai/artifact link in the run's files, else the `review` link of its queue items) |
| `runOutputs.json` | output of a run | runId, key, type, title, status, itemId (queue id in `outputs/planner/plan.json`), media [{driveId, name, mimeType}], text (≤ 4000 chars) |
| `clips.json` | podcast clip in `outputs/clip-bank/pod1-3.json` | clipId, episode, title, speaker, guest, startS, durationS, hook, quote, status, topic, formats (vN with a Drive file), video (v1, else first), audio |
| `podcastEpisodes.json` | pod1, pod2, pod3 + Get Real ep. 3 (`2026-11-04-podcast-ep3`, a different show) | episodeId, title, guest, guestOrg, guestTitle, month, durationS, video, audio, audioRaw, clips, summary |
| `unmatched.json` | output or link with no Drive file | runId, key, file |

## Where each run's outputs come from
- `manifest.json` / `manifest_spec.json` (Nov 4 runs, levelup-reels): merged by key. Text outputs read the `.md` file.
- `2026-11-07-catalog`: `manifest.csv` (840 rows). Text comes from `text/*.md` sections (`### <source>[-n]`).
- `meta-ads`: `manifest.csv` + `videos.csv` (and `round2/`). `testimonials-a`: `manifest.csv` (one row per ad, 9:16 + 4:5 files).
  `testimonials-b`: `specs/manifest.json`. `vsl-a`: `manifest.json`. `vsl-b`: `manifest.jsonl`. `levelup-posts`: its 4 queue items.
- All other runs: media files named in the run's READMEs, plus media files saved in the run folder. When a README links
  Drive files, only the linked files count (the other names there are sources).

## Drive matching (never guessed)
In order: the queue item's files in `posting/media.json`, then the exact local path in `posting/drive_uploads.json`,
then a Drive link written in the README, then an exact file name that only one Drive file has
(`posting/drive_inventory.json` + uploads). When two Drive files share a name, the one in a folder the same run already
uses is taken if exactly one is; otherwise the output stays without media and is listed in `unmatched.json`.
Refresh the inventory first if Drive changed (see `posting/media-README.md`, "Re-run").

Clip formats: media.json (what the queue posts) first, then `/home/user/work/formats/<clip>/<clip>-vN.mp4` uploads,
then a unique Drive name (this is how the V8 re-renders are found).

## Podcast episodes
- `video`: edited master in Drive OCTOBER 2026 → VIDEO V+S (`1JVEoN5wvfCp81mX_wnKjw5Ck0sUjGn9q`), ids fixed in the script (checked Nov 17).
- `audio`: ElevenLabs voice-isolated MP3 of the full raw recording; `audioRaw`: the raw recording.
  Both come from `outputs/2026-11-10-podcast-voice-isolated/README.md`. They are the unedited full-length tracks, so they
  are longer than the edited master and not in sync with it.
- `durationS`: end of the last spoken line in the edited master's transcript (`/home/user/work/<pod>/tx/transcript.json`).
- `date` is unknown (recorded October 2026), so `month` is given instead.

## Audio clips (`tools/export_app_audio.py`)
For every clip with a local render (`<clip>-v1.mp4`, else the lowest vN) it copies the audio stream to `<clip>-audio.m4a`
(AAC is copied as is; anything else gets a plain AAC 128k encode; no filters, normalising or denoising), uploads it to
`_ENGINE / 02-review / podcast-audio-clips`, records the id in `posting/audio_clips.json` and deletes the local `.m4a`.
Already recorded clips are skipped. The renders carry the format's music bed and sound pass, so the clip audio is the mixed
reel audio, not the bare voice.
