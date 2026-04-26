import { useEffect, useState } from 'react';
import { CheckCircle2, ChevronDown, ChevronRight, Loader2, Plug, Stethoscope, XCircle } from 'lucide-react';
import { fetchConnection, fetchDiagnostics, type DiagnosticReport } from '../lib/api';
import { getTallyUrl, setTallyUrl } from '../lib/settings';
import type { ConnectionStatus } from '../lib/types';
import { Card } from '../components/Card';

export default function Settings() {
  const [url, setUrl] = useState(getTallyUrl());
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [testing, setTesting] = useState(false);

  const [diag, setDiag] = useState<DiagnosticReport | null>(null);
  const [diagRunning, setDiagRunning] = useState(false);
  const [diagError, setDiagError] = useState<string | null>(null);
  const [openStep, setOpenStep] = useState<number | null>(null);

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

  const runDiagnostics = async () => {
    save();
    setDiagRunning(true);
    setDiagError(null);
    try {
      setDiag(await fetchDiagnostics());
    } catch (err) {
      setDiagError((err as Error).message);
    } finally {
      setDiagRunning(false);
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
                  {status.ok ? `Connected to ${status.company ?? 'Tally (no company loaded)'}` : 'Could not reach Tally'}
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

      <Card
        title="Diagnostics"
        subtitle="Run every Tally request and see exactly which calls return data"
      >
        <div className="flex flex-col gap-4">
          <button className="btn-primary self-start" onClick={runDiagnostics} disabled={diagRunning}>
            {diagRunning ? <Loader2 size={14} className="animate-spin" /> : <Stethoscope size={14} />}
            Why am I in demo mode?
          </button>

          {diagError && (
            <p className="text-sm text-accent-rose">{diagError}</p>
          )}

          {diag && (
            <div className="flex flex-col gap-3">
              <div className="rounded-lg bg-surface-2/50 border border-white/5 px-4 py-3 text-sm">
                <p>
                  Tally URL: <code>{diag.url}</code>{' '}
                  {diag.ping_ok ? (
                    <span className="text-accent-mint">· reachable</span>
                  ) : (
                    <span className="text-accent-rose">· unreachable</span>
                  )}
                  {diag.latency_ms !== null && ` (${diag.latency_ms.toFixed(0)} ms)`}
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Loaded company: <strong>{diag.company ?? '(none — no company loaded)'}</strong>
                </p>
                {diag.ping_error && (
                  <p className="text-xs text-accent-rose mt-1">{diag.ping_error}</p>
                )}
              </div>

              <div className="flex flex-col gap-2">
                {diag.steps.map((s, i) => (
                  <div key={s.label} className="rounded-lg border border-white/5 bg-surface-2/30">
                    <button
                      onClick={() => setOpenStep(openStep === i ? null : i)}
                      className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-white/5"
                    >
                      <span className="flex items-center gap-2">
                        {openStep === i ? (
                          <ChevronDown size={14} />
                        ) : (
                          <ChevronRight size={14} />
                        )}
                        {s.ok ? (
                          <CheckCircle2 size={14} className="text-accent-mint" />
                        ) : (
                          <XCircle size={14} className="text-accent-rose" />
                        )}
                        <span>{s.label}</span>
                      </span>
                      <span className="text-xs text-slate-400">
                        {s.ok ? `${s.row_count} rows` : 'failed'}
                      </span>
                    </button>
                    {openStep === i && (
                      <div className="px-4 py-3 border-t border-white/5 text-xs flex flex-col gap-2">
                        {s.error && (
                          <p className="text-accent-rose">{s.error}</p>
                        )}
                        <details>
                          <summary className="cursor-pointer text-slate-300">Request envelope</summary>
                          <pre className="mt-2 p-2 bg-black/40 rounded overflow-auto whitespace-pre-wrap text-[11px]">
                            {s.envelope_preview}
                          </pre>
                        </details>
                        {s.raw_preview && (
                          <details>
                            <summary className="cursor-pointer text-slate-300">Raw response (first 600 chars)</summary>
                            <pre className="mt-2 p-2 bg-black/40 rounded overflow-auto whitespace-pre-wrap text-[11px]">
                              {s.raw_preview}
                            </pre>
                          </details>
                        )}
                        {s.sample.length > 0 && (
                          <details>
                            <summary className="cursor-pointer text-slate-300">Parsed sample</summary>
                            <pre className="mt-2 p-2 bg-black/40 rounded overflow-auto text-[11px]">
                              {JSON.stringify(s.sample, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    )}
                  </div>
                ))}
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
          <li>
            Make sure a <strong>company is loaded</strong> (Gateway of Tally must be visible) — the
            HTTP gateway only serves data for the currently-loaded company.
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
