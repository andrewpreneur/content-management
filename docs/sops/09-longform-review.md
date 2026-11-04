# SOP 09 — Long-form review (mistakes, repetitions, dead air)
1. Transcribe: `python3 tools/transcribe.py video.mp4 work/<name>/`
2. Review: `python3 tools/longform_review.py work/<name>/transcript.json work/<name>/review --video video.mp4 --render`
   - **repeat** (≥90% same sentence within 30 s) → earlier take cut (the later one is usually the clean retake)
   - **check** (82–90% similar) → listed, not cut: could be a callback by another speaker
   - **stutter** ("the the", "I I") → cut; punctuated doubles ("really, really", "fail, fail forward") are emphasis and kept
   - **filler** (um/uh) → cut; **pause** > 1.2 s → tightened
   - verbal habits ("like", "you know", "kind of") → counted, not cut
3. Output: `review.md` (every issue with time + words), `cuts.csv` (in/out for Premiere/DaVinci), `roughcut.mp4`.
4. A human watches the rough cut before anything ships. Whisper hides many "um"s, so counts are a floor.
