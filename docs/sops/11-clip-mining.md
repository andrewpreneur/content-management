# SOP 11 — Mine a podcast/long video for clips (→ clip bank → 7-week format rotation)

**Plan (Andrew, Nov 4):** each clip is posted once a week for 7 weeks, a different format each week (V1–V7, `docs/editing-styles.md`).
Never the same clip twice in one week. Daily volume (20–30 posts) comes from *many different clips*, so the bank needs ~175 live clips
at full volume (25/day × 7 days), refilled at ~25 new clips/week.

**Only use edited masters.** Podcast masters live in the edited folder (`1JVEoN5wvfCp81mX_wnKjw5Ck0sUjGn9q`: Pod1–Pod3).
Files in RAW (`1OZbZMppuCXBnX8sUuYSH1FYgqq_C7Hfw`, e.g. Pod4/Pod5) are not edited by the editing team yet: don't mine them.
Andrew is adding a Drive index explaining the folder structure; follow it once it exists.

1. Download + transcribe: `python3 tools/transcribe.py POD.mp4 work/podN/tx`
2. Find candidates: `python3 tools/clip_finder.py work/podN/tx/transcript.json work/podN/clips --source podN`
   → `candidates.md` (non-overlapping 15–45 s windows on sentence boundaries, hook-scored, topic-deduplicated). Read it; the score only
   catches weak/context-dependent openers and rambling.
3. Pick clips into `outputs/clip-bank/podN.json`: each clip = first words + last words (exact transcript text), a 2-line story `title`,
   a `hook_q` (question hook for V4/V5), a `hook_plain` (V7), speaker, topic, and `notes` for anything to verify (names/companies are often misheard).
   Rules: opener must make sense with no context; end on a landing line; one idea per clip; 12–45 s.
4. Resolve + clean + preview: `python3 tools/clip_bank.py outputs/clip-bank/podN.json --preview`
   → exact in/out on word boundaries, cleaned voice (`clean_audio.py --gate strong`, Andrew-approved), word timings, letterbox preview.
5. Previews go to the review page for Andrew's yes/no, then the approved clips get the 7 formats.
