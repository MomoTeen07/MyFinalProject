# Contexte du projet — Football QA

| Élément | Valeur |
|---|---|
| Dernière mise à jour | 22/11/2026 |
| Commit de référence | branche `app/v3` — **toujours vérifier avec `git log -1`** (`18e6c65` au moment de la vérification) ; la campagne Squash V1 a été exécutée sur `a0ea6e6` |
| Branches ouvertes | `app/v3` (travail en cours), `app/v2` (terminée), `main` |
| État | V3 implémentée et vérifiée fonctionnellement ; corrections locales non commitées ; phase Testing non démarrée |
| Reste à faire | Validation utilisateur, puis phase Testing et campagne V3 ; documentation de campagne et soutenance |

Ce fichier est le **point d'entrée pour reprendre le travail**. Il décrit l'état
réel du dépôt et des environnements locaux, pas seulement l'intention.

## 1. Ce qui est terminé

| Domaine | Livrable | État |
|---|---|---|
| Cadrage | `docs/TEST_PLAN.md` (périmètre, hypothèses, 10 risques, critères d'entrée/sortie, § 1.1 choix de l'application) | Terminé |
| Cas manuels | `docs/TEST_CASES.md` (50 cas : 36 V1 + 14 V2, techniques PE/VL/TD/EX, résultats) | V1 : 32 conformes / 4 anomalies ; V2 : 14/14 |
| Anomalies | `docs/ANOMALIES.md` (ANO-001 à ANO-005, reproduction, preuve, gravité, priorité) | Terminé, non corrigées volontairement |
| Traçabilité | `docs/TRACEABILITY.md` (20 exigences, 50 cas, 15 endpoints V1/V2) | Terminé, 50/50 cas tracés ; V3 à tracer en phase Testing |
| Rapport | `docs/CAMPAIGN_REPORT.md` (métriques, risques résiduels, recommandations) | Terminé |
| Soutenance | `docs/DEFENSE.md` (trame 25 min, 5 séquences de démo, questions/réponses) | Terminé, à répéter |
| API | `tests/pytest/` (100 passed, 4 xfailed) + `postman/` (31 requêtes, 76 assertions) | Vérifié le 22/11/2026 en données réelles |
| UI | `tests/playwright/` (7 page objects, 27 tests) | Vérifié le 22/11/2026 en données réelles |
| Backend | 19 tests unitaires (sécurité, presse, service football) | Vérifié le 22/11/2026 |
| CI | `.github/workflows/ci.yml` (2 jobs, 4 artefacts, Allure agrégé) | Verte sur `main` |
| Campagne | Squash TM 15.0.3 : `infra/squash/`, 16 exigences, 36 cas, 32 `SUCCESS` / 4 `FAILURE` | Terminé, vérifié par API |
| **V2 — F2 buteurs/passeurs** | API `/scorers`, onglet « Buteurs », bascule Buts/Passes, 9 tests PyTest, 3 tests UI, 4 requêtes Postman | **Terminé sur `app/v2`** |
| **V2 — F3a actualités** | API `/news`, section « Résultats récents » à l'accueil, 6 tests PyTest, 2 tests UI, 2 requêtes Postman | **Terminé sur `app/v2`** |
| **V2 — F3b presse** | API `/press` toujours `200`, section « À la une », 6 tests unitaires, 3 tests API, 1 test UI, 2 requêtes Postman | **Terminé sur `app/v2`** |
| **V2 — F4 détail de match** | API `/matches/{id}` (404 propre), page `/matches/:id`, liens depuis la liste et les actualités, 3 tests API, 2 tests UI, 2 requêtes Postman | **Terminé sur `app/v2`** |
| **V2 — F1 pagination matchs** | API `/matches` (`page`, `page_size`, `status`, `team_id`, `sort`), filtres/tri/pagination UI | **Terminé sur `app/v2` (`c37e9d0`)** |
| **V3 — F1 prochains matchs** | API `/fixtures`, carte « Prochains matchs » de l'accueil, exclusion des matchs commencés | **Implémenté sur `app/v3`** |
| **V3 — F2 fiche équipe** | Panneaux classement/forme, prochain match avec repli au-delà de 10 jours, derniers résultats | **Implémenté sur `app/v3`** |
| **V3 — F3 favoris** | API `/favorites/overview`, tableau de bord par équipe, dégradation gracieuse | **Implémenté sur `app/v3`** |
| **V3 — F4 détail match** | API `/matches/{id}/head2head`, classement/forme, derniers matchs antérieurs, confrontations | **Implémenté sur `app/v3`** |
| **V3 — robustesse** | Boutons « Réessayer » secondaires, document HTML complet avec `meta viewport`, tableaux mobiles défilables avec indication | **Vérifié le 22/11/2026** |

