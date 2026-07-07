# SEO Audit Report: activeoahutours.com

**Date:** May 29, 2026
**Task:** GRO-117 — SEO Audit & Competitive Analysis
**URL:** https://activeoahutours.com

---

## 1. Executive Summary

Active Oahu Tours is a kayak rental & tour operator based in Kailua, Oahu. The site runs on WordPress, hosted on Flywheel, fronted by Cloudflare (with APO enabled). It uses FareHarbor for bookings and Weglot for Japanese translation. The site has solid fundamentals but several critical SEO gaps compared to competitors — especially around schema markup, internal linking, and content depth.

**Overall Grade: B-** — Good technical foundation, but missing key on-page & structured data elements that competitors leverage for rich results.

---

## 2. Current Tech Stack

| Layer | Technology |
|-------|-----------|
| CMS | WordPress (Kadence theme + blocks) |
| Hosting | Flywheel (x-fw-server: Flywheel/5.1.0) |
| CDN / Proxy | Cloudflare (CF-APO for WordPress, CF Edge Cache) |
| Booking | FareHarbor (embedded iframes + direct links) |
| Translation | Weglot (en → ja) |
| SEO Plugin | Yoast SEO (sitemaps confirmed) |
| Page Builder | Kadence Blocks (heavy use in source) |

---

## 3. Page Inventory (from Sitemap)

| Sitemap | Approx URLs | Last Modified | Notes |
|---------|------------|---------------|-------|
| page-sitemap.xml | 58 | 2026-04-21 | Main pages + blog content |
| activities-sitemap.xml | 22 | 2026-02-12 | Activity/tour CPT pages |
| rentals-sitemap.xml | 18 | 2025-05-22 | Rental pages |
| reviews-sitemap.xml | ? | 2025-05-16 | Review CPT |
| kayakguide-sitemap.xml | ? | 2023-02-02 | Guide content |
| category-sitemap.xml | ? | 2023-02-02 | Categories |
| job-sitemap.xml | ? | 2021-10-05 | Job listings |
| geo-sitemap.xml | ? | 2016-11-15 | Old geo data |

**Estimated total indexed pages: ~100-120**

---

## 4. On-Page SEO Analysis

### 4.1 Homepage

| Element | Value | Status |
|---------|-------|--------|
| Title | "Oahu Kayak Rentals in Kailua, Kayak to Mokulua Islands & Chinamans Hat" (65 chars) | ⚠️ Long — title tag shows `&amp;` instead of `&`, wastes chars |
| Meta Description | "Experience the best kayaking on Oahu with easy pickup at our shop..." (154 chars) | ✅ Good |
| H1 | "Oahu Kayak Rentals & Tours" | ✅ |
| Canonical | `https://activeoahutours.com` | ✅ |
| OG Title | "Oahu Kayak & Gear Rentals Near Laie, Kahana, Kualoa & Chinamans Hat" | ⚠️ Different from `<title>` |
| OG Description | Similar but slightly different | ⚠️ Inconsistent with meta description |
| OG Image | `/wp-content/uploads/2021/06/DSC5297_2000-e1642616607887.jpg` | ✅ Present (2000px wide) |
| Heading Structure | H1 ×1, H2 ×? (mixed), H3 ×17+ | ⚠️ Messy hierarchy — kadence blocks create many heading levels |

### 4.2 Key Inner Pages

#### /activities/ (Tours listing)
| Element | Status |
|---------|--------|
| Title: "Oahu Kayak Tours & Adventures, Kayak in Kailua, Oahu" | ✅ |
| Meta Description: decent | ✅ |
| OG:type = "object" | ⚠️ Should be "website" |
| **Missing OG Image** | 🔴 CRITICAL |
| **Missing OG Description** | 🔴 CRITICAL |
| H1: "Oahu Kayaking Activities and Tours" | ✅ |

#### /about-active-oahu-tours/
| Element | Status |
|---------|--------|
| Title: "About our Oahu Tours and Activities - Near Laie, Hawaii and PCC" | ✅ |
| Description fine | ✅ |
| OG Image present | ✅ |
| **Featured image missing alt text** | 🔴 |

#### /contact-us/
| Element | Status |
|---------|--------|
| Title fine | ✅ |
| **Missing OG Image** | 🔴 CRITICAL |
| **No OG Description** | 🔴 |

#### /tours/ — ❌ 404 Not Found
No `/tours/` page exists. The equivalent is `/activities/`, but `/tours/` returning 404 is a wasted opportunity for a redirect to `/activities/`.

### 4.3 URL Structure Notes
- Tour/adventure pages live under `/oahu-kayaking-and-beach-adventures/` subdirectory — long but descriptive
- Rental pages under `/oahu-equipment-rentals/`
- The site uses descriptive slugs with keywords: good for SEO
- `/tours/` (404) should 301 redirect to `/activities/`

---

## 5. Schema / Structured Data

