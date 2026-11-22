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

export default function MatchDetails() {
  const { id } = useParams();
  const [match, setMatch] = useState(null);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    setError('');

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

  const teamLink = (team) => (
    team.id && SUPPORTED.has(match?.competition?.code)
      ? <Link className="team" to={`/teams/${match.competition.code}/${team.id}`}>{team.name}</Link>
      : <span className="team">{team.name}</span>
  );

  return (
    <section>
      <Link to="/championships" className="back">← Tous les championnats</Link>
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
        <article className="card match-details">
          <div className="match-meta">
            <time dateTime={match.utcDate || undefined}>{formatMatchDate(match.utcDate)}</time>
            <span>{matchStatuses[match.status] || match.status || 'Statut inconnu'}</span>
          </div>
          <div className="matchup">
            {teamLink(match.homeTeam)}
            <strong className="match-score">
              {match.score?.home != null && match.score?.away != null
                ? `${match.score.home} – ${match.score.away}`
                : 'vs'}
            </strong>
            {teamLink(match.awayTeam)}
          </div>
          {match.matchday != null && (
            <p className="muted">Journée {match.matchday}</p>
          )}
        </article>
      )}
    </section>
  );
}
