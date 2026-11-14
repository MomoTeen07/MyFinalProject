/** Page de connexion / inscription. */
export class AuthPage {
  constructor(page) {
    this.page = page;
    this.nameInput = page.getByLabel('Nom');
    this.emailInput = page.getByTestId('email-input');
    this.passwordInput = page.getByTestId('password-input');
    this.submitButton = page.getByTestId('submit-login');
    this.errorAlert = page.getByRole('alert');
  }

  async gotoLogin() {
    await this.page.goto('/login');
  }

  async gotoRegister() {
    await this.page.goto('/register');
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async register(name, email, password) {
    await this.nameInput.fill(name);
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
