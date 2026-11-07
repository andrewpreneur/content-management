# Meta ad batch · Nov 7, 2026

**Review page:** https://claude.ai/artifact/Txe7mDfm8r3ej2qMLXVCTZ (private; statics, videos, copy buttons for every ad)

Drafts only. Nothing is uploaded to Meta or posted anywhere.

## What's here
| What | Count | Where |
|---|---|---|
| Static ads, 4:5 (1080×1350) | 65 | `statics/<id>.jpg` |
| Same statics in 9:16 (1080×1920, Reels/Stories safe zones kept) | 20 | `statics/<id>_916.jpg` |
| Video ads, 4:5, 6.6–14.1 s | 18 | branch `render-drop/meta-ads` → `meta-ads/<id>.mp4` (previews on the review page) |
| Ad copy for every static (primary text, headline, description, CTA, landing page, angle, hook) | 65 rows | `manifest.csv` |
| Ad copy for every video | 18 rows | `videos.csv` |
| Teardown of the old creative guy's work | 1 | `teardown.md` + contact sheets in `teardown/` |

Rebuild: `python3 tools/meta_ads_batch_1107.py` (statics + manifest), `python3 tools/meta_ads_videos.py` (videos), `python3 tools/meta_ads_videos_manifest.py`, `python3 tools/meta_ads_review_page.py`. Local assets (real frames of Andrew, cutouts, customer frames) are under `/home/user/work/ma` on the worker box and are re-made from the Drive IDs in `docs/overnight/2026-11-07-brief.md`.

## The offer, as the ads say it
- **LP-A, One Feature:** "I sell ONE GHL feature for $99/month." One feature people already want (they type what they want, the software builds it), white-labelled, $99/mo per user. CTA = the free breakdown (VSL / YouTube, the same destination as the old B002/B003 ads).
- **LP-B, SaaSSuite:** onboarding, training videos, AI answers, support tickets with real humans, custom menu and dashboard. CTA = start free.

Claims used: only what is already in Andrew's approved ads or said on camera by customers. No income results, no "500 agencies", no "$150K agency" (not verified tonight).

## How to test (from the Meta playbook)
One concept = one new ABO ad set with its 4–5 variants, broad targeting, Highest Volume. Hands off for 72 h. Judge at 3–5× target cost per result on a 7-day view. Don't put the same ad in two campaigns. Suggested first wave: C01, C04, C05, C10, C12 statics + V13, V16, V01 videos. Then refill weekly with the next concepts.

## Concepts (16) and every static
| Concept | Angle | LP | Variants (hook) | 9:16 |
|---|---|---|---|---|
| C01 One feature, $99/mo | Outcome | A | a Direct claim · b Stop/start · c Reframe the want · d Three-beat promise | a, b |
| C02 Feature overload | Pain | A | a Callout + blame flip · b Demo length pain · c Less is more · d Hour-long explain | a |
| C03 You became the help desk | Pain (support) | B | a Identity flip · b Timestamp pain · c Keeping is the hard part · d Churn myth | a, b |
| C04 Customer quotes | Proof | B | a Rob "real humans" · b Brentney "now I can scale" · c Ben "always follows through" · d Rob "customize your dashboard" · e Jessica "on top of everything" | a, b, c |
| C05 Us vs them | Comparison | A | a All of GHL vs one feature · b $997 course vs system · c Agency vs SaaS · d Build vs resell AI | a |
| C06 The one-feature math | Math | A | a Scale ladder · b 20 gym owners · c Goal backsolve · d Per-user per-year | a |
| C07 SaaSSuite feature callouts | Feature | B | a After-signup checklist · b Hidden half · c Three verbs · d Division of labour | a |
| C08 Notes app | Native | A | a The method · b Client asks · c SaaS to-do (B) · d AI money ideas | a |
| C09 Tweet-style | Native | A | a Agents vs one · b Unpopular opinion · c Keeping clients (dark) · d The one that pays | a |
| C10 iMessage | Native | A | a Vibe coding · b Which one · c Midnight support (B) · d Show me | a |
| C11 Sticky note | Ugly / handwritten | A | a Stop all · b Already want (with Andrew) · c Churn = confusion · d 3 steps | a |
| C12 Founder photo | Andrew photo-led | A | a The one I'd sell · b Already want · c Which / who / what to charge · d I teach one thing | a, c |
| C13 Contrarian | Contrarian | A | a Don't learn to code · b No more agents · c Fewer features · d Boring wins | a |
| C14 Persona callout | Callout | A | a GHL affiliates · b Agency owners · c Coaches · d Web designers | a |
| C15 Search / forum | Native | A/B | a Google "make money with GHL" · b Reddit AMA by Andrew · c Google "support my clients" (B) · d Reddit PSA by Andrew | – |
| C16 Lists | Education | A/B | a 3 reasons affiliates stall · b 3-step method · c After a client signs (B) · d Retro error pop-up | b |

