import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { fetchBalanceSheet, fetchProfitLoss, fetchTrialBalance } from '../lib/api';
import { useAsync } from '../hooks/useAsync';
import { formatCompact, formatInr } from '../lib/format';
import { Card } from '../components/Card';
import Loading from '../components/Loading';
import DataModeBanner from '../components/DataModeBanner';

export default function Financials() {
  const pl = useAsync(fetchProfitLoss, []);
  const bs = useAsync(fetchBalanceSheet, []);
  const tb = useAsync(fetchTrialBalance, []);

  if (pl.loading || bs.loading || tb.loading) return <Loading />;
  if (pl.error || bs.error || tb.error || !pl.data || !bs.data || !tb.data) {
    return (
      <p className="text-accent-rose">
        Failed: {(pl.error ?? bs.error ?? tb.error)?.message}
      </p>
    );
  }

  const anyLive = pl.data.used_live_data || bs.data.used_live_data || tb.data.used_live_data;

  return (
    <div className="flex flex-col gap-6">
      <DataModeBanner usedLive={anyLive} />
      <h2 className="text-2xl font-semibold">Financials</h2>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card title="Profit & Loss" subtitle="Current financial year">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={[
                  { name: 'Revenue', amount: pl.data.data.revenue.reduce((s, r) => s + r.amount, 0) },
                  { name: 'Expenses', amount: pl.data.data.expenses.reduce((s, e) => s + e.amount, 0) },
                  { name: 'Net Profit', amount: pl.data.data.net_profit },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => formatCompact(v)} />
                <Tooltip
                  contentStyle={{ background: '#121a33', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}
                  formatter={(v: number) => formatInr(v)}
                />
                <Bar dataKey="amount" fill="#5b8cff" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <Stat label="Gross Profit" value={pl.data.data.gross_profit} />
            <Stat label="Net Profit" value={pl.data.data.net_profit} />
          </div>
        </Card>

        <Card title="Balance Sheet" subtitle="Assets vs liabilities">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={[
                  { name: 'Assets', amount: bs.data.data.total_assets },
                  { name: 'Liabilities', amount: bs.data.data.total_liabilities },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => formatCompact(v)} />
                <Tooltip
                  contentStyle={{ background: '#121a33', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}
                  formatter={(v: number) => formatInr(v)}
                />
                <Bar dataKey="amount" fill="#3ed6a8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <Stat label="Total Assets" value={bs.data.data.total_assets} />
            <Stat label="Total Liabilities" value={bs.data.data.total_liabilities} />
          </div>
        </Card>
      </div>

      <Card title="Trial Balance" subtitle="Debit / Credit across all ledgers">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 uppercase tracking-wider text-[11px] border-b border-white/5">
                <th className="py-2 pr-4 font-medium">Ledger</th>
                <th className="py-2 pl-4 font-medium text-right">Debit</th>
                <th className="py-2 pl-4 font-medium text-right">Credit</th>
              </tr>
            </thead>
            <tbody>
              {tb.data.data.map((row, i) => (
                <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-2 pr-4 font-medium">{row.name}</td>
                  <td className="py-2 pl-4 text-right tabular-nums">{row.debit ? formatInr(row.debit) : '—'}</td>
                  <td className="py-2 pl-4 text-right tabular-nums">{row.credit ? formatInr(row.credit) : '—'}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t border-white/10 text-slate-200 font-semibold">
                <td className="py-2 pr-4">Total</td>
                <td className="py-2 pl-4 text-right tabular-nums">
                  {formatInr(tb.data.data.reduce((s, r) => s + r.debit, 0))}
                </td>
                <td className="py-2 pl-4 text-right tabular-nums">
                  {formatInr(tb.data.data.reduce((s, r) => s + r.credit, 0))}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-white/5 bg-surface-soft/60 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wider text-slate-400">{label}</div>
      <div className="text-base font-semibold tabular-nums">{formatInr(value)}</div>
    </div>
  );
}
