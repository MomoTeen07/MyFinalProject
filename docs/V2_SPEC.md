# Spécification V2 — Football QA

| Élément | Valeur |
|---|---|
| Statut | **Proposition à valider** — aucun code ne démarre avant accord |
| Base | `main` figé par le tag `v1.0-campagne-v1` (`eabd40f`) |
| Branche de développement | `app/v2` |
| Objectif | Enrichir l'application support **sans invalider** la démarche QA déjà produite |
| Dernière révision | 22/11/2026 — note de favori, rôle admin et profil écartés ; actualités (résultats + presse RMC) ajoutées |

## 1. Principes

1. **Additif uniquement.** On ajoute des fonctionnalités, on ne réécrit pas l'existant.
2. **Défauts conservés.** ANO-001 à ANO-005 restent ouvertes : elles sont la preuve
   de la campagne et le support de démonstration. Corriger un défaut = perdre une
   anomalie reproductible.
3. **Une fonctionnalité = une PR = une CI verte.** Pas de méga-branche.
4. **Les tests ne sont jamais supprimés.** Ils sont adaptés au fil de l'eau, dans
   la même PR que le changement d'API.
5. **Aucune refonte visuelle.** Le CSS et les composants existants sont réutilisés.
6. **Aucune migration de base** : la V2 n'ajoute aucune colonne.

## 2. Périmètre retenu (4 fonctionnalités)

### F1 — Pagination, tri et filtres des matchs

- **Besoin** : en données réelles, la Premier League renvoie 380 matchs, tous
  rendus d'un coup. Défaut de performance réel, aujourd'hui invisible en simulé.
- **API** : `GET /api/football/leagues/{code}/matches?page=1&page_size=50&status=&team_id=&sort=date|date_desc`
- **Contrat** : réponse en enveloppe `{ items, total, page, page_size, total_pages }`.
  **Changement cassant** assumé : le tableau nu disparaît.
