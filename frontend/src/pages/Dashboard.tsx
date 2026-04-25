import {
  TrendingUp,
  TrendingDown,
  Wallet,
  Package,
  Landmark,
  Banknote,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { fetchDashboard } from '../lib/api';
import { useAsync } from '../hooks/useAsync';
import { formatCompact, formatDate, formatInr, formatPeriodLabel } from '../lib/format';
import { Card } from '../components/Card';
import KpiCard from '../components/KpiCard';
import Loading from '../components/Loading';
import DataModeBanner from '../components/DataModeBanner';

const pieColors = ['#5b8cff', '#3ed6a8', '#f4c95d', '#ff7d7d'];

export default function Dashboard() {
  const { data, loading, error } = useAsync(fetchDashboard, []);

  if (loading) return <Loading label="Fetching dashboard…" />;
  if (error || !data) return <p className="text-accent-rose">Failed to load: {error?.message}</p>;

  const { data: d, used_live_data } = data;

  const mergedTrend = d.sales_trend.map((s, i) => ({
    period: formatPeriodLabel(s.period),
    sales: s.amount,
    purchases: d.purchase_trend[i]?.amount ?? 0,
  }));

  const receivablesByBucket = aggregate(d.receivables);
  const payablesByBucket = aggregate(d.payables);

  return (
    <div className="flex flex-col gap-6">
      <DataModeBanner usedLive={used_live_data} />

      <div className="flex items-baseline justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">{d.company.name}</h2>
          <p className="text-sm text-slate-400">
            Financial overview · snapshot as of {formatDate(new Date().toISOString())}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard label="Total Sales" value={d.kpis.total_sales} icon={TrendingUp} accent="text-accent-mint" />
        <KpiCard label="Total Purchases" value={d.kpis.total_purchases} icon={TrendingDown} accent="text-accent-rose" />
        <KpiCard label="Receivables" value={d.kpis.receivables} icon={Wallet} accent="text-brand" />
        <KpiCard label="Payables" value={d.kpis.payables} icon={Banknote} accent="text-accent-gold" />
        <KpiCard label="Cash & Bank" value={d.kpis.cash_and_bank} icon={Landmark} accent="text-accent-violet" />
        <KpiCard label="Stock Value" value={d.kpis.stock_value} icon={Package} accent="text-brand-400" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <Card className="xl:col-span-2" title="Sales vs Purchases" subtitle="Monthly, last 12 months">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mergedTrend} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
                <defs>
                  <linearGradient id="gSales" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3ed6a8" stopOpacity={0.55} />
                    <stop offset="100%" stopColor="#3ed6a8" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id="gPur" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#5b8cff" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="#5b8cff" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="period" stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis
                  stroke="#9aa4c0"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => formatCompact(v)}
                />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: '#cbd5e1' }} />
                <Area type="monotone" dataKey="sales" name="Sales" stroke="#3ed6a8" fill="url(#gSales)" strokeWidth={2} />
                <Area type="monotone" dataKey="purchases" name="Purchases" stroke="#5b8cff" fill="url(#gPur)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Receivables aging" subtitle="Amount due by bucket">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={receivablesByBucket}
                  dataKey="amount"
                  nameKey="bucket"
                  innerRadius={52}
                  outerRadius={88}
                  paddingAngle={2}
                >
                  {receivablesByBucket.map((_, i) => (
                    <Cell key={i} fill={pieColors[i % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: '#cbd5e1' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card title="Top customers" subtitle="By net sales value">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={d.top_customers.slice(0, 7)} layout="vertical" margin={{ left: 8, right: 12 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis
                  type="number"
                  stroke="#9aa4c0"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => formatCompact(v)}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#9aa4c0"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  width={150}
                />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="amount" fill="#3ed6a8" radius={[4, 4, 4, 4]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Payables aging" subtitle="Amount owed by bucket">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={payablesByBucket}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="bucket" stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis
                  stroke="#9aa4c0"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => formatCompact(v)}
                />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="amount" fill="#f4c95d" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card title="Recent vouchers" subtitle="Latest Day Book entries">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 uppercase tracking-wider text-[11px] border-b border-white/5">
                <th className="py-2 pr-4 font-medium">Date</th>
                <th className="py-2 pr-4 font-medium">Voucher</th>
                <th className="py-2 pr-4 font-medium">Type</th>
                <th className="py-2 pr-4 font-medium">Party</th>
                <th className="py-2 pl-4 font-medium text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {d.recent_vouchers.map((v, i) => (
                <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-2 pr-4 text-slate-300">{formatDate(v.date)}</td>
                  <td className="py-2 pr-4 font-mono text-xs text-slate-200">{v.voucher_number}</td>
                  <td className="py-2 pr-4">
                    <span className="pill bg-white/5 text-slate-300">{v.voucher_type}</span>
                  </td>
                  <td className="py-2 pr-4">{v.party}</td>
                  <td className="py-2 pl-4 text-right tabular-nums font-medium">{formatInr(v.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function aggregate(entries: { aging_bucket: string; amount: number }[]) {
  const buckets = ['0-30', '31-60', '61-90', '90+'] as const;
  return buckets.map((bucket) => ({
    bucket,
    amount: entries.filter((e) => e.aging_bucket === bucket).reduce((s, e) => s + e.amount, 0),
  }));
}

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-white/10 bg-surface-card/95 px-3 py-2 text-xs shadow-card">
      {label && <div className="mb-1 text-slate-400">{label}</div>}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full" style={{ background: p.color ?? p.payload?.fill }} />
          <span className="text-slate-300">{p.name ?? p.dataKey}</span>
          <span className="ml-auto tabular-nums font-medium text-slate-100">{formatInr(p.value as number)}</span>
        </div>
      ))}
    </div>
  );
}
