import { expect, test } from '@playwright/test';

test('home displays the product heading', async ({ page }) => {
  await page.goto('/');
  // Le libellé « Football QA » apparaît aussi dans la navigation et dans la
  // carte de présentation : on cible explicitement le titre de la carte.
  await expect(page.getByRole('heading', { name: 'Football QA', exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: /Explorer les championnats/ })).toBeVisible();
});

test('championships are visible', async ({ page }) => {
  await page.goto('/championships');
  await expect(page.getByTestId('championship-list')).toBeVisible();
  await expect(page.getByTestId('championship-card')).toHaveCount(6);
  await expect(page.getByRole('heading', { name: 'Premier League' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Ligue des champions' })).toBeVisible();
});
