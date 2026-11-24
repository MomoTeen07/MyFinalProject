import { BrowserRouter, Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import Home from './pages/Home';
import Championships from './pages/Championships';
import Championship from './pages/Championship';
import TeamDetails from './pages/TeamDetails';
import MatchDetails from './pages/MatchDetails';
import Favorites from './pages/Favorites';
import Auth from './pages/Auth';

function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <p className="notice">Chargement de ta session…</p>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return children;
}

function AppRoutes() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/championships" element={<Championships />} />
        <Route path="/championships/:code" element={<Championship />} />
        <Route path="/teams/:code/:id" element={<TeamDetails />} />
        <Route path="/matches/:id" element={<MatchDetails />} />
        <Route path="/favorites" element={<RequireAuth><Favorites /></RequireAuth>} />
        <Route path="/login" element={<Auth />} />
        <Route path="/register" element={<Auth register />} />
        <Route path="*" element={<section><h1>Page introuvable</h1><Link className="back" to="/">Retour à l’accueil</Link></section>} />
      </Routes>
    </MainLayout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
