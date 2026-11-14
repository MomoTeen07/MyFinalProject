# Support de soutenance — Football QA

| Élément | Valeur |
|---|---|
| Durée | 20 à 30 minutes + questions |
| Format | Présentation, démonstration en direct, défense des choix |
| Public | Jury de la formation Testeur QA 2026 (BStorm) |
| Application | Football QA — dépôt `MomoTeen07/MyFinalProject` |
| Date | Session de soutenance (à confirmer par le formateur) |

## 1. Trame proposée (25 minutes)

| Temps | Séquence | Message clé |
|---|---|---|
| 0–2 min | Contexte et application | Application web réelle, API REST, base PostgreSQL, rôles et règles métier |
| 2–7 min | Stratégie et analyse de risques | Approche risk-based : 10 risques notés, 6 risques critiques couverts à 100 % |
| 7–12 min | Démonstration : tests automatisés | Exécution d'une suite ciblée, rapport Allure, artefacts d'échec |
| 12–16 min | Démonstration : anomalie rejouée | ANO-001 en direct, comparaison attendu/obtenu, preuve |
| 16–20 min | Pipeline CI | Historique des exécutions vertes, jobs, artefacts publiés |
| 20–24 min | Métriques, limites, recommandations | 118 vérifications, 100 % de réussite hors xfail, 4 anomalies, risques résiduels |
| 24–25 min | Prise de recul | Ce que je ferais différemment, améliorations priorisées |
| 25–30 min | Questions | Fondamentaux ISTQB appliqués au projet |

## 2. Démonstration en direct

### 2.1 Préparation (à faire 15 minutes avant)

```bash
# 1. Application saine
docker compose up --build --detach --wait
curl http://localhost:8001/health

# 2. Dépendances installées
.venv-qa/Scripts/python.exe -m pytest --version
cd tests/playwright && npx playwright --version

# 3. Onglets ouverts
#    - http://localhost:5174 (application)
#    - http://localhost:8001/docs (API)
#    - GitHub > Actions (pipeline)
#    - docs/CAMPAIGN_REPORT.md (métriques)
```

Plan B si le réseau ou Docker est indisponible : diffuser les captures et les
artefacts Allure déjà générés (`allure-report/`, `playwright-report/`), et
rejouer l'anomalie avec la commande `curl` documentée.

### 2.2 Séquence 1 — un test UI qui passe (2 min)

```bash
cd tests/playwright
npx playwright test tests/favorites.spec.js -g "ajout, consultation" --reporter=line
```

Points à commenter :

- structure **Page Object Model** (6 pages, sélecteurs centralisés) ;
- fixture `loginAs` : compte unique créé par l'API, session injectée une seule
  fois (pas de `addInitScript`, pour pouvoir tester la déconnexion) ;
- attentes robustes : assertions auto-retentées de Playwright, pas de
  `waitForTimeout`.

### 2.3 Séquence 2 — le pipeline (2 min)

Ouvrir **GitHub → Actions → QA CI** :

- job `Backend unit checks` : 4 tests ;
- job `API and UI checks` : Docker Compose, 53 tests API, 17 tests UI, Newman ;
- artefacts : `allure-report`, `playwright-report`, `postman-report`,
  `playwright-test-results` en cas d'échec.

Message : la CI rejoue exactement la procédure locale, sur une base éphémère ;
une PR ne peut être fusionnée qu'avec une CI verte.

### 2.4 Séquence 3 — anomalie rejouée (3 min)

```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo.ano001@example.com","password":"Password123!","name":"Demo"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -i -X POST http://localhost:8001/api/favorites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"team_id":987654321,"league_code":"PL","team_name":"Ghost FC"}'
```

Commenter : attendu `422` (équipe inexistante), obtenu `201` ; le favori
apparaît dans l'interface et mène à une fiche inexistante. C'est exactement le
test `xfail(strict=True)` de la suite, visible dans Allure.

### 2.5 Séquence 4 — test d'API et rapport (2 min)

