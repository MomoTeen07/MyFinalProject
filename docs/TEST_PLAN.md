# Plan de test — Football QA

| Élément | Valeur |
|---|---|
| Projet | Application « Football QA » (championnats, classements, favoris) |
| Version testée | commit `main` du 13/11/2026 — API 1.0.0 |
| Auteur | Mohamed Abdo — formation Testeur QA 2026 (BStorm) |
| Version du plan | 1.0 |
| Statut | Approuvé pour la campagne V1 |
| Outil de gestion | Squash TM 15 (`infra/squash`) |

## 1. Objet et contexte

Ce plan décrit la stratégie de test appliquée à **Football QA**, application web
de consultation de championnats de football permettant à un utilisateur
authentifié d'enregistrer des équipes favorites.

L'application est composée de :

- un **frontend React** (Vite) servi par Nginx, accessible sur
  `http://localhost:5174` ;
- une **API REST FastAPI** exposée sur `http://localhost:8001`, protégée par
  jeton JWT sur les routes personnelles ;
- une **base PostgreSQL 16** persistante (volume Docker) ;
- une **source de données football** externe (football-data.org), remplacée en
  local par un jeu de données simulé (`MOCK_FOOTBALL_API=true`).

Le plan couvre l'ensemble de la chaîne qualité attendue : cadrage, tests
manuels, tests d'API, automatisation UI, intégration continue, rapport de
campagne et soutenance.

### 1.1 Choix de l'application

Le choix de l'application fait partie de l'épreuve. **Football QA a été soumise
au formateur et validée avant le début des travaux**, ce qui garantit un niveau
de difficulté comparable entre stagiaires.

| Critère de l'énoncé | Réponse de Football QA |
|---|---|
| Application web avec interface utilisateur | Frontend React/Vite : connexion, inscription, championnats, classement, calendrier, fiche équipe et favoris |
| API testable avec authentification | API REST FastAPI, 11 endpoints, JWT `Bearer` sur les routes personnelles |
| Persistance et règles métier | PostgreSQL 16, migrations Alembic, favoris uniques par utilisateur, cloisonnement des comptes |
| Exécutable localement | Docker Compose, 3 conteneurs, mode simulé sans clé payante |
| Complexité suffisante | Parcours visiteur et authentifié, états de chargement et d'erreur, données externes, pages dédiées (accueil, championnats, championnat, équipe, favoris, authentification) |
| Accès licite | Dépôt applicatif du projet, code source accessible, aucune restriction de test |

