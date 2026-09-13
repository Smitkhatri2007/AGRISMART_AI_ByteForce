"""
AgriSmart AI - Configuration Settings
Loads environment variables for local development and Render cloud deployment.
Includes built-in zero-dependency .env file loader.
"""

import os
from typing import List

# Automatically load .env file if present in project root (zero external dependencies required)
_env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(_env_file):
    try:
        with open(_env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    key = k.strip()
                    val = v.split("#")[0].strip().strip('"').strip("'")
                    # Set in os.environ if not already defined
                    if key not in os.environ:
                        os.environ[key] = val
    except Exception:
        pass


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

    # Google Gemini Pro Configuration (Deprecated, switching to Groq)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    CORS_ORIGINS: List[str] = ["*"]


settings = Settings()