```bash
.venv-qa/Scripts/python.exe -m pytest tests/pytest/tests -q
npx --yes newman@6 run postman/Football-QA.postman_collection.json \
  -e postman/Football-QA.postman_environment.json
```

### 2.6 Séquence 5 — campagne Squash TM (1 min, si le temps le permet)

Ouvrir `http://localhost:8090/squash/project/1/campaign-workspace`
(`admin` / `admin`) et commenter :

- arborescence campagne → itération → suite → 36 cas ;
- une exécution `FAILURE` (TC-SEC-08) : statut, pas de test, commentaire
  daté renvoyant à `docs/ANOMALIES.md` ;
- rapport d'avancement : 32 `SUCCESS`, 4 `FAILURE`, 88,9 % de réussite.

Démarrage si besoin : `docker compose -f infra/squash/docker-compose.yml up -d`
puis `python infra/squash/seed_campaign.py` (procédure complète :
`docs/SQUASH.md`).

## 3. Choix techniques à défendre

| Choix | Justification | Alternative écartée |
|---|---|---|
| **Playwright** | Attentes auto-retentées, traces/vidéos intégrées, parallélisation, gratuit | Selenium : plus verbeux, gestion des attentes manuelle |
| **Page Object Model** | Sélecteurs centralisés, maintenance et lisibilité, réutilisation des fixtures | Sélecteurs dispersés dans les tests |
| **PyTest + JSON Schema** | Data-driven (`parametrize`), contrats explicites, rapports Allure | Tests codés en dur, sans contrat |
| **Postman + Newman** | Collection exigée par l'énoncé, importable, exécutable en CI | Bruno (écarté après validation du choix Postman) |
| **Allure** | Agrégation PyTest + Playwright dans un rapport unique, historique et sévérité | Rapports séparés, moins lisibles pour le jury |
| **`xfail(strict=True)`** | Un défaut connu reste visible sans bloquer la CI ; si le défaut est corrigé, le test échoue et force la mise à jour | `skip` : masquerait le défaut ; test rouge : CI inutilisable |
| **Anomalies non corrigées** | Preuve QA attendue ; l'application est le produit testé, pas le livrable | Corriger le code applicatif hors périmètre |
| **Squash TM** | Outil de gestion imposé, traçabilité exigence → cas → exécution → anomalie | JIRA/Xray : écarté par l'énoncé |
| **Mode simulé** | Budget 0 €, aucune dépendance à une clé payante, données stables | API réelle : coût et quotas |

## 4. Questions probables et réponses

### 4.1 Fondamentaux ISTQB

**Qu'est-ce qu'un test basé sur les risques ?**
On classe les risques par probabilité × impact, puis on alloue l'effort de test
en priorité aux risques les plus critiques. Ici, 10 risques notés de 1 à 9 ;
les 6 risques ≥ 6 sont couverts par des tests automatisés et manuels.

**Différence entre erreur, défaut et défaillance ?**
L'erreur est humaine (mauvaise hypothèse de validation), le défaut est sa
manifestation dans le code (`FavoriteCreate` ne vérifie pas le référentiel), la
défaillance est l'effet observable (favori « Ghost FC » créé et affiché).

**Vérification ou validation ?**
Vérification : « a-t-on construit le produit correctement ? » (contrats JSON
Schema, validation des entrées). Validation : « a-t-on construit le bon
produit ? » (parcours utilisateur, valeur métier des favoris).

**Quels critères d'entrée et de sortie ?**
Entrée : application saine, données simulées disponibles, suites installées,
commit figé. Sortie : 100 % des tests automatisés verts (hors xfail documentés),
0 échec Postman, anomalies majeures documentées et reproductibles, traçabilité
complète, CI verte.

**Qu'est-ce qu'une valeur limite ? Pourquoi 7/8/9 ?**
La limite basse du mot de passe est 8. On teste 7 (juste en dessous, doit être
refusé), 8 (limite, doit être accepté) et 9 (juste au-dessus, accepté). Cela
détecte les erreurs de comparaison `<` au lieu de `<=`.