- **Règles** : `page >= 1`, `1 <= page_size <= 100`, `status` dans une liste
  fermée (celle déjà utilisée par l'interface), `sort` dans `{date, date_desc}`,
  page au-delà de la dernière → `items: []`. Paramètre invalide → `422`.
- **Mise en œuvre** : filtrage et pagination **applicatifs**, après récupération
  et mise en cache de la liste complète. Déterministe, indépendant des
  capacités de filtrage du fournisseur, donc testable.
- **UI** : sélecteur de page, filtre de statut, tri. État « aucun résultat »
  distinct de l'erreur.
- **Valeur QA** : partitions d'équivalence, valeurs limites (`0`, `1`, `101`),
  combinaisons de filtres, stabilité de la pagination entre deux appels.

### F2 — Meilleurs buteurs et passeurs

- **Besoin** : valoriser les performances individuelles d'un championnat, et
  donner un second classement à tester (ordre, égalités, données manquantes).
- **Source** : `GET /competitions/{code}/scorers?limit=N` du fournisseur.
  **Constat du 22/11/2026** : `assists` vaut `null` (et non `0`) quand la donnée
  manque — ex. Haaland, 9 buts, `assists: null`. Ce cas est normalisé côté
  service et testé explicitement.
- **API** : `GET /api/football/leagues/{code}/scorers?limit=10&sort=goals|assists`
  - `limit` : `1..50`, défaut `10` ; `sort` : `goals` (défaut) ou `assists`.
  - Réponse : `{ competition, season, items: [{ position, player, team,
    goals, assists, penalties, playedMatches }] }`.
- **Règles de classement (déterministes, donc testables)** :
  1. tri décroissant sur la métrique demandée ;
  2. égalité → plus de buts marqués ;
  3. nouvelle égalité → moins de matchs joués ;
  4. dernière égalité → nom du joueur, ordre alphabétique.
  `assists` absent du fournisseur est exposé comme `0` (jamais `null`).
- **Erreurs** : championnat inconnu → `404` avant appel fournisseur ;
  `limit` hors bornes ou `sort` inconnu → `422` ; aucune donnée → `200` avec
  `items: []`.
- **Mode simulé** : jeu `MOCK_SCORERS` déterministe pour les 6 championnats,
  afin que les tests unitaires restent hors ligne.
- **UI** : troisième onglet « Buteurs » dans la page championnat, avec bascule
  **« Buts / Passes »** dans un seul onglet (décision du 22/11/2026), tableau
  `#`, joueur, équipe (lien vers la fiche), matchs, buts, passes. `limit`
  par défaut : **10**. États chargement / erreur / vide réutilisés.
- **Valeur QA** : tri multi-critères, égalités, `null` vs `0`, bornes de `limit`,
  énumération de `sort`, état vide, cohérence UI ↔ API, liens joueur → équipe.

### F3 — Actualités au démarrage : résultats récents + presse

Deux blocs distincts sur la page d'accueil, avec des garanties différentes.

#### F3a — Fil de résultats récents (socle, fiable)

- **Besoin** : afficher les résultats marquants des derniers jours dès
  l'ouverture de l'application.
- **Source** : `GET /matches?dateFrom=...&dateTo=...` (endpoint global).
  **Constat du 22/11/2026** : 57 matchs sur 7 jours, dont **29 terminés** dans
  nos 6 championnats, en **un seul appel** fournisseur (contre 6 si on
  interrogeait chaque championnat). Le cache s'applique comme ailleurs.
- **API** : `GET /api/football/news?days=7&limit=10`
  - `days` : `1..30`, défaut `7` ; `limit` : `1..20`, défaut `10`.
  - Réponse : `{ window: { from, to, days }, items: [{ id, competition,
    utcDate, status, homeTeam, awayTeam, score, headline }] }`.
- **Règles** :
  - ne conserver que les matchs **terminés** de nos 6 championnats
    (le fournisseur renvoie aussi BSA, DED, ELC) ;
  - score complet obligatoire, sinon le match est ignoré ;
  - tri : date décroissante, puis identifiant décroissant (déterministe) ;
  - `headline` généré côté service, en français, trois branches testables :
    - victoire domicile : `« {home} s'impose {h}-{a} face à {away} »` ;
    - victoire extérieur : `« {away} s'impose {a}-{h} sur le terrain de {home} »` ;
    - match nul : `« {home} et {away} se quittent dos à dos ({h}-{a}) »`.
- **Erreurs** : `days` ou `limit` hors bornes → `422` ; aucun match terminé →
  `200` avec `items: []` ; panne fournisseur → `502`/`503` (comportement actuel,
  ANO-005 non corrigée).
- **Mode simulé** : `MOCK_NEWS` déterministe, couvrant les trois branches de
  `headline`.
- **Valeur QA** : trois branches de formatage, bornes `days`/`limit`, état vide,
  ordre stable, fuseau horaire, indépendance vis-à-vis des compétitions non
  supportées, coût fournisseur (un seul appel).

#### F3b — Bloc « Presse » (RMC Sport, dégradation gracieuse)

- **Besoin** : donner un vrai effet « actualités » avec des titres éditoriaux
  en français.
- **Source** : flux RSS `https://rmcsport.bfmtv.com/rss/football/`
  (HTTP 200, 30 items, vérifié le 22/11/2026). Aucune clé, budget 0 €.
- **API** : `GET /api/football/press?limit=5` — `limit` : `1..10`, défaut `5`.
  - Réponse : `{ available, source: { name, url }, fetchedAt, items: [
    { title, link, publishedAt } ] }`.
- **Règle d'or — jamais bloquant** : toute erreur (timeout 5 s, statut non-200,
  XML invalide, zéro item) renvoie **`200`** avec `available: false` et
  `items: []`. Aucune route de presse ne renvoie `5xx`. Le bloc disparaît
  proprement côté interface.
- **Traitement** : parsing `xml.etree.ElementTree` (bibliothèque standard, aucune
  dépendance ajoutée), suppression des balises HTML, titre tronqué à 140
  caractères, seuls `title`, `link` et `publishedAt` sont conservés.
- **Cache** : 600 s par défaut (`PRESS_CACHE_TTL_SECONDS`), pour rester discret
  vis-à-vis du site source.
- **Configuration** : `PRESS_FEED_URL`, `PRESS_TIMEOUT_SECONDS` (5),
  `PRESS_CACHE_TTL_SECONDS` (600). L'URL est surchargeable pour tester l'échec
  sans réseau.
- **Attribution et légalité** : le bloc affiche « Source : RMC Sport » et chaque
  titre pointe vers l'article d'origine (`target="_blank"`,
  `rel="noopener noreferrer"`). Aucun contenu intégral, aucune image, aucune
  réécriture : uniquement titre + lien + date.
