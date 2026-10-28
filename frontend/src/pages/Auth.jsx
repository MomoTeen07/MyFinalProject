import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Auth({ register = false }) {
  const { login, register: signup } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      if (register) await signup(name, email, password);
      else await login(email, password);
      navigate(location.state?.from || '/championships', { replace: true });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="auth">
      <div className="auth-card">
        <span className="eyebrow">FOOTBALL QA</span>
        <h1>{register ? 'Créer un compte' : 'Connexion'}</h1>
        <p className="muted">{register ? 'Commence à suivre tes équipes.' : 'Accède à tes équipes favorites.'}</p>
        <form onSubmit={submit}>
          {register && <label>Nom<input autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} required minLength="2" maxLength="100" /></label>}
          <label>Adresse e-mail<input data-testid="email-input" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
          <label>Mot de passe<input data-testid="password-input" type="password" autoComplete={register ? 'new-password' : 'current-password'} value={password} onChange={(event) => setPassword(event.target.value)} required minLength="8" maxLength={register ? 128 : 1024} /></label>
          <button data-testid="submit-login" className="primary" type="submit" disabled={submitting}>
            {submitting ? 'Connexion…' : register ? 'Créer mon compte' : 'Se connecter'}
          </button>
        </form>
        {error && <div className="error" role="alert">{error}</div>}
        <p className="switch">{register ? 'Déjà inscrit ? ' : 'Pas encore de compte ? '}<Link to={register ? '/login' : '/register'}>{register ? 'Se connecter' : 'Créer un compte'}</Link></p>
      </div>
    </section>
  );
}
