# Football QA

Application web de consultation du football, conçue comme support d’un projet final QA.

> **État : V3 terminée, campagne finale close.** 59 cas manuels, 222 vérifications
> passantes + 4 `xfail`, 5 anomalies, 18/18 endpoints, Squash 54/5. Détail dans
> [`CAMPAIGN_REPORT.md`](CAMPAIGN_REPORT.md).

> **Reprise du travail** : l’état d’avancement, les environnements locaux, les
> commandes de vérification et les pièges connus sont consignés dans
> [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md). C’est le point d’entrée pour
> reprendre le projet là où il s’est arrêté.

## Choix de l’application

Football QA a été retenue comme application support du projet final. Le choix a
été **soumis au formateur et validé avant le début des travaux**, afin de
garantir un niveau de difficulté comparable entre stagiaires.

| Critère de l’énoncé | Réponse de Football QA | Preuve dans le dépôt |
|---|---|---|
| Application web avec interface utilisateur | Frontend React/Vite servi par Nginx : connexion, inscription, actualités et presse, prochains matchs, championnats, classement, calendrier paginé, détail de match, buteurs, fiche équipe enrichie, tableau de bord des favoris | `frontend/src/pages/`, `tests/playwright/` |
| API testable avec authentification | API REST FastAPI, 18 endpoints, jeton JWT `Bearer` sur les routes personnelles | `backend/app/api/`, `postman/` |
| Persistance et règles métier | PostgreSQL 16 avec migrations Alembic : comptes, favoris uniques par utilisateur, cloisonnement des données | `backend/app/db/`, `docs/CONCEPTION.md` |
| Exécutable localement | Docker Compose (3 conteneurs), mode de données simulé sans clé ni service payant | `docker-compose.yml`, section « Démarrage local » |
| Complexité suffisante | Parcours visiteur et authentifié, états de chargement et d’erreur, données d’une API externe, pages dédiées (accueil, championnats, championnat, équipe, favoris, détail de match, authentification) et parcours V3 (prochains matchs, fiche équipe enrichie, tableau de bord, confrontations) | `docs/TEST_PLAN.md` § 4 |
| Accès licite | Dépôt applicatif du projet, code source accessible, aucune restriction de test | ce dépôt |

La validation est antérieure à la campagne V1 (13/11/2026). Les anomalies
relevées portent sur cette application **non modifiée** : aucun correctif
applicatif n’a été appliqué, les défauts sont documentés et rejoués par les
tests marqués `xfail` (voir `docs/ANOMALIES.md`).

## Stack

- Frontend : React, Vite et CSS
- Backend : Python, FastAPI et SQLAlchemy
- Authentification : JWT
- Base de données : PostgreSQL avec migrations Alembic
- Données de football : football-data.org ou données simulées
- Conteneurs : Docker Compose
- Tests : PyTest, Playwright, collection Postman

## Démarrage local avec Docker

1. Copiez `.env.example` vers `.env`.
2. Remplacez `JWT_SECRET` par une chaîne aléatoire privée d’au moins 32 caractères. Le backend refuse la valeur d’exemple.
3. Les identifiants PostgreSQL de l’exemple conviennent uniquement au développement local. Changez-les si le service doit être accessible à d’autres machines.
4. Ajoutez un jeton `FOOTBALL_API_TOKEN` pour les données réelles, ou gardez `MOCK_FOOTBALL_API=true` pour utiliser les données simulées.
5. À la racine du projet, lancez :

   ```bash
   docker compose up --build
   ```

L’application et l’API sont publiées sur `127.0.0.1` par défaut :

- Application : <http://localhost:5174>
- API : <http://localhost:8001>
- Documentation Swagger : <http://localhost:8001/docs>
- PostgreSQL : `localhost:5433`

Compose transmet les appels `/api` du frontend au backend via Nginx. Il lance les migrations Alembic avant de démarrer l’API. Le premier démarrage adopte le schéma existant sans recréer les tables ni supprimer les comptes et favoris.

## Développement du frontend

