import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Sales from './pages/Sales';
import Purchases from './pages/Purchases';
import Stock from './pages/Stock';
import Outstanding from './pages/Outstanding';
import Ledgers from './pages/Ledgers';
import Financials from './pages/Financials';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="sales" element={<Sales />} />
        <Route path="purchases" element={<Purchases />} />
        <Route path="stock" element={<Stock />} />
        <Route path="outstanding" element={<Outstanding />} />
        <Route path="ledgers" element={<Ledgers />} />
        <Route path="financials" element={<Financials />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
