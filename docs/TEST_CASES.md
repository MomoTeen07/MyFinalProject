# Cas de test et résultats d'exécution

| Élément | Valeur |
|---|---|
| Campagne | Campagne V1 (36 cas) + V2 en cours (4 buteurs + 4 actualités + 3 presse + 3 match) |
| Date d'exécution | 13/11/2026 (V1) — 22/11/2026 (V2) |
| Environnement | Docker local, API `:8001`, UI `:5174`. V1 : mode simulé. V2 : données réelles |
| Commit testé | V1 : `a0ea6e6` (`main`) — V2 : branche `app/v2` |
| Exécutant | Mohamed Abdo |
| Nombre de cas | 50 cas formels (36 V1 + 14 V2) + 1 session exploratoire |

Les cas sont conçus avec des techniques explicites : **partitions
d'équivalence** (PE), **valeurs limites** (VL), **table de décision** (TD),
**tests exploratoires** (EX) et **vérification de contrat** (CT). Le statut
`Passé` signifie que le résultat obtenu correspond au résultat attendu ;
`Anomalie` renvoie au rapport correspondant dans `docs/ANOMALIES.md`.

## 1. Authentification

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-AUTH-01 | Inscription valide (mot de passe de 8 caractères) | VL (limite basse) | Ouvrir `/register`, saisir nom « QA User », e-mail neuf, mot de passe `Passw0rd` (8 car.), valider | 201, jeton renvoyé, redirection vers `/championships`, nom affiché dans la barre | 201, jeton, redirection, nom affiché | Passé (automatisé UI + API) |
| TC-AUTH-02 | Inscription avec un e-mail déjà utilisé | PE (invalide) | Inscrire deux fois la même adresse, la seconde en majuscules | 409 « Un compte existe déjà avec cette adresse e-mail. » | 409, message conforme (comparaison insensible à la casse) | Passé |
| TC-AUTH-03 | Inscription avec un e-mail invalide | PE (invalide) | `not-an-email` dans le champ e-mail | 422, champ `email` en erreur | 422, champ `email` en erreur | Passé |
| TC-AUTH-04 | Mot de passe de 7 caractères | VL (8 − 1) | Mot de passe `Passw0r` | 422, champ `password` en erreur | 422 | Passé |
| TC-AUTH-05 | Mot de passe de 129 caractères | VL (128 + 1) | Mot de passe de 129 caractères | 422, champ `password` en erreur | 422 | Passé |
| TC-AUTH-06 | Nom d'un caractère | VL (2 − 1) | Nom `A` | 422, champ `name` en erreur | 422 | Passé |
| TC-AUTH-07 | Nom de 2 caractères | VL (limite basse) | Nom `Al` | 201 | 201 | Passé |
| TC-AUTH-08 | Nom de 101 caractères | VL (100 + 1) | Nom de 101 caractères | 422, champ `name` en erreur | 422 | Passé |
| TC-AUTH-09 | Connexion valide | PE (valide) | Compte existant, mot de passe correct | 200, jeton, accès aux favoris | 200, jeton, session UI persistante | Passé (automatisé UI + API + Postman) |
| TC-AUTH-10 | Connexion avec un mauvais mot de passe | PE (invalide) | E-mail connu, mot de passe erroné | 401, message générique | 401 « Adresse e-mail ou mot de passe incorrect. » | Passé |
| TC-AUTH-11 | Déconnexion | — | Se connecter, cliquer « Déconnexion », ouvrir `/favorites` | Retour à l'état visiteur, redirection vers `/login` | Bouton « Connexion » réaffiché, redirection vers `/login` | Passé (automatisé UI) |