- **UI** : bloc « Presse » sous le fil de résultats, masqué si
  `available: false`. Aucun état d'erreur visible pour l'utilisateur.
- **Valeur QA** : parsing XML, encodage, champs manquants, flux indisponible →
  `200` + `available:false`, bornes de `limit`, cache, absence de fuite de HTML,
  test négatif avec une URL injoignable (`http://127.0.0.1:9/`).
- **Limite assumée** : le flux est un contrat non versionné. C'est pourquoi il
  est isolé, caché, non bloquant, et que les tests d'interface restent
  **tolérants** (bloc visible *ou* masqué, jamais d'échec).

### F4 — Page détail d'un match

- **Besoin** : nouveau parcours de bout en bout, et gestion du `404` fournisseur.
- **API** : `GET /api/football/matches/{id}` (relais du fournisseur).
- **UI** : `/matches/:id` — compétition, statut, score, équipes, date.
  Liens ajoutés depuis la liste des matchs **et** depuis les actualités.
- **Règles** : identifiant inconnu → `404` (sert de cas concret pour ANO-005,
  sans la corriger).
- **Valeur QA** : parcours E2E supplémentaire, dépendance à une donnée externe
  non déterministe (oracle API).

## 3. Hors périmètre (explicite)

- Correction d'ANO-001 à ANO-005.
- **Note personnelle sur un favori** — écartée le 22/11/2026.
- **Rôle administrateur et matrice de permissions** — écarté le 22/11/2026.
- **Profil et changement de mot de passe** — écarté le 22/11/2026 (non
  essentiel : la régression d'authentification reste couverte par les tests
  existants et ANO-004).
- **Contenu éditorial complet** (corps d'article, images, réécriture) : le bloc
  presse se limite à titre + lien + date, avec attribution explicite. Aucune
  republication de contenu.
- **Seconde source de presse** : un seul flux (RMC Sport). Pas d'agrégation
  multi-sources, pas de repli automatique sur BBC.
- Paiement, messagerie, notifications, temps réel.
- Upload de fichiers, avatars, i18n, thème sombre, refonte graphique.
- Modification de l'e-mail ou suppression de compte.
- Refresh token, révocation de jeton, MFA.
- Toute modification du projet `football-qa-agents` (en stand-by).

## 4. Modèle de données et migrations

**Aucune migration Alembic.** Les quatre fonctionnalités réutilisent le schéma
existant :

- `users` et `favorites` : inchangés ;
- matchs, buteurs, actualités : données du fournisseur, mises en cache en
  mémoire, non persistées.

C'est un choix délibéré : moins de risque de régression, et la base reste
strictement identique à celle de la campagne V1.

## 5. Contrats d'API (récapitulatif)

| Méthode | Route | Accès | Statuts |
|---|---|---|---|
| GET | `/api/football/leagues/{code}/matches` | public | 200, 404, 422 |
| GET | `/api/football/leagues/{code}/scorers` | public | 200, 404, 422 |
| GET | `/api/football/news` | public | 200, 422, 502, 503 |
| GET | `/api/football/press` | public | **200 uniquement** (`available: false` en cas d'échec) |
| GET | `/api/football/matches/{id}` | public | 200, 404, 502 |

On passe de 11 à **15 endpoints**. La route `press` est la seule du projet à ne
jamais renvoyer d'erreur : c'est un choix explicite pour qu'une source externe
non contractuelle ne puisse pas casser l'accueil.

## 6. Impact QA (à prévoir dès la première PR)

| Élément | Impact |
|---|---|
| `tests/pytest/tests/test_football.py` | contrat `matches` en enveloppe, pagination, filtres, buteurs (tri, égalités, `null` → `0`, bornes), actualités (3 branches, bornes, état vide) |
| `tests/pytest/tests/test_press.py` | **nouveau fichier** : flux valide simulé, flux injoignable → `200` + `available:false`, XML invalide, flux vide, bornes de `limit`, nettoyage HTML, troncature |
| `tests/pytest/tests/test_favorites.py` | **aucun changement** |
| `tests/pytest/tests/test_auth.py` | **aucun changement** |
| `tests/pytest/tests/test_security.py` | **aucun changement** |
| Schémas JSON | `matches` (enveloppe), nouveaux `scorers`, `news` et `press` |
| Postman | 3 dossiers + assertions (objectif ≈ 55) |
| Playwright | pagination/filtres, onglet buteurs, actualités à l'accueil, détail match, bloc presse **tolérant** (visible *ou* masqué) |
| `docs/TEST_CASES.md` | +15 à +18 cas manuels |
| `docs/TRACEABILITY.md` | nouvelles exigences R-17 à R-20 |
| Squash TM | nouvelles exigences et cas, campagne V2 |
| `docs/CAMPAIGN_REPORT.md` | métriques V2, anomalies nouvelles |
| `README.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` | mis à jour à chaque PR |

**Règle de non-régression CI** : aucun test automatisé ne doit dépendre de la
disponibilité de RMC Sport. Les tests de la presse utilisent exclusivement un
flux local simulé (fixture XML) ou une URL volontairement injoignable. En CI,
seul le fil de résultats (football-data.org) reste une dépendance externe réelle.

## 7. Séquencement proposé

1. **PR V2-0** : cette spécification (documentation seule).
2. **PR V2-1** : F2 buteurs/passeurs — la moins risquée, aucune migration,
   immédiatement démontrable.
3. **PR V2-2** : F3a fil de résultats récents — visible dès l'accueil, un seul
   appel fournisseur, aucun risque de rupture.
4. **PR V2-3** : F3b bloc presse RMC — isolé, non bloquant, testé hors ligne.
5. **PR V2-4** : F4 détail de match — active les liens depuis la liste et les
   actualités.
6. **PR V2-5** : F1 pagination — seul changement cassant, traité quand le reste
   est stable.
7. **PR V2-6** : campagne V2 (traçabilité, Squash, rapport, démo).

Chaque PR : code + tests adaptés + docs + CI verte. Aucune PR ne casse `main`.

## 8. Definition of Done (par fonctionnalité)

- [ ] Implémentation backend (sans migration si possible)
- [ ] Tests backend, API et UI adaptés ou ajoutés, verts en local **et** en CI
- [ ] Collection Postman mise à jour
- [ ] `README.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` à jour
- [ ] Aucun secret dans le diff, aucune régression sur les suites existantes
- [ ] Anomalies existantes toujours reproductibles

## 9. Décisions à valider avant tout code

1. **Périmètre** : les 4 fonctionnalités (F1, F2, F3a+F3b, F4), ou 3 en reportant
   la pagination (F1) ?
2. **Pagination** : accepter le changement cassant de contrat (enveloppe
   `{items, total, page, page_size, total_pages}`) ?
3. **Ordre** : valider la séquence F2 → F3a → F3b → F4 → F1 ?

Déjà tranché : bascule Buts/Passes dans un seul onglet, `limit` à 10 pour les
buteurs, actualités = résultats récents **+** bloc presse RMC avec dégradation
gracieuse, aucune migration de base.

## 10. Risques identifiés et parades

| Risque | Impact | Parade retenue |
|---|---|---|
| Flux RSS RMC non contractuel (structure modifiable, accès révocable) | Bloc presse cassé silencieusement | Route toujours `200`, `available:false`, parsing tolérant, test avec flux local |
| Quota football-data.org (10 req/min) | `502` transitoires (déjà observé, ANO-005) | Cache existant, un seul appel pour les actualités, pas d'appel supplémentaire par championnat |
| Changement de contrat sur `matches` (enveloppe) | Tests et interface existants cassés | Traité en dernier (V2-5), tests adaptés dans la même PR |
| Contenu éditorial tiers | Risque juridique | Titre + lien + date uniquement, attribution « Source : RMC Sport », aucune image |
| Démo dépendante du réseau | Soutenance fragile | Mode simulé disponible (`MOCK_FOOTBALL_API=true`) et bloc presse masquable |

## 11. Ce que la V2 apporte à la démarche QA (argumentaire soutenance)

- Une **deuxième source externe** traitée avec une stratégie de dégradation
  gracieuse : illustration concrète de la gestion du risque fournisseur.
- Un **classement** (buteurs/passeurs) qui exerce tri multi-critères, égalités et
  données manquantes (`null` → `0`) : cas limites réels, pas inventés.
- Un **changement de contrat assumé et planifié** (pagination) : montre la
  maîtrise de l'impact sur les tests existants.
- Un **parcours E2E supplémentaire** (détail de match) sans corriger les
  anomalies existantes, qui restent la matière des rapports d'anomalie.
