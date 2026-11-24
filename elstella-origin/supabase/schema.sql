-- ORIGIN ATLAS optional shared-workspace schema (Supabase/Postgres).
-- Run in the Supabase SQL editor only after creating a project.
-- Each authenticated account can read/write only its own workspace.
create table if not exists public.origin_workspaces (
  user_id uuid primary key references auth.users(id) on delete cascade,
  payload jsonb not null default '{"evidence":[],"hypotheses":[]}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.origin_workspaces enable row level security;
drop policy if exists "workspace_select_own" on public.origin_workspaces;
create policy "workspace_select_own" on public.origin_workspaces
  for select to authenticated using (auth.uid() = user_id);
drop policy if exists "workspace_insert_own" on public.origin_workspaces;
create policy "workspace_insert_own" on public.origin_workspaces
  for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists "workspace_update_own" on public.origin_workspaces;
create policy "workspace_update_own" on public.origin_workspaces
  for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- No anonymous access and no service-role key in the browser.
