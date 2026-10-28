import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api/client';

const matchStatuses = {
  FINISHED: 'Terminé',
  IN_PLAY: 'En cours',
  PAUSED: 'Mi-temps',
  SCHEDULED: 'À venir',
  TIMED: 'À venir',
  POSTPONED: 'Reporté',
  CANCELLED: 'Annulé',
  AWARDED: 'Décision officielle',
};

function formatMatchDate(value) {
  if (!value) return 'Date à confirmer';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Date à confirmer';
  return new Intl.DateTimeFormat('fr-BE', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Europe/Brussels',
  }).format(date);
}

function MatchCard({ match, leagueCode }) {
  const score = match.score?.fullTime;
  const hasScore = score?.home != null && score?.away != null;
  const status = matchStatuses[match.status] || match.status || 'Statut inconnu';

  const teamLink = (team) => team.id
    ? <Link className="fixture-team" to={`/teams/${leagueCode}/${team.id}`}>{team.name}</Link>
    : <span className="fixture-team">{team.name}</span>;

  return (
    <article className="card match">
      <div className="match-meta">
        <time dateTime={match.utcDate || undefined}>{formatMatchDate(match.utcDate)}</time>
        <span>{status}</span>
      </div>
      <div className="matchup">
        {teamLink(match.homeTeam)}
        <strong className="match-score">{hasScore ? `${score.home} – ${score.away}` : 'vs'}</strong>
        {teamLink(match.awayTeam)}
      </div>
    </article>
  );
}

export default function Championship() {
  const { code } = useParams();
  const [tab, setTab] = useState('standings');
  const [league, setLeague] = useState(null);
  const [standings, setStandings] = useState([]);
  const [matches, setMatches] = useState([]);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    setError('');
    setLeague(null);

    Promise.all([
      api(`/api/football/leagues/${code}/standings`, { signal: controller.signal }),
      api(`/api/football/leagues/${code}/matches`, { signal: controller.signal }),
      api('/api/football/leagues', { signal: controller.signal }).catch(() => []),
    ])
      .then(([table, fixtures, leagues]) => {
        setStandings(Array.isArray(table) ? table : []);
        setMatches(Array.isArray(fixtures) ? fixtures : []);
        setLeague(leagues.find((item) => item.code === code) || { code, name: code });
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
      <span className="eyebrow">{league?.country || 'CHAMPIONNAT'}</span>
      <h1>{league?.name || code}</h1>
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
        <div className="grid">{matches.map((match) => <MatchCard key={match.id} match={match} leagueCode={code} />)}</div>
      )}
    </section>
  );
}
