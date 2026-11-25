# Campagne Squash TM — Football QA

| Élément | Valeur |
|---|---|
| Outil | Squash TM 15.0.3 (open source, édition Community) |
| Base | PostgreSQL 17 |
| URL locale | `http://localhost:8090/squash` |
| Identifiants | `admin` / `admin` (instance locale neuve, à changer hors démonstration) |
| Projet Squash | *Football QA* (id 1) |
| Campagne | *Campagne finale V3 — Football QA* (réf. `CAMP-V3`) |
| Itération | *Itération 1 — campagne finale V3* (réf. `IT-V3`) |
| Suite | *Suite complète — 59 cas* |
| Contenu | 25 exigences, 5 dossiers, 59 cas de test, 59 exécutions |
| Résultat | 54 `SUCCESS`, 5 `FAILURE` (ANO-001 à ANO-005) |

Squash TM est l'outil de gestion de campagne imposé par l'énoncé. Il porte la
traçabilité **exigence → cas de test → exécution → anomalie** ; il ne remplace
ni les suites automatisées (PyTest, Playwright, Postman) ni les documents
`docs/`, qui restent la source de vérité versionnée.

La campagne finale V3 intègre les 36 cas V1, les 14 cas V2 et les 9 cas V3.
L'ancienne campagne V1 (`CAMP-V1`, 16 exigences / 36 cas / 32 `SUCCESS` /
4 `FAILURE`) reste l'historique documenté dans `docs/TEST_CASES.md` et
`docs/CAMPAIGN_REPORT.md` ; l'instance locale est recréée avec la campagne
finale pour que l'outil de gestion porte bien la version livrée.

## 1. Démarrage et arrêt

Le service est isolé dans `infra/squash/docker-compose.yml` : il n'est **pas**
nécessaire pour exécuter les tests de l'application.

```bash
# Démarrage (1 à 3 minutes avant que l'interface réponde)
docker compose -f infra/squash/docker-compose.yml up -d

# Vérification
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8090/squash/login
# 200

# Arrêt en conservant les données
docker compose -f infra/squash/docker-compose.yml down

# Remise à zéro complète (volumes supprimés)
docker compose -f infra/squash/docker-compose.yml down --volumes
```

L'interface est accessible à l'adresse `http://localhost:8090/squash`. Les
données persistent dans le volume `squash_squashtm-db` ; les journaux sont dans
`squash_squashtm-logs`.

> **Authentification de l'API REST.** Depuis Squash TM 15, l'authentification
> Basic est refusée par défaut (`401 Basic authentication is not allowed for
> REST API`). Le compose local ajoute donc
> `JAVA_TOOL_OPTIONS: "-Djava.awt.headless=true -Dsquash.rest-api.disallow-basic-authentication=false"`
> pour permettre au script de seed et aux vérifications en ligne de commande
> de fonctionner. **Cette option est réservée à un usage local** : sur une
> instance partagée, il faut créer un jeton d'API personnel
> (`POST /api/rest/latest/tokens`) et laisser la valeur par défaut.

## 2. Création de la campagne

La campagne est créée par script REST, pas par saisie manuelle : la procédure
est reproductible et versionnée.

```bash
# Prérequis : Squash TM démarré et l'interface répond en 200
python infra/squash/seed_campaign.py
```

Sortie attendue :

```text
Projet « Football QA » créé (id 1)
5 dossiers de cas de test créés
25 exigences créées
59 cas de test créés et rattachés aux exigences
Campagne « Campagne finale V3 — Football QA » créée (id 1)
Itération « Itération 1 — campagne finale V3 » créée (id 1)
Suite « Suite complète — 59 cas » créée (id 1, 59 cas)
54 exécutions réussies, 5 exécutions en échec

Campagne disponible :
  http://localhost:8090/squash/project/1/campaign-workspace
```

Le script est **idempotent par refus** : si un projet nommé *Football QA*
existe déjà, il s'arrête sans rien modifier. Pour rejouer la création :

```bash
docker compose -f infra/squash/docker-compose.yml down --volumes
docker compose -f infra/squash/docker-compose.yml up -d
python infra/squash/seed_campaign.py
```

Variables d'environnement acceptées : `SQUASH_URL` (défaut
`http://localhost:8090`), `SQUASH_USER` et `SQUASH_PASSWORD` (défaut
`admin`/`admin`). Aucune dépendance externe : uniquement la bibliothèque
standard Python 3.12.

### 2.1 Ce que crée le script

