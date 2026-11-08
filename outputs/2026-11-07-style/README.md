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
| Clip | Len | Speaker | Hook | Big moments (V8) | Files |
|---|---|---|---|---|---|
| pod1-05 | 21.7 s | Andy | Should you charge less when you're starting out? | a little bit of DIRT · you're getting PAID TO LEARN · at a LOWER PRICE · the right privilege to CHARGE | `render-drop/style:pod1-05/pod1-05-v8.mp4`, `-v1.mp4` |
| pod1-10 | 18.1 s | Andrew | Why local businesses never switch systems? | set up for them ASAP · for the next 30 years · still on WORDPRESS | `render-drop/style:pod1-10/pod1-10-v8.mp4`, `-v1.mp4` |
| pod1-04 | 26.1 s | Andy | Where do your first SaaS customers come from? | a bridge of TRUST · in your career PROFESSION · make a REFERRAL · if you have INTEGRITY · you'll make MISTAKES | `render-drop/style:pod1-04/pod1-04-v8.mp4`, `-v1.mp4` |
| pod1-01 | 31.8 s | Andy (SoloLink) | How many tools could your clients drop? | manually keeping track through TRELLO BOARDS · a person's FIRST · a lot of MANUAL WORK · the tasks get ASSIGNED · stop by their BUSINESS · now been able to SYSTEMIZE | `render-drop/style:pod1-01/pod1-01-v8.mp4`, `-v1.mp4` |
| pod2-01 | 18.5 s | Blake Coker (Task Engine) | Would you build an agency for banks? | a focus on MIDSIZE BANKS · google, SEO | `render-drop/style:pod2-01/pod2-01-v8.mp4`, `-v1.mp4` |
| pod2-03 | 28.1 s | Andrew → Blake | How do you land your first big client? | home SERVICE · from my previous JOB · in the banking BUSINESS · a friend of MINE · REFERRALS | `render-drop/style:pod2-03/pod2-03-v8.mp4`, `-v1.mp4` |
| pod2-05 | 18.0 s | Andrew + Blake | Why your cold DMs aren't working? | i'll do your GHL STUFF · what are the PAIN POINTS · your first few CUSTOMERS · your time and just LISTEN | `render-drop/style:pod2-05/pod2-05-v8.mp4`, `-v1.mp4` |
| pod3-01 | 21.8 s | Ohaji | How did 2 months beat 4 years of college? | this is INSANE · life works and about FAILURE · failure is BAD · you fail, you KEEP GOING · failure is GOOD | `render-drop/style:pod3-01/pod3-01-v8.mp4`, `-v1.mp4` |
| pod3-05 | 41.1 s | green intern | Who actually supports you when you start posting? | see a lot of LURKERS · about me behind my BACK · working a corporate 9 TO 5 · creating CONTENT · got a lot of STRANGERS · standing on that support 10 toes down · kept me GOING | `render-drop/style:pod3-05/pod3-05-v8.mp4`, `-v1.mp4` |
| pod3-08 | 21.1 s | Ty | Can you start an agency with zero experience? | out of the horse TRAINING INDUSTRY · gave my life more PURPOSE · digital marketing and AUTOMATION · build AI AGENTS | `render-drop/style:pod3-08/pod3-08-v8.mp4`, `-v1.mp4` |

Known issue: **pod3-01** — the speaker map (shared with V1) frames a listener while Ohaji talks. Needs a manual speaker fix in the clip bank before posting. HOLD kept on the V8 plan item (`clip__pod3-01__w3`, 2026-11-21 08:30). Not approved.

## Calendar order (Nov 8, planning only)
Andrew asked (Nov 7, 11:41 PM CT) for one or two V8 reels that open on his face, then more speaker-2 clips. Post order in `outputs/planner/plan.json`: 2026-11-09 08:30 is now `pod2-08` (speaker `Andrew`), and `pod2-01` (Blake) moved to 15:00 the same day. Slot 2 stays `pod3-04`. A second Andrew reel was not added: every other solo-Andrew V8 clip already posts again inside Nov 9–15. Detail and the pending handoff: `v8-rollout.md`. Editing, captions, and audio were not changed. Nothing was approved or scheduled.

Videos: branch `render-drop/style` (`<clip>/<clip>-v8.mp4`, `<clip>/<clip>-v1.mp4`). Previews (540p) on the review page.

## How to render
`python3 tools/formats.py outputs/clip-bank/pod1.json pod1-05 --formats v8` (about 13 min for a 22 s clip alone on 4 cores; `--build-only` builds the page for a stills check).
