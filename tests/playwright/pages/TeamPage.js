/** Fiche d'une équipe et gestion du favori. */
export class TeamPage {
  constructor(page) {
    this.page = page;
    this.heading = page.getByRole('heading', { level: 1 });
    this.favoriteButton = page.getByTestId('favorite-button');
    this.loginNotice = page.getByText('Connecte-toi pour gérer tes favoris.');
    this.errorAlert = page.getByRole('alert');
  }

  async goto(code, teamId) {
    await this.page.goto(`/teams/${code}/${teamId}`);
  }

  async toggleFavorite() {
    await this.favoriteButton.click();
  }
}
