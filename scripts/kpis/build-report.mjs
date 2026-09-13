#!/usr/bin/env node
// scripts/kpis/build-report.mjs
// Aggregate GA4 + Stripe + Telegram metrics into a single JSON+HTML payload
// using the canonical `kpi-collections.json` definitions.

import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));
const REPO_ROOT = process.env.HDE_REPO_ROOT || HERE;
const COLL_PATH = process.env.HDE_KPI_COLLECTION_PATH
  || (fs.existsSync(path.join(HERE, 'kpi-collections.json'))
      ? path.join(HERE, 'kpi-collections.json')
      : path.join(REPO_ROOT, 'scripts', 'kpis', 'kpi-collections.json'));

const collections = JSON.parse(fs.readFileSync(COLL_PATH, 'utf8'));

const STRIPE_ENABLED = !!process.env.STRIPE_SECRET_KEY;
const GA4_ENABLED = !!process.env.HDE_GOOGLE_SERVICE_ACCOUNT_JSON;
const FIXTURE_PATH = path.join(HERE, 'fixtures', 'kpi-fixtures.json');
const fixtures = fs.existsSync(FIXTURE_PATH) ? JSON.parse(fs.readFileSync(FIXTURE_PATH, 'utf8')) : {};

async function fetchStripeEvents({ windowStartISO, windowEndISO }) {
  if (!STRIPE_ENABLED) {
    return (fixtures.stripe_events || []).filter((e) => e.created_iso >= windowStartISO && e.created_iso < windowEndISO);
  }
  const key = process.env.STRIPE_SECRET_KEY;
  const auth = Buffer.from(`${key}:`).toString('base64');
  const start = Math.floor(Date.parse(windowStartISO) / 1000);
  const end = Math.floor(Date.parse(windowEndISO) / 1000);
  const url1 = `https://api.stripe.com/v1/events?created[gte]=${start}&created[lt]=${end}&limit=200`;
  const res = await fetch(url1, { headers: { Authorization: `Bearer ${auth}` } });
  if (!res.ok) throw new Error(`stripe events fetch failed: ${res.status}`);
  const data = await res.json();
  return (data.data || []).map((e) => {
    const obj = e.data?.object || {};
    return {
      event_id: e.id,
      event_type: e.type,
      created_iso: new Date(e.created * 1000).toISOString(),
      amount_usd: (obj.amount_total || 0) / 100,
      metadata: obj.metadata || {},
      metadata_funnel: obj.metadata?.funnel || '',
      customer_email: obj.customer_details?.email || obj.customer_email || '',
    };
  });
}

async function fetchGa4Metrics({ windowStartISO, windowEndISO }) {
  // The real implementation calls the GA4 Data API; for test/dev we use fixtures.
  if (!GA4_ENABLED) return fixtures.ga4_metrics || {};
  throw new Error('GA4 path requires @google-analytics/data runtime.');
}

function matchFilter(filter, e) {
  if (!filter) return true;
  const m = filter.match(/^(\w+)\.(\w+)\s*(==|!=)\s*(\w+)$/);
  if (!m) return true;
  const [, group, key, op, val] = m;
  const left = group === 'metadata' ? e.metadata?.[key] : e[`${group}_${key}`];
  return op === '==' ? left === val : left !== val;
}

function derive({ formula, metrics, priorMetrics }) {
  const expr = formula.replace(/[A-Za-z_][A-Za-z0-9_]*/g, (id) => {
    if (id === 'true' || id === 'false') return id;
    if (metrics[id] !== undefined) return String(metrics[id] || 0);
    if (priorMetrics && priorMetrics[id] !== undefined) return String(priorMetrics[id] || 0);
    return '0';
  });
  if (!/^[\d\s+\-*/().]+$/.test(expr)) return { error: `formula ${formula} could not be evaluated safely` };
  try { return { value: Function(`"use strict";return (${expr})`)() }; }
  catch (err) { return { error: String(err.message) }; }
}

function applyFormat(format, value) {
  if (format === 'percent') return `${(value * 100).toFixed(1)}%`;
  return String(value);
}

function pctChange(now, prior) {
  if (!prior) return now ? 'NEW' : '0%';
  const p = ((now - prior) / prior) * 100;
  const sign = p > 0 ? '▲' : p < 0 ? '▼' : '·';
  return `${sign} ${Math.abs(p).toFixed(0)}%`;
}