Dans `frontend/`, installez les versions verrouillées puis démarrez Vite :

```bash
npm ci
npm run dev
```

Utilisez Node.js 22 ou une version compatible avec les versions de Vite verrouillées. Le proxy Vite envoie les appels `/api` vers le backend local sur `http://localhost:8001`.

Pour lancer aussi le backend directement sur la machine, démarrez PostgreSQL avec Docker Compose, installez `backend/requirements.txt`, puis depuis `backend/` lancez `alembic upgrade head` et `uvicorn app.main:app --reload --port 8001`. L’URL de base `DATABASE_URL` de `.env.example` vise PostgreSQL sur `localhost:5433`.

## Migrations de base de données

Les révisions Alembic se trouvent dans `backend/migrations/versions/`. Pour créer une migration après une évolution des modèles :

```bash
docker compose exec backend alembic revision --autogenerate -m "description du changement"
```

Relisez et ajustez toute migration générée avant de la conserver. Les migrations s’appliquent au prochain démarrage du backend. La migration initiale est une migration de référence et son retour arrière ne supprime pas les données.

## Environnement de tests

Les commandes ci-dessous préparent et lancent les tests déjà présents ; aucun test n’est exécuté au démarrage de l’application.

Tests du backend :

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest tests
```

Collection Postman (scénario chaîné et contrôles de sécurité), avec l’application démarrée par Docker :

```bash
npx --yes newman@6 run postman/Football-QA.postman_collection.json \
  -e postman/Football-QA.postman_environment.json
```

La collection est également importable dans Postman : dossier `postman/`, variable `baseUrl` à adapter. Elle couvre l’inscription, la connexion, la session, les contrats football (buteurs et passeurs, actualités récentes, presse, prochains matchs, détail de match, confrontations directes, tableau de bord des favoris), le parcours favori complet et quatre contrôles de sécurité (31 requêtes, 76 assertions). Le détail est documenté dans `postman/README.md`.

Tests de contrat API, avec l'application démarrée par Docker :

```bash
python -m pip install -r tests/pytest/requirements.txt
REAL_FOOTBALL_DATA=true python -m pytest tests/pytest/tests --alluredir=allure-results-api
```

`REAL_FOOTBALL_DATA=true` indique que l'instance sert des données réelles : le
seul test dont l'attendu diffère du mode simulé (ANO-005) est alors marqué
`xfail`.

Tests Playwright, avec l’application accessible sur `http://localhost:5174` :

```bash
cd tests/playwright
npm ci
npm run install:browsers
npm test
```

Pour viser une autre adresse frontend, définissez `BASE_URL` avant `npm test`.

La suite UI suit le patron **Page Object Model** :

```
tests/playwright/
├── pages/        AuthPage, LoginPage, Navbar, ChampionshipsPage, ChampionshipPage, TeamPage, FavoritesPage
├── fixtures/     comptes uniques par l'API et session injectée
└── tests/        auth.spec.js, championships.spec.js, favorites.spec.js, match.spec.js, news.spec.js, smoke.spec.js
```

Chaque test crée son propre compte : aucun état partagé entre exécutions, donc
la suite est rejouable sans nettoyage de base. Les scénarios couvrent
l’authentification, les actualités et la presse de l’accueil, les prochains
matchs, les six championnats, le classement, le calendrier paginé, le détail
d'un match et ses confrontations, le classement des buteurs et des passeurs,
la fiche équipe enrichie, le parcours critique des favoris (ajout →
consultation → suppression) et le cloisonnement entre deux comptes.

### Rapports Allure

Les deux suites produisent le format standard Allure 2 :

- PyTest : `allure-results-api/` (option `--alluredir`).
- Playwright : `tests/playwright/allure-results/` (reporter `allure-playwright`).
- Backend : `allure-results-backend/` en CI.

Agrégation locale en un rapport HTML unique (nécessite Java 17) :

```bash
npm install --global allure-commandline
allure generate allure-results-api tests/playwright/allure-results --clean --output allure-report
allure open allure-report
```

