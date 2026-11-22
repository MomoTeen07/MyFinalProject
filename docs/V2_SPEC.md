# Spécification V2 — Football QA

| Élément | Valeur |
|---|---|
| Statut | **Proposition à valider** — aucun code ne démarre avant accord |
| Base | `main` figé par le tag `v1.0-campagne-v1` (`eabd40f`) |
| Branche de développement | `app/v2` |
| Objectif | Enrichir l'application support **sans invalider** la démarche QA déjà produite |
| Dernière révision | 22/11/2026 — note de favori et rôle admin écartés |

## 1. Principes

1. **Additif uniquement.** On ajoute des fonctionnalités, on ne réécrit pas l'existant.
2. **Défauts conservés.** ANO-001 à ANO-005 restent ouvertes : elles sont la preuve
   de la campagne et le support de démonstration. Corriger un défaut = perdre une
   anomalie reproductible.
3. **Une fonctionnalité = une PR = une CI verte.** Pas de méga-branche.
4. **Les tests ne sont jamais supprimés.** Ils sont adaptés au fil de l'eau, dans
   la même PR que le changement d'API.
5. **Aucune refonte visuelle.** Le CSS et les composants existants sont réutilisés.
6. **Aucune migration de base** : la V2 n'ajoute aucune colonne.

## 2. Périmètre retenu (4 fonctionnalités)

### F1 — Pagination, tri et filtres des matchs

- **Besoin** : en données réelles, la Premier League renvoie 380 matchs, tous
  rendus d'un coup. Défaut de performance réel, aujourd'hui invisible en simulé.
- **API** : `GET /api/football/leagues/{code}/matches?page=1&page_size=50&status=&team_id=&sort=date|date_desc`
- **Contrat** : réponse en enveloppe `{ items, total, page, page_size, total_pages }`.
  **Changement cassant** assumé : le tableau nu disparaît.
