/** Barre de navigation principale. */
export class Navbar {
  constructor(page) {
    this.page = page;
    this.root = page.getByRole('navigation', { name: 'Navigation principale' });
    this.loginLink = page.getByTestId('login-button');
    this.favoritesLink = page.getByTestId('favorites-link');
    this.logoutButton = this.root.getByRole('button', { name: 'Déconnexion' });
    this.userLabel = this.root.locator('.nav-user');
  }

  async openFavorites() {
    await this.favoritesLink.click();
  }

  async logout() {
    await this.logoutButton.click();
  }
}