## 2. Historique des PR (toutes fusionnées en squash)

Tableau arrêté à la **#13** ; pour la suite :
`gh pr list --state merged --limit 20`.

| PR | Commit | Sujet |
|---|---|---|
| #1 | `2689178` | CI + rapports Allure + correctif du test d'accueil |
| #2 | `2727d46` | Suite API PyTest + collection Postman (remplace Bruno) |
| #3 | `a0ea6e6` | Suite UI Playwright en Page Object Model |
| #4 | `b4fffe9` | Plan de test, cas manuels, anomalies, traçabilité, rapport, soutenance |
| #5 | `b4c3e1e` | Campagne Squash TM versionnée + scripts de seed REST |
| #6 | `396ffda` | Lien campagne Squash dans le rapport et la soutenance |
| #7 | `748150c` | Traçabilité du choix de l'application et de sa validation |
| #8 | `d00656f` | Point de reprise `PROJECT_CONTEXT.md` |
| #9 | `e178ea5` | Bascule entre les deux PC (§ 11) |
| #10 | `505398e` | Mode « données réelles » football-data.org documenté |
| #11 | `dcb1a7d` | Point de reprise mis à jour (PR #8 à #10, piège « mode réel ») |
| #12 | `3170350` | `FOOTBALL_CACHE_TTL_SECONDS` transmis au backend par Compose |
| #13 | `13b27ab` | Point de reprise : mode « données réelles » consigné (§ 11.3) |

Après la PR #12, la campagne Squash et les suites restent en mode simulé ;
seules la documentation, `.env.example` et une variable d'environnement du
service `backend` ont changé.

**21/11/2026 — suites automatisées en données réelles.** Les suites PyTest,
Postman et Playwright ne dépendent plus du référentiel simulé : les attentes
sont des invariants et, côté UI, un oracle API (fixture `football`). La CI
exige désormais le secret `FOOTBALL_API_TOKEN` et force
`MOCK_FOOTBALL_API=false`. La **campagne manuelle V1** reste, elle, documentée
telle qu'exécutée en mode simulé (§ 11.3) : ne pas la présenter comme réelle
sans rejouer les 36 cas.

La campagne Squash cible le commit `a0ea6e6` ; les PR #6 à #12 ne changent que
de la documentation, sauf la #12 (une ligne de `docker-compose.yml`, sans effet
sur les tests).

### V2 terminée (branche `app/v2`, base = tag `v1.0-campagne-v1`)

| Élément | État |
|---|---|
| Périmètre | 4 fonctionnalités, décidées le 22/11/2026 : F1 pagination, F2 buteurs/passeurs, F3 actualités (résultats + presse RMC), F4 détail de match |
| Spec | `docs/V2_SPEC.md`, principe **additif** : ANO-001 à ANO-005 conservées |
| F1 pagination | **Implémentée** (`c37e9d0`) : pagination, filtres de statut et tri des matchs |
| F2 buteurs | **Implémentée et verte** (22/11/2026) : classement buts/passes, tri déterministe, `null` → 0 |
| F3a actualités | **Implémentée et verte** (22/11/2026) : fil de résultats récents, 3 branches de titre, `days` borné à 10 |
| F3b presse | **Implémentée et verte** (22/11/2026) : flux RMC, route toujours `200`, cache 600 s, dégradation gracieuse |
| F4 détail de match | **Implémentée et verte** (22/11/2026) : `/matches/{id}`, 404 propre, page dédiée |