## 2. Football

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-FOOT-01 | Liste des championnats | PE (valide) | Ouvrir `/championships` | 6 cartes : Premier League, Ligue 1, La Liga, Serie A, Bundesliga, Ligue des champions | 6 cartes conformes | Passé (automatisé UI + API + Postman) |
| TC-FOOT-02 | Classement de la Premier League | CT | Ouvrir `/championships/PL` | 4 lignes, positions croissantes de 1 à 4, Arsenal visible | 4 lignes ordonnées, Arsenal en tête | Passé (automatisé UI + API) |
| TC-FOOT-03 | Calendrier dans l'onglet « Matchs » | CT | Ouvrir `/championships/PL`, cliquer l'onglet « Matchs » | 3 matchs, statut « À venir », équipes domicile/extérieur | 3 matchs « À venir », Arsenal vs Chelsea | Passé (automatisé UI + API) |
| TC-FOOT-04 | Fiche équipe | CT | Cliquer « Arsenal » dans le classement | URL `/teams/PL/57`, titre « Arsenal », stade affiché, bouton favori si connecté | URL, titre, stade et bouton conformes | Passé (automatisé UI + API) |
| TC-FOOT-05 | Championnat inconnu | PE (invalide) | Ouvrir `/championships/XX` | Message d'erreur récupérable et bouton « Réessayer » | `Impossible de charger…` + bouton « Réessayer » | Passé (automatisé UI) |
| TC-FOOT-06 | Équipe inconnue | PE (invalide) | `GET /api/football/leagues/PL/teams/999999` | 404 avec message | 404 | Passé (automatisé API + Postman) |

## 3. Favoris

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-FAV-01 | Ajout d'un favori | PE (valide) | Se connecter, ouvrir la fiche Arsenal, cliquer « Ajouter aux favoris » | Bouton « Dans mes favoris », favori listé dans `/favorites` | Bouton actif, carte Arsenal listée | Passé (automatisé UI + API + Postman) |
| TC-FAV-02 | Doublon refusé | PE (invalide) | Ajouter deux fois la même équipe | 409 « Team already in favorites », un seul favori | 409, aucun doublon | Passé (automatisé API + Postman) |
| TC-FAV-03 | Tri de la liste | VL / ordre | Ajouter Arsenal puis Chelsea | Chelsea puis Arsenal (plus récent en premier) | Ordre décroissant conforme | Passé (automatisé API) |
| TC-FAV-04 | Suppression d'un favori | — | Supprimer la carte Arsenal depuis `/favorites` | 204, carte retirée, état vide affiché | 204, état « Aucune équipe favorite » | Passé (automatisé UI + API + Postman) |
| TC-FAV-05 | Suppression d'un favori inexistant | PE (invalide) | `DELETE /api/favorites/999999999` | 404 | 404 | Passé (automatisé API + Postman) |
| TC-FAV-06 | Isolation entre deux comptes | TD | Compte A ajoute Arsenal ; compte B liste puis tente de supprimer ce favori | Liste de B vide ; suppression refusée (404) | Liste vide ; 404 | Passé (automatisé UI + API) |
| TC-FAV-07 | Persistance après rechargement et redémarrage | — | Ajouter un favori, recharger, `docker compose restart`, rouvrir | Favori toujours présent | Favori présent après rechargement et redémarrage | Passé |
| TC-FAV-08 | Nom accentué préservé | VL (jeu de caractères) | Ajouter `Atlético de Madrid` | Nom renvoyé et affiché avec accents | Nom conforme | Passé (automatisé API) |
| TC-FAV-09 | Visiteur sans droit d'ajout | TD | Ouvrir la fiche Arsenal sans session | Aucun bouton favori, message d'invitation à se connecter | Bouton absent, message « Connecte-toi pour gérer tes favoris. » | Passé (automatisé UI) |

## 4. Sécurité et robustesse

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-SEC-01 | Accès sans jeton | TD | `GET /api/users/me` et `GET /api/favorites` sans en-tête `Authorization` | 401 « Authentication required » | 401 | Passé (automatisé API + Postman) |
| TC-SEC-02 | Jeton malformé | PE (invalide) | `Authorization: Bearer abc.def.ghi` | 401 « Invalid or expired token » | 401 | Passé (automatisé API + Postman) |
| TC-SEC-03 | Jeton `alg: none` | PE (invalide) | Jeton forgé sans signature | 401 | 401 | Passé (automatisé API + Postman) |
| TC-SEC-04 | Signature falsifiée | PE (invalide) | Modifier `sub` d'un jeton valide sans recalculer la signature | 401 | 401 | Passé (automatisé API) |
| TC-SEC-05 | Limitation des tentatives de connexion | VL (12 essais) | 12 connexions avec un mauvais mot de passe | Blocage ou 429 attendu | 12 × 401, aucun 429 | **Anomalie ANO-004** |
| TC-SEC-06 | Identifiant d'équipe hors limites | VL (0, −1) et PE (texte) | `team_id` = 0, −1, `"abc"` | 422, champ `team_id` en erreur | 422 | Passé (automatisé API) |
| TC-SEC-07 | Nom d'équipe vide ou espaces | VL | `team_name` = `""`, `"   "`, 151 caractères | 422, champ `team_name` en erreur | 422 | Passé (automatisé API) |
| TC-SEC-08 | Équipe inexistante acceptée en favori | PE (invalide) | `POST /api/favorites` avec `team_id = 987654321`, `team_name = "Ghost FC"` | 422 : l'équipe n'existe pas dans le référentiel | **201**, favori créé | **Anomalie ANO-001** |
| TC-SEC-09 | Schéma d'URL de l'écusson | PE (invalide) | `team_crest = "javascript:alert(1)"` | 422 : schéma non autorisé | **201**, valeur stockée telle quelle | **Anomalie ANO-002** |
| TC-SEC-10 | Santé du service avec base arrêtée | — | `docker compose stop db`, puis `GET /health` et `POST /api/auth/register` | `/health` doit signaler l'indisponibilité | `/health` → 200 `{"status":"ok"}` ; inscription → 500 | **Anomalie ANO-003** |