En cas d’échec Playwright, `tests/playwright/test-results/` conserve la trace, la capture et la vidéo de chaque tentative : c’est la preuve à joindre à un rapport d’anomalie.

## Intégration continue

Le workflow `.github/workflows/ci.yml` s’exécute sur chaque **pull request**, sur les push vers `main` et sur lancement manuel. Les push de branches de travail ne déclenchent volontairement **qu’une seule** exécution (celle de la PR) : deux pipelines simultanés épuiseraient le quota de 10 requêtes/minute du fournisseur. Il prépare une base PostgreSQL éphémère, lance les tests unitaires backend puis les suites API, Postman et UI, agrège les résultats Allure (API + UI) et publie les artefacts `allure-report`, `allure-results-backend`, `playwright-report`, `postman-report` et, en cas d’échec, `playwright-test-results` (traces, captures, vidéos). Les identifiants configurés dans ce workflow sont réservés à cette base temporaire.

## Documentation QA

| Document | Contenu |
|---|---|
| [`docs/TEST_PLAN.md`](TEST_PLAN.md) | Périmètre, hypothèses, analyse de risques (P × I), critères d’entrée et de sortie, organisation |
| [`docs/TEST_CASES.md`](TEST_CASES.md) | 59 cas manuels (36 V1, 14 V2, 9 V3) avec technique de conception, étapes, attendu, obtenu et statut |
| [`docs/V3_SPEC.md`](V3_SPEC.md) | Spécification V3 et résultats de la campagne V3 |
| [`docs/ANOMALIES.md`](ANOMALIES.md) | Rapports ANO-001 à ANO-005 : contexte, reproduction, preuve, gravité, priorité, correction proposée |
| [`docs/TRACEABILITY.md`](TRACEABILITY.md) | Matrice 25 exigences → 59 cas → exécution → anomalie, et couverture des 18 endpoints |
| [`docs/CAMPAIGN_REPORT.md`](CAMPAIGN_REPORT.md) | Métriques finales V3, bilan des anomalies, risques résiduels, recommandations |
| [`docs/DEFENSE.md`](DEFENSE.md) | Trame de soutenance, script de démonstration, questions probables |
| [`docs/SQUASH.md`](SQUASH.md) | Campagne finale Squash TM : démarrage, création par script REST, vérification, limites |
| [`docs/CONCEPTION.md`](CONCEPTION.md) | Conception technique de l’application |

Synthèse de la **campagne finale V3** : **222 vérifications automatisées
passantes + 4 `xfail`** (19 backend, 100 API, 27 UI, 76 assertions Postman),
**59 cas manuels** (54 conformes, 5 anomalies), **18/18 endpoints** couverts,
**25/25 exigences** tracées, **6/6 risques critiques** couverts, pipeline vert.
Cinq anomalies sont documentées : ANO-001 à ANO-005.

> **Périmètre** : les résultats V1 (36 cas) ont été obtenus en mode simulé le
> 13/11/2026 ; les campagnes V2 (14 cas) et V3 (9 cas) ont été exécutées en
> données réelles. La campagne manuelle V3 est **terminée** : elle couvre les
> parcours enrichis et la non-régression en données réelles.

### V2 (terminée)

La V2 a ajouté des fonctionnalités sans corriger les anomalies de la V1
(voir [`docs/V2_SPEC.md`](V2_SPEC.md)). État au 22/11/2026 :

| Élément | V1 | V2 |
|---|---|---|
| Endpoints | 11 | 15 (buteurs, actualités, presse, détail de match) |
| Tests backend | 4 | 10 |
| Tests de contrat API | 52 passés + 4 `xfail` | 78 passés + 4 `xfail` |
| Assertions Postman | 41 | 69 |
| Tests UI Playwright | 17 | 25 |
| Cas manuels | 36 | 50 |

Vérifications du 22/11/2026 en **données réelles** : backend 10/10, API
78 passés + 4 `xfail`, Postman 69/69, Playwright 25/25.

### V3 (version livrée, campagne terminée)