### V3 en cours (branche `app/v3`, base = `app/v2`)

| Élément | État |
|---|---|
| Périmètre | 4 fonctionnalités : prochains matchs, fiche équipe enrichie, tableau de bord des favoris, détail de match enrichi ; la pagination F1 de la V2 est reprise telle quelle |
| Spec | `docs/V3_SPEC.md`, principe **additif** : ANO-001 à ANO-005 conservées |
| F1 accueil | `/fixtures` inter-compétitions, matchs déjà commencés exclus, retry |
| F2 fiche équipe | Classement, forme calculée, prochain match (repli au-delà de 10 jours), derniers résultats |
| F3 favoris | `/favorites/overview` : classement, forme, trois derniers résultats, prochain match, dégradation gracieuse |
| F4 détail match | `/head2head`, classement/forme, derniers matchs antérieurs au match, confrontations à la demande |
| Robustesse | Retry secondaires, `meta viewport`, tables mobiles défilables avec indication |
| Vérification | 22/11/2026 : backend 19/19, API 100 + 4 `xfail`, Postman 76/76, UI 27/27, fonctionnel 31/31 |
| Reste | Validation utilisateur puis **phase Testing** (campagne V3 : cas manuels, traçabilité, Squash, rapport, démo) |

Aucune migration de base n'est prévue pour les fonctionnalités V2/V3. Les tests
ne sont jamais supprimés, seulement adaptés dans la PR qui change l'API.

## 3. Reprise en 5 minutes

```powershell
cd C:\Users\MAbdo\Desktop\Football-QA\MyFinalProject
git pull --ff-only origin main
git log --oneline -5
docker ps --format "{{.Names}} | {{.Status}} | {{.Ports}}"

# Application (API 8001, UI 5174, PostgreSQL 5433)
docker compose up -d --wait
curl.exe -s http://localhost:8001/health

# Squash TM (1 à 3 minutes avant de répondre)
docker compose -f infra/squash/docker-compose.yml up -d
Start-Process http://localhost:8090/squash
```

Vérification des suites (résultats attendus) :

```powershell
# Backend : 19 passed (environnement avec les dépendances de backend/requirements.txt)
Push-Location backend
..\.venv-qa\Scripts\python.exe -m pytest tests -q
Pop-Location

# API : 100 passed, 4 xfailed (données réelles)
$env:REAL_FOOTBALL_DATA='true'
.venv-qa\Scripts\python.exe -m pytest tests/pytest/tests -q --alluredir=allure-results-api

# Postman : 31 requêtes, 76 assertions, 0 échec
npx --yes newman@6 run postman/Football-QA.postman_collection.json -e postman/Football-QA.postman_environment.json

# UI : 27 passed
Push-Location tests\playwright
npx playwright test
Pop-Location
```

Campagne Squash (attendu : 32 `SUCCESS`, 4 `FAILURE`) :

```powershell
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:admin'))
$h = @{ Authorization = "Basic $auth" }
$plan = (Invoke-RestMethod -Headers $h 'http://localhost:8090/squash/api/rest/latest/iterations/1/test-plan?size=100')._embedded.'test-plan'
$plan | Group-Object execution_status | Select-Object Name, Count
```

Si la campagne a disparu (volume supprimé) :

```powershell
docker compose -f infra/squash/docker-compose.yml down --volumes
docker compose -f infra/squash/docker-compose.yml up -d
python infra/squash/build_campaign_data.py
python infra/squash/seed_campaign.py
```

## 4. Environnements et ports

| Stack | Conteneurs | Ports | Démarrage |
|---|---|---|---|
| Application | `myfinalproject-{db,backend,frontend}` | 5433, 8001, 5174 | `docker compose up -d --wait` |
| Squash TM | `squash-squashtm-{db,}` | 8090 | `docker compose -f infra/squash/docker-compose.yml up -d` |
| Tests de l'agent | `football-qa-test-{db,backend,frontend}` | 5434, 8002, 5175 | `football-qa-agents/infra/docker-compose.test.yml` |

