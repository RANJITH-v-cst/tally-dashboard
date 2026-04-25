import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { fetchDashboard } from '../lib/api';
import { useAsync } from '../hooks/useAsync';
import { formatCompact, formatInr, formatPeriodLabel } from '../lib/format';
import { Card } from '../components/Card';
import Loading from '../components/Loading';
import DataModeBanner from '../components/DataModeBanner';

export default function Sales() {
  const { data, loading, error } = useAsync(fetchDashboard, []);
  if (loading) return <Loading />;
  if (error || !data) return <p className="text-accent-rose">Failed: {error?.message}</p>;
  const { data: d, used_live_data } = data;
  const total = d.sales_trend.reduce((s, t) => s + t.amount, 0);
  const trend = d.sales_trend.map((t) => ({ ...t, period: formatPeriodLabel(t.period) }));

  return (
    <div className="flex flex-col gap-6">
      <DataModeBanner usedLive={used_live_data} />
      <div>
        <h2 className="text-2xl font-semibold">Sales</h2>
        <p className="text-sm text-slate-400">
          Total sales (last 12 months): <span className="text-slate-200 font-medium">{formatInr(total)}</span>
        </p>
      </div>

      <Card title="Monthly sales trend" subtitle="Revenue over time">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="period" stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis
                stroke="#9aa4c0"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => formatCompact(v)}
              />
              <Tooltip
                contentStyle={{ background: '#121a33', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}
                labelStyle={{ color: '#cbd5e1' }}
                formatter={(v: number) => formatInr(v)}
              />
              <Line type="monotone" dataKey="amount" stroke="#3ed6a8" strokeWidth={2.5} dot={{ fill: '#3ed6a8', r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="Top customers" subtitle="By revenue contribution">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={d.top_customers}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="name" stroke="#9aa4c0" fontSize={10} tickLine={false} axisLine={false} interval={0} angle={-15} dy={8} height={60} />
              <YAxis
                stroke="#9aa4c0"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => formatCompact(v)}
              />
              <Tooltip
                contentStyle={{ background: '#121a33', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}
                formatter={(v: number) => formatInr(v)}
              />
              <Bar dataKey="amount" fill="#3ed6a8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
