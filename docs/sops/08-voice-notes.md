# SOP 08 — Voice notes → content
Andrew records a voice dump (phone, any length), drops it in Drive `_ENGINE/01-inbox/voice/`, and sets "Anyone with the link" (until a service account exists; files over 10 MB can't come through the Drive connector).

1. Download + transcribe: `python3 tools/transcribe.py note.m4a work/vn/<date>/`.
2. Split into ideas: read the transcript, list each distinct idea (usually 5–10) with its strongest real sentence (timestamped). Keep his words; don't add claims he didn't make.
3. Pick the top 3 ideas (sharpest opinion, clearest story, most useful for the One Feature audience).
4. For each idea: 1 LinkedIn (novel-style), 2 Threads, 1 X post, carousel copy (`outputs/content-bank/bank.json` shape → `tools/content_bank.py`), and 1 short-video script with 3 opening lines for Andrew to film (goes on the next filming list in `todo/`).
5. Optional audio clip: `tools/audiogram.py` on the best 20–40 s (the voice note itself is the audio).
6. But/Therefore check + brand voice check, manifest, add as a tab on the review page (SOP 04).
