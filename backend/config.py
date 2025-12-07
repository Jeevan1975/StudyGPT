from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    DATABASE_PASSWORD: str
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str
    
    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parent.parent / ".env")
    )
    
    
settings = Settings()