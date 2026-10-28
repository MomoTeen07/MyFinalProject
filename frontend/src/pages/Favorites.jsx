import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import TeamCrest from '../components/TeamCrest';

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [deleting, setDeleting] = useState(null);

  const load = useCallback(async (signal) => {
    setError('');
    setStatus('loading');
    try {
      const result = await api('/api/favorites', { signal });
      setFavorites(Array.isArray(result) ? result : []);
      setStatus('success');
    } catch (requestError) {
      if (requestError.name === 'AbortError') return;
      setError(requestError.message);
      setStatus('error');
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal);
    return () => controller.abort();
  }, [load]);

  const remove = async (id) => {
    setDeleting(id);
    setError('');
    try {
      await api(`/api/favorites/${id}`, { method: 'DELETE' });
      setFavorites((current) => current.filter((favorite) => favorite.id !== id));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setDeleting(null);
    }
  };

  return (
    <section>
      <span className="eyebrow">ESPACE PERSONNEL</span>
      <h1>Mes favoris ⭐</h1>
      <p className="muted">Tes équipes favorites, conservées dans ton compte.</p>
      {error && <div className="error" role="alert">{error}</div>}
      {status === 'loading' && <p className="notice" role="status">Chargement de tes favoris…</p>}
      {status === 'error' && <button className="primary" onClick={() => load()}>Réessayer</button>}
      {status === 'success' && favorites.length === 0 && (
        <div className="empty card"><div>☆</div><h2>Aucune équipe favorite</h2><p>Ajoute une équipe depuis sa page de détail.</p><Link className="primary" to="/championships">Explorer les championnats</Link></div>
      )}
      {status === 'success' && favorites.length > 0 && (
        <div className="grid">
          {favorites.map((favorite) => (
            <div className="card fav" key={favorite.id}>
              <div>
                <TeamCrest src={favorite.team_crest} name={favorite.team_name} small />
                {favorite.league_code
                  ? <Link className="favorite-team" to={`/teams/${favorite.league_code}/${favorite.team_id}`}><h2>{favorite.team_name}</h2></Link>
                  : <h2>{favorite.team_name}</h2>}
              </div>
              <button disabled={deleting === favorite.id} onClick={() => remove(favorite.id)}>
                {deleting === favorite.id ? 'Suppression…' : 'Supprimer'}
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
