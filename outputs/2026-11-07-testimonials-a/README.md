# Testimonial ads — testimonials-a (Nov 7, 2026)

**Review page (watch + Approve/Skip): https://claude.ai/artifact/2yutvrpgA3JW8S3rgrvhuB** (private to Andrew; picks are saved in the page)

All drafts. Nothing posted.

## What's here
- **60 ads, 78 video files** (60 in 9:16, 18 also in 4:5): Mark 14, Lee 12, Ben 10, Jessica 4, Tania 12, multi-person supercuts 8 (05-08 also use Brentney + Rob from testimonials-b).
- Full-quality videos: branch **`render-drop/testimonials-a`** (`<id>/<id>-916.mp4`, `<id>/<id>-45.mp4`). H.264 CRF 21 (≤4 Mb/s), AAC 128k, faststart, 1080×1920 / 1080×1350.
- `quote-bank.md` — best lines per person for statics, carousels, landing pages (plus what must NOT be used).
- `transcripts/` — word-timed transcripts (mark, lee, ben, jessica, tania-vt, tania-call).
- `manifest.csv` — every file: hook, hook type, length, source, exact source segments, music, loudness.
- `specs.json` / `build_specs.py` — the cut list; re-render with `python3 tools/testimonial_ads.py outputs/2026-11-07-testimonials-a/specs.json OUT_DIR`.

## How each ad is built (`tools/testimonial_ads.py`)
Real client footage only (no AI faces). Hook in the first 3 s, one of five types: **stat** (big number), **quote** (their best line), **question**, **headline** (yellow bar), or a 1.3 s **text card** before the footage. Then word-by-word captions (active word yellow), name + business lower third, light punch-ins on cuts and every ~4 s, a top label, and a 2.8 s end card: "Want results like <name>? BOOK A CALL WITH ANDREW" with Andrew's photo. Mixkit music bed ~18 LU under the voice, ducked while people talk. Audio checked on every file: -14 LUFS (±0.3), peaks ≤ -1 dBFS, no dropouts. Frames checked on every file (7 stills each).

## Things Andrew should know (decide before running paid)
1. **Tania's ads come from a recorded support call, not a testimonial she filmed.** She knew it was recorded, but get her OK before using her name/photo in paid ads. Her camera was off, so her ads show her real photo + the call audio (screen blurred so no client data or URLs show). Her venting about HighLevel staff is cut out of everything.
2. **Jessica's clip is 9 s from a call in speaker view**: it cuts to Andrew smiling twice. Kept as real reaction shots; her name tag only shows on her shots. Business name unknown (lower third says "Client").
3. **Ben**: last name and agency name unknown (lower third says "Ben · Agency owner"). Send them if you want them added.
4. **Mark and Lee** were already framed in an old purple phone mockup; the ads crop the clean phone screen, so their footage is upscaled (fine on phones, slightly soft on desktop).
5. End-card CTA is a placeholder ("BOOK A CALL WITH ANDREW"). Swap in one line in `tools/testimonial_ads.py` (`cta`) if you want a keyword or a different offer.
6. Ben here and testimonials-b's "Agency owner" are the same video (two Drive copies). Pick one name for both.

