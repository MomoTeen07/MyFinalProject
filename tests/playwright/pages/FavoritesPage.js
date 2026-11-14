/** Liste des équipes favorites de l'utilisateur. */
export class FavoritesPage {
  constructor(page) {
    this.page = page;
    this.heading = page.getByRole('heading', { level: 1 });
    this.cards = page.locator('.card.fav');
    this.emptyState = page.getByRole('heading', { name: 'Aucune équipe favorite' });
    this.errorAlert = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/favorites');
  }

  card(name) {
    return this.cards.filter({ has: this.page.getByRole('heading', { name, exact: true }) });
  }

  async remove(name) {
    await this.card(name).getByRole('button', { name: 'Supprimer' }).click();
  }
}
