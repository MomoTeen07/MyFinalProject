# Architecture

## Responsibilities

The React frontend presents football data and handles user actions. FastAPI owns authentication, authorization, and business rules. PostgreSQL stores accounts and favorites. The football service fetches competition data from the configured provider or returns local mock data.

Nginx serves the compiled frontend and forwards `/api` requests to FastAPI. During local Vite development, Vite forwards the same paths to the backend. This keeps the browser on one origin and avoids hard-coded API hostnames in the application code.

## Database changes

Alembic owns schema changes. The first revision adopts the tables created by earlier versions of the application when they already exist, so accounts and favorites are retained. Future model changes should be represented by reviewed Alembic revisions.

## Authentication and favorites

Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes. New hashes use 600,000 iterations; existing hashes are upgraded after a successful login. JWT secrets come from environment configuration.

The database uniqueness constraint on `(user_id, team_id)` prevents duplicate favorites under concurrent requests. Favorite reads, inserts, and deletes require authentication and are scoped to the authenticated user.
