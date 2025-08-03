from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator
import os

class Settings(BaseSettings):
    # Database - Neon Configuration
    # Railway will set DATABASE_URL environment variable
    DATABASE_URL: str = "postgresql://neondb_owner:npg_e6bOIDHrsf8T@ep-empty-glade-a1f1p80o-pooler.ap-southeast-1.aws.neon.tech/inventory_db?sslmode=require&channel_binding=require"
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Inventory Management System"
    
    # CORS - Allow Railway domain
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "https://*.railway.app",
        "https://*.up.railway.app"
    ]
    
    # Environment
    DEBUG: bool = False  # Set to False for production
    ENVIRONMENT: str = "production"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields to prevent validation errors

settings = Settings() 