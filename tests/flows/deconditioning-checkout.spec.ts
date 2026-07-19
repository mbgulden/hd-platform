import { test, expect } from '@playwright/test';

const stagingUrl = process.env.PWP_STAGING_URL;

test.describe('local route flows', () => {
  test('free reading generator loads the embedded widget shell', async ({ page }) => {
    await page.goto('/free-human-design-reading-generator/');
    await expect(page.locator('body')).toContainText('Free Human Design Reading Generator');
    await expect(page.locator('.hde-chart-widget')).toBeVisible();
  });

  test('free reading generator reserves widget space before JavaScript hydrates', async ({ page }) => {
    await page.route('**/widget.js', (route) => route.abort());
    await page.goto('/free-human-design-reading-generator/');

    const panel = page.locator('.widget-panel');
    await expect(page.locator('.widget-skeleton')).toBeVisible();

    const box = await panel.boundingBox();
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(560);
  });

  test('buy report page exposes the Human Design blueprint CTA', async ({ page }) => {
    await page.goto('/buy-report/');
    await expect(page.locator('body')).toContainText('Your Human Design Blueprint');
  });

  test('gate index links to gate 1', async ({ page }) => {
    await page.goto('/human-design/gates/');
    await expect(page.locator('a[href$="gate-1.html"]').first()).toBeVisible();
  });
});

test.describe('staging process flow', () => {
  test.skip(!stagingUrl, 'Set PWP_STAGING_URL to run live staging process checks');

  test('staging checkout surface is reachable', async ({ page }) => {
    await page.goto(`${stagingUrl}/buy-report/`);
    await expect(page.locator('body')).toContainText('Human Design');
  });

  test('staging gates surface is reachable with light theme CSS', async ({ page }) => {
    await page.goto(`${stagingUrl}/human-design/gates/`);
    await expect(page.locator('body')).toContainText('The 64 Gates of Human Design');
    const css = await page.evaluate(() => [...document.styleSheets].map((sheet) => sheet.href).filter(Boolean));
    expect(css.join('\n')).toContain('/hde-light-theme.css');
  });
});
