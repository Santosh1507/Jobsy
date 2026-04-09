import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Jobsy - WhatsApp Job Automation"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # WhatsApp API (Twilio)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    
    # Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:70b")
    
    # Job Scraping
    LINKEDIN_COOKIE: Optional[str] = os.getenv("LINKEDIN_COOKIE", "")
    Naukri_API_KEY: Optional[str] = os.getenv("NAUKRI_API_KEY", "")
    
    # Email Finder (Apollo.io)
    APOLLO_API_KEY: Optional[str] = os.getenv("APOLLO_API_KEY", "")
    HUNTER_API_KEY: Optional[str] = os.getenv("HUNTER_API_KEY", "")
    
    # Storage
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Scheduling
    JOB_DROP_TIME: str = "08:00"
    MAX_APPLICATIONS_PER_DAY: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()