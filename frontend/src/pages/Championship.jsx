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
  SUSPENDED: 'Suspendu',
};

const MATCHES_PAGE_SIZE = 20;

// Liste fermée alignée sur l'énumération de l'API (`MatchStatus`).
const matchFilterStatuses = [
  ['SCHEDULED', 'Programmé'],
  ['TIMED', 'Horaire fixé'],
  ['IN_PLAY', 'En cours'],
  ['PAUSED', 'Mi-temps'],
  ['FINISHED', 'Terminé'],
  ['POSTPONED', 'Reporté'],
  ['CANCELLED', 'Annulé'],
  ['AWARDED', 'Décision officielle'],
  ['SUSPENDED', 'Suspendu'],
];

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
  const [matchesMeta, setMatchesMeta] = useState(null);
  const [matchesStatus, setMatchesStatus] = useState('idle');
  const [matchesError, setMatchesError] = useState('');
  const [matchesAttempt, setMatchesAttempt] = useState(0);
  const [matchStatusFilter, setMatchStatusFilter] = useState('');
  const [matchSort, setMatchSort] = useState('date');
  const matchQueryKey = `${code}|${matchStatusFilter}|${matchSort}`;
  const [matchPageState, setMatchPageState] = useState({ key: matchQueryKey, page: 1 });
  const matchPage = matchPageState.key === matchQueryKey ? matchPageState.page : 1;
  const goToMatchPage = (page) => setMatchPageState({ key: matchQueryKey, page });
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [scorers, setScorers] = useState(null);
  const [scorerSort, setScorerSort] = useState('goals');
  const [scorerStatus, setScorerStatus] = useState('idle');
  const [scorerError, setScorerError] = useState('');
  const [scorerAttempt, setScorerAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    setError('');
    setLeague(null);

    Promise.all([
      api(`/api/football/leagues/${code}/standings`, { signal: controller.signal }),
      api('/api/football/leagues', { signal: controller.signal }).catch(() => []),
    ])
      .then(([table, leagues]) => {
        setStandings(Array.isArray(table) ? table : []);
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
  }, [code, tab, scorerSort, scorerAttempt]);

  useEffect(() => {
    if (tab !== 'matches') return undefined;

    const controller = new AbortController();
    setMatchesStatus('loading');
    setMatchesError('');

    const params = new URLSearchParams({
      page: String(matchPage),
      page_size: String(MATCHES_PAGE_SIZE),
      sort: matchSort,
    });
    if (matchStatusFilter) params.set('status', matchStatusFilter);

    api(`/api/football/leagues/${code}/matches?${params.toString()}`, {
      signal: controller.signal,
    })
      .then((payload) => {
        setMatches(Array.isArray(payload?.items) ? payload.items : []);
        setMatchesMeta(payload);
        setMatchesStatus('success');
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return;
        setMatchesError(requestError.message);
        setMatchesStatus('error');
      });

    return () => controller.abort();
  }, [code, tab, matchPage, matchStatusFilter, matchSort, matchesAttempt]);

  const scorerItems = scorers?.items || [];
  const matchTotalPages = matchesMeta?.total_pages || 0;

  return (
    <section>
      <Link to="/championships" className="back">← Tous les championnats</Link>
      <span className="eyebrow">{league?.country || 'CHAMPIONNAT'}</span>
      <h1>{league?.name || code}</h1>
      <div className="tabs" role="tablist" aria-label="Données du championnat">
        <button role="tab" aria-selected={tab === 'standings'} className={tab === 'standings' ? 'active' : ''} onClick={() => setTab('standings')}>Classement</button>
        <button role="tab" aria-selected={tab === 'matches'} className={tab === 'matches' ? 'active' : ''} onClick={() => setTab('matches')}>Matchs</button>
        <button role="tab" aria-selected={tab === 'scorers'} className={tab === 'scorers' ? 'active' : ''} onClick={() => setTab('scorers')}>Statistiques</button>
      </div>
      {status === 'loading' && <p className="notice" role="status">Chargement des données…</p>}
      {status === 'error' && <div className="error" role="alert">Impossible de charger les données : {error}</div>}
      {status === 'error' && <button className="primary" onClick={() => setAttempt((value) => value + 1)}>Réessayer</button>}
      {status === 'success' && tab === 'standings' && standings.length === 0 && <p className="empty">Aucun classement disponible.</p>}
      {status === 'success' && tab === 'standings' && standings.length > 0 && (
        <>
          <p className="table-hint">Glisse horizontalement dans le tableau pour voir toutes les colonnes.</p>
          <div className="table-wrap"><table><thead><tr><th>#</th><th>Équipe</th><th>J</th><th>G</th><th>N</th><th>P</th><th>Pts</th></tr></thead>
            <tbody>{standings.map((row) => <tr key={row.team.id}><td>{row.position}</td><td><Link className="team" to={`/teams/${code}/${row.team.id}`}>{row.team.name}</Link></td><td>{row.playedGames}</td><td>{row.won}</td><td>{row.draw}</td><td>{row.lost}</td><td><b>{row.points}</b></td></tr>)}</tbody>
          </table></div>
        </>
      )}
      {status === 'success' && tab === 'matches' && (
        <>
          <div className="filters">
            <label>
              Statut
              <select
                value={matchStatusFilter}
                onChange={(event) => setMatchStatusFilter(event.target.value)}
              >
                <option value="">Tous</option>
                {matchFilterStatuses.map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </label>
            <label>
              Tri
              <select value={matchSort} onChange={(event) => setMatchSort(event.target.value)}>
                <option value="date">Date (croissant)</option>
                <option value="date_desc">Date (décroissant)</option>
              </select>
            </label>
          </div>
          {matchesStatus === 'loading' && <p className="notice" role="status">Chargement des matchs…</p>}
          {matchesStatus === 'error' && (
            <>
              <div className="error" role="alert">Impossible de charger les matchs : {matchesError}</div>
              <button className="primary small" onClick={() => setMatchesAttempt((value) => value + 1)}>
                Réessayer
              </button>
            </>
          )}
          {matchesStatus === 'success' && matches.length === 0 && (
            <p className="empty">
              {matchStatusFilter ? 'Aucun match pour ce filtre.' : 'Aucun match disponible.'}
            </p>
          )}
          {matchesStatus === 'success' && matches.length > 0 && (
            <div className="grid">{matches.map((match) => <MatchCard key={match.id} match={match} leagueCode={code} />)}</div>
          )}
          {matchesStatus === 'success' && matchTotalPages > 0 && (
            <nav className="pager" aria-label="Pagination des matchs">
              <button
                type="button"
                disabled={matchPage <= 1}
                onClick={() => goToMatchPage(matchPage - 1)}
              >
                Précédent
              </button>
              <span>Page {matchesMeta?.page ?? matchPage} / {matchTotalPages}</span>
              <button
                type="button"
                disabled={matchPage >= matchTotalPages}
                onClick={() => goToMatchPage(matchPage + 1)}
              >
                Suivant
              </button>
            </nav>
          )}
        </>
      )}
      {status === 'success' && tab === 'scorers' && (
        <>
          <div className="tabs" role="group" aria-label="Critère des statistiques">
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
          {scorerStatus === 'loading' && <p className="notice" role="status">Chargement des statistiques…</p>}
          {scorerStatus === 'error' && (
            <>
              <div className="error" role="alert">Impossible de charger les statistiques : {scorerError}</div>
              <button className="primary small" onClick={() => setScorerAttempt((value) => value + 1)}>
                Réessayer
              </button>
            </>
          )}
          {scorerStatus === 'success' && seasonLabel(scorers?.season) && (
            <p className="muted">{seasonLabel(scorers?.season)}</p>
          )}
          {scorerStatus === 'success' && scorerItems.length === 0 && (
            <p className="empty">Aucun buteur disponible.</p>
          )}
          {scorerStatus === 'success' && scorerItems.length > 0 && (
            <>
              <p className="table-hint">Glisse horizontalement dans le tableau pour voir toutes les colonnes.</p>
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
            </>
          )}
        </>
      )}
    </section>
  );
}
