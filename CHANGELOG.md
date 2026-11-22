# Journal des modifications

Toutes les évolutions notables de ce dépôt sont consignées ici.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnage sémantique.

## [Non publié]

### Ajouté — V2, F3b : bloc presse RMC Sport (22/11/2026)

- **API** : `GET /api/football/press?limit=5` (`limit` de 1 à 10). Réponse
  `{ available, source, fetchedAt, items: [{ title, link, publishedAt }] }`.
- **Règle d'or** : la route renvoie **toujours `200`**. Timeout, statut non-200,
  XML invalide ou flux vide → `available: false` et `items: []`. Aucun `5xx` :
  une source externe non contractuelle ne peut pas casser l'accueil.
- **Traitement** : `xml.etree.ElementTree` (bibliothèque standard, aucune
  dépendance ajoutée), suppression des balises HTML, normalisation des espaces,
  titre tronqué à 140 caractères, seuls titre / lien / date conservés, liens non
  HTTP écartés, date RFC 822 convertie en ISO 8601 UTC, tri du plus récent.
- **Cache et configuration** : `PRESS_CACHE_TTL_SECONDS` (600 s),
  `PRESS_FEED_URL`, `PRESS_TIMEOUT_SECONDS` (5 s), transmis par Compose et
  documentés dans `.env.example`.
- **Interface** : section « À la une » sous les résultats, attribution
  « Source : RMC Sport », liens `target="_blank"` +
  `rel="noopener noreferrer"`, masquée si le flux est indisponible.
- **Tests** : 6 tests unitaires hors ligne (`backend/tests/test_press.py` :
  parsing, timeout, XML invalide, HTTP 503, troncature, limite), 3 tests API,
  1 test UI tolérant (bloc visible *ou* masqué), 2 requêtes Postman. Nouveau
  schéma `tests/pytest/schemas/press_schema.json`.
  Validation du 22/11/2026 en réel : flux disponible (30 titres, 5 exposés),
  backend **10 passed**, API **75 passed + 4 xfailed**, Postman **64 assertions
  / 0 échec**, Playwright **23 passed**.
- **Documentation** : `docs/V2_SPEC.md`, `docs/TEST_CASES.md` (TC-PRESS-01 à 03),
  `docs/TRACEABILITY.md` (R-19), `README.md`, `.env.example`.

### Ajouté — V2, F3a : actualités récentes (22/11/2026)

- **API** : `GET /api/football/news?days=7&limit=10`. Réponse
  `{ window: { from, to, days }, items }`. Ne conserve que les matchs
  **terminés** des 6 championnats supportés (le fournisseur renvoie aussi BSA,
  DED et ELC), exige un score complet, trie par date décroissante puis par
  identifiant décroissant.
- **Contrainte fournisseur découverte** : le plan gratuit refuse une plage
  `dateFrom`/`dateTo` de plus de 10 jours d'écart (HTTP 400 : 11 jours passent,
  12 échouent). `days` est donc borné à `1..10` côté API, ce qui renvoie un
  `422` explicite au lieu d'un `502` opaque (`NEWS_MAX_DAYS`).
- **Titre généré** côté service, en français, trois branches testables :
  victoire domicile, victoire extérieur, match nul. Vérifié en réel :
  « Real Madrid CF s'impose 2-1 face à RC Celta de Vigo ».
- **Interface** : section « Résultats récents » sur la page d'accueil,
  5 éléments, compétition, titre, score et temps relatif en français
  (`Intl.RelativeTimeFormat`), états chargement / erreur / vide.
- **Mode simulé** : `MOCK_NEWS` déterministe couvrant les trois branches.
- **Tests** : 6 tests PyTest (contrat JSON Schema, compétitions supportées, tri,
  trois branches de titre, 5 paramètres invalides), 2 tests Playwright,
  2 requêtes Postman. Nouveau schéma `tests/pytest/schemas/news_schema.json`,
  nouvelle fixture Playwright `news`.
  Validation locale du 22/11/2026 en données réelles : PyTest **70 passed +
  4 xfailed**, Postman **59 assertions / 0 échec**, Playwright **22 passed**,
  backend **4 passed**.
