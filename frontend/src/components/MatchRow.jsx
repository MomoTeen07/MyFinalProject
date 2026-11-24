import { Link } from 'react-router-dom';

const statusLabels = {
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

const shortDate = new Intl.DateTimeFormat('fr-BE', {
  dateStyle: 'short',
  timeStyle: 'short',
  timeZone: 'Europe/Brussels',
});

export function formatShortDate(value) {
  const date = new Date(value);
  if (!value || Number.isNaN(date.getTime())) return 'Date à confirmer';
  return shortDate.format(date);
}

/** Ligne compacte réutilisée par les favoris, la fiche équipe et le détail match. */
export default function MatchRow({ match, showCompetition = false }) {
  const score = match.score?.fullTime || match.score || {};
  const hasScore = score.home != null && score.away != null;

  return (
    <li className="match-row">
      <div className="match-row-meta">
        <time dateTime={match.utcDate || undefined}>{formatShortDate(match.utcDate)}</time>
        {showCompetition && match.competition?.name && <span>{match.competition.name}</span>}
        <span>{statusLabels[match.status] || match.status || 'Statut inconnu'}</span>
      </div>
      <div className="match-row-main">
        <span className="match-row-team">{match.homeTeam?.name || 'Équipe inconnue'}</span>
        <strong className="match-row-score">
          {hasScore ? `${score.home} – ${score.away}` : 'vs'}
        </strong>
        <span className="match-row-team">{match.awayTeam?.name || 'Équipe inconnue'}</span>
        {match.id != null && <Link className="match-row-link" to={`/matches/${match.id}`}>Détails</Link>}
      </div>
    </li>
  );
}
