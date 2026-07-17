import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { readFileSync } from 'node:fs';

const routes = JSON.parse(readFileSync(new URL('../../.pwp/routes.json', import.meta.url), 'utf8'));

for (const route of routes.routes) {
  test(`${route.name} has no serious or critical axe violations`, async ({ page }) => {
    await page.goto(route.path);
    await expect(page.locator('body')).toContainText(route.requiredText);
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    const serious = results.violations.filter((v) => ['serious', 'critical'].includes(v.impact ?? ''));
    expect(serious, JSON.stringify(serious, null, 2)).toHaveLength(0);
  });
}
