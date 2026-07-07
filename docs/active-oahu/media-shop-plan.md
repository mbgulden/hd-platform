# Self-Service Media Shop — Architecture & Design

**Ticket:** GRO-131  
**Date:** May 29, 2026  
**Author:** Hermes Agent (Media Shop Architecture)  
**Status:** Architecture Complete — Ready for implementation  
**Depends On:** GRO-119 (Astro Migration), GRO-126 (Media Inventory), GRO-127 (Media Tagging)

---

## Executive Summary

Active Oahu Tours holds **698 GB** of professional photos and videos (9,592 files: 8,425 photos, 1,167 videos), captured over years of kayak tours, drone flights, and adventure photography across Oahu's windward coast. This document designs a **self-service media shop** to monetize that archive — selling physical prints, digital downloads, and usage licenses directly from the Astro-powered website.

### Three Revenue Streams

| Stream | Platform | Revenue Model | Margins |
|--------|----------|---------------|---------|
| **Physical prints** (canvas, framed, poster) | Printful (print-on-demand) | Markup over Printful base cost | ~40-65% |
| **Digital downloads** (personal/commercial) | Stripe Checkout + Cloudflare R2 | One-time payment, instant delivery | ~93% (after Stripe fees) |
| **Photo licensing** (commercial/exclusive) | Stripe Checkout + manual/auto delivery | Tiered pricing, one-time or buyout | ~93% |

---

## 1. Market & Platform Research

### 1.1 Print-on-Demand — Comparison

| Criterion | Printful | Gelato | Printify |
|-----------|----------|--------|----------|
| Print quality | ★★★★★ Industry best | ★★★★ Very good | ★★★ Variable by provider |
| Product range | Canvas, framed, posters, metal, acrylic, apparel | Canvas, framed, posters, photo books | Canvas, framed, posters (provider-dependent) |
| US fulfillment | NC, CA, TX, WI, NY | Network of 130+ global locations | Multiple US providers |
| Hawaii shipping | ~$8-12 (from CA typically) | ~$7-11 (may print in Honolulu if available) | ~$8-14 |
| API maturity | Excellent REST API, webhooks | Good REST API | Good API (varies by provider) |
| Base cost (24×36 canvas) | ~$65-85 | ~$55-75 | ~$50-70 (best provider) |
| White-label | Full | Full | Full |
| Custom packaging | Yes (extra) | Limited | No |
| Ease of setup | ★★★★★ | ★★★★ | ★★★ |

**Winner: Printful.** Best quality for fine art prints (our primary use case), best API, consistent output. Canvas prints at $65-85 base let us retail at $249 (65%+ margin). Gelato is a strong #2 if international shipping becomes priority.

### 1.2 Digital Downloads — Comparison

| Criterion | Stripe (self-hosted) | Gumroad | Lemon Squeezy |
|-----------|---------------------|---------|---------------|
| Transaction fee | 2.9% + $0.30 | 10% (free) / 3.5% (paid) | 5% + $0.50 |
| Monthly cost | $0 | $0-$10/mo | $0 |
| File delivery | Custom (R2 signed URLs) | Built-in | Built-in |
| Custom domain | Full control | Paid plan only | Yes |
| Global tax (VAT/GST) | Stripe Tax ($) | Built-in | Built-in (MoR) |
| License key / tier support | Custom | Limited | Custom fields |
| API/integration | Best-in-class | Good | Good |
| Hawaii GET handling | Manual (configure in Stripe) | Built-in | Built-in |
| Payout schedule | 2-day rolling | Weekly (free) / Instant (paid) | Varies |

**Winner: Stripe (self-hosted).** The Astro site is already JavaScript-heavy. Stripe Checkout is a drop-in hosted payment page with zero monthly cost and the lowest per-transaction fees. At $29/download, Stripe takes ~$1.14 vs Gumroad's $2.90. For a static site, we integrate via a **Cloudflare Worker** webhook handler — 100K free requests/day, no server needed.

### 1.3 Photo Licensing — Comparison

| Criterion | Pixsy | PhotoShelter | Custom (Stripe + Manual) |
|-----------|-------|-------------|--------------------------|
| Focus | Copyright enforcement | Pro photographer platform | Direct sales |
| Monthly cost | Free scan / paid enforcement | $10-50/mo | $0 |
| License management | No | Full DAM + licensing | Custom workflow |
| Complexity | Low | High | Medium |
| Fit for our scale | Wrong use case | Overkill at 698 GB | Perfect |