## 5. V2 — Buteurs et passeurs

Section ajoutée le 22/11/2026 pour la fonctionnalité F2 de la
[`V2_SPEC.md`](V2_SPEC.md). Exécution sur **données réelles**
(`MOCK_FOOTBALL_API=false`), Premier League.

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-SCOR-01 | Classement des buteurs | CT | Ouvrir `/championships/PL`, cliquer l'onglet « Buteurs » | 10 lignes, positions 1 à 10, buts strictement décroissants (à égalité : moins de matchs, puis nom) | 10 lignes ; Haaland 9 buts en tête ; égalités à 6 buts départagées par les matchs puis le nom | Passé (automatisé UI + API + Postman) |
| TC-SCOR-02 | Bascule « Buts / Passes » | TD | Dans l'onglet « Buteurs », cliquer « Passes » | Le tableau est réordonné par passes décroissantes, la colonne active est signalée | Réordonné : Evanilson 4 passes, puis Groβ, Wirtz, McGinn (départage buts puis nom) | Passé (automatisé UI + API + Postman) |
| TC-SCOR-03 | Bornes des paramètres | VL (0, 51) et PE (invalide) | `GET /api/football/leagues/PL/scorers` avec `limit=0`, `limit=51`, `limit=abc`, `sort=penalties` | 422 pour chacun | 422 pour les quatre | Passé (automatisé API + Postman) |
| TC-SCOR-04 | Donnée absente et championnat inconnu | PE (invalide) | Observer un joueur sans passe fournie ; appeler `/leagues/XX/scorers` | `assists` exposé à `0` (jamais `null`) ; 404 pour `XX` | Haaland (9 buts, `assists: null` côté fournisseur) exposé à `0` ; 404 pour `XX` | Passé (automatisé API) |

## 6. V2 — Actualités récentes