### Current Schema (activeoahutours.com)
```json
// Schema 1: WebSite
{"@type":"WebSite", "name":"Active Oahu Tours & Activities",
 "potentialAction":{"@type":"SearchAction"...}}

// Schema 2: Organization
{"@type":"Organization", "name":"Active Oahu, LLC",
 "sameAs":["facebook","instagram","twitter"], "logo":"..."}
```

### Missing Schema (CRITICAL)
- 🔴 **LocalBusiness** — address, phone, geo coordinates, opening hours
- 🔴 **Tour / TouristAttraction** — individual tours have no product schema
- 🔴 **Review** — no aggregate rating schema despite TripAdvisor awards
- 🔴 **BreadcrumbList** — no breadcrumb schema on any page
- 🔴 **FAQ** — FAQ page exists (`/faq/`) but no FAQ schema

### Competitor Comparison: Schema

| Site | Schema Types |
|------|-------------|
| **Kualoa Ranch** (kualoa.com) | Minimal — WebSite only (effectively empty JSON-LD) |
| **Kailua Beach Adventures** (kailuabeachadventures.com) | ✅ WebSite + Organization + **LocalBusiness** (with openingHours, address, phone, image) |
| **Go Oahu** (gooahu.com) | ✅ TouristInformationCenter + Organization + WebSite + WebPage + Article + Person |
| **HawaiiActivities.com** | ✅ TouristDestination (aggregator schema) |
| **Blue Hawaii Private Tours** | ❌ No schema at all |
| **Active Oahu** | ⚠️ WebSite + Organization only |

---

## 6. Technical SEO

### 6.1 Performance & Caching
| Metric | Value |
|--------|-------|
| Homepage HTML size | ~194 KB |
| Cloudflare APO | ✅ Active (cf-apo-via: tcache) |
| Cloudflare Edge Cache | ✅ Active |
| Flywheel server cache | ✅ (x-cache: MISS, HIT patterns) |
| Time to first byte | ~0.58s (cached) |

### 6.2 Security Headers
| Header | Status |
|--------|--------|
| Content-Security-Policy | ⚠️ Report-only mode (not enforced) |
| X-Content-Type-Options: nosniff | ✅ |
| Strict-Transport-Security (HSTS) | ❌ Missing |
| X-Frame-Options | ❌ Missing |
| Referrer-Policy: no-referrer-when-downgrade | ✅ |
| Permissions-Policy | ❌ Missing |

### 6.3 Mobile
- Viewport meta tag: ✅ Present (`width=device-width, initial-scale=1`)
- Kadence theme is responsive

### 6.4 Hreflang (Weglot)
```
<link rel="alternate" hreflang="en" href="https://activeoahutours.com/"/>
<link rel="alternate" hreflang="ja" href="https://activeoahutours.com/ja/"/>
```
✅ Basic implementation. Only 2 languages (en, ja). No x-default tag.

### 6.5 Robots.txt
```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Sitemap: https://activeoahutours.com/wp-sitemap.xml
```
⚠️ Sitemap URL points to WordPress core sitemap, not the Yoast sitemap at `/sitemap.xml`. Both exist — potential confusion.

### 6.6 Images
- 23 `<img>` tags on homepage
- 2 images with empty `alt=""` — minor
- 15 images with `loading="lazy"` — good
- About page featured image missing alt text entirely — accessibility + SEO issue

---

## 7. Content & Keyword Analysis

### 7.1 Current Keyword Targeting (Homepage)
- Primary: "Oahu kayak rentals", "kayak in Kailua", "Mokulua Islands", "Chinamans Hat"
- The title tag mixes too many keyword phrases — dilutes focus
- Title is more rental-focused, but site also sells guided tours — inconsistent

### 7.2 Blog / Guide Content
The site has substantial guide content under `/oahu-kayaking-and-beach-adventures/`:
- "Ultimate Guide for Kailua Beach Park"
- "Top 5 Things To Do On Oahu"
- "Best Places to Kayak on Oahu"
- "Kayak Deliveries on Oahu"
- "What to Do in Kailua — Hidden Gems"

This is a strength — informational content targeting long-tail queries.

### 7.3 Content Gaps vs Competitors
| Topic | Active Oahu | Kualoa | Kailua Beach Adv. |
|-------|------------|--------|-------------------|
| Tour listing page | ✅ (/activities/) | ✅ Rich filters | ✅ Bundle deals |
| Testimonials on homepage | ❌ None | ✅ Carousel with 5 reviews | ✅ |
| Awards / badges | Hidden deep in /about/ | ✅ On homepage footer | ✅ |
| Video content | ❌ | ✅ Hero video | ❌ |
| Price visibility | FareHarbor embeds | ✅ On tour cards | ❌ (external) |
| "Best of" / package deals | ❌ | ✅ "Best of Kualoa Full Day" | ✅ "Bundle & Save" |
| Sustainability messaging | ❌ | ✅ "Kualoa Grown" section | ❌ |

---

## 8. Competitor Benchmark

### 8.1 Direct Competitors Identified

