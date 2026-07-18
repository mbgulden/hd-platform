#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const routesPath = join(root, '.pwp', 'routes.json');
const distDir = join(root, 'dist');
const outputDir = join(root, 'okf', 'output', 'pwp-visual-qa');
const outputPath = join(outputDir, 'analytics.json');

const eventRequirements = [
  {
    route: '/buy-report/',
    name: 'buy-report-checkout-start',
    requiredEvents: ['begin_checkout'],
    reason: 'report purchase CTA must emit checkout intent before Stripe handoff'
  },
  {
    route: '/checkout/pay/',
    name: 'checkout-pay-submit',
    requiredEvents: ['add_payment_info', 'begin_checkout'],
    reason: 'payment form must emit a monetization funnel event before redirect'
  },
  {
    route: '/success/',
    name: 'success-purchase',
    requiredEvents: ['purchase', 'generate_lead'],
    reason: 'success/report-delivery surface must emit a conversion/onboarding event'
  }
];

const htmlForRoute = (routePath) => {
  const cleanPath = routePath.split('?')[0].replace(/^\//, '');
  const candidates = [];
  if (!cleanPath || cleanPath.endsWith('/')) {
    candidates.push(join(distDir, cleanPath, 'index.html'));
  } else if (cleanPath.endsWith('.html')) {
    candidates.push(join(distDir, cleanPath));
  } else {
    candidates.push(join(distDir, cleanPath, 'index.html'));
    candidates.push(join(distDir, `${cleanPath}.html`));
  }
  const found = candidates.find((candidate) => existsSync(candidate));
  return found ? { path: found, html: readFileSync(found, 'utf8') } : { path: candidates[0], html: null };
};

const hasGlobalAnalytics = (html) => {
  const hasTagLoader = /googletagmanager\.com\/(gtag\/js|gtm\.js)/.test(html);
  const hasDataLayer = /window\.dataLayer\s*=\s*window\.dataLayer\s*\|\|\s*\[\]/.test(html);
  const hasConfig = /gtag\(['"]config['"],\s*['"]G-[A-Z0-9]+['"]/.test(html) || /GTM-[A-Z0-9]+/.test(html);
  return hasTagLoader && hasDataLayer && hasConfig;
};

const hasAnyRequiredEvent = (html, eventNames) => {
  const hasAnalyticsApi = /window\.gtag|gtag\(['"]event['"]|dataLayer\.push/.test(html);
  if (!hasAnalyticsApi) return false;
  return eventNames.some((eventName) => {
    const quoted = eventName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return new RegExp(`['\"]${quoted}['\"]`).test(html);
  });
};

if (!existsSync(routesPath)) {
  throw new Error(`Missing PWP routes file: ${routesPath}`);
}
if (!existsSync(distDir)) {
  throw new Error(`Missing build output: ${distDir}. Run npm run build before analytics verification.`);
}

const routes = JSON.parse(readFileSync(routesPath, 'utf8')).routes || [];
const globalChecks = routes.map((route) => {
  const rendered = htmlForRoute(route.path);
  const ok = Boolean(rendered.html && hasGlobalAnalytics(rendered.html));
  return {
    name: route.name,
    route: route.path,
    file: rendered.path,
    ok,
    check: 'global-ga-or-gtm'
  };
});

const eventChecks = eventRequirements.map((requirement) => {
  const rendered = htmlForRoute(requirement.route);
  const ok = Boolean(rendered.html && hasAnyRequiredEvent(rendered.html, requirement.requiredEvents));
  return {
    name: requirement.name,
    route: requirement.route,
    file: rendered.path,
    ok,
    check: 'event-hook',
    requiredEvents: requirement.requiredEvents,
    reason: requirement.reason,
    skipped: !rendered.html
  };
});

const failures = [...globalChecks, ...eventChecks].filter((check) => !check.ok);
const summary = {
  ok: failures.length === 0,
  generatedAt: new Date().toISOString(),
  globalRoutesChecked: globalChecks.length,
  eventRoutesChecked: eventChecks.length,
  failures,
  globalChecks,
  eventChecks
};

mkdirSync(outputDir, { recursive: true });
writeFileSync(outputPath, JSON.stringify(summary, null, 2));

if (failures.length > 0) {
  console.error(`[pwp:analytics] FAIL: ${failures.length} analytics requirement(s) missing. Evidence: ${outputPath}`);
  for (const failure of failures) {
    console.error(`- ${failure.route} (${failure.check}) -> ${failure.file}`);
  }
  process.exit(1);
}

console.log(`[pwp:analytics] ok: ${globalChecks.length} routed pages have GA/GTM and ${eventChecks.length} funnel surfaces have event hooks. Evidence: ${outputPath}`);
