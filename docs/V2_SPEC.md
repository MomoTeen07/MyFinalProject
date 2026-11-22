# Spécification V2 — Football QA

| Élément | Valeur |
|---|---|
| Statut | **Proposition à valider** — aucun code ne démarre avant accord |
| Base | `main` figé par le tag `v1.0-campagne-v1` (`eabd40f`) |
| Branche de développement | `app/v2` |
| Objectif | Enrichir l'application support **sans invalider** la démarche QA déjà produite |

## 1. Principes

1. **Additif uniquement.** On ajoute des fonctionnalités, on ne réécrit pas l'existant.
2. **Défauts conservés.** ANO-001 à ANO-005 restent ouvertes : elles sont la preuve
   de la campagne et le support de démonstration. Corriger un défaut = perdre une
   anomalie reproductible.
3. **Une fonctionnalité = une PR = une CI verte.** Pas de méga-branche.
4. **Les tests ne sont jamais supprimés.** Ils sont adaptés au fil de l'eau, dans
   la même PR que le changement d'API.
5. **Aucune refonte visuelle.** Le CSS et les composants existants sont réutilisés.

## 2. Périmètre proposé (5 fonctionnalités)

### F1 — Pagination, tri et filtres des matchs

- **Besoin** : en données réelles, la Premier League renvoie 380 matchs, tous
  rendus d'un coup. Défaut de performance réel, aujourd'hui invisible en simulé.
- **API** : `GET /api/football/leagues/{code}/matches?page=1&page_size=50&status=&team_id=&sort=date|date_desc`
- **Contrat** : réponse en enveloppe `{ items, total, page, page_size, total_pages }`.
  **Changement cassant** assumé : le tableau nu disparaît.
- **Règles** : `page >= 1`, `1 <= page_size <= 100`, `status` dans une liste
  fermée, `sort` dans `{date, date_desc}`, page au-delà de la dernière → `items: []`.
  Paramètre invalide → `422`.
- **UI** : sélecteur de page, filtre de statut, tri. État « aucun résultat »
  distinct de l'erreur.
- **Valeur QA** : partitions d'équivalence, valeurs limites (`0`, `1`, `101`),
  combinaisons de filtres, pagination stable entre deux appels.

### F2 — Note personnelle sur un favori

- **Besoin** : un utilisateur veut annoter une équipe suivie.
- **Données** : `favorites.note` (`VARCHAR(280)`, nullable), `favorites.updated_at`.
- **API** : `PATCH /api/favorites/{id}` avec `{ "note": "..." }` → `200`.
  Note vide ou `null` = suppression de la note. `> 280` caractères → `422`.
- **Règles** : un utilisateur ne peut modifier que **ses** favoris (`404` sinon).
- **UI** : édition en place depuis `/favorites`, compteur de caractères.
- **Valeur QA** : CRUD imbriqué, validation de longueur, cloisonnement,
  injection HTML dans un champ texte libre.

### F3 — Rôle administrateur en lecture seule

- **Besoin** : matérialiser une matrice de permissions testable (401/403).
- **Données** : `users.role` (`VARCHAR(20)`, défaut `user`, valeurs `user|admin`).
- **API** : `GET /api/admin/users` (liste paginée, sans secret) et
  `GET /api/admin/stats` (comptes, favoris). Réservé au rôle `admin`.
- **Règles** : anonyme → `401`, authentifié non-admin → `403`, admin → `200`.
  Aucune route d'écriture admin (lecture seule assumée).
- **Provisionnement** : script `scripts/promote_admin.py <email>`, jamais de
  route publique d'auto-promotion.
- **UI** : entrée de navigation visible uniquement pour un admin, page de liste.
- **Valeur QA** : matrice de permissions, cloisonnement, absence de fuite de
  `password_hash`, test de sécurité transverse.

### F4 — Profil et changement de mot de passe

- **Besoin** : compléter le parcours authentifié, créer de la régression utile.
- **API** : `PATCH /api/users/me` (`name`) et
  `POST /api/users/me/password` (`current_password`, `new_password`) → `204`.
- **Règles** : ancien mot de passe obligatoire, nouveau ≥ 8 caractères et
  différent de l'ancien, e-mail non modifiable. Mot de passe incorrect → `401`.
- **Limite assumée et documentée** : les jetons déjà émis restent valides après
  changement (pas de `token_version`). Candidat à une nouvelle anomalie.
