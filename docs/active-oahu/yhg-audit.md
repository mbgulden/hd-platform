# Your Hawaii Guide (yourhawaiiguide.com) — Site Audit

**Date**: 2026-05-29  
**Task**: GRO-133  
**Status**: CRITICAL — Site content has been lost; blog posts are empty shells

---

## 1. Domain & Hosting

| Property | Detail |
|----------|--------|
| Domain | yourhawaiiguide.com |
| Registrar | Squarespace Domains II LLC |
| Registration Date | 2018-02-08 |
| Expiration Date | 2032-02-08 |
| Last Updated | 2024-04-09 |
| Organization | Active Oahu, LLC |
| Nameservers | ns-cloud-a1~a4.googledomains.com (Google Domains DNS) |
| Hosting | Flywheel (confirmed via `x-fw-server: Flywheel/5.1.0`) |
| WordPress Version | 6.9.4 |
| Theme | Custom "activeoahu" theme (same name as sibling site) |
| SSL | Valid (HTTPS loads, no issues) |

---

## 2. Content Inventory

### 2.1 Page Types & Counts

| Content Type | Count | Sitemap Last Modified |
|-------------|-------|----------------------|
| Pages | 24 | 2023-11-29 |
| Blog Posts | 26 | 2022-09-01 |
| Activities (CPT) | 75 | 2023-09-05 |
| Companies (CPT) | 34 | 2023-09-05 |
| Categories | 39 | — |
| Tags | 75 | — |
| Free Things To Do | In free-sitemap.xml | 2022-05-27 |

### 2.2 Blog Posts — ALL CONTENT LOST

**CRITICAL FINDING**: All 26 blog posts have **empty body content**. The WordPress REST API returns either `""` or `"<p></p>\n"` for every post's `content.rendered` field. Individual post pages load but display **no article text** — only the header, navigation, featured image card, and footer.

The post listing page (`/blog/`) renders grid cards with featured images and "X min read" labels, but clicking through to any post yields an empty page.

**Post timeline**:
- **2022 (May)**: 4 posts — food/restaurant content (very short, likely Instagram-embeds only)
  - "The pancakes are iconic"
  - "One of Waikiki's best kept secrets"
  - "Some of the best ramen on Kalakaua"
  - "A Wednesday night at home"
- **2019 (Oct)**: 1 post — "Snorkeling with Wild Dolphins in Oahu"
- **2018 (Jan–Apr)**: 12 posts — hikes, beaches, adventures
- **2017 (Mar–Dec)**: 9 posts — beaches, activities, North Shore content

**Post topics** (titles only survive):
- Hiking: Lanikai Pillboxes, Hauʻula Loop, Makaua Falls, Kaʻaʻawa ridge
- Beaches: Hukilau, Pounders, Castle's, Kawela Bay, 3 North Shore beaches
- Water: Rainforest kayaking, Turtle Canyon snorkel, shark cage diving, open-ocean shark swim
- Activities: Skydiving, longboard surfing, beginner surf lessons, rock climbing
- Sights: Byodo-In Temple, Hoʻomaluhia Gardens, Laie Point

### 2.3 Pages

**Content pages** (have real content):
- Home (page ID 970)
- About
- Blog ("Adventure Log")
- Activity Listing
- Activity Map
- Bucket List
- Search

**Utility pages** (membership/ecommerce):
- Log In, Sign Up, My Account, My Profile, Reset Password
- Member Directory
- Checkout, Order Confirmation, Order Failed
- Cancellation Policy, Privacy Policy, How to Cancel/Request a Refund

**Map pages**:
- All Activities Map
- Company Map
- Free Things To Do Map
- Bucket List Map View
- Activities Filter

### 2.4 Activities (Custom Post Type)

75 activity entries. The sitemap shows they include items like:
- `/activities/surfing-lessons/`
- `/activities/surf-hnl-surf-lessons/`
- `/activities/turtle-canyons-snorkel-excursion/`
- `/activities/waikiki-sunset-cruise/`

