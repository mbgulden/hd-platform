import { test, expect } from '@playwright/test';

const stagingUrl = process.env.PWP_STAGING_URL;

test.describe('local route flows', () => {
  test('free reading generator loads the embedded widget shell', async ({ page }) => {
    await page.goto('/free-human-design-reading-generator/');
    await expect(page.locator('body')).toContainText('Free Human Design Reading Generator');
  });

  test('buy report page exposes the Human Design blueprint CTA', async ({ page }) => {
    await page.goto('/buy-report/');
    await expect(page.locator('body')).toContainText('Your Human Design Blueprint');
  });


  test('buy report checkout emits funnel analytics through Stripe redirect', async ({ page }) => {
    await page.route('**/api/checkout/create-session', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          url: 'https://checkout.stripe.com/c/pay/cs_test_funnel_123',
          session_id: 'cs_test_funnel_123',
        }),
      });
    });
    await page.route('https://checkout.stripe.com/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'text/html', body: '<h1>Stripe checkout</h1>' });
    });

    const events: Array<{ name: string; detail: Record<string, unknown> }> = [];
    let sawRedirect: (value: void) => void;
    const redirectEvent = new Promise<void>((resolve) => { sawRedirect = resolve; });
    await page.exposeFunction('recordHdeCheckoutEvent', (event: { name: string; detail: Record<string, unknown> }) => {
      events.push(event);
      if (event.name === 'checkout_stripe_redirect') sawRedirect();
    });

    await page.goto('/buy-report/');
    await page.evaluate(() => {
      for (const name of [
        'checkout_report_selected',
        'checkout_cta_clicked',
        'checkout_session_create_started',
        'checkout_session_created',
        'checkout_stripe_redirect',
      ]) {
        window.addEventListener(`hde:${name}`, (event) => {
          (window as any).recordHdeCheckoutEvent({ name, detail: (event as CustomEvent).detail });
        });
      }
    });

    await page.locator('#card-bundle').click();
    await page.locator('#name').fill('Ada Lovelace');
    await page.locator('#email').fill('ada@example.com');
    await page.locator('#birthdate').fill('1815-12-10');
    await page.locator('#birthtime').fill('08:30');
    await page.locator('#location').fill('London, UK');

    await Promise.all([
      redirectEvent,
      page.locator('#buyBtn').click(),
    ]);

    expect(events.map((event) => event.name)).toEqual([
      'checkout_report_selected',
      'checkout_cta_clicked',
      'checkout_session_create_started',
      'checkout_session_created',
      'checkout_stripe_redirect',
    ]);
    expect(events.at(-1)?.detail).toMatchObject({
      funnel: 'report_checkout',
      report: 'bundle',
      checkout_session_id: 'cs_test_funnel_123',
      stripe_redirect_host: 'checkout.stripe.com',
    });
  });

  test('success page emits purchase confirmation analytics after session lookup', async ({ page }) => {
    await page.route('**/api/checkout/session?session_id=cs_test_success', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          email: 'ada@example.com',
          report: 'bundle',
          is_premium: false,
        }),
      });
    });

    await page.goto('/success?session_id=cs_test_success');
    await page.waitForFunction(() =>
      (window as any).dataLayer?.some((event: any) => event.event === 'checkout_purchase_confirmed')
    );

    const purchaseEvent = await page.evaluate(() =>
      (window as any).dataLayer.find((event: any) => event.event === 'checkout_purchase_confirmed')
    );
    expect(purchaseEvent).toMatchObject({
      funnel: 'report_checkout',
      checkout_session_id: 'cs_test_success',
      lookup_type: 'session_id',
      report: 'bundle',
    });
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
