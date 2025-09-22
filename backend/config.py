from pydantic_settings import BaseSettings
from typing import List
import os
import secrets

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./database/flow_ml.db"
    
    # JWT Settings
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours for better UX
    
    # File Storage
    upload_dir: str = "./data"
    max_file_size: int = 52428800  # 50MB in bytes
    
    # LLM API removed for MVP
    
    # App Settings
    app_name: str = "Flow ML Backend"
    debug: bool = True  # Set to True for development
    environment: str = "development"
    
    # CORS Settings - Allow all origins in development
    cors_origins: List[str] = ["*"]
    
    # No tier limits - everything is free!
    max_file_size: int = 524288000  # 500MB
    max_rows: int = 1000000  # 1M rows
    
    # Security
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
