# vsl-b: one-feature VSL edits (Nov 7, 2026 overnight)

**Review page (previews):** https://claude.ai/artifact/9j8TLGqaj7vDcWzqNf4VsN

**Videos:** branch `render-drop/vsl-b` (full-quality H.264 CRF 21, ≤4 Mb/s). 40 renders so far. Nothing posted anywhere.

## What each version is
- **A** clean edit: full message, brand kit (navy/yellow, Inter Tight + Playfair accents), word captions, punch-ins every 2-3 s, lower third, motion cards in a split layout, screen-recording cutaways (feature pairs), end card. 9:16, 4:5 and 16:9 (landscape VSL).
- **L** same clean edit in a light theme with pill captions. 9:16 and 4:5.
- **H1-H3** three different openings on the same body (hook headline + a line pulled from later in the video, then the full message). 9:16.
- **AD** 30-45 s ad cut with hook headline and progress bar. 9:16 and 4:5.
- **M1** no face: full-frame motion cards and screen recordings over Andrew's original voice. 9:16 and 4:5.
- **T1** no face, no voice: text + motion cards on music (script condensed from the video). 9:16 and 4:5.

How it was made: `tools/vslb/` (ffmpeg face edit + HTML motion overlay rendered with Playwright). Specs per video in `specs/`. Re-render one: `python3 outputs/2026-11-07-vsl-b/specs/v5.py v5-AD-916`.

## Every output

