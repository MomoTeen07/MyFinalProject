# Journal des modifications

Toutes les évolutions notables de ce dépôt sont consignées ici.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnage sémantique.

## [Non publié]

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
