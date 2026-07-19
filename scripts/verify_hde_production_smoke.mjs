#!/usr/bin/env node
/** Static contract verifier for GRO-4008 production smoke cron. */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root = path.resolve(new URL('..', import.meta.url).pathname, '..');
const smokePath = path.join(root, 'scripts', 'hde-production-smoke.mjs');
const packagePath = path.join(root, 'package.json');
const docsPath = path.join(root, 'scripts', 'docs', 'gro-4008-production-smoke-cron.md');

function read(file) {
  return fs.readFileSync(file, 'utf8');
}

function requireIncludes(haystack, needle, label) {
  if (!haystack.includes(needle)) {
    throw new Error(`missing ${label}: ${needle}`);
  }
}

const smoke = read(smokePath);
const pkg = JSON.parse(read(packagePath));
const docs = read(docsPath);

for (const [needle, label] of [
  ['createCheckoutViaPublicApi', 'public checkout API smoke'],
  ['createCheckoutViaStripe', 'direct Stripe fallback'],
  ['verifyStripeSession', 'Stripe unpaid session verification'],
  ["payment_status === 'paid'", 'paid-session safety guard'],
  ['expireStripeSession', 'checkout cleanup/expiration'],
  ['verifyReportDelivery', 'report delivery route probe'],
  ['HDE_SMOKE_ALLOW_REPORT_404', 'no-fixture report route mode'],
  ['HDE_SMOKE_REPORT_URL', 'configured report fixture mode'],
  ['STRIPE_SECRET_KEY', 'Stripe credential source'],
  ['redact(stripeKey)', 'redacted secret reporting'],
]) {
  requireIncludes(smoke, needle, label);
}

if (pkg.scripts['smoke:production'] !== 'node scripts/hde-production-smoke.mjs') {
  throw new Error('package.json missing smoke:production script');
}
if (pkg.scripts['verify:production-smoke'] !== 'node scripts/verify_hde_production_smoke.mjs') {
  throw new Error('package.json missing verify:production-smoke script');
}

for (const [needle, label] of [
  ['*/15 * * * *', 'cron cadence example'],
  ['npm run smoke:production', 'smoke command'],
  ['never completes payment', 'live-safe checkout statement'],
  ['404 is acceptable', 'report route no-fixture behavior'],
  ['STRIPE_SECRET_KEY', 'required Stripe variable docs'],
]) {
  requireIncludes(docs, needle, label);
}

console.log('OK: GRO-4008 production smoke contract is present and live-safe.');
process.exit(0);
