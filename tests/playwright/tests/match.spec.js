import { expect, test } from '../fixtures/test.js';

/**
 * Page détail d'un match (V2, F4).
 *
 * L'identifiant vient de l'API (fixture `football`) : aucun identifiant figé.
 */
test.describe('Détail d’un match', () => {
  test('les équipes et le score sont affichés', async ({ page, football }) => {
    const match = football.matches[0];
    await page.goto(`/matches/${match.id}`);

    await expect(
      page.getByRole('heading', { level: 1, name: 'Détail du match' }),
    ).toBeVisible();

    const matchup = page.locator('.match-details .matchup');
    await expect(matchup).toContainText(match.homeTeam.name);
    await expect(matchup).toContainText(match.awayTeam.name);
  });

  test('le contexte du match est disponible', async ({ page, football }) => {
    const match = football.matches[0];
    await page.goto(`/matches/${match.id}`);

    await expect(page.getByRole('heading', { name: 'Classement' })).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Afficher les confrontations directes' }),
    ).toBeVisible();
  });

  test('un identifiant inconnu affiche une erreur récupérable', async ({ page }) => {
    await page.goto('/matches/999999999');

    await expect(page.getByRole('alert')).toContainText('Impossible de charger le match');
    await expect(page.getByRole('button', { name: 'Réessayer' })).toBeVisible();
  });
});
