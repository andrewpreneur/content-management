# Content engine → software: Your Content System (Lovable + Convex)

**Status Nov 17: built.** Convex replaced Supabase (Andrew). See `docs/lovable-hosting.md`. The Supabase notes below are kept for reference only.

Andrew (Nov 17): "this whole git and all the artifacts we're going to turn into a software. When ready I'll make the
Lovable project and we copy the git over." This doc is the build plan. Hosting steps: `docs/lovable-hosting.md`.

## The app (one login, one sidebar)
| Page | Replaces | Data |
|---|---|---|
| **Post queue + approvals** | Content HQ queue tab | `plan_items`, `approvals` (from `outputs/planner/plan.json`, `posting/state.json`) |
| **Calendar** | old planner artifact | `plan_items` by date/platform |
| **Library (everything we've posted)** | nothing yet | `posts` (YouTube, TikTok, Instagram…: title, length, date, views, thumbnail) from `tools/social_scrape.py` |
| **YouTube uploads** | Content HQ YouTube tab | `drive_videos`, `youtube_videos`, `upload_status` (`supabase/youtube_tracker.sql`, `tools/yt_tracker.py`) |
| **Review rooms** | ~15 review artifacts (VSLs, ads, reels, carousels, testimonials) | `assets` (Drive links + thumbs), `approvals` |
| **Filming list** | `todo/` | `filming_tasks` |
| **Brand + rules** | `docs/brand.md`, video rules | markdown pages |

## Data model (Supabase)
Existing `supabase/schema.sql` (pages, scripts, assets, outputs, posts) + `supabase/youtube_tracker.sql`. Add:
`accounts` (platform, handle, method), `plan_items` (date, time, kind, platforms, caption per platform, drive link, thumb, status),
`approvals` (item, status, note, by, at), `filming_tasks`. Thumbnails → Supabase Storage bucket `thumbs/<platform>/<id>.jpg`.

## Who writes what
- **Agents (scheduled Claude sessions)** keep doing the work: scrape channels, list Drive, match uploads, make content, schedule posts.
  They write to Supabase with the service-role key (saved as a secret on the cloud environment, never in git).
- **The app** is for Andrew and the team: approve, mark uploaded, see the calendar and library. Writes go through Supabase RLS.

## Migration (once the Lovable repo exists)
1. Push the app code (React + Vite + Tailwind + shadcn, the Lovable stack; components from `andrewpreneur/andrews-components`).
2. Run the SQL files in the Lovable-connected Supabase.
3. `tools/seed_supabase.py` (to write) loads plan.json, state.json, library/posts.json (+ thumbs), tracker/*.json.
4. Point the scheduled tasks at Supabase instead of JSON files; keep JSON exports in git as a backup.
5. Content HQ artifact stays live until the app is approved, then links to the app.

## Ready now (data the app will load)
- `library/posts.json` + `library/thumbs/` (all-platform post library)
- `tracker/*.json` (V+S inventory, channel, AI review, marks, final answer)
- `outputs/planner/plan.json` + `posting/state.json` (queue + approvals)
