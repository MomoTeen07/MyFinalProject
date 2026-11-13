import { defineConfig, devices } from '@playwright/test';

/**
 * Configuration Playwright du projet final QA.
 *
 * - `allure-playwright` alimente `tests/playwright/allure-results`, fusionné
 *   avec les résultats PyTest dans le rapport Allure de la CI.
 * - Les artefacts d'échec (trace, capture, vidéo) sont conservés pour rendre
 *   chaque anomalie reproductible.
 */
export default defineConfig({
  testDir: './tests',
  outputDir: './test-results',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  timeout: 30_000,
  expect: { timeout: 7_000 },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['allure-playwright'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5174',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    testIdAttribute: 'data-testid',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