Identifiants Squash locaux : `admin` / `admin` (instance de démonstration, à
changer hors projet). Ne jamais versionner `.env` ni les clés.

## 5. Les deux copies du dépôt (à conserver)

| Chemin | Rôle |
|---|---|
| `C:\Users\MAbdo\Desktop\Football-QA\MyFinalProject` | Copie de travail : c'est ici que les branches et PR sont créées |
| `C:\Users\MAbdo\Desktop\Football-Agent\football-qa` | Clone de MyFinalProject exigé par `football-qa-agents/infra/docker-compose.test.yml` (`context: ../../football-qa/backend` et `.../frontend`) |

Après chaque fusion sur `main`, resynchroniser la seconde copie :

```powershell
git -C C:\Users\MAbdo\Desktop\Football-Agent\football-qa pull --ff-only
```

Une jonction Windows a déjà été refusée : ne pas supprimer ni déplacer ce clone.

## 6. Règles de travail à conserver

1. **Jamais de push direct sur `main`** : une branche par sujet, une PR, CI verte,
   fusion en squash, suppression de la branche, puis `git pull --ff-only`.
2. **Chaque modification met à jour la documentation** : `README.md`,
   `CHANGELOG.md` et ce fichier si l'état ou les commandes changent.
3. **Anomalies applicatives non corrigées** : les défauts sont la preuve QA.
   Les tests correspondants restent en `xfail(strict=True)` ; si un défaut est
   corrigé, le test doit passer en `pass` et la campagne Squash être mise à jour.
4. **Budget 0 €** : aucun service payant, aucune clé requise, aucun scheduler.
5. **Aucun secret** dans le dépôt, les logs, les rapports ou les commits.

## 7. Pièges connus (déjà rencontrés)

| Sujet | À savoir |
|---|---|
| API REST Squash | Basic refusé par défaut en v15 ; le compose local ajoute `-Dsquash.rest-api.disallow-basic-authentication=false` (usage local uniquement) |
| Seed Squash | Idempotent par refus : si le projet *Football QA* existe, le script s'arrête ; reset par `down --volumes` |
| Cas de test Squash | `_type: "test-case"` avec `steps` inline ; `standard-test-case` renvoie 400 |
| Plan de test Squash | L'itération ne reprend pas le plan de la campagne : ajout explicite par `POST /iterations/{id}/test-plan` (non documenté mais stable) |
| Suppression Squash | `DELETE /projects/{id}` renvoie 405 : passer par les volumes |
| `xfail` strict | Un `xfail` qui passe devient `XPASS` et fait échouer la CI : c'est voulu |
| Playwright | Session injectée par `goto('/')` + `localStorage` + `reload` (pas d'`addInitScript`, sinon la déconnexion n'est plus testable) |
| Libellés UI | Le statut de match s'écrit exactement « À venir » |
| Mode réel | `MOCK_FOOTBALL_API=false` exige `FOOTBALL_API_TOKEN` (compte gratuit football-data.org, 10 req/min, cache 300 s). Les suites API/UI sont indépendantes du référentiel et tournent en réel ; la campagne manuelle V1 reste documentée en simulé. Une erreur 502/503 transitoire est récupérable par « Réessayer ». Voir README § *Données réelles* |
| Mobile | `frontend/index.html` doit rester un document complet (`doctype`, `lang`, `meta charset`, `meta viewport`). Un fragment HTML faisait rendre la page en 980 px et désactivait les media queries. |
| CI | Les jobs démarrent leur propre stack et terminent par `docker compose down --volumes` : ne pas compter sur les données de la CI |
| PowerShell | La console peut mal afficher l'UTF-8 ; les fichiers sont en UTF-8, vérifier avec Python si besoin |

## 8. Ce qui n'est pas versionné (normal)

- `.env` (secrets locaux), `.venv-qa/`, `node_modules/`, `allure-results*/`,
  `allure-report/`, `tests/playwright/test-results/`, `playwright-report/`,
  `__pycache__/`.
