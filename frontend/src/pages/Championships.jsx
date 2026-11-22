import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';

export default function Championships() {
  const [leagues, setLeagues] = useState([]);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    api('/api/football/leagues', { signal: controller.signal })
      .then((result) => {
        setLeagues(Array.isArray(result) ? result : []);
        setStatus('success');
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return;
        setError(requestError.message || 'Impossible de charger les championnats.');
        setStatus('error');
      });
    return () => controller.abort();
  }, [attempt]);

  return (
    <section>
      <span className="eyebrow">FOOTBALL</span>
      <h1>Championnats</h1>
      <p className="muted">Choisis un championnat pour consulter son classement et ses matchs.</p>
      {status === 'loading' && <p className="notice" role="status">Chargement des championnats…</p>}
      {status === 'error' && <div className="error" role="alert">Impossible de charger les championnats : {error}</div>}
      {status === 'error' && <button className="primary" onClick={() => setAttempt((value) => value + 1)}>Réessayer</button>}
      {status === 'success' && leagues.length === 0 && <div className="empty" data-testid="championships-empty"><div>⚽</div><p>Aucun championnat disponible</p></div>}
      {status === 'success' && leagues.length > 0 && (
        <div className="grid" data-testid="championship-list">
          {leagues.map((league) => (
            <Link className="card league" data-testid="championship-card" key={league.code} to={`/championships/${league.code}`}>
              <span className="league-icon" aria-hidden="true">🏆</span>
              <div className="league-text"><h2>{league.name}</h2><p>{league.country}</p></div>
              <span aria-hidden="true">→</span>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
