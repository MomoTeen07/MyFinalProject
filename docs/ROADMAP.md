# Feuille de route

État au **25/11/2026**. Ce document existe pour une raison simple : un projet sans définition
de « terminé » ne se termine jamais.

## Où en est le projet

| Version | Fonctionnalités | Campagne de test |
| --- | --- | --- |
| **V1** | Parcours visiteur et authentifié, favoris, 11 endpoints | **Terminée** — 36 cas, 118 vérifications, 5 anomalies (tag `v1.0-campagne-v1`) |
| **V2** | Buteurs/passeurs, actualités, presse, détail de match, pagination — 15 endpoints | Vérifications automatisées rejouées en données réelles |
| **V3** | Prochains matchs, fiche équipe enrichie, tableau de bord favoris, confrontations — 18 endpoints | **Non démarrée** (campagne manuelle) |

Les fonctionnalités V3 sont fusionnées dans `main`. Ce qui manque n'est pas du code : c'est
**la validation**.

## Prochain jalon — clôturer V3

- [ ] Exécuter la campagne manuelle V3 (50 cas) et consigner attendu / obtenu / statut dans `docs/TEST_CASES.md`
- [ ] Mettre à jour `docs/CAMPAIGN_REPORT.md` avec les métriques V3
- [ ] Vérifier la traçabilité V3 dans `docs/TRACEABILITY.md`
- [ ] Passer la checklist [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)
- [ ] Créer le tag de fin de V3

> Le tag `v3.0` a été créé **avant** la campagne : ne pas publier de release dessus avant la clôture.

## Points ouverts (indépendants de V3)

- [ ] Publier le rapport Allure sur GitHub Pages et lier le rapport depuis le README
- [ ] Ajouter une capture d'écran de l'application dans le README
- [ ] Mesurer la couverture de `backend/` et l'afficher (badge)

## Après la clôture — et seulement après

Ces sujets ne sont volontairement pas ouverts maintenant : ajouter du périmètre avant d'avoir
fermé V3 reviendrait à empiler des chantiers.

- [ ] Tests de performance (k6 ou Locust) sur le parcours de consultation
- [ ] Tests d'accessibilité (`@axe-core/playwright`) sur les pages principales

## Explicitement hors périmètre

- **Corriger les anomalies** : elles sont la matière de la campagne et sont rejouées par des `xfail` stricts.
- **Refondre les suites existantes** : elles fonctionnent et sont vertes ; un refactor pendant une
  phase active crée plus de risque que de valeur.
