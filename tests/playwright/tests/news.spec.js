import { expect, test } from '../fixtures/test.js';

/**
 * Fil de résultats récents de la page d'accueil.
 *
 * Les attentes viennent de l'API (fixture `news`) : aucun nom de club ni score
 * figé. Le test reste donc valable d'une journée à l'autre.
 */
test.describe('Actualités', () => {
  test('les résultats récents sont affichés', async ({ page, news }) => {
    await page.goto('/');

    const section = page.getByRole('region', { name: 'Résultats récents' });
    await expect(section).toBeVisible();

    if (news.items.length === 0) {
      await expect(section.getByText('Aucun résultat récent disponible.')).toBeVisible();
      return;
    }

    const items = section.locator('li.news-item');
    await expect(items).toHaveCount(Math.min(5, news.items.length));

    const first = news.items[0];
    await expect(items.first()).toContainText(first.competition.name);
    await expect(items.first()).toContainText(first.headline);
    await expect(items.first()).toContainText(`${first.score.home} – ${first.score.away}`);
  });

  test('chaque actualité pointe une compétition supportée', async ({ page, news }) => {
    await page.goto('/');

    const section = page.getByRole('region', { name: 'Résultats récents' });
    const labels = await section.locator('li.news-item .eyebrow').allTextContents();

    expect(labels).toHaveLength(Math.min(5, news.items.length));
    for (const label of labels) {
      expect([
        'Premier League',
        'Ligue 1',
        'La Liga',
        'Serie A',
        'Bundesliga',
        'Ligue des champions',
      ]).toContain(label);
    }
  });
});
