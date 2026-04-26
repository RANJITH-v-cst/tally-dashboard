"""High-level service layer.

Handles the live-vs-mock decision: for each report we try the live Tally
gateway and fall back to the bundled mock dataset only for the parts we
couldn't get from Tally. The dashboard payload therefore stitches whatever
the gateway gave us together with mock derivatives (trends, aging) so the
UI is always usable.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

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

    # ---------------------------------------------------------------- helpers

    async def _safe_post(self, envelope: str) -> tuple[dict | None, str | None]:
        """Send a request and return (parsed_dict_or_none, error_message_or_none)."""
        try:
            payload = await self.client.post_xml_parsed(envelope)
            return payload, None
        except TallyError as exc:
            return None, str(exc)

    async def _resolve_company_name(self) -> str | None:
        """Find the name of the loaded company (or first company) in Tally."""
        for builder in (xml_requests.loaded_companies, xml_requests.list_companies):
            payload, _ = await self._safe_post(builder())
            if payload is None:
                continue
            companies = parser.parse_companies(payload)
            if companies:
                return companies[0]
        return None

    # ---------------------------------------------------------------- connection

    async def check_connection(self) -> ConnectionStatus:
        ok, latency, error = await self.client.ping()
        company: str | None = None
        if ok:
            try:
                company = await self._resolve_company_name()
                if company is None:
                    error = (
                        "Tally responded but no company list could be parsed. "
                        "Make sure a company is loaded (Gateway of Tally must "
                        "be visible) and ODBC is enabled."
                    )
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

    # ---------------------------------------------------------------- dashboard

    async def dashboard(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[DashboardPayload, bool]:
        """Return (payload, used_live_data).

        `used_live_data` is True if *any* part of the payload came from
        Tally — including just the company name. Mock derivatives fill in
        the gaps so the UI never breaks.
        """
        today = date.today()
        to_date = to_date or today
        from_date = from_date or (today - timedelta(days=365))

        base = mock_data.mock_dashboard()
        used_live = False

        company = await self._resolve_company_name()
        if company:
            base.company.name = company
            used_live = True
        else:
            return base, False  # Tally not reachable / no company loaded

        # Ledgers → receivables / payables / cash KPIs
        ledgers_payload, _ = await self._safe_post(xml_requests.ledgers(company))
        if ledgers_payload:
            ledgers_raw = parser.parse_ledgers(ledgers_payload)
            if ledgers_raw:
                used_live = True
                base.kpis.receivables = sum(
                    l["closing_balance"]
                    for l in ledgers_raw
                    if "debtor" in l["parent"].lower()
                ) or base.kpis.receivables
                base.kpis.payables = abs(
                    sum(
                        l["closing_balance"]
                        for l in ledgers_raw
                        if "creditor" in l["parent"].lower()
                    )
                ) or base.kpis.payables
                base.kpis.cash_and_bank = sum(
                    l["closing_balance"]
                    for l in ledgers_raw
                    if "bank" in l["parent"].lower() or "cash" in l["name"].lower()
                ) or base.kpis.cash_and_bank

        # Stock items → top stock + total stock value
        stock_payload, _ = await self._safe_post(xml_requests.stock_items(company))
        if stock_payload:
            stock_raw = parser.parse_stock_summary(stock_payload)
            if stock_raw:
                used_live = True
                base.top_stock_items = [
                    StockItem(**s)
                    for s in sorted(stock_raw, key=lambda s: s["value"], reverse=True)[:10]
                ]
                base.kpis.stock_value = sum(s["value"] for s in stock_raw) or base.kpis.stock_value

        # Day Book → recent vouchers + sales/purchase totals
        day_book_payload, _ = await self._safe_post(
            xml_requests.day_book(from_date, to_date, company)
        )
        if day_book_payload:
            day_book_raw = parser.parse_day_book(day_book_payload)
            if day_book_raw:
                used_live = True
                base.recent_vouchers = [
                    VoucherEntry(**v)
                    for v in sorted(day_book_raw, key=lambda v: v["date"], reverse=True)[:15]
                ]
                sales = sum(
                    v["amount"]
                    for v in day_book_raw
                    if "sales" in v["voucher_type"].lower()
                )
                purchases = sum(
                    v["amount"]
                    for v in day_book_raw
                    if "purchase" in v["voucher_type"].lower()
                )
                if sales:
                    base.kpis.total_sales = sales
                if purchases:
                    base.kpis.total_purchases = purchases

        return base, used_live

    # ---------------------------------------------------------------- per-report

    async def ledgers(self) -> tuple[list[LedgerBalance], bool]:
        company = await self._resolve_company_name()
        payload, _ = await self._safe_post(xml_requests.ledgers(company or ""))
        if payload:
            raw = parser.parse_ledgers(payload)
            if raw:
                return [LedgerBalance(**r) for r in raw], True
        return mock_data.mock_ledgers(), False

    async def trial_balance(
        self, from_date: date, to_date: date
    ) -> tuple[list[TrialBalanceRow], bool]:
        company = await self._resolve_company_name()
        payload, _ = await self._safe_post(
            xml_requests.trial_balance(from_date, to_date, company or "")
        )
        if payload:
            raw = parser.parse_trial_balance(payload)
            if raw:
                return [TrialBalanceRow(**r) for r in raw], True
        return mock_data.mock_trial_balance(), False

    async def profit_loss(
        self, from_date: date, to_date: date
    ) -> tuple[ProfitLoss, bool]:
        # Tally's P&L XML is free-form per ledger group; we currently
        # serve mock until we have a live response sample to parse.
        return mock_data.mock_profit_loss(), False

    async def balance_sheet(self, as_of: date) -> tuple[BalanceSheet, bool]:
        return mock_data.mock_balance_sheet(), False

    # ---------------------------------------------------------------- diagnostics

    async def diagnostics(self) -> dict[str, Any]:
        """Run every Tally request and return a structured summary.

        Used by the Settings → Diagnostics panel so the user can see
        exactly which calls succeed / fail and why each section is showing
        live or demo data.
        """
        today = date.today()
        from_date = today - timedelta(days=365)

        ok, latency, ping_error = await self.client.ping()
        company = await self._resolve_company_name() if ok else None

        async def run(label: str, builder, parser_fn, builder_args=()) -> dict[str, Any]:
            envelope = builder(*builder_args)
            try:
                raw = await self.client.post_xml(envelope)
                parsed = await self.client.post_xml_parsed(envelope)
                rows = parser_fn(parsed)
                return {
                    "label": label,
                    "ok": True,
                    "row_count": len(rows),
                    "sample": rows[:2],
                    "raw_preview": raw[:600],
                    "envelope_preview": envelope[:600],
                    "error": None,
                }
            except TallyError as exc:
                return {
                    "label": label,
                    "ok": False,
                    "row_count": 0,
                    "sample": [],
                    "raw_preview": "",
                    "envelope_preview": envelope[:600],
                    "error": str(exc),
                }

        company_arg = company or ""
        steps = [
            await run("List of Companies", xml_requests.list_companies, parser.parse_companies_full),
            await run("Loaded Companies", xml_requests.loaded_companies, parser.parse_companies_full),
            await run("Ledgers", xml_requests.ledgers, parser.parse_ledgers, (company_arg,)),
            await run("Stock Items", xml_requests.stock_items, parser.parse_stock_summary, (company_arg,)),
            await run(
                "Day Book (last 365 days)",
                xml_requests.day_book,
                parser.parse_day_book,
                (from_date, today, company_arg),
            ),
            await run(
                "Trial Balance",
                xml_requests.trial_balance,
                parser.parse_trial_balance,
                (from_date, today, company_arg),
            ),
        ]

        return {
            "url": self.client.url,
            "ping_ok": ok,
            "latency_ms": round(latency, 2) if latency is not None else None,
            "ping_error": ping_error,
            "company": company,
            "steps": steps,
        }