| Étape | Objet Squash | Contenu |
|---|---|---|
| 1 | Projet *Football QA* | Description de la campagne finale V3 |
| 2 | Dossiers de cas de test | *Authentification*, *Football*, *Favoris*, *Sécurité et robustesse*, *V3 — parcours enrichis* |
| 3 | Exigences (25) | R-01 à R-25, reprises de `docs/TRACEABILITY.md`, critique `MAJOR`/`CRITICAL`, statut `APPROVED` |
| 4 | Cas de test (59) | Repris de `docs/TEST_CASES.md` : nom, référence `TC-*`, prérequis, description (technique de conception, résultat obtenu, exigences) et **pas de test** action/résultat attendu |
| 5 | Couvertures | Chaque cas est rattaché à ses exigences (`POST /test-cases/{id}/coverages/{versionIds}`) |
| 6 | Campagne | *Campagne finale V3 — Football QA*, statut `PLANNED`, description avec le décompte 54/5 |
| 7 | Itération | *Itération 1 — campagne finale V3*, statut `PLANNED` |
| 8 | Plan de test | 59 items ajoutés explicitement à l'itération (l'itération ne reprend pas automatiquement le plan de la campagne) |
| 9 | Suite | *Suite complète — 59 cas*, contient les 59 items |
| 10 | Exécutions | Une exécution par cas, statut `SUCCESS` (54) ou `FAILURE` (5), chaque pas positionné (`/execution-steps/{id}/execution-status/{Success\|Failure}`), commentaire daté du 25/11/2026 |

Les cinq `FAILURE` correspondent aux cas non conformes :

| Cas | Anomalie | Commentaire d'exécution |
|---|---|---|
| TC-SEC-05 | ANO-004 | 12 × 401, aucune limitation de tentatives |
| TC-SEC-08 | ANO-001 | `201` pour une équipe inexistante (`Ghost FC`) |
| TC-SEC-09 | ANO-002 | `201` pour `team_crest = javascript:alert(1)` |
| TC-SEC-10 | ANO-003 | `/health` → 200 avec la base arrêtée |
| TC-V3-09 | ANO-005 | `502` au lieu de `404` pour une équipe inconnue en données réelles |

Le détail (contexte, reproduction, preuve, gravité, priorité, correction
proposée) reste dans `docs/ANOMALIES.md`. Squash TM n'étant pas connecté à un
bugtracker (Jira/Mantis/Redmine non installés — budget 0 €), les anomalies sont
référencées dans les commentaires d'exécution plutôt que dans des tickets
Squash.

## 3. Données de la campagne

`infra/squash/campaign_data.json` est **généré à partir des documents QA** :

- exigences et cas issus de `docs/TRACEABILITY.md` ;
- titres, techniques, étapes, attendus et statuts issus de `docs/TEST_CASES.md` ;
- anomalies issues des statuts des cas (`Anomalie ANO-*`).

Toute modification des cas ou de la traçabilité doit donc être répercutée dans
ce fichier JSON, puis la campagne recréée :

```bash
python infra/squash/build_campaign_data.py
# 25 exigences, 59 cas (54 SUCCESS, 5 FAILURE) -> infra\squash\campaign_data.json
python infra/squash/seed_campaign.py
```

Le script gère désormais les préfixes V2 (`SCOR`, `NEWS`, `PRESS`, `MATCH`) et
V3 (`V3`), en plus des préfixes V1. Il échouait auparavant sur `KeyError:
'SCOR'` après l'ajout des cas V2.

## 4. Vérification de la campagne

### 4.1 Dans l'interface

1. Ouvrir `http://localhost:8090/squash` et se connecter (`admin` / `admin`).
2. Aller dans l'espace **Campagne** du projet *Football QA*.
3. Vérifier l'arborescence : campagne → itération → suite → 59 items.
4. Ouvrir une exécution : statut, commentaire daté, pas de test.
5. Utiliser **Rapports** → *Avancement des exécutions* pour obtenir la
   répartition 54/5 et le taux de réussite (91,5 %).

### 4.2 En ligne de commande

Sous PowerShell (Windows) :

```powershell
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:admin'))
$headers = @{ Authorization = "Basic $auth" }
$plan = (Invoke-RestMethod -Headers $headers `
  'http://localhost:8090/squash/api/rest/latest/iterations/1/test-plan?size=100')._embedded.'test-plan'

