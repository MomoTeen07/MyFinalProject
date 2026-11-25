# Football QA

**Application de consultation du football, utilisée comme système sous test pour une campagne QA versionnée.**

[![QA CI](https://github.com/MomoTeen07/football-qa/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MomoTeen07/football-qa/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-E2E-2EAD33?logo=playwright&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Licence](https://img.shields.io/badge/Licence-MIT-3DA639)

> **Statut : V3 en cours.**
> Les fonctionnalités V3 sont fusionnées dans `main`. La **campagne manuelle V3 n'est pas démarrée**.
> Dernière preuve figée : **campagne V1** — 36 cas exécutés, 118 vérifications automatisées,
> 5 anomalies documentées (tag `v1.0-campagne-v1`).
> Ce qui reste à faire : [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## En 30 secondes

Ce dépôt contient **deux choses** :

1. une application full-stack fonctionnelle — React, FastAPI, PostgreSQL, JWT, 18 endpoints ;
2. la **campagne de test** qui l'accompagne — plan, cas manuels, automatisation API et UI,
   rapports d'anomalies, traçabilité.

L'application est **volontairement non corrigée** : les anomalies trouvées sont conservées,
documentées et rejouées par des tests `xfail` stricts. L'objectif n'est pas de livrer un produit,
c'est de démontrer une **démarche de test complète** — de l'analyse de risques à la synthèse de campagne.

## Ce que ce dépôt démontre

| Sujet | Où le vérifier |
| --- | --- |
| Analyse de risques (probabilité × impact) et stratégie | [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) |
| Conception de cas (36 exécutés en V1, 50 conçus) | [`docs/TEST_CASES.md`](docs/TEST_CASES.md) |
| Traçabilité exigence → cas → exécution → anomalie | [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) |
| Rapports d'anomalies (gravité, preuve, correctif proposé) | [`docs/ANOMALIES.md`](docs/ANOMALIES.md) |
| Synthèse de campagne et risques résiduels | [`docs/CAMPAIGN_REPORT.md`](docs/CAMPAIGN_REPORT.md) |
| Automatisation UI — Playwright, Page Object Model | [`tests/playwright/`](tests/playwright/) |
| Tests de contrat API — pytest + JSON Schema | [`tests/pytest/`](tests/pytest/) |
| API chaînée — Postman / Newman | [`postman/`](postman/) |
| Gestion de campagne — Squash TM | [`docs/SQUASH.md`](docs/SQUASH.md) |
| CI — Docker Compose, artefacts Allure / Playwright / Postman | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |

## Résultats

**Campagne V1 — terminée et figée** (détail du périmètre dans [`CHANGELOG.md`](CHANGELOG.md)) :

| Métrique | Valeur |
| --- | --- |
| Cas manuels exécutés | 36 |
| Vérifications automatisées | 118 (4 backend, 56 API, 17 UI, 41 assertions Postman) |
| Anomalies documentées | 5 (`ANO-001` à `ANO-005`) |
| Endpoints couverts (périmètre V1) | 11 / 11 |
| Pipeline | vert |

Les rapports **Allure**, **Playwright** et **Postman** sont produits à chaque exécution et
téléchargeables depuis l'onglet [Actions](https://github.com/MomoTeen07/football-qa/actions).
Un lien public permanent n'est pas encore en place — c'est un des points ouverts de
[`docs/ROADMAP.md`](docs/ROADMAP.md).

## Lancer localement

Prérequis : Docker et Docker Compose. Aucune clé API n'est nécessaire : l'application démarre
sur des données simulées et déterministes.

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
| [`docs/CONCEPTION.md`](docs/CONCEPTION.md) | conception technique de l'application |
| [`CHANGELOG.md`](CHANGELOG.md) | historique daté des modifications |

## Périmètre et limites

- Projet réalisé dans le cadre d'une **formation en test logiciel**. L'application support a été
  soumise au formateur et validée avant le début des travaux.
- Les anomalies ne sont **pas corrigées** : elles constituent la matière de la campagne. Chaque
  test associé est marqué `xfail(strict=True)` et échouera si l'anomalie est un jour corrigée.
- Par défaut, l'application fonctionne sur des **données simulées** (sans clé ni quota). Le mode
  données réelles et ses limites sont décrits dans [`docs/GUIDE.md`](docs/GUIDE.md).
- La campagne manuelle **V3** reste à mener : c'est le prochain jalon, pas un résultat acquis.

## Licence

[MIT](LICENSE) — code de l'application et suites de test réutilisables avec attribution.
