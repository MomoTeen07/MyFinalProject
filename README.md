# Football QA

Application web de consultation du football, conçue comme support d’un projet final QA.

## Stack

- Frontend : React, Vite et CSS
- Backend : Python et FastAPI
- Authentification : JWT
- Base de données : PostgreSQL
- Données de football : football-data.org ou données simulées
- Conteneurs : Docker Compose
- Tests disponibles : PyTest et Playwright

## Démarrage avec Docker

1. Copiez `.env.example` vers `.env`.
2. Remplacez `JWT_SECRET` par une valeur aléatoire d’au moins 32 caractères. Ne réutilisez pas la valeur d’exemple.
3. Ajoutez un `FOOTBALL_API_TOKEN` valide pour utiliser les données réelles, ou gardez `MOCK_FOOTBALL_API=true` pour le mode simulé.
4. À la racine du projet, lancez :

   ```bash
   docker compose up --build
   ```

Puis ouvrez :

- Application : <http://localhost:5174>
- API : <http://localhost:8001>
- Documentation Swagger : <http://localhost:8001/docs>

Le frontend transmet les appels `/api` au backend via Nginx. En développement Vite, ces appels sont transmis à `http://localhost:8001`.

## Développement du frontend

Dans `frontend/` :

```bash
npm install
npm run dev
```

## Parcours critique

Accueil → Connexion → Championnat → Classement → Équipe → Ajouter aux favoris → Mes favoris → Suppression → Vérification.

## Règles métier principales

- Un utilisateur non connecté ne peut pas gérer ses favoris.
- Un utilisateur connecté peut ajouter une équipe.
- Une équipe ne peut pas être ajoutée deux fois par utilisateur.
- Un utilisateur ne voit que ses favoris.
- La suppression retire réellement la relation de la base.
- Les favoris persistent après déconnexion et reconnexion.
- Un utilisateur peut avoir plusieurs favoris.

## Configuration de sécurité

Le secret JWT doit être unique et privé. La valeur d’exemple est refusée par le backend. Les identifiants PostgreSQL fournis par défaut dans Compose sont destinés au développement local ; remplacez-les avant toute exposition du service.
