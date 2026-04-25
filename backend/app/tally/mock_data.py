"""Deterministic mock dataset used when Tally is unreachable.

Returned shapes are the same Pydantic models the real connector produces,
so the frontend cannot tell which source is in use — apart from a banner
that is toggled by ``ConnectionStatus.ok``.
"""
from __future__ import annotations

from datetime import date, timedelta

from ..models import (
    BalanceSheet,
    BalanceSheetSection,
    CompanyInfo,
    DashboardPayload,
    KpiSummary,
    LedgerBalance,
    OutstandingEntry,
    PartyAmount,
    ProfitLoss,
    ProfitLossSection,
    StockItem,
    TrendPoint,
    TrialBalanceRow,
    VoucherEntry,
)


def mock_company() -> CompanyInfo:
    return CompanyInfo(
        name="Acme Traders Pvt Ltd",
        financial_year_start=date(2025, 4, 1),
        books_begin_from=date(2024, 4, 1),
    )


def mock_kpis() -> KpiSummary:
    return KpiSummary(
        total_sales=18_742_350.0,
        total_purchases=12_305_180.0,
        receivables=3_126_500.0,
        payables=1_872_400.0,
        cash_and_bank=4_820_110.0,
        stock_value=6_430_900.0,
    )


def _months(n: int) -> list[str]:
    today = date.today().replace(day=1)
    out: list[str] = []
    cur = today
    for _ in range(n):
        out.append(cur.strftime("%Y-%m"))
        # step back one month
        first_prev = (cur.replace(day=1) - timedelta(days=1)).replace(day=1)
        cur = first_prev
    return list(reversed(out))


def mock_sales_trend() -> list[TrendPoint]:
    values = [1_220_000, 1_305_000, 1_480_000, 1_625_000, 1_710_000, 1_840_000,
              1_925_000, 1_650_000, 1_790_000, 1_880_000, 1_970_000, 2_010_000]
    return [TrendPoint(period=p, amount=v) for p, v in zip(_months(12), values)]


def mock_purchase_trend() -> list[TrendPoint]:
    values = [800_000, 880_000, 910_000, 1_010_000, 1_100_000, 1_180_000,
              1_230_000, 1_060_000, 1_170_000, 1_200_000, 1_260_000, 1_305_000]
    return [TrendPoint(period=p, amount=v) for p, v in zip(_months(12), values)]


def mock_top_customers() -> list[PartyAmount]:
    return [
        PartyAmount(name="Reliance Retail Ltd", amount=2_840_000),
        PartyAmount(name="DMart Wholesale", amount=2_115_000),
        PartyAmount(name="Metro Cash & Carry", amount=1_720_500),
        PartyAmount(name="Spencer's Retail", amount=1_512_300),
        PartyAmount(name="More Supermarkets", amount=1_184_200),
        PartyAmount(name="Star Bazaar", amount=965_700),
        PartyAmount(name="Nilgiri's", amount=812_400),
    ]


def mock_top_suppliers() -> list[PartyAmount]:
    return [
        PartyAmount(name="ITC Limited", amount=1_920_000),
        PartyAmount(name="Hindustan Unilever", amount=1_650_400),
        PartyAmount(name="Nestle India", amount=1_312_100),
        PartyAmount(name="Britannia Industries", amount=1_080_500),
        PartyAmount(name="Parle Products", amount=875_200),
        PartyAmount(name="Dabur India", amount=712_900),
    ]


def mock_stock_items() -> list[StockItem]:
    return [
        StockItem(name="Basmati Rice 5kg", quantity=1240, unit="Bag", rate=620, value=768_800),
        StockItem(name="Refined Sunflower Oil 1L", quantity=3850, unit="Btl", rate=155, value=596_750),
        StockItem(name="Aashirvaad Atta 10kg", quantity=980, unit="Bag", rate=495, value=485_100),
        StockItem(name="Tata Salt 1kg", quantity=5200, unit="Pkt", rate=28, value=145_600),
        StockItem(name="Nescafe Classic 100g", quantity=640, unit="Jar", rate=290, value=185_600),
        StockItem(name="Parle-G 800g", quantity=2100, unit="Pkt", rate=95, value=199_500),
        StockItem(name="Amul Butter 500g", quantity=880, unit="Pkt", rate=265, value=233_200),
        StockItem(name="Colgate MaxFresh 150g", quantity=1420, unit="Pkt", rate=110, value=156_200),
    ]


