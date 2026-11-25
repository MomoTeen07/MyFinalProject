# Rapport de campagne — Football QA

| Élément | Valeur |
|---|---|
| Campagne | **Campagne finale V3** (V1 + V2 + V3) |
| Version testée | V3 — commit `3ba1ec9` (tag `v3.0`) ; HEAD documentaire `59ce997` |
| Période | 13/11/2026 (V1), 22/11/2026 (V2), 25/11/2026 (V3) |
| Testeur | Mohamed Abdo |
| Environnement | Docker local : API `:8001`, UI `:5174`, PostgreSQL 16. V1 en mode simulé ; V2/V3 en **données réelles** |
| Outils | PyTest, Playwright (POM), Postman/Newman, Allure, GitHub Actions, Squash TM |
| Statut | **Campagne conforme aux critères de sortie**, 5 anomalies ouvertes documentées |

## 1. Résumé exécutif

La campagne finale couvre la version réellement livrée, la **V3** : accueil avec
prochains matchs, fiche équipe enrichie, tableau de bord des favoris, détail de
match et confrontations directes. Elle consolide la campagne V1 (36 cas, mode
simulé), la campagne V2 (14 cas, données réelles) et la campagne V3 (9 cas,
données réelles), soit **59 cas manuels** et **222 vérifications automatisées
passantes + 4 `xfail`**.

**Aucun test automatisé n'échoue** : 222 vérifications passent, 4 sont marquées
`xfail(strict=True)` car elles révèlent des défauts réels et reproductibles.
Cinq anomalies sont ouvertes, dont **deux majeures** : l'acceptation d'une
équipe inexistante en favori (ANO-001) et un point de santé qui masque
l'indisponibilité de la base (ANO-003). Aucune anomalie bloquante n'a été
relevée sur le parcours critique : ajouter, consulter et supprimer un favori
fonctionne de bout en bout, y compris après redémarrage.

Le pipeline GitHub Actions est vert sur `main` et publie un rapport Allure
agrégé (API + UI), un rapport Playwright et, en cas d'échec, les traces et
vidéos. Les résultats Allure du backend sont publiés dans un artefact séparé.

La campagne finale est également organisée dans **Squash TM 15.0.3** :
**25 exigences**, **59 cas de test** avec pas et couvertures, une campagne, une
itération, une suite et **59 exécutions** (**54 `SUCCESS`**, **5 `FAILURE`**
pour ANO-001 à ANO-005). La procédure de démarrage, de création et de
vérification est décrite dans [`docs/SQUASH.md`](SQUASH.md).

## 2. Historique des campagnes

| Campagne | Date | Données | Cas manuels | Conformes | Anomalies | Vérifications automatisées |
|---|---|---|---:|---:|---|---|
| V1 | 13/11/2026 | Simulé | 36 | 32 (88,9 %) | ANO-001 à ANO-004 | 118 (4 backend, 56 API, 17 UI, 41 assertions Postman) |
| V2 | 22/11/2026 | Réel | 14 | 14 (100 %) | — | 10 backend, 78 + 4 `xfail` API, 25 UI, 69 assertions Postman |
| V3 | 25/11/2026 | Réel | 9 | 8 (88,9 %) | ANO-005 | 19 backend, 100 + 4 `xfail` API, 27 UI, 76 assertions Postman |
| **Final** | **25/11/2026** | **Réel (V2/V3)** | **59** | **54 (91,5 %)** | **5** | **222 passants + 4 `xfail`** |

La V3 est volontairement couverte par **9 cas manuels choisis par les risques**
(prochains matchs, fiche équipe, tableau de bord des favoris, détail de match,
responsive et non-régression en données réelles). Le reste du périmètre est
couvert par les suites automatisées, rejouées à chaque pipeline. Ce dosage est
assumé : l'énoncé demande des choix pertinents, pas de tout tester.

## 3. Métriques d'exécution

### 3.1 Suites automatisées — état final V3

