import { FavoritesPage } from '../pages/FavoritesPage.js';
import { Navbar } from '../pages/Navbar.js';
import { TeamPage } from '../pages/TeamPage.js';
import { expect, test } from '../fixtures/test.js';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5174';

/**
 * Les équipes utilisées sont lues dans le classement réel (fixture `football`)
 * au lieu d'être codées en dur : les identifiants et les noms changent avec la
 * saison, les règles métier testées non.
 */
test.describe('Parcours critique des favoris', () => {
  test("ajout, consultation puis suppression d'une équipe favorite", async ({ page, loginAs, football }) => {
    const team = new TeamPage(page);
    const favorites = new FavoritesPage(page);
    const navbar = new Navbar(page);
    const target = football.teams[0];

    await team.goto('PL', target.id);
    await expect(team.heading).toHaveText(target.name);
    await expect(team.favoriteButton).toContainText('Ajouter aux favoris');

    await team.toggleFavorite();
    await expect(team.favoriteButton).toContainText('Dans mes favoris');

    await navbar.openFavorites();
    await expect(page).toHaveURL(/\/favorites$/);
    await expect(favorites.card(target.name)).toBeVisible();

    await favorites.remove(target.name);
    await expect(favorites.emptyState).toBeVisible();
    await expect(favorites.cards).toHaveCount(0);
  });

  test('le favori est conservé après rechargement', async ({ page, loginAs, football }) => {
    const team = new TeamPage(page);
    const favorites = new FavoritesPage(page);
    const target = football.teams[1];

    await team.goto('PL', target.id);
    await team.toggleFavorite();
    await expect(team.favoriteButton).toContainText('Dans mes favoris');

    await favorites.goto();
    await page.reload();

    await expect(favorites.card(target.name)).toBeVisible();
  });

  test("l'état du bouton reflète un favori déjà enregistré", async ({ page, loginAs, football }) => {
    const team = new TeamPage(page);
    const target = football.teams[2];

    await team.goto('PL', target.id);
    await team.toggleFavorite();
    await expect(team.favoriteButton).toContainText('Dans mes favoris');

    await team.goto('PL', target.id);
    await expect(team.favoriteButton).toContainText('Dans mes favoris');
  });

  test('deux comptes ne partagent pas leurs favoris', async ({ page, loginAs, browser, football }) => {
    const team = new TeamPage(page);
    const target = football.teams[0];
    await team.goto('PL', target.id);
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
    await expect(otherFavorites.card(target.name)).toHaveCount(0);

    await otherContext.close();
  });

  test('un visiteur ne peut pas ajouter de favori', async ({ page, football }) => {
    const team = new TeamPage(page);
    const target = football.teams[0];

    await team.goto('PL', target.id);

    await expect(team.heading).toHaveText(target.name);
    await expect(team.favoriteButton).toHaveCount(0);
    await expect(team.loginNotice).toBeVisible();
  });
});
