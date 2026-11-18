# Your Content System (Lovable + Supabase)

- **App**: Lovable project, repo `andrewpreneur/content-hq` (front end), published by `.github/workflows/lovable-publish.yml`.
- **Supabase**: project `rchfmtgkfnnyzpbmyxrm` (YourContentSystem). Sign-in (Supabase Auth), all data (locked tables, read
  only through the `api` Edge Function), Storage bucket `library` (style clips and samples), pg_cron (poster every 5 min,
  scheduler every 30, Drive check). Backend code: `content-hq/backend/supabase/`. The Supabase token for
  api.supabase.com is proxy-injected in the cloud environment.
- Moved off Convex on Nov 18, 2026 (all data copied; the Convex project `harmless-ibis-268` can be deleted).

## Feed it from this repo
`python3 tools/ycs_sync.py all` (brand `$YCS_BRAND`, default `andrewpreneurship`):
1. pull: Andrew's approvals → `posting/state.json`, manual YouTube marks → `tracker/marks.json`, brand styles →
   `docs/brand-video/brand-styles.json`.
2. rebuild the YouTube tracker, export (`tools/export_convex.py` builds the rows; the name is historical) and push every
   table through the `ingest` function. Approvals, slots, post runs, notes and connections are never touched.
Engine key: `$YCS_INGEST_KEY`, else read once from the project's Vault and cached in `~/.ycs_ingest_key`.
Style system: `python3 tools/export_styles.py --clips DIR --samples DIR`.
