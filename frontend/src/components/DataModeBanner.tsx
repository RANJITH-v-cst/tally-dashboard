import { Info } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DataModeBanner({ usedLive }: { usedLive: boolean }) {
  if (usedLive) return null;
  return (
    <div className="mb-5 flex items-start gap-3 rounded-xl border border-accent-gold/30 bg-accent-gold/10 px-4 py-3 text-sm text-accent-gold">
      <Info size={16} className="mt-0.5 shrink-0" />
      <div className="leading-relaxed">
        <p className="font-medium">Showing demo data</p>
        <p className="text-accent-gold/80">
          Tally isn't reachable from this backend yet. Point the app at your Tally URL
          (default <code>http://localhost:9000</code>) in{' '}
          <Link to="/settings" className="underline underline-offset-2">
            Settings
          </Link>{' '}
          to see your real company data.
        </p>
      </div>
    </div>
  );
}
