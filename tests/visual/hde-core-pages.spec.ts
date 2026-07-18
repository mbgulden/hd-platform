import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const routes = JSON.parse(readFileSync(new URL('../../.pwp/routes.json', import.meta.url), 'utf8'));

const expectedNavLabels = ['Free Reading', 'Reports', 'Sanctuary', 'API', 'Learn', 'Coaching'];
const expectedFooterGroups = ['Start', 'Products', 'Learn'];

test.describe('HDE core page visual smoke', () => {
  for (const route of routes.routes) {
    test(`${route.name} renders expected cream/sage surface and emdash shell`, async ({ page }, testInfo) => {
      await page.goto(route.path);
      await expect(page.locator('body')).toContainText(route.requiredText);

      await expect(page.locator('body > header.emdash-site-header')).toHaveCount(1);
      await expect(page.locator('body > footer.emdash-site-footer')).toHaveCount(1);
      await expect(page.locator('body > header.emdash-site-header nav[aria-label="Main Navigation"]')).toHaveCount(1);
      await expect(page.locator('body > footer.emdash-site-footer .footer-group')).toHaveCount(3);
      await expect(page.locator('.hde-standard-header, .hde-standard-footer, [class*="hde-standard-"]')).toHaveCount(0);

      if (testInfo.project.name.includes('mobile')) {
        const menu = page.locator('#menuTrigger');
        await expect(menu).toBeVisible();
        await menu.click();
        await expect(menu).toHaveAttribute('aria-expanded', 'true');
        await expect(page.locator('body')).toHaveClass(/drawer-open/);
        await expect(page.locator('body > header.emdash-site-header nav')).toBeVisible();
      }

      for (const label of expectedNavLabels) {
        await expect(page.locator('body > header.emdash-site-header nav').getByRole('link', { name: label })).toHaveCount(1);
      }
      for (const label of expectedFooterGroups) {
        await expect(page.locator('body > footer.emdash-site-footer').getByRole('heading', { name: label })).toHaveCount(1);
      }

      const styles = await page.evaluate(() => {
        const h1 = document.querySelector('h1');
        const nav = document.querySelector('body > header.emdash-site-header');
        const footer = document.querySelector('body > footer.emdash-site-footer');
        const h1Style = h1 ? getComputedStyle(h1) : null;
        const navStyle = nav ? getComputedStyle(nav) : null;
        const footerStyle = footer ? getComputedStyle(footer) : null;
        return {
          bodyText: getComputedStyle(document.body).color,
          bodyBg: getComputedStyle(document.body).backgroundColor,
          h1Color: h1Style?.color ?? null,
          h1Bg: h1Style?.backgroundImage ?? null,
          navBg: navStyle?.backgroundColor ?? null,
          footerBg: footerStyle?.backgroundColor ?? null,
          css: [...document.styleSheets].map((sheet) => sheet.href).filter(Boolean),
        };
      });
      expect(styles.bodyText).toBe('rgb(47, 54, 49)');
      if (styles.h1Color) expect(styles.h1Color).toBe('rgb(47, 54, 49)');
      if (styles.h1Bg) expect(styles.h1Bg).toBe('none');
      expect(styles.navBg).toContain('250, 247, 240');
      expect(styles.footerBg).toBe('rgb(246, 241, 231)');
      expect(JSON.stringify(styles)).not.toContain('rgb(102, 126, 234)');
      expect(JSON.stringify(styles)).not.toContain('rgb(118, 75, 162)');
    });
  }
});
