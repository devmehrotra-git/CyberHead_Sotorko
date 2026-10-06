"""FastAPI application entry point for Sotorko."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="A vernacular digital-safety companion by Team CyberHead.",
    version=settings.app_version,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
