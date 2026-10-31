-- Progetti degli utenti di ntcfem.
-- Ogni utente vede e modifica solo i propri progetti (Row Level Security).

create table if not exists public.progetti (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users (id) on delete cascade,
  nome        text not null check (char_length(nome) between 1 and 120),
  modello     jsonb not null,
  risultati   jsonb,
  creato      timestamptz not null default now(),
  aggiornato  timestamptz not null default now()
);

create index if not exists progetti_user_id_idx on public.progetti (user_id, aggiornato desc);

alter table public.progetti enable row level security;

create policy "progetti: lettura propri" on public.progetti
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "progetti: inserimento propri" on public.progetti
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "progetti: modifica propri" on public.progetti
  for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "progetti: eliminazione propri" on public.progetti
  for delete to authenticated using ((select auth.uid()) = user_id);

create or replace function public.progetti_aggiorna_data()
returns trigger language plpgsql set search_path = '' as $$
begin
  new.aggiornato := now();
  return new;
end;
$$;

create trigger progetti_aggiornato before update on public.progetti
  for each row execute function public.progetti_aggiorna_data();
