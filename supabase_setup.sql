-- UNIVERSE AI STUDIO Supabase schema
-- Review against your existing production schema before applying.

create table if not exists public.ai_memory (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  project_name text not null default 'My First Film',
  memory_type text not null,
  title text not null,
  content jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists ai_memory_user_project_created_idx
  on public.ai_memory (user_id, project_name, created_at desc);

alter table public.ai_memory enable row level security;
drop policy if exists "Users manage their own AI memories" on public.ai_memory;
create policy "Users manage their own AI memories"
  on public.ai_memory for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create table if not exists public.studio_assets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  project_name text not null default 'My First Film',
  bucket_id text not null default 'studio-assets',
  file_path text not null,
  file_name text not null,
  file_type text not null default 'other',
  mime_type text not null default 'application/octet-stream',
  size_bytes bigint not null default 0,
  created_at timestamptz not null default now()
);

create index if not exists studio_assets_user_project_created_idx
  on public.studio_assets (user_id, project_name, created_at desc);

alter table public.studio_assets enable row level security;
drop policy if exists "Users manage their own studio asset records" on public.studio_assets;
create policy "Users manage their own studio asset records"
  on public.studio_assets for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

insert into storage.buckets (id, name, public, file_size_limit)
values ('studio-assets', 'studio-assets', false, 52428800)
on conflict (id) do update
set public = false, file_size_limit = 52428800;

drop policy if exists "Users read their own studio assets" on storage.objects;
create policy "Users read their own studio assets"
  on storage.objects for select
  using (
    bucket_id = 'studio-assets'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

drop policy if exists "Users upload their own studio assets" on storage.objects;
create policy "Users upload their own studio assets"
  on storage.objects for insert
  with check (
    bucket_id = 'studio-assets'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

drop policy if exists "Users delete their own studio assets" on storage.objects;
create policy "Users delete their own studio assets"
  on storage.objects for delete
  using (
    bucket_id = 'studio-assets'
    and (storage.foldername(name))[1] = auth.uid()::text
  );