These appear to be product/tour listing pages with booking integration (FareHarbor). Content quality of these CPT entries was not deeply inspected but they appear to have descriptions based on the /activities/ archive page.

### 2.5 Companies (Custom Post Type)

34 company profiles including:
- Aloha Motorsports, Surf HNL, Aaron's Dive Shop, Hawaii Shark Encounters, etc.

---

## 3. Technical Setup

### 3.1 Plugins Detected
- **Favorites** (v2.3.4) — Bucket List / wishlist functionality
- **WP User Avatar** (v4.15.6) — User profiles
- **Site Kit by Google** (v1.126.0) — GA4 + Search Console connector
- **FareHarbor** — Booking embed (`fareharbor.com/embeds/api/v1/`)

### 3.2 Analytics
- **Universal Analytics**: UA-56349810-1 (legacy, still firing via inline script)
- **GA4**: GT-TX295KR (via Site Kit)
- Google Tag Manager not used — direct gtag implementation
- **Note**: Both tracking codes are present. UA property is deprecated (Google stopped processing July 2024). GA4 property is active.

### 3.3 Schema.org Markup
- WebSite: `name: "Active Oahu"` (⚠️ brand confusion with activeoahu.com)
- Organization: `name: "Active Oahu, LLC"`
- Open Graph: Facebook App ID `427151840970360`, publisher `facebook.com/activeoahutours`
- Twitter: `@activeoahutours`

### 3.4 robots.txt
```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Sitemap: https://yourhawaiiguide.com/wp-sitemap.xml
```
✅ Clean — no blocking of content areas.

### 3.5 Sitemaps
- `/wp-sitemap.xml` — WordPress core sitemap index
- 7 sub-sitemaps: posts, pages, activities, companies, free, categories, post_tags

---

## 4. Relationship to Sibling Sites

### 4.1 activeoahu.com
- **301 redirect**: `activeoahu.com/blog` → `yourhawaiiguide.com/blog/`
- activeoahu.com is the operational site (kayak rentals, e-bike tours, Kailua shop)
- activeoahu.com does NOT host its own blog — it depends on YHG for content marketing
- **Shared branding**: Both use "Active Oahu" in schema/site name
- YHG's schema declares `name: "Active Oahu"` — creates brand identity confusion
- YHG homepage links to `activeoahutours.com` for direct booking

### 4.2 activeoahutours.com
- Booking-focused site (kayak tours, rentals)
- `/blog` → 301 redirects to homepage (no blog at all)
- Cloudflare hosting, FareHarbor integration
- TripAdvisor integration
- **No content overlap** — purely transactional/booking

### 4.3 Content Overlap Assessment
| Content Area | YHG | activeoahu.com | activeoahutours.com |
|-------------|-----|---------------|-------------------|
| Blog/Articles | 26 (empty) | Redirects to YHG | None |
| Tour Listings | 75 activities | Operational pages | Booking pages |
| Company Profiles | 34 | N/A | N/A |
| Maps | Multiple | N/A | N/A |

**Key insight**: YHG was built as the content marketing / SEO arm for the Active Oahu brand. activeoahu.com handles operations, activeoahutours.com handles bookings. YHG's blog was supposed to drive organic traffic and funnel to the other sites. With the blog content gone, this strategy is broken.

---

## 5. Content Quality Assessment

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Blog Content | ❌ ZERO | All 26 posts are empty shells — content lost |
| Page Content | ⚠️ THIN | Homepage and a few landing pages have text; many pages are templates |
| Activity Listings | ⚠️ UNKNOWN | 75 entries exist but content depth not verified |
| Metadata | ⚠️ ADEQUATE | Titles exist; NO meta descriptions on blog posts |
| Images | ✅ PRESENT | Featured images survive for all posts |
| Freshness | ❌ STALE | Last content: May 2022 (4+ years ago) |
| Internal Linking | ⚠️ BASIC | Nav menu links between sections; blog grid has "More Info" links |

