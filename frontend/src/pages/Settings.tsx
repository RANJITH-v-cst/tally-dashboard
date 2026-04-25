import { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, Plug, XCircle } from 'lucide-react';
import { fetchConnection } from '../lib/api';
import { getTallyUrl, setTallyUrl } from '../lib/settings';
import type { ConnectionStatus } from '../lib/types';
import { Card } from '../components/Card';

export default function Settings() {
  const [url, setUrl] = useState(getTallyUrl());
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    setUrl(getTallyUrl());
  }, []);

  const save = () => {
    const normalized = url.trim().replace(/\/$/, '');
    setTallyUrl(normalized);
    setUrl(normalized);
  };

  const test = async () => {
    save();
    setTesting(true);
    try {
      setStatus(await fetchConnection());
    } catch (err) {
      setStatus({
        ok: false,
        url,
        company: null,
        error: (err as Error).message,
        latency_ms: null,
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <div>
        <h2 className="text-2xl font-semibold">Settings</h2>
        <p className="text-sm text-slate-400">Point the dashboard at your local Tally instance.</p>
      </div>

      <Card title="Tally connection" subtitle="URL of the TallyPrime / Tally ERP 9 HTTP gateway">
        <div className="flex flex-col gap-4">
          <div>
            <label className="text-xs uppercase tracking-wider text-slate-400">Tally URL</label>
            <div className="flex gap-2 mt-1.5">
              <input
                className="input"
                placeholder="http://localhost:9000"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <button className="btn-primary" onClick={test} disabled={testing}>
                {testing ? <Loader2 size={14} className="animate-spin" /> : <Plug size={14} />}
                Test
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-1.5">
              Leave blank to use the server default (the <code>TALLY_URL</code> env var).
            </p>
          </div>

          {status && (
            <div
              className={`rounded-lg border px-4 py-3 text-sm flex items-start gap-3 ${
                status.ok
                  ? 'border-accent-mint/30 bg-accent-mint/10 text-accent-mint'
                  : 'border-accent-rose/30 bg-accent-rose/10 text-accent-rose'
              }`}
            >
              {status.ok ? <CheckCircle2 size={16} className="mt-0.5" /> : <XCircle size={16} className="mt-0.5" />}
              <div>
                <p className="font-medium">
                  {status.ok ? `Connected to ${status.company ?? 'Tally'}` : 'Could not reach Tally'}
                </p>
                <p className="text-xs opacity-80 mt-0.5">
                  URL: <code>{status.url}</code>
                  {status.latency_ms !== null && ` · ${status.latency_ms.toFixed(0)} ms`}
                  {status.error && ` · ${status.error}`}
                </p>
              </div>
            </div>
          )}
        </div>
      </Card>

      <Card title="How to enable the Tally gateway">
        <ol className="list-decimal ml-5 space-y-2 text-sm text-slate-300">
          <li>Open TallyPrime (or Tally ERP 9) on the machine where your books live.</li>
          <li>
            Press <kbd className="pill bg-white/5">F1</kbd> → <em>Settings</em> →{' '}
            <em>Connectivity</em> → <em>Client/Server configuration</em>.
          </li>
          <li>
            Set <em>TallyPrime acts as</em> to <strong>Both</strong>, Port to <strong>9000</strong>.
          </li>
          <li>Accept and keep TallyPrime running while using this dashboard.</li>
          <li>
            Confirm the gateway is up by opening <code>http://localhost:9000</code> in a browser — you
            should see <em>"TallyPrime Server is Running"</em>.
          </li>
        </ol>
      </Card>
    </div>
  );
}
