import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  ShoppingCart,
  Package,
  Wallet,
  BookOpen,
  Scale,
  Settings as SettingsIcon,
} from 'lucide-react';
import ConnectionBadge from './ConnectionBadge';

const nav = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/sales', label: 'Sales', icon: TrendingUp },
  { to: '/purchases', label: 'Purchases', icon: ShoppingCart },
  { to: '/stock', label: 'Stock', icon: Package },
  { to: '/outstanding', label: 'Outstanding', icon: Wallet },
  { to: '/ledgers', label: 'Ledgers', icon: BookOpen },
  { to: '/financials', label: 'Financials', icon: Scale },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
];

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 border-r border-white/5 bg-surface-card/60 backdrop-blur px-4 py-5 flex flex-col gap-6">
        <div>
          <div className="text-lg font-semibold tracking-tight flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-brand"></span>
            Tally&nbsp;<span className="text-brand">Dashboard</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">Live ODBC / XML connector</p>
        </div>
        <nav className="flex flex-col gap-1">
          {nav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition ${
                  isActive
                    ? 'bg-brand/15 text-white border border-brand/30'
                    : 'text-slate-300 hover:bg-white/5 border border-transparent'
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto text-[11px] text-slate-500 leading-relaxed">
          <p className="font-medium text-slate-400">Tip</p>
          <p>Enable Tally's ODBC server on port 9000, then set the URL in Settings.</p>
        </div>
      </aside>
      <main className="flex-1 min-w-0">
        <header className="sticky top-0 z-10 bg-surface/80 backdrop-blur border-b border-white/5 px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Business Intelligence</h1>
            <p className="text-xs text-slate-400">
              Live insights from your TallyPrime / Tally ERP 9 data
            </p>
          </div>
          <ConnectionBadge />
        </header>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
