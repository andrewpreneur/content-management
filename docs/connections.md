# Connections — how we read and post to every platform

Principle: **one posting layer, one scraping layer, one database.**
- **Post + own-page stats:** GoHighLevel Social Planner (API is available through the HighLevel MCP: `create-post`, `get-posts`, `get-statistics`). Supports Facebook, Instagram, LinkedIn, TikTok, YouTube, Threads, Pinterest, Google Business. Andrew already pays for it and owns the HighLevel relationship.
- **Scrape (own pages deep data + competitors):** Apify actors, scheduled daily, writing into Supabase.
- **Database:** Supabase (`supabase/schema.sql`).

## Per platform

| Platform | Our page | Live updates (own) | Competitor scraping | Posting | Notes |
|---|---|---|---|---|---|
| Instagram | @andrewpreneurship, @aiandrewpreneurship | GHL Social Planner stats + Apify `apify/instagram-scraper` daily (per-post views, likes, comments, captions) | `apify/instagram-scraper`, `apify/instagram-reel-scraper` | GHL Social Planner | Official Graph API gives deeper insights (saves, shares, reach); add later via Meta app if needed |
| Facebook | andrewpreneurship | GHL stats + Apify `apify/facebook-posts-scraper` | same | GHL | |
| YouTube (long + Shorts) | @andrewpreneurship | **YouTube Data API v3** (free, official) for views/likes/comments; Apify `streamers/youtube-scraper` as backup | YouTube Data API (search + channel uploads) | GHL (or YouTube API direct for long-form with chapters/thumbnails) | Needs a Google Cloud API key |
| YouTube Shorts | same | same | `streamers/youtube-shorts-scraper` | GHL | |
| LinkedIn | realandrewgeorge | Apify LinkedIn profile-posts actor (personal profiles have no public analytics API) | same actor | GHL | Personal profile posting via GHL is supported |
| TikTok | TBD handle | Apify `clockworks/tiktok-scraper` | same | GHL (TikTok or TikTok Business) | |
| Threads | @andrewpreneurship | Apify Threads scraper | same | GHL | |
| X / Twitter | create | Apify tweet scraper | Apify tweet scraper | GHL does not post to X → use Blotato/Ayrshare or X API ($) | Decide when page exists |
| Substack | create | RSS feed (free) | RSS | Manual paste or email-to-post | No public posting API |
| beehiiv | create (optional) | beehiiv API | — | beehiiv API | Consider GHL email instead; one less tool |
| Podcast | create | Spotify/Apple via RSS host (e.g. Transistor API) | Apify podcast scrapers | Host API | Audio from every filming session |

## "Live" in practice
- Daily 6 AM CT pull of all own pages + competitor list (Apify schedules → webhook → Supabase).
- Hourly pull of posts < 48h old, so we can kill/boost fast.
- Weekly roll-up: top 10 posts per platform, which hooks/formats won → `research/` + Second Brain.

## What Andrew needs to do (one-time)
1. Apify: create an API token (Apify Console → Settings → Integrations → API token) and add it to this cloud environment as a secret named `APIFY_TOKEN`.
2. HighLevel: in the sub-account used for social, connect each page in **Marketing → Social Planner** (IG, FB, YouTube, LinkedIn, TikTok, Threads). Tell us which sub-account.
3. Google Cloud: YouTube Data API key → secret `YOUTUBE_API_KEY`.
4. Supabase: new project `content-engine` (or reuse one) → secrets `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.
5. Network: allow these hosts in the cloud environment settings: `api.apify.com`, `*.supabase.co`, `www.googleapis.com`, `api.elevenlabs.io`, Higgsfield's API host, `13cristianaguilar-bot.github.io`.
