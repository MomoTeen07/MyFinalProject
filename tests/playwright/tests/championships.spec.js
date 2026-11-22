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

  test('l’onglet buteurs affiche le classement des buteurs', async ({ page, football }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('PL');

    await championship.openScorers();

    const expectedCount = Math.min(10, football.scorers.items.length);
    await expect(championship.tableRows).toHaveCount(expectedCount);
    const top = football.scorers.items[0];
    await expect(championship.tableRows.first()).toContainText(top.player.name);
    await expect(championship.tableRows.first()).toContainText(top.team.name);
    await expect(championship.scorerColumn(4).first()).toHaveText(String(top.goals));
    await expect(championship.scorerColumn(5).first()).toHaveText(String(top.assists));
  });

  test('la bascule Buts/Passes reclasse le tableau', async ({ page, football }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('PL');
    await championship.openScorers();
    await expect(championship.goalsToggle).toHaveAttribute('aria-pressed', 'true');

    await championship.assistsToggle.click();

    await expect(championship.assistsToggle).toHaveAttribute('aria-pressed', 'true');
    const top = football.scorersByAssists.items[0];
    await expect(championship.tableRows.first()).toContainText(top.player.name);
    await expect(championship.scorerColumn(5).first()).toHaveText(String(top.assists));
  });

  test('un buteur mène à la fiche de son équipe', async ({ page, football }) => {
    const championship = new ChampionshipPage(page);
    const team = new TeamPage(page);
    const expected = football.scorers.items[0].team;
    await championship.goto('PL');
    await championship.openScorers();

    await championship.teamLink(expected.name).first().click();

    await expect(page).toHaveURL(new RegExp(`/teams/PL/${expected.id}$`));
    await expect(team.heading).toHaveText(expected.name);
  });

  test('un championnat inconnu affiche une erreur récupérable', async ({ page }) => {
    const championship = new ChampionshipPage(page);
    await championship.goto('XX');

    await expect(championship.errorAlert).toContainText('Impossible de charger');
    await expect(page.getByRole('button', { name: 'Réessayer' })).toBeVisible();
  });
});
