#!/usr/bin/env node
import { existsSync, readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, normalize } from 'node:path';

const root = process.cwd();
const dist = join(root, 'dist');
const routes = JSON.parse(readFileSync(join(root, '.pwp/routes.json'), 'utf8')).routes;
const outputDir = join(root, 'okf/output/pwp-visual-qa');
mkdirSync(outputDir, { recursive: true });

const skip = /^(mailto:|tel:|#|javascript:|https?:\/\/(checkout\.stripe\.com|t\.me|humandesignengine\.com)|\/(api|v1)\/)/i;
const attrPattern = /\b(?:href|src)=["']([^"']+)["']/gi;

function routeToFile(pathname) {
  const clean = pathname.split('#')[0].split('?')[0] || '/';
  const decoded = decodeURIComponent(clean);
  const candidates = [];
  if (decoded.endsWith('/')) candidates.push(join(dist, decoded, 'index.html'));
  candidates.push(join(dist, decoded));
  if (!decoded.endsWith('.html')) candidates.push(join(dist, `${decoded}.html`));
  if (!decoded.endsWith('/')) candidates.push(join(dist, decoded, 'index.html'));
  return candidates.find((candidate) => existsSync(normalize(candidate)));
}

const checked = [];
const broken = [];
for (const route of routes) {
  const file = routeToFile(route.path);
  if (!file) {
    broken.push({ route: route.path, link: route.path, reason: 'configured route missing from dist' });
    continue;
  }
  const html = readFileSync(file, 'utf8');
  for (const match of html.matchAll(attrPattern)) {
    const link = match[1].trim();
    if (!link || skip.test(link)) continue;
    if (/^https?:\/\//i.test(link)) continue;
    if (!link.startsWith('/')) continue;
    const target = routeToFile(link);
    checked.push({ route: route.path, link, ok: Boolean(target) });
    if (!target) broken.push({ route: route.path, link, reason: 'internal target missing from dist' });
  }
}

const summary = { ok: broken.length === 0, route_count: routes.length, checked_count: checked.length, broken_count: broken.length, broken };
writeFileSync(join(outputDir, 'link-check.json'), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
if (!summary.ok) process.exit(1);
