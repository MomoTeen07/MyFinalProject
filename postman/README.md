# Collection Postman — Football QA

Collection de tests d'API du projet final QA, exécutable dans Postman ou en
ligne de commande avec Newman.

## Fichiers

| Fichier | Rôle |
|---|---|
| `Football-QA.postman_collection.json` | 22 requêtes, 4 dossiers, 52 assertions |
| `Football-QA.postman_environment.json` | Environnement local (`baseUrl = http://localhost:8001`) |

## Prérequis

L'application doit être démarrée et saine :

```bash
docker compose up --build --detach --wait
```

Vérification rapide : <http://localhost:8001/health> renvoie `{"status":"ok"}`.

## Exécution

Dans Postman : **Import** → sélectionner les deux fichiers → choisir
l'environnement « Football QA - local » → **Run collection**.

En ligne de commande (Newman, gratuit, Node.js 18+) :

```bash
npx --yes newman@6 run postman/Football-QA.postman_collection.json \
  -e postman/Football-QA.postman_environment.json
```

Rapport JUnit pour la CI :

```bash
npx --yes newman@6 run postman/Football-QA.postman_collection.json \
  -e postman/Football-QA.postman_environment.json \
  --reporters cli,junit --reporter-junit-export postman-report.xml
```

## Couverture

| Dossier | Requêtes | Ce qui est vérifié |
|---|---|---|
| `01 - Authentification` | 5 | Inscription, doublon 409, connexion, refus 401 sans énumération de compte, profil courant |
| `02 - Football` | 9 | Championnats (6), classement ordonné, calendrier, buteurs (enveloppe, positions, tri), passeurs (tri et départage), limite invalide 422, championnat inconnu 404, fiche équipe |
| `03 - Favoris (scénario chaîné)` | 5 | Ajout, liste, doublon 409, suppression 204, suppression déjà effectuée 404 |
| `04 - Sécurité` | 3 | Accès sans jeton, jeton malformé, jeton `alg: none` |

Le scénario chaîné correspond à l'exigence de l'énoncé : **connexion → ajout
d'un favori → consultation → suppression → vérification**. Le jeton renvoyé par
l'inscription ou la connexion est mémorisé dans la variable de collection
`token` ; l'identifiant du favori dans `favoriteId`.

## Variables

| Variable | Usage |
|---|---|
| `baseUrl` | Racine de l'API (environnement) |
| `uniqueEmail` | Générée automatiquement à chaque exécution (`Date.now()`) |
| `password` | Mot de passe des comptes de test (`Password123!`) |
| `token` / `favoriteId` | Renseignées par les scripts de test |

Chaque exécution crée un compte neuf : la collection est rejouable sans
nettoyage préalable et n'utilise que des données de test.

## Limites connues

- Pas de collection de non-régression sur les données réelles
  (`FOOTBALL_API_TOKEN` absent en local).
- Les assertions sur les buteurs portent sur des **invariants** (tri, bornes,
  absence de `null`), pas sur des noms de joueurs : elles restent valables
  quand la saison change.
- Les contrôles de sécurité couvrent l'authentification et le cloisonnement ;
  ils ne remplacent pas la suite PyTest, qui teste en plus la falsification de
  signature et l'absence de limitation des tentatives (anomalie ANO-004).
