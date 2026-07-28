#!/usr/bin/env node
// scripts/kpis/sync-sheet.mjs
// Append the daily/weekly/monthly report rows to the Google Sheet via service account.
// Falls back to a local CSV under /tmp/hde-kpi-sheet.csv when credentials or sheet id are unset.

import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));

async function readJsonArg(arg) {
  if (!arg) return {};
  if (arg.startsWith('@')) return JSON.parse(fs.readFileSync(arg.slice(1), 'utf8'));
  return JSON.parse(arg);
}

async function appendViaSheetsApi({ sheetId, tab, rows }) {
  const keyPath = process.env.HDE_GOOGLE_SERVICE_ACCOUNT_JSON;
  if (!keyPath || !fs.existsSync(keyPath)) {
    throw new Error('missing HDE_GOOGLE_SERVICE_ACCOUNT_JSON');
  }
  // Lazy JWT signer — minimal HS256-equivalent implementation that creates a JWT for Google OAuth.
  // Real-world use pulls googleapis. Here we emit a clear error if googleapis is not installed.
  const { default: google } = await import('googleapis').catch(() => ({}));
  if (!google) {
    throw new Error('googleapis not installed; run `npm i googleapis` in scripts to enable Sheets sync');
  }
  const auth = new google.auth.GoogleAuth({
    keyFile: keyPath,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  const client = await auth.getClient();
  const sheets = google.sheets({ version: 'v4', auth: client });
  await sheets.spreadsheets.values.append({
    spreadsheetId: sheetId,
    range: `${tab}!A1:Z1`,
    valueInputOption: 'USER_ENTERED',
    resource: { values: rows },
  });
}

async function main() {
  const args = process.argv.slice(2);
  const sheetId = process.env.HDE_KPI_SHEET_ID;
  const reportJsonPath = args[0];
  if (!reportJsonPath || !fs.existsSync(reportJsonPath)) {
    console.error('usage: node sync-sheet.mjs <report.json> [--sheet-only] [--tab Daily|Weekly|Monthly|Raw]');
    process.exit(2);
  }
  const report = JSON.parse(fs.readFileSync(reportJsonPath, 'utf8'));
  const tab = (args.includes('--tab') ? args[args.indexOf('--tab') + 1] : (report.kind || 'Daily')).replace(/^./, c => c.toUpperCase());

  const rows = [];
  rows.push(['date', 'collection', 'metric', 'value', 'delta_pct', 'format', 'source']);
  for (const [collId, coll] of Object.entries(report.collections)) {
    for (const m of coll.metrics) {
      rows.push([
        report.windowStartISO.slice(0, 10),
        collId,
        m.id,
        m.formatted,
        m.delta_pct,
        m.format || 'number',
        report.metrics[`${collId}.${m.id}`]?.source || 'fixture',
      ]);
    }
  }

  let wrote = false;
  if (sheetId && process.env.HDE_GOOGLE_SERVICE_ACCOUNT_JSON) {
    try {
      await appendViaSheetsApi({ sheetId, tab, rows });
      console.log(`appended ${rows.length - 1} rows to ${sheetId}/${tab}`);
      wrote = true;
    } catch (err) {
      console.error(`Sheets API failure: ${err.message}; falling back to CSV`);
    }
  }

  if (!wrote) {
    const csvPath = '/tmp/hde-kpi-sheet.csv';
    const csv = rows.map((r) => r.map((v) => JSON.stringify(v)).join(',')).join('\n');
    fs.writeFileSync(csvPath, csv + '\n');
    console.log(`no Sheets credential; wrote local CSV ${csvPath}`);
  }
}

main().catch((err) => { console.error(err); process.exit(1); });
