import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.cwd();
const docsDir = path.join(repoRoot, 'docs');
const distDir = path.join(repoRoot, 'dist');
const site = 'https://humandesignengine.com';

const preserved = [];
const skipped = [];

const emdashShellStyles = `
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/hde-light-theme.css">
`;

const emdashHeaderHtml = `<header class="emdash-site-header">
  <div class="nav-inner">
    <a class="nav-logo" href="/" aria-label="Human Design Engine Home">
      <span class="nav-logo-text">Human Design<span>Engine</span></span>
    </a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="menu-container" aria-label="Toggle menu" id="menuTrigger">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M4 6h16M4 12h16M4 18h16" class="hamburger-icon"></path>
        <path d="M6 18L18 6M6 6l12 12" class="close-icon" style="display: none;"></path>
      </svg>
    </button>
    <nav aria-label="Main Navigation" id="menu-container">
      <ul class="nav-links" id="menuLinks">
        <li><a href="/free-human-design-reading-generator/">Free Reading</a></li>
        <li><a href="/buy-report/">Reports</a></li>
        <li><a href="/deconditioning/">Sanctuary</a></li>
        <li><a href="/docs/">API</a></li>
        <li><a href="/human-design/gates/">Learn</a></li>
        <li><a href="/landing-sheplantedatree/">Coaching</a></li>
      </ul>
    </nav>
    <a class="nav-cta" href="/free-human-design-reading-generator/">Generate Free Reading</a>
  </div>
</header>`;

const emdashFooterHtml = `<footer class="emdash-site-footer" style="text-align: left;">
  <div class="footer-inner" style="text-align: left; justify-items: start;">
    <div class="footer-logo">Human Design Engine</div>
    <div class="footer-groups" aria-label="Footer navigation">
      <section class="footer-group" aria-labelledby="footer-start">
        <h2 id="footer-start">Start</h2>
        <ul>
          <li><a href="/free-human-design-reading-generator/">Free Reading Generator</a></li>
          <li><a href="/bodygraph.html">Bodygraph Tool</a></li>
          <li><a href="/hd-engine/free-tools/gate-lookup.html">Gate Lookup</a></li>
          <li><a href="/hd-engine/free-tools/type-quiz.html">Type Quiz</a></li>
        </ul>
      </section>
      <section class="footer-group" aria-labelledby="footer-products">
        <h2 id="footer-products">Products</h2>
        <ul>
          <li><a href="/buy-report/">Reports</a></li>
          <li><a href="/deconditioning/">Somatic Sanctuary</a></li>
          <li><a href="/docs/">Developer API</a></li>
          <li><a href="/landing-sheplantedatree/">Coaching</a></li>
        </ul>
      </section>
      <section class="footer-group" aria-labelledby="footer-learn">
        <h2 id="footer-learn">Learn</h2>
        <ul>
          <li><a href="/human-design/gates/">Gates</a></li>
          <li><a href="/human-design/channels/">Channels</a></li>
          <li><a href="/human-design/centers/">Centers</a></li>
          <li><a href="/human-design/authorities/">Authorities</a></li>
          <li><a href="/human-design/types/">Types</a></li>
          <li><a href="/human-design/profiles/">Profiles</a></li>
        </ul>
      </section>
    </div>
    <div class="footer-copy">© 2026 Human Design Engine. All calculations verified.</div>
  </div>
</footer>`;

const emdashShellScriptHtml = `<script>
(() => {
  const trigger = document.getElementById('menuTrigger');
  const links = document.querySelectorAll('#menuLinks a');
  if (!trigger) return;
  const hamburgerIcon = trigger.querySelector('.hamburger-icon');
  const closeIcon = trigger.querySelector('.close-icon');
  const toggleMenu = (open) => {
    trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.classList.toggle('drawer-open', open);
    if (hamburgerIcon) hamburgerIcon.style.display = open ? 'none' : 'block';
    if (closeIcon) closeIcon.style.display = open ? 'block' : 'none';
  };
  trigger.addEventListener('click', () => toggleMenu(trigger.getAttribute('aria-expanded') !== 'true'));
  links.forEach((link) => link.addEventListener('click', () => toggleMenu(false)));
  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') toggleMenu(false);
  });
})();
</script>`;

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

