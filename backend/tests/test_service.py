"""Service-layer tests using a stubbed Tally HTTP client."""
from __future__ import annotations

from typing import Iterable

import pytest

from app.tally import service as service_module
from app.tally.client import TallyError
from app.tally.service import TallyService


class _StubClient:
    """Replays scripted XML responses for each post_xml call."""

    def __init__(self, responses: Iterable[str | TallyError], *, ping_ok: bool = True) -> None:
        self._responses = list(responses)
        self._index = 0
        self.url = "http://stub:9000"
        self._ping_ok = ping_ok

    async def ping(self) -> tuple[bool, float, str | None]:
        return self._ping_ok, 1.0, None if self._ping_ok else "down"

    async def post_xml(self, envelope: str) -> str:
        item = self._next()
        if isinstance(item, TallyError):
            raise item
        return item

    async def post_xml_parsed(self, envelope: str) -> dict:
        import xmltodict

        return xmltodict.parse(await self.post_xml(envelope)) or {}

    def _next(self) -> str | TallyError:
        if self._index >= len(self._responses):
            raise TallyError("ran out of scripted responses")
        item = self._responses[self._index]
        self._index += 1
        return item


@pytest.mark.asyncio
async def test_dashboard_falls_back_to_mock_when_unreachable() -> None:
    svc = TallyService()
    svc.client = _StubClient(
        [TallyError("unreachable"), TallyError("unreachable")],
        ping_ok=False,
    )
    payload, used_live = await svc.dashboard()
    assert used_live is False
    assert payload.company.name  # mock company name
    assert payload.recent_vouchers


@pytest.mark.asyncio
async def test_dashboard_uses_company_name_when_available(monkeypatch) -> None:
    company_xml = """<ENVELOPE>
      <COMPANY NAME="Stub Co Ltd"><STARTINGFROM>20240401</STARTINGFROM></COMPANY>
    </ENVELOPE>"""
    empty = "<ENVELOPE></ENVELOPE>"
    svc = TallyService()
    # _resolve_company_name tries loaded_companies first, then list_companies.
    # The dashboard then calls _resolve_company_name again at the top, plus
    # ledgers/stock/day_book — total of 5 calls beyond the connection pings.
    svc.client = _StubClient(
        [company_xml] * 6 + [empty] * 6,
        ping_ok=True,
    )
    payload, used_live = await svc.dashboard()
    assert used_live is True
    assert payload.company.name == "Stub Co Ltd"


@pytest.mark.asyncio
async def test_diagnostics_returns_step_results() -> None:
    company_xml = """<ENVELOPE>
      <COMPANY NAME="Stub"><STARTINGFROM>20240401</STARTINGFROM></COMPANY>
    </ENVELOPE>"""
    empty = "<ENVELOPE></ENVELOPE>"
    svc = TallyService()
    svc.client = _StubClient([company_xml] * 4 + [empty] * 12, ping_ok=True)
    diag = await svc.diagnostics()
    assert diag["ping_ok"] is True
    assert diag["company"] == "Stub"
    labels = [s["label"] for s in diag["steps"]]
    assert "List of Companies" in labels
    assert "Day Book (last 365 days)" in labels
