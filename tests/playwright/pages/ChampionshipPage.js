/** Détail d'un championnat : classement, matchs et buteurs. */
export class ChampionshipPage {
  constructor(page) {
    this.page = page;
    this.standingsTab = page.getByRole('tab', { name: 'Classement' });
    this.matchesTab = page.getByRole('tab', { name: 'Matchs' });
    this.scorersTab = page.getByRole('tab', { name: 'Buteurs' });
    this.tableRows = page.locator('table tbody tr');
    this.matchCards = page.locator('article.match');
    this.errorAlert = page.getByRole('alert');
    this.backLink = page.getByRole('link', { name: /Tous les championnats/ });
    this.goalsToggle = page.getByRole('button', { name: 'Buts', exact: true });
    this.assistsToggle = page.getByRole('button', { name: 'Passes', exact: true });
  }

  async goto(code) {
    await this.page.goto(`/championships/${code}`);
  }

  async openMatches() {
    await this.matchesTab.click();
  }

  async openScorers() {
    await this.scorersTab.click();
  }

  teamLink(name) {
    return this.page.getByRole('link', { name, exact: true });
  }

  /** Cellules d'une colonne du tableau des buteurs (index 0 = « # »). */
  scorerColumn(index) {
    return this.page.locator(`table tbody tr td:nth-child(${index + 1})`);
  }
}