def mock_receivables() -> list[OutstandingEntry]:
    return [
        OutstandingEntry(party="Reliance Retail Ltd", amount=820_000, aging_bucket="0-30"),
        OutstandingEntry(party="DMart Wholesale", amount=645_000, aging_bucket="0-30"),
        OutstandingEntry(party="Metro Cash & Carry", amount=512_500, aging_bucket="31-60"),
        OutstandingEntry(party="Spencer's Retail", amount=380_000, aging_bucket="31-60"),
        OutstandingEntry(party="More Supermarkets", amount=295_000, aging_bucket="61-90"),
        OutstandingEntry(party="Star Bazaar", amount=268_000, aging_bucket="61-90"),
        OutstandingEntry(party="Nilgiri's", amount=206_000, aging_bucket="90+"),
    ]


def mock_payables() -> list[OutstandingEntry]:
    return [
        OutstandingEntry(party="ITC Limited", amount=520_000, aging_bucket="0-30"),
        OutstandingEntry(party="Hindustan Unilever", amount=415_000, aging_bucket="0-30"),
        OutstandingEntry(party="Nestle India", amount=312_400, aging_bucket="31-60"),
        OutstandingEntry(party="Britannia Industries", amount=245_000, aging_bucket="31-60"),
        OutstandingEntry(party="Parle Products", amount=198_000, aging_bucket="61-90"),
        OutstandingEntry(party="Dabur India", amount=182_000, aging_bucket="90+"),
    ]


def mock_recent_vouchers() -> list[VoucherEntry]:
    today = date.today()
    data = [
        (0, "SAL/2526/1201", "Sales", "Reliance Retail Ltd", 184_300, "Invoice raised"),
        (0, "PUR/2526/0842", "Purchase", "ITC Limited", 96_500, "GRN received"),
        (1, "RCP/2526/0455", "Receipt", "DMart Wholesale", 325_000, "Bank credit"),
        (1, "PAY/2526/0382", "Payment", "Hindustan Unilever", 150_000, "Vendor payout"),
        (2, "SAL/2526/1200", "Sales", "Metro Cash & Carry", 212_800, "Invoice raised"),
        (2, "JRN/2526/0078", "Journal", "Depreciation", 42_000, "Monthly depreciation"),
        (3, "SAL/2526/1199", "Sales", "Spencer's Retail", 138_900, "Invoice raised"),
        (3, "CNT/2526/0034", "Contra", "Bank Transfer", 500_000, "HDFC to ICICI"),
    ]
    return [
        VoucherEntry(
            date=today - timedelta(days=days_ago),
            voucher_number=num,
            voucher_type=vtype,
            party=party,
            amount=amount,
            narration=narration,
        )
        for (days_ago, num, vtype, party, amount, narration) in data
    ]


def mock_ledgers() -> list[LedgerBalance]:
    return [
        LedgerBalance(name="Cash-in-Hand", parent="Current Assets", opening_balance=500_000, closing_balance=420_110),
        LedgerBalance(name="HDFC Bank A/c", parent="Bank Accounts", opening_balance=2_800_000, closing_balance=3_150_000),
        LedgerBalance(name="ICICI Bank A/c", parent="Bank Accounts", opening_balance=1_200_000, closing_balance=1_250_000),
        LedgerBalance(name="Sundry Debtors", parent="Current Assets", opening_balance=2_400_000, closing_balance=3_126_500),
        LedgerBalance(name="Sundry Creditors", parent="Current Liabilities", opening_balance=-1_500_000, closing_balance=-1_872_400),
        LedgerBalance(name="Sales Accounts", parent="Revenue", opening_balance=0, closing_balance=-18_742_350),
        LedgerBalance(name="Purchase Accounts", parent="Expenses", opening_balance=0, closing_balance=12_305_180),
        LedgerBalance(name="Rent", parent="Indirect Expenses", opening_balance=0, closing_balance=480_000),
        LedgerBalance(name="Salaries", parent="Indirect Expenses", opening_balance=0, closing_balance=2_160_000),
        LedgerBalance(name="Electricity", parent="Indirect Expenses", opening_balance=0, closing_balance=186_000),
    ]


