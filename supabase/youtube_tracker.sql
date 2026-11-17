-- YouTube upload tracker (for the Lovable-hosted Content HQ). Mirrors tracker/*.json in the repo.
-- drive_videos: every finished edit in the Drive V+S folders.  youtube_videos: every video on our channels.
-- upload_status: the answer per Drive video (auto match, AI review or a manual mark, manual wins).
create table if not exists drive_videos (
  drive_id text primary key, name text not null, folder_label text, subpath text, duration_s numeric,
  created timestamptz, url text, seen_at timestamptz default now()
);
create table if not exists youtube_videos (
  id text primary key, channel text not null, tab text, title text, duration_s numeric, url text, seen_at timestamptz default now()
);
create table if not exists upload_status (
  drive_id text primary key references drive_videos(drive_id) on delete cascade,
  status text not null check (status in ('posted','not_posted','check','skip')),
  source text not null check (source in ('auto','ai','manual')),
  youtube_id text references youtube_videos(id), score int, reason text,
  marked_by text, updated_at timestamptz default now()
);
create index if not exists upload_status_status on upload_status(status);
alter table drive_videos enable row level security; alter table youtube_videos enable row level security; alter table upload_status enable row level security;
-- Signed-in team members can read everything and set manual marks; the scanner writes with the service role.
create policy "team read drive" on drive_videos for select to authenticated using (true);
create policy "team read yt" on youtube_videos for select to authenticated using (true);
create policy "team read status" on upload_status for select to authenticated using (true);
create policy "team mark" on upload_status for update to authenticated using (true) with check (source = 'manual');
create policy "team insert mark" on upload_status for insert to authenticated with check (source = 'manual');
