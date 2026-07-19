#!/usr/bin/env node
import https from 'node:https';

const issueId = process.argv[2] || 'GRO-4010';
const apiKey = process.env.LINEAR_API_KEY;

if (!apiKey) {
  console.error('LINEAR_API_KEY is required. Source the profile env before running this verifier.');
  process.exit(2);
}

const query = `
query($id: String!) {
  issue(id: $id) {
    identifier
    title
    state { name type }
    labels { nodes { name } }
    children(first: 50) {
      nodes {
        identifier
        title
        state { name type }
        labels { nodes { name } }
      }
    }
  }
}
`;

function requestLinear(payload) {
  const body = JSON.stringify(payload);
  const options = {
    hostname: 'api.linear.app',
    path: '/graphql',
    method: 'POST',
    headers: {
      ['Authorization']: apiKey,
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(body),
    },
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        let parsed;
        try {
          parsed = JSON.parse(data);
        } catch (err) {
          reject(new Error(`Linear returned non-JSON response (${res.statusCode}): ${data.slice(0, 200)}`));
          return;
        }
        if (res.statusCode < 200 || res.statusCode >= 300 || parsed.errors) {
          reject(new Error(`Linear query failed (${res.statusCode}): ${JSON.stringify(parsed.errors || parsed).slice(0, 1000)}`));
          return;
        }
        resolve(parsed.data.issue);
      });
    });
    req.on('error', reject);
    req.setTimeout(30000, () => {
      req.destroy(new Error('Linear query timed out after 30s'));
    });
    req.write(body);
    req.end();
  });
}

function labelNames(issue) {
  return (issue.labels?.nodes || []).map((label) => label.name).sort();
}

const issue = await requestLinear({ query, variables: { id: issueId } });
if (!issue) {
  console.error(`Issue ${issueId} was not found.`);
  process.exit(3);
}

const children = issue.children?.nodes || [];
const incomplete = children.filter((child) => child.state?.name !== 'Done');
const report = {
  issue: issue.identifier,
  title: issue.title,
  state: issue.state?.name,
  labels: labelNames(issue),
  child_count: children.length,
  done_children: children.length - incomplete.length,
  incomplete_children: incomplete.map((child) => ({
    identifier: child.identifier,
    title: child.title,
    state: child.state?.name,
    labels: labelNames(child),
  })),
  green: children.length > 0 && incomplete.length === 0,
  gate: 'Parent epic is green only when every child issue is Done with its own production/staging proof evidence.',
};

console.log(JSON.stringify(report, null, 2));

if (!report.green) {
  process.exit(1);
}
