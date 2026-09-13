"""
AgriSmart AI - FastAPI Application Entrypoint
Ref: SIH 2026 Problem Statement 1
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import core_disease, chat, advisory


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

# Configure Cross-Origin Resource Sharing (CORS) - Allow all origins (Vercel, Render, Localhost, Mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(core_disease.router)
app.include_router(chat.router)
app.include_router(advisory.router)


@app.get("/health", tags=["Health & Status"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "model_engine": "ready"
    }


import os
from fastapi.staticfiles import StaticFiles

# Safely mount the frontend directory if present
_candidate_frontend_dirs = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend")),
    os.path.abspath("frontend"),
    os.path.abspath("../frontend")
]
for _f_dir in _candidate_frontend_dirs:
    if os.path.isdir(_f_dir) and os.path.isfile(os.path.join(_f_dir, "index.html")):
        app.mount("/", StaticFiles(directory=_f_dir, html=True), name="frontend")
        break


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
