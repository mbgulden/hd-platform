# Cloudflare Pages Setup Guide — Active Oahu Tours

**Ticket:** GRO-123  
**Date:** May 29, 2026  
**Author:** Hermes Agent  
**Status:** Ready for deployment (requires Cloudflare auth)

---

## Executive Summary

This guide covers deploying the Active Oahu Tours Astro site to **Cloudflare Pages** with automatic CI/CD from GitHub. The site replaces the current WordPress install; Cloudflare Pages handles custom domain, SSL, preview deployments, and branch-based environments.

**Current state:** All configuration files are created and ready. Final deployment requires Cloudflare dashboard access to connect the GitHub repo and set DNS.

---

## 1. Architecture Overview

```
GitHub Repo (mbgulden/active-oahu-tours)
    │
    │ push to main
    ▼
Cloudflare Pages Build
    │ npm ci && npm run build
    │ Output: dist/
    ▼
Cloudflare CDN (285+ locations)
    │
    ├─ activeoahutours.com          (production)
    ├─ staging.activeoahutours.com  (staging branch)
    └─ {hash}.active-oahu-tours.pages.dev  (preview)
```

| Component | Details |
|---|---|
| **Framework** | Astro 5.18 (static output) |
| **Build command** | `npm run build` (runs `astro build`) |
| **Output directory** | `dist/` |
| **Node version** | 20+ (22.22.2 in dev) |
| **CSS** | Tailwind CSS 4 via @astrojs/tailwind |
| **Hosting target** | Cloudflare Pages |

---

## 2. Files Created

### 2.1 `wrangler.toml` — Cloudflare Pages Config

**Path:** `active-oahu-tours/wrangler.toml`

Defines the Pages project name, output directory, and documents all environment variables and deployment rules. Serves as the source of truth for Pages configuration.

### 2.2 `public/_headers` — Security & Cache Headers

**Path:** `active-oahu-tours/public/_headers`