Section ajoutée le 22/11/2026 pour la fonctionnalité F3a de la
[`V2_SPEC.md`](V2_SPEC.md). Exécution sur **données réelles**, page d'accueil.

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-NEWS-01 | Fil de résultats à l'accueil | CT | Ouvrir `/` | Section « Résultats récents », 5 éléments au maximum, compétition, titre et score affichés, tri du plus récent au plus ancien | 5 éléments, tri conforme (Real Madrid 2-1 Celta en tête) | Passé (automatisé UI + API + Postman) |
| TC-NEWS-02 | Trois branches de formulation | TD | Observer les titres générés | Victoire domicile « X s'impose a-b face à Y », victoire extérieur « Y s'impose b-a sur le terrain de X », nul « X et Y se quittent dos à dos (a-a) » | Les trois branches observées et conformes | Passé (automatisé API + Postman) |
| TC-NEWS-03 | Bornes de la fenêtre | VL (0, 11) et PE (texte) | `GET /api/football/news` avec `days=0`, `days=11`, `limit=21`, `days=abc` | 422 pour chacun (le fournisseur refuse plus de 10 jours d'écart) | 422 pour les quatre | Passé (automatisé API + Postman) |
| TC-NEWS-04 | Compétitions non supportées | PE (invalide) | Comparer la réponse du fournisseur (contient BSA, DED, ELC) et le fil renvoyé | Seuls PL, FL1, PD, SA, BL1 et CL sont exposés | Aucune compétition hors périmètre | Passé (automatisé API) |

## 7. V2 — Bloc presse

Section ajoutée le 22/11/2026 pour la fonctionnalité F3b de la
[`V2_SPEC.md`](V2_SPEC.md). Source externe **non contractuelle** : les cas
vérifient la dégradation, pas la disponibilité du site source.

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-PRESS-01 | Bloc presse et attribution | CT | Ouvrir `/`, observer la section « À la une » | Titres en français, chacun lien vers l'article d'origine (`target="_blank"`, `rel="noopener noreferrer"`), mention « Source : RMC Sport » | Section affichée, 5 titres, liens et mention conformes | Passé (automatisé UI + API + Postman) |
| TC-PRESS-02 | Dégradation gracieuse | PE (invalide) | Flux injoignable, XML invalide, flux vide (tests unitaires hors ligne) | `200` avec `available: false` et `items: []`, jamais `5xx` ; bloc masqué côté interface | `available: false`, aucun `5xx`, bloc absent | Passé (automatisé unitaire + UI) |
| TC-PRESS-03 | Nettoyage et bornes | VL et PE | Titre contenant du HTML, titre de 300 caractères, `limit=0`, `limit=11` | Balises retirées, titre tronqué à 140 caractères, 422 hors bornes | Nettoyage et troncature conformes, 422 sur les deux bornes | Passé (automatisé unitaire + API) |

## 8. V2 — Détail d'un match

Section ajoutée le 22/11/2026 pour la fonctionnalité F4 de la
[`V2_SPEC.md`](V2_SPEC.md). Exécution sur **données réelles**.

| ID | Titre | Technique | Étapes | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|
| TC-MATCH-01 | Détail d'un match | CT | Depuis l'onglet « Matchs », cliquer « Détails » (ou « Voir le match » depuis l'accueil) | Compétition, date, statut, équipes et score affichés, cohérents avec la liste | Arsenal FC 3-0 Coventry City FC, statut « Terminé » | Passé (automatisé UI + API + Postman) |
| TC-MATCH-02 | Identifiant inconnu | PE (invalide) | `GET /api/football/matches/999999999` | 404, message affiché avec bouton « Réessayer » | 404, écran récupérable | Passé (automatisé UI + API + Postman) |
| TC-MATCH-03 | Identifiant non numérique | VL et PE | `GET /api/football/matches/abc` | 422 | 422 | Passé (automatisé API) |

## 9. Session exploratoire

| ID | Charte | Durée | Zones explorées | Constats |
|---|---|---|---|---|
| EX-01 | Explorer les états limites et les erreurs réseau sur les parcours championnat et favoris | 45 min | Navigation arrière après déconnexion, double clic sur « Ajouter aux favoris », coupure réseau simulée, URL directe `/teams/PL/abc`, collage d'un e-mail avec espaces, écusson invalide | Aucun crash ; les écrans d'erreur sont récupérables ; `team_name` trop long refusé ; **ANO-001**, **ANO-002**, **ANO-003** confirmées ; aucun défaut d'accessibilité bloquant (libellés et rôles présents) |

## 10. Synthèse d'exécution

### Campagne V1 (13/11/2026, mode simulé)

| Domaine | Cas | Passés | Anomalies |
|---|---|---|---|
| Authentification | 11 | 11 | 0 |
| Football | 6 | 6 | 0 |
| Favoris | 9 | 9 | 0 |
| Sécurité / robustesse | 10 | 6 | 4 (ANO-001, ANO-002, ANO-003, ANO-004) |
| Exploratoire | 1 session | — | ANO-003 confirmée |
| **Total** | **36** | **32 (88,9 %)** | **4 anomalies distinctes** |

### V2 — buteurs, actualités, presse et détail de match (22/11/2026, données réelles)

| Domaine | Cas | Passés | Anomalies |
|---|---|---|---|
| Buteurs / passeurs | 4 | 4 | 0 |
| Actualités récentes | 4 | 4 | 0 |
| Bloc presse | 3 | 3 | 0 |
| Détail d'un match | 3 | 3 | 0 |
| **Total V2 (F2 + F3 + F4)** | **14** | **14 (100 %)** | **0** |

Les cas marqués « automatisé » sont rejoués à chaque pipeline ; les autres sont
rejoués manuellement à chaque campagne. Les anomalies ANO-001, ANO-002 et
ANO-004 sont couvertes par des tests `xfail(strict=True)` : elles restent
visibles dans le rapport Allure sans faire échouer la CI, la correction étant
hors périmètre du projet.