| id | source | version | format | length | hook / opening | file |
|---|---|---|---|---|---|---|
| v5-A-916 | VIDEO 5 | clean edit | 9:16 | 63s |  | `render-drop/vsl-b:v5/v5-A-916.mp4` |
| v5-H1-916 | VIDEO 5 | hook 1 | 9:16 | 63s | Vibe coding became the word of the year in 9 months | `render-drop/vsl-b:v5/v5-H1-916.mp4` |
| v5-A-45 | VIDEO 5 | clean edit | 4:5 | 63s |  | `render-drop/vsl-b:v5/v5-A-45.mp4` |
| v5-H3-916 | VIDEO 5 | hook 3 | 9:16 | 45s | You can't resell ChatGPT. You can resell this. | `render-drop/vsl-b:v5/v5-H3-916.mp4` |
| v5-A-169 | VIDEO 5 | clean edit (landscape VSL) | 16:9 | 63s |  | `render-drop/vsl-b:v5/v5-A-169.mp4` |
| v5-H2-916 | VIDEO 5 | hook 2 | 9:16 | 66s | $99/mo for one GHL feature | `render-drop/vsl-b:v5/v5-H2-916.mp4` |
| v5-AD-916 | VIDEO 5 | ad cut | 9:16 | 30s | Sell AI Studio under your name | `render-drop/vsl-b:v5/v5-AD-916.mp4` |
| v5-AD-45 | VIDEO 5 | ad cut | 4:5 | 30s | Sell AI Studio under your name | `render-drop/vsl-b:v5/v5-AD-45.mp4` |
| v5-T1-916 | VIDEO 5 | text + motion, music only | 9:16 | 29s |  | `render-drop/vsl-b:v5/v5-T1-916.mp4` |
| v5-T1-45 | VIDEO 5 | text + motion, music only | 4:5 | 29s |  | `render-drop/vsl-b:v5/v5-T1-45.mp4` |
| v6-A-45 | VIDEO 6 | clean edit | 4:5 | 36s |  | `render-drop/vsl-b:v6/v6-A-45.mp4` |
| v6-A-916 | VIDEO 6 | clean edit | 9:16 | 36s |  | `render-drop/vsl-b:v6/v6-A-916.mp4` |
| v6-A-169 | VIDEO 6 | clean edit (landscape VSL) | 16:9 | 36s |  | `render-drop/vsl-b:v6/v6-A-169.mp4` |
| v6-H1-916 | VIDEO 6 | hook 1 | 9:16 | 36s | I've sold GHL for years. This sells easiest. | `render-drop/vsl-b:v6/v6-H1-916.mp4` |
| v6-H2-916 | VIDEO 6 | hook 2 | 9:16 | 42s | Stop selling the CRM | `render-drop/vsl-b:v6/v6-H2-916.mp4` |
| v6-AD-916 | VIDEO 6 | ad cut | 9:16 | 22s | The easiest GHL feature to sell | `render-drop/vsl-b:v6/v6-AD-916.mp4` |
| v6-H3-916 | VIDEO 6 | hook 3 | 9:16 | 42s | Put your logo on vibe coding | `render-drop/vsl-b:v6/v6-H3-916.mp4` |
| v6-T1-916 | VIDEO 6 | text + motion, music only, no voice | 9:16 | 21s |  | `render-drop/vsl-b:v6/v6-T1-916.mp4` |
| v6-AD-45 | VIDEO 6 | ad cut | 4:5 | 22s | The easiest GHL feature to sell | `render-drop/vsl-b:v6/v6-AD-45.mp4` |
| v6-T1-45 | VIDEO 6 | text + motion, music only, no voice | 4:5 | 21s |  | `render-drop/vsl-b:v6/v6-T1-45.mp4` |
| cv-A-45 | ConvoAISchedule | clean edit | 4:5 | 96s |  | `render-drop/vsl-b:convo/cv-A-45.mp4` |
| cv-A-916 | ConvoAISchedule | clean edit | 9:16 | 96s |  | `render-drop/vsl-b:convo/cv-A-916.mp4` |
| cv-A-169 | ConvoAISchedule | clean edit (landscape VSL) | 16:9 | 96s |  | `render-drop/vsl-b:convo/cv-A-169.mp4` |
| v6-M1-916 | VIDEO 6 | motion, no face, original voice | 9:16 | 36s |  | `render-drop/vsl-b:v6/v6-M1-916.mp4` |
| v5-M1-45 | VIDEO 5 | motion, no face, original voice | 4:5 | 63s |  | `render-drop/vsl-b:v5/v5-M1-45.mp4` |
| v5-M1-916 | VIDEO 5 | motion, no face, original voice | 9:16 | 63s |  | `render-drop/vsl-b:v5/v5-M1-916.mp4` |
| v6-M1-45 | VIDEO 6 | motion, no face, original voice | 4:5 | 36s |  | `render-drop/vsl-b:v6/v6-M1-45.mp4` |
| cv-H1-916 | ConvoAISchedule | hook 1 | 9:16 | 96s | Your AI agent needs working hours | `render-drop/vsl-b:convo/cv-H1-916.mp4` |
| cv-H2-916 | ConvoAISchedule | hook 2 | 9:16 | 101s | Hire an AI for the night shift | `render-drop/vsl-b:convo/cv-H2-916.mp4` |
| cv-H3-916 | ConvoAISchedule | hook 3 | 9:16 | 102s | Is your AI agent ghosting leads at 5 PM? | `render-drop/vsl-b:convo/cv-H3-916.mp4` |
| cv-AD-916 | ConvoAISchedule | ad cut | 9:16 | 43s | Give your AI agent working hours | `render-drop/vsl-b:convo/cv-AD-916.mp4` |
| cv-T1-916 | ConvoAISchedule | text + motion, music only, no voice | 9:16 | 26s |  | `render-drop/vsl-b:convo/cv-T1-916.mp4` |
| cv-AD-45 | ConvoAISchedule | ad cut | 4:5 | 43s | Give your AI agent working hours | `render-drop/vsl-b:convo/cv-AD-45.mp4` |
| cv-M1-916 | ConvoAISchedule | motion, no face, original voice | 9:16 | 96s |  | `render-drop/vsl-b:convo/cv-M1-916.mp4` |
| cv-T1-45 | ConvoAISchedule | text + motion, music only, no voice | 4:5 | 26s |  | `render-drop/vsl-b:convo/cv-T1-45.mp4` |
| cv-M1-45 | ConvoAISchedule | motion, no face, original voice | 4:5 | 96s |  | `render-drop/vsl-b:convo/cv-M1-45.mp4` |
| dyk-A-916 | DYKCustomAudiences | clean edit | 9:16 | 101s |  | `render-drop/vsl-b:dyk/dyk-A-916.mp4` |
| dyk-A-45 | DYKCustomAudiences | clean edit | 4:5 | 101s |  | `render-drop/vsl-b:dyk/dyk-A-45.mp4` |
| dyk-A-169 | DYKCustomAudiences | clean edit (landscape VSL) | 16:9 | 101s |  | `render-drop/vsl-b:dyk/dyk-A-169.mp4` |
| dyk-H1-916 | DYKCustomAudiences | hook 1 | 9:16 | 101s | Your smart lists can feed your Meta ads | `render-drop/vsl-b:dyk/dyk-H1-916.mp4` |

Sources (Drive, read-only): VSLs/ConvoAISchedule_VIDEO + _SCREEN (Drive 1SBnkwrzd8tB_3-OgOC9u5jJ85eBdGiNm / 11eKLLz6jM0vNwC3zWior1Ogkfclg0nQZ); VSLs/ConvoAISchedule_VIDEO + _SCREEN (Drive 1SBnkwrzd8tB_3-OgOC9u5jJ85eBdGiNm / 11eKLLz6jM0vNwC3zWior1Ogkfclg0nQZ) (script only); VSLs/DYKCustomAudiences_VIDEO + _SCREEN (Drive 1sgq7xj_JrEX2udQDijnNqPDYjQk4Ce0s / 1oRWDEsuJHPnCtyqWxR5T8kdfN6qy__8O); VSLs/VIDEO 5 (Drive 1-bixWq9KXz0kb-DQsuJKTPGmh7uDrFSn); VSLs/VIDEO 5 (Drive 1-bixWq9KXz0kb-DQsuJKTPGmh7uDrFSn) (script only); VSLs/VIDEO 6 (Drive 1_n-UedWGJ7ZQO9VW1QzZxDN7X-i-vmDH); VSLs/VIDEO 6 (Drive 1_n-UedWGJ7ZQO9VW1QzZxDN7X-i-vmDH) (script only)
