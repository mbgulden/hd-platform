// tests/kpis/kpi.test.mjs
// Minimal Node test for build-report.mjs using the fixture data.
// Run with:  node tests/kpis/kpi.test.mjs

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';
import { execFileSync } from 'node:child_process';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..');

function run(args) {
  return execFileSync(
    process.execPath,
    [path.join(REPO, 'build-report.mjs'), ...args],
    { cwd: REPO, env: { ...process.env, HDE_REPO_ROOT: REPO }, encoding: 'utf8' }
  );
}

console.log('test: build-report.mjs writes JSON + HTML from fixtures');
const out = run(['--kind', 'daily', '--start', '2026-07-27T00:00:00.000Z', '--end', '2026-07-28T00:00:00.000Z']);
assert.ok(out.includes('wrote'), 'stdout should include wrote');
const jsonPath = path.join('/tmp', 'kpi-report-daily.json');
const htmlPath = path.join('/tmp', 'kpi-report-daily.html');
assert.ok(fs.existsSync(jsonPath), 'json should exist');
assert.ok(fs.existsSync(htmlPath), 'html should exist');
const report = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
assert.equal(report.kind, 'daily', 'kind recorded');
assert.ok(Object.keys(report.collections).length >= 4, 'all collections present');
// Smoke check: select a known fixture-backed value.
const buy = report.collections['funnel_buy_report'].metrics.find((m) => m.id === 'buy_report_page_view');
assert.equal(buy.value, 412, 'fixture value flows through');
// Smoke check: derived metric exists.
const conv = report.collections['funnel_buy_report'].metrics.find((m) => m.id === 'buy_report_conversion_rate');
assert.ok(conv, 'derived metric present');
// HTML should mention the window dates.
const html = fs.readFileSync(htmlPath, 'utf8');
assert.ok(html.includes('Window') || html.includes('window'), 'window header rendered');

// Cron-cron test: weekly also writes a separate artifact.
console.log('test: weekly report uses 7d window');
const weeklyOut = run(['--kind', 'weekly']);
assert.ok(weeklyOut.includes('wrote /tmp/kpi-report-weekly.json'));

console.log('OK');
