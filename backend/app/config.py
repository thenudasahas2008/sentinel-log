import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "SentinelLog"
    APP_VERSION: str = "2.4.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Security & JWT
    SECRET_KEY: str = "sentinel_secret_key_change_in_production_893247891234"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/sentinel_log.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # Ingestion & Uploads
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = [".log", ".txt", ".json", ".csv", ".evtx", ".syslog"]
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    REPORTS_DIR: str = str(BASE_DIR / "reports_storage")
    
    # Threat Intelligence Integrations (Disabled by default)
    ENABLE_EXTERNAL_THREAT_INTEL: bool = False
    VIRUSTOTAL_API_KEY: Optional[str] = None
    ABUSEIPDB_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120
    
    # Detection Engine Defaults
    BRUTE_FORCE_THRESHOLD: int = 5
    BRUTE_FORCE_WINDOW_MINUTES: int = 10
    PASSWORD_SPRAY_USER_THRESHOLD: int = 3
    PASSWORD_SPRAY_WINDOW_MINUTES: int = 15
    IMPOSSIBLE_TRAVEL_SPEED_KMH: float = 900.0

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