| Suite | Exécutés | Réussis | Échecs | xfail | Taux de réussite |
|---|---:|---:|---:|---:|---:|
| Backend (PyTest) | 19 | 19 | 0 | 0 | 100 % |
| API (PyTest) | 104 | 100 | 0 | 4 | 100 % (hors xfail) |
| UI (Playwright, 2 workers) | 27 | 27 | 0 | 0 | 100 % |
| Postman (Newman) | 76 assertions | 76 | 0 | 0 | 100 % |
| **Total** | **226** | **222** | **0** | **4** | **100 % (hors xfail)** |

Le taux de réussite est calculé hors `xfail` : un `xfail` strict qui passe
deviendrait un échec, ce qui garantit que ces tests restent représentatifs des
défauts constatés.

### 3.2 Cas manuels — consolidation

| Campagne | Domaine | Cas | Réussis | Anomalies |
|---|---|---|---:|---|
| V1 | Authentification | 11 | 11 | 0 |
| V1 | Football | 6 | 6 | 0 |
| V1 | Favoris | 9 | 9 | 0 |
| V1 | Sécurité / robustesse | 10 | 6 | 4 (ANO-001 à ANO-004) |
| V2 | Buteurs, actualités, presse, détail de match | 14 | 14 | 0 |
| V3 | Prochains matchs, fiche équipe, favoris, match, responsive | 8 | 8 | 0 |
| V3 | Non-régression en données réelles | 1 | 0 | 1 (ANO-005) |
| **Total** | | **59** | **54 (91,5 %)** | **5 anomalies distinctes** |

### 3.3 Couverture

| Indicateur | Valeur |
|---|---|
| Endpoints API couverts | 18 / 18 (100 %) |
| Exigences tracées et couvertes | 25 / 25 (100 %) |
| Risques de criticité ≥ 6 couverts | 6 / 6 (100 %) |
| Parcours critique UI couvert | 1 / 1 (100 %) |
| Navigateurs | 1 / 3 (Chromium uniquement) |
| Champs de formulaire avec validation testée | 6 / 6 |
| Cas manuels exécutés | 59 / 59 (100 %) |

## 4. Bilan des anomalies

| ID | Titre | Gravité | Priorité | Impact | Décision |
|---|---|---|---|---|---|
| ANO-001 | Équipe inexistante acceptée en favori | Majeure | Haute | Données incohérentes, liens morts | À corriger avant mise en production |
| ANO-002 | `team_crest` sans restriction de schéma | Moyenne | Moyenne | Hygiène de sécurité, pas d'XSS constatée (`<img src>`) | À corriger au prochain cycle |
| ANO-003 | `/health` mensonger base arrêtée | Majeure | Haute | Panne non détectée par la supervision et la CI | À corriger avant mise en production |
| ANO-004 | Pas de limitation des tentatives de connexion | Moyenne | Haute | Force brute facilitée | À corriger au prochain cycle |
| ANO-005 | Équipe inconnue traduite en 502 au lieu de 404 en données réelles | Moyenne | Moyenne | Contrat d'erreur incorrect, supervision bruitée | À corriger au prochain cycle |

Détail, preuves et procédures de reproduction : `docs/ANOMALIES.md`.

### 4.1 Répartition par gravité

| Gravité | Nombre | Part |
|---|---:|---:|
| Bloquante | 0 | 0 % |
| Majeure | 2 | 40 % |
| Moyenne | 3 | 60 % |
| Mineure | 0 | 0 % |

### 4.2 Densité et efficacité

- **5 anomalies** pour **59 cas manuels**, soit une densité de 0,085 anomalie
  par cas.
- **4 anomalies sur 5** sont détectées par des tests automatisés rejouables
  (`xfail` strict) : ANO-001, ANO-002, ANO-004 et ANO-005. ANO-003 est vérifiée
  manuellement en arrêtant la base.
- **0 anomalie bloquante** : le parcours critique reste utilisable.
- La campagne V3 a confirmé ANO-005 en données réelles via TC-V3-09.

## 5. Analyse des risques résiduels

