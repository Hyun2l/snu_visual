-- 막차 대합실 채팅 (Supabase)
-- Supabase 대시보드 → SQL Editor 에 통째로 붙여 넣고 Run.
-- 여러 번 실행해도 되게 만들었다.
--
-- 입장 방식: 익명 로그인 + 입장 코드.
--   이메일을 모으지 않는다 (공개 저장소라 명단이 새어 나갈 일이 없다).
--   입장 코드는 DB에만 있다. 코드를 아는 사람만 읽고 쓸 수 있다.

-- ── 설정값 (입장 코드) ─────────────────────────────
create table if not exists public.settings (
  key text primary key,
  value text not null
);
alter table public.settings enable row level security;
-- 정책 없음 = API로는 아무도 못 읽음. SQL Editor 에서만 본다.

-- ── 멤버 ───────────────────────────────────────
create table if not exists public.members (
  uid uuid primary key references auth.users(id) on delete cascade,
  is_admin boolean not null default false,
  joined_at timestamptz not null default now()
);
alter table public.members enable row level security;

drop policy if exists "read own membership" on public.members;
create policy "read own membership" on public.members
  for select to authenticated using (uid = auth.uid());

create or replace function public.is_member() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from members where uid = auth.uid());
$$;

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from members where uid = auth.uid() and is_admin);
$$;

-- 입장 코드가 맞으면 멤버로 넣는다. 틀리면 false.
create or replace function public.join_room(code text) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then
    return false;
  end if;
  if not exists (select 1 from settings where key = 'join_code' and value = code) then
    perform pg_sleep(1);  -- 코드 맞히기 시도를 느리게
    return false;
  end if;
  insert into members (uid) values (auth.uid()) on conflict do nothing;
  return true;
end $$;

revoke all on function public.join_room(text) from public, anon;
grant execute on function public.join_room(text) to authenticated;

-- ── 한마디 ─────────────────────────────────────
create table if not exists public.messages (
  id bigint generated always as identity primary key,
  uid uuid not null default auth.uid() references auth.users(id) on delete cascade,
  station text not null check (char_length(station) between 1 and 20),
  line text check (line ~ '^[1-9]$'),
  kind text not null default 'text' check (kind in ('text', 'preset')),
  text text not null check (char_length(text) between 1 and 60),
  created_at timestamptz not null default now()
);
create index if not exists messages_created_at on public.messages (created_at desc);
alter table public.messages enable row level security;

drop policy if exists "members read" on public.messages;
create policy "members read" on public.messages
  for select to authenticated using (public.is_member());

drop policy if exists "members write own" on public.messages;
create policy "members write own" on public.messages
  for insert to authenticated with check (public.is_member() and uid = auth.uid());

drop policy if exists "admin delete" on public.messages;
create policy "admin delete" on public.messages
  for delete to authenticated using (public.is_admin());

-- 같은 사람은 3초에 한 번. 시각은 서버 시계로 고정.
create or replace function public.messages_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.created_at := now();
  if exists (
    select 1 from messages
    where uid = new.uid and created_at > now() - interval '3 seconds'
  ) then
    raise exception 'rate_limited' using errcode = 'P0001';
  end if;
  return new;
end $$;

drop trigger if exists messages_guard on public.messages;
create trigger messages_guard before insert on public.messages
  for each row execute function public.messages_guard();

-- ── 실시간 ─────────────────────────────────────
do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'messages'
  ) then
    alter publication supabase_realtime add table public.messages;
  end if;
end $$;

-- ── 처음 한 번: 입장 코드 정하기 (값은 바꿔서 실행, 저장소에 적지 말 것) ──
-- insert into public.settings (key, value) values ('join_code', '여기에-코드')
--   on conflict (key) do update set value = excluded.value;
--
-- ── 관리자 지정: 테스트 페이지에서 본인 uid 확인 후 ──
-- update public.members set is_admin = true where uid = '본인-uid';
--
-- ── 오래된 한마디 정리 (가끔 수동으로) ──
-- delete from public.messages where created_at < now() - interval '7 days';
