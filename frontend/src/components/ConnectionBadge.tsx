import { useEffect, useState } from 'react';
import { Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { fetchConnection } from '../lib/api';
import type { ConnectionStatus } from '../lib/types';

export default function ConnectionBadge() {
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    setLoading(true);
    try {
      setStatus(await fetchConnection());
    } catch (err) {
      setStatus({
        ok: false,
        url: '',
        company: null,
        error: (err as Error).message,
        latency_ms: null,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 15_000);
    return () => clearInterval(id);
  }, []);

  if (loading && !status) {
    return (
      <div className="pill bg-white/5 text-slate-300 border border-white/10">
        <Activity size={14} /> Checking Tally…
      </div>
    );
  }

  if (status?.ok) {
    return (
      <div className="pill bg-accent-mint/15 text-accent-mint border border-accent-mint/30">
        <CheckCircle2 size={14} /> Live · {status.company ?? 'Tally connected'}
        {status.latency_ms !== null && (
          <span className="text-accent-mint/70">· {status.latency_ms.toFixed(0)}ms</span>
        )}
      </div>
    );
  }

  return (
    <div className="pill bg-accent-gold/15 text-accent-gold border border-accent-gold/30" title={status?.error ?? ''}>
      <AlertTriangle size={14} /> Demo mode · Tally unreachable
    </div>
  );
}
