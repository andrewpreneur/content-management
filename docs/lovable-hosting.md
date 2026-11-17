# Your Content System (Lovable + Convex)

Live app: the Lovable project connected to **andrewpreneur/content-hq** (publish it from Lovable → Publish).
- **Google Drive**: every file (footage, V+S edits, renders). Nothing gets deleted unless it's saved here or in GitHub.
- **GitHub**: this repo (the engine: rules, scripts, scrapers, agents), andrews-components, and content-hq (the app).
- **Convex**: live data. Deployment `harmless-ibis-268` (team token saved as a network secret for api.convex.dev on the CONTENT cloud environment).
- **Lovable**: hosts the front end; edits in Lovable sync to content-hq and back.

Pages: Dashboard, Post queue (approve/change/skip), Calendar, YouTube uploads (V+S tracker), Library (everything posted), Collections, How it works.
Writes need the team passcode (Convex env TEAM_PASSCODE; Andrew has it).

## Agent loop
1. Refresh data here: `tools/yt_tracker.py scan|match`, `tools/social_scrape.py scrape`, planner/posting tools.
2. Export: `python3 tools/export_convex.py /tmp/ycs_export`.
3. In content-hq: `CONVEX_DEPLOY_KEY=$(cat ~/.convex_deploy_key) bash scripts/import-from-repo.sh /tmp/ycs_export`
   (no deploy key in a new session? create one: `POST https://api.convex.dev/v1/deployments/harmless-ibis-268/create_deploy_key` with the proxy-injected team token, save to ~/.convex_deploy_key, never print or commit it).
4. Read Andrew's taps back: `npx convex run queue:allApprovals` → posting/state.json; `npx convex run youtube:manualMarks` → tracker/marks.json (before step 3, so marks survive the import).
