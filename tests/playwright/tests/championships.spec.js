import { ChampionshipPage } from '../pages/ChampionshipPage.js';
import { ChampionshipsPage } from '../pages/ChampionshipsPage.js';
import { TeamPage } from '../pages/TeamPage.js';
import { expect, test } from '../fixtures/test.js';

const LEAGUES = [
  'Premier League',
  'Ligue 1',
  'La Liga',
  'Serie A',
  'Bundesliga',
  'Ligue des champions',
];

/**
 * Les attentes sont dérivées de l'API (fixture `football`) : la suite tourne
 * contre les données réelles du fournisseur, sans valeur figée du mode simulé.
 */
test.describe('Championnats', () => {
  test('les six championnats sont affichés', async ({ page }) => {
    const championships = new ChampionshipsPage(page);
    await championships.goto();

    await expect(championships.cards).toHaveCount(LEAGUES.length);
    for (const name of LEAGUES) {
      await expect(championships.card(name)).toBeVisible();
    }
  });

  test('le classement de la Premier League est complet', async ({ page, football }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('PL');

    await expect(page.getByRole('heading', { level: 1, name: football.leagueName })).toBeVisible();
    await expect(championship.tableRows).toHaveCount(football.standings.length);
    await expect(championship.teamLink(football.standings[0].team.name)).toBeVisible();
    await expect(championship.tableRows.first()).toContainText(String(football.standings[0].position));
  });

  test('les matchs sont affichés dans un onglet dédié', async ({ page, football }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('PL');

    await championship.openMatches();

    await expect(championship.matchCards).toHaveCount(football.matches.length);
    await expect(championship.matchCards.first()).toBeVisible();
    await expect(championship.matchCards.first().locator('time')).toHaveCount(1);
  });

  test('le classement mène à la fiche équipe', async ({ page, football }) => {
    const championship = new ChampionshipPage(page);
    const team = new TeamPage(page);
    const expected = football.standings[0].team;
    await championship.goto('PL');

    await championship.teamLink(expected.name).click();

    await expect(page).toHaveURL(new RegExp(`/teams/PL/${expected.id}$`));
    await expect(team.heading).toHaveText(expected.name);
    await expect(team.venue).not.toBeEmpty();
  });

  test('un championnat inconnu affiche une erreur récupérable', async ({ page }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('XX');

    await expect(championship.errorAlert).toContainText('Impossible de charger');
    await expect(page.getByRole('button', { name: 'Réessayer' })).toBeVisible();
  });
});
