import { fetchDashboard } from '../lib/api';
import { useAsync } from '../hooks/useAsync';
import { formatInr, formatNumber } from '../lib/format';
import { Card } from '../components/Card';
import Loading from '../components/Loading';
import DataModeBanner from '../components/DataModeBanner';

export default function Stock() {
  const { data, loading, error } = useAsync(fetchDashboard, []);
  if (loading) return <Loading />;
  if (error || !data) return <p className="text-accent-rose">Failed: {error?.message}</p>;
  const { data: d, used_live_data } = data;
  const totalValue = d.top_stock_items.reduce((s, i) => s + i.value, 0);

  return (
    <div className="flex flex-col gap-6">
      <DataModeBanner usedLive={used_live_data} />
      <div>
        <h2 className="text-2xl font-semibold">Stock</h2>
        <p className="text-sm text-slate-400">
          Top items by value · total closing value{' '}
          <span className="text-slate-200 font-medium">{formatInr(totalValue)}</span>
        </p>
      </div>

      <Card title="Stock Summary">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 uppercase tracking-wider text-[11px] border-b border-white/5">
                <th className="py-2 pr-4 font-medium">Item</th>
                <th className="py-2 pr-4 font-medium">Unit</th>
                <th className="py-2 pl-4 font-medium text-right">Quantity</th>
                <th className="py-2 pl-4 font-medium text-right">Rate</th>
                <th className="py-2 pl-4 font-medium text-right">Closing value</th>
                <th className="py-2 pl-4 font-medium text-right">Share</th>
              </tr>
            </thead>
            <tbody>
              {d.top_stock_items.map((item, i) => (
                <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-2 pr-4 font-medium">{item.name}</td>
                  <td className="py-2 pr-4 text-slate-400">{item.unit}</td>
                  <td className="py-2 pl-4 text-right tabular-nums">{formatNumber(item.quantity)}</td>
                  <td className="py-2 pl-4 text-right tabular-nums">{formatInr(item.rate)}</td>
                  <td className="py-2 pl-4 text-right tabular-nums font-medium">{formatInr(item.value)}</td>
                  <td className="py-2 pl-4 text-right tabular-nums text-slate-400">
                    {((item.value / totalValue) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