**Différence gravité / priorité ?**
La gravité est l'impact sur le métier ; la priorité est l'ordre de correction
décidé par l'équipe. ANO-002 est de gravité moyenne (pas d'XSS constatée) mais
reste à corriger ; ANO-004 est de gravité moyenne mais de priorité haute
(risque d'usurpation).

### 4.2 Questions sur le projet

**Pourquoi seulement Chromium ?**
Coût d'exécution et budget 0 €. Playwright supporte Firefox et WebKit : les
ajouter est un changement de configuration, prévu en priorité 2.

**Comment gérez-vous les tests instables ?**
Attentes auto-retentées, timeouts explicites (7 s), 2 tentatives en CI, traces
et vidéos à l'échec pour diagnostiquer. Aucun `waitForTimeout` dans les tests.

**Pourquoi ne pas corriger les anomalies ?**
Le livrable est la démarche QA, pas une nouvelle version de l'application. Les
corriger masquerait la preuve et sortirait du périmètre validé par le formateur.

**Comment savez-vous que la couverture est suffisante ?**
Chaque exigence est tracée vers au moins un cas et un test automatisé
(`TRACEABILITY.md`), les 11 endpoints sont couverts et les 6 risques critiques
ont une couverture automatisée et manuelle.

**Comment l'API est-elle isolée entre comptes ?**
Le jeton porte l'identifiant utilisateur ; toutes les requêtes favorites
filtrent sur `user_id`. Testé côté API (liste vide, suppression 404) et côté UI
(deux contextes navigateur distincts).

**Que se passe-t-il si l'API externe tombe ?**
En local et en CI, `MOCK_FOOTBALL_API=true` : aucune dépendance réseau. En
production, le service football a un cache ; ce comportement n'est pas couvert
par la campagne (limite assumée).

### 4.3 Questions pièges

**« Votre CI est verte alors que 3 tests échouent : n'est-ce pas de la triche ? »**
Non : `xfail(strict=True)` déclare un défaut connu et attendu. Le test reste
exécuté, son échec est visible dans Allure avec la référence ANO-xxx, et si le
défaut est corrigé le test devient rouge (`XPASS` strict) pour forcer la mise à
jour. La CI mesure la non-régression, pas l'absence de défauts.

**« Pourquoi 4 anomalies seulement ? »**
Le périmètre est volontairement ciblé sur les risques critiques. La densité
(0,11 anomalie par cas) est cohérente avec une application simple ; l'énoncé
précise que la qualité de la démarche prime sur le volume.

**« Quelle est votre plus grande faiblesse ? »**
La couverture mono-navigateur et l'absence de tests de performance. Elles sont
documentées avec un plan d'action chiffré.

## 5. Limites et prise de recul

| Limite | Conséquence | Amélioration |
|---|---|---|
| Chromium uniquement | Régressions spécifiques Firefox/Safari non détectées | Ajouter 2 projets Playwright en CI |
| Pas de tests de charge | Capacité inconnue | k6 ou Locust sur environnement dédié |
| API football simulée | Contrat externe non vérifié | Test de contrat consommateur |
| Pas d'accessibilité normée | Conformité WCAG non prouvée | axe-core + audit manuel |
| Session exploratoire unique | Couverture des cas imprévus limitée | Sessions exploratoires par itération |
| Historique Git initial | Traçabilité des premiers commits faible | Convention Conventional Commits depuis le début de la campagne |

## 6. Checklist de démonstration

- [ ] Application démarrée, `health` à 200, 3 conteneurs *healthy*
- [ ] Compte de démonstration créé (ou commande d'inscription prête)
- [ ] Terminal à la racine du dépôt, environnement virtuel actif
- [ ] Onglet navigateur sur l'application et sur `/docs`
- [ ] Onglet GitHub Actions sur le dernier run vert
- [ ] `docs/CAMPAIGN_REPORT.md` ouvert sur les métriques
- [ ] Squash TM ouvert sur la campagne (32/4) ou prêt à démarrer
- [ ] Commande ANO-001 copiée dans le presse-papiers
- [ ] Rapport Allure généré en local (secours hors ligne)
- [ ] Chronomètre : répétition complète en moins de 20 minutes