def mock_trial_balance() -> list[TrialBalanceRow]:
    return [
        TrialBalanceRow(name="Cash-in-Hand", parent="Current Assets", debit=420_110, credit=0),
        TrialBalanceRow(name="HDFC Bank A/c", parent="Bank Accounts", debit=3_150_000, credit=0),
        TrialBalanceRow(name="ICICI Bank A/c", parent="Bank Accounts", debit=1_250_000, credit=0),
        TrialBalanceRow(name="Sundry Debtors", parent="Current Assets", debit=3_126_500, credit=0),
        TrialBalanceRow(name="Stock-in-Hand", parent="Current Assets", debit=6_430_900, credit=0),
        TrialBalanceRow(name="Sundry Creditors", parent="Current Liabilities", debit=0, credit=1_872_400),
        TrialBalanceRow(name="Capital Account", parent="Capital Account", debit=0, credit=8_000_000),
        TrialBalanceRow(name="Sales", parent="Revenue", debit=0, credit=18_742_350),
        TrialBalanceRow(name="Purchases", parent="Expenses", debit=12_305_180, credit=0),
        TrialBalanceRow(name="Salaries", parent="Indirect Expenses", debit=2_160_000, credit=0),
        TrialBalanceRow(name="Rent", parent="Indirect Expenses", debit=480_000, credit=0),
        TrialBalanceRow(name="Electricity", parent="Indirect Expenses", debit=186_000, credit=0),
        TrialBalanceRow(name="Freight & Transport", parent="Direct Expenses", debit=312_060, credit=0),
    ]


def mock_profit_loss() -> ProfitLoss:
    revenue = [
        ProfitLossSection(name="Sales Accounts", amount=18_742_350),
        ProfitLossSection(name="Other Income", amount=215_400),
    ]
    expenses = [
        ProfitLossSection(name="Purchase Accounts", amount=12_305_180),
        ProfitLossSection(name="Direct Expenses", amount=312_060),
        ProfitLossSection(name="Salaries", amount=2_160_000),
        ProfitLossSection(name="Rent", amount=480_000),
        ProfitLossSection(name="Electricity", amount=186_000),
        ProfitLossSection(name="Other Indirect Expenses", amount=412_000),
    ]
    total_rev = sum(r.amount for r in revenue)
    total_exp = sum(e.amount for e in expenses)
    gross_profit = revenue[0].amount - expenses[0].amount - expenses[1].amount
    return ProfitLoss(
        revenue=revenue,
        expenses=expenses,
        gross_profit=gross_profit,
        net_profit=total_rev - total_exp,
    )


def mock_balance_sheet() -> BalanceSheet:
    assets = [
        BalanceSheetSection(name="Fixed Assets", amount=4_200_000),
        BalanceSheetSection(name="Stock-in-Hand", amount=6_430_900),
        BalanceSheetSection(name="Sundry Debtors", amount=3_126_500),
        BalanceSheetSection(name="Cash & Bank", amount=4_820_110),
    ]
    liabilities = [
        BalanceSheetSection(name="Capital Account", amount=8_000_000),
        BalanceSheetSection(name="Reserves & Surplus", amount=6_825_110),
        BalanceSheetSection(name="Sundry Creditors", amount=1_872_400),
        BalanceSheetSection(name="Other Current Liabilities", amount=1_880_000),
    ]
    return BalanceSheet(
        assets=assets,
        liabilities=liabilities,
        total_assets=sum(a.amount for a in assets),
        total_liabilities=sum(l.amount for l in liabilities),
    )


def mock_dashboard() -> DashboardPayload:
    return DashboardPayload(
        company=mock_company(),
        kpis=mock_kpis(),
        sales_trend=mock_sales_trend(),
        purchase_trend=mock_purchase_trend(),
        top_customers=mock_top_customers(),
        top_suppliers=mock_top_suppliers(),
        top_stock_items=mock_stock_items(),
        receivables=mock_receivables(),
        payables=mock_payables(),
        recent_vouchers=mock_recent_vouchers(),
    )
