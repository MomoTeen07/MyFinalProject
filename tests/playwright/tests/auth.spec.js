import { AuthPage } from '../pages/AuthPage.js';
import { Navbar } from '../pages/Navbar.js';
import { expect, test, uniqueEmail } from '../fixtures/test.js';

test.describe('Authentification', () => {
  test('un visiteur est redirigé vers la connexion pour les favoris', async ({ page }) => {
    await page.goto('/favorites');

    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole('heading', { name: 'Connexion' })).toBeVisible();
  });

  test('des identifiants invalides affichent un message explicite', async ({ page }) => {
    const auth = new AuthPage(page);
    await auth.gotoLogin();

    await auth.login('inconnu@example.com', 'MauvaisMotDePasse1!');

    await expect(auth.errorAlert).toContainText('incorrect');
    await expect(page).toHaveURL(/\/login$/);
  });

  test("l'inscription connecte l'utilisateur et affiche son nom", async ({ page }) => {
    const auth = new AuthPage(page);
    const navbar = new Navbar(page);
    const email = uniqueEmail('qa.register');

    await auth.gotoRegister();
    await auth.register('Nouveau Testeur', email, 'Password123!');

    await expect(page).toHaveURL(/\/championships$/);
    await expect(navbar.favoritesLink).toBeVisible();
    await expect(navbar.userLabel).toContainText('Nouveau Testeur');
  });

  test('la session survit à un rechargement de page', async ({ page, loginAs }) => {
    await page.goto('/favorites');
    await expect(page.getByRole('heading', { name: /Mes favoris/ })).toBeVisible();

    await page.reload();

    await expect(page.getByRole('heading', { name: /Mes favoris/ })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Connexion' })).toHaveCount(0);
  });

  test('la déconnexion ferme la session', async ({ page, loginAs }) => {
    const navbar = new Navbar(page);
    await page.goto('/championships');
    await expect(navbar.logoutButton).toBeVisible();

    await navbar.logout();

    await expect(navbar.loginLink).toBeVisible();
    await expect(navbar.favoritesLink).toHaveCount(0);

    await page.goto('/favorites');
    await expect(page).toHaveURL(/\/login$/);
  });
});
