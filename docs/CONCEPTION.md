# Conception

## Responsabilités

Le frontend React présente les données et déclenche les actions utilisateur. FastAPI porte l'authentification, les autorisations et les règles métier. PostgreSQL conserve les utilisateurs et les favoris. Le service football récupère les données sportives depuis l'API externe configurée.

## Favoris

La contrainte unique `(user_id, team_id)` garantit l'absence de doublon même en cas de requêtes concurrentes. Toutes les lectures et suppressions de favoris filtrent par `user_id` afin d'empêcher l'accès à ceux d'un autre utilisateur.
