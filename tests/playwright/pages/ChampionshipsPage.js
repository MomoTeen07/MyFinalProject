/** Liste des championnats. */
export class ChampionshipsPage {
  constructor(page) {
    this.page = page;
    this.cards = page.getByTestId('championship-card');
    this.list = page.getByTestId('championship-list');
    this.empty = page.getByTestId('championships-empty');
    this.errorAlert = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/championships');
  }

  card(name) {
    return this.cards.filter({ has: this.page.getByRole('heading', { name }) });
  }

  async open(name) {
    await this.card(name).click();
  }
}
