"""
AgriSmart AI - Database Engine & Session Management
Supports dual modes:
- Zero-setup file-based SQLite for local development and offline judging reproduction.
- PostgreSQL for Render cloud production.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Configure connection args based on database dialect
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a transactional database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all database tables defined in app.models.
    Called on application startup.
    """
    # Import all models here so that Base registers them before creating tables
    import app.models.farm
    import app.models.diagnosis
    Base.metadata.create_all(bind=engine)
