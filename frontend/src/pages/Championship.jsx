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

function seasonLabel(season) {
  const start = season?.startDate?.slice(0, 4);
  const end = season?.endDate?.slice(0, 4);
  if (!start || !end) return '';
  return `Saison ${start}/${end}`;
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
        <Link className="match-link" to={`/matches/${match.id}`}>Détails</Link>
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
  const [scorers, setScorers] = useState(null);
  const [scorerSort, setScorerSort] = useState('goals');
  const [scorerStatus, setScorerStatus] = useState('idle');
  const [scorerError, setScorerError] = useState('');

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

  useEffect(() => {
    if (tab !== 'scorers') return undefined;

    const controller = new AbortController();
    setScorerStatus('loading');
    setScorerError('');

    api(`/api/football/leagues/${code}/scorers?limit=10&sort=${scorerSort}`, {
      signal: controller.signal,
    })
      .then((payload) => {
        setScorers(payload);
        setScorerStatus('success');
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return;
        setScorerError(requestError.message);
        setScorerStatus('error');
      });

    return () => controller.abort();
  }, [code, tab, scorerSort]);

  const scorerItems = scorers?.items || [];

  return (
    <section>
      <Link to="/championships" className="back">← Tous les championnats</Link>
      <span className="eyebrow">{league?.country || 'CHAMPIONNAT'}</span>
      <h1>{league?.name || code}</h1>
      <div className="tabs" role="tablist" aria-label="Données du championnat">
        <button role="tab" aria-selected={tab === 'standings'} className={tab === 'standings' ? 'active' : ''} onClick={() => setTab('standings')}>Classement</button>
        <button role="tab" aria-selected={tab === 'matches'} className={tab === 'matches' ? 'active' : ''} onClick={() => setTab('matches')}>Matchs</button>
        <button role="tab" aria-selected={tab === 'scorers'} className={tab === 'scorers' ? 'active' : ''} onClick={() => setTab('scorers')}>Buteurs</button>
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
      {status === 'success' && tab === 'scorers' && (
        <>
          <div className="tabs" role="group" aria-label="Critère du classement des buteurs">
            <button
              type="button"
              aria-pressed={scorerSort === 'goals'}
              className={scorerSort === 'goals' ? 'active' : ''}
              onClick={() => setScorerSort('goals')}
            >
              Buts
            </button>
            <button
              type="button"
              aria-pressed={scorerSort === 'assists'}
              className={scorerSort === 'assists' ? 'active' : ''}
              onClick={() => setScorerSort('assists')}
            >
              Passes
            </button>
          </div>
          {scorerStatus === 'loading' && <p className="notice" role="status">Chargement des buteurs…</p>}
          {scorerStatus === 'error' && (
            <div className="error" role="alert">Impossible de charger les buteurs : {scorerError}</div>
          )}
          {scorerStatus === 'success' && seasonLabel(scorers?.season) && (
            <p className="muted">{seasonLabel(scorers?.season)}</p>
          )}
          {scorerStatus === 'success' && scorerItems.length === 0 && (
            <p className="empty">Aucun buteur disponible.</p>
          )}
          {scorerStatus === 'success' && scorerItems.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Joueur</th>
                    <th>Équipe</th>
                    <th>J</th>
                    <th className={scorerSort === 'goals' ? 'stat-active' : ''}>Buts</th>
                    <th className={scorerSort === 'assists' ? 'stat-active' : ''}>Passes</th>
                  </tr>
                </thead>
                <tbody>
                  {scorerItems.map((row) => (
                    <tr key={`${row.position}-${row.player.id}-${row.team.id}`}>
                      <td>{row.position}</td>
                      <td>{row.player.name}</td>
                      <td>
                        {row.team.id
                          ? <Link className="team" to={`/teams/${code}/${row.team.id}`}>{row.team.name}</Link>
                          : <span className="team">{row.team.name}</span>}
                      </td>
                      <td>{row.playedMatches}</td>
                      <td className={scorerSort === 'goals' ? 'stat-active' : ''}><b>{row.goals}</b></td>
                      <td className={scorerSort === 'assists' ? 'stat-active' : ''}><b>{row.assists}</b></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}
