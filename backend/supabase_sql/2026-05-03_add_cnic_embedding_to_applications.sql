-- Add a CNIC face embedding column to applications.
-- Run this in your Supabase project's SQL editor.

alter table public.applications
add column if not exists cnic_embedding jsonb;