---

## 6. SEO / Indexing Status

### 6.1 Indexed Pages
- Google `site:yourhawaiiguide.com` search was inconclusive (automated query blocked)
- Sitemaps submitted: 7 sub-sitemaps covering all content types
- Given content loss and staleness, likely heavily deindexed

### 6.2 SEO Issues
1. **No meta descriptions** on any blog post or archive page — only the homepage has one
2. **All blog body content is empty** — Google sees blank pages with no unique text
3. **Brand name inconsistency**: Site title is "Your Hawaii Guide" but schema says "Active Oahu"
4. **No recent content**: Last post May 2022 — 4+ years of no updates signals abandonment
5. **Thin content pages**: Many utility pages (login, checkout, etc.) add noise to index
6. **Duplicate GA properties**: Both UA (dead) and GA4 fire on every page

### 6.3 Domain Authority Indicators
- Domain age: ~8 years (registered 2018)
- Content age: 4+ years stale
- No backlink analysis performed (requires external tool)
- The domain likely had some authority from 2017-2019 content era, now severely decayed

---

## 7. Critical Issues Summary

| # | Issue | Severity | Impact |
|---|-------|----------|--------|
| 1 | **All 26 blog posts have empty content** | 🔴 CRITICAL | Zero SEO value; site is a content graveyard |
| 2 | **No content published since May 2022** | 🔴 CRITICAL | 4+ years stale; Google treats as abandoned |
| 3 | **No meta descriptions** on posts/pages | 🟡 HIGH | Poor CTR in SERPs |
| 4 | **Brand name confusion** (YHG vs Active Oahu) | 🟡 HIGH | Schema conflicts, user confusion |
| 5 | **Dual GA tracking** (UA dead + GA4) | 🟢 LOW | UA code is dead weight; no harm but messy |
| 6 | **Bootstrap 3.3.5 / jQuery 2.2.2** | 🟡 MEDIUM | Very outdated frontend dependencies |
| 7 | **Membership features with no content** | 🟡 MEDIUM | Dead features (login, checkout) add noise |

---

## 8. Recommendations

### Immediate (Week 1)
1. **Recover blog content**: Check WordPress revisions, database backups, or Wayback Machine for original post content. The posts have titles and featured images so they can be reconstructed.
2. **Audit remaining CPT content**: Verify that the 75 Activities and 34 Companies have actual descriptions.

### Short-Term (Month 1)
3. **Fix meta descriptions**: Add unique meta descriptions to all pages and posts.
4. **Resolve brand naming**: Either commit to "Your Hawaii Guide" branding or fully merge into "Active Oahu" — consistent titles, schema, and navigation.
5. **Remove dead UA tracking**: The UA-56349810-1 code fires on every page but Google stopped processing it. Remove or consolidate to GA4 only.
6. **Redirect strategy**: Decide if YHG should continue as a standalone content site or be folded into activeoahu.com.

### Strategic
7. **Content strategy**: If YHG is kept, it needs a content plan — the Oahu activities niche is competitive and 4 years without updates has likely killed any rankings.
8. **Technical upgrade**: Update Bootstrap, jQuery, and modernize the custom theme.
9. **Consider consolidation**: Three domains (activeoahu.com, activeoahutours.com, yourhawaiiguide.com) fragment authority. Consider consolidating blog content into activeoahu.com/blog/ (which already redirects to YHG — reverse this).

---

## 8. Data Sources
- WordPress REST API: `/wp-json/wp/v2/posts`, `/wp-json/wp/v2/pages`
- XML Sitemaps: `/sitemap.xml`, `/post-sitemap.xml`, `/page-sitemap.xml`, etc.
- RDAP/WHOIS lookup
- Direct HTML inspection of homepage, blog listing, and individual posts
- HTTP headers for hosting detection
- Comparison curl of activeoahu.com and activeoahutours.com
