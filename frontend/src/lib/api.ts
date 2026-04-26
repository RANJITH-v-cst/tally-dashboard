import axios from 'axios';
import { getTallyUrl } from './settings';
import type {
  BalanceSheet,
  ConnectionStatus,
  DashboardPayload,
  LedgerBalance,
  ProfitLoss,
  TrialBalanceRow,
  WrappedResponse,
} from './types';

const baseURL = import.meta.env.VITE_API_URL ?? '/api';

const http = axios.create({ baseURL, timeout: 30_000 });

http.interceptors.request.use((config) => {
  const url = getTallyUrl();
  if (url) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>)['X-Tally-Url'] = url;
  }
  return config;
});

export async function fetchConnection(): Promise<ConnectionStatus> {
  const { data } = await http.get<ConnectionStatus>('/connection');
  return data;
}

export async function fetchDashboard(): Promise<WrappedResponse<DashboardPayload>> {
  const { data } = await http.get<WrappedResponse<DashboardPayload>>('/dashboard');
  return data;
}

export async function fetchLedgers(): Promise<WrappedResponse<LedgerBalance[]>> {
  const { data } = await http.get<WrappedResponse<LedgerBalance[]>>('/ledgers');
  return data;
}

export async function fetchTrialBalance(): Promise<WrappedResponse<TrialBalanceRow[]>> {
  const { data } = await http.get<WrappedResponse<TrialBalanceRow[]>>('/trial-balance');
  return data;
}

export async function fetchProfitLoss(): Promise<WrappedResponse<ProfitLoss>> {
  const { data } = await http.get<WrappedResponse<ProfitLoss>>('/profit-loss');
  return data;
}

export async function fetchBalanceSheet(): Promise<WrappedResponse<BalanceSheet>> {
  const { data } = await http.get<WrappedResponse<BalanceSheet>>('/balance-sheet');
  return data;
}

export interface DiagnosticStep {
  label: string;
  ok: boolean;
  row_count: number;
  sample: unknown[];
  raw_preview: string;
  envelope_preview: string;
  error: string | null;
}

export interface DiagnosticReport {
  url: string;
  ping_ok: boolean;
  latency_ms: number | null;
  ping_error: string | null;
  company: string | null;
  steps: DiagnosticStep[];
}

export async function fetchDiagnostics(): Promise<DiagnosticReport> {
  const { data } = await http.get<DiagnosticReport>('/diagnostics');
  return data;
}