- **Règles** : `page >= 1`, `1 <= page_size <= 100`, `status` dans une liste
  fermée (celle déjà utilisée par l'interface), `sort` dans `{date, date_desc}`,
  page au-delà de la dernière → `items: []`. Paramètre invalide → `422`.
- **Mise en œuvre** : filtrage et pagination **applicatifs**, après récupération
  et mise en cache de la liste complète. Déterministe, indépendant des
  capacités de filtrage du fournisseur, donc testable.
- **UI** : sélecteur de page, filtre de statut, tri. État « aucun résultat »
  distinct de l'erreur.
- **Valeur QA** : partitions d'équivalence, valeurs limites (`0`, `1`, `101`),
  combinaisons de filtres, stabilité de la pagination entre deux appels.

### F2 — Meilleurs buteurs et passeurs

- **Besoin** : valoriser les performances individuelles d'un championnat, et
  donner un second classement à tester (ordre, égalités, données manquantes).
- **Source** : `GET /competitions/{code}/scorers?limit=N` du fournisseur.
  **Constat du 22/11/2026** : `assists` vaut `null` (et non `0`) quand la donnée
  manque — ex. Haaland, 9 buts, `assists: null`. Ce cas est normalisé côté
  service et testé explicitement.
- **API** : `GET /api/football/leagues/{code}/scorers?limit=10&sort=goals|assists`
  - `limit` : `1..50`, défaut `10` ; `sort` : `goals` (défaut) ou `assists`.
  - Réponse : `{ competition, season, items: [{ position, player, team,
    goals, assists, penalties, playedMatches }] }`.
- **Règles de classement (déterministes, donc testables)** :
  1. tri décroissant sur la métrique demandée ;
  2. égalité → plus de buts marqués ;
  3. nouvelle égalité → moins de matchs joués ;
  4. dernière égalité → nom du joueur, ordre alphabétique.
  `assists` absent du fournisseur est exposé comme `0` (jamais `null`).
- **Erreurs** : championnat inconnu → `404` avant appel fournisseur ;
  `limit` hors bornes ou `sort` inconnu → `422` ; aucune donnée → `200` avec
  `items: []`.
- **Mode simulé** : jeu `MOCK_SCORERS` déterministe pour les 6 championnats,
  afin que les tests unitaires restent hors ligne.
- **UI** : troisième onglet « Buteurs » dans la page championnat, avec bascule
  « Buts / Passes », tableau `#`, joueur, équipe (lien vers la fiche), matchs,
  buts, passes. États chargement / erreur / vide réutilisés.
- **Valeur QA** : tri multi-critères, égalités, `null` vs `0`, bornes de `limit`,
  énumération de `sort`, état vide, cohérence UI ↔ API, liens joueur → équipe.

### F3 — Profil et changement de mot de passe

- **Besoin** : compléter le parcours authentifié, créer de la régression utile.
- **API** : `PATCH /api/users/me` (`name`) et
  `POST /api/users/me/password` (`current_password`, `new_password`) → `204`.
- **Règles** : ancien mot de passe obligatoire, nouveau ≥ 8 caractères et
  différent de l'ancien, e-mail non modifiable. Mot de passe incorrect → `401`.
- **Limite assumée et documentée** : les jetons déjà émis restent valides après
  changement (pas de `token_version`). Candidat à une nouvelle anomalie.
- **UI** : page `/profile` avec deux formulaires.
- **Valeur QA** : régression authentification, valeurs limites, cas négatifs.

### F4 — Page détail d'un match

- **Besoin** : nouveau parcours de bout en bout, et gestion du `404` fournisseur.
- **API** : `GET /api/football/matches/{id}` (relais du fournisseur).
- **UI** : `/matches/:id` — compétition, statut, score, équipes, date.
  Lien depuis la liste des matchs.
- **Règles** : identifiant inconnu → `404` (sert de cas concret pour ANO-005,
  sans la corriger).
- **Valeur QA** : parcours E2E supplémentaire, dépendance à une donnée externe
  non déterministe (oracle API).

## 3. Hors périmètre (explicite)

- Correction d'ANO-001 à ANO-005.
- **Note personnelle sur un favori** — écartée le 22/11/2026.
- **Rôle administrateur et matrice de permissions** — écarté le 22/11/2026.
  Conséquence assumée : on perd le test transverse 401/403 par rôle. La sécurité
  reste couverte par ANO-001 à ANO-004 et par les tests d'authentification.
- Paiement, messagerie, notifications, temps réel.
- Upload de fichiers, avatars, i18n, thème sombre, refonte graphique.
- Modification de l'e-mail ou suppression de compte.
- Refresh token, révocation de jeton, MFA.
- Toute modification du projet `football-qa-agents` (en stand-by).

## 4. Modèle de données et migrations

**Aucune migration Alembic.** Les quatre fonctionnalités réutilisent le schéma
existant :

- `users` : `name` existe déjà (F3) ;
- `favorites` : inchangé ;
- matchs, buteurs, compétitions : données du fournisseur, mises en cache en
  mémoire, non persistées.

C'est un choix délibéré : moins de risque de régression, et la base reste
strictement identique à celle de la campagne V1.

## 5. Contrats d'API (récapitulatif)

| Méthode | Route | Accès | Statuts |
|---|---|---|---|
| GET | `/api/football/leagues/{code}/matches` | public | 200, 404, 422 |
| GET | `/api/football/leagues/{code}/scorers` | public | 200, 404, 422 |
| GET | `/api/football/matches/{id}` | public | 200, 404, 502 |
| PATCH | `/api/users/me` | authentifié | 200, 401, 422 |
| POST | `/api/users/me/password` | authentifié | 204, 401, 422 |

On passe de 11 à **15 endpoints**.

## 6. Impact QA (à prévoir dès la première PR)

| Élément | Impact |
|---|---|
| `tests/pytest/tests/test_football.py` | contrat `matches` en enveloppe, pagination, filtres, buteurs (tri, égalités, `null` → `0`, bornes) |
| `tests/pytest/tests/test_favorites.py` | **aucun changement** (schéma et routes inchangés) |
| `tests/pytest/tests/test_auth.py` | profil, changement de mot de passe |
| `tests/pytest/tests/test_security.py` | `401` sur les routes profil, non-fuite de `password_hash` |
| Schémas JSON | `matches` (enveloppe), nouveau `scorers` |
| Postman | 2 dossiers + assertions (objectif ≈ 55) |
| Playwright | pagination/filtres, onglet buteurs, profil, détail match |
| `docs/TEST_CASES.md` | +12 à +15 cas manuels |
| `docs/TRACEABILITY.md` | nouvelles exigences R-17 à R-20 |
| Squash TM | nouvelles exigences et cas, campagne V2 |
| `docs/CAMPAIGN_REPORT.md` | métriques V2, anomalies nouvelles |
| `README.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` | mis à jour à chaque PR |

## 7. Séquencement

1. **PR V2-0** : cette spécification (documentation seule).
2. **PR V2-1** : F2 buteurs/passeurs — la moins risquée, aucune migration,
   immédiatement démontrable.
3. **PR V2-2** : F3 profil et mot de passe.
4. **PR V2-3** : F1 pagination — structurante, elle touche le contrat des matchs.
5. **PR V2-4** : F4 détail de match.
6. **PR V2-5** : campagne V2 (traçabilité, Squash, rapport, démo).

Chaque PR : code + tests adaptés + docs + CI verte. Aucune PR ne casse `main`.

## 8. Definition of Done (par fonctionnalité)

- [ ] Implémentation backend (sans migration si possible)
- [ ] Tests backend, API et UI adaptés ou ajoutés, verts en local **et** en CI
- [ ] Collection Postman mise à jour
- [ ] `README.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` à jour
- [ ] Aucun secret dans le diff, aucune régression sur les suites existantes
- [ ] Anomalies existantes toujours reproductibles

## 9. Décisions à valider avant tout code

1. **Périmètre** : les 4 fonctionnalités, ou seulement 2 (F1 + F2) ?
2. **Pagination** : accepter le changement cassant de contrat (enveloppe) ?
3. **Buteurs** : bascule « Buts / Passes » dans un seul onglet, ou deux onglets
   distincts ? Et `limit` par défaut à 10 ou 20 ?
4. **Ordre** : commencer par F2 (sûr, démontrable vite) comme proposé, ou
   attaquer F1 tout de suite ?
