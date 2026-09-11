"""
AgriSmart AI - FastAPI Application Entrypoint
Ref: SIH 2026 Problem Statement 1
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import core_disease


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Auto-create database tables (SQLite or Render PostgreSQL)
    init_db()
    yield
    # Shutdown: Clean up any resources if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "AgriSmart AI Backend API - Intelligent Agriculture for a Sustainable Future.\n\n"
        "Features AI-powered crop disease detection, precaution guidance, "
        "smart irrigation, weather intelligence, and agentic advisory systems."
    ),
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(core_disease.router)


@app.get("/", tags=["Health & Status"])
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "contract": {
            "cli": "python predict.py --image <path>",
            "callable": "from model.predict import predict"
        }
    }


@app.get("/health", tags=["Health & Status"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "model_engine": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
