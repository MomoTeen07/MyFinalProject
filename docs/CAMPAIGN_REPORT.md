# Rapport de campagne — Football QA

| Élément | Valeur |
|---|---|
| Campagne | Campagne V1 |
| Version testée | commit `a0ea6e6` (`main`), API 1.0.0 |
| Période | 13/11/2026 |
| Testeur | Mohamed Abdo |
| Environnement | Docker local : API `:8001`, UI `:5174`, PostgreSQL 16. Campagne manuelle V1 en mode simulé ; suites automatisées rejouées en **données réelles** le 21/11/2026 |
| Outils | PyTest, Playwright (POM), Postman/Newman, Allure, GitHub Actions, Squash TM |
| Statut | **Campagne conforme aux critères de sortie**, 5 anomalies ouvertes documentées |

## 1. Résumé exécutif

La campagne V1 a couvert l'ensemble du périmètre défini dans le plan de test :
authentification, consultation football, gestion des favoris, sécurité des
jetons et supervision. **118 vérifications automatisées** ont été exécutées
(4 backend, 56 API, 17 UI, 41 assertions Postman) et **36 cas manuels**.
**Aucun test automatisé n'échoue** : 114 passent, 4 sont marqués `xfail` car ils
révèlent des défauts réels et reproductibles. Depuis le 21/11/2026, les suites
automatisées s'exécutent sur les **données réelles** du fournisseur, sans
assertion figée sur le référentiel simulé.

Cinq anomalies ont été identifiées, dont **deux majeures** : l'acceptation
d'une équipe inexistante en favori (ANO-001) et un point de santé qui masque
l'indisponibilité de la base (ANO-003). Aucune anomalie bloquante n'a été
relevée sur le parcours critique : ajouter, consulter et supprimer un favori
fonctionne de bout en bout, y compris après redémarrage.

Le pipeline GitHub Actions est vert sur `main` et publie un rapport Allure
agrégé (backend, API, UI), un rapport Playwright et, en cas d'échec, les traces
et vidéos.

La campagne est également organisée dans **Squash TM 15.0.3** : 16 exigences,
36 cas de test avec pas et couvertures, une campagne, une itération, une suite
et 36 exécutions (**32 `SUCCESS`**, **4 `FAILURE`** pour ANO-001 à ANO-004).
ANO-005, détectée en données réelles, est couverte par la suite automatisée et
n'est pas encore reportée dans la campagne Squash.
La procédure de démarrage, de création et de vérification est décrite dans
[`docs/SQUASH.md`](SQUASH.md).

## 2. Métriques d'exécution

### 2.1 Suites automatisées

| Suite | Exécutés | Réussis | Échecs | xfail | Durée | Taux de réussite |
|---|---|---|---|---|---|---|
| Backend (PyTest) | 4 | 4 | 0 | 0 | 3,3 s | 100 % |
| API (PyTest) | 56 | 52 | 0 | 4 | 125 s | 100 % (hors xfail) |
| UI (Playwright, 2 workers) | 17 | 17 | 0 | 0 | 27 s | 100 % |
| Postman (Newman) | 41 assertions | 41 | 0 | 0 | 2,4 s | 100 % |
| **Total** | **118 vérifications** | **114** | **0** | **4** | **≈ 2 min 40** | **100 %** |

Le taux de réussite est calculé hors `xfail` : un `xfail` strict qui passe
deviendrait un échec, ce qui garantit que ces tests restent représentatifs des
défauts constatés.

### 2.2 Cas manuels

| Domaine | Cas | Réussis | Anomalies |
|---|---|---|---|
| Authentification | 11 | 11 | 0 |
| Football | 6 | 6 | 0 |
| Favoris | 9 | 9 | 0 |
| Sécurité / robustesse | 10 | 6 | 4 |
| **Total** | **36** | **32 (88,9 %)** | **4 cas → 4 anomalies** |

### 2.3 Couverture

| Indicateur | Valeur |
|---|---|
| Endpoints API couverts | 11 / 11 (100 %) |
| Exigences tracées et couvertes | 16 / 16 (100 %) |
| Risques de criticité ≥ 6 couverts | 6 / 6 (100 %) |
| Parcours critique UI couvert | 1 / 1 (100 %) |
| Navigateurs | 1 / 3 (Chromium uniquement) |
| Champs de formulaire avec validation testée | 6 / 6 |

## 3. Bilan des anomalies

| ID | Titre | Gravité | Priorité | Impact | Décision |
|---|---|---|---|---|---|
| ANO-001 | Équipe inexistante acceptée en favori | Majeure | Haute | Données incohérentes, liens morts | À corriger avant mise en production |
| ANO-002 | `team_crest` sans restriction de schéma | Moyenne | Moyenne | Hygiène de sécurité, pas d'XSS constatée (`<img src>`) | À corriger au prochain cycle |
| ANO-003 | `/health` mensonger base arrêtée | Majeure | Haute | Panne non détectée par la supervision et la CI | À corriger avant mise en production |
| ANO-004 | Pas de limitation des tentatives de connexion | Moyenne | Haute | Force brute facilitée | À corriger au prochain cycle |

