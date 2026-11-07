# Meta ad batch · Nov 7, 2026

**Review page:** __REVIEW_URL__

Drafts only. Nothing is uploaded to Meta or posted anywhere.

## What's here
| What | Count | Where |
|---|---|---|
| Static ads, 4:5 (1080×1350) | 65 | `statics/<id>.jpg` |
| Same statics in 9:16 (1080×1920, Reels/Stories safe zones kept) | 20 | `statics/<id>_916.jpg` |
| Video ads, 4:5, 6.6–15.6 s | 18 | branch `render-drop/meta-ads` → `meta-ads/<id>.mp4` (previews on the review page) |
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
__VIDEO_ROWS__

Rules kept: no AI faces anywhere. Motion ads are UI/text only. Footage ads are 100% real (Andrew's VSL, customers' own testimonial videos). Captions are word-timed from Whisper transcripts and checked against the audio.

## Needs Andrew
1. Approve or kill by concept on the review page (one tap per card is enough; tell us the ids).
2. Confirm we may run Rob, Brentney, Ben and Jessica's words and faces in paid ads (they recorded testimonials; paid use should be OK'd).
3. Landing pages: LP-A = the current One Feature VSL. LP-B (SaaSSuite free account) needs a URL.
4. Higher-res photos: the Drive photo picks (stage, giant check) need a login to download, so tonight's ads use frames from the VSL shoot instead.
