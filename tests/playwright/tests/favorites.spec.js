import { FavoritesPage } from '../pages/FavoritesPage.js';
import { Navbar } from '../pages/Navbar.js';
import { TeamPage } from '../pages/TeamPage.js';
import { expect, test } from '../fixtures/test.js';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5174';

test.describe('Parcours critique des favoris', () => {
  test("ajout, consultation puis suppression d'une équipe favorite", async ({ page, loginAs }) => {
    const team = new TeamPage(page);
    const favorites = new FavoritesPage(page);
    const navbar = new Navbar(page);

    await team.goto('PL', 57);
    await expect(team.heading).toHaveText('Arsenal');
    await expect(team.favoriteButton).toContainText('Ajouter aux favoris');

    await team.toggleFavorite();
    await expect(team.favoriteButton).toContainText('Dans mes favoris');

    await navbar.openFavorites();
    await expect(page).toHaveURL(/\/favorites$/);
    await expect(favorites.card('Arsenal')).toBeVisible();

    await favorites.remove('Arsenal');
    await expect(favorites.emptyState).toBeVisible();
    await expect(favorites.cards).toHaveCount(0);
  });

  test('le favori est conservé après rechargement', async ({ page, loginAs }) => {
    const team = new TeamPage(page);
    const favorites = new FavoritesPage(page);

    await team.goto('PL', 61);
    await team.toggleFavorite();
    await expect(team.favoriteButton).toContainText('Dans mes favoris');

    await favorites.goto();
    await page.reload();

    await expect(favorites.card('Chelsea')).toBeVisible();
  });

  test("l'état du bouton reflète un favori déjà enregistré", async ({ page, loginAs }) => {
    const team = new TeamPage(page);

    await team.goto('PL', 64);
    await team.toggleFavorite();
    await expect(team.favoriteButton).toContainText('Dans mes favoris');

    await team.goto('PL', 64);
    await expect(team.favoriteButton).toContainText('Dans mes favoris');
  });

  test('deux comptes ne partagent pas leurs favoris', async ({ page, loginAs, browser, account }) => {
    const team = new TeamPage(page);
    await team.goto('PL', 57);
    await team.toggleFavorite();
    await expect(team.favoriteButton).toContainText('Dans mes favoris');

    const otherContext = await browser.newContext({ baseURL: BASE_URL });
    const otherPage = await otherContext.newPage();
    const register = await otherContext.request.post('/api/auth/register', {
      data: {
        email: `qa.isolation.${Date.now()}@example.com`,
        password: 'Password123!',
        name: 'Autre Compte',
      },
    });
    expect(register.status()).toBe(201);
    const otherToken = (await register.json()).access_token;
    await otherPage.addInitScript((token) => {
      window.localStorage.setItem('token', token);
    }, otherToken);

    const otherFavorites = new FavoritesPage(otherPage);
    await otherFavorites.goto();

    await expect(otherFavorites.emptyState).toBeVisible();
    await expect(otherFavorites.card('Arsenal')).toHaveCount(0);

    await otherContext.close();
  });

  test('un visiteur ne peut pas ajouter de favori', async ({ page }) => {
    const team = new TeamPage(page);

    await team.goto('PL', 57);

    await expect(team.heading).toHaveText('Arsenal');
    await expect(team.favoriteButton).toHaveCount(0);
    await expect(team.loginNotice).toBeVisible();
  });
});
