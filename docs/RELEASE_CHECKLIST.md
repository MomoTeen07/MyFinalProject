# Définition de « terminé »

Une version n'est pas terminée parce que le code est écrit. Elle l'est quand tout ce qui suit
est vrai. À passer avant chaque tag.

## Code et CI

- [x] `main` est vert sur la dernière exécution
- [x] Aucune branche de travail non fusionnée ne contient de correctif attendu
- [x] `docker compose up --build` démarre l'application sans intervention manuelle
- [x] Aucun secret, jeton ou identifiant réel dans le dépôt (`git grep` sur les motifs usuels)

## Tests

- [x] Les tests backend passent : 19/19
- [x] La suite de contrat API passe sur l'application démarrée : 100 passés + 4 `xfail`
- [x] La suite Playwright passe sur le navigateur configuré (Chromium) : 27/27
- [x] La collection Postman/Newman passe : 31 requêtes, 76 assertions, 0 échec
- [x] Chaque anomalie connue est couverte par un test `xfail(strict=True)` ou une vérification manuelle et référencée dans `docs/ANOMALIES.md`

## Campagne

- [x] Tous les cas de la version sont exécutés (59 cas, attendu / obtenu / statut renseignés)
- [x] La matrice de traçabilité ne contient aucune exigence orpheline (25/25)
- [x] `docs/CAMPAIGN_REPORT.md` contient les métriques de la version (59 cas, 222 passants + 4 `xfail`, 5 anomalies)
- [x] Les anomalies sont classées par gravité et priorité, avec reproduction et preuve
- [x] Campagne Squash TM finale : 25 exigences, 59 cas, 54 `SUCCESS` / 5 `FAILURE`

## Documentation

- [x] `README.md` reflète l'état réel, y compris ce qui n'est pas fait
- [x] `docs/ROADMAP.md` est à jour (V3 clôturée, jalon suivant identifié)
- [x] `CHANGELOG.md` contient l'entrée datée de la version

## Publication

- [ ] Tag de clôture créé après fusion de la PR (`v3.1-campagne-finale`)
- [ ] Notes de release rédigées : périmètre, chiffres, anomalies connues, limites
- [x] La campagne est close : la release peut être marquée **latest** et non *pre-release*
