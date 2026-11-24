# Reprise V2 — Football QA

> **À lire en premier.** Ce fichier est le point de reprise de la V2 de
> l'application support. Il contient l'état exact du dépôt, les décisions déjà
> actées (ne pas les re-débattre) et la seule tâche restante : **F1 pagination**.
> Supprimer ce fichier une fois la V2 terminée.

## 1. Où en est le projet

| Élément | Valeur |
|---|---|
| Dépôt | `C:\Users\MAbdo\Desktop\Football-Agent\football-qa` |
| Remote | `https://github.com/MomoTeen07/MyFinalProject.git` |
| Branche de travail | `app/v2`, dernier commit `c52dcb4`, arbre propre |
| `main` | **figée**, tag `v1.0-campagne-v1` (`eabd40f`), CI verte |
| PR | **#16, en brouillon**, https://github.com/MomoTeen07/MyFinalProject/pull/16 |
| Fusion | uniquement quand la V2 est complète **et** avec accord explicite de l'utilisateur |
| CI | verte sur `c52dcb4` (2 jobs). Un seul run par push depuis le correctif de déclenchement |

Règle absolue : **jamais de push direct sur `main`**, jamais de test supprimé,
ANO-001 à ANO-005 restent ouvertes (elles sont la matière des rapports
d'anomalie et de la soutenance).

## 2. Ce qui est déjà livré sur `app/v2`

| # | Fonctionnalité | Commit | API |
|---|---|---|---|
| F2 | Buteurs / passeurs | `f72bf85` | `GET /api/football/leagues/{code}/scorers?limit=10&sort=goals\|assists` |
| F3a | Actualités (résultats récents) | `19fc5e5` | `GET /api/football/news?days=7&limit=10` |
| F3b | Presse RMC Sport | `7e21290` | `GET /api/football/press?limit=5` |
| F4 | Détail d'un match | `c52dcb4` | `GET /api/football/matches/{id}` |
| — | Correctif CI (double pipeline) | `454271c` | — |

Compteurs actuels, vérifiés en **données réelles** le 22/11/2026 :

| Suite | Valeur |
|---|---|
| Backend | 10 passed |
| API PyTest | 78 passed + 4 `xfailed` |
| Postman | 28 requêtes / 69 assertions |
| Playwright | 25 passed |
| Cas manuels | 50 (36 V1 + 14 V2) |
| Endpoints | 15 |

## 3. Décisions actées — ne pas les rouvrir

1. **Périmètre V2** : 4 fonctionnalités (F1 pagination, F2 buteurs, F3 actualités
   + presse, F4 détail de match). Ni rôle admin, ni note de favori, ni profil.
2. **Pagination** : changement cassant **accepté** — réponse en enveloppe
   `{ items, total, page, page_size, total_pages }`, tests adaptés dans la même PR.
3. **Ordre** : F2 → F3a → F3b → F4 → **F1** → campagne V2.
4. **Aucune migration de base** sur les 4 fonctionnalités.
5. **Presse non bloquante** : `/press` renvoie toujours `200`, `available: false`
   en cas d'échec, jamais de `5xx`.
6. **F4** : identifiant de match inconnu → `404` **localement à cette route**.
   ANO-005 (équipe inconnue → `502`) reste volontairement ouverte sur `/teams`.
7. **Mode de travail demandé par l'utilisateur (22/11/2026)** : priorité au
   **développement**. Pendant le code, vérification minimale (build + 2–3 appels
   réels). Les suites complètes, les cas manuels et la doc se mettent à jour
   **en fin de V2**, pas à chaque fonctionnalité. Seule exception : les tests
   qui cassent à cause d'un changement de contrat, à réparer tout de suite pour
   garder la CI verte.

## 4. Tâche restante : F1 — pagination, tri et filtres des matchs

Spécification complète : `docs/V2_SPEC.md` § F1.

### Contrat cible

```
GET /api/football/leagues/{code}/matches
    ?page=1&page_size=50&status=FINISHED&team_id=57&sort=date|date_desc
→ 200 { items: [...], total, page, page_size, total_pages }
```

Règles :

- `page >= 1` ; `1 <= page_size <= 100` ; valeurs invalides → `422` ;
- `status` = liste fermée : `SCHEDULED, TIMED, IN_PLAY, PAUSED, FINISHED,
  POSTPONED, CANCELLED, AWARDED, SUSPENDED` → `Literal` (le `422` est automatique) ;
- `team_id` = entier `>= 0`, filtre sur l'équipe à domicile **ou** à l'extérieur ;
- `sort` = `date` (croissant, ordre du fournisseur) ou `date_desc` ;
- tri stable : `(utcDate, id)`, inverse si `date_desc` ;
- page au-delà de la dernière → `200` avec `items: []` ;
- `total_pages = ceil(total / page_size)`, `0` si `total == 0` ;
- filtrage et pagination **applicatifs**, après récupération et mise en cache de
  la liste complète (le fournisseur ne sait pas paginer finement).

### Décisions d'implémentation déjà prises (à reprendre telles quelles)

- `page_size` par défaut : **50** côté API ; l'interface demande **20**.
- `MOCK_MATCHES` / `_mock_matches(code)` : **6 matchs** dont 2 `FINISHED`, pour
  que la pagination soit démontrable hors ligne.
- `get_match` (F4) en mode simulé : cherche dans `_mock_matches("PL")`, donc les
  identifiants valides passent de 1–3 à **1–6**.
- Interface : chargement **paresseux** des matchs quand l'onglet « Matchs »
  devient actif ; remise à la page 1 quand `status`, `sort` ou `code` change ;
  états distincts « Aucun match pour ce filtre. » / « Aucun match disponible. » ;
  contrôles `Précédent` / `Page x / y` / `Suivant` désactivés aux bornes.

### Implémentation de référence (backend)

```python
def get_matches(code, page=1, page_size=50, status=None, team_id=None, sort="date"):
    if code not in LEAGUES:
        raise HTTPException(status_code=404, detail="Championship not found")

    matches = (_mock_matches(code) if settings.mock_football_api
               else _fetch(f"/competitions/{code}/matches").get("matches", []))

    if status:
        matches = [m for m in matches if m.get("status") == status]
    if team_id is not None:
        matches = [m for m in matches
                   if (m.get("homeTeam") or {}).get("id") == team_id
                   or (m.get("awayTeam") or {}).get("id") == team_id]

    matches = sorted(matches,
                     key=lambda m: (m.get("utcDate") or "", m.get("id") or 0),
                     reverse=sort == "date_desc")

    total = len(matches)
    total_pages = (total + page_size - 1) // page_size if total else 0
    start = (page - 1) * page_size
    return {"items": matches[start:start + page_size], "total": total,
            "page": page, "page_size": page_size, "total_pages": total_pages}
```

Route FastAPI :

```python
@router.get("/leagues/{code}/matches")
def matches(code: str,
            page: int = Query(1, ge=1),
            page_size: int = Query(50, ge=1, le=100),
            status: MatchStatus | None = Query(None),
            team_id: int | None = Query(None, ge=0),
            sort: Literal["date", "date_desc"] = Query("date")):
    return get_matches(code, page=page, page_size=page_size,
                       status=status, team_id=team_id, sort=sort)
```

`MatchStatus` = `Literal[...]` avec les 9 statuts ci-dessus.

## 5. Tests à réparer immédiatement (sinon CI rouge)

| Fichier | Changement minimal |
|---|---|
| `tests/pytest/schemas/matches_schema.json` | passe d'un tableau à l'enveloppe (`items`, `total`, `page`, `page_size`, `total_pages`) |
| `tests/pytest/tests/test_football.py` | `test_matches_match_the_contract` lit `payload["items"]` ; ajouter pagination stable et 422 sur `page=0`, `page_size=101`, `sort=alpha` |
| `tests/playwright/fixtures/test.js` | la requête doit utiliser `?page_size=20&sort=date` et exposer `matchesPayload.items` (sinon le compteur UI ne correspond pas) |
| `tests/playwright/tests/championships.spec.js` | compteur de cartes = `football.matches.length` (déjà 20 maximum) |
| `postman/Football-QA.postman_collection.json` | « Calendrier Premier League » vérifie l'enveloppe et pose `matchId = body.items[0].id` |

## 6. Documentation à mettre à jour en fin de V2

Compteurs à recalculer après F1 (ne pas les inventer) :

- `docs/V2_SPEC.md` : F1 → « implémenté le … », décisions.
- `docs/TEST_CASES.md` : nouveaux cas `TC-PAGI-*`, total, synthèse V2.
- `docs/TRACEABILITY.md` : nouvelle exigence (R-21), ligne endpoint, compteurs.
- `docs/CAMPAIGN_REPORT.md` : campagne V2 (à rejouer, pas encore faite).
- `docs/ANOMALIES.md` : aucune nouvelle anomalie attendue ; ne pas corriger les 5 existantes.
- `README.md` : table V2, nombre d'endpoints, assertions Postman, cas manuels.
- `PROJECT_CONTEXT.md` : tableau V2, commandes, compteurs.
- `CHANGELOG.md` : entrée F1.
- `postman/README.md` : requêtes et assertions.
- `docs/SQUASH.md` : campagne V2 (exigences, cas, exécutions).

## 7. Environnement local

- Docker Desktop : `C:\Users\MAbdo\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe`
  (le moteur doit être démarré avant `docker compose`).
- Ports : UI `5174`, API `8001`, PostgreSQL `5433`.
- `.env` local contient le vrai `FOOTBALL_API_TOKEN` : **ne jamais l'afficher ni le committer**.
- Venv de test : `football-qa\.venv-qa` (ignoré par Git), dépendances de
  `tests/pytest/requirements.txt` déjà installées.
- Les tests backend ne sont pas dans l'image (`.dockerignore`) : il faut
  `docker compose cp backend/tests backend:/app/tests` avant de les lancer.

```powershell
cd C:\Users\MAbdo\Desktop\Football-Agent\football-qa
docker compose up -d --build backend frontend

$env:REAL_FOOTBALL_DATA='true'
.\.venv-qa\Scripts\python.exe -m pytest tests/pytest/tests -q      # attendu : 78 + 4 xfail (avant F1)

docker compose cp backend/tests backend:/app/tests
docker compose exec -T backend python -m pytest tests -q           # attendu : 10

npx --yes newman@6 run postman/Football-QA.postman_collection.json `
  -e postman/Football-QA.postman_environment.json                  # attendu : 69 assertions

cd tests\playwright; npm test                                      # attendu : 25 passed
```

## 8. Pièges déjà rencontrés — ne pas les re-découvrir

| Piège | Conséquence | Parade |
|---|---|---|
| `push` sans filtre dans `ci.yml` | deux pipelines par commit, quota 10 req/min épuisé, `503` transitoires | déjà corrigé : `push: branches: [main]` + `pull_request` |
| Plage `dateFrom`/`dateTo` > 10 jours | le fournisseur renvoie `400` | `NEWS_MAX_DAYS = 10`, `422` applicatif |
| `assists: null` chez le fournisseur | `TypeError` sur un tri naïf | normalisé à `0` |
| Identifiant d'équipe inconnu | `502` au lieu de `404` (ANO-005) | **ne pas corriger** : anomalie à conserver |
| Deux CI simultanées sur le même jeton | quota partagé, échecs intermittents | un seul run par branche |
| `Set-Content -Encoding utf8` sur un fichier accentué | accents corrompus (`Ǹ`) | utiliser l'outil d'édition, jamais réécrire en masse |
| `docker compose exec backend pytest tests` sans copie | `file or directory not found` | `docker compose cp` d'abord |

## 9. Definition of Done de la V2

- [ ] F1 implémentée, contrat en enveloppe, filtres et tri fonctionnels
- [ ] Tests existants adaptés, nouveaux cas de pagination ajoutés
- [ ] Suites vertes en local **et** en CI, en données réelles
- [ ] Docs et compteurs alignés (section 6)
- [ ] Campagne V2 rejouée (Squash, rapport, démo)
- [ ] PR #16 sortie du brouillon, puis fusionnée **avec l'accord de l'utilisateur**
- [ ] `docs/V2_HANDOFF.md` (ce fichier) supprimé
