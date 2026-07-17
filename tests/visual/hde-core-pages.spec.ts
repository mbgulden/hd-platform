import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const routes = JSON.parse(readFileSync(new URL('../../.pwp/routes.json', import.meta.url), 'utf8'));

test.describe('HDE core page visual smoke', () => {
  for (const route of routes.routes) {
    test(`${route.name} renders expected cream/sage surface`, async ({ page }) => {
      await page.goto(route.path);
      await expect(page.locator('body')).toContainText(route.requiredText);
      const styles = await page.evaluate(() => {
        const h1 = document.querySelector('h1');
        const nav = document.querySelector('nav');
        const h1Style = h1 ? getComputedStyle(h1) : null;
        const navStyle = nav ? getComputedStyle(nav) : null;
        return {
          bodyText: getComputedStyle(document.body).color,
          bodyBg: getComputedStyle(document.body).backgroundColor,
          h1Color: h1Style?.color ?? null,
          h1Bg: h1Style?.backgroundImage ?? null,
          navBg: navStyle?.backgroundColor ?? null,
          css: [...document.styleSheets].map((sheet) => sheet.href).filter(Boolean),
        };
      });
      expect(styles.bodyText).toBe('rgb(47, 54, 49)');
      if (styles.h1Color) expect(styles.h1Color).toBe('rgb(47, 54, 49)');
      if (styles.h1Bg) expect(styles.h1Bg).toBe('none');
      expect(JSON.stringify(styles)).not.toContain('rgb(102, 126, 234)');
      expect(JSON.stringify(styles)).not.toContain('rgb(118, 75, 162)');
    });
  }
});