- Après un clone : réinstaller les dépendances et régénérer les rapports
  (voir README § Environnement de tests).

## 9. Reste à faire

1. **Valider la V3 fonctionnelle** avec l'utilisateur (rapport de vérification du 22/11/2026).
2. **Phase Testing V3** : cas manuels, traçabilité, campagne Squash, rapport,
   démonstration. Ne pas la démarrer sans validation explicite.
3. Préparer les **slides** de soutenance à partir de `docs/DEFENSE.md`.
4. Faire les **captures d'écran** : pipeline vert, rapport Allure, campagne
   Squash (32/4), anomalie ANO-001, mobile.
5. Répéter la démonstration complète **en moins de 20 minutes** (checklist dans
   `docs/DEFENSE.md` § 6).
6. Vérifier la date et le format de dépôt communiqués par le formateur.

## 10. Où trouver quoi

| Document | Usage |
|---|---|
| `README.md` | Installation, exécution de chaque partie, choix de l'application, CI |
| `docs/TEST_PLAN.md` | Stratégie, risques, critères, planning |
| `docs/TEST_CASES.md` | 50 cas et résultats |
| `docs/V3_SPEC.md` | Spécification V3 et critères d'acceptation |
| `docs/ANOMALIES.md` | 5 rapports d'anomalie |
| `docs/TRACEABILITY.md` | Exigence → cas → exécution → anomalie |
| `docs/CAMPAIGN_REPORT.md` | Métriques et bilan de campagne |
| `docs/SQUASH.md` | Campagne Squash : démarrage, seed, vérification, limites |
| `docs/DEFENSE.md` | Trame, démonstration, questions probables |
| `docs/CONCEPTION.md` | Conception technique de l'application |
| `CHANGELOG.md` | Historique des modifications |

## 11. Changer de PC (personnel ↔ professionnel)

Le travail se fait sur deux machines. **Seul Git se synchronise** :

| Se synchronise | Ne se synchronise pas (à recréer localement) |
|---|---|
| Les 3 dépôts Git (`main`) | `.env` (clés Gemini, Telegram, `OFFICE_URL`, `REAL_AGENTS_ENABLED`) |
| Code, tests, documentation | `.venv` / `node_modules` / navigateurs Playwright |
| Fichiers Compose | Volumes Docker : bases PostgreSQL, campagne Squash |
| | Rapports locaux : `reports/`, `workspace/`, `allure-results*/`, `test-results/` |

### 11.1 Procédure à l'arrivée sur l'autre PC

```powershell
# 1. Mettre à jour les dépôts (adapter les chemins au PC)
git -C C:\Users\stgadmin\Desktop\football-qa-agents switch main
git -C C:\Users\stgadmin\Desktop\football-qa-agents pull --ff-only

git -C <chemin_MyFinalProject> switch main
git -C <chemin_MyFinalProject> pull --ff-only

# 2. Resynchroniser le clone cible des agents (voir § 5)
git -C <chemin_...\football-qa> pull --ff-only
```

```powershell
# 3. Vérifier les prérequis locaux, sans afficher les secrets
Test-Path <chemin_MyFinalProject>\.env
Test-Path C:\Users\stgadmin\Desktop\football-qa-agents\.env

# 4. Réinstaller les dépendances du projet d'agents
cd C:\Users\stgadmin\Desktop\football-qa-agents
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m playwright install chromium
```

```powershell
# 5. Reconstruire les stacks (les volumes sont locaux à chaque PC)
cd <chemin_MyFinalProject>
docker compose up -d --build --wait
docker compose -f infra/squash/docker-compose.yml up -d

# 6. Recréer la campagne Squash sur ce PC (volume neuf)
python infra/squash/build_campaign_data.py
python infra/squash/seed_campaign.py
```

