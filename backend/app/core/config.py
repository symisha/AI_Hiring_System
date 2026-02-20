from pydantic_settingsimport BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"   

Settings = Settings()