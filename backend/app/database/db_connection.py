from supabase import create_client, Client
from app.config.config import Settings

supabase_url: str = Settings.SUPABASE_URL
supabase_key: str = Settings.SUPABASE_KEY

supabase: Client = create_client(supabase_url, supabase_key)


