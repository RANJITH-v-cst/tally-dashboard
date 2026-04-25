"""High-level service layer.

Handles the live-vs-mock decision: if the Tally gateway is reachable and
returns a plausible response we use real data; otherwise we fall back to
the bundled mock dataset so the UI is always usable for demos.
"""
from __future__ import annotations

from datetime import date, timedelta

from . import mock_data, parser, requests as xml_requests
from .client import TallyClient, TallyError
from ..models import (
    BalanceSheet,
    ConnectionStatus,
    DashboardPayload,
    LedgerBalance,
    ProfitLoss,
    StockItem,
    TrialBalanceRow,
    VoucherEntry,
)


class TallyService:
    def __init__(self, url: str | None = None) -> None:
        self.client = TallyClient(url=url)

    async def check_connection(self) -> ConnectionStatus:
        ok, latency, error = await self.client.ping()
        company: str | None = None
        if ok:
            try:
                payload = await self.client.post_xml_parsed(xml_requests.list_companies())
                names = parser.parse_companies(payload)
                company = names[0] if names else None
            except TallyError as exc:
                ok = False
                error = str(exc)
        return ConnectionStatus(
            ok=ok,
            url=self.client.url,
            company=company,
            error=error,
            latency_ms=round(latency, 2) if latency is not None else None,
        )

    async def _live_dashboard(self, from_date: date, to_date: date) -> DashboardPayload | None:
        try:
            companies = parser.parse_companies(
                await self.client.post_xml_parsed(xml_requests.list_companies())
            )
        except TallyError:
            return None
        if not companies:
            return None
        company = companies[0]

        try:
            ledgers_raw = parser.parse_ledgers(
                await self.client.post_xml_parsed(xml_requests.ledgers())
            )
            day_book_raw = parser.parse_day_book(
                await self.client.post_xml_parsed(
                    xml_requests.day_book(from_date, to_date, company)
                )
            )
            stock_raw = parser.parse_stock_summary(
                await self.client.post_xml_parsed(xml_requests.stock_summary(company))
            )
        except TallyError:
            return None

        # When we do have live data we still stitch in mock derivatives for
        # views we cannot trivially compute from the raw XML (trend charts,
        # aging buckets). A future iteration can replace these with proper
        # aggregations once we have live data to exercise.
        base = mock_data.mock_dashboard()
        if ledgers_raw:
            base.kpis.receivables = sum(
                l["closing_balance"] for l in ledgers_raw
                if "debtor" in l["parent"].lower()
            ) or base.kpis.receivables
            base.kpis.payables = abs(sum(
                l["closing_balance"] for l in ledgers_raw
                if "creditor" in l["parent"].lower()
            )) or base.kpis.payables
            base.kpis.cash_and_bank = sum(
                l["closing_balance"] for l in ledgers_raw
                if "bank" in l["parent"].lower() or "cash" in l["name"].lower()
            ) or base.kpis.cash_and_bank

        if stock_raw:
            base.top_stock_items = [
                StockItem(**s)
                for s in sorted(stock_raw, key=lambda s: s["value"], reverse=True)[:10]
            ]
            base.kpis.stock_value = sum(s["value"] for s in stock_raw)

        if day_book_raw:
            base.recent_vouchers = [
                VoucherEntry(**v) for v in sorted(day_book_raw, key=lambda v: v["date"], reverse=True)[:15]
            ]
            base.kpis.total_sales = sum(
                v["amount"] for v in day_book_raw
                if "sales" in v["voucher_type"].lower()
            ) or base.kpis.total_sales
            base.kpis.total_purchases = sum(
                v["amount"] for v in day_book_raw
                if "purchase" in v["voucher_type"].lower()
            ) or base.kpis.total_purchases

        base.company.name = company
        return base

    async def dashboard(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[DashboardPayload, bool]:
        """Return (payload, used_live_data)."""
        today = date.today()
        to_date = to_date or today
        from_date = from_date or (today - timedelta(days=365))
        live = await self._live_dashboard(from_date, to_date)
        if live is not None:
            return live, True
        return mock_data.mock_dashboard(), False

    async def ledgers(self) -> tuple[list[LedgerBalance], bool]:
        try:
            raw = parser.parse_ledgers(
                await self.client.post_xml_parsed(xml_requests.ledgers())
            )
            if raw:
                return [LedgerBalance(**r) for r in raw], True
        except TallyError:
            pass
        return mock_data.mock_ledgers(), False

    async def trial_balance(
        self, from_date: date, to_date: date
    ) -> tuple[list[TrialBalanceRow], bool]:
        try:
            raw = parser.parse_trial_balance(
                await self.client.post_xml_parsed(
                    xml_requests.trial_balance(from_date, to_date)
                )
            )
            if raw:
                return [TrialBalanceRow(**r) for r in raw], True
        except TallyError:
            pass
        return mock_data.mock_trial_balance(), False

    async def profit_loss(
        self, from_date: date, to_date: date
    ) -> tuple[ProfitLoss, bool]:
        # Tally's P&L XML is free-form per ledger group; without live data to
        # sample against we fall back to mock and surface used_live=False.
        return mock_data.mock_profit_loss(), False

    async def balance_sheet(self, as_of: date) -> tuple[BalanceSheet, bool]:
        return mock_data.mock_balance_sheet(), False
