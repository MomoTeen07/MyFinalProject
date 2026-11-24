# Spécification fonctionnelle — V3

| Élément | Valeur |
|---|---|
| Branche | `app/v3` |
| Base | `app/v2` |
| Principe | **additif** : aucune fonctionnalité existante supprimée, ANO-001 à ANO-005 conservées |
| Vérification fonctionnelle | 22/11/2026, données réelles |
| Phase Testing | **non démarrée** |

## 1. Périmètre

La V3 enrichit la consultation sans modifier les règles métier de la V1/V2 :
prochains matchs de l'accueil, contexte de la fiche équipe, tableau de bord des
favoris et contexte du détail de match. La pagination, le tri et les filtres des
matchs sont livrés par la V2 (F1) et restent couverts par les tests.

## 2. F1 — Prochains matchs de l'accueil

**API** : `GET /api/football/fixtures`

| Paramètre | Valeur | Défaut |
|---|---|---|
| `days` | entier 1 à 10 | 3 |
| `limit` | entier 1 à 20 | 4 |
| `team_id` | entier ≥ 0 | aucun |

La route agrège les six compétitions supportées, ne conserve que les matchs
`SCHEDULED` et `TIMED`, exclut ceux déjà commencés et renvoie une vue normalisée
`{ id, utcDate, status, competition, homeTeam, awayTeam, score }`, triée par date.

**Interface** : carte « Prochains matchs » sur l'accueil, quatre rencontres
maximum, lien vers le détail de chaque match, états chargement / vide / erreur
avec bouton « Réessayer ».

## 3. F2 — Fiche équipe enrichie

**Sources** :

- `GET /api/football/leagues/{code}/standings` : position, points, matchs joués, forme ;
- `GET /api/football/leagues/{code}/matches?team_id=…&status=FINISHED&page_size=3&sort=date_desc` : derniers résultats ;
- `GET /api/football/fixtures?days=10&limit=1&team_id=…` : prochain match inter-compétitions ;
- `GET /api/football/leagues/{code}/matches?team_id=…&page_size=100&sort=date` : repli sur le calendrier du championnat au-delà de 10 jours.

**Interface** : bouton « Afficher les matchs et le classement » (chargement à la
demande), panneaux Classement, Prochain match et Derniers résultats. La forme
est calculée à partir des résultats récents ; la forme fournisseur sert de repli.
Le bouton favori reste disponible pour un utilisateur connecté, avec état
optimiste et protection contre les réponses de lecture obsolètes.

## 4. F3 — Tableau de bord des favoris

**API** : `GET /api/favorites/overview`

Réponse : `{ window, items: [{ id, team_id, league_code, team_name, team_crest, rank, recent, next }] }`.

- `rank` : position, points, matchs joués et forme issus du classement ;
- `recent` : trois derniers résultats terminés ;
- `next` : prochain match programmé.

La fenêtre courte du fournisseur (7 jours passés / 10 jours à venir) est
complétée par le calendrier complet du championnat quand elle ne suffit pas.
Les erreurs fournisseur sont absorbées : une carte reste affichable sans
contexte sportif.

**Interface** : tableau de bord vertical par équipe, classement, forme,
derniers résultats, prochain match, suppression et état vide. Le cloisonnement
entre comptes et la persistance après reconnexion restent garantis par la V1.

## 5. F4 — Détail de match enrichi

**API** : `GET /api/football/matches/{match_id}/head2head?limit=1..10`

Réponse : `{ match_id, aggregates, items }`, où `items` contient des résumés de
matchs triés du plus récent au plus ancien.

**Interface** :

- score, équipes, date, statut, journée, stade, mi-temps, arbitre ;
- buts, cartons, remplacements, compositions et statistiques lorsque le
  fournisseur les expose ;
- classement et forme des deux équipes ;
- derniers matchs **antérieurs à la date du match consulté** (maximum trois par équipe) ;
- confrontations directes chargées à la demande, avec résumé
  (nombre de matchs, buts, V/N/D) et état vide ;
- boutons « Réessayer » sur les erreurs de match et de confrontations.

## 6. Robustesse et affichage

- `frontend/index.html` est un document HTML complet : `doctype`, `lang="fr"`,
  `charset UTF-8`, `meta viewport`, titre, description et favicon. Sans
  `meta viewport`, un téléphone rendait la page en 980 px.
- Les blocs secondaires (matchs, statistiques, prochains matchs, confrontations)
  proposent un bouton « Réessayer » après une erreur.
- Les tableaux larges sont défilables horizontalement sur petit écran, avec une
  indication visible ; les colonnes numériques ne se coupent pas.
- Les états chargement, vide et erreur sont couverts sur l'accueil, les
  championnats, les matchs, les statistiques, les favoris, la fiche équipe et le
  détail de match.

## 7. Critères d'acceptation vérifiés

- Les six championnats s'affichent avec leur classement complet et leur calendrier.
- La pagination, le tri et les filtres des matchs de la V2 restent cohérents avec l'API (non-régression).
- Les prochains matchs sont triés et excluent les rencontres déjà commencées.
- Les statistiques buts/passes sont triées et basculables.
- Les favoris sont ajoutés, consultés, conservés, cloisonnés et supprimés.
- Les confrontations et les derniers matchs sont cohérents avec la date du match.
- Les erreurs API et les états vides ne produisent pas d'erreur JavaScript.
- L'interface reste utilisable de 320 px à 1920 px.

## 8. Limites connues

- Le fournisseur gratuit limite à 10 requêtes/minute ; le cache de 300 s réduit
  la consommation. Une erreur transitoire reste possible et l'interface propose
  un réessai.
- Le repli du prochain match couvre le championnat de l'équipe ; un match d'une
  autre compétition situé au-delà de 10 jours peut ne pas être affiché.
- Le fournisseur peut renvoyer moins de confrontations que le nombre annoncé
  dans `aggregates` ; l'interface s'appuie sur les éléments réellement reçus.
- Les anomalies ANO-001 à ANO-005 restent ouvertes et documentées.
