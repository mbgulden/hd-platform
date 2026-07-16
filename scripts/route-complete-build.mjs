import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.cwd();
const docsDir = path.join(repoRoot, 'docs');
const distDir = path.join(repoRoot, 'dist');
const site = 'https://humandesignengine.com';

const preserved = [];
const skipped = [];

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

function routeForHtml(file) {
  let rel = '/' + path.relative(distDir, file).replaceAll(path.sep, '/');
  if (rel.endsWith('/index.html')) rel = rel.slice(0, -10) || '/';
  return rel;
}

function normalizeLegacyHtmlLinks(contents) {
  return contents
    .replaceAll('href="/reports"', 'href="/buy-report/"')
    .replaceAll("href='/reports'", "href='/buy-report/'")
    .replaceAll('href="/api"', 'href="/docs/"')
    .replaceAll("href='/api'", "href='/docs/'")
    .replaceAll('href="/api/"', 'href="/docs/"')
    .replaceAll("href='/api/'", "href='/docs/'")
    .replaceAll('href="/privacy"', 'href="/privacy/"')
    .replaceAll("href='/privacy'", "href='/privacy/'")
    .replaceAll('href="/privacy.html"', 'href="/privacy/"')
    .replaceAll("href='/privacy.html'", "href='/privacy/'")
    .replaceAll('href="/terms.html"', 'href="/terms/"')
    .replaceAll("href='/terms.html'", "href='/terms/'")
    .replace(/href="(\/human-design\/(?:channels|centers|gates|authorities|types|profiles)\/[^"#?]+?)\/?"/g, (match, route) => {
      if (route.endsWith('.html') || route.endsWith('/')) return match;
      return `href="${route}.html"`;
    })
    .replace(/href='(\/human-design\/(?:channels|centers|gates|authorities|types|profiles)\/[^'#?]+?)\/?'/g, (match, route) => {
      if (route.endsWith('.html') || route.endsWith('/')) return match;
      return `href='${route}.html'`;
    })
    .replace(/href="(\/human-design\/(?:channels|centers|gates|authorities|types|profiles)\/[^"#?]+?)\/"/g, (match, route) => {
      if (route.endsWith('.html')) return match;
      return `href="${route}.html"`;
    })
    .replace(/href='(\/human-design\/(?:channels|centers|gates|authorities|types|profiles)\/[^'#?]+?)\/'/g, (match, route) => {
      if (route.endsWith('.html')) return match;
      return `href='${route}.html'`;
    });
}

function copyLegacyDocs() {
  if (!fs.existsSync(docsDir)) {
    console.warn('[route-complete] docs/ not found; skipping legacy preservation');
    return;
  }
  ensureDir(distDir);
  for (const src of walk(docsDir)) {
    const rel = path.relative(docsDir, src);
    const dest = path.join(distDir, rel);
    // Astro-generated pages win for extensionless route directories. Legacy .html
    // files are still copied alongside them to preserve production URLs such as
    // /buy-report.html and /landing-api.html.
    if (fs.existsSync(dest)) {
      skipped.push(rel.replaceAll(path.sep, '/'));
      continue;
    }
    ensureDir(path.dirname(dest));
    if (src.endsWith('.html')) {
      fs.writeFileSync(dest, normalizeLegacyHtmlLinks(fs.readFileSync(src, 'utf8')));
    } else {
      fs.copyFileSync(src, dest);
    }
    preserved.push(rel.replaceAll(path.sep, '/'));
  }
}

