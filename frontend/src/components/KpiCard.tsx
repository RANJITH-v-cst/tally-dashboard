import type { LucideIcon } from 'lucide-react';
import { formatCompact } from '../lib/format';

interface KpiCardProps {
  label: string;
  value: number;
  icon: LucideIcon;
  accent?: string;
  hint?: string;
}

export default function KpiCard({ label, value, icon: Icon, accent = 'text-brand', hint }: KpiCardProps) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wider text-slate-400">{label}</span>
        <span className={`p-2 rounded-lg bg-white/5 ${accent}`}>
          <Icon size={16} />
        </span>
      </div>
      <div className="mt-3 text-2xl font-semibold tabular-nums">{formatCompact(value)}</div>
      {hint && <p className="text-xs text-slate-500 mt-1">{hint}</p>}
    </div>
  );
}
