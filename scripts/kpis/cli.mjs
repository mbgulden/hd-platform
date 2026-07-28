#!/usr/bin/env node
// scripts/kpis/cli.mjs
// Single CLI wiring build-report → sync-sheet → send-email → render-dashboard.
// Usage:
//   node scripts/kpis/cli.mjs daily   [--start ISO --end ISO --priorStart ISO --priorEnd ISO]
//   node scripts/kpis/cli.mjs weekly
//   node scripts/kpis/cli.mjs monthly
//   node scripts/kpis/cli.mjs dashboard <report.json>

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import url from 'node:url';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));

function runScript(script, args) {
  const cmd = path.join(HERE, script);
  const fullEnv = { ...process.env, HDE_REPO_ROOT: process.env.HDE_REPO_ROOT || HERE };
  return execFileSync(process.execPath, [cmd, ...args], { cwd: HERE, env: fullEnv, encoding: 'utf8', stdio: 'pipe' });
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
    } else out._.push(a);
  }
  return out;
}

async function kindPipeline(kind) {
  const args = parseArgs(process.argv.slice(3));
  const reportArgs = ['build-report.mjs', '--kind', kind];
  if (args.start) reportArgs.push('--start', args.start);
  if (args.end) reportArgs.push('--end', args.end);
  if (args.priorStart) reportArgs.push('--priorStart', args.priorStart);
  if (args.priorEnd) reportArgs.push('--priorEnd', args.priorEnd);
  const jsonPath = `/tmp/kpi-report-${kind}.json`;
  runScript('build-report.mjs', reportArgs.slice(1));
  const htmlPath = jsonPath.replace(/\.json$/, '.html');
  console.log(`[${kind}] built → ${jsonPath}, ${htmlPath}`);

  runScript('sync-sheet.mjs', [jsonPath, '--tab', kind[0].toUpperCase() + kind.slice(1)]);
  console.log(`[${kind}] sheet synced`);

  runScript('send-email.mjs', [jsonPath]);
  console.log(`[${kind}] email rendered`);

  if (process.env.HDE_KPI_DASHBOARD_PATH) {
    runScript('render-dashboard.mjs', [jsonPath, '--out', process.env.HDE_KPI_DASHBOARD_PATH]);
    console.log(`[${kind}] dashboard rendered → ${process.env.HDE_KPI_DASHBOARD_PATH}`);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];
  if (!cmd) {
    console.error('usage: cli.mjs daily|weekly|monthly|dashboard [<report.json>]');
    process.exit(2);
  }
  if (cmd === 'daily' || cmd === 'weekly' || cmd === 'monthly') {
    await kindPipeline(cmd);
  } else if (cmd === 'dashboard') {
    const report = args._[1] || `/tmp/kpi-report-${args.kind || 'daily'}.json`;
    runScript('render-dashboard.mjs', [report, '--out', process.env.HDE_KPI_DASHBOARD_PATH || path.join(HERE, '..', '..', 'docs', 'pwp', 'kpi-dashboard.html')]);
    console.log('dashboard rendered');
  } else {
    console.error(`unknown command: ${cmd}`);
    process.exit(2);
  }
}

main().catch((err) => { console.error(err); process.exit(1); });
