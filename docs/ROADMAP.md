# Feuille de route

État au **25/11/2026**. Ce document existe pour une raison simple : un projet sans définition
de « terminé » ne se termine jamais.

## Où en est le projet

| Version | Fonctionnalités | Campagne de test |
| --- | --- | --- |
| **V1** | Parcours visiteur et authentifié, favoris, 11 endpoints | **Terminée** — 36 cas, 118 vérifications, 4 anomalies (tag `v1.0-campagne-v1`) |
| **V2** | Buteurs/passeurs, actualités, presse, détail de match, pagination — 15 endpoints | **Terminée** — 14 cas, vérifications automatisées en données réelles |
| **V3** | Prochains matchs, fiche équipe enrichie, tableau de bord favoris, confrontations — 18 endpoints | **Terminée** — 9 cas, 222 vérifications passantes + 4 `xfail`, 5 anomalies |

Les fonctionnalités V3 sont fusionnées dans `main` et la campagne finale est close.

## Jalon V3 — clôturé

- [x] Exécuter la campagne manuelle V3 (9 cas) et consigner attendu / obtenu / statut dans `docs/TEST_CASES.md`
- [x] Mettre à jour `docs/CAMPAIGN_REPORT.md` avec les métriques V3
- [x] Vérifier la traçabilité V3 dans `docs/TRACEABILITY.md` (25 exigences, 18 endpoints)
- [x] Passer la checklist [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)
- [ ] Créer le tag de clôture après fusion de la PR de campagne

> Le tag `v3.0` marque la version de code ; il a été créé **avant** la campagne.
> Le tag de clôture doit être créé après fusion de la PR finale, par exemple
> `v3.1-campagne-finale`.

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