Search and Reddit mock-ups only show Andrew's own content and posts under his own name. No fake reviews, likes or upvote counts.

## Video ads (18)
| id | kind | length | hook | source | file |
|---|---|---|---|---|---|
| V01 | motion | 10.0 s | Text thread: vibe coding | static C10a animated | `render-drop/meta-ads:meta-ads/V01.mp4` |
| V02 | motion | 8.5 s | Text thread: which one? | static C10b animated | `render-drop/meta-ads:meta-ads/V02.mp4` |
| V03 | motion | 9.8 s | Text thread: midnight support | static C10c animated | `render-drop/meta-ads:meta-ads/V03.mp4` |
| V04 | motion | 9.0 s | Text thread: show me | static C10d animated | `render-drop/meta-ads:meta-ads/V04.mp4` |
| V05 | motion | 9.6 s | Notes: cross out, check off | static C08a animated | `render-drop/meta-ads:meta-ads/V05.mp4` |
| V06 | motion | 8.8 s | Receipt: the one-feature math | static C06a animated | `render-drop/meta-ads:meta-ads/V06.mp4` |
| V07 | motion | 9.4 s | Split: all of GHL vs one feature | static C05a animated | `render-drop/meta-ads:meta-ads/V07.mp4` |
| V08 | motion | 6.8 s | Sticky note drop: 3 steps | static C11d animated | `render-drop/meta-ads:meta-ads/V08.mp4` |
| V09 | motion | 6.6 s | Retro error pop-up | static C16d animated | `render-drop/meta-ads:meta-ads/V09.mp4` |
| V10 | motion | 6.8 s | Tweet card | static C09a animated | `render-drop/meta-ads:meta-ads/V10.mp4` |
| V11 | motion | 7.8 s | List: after the client signs | static C16c animated | `render-drop/meta-ads:meta-ads/V11.mp4` |
| V12 | motion | 8.2 s | Feature callouts on real UI | static C07a animated | `render-drop/meta-ads:meta-ads/V12.mp4` |
| V13 | footage | 13.5 s | Andrew VSL: greatest advancement + sell one feature | v1.mp4 0.0–5.3s + 35.7–41.8s | `render-drop/meta-ads:meta-ads/V13.mp4` |
| V14 | footage | 12.4 s | Andrew VSL: not emails, not agents | v1.mp4 5.3–15.5s | `render-drop/meta-ads:meta-ads/V14.mp4` |
| V15 | footage | 13.5 s | Andrew VSL: behind closed doors | v1.mp4 15.5–20.8s + 35.7–41.8s | `render-drop/meta-ads:meta-ads/V15.mp4` |
| V16 | footage | 15.0 s | Rob testimonial: real humans on support | rob.mp4 11.3–24.1s | `render-drop/meta-ads:meta-ads/V16.mp4` |
| V17 | footage | 13.7 s | Brentney testimonial: support was slowing growth | brentney.mp4 12.5–18.2s + 21.8–27.6s | `render-drop/meta-ads:meta-ads/V17.mp4` |
| V18 | footage | 14.1 s | Ben testimonial: agency builds HighLevel with Andrew | ben.mp4 0.0–11.9s | `render-drop/meta-ads:meta-ads/V18.mp4` |

Rules kept: no AI faces anywhere. Motion ads are UI/text only. Footage ads are 100% real (Andrew's VSL, customers' own testimonial videos). Captions are word-timed from Whisper transcripts and checked against the audio.

## Round 2 (testimonial ads) + launch plan
- **Launch plan:** `launch-plan.md`. It groups everything into test sets of 3–5 (wave 1 / wave 2 / backlog), with a budget split and what to test first.
- **20 statics** from exact customer quotes: `round2/statics/R2S01–R2S20.jpg`, copy in `round2/manifest.csv`. People: Rob, Brentney, Ben, Jessica Garcia (LP-B), Mark Cleary and Lee Knaz (LP-C, parked until Andrew gives a "work with Andrew" URL and OKs paid use).
- **15 videos** (12–26 s, 6× 4:5 + 9× 9:16). Each is a 1.8 s hook card in front of a finished testimonial ad from `render-drop/testimonials-a|b`. Files: `render-drop/meta-ads:meta-ads/round2/R2V01–R2V15.mp4`, copy in `round2/videos.csv`. Tania and Mason are not used.
- On the review page: the "Round 2" tab.

## Needs Andrew
1. Approve or kill by concept on the review page (one tap per card is enough; tell us the ids).
2. Confirm we may run Rob, Brentney, Ben and Jessica's words and faces in paid ads (they recorded testimonials; paid use should be OK'd).
3. Landing pages: LP-A = the current One Feature VSL. LP-B (SaaSSuite free account) needs a URL.
4. Higher-res photos: the Drive photo picks (stage, giant check) need a login to download, so tonight's ads use frames from the VSL shoot instead.