Sets:
- `X-Frame-Options: DENY` (prevents clickjacking)
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security` (HSTS preload)
- `Permissions-Policy` (restrict camera/mic/geo)
- Immutable cache for `/_astro/*` (hashed assets)
- 7-day cache for `/images/*`
- 1-hour cache for HTML

### 2.3 `public/_redirects` — URL Redirects

**Path:** `active-oahu-tours/public/_redirects`

Handles old WordPress paths → new Astro routes, booking deep links → FareHarbor, and www → apex canonical redirect.

### 2.4 `.github/workflows/deploy.yml` — CI/CD Pipeline

Optional. Cloudflare Pages auto-deploys on push via GitHub integration. This workflow is an alternative for teams that want wrangler-driven deploys with additional build steps (tests, linting).

---

## 3. Environment Variables

Set these in **Cloudflare Dashboard > Workers & Pages > active-oahu-tours > Settings > Environment Variables**.

| Variable | Value | Environment | Notes |
|---|---|---|---|
| `NODE_VERSION` | `20` | All | Ensures Node 20+ on build |
| `PUBLIC_SITE_URL` | `https://activeoahutours.com` | Production | Used by Astro for canonical URLs |
| `PUBLIC_GA_ID` | `G-XXXXXXXXXX` | Production | Google Analytics 4 measurement ID |
| `PUBLIC_FAREHARBOR_SHORTNAME` | `activeoahu` | Production | FareHarbor booking integration |
| `DEPLOY_ENV` | `production` | Production | Used in code for conditional logic |
| `DEPLOY_ENV` | `preview` | Preview | Marks PR/staging deploys |

**To add in Cloudflare Dashboard:**

1. Go to Workers & Pages → active-oahu-tours → Settings → Environment Variables
2. Click "Add variable"
3. Choose "Production" or "Preview" environment
4. Add each variable above
5. Click "Save"

**For GitHub Actions secrets (if using CI/CD workflow):**

```
CLOUDFLARE_API_TOKEN    = <API token with Pages edit permission>
CLOUDFLARE_ACCOUNT_ID   = <Your Cloudflare account ID>
```

---

## 4. DNS Configuration

### 4.1 Prerequisites

- Domain `activeoahutours.com` must be in your Cloudflare account
- Nameservers must point to Cloudflare (e.g., `adam.ns.cloudflare.com`, `linda.ns.cloudflare.com`)

### 4.2 DNS Records

After creating the Pages project and adding the custom domain, Cloudflare automatically configures DNS. Verify/add these records in **Cloudflare Dashboard > activeoahutours.com > DNS > Records**:

| Type | Name | Target | TTL | Proxy |
|---|---|---|---|---|
| CNAME | `@` | `active-oahu-tours.pages.dev` | Auto | Proxied |
| CNAME | `www` | `active-oahu-tours.pages.dev` | Auto | Proxied |
| CNAME | `staging` | `active-oahu-tours.pages.dev` | Auto | Proxied |

**Note:** Cloudflare Pages usually creates these CNAME records automatically when you add the custom domain in the Pages dashboard. The `staging` subdomain must be added manually if needed.

### 4.3 SSL/TLS Settings

Cloudflare Pages provides automatic SSL. In **SSL/TLS > Overview**, set:

- **SSL/TLS encryption mode:** `Full (strict)` — Pages serves valid certs
- **Always Use HTTPS:** ON
- **Automatic HTTPS Rewrites:** ON

### 4.4 WordPress Cutover

The site currently serves WordPress on Cloudflare. To cut over:

1. In DNS, remove the existing A record pointing to Flywheel/WP Engine IP
2. Add the CNAME pointing to `active-oahu-tours.pages.dev`
3. Wait for propagation (~5-10 minutes typically with Cloudflare)
4. Verify at `https://activeoahutours.com`

---

## 5. Step-by-Step Setup

### Step 1: Create Git Repository

```bash
cd /home/ubuntu/work/active-oahu-tours
git init
git add .
git commit -m "Initial commit: Active Oahu Tours Astro site"
```

Push to GitHub:
```bash
# Create repo on GitHub: mbgulden/active-oahu-tours
git remote add origin https://github.com/mbgulden/active-oahu-tours.git
git branch -M main
git push -u origin main
```

### Step 2: Create Cloudflare Pages Project

**Option A — Via Dashboard (Recommended):**

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) → Workers & Pages
2. Click **Create** → **Pages** → **Connect to Git**
3. Select `mbgulden/active-oahu-tours`
4. Configure:
   - **Build command:** `npm run build`
   - **Output directory:** `dist`
   - **Node.js version:** `20`
5. Click **Save and Deploy**

**Option B — Via Wrangler CLI:**

```bash
# Authenticate
npx wrangler login

# Create project
npx wrangler pages project create active-oahu-tours \
  --production-branch main

# Deploy
npx wrangler pages deploy dist/ --project-name active-oahu-tours
```

### Step 3: Add Custom Domain

1. In Pages → active-oahu-tours → **Custom Domains**
2. Click **Set up a custom domain**
3. Enter `activeoahutours.com`
4. Cloudflare auto-configures DNS (or follow prompts)
5. Add `www.activeoahutours.com` as redirect to apex
6. (Optional) Add `staging.activeoahutours.com` for staging branch

### Step 4: Configure Environment Variables

Add the variables from Section 3 in:
**Pages → active-oahu-tours → Settings → Environment Variables**

### Step 5: Configure Branch Deploys

1. Pages → active-oahu-tours → **Settings** → **Builds & Deployments**
2. **Production branch:** `main`
3. **Preview branches:** All non-production branches (`*`)
4. Enable **Preview deployments** (auto-creates unique URLs for PRs)

For staging:
- Push a `staging` branch: `git checkout -b staging && git push origin staging`
- Add `staging.activeoahutours.com` as custom domain
- Configure staging branch deploy via **Branch deploy rules**

### Step 6: Verify Build

Push a change to `main`:
```bash
echo "# test" >> README.md
git add README.md
git commit -m "test: verify Cloudflare Pages deploy"
git push origin main
```

Monitor at: **Pages → active-oahu-tours → Deployments**

---

## 6. Existing cloudflared Tunnel (HD Engine)

A Cloudflare Tunnel is configured for the Human Design Engine project, NOT for Active Oahu Tours. The tunnel uses:

- **Config:** `/home/ubuntu/.cloudflared/config.yml`
- **Setup script:** `/home/ubuntu/work/hd-platform/infra/setup-tunnel.sh`

**Active Oahu Tours does NOT use cloudflared.** It uses Cloudflare Pages (static site hosting, no tunnel needed). The tunnel is for the FastAPI backend services on HD Engine.

**Current cloudflared state:**
- Installed: `cloudflared version 2026.5.0`
- Not authenticated: No `~/.cloudflared/cert.pem`
- No active tunnels (requires Cloudflare login to list)

---

## 7. Testing Checklist

### Pre-Deploy

- [ ] Astro builds successfully: `npm run build`
- [ ] `dist/` directory contains index.html and assets
- [ ] `_headers` and `_redirects` files present in dist/
- [ ] All environment variables documented
- [ ] Git repo initialized and pushed to GitHub

### Post-Deploy

- [ ] Cloudflare Pages build succeeds (green check in dashboard)
- [ ] `activeoahutours.com` loads over HTTPS
- [ ] `www.activeoahutours.com` redirects to apex
- [ ] All old WordPress URLs redirect correctly (check /tours, /book, /faq)
- [ ] SSL certificate is valid (padlock icon)
- [ ] Security headers present: `curl -I https://activeoahutours.com`
- [ ] Preview deployments work: open a PR and check unique URL
- [ ] Images load with correct cache headers
- [ ] JavaScript bundles have immutable cache headers
- [ ] FareHarbor booking widget loads
- [ ] Google Analytics fires (check GA4 real-time)

### Testing Commands

```bash
# Check headers
curl -I https://activeoahutours.com | grep -E '(x-frame|x-content|strict-transport)'

# Check redirects (after deploy)
curl -I https://activeoahutours.com/tours
# Should return: HTTP/2 301 → /#tours

# Check immutable cache on hashed assets
curl -I https://activeoahutours.com/_astro/somefile.hash.css
# Should return: cache-control: public, max-age=31536000, immutable
```

---

## 8. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Build fails: `astro: not found` | Node version too old | Set `NODE_VERSION=20` in env vars |
| 404 on all routes | Build output path mismatch | Verify output dir is `dist/` |
| SSL cert error | DNS not proxied | Enable Cloudflare proxy (orange cloud) |
| Mixed content warnings | Images hardcoded as HTTP | Use `//` or `https://` for all resources |
| Preview deploy not creating | GitHub permissions | Re-authorize Cloudflare Pages GitHub app |
| `_redirects` not working | File not in dist/ root | Ensure `public/_redirects` exists before build |

---

## 9. Next Steps

1. **Complete Cloudflare auth** — Login to Cloudflare dashboard and create the Pages project
2. **Push to GitHub** — Initialize git repo and push to `mbgulden/active-oahu-tours`
3. **DNS cutover** — Schedule WordPress → Pages migration during low-traffic window
4. **SEO redirects** — Verify all old URLs redirect correctly (critical for SEO)
5. **FareHarbor integration** — Ensure booking widget loads from new origin
6. **Google Analytics** — Verify GA4 property receives data from new site

---

## 10. References

- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Cloudflare Pages + Astro Guide](https://developers.cloudflare.com/pages/framework-guides/astro/)
- [Wrangler Configuration](https://developers.cloudflare.com/pages/platform/wrangler/)
- [Cloudflare Pages Headers](https://developers.cloudflare.com/pages/platform/headers/)
- [Cloudflare Pages Redirects](https://developers.cloudflare.com/pages/platform/redirects/)
