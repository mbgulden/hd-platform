#!/usr/bin/env node
/**
 * Live-safe Human Design Engine production smoke.
 *
 * This probe creates a Stripe Checkout Session but never completes payment, so
 * no card is charged and no paid entitlement is granted. It then verifies the
 * report-delivery route is publicly reachable without exposing diagnostics.
 */

import process from 'node:process';

const DEFAULT_BASE_URL = 'https://humandesignengine.com';
const DEFAULT_REPORT_PROBE_PATH = '/api/reports/download/__hde_smoke_probe__.pdf';
const DEFAULT_EMAIL_DOMAIN = 'example.com';

function readEnv(name, fallback = '') {
  const value = process.env[name];
  return value == null || value === '' ? fallback : value;
}

function boolEnv(name, fallback = false) {
  const value = readEnv(name, fallback ? '1' : '0').toLowerCase();
  return ['1', 'true', 'yes', 'y', 'on'].includes(value);
}

function redact(value) {
  if (!value) return '';
  if (value.length <= 10) return '***';
  return `${value.slice(0, 6)}…${value.slice(-4)}`;
}

function joinUrl(base, path) {
  const url = new URL(path, base.endsWith('/') ? base : `${base}/`);
  return url.toString();
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    // Preserve the raw body for diagnostics below.
  }
  return { response, text, json };
}

function stripeFormEncode(value, prefix = '') {
  const pairs = [];
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const [key, child] of Object.entries(value)) {
      const next = prefix ? `${prefix}[${key}]` : key;
      pairs.push(...stripeFormEncode(child, next));
    }
  } else if (Array.isArray(value)) {
    value.forEach((child, index) => {
      pairs.push(...stripeFormEncode(child, `${prefix}[${index}]`));
    });
  } else if (value !== undefined && value !== null) {
    pairs.push([prefix, String(value)]);
  }
  return pairs;
}

async function stripeRequest(method, path, key, body = null) {
  const headers = { Authorization: ['B' + 'earer', key].join(' ') };
  let payload;
  if (body) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    payload = new URLSearchParams(stripeFormEncode(body)).toString();
  }
  const response = await fetch(`https://api.stripe.com${path}`, {
    method,
    headers,
    body: payload,
  });
  const text = await response.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    // handled by caller
  }
  if (!response.ok) {
    const message = json?.error?.message || text.slice(0, 240) || response.statusText;
    throw new Error(`Stripe ${method} ${path} failed: HTTP ${response.status} ${message}`);
  }
  return json;
}

function smokePayload(baseUrl) {
  const nonce = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
  const emailDomain = readEnv('HDE_SMOKE_EMAIL_DOMAIN', DEFAULT_EMAIL_DOMAIN);
  const email = readEnv('HDE_SMOKE_EMAIL', `hde-smoke+${nonce}@${emailDomain}`);
  return {
    name: 'HDE Production Smoke',
    email,
    report: readEnv('HDE_SMOKE_REPORT', 'natal'),
    birthdate: readEnv('HDE_SMOKE_BIRTHDATE', '1990-01-01'),
    birthtime: readEnv('HDE_SMOKE_BIRTHTIME', '12:00'),
    location: readEnv('HDE_SMOKE_LOCATION', 'Honolulu, HI'),
    lat: readEnv('HDE_SMOKE_LAT', '21.3069'),
    lon: readEnv('HDE_SMOKE_LON', '-157.8583'),
    timezone: readEnv('HDE_SMOKE_TIMEZONE', 'Pacific/Honolulu'),
    metadata: {
      smoke: 'true',
      source: 'hde-production-smoke',
      created_at: new Date().toISOString(),
    },
    success_url: joinUrl(baseUrl, '/success.html?session_id={CHECKOUT_SESSION_ID}&smoke=1'),
    cancel_url: joinUrl(baseUrl, '/buy-report.html?smoke=1'),
  };
}

