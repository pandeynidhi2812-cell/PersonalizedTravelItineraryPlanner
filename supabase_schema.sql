-- Optional: run this in the Supabase SQL editor to receive mirrored trips.
create table if not exists public.trips (
    id           bigint primary key,
    owner_email  text,
    title        text not null,
    destination  text,
    start_date   date,
    end_date     date,
    travelers    int,
    budget       int,
    style        text,
    pace         text,
    interests    jsonb,
    itinerary    jsonb,
    total_cost   int,
    updated_at   timestamptz default now()
);

-- The backend uses the service_role key, which bypasses RLS. Keep RLS on so the table
-- is not readable with the public anon key.
alter table public.trips enable row level security;
