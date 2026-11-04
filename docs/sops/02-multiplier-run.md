# SOP 02 — Multiplier run: 1 source → 20+ outputs
Read `docs/brand.md` (voice + **But/Therefore rule**) and `docs/ai-video-rules.md` first. Example run: `outputs/2026-11-04-funnelstore/`.

| Step | Output | Command / how | Time |
|---|---|---|---|
| 1 | Strongest moments | Read `transcript.txt`; pick 5–7 beats: hook line, what changed, how, result, "it's simple". Each beat must join the next with *but* or *therefore*. Write `work/edl/master.json` (see `tools/reel.py` docstring): `a` = spoken range, `v` = optional b-roll start, `cx` = crop centre. | 15 min |
| 2 | Master reel | `python3 tools/reel.py edl/master.json master.mp4 --srt master.srt` | 2 min |
| 3 | 3 re-edits | Copy the EDL, **open on a different real spoken line** + new hook text. `reedit1..3.json`. (When Higgsfield works: an AI-generated open per AI rule 1 instead.) | 10 min |
| 4 | 6 Trial Reels | `python3 tools/reel.py edl/master.json clean.mp4 --clean --srt clean.srt` then `python3 tools/variants.py clean.mp4 trial/ --hook "A" --hook "B" --srt clean.srt --alt-open reedit2.mp4 --no-mirror` (screen footage → no mirror). IG Trial Reels only. | 5 min |
| 5 | Podcast clip + audiogram | `ffmpeg … highpass,afftdn,acompressor,loudnorm=I=-16` → mp3; `showwaves` audiogram (see run log). Extended segment = script in `text/podcast-extended-segment.md`; voice with ElevenLabs only when Andrew's clone is confirmed. | 5 min |
| 6 | Text pack | Write from the transcript using prompts in `tools/prompts/text-pack.md`: 3 LinkedIn, 3 Threads, 1 X thread, long email, Substack essay, YouTube outline + titles/thumbnails, reel captions. | 30 min |
| 7 | Carousel | Grab 4K frames (`ffmpeg -ss T -i src -frames:v 1 s_T.png`), write `carousel/spec.json`, `python3 tools/carousel.py spec.json carousel/ --pdf` | 15 min |
| 8 | Story sequence | `stories/spec.json` per `docs/stories.md` + SOP 03, `python3 tools/story.py spec.json stories/` | 15 min |
| 9 | Spanish | Translate each transcript line → `es.json` (key = line start time), EDL with Spanish hook/title/cta/series → `reel.py … --translations es.json`. Dub only via ElevenLabs once connected. | 15 min |
| 10 | Manifest | Every file = one row shaped like `supabase/schema.sql` `outputs` (status `draft`). `python3 tools/manifest.py <run dir>` | 2 min |
| 11 | Review | Upload ≤15 MB files to Drive `_ENGINE/02-review/<run>/`; publish/refresh the review page. → SOP 04 | 10 min |

**Quality gate before review (self-check):** watch the master once start to end; every caption readable over the footage; no "and then" between beats; brand spelling "HighLevel", "SaaSSuite"; no invented client stories or prices (use `[Andrew: …]` placeholders); CTA keyword consistent across all outputs.
