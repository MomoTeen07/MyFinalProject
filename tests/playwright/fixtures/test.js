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

  /**
   * Oracle de données réelles.
   *
   * Les attentes de l'interface sont dérivées des réponses de l'API, jamais de
   * valeurs figées du mode simulé : la suite reste valable quand la saison, le
   * nombre d'équipes ou les noms changent. Les réponses sont mises en cache par
   * le backend (`FOOTBALL_CACHE_TTL_SECONDS`), donc les appels répétés ne
   * consomment pas le quota du fournisseur.
   */
  football: async ({ request }, use) => {
    const leaguesResponse = await request.get('/api/football/leagues');
    expect(leaguesResponse.status(), await leaguesResponse.text()).toBe(200);
    const leagues = await leaguesResponse.json();

    const standingsResponse = await request.get('/api/football/leagues/PL/standings');
    expect(standingsResponse.status(), await standingsResponse.text()).toBe(200);
    const standings = await standingsResponse.json();

    const matchesResponse = await request.get(
      '/api/football/leagues/PL/matches?page_size=20&sort=date',
    );
    expect(matchesResponse.status(), await matchesResponse.text()).toBe(200);
    const matchesPayload = await matchesResponse.json();

    const scorersResponse = await request.get('/api/football/leagues/PL/scorers?limit=10');
    expect(scorersResponse.status(), await scorersResponse.text()).toBe(200);
    const scorers = await scorersResponse.json();

    const assistsResponse = await request.get(
      '/api/football/leagues/PL/scorers?limit=10&sort=assists',
    );
    expect(assistsResponse.status(), await assistsResponse.text()).toBe(200);
    const scorersByAssists = await assistsResponse.json();

    expect(standings.length, 'le classement réel de la Premier League est vide').toBeGreaterThan(0);
    expect(standings.length, 'au moins deux équipes sont nécessaires').toBeGreaterThan(1);
    expect(scorers.items.length, 'le classement des buteurs est vide').toBeGreaterThan(0);
    expect(matchesPayload.items.length, 'le calendrier de la Premier League est vide')
      .toBeGreaterThan(0);

    await use({
      leagueName: leagues.find((league) => league.code === 'PL')?.name ?? 'PL',
      standings,
      teams: standings.map((row) => row.team),
      matches: matchesPayload.items,
      matchesPayload,
      scorers,
      scorersByAssists,
    });
  },

  /**
   * Oracle du fil d'actualités.
   *
   * Séparé de `football` pour ne pas ralentir les tests qui n'en ont pas
   * besoin. La fenêtre par défaut (7 jours) est mise en cache par le backend.
   */
  news: async ({ request }, use) => {
    const response = await request.get('/api/football/news?days=7&limit=5');
    expect(response.status(), await response.text()).toBe(200);
    await use(await response.json());
  },
});

export { expect };
export { uniqueEmail, PASSWORD };
