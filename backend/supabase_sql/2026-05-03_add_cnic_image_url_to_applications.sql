-- Add a dedicated CNIC image URL column to applications.
-- Run this in your Supabase project's SQL editor.

alter table public.applications
add column if not exists cnic_image_url text;

-- Optional: if you want to enforce it going forward, make it NOT NULL after backfilling:
-- alter table public.applications alter column cnic_image_url set not null;
