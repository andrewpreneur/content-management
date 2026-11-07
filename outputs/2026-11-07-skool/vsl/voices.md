# Voice files (ElevenLabs, generated Nov 7, 2026)

Model `eleven_multilingual_v2`, generated paragraph by paragraph through `/v1/text-to-speech/{voice}/with-timestamps` with previous/next text for continuity (`src/tts.py`). Every paragraph was transcribed back with faster-whisper `small.en` (`src/qc_voice.py`). Lines with wrong words or long pauses were re-rolled with a new seed (`src/fix.py`). Stitched with `src/stitch.py`: trim, match each paragraph to -18 LUFS, shorten pauses over 0.6 s, 0.30 s between paragraphs.

No new voice clone was created. Andrew = his existing clone "Andrew VoiceMail" `Om3UwRqy6aVx0QxEw9Dg`.

| Set | Voice | Voice ID | Settings | Paragraphs | Voice length |
|---|---|---|---|---|---|
| vsl1-andrew | Andrew VoiceMail (clone) | `Om3UwRqy6aVx0QxEw9Dg` | stab 0.55, sim 0.8, style 0.15, speed 0.87 | 11 | 71.4 s |
| vsl1-pro | Alex - Upbeat, Energetic and Clear | `yl2ZDV1MzN4HbQJbMihG` | stab 0.42, sim 0.8, style 0.25, speed 1.0 | 11 | 75.2 s |
| vsl1cut-andrew | Andrew VoiceMail (clone) | `Om3UwRqy6aVx0QxEw9Dg` | stab 0.55, sim 0.8, style 0.15, speed 0.87 | 6 | 34.2 s |
| vsl1cut-pro | Alex - Upbeat, Energetic and Clear | `yl2ZDV1MzN4HbQJbMihG` | stab 0.42, sim 0.8, style 0.25, speed 1.0 | 6 | 37.1 s |
| vsl2-andrew | Andrew VoiceMail (clone) | `Om3UwRqy6aVx0QxEw9Dg` | stab 0.55, sim 0.8, style 0.15, speed 0.87 | 10 | 67.6 s |
| vsl2-pro | Joe Inglewood - Magnetic and Captivating | `UpphzPau5vxibPYV2NeV` | stab 0.42, sim 0.8, style 0.25, speed 1.06 | 10 | 87.6 s |
| vsl3-andrew | Andrew VoiceMail (clone) | `Om3UwRqy6aVx0QxEw9Dg` | stab 0.55, sim 0.8, style 0.15, speed 0.87 | 12 | 67.1 s |
| vsl3-pro | Brian | `n8kTUi6dVrplENT9Un56` | stab 0.42, sim 0.8, style 0.25, speed 1.0 | 12 | 79.4 s |
| vsl3cut-andrew | Andrew VoiceMail (clone) | `Om3UwRqy6aVx0QxEw9Dg` | stab 0.55, sim 0.8, style 0.15, speed 0.87 | 6 | 32.8 s |
| vsl3cut-pro | Brian | `n8kTUi6dVrplENT9Un56` | stab 0.42, sim 0.8, style 0.25, speed 1.0 | 6 | 38.9 s |

Stitched voice tracks (MP3) are on branch `render-drop/skool-vsl` under `voice/`. Word timestamps per set: `timing/<set>.json`.

**Pronunciation check:** whisper heard "GoHighLevel", "Claude" and "SaaS" right in every set (SaaS is said "sass").
**Re-rolled lines:** vsl2-andrew p01 ("GoHighLevels"), p07 and p09 (dropped or extra word); vsl3-andrew p06, p09, p12 (extra "and", "this" said as "the"); vsl3-pro p02 and vsl3cut-pro p02 (1.2 s pause).
**Andrew's clone runs fast:** at speed 1.0 it was about 4+ words per second and sounded rushed, so his sets use speed 0.87 and stability 0.55 (the clone's loudness also jumps between lines; stitching evens it out).
**Pro voices:** VSL 1 = Alex (upbeat, matches the playful puzzle look), VSL 2 = Joe Inglewood (warm, personal; speed 1.06 so it keeps moving), VSL 3 = Brian (confident, for the ambitious one). Cuts use the same voice as their parent VSL.
