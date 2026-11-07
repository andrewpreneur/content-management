# Launch plan: Meta ad test sets (Nov 7, 2026)

Everything here is a draft. Nothing launches until Andrew approves, and nothing has been uploaded to Meta.
Creative ids refer to `manifest.csv` / `videos.csv` (round 1) and `round2/manifest.csv` / `round2/videos.csv` (round 2). All of them are on the review page.

## The rules we follow (from the Meta playbook)
- **One test set = one new ABO ad set** with 3–5 creatives that share one idea. Broad targeting, Advantage+ creative extras off, Highest Volume bidding.
- **Budget each ad set for 1–2 conversions a day** at the target cost. Formula: daily budget = 1–2 × target cost per result.
- **Hands off for 72 hours.** Judge on a 7-day view after 3–5 × target cost per result has been spent. Fast kill: 2–3 × target cost with zero results.
- **Never edit a winner.** Leave it running and scale it in place (+20–30% every 3–5 days, or one bigger bump when stable 5–7 days). Put new ideas in new ad sets.
- **Don't run the same ad (post ID) in two campaigns.**
- **Optimize on the deepest event that gets about 1–2 a day per ad set** (free account signup for LP-B, VSL lead/registration for LP-A). Send activation and paid events back with CAPI so Meta learns who buys.
- Budget lens once winners exist: **70%** proven winners, **20%** new versions of winners, **10%** wild tests.

## Budget split (example; Andrew sets the real target)
We don't know the target cost per result yet. Example at **$30 per free signup / VSL lead**:

| Wave | Ad sets | Per ad set / day | Total / day | Runs |
|---|---|---|---|---|
| Wave 1 | 5 | $30–60 | $150–300 | days 1–7 |
| Wave 2 | 6 | $30–60 | $180–360 | days 8–14 (winners from wave 1 keep running) |
| Wave 3 | backlog | refill 5+ new ads a week | | weekly |

If the real target is different, scale every number by (real target ÷ $30). If the budget is smaller, run fewer sets at full budget rather than all sets underfunded.

## Wave 1: test first (proof + the clearest offer)
Why these: the old creatives had zero proof, so proof is the biggest gap. The One Feature line is the one message Andrew already approved. Each set is a different idea, so Meta treats them as genuinely different (Andromeda rewards that).

| Set | Idea | Creatives (3–5) | LP | Why |
|---|---|---|---|---|
| W1-1 | Customer quote cards | C04a, C04b, C04c, C04d, C04e | B | Real words on a clean card: the cheapest proof test |
| W1-2 | Testimonial videos: support | V16, V17, R2V01, R2V04, R2V05 | B | Video gets weighted delivery; Rob and Brentney name the exact pain SaaSSuite fixes |
| W1-3 | One feature, $99/mo | C01a, C01b, C01c, C01d | A | The approved message in the approved look, now with the real Andrew |
| W1-4 | Andrew on camera (VSL cuts) | V13, V14, V15, C12a, C12c | A | Founder-led video plus the same promise as the VSL (message match) |
| W1-5 | Native text thread | V01, V02, V04, C10a | A | The B002 SMS format Andrew already approved, rebuilt |

## Wave 2: after wave 1 has a 7-day read
| Set | Idea | Creatives | LP |
|---|---|---|---|
| W2-1 | You became the help desk (pain) | C03a, C03b, C03c, C03d | B |
| W2-2 | Brentney before/after | R2S01, R2S09, R2S10, R2S11, R2S12 | B |
| W2-3 | Us vs them | C05a, C05b, C05c, C05d, V07 | A |
| W2-4 | The one-feature math | C06a, C06b, C06c, C06d, V06 | A |
| W2-5 | Ben, agency owner: trust | R2S13, R2S14, R2S15, R2V09, R2V12 | B |
| W2-6 | Feature overload (pain) | C02a, C02b, C02c, C02d, V09 | A |

## Wave 3 backlog (refill weekly, 5+ new ads a week)
| Set | Creatives | LP |
|---|---|---|
| SaaSSuite features | C07a, C07b, C07c, C07d, V11, V12 | B |
| Rob: what SaaSSuite does | R2S02, R2S05, R2S06, R2V02, R2V03 | B |
| Multi-customer + agency | R2S07, R2S08, R2V07, R2V08, R2V10 | B |
| Short trust clips | R2S03, R2S04, R2V06, R2V11 | B |
| Notes app | C08a, C08b, C08c, C08d, V05 | A |
| Tweet-style | C09a, C09b, C09c, C09d, V10 | A |
| Sticky notes | C11a, C11b, C11c, C11d, V08 | A |
| Contrarian | C13a, C13b, C13c, C13d | A |
| Persona callouts | C14a, C14b, C14c, C14d | A |
| Search / Reddit native | C15a, C15b, C15c, C15d | A/B |
| Lists | C16a, C16b, C16c, C16d | A/B |
| **Blocked:** Andrew 1:1 clients | R2S16–R2S20, R2V13, R2V14, R2V15 | C (needs URL) |

## Blockers (Andrew)
1. **Target cost per result and daily budget.** Every number above is an example.
2. **LP-B URL** (SaaSSuite free account) and **LP-C URL** (work with Andrew 1:1). LP-C ads stay parked until there is a page.
3. **Consent for paid use:** Rob, Brentney, Ben, Jessica (wave 1–2), Mark and Lee (LP-C). Tania and Mason are not used at all.
4. **Ben's real name/business.** The testimonials-b worker calls him "Agency owner"; testimonials-a and our ads say "Ben" from the file name. Confirm.
5. **Mark's "5 online clients" is an individual result** from Andrew's 1:1 help, not SaaSSuite. It runs only on LP-C, labelled "Individual result".

## Tracking check before spend
Pixel + CAPI both firing with deduplication; fbclid/fbp/fbc saved at signup into Supabase; signup → activated → paid events sent back to Meta. If any of that is missing, fix it first: scaling on broken signal teaches Meta the wrong buyers.
