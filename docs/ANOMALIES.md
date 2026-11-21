# Rapports d'anomalie — Football QA

| Élément | Valeur |
|---|---|
| Campagne | Campagne V1 |
| Version | commit `a0ea6e6` |
| Environnement | Docker local (`API :8001`, `UI :5174`, PostgreSQL 16) |
| Date | 13/11/2026 (ANO-001 à 004), 21/11/2026 (ANO-005, données réelles) |
| Anomalies ouvertes | 5 (0 bloquante, 1 majeure, 3 moyennes, 1 mineure) |

Chaque anomalie est reproductible avec les commandes fournies : aucune ne
dépend d'un état antérieur de la base. Toutes ont été constatées sur
l'application réellement démarrée, pas sur un mock.

## Synthèse

| ID | Titre | Gravité | Priorité | Statut | Test associé |
|---|---|---|---|---|---|
| ANO-001 | L'API accepte un favori dont l'équipe n'existe pas | Majeure | Haute | Ouverte | TC-SEC-08, `xfail` `test_unknown_team_cannot_be_added_as_favorite` |
| ANO-002 | `team_crest` accepte n'importe quel schéma d'URL | Moyenne | Moyenne | Ouverte | TC-SEC-09, `xfail` `test_crest_url_scheme_is_restricted` |
| ANO-003 | `/health` renvoie 200 alors que la base est arrêtée | Majeure | Haute | Ouverte | TC-SEC-10 |
| ANO-004 | Aucune limitation des tentatives de connexion | Moyenne | Haute | Ouverte | TC-SEC-05, `xfail` `test_repeated_failed_logins_are_throttled` |
| ANO-005 | En données réelles, une équipe inconnue renvoie 502 au lieu de 404 | Moyenne | Moyenne | Ouverte | `xfail` `test_unknown_team_returns_404` |

> **Statut « Ouverte »** : les anomalies sont documentées, non corrigées. La
> correction est hors périmètre du projet final ; elles sont conservées comme
> preuve de la démarche QA et comme support de démonstration en soutenance.

---

## ANO-001 — L'API accepte un favori dont l'équipe n'existe pas

