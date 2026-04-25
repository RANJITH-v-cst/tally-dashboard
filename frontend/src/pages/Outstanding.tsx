import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { fetchDashboard } from '../lib/api';
import { useAsync } from '../hooks/useAsync';
import { formatCompact, formatInr } from '../lib/format';
import { Card } from '../components/Card';
import Loading from '../components/Loading';
import DataModeBanner from '../components/DataModeBanner';
import type { OutstandingEntry } from '../lib/types';

const buckets: Array<OutstandingEntry['aging_bucket']> = ['0-30', '31-60', '61-90', '90+'];

function aging(entries: OutstandingEntry[]) {
  return buckets.map((bucket) => ({
    bucket,
    amount: entries.filter((e) => e.aging_bucket === bucket).reduce((s, e) => s + e.amount, 0),
  }));
}

export default function Outstanding() {
  const { data, loading, error } = useAsync(fetchDashboard, []);
  if (loading) return <Loading />;
  if (error || !data) return <p className="text-accent-rose">Failed: {error?.message}</p>;
  const { data: d, used_live_data } = data;
  const receivableTotal = d.receivables.reduce((s, e) => s + e.amount, 0);
  const payableTotal = d.payables.reduce((s, e) => s + e.amount, 0);

  return (
    <div className="flex flex-col gap-6">
      <DataModeBanner usedLive={used_live_data} />
      <div>
        <h2 className="text-2xl font-semibold">Outstanding</h2>
        <p className="text-sm text-slate-400">
          Receivables: <span className="text-accent-mint font-medium">{formatInr(receivableTotal)}</span> ·
          Payables: <span className="text-accent-gold font-medium">{formatInr(payableTotal)}</span>
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <AgingCard title="Receivables aging" data={aging(d.receivables)} color="#3ed6a8" />
        <AgingCard title="Payables aging" data={aging(d.payables)} color="#f4c95d" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <PartyTable title="Receivables by party" entries={d.receivables} />
        <PartyTable title="Payables by party" entries={d.payables} />
      </div>
    </div>
  );
}

function AgingCard({ title, data, color }: { title: string; data: Array<{ bucket: string; amount: number }>; color: string }) {
  return (
    <Card title={title} subtitle="Amount by aging bucket">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="bucket" stroke="#9aa4c0" fontSize={11} tickLine={false} axisLine={false} />
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
            <Bar dataKey="amount" fill={color} radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

function PartyTable({ title, entries }: { title: string; entries: OutstandingEntry[] }) {
  return (
    <Card title={title}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-400 uppercase tracking-wider text-[11px] border-b border-white/5">
              <th className="py-2 pr-4 font-medium">Party</th>
              <th className="py-2 pr-4 font-medium">Aging</th>
              <th className="py-2 pl-4 font-medium text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e, i) => (
              <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                <td className="py-2 pr-4">{e.party}</td>
                <td className="py-2 pr-4">
                  <span className="pill bg-white/5 text-slate-300">{e.aging_bucket}</span>
                </td>
                <td className="py-2 pl-4 text-right tabular-nums font-medium">{formatInr(e.amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
