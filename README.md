# ⚽ Football QA

Application web de consultation de football conçue comme support d'un projet final QA.

## Stack

- Frontend : React + JavaScript + CSS
- Backend : Python + FastAPI
- Authentification : JWT
- Base : PostgreSQL
- Données football : API football externe configurable
- Conteneurs : Docker
- Tests : PyTest, Playwright, SQL

## Démarrage rapide

```bash
docker compose up --build
```

Puis :
- Frontend : http://localhost:5174
- API : http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs

Le projet utilise par défaut les données réelles de football-data.org. Copiez `.env.example` vers `.env`, renseignez `FOOTBALL_API_TOKEN` avec votre clé football-data.org, puis lancez Docker. Le mode de développement sans API reste disponible avec `MOCK_FOOTBALL_API=true`.

## Parcours critique

Accueil → Connexion → Championnat → Classement → Équipe → Ajouter aux favoris → Mes favoris → Suppression → Vérification.

## Règles métier principales

- Un utilisateur non connecté ne peut pas gérer ses favoris.
- Un utilisateur connecté peut ajouter une équipe.
- Une même équipe ne peut pas être ajoutée deux fois par utilisateur.
- Un utilisateur ne voit que ses propres favoris.
- La suppression supprime réellement la relation en base.
- Les favoris persistent après déconnexion/reconnexion.
- Un utilisateur peut avoir plusieurs favoris.
