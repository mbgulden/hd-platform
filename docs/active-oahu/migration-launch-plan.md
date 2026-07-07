# Migration Launch Plan — Active Oahu Tours

**Ticket:** GRO-125
**Date:** May 29, 2026
**Author:** Hermes Agent (Launch Planning)
**Depends On:** GRO-119 (Architecture), GRO-123 (Cloudflare Setup), GRO-117 (SEO Audit)
**Status:** Ready for execution

---

## Executive Summary

This is the **day-of launch runbook** for migrating activeoahutours.com from WordPress (Flywheel + Cloudflare APO) to Astro 5 on Cloudflare Pages. It covers pre-launch verification, an hour-by-hour launch day timeline, rollback procedures, and a 30-day post-launch monitoring plan.

**Critical success factors:**
- Zero booking downtime (FareHarbor operates independently of our CMS)
- Zero SEO equity loss (exact URL preservation + comprehensive 301 redirects)
- Rollback capability in under 15 minutes if needed

---

## 1. Pre-Launch Checklist

> **Complete every item.** Any unchecked item is a launch blocker.

### 1.1 Content & Pages

- [ ] **All 22 tour pages built and rendering correctly** — Verify each `/activities/[slug]` page at its exact WordPress URL
- [ ] **All 28 guide pages built and rendering correctly** — Verify each `/oahu-kayaking-and-beach-adventures/[slug]` page
- [ ] **All 18 rental pages built and rendering correctly** — Verify each `/rentals/[slug]` page
- [ ] **All 12 core static pages built** — Home, About, Contact, FAQ, Reviews, Storefront, Tour Packages, Multi-day Rentals, Cancellation Policy, Privacy Policy, Trip Insurance Terms, Best Kayaking Trips
- [ ] **404 page styled and functional** — Custom branded 404 at `/404.html`, verified on staging
- [ ] **Homepage renders with all sections** — Hero, tour grid, trust signals, testimonials, CTAs
- [ ] **Japanese translation pages available** — Weglot `/ja/` routes confirmed working

### 1.2 Structured Data (6 JSON-LD Types)

