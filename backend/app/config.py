"""
Application Configuration
==========================
Centralized configuration using Pydantic Settings.
Reads from environment variables and .env file.
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Create a .env file in the backend/ directory with these values,
    or set them as environment variables.
    """
    
    # ─── App Settings ────────────────────────────────────────────────────
    APP_NAME: str = "Sentiment Chatbot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ─── CORS Settings ───────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"
    
    # ─── Model Settings ─────────────────────────────────────────────────
    MODEL_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ml", "trained_model"
    )
    
    # ─── Database Settings ───────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    
    # ─── Rate Limiting ───────────────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 60       # Max requests per window
    RATE_LIMIT_WINDOW: int = 60         # Window in seconds
    
    # ─── Logging ─────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    @property
    def cors_origins_list(self) -> list:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()
