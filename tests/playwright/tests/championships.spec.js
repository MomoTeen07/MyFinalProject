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

test.describe('Championnats', () => {
  test('les six championnats sont affichés', async ({ page }) => {
    const championships = new ChampionshipsPage(page);
    await championships.goto();

    await expect(championships.cards).toHaveCount(LEAGUES.length);
    for (const name of LEAGUES) {
      await expect(championships.card(name)).toBeVisible();
    }
  });

  test('le classement de la Premier League est complet', async ({ page }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('PL');

    await expect(page.getByRole('heading', { level: 1, name: 'Premier League' })).toBeVisible();
    await expect(championship.tableRows).toHaveCount(4);
    await expect(championship.teamLink('Arsenal')).toBeVisible();
    await expect(page.locator('table tbody tr').first()).toContainText('1');
  });

  test('les matchs sont affichés dans un onglet dédié', async ({ page }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('PL');

    await championship.openMatches();

    await expect(championship.matchCards).toHaveCount(3);
    await expect(championship.matchCards.first()).toContainText('À venir');
  });

  test('le classement mène à la fiche équipe', async ({ page }) => {
    const championship = new ChampionshipPage(page);
    const team = new TeamPage(page);
    await championship.goto('PL');

    await championship.teamLink('Arsenal').click();

    await expect(page).toHaveURL(/\/teams\/PL\/57$/);
    await expect(team.heading).toHaveText('Arsenal');
    await expect(page.getByText('Football QA Stadium')).toBeVisible();
  });

  test('un championnat inconnu affiche une erreur récupérable', async ({ page }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('XX');

    await expect(championship.errorAlert).toContainText('Impossible de charger');
    await expect(page.getByRole('button', { name: 'Réessayer' })).toBeVisible();
  });
});
