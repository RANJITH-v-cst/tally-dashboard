"""FastAPI routes consumed by the frontend."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Header, Query
from pydantic import BaseModel

from ..models import (
    BalanceSheet,
    ConnectionStatus,
    DashboardPayload,
    LedgerBalance,
    ProfitLoss,
    TrialBalanceRow,
)
from ..tally.service import TallyService

router = APIRouter(prefix="/api")


def _service(url: str | None) -> TallyService:
    return TallyService(url=url or None)


class DashboardResponse(BaseModel):
    data: DashboardPayload
    used_live_data: bool


class LedgersResponse(BaseModel):
    data: list[LedgerBalance]
    used_live_data: bool


class TrialBalanceResponse(BaseModel):
    data: list[TrialBalanceRow]
    used_live_data: bool


class ProfitLossResponse(BaseModel):
    data: ProfitLoss
    used_live_data: bool


class BalanceSheetResponse(BaseModel):
    data: BalanceSheet
    used_live_data: bool


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/connection", response_model=ConnectionStatus)
async def connection(
    x_tally_url: str | None = Header(default=None, alias="X-Tally-Url"),
) -> ConnectionStatus:
    return await _service(x_tally_url).check_connection()


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    x_tally_url: str | None = Header(default=None, alias="X-Tally-Url"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> DashboardResponse:
    data, live = await _service(x_tally_url).dashboard(from_date, to_date)
    return DashboardResponse(data=data, used_live_data=live)


@router.get("/ledgers", response_model=LedgersResponse)
async def ledgers(
    x_tally_url: str | None = Header(default=None, alias="X-Tally-Url"),
) -> LedgersResponse:
    data, live = await _service(x_tally_url).ledgers()
    return LedgersResponse(data=data, used_live_data=live)


@router.get("/trial-balance", response_model=TrialBalanceResponse)
async def trial_balance(
    x_tally_url: str | None = Header(default=None, alias="X-Tally-Url"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> TrialBalanceResponse:
    today = date.today()
    to_d = to_date or today
    from_d = from_date or (today - timedelta(days=365))
    data, live = await _service(x_tally_url).trial_balance(from_d, to_d)
    return TrialBalanceResponse(data=data, used_live_data=live)


@router.get("/profit-loss", response_model=ProfitLossResponse)
async def profit_loss(
    x_tally_url: str | None = Header(default=None, alias="X-Tally-Url"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> ProfitLossResponse:
    today = date.today()
    to_d = to_date or today
    from_d = from_date or (today - timedelta(days=365))
    data, live = await _service(x_tally_url).profit_loss(from_d, to_d)
    return ProfitLossResponse(data=data, used_live_data=live)


@router.get("/balance-sheet", response_model=BalanceSheetResponse)
async def balance_sheet(
    x_tally_url: str | None = Header(default=None, alias="X-Tally-Url"),
    as_of: date | None = Query(default=None),
) -> BalanceSheetResponse:
    data, live = await _service(x_tally_url).balance_sheet(as_of or date.today())
    return BalanceSheetResponse(data=data, used_live_data=live)


@router.get("/diagnostics")
async def diagnostics(
    x_tally_url: str | None = Header(default=None, alias="X-Tally-Url"),
) -> dict[str, Any]:
    """Run every Tally request and report what came back.

    Used by the Settings → Diagnostics panel so users can see exactly
    which calls succeed / fail and which sections are showing demo data
    versus live data.
    """
    return await _service(x_tally_url).diagnostics()
