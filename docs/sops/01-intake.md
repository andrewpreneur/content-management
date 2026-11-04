# SOP 01 — Intake: footage → inbox → manifest
**Owner:** engine (Claude). **Andrew's part:** upload only.

1. **Andrew** films from `todo/` and uploads to Drive `_ENGINE/01-inbox` (`1B2A_2_3B6Rm060keaIrswnJl1TgtmK5j`). Name: `YYYY-MM-DD-<topic>.mp4`. For each clip, say 2–3 different opening lines (the re-edits use them).
2. **Make it downloadable** (until we have a service account): in Drive, right-click the file → Share → General access → "Anyone with the link" → Viewer. Only on the inbox copy, never on originals.
3. **Engine downloads** a copy (never moves or edits the original):
   `curl -sL -o src.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`
4. **Probe + proxy:** `ffprobe` for length/resolution. For 4K screen recordings make a 1080p proxy (`ffmpeg -i src.mp4 -vf scale=1920:1080 -crf 15 proxy.mp4`) — renders get ~3× faster with no visible loss at 9:16.
5. **Transcribe:** `python3 tools/transcribe.py src.mp4 work/<source>/` → `transcript.json` (word timings), `.txt`, `.srt`.
6. **Create the run folder:** `outputs/YYYY-MM-DD-<source>/` with `manifest.json` (`source` block: Drive id, duration, transcript path). Videos stay out of git (`.gitignore`); they go to Drive `02-review`.
7. **Log** in `logs/YYYY-MM-DD.md`: source received, length, anything odd (no face cam, bad audio).

**Checks:** audio is clean (no clipping, music under voice), and the clip has at least one clear "result" moment on screen.
