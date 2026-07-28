#!/usr/bin/env node
import fs from 'node:fs';

const baseUrl = (process.env.HDE_PRODUCTION_URL || 'https://humandesignengine.com').replace(/\/$/, '');
const sitemapUrl = `${baseUrl}/sitemap.xml`;
const expectedGaId = process.env.HDE_EXPECTED_GA_ID || 'G-Q6TPL08VM7';
const timeoutMs = Number(process.env.HDE_ANALYTICS_TIMEOUT_MS || 15000);
const concurrency = Number(process.env.HDE_ANALYTICS_CONCURRENCY || 8);
const outputPath = process.env.HDE_ANALYTICS_OUTPUT || '/tmp/hde-live-analytics-coverage.json';
const eventRoutes = [
  { route: '/buy-report/', expectedEvent: 'begin_checkout' },
  { route: '/checkout/pay/', expectedEvent: 'add_payment_info' },
  { route: '/success/', expectedEvent: 'purchase' },
];

function countMatches(text, pattern) {
  return [...text.matchAll(pattern)].length;
}

async function fetchText(url) {
    const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Ned-HDE-analytics-coverage/1.0 (+https://humandesignengine.com)',
        Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
      redirect: 'follow',
    });
    const body = await response.text();
    return { url, status: response.status, finalUrl: response.url, ok: response.ok, body };
  } catch (error) {
    return { url, status: 0, finalUrl: url, ok: false, body: '', error: `${error.name || 'Error'}: ${error.message}` };
  } finally {
    clearTimeout(timer);
  }
}

function parseSitemap(xml) {
  const urls = [...xml.matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/g)].map((match) => match[1].trim());
  return [...new Set(urls)].sort();
}


