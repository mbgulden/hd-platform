import { test, expect, type Page, type TestInfo } from '@playwright/test';
import { readFileSync } from 'node:fs';

const routes = JSON.parse(readFileSync(new URL('../../.pwp/routes.json', import.meta.url), 'utf8'));

const expectedNavLabels = ['Free Reading', 'Reports', 'Sanctuary', 'API', 'Learn', 'Coaching'];
const expectedFooterGroups = ['Start', 'Products', 'Learn'];
const libraryIndexRoutes = new Set(['gates-index', 'channels-index', 'centers-index', 'authorities-index', 'types-index', 'profiles-index']);

const parseRgb = (value: string | null) => {
  if (!value) return null;
  const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (!match) return null;
  return match.slice(1, 4).map(Number);
};

const luminance = ([r, g, b]: number[]) => {
  const srgb = [r, g, b].map((v) => {
    const n = v / 255;
    return n <= 0.03928 ? n / 12.92 : Math.pow((n + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * srgb[0] + 0.7152 * srgb[1] + 0.0722 * srgb[2];
};

const contrastRatio = (fg: string | null, bg: string | null) => {
  const f = parseRgb(fg);
  const b = parseRgb(bg);
  if (!f || !b) return 0;
  const [l1, l2] = [luminance(f), luminance(b)].sort((a, z) => z - a);
  return (l1 + 0.05) / (l2 + 0.05);
};

test.describe('HDE core page visual smoke', () => {
  for (const route of routes.routes) {
    test(`${route.name} renders expected cream/sage surface and emdash shell`, async ({ page }: { page: Page }, testInfo: TestInfo) => {
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
        const drawerStyles = await page.locator('body > header.emdash-site-header nav').evaluate((nav) => {
          const style = getComputedStyle(nav);
          const rect = nav.getBoundingClientRect();
          return {
            backgroundColor: style.backgroundColor,
            backgroundImage: style.backgroundImage,
            height: rect.height,
            boxShadow: style.boxShadow,
          };
        });
        expect(drawerStyles.backgroundColor).toBe('rgb(250, 247, 240)');
        expect(drawerStyles.backgroundImage).toContain('linear-gradient');
        expect(drawerStyles.boxShadow).not.toBe('none');
        expect(drawerStyles.height).toBeGreaterThan(500);
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
        const footerInner = document.querySelector('body > footer.emdash-site-footer .footer-inner');
        const h1Style = h1 ? getComputedStyle(h1) : null;
        const navStyle = nav ? getComputedStyle(nav) : null;
        const footerStyle = footer ? getComputedStyle(footer) : null;
        const footerInnerStyle = footerInner ? getComputedStyle(footerInner) : null;
        return {
          bodyText: getComputedStyle(document.body).color,
          bodyBg: getComputedStyle(document.body).backgroundColor,
          h1Color: h1Style?.color ?? null,
          h1Bg: h1Style?.backgroundImage ?? null,
          navBg: navStyle?.backgroundColor ?? null,
          footerBg: footerStyle?.backgroundColor ?? null,
          footerTextAlign: footerStyle?.textAlign ?? null,
          footerInnerJustifyItems: footerInnerStyle?.justifyItems ?? null,
          css: [...document.styleSheets].map((sheet) => sheet.href).filter(Boolean),
        };
      });
      expect(styles.bodyText).toBe('rgb(47, 54, 49)');
      if (styles.h1Color) expect(styles.h1Color).toBe('rgb(47, 54, 49)');
      if (styles.h1Bg) expect(styles.h1Bg).toBe('none');
      expect(styles.navBg).toContain('250, 247, 240');
      expect(styles.footerBg).toBe('rgb(246, 241, 231)');
      expect(styles.footerTextAlign).toBe('left');
      expect(styles.footerInnerJustifyItems).toBe('start');
      expect(JSON.stringify(styles)).not.toContain('rgb(102, 126, 234)');
      expect(JSON.stringify(styles)).not.toContain('rgb(118, 75, 162)');

      if (libraryIndexRoutes.has(route.name)) {
        const localNav = page.locator('.breadcrumb, .breadcrumbs, .page-subnav, .subnav, .type-subnav, .type-nav, .container > nav.nav').first();
        await expect(localNav).toBeVisible();
        const localNavStyles = await localNav.evaluate((el) => {
          const style = getComputedStyle(el);
          return {
            display: style.display,
            flexWrap: style.flexWrap,
            textAlign: style.textAlign,
            backgroundColor: style.backgroundColor,
            borderRadius: style.borderRadius,
          };
        });
        expect(localNavStyles.display).toBe('flex');
        expect(localNavStyles.flexWrap).toBe('wrap');
        expect(localNavStyles.textAlign).toBe('left');
      }

      if (route.name === 'type-quiz') {
        const question = page.locator('.question-text').first();
        await expect(question).toBeVisible();
        const questionStyles = await question.evaluate((el) => {
          const style = getComputedStyle(el);
          const card = el.closest('.question-card');
          const cardStyle = card ? getComputedStyle(card) : null;
          return { color: style.color, backgroundColor: cardStyle?.backgroundColor ?? getComputedStyle(document.body).backgroundColor };
        });
        expect(questionStyles.color).toBe('rgb(47, 54, 49)');
        expect(contrastRatio(questionStyles.color, questionStyles.backgroundColor)).toBeGreaterThanOrEqual(7);
      }
    });
  }
});
