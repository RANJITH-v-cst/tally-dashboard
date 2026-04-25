"""Runtime configuration for the backend.

The Tally URL is the HTTP/XML gateway exposed by TallyPrime / Tally ERP 9
(default port 9000). It can be overridden per-request by the frontend via
the ``X-Tally-Url`` header so users can point the dashboard at their own
Tally instance without restarting the server.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    tally_url: str
    request_timeout_seconds: float
    cors_origins: tuple[str, ...]


def _split_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def load_settings() -> Settings:
    return Settings(
        tally_url=os.getenv("TALLY_URL", "http://localhost:9000"),
        request_timeout_seconds=float(os.getenv("TALLY_TIMEOUT", "30")),
        cors_origins=_split_csv(os.getenv("CORS_ORIGINS", "*")) or ("*",),
    )


settings = load_settings()
