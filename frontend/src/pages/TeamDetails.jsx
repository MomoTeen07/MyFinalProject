import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api/client';
import TeamCrest from '../components/TeamCrest';
import { useAuth } from '../context/AuthContext';

export default function TeamDetails() {
  const { code, id } = useParams();
  const { user } = useAuth();
  const [team, setTeam] = useState(null);
  const [favorite, setFavorite] = useState(null);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const loadTeam = useCallback(async (signal) => {
    setStatus('loading');
    setError('');
    try {
      const result = await api(`/api/football/leagues/${code}/teams/${id}`, { signal });
      setTeam(result);
      setStatus('success');
    } catch (requestError) {
      if (requestError.name === 'AbortError') return;
      setError(requestError.message);
      setStatus('error');
    }
  }, [code, id]);

  useEffect(() => {
    const controller = new AbortController();
    setTeam(null);
    setFavorite(null);
    loadTeam(controller.signal);
    return () => controller.abort();
  }, [loadTeam]);

  useEffect(() => {
    if (!user) { setFavorite(null); return; }
    let active = true;
    api('/api/favorites')
      .then((items) => { if (active) setFavorite(items.find((item) => item.team_id === Number(id)) || null); })
      .catch((requestError) => { if (active) setError(requestError.message); });
    return () => { active = false; };
  }, [user, id]);

  const toggleFavorite = async () => {
    setSaving(true);
    setError('');
    try {
      if (favorite) {
        await api(`/api/favorites/${favorite.id}`, { method: 'DELETE' });
        setFavorite(null);
      } else {
        const created = await api('/api/favorites', {
          method: 'POST',
          body: JSON.stringify({ team_id: team.id, league_code: code, team_name: team.name, team_crest: team.crest || null }),
        });
        setFavorite(created);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  if (status === 'loading') return <p className="notice" role="status">Chargement de l’équipe…</p>;
  if (status === 'error') return <section><Link to={`/championships/${code}`} className="back">← Retour au championnat</Link><div className="error" role="alert">{error}</div><button className="primary" onClick={() => loadTeam()}>Réessayer</button></section>;

  return (
    <section>
      <Link to={`/championships/${code}`} className="back">← Retour au championnat</Link>
      <div className="team-header card">
        <TeamCrest src={team.crest} name={team.name} />
        <div><span className="eyebrow">ÉQUIPE</span><h1>{team.name}</h1><p>{team.venue || 'Stade non renseigné'}</p></div>
        {user && <button data-testid="favorite-button" disabled={saving} className={favorite ? 'favorite active' : 'favorite'} onClick={toggleFavorite}>
          {saving ? 'Mise à jour…' : favorite ? '★ Dans mes favoris' : '☆ Ajouter aux favoris'}
        </button>}
      </div>
      {!user && <div className="notice">Connecte-toi pour gérer tes favoris. <Link to="/login">Connexion</Link></div>}
      {error && <div className="error" role="alert">{error}</div>}
    </section>
  );
}