## Every output
| id | format | length | hook type | hook | source |
|---|---|---|---|---|---|
| `mark-01/mark-01-916.mp4` | 9:16 | 14.94s (15s) | stat | 5 / online clients in under a month | mark (1DO6aV…) |
| `mark-01/mark-01-45.mp4` | 4:5 | 14.94s (15s) | stat | 5 / online clients in under a month | mark (1DO6aV…) |
| `mark-02/mark-02-916.mp4` | 9:16 | 13.07s (15s) | quote | He's helped me land five online clients | mark (1DO6aV…) |
| `mark-03/mark-03-916.mp4` | 9:16 | 13.07s (15s) | question | Stuck on bringing in new leads? | mark (1DO6aV…) |
| `mark-04/mark-04-916.mp4` | 9:16 | 13.73s (15s) | headline | Sales calls that don't feel like sales calls | mark (1DO6aV…) |
| `mark-05/mark-05-916.mp4` | 9:16 | 17.13s (15s) | card | They said no to the sale. Then this happened. | mark (1DO6aV…) |
| `mark-05/mark-05-45.mp4` | 4:5 | 17.13s (15s) | card | They said no to the sale. Then this happened. | mark (1DO6aV…) |
| `mark-06/mark-06-916.mp4` | 9:16 | 13.28s (15s) | quote | That was all Andrew's idea. | mark (1DO6aV…) |
| `mark-07/mark-07-916.mp4` | 9:16 | 22.94s (30s) | stat | 12 yrs / a personal trainer. Stuck on leads. | mark (1DO6aV…) |
| `mark-08/mark-08-916.mp4` | 9:16 | 21.9s (30s) | question | Do your DMs turn into clients? | mark (1DO6aV…) |
| `mark-09/mark-09-916.mp4` | 9:16 | 25.23s (30s) | headline | Stuck on leads → 5 new clients in under a month | mark (1DO6aV…) |
| `mark-09/mark-09-45.mp4` | 4:5 | 25.23s (30s) | headline | Stuck on leads → 5 new clients in under a month | mark (1DO6aV…) |
| `mark-10/mark-10-916.mp4` | 9:16 | 21.08s (30s) | quote | They said no to the sale. Then they signed. | mark (1DO6aV…) |
| `mark-11/mark-11-916.mp4` | 9:16 | 54.65s (60s) | card | How a personal trainer landed 5 clients in under a month | mark (1DO6aV…) |
| `mark-11/mark-11-45.mp4` | 4:5 | 54.65s (60s) | card | How a personal trainer landed 5 clients in under a month | mark (1DO6aV…) |
| `mark-12/mark-12-916.mp4` | 9:16 | 35.07s (45s) | stat | 5 / new clients in a month. Plus 2 won back. | mark (1DO6aV…) |
| `mark-13/mark-13-916.mp4` | 9:16 | 12.3s (15s) | question | Personal trainer? Watch this. | mark (1DO6aV…) |
| `mark-14/mark-14-916.mp4` | 9:16 | 24.27s (30s) | quote | You definitely can't go wrong. | mark (1DO6aV…) |
| `lee-01/lee-01-916.mp4` | 9:16 | 16.37s (15s) | quote | The support has been tremendous | lee (1lYYpK…) |
| `lee-01/lee-01-45.mp4` | 4:5 | 16.37s (15s) | quote | The support has been tremendous | lee (1lYYpK…) |
| `lee-02/lee-02-916.mp4` | 9:16 | 14.13s (15s) | question | No idea what you're doing on social media? | lee (1lYYpK…) |
| `lee-03/lee-03-916.mp4` | 9:16 | 16.93s (15s) | headline | A coach, brand new to social media | lee (1lYYpK…) |
| `lee-04/lee-04-916.mp4` | 9:16 | 13.65s (15s) | quote | One of the kindest humans you would meet | lee (1lYYpK…) |
| `lee-05/lee-05-916.mp4` | 9:16 | 16.47s (15s) | card | Brand new to social media? Watch this. | lee (1lYYpK…) |
| `lee-06/lee-06-916.mp4` | 9:16 | 26.44s (30s) | headline | No plan → a plan that works | lee (1lYYpK…) |
| `lee-06/lee-06-45.mp4` | 4:5 | 26.44s (30s) | headline | No plan → a plan that works | lee (1lYYpK…) |
| `lee-07/lee-07-916.mp4` | 9:16 | 27.47s (30s) | question | Looking for real guidance on social media? | lee (1lYYpK…) |
| `lee-08/lee-08-916.mp4` | 9:16 | 24.97s (30s) | quote | He knows what he's doing and cares | lee (1lYYpK…) |
| `lee-09/lee-09-916.mp4` | 9:16 | 59.9s (60s) | card | What happened when a coach got real guidance on social media | lee (1lYYpK…) |
| `lee-09/lee-09-45.mp4` | 4:5 | 59.9s (60s) | card | What happened when a coach got real guidance on social media | lee (1lYYpK…) |
| `lee-10/lee-10-916.mp4` | 9:16 | 35.93s (45s) | headline | Expert skills. A plan a beginner can follow. | lee (1lYYpK…) |
| `lee-11/lee-11-916.mp4` | 9:16 | 15.63s (15s) | quote | Absolutely worth it. | lee (1lYYpK…) |
| `lee-12/lee-12-916.mp4` | 9:16 | 26.85s (30s) | question | Need a plan for social media? | lee (1lYYpK…) |
| `ben-01/ben-01-916.mp4` | 9:16 | 15.3s (15s) | quote | Always follows through with what he says | ben (1yf2DD…) |
| `ben-01/ben-01-45.mp4` | 4:5 | 15.3s (15s) | quote | Always follows through with what he says | ben (1yf2DD…) |
| `ben-02/ben-02-916.mp4` | 9:16 | 15.3s (15s) | question | Need help building out GoHighLevel? | ben (1yf2DD…) |
| `ben-03/ben-03-916.mp4` | 9:16 | 15.4s (15s) | headline | An agency owner on Andrew's team | ben (1yf2DD…) |
| `ben-04/ben-04-916.mp4` | 9:16 | 17.07s (15s) | card | What agency owners say about Andrew's team | ben (1yf2DD…) |
| `ben-05/ben-05-916.mp4` | 9:16 | 24.1s (30s) | quote | He's taken really good care of us | ben (1yf2DD…) |
| `ben-05/ben-05-45.mp4` | 4:5 | 24.1s (30s) | quote | He's taken really good care of us | ben (1yf2DD…) |
| `ben-06/ben-06-916.mp4` | 9:16 | 21.35s (30s) | headline | HighLevel built out for us and our clients | ben (1yf2DD…) |
| `ben-07/ben-07-916.mp4` | 9:16 | 15.27s (15s) | question | Thinking about working with Andrew? | ben (1yf2DD…) |
| `ben-08/ben-08-916.mp4` | 9:16 | 26.97s (30s) | card | Real agency. Real build. | ben (1yf2DD…) |
| `ben-08/ben-08-45.mp4` | 4:5 | 26.97s (30s) | card | Real agency. Real build. | ben (1yf2DD…) |
| `ben-09/ben-09-916.mp4` | 9:16 | 13.27s (15s) | quote | I highly recommend it. | ben (1yf2DD…) |
| `ben-10/ben-10-916.mp4` | 9:16 | 12.9s (15s) | headline | Builds for our clients and for us | ben (1yf2DD…) |
| `jessica-01/jessica-01-916.mp4` | 9:16 | 10.57s (15s) | quote | You're on top of everything for us | jessica (1xBZ3x…) |
| `jessica-01/jessica-01-45.mp4` | 4:5 | 10.57s (15s) | quote | You're on top of everything for us | jessica (1xBZ3x…) |
| `jessica-02/jessica-02-916.mp4` | 9:16 | 10.57s (15s) | question | Want a team that's actually on top of it? | jessica (1xBZ3x…) |
| `jessica-03/jessica-03-916.mp4` | 9:16 | 11.87s (15s) | card | Unscripted. Straight from a client call. | jessica (1xBZ3x…) |
| `jessica-04/jessica-04-916.mp4` | 9:16 | 9.18s (15s) | headline | So helpful. So on top of it. | jessica (1xBZ3x…) |
| `tania-01/tania-01-916.mp4` | 9:16 | 16.68s (15s) | card | She was 20 hours in. Then she got on a call. | taniatestimonial.mp4 (1FfSs6…) |
| `tania-01/tania-01-45.mp4` | 4:5 | 16.68s (15s) | card | She was 20 hours in. Then she got on a call. | taniatestimonial.mp4 (1FfSs6…) |
| `tania-02/tania-02-916.mp4` | 9:16 | 14.34s (15s) | quote | I don't know you, but I love you so much | taniatestimonial.mp4 (1FfSs6…) |
| `tania-03/tania-03-916.mp4` | 9:16 | 18.39s (15s) | question | 20 hours stuck in GoHighLevel? | taniatestimonial.mp4 (1FfSs6…) |
| `tania-04/tania-04-916.mp4` | 9:16 | 15.63s (15s) | quote | They have to have your knowledge | taniatestimonial.mp4 (1FfSs6…) |
| `tania-05/tania-05-916.mp4` | 9:16 | 14.57s (15s) | headline | Not a marketer? Hire an actual expert. | taniatestimonial.mp4 (1FfSs6…) |
| `tania-06/tania-06-916.mp4` | 9:16 | 14.02s (15s) | quote | I will send everybody to you | taniatestimonial.mp4 (1FfSs6…) |
| `tania-07/tania-07-916.mp4` | 9:16 | 29.48s (30s) | card | A sales trainer's real call with Andrew | taniatestimonial.mp4 (1FfSs6…) |
| `tania-07/tania-07-45.mp4` | 4:5 | 29.48s (30s) | card | A sales trainer's real call with Andrew | taniatestimonial.mp4 (1FfSs6…) |
| `tania-08/tania-08-916.mp4` | 9:16 | 23.93s (30s) | question | Spending a bazillion dollars on marketing? | taniatestimonial.mp4 (1FfSs6…) |
| `tania-09/tania-09-916.mp4` | 9:16 | 39.78s (45s) | headline | 20 hours stuck. One call. | taniatestimonial.mp4 (1FfSs6…) |
| `tania-09/tania-09-45.mp4` | 4:5 | 39.78s (45s) | headline | 20 hours stuck. One call. | taniatestimonial.mp4 (1FfSs6…) |
| `tania-10/tania-10-916.mp4` | 9:16 | 15.38s (15s) | stat | 20 hrs / stuck on one setup. Fixed on one call. | taniatestimonial.mp4 (1FfSs6…) |
| `tania-11/tania-11-916.mp4` | 9:16 | 22.17s (30s) | quote | I promise you, this is going to pay off | taniatestimonial.mp4 (1FfSs6…) |
| `tania-12/tania-12-916.mp4` | 9:16 | 60.61s (60s) | card | Inside a real client call | taniatestimonial.mp4 (1FfSs6…) |
| `supercut-01/supercut-01-916.mp4` | 9:16 | 20.23s (30s) | headline | What clients say after working with Andrew | supercut: mark + lee + ben + jessica |
| `supercut-01/supercut-01-45.mp4` | 4:5 | 20.23s (30s) | headline | What clients say after working with Andrew | supercut: mark + lee + ben + jessica |
| `supercut-02/supercut-02-916.mp4` | 9:16 | 9.01s (15s) | quote | Absolutely worth it. | supercut: lee + mark + ben + jessica |
| `supercut-03/supercut-03-916.mp4` | 9:16 | 37.53s (45s) | card | 4 clients. 4 different businesses. | supercut: mark + lee + ben + jessica |
| `supercut-03/supercut-03-45.mp4` | 4:5 | 37.53s (45s) | card | 4 clients. 4 different businesses. | supercut: mark + lee + ben + jessica |
| `supercut-04/supercut-04-916.mp4` | 9:16 | 18.51s (30s) | question | Thinking about working with Andrew? | supercut: ben + mark + lee |
| `supercut-05/supercut-05-916.mp4` | 9:16 | 29.57s (30s) | headline | What SaaSSuite clients say about Andrew | supercut: brentney + rob + mark + lee |
| `supercut-05/supercut-05-45.mp4` | 4:5 | 29.57s (30s) | headline | What SaaSSuite clients say about Andrew | supercut: brentney + rob + mark + lee |
| `supercut-06/supercut-06-916.mp4` | 9:16 | 46.97s (45s) | card | 6 clients. 6 real stories. | supercut: mark + brentney + rob + lee + ben + jessica |
| `supercut-06/supercut-06-45.mp4` | 4:5 | 46.97s (45s) | card | 6 clients. 6 real stories. | supercut: mark + brentney + rob + lee + ben + jessica |
| `supercut-07/supercut-07-916.mp4` | 9:16 | 24.85s (30s) | question | Worried about supporting your clients? | supercut: brentney + rob |
| `supercut-08/supercut-08-916.mp4` | 9:16 | 17.0s (15s) | quote | Real humans answering your clients' questions | supercut: rob + brentney |
