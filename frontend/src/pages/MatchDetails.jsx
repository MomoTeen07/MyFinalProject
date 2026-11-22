import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api/client';
import FormBadges, { formResults } from '../components/FormBadges';
import MatchRow from '../components/MatchRow';

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

const stageLabels = {
  REGULAR_SEASON: 'Saison régulière',
  PLAYOFFS: 'Play-offs',
  GROUP_STAGE: 'Phase de groupes',
  LAST_16: 'Huitièmes de finale',
  QUARTER_FINALS: 'Quarts de finale',
  SEMI_FINALS: 'Demi-finales',
  FINAL: 'Finale',
};

const cardLabels = {
  YELLOW: 'Carton jaune',
  RED: 'Carton rouge',
  YELLOW_RED: 'Deuxième jaune',
};

const statLabels = {
  ball_possession: 'Possession',
  shots: 'Tirs',
  shots_on_goal: 'Tirs cadrés',
  shots_off_goal: 'Tirs non cadrés',
  corner_kicks: 'Corners',
  fouls: 'Fautes',
  offsides: 'Hors-jeu',
  saves: 'Arrêts',
  yellow_cards: 'Cartons jaunes',
  red_cards: 'Cartons rouges',
  free_kicks: 'Coups francs',
  goal_kicks: 'Six mètres',
  throw_ins: 'Touches',
};

const SUPPORTED = new Set(['PL', 'FL1', 'PD', 'SA', 'BL1', 'CL']);

function formatMatchDate(value) {
  if (!value) return 'Date à confirmer';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Date à confirmer';
  return new Intl.DateTimeFormat('fr-BE', {
    dateStyle: 'full',
    timeStyle: 'short',
    timeZone: 'Europe/Brussels',
  }).format(date);
}

function formatMinute(event) {
  if (event?.minute == null) return '';
  return event.injuryTime ? `${event.minute}+${event.injuryTime}'` : `${event.minute}'`;
}

function sortRecent(matches) {
  return [...matches].sort((a, b) => {
    const left = `${a.utcDate || ''}-${a.id || 0}`;
    const right = `${b.utcDate || ''}-${b.id || 0}`;
    return right.localeCompare(left);
  });
}

function headToHeadBalance(items, homeTeam, awayTeam) {
  const balance = { matches: items.length, goals: 0, homeWins: 0, draws: 0, awayWins: 0 };
  if (!homeTeam?.id || !awayTeam?.id) return balance;

  items.forEach((match) => {
    const homeGoals = match.score?.fullTime?.home ?? match.score?.home;
    const awayGoals = match.score?.fullTime?.away ?? match.score?.away;
    if (homeGoals == null || awayGoals == null) return;

    balance.goals += homeGoals + awayGoals;
    const currentHomeWasHome = match.homeTeam?.id === homeTeam.id;
    const currentHomeGoals = currentHomeWasHome ? homeGoals : awayGoals;
    const currentAwayGoals = currentHomeWasHome ? awayGoals : homeGoals;

    if (currentHomeGoals > currentAwayGoals) balance.homeWins += 1;
    else if (currentHomeGoals < currentAwayGoals) balance.awayWins += 1;
    else balance.draws += 1;
  });

  return balance;
}

