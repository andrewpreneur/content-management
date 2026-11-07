Review page: https://claude.ai/artifact/4v56ihPm4EtTLbjjFdL4Gj

# Style stream — Nov 7, 2026: V3 "kinetic" retired, V8 "Animated" built

Andrew: "kill the kinetic style (V3), it doesn't look good. Go deeper into the example reels and hone that editing style with the animations."

## What changed
- **Teardown** of all 13 example reels in `examplereelsandformats`: `teardown.md`, frame strips in `shots/`.
  Main finding: V3 shouted every beat. The examples keep a small, quiet caption most of the time and land one big animated moment every 3–4 s.
- **V8 "Animated"** (`motion/templates/v8.html`, `tools/formats.py` → `v8_plan`, `emph_beats`, `v8_cues`) replaces V3 everywhere:
  `tools/planner.py`, `tools/reels_page.py`, `tools/render_queue.py` list V8 in V3's slot. V1, V2, V4–V7 untouched.
  V3 code is still in `formats.py`/`motion/templates/v3.html` so old plan items don't crash, but nothing schedules it any more.
- **Clip bank `emph`**: optional per-clip list of punch phrases (`"lead words|KEY WORDS"`), written when the clip is picked
  (see `tools/clip_bank.py`). Added for the 10 test clips. Without it a word-score heuristic picks the beats; it also fills gaps > ~6 s.
- `outputs/planner/plan.json` was **not** regenerated (other sessions own it). It still lists 40 "v3" items; the next
  `python3 tools/planner.py` run turns them into V8. Until then a v3 item still renders the old style if the queue reaches it.

## V8 grammar (from the examples)
| Element | From | How |
|---|---|---|
| Phrase-build captions, word pops, key words yellow italic serif, negative words coral | Nick Saraev | 2–4 words per phrase, blur 8→0 + scale 0.84→1 per word |
| Hook header: white line + punch phrase in a blue box wiping in | Saraev | first sentence only; moves below the face when the face sits high |
| Big beat every ~3.5 s: small lead-in + huge gradient key word, letters stagger in | gp_multimedia | punch-in zoom 1.13×, whoosh; caption hidden during the beat |
| Counters ("30 years") | gp 450,000 / Saraev 21%→60% | digits roll up in 0.6 s |
| Glass chips with an icon (Clients, Automation, Content…) | gp "Real Leads" | pop beside the speaker, ≥4.5 s apart |
| Icon bursts on wins/money/referrals | gp hearts | 5 badges spring out around the caption |
| Handwritten name note + arrow | Diary of a CEO "Snapchat Founder" | first time a named guest talks |
| Rack-focus blur on speaker change, one B&W dip on the hardest negative line | gp | no white flashes |
| SFX on big moments only (~1 per 5 s), -16 LUFS | gp (5 hits in 27 s) | `tools/sound_mix.py` (sound-effects skill method, CC0 kit) |

## Test renders (10 clips, V8 + old V1 for comparison)
CLIPS_TABLE

Videos: branch `render-drop/style` (`<clip>/<clip>-v8.mp4`, `<clip>/<clip>-v1.mp4`). Previews (540p) on the review page.

## How to render
`python3 tools/formats.py outputs/clip-bank/pod1.json pod1-05 --formats v8` (about 13 min for a 22 s clip alone on 4 cores; `--build-only` builds the page for a stills check).