| Risque résiduel | Niveau | Justification | Mesure d'atténuation |
|---|---|---|---|
| Favoris incohérents (ANO-001) | **Élevé** | Aucun contrôle référentiel ; un client peut créer des données fausses | Corriger avant production ; sinon purge périodique des favoris orphelins |
| Panne de base non détectée (ANO-003) | **Élevé** | La supervision et `docker compose --wait` font confiance à `/health` | Ajouter un contrôle `SELECT 1` et une sonde de liveness distincte |
| Force brute sur la connexion (ANO-004) | Moyen | Aucun quota ; dépend de la robustesse des mots de passe | Limitation par IP et par compte, MFA à terme |
| Écusson non validé (ANO-002) | Faible | Pas d'exécution constatée, contexte `<img>` | Validation d'URL avant réutilisation dans un autre contexte |
| Mapping d'erreurs fournisseur (ANO-005) | Faible | Un `400` du fournisseur devient `502` au lieu de `404` | Traduire les codes du fournisseur avant de les relayer |
| Dépendance au fournisseur réel | Moyen | Quota 10 req/min, latence et 5xx transitoires ; V2/V3 exécutées en réel | Cache 900 s en CI, reprise bornée, repli simulé disponible |
| Couverture mono-navigateur | Moyen | Chromium seulement ; Safari/Firefox non vérifiés | Ajouter les projets Playwright Firefox/WebKit en CI |
| Absence de tests de charge | Moyen | Aucun profil de performance validé | Test de montée en charge k6/Locust sur un environnement dédié |
| Contexte V3 dégradé | Faible | Les appels de contexte sont absorbés ; une carte reste affichable sans classement ni match | Tests déjà en place ; surveiller les erreurs fournisseur |
| Campagne V3 limitée à 9 cas | Faible | Choix risk-based ; le reste est couvert par 222 vérifications automatisées | Rejouer les cas V3 à chaque changement de contrat fournisseur |

## 6. Recommandations

### 6.1 Priorité 1 — avant toute mise en production

1. **Corriger ANO-003** : `/health` doit interroger la base et renvoyer `503`
   en cas d'échec. Impact direct sur la supervision et l'orchestration.
2. **Corriger ANO-001** : valider l'existence de l'équipe avant l'insertion du
   favori, avec un test de non-régression qui passera de `xfail` à `pass`.
3. **Corriger ANO-004** : limiter les tentatives de connexion (5 échecs /
   15 min) et journaliser les échecs.

### 6.2 Priorité 2 — prochain cycle

4. **Corriger ANO-002** : restreindre `team_crest` aux schémas `http`/`https`.
5. **Corriger ANO-005** : traduire les codes du fournisseur (`400`/`404` → `404`,
   `401`/`403` → `502`, `5xx` → `502`) et conserver le `503` pour `429`.
6. **Étendre la CI** : projets Playwright Firefox et WebKit, publication du
   rapport Allure sur GitHub Pages (gratuit pour un dépôt public).
7. **Compléter la couverture manuelle** : cas sur les erreurs réseau
   (timeout, 500) et sur les limites de pagination si le référentiel grandit.

### 6.3 Priorité 3 — industrialisation

8. Ajouter un **test de contrat consommateur** avec l'API football-data.org
   (schéma OpenAPI ou Pact) pour anticiper les ruptures de contrat.
9. Mettre en place un **environnement de recette** éphémère par branche
   (Docker Compose + runner GitHub) afin de tester avant fusion.
10. Ajouter un **contrôle d'accessibilité automatisé** (axe-core) sur les pages
    principales.
11. **Nettoyer l'historique Git** : les commits antérieurs au projet QA
    (« BASE CORRECT », « Correction de code ») ne respectent pas la convention
    Conventional Commits appliquée depuis le début de la campagne.

## 7. Conclusion

La campagne finale V3 atteint ses critères de sortie : suites automatisées
vertes, campagne manuelle exécutée sur la version livrée, traçabilité complète,
anomalies documentées et reproductibles, pipeline visible et campagne Squash
alignée.

La démarche a permis de détecter cinq défauts réels, dont deux majeurs, sur une
application volontairement non modifiée. Les principales limites sont la
couverture mono-navigateur, l'absence de tests de performance et le nombre
volontairement réduit de cas manuels V3. Elles sont assumées dans le cadre d'un
budget 0 € et d'une approche basée sur les risques. Les anomalies ouvertes
constituent une preuve de la valeur du travail QA et un support direct pour la
démonstration de soutenance.