- **Documentation** : `docs/V2_SPEC.md` (borne `days` corrigée), `docs/TEST_CASES.md`
  (TC-NEWS-01 à 04), `docs/TRACEABILITY.md` (R-18), `README.md`.

### Ajouté — V2, F2 : buteurs et passeurs (22/11/2026)

- **API** : `GET /api/football/leagues/{code}/scorers?limit=10&sort=goals|assists`.
  Réponse en enveloppe `{ competition, season, sort, items }`. `limit` borné à
  `1..50` (défaut 10), `sort` limité à `goals`/`assists`, championnat inconnu →
  `404`, paramètre invalide → `422`. Le classement applique quatre critères
  déterministes : métrique décroissante, puis buts, puis matchs joués croissants,
  puis nom du joueur. Le fournisseur ne sachant trier que par buts, un vivier de
  100 joueurs est récupéré puis trié côté application.
- **Normalisation** : `assists: null` renvoyé par le fournisseur (cas réel
  Haaland, 9 buts) est exposé comme `0`, jamais `null`. Compteurs non entiers
  ramenés à `0`.
- **Interface** : troisième onglet « Buteurs » dans la page championnat, avec
  bascule « Buts / Passes » (`aria-pressed`), tableau `#`, joueur, équipe (lien
  vers la fiche), matchs, buts, passes, colonne active mise en évidence, états
  chargement / erreur / vide et libellé de saison.
- **Mode simulé** : jeu `MOCK_SCORERS` déterministe pour les 6 championnats,
  couvrant égalités de buts, départage par matchs puis par nom, et `assists`
  absent.
- **Tests** : 9 tests PyTest (contrat JSON Schema, ordre déterministe,
  `null` → 0, tri par passes, 4 paramètres invalides, 404), 3 tests Playwright,
  4 requêtes Postman. Nouveau schéma `tests/pytest/schemas/scorers_schema.json`.
  Validation locale du 22/11/2026 en données réelles : PyTest **61 passed +
  4 xfailed**, Postman **52 assertions / 0 échec**, Playwright **20 passed**,
  backend **4 passed**.
- **Documentation** : `docs/V2_SPEC.md` (périmètre V2), `docs/TEST_CASES.md`
  (TC-SCOR-01 à 04), `docs/TRACEABILITY.md` (R-17), `README.md`.

### Modifié

- **Suites QA rejouées sur les données réelles** (21/11/2026) : la CI force
  `MOCK_FOOTBALL_API=false`, exige le secret `FOOTBALL_API_TOKEN` (garde-fou
  explicite si absent) et porte `FOOTBALL_CACHE_TTL_SECONDS` à 900 s. Les
  attentes figées du référentiel simulé (4 équipes, « Arsenal », 3 matchs,
  « Football QA Stadium ») sont remplacées par des **invariants** et par un
  **oracle API** : la fixture Playwright `football` lit le classement et le
  calendrier réels, puis compare l'interface aux réponses de l'API. PyTest
  ajoute une reprise bornée sur 5xx transitoire. Fichiers :
  `tests/pytest/tests/test_football.py`,
  `tests/playwright/fixtures/test.js`,
  `tests/playwright/tests/championships.spec.js`,
  `tests/playwright/tests/favorites.spec.js`,
  `postman/Football-QA.postman_collection.json`, `.github/workflows/ci.yml`.
  Validation locale du 21/11/2026 : PyTest **52 passed, 4 xfailed**,
  Postman **41 assertions / 0 échec**, Playwright **17 passed**.

- **`README.md`** : la section « Impact sur les tests et la campagne » décrit
  désormais l'exécution en données réelles, l'oracle API et le rôle du mode
  simulé (développement hors ligne et tests unitaires uniquement).

