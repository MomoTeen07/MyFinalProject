import {test,expect} from '@playwright/test';
test('home displays football QA',async({page})=>{await page.goto('/');await expect(page.getByText('Football QA')).toBeVisible();});
test('championships are visible',async({page})=>{await page.goto('/championships');await expect(page.getByTestId('championship-list')).toBeVisible();await expect(page.getByTestId('championship-card')).toHaveCount(5);await expect(page.getByText('Premier League')).toBeVisible();await expect(page.getByText('Ligue 1')).toBeVisible();});