| # | Competitor | URL | Platform | Strengths |
|---|-----------|-----|----------|-----------|
| 1 | **Kualoa Ranch** | kualoa.com | Webflow | Brand authority, rich tour pages, awards, video, massive content, 4000+ acres |
| 2 | **Kailua Beach Adventures** | kailuabeachadventures.com | Squarespace | LocalBusiness schema, 40+ years history, bundle deals, direct competitor in Kailua |
| 3 | **Go Oahu** | gooahu.com | WordPress | Aggregator with Rank Math PRO schema, TouristInformationCenter schema |
| 4 | **HawaiiActivities.com** | hawaiiactivities.com | Custom/Veltra | Aggregator, TouristDestination schema, massive authority |
| 5 | **Blue Hawaii Private Tours** | bluehawaiiprivatetours.com | WordPress | Weak SEO — not a strong threat currently |

### 8.2 Competitive Gap Summary
Active Oahu's biggest competitor in the Kailua kayak space is **Kailua Beach Adventures**, which has:
- 3 schema types vs Active Oahu's 2
- LocalBusiness schema with full NAP + hours
- Homepage testimonials
- Bundle/save offers
- "40+ years" credibility marker

**Kualoa Ranch** is in a different league but sets the UX/content bar for Oahu tour operators.

---

## 9. Priority Recommendations

### 🔴 HIGH PRIORITY (Implement Immediately)

1. **Add LocalBusiness Schema**
   - Include: address (Kailua storefront), phone, geo coordinates, opening hours, price range
   - This is table stakes for local SEO — Kailua Beach Adventures has this

2. **Fix /tours/ 404 → 301 redirect to /activities/**
   - `/tours/` is a common URL path users try; returning 404 loses traffic

3. **Add OG Images to /activities/ and /contact-us/**
   - Social sharing previews broken for key pages

4. **Add Tour/Product Schema to individual activity pages**
   - Use `TouristAttraction` or `Trip` schema on each tour/adventure page
   - Include price, duration, location, description, images

5. **Fix robots.txt sitemap reference**
   - Points to `/wp-sitemap.xml` (WP core) but Yoast generates `/sitemap.xml`
   - Choose one and be consistent, or link both

### 🟡 MEDIUM PRIORITY

6. **Add Review/AggregateRating Schema**
   - Active Oahu won 2022 TripAdvisor Travelers' Choice — showcase this in schema
   - Add testimonials section to homepage (competitors all have this)

7. **HSTS Security Header**
   - Add `Strict-Transport-Security: max-age=31536000; includeSubDomains`

8. **Heading Structure Cleanup**
   - Too many H3/H4 tags from Kadence blocks — audit and restructure
   - Ensure single H1 per page, logical H2→H3→H4 hierarchy

9. **Add BreadcrumbList Schema**
   - Yoast should support this; enable if not already

10. **FAQ Schema on /faq/ pages**
    - The faq content is structured as Q&A — perfect for FAQ rich results

### 🟢 LOW PRIORITY

11. **Title Tag Consistency**
    - Align `<title>`, OG title, and H1 to the same primary keyword focus
    - Consider: "Oahu Kayak Tours & Rentals | Active Oahu" (~45 chars)

12. **Homepage Testimonials Section**
    - Add 3-5 curated reviews with star ratings visible above the fold

13. **Add x-default hreflang**
    - Currently only en + ja; add `<link rel="alternate" hreflang="x-default" href="..."/>`

14. **Enforce CSP**
    - Move from report-only to enforced Content-Security-Policy

15. **Image Alt Text Audit**
    - Fix missing alt on about page featured image
    - Ensure all images have descriptive alt text

16. **"Bundle & Save" / Package Deals Page**
    - Competitors promote bundles; Active Oahu has `/oahu-tour-packages/` — feature it more prominently

---

## 10. Quick Wins Summary

| Action | Effort | Impact |
|--------|--------|--------|
| 301 /tours/ → /activities/ | 5 min | Medium |
| Add LocalBusiness schema via Yoast | 15 min | High |
| Add OG images to /activities/ & /contact/ | 10 min | Medium |
| Enable breadcrumb schema in Yoast | 5 min | Medium |
| Add HSTS header via Cloudflare | 5 min | Low-Med |
| Fix robots.txt sitemap URL | 5 min | Low |
| Add testimonials section to homepage | 1-2 hrs | High |

---

## 11. Technology Strengths

- **Cloudflare APO**: Excellent for WordPress performance — page caching at edge
- **Flywheel**: Solid managed WP hosting with built-in caching
- **Yoast SEO**: Industry-standard plugin, properly configured sitemaps
- **Weglot**: Good translation implementation with proper hreflang tags
- **FareHarbor**: Leading tour booking platform with robust embed support

## 12. Methodology

This audit was conducted via:
- `curl` fetches of homepage + key inner pages with `Mozilla/5.0` user agent
- HTTP response header analysis
- Sitemap enumeration via Yoast sitemap index
- Manual source code inspection of meta tags, schema, and heading structure
- Competitive analysis via same methodology on 5 competitor sites

No crawling tools, paid APIs, or JavaScript rendering were used. Some client-side content may not be captured.

---

*Report generated for GRO-117 | Active Oahu SEO Audit*
