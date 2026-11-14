/** Détail d'un championnat : classement et matchs. */
export class ChampionshipPage {
  constructor(page) {
    this.page = page;
    this.standingsTab = page.getByRole('tab', { name: 'Classement' });
    this.matchesTab = page.getByRole('tab', { name: 'Matchs' });
    this.tableRows = page.locator('table tbody tr');
    this.matchCards = page.locator('article.match');
    this.errorAlert = page.getByRole('alert');
    this.backLink = page.getByRole('link', { name: /Tous les championnats/ });
  }

  async goto(code) {
    await this.page.goto(`/championships/${code}`);
  }

  async openMatches() {
    await this.matchesTab.click();
  }

  teamLink(name) {
    return this.page.getByRole('link', { name, exact: true });
  }
}