La correspondance détaillée, avec les fichiers de preuve, est tenue à jour dans
le [`README.md`](../README.md#choix-de-lapplication). L'application est testée
**non modifiée** : les anomalies constatées sont documentées et non corrigées.

## 2. Périmètre

### 2.1 Dans le périmètre

| Domaine | Contenu |
|---|---|
| Authentification | Inscription, connexion, déconnexion, session persistante, validation des entrées |
| Football | Liste des championnats, classement, calendrier, fiche équipe, erreurs 404 |
| Favoris | Ajout, consultation, suppression, doublon, isolation entre comptes, persistance |
| Sécurité applicative | JWT (absence, malformation, `alg: none`, signature falsifiée), cloisonnement des données, robustesse (brute force) |
| Interface | Parcours critique de bout en bout, états de chargement et d'erreur, accessibilité de base (libellés, rôles ARIA) |
| CI/CD | Pipeline GitHub Actions, rapports Allure, artefacts d'échec |
| Non-régression technique | Tests unitaires backend, contrats JSON Schema |

### 2.2 Hors périmètre

- Performance et montée en charge (aucun test de charge : budget 0 €, pas
  d'environnement dédié).
- Tests de compatibilité multi-navigateurs : la suite UI cible Chromium. Firefox
  et WebKit sont supportés par Playwright mais non exécutés.
- Tests d'accessibilité normés (WCAG AA) : seuls des contrôles de structure
  (rôles, libellés) sont effectués.
- Sécurité offensive complète (pentest), conformité RGPD, audit
  d'infrastructure.
- Intégration réelle avec l'API football-data.org dans le périmètre de la
  **campagne manuelle V1** : le plan gratuit existe (10 requêtes/minute), mais
  les résultats manuels ont été obtenus en mode simulé, conformément au budget
  0 €. Les **suites automatisées** (PyTest, Postman, Playwright) ont été rendues
  indépendantes du référentiel et rejouées en données réelles le 21/11/2026 ;
  la CI exige désormais le secret `FOOTBALL_API_TOKEN`.

## 3. Hypothèses et contraintes

| # | Hypothèse / contrainte |
|---|---|
| H1 | L'application a été soumise au formateur et validée avant le début des travaux (voir § 1.1 et le README). |
| H2 | Toutes les exécutions se font en local via Docker Compose ; aucun environnement de recette distant. |
| H3 | Le budget est de 0 € : outils open source uniquement (Playwright, PyTest, Postman/Newman, Allure, Squash TM). |
| H4 | Le référentiel de la **campagne manuelle V1** est le mode simulé (`MOCK_FOOTBALL_API=true` : 6 championnats, 4 équipes par classement, 3 matchs). Les suites automatisées ne dépendent plus de ce référentiel : elles vérifient des invariants et, côté UI, comparent l'interface aux réponses réelles de l'API (oracle). Le mode réel change les données, pas les règles ni les anomalies. |
| H5 | Les tests créent leurs propres comptes : aucun jeu de données de production n'est utilisé. |
| H6 | Les défauts applicatifs constatés sont documentés et non corrigés : ils constituent une preuve QA attendue par le jury. |
| H7 | Un seul testeur, une seule machine : les tests sont séquentiels côté API, parallélisés (2 workers) côté UI. |

## 4. Approche basée sur les risques

### 4.1 Méthode

Chaque risque est noté :

- **Probabilité** (P) : 1 = rare, 2 = possible, 3 = probable ;
- **Impact** (I) : 1 = mineur, 2 = majeur, 3 = critique ;
- **Criticité** = P × I.

La priorité d'effort de test suit la criticité décroissante. Les risques de
criticité ≥ 6 sont couverts par des tests automatisés **et** des tests manuels ;
les risques de criticité 3 à 5 par des tests automatisés seuls ou des contrôles
exploratoires.

### 4.2 Matrice des risques

| ID | Risque | P | I | Criticité | Couverture |
|---|---|---|---|---|---|
| R1 | Fuite de données entre comptes (favoris d'autrui visibles ou supprimables) | 2 | 3 | **6** | TC-FAV-06, TC-SEC-06, TC-SEC-07, tests API `test_security.py`, test UI d'isolation |
| R2 | Régression du parcours critique (ajout/consultation/suppression d'un favori) | 3 | 2 | **6** | TC-FAV-01 à TC-FAV-05, suite Playwright `favorites.spec.js` |
| R3 | Authentification contournable (JWT forgé, `alg: none`) | 1 | 3 | 3 | TC-SEC-01 à TC-SEC-04, `test_security.py`, collection Postman |
| R4 | Perte des favoris après redémarrage (persistance) | 2 | 3 | **6** | TC-FAV-07, TC-FAV-08, vérification du volume PostgreSQL |
| R5 | Abus de connexion (brute force, pas de limitation) | 3 | 2 | **6** | TC-SEC-05 → **ANO-004** |
| R6 | Données invalides acceptées (équipe inexistante, URL d'écusson arbitraire) | 2 | 3 | **6** | TC-SEC-08, TC-SEC-09 → **ANO-001**, **ANO-002** |
| R7 | Contrats d'API non respectés après évolution | 2 | 2 | 4 | Tests JSON Schema (`schemas/`) |
| R8 | Indisponibilité non détectée (supervision mensongère) | 2 | 2 | 4 | TC-SEC-10 → **ANO-003** |
| R9 | Régression visuelle ou de navigation | 3 | 1 | 3 | Suite Playwright `championships.spec.js`, `smoke.spec.js` |
| R10 | Environnement non reproductible (CI ≠ local) | 1 | 3 | 3 | Pipeline GitHub Actions identique à la procédure locale |

### 4.3 Priorisation retenue

1. **Sécurité des données personnelles** (R1, R3) : cloisonnement et intégrité
   des jetons.
2. **Parcours métier critique** (R2, R4) : le favori est la seule donnée créée
   par l'utilisateur.
3. **Robustesse et validation** (R5, R6, R7) : entrées non fiables.
4. **Exploitabilité** (R8, R10) : capacité à détecter une panne et à rejouer les
   tests.
5. **Confort et régression mineure** (R9).

## 5. Niveaux et types de test

| Niveau | Outil | Portée | Nombre |
|---|---|---|---|
| Unitaire | PyTest | Services backend (sécurité des mots de passe, jetons) | 4 tests |
| Intégration API | PyTest + JSON Schema | 11 endpoints REST, validation, sécurité | 53 tests, 3 xfail |
| API « client » | Postman / Newman | Collection importable, scénario chaîné | 18 requêtes, 41 assertions |
| Interface (E2E) | Playwright + POM | Parcours critique, états d'erreur, session | 17 tests |
| Manuel | Squash TM | Cas conçus par partitions d'équivalence et valeurs limites | 36 cas |
| Exploratoire | Session chronométrée | Zones grises : erreurs réseau, données limites, navigation | 1 session de 45 min |

### 5.1 Techniques de conception

- **Partitions d'équivalence** : e-mail valide/invalide, mot de passe
  conforme/non conforme, code championnat existant/inconnu, identifiant
  d'équipe existant/inexistant.
- **Valeurs limites** : mot de passe 7/8/9 et 128/129 caractères ; nom 1/2/3 et
  100/101 caractères ; `team_name` 1/150/151 caractères ; `team_crest`
  500/501 caractères ; `team_id` 0/1/-1.
- **Tables de décision** : visiteur / utilisateur authentifié × action
  (consulter, ajouter, supprimer) × ressource (à soi / à autrui).
- **Tests exploratoires** : session guidée par les risques R1, R5, R6, R8.
- **Tests de contrat** : JSON Schema pour chaque réponse de l'API football et
  des favoris.

## 6. Environnement et données

| Composant | Version / configuration |
|---|---|
| Système | Windows 11, Docker Desktop 29.9.2, Compose v5.6.1 |
| Python | 3.12.10, PyTest 8.4.1, jsonschema 4.25.1, allure-pytest 2.16.2 |
| Node.js | 20.10.0 (local), 22 (CI), Playwright 1.x, allure-playwright 3.14.0 |
| Postman | Newman 6.x (CLI), collection `postman/` |
| Base | PostgreSQL 16-alpine, port hôte 5433, volume `postgres_data` |
| Application | API `:8001`, UI `:5174`. Campagne manuelle V1 en mode simulé ; suites automatisées en mode réel (`MOCK_FOOTBALL_API=false`) |
| Gestion de test | Squash TM 15.0.3, `http://localhost:8090/squash` |

**Jeux de données** : comptes générés à la volée (`qa.<uuid>@example.com`),
équipes **lues dynamiquement** dans l'API (identifiants stables : Arsenal 57,
Chelsea 61, Liverpool 64, Atlético 78) et entrées invalides figées dans
`tests/pytest/data/`.

**Remise à zéro** : `docker compose down --volumes` puis
`docker compose up --build --detach --wait`.

## 7. Critères d'entrée

- Application démarrée et les trois conteneurs `healthy`.
- `GET /health` répond `200 {"status":"ok"}`.
- Jeux de données simulés disponibles (6 championnats).
- Suites de test installées (`requirements.txt`, `npm ci`).
- Version de l'application figée (commit identifié).

## 8. Critères de sortie

| Critère | Seuil |
|---|---|
| Tests automatisés backend + API + UI | 100 % verts (les xfail documentés sont autorisés) |
| Assertions Postman | 0 échec |
| Cas manuels critiques (priorité haute) | 100 % exécutés, aucun bloquant ouvert non documenté |
| Anomalies critiques / majeures | Documentées, reproductibles, avec preuve |
| Traçabilité exigence → cas → exécution → anomalie | Complète (`docs/TRACEABILITY.md`) |
| Pipeline CI | Vert sur `main`, exécution visible dans l'historique |
| Rapport de campagne | Publié (`docs/CAMPAIGN_REPORT.md`) |

## 9. Organisation et planning

| Phase | Activité | Livrable |
|---|---|---|
| J1 | Cadrage, analyse de risques, plan de test | Ce document |
| J2 | Conception des cas manuels, exécution, rapports d'anomalie | `TEST_CASES.md`, `ANOMALIES.md` |
| J3 | Tests d'API (PyTest + Postman) | `tests/pytest/`, `postman/` |
| J4 | Automatisation UI (POM) | `tests/playwright/` |
| J5 | CI, rapports Allure, campagne Squash TM | `.github/workflows/ci.yml`, `infra/squash/` |
| J6 | Rapport de campagne, support de soutenance | `CAMPAIGN_REPORT.md`, `DEFENSE.md` |

## 10. Risques projet et parades

| Risque projet | Parade |
|---|---|
| Indisponibilité de l'API football externe | Suites automatisées en réel avec reprise bornée ; cache 900 s en CI ; repli simulé pour le hors-ligne |
| Tests UI instables (attentes) | Attentes par assertion Playwright, `expect.timeout` à 7 s, 2 tentatives en CI, traces et vidéos à l'échec |
| Données de test polluées entre exécutions | Comptes uniques par test, base éphémère en CI (`--volumes`) |
| Dépendance à un service payant | Aucune : tous les outils sont open source, aucune clé requise |
| Corruption de l'historique Git | Une branche par sujet, PR obligatoire, fusion en squash après CI verte |

## 11. Livrables

- Plan de test (ce document).
- Cas de test manuels et résultats d'exécution (`docs/TEST_CASES.md`).
- Rapports d'anomalie (`docs/ANOMALIES.md`).
- Matrice de traçabilité (`docs/TRACEABILITY.md`).
- Campagne Squash TM (`infra/squash/`, `docs/SQUASH.md`).
- Suites automatisées : `backend/tests/`, `tests/pytest/`, `tests/playwright/`,
  `postman/`.
- Pipeline et rapports : `.github/workflows/ci.yml`, artefacts Allure.
- Rapport de campagne (`docs/CAMPAIGN_REPORT.md`).
- Support de soutenance (`docs/DEFENSE.md`).
