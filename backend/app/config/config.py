from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # goes to /backend

class AppSettings(BaseSettings):
    ADMIN_EMAIL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    OPENAI_API_KEY: str
    BACKEND_URL: str
    FRONTEND_URL: str
    LLAMA_API_KEY: str
    FRONTEND_INTERVIEW_URL: str = "http://localhost:8080/interview.html"
    INTERVIEW_LINK_SECRET: str = ""
    INTERVIEW_LINK_TTL_SECONDS: int = 86400
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="allow"
    )

Settings = AppSettings()
settings = Settings