```powershell
# 7. Vérifier avant de travailler (données réelles)
$env:REAL_FOOTBALL_DATA='true'
.venv-qa\Scripts\python.exe -m pytest tests/pytest/tests -q   # 100 passed, 4 xfailed
Push-Location tests\playwright; npx playwright test; Pop-Location  # 27 passed
Push-Location backend; ..\.venv-qa\Scripts\python.exe -m pytest tests -q; Pop-Location  # 19 passed

# Variante backend si .venv-qa ne contient que les dépendances de tests API :
docker compose run --rm --no-deps -v "${PWD}/backend/tests:/app/tests" backend python -m pytest tests -q
```

```powershell
# 8. Relancer l'interface Telegram et le bureau (aucun scheduler)
cd C:\Users\stgadmin\Desktop\football-qa-agents
.venv\Scripts\python.exe -m app.telegram.gateway
.venv\Scripts\python.exe scripts\run_office.py --open
```

### 11.2 Précautions spécifiques

1. **Ne pas copier les volumes Docker** d'un PC à l'autre : les recréer. La base
   de test des agents se réensemence avec `scripts\seed_test_data.py`.
2. **Ne jamais transmettre `.env`** par chat, mail ou commit : les clés sont
   locales à chaque machine (elles existent déjà sur le PC professionnel).
3. **Vérifier le chemin du clone cible** : depuis
   `football-qa-agents/infra`, `..\..\football-qa` doit pointer vers le clone de
   `MyFinalProject` ; sinon la stack `football-qa-test` ne construit rien.
4. **Ports attendus** : 8001/5174/5433 (application), 8002/5175/5434 (tests des
   agents), 8090 (Squash), 5180 (bureau). Libérer tout conflit avant `up`.
5. **`gh` (GitHub CLI)** n'est pas garanti sur le PC professionnel : vérifier
   `gh auth status` avant de créer une PR. Ne jamais coller de jeton dans le
   terminal ni dans un fichier versionné.
6. **La CI reste la référence** : avant de reprendre, vérifier que le dernier
   run de `main` est vert ; localement, les résultats attendus sont ceux du
   § 1.
7. **Premier message au bot** : vérifier que l'allowlist Telegram autorise bien
   le compte utilisé, puis créer une mission courte pour valider la chaîne
   (bot → agents → stack de test → rapports).

### 11.3 Mode de données : simulé ou réel (propre à chaque PC)

Le mode est porté par `.env`, donc **il ne se synchronise pas** :

| PC | `.env` | Ce que ça implique |
|---|---|---|
| Personnel (état au 15/11/2026) | `MOCK_FOOTBALL_API=false` + jeton renseigné | Classements réels (20 équipes en PL), 10 requêtes/minute, cache 300 s |
| Professionnel | `MOCK_FOOTBALL_API=true` (défaut) ou jeton local | Laisser en simulé pour lancer les suites et la démo des tests |

Passer en réel sur une machine :

```powershell
# 1. Renseigner le jeton dans .env (jamais dans Git, jamais dans le chat)
#    FOOTBALL_API_TOKEN=<jeton>  et  MOCK_FOOTBALL_API=false
# 2. Recréer le backend pour qu'il relise .env
docker compose up -d --force-recreate backend
# 3. Vérifier
curl.exe -s http://localhost:8001/api/football/leagues/PL/standings
```

Revenir au simulé : remettre `MOCK_FOOTBALL_API=true`, puis la même recréation
du backend. Depuis le 21/11/2026, les suites API/UI sont **indépendantes du
référentiel** et s'exécutent dans les deux modes. En réel, lancer PyTest avec
`REAL_FOOTBALL_DATA=true` (active le `xfail` d'ANO-005) et surveiller le quota
de 10 requêtes/minute. Vérifié le 15/11/2026 en réel :
6 championnats (20/18/20/20/18/36 équipes), 380 matchs en PL, interface à
20 lignes, aucune erreur console. Rejoué le 21/11/2026 : PyTest 52 passed +
4 xfailed, Postman 41 assertions / 0 échec, Playwright 17 passed. Vérifié à
nouveau le 22/11/2026 sur la V3 : backend 19 passed, API 100 passed + 4 xfailed,
Postman 76 assertions / 0 échec, Playwright 27 passed.
