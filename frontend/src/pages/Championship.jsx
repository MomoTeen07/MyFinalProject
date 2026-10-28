import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api/client';

export default function Championship() {
  const { code } = useParams();
  const [tab, setTab] = useState('standings');
  const [standings, setStandings] = useState([]);
  const [matches, setMatches] = useState([]);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    setError('');
    Promise.all([
      api(`/api/football/leagues/${code}/standings`, { signal: controller.signal }),
      api(`/api/football/leagues/${code}/matches`, { signal: controller.signal }),
    ])
      .then(([table, fixtures]) => {
        setStandings(Array.isArray(table) ? table : []);
        setMatches(Array.isArray(fixtures) ? fixtures : []);
        setStatus('success');
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return;
        setError(requestError.message);
        setStatus('error');
      });
    return () => controller.abort();
  }, [code, attempt]);

  return (
    <section>
      <Link to="/championships" className="back">← Tous les championnats</Link>
      <h1>{code} : classement et matchs</h1>
      <div className="tabs" role="tablist" aria-label="Données du championnat">
        <button role="tab" aria-selected={tab === 'standings'} className={tab === 'standings' ? 'active' : ''} onClick={() => setTab('standings')}>Classement</button>
        <button role="tab" aria-selected={tab === 'matches'} className={tab === 'matches' ? 'active' : ''} onClick={() => setTab('matches')}>Matchs</button>
      </div>
      {status === 'loading' && <p className="notice" role="status">Chargement des données…</p>}
      {status === 'error' && <div className="error" role="alert">Impossible de charger les données : {error}</div>}
      {status === 'error' && <button className="primary" onClick={() => setAttempt((value) => value + 1)}>Réessayer</button>}
      {status === 'success' && tab === 'standings' && standings.length === 0 && <p className="empty">Aucun classement disponible.</p>}
      {status === 'success' && tab === 'standings' && standings.length > 0 && (
        <div className="table-wrap"><table><thead><tr><th>#</th><th>Équipe</th><th>J</th><th>G</th><th>N</th><th>P</th><th>Pts</th></tr></thead>
          <tbody>{standings.map((row) => <tr key={row.team.id}><td>{row.position}</td><td><Link className="team" to={`/teams/${code}/${row.team.id}`}>{row.team.name}</Link></td><td>{row.playedGames}</td><td>{row.won}</td><td>{row.draw}</td><td>{row.lost}</td><td><b>{row.points}</b></td></tr>)}</tbody>
        </table></div>
      )}
      {status === 'success' && tab === 'matches' && matches.length === 0 && <p className="empty">Aucun match disponible.</p>}
      {status === 'success' && tab === 'matches' && matches.length > 0 && (
        <div className="grid">{matches.map((match) => <div className="card match" key={match.id}>
          <span>{match.utcDate ? new Date(match.utcDate).toLocaleDateString() : 'Date à confirmer'}</span>
          <strong>{match.homeTeam.name}</strong><span>vs</span><strong>{match.awayTeam.name}</strong>
        </div>)}</div>
      )}
    </section>
  );
}
