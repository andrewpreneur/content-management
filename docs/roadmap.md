# Roadmap — 30 / 60 / 90 days (started Nov 4, 2026)

## Days 1–30 (to Dec 4): build the multiplier, prove it on real content
- [x] Import Cristian's content hub (45 scripts, formats, hookpoint specs) into `content-engine/`
- [x] Pages registry, connections plan, infra plan, AI rules, multiplier spec
- [ ] Andrew: allow network hosts + add API secrets (Apify, Supabase, YouTube) — see `connections.md`
- [ ] Supabase project + `supabase/schema.sql` applied
- [ ] Apify daily scrape: own pages + top 20 competitors → Supabase
- [ ] Drive `_ENGINE` folders + upload watcher
- [ ] Render worker v1 (FFmpeg): 6 reel variants from one master
- [ ] Brand kit + editing style doc in Second Brain (fill TBD colors/fonts)
- [ ] First filming list run end to end: 5 clips → 100 outputs → Andrew approves
- [ ] Connect pages in GHL Social Planner; first scheduled posts
- [ ] Higgsfield + ElevenLabs connected; Andrew character sheet + voice clone tested
- [ ] Half-screen long-form template v1
- **Exit:** 20+ posts/day sustained for 7 days.

## Days 31–60 (to Jan 3): 100 posts/day
- Weekly 2-hour filming session (25 clips) from the auto-generated filming list
- Spanish page live (IG, TikTok, YT, FB); Portuguese page next
- Create X, Substack, podcast feed
- Review app in Lovable (approve on phone); GHL SMS when drafts are ready
- Weekly report: what won, what to film next, competitor angles
- **Exit:** 100 posts/day across ≥25 accounts for 7 days.

## Days 61–90 (to Feb 2): 1,000 posts/day
- 8–12 language/niche pages × 7 platforms
- Sampled review (Andrew/editor reviews 10%; rules engine checks the rest)
- Auto-kill underperformers after 48h, auto-remix winners
- **Exit:** 1,000 posts/day capacity, with platform rate limits and account-health checks.

## Risks
- Platform spam/duplicate detection → variant rules in `multiplier.md`, account warm-up for new pages.
- GHL Social Planner rate limits per account → may need a second posting provider at 1,000/day.
- Approval bottleneck → move to sampled review by day 60.