Détail, preuves et procédures de reproduction : `docs/ANOMALIES.md`.

### 3.1 Répartition par gravité

| Gravité | Nombre | Part |
|---|---|---|
| Bloquante | 0 | 0 % |
| Majeure | 2 | 50 % |
| Moyenne | 2 | 50 % |
| Mineure | 0 | 0 % |

### 3.2 Densité et efficacité

- **4 anomalies** pour **36 cas manuels**, soit une densité de 0,11 anomalie
  par cas.
- **3 anomalies sur 4** sont détectées par des tests automatisés rejouables
  (`xfail` strict), donc protégées contre toute régression silencieuse.
- **0 anomalie bloquante** : le parcours critique reste utilisable.

## 4. Analyse des risques résiduels

| Risque résiduel | Niveau | Justification | Mesure d'atténuation |
|---|---|---|---|
| Favoris incohérents (ANO-001) | **Élevé** | Aucun contrôle référentiel ; un client peut créer des données fausses | Corriger avant production ; sinon purge périodique des favoris orphelins |
| Panne de base non détectée (ANO-003) | **Élevé** | La supervision et `docker compose --wait` font confiance à `/health` | Ajouter un contrôle `SELECT 1` et une sonde de liveness distincte |
| Force brute sur la connexion (ANO-004) | Moyen | Aucun quota ; dépend de la robustesse des mots de passe | Limitation par IP et par compte, MFA à terme |
| Écusson non validé (ANO-002) | Faible | Pas d'exécution constatée, contexte `<img>` | Validation d'URL avant réutilisation dans un autre contexte |
| Couverture mono-navigateur | Moyen | Chromium seulement ; Safari/Firefox non vérifiés | Ajouter les projets Playwright Firefox/WebKit en CI (coût : temps de calcul) |
| Absence de tests de charge | Moyen | Aucun profil de performance validé | Test de montée en charge k6/Locust sur un environnement dédié |
| Mapping d'erreurs fournisseur (ANO-005) | Faible | Un `400` du fournisseur devient `502` au lieu de `404` | Traduire les codes du fournisseur avant de les relayer |
| Dépendance au fournisseur réel | Moyen | Quota 10 req/min, latence et 5xx transitoires ; suites automatisées exécutées en réel depuis le 21/11/2026 | Cache 900 s en CI, reprise bornée, repli simulé disponible |
| Tests UI dépendants d'un backend réel | Faible | Les fixtures créent des comptes via l'API et lisent l'oracle réel | Comptes uniques et oracle API (déjà en place) |

## 5. Recommandations

### 5.1 Priorité 1 — avant toute mise en production

1. **Corriger ANO-003** : `/health` doit interroger la base et renvoyer `503`
   en cas d'échec. Impact direct sur la supervision et l'orchestration.
2. **Corriger ANO-001** : valider l'existence de l'équipe avant l'insertion du
   favori, avec un test de non-régression qui passera de `xfail` à `pass`.
3. **Corriger ANO-004** : limiter les tentatives de connexion (5 échecs /
   15 min) et journaliser les échecs.

### 5.2 Priorité 2 — prochain cycle

4. **Corriger ANO-002** : restreindre `team_crest` aux schémas `http`/`https`.
5. **Étendre la CI** : projets Playwright Firefox et WebKit, publication du
   rapport Allure sur GitHub Pages (gratuit pour un dépôt public).
6. **Compléter la couverture manuelle** : cas de test sur les erreurs réseau
   (timeout, 500) et sur les limites de pagination si le référentiel grandit.

### 5.3 Priorité 3 — industrialisation

7. Ajouter un **test de contrat consommateur** avec l'API football-data.org
   (schéma OpenAPI ou Pact) pour anticiper les ruptures de contrat.
8. Mettre en place un **environnement de recette** éphémère par branche
   (Docker Compose + runner GitHub) afin de tester avant fusion.
9. Ajouter un **contrôle d'accessibilité automatisé** (axe-core) sur les pages
   principales.
10. **Nettoyer l'historique Git** : les commits antérieurs au projet QA
    (« BASE CORRECT », « Correction de code ») ne respectent pas la convention
    Conventional Commits appliquée depuis le début de la campagne.

## 6. Conclusion

La campagne V1 atteint ses critères de sortie : suites automatisées vertes,
traçabilité complète, anomalies documentées et reproductibles, pipeline
visible. La démarche a permis de détecter quatre défauts réels, dont deux
majeurs, sur une application volontairement non modifiée.

La principale limite est la couverture mono-navigateur et l'absence de tests de
performance, assumées dans le cadre d'un budget 0 €. Les anomalies ouvertes
constituent une preuve de la valeur du travail QA et un support direct pour la
démonstration de soutenance.
