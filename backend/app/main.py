from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from app.config import settings

app = FastAPI(
    title="Job Market Analytics API",
    description="Backend API for Job Market & Skill Demand Analytics Platform",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", summary="Health Check Endpoint")
def get_health() -> Dict[str, str]:
    """
    Health check endpoint returning system status.

    Returns:
        Dict[str, str]: Status payload indicating application availability.
    """
    return {"status": "ok"}
