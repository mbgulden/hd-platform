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

      const shell = await page.evaluate(() => {
        const text = (el: Element | null) => el?.textContent?.replace(/\s+/g, ' ').trim() ?? '';
        const headers = [...document.querySelectorAll('body > header')];
        const footers = [...document.querySelectorAll('body > footer')];
        const header = headers[0] ?? null;
        const footer = footers[0] ?? null;
        const menuButton = header?.querySelector<HTMLButtonElement>('.menu-toggle') ?? null;
        const nav = header?.querySelector('nav') ?? null;
        return {
          headerCount: headers.length,
          footerCount: footers.length,
          headerText: text(header),
          footerText: text(footer),
          navLinkTexts: [...(header?.querySelectorAll('nav a') ?? [])].map(text),
          footerGroupTexts: [...(footer?.querySelectorAll('.footer-group h2') ?? [])].map(text),
          hasLegacyStandardClass: Boolean(document.querySelector('.hde-standard-header, .hde-standard-footer')),
          hasMenuButton: Boolean(menuButton),
          menuExpanded: menuButton?.getAttribute('aria-expanded') ?? null,
          menuVisible: nav ? getComputedStyle(nav).visibility : null,
        };
      });
      expect(shell.headerCount).toBe(1);
      expect(shell.footerCount).toBe(1);
      expect(shell.headerText).toContain('Human Design');
      expect(shell.headerText).toContain('Free Reading');
      expect(shell.navLinkTexts).toEqual(['Free Reading', 'Reports', 'Sanctuary', 'API', 'Learn', 'Coaching']);
      expect(shell.footerText).toContain('Human Design Engine');
      expect(shell.footerGroupTexts).toEqual(['Start', 'Products', 'Learn']);
      expect(shell.hasLegacyStandardClass).toBe(false);

      if ((page.viewportSize()?.width ?? 9999) <= 868) {
        const button = page.locator('body > header .menu-toggle');
        await expect(button).toBeVisible();
        await expect(button).toHaveAttribute('aria-expanded', 'false');
        await button.click();
        await expect(button).toHaveAttribute('aria-expanded', 'true');
        await expect(page.locator('body')).toHaveClass(/drawer-open/);
        await expect(page.locator('body > header nav')).toBeVisible();
        await page.keyboard.press('Escape');
        await expect(button).toHaveAttribute('aria-expanded', 'false');
      }
    });
  }
});