### Corrigé

- **Double exécution de la CI sur les branches de travail** (22/11/2026) : la
  clé `push` sans filtre déclenchait un pipeline en plus de celui de la pull
  request. Deux backends interrogeaient alors le fournisseur en parallèle et
  épuisaient le quota de 10 requêtes/minute (un `503` transitoire a fait échouer
  une fiche équipe). Le workflow ne s'exécute plus sur les push de branches
  (`branches: [main]`). Le test du lien « buteur → équipe » vérifie désormais la
  cible du lien sans navigation, ce qui supprime un appel fournisseur inutile
  et rend le test déterministe.

- **`FOOTBALL_CACHE_TTL_SECONDS` ignoré par Compose** : la variable était
  documentée (README, `.env.example`) mais n'était pas transmise au conteneur
  backend, qui retombait sur sa valeur par défaut de 300 s. Elle est désormais
  passée par `docker-compose.yml` (`${FOOTBALL_CACHE_TTL_SECONDS:-300}`), ce qui
  rend le réglage du cache réellement effectif, en particulier avec l'API
  football-data.org.

- **CI rouge depuis le 10 novembre 2026** : le test `home displays football QA`
  échouait en mode strict car le libellé « Football QA » apparaît trois fois
  dans la page (navigation, carte de présentation, en-tête du formulaire). Le
  test cible désormais le titre de la carte avec
  `getByRole('heading', { name: 'Football QA', exact: true })`.

### Ajouté

- **ANO-005** (`docs/ANOMALIES.md`) : en données réelles, une équipe inconnue
  est traduite en `502` au lieu de `404` par `football_service._fetch`. Le
  défaut n'apparaît pas en mode simulé ; il est couvert par le test
  `test_unknown_team_returns_404` marqué `xfail` conditionnel.

- **Documentation du mode « données réelles »** (README § *Données réelles*) :
  création d'un compte gratuit football-data.org, renseignement local de
  `FOOTBALL_API_TOKEN` et `MOCK_FOOTBALL_API=false`, recréation du backend,
  vérification du classement complet. La section précise les quotas du plan
  gratuit (10 requêtes/minute), le rôle du cache `FOOTBALL_CACHE_TTL_SECONDS`,
  et le fait que la **campagne V1 a été exécutée en mode simulé** (assertions à
  4 équipes) ; les suites automatisées ont depuis été rendues indépendantes du
  référentiel et rejouées sur les données réelles. `docs/TEST_PLAN.md` est
  aligné : le
  hors-périmètre et l'hypothèse H4 distinguent désormais le référentiel de la
  campagne et l'option « données réelles ». `.env.example` est commenté (mode
  simulé par défaut, marche à suivre pour le mode réel, jamais de jeton
  versionné).
