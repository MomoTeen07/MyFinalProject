const resultLabels = {
  W: 'Victoire',
  D: 'Match nul',
  L: 'Défaite',
};

const displayLabels = {
  W: 'V',
  D: 'N',
  L: 'D',
};

/**
 * Déduit la forme d'une équipe depuis ses derniers matchs (triés du plus récent
 * au plus ancien). Le fournisseur laisse souvent `form` vide : ce calcul évite
 * un classement sans information.
 */
export function formResults(matches, teamId) {
  if (!Array.isArray(matches) || teamId == null) return [];

  return [...matches]
    .reverse()
    .map((match) => {
      const isHome = match.homeTeam?.id === teamId;
      const isAway = match.awayTeam?.id === teamId;
      if (!isHome && !isAway) return null;

      const homeGoals = match.score?.fullTime?.home ?? match.score?.home;
      const awayGoals = match.score?.fullTime?.away ?? match.score?.away;
      if (homeGoals == null || awayGoals == null) return null;

      const ownGoals = isHome ? homeGoals : awayGoals;
      const opponentGoals = isHome ? awayGoals : homeGoals;
      if (ownGoals > opponentGoals) return 'W';
      if (ownGoals < opponentGoals) return 'L';
      return 'D';
    })
    .filter(Boolean);
}

function formFromString(value) {
  if (typeof value !== 'string') return [];
  return value
    .toUpperCase()
    .split('')
    .filter((result) => ['W', 'D', 'L'].includes(result));
}

/** Badges V/N/D réutilisés par le match, la fiche équipe et les favoris. */
export default function FormBadges({ results = [], fallback = null, label = 'Forme' }) {
  const values = results.length > 0 ? results : formFromString(fallback);
  if (values.length === 0) return null;

  return (
    <span className="form-line">
      {label && <span className="muted">{label}</span>}
      <span className="form-badges">
        {values.map((result, index) => (
          <span
            key={`${result}-${index}`}
            className={`form-badge form-${result.toLowerCase()}`}
            title={resultLabels[result]}
          >
            {displayLabels[result]}
          </span>
        ))}
      </span>
    </span>
  );
}
