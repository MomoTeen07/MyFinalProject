# Contexte du projet — Football QA

| Élément | Valeur |
|---|---|
| Dernière mise à jour | 15/11/2026 |
| Commit de référence | `main` — `505398e` au moment de la rédaction ; voir `git log -1` pour le dernier commit |
| Branches ouvertes | aucune (seul `main` local et distant) |
| État | Livrables du projet final QA complets, CI verte, campagne Squash TM créée |
| Reste à faire | Manuel uniquement : préparation des slides, captures d'écran, soutenance |

Ce fichier est le **point d'entrée pour reprendre le travail**. Il décrit l'état
réel du dépôt et des environnements locaux, pas seulement l'intention.

## 1. Ce qui est terminé

| Domaine | Livrable | État |
|---|---|---|
| Cadrage | `docs/TEST_PLAN.md` (périmètre, hypothèses, 10 risques, critères d'entrée/sortie, § 1.1 choix de l'application) | Terminé |
| Cas manuels | `docs/TEST_CASES.md` (36 cas, techniques PE/VL/TD/EX, résultats) | Terminé, 32 conformes / 4 anomalies |
| Anomalies | `docs/ANOMALIES.md` (ANO-001 à ANO-004, reproduction, preuve, gravité, priorité) | Terminé, non corrigées volontairement |
| Traçabilité | `docs/TRACEABILITY.md` (16 exigences, 36 cas, 11 endpoints) | Terminé, 36/36 cas tracés |
| Rapport | `docs/CAMPAIGN_REPORT.md` (métriques, risques résiduels, recommandations) | Terminé |
| Soutenance | `docs/DEFENSE.md` (trame 25 min, 5 séquences de démo, questions/réponses) | Terminé, à répéter |
| API | `tests/pytest/` (53 passed, 3 xfailed) + `postman/` (18 requêtes, 41 assertions) | Terminé, CI verte |
| UI | `tests/playwright/` (6 page objects, 17 tests) | Terminé, CI verte |
| Backend | 4 tests unitaires | Terminé |
| CI | `.github/workflows/ci.yml` (2 jobs, 4 artefacts, Allure agrégé) | Verte sur `main` |
| Campagne | Squash TM 15.0.3 : `infra/squash/`, 16 exigences, 36 cas, 32 `SUCCESS` / 4 `FAILURE` | Terminé, vérifié par API |

## 2. Historique des PR (toutes fusionnées en squash)

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

Après la PR #10, la campagne Squash et les suites restent en mode simulé ;
seules la documentation et `.env.example` ont changé.

La campagne Squash cible le commit `a0ea6e6` ; les PR #6 à #10 ne changent que
de la documentation.

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
# Backend : 4 passed
Push-Location backend
..\.venv-qa\Scripts\python.exe -m pytest tests -q
Pop-Location

# API : 53 passed, 3 xfailed
.venv-qa\Scripts\python.exe -m pytest tests/pytest/tests -q --alluredir=allure-results-api

# Postman : 41 assertions, 0 échec
npx --yes newman@6 run postman/Football-QA.postman_collection.json -e postman/Football-QA.postman_environment.json

# UI : 17 passed
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
| Mode réel | `MOCK_FOOTBALL_API=false` exige `FOOTBALL_API_TOKEN` (compte gratuit football-data.org, 10 req/min, cache 300 s). Les suites et la campagne décrivent le mock (4 équipes) : les lancer contre `8002`/`5175` via `API_URL`/`BASE_URL`. Voir README § *Données réelles* |
| CI | Les jobs démarrent leur propre stack et terminent par `docker compose down --volumes` : ne pas compter sur les données de la CI |
| PowerShell | La console peut mal afficher l'UTF-8 ; les fichiers sont en UTF-8, vérifier avec Python si besoin |

## 8. Ce qui n'est pas versionné (normal)

- `.env` (secrets locaux), `.venv-qa/`, `node_modules/`, `allure-results*/`,
  `allure-report/`, `tests/playwright/test-results/`, `playwright-report/`,
  `__pycache__/`.
- Après un clone : réinstaller les dépendances et régénérer les rapports
  (voir README § Environnement de tests).

## 9. Reste à faire (manuel, hors dépôt)

1. Préparer les **slides** de soutenance à partir de `docs/DEFENSE.md`.
2. Faire les **captures d'écran** : pipeline vert, rapport Allure, campagne
   Squash (32/4), anomalie ANO-001.
3. Répéter la démonstration complète **en moins de 20 minutes** (checklist dans
   `docs/DEFENSE.md` § 6).
4. Vérifier la date et le format de dépôt communiqués par le formateur.

## 10. Où trouver quoi

| Document | Usage |
|---|---|
| `README.md` | Installation, exécution de chaque partie, choix de l'application, CI |
| `docs/TEST_PLAN.md` | Stratégie, risques, critères, planning |
| `docs/TEST_CASES.md` | 36 cas et résultats |
| `docs/ANOMALIES.md` | 4 rapports d'anomalie |
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
# 7. Vérifier avant de travailler
.venv-qa\Scripts\python.exe -m pytest tests/pytest/tests -q   # 53 passed, 3 xfailed
Push-Location tests\playwright; npx playwright test; Pop-Location  # 17 passed
Push-Location backend; ..\.venv-qa\Scripts\python.exe -m pytest tests -q; Pop-Location  # 4 passed
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
