from supabase import create_client, Client
from app.config.config import Settings
from supabase._async.client import AsyncClient, create_client as create_async_client

supabase_url: str = Settings.SUPABASE_URL
supabase_key: str = Settings.SUPABASE_KEY  # ✅ Use service role key

supabase: Client = create_client(supabase_url, supabase_key)