function writeSitemap() {
  const htmlFiles = walk(distDir).filter((f) => f.endsWith('.html'));
  const routes = new Set(['/']);
  for (const file of htmlFiles) routes.add(routeForHtml(file));

  // First-class aliases that Cloudflare/static hosts commonly resolve without
  // trailing slash. Keep them in the sitemap only when their directory index exists.
  for (const route of [...routes]) {
    if (route !== '/' && route.endsWith('/')) routes.add(route.slice(0, -1));
  }

  // Filter routes: exclude redirected legacy paths and non-canonical trailing slash duplicates
  const filteredRoutes = [...routes].filter((route) => {
    // Exclude explicitly redirected files
    if (route === '/buy-report.html' || route === '/success.html' || route === '/privacy.html' || route === '/terms.html') {
      return false;
    }
    // Exclude non-canonical duplicates (no trailing slash when trailing slash version exists)
    if (route !== '/' && !route.endsWith('/') && routes.has(route + '/')) {
      return false;
    }
    return true;
  });

  const urls = filteredRoutes
    .sort((a, b) => a.localeCompare(b))
    .map((route) => {
      const loc = `${site}${route === '/' ? '/' : route}`;
      return `  <url><loc>${escapeXml(loc)}</loc></url>`;
    })
    .join('\n');

  fs.writeFileSync(
    path.join(distDir, 'sitemap.xml'),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`
  );
  fs.writeFileSync(
    path.join(distDir, 'robots.txt'),
    `User-agent: *\nAllow: /\nSitemap: ${site}/sitemap.xml\n`
  );
  return filteredRoutes.length;
}

function writeRedirects() {
  const redirectMap = new Map([
    ['/human-design/authorities', ['/human-design/authorities/', '301']],
    ['/human-design/centers', ['/human-design/centers/', '301']],
    ['/human-design/channels', ['/human-design/channels/', '301']],
    ['/human-design/gates', ['/human-design/gates/', '301']],
    ['/human-design/profiles', ['/human-design/profiles/', '301']],
    ['/human-design/types', ['/human-design/types/', '301']],
    ['/landing-', ['/', '301']],
    ['/reports', ['/buy-report/', '301']],
    ['/reports/', ['/buy-report/', '301']],
    ['/buy-report', ['/buy-report/', '301']],
    ['/success', ['/success/', '301']],
  ]);

  for (const file of walk(distDir).filter((f) => f.endsWith('.html'))) {
    const route = routeForHtml(file);
    if (route === '/' || route.endsWith('/')) continue;
    if (!route.endsWith('.html')) continue;
    const extensionless = route.slice(0, -5);
    const extensionlessDir = path.join(distDir, extensionless.slice(1));
    const hasAstroDirectoryRoute = fs.existsSync(path.join(extensionlessDir, 'index.html'));
    if (!hasAstroDirectoryRoute) {
      if (!redirectMap.has(extensionless)) redirectMap.set(extensionless, [route, '301']);
      if (!redirectMap.has(`${extensionless}/`)) redirectMap.set(`${extensionless}/`, [route, '301']);
    }

    const channelMatch = route.match(/^\/human-design\/channels\/(\d+)-(\d+)-.+\.html$/);
    if (channelMatch) {
      const short = `/human-design/channels/${channelMatch[1]}-${channelMatch[2]}.html`;
      const shortNoExt = short.slice(0, -5);
      const reverse = `/human-design/channels/${channelMatch[2]}-${channelMatch[1]}.html`;
      const reverseNoExt = reverse.slice(0, -5);
      for (const alias of [short, shortNoExt, `${shortNoExt}/`, reverse, reverseNoExt, `${reverseNoExt}/`]) {
        if (!redirectMap.has(alias)) redirectMap.set(alias, [route, '301']);
      }
    }
  }

  const lines = [...redirectMap.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([from, [to, status]]) => `${from} ${to} ${status}`);
  let materialized = 0;
  for (const [from, [to]] of redirectMap.entries()) {
    if (materializeRedirectPage(from, to)) materialized += 1;
  }
  fs.writeFileSync(path.join(distDir, '_redirects'), lines.join('\n') + '\n');
  return { redirectCount: lines.length, materializedRedirectCount: materialized };
}

function materializeRedirectPage(from, to) {
  let target;
  if (from.endsWith('/')) {
    const dirTarget = path.join(distDir, from.slice(1, -1));
    if (fs.existsSync(dirTarget) && !fs.statSync(dirTarget).isDirectory()) return false;
    target = path.join(dirTarget, 'index.html');
  } else {
    target = path.join(distDir, from.slice(1));
    if (fs.existsSync(target) && fs.statSync(target).isDirectory()) return false;
  }

  // Overwrite if it is an explicit redirect of a legacy file to an Astro folder route
  const isLegacyFileRedirect = (from === '/buy-report.html' || from === '/success.html' || from === '/privacy.html' || from === '/terms.html');
  if (fs.existsSync(target) && !isLegacyFileRedirect) return false;

  ensureDir(path.dirname(target));
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=${escapeXml(to)}"><link rel="canonical" href="${escapeXml(to)}"><title>Redirecting…</title></head><body><p>Redirecting to <a href="${escapeXml(to)}">${escapeXml(to)}</a>.</p></body></html>\n`;
  fs.writeFileSync(target, html);
  return true;
}


function syncFirstClassHtmlAliases() {
  const aliases = ['buy-report', 'success', 'privacy', 'terms'];
  let synced = 0;
  for (const alias of aliases) {
    const canonical = path.join(distDir, alias, 'index.html');
    const htmlAlias = path.join(distDir, `${alias}.html`);
    if (!fs.existsSync(canonical)) continue;
    fs.copyFileSync(canonical, htmlAlias);
    synced += 1;
  }
  return synced;
}

function escapeXml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;');
}

copyLegacyDocs();
const routeCount = writeSitemap();
const { redirectCount, materializedRedirectCount } = writeRedirects();
const syncedAliasCount = syncFirstClassHtmlAliases();
const summary = {
  preserved_files: preserved.length,
  skipped_files: skipped.length,
  route_count: routeCount,
  redirect_count: redirectCount,
  materialized_redirect_count: materializedRedirectCount,
  synced_alias_count: syncedAliasCount,
  dist: distDir,
};
fs.writeFileSync(path.join(distDir, 'route-complete-summary.json'), JSON.stringify(summary, null, 2));
console.log(`[route-complete] preserved ${preserved.length} legacy files, generated ${routeCount} sitemap routes, ${redirectCount} redirects, ${materializedRedirectCount} redirect pages, and synced ${syncedAliasCount} first-class aliases`);
if (skipped.length) console.log(`[route-complete] skipped ${skipped.length} directory collisions`);
