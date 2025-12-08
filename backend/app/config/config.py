from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ADMIN_EMAIL: str    # for testing purpose only 
    SUPABASE_URL: str
    SUPABASE_KEY: str
    OPENAI_API_KEY: str
    BACKEND_URL: str
    FRONTEND_URL: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  #ignore evrthing else in .env file except defined variables

Settings = Settings()   # Create an instance of the Settings class to access environment variables