- **UI** : page `/profile` avec deux formulaires.
- **Valeur QA** : régression authentification, valeurs limites, cas négatifs.

### F5 — Page détail d'un match

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
- Paiement, messagerie, notifications, temps réel.
- Upload de fichiers, avatars, i18n, thème sombre, refonte graphique.
- Modification de l'e-mail ou suppression de compte.
- Refresh token, révocation de jeton, MFA.
- Toute modification du projet `football-qa-agents` (en stand-by).

## 4. Modèle de données et migrations

| Table | Colonne | Type | Défaut | Migration |
|---|---|---|---|---|
| `users` | `role` | `VARCHAR(20)` | `user` | révision 1 |
| `favorites` | `note` | `VARCHAR(280)` | `NULL` | révision 1 |
| `favorites` | `updated_at` | `TIMESTAMP` | `created_at` | révision 1 |

Deux révisions Alembic maximum, réversibles, sans perte de données.
Le rôle admin est attribué par script, jamais par l'API publique.

## 5. Contrats d'API (récapitulatif)

| Méthode | Route | Accès | Statuts |
|---|---|---|---|
| GET | `/api/football/leagues/{code}/matches` | public | 200, 404, 422 |
| GET | `/api/football/matches/{id}` | public | 200, 404, 502 |
| PATCH | `/api/favorites/{id}` | authentifié | 200, 404, 422 |
| GET | `/api/admin/users` | admin | 200, 401, 403 |
| GET | `/api/admin/stats` | admin | 200, 401, 403 |
| PATCH | `/api/users/me` | authentifié | 200, 401, 422 |
| POST | `/api/users/me/password` | authentifié | 204, 401, 422 |

On passe de 11 à **18 endpoints**.

## 6. Impact QA (à prévoir dès la première PR)

| Élément | Impact |
|---|---|
| `tests/pytest/tests/test_football.py` | contrat `matches` en enveloppe, nouveaux cas de pagination |
| `tests/pytest/tests/test_favorites.py` | `PATCH` note, cloisonnement, validation |
| `tests/pytest/tests/test_auth.py` | profil, changement de mot de passe |
| `tests/pytest/tests/test_security.py` | matrice 401/403, fuite de `password_hash` |
| Schémas JSON | `matches` (enveloppe), `admin_user`, `stats` |
| Postman | nouveaux dossiers + assertions (objectif ≈ 60) |
| Playwright | pagination/filtres, note de favori, page admin, profil, détail match |
| `docs/TEST_CASES.md` | +15 à +20 cas manuels |
| `docs/TRACEABILITY.md` | nouvelles exigences R-17 à R-21 |
| Squash TM | nouvelles exigences et cas, campagne V2 |
| `docs/CAMPAIGN_REPORT.md` | métriques V2, anomalies nouvelles |
| `README.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` | mis à jour à chaque PR |

## 7. Séquencement

1. **PR V2-0** : cette spécification (documentation seule).
2. **PR V2-1** : F1 pagination — la plus structurante, elle touche le contrat.
3. **PR V2-2** : F2 note de favori.
4. **PR V2-3** : F4 profil et mot de passe.
5. **PR V2-4** : F3 rôle admin.
6. **PR V2-5** : F5 détail de match.
7. **PR V2-6** : campagne V2 (traçabilité, Squash, rapport, démo).

Chaque PR : code + tests adaptés + docs + CI verte. Aucune PR ne casse `main`.

## 8. Definition of Done (par fonctionnalité)

- [ ] Implémentation backend + migration si nécessaire
- [ ] Tests backend, API et UI adaptés ou ajoutés, verts en local **et** en CI
- [ ] Collection Postman mise à jour
- [ ] `README.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md` à jour
- [ ] Aucun secret dans le diff, aucune régression sur les suites existantes
- [ ] Anomalies existantes toujours reproductibles

## 9. Décisions à valider avant tout code

1. **Périmètre** : les 5 fonctionnalités, ou réduire à 3 (F1, F2, F4) ?
2. **Pagination** : accepter le changement cassant de contrat (enveloppe) ?
3. **Rôle admin** : utile pour le jury, ou complexité inutile ?
4. **Note de favori** : texte libre seul, ou texte + note de 1 à 5 ?
5. **Ordre** : garder F1 en premier, ou commencer par les fonctionnalités les
   moins risquées (F2, F4) pour sécuriser une V2 utilisable rapidement ?
