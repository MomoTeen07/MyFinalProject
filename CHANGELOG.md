# Journal des modifications

Toutes les évolutions notables de ce dépôt sont consignées ici.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnage sémantique.

## [Non publié]

### Corrigé

- **CI rouge depuis le 10 novembre 2026** : le test `home displays football QA`
  échouait en mode strict car le libellé « Football QA » apparaît trois fois
  dans la page (navigation, carte de présentation, en-tête du formulaire). Le
  test cible désormais le titre de la carte avec
  `getByRole('heading', { name: 'Football QA', exact: true })`.

### Ajouté

- **Rapports Allure** : `allure-pytest` pour les suites backend et API,
  `allure-playwright` pour la suite UI. La CI agrège les trois jeux de
  résultats et publie un rapport HTML unique en artefact.
- **Artefacts d'échec UI** : traces, captures et vidéos conservées dans
  `tests/playwright/test-results/` (`trace: retain-on-failure`) pour rendre
  chaque anomalie reproductible.

### Modifié

- `.gitignore` : exclusion de `allure-results/`, `allure-report/`,
  `test-results/`, `playwright-report/` et `.venv*/`.
- Le fichier `tests/playwright/test-results/.last-run.json`, précédemment
  versionné, est retiré du suivi Git.
