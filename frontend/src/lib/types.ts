export interface CompanyInfo {
  name: string;
  financial_year_start: string | null;
  books_begin_from: string | null;
}

export interface KpiSummary {
  total_sales: number;
  total_purchases: number;
  receivables: number;
  payables: number;
  cash_and_bank: number;
  stock_value: number;
  currency: string;
}

export interface TrendPoint {
  period: string;
  amount: number;
}

export interface PartyAmount {
  name: string;
  amount: number;
}

export interface StockItem {
  name: string;
  quantity: number;
  unit: string;
  rate: number;
  value: number;
}

export type AgingBucket = '0-30' | '31-60' | '61-90' | '90+';

export interface OutstandingEntry {
  party: string;
  amount: number;
  aging_bucket: AgingBucket;
}

export interface LedgerBalance {
  name: string;
  parent: string;
  opening_balance: number;
  closing_balance: number;
}

export interface TrialBalanceRow {
  name: string;
  parent: string;
  debit: number;
  credit: number;
}

export interface VoucherEntry {
  date: string;
  voucher_number: string;
  voucher_type: string;
  party: string;
  amount: number;
  narration: string;
}

export interface ProfitLossSection {
  name: string;
  amount: number;
}

export interface ProfitLoss {
  revenue: ProfitLossSection[];
  expenses: ProfitLossSection[];
  gross_profit: number;
  net_profit: number;
}

export interface BalanceSheetSection {
  name: string;
  amount: number;
}

export interface BalanceSheet {
  assets: BalanceSheetSection[];
  liabilities: BalanceSheetSection[];
  total_assets: number;
  total_liabilities: number;
}

export interface DashboardPayload {
  company: CompanyInfo;
  kpis: KpiSummary;
  sales_trend: TrendPoint[];
  purchase_trend: TrendPoint[];
  top_customers: PartyAmount[];
  top_suppliers: PartyAmount[];
  top_stock_items: StockItem[];
  receivables: OutstandingEntry[];
  payables: OutstandingEntry[];
  recent_vouchers: VoucherEntry[];
}

export interface ConnectionStatus {
  ok: boolean;
  url: string;
  company: string | null;
  error: string | null;
  latency_ms: number | null;
}

export interface WrappedResponse<T> {
  data: T;
  used_live_data: boolean;
}
