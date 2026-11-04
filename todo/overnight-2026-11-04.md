# Overnight run — Nov 4, 2026 (CT) → morning show-and-tell

Read `CLAUDE.md`, `docs/STATUS.md`, `docs/brand.md`, `docs/multiplier.md`, `docs/ai-video-rules.md` first.
Andrew is asleep. Don't ask him anything; log blockers for the morning. He checks in tomorrow morning.

## Goal for the morning
Show Andrew **one existing piece of content turned into 20+ outputs**, all drafts (nothing posts live), in one place he can review on his phone:
a published Artifact page ("One → Twenty") with every output playable or readable, plus the files in Drive `_ENGINE/02-review`.
Also build the SOPs + scripts so the next run is push-button.

## Inputs (already available)
| What | Where |
|---|---|
| Test footage (copies, link-shared) | Drive `_ENGINE/01-inbox` (`1B2A_2_3B6Rm060keaIrswnJl1TgtmK5j`): `TEST-FunnelStoreScreen.mp4` (`1j3uBAoJ6tPdwGh54_ZqBBgyzTRRpIXIR`, 2:39, 4K screen + audio) — **shared, downloadable**. `TEST-SwitchYard Video.mp4` (`1XJZYcuIrwxFlFDufG5LZY4e9T9Sj-kCA`, 1.1 GB) and `TEST-SwitchYard Screen.mp4` (`1vpfI00lOfa_h-j7Srm6-3Gxohv4GnEvq`) — Andrew may link-share these himself; retry download each hour. |
| Download | `curl -sL -o f.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"` (works only for link-shared files) |
| Never | Edit/delete/move originals anywhere in Drive. Only copy into `_ENGINE`. Don't change sharing on anything. |
| Photos of Andrew | Drive folder **RAWFROMPHOTS** `1A5AMccYaT_xhQs4xLi7o15jBZscjEElE` (images readable via Drive `read_file_content` for viewing; downloading needs link-sharing → if blocked, use Higgsfield Soul/character + whatever you can view) |
| Podcast | RSS: https://media.rss.com/get-real-andrew-george/feed.xml ("Get Real with Andrew George"). Pull episodes, transcripts/audio. Check whether RSS.com has a publishing API (Andrew asked) — report. |
| Scripts | 45 in `content-engine/scripts/` |
| Voice | ElevenLabs: key saved as a cloud secret (expect env `ELEVENLABS_API_KEY`; if missing, check proxy-injected auth by calling the API). Find/confirm Andrew's cloned voice in the account; don't create a new clone without one on file. |
| AI video/image | Higgsfield: key saved as a secret (expect `HIGGSFIELD_API_KEY` or similar; API host `platform.higgsfield.ai` / `api.higgsfield.ai`, auth header `Authorization: Key <id>:<secret>`). Also CLI `higgsfield` + skills in `.agents/skills/`. Credits cost money: cap tonight's spend at ~$40 total. Follow `docs/ai-video-rules.md` strictly. |
| Render | ffmpeg + `tools/variants.py` (Trial Reel variants). |

## The 1 → 20 test (pick the best source; SwitchYard talking video if downloadable, else FunnelStore screen + podcast audio)
1. Transcribe (install `openai-whisper` or `faster-whisper` via pip), find the 3–5 strongest moments.
2. Master reel 9:16 (captions, hook text, brand look from `docs/brand.md`).
3. 3 main-feed re-edits with **different opening hooks** (alt spoken line from the footage, or a Higgsfield-generated open per AI rules #1–3).
4. 6 Trial Reel variants (`tools/variants.py`).
5. Podcast clip (audio) + an extended podcast segment script; ElevenLabs voice only if Andrew's clone exists.
6. YouTube long-form outline + title/thumbnail concepts (Sell This Feature format).
7. 3 LinkedIn posts (novel-style, 3 angles), 3 Threads posts, 1 X thread.
8. 1 carousel (render slides as PNGs, 1080×1350).
9. 1 long email (GHL), 1 Substack/community essay.
10. **Story sequence** (see below), 1 full set.
11. Spanish: translated captions + (if possible) ElevenLabs dub of the master reel.
Record every output in a manifest (`outputs/2026-11-04-<source>/manifest.json`, matching `supabase/schema.sql` `outputs` fields).

## Stories (new workstream)
Research story strategies — **@nik_setting**, **Shelby Sapp**, others — and write `docs/stories.md`: the proven sequence (e.g. **authority → testimonial → resource → link/DM CTA**), frame-by-frame templates, text styles, cadence. Then build one sequence for Andrew:
- Use real photos from RAWFROMPHOTS where they fit (view them; note which are usable and why in `research/brand/photo-library.md`).
- Generate aesthetic lifestyle images of Andrew with Higgsfield (at a computer, in the car, travelling, coffee shop, office) using his character/Soul reference — images only, consistent with his real look.
- Output 1080×1920 PNG frames with text overlays.

## SOPs to write (`docs/sops/`)
- `01-intake.md` (footage → inbox → manifest), `02-multiplier-run.md` (step-by-step 1 → 20), `03-stories.md`, `04-review-and-approve.md`, `05-posting.md` (GHL Social Planner; nothing live without approval), `06-agents.md` (who does what, daily cap 5).
- Turn repeatable steps into scripts in `tools/` (transcribe, cut, caption burn-in, carousel renderer, story renderer, text-post writer prompts).

## Deliver by morning
- Artifact page "One → Twenty" (private) with all outputs; videos ≤15 MB each (re-encode 720p if needed). Link it in the log.
- Copy finished files into Drive `_ENGINE/02-review` (small files only; note if upload size blocks).
- Update `docs/STATUS.md`, `logs/2026-11-04.md`, and a Second Brain log doc. Commit + push to `main` regularly (at least hourly).
- Morning note for Andrew: ≤8 lines — link, what worked, what needs him.

## Agents
Already used 3/5 today (Nov 4 CT). You may spawn **at most 2** more. Prefer doing work yourself.