**Winner: Custom.** PhotoShelter is designed for full-time pros managing thousands of client deliveries — overkill for our curated gallery of ~50-200 hero images. A custom Stripe-based checkout with clear license tier descriptions is simpler, cheaper, and more flexible.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ACTIVE OAHU GALLERY SHOP                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  Astro Site   │    │  Cloudflare   │    │   Printful API        │   │
│  │  (Static SSG) │    │  Worker       │    │   (REST + Webhooks)   │   │
│  │               │    │  (Webhook)    │    │                       │   │
│  │  /gallery     │───▶│               │───▶│  Create order         │   │
│  │  /gallery/*   │    │  Stripe       │    │  Confirm shipment     │   │
│  │  /shop        │    │  webhook      │    │  Track delivery       │   │
│  │               │    │  handler      │    │                       │   │
│  └──────┬────────┘    └──────┬───────┘    └──────────────────────┘   │
│         │                    │                                        │
│         │  Stripe Checkout   │  Email customer                       │
│         │  (Hosted page)     │  Download link                       │
│         │                    │                                        │
│  ┌──────▼────────┐    ┌──────▼───────┐    ┌──────────────────────┐   │
│  │  Stripe.com    │    │  Cloudflare   │    │  Resend (Email)       │   │
│  │  Payment        │    │  R2 Storage   │    │  Transactional        │   │
│  │  Processing     │    │  Full-res     │    │  emails               │   │
│  └────────────────┘    │  images       │    └──────────────────────┘   │
│                        └──────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 Component Breakdown

#### A. Astro Static Site (Frontend)

The shop lives at `/gallery/` as part of the Astro site on Cloudflare Pages.

**Pages:**
- `/gallery/` — Gallery index with category browsing, featured items, search
- `/gallery/[category]/` — Category pages (e.g., `/gallery/mokulua-islands/`)
- `/gallery/[category]/[slug]/` — Product detail page with size/format picker
- `/gallery/cart/` — Cart review (client-side state via localStorage + Astro nano-stores)
- `/checkout/complete/` — Order confirmation page (reads Stripe session from URL)

**Key Components:**
- `ProductCard.astro` — Thumbnail + title + starting price
- `ProductDetail.astro` — Full image preview (watermarked), format/size selector, pricing table, add-to-cart
- `CartDrawer.astro` — Slide-out cart summary
- `CheckoutButton.astro` — Initiates Stripe Checkout redirect

**How it works:**
1. User browses watermarked previews at multiple responsive sizes
2. Selects product, format (print/digital/license), size, and quantity
3. Adds to client-side cart (localStorage, no account required)
4. Clicks Checkout → redirects to Stripe Checkout (hosted page)
5. Stripe handles payment, tax (Hawaii GET 4.712%), and redirects back
6. Webhook fires for fulfillment

#### B. Stripe Checkout (Payment)

- **Hosted Checkout** — No sensitive card data touches our site
- **Products in Stripe Dashboard** — Each product variant (e.g., "Mokulua Golden Hour — 24×36 Canvas") is a Stripe Price object
- **Metadata** — Product ID, variant type (print/digital/license), size, format stored as Stripe metadata
- **Tax** — Hawaii GET (4.712%) configured per product via Stripe Tax
- **Shipping** — Printful rates shown at checkout (pulled via Printful API or hardcoded as flat rates per region)

#### C. Cloudflare Worker (Webhook Handler)

A single Worker handles the `checkout.session.completed` Stripe webhook:

```
POST /api/webhooks/stripe (Cloudflare Worker)
    │
    ├── Verify Stripe webhook signature (essential!)
    │
    ├── IF product type = "digital" OR "license":
    │   ├── Generate signed R2 download URL (24h expiry, 3 downloads max)
    │   ├── Send email via Resend with download link
    │   └── Update download counter in KV store
    │
    ├── IF product type = "print":
    │   ├── Call Printful API: POST /orders
    │   │   ├── Map product → Printful variant ID
    │   │   ├── Attach shipping address from Stripe session
    │   │   └── Attach full-res file (or reference R2 URL)
    │   ├── Send confirmation email to customer
    │   └── Store order reference in KV
    │
    └── IF product type = "exclusive" (license buyout):
        ├── Generate download link (same as digital)
        ├── Mark product as SOLD in KV store
        ├── Update products.json (remove from listings via CI rebuild)
        └── Send email + trigger site rebuild via Cloudflare Deploy Hook
```

**Why Cloudflare Worker:**
- Free tier: 100,000 requests/day (well above our needs)
- Zero cold start (global edge network)
- Integrated with R2, KV, and Resend
- No server to maintain

#### D. Printful API Integration

**Flow:**
1. Webhook receives order with shipping address
2. Worker maps our product SKU to Printful variant (`variant_id`)
3. Creates Printful order with:
   - `external_id`: our order reference (Stripe session ID)
   - `items[]`: variant + file URL (full-res from R2)
   - `recipient`: customer name + shipping address
   - `retail_costs`: our retail price (for customs docs)
4. Printful prints + ships → webhook notifies us → Worker emails customer with tracking

**Printful Variant Mapping:**

| Our Product | Printful Product | Printful Variant ID |
|-------------|-----------------|-------------------|
| 24×36 Canvas | Canvas 24×36″ | (assigned at setup) |
| 16×20 Framed | Framed Poster 16×20″ | (assigned at setup) |
| 18×24 Poster | Premium Poster 18×24″ | (assigned at setup) |

We maintain a `data/shop/printful-mapping.json` that maps our `product_id + format + size` to Printful variant IDs.

#### E. Cloudflare R2 (File Storage)

**Bucket structure:**
```
active-oahu-media/
├── full-res/
│   ├── prod-moku-golden-hour.jpg       (5464×3640, ~15MB)
│   ├── prod-moku-golden-hour.dng       (raw, ~60MB, exclusive only)
│   ├── prod-kayak-landing-moku.jpg     (6000×4000, ~18MB)
│   └── ...
├── watermarked/
│   ├── prod-moku-golden-hour-wm.jpg    (1600px wide, ~500KB)
│   └── ...
└── thumbnails/
    ├── prod-moku-golden-hour-400w.jpg  (400px, ~40KB)
    ├── prod-moku-golden-hour-800w.jpg  (800px, ~120KB)
    └── ...
```

**Cost estimate (R2):**
- Storage: 100 GB × $0.015/GB = $1.50/month
- Bandwidth: Free (R2 has zero egress to Cloudflare)
- Class A ops: ~$0.0004 per 1,000 (negligible)
- **Total: ~$2/month**

#### F. Email (Resend)

Transactional emails for:
1. Order confirmation (print) — "Your order is being printed!"
2. Download link (digital) — secure signed URL
3. Shipping notification (print) — tracking number
4. License certificate (license purchases)

Resend free tier: 100 emails/day, 3,000/month. Sufficient for launch.

---

## 3. Product Structure

### 3.1 Product Categories

| Category | Files Available | Hero Content |
|----------|----------------|--------------|
| **Mokulua Islands** | 1,272 files | Drone aerials, kayak approach, golden hour |
| **Drone Aerials** | 2,276 files | Kaneohe Bay, sandbars, coastal panoramas |
| **Kayak Action** | 1,389+ files | Paddling shots, island landings, group action |
| **Chinaman's Hat** | 1,159 files | Sunrise paddles, summit views, coastal landscapes |
| **Kahana Bay** | 1,020 files | River jungle paddles, rainforest, serene bays |
| **Underwater & Snorkeling** | 232+ files | Sea turtles, tropical fish, coral, clear water |

### 3.2 Print Products

| Format | Sizes Available | Starting Price | Printful Base Cost | Margin |
|--------|----------------|---------------|-------------------|--------|
| **Poster** (premium matte) | 12×18, 18×24, 24×36 | $39 | $8-22 | ~55-65% |
| **Canvas** (gallery wrap) | 16×20, 20×24, 24×36, 30×40 | $149 | $50-85 | ~45-55% |
| **Framed** (matte black/white/oak) | 8×10, 11×14, 16×20, 20×30 | $89 | $35-70 | ~50-60% |

### 3.3 Digital License Tiers

| Tier | Price | Resolution | Uses | Restrictions |
|------|-------|-----------|------|-------------|
| **Personal Use** | $29 | Full (up to 6000×4000) | Wall art, personal wallpaper | No reproduction, no commercial use, no redistribution |
| **Commercial License** | $149 | Full (up to 6000×4000) | Website, marketing, ads, editorial, up to 100K impressions | No resale as art, no merchandise, no sublicensing |
| **Exclusive Rights** | $1,499 | Full + RAW file | Unlimited commercial, merchandise, sublicensing | We retain portfolio rights only; image removed from shop |

### 3.4 Pricing Strategy Rationale

- **Prints:** Priced at ~2.5-3× Printful base cost. Comparable to fine art prints on Etsy and local Hawaii galleries ($150-400 for canvas). Our unique, locally-shot content commands premium.
- **Digital (Personal):** $29 is impulse-buy territory for a beautiful Hawaii photo. Comparable to stock photo sites (Shutterstock: $29 for 2 images, Adobe Stock: $29.99 for 3).
- **Digital (Commercial):** $149 is standard for extended commercial stock licenses. Getty Images charges $150-500 for similar rights.
- **Exclusive: $1,499** — One-time buyout. Compares favorably to exclusive rights on 500px ($250-500) or custom commissions ($2,000-5,000 for drone photography).

---

## 4. User Flow

### 4.1 Browse → Purchase Print

```
1. Visitor lands on /gallery/
2. Browses categories (Mokulua Islands, Drone Aerials, etc.)
3. Clicks product → /gallery/mokulua-islands/golden-hour-panorama/
4. Views watermarked preview (full-width, zoom on hover)
5. Selects "Canvas Print" → "24×36"" → "Quantity: 1"
6. Price updates: $249.00 + $12.99 shipping
7. Clicks "Add to Cart" → CartDrawer slides in
8. Reviews cart, clicks "Checkout with Card"
9. Redirected to Stripe Checkout (hosted page)
10. Enters shipping address + card details
11. Stripe processes payment, shows confirmation
12. Redirected back to /checkout/complete/?session=cs_xxx
13. Receives email: "Your canvas print is being made!"
14. 3-5 days later: shipping confirmation with tracking
15. 5-10 days total: print arrives
```

### 4.2 Browse → Purchase Digital Download

```
1-7. Same as above
8. Visitor selects "Digital Download" → "Personal Use ($29)"
9. Clicks "Buy Digital Download"
10. Redirected to Stripe Checkout (no shipping address needed)
11. Payment processed instantly
12. Redirected to /checkout/complete/ with download button
13. Email arrives with secure download link (R2 signed URL)
14. Link valid for 24 hours, up to 3 downloads
15. File: watermark-free, full-resolution JPEG
```

### 4.3 Purchase Exclusive License

```
1-7. Same as above
8. Visitor selects "Exclusive Rights ($1,499)"
9. Clicks "Purchase Exclusive License" — modal confirms: "This image will be permanently removed from our shop."
10. Redirected to Stripe Checkout
11. Payment processed
12. Webhook handler:
    a. Generates download link (JPEG + RAW)
    b. Marks product as SOLD in Cloudflare KV
    c. Triggers Cloudflare Pages redeploy (via Deploy Hook)
    d. Product page now shows "Sold — Exclusive Rights"
13. Customer receives: JPEG, RAW/DNG, license certificate PDF
```

---

## 5. Technical Implementation Plan

### 5.1 Phase 1: Foundation (Week 1)

- [ ] **Stripe Setup**
  - Create Stripe account, configure products + prices
  - Set up Hawaii GET (4.712%) in Stripe Tax
  - Create webhook endpoint secret
- [ ] **R2 Bucket Setup**
  - Create `active-oahu-media` bucket
  - Upload 5 sample full-res images + watermarked thumbs
  - Configure CORS for Astro site domain
- [ ] **Cloudflare Worker**
  - Create `stripe-webhook` Worker
  - Implement signature verification
  - Implement digital download email flow
  - Deploy to Cloudflare

### 5.2 Phase 2: Astro Shop Pages (Week 2)

- [ ] **Gallery Index Page** (`/gallery/index.astro`)
  - Category grid from `products.json`
  - Featured products carousel
- [ ] **Category Pages** (`/gallery/[category].astro`)
  - Filtered product grid with thumbnails
  - Starting price overlay
- [ ] **Product Pages** (`/gallery/[category]/[slug].astro`)
  - Watermarked image with zoom (CSS `image-rendering` or lightbox)
  - Format/size selector (radio/card UI)
  - Live price calculation
  - Add to cart
- [ ] **Cart (Client-Side)**
  - Nano-stores for cart state
  - CartDrawer component
  - Stripe Checkout redirect builder

### 5.3 Phase 3: Printful Integration (Week 3)

- [ ] **Printful Account Setup**
  - Create account, configure store
  - Create product templates (canvas, framed, poster)
  - Generate and store variant IDs in `printful-mapping.json`
- [ ] **Webhook Handler — Print Orders**
  - Implement Printful order creation
  - Map our SKUs to Printful variants
  - Pass R2 file URLs to Printful
- [ ] **Shipping Tracking Webhook**
  - Listen for Printful `package_shipped` webhook
  - Email customer with tracking link
- [ ] **Tax Configuration**
  - Verify Hawaii GET handling for physical goods
  - Set up Printful tax settings (US sales tax handled by Printful)

### 5.4 Phase 4: Polish & Launch (Week 4)

- [ ] **License Certificate PDF Generation**
  - Auto-generate simple license certificate PDF on purchase
  - Include: image thumbnail, license tier, usage rights, date, purchaser name
- [ ] **Email Templates**
  - Design branded email templates in Resend
  - Print confirmation, digital download, shipping update, license certificate
- [ ] **Analytics**
  - Plausible/Fathom events for: product view, add to cart, checkout start, purchase
- [ ] **SEO**
  - Product page meta: title, description, Open Graph image (watermarked)
  - Image sitemap for product pages
  - Structured data: `Product` schema with price, availability, images
- [ ] **Testing**
  - Stripe test mode full flow
  - Printful test orders
  - Mobile responsiveness
  - Hawaii GET calculation verification

### 5.5 Phase 5: Post-Launch (Ongoing)

- [ ] **Curate additional products** — expand from 5 to 50-100 products
- [ ] **A/B test pricing** — experiment with print markups
- [ ] **Add video licensing** — extend to 4K drone footage licensing
- [ ] **Customer accounts** — optional accounts for download history (Stripe Customer Portal)
- [ ] **Tour upsells** — "Booked a tour? Get 20% off prints of your adventure!"

---

## 6. Data Models

### 6.1 products.json (Astro Data File)

Full catalog at `data/shop/products.json`. Key fields:

```json
{
  "id": "prod-moku-golden-hour",
  "name": "Mokulua Islands — Golden Hour Panorama",
  "slug": "mokulua-islands-golden-hour-panorama",
  "category": "mokulua-islands",
  "tags": ["drone", "mokulua-islands", "sunset"],
  "description": "...",
  "photographer": "Michael",
  "resolution": "5464×3640",
  "aspect_ratio": "3:2",
  "featured": true,
  "thumbnails": {
    "sm": "/shop/thumbs/...",
    "md": "/shop/thumbs/...",
    "lg": "/shop/thumbs/...",
    "watermark": "/shop/thumbs/..."
  },
  "pricing": {
    "prints": {
      "poster": { "12x18": 39, "18x24": 59, "24x36": 89 },
      "canvas": { "16x20": 149, ... },
      "framed": { "8x10": 89, ... }
    },
    "digital": {
      "personal": 29,
      "commercial": 149,
      "exclusive": 1499
    }
  }
}
```

### 6.2 Stripe Product Mapping

Each product variant is a Stripe Price. We store metadata on each Price:
- `product_id`: "prod-moku-golden-hour"
- `type`: "print" | "digital" | "license"
- `format`: "canvas" | "framed" | "poster" | null
- `size`: "24x36" | null
- `license_tier`: "personal" | "commercial" | "exclusive" | null

### 6.3 Printful Variant Mapping

`data/shop/printful-mapping.json`:

```json
{
  "canvas_16x20": { "printful_product_id": 1, "printful_variant_id": 4011 },
  "canvas_24x36": { "printful_product_id": 1, "printful_variant_id": 4013 },
  "framed_8x10_black": { "printful_product_id": 32, "printful_variant_id": 25601 },
  ...
}
```

### 6.4 Order State (Cloudflare KV)

Key: `order:{stripe_session_id}`
Value:
```json
{
  "session_id": "cs_xxx",
  "customer_email": "buyer@example.com",
  "product_ids": ["prod-moku-golden-hour"],
  "type": "print",
  "status": "pending_fulfillment",
  "printful_order_id": null,
  "tracking_url": null,
  "download_url": null,
  "created_at": "2026-06-01T12:00:00Z"
}
```

---

## 7. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Unauthorized download access** | R2 signed URLs with 24h expiry + max 3 downloads. Stripe webhook signature verification prevents forged requests. |
| **Card data exposure** | Stripe Checkout (hosted) — zero card data on our infrastructure. PCI-DSS handled entirely by Stripe. |
| **Image theft from previews** | Watermark on all preview images. Maximum preview size: 1600px wide (suitable for display, insufficient for quality prints). |
| **Webhook replay attacks** | Stripe signature verification + idempotency key checking via KV. |
| **Printful API key leakage** | Stored as Cloudflare Worker secret (encrypted at rest). Never exposed client-side. |
| **Exclusive rights conflicts** | Atomic check-and-set in KV. Once marked SOLD, further purchases blocked at product page level + webhook level. |

---

## 8. Cost Analysis

### Monthly Operating Costs (Launch)

| Service | Plan | Monthly Cost |
|---------|------|-------------|
| Cloudflare Pages | Free (500 builds/mo, unlimited bandwidth) | $0 |
| Cloudflare Workers | Free (100K req/day) | $0 |
| Cloudflare R2 | 100 GB × $0.015 | ~$2 |
| Cloudflare KV | 10K reads/day (free tier) | $0 |
| Stripe | Pay-as-you-go (2.9% + $0.30) | Variable |
| Resend | Free (3,000 emails/mo) | $0 |
| Printful | Pay-per-product (no monthly fee) | $0 |
| **Total Fixed** | | **~$2/month** |

### Per-Transaction Costs

| Product | Retail Price | Stripe Fee | Printful Base | Net Margin |
|---------|-------------|-----------|--------------|------------|
| 24×36 Canvas | $249.00 | $7.52 | ~$75 | **$166.48 (67%)** |
| 18×24 Poster | $59.00 | $2.01 | ~$15 | **$41.99 (71%)** |
| Personal Digital | $29.00 | $1.14 | $0 | **$27.86 (96%)** |
| Commercial License | $149.00 | $4.62 | $0 | **$144.38 (97%)** |
| Exclusive Rights | $1,499.00 | $43.77 | $0 | **$1,455.23 (97%)** |

### Break-Even

- Fixed costs: ~$24/year
- Break-even at: **1 print OR 1 digital download**
- Realistic Year 1: 50-200 sales (conservative) → $5,000-$50,000 revenue

---

## 9. Recommendations Summary

### Platform Choices

| Function | Recommendation | Why |
|----------|---------------|-----|
| **Payment** | Stripe | Lowest fees, best API, works with static sites. Stripe Checkout handles PCI compliance. |
| **Print fulfillment** | Printful | Best print quality for fine art. Mature API. Consistent output. Ships from California (fast to Hawaii). |
| **Digital delivery** | Cloudflare R2 + Worker | Zero egress fees, 24h signed URLs, 100K free Worker requests/day. No server needed. |
| **Email** | Resend | Free tier sufficient (3K/mo), modern API, React email templates. |
| **State** | Cloudflare KV | Order state, download counters, exclusive-sold flags. Free tier sufficient. |

### What We DON'T Need

- ❌ **Shopify/WooCommerce** — Overkill. Adds monthly cost ($39+). Static Astro + Stripe is sufficient.
- ❌ **Gumroad/Lemon Squeezy** — Higher per-transaction fees. Less flexibility. Good for creators with no dev capacity; we have dev capacity.
- ❌ **PhotoShelter/SmugMug** — Full DAM platforms with monthly fees ($10-50+). Overkill for a curated gallery.
- ❌ **Custom server** — Cloudflare Workers handle everything server-side. No Node.js server, no Docker, no database.

### Key Architecture Principles

1. **Static-first** — Astro generates all product pages at build time from `products.json`. No server-side rendering needed.
2. **Watermarked previews** — All gallery images are watermarked. Full-res files live in R2, only accessible via signed URLs.
3. **Stripe Checkout (hosted)** — Zero PCI scope. Stripe handles the hard parts.
4. **Webhook-driven fulfillment** — A single Cloudflare Worker handles all post-payment logic. No polling, no cron jobs.
5. **Source-of-truth is the repo** — `products.json` and `printful-mapping.json` live in git. Adding a product is a PR.
6. **Build-on-sale (exclusives)** — When an exclusive license is purchased, a Deploy Hook triggers Cloudflare Pages to rebuild the site, removing the sold product from listings.

---

## 10. Next Steps

1. **Set up Stripe account** and configure sample products in test mode
2. **Create R2 bucket** and upload 5 watermarked preview images
3. **Build Cloudflare Worker** for `checkout.session.completed` webhook
4. **Develop Astro gallery pages** using static `products.json` data
5. **Set up Printful account** and configure product templates
6. **End-to-end test** with Stripe test cards
7. **Launch** with 5 featured products → expand to 50+

---

*End of architecture document.*
