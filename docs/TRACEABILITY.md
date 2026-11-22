# Matrice de traçabilité — Football QA

| Élément | Valeur |
|---|---|
| Campagne | Campagne V1 + V2 (fonctionnalité F2) |
| Version | V1 : commit `a0ea6e6` — V2 : branche `app/v2` |
| Date | 13/11/2026 (V1) — 22/11/2026 (V2) |
| Chaîne couverte | Exigence → cas de test → exécution → anomalie |
| Couverture | 19 exigences / 19 couvertes (100 %) |

Chaque exigence est reliée à au moins un cas manuel, à un test automatisé
(PyTest, Playwright ou Postman) et, le cas échéant, à une anomalie. Les
identifiants de cas renvoient à `docs/TEST_CASES.md`, ceux des anomalies à
`docs/ANOMALIES.md`.

## 1. Exigences fonctionnelles

| ID | Exigence | Cas manuels | Automatisation | Anomalie | Statut |
|---|---|---|---|---|---|
| R-01 | Un visiteur peut créer un compte avec un e-mail valide, un mot de passe de 8 à 128 caractères et un nom de 2 à 100 caractères | TC-AUTH-01, TC-AUTH-02, TC-AUTH-03, TC-AUTH-04, TC-AUTH-05, TC-AUTH-06, TC-AUTH-07, TC-AUTH-08 | `test_auth.py` (7 cas de validation), Postman « Inscription » | — | Conforme |
| R-02 | Un utilisateur peut se connecter et reçoit un jeton JWT exploitable | TC-AUTH-09, TC-AUTH-10, TC-SEC-05 | `test_auth.py::test_login_returns_a_valid_session`, Postman « Connexion » | ANO-004 (pas de limitation des tentatives) | Conforme avec réserve de robustesse |
| R-03 | Un utilisateur peut se déconnecter ; une session expirée ou absente redirige vers la connexion | TC-AUTH-11 | `auth.spec.js` (déconnexion, session après rechargement) | — | Conforme |
| R-04 | La liste des championnats affiche les 6 compétitions du référentiel | TC-FOOT-01, TC-FOOT-05 | `test_football.py`, `championships.spec.js`, Postman « Championnats » | — | Conforme |
| R-05 | Le classement d'un championnat affiche les équipes triées par position | TC-FOOT-02 | `test_football.py` (6 championnats, JSON Schema), `championships.spec.js`, Postman | — | Conforme |
| R-06 | Le calendrier d'un championnat affiche les matchs et leur statut | TC-FOOT-03 | `test_football.py`, `championships.spec.js`, Postman | — | Conforme |
| R-07 | La fiche équipe affiche le nom, le stade et l'écusson | TC-FOOT-04, TC-FOOT-06 | `test_football.py::test_team_details_match_the_contract`, `championships.spec.js`, Postman | — | Conforme |
| R-08 | Un utilisateur authentifié peut ajouter une équipe à ses favoris | TC-FAV-01, TC-FAV-08, TC-FAV-09 | `test_favorites.py`, `favorites.spec.js`, Postman « Ajouter Arsenal » | ANO-001 (équipe inexistante), ANO-002 (écusson) | Conforme avec réserves |
| R-09 | Un utilisateur voit uniquement ses favoris, du plus récent au plus ancien | TC-FAV-03, 06 | `test_favorites.py::test_newest_favorite_is_listed_first`, `test_security.py`, `favorites.spec.js` | — | Conforme |
| R-10 | Un utilisateur peut supprimer un de ses favoris | TC-FAV-04, TC-FAV-05 | `test_favorites.py::test_chained_scenario_add_list_delete`, `favorites.spec.js`, Postman | — | Conforme |
| R-11 | Une même équipe ne peut pas être ajoutée deux fois | TC-FAV-02 | `test_favorites.py::test_the_same_team_cannot_be_added_twice`, Postman | — | Conforme |
| R-12 | Les données d'un compte ne sont ni lisibles ni supprimables par un autre compte | TC-FAV-06 | `test_security.py`, `favorites.spec.js` (deux contextes) | — | Conforme |
| R-13 | Les données favorites survivent à un rechargement et à un redémarrage | TC-FAV-07 | Vérification manuelle + volume PostgreSQL | — | Conforme |
| R-17 | Un visiteur peut consulter le classement des buteurs et des passeurs d'un championnat, avec un ordre déterministe et des compteurs jamais nuls | TC-SCOR-01 à 04 | `test_football.py` (7 tests : contrat JSON Schema, tri, `null` → 0, bornes, 404), `championships.spec.js` (3 tests), Postman (4 requêtes) | — | Conforme |
| R-18 | La page d'accueil affiche les résultats récents des 6 championnats, triés du plus récent au plus ancien, avec un titre cohérent avec le score | TC-NEWS-01 à 04 | `test_football.py` (6 tests : contrat, compétitions, tri, trois branches de titre, 5 bornes), `news.spec.js` (2 tests), Postman (2 requêtes) | — | Conforme |
| R-19 | La page d'accueil peut afficher des titres de presse attribués à leur source, sans qu'une panne du flux ne dégrade le service | TC-PRESS-01 à 03 | `test_football.py` (3 tests de contrat), `backend/tests/test_press.py` (6 tests : parsing, timeout, XML invalide, HTTP 503, troncature, limite), `news.spec.js` (1 test tolérant), Postman (2 requêtes) | — | Conforme |

