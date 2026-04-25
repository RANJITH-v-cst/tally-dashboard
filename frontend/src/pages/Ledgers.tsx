import { useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import { fetchLedgers } from '../lib/api';
import { useAsync } from '../hooks/useAsync';
import { formatInr } from '../lib/format';
import { Card } from '../components/Card';
import Loading from '../components/Loading';
import DataModeBanner from '../components/DataModeBanner';

export default function Ledgers() {
  const { data, loading, error } = useAsync(fetchLedgers, []);
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => {
    if (!data) return [];
    const q = query.toLowerCase().trim();
    if (!q) return data.data;
    return data.data.filter(
      (l) => l.name.toLowerCase().includes(q) || l.parent.toLowerCase().includes(q),
    );
  }, [data, query]);

  if (loading) return <Loading />;
  if (error || !data) return <p className="text-accent-rose">Failed: {error?.message}</p>;

  return (
    <div className="flex flex-col gap-6">
      <DataModeBanner usedLive={data.used_live_data} />
      <div className="flex items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Ledgers</h2>
          <p className="text-sm text-slate-400">
            {data.data.length} ledgers · search by name or group
          </p>
        </div>
        <div className="relative w-80 max-w-full">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            className="input pl-9"
            placeholder="Search ledgers…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 uppercase tracking-wider text-[11px] border-b border-white/5">
                <th className="py-2 pr-4 font-medium">Ledger</th>
                <th className="py-2 pr-4 font-medium">Group</th>
                <th className="py-2 pl-4 font-medium text-right">Opening</th>
                <th className="py-2 pl-4 font-medium text-right">Closing</th>
                <th className="py-2 pl-4 font-medium text-right">Movement</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((l, i) => {
                const delta = l.closing_balance - l.opening_balance;
                return (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-2 pr-4 font-medium">{l.name}</td>
                    <td className="py-2 pr-4 text-slate-400">{l.parent}</td>
                    <td className="py-2 pl-4 text-right tabular-nums">{formatInr(l.opening_balance)}</td>
                    <td className="py-2 pl-4 text-right tabular-nums font-medium">{formatInr(l.closing_balance)}</td>
                    <td
                      className={`py-2 pl-4 text-right tabular-nums ${
                        delta > 0 ? 'text-accent-mint' : delta < 0 ? 'text-accent-rose' : 'text-slate-400'
                      }`}
                    >
                      {delta >= 0 ? '+' : ''}
                      {formatInr(delta)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <p className="text-center text-slate-500 text-sm py-8">No ledgers match "{query}".</p>
          )}
        </div>
      </Card>
    </div>
  );
}
