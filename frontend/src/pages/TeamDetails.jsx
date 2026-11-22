import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api/client';
import MatchRow from '../components/MatchRow';
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
  const favoriteMutation = useRef(0);
  const [overview, setOverview] = useState({ rank: null, recent: [], next: null });
  const [overviewStatus, setOverviewStatus] = useState('idle');
  const [overviewRequested, setOverviewRequested] = useState(false);

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
    setOverviewRequested(false);
    setOverviewStatus('idle');
    setOverview({ rank: null, recent: [], next: null });
    loadTeam(controller.signal);
    return () => controller.abort();
  }, [loadTeam]);

  useEffect(() => {
    if (!user) { setFavorite(null); return; }
    let active = true;
    const version = favoriteMutation.current;
    api('/api/favorites')
      .then((items) => {
        // Une réponse de lecture partie avant une mutation ne doit pas écraser
        // l'état optimiste du bouton favori.
        if (active && version === favoriteMutation.current) {
          setFavorite(items.find((item) => item.team_id === Number(id)) || null);
        }
      })
      .catch((requestError) => { if (active) setError(requestError.message); });
    return () => { active = false; };
  }, [user, id]);

  useEffect(() => {
    if (!team || !overviewRequested) return undefined;

    const controller = new AbortController();
    const signal = controller.signal;
    const load = (path) => api(path, { signal }).catch(() => null);

    setOverviewStatus('loading');
    Promise.all([
      load(`/api/football/leagues/${code}/standings`),
      load(`/api/football/leagues/${code}/matches?team_id=${team.id}&status=FINISHED&page_size=3&sort=date_desc`),
      load(`/api/football/fixtures?days=10&limit=1&team_id=${team.id}`),
    ]).then(([standings, recent, upcoming]) => {
      if (controller.signal.aborted) return;
      const row = Array.isArray(standings)
        ? standings.find((entry) => entry.team?.id === team.id)
        : null;
      setOverview({
        rank: row
          ? {
            position: row.position,
            points: row.points,
            playedGames: row.playedGames,
            form: row.form,
          }
          : null,
        recent: Array.isArray(recent?.items)
          ? [...recent.items].sort((a, b) => (b.utcDate || '').localeCompare(a.utcDate || ''))
          : [],
        next: Array.isArray(upcoming?.items) && upcoming.items.length > 0 ? upcoming.items[0] : null,
      });
      setOverviewStatus('success');
    });

    return () => controller.abort();
  }, [team, code, overviewRequested]);

  const toggleFavorite = async () => {
    favoriteMutation.current += 1;
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

      {!overviewRequested && (
        <button className="primary small overview-toggle" onClick={() => setOverviewRequested(true)}>
          Afficher les matchs et le classement
        </button>
      )}
      {overviewStatus === 'loading' && <p className="notice" role="status">Chargement des matchs de l’équipe…</p>}
      {overviewStatus === 'success' && (
        <div className="context-grid">
          <section className="card panel">
            <h2>Classement</h2>
            {overview.rank ? (
              <div className="standing-row">
                <span className="standing-rank">#{overview.rank.position}</span>
                <span>{overview.rank.points} pts</span>
                <span>{overview.rank.playedGames} J</span>
                {overview.rank.form && <span className="muted">Forme : {overview.rank.form}</span>}
              </div>
            ) : (
              <p className="muted">Aucun classement disponible.</p>
            )}
          </section>
          <section className="card panel">
            <h2>Prochain match</h2>
            {overview.next ? (
              <ul className="match-list"><MatchRow match={overview.next} showCompetition /></ul>
            ) : (
              <p className="muted">Aucun match programmé pour le moment.</p>
            )}
          </section>
          <section className="card panel">
            <h2>Derniers résultats</h2>
            {overview.recent.length > 0 ? (
              <ul className="match-list">
                {overview.recent.map((item) => <MatchRow key={item.id} match={item} showCompetition />)}
              </ul>
            ) : (
              <p className="muted">Aucun match récent disponible.</p>
            )}
          </section>
        </div>
      )}
    </section>
  );
}
