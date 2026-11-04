-- Content engine schema (Supabase / Postgres). Apply in Supabase SQL editor.

create table if not exists pages (
  id uuid primary key default gen_random_uuid(),
  brand text not null,                 -- andrewpreneurship, aiandrewpreneurship, realandrewgeorge, ...
  platform text not null,              -- instagram, facebook, youtube, youtube_shorts, linkedin, tiktok, threads, x, substack, beehiiv, podcast
  handle text,
  language text not null default 'en',
  exists_live boolean not null default false,
  ghl_account_id text,                 -- GHL Social Planner account id once connected
  created_at timestamptz not null default now(),
  unique (platform, handle)
);

create table if not exists competitors (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  platform text not null,
  handle text not null,
  niche text,
  priority int default 3,
  notes text,
  unique (platform, handle)
);

-- Every post we scrape: ours (page_id) or a competitor's (competitor_id)
create table if not exists posts (
  id uuid primary key default gen_random_uuid(),
  page_id uuid references pages(id),
  competitor_id uuid references competitors(id),
  platform text not null,
  external_id text not null,
  url text,
  posted_at timestamptz,
  format text,                         -- reel, carousel, image, long_video, short, text
  caption text,
  hook text,                           -- first line / first 3s transcript
  transcript text,
  duration_s numeric,
  thumbnail_url text,
  raw jsonb,
  unique (platform, external_id)
);

create table if not exists post_metrics (
  post_id uuid references posts(id) on delete cascade,
  captured_at timestamptz not null default now(),
  views bigint, likes bigint, comments bigint, shares bigint, saves bigint, reach bigint,
  primary key (post_id, captured_at)
);

create table if not exists scripts (
  id uuid primary key default gen_random_uuid(),
  source text default 'content-hub',
  batch text, reel_number int,
  title text not null, format text, hook text, full_script text,
  camera text, cta text, editor_notes text, reference_clip text,
  status text not null default 'idea'   -- idea, on_film_list, filmed, editing, done
);

-- Raw footage and finished files (Drive or R2)
create table if not exists assets (
  id uuid primary key default gen_random_uuid(),
  script_id uuid references scripts(id),
  kind text not null,                  -- raw_clip, screen_rec, audio, render, image, thumbnail
  storage text not null default 'drive',
  path text not null,                  -- Drive file id or R2 key
  duration_s numeric,
  transcript text,
  created_at timestamptz not null default now()
);

-- Every piece of content the multiplier produces
create table if not exists outputs (
  id uuid primary key default gen_random_uuid(),
  script_id uuid references scripts(id),
  parent_output_id uuid references outputs(id),   -- variant of which master
  page_id uuid references pages(id),
  output_type text not null,           -- reel, reel_variant, carousel, linkedin_post, threads_post, email, podcast, long_video, substack, translation
  variant_changes text[],              -- e.g. {speed+0.1, mirror, hook_text}
  language text not null default 'en',
  caption text,
  asset_id uuid references assets(id),
  status text not null default 'draft', -- draft, review, approved, rejected, scheduled, posted
  review_notes text,
  scheduled_for timestamptz,
  ghl_post_id text,
  posted_post_id uuid references posts(id),
  created_at timestamptz not null default now()
);

create index if not exists outputs_status_idx on outputs(status);
create index if not exists posts_posted_at_idx on posts(posted_at desc);
