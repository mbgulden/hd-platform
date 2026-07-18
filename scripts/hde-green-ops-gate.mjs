#!/usr/bin/env node
/**
 * HDE GREEN operational reliability gate.
 *
 * GRO-4004 is the parent safety epic. This script keeps the parent honest: the
 * category is not green until every dependent child has concrete verification.
 * With LINEAR_API_KEY set, it reads live Linear state; without it, it emits the
 * static dependency order so cron/CI can still publish the required work queue.
 */

const CHILDREN = [
  {
    id: 'GRO-4005',
    title: 'Add Cloudflare Pages security headers safely',
    gate: 'security_headers',
    requiredEvidence: ['Cloudflare/static header configuration', 'production or staging header curl proof'],
  },
  {
    id: 'GRO-4006',
    title: 'Fix free-reading CLS/layout stability',
    gate: 'layout_stability',
    requiredEvidence: ['CLS-focused build/UI proof', 'before/after layout evidence'],
  },
  {
    id: 'GRO-4007',
    title: 'Protect public API health/diagnostic routing',
    gate: 'public_api_routing',
    requiredEvidence: ['public route allowlist/denylist proof', 'health endpoint smoke result'],
  },
  {
    id: 'GRO-4008',
    title: 'Add production smoke cron for checkout/report delivery',
    gate: 'smoke_cron',
    requiredEvidence: ['checkout smoke command', 'report delivery smoke command', 'cron/install note'],
  },
  {
    id: 'GRO-4009',
    title: 'Run final PWP + Lighthouse + API proof and publish green report',
    gate: 'final_green_report',
    requiredEvidence: ['PWP proof', 'Lighthouse proof', 'API proof', 'published green report'],
  },
];

const DONE_STATES = new Set(['Done', 'Canceled', 'Cancelled']);

function parseArgs(argv) {
  const args = { json: false, requireGreen: false };
  for (const arg of argv) {
    if (arg === '--json') args.json = true;
    if (arg === '--require-green') args.requireGreen = true;
  }
  return args;
}

async function linearRequest(query, variables) {
  const token = process.env.LINEAR_API_KEY;
  if (!token) return null;

  const response = await fetch('https://api.linear.app/graphql', {
    method: 'POST',
    headers: {
      Authorization: token,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, variables }),
  });

  const payload = await response.json();
  if (!response.ok || payload.errors) {
    throw new Error(`Linear query failed: ${JSON.stringify(payload.errors ?? payload)}`);
  }
  return payload.data;
}

async function fetchLiveStates() {
  const query = `
    query($ids: [String!]!) {
      issues(filter: { identifier: { in: $ids } }, first: 20) {
        nodes {
          identifier
          title
          state { name type }
          updatedAt
          url
          labels { nodes { name } }
        }
      }
    }
  `;
  const data = await linearRequest(query, { ids: CHILDREN.map((child) => child.id) });
  if (!data) return new Map();
  return new Map(data.issues.nodes.map((issue) => [issue.identifier, issue]));
}

function summarize(child, live) {
  const stateName = live?.state?.name ?? 'UNKNOWN';
  const done = DONE_STATES.has(stateName);
  return {
    ...child,
    state: stateName,
    stateType: live?.state?.type ?? 'UNKNOWN',
    url: live?.url ?? null,
    updatedAt: live?.updatedAt ?? null,
    labels: live?.labels?.nodes?.map((node) => node.name).sort() ?? [],
    done,
    blockingParentGreen: !done,
  };
}

function renderText(report) {
  const lines = [];
  lines.push(`HDE GREEN security/reliability gate: ${report.green ? 'GREEN' : 'NOT GREEN'}`);
  lines.push(`Dependency order: ${report.children.map((child) => child.id).join(' → ')}`);
  lines.push('');
  for (const child of report.children) {
    const marker = child.done ? '✅' : '🟡';
    lines.push(`${marker} ${child.id} — ${child.state} — ${child.title}`);
    lines.push(`   gate: ${child.gate}`);
    lines.push(`   required evidence: ${child.requiredEvidence.join('; ')}`);
  }
  if (report.blockers.length) {
    lines.push('');
    lines.push(`Parent GRO-4004 must stay open until these child gates are green: ${report.blockers.join(', ')}`);
  }
  return lines.join('\n');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const liveStates = await fetchLiveStates();
  const children = CHILDREN.map((child) => summarize(child, liveStates.get(child.id)));
  const blockers = children.filter((child) => child.blockingParentGreen).map((child) => child.id);
  const report = {
    parent: 'GRO-4004',
    title: 'HDE GREEN — Security, performance, and operational reliability',
    generatedAt: new Date().toISOString(),
    liveLinear: liveStates.size > 0,
    dependencyOrder: CHILDREN.map((child) => child.id),
    green: blockers.length === 0,
    blockers,
    children,
  };

  if (args.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(renderText(report));
  }

  if (args.requireGreen && !report.green) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(2);
});
