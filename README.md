# Football QA

Application web de consultation du football, conçue comme support d’un projet final QA.

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
| Application web avec interface utilisateur | Frontend React/Vite servi par Nginx : connexion, inscription, championnats, classement, calendrier, fiche équipe, favoris | `frontend/src/pages/`, `tests/playwright/` |
| API testable avec authentification | API REST FastAPI, 11 endpoints, jeton JWT `Bearer` sur les routes personnelles | `backend/app/api/`, `postman/` |
| Persistance et règles métier | PostgreSQL 16 avec migrations Alembic : comptes, favoris uniques par utilisateur, cloisonnement des données | `backend/app/db/`, `docs/CONCEPTION.md` |
| Exécutable localement | Docker Compose (3 conteneurs), mode de données simulé sans clé ni service payant | `docker-compose.yml`, section « Démarrage local » |
| Complexité suffisante | Parcours visiteur et authentifié, états de chargement et d’erreur, données d’une API externe, pages dédiées (accueil, championnats, championnat, équipe, favoris, authentification) | `docs/TEST_PLAN.md` § 4 |
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

La collection est également importable dans Postman : dossier `postman/`, variable `baseUrl` à adapter. Elle couvre l’inscription, la connexion, la session, les contrats football, le parcours favori complet et quatre contrôles de sécurité (41 assertions). Le détail est documenté dans `postman/README.md`.

Tests de contrat API, avec l’application démarrée par Docker :

```bash
python -m pip install -r tests/pytest/requirements.txt
python -m pytest tests/pytest/tests --alluredir=allure-results-api
```

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
├── pages/        AuthPage, Navbar, ChampionshipsPage, ChampionshipPage, TeamPage, FavoritesPage
├── fixtures/     comptes uniques par l'API et session injectée
└── tests/        auth.spec.js, championships.spec.js, favorites.spec.js, smoke.spec.js
```

Chaque test crée son propre compte : aucun état partagé entre exécutions, donc
la suite est rejouable sans nettoyage de base. Les scénarios couvrent
l’authentification, les six championnats, le classement, le calendrier, la fiche
équipe, le parcours critique des favoris (ajout → consultation → suppression) et
le cloisonnement entre deux comptes.

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

Le workflow `.github/workflows/ci.yml` s’exécute sur chaque push, pull request et lancement manuel. Il prépare une base PostgreSQL éphémère, lance les tests unitaires backend puis les suites API, Postman et UI, agrège les résultats Allure et publie quatre artefacts : `allure-report`, `playwright-report`, `postman-report` et, en cas d’échec, `playwright-test-results` (traces, captures, vidéos). Les identifiants configurés dans ce workflow sont réservés à cette base temporaire.

## Documentation QA

| Document | Contenu |
|---|---|
| [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) | Périmètre, hypothèses, analyse de risques (P × I), critères d’entrée et de sortie, organisation |
| [`docs/TEST_CASES.md`](docs/TEST_CASES.md) | 36 cas manuels avec technique de conception, étapes, attendu, obtenu et statut |
| [`docs/ANOMALIES.md`](docs/ANOMALIES.md) | Rapports ANO-001 à ANO-004 : contexte, reproduction, preuve, gravité, priorité, correction proposée |
| [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) | Matrice exigence → cas → exécution → anomalie et couverture des endpoints |
| [`docs/CAMPAIGN_REPORT.md`](docs/CAMPAIGN_REPORT.md) | Métriques, bilan des anomalies, risques résiduels, recommandations |
| [`docs/DEFENSE.md`](docs/DEFENSE.md) | Trame de soutenance, script de démonstration, questions probables |
| [`docs/SQUASH.md`](docs/SQUASH.md) | Campagne Squash TM : démarrage, création par script REST, vérification, limites |
| [`docs/CONCEPTION.md`](docs/CONCEPTION.md) | Conception technique de l’application |

Synthèse de la campagne V1 : **115 vérifications automatisées** (4 backend,
53 API, 17 UI, 41 assertions Postman) et 3 `xfail` documentés, **36 cas
manuels**, **4 anomalies** reproductibles, **11/11 endpoints** couverts,
pipeline vert.

## Gestion de campagne (Squash TM)

La campagne V1 est également portée par **Squash TM 15.0.3**
(`infra/squash/docker-compose.yml`, `http://localhost:8090/squash`).

```bash
docker compose -f infra/squash/docker-compose.yml up -d
python infra/squash/seed_campaign.py
```

Le script crée le projet *Football QA*, ses 16 exigences, ses 4 dossiers,
ses 36 cas de test avec pas et couvertures, la campagne `CAMP-V1`, son
itération, la suite complète et les 36 exécutions (**32 `SUCCESS`**, **4
`FAILURE`** pour ANO-001 à ANO-004). Squash TM est un outil de gestion, pas une
dépendance des tests : il n’est pas démarré en CI. Procédure complète et limites
dans [`docs/SQUASH.md`](docs/SQUASH.md).


## Configuration

Les ports, le bind local, les paramètres PostgreSQL, le secret JWT, les origines CORS, le cache football (`FOOTBALL_CACHE_TTL_SECONDS`) et le mode de données sont configurables dans `.env`. Le cache externe dure cinq minutes par défaut et peut être désactivé avec une valeur de `0`. Utilisez des caractères URI sûrs dans `POSTGRES_PASSWORD`, ou encodez les caractères réservés avant de les inclure dans l’URL PostgreSQL générée par Compose.

Le port et les identifiants PostgreSQL par défaut sont réservés au développement local. Pour un déploiement, changez les secrets, limitez les origines CORS et utilisez un gestionnaire de secrets adapté à l’environnement.

## Parcours métier

Accueil → Connexion → Championnat → Classement → Équipe → Ajouter aux favoris → Mes favoris → Suppression → Vérification.

- Un visiteur ne peut pas gérer de favoris.
- Un utilisateur connecté peut enregistrer plusieurs équipes.
- Une équipe ne peut être enregistrée qu’une fois par utilisateur.
- Chaque utilisateur ne consulte que ses favoris.
- La suppression retire réellement la relation en base.
- Les favoris persistent après déconnexion et reconnexion.