La V3 s'appuie sur la pagination des matchs livrée en V2 et enrichit les
parcours sans corriger les anomalies volontairement conservées : prochains
matchs sur l'accueil, contexte de la fiche équipe, tableau de bord des favoris,
contexte du détail de match et confrontations directes.

| Élément | V2 | V3 |
|---|---|---|
| Endpoints | 15 | 18 (prochains matchs, confrontations, tableau de bord favoris) |
| Tests backend | 10 | 19 |
| Tests de contrat API | 78 passés + 4 `xfail` | 100 passés + 4 `xfail` |
| Assertions Postman | 69 (28 requêtes) | 76 (31 requêtes) |
| Tests UI Playwright | 25 | 27 |
| Cas manuels | 50 | 59 (36 V1 + 14 V2 + 9 V3) |
| Exigences tracées | 20 | 25 |

Vérifications du 25/11/2026 en **données réelles** : backend 19/19, API
100 passés + 4 `xfail`, Postman 76/76, Playwright 27/27. La campagne manuelle
V3 du 25/11/2026 ajoute **9 cas** : 8 conformes, 1 anomalie (ANO-005). La
vérification fonctionnelle couvre les six championnats, les états vides et
d'erreur, le mobile iPhone 13 (390 px) et Galaxy S9+ (320 px), sans débordement
horizontal ni erreur JavaScript.

### Versions et tags

| Repère | Commit | Usage |
|---|---|---|
| `v1.0-campagne-v1` | `eabd40f` | État consolidé après la campagne V1 et le passage des suites en données réelles |
| Application V1 testée | `a0ea6e6` | Commit de l'application au moment de la campagne V1 |
| `v3.0` | `3ba1ec9` | Version de code V3 |
| `v3.1-campagne-finale` | `db1923a` | Campagne finale V3 (contenu et rapports) |
| `v3.1.1-campagne-finale` | `main` après fusion | Clôture finale, CI verte et correctif Postman |

## Gestion de campagne (Squash TM)

La **campagne finale V3** est portée par **Squash TM 15.0.3**
(`infra/squash/docker-compose.yml`, `http://localhost:8090/squash`).

```bash
docker compose -f infra/squash/docker-compose.yml up -d
python infra/squash/build_campaign_data.py
python infra/squash/seed_campaign.py
```

Le script crée le projet *Football QA*, ses **25 exigences**, ses **5 dossiers**,
ses **59 cas de test** avec pas et couvertures, la campagne `CAMP-V3`, son
itération, la suite complète et les **59 exécutions** (**54 `SUCCESS`**, **5
`FAILURE`** pour ANO-001 à ANO-005). La campagne V1 (16 exigences / 36 cas) reste
l'historique documenté. Squash TM est un outil de gestion, pas une dépendance
des tests : il n’est pas démarré en CI. Procédure complète et limites dans
[`docs/SQUASH.md`](SQUASH.md).


## Configuration

Les ports, le bind local, les paramètres PostgreSQL, le secret JWT, les origines CORS, le cache football (`FOOTBALL_CACHE_TTL_SECONDS`) et le mode de données sont configurables dans `.env`. Le cache externe dure cinq minutes par défaut et peut être désactivé avec une valeur de `0`.

Le bloc presse se règle séparément : `PRESS_FEED_URL` (flux RSS, RMC Sport par défaut), `PRESS_TIMEOUT_SECONDS` (5 s) et `PRESS_CACHE_TTL_SECONDS` (600 s). Une panne du flux masque la section sans jamais renvoyer d'erreur. Utilisez des caractères URI sûrs dans `POSTGRES_PASSWORD`, ou encodez les caractères réservés avant de les inclure dans l’URL PostgreSQL générée par Compose.

Le port et les identifiants PostgreSQL par défaut sont réservés au développement local. Pour un déploiement, changez les secrets, limitez les origines CORS et utilisez un gestionnaire de secrets adapté à l’environnement.

## Données réelles (football-data.org)

