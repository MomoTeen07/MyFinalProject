# Football QA

**Application de consultation du football, utilisée comme système sous test pour une campagne QA versionnée.**

[![QA CI](https://github.com/MomoTeen07/football-qa/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MomoTeen07/football-qa/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-E2E-2EAD33?logo=playwright&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Licence](https://img.shields.io/badge/Licence-MIT-3DA639)

> **Statut : V3 terminée — campagne finale close.**
> **222 vérifications passantes + 4 `xfail`**, **59 cas manuels** (54 conformes,
> 5 anomalies), **18/18 endpoints**, **25/25 exigences** tracées, campagne
> Squash **54 `SUCCESS` / 5 `FAILURE`**, pipeline vert.
> Détail : [`docs/CAMPAIGN_REPORT.md`](docs/CAMPAIGN_REPORT.md).

---

## En 30 secondes

Ce dépôt contient **deux choses** :

1. une application full-stack fonctionnelle — React, FastAPI, PostgreSQL, JWT, 18 endpoints ;
2. la **campagne de test** qui l'accompagne — plan, cas manuels, automatisation API et UI,
   rapports d'anomalies, traçabilité.

L'application est **volontairement non corrigée** : les anomalies trouvées sont conservées,
documentées et rejouées par des tests `xfail` stricts. L'objectif n'est pas de livrer un produit,
c'est de démontrer une **démarche de test complète** — de l'analyse de risques à la synthèse de campagne.

## Choix de l'application

| Critère de l'énoncé | Réponse de Football QA |
|---|---|
| Application web avec interface utilisateur | Frontend React/Vite servi par Nginx : connexion, inscription, actualités et presse, prochains matchs, championnats, classement, calendrier paginé, détail de match, buteurs, fiche équipe enrichie, tableau de bord des favoris |
| API testable avec authentification | API REST FastAPI, 18 endpoints, jeton JWT `Bearer` sur les routes personnelles |
| Persistance et règles métier | PostgreSQL 16 avec migrations Alembic : comptes, favoris uniques par utilisateur, cloisonnement des données |
| Exécutable localement | Docker Compose (3 conteneurs), mode de données simulé sans clé ni service payant |
| Complexité suffisante | Parcours visiteur et authentifié, états de chargement et d'erreur, données d'une API externe, pages dédiées et parcours V3 (prochains matchs, fiche équipe enrichie, tableau de bord, confrontations) |
| Accès licite | Dépôt applicatif du projet, code source accessible, aucune restriction de test |

Le choix a été **soumis au formateur et validé avant le début des travaux**.

## Ce que ce dépôt démontre

| Sujet | Où le vérifier |
| --- | --- |
| Analyse de risques (probabilité × impact) et stratégie | [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) |
| Conception de cas (59 cas : 36 V1, 14 V2, 9 V3) | [`docs/TEST_CASES.md`](docs/TEST_CASES.md) |
| Traçabilité exigence → cas → exécution → anomalie | [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) |
| Rapports d'anomalies (gravité, preuve, correctif proposé) | [`docs/ANOMALIES.md`](docs/ANOMALIES.md) |
| Synthèse de campagne et risques résiduels | [`docs/CAMPAIGN_REPORT.md`](docs/CAMPAIGN_REPORT.md) |
| Automatisation UI — Playwright, Page Object Model | [`tests/playwright/`](tests/playwright/) |
| Tests de contrat API — pytest + JSON Schema | [`tests/pytest/`](tests/pytest/) |
| API chaînée — Postman / Newman | [`postman/`](postman/) |
| Gestion de campagne — Squash TM | [`docs/SQUASH.md`](docs/SQUASH.md) |
| CI — Docker Compose, artefacts Allure / Playwright / Postman | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |

## Résultats — campagne finale V3

| Métrique | Valeur |
| --- | --- |
| Cas manuels exécutés | **59** (36 V1 + 14 V2 + 9 V3) |
| Cas conformes | **54** (91,5 %), 5 anomalies documentées |
| Vérifications automatisées | **222 passantes + 4 `xfail`** (19 backend, 100 API, 27 UI, 76 assertions Postman) |
| Anomalies documentées | **5** (`ANO-001` à `ANO-005`) : 2 majeures, 3 moyennes |
| Endpoints couverts | **18 / 18** |
| Exigences tracées | **25 / 25** |
| Risques critiques (≥ 6) couverts | **6 / 6** |
| Campagne Squash TM | **54 `SUCCESS` / 5 `FAILURE`** (25 exigences, 59 cas) |
| Pipeline | **vert** |

Historique : V1 (13/11/2026, mode simulé) — 36 cas, 118 vérifications, 4 anomalies ;
V2 (22/11/2026, données réelles) — 14 cas, 14 conformes ; V3 (25/11/2026, données réelles) —
9 cas, 8 conformes, ANO-005.

Les rapports **Allure**, **Playwright** et **Postman** sont produits à chaque exécution et
téléchargeables depuis l'onglet [Actions](https://github.com/MomoTeen07/football-qa/actions).

## Lancer localement

Prérequis : Docker et Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

| Service | URL |
| --- | --- |
| Application | http://localhost:5174 |
| API | http://localhost:8001 |
| Documentation Swagger | http://localhost:8001/docs |

Les suites de test se lancent séparément et ne sont pas exécutées au démarrage. Commandes
détaillées, variables d'environnement, migrations Alembic, mode données réelles et gestion des
quotas : [`docs/GUIDE.md`](docs/GUIDE.md).

## Structure

```text
backend/    FastAPI, SQLAlchemy, migrations Alembic
frontend/   React + Vite, servi par Nginx
tests/      suite pytest (contrat API) et suite Playwright (UI)
postman/    collection chaînée + environnement
infra/      campagne Squash TM (docker compose dédié)
docs/       plan, cas, anomalies, traçabilité, rapports
```

## Documentation

| Document | Contenu |
| --- | --- |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | état des versions, ce qui reste, prochains jalons |
| [`docs/GUIDE.md`](docs/GUIDE.md) | guide complet : démarrage, tests, configuration, quotas, campagnes V1/V2/V3 |
| [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) | périmètre, hypothèses, risques, critères d'entrée et de sortie |
| [`docs/TEST_CASES.md`](docs/TEST_CASES.md) | 59 cas manuels et résultats |
| [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) | matrice 25 exigences → 59 cas → exécution → anomalie |
| [`docs/ANOMALIES.md`](docs/ANOMALIES.md) | rapports ANO-001 à ANO-005 |
| [`docs/CAMPAIGN_REPORT.md`](docs/CAMPAIGN_REPORT.md) | métriques finales, risques résiduels, recommandations |
| [`docs/SQUASH.md`](docs/SQUASH.md) | campagne finale Squash TM |
| [`docs/DEFENSE.md`](docs/DEFENSE.md) | trame de soutenance et démonstration |
| [`docs/CONCEPTION.md`](docs/CONCEPTION.md) | conception technique de l'application |
| [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) | définition de « terminé » |
| [`CHANGELOG.md`](CHANGELOG.md) | historique daté des modifications |

## Versions et tags

| Repère | Commit | Usage |
|---|---|---|
| `v1.0-campagne-v1` | `eabd40f` | État consolidé après la campagne V1 |
| Application V1 testée | `a0ea6e6` | Commit de l'application au moment de la campagne V1 |
| `v3.0` | `3ba1ec9` | Version de code V3 |
| `v3.1-campagne-finale` | `db1923a` | Campagne finale V3 (contenu et rapports) |
| `v3.1.1-campagne-finale` | `main` après fusion | Clôture finale, CI verte et correctif Postman |

## Périmètre et limites

- Projet réalisé dans le cadre d'une **formation en test logiciel**. L'application support a été
  soumise au formateur et validée avant le début des travaux.
- Les anomalies ne sont **pas corrigées** : elles constituent la matière de la campagne. Chaque
  test associé est marqué `xfail(strict=True)` et échouera si l'anomalie est un jour corrigée.
- La campagne manuelle V3 est **terminée** : 9 cas choisis par les risques, complétés par les
  suites automatisées. Le détail et les limites sont dans
  [`docs/CAMPAIGN_REPORT.md`](docs/CAMPAIGN_REPORT.md).
- La couverture est **mono-navigateur** (Chromium) ; Firefox et WebKit sont des améliorations
  planifiées, pas des résultats acquis.
- Les tests de performance et l'accessibilité normée sont **hors périmètre** et documentés comme
  tels dans le plan de test.

## Dépôt de rendu

Le dépôt de rendu du projet final est **`MomoTeen07/football-qa`** (ce dépôt). Le dossier voisin
`football-qa-agents` est un projet personnel distinct, non requis par l'énoncé : il ne fait pas
partie du dépôt unique à rendre.

## Crédits et code réutilisé

- Application, tests et documentation écrits par Mohamed Abdo pour la formation Testeur QA 2026
  (BStorm).
- Bibliothèques open source : FastAPI, SQLAlchemy, Alembic, React, Vite, PyTest, Playwright,
  Newman, Allure, Squash TM. Versions verrouillées dans `backend/requirements.txt`,
  `frontend/package-lock.json` et `tests/playwright/package-lock.json`.
- Données football : API publique [football-data.org](https://www.football-data.org/) (plan
  gratuit) et flux RSS public de RMC Sport. Aucun code propriétaire n'est réutilisé.
- Le format `CHANGELOG.md` suit [Keep a Changelog](https://keepachangelog.com/).

## Licence

[MIT](LICENSE) — code de l'application et suites de test réutilisables avec attribution.