// Scan body for referenced /_astro/*.js module URLs (Astro client hydration).
function extractAstroModuleUrls(body) {
  const re = /src=["\']([^"\']+?_astro\/[^"\']+\.js)["\']/g;
  const out = [];
  let m;
  while ((m = re.exec(body)) !== null) out.push(m[1]);
  return [...new Set(out)];
}

async function fetchModulesConcat(urls) {
  const texts = await Promise.all(urls.map(async (u) => {
    try {
      const abs = u.startsWith('http') ? u : new URL(u, baseUrl).toString();
      const r = await fetchText(abs);
      return (r && r.body) || '';
    } catch (err) {
      return '';
    }
  }));
  return texts.join('\n');
}

// Extract GA4-recommended event names from an arbitrary text (page body or module body).
function extractGa4EventNames(text) {
  if (!text) return [];
  const fromGtag = [...text.matchAll(/gtag\(\s*['"]event['"]\s*,\s*['"]([^'"]+)['"]/g)].map((m) => m[1]);
  const fromMap = [...text.matchAll(/['"](begin_checkout|add_payment_info|purchase|select_item|select_content|view_item|complete_registration)['"]/g)].map((m) => m[1]);
  return [...new Set([...fromGtag, ...fromMap])];
}

// Augment an inspected page record by combining its body eventNames with module eventNames.
async function augmentPageWithModules(page) {
  const modules = extractAstroModuleUrls(page.body);
  const moduleBody = modules.length ? await fetchModulesConcat(modules) : '';
  const moduleEvents = extractGa4EventNames(moduleBody);
  return { ...page, eventNames: [...new Set([...(page.eventNames || []), ...moduleEvents])] };
}

function inspectHtml(url, status, finalUrl, body, error) {
  const gaScriptCount = countMatches(body, new RegExp(`https://www\\.googletagmanager\\.com/gtag/js\\?id=${expectedGaId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'g'));
  const gaConfigCount = countMatches(body, new RegExp(`gtag\\(\\s*['\"]config['\"]\\s*,\\s*['\"]${expectedGaId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}['\"]`, 'g'));
  const gtmContainerIds = [...body.matchAll(/GTM-[A-Z0-9]+/g)].map((match) => match[0]);
  const gtmContainerCount = gtmContainerIds.length;
  const dataLayerInitCount = countMatches(body, /window\.dataLayer\s*=\s*window\.dataLayer\s*\|\|\s*\[\]/g);
  const eventNamesFromGtag = [...body.matchAll(/gtag\(\s*['"]event['"]\s*,\s*['"]([^'"]+)['"]/g)].map((match) => match[1]);
  // Also catch GA4-recommended event names that are emitted via a name->ga4 dispatcher table (e.g. checkout_report_selected: 'begin_checkout').
  const eventNamesFromMap = [...body.matchAll(/['"](begin_checkout|add_payment_info|purchase|select_item|select_content|view_item|complete_registration)['"]/g)].map((match) => match[1]);
  const eventNames = [...eventNamesFromGtag, ...eventNamesFromMap];
  const hasExpectedGa = gaScriptCount > 0 && gaConfigCount > 0;
  const hasDuplicateGaSnippet = gaScriptCount > 1 || gaConfigCount > 1;
  const hasDuplicateGtmSnippet = gtmContainerCount > 1;
  return {
    url,
    status,
    finalUrl,
    ok: status >= 200 && status < 300,
    error,
    gaScriptCount,
    gaConfigCount,
    dataLayerInitCount,
    gtmContainerIds: [...new Set(gtmContainerIds)],
    gtmContainerCount,
    eventNames: [...new Set(eventNames)],
    hasExpectedGa,
    hasDuplicateGaSnippet,
    hasDuplicateGtmSnippet,
  };
}

async function mapLimit(items, limit, fn) {
  const results = new Array(items.length);
  let nextIndex = 0;
  async function worker() {
    while (nextIndex < items.length) {
      const index = nextIndex++;
      results[index] = await fn(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return results;
}

const startedAt = new Date().toISOString();
const sitemap = await fetchText(sitemapUrl);
if (!sitemap.ok) {
  const result = {
    ok: false,
    startedAt,
    finishedAt: new Date().toISOString(),
    baseUrl,
    sitemapUrl,
    expectedGaId,
    error: `Unable to fetch sitemap: HTTP ${sitemap.status}${sitemap.error ? ` ${sitemap.error}` : ''}`,
  };
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`);
  console.error(result.error);
  process.exit(2);
}

const sitemapUrls = parseSitemap(sitemap.body);
const pageFetches = await mapLimit(sitemapUrls, concurrency, fetchText);
const pagesInspected = pageFetches.map((page) => ({ body: page.body, ...inspectHtml(page.url, page.status, page.finalUrl, page.body, page.error) }));
const pages = await mapLimit(pagesInspected, concurrency, augmentPageWithModules);
const eventChecks = await mapLimit(eventRoutes, Math.min(concurrency, eventRoutes.length), async ({ route, expectedEvent }) => {
  const url = `${baseUrl}${route}`;
  const page = await fetchText(url);
  const inspected0 = { body: page.body, ...inspectHtml(url, page.status, page.finalUrl, page.body, page.error) };
  const inspected = await augmentPageWithModules(inspected0);
  return {
    route,
    url,
    expectedEvent,
    status: inspected.status,
    ok: inspected.ok,
    eventNames: inspected.eventNames,
    hasExpectedEvent: inspected.eventNames.includes(expectedEvent),
    hasExpectedGa: inspected.hasExpectedGa,
    gaScriptCount: inspected.gaScriptCount,
    gaConfigCount: inspected.gaConfigCount,
  };
});

const non200 = pages.filter((page) => !page.ok);
const missingGa = pages.filter((page) => page.ok && !page.hasExpectedGa);
const duplicateGa = pages.filter((page) => page.hasDuplicateGaSnippet);
const duplicateGtm = pages.filter((page) => page.hasDuplicateGtmSnippet);
const missingEvents = eventChecks.filter((check) => check.ok && !check.hasExpectedEvent);
const failedEventRoutes = eventChecks.filter((check) => !check.ok);
const gtmIds = [...new Set(pages.flatMap((page) => page.gtmContainerIds))].sort();

const result = {
  ok: non200.length === 0 && missingGa.length === 0 && duplicateGa.length === 0 && duplicateGtm.length === 0 && missingEvents.length === 0 && failedEventRoutes.length === 0,
  startedAt,
  finishedAt: new Date().toISOString(),
  baseUrl,
  sitemapUrl,
  expectedGaId,
  counts: {
    sitemapUrls: sitemapUrls.length,
    crawledPages: pages.length,
    non200: non200.length,
    pagesMissingExpectedGa: missingGa.length,
    pagesWithDuplicateGaSnippet: duplicateGa.length,
    pagesWithDuplicateGtmSnippet: duplicateGtm.length,
    eventRoutesChecked: eventChecks.length,
    eventRoutesMissingExpectedEvent: missingEvents.length,
    eventRoutesFailed: failedEventRoutes.length,
  },
  gtmIds,
  samples: {
    non200: non200.slice(0, 20).map(({ url, status, finalUrl, error }) => ({ url, status, finalUrl, error })),
    missingGa: missingGa.slice(0, 30).map(({ url, status, gaScriptCount, gaConfigCount }) => ({ url, status, gaScriptCount, gaConfigCount })),
    duplicateGa: duplicateGa.slice(0, 30).map(({ url, gaScriptCount, gaConfigCount }) => ({ url, gaScriptCount, gaConfigCount })),
    duplicateGtm: duplicateGtm.slice(0, 30).map(({ url, gtmContainerCount, gtmContainerIds }) => ({ url, gtmContainerCount, gtmContainerIds })),
    missingEvents: missingEvents.map(({ route, expectedEvent, eventNames, status }) => ({ route, expectedEvent, eventNames, status })),
    failedEventRoutes: failedEventRoutes.map(({ route, status, url }) => ({ route, status, url })),
  },
  eventChecks,
  pages,
};

fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify({ ok: result.ok, outputPath, counts: result.counts, gtmIds }, null, 2));
if (!result.ok) {
  process.exit(1);
}