function injectLegacyLightTheme(contents) {
  if (!contents.includes('<html') || contents.includes('/hde-light-theme.css')) return contents;
  const link = '<link rel="stylesheet" href="/hde-light-theme.css">';
  if (contents.includes('</head>')) return contents.replace('</head>', `${link}\n</head>`);
  return link + '\n' + contents;
}

function replaceLegacyDarkInlineStyles(contents) {
  const replacements = new Map([
    ['#060d1a', '#FAF7F0'],
    ['#0a1628', '#FDFBF7'],
    ['#0f1d36', '#F6F1E7'],
    ['#0f1428', '#FAF7F0'],
    ['#111827', '#2F3631'],
    ['#1f2937', '#4B514E'],
    ['#c9a84c', '#5F7261'],
    ['#e8e6e3', '#2F3631'],
    ['#667eea', '#5F7261'],
    ['#764ba2', '#2F3631'],
    ['#a78bfa', '#5F7261'],
    ['#8899aa', '#4B514E'],
    ['rgba(10, 22, 40, 0.6)', 'rgba(255, 255, 255, 0.76)'],
    ['rgba(15, 29, 54, 0.4)', 'rgba(255, 255, 255, 0.76)'],
    ['rgba(201, 168, 76, 0.25)', 'rgba(95, 114, 97, 0.18)'],
    ['rgba(201, 168, 76, 0.15)', 'rgba(95, 114, 97, 0.15)'],
    ['rgba(201, 168, 76, 0.1)', 'rgba(95, 114, 97, 0.12)'],
    ['rgba(102,126,234,0.2)', 'rgba(95,114,97,0.18)'],
    ['rgba(102,126,234,0.12)', 'rgba(95,114,97,0.10)'],
    ['rgba(118,75,162,0.12)', 'rgba(95,114,97,0.10)'],
    ['rgba(118,75,162,0.25)', 'rgba(95,114,97,0.20)'],
  ]);
  let out = contents;
  for (const [from, to] of replacements) {
    out = out.replaceAll(from, to).replaceAll(from.toUpperCase(), to);
  }
  out = out
    .replace(/#060d1a/gi, '#FAF7F0')
    .replace(/#0a1628/gi, '#FDFBF7')
    .replace(/#0f1d36/gi, '#F6F1E7')
    .replace(/#0f1428/gi, '#FAF7F0')
    .replace(/#111827/gi, '#2F3631')
    .replace(/#1f2937/gi, '#4B514E')
    .replace(/#c9a84c/gi, '#5F7261')
    .replace(/#e8e6e3/gi, '#2F3631')
    .replace(/#667eea/gi, '#5F7261')
    .replace(/#764ba2/gi, '#2F3631')
    .replace(/#a78bfa/gi, '#5F7261')
    .replace(/#8899aa/gi, '#4B514E')
    .replace(/rgba\(\s*10\s*,\s*22\s*,\s*40\s*,\s*[^)]+\)/gi, 'rgba(255, 255, 255, 0.76)')
    .replace(/rgba\(\s*15\s*,\s*29\s*,\s*54\s*,\s*[^)]+\)/gi, 'rgba(255, 255, 255, 0.76)')
    .replace(/rgba\(\s*201\s*,\s*168\s*,\s*76\s*,\s*[^)]+\)/gi, 'rgba(95, 114, 97, 0.16)')
    .replace(/rgba\(\s*102\s*,\s*126\s*,\s*234\s*,\s*[^)]+\)/gi, 'rgba(95, 114, 97, 0.14)')
    .replace(/rgba\(\s*118\s*,\s*75\s*,\s*162\s*,\s*[^)]+\)/gi, 'rgba(95, 114, 97, 0.14)');
  return out;
}

function normalizeLegacyHtmlLinks(contents) {
  return applyEmdashLegacyShell(replaceLegacyDarkInlineStyles(injectLegacyLightTheme(contents)))
    .replaceAll('<input id="agree" required type="checkbox"/>', '<input id="agree" required type="checkbox" aria-label="Agree to the Affiliate Terms"/>')
    .replaceAll('<input id="agree" required="" type="checkbox">', '<input id="agree" required="" type="checkbox" aria-label="Agree to the Affiliate Terms">')
    .replaceAll('<input id="agree" required="" type="checkbox"/>', '<input id="agree" required="" type="checkbox" aria-label="Agree to the Affiliate Terms"/>')
    .replaceAll('<label>I agree to the <a href="#">Affiliate Terms</a>.', '<label for="agree">I agree to the <a href="#">Affiliate Terms</a>.')
    .replaceAll('<nav class="nav">', '<nav class="page-subnav nav" style="display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-start; gap: 10px; text-align: left;">')
    .replaceAll('<div style="overflow-x: auto; -webkit-overflow-scrolling: touch;">', '<div style="overflow-x: auto; -webkit-overflow-scrolling: touch;" tabindex="0" role="region" aria-label="Scrollable data table">')
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

function applyEmdashLegacyShell(contents) {
  if (!contents.includes('<html') || !contents.includes('<body')) return contents;
  let out = contents;
  if (!out.includes('fonts.googleapis.com/css2?family=Outfit')) {
    out = out.includes('</head>') ? out.replace('</head>', `${emdashShellStyles}</head>`) : `${emdashShellStyles}${out}`;
  }
  // Legacy copied HTML is not Astro, but it still uses the same generated shell contract.
  // Remove each page's old navigation/footer block so one template controls the site chrome.
  out = out.replace(/<!--\s*NAV\s*-->\s*<nav\b[\s\S]*?<\/nav>\s*/gi, '');
  out = out.replace(/<body([^>]*)>\s*<nav\b[\s\S]*?<\/nav>\s*/i, '<body$1>');
  out = out.replace(/<body([^>]*)>/i, '<body$1 class="emdash-legacy-shell">');
  if (!out.includes('emdash-site-header')) {
    out = out.replace(/<body([^>]*)>/i, `<body$1>\n${emdashHeaderHtml}\n`);
  }
  if (!out.includes('emdash-site-footer')) {
    out = out.replace(/<footer\b[\s\S]*?<\/footer>\s*(?=<\/body>)/i, '');
    out = out.includes('</body>')
      ? out.replace(/<\/body>/i, `${emdashFooterHtml}\n${emdashShellScriptHtml}\n</body>`)
      : `${out}\n${emdashFooterHtml}\n${emdashShellScriptHtml}`;
  }
  return out;
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
    fs.chmodSync(dest, 0o644);
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

function normalizeBuiltHtml() {
  let normalized = 0;
  for (const file of walk(distDir).filter((f) => f.endsWith('.html'))) {
    const before = fs.readFileSync(file, 'utf8');
    const after = normalizeLegacyHtmlLinks(before);
    if (after !== before) {
      fs.writeFileSync(file, after);
      normalized += 1;
    }
  }
  return normalized;
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
const normalizedHtmlCount = normalizeBuiltHtml();
const summary = {
  preserved_files: preserved.length,
  skipped_files: skipped.length,
  route_count: routeCount,
  redirect_count: redirectCount,
  materialized_redirect_count: materializedRedirectCount,
  synced_alias_count: syncedAliasCount,
  normalized_html_count: normalizedHtmlCount,
  dist: distDir,
};
fs.writeFileSync(path.join(distDir, 'route-complete-summary.json'), JSON.stringify(summary, null, 2));
console.log(`[route-complete] preserved ${preserved.length} legacy files, generated ${routeCount} sitemap routes, ${redirectCount} redirects, ${materializedRedirectCount} redirect pages, and synced ${syncedAliasCount} first-class aliases; normalized ${normalizedHtmlCount} built HTML files`);
if (skipped.length) console.log(`[route-complete] skipped ${skipped.length} directory collisions`);
