#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';

const outputDir = 'okf/output/pwp-visual-qa';
mkdirSync(outputDir, { recursive: true });

const steps = [
  ['build', 'npm', ['run', 'build']],
  ['analytics', 'node', ['scripts/pwp-analytics-check.mjs']],
  ['visual', 'npm', ['run', 'qa:visual']],
  ['a11y', 'npm', ['run', 'qa:a11y']],
  ['flows', 'npm', ['run', 'qa:flows']],
  ['lighthouse', 'npm', ['run', 'qa:lighthouse']],
  ['links', 'npm', ['run', 'qa:links']]
];

const results = [];
for (const [name, cmd, args] of steps) {
  const started = new Date().toISOString();
  console.log(`\n[pwp:verify] ${name}: ${cmd} ${args.join(' ')}`);
  const result = spawnSync(cmd, args, { stdio: 'inherit', shell: false, env: process.env });
  const finished = new Date().toISOString();
  results.push({ name, command: `${cmd} ${args.join(' ')}`, exitCode: result.status, started, finished });
  if (result.status !== 0) {
    writeFileSync(`${outputDir}/summary.json`, JSON.stringify({ ok: false, failed: name, results }, null, 2));
    process.exit(result.status ?? 1);
  }
}
writeFileSync(`${outputDir}/summary.json`, JSON.stringify({ ok: true, results }, null, 2));
console.log(`\n[pwp:verify] ok; evidence written to ${outputDir}`);
