#!/usr/bin/env node
/**
 * GRO-4009 final green proof runner.
 * Runs the full portable website proof, Lighthouse (via pwp:verify), and the
 * live-safe production API smoke, then writes a redacted evidence bundle.
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();
const outputDir = path.join(root, 'okf', 'output', 'pwp-visual-qa');
const resultPath = path.join(outputDir, 'gro-4009-final-green-proof.json');
const reportPath = path.join(root, 'scripts', 'docs', 'gro-4009-final-green-proof-report.md');

function run(name, command, args, env = process.env) {
  const started = new Date().toISOString();
  console.log(`\n[gro-4009] ${name}: ${command} ${args.join(' ')}`);
  const result = spawnSync(command, args, {
    cwd: root,
    env,
    shell: false,
    encoding: 'utf8',
    maxBuffer: 20 * 1024 * 1024,
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  return {
    name,
    command: `${command} ${args.join(' ')}`,
    started_at: started,
    finished_at: new Date().toISOString(),
    exit_code: result.status ?? 1,
    stdout_tail: tail(result.stdout),
    stderr_tail: tail(result.stderr),
  };
}

function tail(text = '', max = 7000) {
  return text.length > max ? text.slice(-max) : text;
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (error) {
    return { error: error.message };
  }
}

function listFiles(dir) {
  try {
    return fs.readdirSync(dir).sort();
  } catch {
    return [];
  }
}

function hasGreenLighthouseArtifacts() {
  const lighthouseDir = path.join(outputDir, 'lighthouse');
  const files = listFiles(lighthouseDir);
  return {
    output_dir: path.relative(root, lighthouseDir),
    files,
    has_reports: files.some((file) => file.endsWith('.html') || file.endsWith('.json')),
  };
}

function redactSmokeJson(raw) {
  try {
    const parsed = JSON.parse(raw);
    if (parsed?.checkout?.session_id) parsed.checkout.session_id = parsed.checkout.session_id.replace(/^(cs_(?:test|live)_).+$/, '$1…redacted');
    if (parsed?.checkout?.smoke_email) parsed.checkout.smoke_email = parsed.checkout.smoke_email.replace(/\+[^@]+@/, '+…@');
    return parsed;
  } catch {
    return null;
  }
}

function writeReport(bundle) {
  const pwp = bundle.pwp_summary;
  const lh = bundle.lighthouse;
  const smoke = bundle.production_smoke;
  const green = bundle.ok ? 'GREEN' : 'NOT GREEN';
  const lines = [
    '# GRO-4009 Final PWP + Lighthouse + API Proof Report',
    '',
    `Status: **${green}**`,
    `Generated: ${bundle.finished_at}`,
    '',
    '## Commands',
    '',
    ...bundle.commands.map((cmd) => `- \`${cmd.command}\` → exit ${cmd.exit_code}`),
    '',
    '## PWP proof',
    '',
    `- Summary: \`${path.relative(root, path.join(outputDir, 'summary.json'))}\``,
    `- PWP ok: \`${Boolean(pwp?.ok)}\``,
    `- Steps: ${Array.isArray(pwp?.results) ? pwp.results.map((r) => `${r.name}=exit ${r.exitCode}`).join(', ') : 'unavailable'}`,
    '',
    '## Lighthouse proof',
    '',
    `- Output directory: \`${lh.output_dir}\``,
    `- Report artifacts: ${lh.files.length ? lh.files.map((f) => `\`${f}\``).join(', ') : 'none'}`,
    `- Reports present: \`${lh.has_reports}\``,
    '',
    '## Production API proof',
    '',
    smoke.ok
      ? `- Smoke ok: \`true\` (${smoke.base_url})`
      : `- Smoke ok: \`false\` — ${smoke.error || 'see command output'}`,
    smoke.checkout?.endpoint ? `- Checkout endpoint: \`${smoke.checkout.endpoint}\`` : '- Checkout endpoint: unavailable',
    smoke.stripe?.status ? `- Stripe session safety: \`${smoke.stripe.status}/${smoke.stripe.payment_status}\`` : '- Stripe session safety: unavailable',
    smoke.report_delivery?.status ? `- Report delivery: HTTP ${smoke.report_delivery.status} ${smoke.report_delivery.content_type}` : '- Report delivery: unavailable',
    smoke.cleanup?.status || smoke.cleanup?.warning ? `- Cleanup: ${smoke.cleanup.status || smoke.cleanup.warning}` : '- Cleanup: unavailable',
    '',
    '## Notes',
    '',
    '- Secrets are redacted. The smoke creates an unpaid checkout session only and attempts to expire it.',
    '- This report is intentionally not marked green unless PWP, Lighthouse artifacts, and the live-safe API smoke all pass in the same run.',
    '',
  ];
  fs.writeFileSync(reportPath, `${lines.join('\n')}\n`);
}

fs.mkdirSync(outputDir, { recursive: true });
const commands = [];
commands.push(run('pwp verify', 'npm', ['run', 'pwp:verify']));
let smokeJson = {};
if (commands.at(-1).exit_code === 0) {
  const smoke = run('production smoke', 'npm', ['run', 'smoke:production']);
  commands.push(smoke);
  smokeJson = redactSmokeJson(smoke.stdout_tail) || { ok: false, error: smoke.stderr_tail || smoke.stdout_tail };
}
const pwpSummary = readJson(path.join(outputDir, 'summary.json'));
const lighthouse = hasGreenLighthouseArtifacts();
const ok = commands.every((cmd) => cmd.exit_code === 0) && pwpSummary.ok === true && lighthouse.has_reports && smokeJson.ok === true;
const bundle = {
  ok,
  started_at: commands[0]?.started_at || new Date().toISOString(),
  finished_at: new Date().toISOString(),
  commands,
  pwp_summary: pwpSummary,
  lighthouse,
  production_smoke: smokeJson,
  artifacts: {
    json: path.relative(root, resultPath),
    markdown_report: path.relative(root, reportPath),
  },
};
fs.writeFileSync(resultPath, JSON.stringify(bundle, null, 2));
writeReport(bundle);
console.log(`\n[gro-4009] evidence: ${path.relative(root, resultPath)}`);
console.log(`[gro-4009] report: ${path.relative(root, reportPath)}`);
process.exit(ok ? 0 : 1);