$plan | Group-Object execution_status | Select-Object Name, Count
$plan | Where-Object execution_status -eq 'FAILURE' |
  ForEach-Object { $_.referenced_test_case.reference }
```

Sortie attendue :

```text
Name    Count
----    -----
SUCCESS    54
FAILURE     5

TC-SEC-05
TC-SEC-08
TC-SEC-09
TC-SEC-10
TC-V3-09
```

## 5. API REST utilisée

| Opération | Méthode et chemin | Remarque |
|---|---|---|
| Lister les projets | `GET /projects` | Pagination `page`/`size` |
| Créer un projet | `POST /projects` | `_type: "project"` |
| Créer un dossier de cas | `POST /test-case-folders` | Endpoint non documenté, fonctionnel |
| Créer une exigence | `POST /requirements` | `current_version` obligatoire |
| Créer un cas de test | `POST /test-cases` | `_type: "test-case"` avec `steps` inline |
| Couvrir une exigence | `POST /test-cases/{id}/coverages/{ids}` | `ids` = versions d'exigence |
| Créer une campagne | `POST /campaigns` | `parent` = projet |
| Créer une itération | `POST /campaigns/{id}/iterations` | `parent` = campagne |
| Ajouter un item au plan | `POST /iterations/{id}/test-plan` | Endpoint non documenté, fonctionnel |
| Créer une suite | `POST /test-suites` | `test_plan` = items de l'itération |
| Créer une exécution | `POST /test-plan-items/{id}/executions` | Statut initial `READY` |
| Statuer une exécution | `PATCH /executions/{id}?fields=execution_status,comment` | `SUCCESS`, `FAILURE`, `BLOCKED`… |
| Statuer un pas | `PATCH /execution-steps/{id}/execution-status/{Success\|Failure}` | Libellés en anglais |

Pièges rencontrés :

- `_type: "standard-test-case"` renvoie `400 Invalid JSON` → utiliser
  `_type: "test-case"` ;
- `POST /test-plan-items` renvoie `405` → passer par
  `/iterations/{id}/test-plan` ;
- `DELETE /projects/{id}` renvoie `405` → la remise à zéro passe par
  `down --volumes` ;
- la création des cas avec `steps` inline fonctionne, un `PATCH` ultérieur sur
  `steps` est refusé.

## 6. Lien avec les autres livrables

| Livrable | Rôle | Lien avec Squash |
|---|---|---|
| `docs/TEST_PLAN.md` | Stratégie, risques, critères | Source des exigences et du périmètre |
| `docs/TEST_CASES.md` | 59 cas manuels | Source des cas et des statuts |
| `docs/ANOMALIES.md` | ANO-001 à ANO-005 | Source des 5 `FAILURE` et des commentaires |
| `docs/TRACEABILITY.md` | Matrice exigence → cas → anomalie | Source des exigences et des couvertures |
| `docs/CAMPAIGN_REPORT.md` | Métriques et bilan | Doit rester cohérent avec les 54/5 |
| Suites automatisées | PyTest, Playwright, Postman | Rejouées par la CI ; Squash porte les cas manuels |

## 7. Limites assumées

- **Pas de bugtracker** : aucune « issue » Squash ; les anomalies sont des
  commentaires d'exécution renvoyant à `docs/ANOMALIES.md`.
- **Pas d'automatisation via Squash** : les suites PyTest/Playwright/Postman
  sont exécutées par GitHub Actions, pas par un serveur d'exécution Squash
  (fonctionnalité payante de l'édition Premium).
- **Instance locale uniquement** : pas de sauvegarde ni de haute disponibilité ;
  les données sont recréées par le script en cas de perte du volume.
- **API REST partiellement documentée** : deux endpoints utilisés
  (`/test-case-folders`, `POST /iterations/{id}/test-plan`) ne figurent pas dans
  la documentation officielle mais sont stables sur la version 15.0.3.

## 8. Après correction d'une anomalie

1. Corriger le défaut applicatif et faire passer le test `xfail` correspondant
   en `pass`.
2. Mettre à jour `docs/ANOMALIES.md` (statut *Corrigée*) et
   `docs/TEST_CASES.md` (statut *Passé*).
3. Régénérer `infra/squash/campaign_data.json`.
4. Recréer la campagne (`down --volumes`, `up -d`, `seed_campaign.py`) ou
   ajouter une nouvelle itération pour conserver l'historique.
5. Pour ANO-005, vérifier les deux modes : simulé (`404`) et réel (`404` après
   correction), puis mettre à jour TC-V3-09.