- **`PROJECT_CONTEXT.md`** : commit de référence et tableau des PR tenus à jour
  (#8 à #13), piège « mode réel » et **§ 11.3 « Mode de données : simulé ou
  réel »** (propre à chaque PC, procédure d'activation, retour au simulé,
  résultats mesurés le 15/11/2026). La référence de commit est désormais
  volontairement générique (`git log -1`) pour ne plus se périmer à chaque
  fusion.
- **Collection Postman complète** (`postman/`) : 18 requêtes et 41 assertions
  couvrant inscription, connexion, session, contrats football, scénario chaîné
  des favoris et contrôles de sécurité (`alg: none`, jeton absent ou malformé).
  Exécutable avec Newman, y compris en CI (`postman-report.xml`).
- **Suite API PyTest étendue** : fixtures de comptes uniques, contrats JSON
  Schema (`schemas/`), jeux de données négatifs (`data/`), scénario chaîné,
  cloisonnement des comptes et tests de sécurité. **53 passed, 3 xfailed**
  (anomalies documentées ANO-001, ANO-002, ANO-004).
- **Rapports Allure** : `allure-pytest` pour les suites backend et API,
  `allure-playwright` pour la suite UI. La CI agrège les trois jeux de
  résultats et publie un rapport HTML unique en artefact.
- **Artefacts d'échec UI** : traces, captures et vidéos conservées dans
  `tests/playwright/test-results/` (`trace: retain-on-failure`) pour rendre
  chaque anomalie reproductible.
- **Suite UI Playwright en Page Object Model** : 6 page objects, fixtures de
  comptes uniques, **17 tests** couvrant l'authentification, les championnats,
  le classement, le calendrier, la fiche équipe, le parcours critique des
  favoris et le cloisonnement entre deux comptes.
- **Livrables QA documentaires** (`docs/`) :
  - `TEST_PLAN.md` : périmètre, hypothèses, analyse de risques (probabilité ×
    impact), critères d'entrée et de sortie, organisation ;
  - `TEST_CASES.md` : 36 cas manuels (partitions d'équivalence, valeurs
    limites, tables de décision) avec résultats d'exécution ;
  - `ANOMALIES.md` : rapports ANO-001 à ANO-004 avec procédure de reproduction,
    preuve, gravité, priorité et correction proposée ;
  - `TRACEABILITY.md` : matrice exigence → cas → exécution → anomalie et
    couverture des 11 endpoints ;
  - `CAMPAIGN_REPORT.md` : métriques, bilan des anomalies, risques résiduels et
    recommandations priorisées ;
  - `DEFENSE.md` : trame de soutenance, script de démonstration et questions
    probables.
- **Campagne Squash TM** (`infra/squash/`) : Squash TM 15.0.3 et PostgreSQL 17
  isolés dans un compose dédié (port `8090`). Le script `seed_campaign.py`
  (bibliothèque standard uniquement) crée par API REST le projet *Football QA*,
  4 dossiers, **16 exigences**, **36 cas de test** avec pas et couvertures, la
  campagne `CAMP-V1`, son itération, la suite des 36 cas et les 36 exécutions
  (**32 `SUCCESS`**, **4 `FAILURE`** rattachées à ANO-001 à ANO-004). Le jeu de
  données `campaign_data.json` est dérivé des documents QA. Procédure complète :
  `docs/SQUASH.md`.
- **Traçabilité du choix de l'application** : section « Choix de l'application »
  dans le README et § 1.1 du plan de test, avec la correspondance critère par
  critère de l'énoncé (interface, API authentifiée, persistance, exécution
  locale, complexité, accès licite) et la mention de la validation par le
  formateur avant le début des travaux. Hypothèse H1 mise à jour et question
  « Pourquoi cette application ? » ajoutée au support de soutenance.
- **`PROJECT_CONTEXT.md`** : point de reprise du projet (état du dépôt et des
  environnements, historique des PR, commandes de redémarrage en 5 minutes,
  vérifications attendues, deux copies du dépôt, règles de travail, pièges
  connus, actions manuelles restantes, index des documents). Référencé en tête
  du README. Complété par une section « Changer de PC » (ce qui se synchronise
  ou non, procédure d'arrivée, précautions).

### Supprimé

- Dossier `bruno/` : remplacé par la collection Postman, conformément à
  l'exigence de l'énoncé (« Postman ou Bruno »).

### Modifié

- `.gitignore` : exclusion de `allure-results/`, `allure-report/`,
  `test-results/`, `playwright-report/` et `.venv*/`.
- Le fichier `tests/playwright/test-results/.last-run.json`, précédemment
  versionné, est retiré du suivi Git.
- `docs/CAMPAIGN_REPORT.md` et `docs/DEFENSE.md` : référence explicite à la
  campagne Squash TM (32 `SUCCESS` / 4 `FAILURE`) et séquence de démonstration
  dédiée. Les métriques du résumé exécutif sont alignées sur le tableau
  détaillé (118 vérifications, 115 réussies, 3 `xfail`).
