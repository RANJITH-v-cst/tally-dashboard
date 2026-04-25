"""FastAPI application entry point for the Tally Dashboard backend."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tally Dashboard API",
        description=(
            "Visualise TallyPrime / Tally ERP 9 data via its HTTP/XML gateway. "
            "Set the Tally URL per-request with the `X-Tally-Url` header, or "
            "via the `TALLY_URL` environment variable on the server."
        ),
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "tally-dashboard-backend",
            "docs": "/docs",
            "tally_url": settings.tally_url,
        }

    return app


app = create_app()
