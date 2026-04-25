"""Thin async client for the Tally HTTP/XML gateway."""
from __future__ import annotations

import time

import httpx
import xmltodict

from ..config import settings


class TallyError(RuntimeError):
    pass


class TallyClient:
    def __init__(self, url: str | None = None, timeout: float | None = None) -> None:
        self.url = url or settings.tally_url
        self.timeout = timeout or settings.request_timeout_seconds

    async def post_xml(self, envelope: str) -> str:
        headers = {"Content-Type": "application/xml"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.url, content=envelope.encode("utf-8"), headers=headers)
        except httpx.HTTPError as exc:
            raise TallyError(f"Could not reach Tally at {self.url}: {exc}") from exc

        if response.status_code != 200:
            raise TallyError(
                f"Tally returned HTTP {response.status_code}: {response.text[:200]}"
            )
        return response.text

    async def post_xml_parsed(self, envelope: str) -> dict:
        raw = await self.post_xml(envelope)
        try:
            return xmltodict.parse(raw) or {}
        except Exception as exc:  # noqa: BLE001
            raise TallyError(f"Could not parse Tally XML response: {exc}") from exc

    async def ping(self) -> tuple[bool, float, str | None]:
        """Lightweight reachability check.

        Returns (ok, latency_ms, error_message).
        """
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=min(self.timeout, 5.0)) as client:
                response = await client.get(self.url)
            latency = (time.perf_counter() - started) * 1000
            # Tally answers GET / with an HTML "TallyPrime Server is Running" page
            ok = response.status_code == 200 and "tally" in response.text.lower()
            return ok, latency, None if ok else "Response did not look like Tally"
        except httpx.HTTPError as exc:
            latency = (time.perf_counter() - started) * 1000
            return False, latency, str(exc)
