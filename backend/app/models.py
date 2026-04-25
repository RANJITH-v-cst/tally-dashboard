"""Pydantic response models for the REST API consumed by the frontend."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CompanyInfo(BaseModel):
    name: str
    financial_year_start: date | None = None
    books_begin_from: date | None = None


class KpiSummary(BaseModel):
    total_sales: float
    total_purchases: float
    receivables: float
    payables: float
    cash_and_bank: float
    stock_value: float
    currency: str = "INR"


class TrendPoint(BaseModel):
    period: str  # e.g. "2025-04"
    amount: float


class PartyAmount(BaseModel):
    name: str
    amount: float


class StockItem(BaseModel):
    name: str
    quantity: float
    unit: str
    rate: float
    value: float


class OutstandingEntry(BaseModel):
    party: str
    amount: float
    aging_bucket: Literal["0-30", "31-60", "61-90", "90+"]


class LedgerBalance(BaseModel):
    name: str
    parent: str
    opening_balance: float
    closing_balance: float


class TrialBalanceRow(BaseModel):
    name: str
    parent: str
    debit: float
    credit: float


class ProfitLossSection(BaseModel):
    name: str
    amount: float


class ProfitLoss(BaseModel):
    revenue: list[ProfitLossSection]
    expenses: list[ProfitLossSection]
    gross_profit: float
    net_profit: float


class BalanceSheetSection(BaseModel):
    name: str
    amount: float


class BalanceSheet(BaseModel):
    assets: list[BalanceSheetSection]
    liabilities: list[BalanceSheetSection]
    total_assets: float
    total_liabilities: float


class VoucherEntry(BaseModel):
    date: date
    voucher_number: str
    voucher_type: str
    party: str
    amount: float
    narration: str = ""


class DashboardPayload(BaseModel):
    company: CompanyInfo
    kpis: KpiSummary
    sales_trend: list[TrendPoint]
    purchase_trend: list[TrendPoint]
    top_customers: list[PartyAmount]
    top_suppliers: list[PartyAmount]
    top_stock_items: list[StockItem]
    receivables: list[OutstandingEntry]
    payables: list[OutstandingEntry]
    recent_vouchers: list[VoucherEntry]


class ConnectionStatus(BaseModel):
    ok: bool
    url: str
    company: str | None = None
    error: str | None = None
    latency_ms: float | None = Field(default=None, ge=0)
