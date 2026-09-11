"""
AgriSmart AI - Configuration Settings
Loads environment variables for local development and Render cloud deployment.
"""

import os
from typing import List


class Settings:
    PROJECT_NAME: str = "AgriSmart AI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Database URL: defaults to local SQLite for zero-setup execution
    # On Render, the managed PostgreSQL database populates DATABASE_URL automatically
    _raw_db_url: str = os.getenv("DATABASE_URL", "sqlite:///./agrismart.db")
    
    @property
    def DATABASE_URL(self) -> str:
        # Render provides PostgreSQL connection strings with 'postgres://' prefix,
        # but SQLAlchemy 1.4/2.0 requires 'postgresql://'
        if self._raw_db_url.startswith("postgres://"):
            return self._raw_db_url.replace("postgres://", "postgresql://", 1)
        return self._raw_db_url

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    CORS_ORIGINS: List[str] = ["*"]


settings = Settings()
