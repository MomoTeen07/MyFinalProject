import { expect, test } from '@playwright/test';

test('home displays the product heading', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1, name: /Le football, simplement/ })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Prochains matchs' })).toBeVisible();
  await expect(page.getByRole('link', { name: /Explorer les championnats/ })).toBeVisible();
});

test('les prochains matchs sont affichés', async ({ page, request }) => {
  const response = await request.get('/api/football/fixtures?days=10&limit=4');
  expect(response.status(), await response.text()).toBe(200);
  const payload = await response.json();

  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Prochains matchs' })).toBeVisible();
  if (payload.items.length === 0) {
    await expect(page.getByText('Aucun match programmé dans les 10 prochains jours.')).toBeVisible();
    return;
  }
  await expect(page.locator('.fixture-link')).toHaveCount(payload.items.length);
});

test('championships are visible', async ({ page }) => {
  await page.goto('/championships');
  await expect(page.getByTestId('championship-list')).toBeVisible();
  await expect(page.getByTestId('championship-card')).toHaveCount(6);
  await expect(page.getByRole('heading', { name: 'Premier League' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Ligue des champions' })).toBeVisible();
});