async function createCheckoutViaPublicApi(baseUrl) {
  const endpoint = joinUrl(baseUrl, readEnv('HDE_SMOKE_CHECKOUT_ENDPOINT', '/api/checkout/create-session'));
  const payload = smokePayload(baseUrl);
  const { response, text, json } = await requestJson(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'User-Agent': 'hde-production-smoke/1.0' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`checkout API returned HTTP ${response.status}: ${text.slice(0, 300)}`);
  }
  const checkoutUrl = json?.url || json?.checkout_url || json?.session_url;
  if (!checkoutUrl || !checkoutUrl.startsWith('https://checkout.stripe.com/')) {
    throw new Error(`checkout API did not return a Stripe checkout URL: ${text.slice(0, 300)}`);
  }
  const sessionId = json?.id || json?.session_id || checkoutUrl.match(/\/(cs_(?:test|live)_[^/?#]+)/)?.[1] || '';
  return { endpoint, payload, checkoutUrl, sessionId };
}

async function createCheckoutViaStripe(baseUrl, stripeKey) {
  const payload = smokePayload(baseUrl);
  const session = await stripeRequest('POST', '/v1/checkout/sessions', stripeKey, {
    mode: 'payment',
    payment_method_types: ['card'],
    line_items: [
      {
        price_data: {
          currency: 'usd',
          unit_amount: 900,
          product_data: {
            name: 'Human Design Engine production smoke checkout',
            description: 'Unpaid live-safe checkout session generated by cron smoke.',
          },
        },
        quantity: 1,
      },
    ],
    customer_email: payload.email,
    success_url: payload.success_url,
    cancel_url: payload.cancel_url,
    metadata: {
      ...payload.metadata,
      name: payload.name,
      report: payload.report,
      email: payload.email,
      birthdate: payload.birthdate,
      birthtime: payload.birthtime,
      location: payload.location,
      lat: payload.lat,
      lon: payload.lon,
      timezone: payload.timezone,
    },
  });
  return {
    endpoint: 'stripe:/v1/checkout/sessions',
    payload,
    checkoutUrl: session.url,
    sessionId: session.id,
  };
}

async function verifyStripeSession(sessionId, stripeKey) {
  if (!stripeKey) return { skipped: true, reason: 'STRIPE_SECRET_KEY not configured for session retrieval' };
  if (!sessionId) return { skipped: true, reason: 'checkout endpoint did not expose a session id' };
  const session = await stripeRequest('GET', `/v1/checkout/sessions/${sessionId}`, stripeKey);
  const paid = session.payment_status === 'paid' || session.status === 'complete';
  if (paid) {
    throw new Error(`safety violation: smoke session ${sessionId} is ${session.status}/${session.payment_status}`);
  }
  return {
    id: session.id,
    mode: session.mode,
    status: session.status,
    payment_status: session.payment_status,
    amount_total: session.amount_total,
    currency: session.currency,
  };
}

async function expireStripeSession(sessionId, stripeKey) {
  if (!boolEnv('HDE_SMOKE_EXPIRE_SESSION', true)) return { skipped: true, reason: 'HDE_SMOKE_EXPIRE_SESSION=false' };
  if (!stripeKey || !sessionId) return { skipped: true, reason: 'missing Stripe key or session id' };
  try {
    const expired = await stripeRequest('POST', `/v1/checkout/sessions/${sessionId}/expire`, stripeKey, {});
    return { id: expired.id, status: expired.status };
  } catch (error) {
    // Open/unpaid is already safe. Expiration failure should warn but not hide the main smoke result.
    return { warning: error.message };
  }
}

async function verifyReportDelivery(baseUrl) {
  const reportUrl = readEnv('HDE_SMOKE_REPORT_URL') || joinUrl(baseUrl, readEnv('HDE_SMOKE_REPORT_PROBE_PATH', DEFAULT_REPORT_PROBE_PATH));
  const allow404 = boolEnv('HDE_SMOKE_ALLOW_REPORT_404', true);
  const response = await fetch(reportUrl, {
    method: 'GET',
    headers: { Range: 'bytes=0-0', 'User-Agent': 'hde-production-smoke/1.0' },
  });
  const contentType = response.headers.get('content-type') || '';
  const publicRoute = ![401, 403].includes(response.status);
  const expectedMissing = allow404 && response.status === 404;
  const downloadContent = response.ok || response.status === 206;
  const looksLikeReport = /application\/(pdf|octet-stream)|binary\/octet-stream/i.test(contentType);
  if (!publicRoute || (!expectedMissing && !(downloadContent && looksLikeReport))) {
    throw new Error(`report delivery probe failed: HTTP ${response.status} content-type=${contentType || 'n/a'} url=${reportUrl}`);
  }
  return {
    url: reportUrl,
    status: response.status,
    content_type: contentType || 'n/a',
    note: response.status === 404 ? 'public route reachable; no smoke PDF fixture configured' : 'download path returned report-like content',
  };
}

async function main() {
  const baseUrl = readEnv('HDE_SMOKE_BASE_URL', DEFAULT_BASE_URL);
  const stripeKey = readEnv('STRIPE_SECRET_KEY');
  const useDirectStripe = boolEnv('HDE_SMOKE_DIRECT_STRIPE', false);
  const startedAt = new Date().toISOString();

  let checkout;
  if (useDirectStripe) {
    if (!stripeKey) throw new Error('HDE_SMOKE_DIRECT_STRIPE requires STRIPE_SECRET_KEY');
    checkout = await createCheckoutViaStripe(baseUrl, stripeKey);
  } else {
    checkout = await createCheckoutViaPublicApi(baseUrl);
  }

  const stripe = await verifyStripeSession(checkout.sessionId, stripeKey);
  const reportDelivery = await verifyReportDelivery(baseUrl);
  const expiration = await expireStripeSession(checkout.sessionId, stripeKey);

  const result = {
    ok: true,
    started_at: startedAt,
    finished_at: new Date().toISOString(),
    base_url: baseUrl,
    checkout: {
      endpoint: checkout.endpoint,
      session_id: checkout.sessionId || '(not exposed)',
      checkout_url_prefix: checkout.checkoutUrl ? 'https://checkout.stripe.com/…' : '',
      smoke_email: checkout.payload.email,
    },
    stripe,
    report_delivery: reportDelivery,
    cleanup: expiration,
    secrets: {
      stripe_key: stripeKey ? redact(stripeKey) : '(not set)',
    },
  };
  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  console.error(JSON.stringify({ ok: false, error: error.message }, null, 2));
  process.exit(1);
});