Validate each schema type using [Google Rich Results Test](https://search.google.com/test/rich-results):

- [ ] **LocalBusiness schema** — Site-wide, in `BaseLayout.astro`. Verify: address, phone, geo, hours, logo, sameAs links
- [ ] **TouristAttraction/Trip schema** — Per-tour via `TourSchema.astro`. Verify: name, description, location, offers (price), provider reference, touristType
- [ ] **FAQPage schema** — On `/faq/` and tour-specific FAQ sections. Verify: questions array parses correctly, no duplicate entries
- [ ] **Article schema** — All guide pages. Verify: headline, datePublished, dateModified, author, publisher reference, about
- [ ] **BreadcrumbList schema** — Dynamic per page. Verify: hierarchy correct (Home → Section → Page), position increments, last item has no URL
- [ ] **HowTo schema** — On applicable guide pages (e.g., kayak-to-Mokulua guide). Verify: steps array, images per step, totalTime

**Validation command:**
```bash
# Run schema validation locally
npx astro build && \
  for f in dist/**/*.html; do \
    echo "Checking: $f"; \
    grep -c 'application/ld+json' "$f"; \
  done
```

**Rich Results Test batch check script:**
```bash
# Test key URLs against Google's API
URLS=(
  "https://staging.activeoahutours.com/"
  "https://staging.activeoahutours.com/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/"
  "https://staging.activeoahutours.com/oahu-kayaking-and-beach-adventures/ultimate-guide-for-kailua-beach-park/"
  "https://staging.activeoahutours.com/faq/"
)
for url in "${URLS[@]}"; do
  echo "=== $url ==="
  curl -s "https://search.google.com/test/rich-results/result?id=$(curl -s -X POST 'https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run?key=YOUR_API_KEY' -H 'Content-Type: application/json' -d "{\"url\":\"$url\"}" | jq -r '.id')"
done
```

### 1.3 Redirects — 301 Map Verification

- [ ] **`public/_redirects` file exists in repo** — Verify at repo root of active-oahu-tours
- [ ] **All 65 redirected URLs mapped** — 51 review pages → `/reviews/`, 7 deleted activities → `/activities/`, 4 job pages → `/contact-us/`, `/tours/` → `/activities/`, WordPress admin paths → 410
- [ ] **Trailing slash normalization tested** — Cloudflare handles `/page` ↔ `/page/` equivalence
- [ ] **`www` → apex redirect verified** — `www.activeoahutours.com` → `activeoahutours.com`
- [ ] **Redirects file copied to `dist/_redirects` after build** — Confirmed in build output

**Local redirect test script:**
```bash
# From active-oahu-tours repo root
cat public/_redirects | while read -r line; do
  [[ "$line" =~ ^# ]] && continue  # skip comments
  [[ -z "$line" ]] && continue     # skip empty
  src=$(echo "$line" | awk '{print $1}')
  dest=$(echo "$line" | awk '{print $2}')
  echo "Testing: $src → $dest"
done
```

### 1.4 Images & Media

- [ ] **All WordPress images downloaded** — Full `wp-content/uploads/` mirrored to `public/images/`
- [ ] **Image paths updated in all .md files** — `wp-content/uploads/` → `/images/`
- [ ] **Images optimized** — Run through Sharp/Squoosh (WebP + fallback, quality 80%)
- [ ] **Alt text present on all migrated images** — Minimum: descriptive alt text on every `<img>`
- [ ] **OG images generated** — Default `og-default.jpg` (1200×630) + per-page OG images for top 10 pages
- [ ] **Favicon and web manifest** — `favicon.ico`, `site.webmanifest` with all icon sizes

### 1.5 FareHarbor Integration

- [ ] **Global FareHarbor snippet in `<head>`** — `fareharbor.com/embeds/api/v1/?autolightframe=yes`
- [ ] **Every tour page has `fareHarborItemId`** — Verified in frontmatter for all 22 tours
- [ ] **Booking button triggers lightframe** — Tested: click → FareHarbor overlay opens
- [ ] **Fallback direct link works** — If JS disabled, button links to `fareharbor.com/embeds/book/activeoahutours/items/[ID]/`
- [ ] **Phone number visible as fallback** — `(808) XXX-XXXX` on all booking CTAs
- [ ] **Booking flow tested end-to-end** — Select date → fill details → reach payment step (stop before charge)

### 1.6 SSL, DNS & Cloudflare

- [ ] **Cloudflare Pages project created** — `active-oahu-tours` in Workers & Pages dashboard
- [ ] **Custom domain configured** — `activeoahutours.com` added in Pages → Custom Domains
- [ ] **DNS records documented** — Current A record (Flywheel IP) noted for rollback
- [ ] **SSL/TLS mode set** — Full (strict) in Cloudflare SSL/TLS settings
- [ ] **Always Use HTTPS enabled** — ON in Cloudflare
- [ ] **`staging.activeoahutours.com` configured** — Points to staging branch deploy
- [ ] **Build environment variables set** — `NODE_VERSION=20`, `PUBLIC_SITE_URL`, `PUBLIC_GA_ID`, `PUBLIC_FAREHARBOR_SHORTNAME`

### 1.7 Analytics & Search Console

- [ ] **GA4 measurement ID configured** — `G-XXXXXXXXXX` in environment variables
- [ ] **Google Tag Manager or direct gtag snippet in `<head>`** — Verified in built HTML
- [ ] **GA4 real-time reports showing data from staging** — Confirm pageviews register
- [ ] **Google Search Console property created** — Domain property for `activeoahutours.com`
- [ ] **Bing Webmaster Tools property created** — `activeoahutours.com` added
- [ ] **Search Console ownership verified** — DNS TXT record or HTML file method confirmed

### 1.8 Sitemap & Robots

- [ ] **Sitemap generated at build time** — `@astrojs/sitemap` outputs `dist/sitemap-index.xml` + `dist/sitemap-0.xml`
- [ ] **Sitemap contains all ~100 migrated URLs** — No thin/review/job URLs included
- [ ] **Sitemap validates** — `xmllint --noout dist/sitemap-*.xml` passes
- [ ] **`robots.txt` configured** — Allows all crawlers, points to sitemap, disallows `/wp-*`
- [ ] **`robots.txt` content verified** — Accessible at `https://staging.activeoahutours.com/robots.txt`

### 1.9 Performance & Security

- [ ] **Lighthouse score acceptable on staging** — Performance ≥ 95, SEO = 100, Best Practices ≥ 90
- [ ] **Security headers verified** — `curl -I https://staging...` shows X-Frame-Options, X-Content-Type-Options, HSTS, Referrer-Policy, Permissions-Policy
- [ ] **Cache headers correct** — Immutable on hashed assets (`/_astro/*`), moderate on HTML, long on images
- [ ] **Mobile responsive** — Tested on iPhone, Android, tablet viewports
- [ ] **Cross-browser tested** — Chrome, Firefox, Safari, Edge
- [ ] **All internal links resolve** — No broken links (run link checker on staging)

### 1.10 Stakeholder Sign-off

- [ ] **Content review complete** — Stakeholder has reviewed all tour/guide/page content on staging
- [ ] **Booking flow approved** — Stakeholder has tested FareHarbor booking on staging
- [ ] **Visual design approved** — Design matches brand guidelines on staging
- [ ] **Launch window confirmed** — Date/time agreed (recommend: Tuesday–Thursday, 10am–2pm Hawaii time / low-traffic window)
- [ ] **Rollback plan reviewed** — Stakeholder understands rollback procedure and timing
- [ ] **Communication prepared** — Customer email template, social media announcement drafted

---

## 2. Launch Day Runbook (Hour by Hour)

**Target launch window:** Tuesday–Thursday, 10:00–14:00 Hawaii time (HST, UTC-10)
**Rationale:** Lowest traffic period for activeoahutours.com; Cloudflare support available during US business hours.

### T-4h: Pre-Launch Preparation (06:00 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| 06:00 | **Final production build** in local repo | Dev | `npm run build` — confirm zero errors |
| 06:15 | **Push to `main` branch** on GitHub | Dev | `git push origin main` — triggers Cloudflare Pages deploy |
| 06:20 | **Monitor Cloudflare Pages build** | Dev | Dashboard → Pages → Deployments — wait for green check |
| 06:30 | **Verify production `.pages.dev` URL** | Dev | `https://active-oahu-tours.pages.dev` loads correctly |
| 06:45 | **Deploy to staging environment** | Dev | Push `staging` branch, verify `staging.activeoahutours.com` |

### T-3h: Staging Validation (07:00 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| 07:00 | **Smoke test all page types on staging** | QA | Check 1 homepage, 3 tours, 3 guides, 2 rentals, 2 static pages, FAQ, Reviews, Contact |
| 07:30 | **Verify all 301 redirects on staging** | QA | Test at least 15 redirects: `/tours/`, old activity URLs, review URLs, job URLs, `/wp-admin/` |
| 07:45 | **Run Lighthouse audit on staging** | QA | Target: Performance 95+, SEO 100. Save report as baseline. |
| 08:00 | **Run schema validation** | QA | Google Rich Results Test on 5 key URLs (homepage, tour, guide, FAQ, contact) |
| 08:15 | **Test FareHarbor booking on staging** | QA | Complete booking flow through payment step on 3 different tours |
| 08:30 | **Test contact form** (if static/Netlify Forms/Fabform) | QA | Submit test inquiry, verify it arrives |
| 08:45 | **Final sitemap review** | Dev | Open `sitemap-0.xml` from dist/, verify all 100 target URLs present |

### T-2h: Search Console & Pre-Cutover Prep (08:00 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| 08:00 | **Search Console: URL Inspection for top 10 URLs** | SEO | Test live URLs in GSC to establish pre-migration baseline |
| 08:15 | **Verify Google Analytics on staging** | SEO | Confirm GA4 receives data from staging domain |
| 08:30 | **Export current Search Console data** | SEO | Save current queries, positions, CTR as pre-migration snapshot |
| 08:45 | **Pre-cutover team sync** | All | 15-min call: confirm go/no-go, assign roles, review rollback triggers |
| 09:00 | **Comm silence begins** | All | No content changes on WordPress; no code pushes to main |

### T-1h: Final Verification (09:00 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| 09:00 | **Last production build verification** | Dev | Confirm `dist/` contains `_redirects`, `_headers`, `robots.txt`, `sitemap-*.xml` |
| 09:10 | **Flush Cloudflare cache** (current WordPress) | Dev | Purge everything in Cloudflare dashboard — forces WordPress to serve fresh |
| 09:15 | **Take WordPress backup** | Dev | Full WP Engine/Flywheel backup point (named: `pre-migration-YYYY-MM-DD`) |
| 09:25 | **Screenshot current homepage** | QA | Full-page screenshot for visual comparison post-launch |
| 09:30 | **Notify stakeholders** — launch in 30 min | PM | Slack/email: "Active Oahu Tours migration beginning at 10:00 HST. Brief booking interruption possible; FareHarbor unaffected." |
| 09:45 | **Open monitoring dashboards** | All | Cloudflare Pages → Deployments, GA4 → Real-time, Search Console → Coverage |

### T-0: DNS Cutover (10:00 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| **10:00** | **DNS SWITCH** — Change A/CNAME record | Dev | In Cloudflare DNS: remove existing A record (Flywheel IP), ensure CNAME `@` → `active-oahu-tours.pages.dev` exists and is **proxied** (orange cloud) |
| **10:02** | **Verify CNAME record active** | Dev | `dig activeoahutours.com` — should return Cloudflare proxy IPs, not Flywheel |
| **10:05** | **Purge Cloudflare cache again** | Dev | Force fresh DNS resolution everywhere |
| **10:10** | **Verify SSL certificate** | Dev | Browse to `https://activeoahutours.com` — confirm padlock, no mixed content warnings |

### T+15min: Live Verification (10:15 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| **10:15** | **Homepage loads on production** | QA | `https://activeoahutours.com` — verify Astro site, not WordPress |
| **10:18** | **Tour page loads** | QA | `https://activeoahutours.com/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/` |
| **10:20** | **Booking flow live test** | QA | Click "Book This Adventure" → FareHarbor lightframe opens → select date → verify pricing |
| **10:25** | **Complete one test booking** | QA | Book a real tour, add note "LAUNCH TEST — DO NOT CHARGE", proceed to payment page, then cancel |
| **10:30** | **Guide page loads** | QA | Verify a guide page with Article schema |
| **10:35** | **Contact form test** | QA | Submit inquiry, verify delivery |
| **10:40** | **Mobile test** | QA | Load homepage + 1 tour page on mobile device — verify responsive layout |
| **10:45** | **Redirects spot-check** | QA | Test `/tours/` → `/activities/`, `/wp-admin/` → 410, 1 old review URL → `/reviews/` |
| **10:55** | **Security headers check** | Dev | `curl -I https://activeoahutours.com \| grep -E 'x-frame\|x-content\|strict-transport\|referrer\|permissions'` |

### T+1h: Search Engine Submission (11:00 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| **11:00** | **Submit sitemap to Google Search Console** | SEO | GSC → Sitemaps → Add `sitemap-index.xml` → Submit |
| **11:05** | **Submit sitemap to Bing Webmaster Tools** | SEO | Bing WMT → Sitemaps → Add `sitemap-index.xml` |
| **11:10** | **Request indexing for top pages** | SEO | GSC → URL Inspection → "Request Indexing" for: `/`, `/activities/`, `/oahu-kayaking-and-beach-adventures/`, top 5 money pages |
| **11:20** | **Verify robots.txt accessible** | SEO | `https://activeoahutours.com/robots.txt` — must allow Googlebot, point to sitemap |
| **11:30** | **Launch announcement** | PM | Post social media / send customer email if planned |
| **12:00** | **Lunch break / quiet monitoring** | All | Keep GA4 real-time + Cloudflare analytics open |

### T+2h to T+4h: Active Monitoring (12:00–14:00 HST)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| 12:00–14:00 | **Monitor GA4 real-time** | SEO | Look for: active users, pageviews, booking events. Should match typical pattern. |
| 12:00–14:00 | **Monitor Cloudflare analytics** | Dev | Check: 200 vs 404 vs 301 rates. 404s should be near zero. |
| 12:00–14:00 | **Monitor Search Console coverage** | SEO | Watch for any "Submitted URL has crawl issue" alerts |
| 13:00 | **Mid-launch check-in** | All | 10-min sync: any issues? any anomalies? |
| 14:00 | **Crawl with Screaming Frog** (optional) | SEO | Crawl `activeoahutours.com` with Screaming Frog — verify 0 internal 404s, correct 301s |

### T+24h: Day 1 Post-Launch (10:00 HST next day)

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| 10:00 | **Search Console: Coverage report review** | SEO | Check for errors, warnings, excluded pages. Address any crawl issues. |
| 10:30 | **Search Console: Performance report** | SEO | Compare clicks/impressions to same-day-last-week baseline |
| 11:00 | **GA4: Page load time check** | SEO | Compare average page load time vs WordPress baseline |
| 11:30 | **404 monitoring** | Dev | Check Cloudflare analytics for any unexpected 404s |
| 12:00 | **Booking volume check** | PM | Verify FareHarbor bookings flowing normally — compare to typical day |

### T+48h: 301 Redirect Validation

| Time | Action | Owner | Notes |
|------|--------|-------|-------|
| 10:00 | **Full redirect audit** | Dev | Test ALL 65 redirects from `_redirects` file against production |
| 10:30 | **Check GSC for redirect chains** | SEO | No 301→301 chains; all redirects should be single-hop |
| 11:00 | **Bing: Index status review** | SEO | Verify Bing has processed sitemap, no errors |
| 11:30 | **GA4: Conversion tracking** | SEO | Verify booking events, phone call clicks, form submissions all tracking |

---

## 3. Rollback Plan — Revert to WordPress in Under 15 Minutes

### 3.1 Rollback Trigger Criteria

Initiate rollback if ANY of these occur:
- **Booking breakage**: FareHarbor integration fails on production (unlikely — FH is independent, but test)
- **>5% 404 rate**: Cloudflare analytics show unexpected 404s on key URLs
- **SSL failure**: HTTPS doesn't establish within 5 min of DNS change
- **Blank pages**: Homepage or money pages don't render
- **Schema spam**: Google flags structured data as invalid across multiple pages
- **Stakeholder calls it**: Anyone authorized can trigger rollback

### 3.2 Rollback Procedure (Step by Step)

**Estimated time: 5–10 minutes | Maximum: 15 minutes**

```
STEP 1: DNS REVERT (1 minute)
─────────────────────────────
1. Log in to Cloudflare Dashboard → activeoahutours.com → DNS
2. Remove CNAME record pointing to active-oahu-tours.pages.dev
3. Restore A record pointing to Flywheel/WP Engine IP:
   Name: @  |  Type: A  |  Target: [Flywheel IP — documented pre-launch]
4. Ensure proxy is ON (orange cloud)
5. Wait 2–3 minutes for Cloudflare edge to update

STEP 2: SSL VERIFICATION (2 minutes)
─────────────────────────────────────
6. Browse to https://activeoahutours.com
7. Verify WordPress site loads (may show briefly stale Astro page due to cache)
8. If stale: Cloudflare → Caching → Purge Everything → wait 30s → retry

STEP 3: FUNCTIONAL CHECK (3 minutes)
─────────────────────────────────────
9. Verify homepage loads (WordPress)
10. Test a booking flow: /activities/kailua-bay-mokulua-island-self-guided-kayak-tour/
11. Verify FareHarbor widget loads and is bookable

STEP 4: SEARCH ENGINE NOTIFICATION (5 minutes)
──────────────────────────────────────────────
12. GSC → Settings → Change of Address: If rollback is permanent,
    NOTIFY Google that the site moved back
13. Re-submit WordPress sitemap if needed

STEP 5: COMMUNICATION (immediately)
─────────────────────────────────────
14. Notify team: "Rollback initiated at [TIME HST]. WordPress restored.
    Investigating Astro launch issue."
15. Post-mortem scheduled for next business day
```

### 3.3 Communication Template — Rollback

**Internal (Slack/Email):**

> ⚠️ **ROLLBACK INITIATED** — Active Oahu Tours Migration
>
> **Time:** [TIMESTAMP HST]
> **Trigger:** [BRIEF REASON — e.g., "404 spike on /activities/" or "SSL not provisioning"]
> **Status:** WordPress restored, DNS reverted, site operational
> **Customer Impact:** None expected (FareHarbor independent; DNS change ~2 min)
> **Next Steps:** Post-mortem tomorrow at 09:00 HST. Do NOT re-attempt launch until root cause identified.
> **Contact:** [PM NAME / PHONE]

**Customer Communication (only if booking interruption > 5 minutes):**

> Aloha from Active Oahu Tours! 🌺
>
> We're making some exciting improvements to our website right now. Our booking system is fully operational — you can still book any tour online at:
>
> https://fareharbor.com/embeds/book/activeoahutours/
>
> Or call us at (808) XXX-XXXX and we'll help you book over the phone. Mahalo for your patience!

---

## 4. Post-Launch Monitoring Plan

### 4.1 Week 1: Daily Checks (Intensive)

**Check each day at 09:00 HST:**

| Check | Tool | Acceptable | Action if Failing |
|-------|------|------------|-------------------|
| **Site loads** | Browser | Homepage renders in < 2s | Rollback if sustained |
| **404 rate** | Cloudflare Analytics | < 1% of requests | Investigate source URLs, add redirects |
| **GA4 real-time** | Google Analytics | Active users within normal range | Check for tracking snippet issues |
| **Bookings received** | FareHarbor dashboard | Within 20% of daily average | Call FareHarbor support if broken |
| **GSC coverage errors** | Search Console | 0 new errors | Fix any crawl errors immediately |
| **Sitemap status** | GSC → Sitemaps | "Success" with all URLs discovered | Re-submit if failed |
| **SSL certificate** | Browser padlock | Valid, no warnings | Cloudflare dashboard → SSL/TLS |
| **Core Web Vitals** | GSC → Experience | "Good" for LCP, INP, CLS | Optimize flagged pages |
| **Schema errors** | GSC → Enhancements | 0 errors across all schema types | Fix invalid schema, re-validate |
| **Contact form** | Test submission | Delivers to inbox | Check form endpoint |

### 4.2 Month 1: Weekly Checks

**Check each Monday at 09:00 HST:**

| Check | Tool | Acceptable | Notes |
|-------|------|------------|-------|
| **Organic traffic trend** | GSC Performance | Within 10% of pre-migration baseline | Some fluctuation normal first 2 weeks |
| **Top keyword positions** | GSC / rank tracker | No page-1 keywords dropped > 3 positions | Investigate any significant drops |
| **Index status** | GSC Coverage | > 95% of submitted URLs indexed | Request indexing for any unindexed URLs |
| **Page speed** | Lighthouse | Performance ≥ 95 maintained | Re-run on homepage + top 5 pages |
| **Redirect chains** | Screaming Frog | 0 chains (all single-hop 301s) | Fix any discovered chains |
| **Broken links** | Screaming Frog / link checker | 0 internal 404s | Fix or redirect broken links |
| **FareHarbor health** | Manual test | Booking flow works end-to-end | Check after any FH platform updates |
| **Security scan** | Cloudflare WAF | 0 blocked threats indicating new vulns | Review any WAF events |

### 4.3 SEO Ranking Monitoring

#### Critical Pages to Monitor Daily (Week 1) / Weekly (Month 1):

| Page | Primary Keyword | Pre-Migration Position | Monitor For |
|------|----------------|----------------------|-------------|
| `/` | "Oahu kayak tours" | [Record from GSC] | No drop > 3 positions |
| `/activities/` | "Oahu kayak rentals" | [Record from GSC] | No drop > 3 positions |
| `/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/` | "Kailua kayak rental" | [Record from GSC] | No drop > 3 positions |
| `/activities/chinamans-hat-self-guided-oahu-kayak-tour/` | "Chinaman's Hat kayak" | [Record from GSC] | No drop > 3 positions |
| `/oahu-kayaking-and-beach-adventures/best-places-to-kayak-on-oahu/` | "best places to kayak Oahu" | [Record from GSC] | No drop > 3 positions |
| `/oahu-kayaking-and-beach-adventures/ultimate-guide-for-kailua-beach-park/` | "Kailua Beach guide" | [Record from GSC] | No drop > 3 positions |

#### SEO Anomaly Response Protocol:

| Symptom | Investigation | Action |
|---------|--------------|--------|
| **Traffic drop > 15%** | Check GSC coverage for new errors; compare indexed pages pre/post | Fix crawl errors; re-submit sitemap; check robots.txt |
| **Single page drops out of index** | URL Inspection in GSC | Request re-indexing; verify no noindex tag; check canonical URL |
| **Schema disappears from SERP** | Rich Results Test on affected page | Fix schema markup; re-validate; re-index |
| **All rankings flatline** | Check if site is de-indexed (site:activeoahutours.com) | Emergency: check robots.txt, noindex tags, manual actions in GSC |
| **CTR drops significantly** | Compare SERP appearance (meta title/description) pre vs post | Adjust meta titles/descriptions if they changed during migration |

---

## 5. Launch Team & Contacts

| Role | Name | Responsibility | Contact |
|------|------|---------------|---------|
| **Launch Commander** | [PM Name] | Final go/no-go decisions, rollback authority | [Phone/Email] |
| **Developer** | [Dev Name] | DNS cutover, build verification, redirect testing | [Phone/Email] |
| **QA Engineer** | [QA Name] | Smoke testing, booking flow testing, mobile testing | [Phone/Email] |
| **SEO Specialist** | [SEO Name] | Search Console, sitemap submission, ranking monitoring | [Phone/Email] |
| **Stakeholder** | Michael Gulden | Content approval, rollback sign-off | mbgulden@gmail.com |

### External Contacts

| Service | Support Channel | Account ID | Notes |
|---------|----------------|------------|-------|
| **Cloudflare** | dashboard + support ticket | [Account ID] | Pages build issues, DNS, SSL |
| **FareHarbor** | support@fareharbor.com | `activeoahutours` shortname | Booking widget issues |
| **WP Engine / Flywheel** | support ticket | [Account ID] | WordPress rollback assistance |
| **GitHub** | github.com/mbgulden/active-oahu-tours | mbgulden | Source code, CI/CD |

---

## 6. Launch Decision Matrix

### GO Criteria (all must be met):

- [ ] All pre-launch checklist items (Section 1) checked off
- [ ] Staging environment smoke test passes (Section 2, T-3h)
- [ ] Schema validation passes (all 6 types)
- [ ] FareHarbor booking tested on staging
- [ ] Lighthouse score ≥ 92 Performance on staging
- [ ] 301 redirects verified on staging
- [ ] SSL working on staging
- [ ] Stakeholder sign-off received
- [ ] Rollback DNS info documented and tested
- [ ] Team briefed on roles and rollback triggers

### NO-GO Criteria (any one triggers delay):

- [ ] Any pre-launch checklist item incomplete
- [ ] Build fails on main branch
- [ ] Schema validation errors on staging
- [ ] Booking flow broken on staging
- [ ] SSL not provisioning
- [ ] > 5% of pages returning 404 on staging
- [ ] Stakeholder withholds approval
- [ ] External dependency down (Cloudflare outage, GitHub outage)

---

## 7. Quick Reference Cards

### DNS Cutover Command Cheat Sheet

```bash
# Verify current DNS (before cutover)
dig activeoahutours.com A
# Should show Flywheel IP

# After cutover — verify
dig activeoahutours.com
# Should show Cloudflare proxy IPs (104.x.x.x or 172.x.x.x)

# Check Cloudflare Pages deployment
curl -I https://active-oahu-tours.pages.dev
# Status: 200

# Test production with host header (before DNS cutover)
curl -H "Host: activeoahutours.com" https://active-oahu-tours.pages.dev/
# Should return Astro HTML

# Purge Cloudflare cache
# Done via dashboard: activeoahutours.com → Caching → Purge Everything
```

### Emergency Rollback Commands

```bash
# 1. Check if WordPress is still running at Flywheel IP
curl -I http://[FLYWHEEL_IP] -H "Host: activeoahutours.com"
# Should return 200 from WordPress

# 2. Check Cloudflare DNS propagation
curl -I https://activeoahutours.com
# If showing Astro and we want WordPress: DNS change hasn't propagated yet — wait 2-3 min

# 3. Force-test WordPress through Cloudflare
curl -I https://activeoahutours.com --resolve activeoahutours.com:443:[FLYWHEEL_IP]
```

### Post-Launch URLs to Keep Open

| URL | Purpose |
|-----|---------|
| `https://dash.cloudflare.com/[account]/activeoahutours.com/analytics` | Traffic analytics, 404 monitoring |
| `https://analytics.google.com/` → GA4 → Real-time | User activity monitoring |
| `https://search.google.com/search-console` → Coverage | Crawl errors, index status |
| `https://fareharbor.com/dashboard/` | Booking activity verification |
| `https://github.com/mbgulden/active-oahu-tours/deployments` | Build/deploy status |

---

## Appendix A: Files Referenced

| File | Path | Purpose |
|------|------|---------|
| Architecture Plan | `docs/active-oahu/astro-migration-plan.md` | Full migration architecture |
| Cloudflare Setup | `docs/active-oahu/cloudflare-pages-setup.md` | Pages config, DNS, env vars |
| SEO Audit | `docs/active-oahu/seo-audit.md` | Current SEO baseline |
| AI SEO Strategy | `docs/active-oahu/ai-seo-strategy.md` | Post-migration SEO plan |
| Schema: LocalBusiness | `data/schema/localbusiness.json` | JSON-LD reference |
| Schema: Tour | `data/schema/tour-mokulua.json` | JSON-LD reference |
| Schema: FAQ | `data/schema/faq-kayak.json` | JSON-LD reference |
| Schema: Article | `data/schema/article-kailua-guide.json` | JSON-LD reference |
| Schema: Breadcrumb | `data/schema/breadcrumb-tour.json` | JSON-LD reference |
| Schema: HowTo | `data/schema/howto-mokulua.json` | JSON-LD reference |
| Wrangler Config | `active-oahu-tours/wrangler.toml` | Cloudflare Pages config |
| Redirects | `active-oahu-tours/public/_redirects` | 301 rules |
| Headers | `active-oahu-tours/public/_headers` | Security + cache headers |

## Appendix B: WordPress Rollback DNS Reference

```
Pre-migration DNS record (DOCUMENT BEFORE LAUNCH — FILL IN ACTUAL VALUES):

Type: A
Name: @
IPv4: [FLYWHEEL_WP_ENGINE_IP]   ← Document this now
TTL: Auto
Proxy: Proxied (orange cloud)

Type: CNAME
Name: www
Target: activeoahutours.com
TTL: Auto
Proxy: Proxied (orange cloud)
```

---

*Document generated for GRO-125 | Migration Launch Plan for Active Oahu Tours*