| Champ | Valeur |
|---|---|
| ID | ANO-001 |
| Gravité | Majeure |
| Priorité | Haute |
| Type | Intégrité des données / validation |
| Composant | `POST /api/favorites` — `backend/app/api/favorites.py` |
| Détectée par | TC-SEC-08 (partitions d'équivalence, identifiant inexistant) |
| Statut | Ouverte |

### Contexte

Un utilisateur authentifié peut ajouter une équipe à ses favoris en fournissant
`team_id`, `team_name` et, facultativement, `league_code` et `team_crest`.
L'API ne vérifie pas que `team_id` correspond à une équipe du référentiel
football.

### Étapes de reproduction

```bash
# 1. Créer un compte et récupérer le jeton
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ano001@example.com","password":"Password123!","name":"ANO 001"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 2. Ajouter une équipe qui n'existe pas
curl -i -X POST http://localhost:8001/api/favorites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"team_id":987654321,"league_code":"PL","team_name":"Ghost FC"}'
```

### Résultat attendu

`422 Unprocessable Entity` : l'équipe `987654321` n'existe pas dans le
référentiel, le favori ne doit pas être créé.

### Résultat obtenu

`201 Created` avec le corps suivant :

```json
{
  "team_id": 987654321,
  "league_code": "PL",
  "team_name": "Ghost FC",
  "team_crest": null,
  "id": 3,
  "created_at": "2026-11-13T17:09:33.679106"
}
```

### Preuve

- Réponse HTTP ci-dessus (code 201 et corps complet).
- Test automatisé : `tests/pytest/tests/test_favorites.py::test_unknown_team_cannot_be_added_as_favorite`
  (`xfail(strict=True)`), visible dans le rapport Allure.

### Impact

- Données incohérentes : favoris pointant vers une équipe inexistante.
- Lien mort depuis `/favorites` vers `/teams/PL/987654321` (écran d'erreur).
- Un client malveillant peut injecter un nom d'équipe arbitraire (usurpation
  d'affichage), le nom n'étant jamais confronté au référentiel.

### Cause probable

`FavoriteCreate` valide le type et les bornes (`team_id > 0`, longueurs) mais
aucun service ne vérifie l'existence de l'équipe auprès du service football.

### Correction proposée (non appliquée)

Avant l'insertion, résoudre l'équipe via le service football
(`get_team(league_code, team_id)`) et renvoyer `422` si elle est absente.
Ajouter un test de non-régression à la suite API.

---

## ANO-002 — `team_crest` accepte n'importe quel schéma d'URL

| Champ | Valeur |
|---|---|
| ID | ANO-002 |
| Gravité | Moyenne |
| Priorité | Moyenne |
| Type | Validation / hygiène de sécurité |
| Composant | `POST /api/favorites` — schéma `FavoriteCreate` |
| Détectée par | TC-SEC-09 (partitions d'équivalence, schéma d'URL invalide) |
| Statut | Ouverte |

### Contexte

Le champ `team_crest` (URL de l'écusson) est validé uniquement sur sa longueur
(500 caractères maximum). Aucun contrôle du schéma d'URL n'est effectué.

### Étapes de reproduction

```bash
curl -i -X POST http://localhost:8001/api/favorites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"team_id":66,"team_name":"Evil","team_crest":"javascript:alert(1)"}'
```

### Résultat attendu

`422` : seuls les schémas `https:` (et éventuellement `http:`) doivent être
acceptés pour une URL d'image.

### Résultat obtenu

`201 Created`, la valeur `javascript:alert(1)` est stockée et renvoyée telle
quelle.

### Preuve

- Réponse `201` avec `"team_crest": "javascript:alert(1)"`.
- Test automatisé : `tests/pytest/tests/test_favorites.py::test_crest_url_scheme_is_restricted`
  (`xfail(strict=True)`).

### Impact

- **Pas d'exécution de script constatée** : le frontend affiche l'écusson via
  `<img src>` (`frontend/src/components/TeamCrest.jsx`), et un schéma
  `javascript:` dans un `src` d'image n'est pas exécuté par les navigateurs.
- Le défaut reste une faille d'hygiène : données non conformes stockées,
  dépendance à un futur composant qui réutiliserait la valeur dans un contexte
  exécutable (lien, `innerHTML`), et possibilité de charger une ressource
  distante arbitraire (suivi, contenu non maîtrisé).

### Correction proposée (non appliquée)

Valider le champ avec un type `HttpUrl` ou un validateur explicite
(`urlparse(...).scheme in {"http", "https"}`) et refuser `data:`, `javascript:`
et les URL relatives.

---

## ANO-003 — `/health` renvoie 200 alors que la base de données est arrêtée

| Champ | Valeur |
|---|---|
| ID | ANO-003 |
| Gravité | Majeure |
| Priorité | Haute |
| Type | Supervision / disponibilité |
| Composant | `GET /health` — `backend/app/main.py` |
| Détectée par | TC-SEC-10 et session exploratoire EX-01 |
| Statut | Ouverte |

### Contexte

Le point de santé renvoie une constante `{"status": "ok"}` sans interroger la
base. Le `healthcheck` Docker Compose du backend s'appuie sur cette route, et
les pipelines attendent `docker compose up --wait` avant de lancer les tests.

### Étapes de reproduction

```bash
docker compose stop db
sleep 5
curl -i http://localhost:8001/health

curl -i -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ano003@example.com","password":"Password123!","name":"ANO 003"}'

docker compose start db
```

### Résultat attendu

`503 Service Unavailable` sur `/health` (ou un indicateur `database: "down"`),
et conteneur backend signalé *unhealthy* par Docker.

### Résultat obtenu

- `/health` → `200 {"status":"ok"}` alors que la base est arrêtée.
- `POST /api/auth/register` → `500`.
- Le conteneur reste *healthy* : la panne n'est pas détectée.

### Preuve

- Sortie des deux requêtes HTTP ci-dessus.
- Le `healthcheck` de `docker-compose.yml` appelle explicitement `/health` :
  la supervision est donc aveugle à la perte de la base.

### Impact

- Une panne de base n'est pas remontée par la supervision ni par
  l'orchestrateur ; le service est déclaré disponible alors qu'aucune opération
  persistante ne fonctionne.
- En CI, un test pourrait démarrer sur une application « saine » mais inutilisable
  et produire des échecs difficiles à diagnostiquer.

### Correction proposée (non appliquée)

Exécuter `SELECT 1` via la session SQLAlchemy dans `/health` et renvoyer `503`
en cas d'échec. Conserver une route `/health/live` séparée (liveness) si un
contrôle sans base est nécessaire.

---

## ANO-004 — Aucune limitation des tentatives de connexion

| Champ | Valeur |
|---|---|
| ID | ANO-004 |
| Gravité | Moyenne |
| Priorité | Haute |
| Type | Sécurité / robustesse |
| Composant | `POST /api/auth/login` — `backend/app/api/auth.py` |
| Détectée par | TC-SEC-05 (12 tentatives erronées) |
| Statut | Ouverte |

### Contexte

La route de connexion ne limite ni le nombre d'essais par compte, ni le débit
par adresse IP. Le message d'erreur est correctement générique (pas
d'énumération de comptes), mais rien ne freine une attaque par force brute.

### Étapes de reproduction

```bash
for i in $(seq 1 12); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8001/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"ano004@example.com","password":"MauvaisMotDePasse1!"}'
done
```

### Résultat attendu

Après un seuil raisonnable (5 à 10 échecs), réponse `429 Too Many Requests`
avec en-tête `Retry-After`.

### Résultat obtenu

12 réponses `401`, aucune limitation, aucun ralentissement.

### Preuve

- Sortie de la boucle : 12 lignes `401`.
- Test automatisé : `tests/pytest/tests/test_security.py::test_repeated_failed_logins_are_throttled`
  (`xfail(strict=True)`).

### Impact

- Attaque par dictionnaire ou force brute facilitée sur les comptes.
- Risque d'usurpation d'identité si un mot de passe faible est utilisé.
- Coût de calcul (hachage Argon2/bcrypt) exploitable pour saturer le service.

### Correction proposée (non appliquée)

Limitation par couple (adresse IP, e-mail) sur une fenêtre glissante
(ex. 5 échecs / 15 min), réponse `429` avec `Retry-After`, journalisation des
échecs. Un test de non-régression vérifierait l'apparition du `429`.

---

## ANO-005 — En données réelles, une équipe inconnue renvoie 502 au lieu de 404

| Champ | Valeur |
|---|---|
| ID | ANO-005 |
| Gravité | Moyenne |
| Priorité | Moyenne |
| Type | Contrat d'API / gestion d'erreur |
| Composant | `GET /api/football/leagues/{code}/teams/{id}` — `backend/app/services/football_service.py` (`_fetch`) |
| Détectée par | `test_unknown_team_returns_404` (`xfail`), exécution en données réelles du 21/11/2026 |
| Statut | Ouverte |

### Contexte

En mode réel, l'API relaie les erreurs du fournisseur football-data.org. Le
service `_fetch` ne distingue que le cas `429` (traduit en `503`) ; toute autre
erreur HTTP du fournisseur devient un `502 Bad Gateway`.

Un identifiant d'équipe inexistant (`999999`) est refusé par le fournisseur
avec un `HTTP 400`, ce qui produit un `502` côté application.

### Étapes de reproduction

```bash
# Prérequis : MOCK_FOOTBALL_API=false et FOOTBALL_API_TOKEN renseigné
curl -i http://localhost:8001/api/football/leagues/PL/teams/999999
```

### Résultat attendu

`404 Not Found` avec un message métier : la ressource demandée n'existe pas.

### Résultat obtenu

`502 Bad Gateway` avec `{"detail":"Football data API returned HTTP 400"}`.

### Preuve

- Réponse HTTP ci-dessus.
- Test automatisé : `tests/pytest/tests/test_football.py::test_unknown_team_returns_404`,
  marqué `xfail(strict=True)` **uniquement** lorsque `REAL_FOOTBALL_DATA=true`
  (le mode simulé renvoie correctement `404`, le défaut n'existe qu'en réel).

### Impact

- Le client ne peut pas distinguer « ressource inconnue » d'une panne du
  fournisseur : le frontend affiche un écran d'erreur récupérable au lieu d'un
  état « introuvable ».
- Les tableaux de bord de supervision comptabilisent ces 502 comme des
  indisponibilités, ce qui masque les vraies pannes.
- Un identifiant erroné (lien obsolète, favori ANO-001) génère une alerte
  d'infrastructure au lieu d'une erreur applicative.

### Cause probable

`_fetch` mappe toute `httpx.HTTPStatusError` non-429 vers `502`, sans tenir
compte du code du fournisseur.

### Correction proposée (non appliquée)

Traduire les codes du fournisseur : `400`/`404` → `404`, `401`/`403` → `502`
(configuration), `5xx` → `502`. Conserver le `503` + `Retry-After` pour `429`.
Ajouter un test de non-régression dans les deux modes.
