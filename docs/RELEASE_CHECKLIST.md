# Définition de « terminé »

Une version n'est pas terminée parce que le code est écrit. Elle l'est quand tout ce qui suit
est vrai. À passer avant chaque tag.

## Code et CI

- [ ] `main` est vert sur la dernière exécution
- [ ] Aucune branche de travail non fusionnée ne contient de correctif attendu
- [ ] `docker compose up --build` démarre l'application sans intervention manuelle
- [ ] Aucun secret, jeton ou identifiant réel dans le dépôt (`git grep` sur les motifs usuels)

## Tests

- [ ] Les tests backend passent : `python -m pytest tests` (dans `backend/`)
- [ ] La suite de contrat API passe sur l'application démarrée
- [ ] La suite Playwright passe sur les 3 navigateurs configurés
- [ ] La collection Postman/Newman passe
- [ ] Chaque anomalie connue est couverte par un test `xfail(strict=True)` et référencée dans `docs/ANOMALIES.md`

## Campagne

- [ ] Tous les cas de la version sont exécutés (attendu / obtenu / statut renseignés)
- [ ] La matrice de traçabilité ne contient aucune exigence orpheline
- [ ] `docs/CAMPAIGN_REPORT.md` contient les métriques de la version (cas, vérifications, anomalies)
- [ ] Les anomalies sont classées par gravité et priorité, avec reproduction et preuve

## Documentation

- [ ] `README.md` reflète l'état réel, y compris ce qui n'est pas fait
- [ ] `docs/ROADMAP.md` est à jour (cases cochées, jalon suivant identifié)
- [ ] `CHANGELOG.md` contient l'entrée datée de la version

## Publication

- [ ] Tag créé au format `v<version>`
- [ ] Notes de release rédigées : périmètre, chiffres, anomalies connues, limites
- [ ] Release marquée **pre-release** tant que la campagne n'est pas close