Le **mode simulé** reste disponible (`MOCK_FOOTBALL_API=true`) : 6 championnats,
4 équipes par classement, 3 matchs et un jeu de buteurs déterministe, sans clé
ni quota. C’est le mode utilisé pour le développement hors ligne et pour les
tests unitaires du backend. La campagne V1 a été exécutée dans ce mode ; les
campagnes V2/V3, la CI et les suites automatisées tournent en **données réelles**
depuis le 21/11/2026.

Pour afficher les classements réels (20 équipes en Premier League, calendrier
complet) :

1. Créer un compte gratuit sur [football-data.org](https://www.football-data.org/client/register)
   (aucune carte bancaire) et récupérer le jeton API.
2. Renseigner **localement** dans `.env` — jamais dans Git :

   ```dotenv
   FOOTBALL_API_TOKEN=votre-jeton
   MOCK_FOOTBALL_API=false
   ```

3. Recréer le backend pour qu’il relise l’environnement :

   ```bash
   docker compose up -d --force-recreate backend
   ```

4. Vérifier :

   ```bash
   curl -s http://localhost:8001/api/football/leagues/PL/standings
   ```

   La réponse contient le classement complet ; l’interface
   `http://localhost:5174/championships/PL` affiche toutes les lignes.

### Quotas et cache

Le plan gratuit de football-data.org autorise **10 requêtes par minute**. Le
backend met les réponses en cache pendant `FOOTBALL_CACHE_TTL_SECONDS`
(300 s par défaut, `0` pour désactiver), ce qui couvre largement la
consultation des 6 championnats. En cas de quota dépassé, l’API renvoie une
erreur et l’interface affiche son écran d’erreur récupérable.

### Impact sur les tests et la campagne

- **CI et suites automatisées sur données réelles** : la CI force
  `MOCK_FOOTBALL_API=false` et exige le secret `FOOTBALL_API_TOKEN`. Les
  assertions sont des **invariants dérivés de l'API** (schéma JSON, ordre des
  positions, cohérence UI ↔ API, bornes) et non des valeurs figées : elles
  restent valables quand la saison, le nombre d'équipes ou les libellés
  changent. Les appels de données sont protégés par une **reprise bornée** sur
  erreur 5xx transitoire, et le cache `FOOTBALL_CACHE_TTL_SECONDS` évite de
  consommer le quota du fournisseur (10 requêtes/minute en gratuit).
- Le **mode simulé** reste disponible pour le développement hors ligne
  (`MOCK_FOOTBALL_API=true`) et pour les tests unitaires du backend, qui ne
  doivent jamais dépendre du réseau.
- Pour tester sans consommer le quota pendant que l'application de travail est
  en réel, utiliser la stack isolée des agents (`http://localhost:8002` /
  `5175`, mode simulé) :

  ```bash
  # API
  API_URL=http://localhost:8002 pytest tests/pytest/tests
  # UI
  BASE_URL=http://localhost:5175 npx playwright test
  ```

- Les résultats de la campagne V1 (36 cas, 32 conformes) ont été obtenus en
  mode simulé. Les suites automatisées ont depuis été rendues **indépendantes
  du référentiel** et rejouées sur les données réelles (voir `CHANGELOG.md`) ;
  le passage en réel ne change pas les règles métier ni les anomalies.
- Les identifiants d’équipes du mode simulé reprennent ceux de
  football-data.org (Arsenal 57, Chelsea 61…) : les favoris existants restent
  cohérents. En revanche, les données réelles évoluent avec la saison.

## Parcours métier

Accueil → Connexion → Championnat → Classement → Équipe → Ajouter aux favoris → Mes favoris → Suppression → Vérification.

- Un visiteur consulte librement les classements, les matchs et le classement
  des buteurs/passeurs ; il ne peut pas gérer de favoris.
- Un utilisateur connecté peut enregistrer plusieurs équipes.
- Une équipe ne peut être enregistrée qu’une fois par utilisateur.
- Chaque utilisateur ne consulte que ses favoris.
- La suppression retire réellement la relation en base.
- Les favoris persistent après déconnexion et reconnexion.
