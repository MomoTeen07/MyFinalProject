import { expect, test as base } from '@playwright/test';

const PASSWORD = 'Password123!';

function uniqueEmail(prefix = 'qa.ui') {
  return `${prefix}.${Date.now()}.${Math.random().toString(16).slice(2, 8)}@example.com`;
}

/**
 * Fixtures partagées.
 *
 * `account` crée un compte neuf par test via l'API (rapide et isolé).
 * `loginAs` injecte le jeton dans le stockage local avant toute navigation,
 * ce qui évite de rejouer le formulaire dans chaque scénario.
 */
export const test = base.extend({
  account: async ({ request }, use) => {
    const email = uniqueEmail();
    const response = await request.post('/api/auth/register', {
      data: { email, password: PASSWORD, name: 'UI QA' },
    });
    expect(response.status(), await response.text()).toBe(201);
    const payload = await response.json();
    await use({ email, password: PASSWORD, name: 'UI QA', token: payload.access_token });
  },

  loginAs: async ({ page, account }, use) => {
    // Le jeton est posé une seule fois dans le stockage local, puis la page est
    // rechargée. On évite `addInitScript`, qui le réinjecterait à chaque
    // navigation et rendrait la déconnexion impossible à tester.
    await page.goto('/');
    await page.evaluate((token) => window.localStorage.setItem('token', token), account.token);
    await page.reload();
    await use(account);
  },
});

export { expect };
export { uniqueEmail, PASSWORD };
