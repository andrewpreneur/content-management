# AI content platforms: copy, build or buy (2026-11-04)

_For Andrew George's engine (100 posts/day by Jan 3, 1,000/day by Feb 2, real Andrew footage multiplied with AI, never 100% avatar videos). Builds on `research/ai-content/2026-11-04.md`. Tools and policy rules covered there are not repeated here._

**Method note:** WebSearch only. WebFetch and curl both failed (DNS or proxy 403) for `docs.higgsfield.ai`, `getripping.com` and `brodyautomates.com`, and `gh` is scoped to this repo. Everything below comes from search-engine summaries of those pages. Prices are from search snippets and third-party guides that often conflict, so treat them as **indicative**. **"Unverified"** means no primary source confirmed it.

---

## TL;DR

1. **Brody Automates:** I could **not** find a released AI-content software product. What I did find: Brody Glanville (@brodyautomates, ~178–179K IG followers, South Africa) co-founded **Merydian**, a venture studio whose first product is **FounderOS**, an open-source "business operating system" for one-person companies. Who founded FounderOS is disputed. **Andrew: send the link or product name you saw.**
2. **GetRipping = "Ripping"**, from Ben Zogby. It is a **Claude Code-based** short-form Instagram system for SaaS founders: hooks, scripts, calendar, analytics, carousels, plus coaching. The site lists **$19/mo Creator and $99/mo Growth** (7-day trial) and says it **requires Claude Code (Max recommended)**. Its architecture is close to ours. Copy the loop. Don't buy it.
3. **Buy:** a posting layer (**Blotato** or self-hosted **Postiz**) and **Higgsfield API** for generated openers and b-roll. **Build:** ideation, hooks, scripts, clip-mining and the analytics feedback loop as Claude skills. **Skip:** Arcads and HeyGen avatar video, because both break the "never 100% AI" rule. Use HeyGen only for lip-sync translation of real footage.
4. **Higgsfield API host:** `api.higgsfield.ai` (generation and status). Also allow `platform.higgsfield.ai` (seen in the status example on the auth page) and `cloud.higgsfield.ai` / `open.higgsfield.ai` (console, pricing). Auth header is `Authorization: Key <KEY_ID>:<KEY_SECRET>`. **The API is billed from a separate USD balance. Andrew's Ultra plan credits don't carry over.** Details at the end.

---

## 1. Brody Automates (Brody Glanville)

