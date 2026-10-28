import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, loading, logout } = useAuth();
  return (
    <nav aria-label="Navigation principale">
      <Link className="brand" to="/">⚽ Football QA</Link>
      <div className="navlinks">
        <Link to="/championships">Championnats</Link>
        {!loading && user && <Link data-testid="favorites-link" to="/favorites">Mes favoris</Link>}
        {!loading && user && <span className="nav-user">👤 {user.name}</span>}
        {!loading && (user
          ? <button type="button" onClick={logout}>Déconnexion</button>
          : <Link data-testid="login-button" className="primary small" to="/login">Connexion</Link>)}
      </div>
    </nav>
  );
}
