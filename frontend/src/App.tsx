import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Sales from './pages/Sales';
import Purchases from './pages/Purchases';
import Stock from './pages/Stock';
import Outstanding from './pages/Outstanding';
import Ledgers from './pages/Ledgers';
import Financials from './pages/Financials';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Loading from './components/Loading';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  const { user, loading } = useAuth();

  if (loading) return <Loading />;

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
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
