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

  /**
   * Source externe non contractuelle : le test compare l'interface à l'API.
   * Si le flux est indisponible, l'absence de bloc est le comportement attendu.
   */
  test('le bloc presse reste cohérent avec l’API', async ({ page, request }) => {
    const response = await request.get('/api/football/press?limit=5');
    expect(response.status(), await response.text()).toBe(200);
    const payload = await response.json();

    await page.goto('/');

    const section = page.getByRole('region', { name: 'À la une' });
    if (!payload.available) {
      await expect(section).toHaveCount(0);
      return;
    }

    await expect(section).toBeVisible();
    await expect(section.getByText('Source : RMC Sport')).toBeVisible();
    await expect(section.locator('li.press-item')).toHaveCount(
      Math.min(5, payload.items.length),
    );

    const link = section.locator('a.press-link').first();
    await expect(link).toHaveAttribute('target', '_blank');
    await expect(link).toHaveAttribute('rel', /noopener/);
    await expect(link).toHaveAttribute('href', /^https?:\/\//);
  });
});
