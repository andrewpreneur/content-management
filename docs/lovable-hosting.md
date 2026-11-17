# Hosting the content system on Lovable

Goal: Content HQ (post queue, approvals, YouTube upload tracker, library) as a real web app on Lovable, with Supabase
for data, built from a GitHub repo we can also edit from Claude Code.

## How Lovable and GitHub connect (important)
Lovable can't take over an existing repo. It creates its own repo and keeps it in two-way sync: edits in Lovable push
to GitHub, and commits pushed to GitHub show up in Lovable. So the setup is: Lovable makes the repo, then we push our code into it.

## Andrew's steps (about 5 minutes)
1. Go to https://lovable.dev → **New project**. Type: `Content HQ for Andrewpreneurship`. Let it make the starter app.
2. In the project, click **GitHub** (top right) → **Connect to GitHub** → pick the `andrewpreneur` account → **Create repository**. Name it `content-hq`.
3. In the project, open **Supabase** (or Lovable Cloud) → connect your existing Supabase project, or let Lovable create one.
4. Tell Claude "content-hq repo is ready".

## What we do next
- Push the Content HQ app into `andrewpreneur/content-hq` (React + Vite + Tailwind, the stack Lovable uses).
- Run `supabase/youtube_tracker.sql` (and the queue tables) in that Supabase project.
- The scanner (`tools/yt_tracker.py`) and the posting agent write to Supabase instead of JSON files. Manual marks are made in the app.
- Publish from Lovable (**Publish** button), optionally on a domain like `hq.andrewpreneurship.com`.

Until then, the live page is Content HQ (Claude artifact) → **YouTube uploads** tab.