export default function MatchDetails() {
  const { id } = useParams();
  const [match, setMatch] = useState(null);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [context, setContext] = useState({ standings: [], homeRecent: [], awayRecent: [] });
  const [contextStatus, setContextStatus] = useState('idle');
  const [h2h, setH2h] = useState([]);
  const [h2hStatus, setH2hStatus] = useState('idle');
  const [h2hRequested, setH2hRequested] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    setError('');
    setMatch(null);
    setContext({ standings: [], homeRecent: [], awayRecent: [] });
    setContextStatus('idle');
    setH2h([]);
    setH2hStatus('idle');
    setH2hRequested(false);

    api(`/api/football/matches/${id}`, { signal: controller.signal })
      .then((payload) => {
        setMatch(payload);
        setStatus('success');
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return;
        setError(requestError.message);
        setStatus('error');
      });

    return () => controller.abort();
  }, [id, attempt]);

  useEffect(() => {
    if (!match) return undefined;

    const controller = new AbortController();
    const signal = controller.signal;
    const code = match.competition?.code;
    const load = (path) => (path ? api(path, { signal }).catch(() => null) : Promise.resolve(null));

    setContextStatus('loading');
    Promise.all([
      load(code ? `/api/football/leagues/${code}/standings` : null),
      load(
        code && match.homeTeam?.id
          ? `/api/football/leagues/${code}/matches?team_id=${match.homeTeam.id}&status=FINISHED&page_size=3&sort=date_desc`
          : null,
      ),
      load(
        code && match.awayTeam?.id
          ? `/api/football/leagues/${code}/matches?team_id=${match.awayTeam.id}&status=FINISHED&page_size=3&sort=date_desc`
          : null,
      ),
    ]).then(([standings, homeMatches, awayMatches]) => {
      if (controller.signal.aborted) return;
      setContext({
        standings: Array.isArray(standings) ? standings : [],
        homeRecent: Array.isArray(homeMatches?.items) ? sortRecent(homeMatches.items) : [],
        awayRecent: Array.isArray(awayMatches?.items) ? sortRecent(awayMatches.items) : [],
      });
      setContextStatus('success');
    });

    return () => controller.abort();
  }, [match]);

  useEffect(() => {
    if (!match || !h2hRequested) return undefined;

    const controller = new AbortController();
    setH2hStatus('loading');

    api(`/api/football/matches/${match.id}/head2head?limit=5`, {
      signal: controller.signal,
    })
      .then((payload) => {
        setH2h(Array.isArray(payload?.items) ? payload.items : []);
        setH2hStatus('success');
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return;
        setH2hStatus('error');
      });

    return () => controller.abort();
  }, [match, h2hRequested]);

  const code = match?.competition?.code;
  const teamLink = (team) => {
    if (!team) return <span className="team">Équipe inconnue</span>;
    return team.id && SUPPORTED.has(code)
      ? <Link className="team" to={`/teams/${code}/${team.id}`}>{team.name}</Link>
      : <span className="team">{team.name}</span>;
  };

  const homeRow = context.standings.find((row) => row.team?.id === match?.homeTeam?.id);
  const awayRow = context.standings.find((row) => row.team?.id === match?.awayTeam?.id);
  const score = match?.score || {};
  const hasScore = score.home != null && score.away != null;
  const homeStats = match?.homeTeam?.statistics;
  const awayStats = match?.awayTeam?.statistics;
  const hasLineups = (match?.homeTeam?.lineup?.length || 0) > 0 || (match?.awayTeam?.lineup?.length || 0) > 0;
  const h2hBalance = headToHeadBalance(h2h, match?.homeTeam, match?.awayTeam);

  return (
    <section>
      <Link to={code ? `/championships/${code}` : '/championships'} className="back">
        ← {match?.competition?.name || 'Tous les championnats'}
      </Link>
      <span className="eyebrow">{match?.competition?.name || 'MATCH'}</span>
      <h1>Détail du match</h1>

      {status === 'loading' && <p className="notice" role="status">Chargement du match…</p>}
      {status === 'error' && (
        <div className="error" role="alert">Impossible de charger le match : {error}</div>
      )}
      {status === 'error' && (
        <button className="primary" onClick={() => setAttempt((value) => value + 1)}>Réessayer</button>
      )}

      {status === 'success' && match && (
        <>
          <article className="card match-details">
            <div className="match-meta">
              <time dateTime={match.utcDate || undefined}>{formatMatchDate(match.utcDate)}</time>
              <span>{matchStatuses[match.status] || match.status || 'Statut inconnu'}</span>
            </div>
            <div className="matchup">
              {teamLink(match.homeTeam)}
              <strong className="match-score">
                {hasScore ? `${score.home} – ${score.away}` : 'vs'}
              </strong>
              {teamLink(match.awayTeam)}
            </div>
            <div className="match-info">
              {match.matchday != null && <span>Journée {match.matchday}</span>}
              {match.stage && <span>{stageLabels[match.stage] || match.stage}</span>}
              {match.group && <span>Groupe {match.group}</span>}
              {match.venue && <span>{match.venue}</span>}
              {match.attendance != null && <span>{match.attendance.toLocaleString('fr-BE')} spectateurs</span>}
              {match.minute != null && <span>{match.minute}{match.injuryTime ? `+${match.injuryTime}` : ''} min</span>}
            </div>
            {score.halfTime?.home != null && score.halfTime?.away != null && (
              <p className="muted">Mi-temps : {score.halfTime.home} – {score.halfTime.away}</p>
            )}
            {match.referees?.length > 0 && (
              <p className="muted">
                Arbitre : {match.referees.find((referee) => referee.type === 'REFEREE')?.name
                  || match.referees[0]?.name || 'Non renseigné'}
              </p>
            )}
          </article>

          {match.goals?.length > 0 && (
            <section className="card panel">
              <h2>Buts</h2>
              <ol className="timeline">
                {match.goals.map((goal, index) => (
                  <li key={`goal-${goal.minute}-${index}`}>
                    <span className="minute">{formatMinute(goal)}</span>
                    <span>
                      <b>{goal.scorer?.name || 'Joueur inconnu'}</b>
                      {goal.assist?.name ? <span className="muted"> (passe : {goal.assist.name})</span> : null}
                      <span className="muted"> · {goal.team?.name || 'Équipe'}</span>
                    </span>
                    <strong>{goal.score?.home} – {goal.score?.away}</strong>
                  </li>
                ))}
              </ol>
            </section>
          )}

          {match.bookings?.length > 0 && (
            <section className="card panel">
              <h2>Cartons</h2>
              <ul className="timeline">
                {match.bookings.map((booking, index) => (
                  <li key={`booking-${booking.minute}-${index}`}>
                    <span className="minute">{formatMinute(booking)}</span>
                    <span>
                      <b>{booking.player?.name || 'Joueur inconnu'}</b>
                      <span className="muted"> · {booking.team?.name || 'Équipe'}</span>
                    </span>
                    <span>{cardLabels[booking.card] || booking.card}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {match.substitutions?.length > 0 && (
            <section className="card panel">
              <h2>Remplacements</h2>
              <ul className="timeline">
                {match.substitutions.map((change, index) => (
                  <li key={`sub-${change.minute}-${index}`}>
                    <span className="minute">{formatMinute(change)}</span>
                    <span>
                      <b>{change.playerIn?.name || 'Entrant'}</b>
                      <span className="muted"> remplace {change.playerOut?.name || 'Sortant'}</span>
                      <span className="muted"> · {change.team?.name || 'Équipe'}</span>
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {hasLineups && (
            <section className="card panel">
              <h2>Compositions</h2>
              <div className="lineups">
                {[match.homeTeam, match.awayTeam].map((team) => (
                  <div key={team.id || team.name}>
                    <h3>{team.name} {team.formation && <span className="muted">{team.formation}</span>}</h3>
                    {team.coach?.name && <p className="muted">Entraîneur : {team.coach.name}</p>}
                    <ul className="lineup-list">
                      {(team.lineup || []).map((player) => (
                        <li key={`${team.id}-${player.id}`}>
                          {player.shirtNumber != null ? `${player.shirtNumber} ` : ''}{player.name}
                          <span className="muted"> {player.position}</span>
                        </li>
                      ))}
                    </ul>
                    {team.bench?.length > 0 && (
                      <details>
                        <summary>Remplaçants ({team.bench.length})</summary>
                        <ul className="lineup-list">
                          {team.bench.map((player) => <li key={`${team.id}-bench-${player.id}`}>{player.name}</li>)}
                        </ul>
                      </details>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {homeStats && awayStats && (
            <section className="card panel">
              <h2>Statistiques</h2>
              <div className="stat-rows">
                {Object.entries(statLabels).map(([key, label]) => {
                  const homeValue = homeStats[key];
                  const awayValue = awayStats[key];
                  if (homeValue == null && awayValue == null) return null;
                  const total = Number(homeValue || 0) + Number(awayValue || 0);
                  const homeWidth = total ? (Number(homeValue || 0) / total) * 100 : 50;
                  return (
                    <div className="stat-row" key={key}>
                      <span>{homeValue ?? '—'}</span>
                      <div className="stat-bar" aria-label={`${label} : ${homeValue ?? 0} à ${awayValue ?? 0}`}>
                        <span className="stat-home" style={{ width: `${homeWidth}%` }} />
                      </div>
                      <span>{awayValue ?? '—'}</span>
                      <small>{label}</small>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          <div className="context-grid">
            <section className="card panel">
              <h2>Classement</h2>
              {contextStatus === 'loading' && <p className="muted">Chargement du classement…</p>}
              {homeRow || awayRow ? (
                <div className="standing-list">
                  {[homeRow, awayRow].map((row, index) => {
                    const team = index === 0 ? match.homeTeam : match.awayTeam;
                    return row ? (
                      <div className="standing-row" key={team.id || team.name}>
                        <span className="standing-rank">#{row.position}</span>
                        <span>{team.name}</span>
                        <span>{row.points} pts</span>
                        <span>{row.playedGames} J</span>
                        <FormBadges
                          results={formResults(
                            index === 0 ? context.homeRecent : context.awayRecent,
                            team.id,
                          )}
                          fallback={row.form}
                          label=""
                        />
                      </div>
                    ) : (
                      <p className="muted" key={team.id || team.name}>Classement indisponible pour {team.name}.</p>
                    );
                  })}
                </div>
              ) : (
                contextStatus !== 'loading' && <p className="muted">Classement indisponible.</p>
              )}
            </section>

            <section className="card panel">
              <h2>Confrontations</h2>
              {!h2hRequested && (
                <>
                  <p className="muted">Retrouve les dernières rencontres entre les deux équipes.</p>
                  <button className="primary small" onClick={() => setH2hRequested(true)}>
                    Afficher les confrontations directes
                  </button>
                </>
              )}
              {h2hStatus === 'loading' && <p className="muted">Chargement des confrontations…</p>}
              {h2hStatus === 'error' && <p className="muted">Confrontations indisponibles pour le moment.</p>}
              {h2hStatus === 'success' && h2h.length === 0 && (
                <p className="muted">Aucune confrontation récente disponible.</p>
              )}
              {h2h.length > 0 && (
                <>
                  <p className="h2h-summary">
                    {h2hBalance.matches} confrontation{h2hBalance.matches > 1 ? 's' : ''}
                    {' · '}
                    {h2hBalance.goals} but{h2hBalance.goals > 1 ? 's' : ''}
                  </p>
                  <p className="h2h-balance">
                    <span>{match.homeTeam.name} : {h2hBalance.homeWins} V · {h2hBalance.draws} N · {h2hBalance.awayWins} D</span>
                    <span>{match.awayTeam.name} : {h2hBalance.awayWins} V · {h2hBalance.draws} N · {h2hBalance.homeWins} D</span>
                  </p>
                  <ul className="match-list">
                    {h2h.map((item) => <MatchRow key={item.id} match={item} showCompetition />)}
                  </ul>
                </>
              )}
            </section>

            <section className="card panel">
              <h2>Derniers matchs · {match.homeTeam.name}</h2>
              {contextStatus === 'loading' && <p className="muted">Chargement…</p>}
              {contextStatus !== 'loading' && context.homeRecent.length === 0 && (
                <p className="muted">Aucun match récent disponible.</p>
              )}
              {context.homeRecent.length > 0 && (
                <ul className="match-list">
                  {context.homeRecent.map((item) => <MatchRow key={item.id} match={item} />)}
                </ul>
              )}
            </section>

            <section className="card panel">
              <h2>Derniers matchs · {match.awayTeam.name}</h2>
              {contextStatus === 'loading' && <p className="muted">Chargement…</p>}
              {contextStatus !== 'loading' && context.awayRecent.length === 0 && (
                <p className="muted">Aucun match récent disponible.</p>
              )}
              {context.awayRecent.length > 0 && (
                <ul className="match-list">
                  {context.awayRecent.map((item) => <MatchRow key={item.id} match={item} />)}
                </ul>
              )}
            </section>
          </div>
        </>
      )}
    </section>
  );
}