function renderHtml(report) {
  const sections = Object.values(report.collections).map((coll) => `
    <h2 style="margin-top:24px;font-family:-apple-system,Inter,sans-serif;color:#2F3631;">${coll.title}</h2>
    <table style="border-collapse:collapse;font-family:-apple-system,Inter,sans-serif;width:100%;max-width:640px;">
      ${coll.metrics.map((m) => `
        <tr>
          <td style="padding:6px 8px;border-bottom:1px solid #eee;color:#5C625E;font-size:14px;">${m.label}</td>
          <td style="padding:6px 8px;border-bottom:1px solid #eee;font-size:14px;font-weight:600;text-align:right;">${m.formatted}</td>
          <td style="padding:6px 8px;border-bottom:1px solid #eee;font-size:12px;color:#8C8275;text-align:right;">${m.delta_pct}</td>
        </tr>
      `).join('')}
    </table>
  `).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><title>[HDE KPI] ${report.kind} report — ${report.windowStartISO.slice(0,10)}</title></head>
    <body style="background:#FAF7F0;margin:0;padding:24px;font-family:-apple-system,Inter,sans-serif;color:#2F3631;">
      <h1 style="margin:0 0 4px 0;">HDE — ${report.kind} KPI report</h1>
      <p style="margin:0;color:#5C625E;">Window ${report.windowStartISO.slice(0,16)} → ${report.windowEndISO.slice(0,16)} UTC</p>
      ${sections}
      <p style="margin-top:32px;color:#8C8275;font-size:12px;">Open the Google Sheet for pivots: <a href="${process.env.HDE_KPI_SHEET_URL || '#'}">${process.env.HDE_KPI_SHEET_URL || '#'}</a></p>
    </body></html>`;
}

async function build({ kind, windowStartISO, windowEndISO, priorWindowStartISO, priorWindowEndISO }) {
  const [stripeEvents, priorStripeEvents, ga4Metrics] = await Promise.all([
    fetchStripeEvents({ windowStartISO, windowEndISO }),
    fetchStripeEvents({ windowStartISO: priorWindowStartISO, windowEndISO: priorWindowEndISO }),
    fetchGa4Metrics({ windowStartISO, windowEndISO }),
  ]);

  const report = { kind, windowStartISO, windowEndISO, generatedAt: new Date().toISOString(), metrics: {}, collections: {} };

  for (const coll of collections.collections) {
    report.collections[coll.id] = {
      title: coll.title,
      source_urls: coll.source_urls || [],
      metrics: [],
    };
    const metrics = {};
    const prior = {};

    for (const metric of coll.metrics) {
      const id = `${coll.id}.${metric.id}`;
      let value = 0;
      let priorValue = 0;

      if (metric.source === 'stripe') {
        const f = (ev) => metric.filter ? matchFilter(metric.filter, ev) : true;
        const evs = stripeEvents.filter((e) => e.event_type === metric.event && f(e));
        const prevs = priorStripeEvents.filter((e) => e.event_type === metric.event && f(e));
        if (metric.field === 'amount_total') {
          value = evs.reduce((acc, e) => acc + (e.amount_usd || 0), 0);
          priorValue = prevs.reduce((acc, e) => acc + (e.amount_usd || 0), 0);
        } else {
          value = evs.length;
          priorValue = prevs.length;
        }
      } else if (metric.source === 'ga4') {
        const m = (ga4Metrics[coll.id] || {})[metric.id] ?? (ga4Metrics[coll.id] || {})[metric.event] ?? 0;
        value = m;
      } else if (metric.source === 'derived') {
        const r = derive({ formula: metric.formula, metrics, priorMetrics: prior });
        value = typeof r.value === 'number' ? r.value : 0;
        const rPrior = derive({ formula: metric.formula, metrics: prior, priorMetrics: {} });
        priorValue = typeof rPrior.value === 'number' ? rPrior.value : 0;
      }

      const entry = { id, label: metric.label, value, prior: priorValue, format: metric.format || 'number' };
      report.metrics[id] = entry;
      metrics[metric.id] = value;
      prior[metric.id] = priorValue;
      report.collections[coll.id].metrics.push({
        id: metric.id,
        label: metric.label,
        value,
        prior: priorValue,
        formatted: applyFormat(metric.format || 'number', value),
        delta_pct: pctChange(value, priorValue),
        format: metric.format,
      });
    }
  }
  report.html = renderHtml(report);
  return report;
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : 'true';
      out[k] = v;
      i++;
    } else {
      out._.push(a);
    }
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const kind = args.kind || 'daily';
  const now = new Date();
  const start = args.start || (() => { const d = new Date(now); d.setUTCHours(0,0,0,0); d.setUTCDate(d.getUTCDate() - (kind === 'daily' ? 1 : kind === 'weekly' ? 7 : 30)); return d.toISOString(); })();
  const end = args.end || (() => { const d = new Date(start); d.setUTCDate(d.getUTCDate() + (kind === 'daily' ? 1 : kind === 'weekly' ? 7 : 30)); return d.toISOString(); })();
  const ps = args.priorStart || (() => { const d = new Date(start); d.setUTCDate(d.getUTCDate() - (kind === 'daily' ? 1 : kind === 'weekly' ? 7 : 30)); return d.toISOString(); })();
  const pe = args.priorEnd || start;

  const report = await build({ kind, windowStartISO: start, windowEndISO: end, priorWindowStartISO: ps, priorWindowEndISO: pe });
  const outJson = args.out || path.join('/tmp', `kpi-report-${kind}.json`);
  fs.writeFileSync(outJson, JSON.stringify(report, null, 2));
  const outHtml = args.outHtml || outJson.replace(/\.json$/, '.html');
  fs.writeFileSync(outHtml, report.html);
  console.log(`wrote ${outJson} + ${outHtml}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