| Item | Finding | Status |
|---|---|---|
| Who | Brody Glanville, "AI Strategist & Content Creator", runs Exosoft, co-founder/CEO of **Merydian** ("venture studio that builds AI-native software companies") | Self-reported ([brodyautomates.com](https://brodyautomates.com/), [merydian.ai](https://www.merydian.ai/), [LinkedIn](https://www.linkedin.com/in/brody-glanville-2818481ba/)) |
| Product found | **FounderOS**: "open source business operating system you can run yourself or have hosted for you". The GitHub repo describes it as a single-operator command center that runs comms, funnel, social, finances and agents as AI departments | [GitHub Bennettxai/FounderOS](https://github.com/Bennettxai/FounderOS). **Conflict:** [Bennett Spooner](https://bennettspooner.com/) claims "Founder & CEO, FounderOS" |
| AI-content software release | **Not found.** His portfolio lists internal tools ("FounderOS access layer", "brand-deal autopilot"). His GitHub has repos such as `ad-engine` and `gamma-studio`, but none is described as a content product | **Unverified.** Need the link |
| Pricing / workflow / buyer | Unknown | Unverified |
| Audience | ~178–179K IG. Main audience reportedly on YouTube, most active on IG. Topics: AI automation, n8n, coding | [IG](https://www.instagram.com/brodyautomates/), [CreatorDB](https://creatordb.app/creatorstats/brodyautomates/), [oleg.ae](https://www.oleg.ae/creators/brodyautomates) |
| How he markets | "**Sauce**" is his signature word for the workflows, repos and templates he gives away to followers (comment-to-get style). Sells through Whop ([whop.com/@brodyautomates](https://whop.com/@brodyautomates/)) and Linkme | Third-party summary, unverified |
| Content volume | 106 Reels scraped by one tracker. No posts/day figure found | Unverified |

**Don't confuse him with:** **bradautomates** (a different creator who makes the Claude Code skills `claude-video` and `head-of-content`, an Apify-based viral-outlier research toolkit, [GitHub](https://github.com/bradautomates/head-of-content)), or Brody Niehoff ("DFY Content System w/ Voice & Avatar Clones").

**What to copy from Brody's playbook (even without the product):**
- "Give the sauce": every post offers a free repo/template/snapshot for a comment keyword. Andrew already has the GHL snapshot equivalent (`Comment SAAS`). Make it a standing CTA format.
- Build-in-public of the engine itself: "I built a system that posts 100×/day from one filming" is content for both IG accounts. It fits @aiandrewpreneurship especially well.
- **bradautomates/head-of-content** (viral-outlier research via Apify) is worth reading as a reference for our competitor-scrape skill once Apify is allowed.

---

## 2. GetRipping, product name "Ripping" ([getripping.com](https://www.getripping.com/))

| Item | Finding |
|---|---|
| Tagline | "Turn Instagram Into A Money Printer For Your SaaS." |
| Who's behind it | **Ben Zogby** (per site). Site claims "$8M+ revenue, bootstrapped, 2023 exit to private equity, 251K followers built", "helped 100+ solo founders break $10k/mo, 4 exits". **No independent source found. Self-reported.** |
| What it does | "Ideas, tools, analytics, and automations" for founders doing short-form. Modules: **hook generation, script writing, production, content calendar, analytics ("Full Analytics & Growth Panel"), carousels**. Finds winning videos, writes scripts, tracks results, and **analytics insights feed back into scripts and edits** |
| Claimed edge | Hooks "based on psychology and trained on 40M winners", "gets better with every run". Positions itself against plain Claude ("generic hooks may hit or miss") |
| Tech | **Requires Claude Code (Max recommended).** The Creator plan runs on *your* Claude usage. It is effectively a packaged Claude Code skill/plugin set plus a web panel (how it's built isn't stated) |
| Pricing | **Creator $19/mo** (shown as down from $39). **Growth $99/mo** (down from $199). 7-day free trial, cancel anytime. Growth's extras aren't clear beyond the analytics panel. Community/coaching (direct access to Ben, "first $100k scaling roadmap") is described as included |
| Who it's for | Solo SaaS founders/small teams using **Instagram as the main sales channel**. That is Andrew's exact niche (SaaSSuite), which also makes it a competitor for the SaaS-founder audience |
| How it's marketed | Founder-led: the founder's own IG results, revenue/exit claims, and a coaching community bundled with the software. Launch-discount anchor pricing |
| Independent reviews / press / launch date | **None found** |

**Takeaway:** Ripping validates our architecture: Claude Code + a hook library + a script engine + an analytics→prompt feedback loop, sold cheaply on top of the user's own Claude plan. We already have the parts (`content-engine/` hookpoint specs, 45 scripts, skills plan). Also note the business model: **SaaSSuite could ship the same thing for GHL/SaaS agency owners** (Andrew's audience), packaged as a Claude Code plugin plus a snapshot. Worth raising with Andrew as a product idea, not just a tool.

---

## 3. Comparable 2026 content systems

| Tool | Stage it covers | Price (indicative) | API? | Notes / sources |
|---|---|---|---|---|
| **Blotato** | Ideation-lite, AI visuals/video, **multi-platform posting** | Starter $29, Creator $97, Agency $499/mo | Yes, all paid plans (API + MCP + n8n/Make). Trial excludes API, and generating a key **ends the trial** | Credits only for AI image/video. Scheduling/publishing free. [pricing.md](https://www.blotato.com/pricing.md), [help](https://help.blotato.com/settings/billing-and-credits) |
| **Postiz** | Scheduling/posting, 24–30+ platforms | Self-host free (AGPL-3.0). Cloud $29 (5 ch) / $39 / $49 (30 ch) / $99 (100 ch) | Yes on all cloud tiers, plus MCP (vendor claim) | Self-host = you need your **own Meta/YouTube app approvals** (can take >1 month). Post caps conflict across sources. [Blotato on Postiz](https://www.blotato.com/blog/postiz-pricing), [socialync](https://www.socialync.io/compare/postiz) |
| **OpusClip** | Long→short clipping, reframe, captions, AI b-roll, virality score | Free 60 credits. Starter ~$15, Pro ~$29/mo (conflicting) | Business (custom). Some say limited on Pro. 10-credit min per API project | [ssemble](https://www.ssemble.com/blog/opus-clip-pricing-2026), [creatify](https://creatify.ai/blog/opusclip-pricing-plans-and-what-you-ll-actually-pay-in-2026) |
| **Submagic** | Captions, zooms, b-roll, Magic Clips | Starter $19, Pro $39, **Business + API $69**/member/mo | Business tier. API minutes ~100 included or add-on (conflicting) | [hooked.so](https://www.hooked.so/compare/submagic-pricing), [toolsurf](https://www.toolsurf.com/submagic-pricing-2026/) |
| **Captions (Mirage)** | AI Edit, captions, dubbing, b-roll, AI actors | App: $9.99–$24.99/mo entry (conflicting) | Yes: usage-based per input minute (captions). Mirage Video 1 in 6s increments | Company renamed to Mirage (Sep 2025), raised $75M (Mar 2026). [API pricing](https://www.captions.ai/help/docs/api/pricing), [eesel](https://www.eesel.ai/blog/captions-ai) |
| **HeyGen** | Avatars, **video translation with lip-sync** | API: pay-as-you-go USD wallet ($5 min). Avatar IV ~$0.05–0.067/s (~$3–4/min) | Yes | Translate-API price **unverified**. [nocode.mba](https://www.nocode.mba/articles/heygen-pricing), [HeyGen blog](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis) |
| **Arcads** | AI-actor UGC ads | ~$110/mo (10 videos), $220 (20). ~$11/video. No trial. No public pricing page | Unverified | 100% AI actors, so **off-limits** for organic. [eesel](https://eesel.ai/blog/arcads-ai-pricing), [fluxnote](https://fluxnote.io/guides/arcads-pricing-2026) |
| **Repurpose.io** | Trigger-based cross-posting | Conflicting: $25–35 entry, up to $179 Agency | Limited | Identical cross-posting is now a liability (IG originality rules). [socialrails](https://socialrails.com/blog/repurpose-io-pricing) |
| **Higgsfield** | Generated angles/openers/b-roll, Soul character images | API pay-per-second (see §5) | Yes | Our planned generator. See §5 |

---

## 4. Copy / build / buy (opinionated)

| Tool | Copy into our engine | Build ourselves | Buy? |
|---|---|---|---|
| **Ripping** | Hook library tagged by framework. "Find winners → script → track → feed back" loop. Analytics panel that writes *prompt context*, not just charts | All of it, as Claude skills over our Supabase `outputs` + metrics. We have Andrew's real scripts, which a generic 40M-hook model doesn't | **No.** At most one $19 month so we can study the UX (unverified that the trial needs a card) |
| **Brody / FounderOS** | "Sauce" comment-to-get CTA. Build-in-public posts about the engine | n/a | **No** (no content product confirmed) |
| **Blotato** | Drafts-first API flow (already in our plan) | Not worth building: platform API approvals are the hard part | **Yes, Starter $29 to start.** Gets us posting to IG/TikTok/YT/LinkedIn/Threads/X fast. Re-evaluate at 1,000/day (account count, rate limits) |
| **Postiz** | MCP posting from Claude | Self-host only if Blotato limits bite. Meta/YouTube app approval takes >1 month, so **start that application now** if we want an exit | **Backup.** Cloud Pro $49 (30 channels) is the cheapest scale path if Blotato's per-account limits fail |
| **OpusClip** | Active-speaker reframe, "ClipAnything" moment ranking idea | Clip-mining skill (transcript → ranked in/out points) + ffmpeg. Our sources are short vertical clips, so long→short matters less | **No.** Only useful if Andrew starts recording long-form/lives |
| **Submagic** | Caption styles, auto-zoom on keywords, b-roll inserts | Word-level captions (Whisper + ASS/ffmpeg) in `tools/variants.py`. That also gives the per-variant caption-style control the originality rules need | **Maybe, Business $69** as a stopgap for captions via API until our Whisper captioner ships. Drop it after |
| **Captions/Mirage** | AI Edit one-tap style | Same as Submagic | **No** (overlaps Submagic, AI-actor focus) |
| **HeyGen** | Lip-sync translation of **real** footage for language pages | Voice via ElevenLabs (already planned) | **Yes, API pay-as-you-go**, only for lip-sync translation on top performers. **Never** avatar-only posts |
| **Arcads** | Nothing for organic | n/a | **No.** Violates the no-100%-AI rule. Possibly SaaSSuite paid ads later, as Andrew's call |
| **Repurpose.io** | n/a | n/a | **No.** Identical cross-posts hurt reach under IG originality rules |
| **Higgsfield** | Camera-move presets as named "opening hook" templates | Prompt library + job runner calling the API directly | **Yes, API balance.** Separate from the Ultra plan |

**Net stack:** Claude skills (ideation, hooks, scripts, clip-mining, captions copy, analytics loop) → our renderer (`tools/variants.py` + Whisper captions) → Higgsfield API (openers/b-roll) + ElevenLabs/HeyGen (dubs) → Blotato drafts → Andrew approves → post. Optional Submagic for the first weeks.

---

## 5. Higgsfield API: facts for direct integration

> Sources: [API reference overview](https://docs.higgsfield.ai/docs/api-reference/overview), [Authentication](https://docs.higgsfield.ai/docs/authentication), [FAQ](https://docs.higgsfield.ai/docs/help/faq), [Get request status](https://docs.higgsfield.ai/docs/api-reference/requests/get-request-status), [Webhooks](https://docs.higgsfield.ai/docs/how-to/webhooks.md), [Changelog](https://docs.higgsfield.ai/docs/changelog), [Soul ID API](https://open.higgsfield.ai/models/soul-id/api-reference), [API pricing](https://open.higgsfield.ai/pricing), [Help center: what is the API](https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api), [Blog: API vs subscriptions](https://higgsfield.ai/blog/ai-video-api-pricing-vs-subscriptions), [Python SDK](https://github.com/higgsfield-ai/higgsfield-client), [CLI](https://github.com/higgsfield-ai/cli). All read through search summaries. **docs.higgsfield.ai was not directly fetchable.**

### Hosts to allow in network settings
| Host | Purpose | Confidence |
|---|---|---|
| **`api.higgsfield.ai`** | Base URL for model calls, request status, Soul ID (`/v1/custom-references`) | **High** (API reference + FAQ + Soul ID docs) |
| `platform.higgsfield.ai` | Appears in the auth page's curl example: `https://platform.higgsfield.ai/requests/{REQUEST_ID}/status` | Medium. Allow it to be safe |
| `docs.higgsfield.ai` | Docs + per-model JSON schemas (so agents can read them) | High |
| `cloud.higgsfield.ai` | Console where keys are created (per official auth page) | Medium. Sources also name `console.higgsfield.ai` and `open.higgsfield.ai` |
| `open.higgsfield.ai` | API pricing / model pages | High |
| CDN for result files | Output URLs host. **Unknown**, so check the first response and allow that host | Unverified |

### Getting a key (exact steps for Andrew)
1. Go to **cloud.higgsfield.ai** (if it doesn't load, try **console.higgsfield.ai** or **open.higgsfield.ai**) and sign in with his Higgsfield account.
2. **Billing:** add a payment method and **top up the USD API balance**. This is a separate balance. **Ultra-plan credits can't be used by the API, and the two can't be transferred either way.**
3. **API keys → Create new key** (server-side credential). You get a **Key ID** and a **Key Secret**. **The secret is shown only once.**
4. Add both as environment secrets (suggest `HIGGSFIELD_KEY_ID` and `HIGGSFIELD_KEY_SECRET`, or a single `HIGGSFIELD_API_KEY="<id>:<secret>"`). Never put them in client/browser code. Rotate if exposed.

### Auth
```
Authorization: Key <KEY_ID>:<KEY_SECRET>
```
- **Not** `Bearer`.
- Legacy headers `hf-api-key` + `hf-secret` still accepted. Don't use them for new code.

### Request lifecycle
- `POST https://api.higgsfield.ai/<model-endpoint-id>` with a JSON body → returns `request_id`, `status_url`, `cancel_url`.
- Poll `status_url` until `completed` / `failed` / `nsfw`, **or** add `?hf_webhook=<our URL>` to get a POST at the final status.
- Cancel works only while **queued**.
- **Failed/moderated requests are not charged.** Reserved amounts are refunded.
- Soul ID (character reference): `POST /v1/custom-references`, poll until `completed`, then pass its UUID in Soul text-to-image requests. Since **Oct 23, 2026** it returns **429 + Retry-After** when too many references are training.

### Models via API (confirmed names; slugs partly unverified)
| Model | Endpoint id / slug | Status |
|---|---|---|
| **Kling 3.0** Standard text→video / image→video | `kling-video/v3.0/std/text-to-video`, `kling-video/v3.0/std/image-to-video` | Docs pages exist |
| Kling 3.0 Pro text→video | `kling-video/v3.0/pro/text-to-video` | Seen in a docs mirror |
| Kling 2.5 / 2.6 / 4.0 | Listed on pricing page | Slugs unverified |
| **Wan** 3.0 / 3.0 Prime | Listed on pricing page | Slugs unverified |
| **Seedance 2.0** (t2v, i2v, reference-to-video) | CLI id `seedance_2_0` | API slug unverified |
| **Soul** (Standard / Soul 2 / Soul Cinema) text→image, **Soul ID** character refs | `higgsfield-ai/soul/v2/standard` (third-party), docs page "SOUL — Text to image" | Soul ID API confirmed. Slug unverified |
| DoP, Marketing Studio Image (Higgsfield own) | Listed | Slugs unverified |
| MiniMax, LTX, PixVerse, Recraft, Ideogram, Grok families | Listed ("50+ models") | Slugs unverified |
| **Veo 3.1** | CLI id `veo3_1` exists | **No API price or endpoint found. Treat as not on API until confirmed** |

### API pricing vs credits
| Model | API price (from open.higgsfield.ai/pricing via search) |
|---|---|
| Soul 2 / Soul Cinema image | **$0.0032 / image** |
| Kling 3.0 (720p) | **from $0.084 / s** (one third-party says $0.112/s) |
| Kling 2.5 / 2.6 / 4.0 | from $0.042 / $0.070 / $0.094 per s |
| Wan 3.0 / Wan 3.0 Prime | from $0.050 / $0.068 per s (one third-party says $0.20/s) |
| Seedance 2.0 t2v/i2v | ~$0.099 / s (list $0.141). Reference-to-video $0.118 / s |
| Veo 3.1 | Not found |

- **Rough cost per opener:** a 5s Kling 3.0 720p clip ≈ **$0.42**. 100 openers/day ≈ **$42/day ≈ $1,260/mo** (arithmetic on the list price above. Verify the live price first).
- **Web credits for comparison** (Andrew's subscription, not usable by the API): ~10 credits per 5s Kling 3.0 720p clip, ~80 credits per 8s Veo 3.1 1080p clip. Plans: Starter $19 (270 cr), Plus $47 annual (1,200), Ultra $99 annual (3,000) ([Krea](https://www.krea.ai/blog/higgsfield-pricing-explained-2026-unlimited-credits-and-real-monthly-costs), [wireflow](https://www.wireflow.ai/blog/higgsfield-ai-pricing)). Andrew had ~221 credits on Nov 4 (STATUS.md).
- **Implication:** for occasional hero openers, Andrew's web credits are cheaper per clip. For 100+ automated generations/day, the API is the only route, and it bills separately.

### Open items to verify once `docs.higgsfield.ai` is allowed
- Exact Soul / Seedance / Wan / Veo endpoint slugs (read `docs.higgsfield.ai/llms.txt`).
- Which status host is canonical (`api.` vs `platform.`).
- Result-file CDN host for the allowlist.
- Rate limits / concurrency per account.