## 2. Exigences non fonctionnelles

| ID | Exigence | Cas manuels | Automatisation | Anomalie | Statut |
|---|---|---|---|---|---|
| R-14 | Seuls les jetons signés et non expirés donnent accès aux ressources personnelles | TC-SEC-01, TC-SEC-02, TC-SEC-03, TC-SEC-04 | `test_security.py` (5 variantes de jetons invalides), Postman (3 requêtes) | — | Conforme |
| R-15 | Les entrées invalides sont refusées avec un code 4xx explicite | TC-SEC-06, TC-SEC-07, TC-SEC-08, TC-SEC-09 ; TC-AUTH-03, TC-AUTH-04, TC-AUTH-05, TC-AUTH-06, TC-AUTH-07, TC-AUTH-08 | `test_auth.py`, `test_favorites.py` (16 cas pilotés par données) | ANO-001, ANO-002 | Partiel : 2 champs sans contrôle métier |
| R-16 | Le service expose un état de santé fiable et une CI qui exécute les suites | TC-SEC-10 | `.github/workflows/ci.yml` (2 jobs), 3 artefacts | ANO-003 | Partiel : `/health` ne teste pas la base |

## 3. Traçabilité inverse (anomalie → couverture)

| Anomalie | Exigence impactée | Cas de détection | Test automatisé | Preuve |
|---|---|---|---|---|
| ANO-001 | R-08, R-15 | TC-SEC-08 | `test_unknown_team_cannot_be_added_as_favorite` (`xfail` strict) | `docs/ANOMALIES.md` § ANO-001 |
| ANO-002 | R-08, R-15 | TC-SEC-09 | `test_crest_url_scheme_is_restricted` (`xfail` strict) | `docs/ANOMALIES.md` § ANO-002 |
| ANO-003 | R-16 | TC-SEC-10 | Vérification manuelle (base arrêtée) | `docs/ANOMALIES.md` § ANO-003 |
| ANO-004 | R-02 (robustesse) | TC-SEC-05 | `test_repeated_failed_logins_are_throttled` (`xfail` strict) | `docs/ANOMALIES.md` § ANO-004 |

## 4. Couverture des endpoints

| Endpoint | Méthode | Cas | Suite automatisée |
|---|---|---|---|
| `/health` | GET | TC-SEC-10 | Manuelle |
| `/api/auth/register` | POST | TC-AUTH-01 à 08 | PyTest + Postman |
| `/api/auth/login` | POST | TC-AUTH-09, 10 ; TC-SEC-05 | PyTest + Postman |
| `/api/users/me` | GET | TC-SEC-01 à 04 | PyTest + Postman |
| `/api/football/leagues` | GET | TC-FOOT-01, TC-FOOT-05 | PyTest + Postman |
| `/api/football/leagues/{code}/standings` | GET | TC-FOOT-02, 05 | PyTest + Playwright + Postman |
| `/api/football/leagues/{code}/matches` | GET | TC-FOOT-03 | PyTest + Playwright + Postman |
| `/api/football/leagues/{code}/scorers` | GET | TC-SCOR-01 à 04 | PyTest + Playwright + Postman |
| `/api/football/news` | GET | TC-NEWS-01 à 04 | PyTest + Playwright + Postman |
| `/api/football/press` | GET | TC-PRESS-01 à 03 | PyTest + Playwright + Postman + unitaire |
| `/api/football/leagues/{code}/teams/{id}` | GET | TC-FOOT-04, 06 | PyTest + Playwright + Postman |
| `/api/favorites` | GET | TC-FAV-03, 06 | PyTest + Playwright + Postman |
| `/api/favorites` | POST | TC-FAV-01, 02, 08 ; TC-SEC-06 à 09 | PyTest + Playwright + Postman |
| `/api/favorites/{id}` | DELETE | TC-FAV-04, 05, 06 | PyTest + Playwright + Postman |

**Couverture des endpoints : 14 / 14 (100 %).**

## 5. Couverture par niveau de test

| Niveau | Tests | Exigences couvertes |
|---|---|---|
| Unitaire backend | 10 | R-02, R-14 (hachage et jetons), R-19 (presse) |
| API PyTest | 79 (75 passés + 4 `xfail`) | R-01, R-02, R-04 à R-15, R-17 à R-19 |
| Postman | 26 requêtes / 64 assertions | R-01, R-02, R-04 à R-14, R-17 à R-19 |
| UI Playwright | 23 | R-03 à R-13, R-17 à R-19 |
| Manuel | 47 cas | R-01 à R-19 |
