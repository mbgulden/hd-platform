# Your Hawaii Guide — Affiliate Aggregator Rebuild Architecture

**Ticket:** GRO-137
**Date:** 2026-05-29
**Author:** Hermes Agent (Architecture Design)
**Depends On:** GRO-133 (YHG Audit), GRO-136 (Content Migration)
**Status:** Architecture Complete — Ready for implementation

---

## Executive Summary

**Your Hawaii Guide is being rebuilt as an *affiliate aggregator*** — an honest, SEO-optimized Oahu tour comparison site that monetizes through affiliate commissions. It is NOT a tour operator (that's activeoahutours.com) — it's a trusted guide that helps visitors choose the right tour and then earns a commission when they book.

**The competitive advantage:** YHG will outrank competitors by being *genuinely more helpful* — honest pros/cons, real pricing transparency, no hidden bias, and richer information than any single operator or aggregator provides.

**Target launch:** 26 comparison and guide pages covering the 75 activities and 34 companies from the original site, rebuilt from scratch with fresh, authoritative content.

---

## 1. Site Identity & Positioning

### 1.1 Brand Positioning

| Element | Detail |
|---------|--------|
| **Site name** | Your Hawaii Guide |
| **Tagline** | "Honest Oahu Tour Comparisons & Local Guides" |
| **Tone** | Friendly, authoritative, transparent, local-expert voice |
| **Differentiator** | We compare ALL operators honestly — not just the ones that pay us |
| **Relationship to Active Oahu** | Independent editorial site. Active Oahu may appear in comparisons with transparent disclosure |
| **Target audience** | Oahu visitors (US mainland, international) researching tours & activities |

### 1.2 Why Affiliate Aggregator (Not Tour Operator)

| Model | Pros | Cons |
|-------|------|------|
| **Tour Operator** (activeoahutours.com) | Direct revenue, full control | Limited to own inventory, booking liability, insurance, staff |
| **Affiliate Aggregator** (YHG rebuild) | No inventory risk, low overhead, covers ALL operators, SEO scale | Lower per-booking revenue, dependent on affiliate programs |
| **Hybrid** | Best of both | Brand confusion, FTC issues without clear disclosure |

**Decision:** YHG = pure affiliate aggregator. Active Oahu Tours = pure operator. Clear separation. No YHG booking infrastructure needed — just links.

---

## 2. Content Strategy

### 2.1 Content Pillars

YHG content is organized into **5 content pillars**, each serving a distinct search intent:

#### Pillar 1: Tour Comparison Pages (💰 Revenue Pages)
These are the **money pages** — high-intent comparison content where users are ready to book.

**Format:**
- **Title pattern:** "Best [Activity] Tours on Oahu Compared [Year]"
- Honest pros/cons for each operator
- Pricing table with affiliate booking links
- "Who it's best for" recommendations
- Aggregate review scores
- FAQ section targeting "people also ask"

**Target Pages (15-20):**
- Best Oahu Kayak Tours Compared 2026
- Best Oahu Snorkel Tours Compared
- Best Oahu Surf Lessons for Beginners
- Best Oahu Sunset Cruises Compared
- Best Oahu Shark Diving Experiences
- Best Oahu SUP Tours & Rentals
- Best Oahu Catamaran Sails
- Best Oahu Hiking Tours (guided)
- Best Oahu Luau Experiences
- Best Oahu Scuba Diving Operators
- Best Oahu Dolphin Tours
- Best Oahu Island Tours (Circle Island)
- Best Oahu Parasailing & Jet Ski
- Best Oahu Helicopter Tours
- Best Oahu Photography Tours

#### Pillar 2: Activity Guides (🔄 Evergreen Research Pages)
These are **research pages** — people figuring out WHAT to do, not yet ready to book. They funnel to comparison pages.

**Format:**
- **Title pattern:** "How to Choose a [Activity] Tour on Oahu"
- "Complete Guide to [Activity] on Oahu"
- What to expect, difficulty levels, best locations
- Gear requirements, safety considerations
- Season/weather considerations
- Link to comparison page for booking

**Target Pages (10-15):**
- How to Choose a Snorkel Tour on Oahu
- Complete Guide to Kayaking on Oahu
- Beginner's Guide to Surfing on Oahu
- What to Know Before Shark Diving in Oahu
- Oahu SUP & Paddleboarding: A First-Timer's Guide
- How to Pick the Right Oahu Luau
- Scuba Diving on Oahu: What Certification You Need
- Oahu Boat Tours Explained (Catamaran vs Sail vs Power)

#### Pillar 3: Regional Guides (📍 Location-Based Pages)
These are **destination planning pages** — people deciding WHERE to base themselves or which area to explore.

**Format:**
- **Title pattern:** "[Region A] vs [Region B] vs [Region C] — Where to Stay on Oahu"
- "Best [Activity] in [Region]"
- Area overviews, pros/cons of each location
- Recommended tours/activities per region
- Links to regional comparison breakdowns

**Target Pages (5-8):**
- Kailua vs Waikiki vs North Shore — Where to Stay on Oahu
- North Shore Oahu: Complete Visitor Guide
- Windward Oahu Guide (Kailua, Kaneohe, Kualoa)
- Waikiki & Honolulu: Tours Without a Car
- Leeward Coast Guide (Ko Olina, Makaha)

#### Pillar 4: Seasonal & Timing Guides (📅 Trip Planning Pages)
These capture **trip-planning traffic** — people researching when to visit.

**Format:**
- **Title pattern:** "Best Time to Visit Oahu for [Activity]"
- Month-by-month conditions
- Crowd levels, pricing seasons
- Alternative activities for off-season

**Target Pages (5-8):**
- Best Time to Visit Oahu for Kayaking
- Best Time to Snorkel on Oahu (Turtle Season Guide)
- Oahu Weather by Month: A Quick Guide
- Whale Watching Season on Oahu (December–April)
- Winter vs Summer on Oahu: Activities Guide

#### Pillar 5: Safety, Gear & Practical Guides (🎒 Preparation Pages)
These capture **pre-trip research** and build topical authority.

**Format:**
- **Title pattern:** "What to Bring [Activity] on Oahu" / "Is [Activity] Safe on Oahu?"
- Packing lists, gear recommendations (affiliate opportunities: Amazon gear links)
- Safety considerations, skill requirements
- Links to comparison pages

**Target Pages (5-8):**
- What to Bring Kayaking on Oahu (Packing List)
- Is Snorkeling Safe on Oahu? Safety Tips
- What to Wear Surfing on Oahu
- Oahu Sun Protection Guide (Reef-Safe Sunscreen)
- Kayaking with Kids on Oahu: Family Guide

**Total planned pages: 40-59 across 5 pillars.**

### 2.2 Content Depth Standards

Every page must meet these minimums to be AI-search-visible and genuinely useful:

| Page Type | Min Word Count | Images | Schema Required | CTA |
|-----------|---------------|--------|----------------|-----|
| Comparison | 2,000+ | 5-8 (operator photos) | Review, FAQ, Breadcrumb | Affiliate booking button |
| Activity Guide | 1,500+ | 4-6 | Article, FAQ, Breadcrumb | "Compare Tours" → Comparison page |
| Regional Guide | 1,500+ | 6-10 | Article, FAQ, Breadcrumb | "Browse [Region] Tours" |
| Seasonal Guide | 1,200+ | 3-5 | Article, Breadcrumb | "Plan Your Trip" |
| Safety/Gear Guide | 1,000+ | 3-5 | Article, FAQ, Breadcrumb | "View Tours" or Amazon gear links |

---

## 3. Affiliate Model

### 3.1 Affiliate Programs

| Platform | Commission | Cookie Window | API Available | Integration Difficulty |
|----------|-----------|---------------|---------------|----------------------|
| **Viator** (TripAdvisor) | 8% (standard) | Session-based | ✅ Partner API | Medium — API key required |
| **GetYourGuide** | 8% | Session-based | ✅ Partner API | Medium — API key required |
| **FareHarbor** (direct links) | N/A (not affiliate) | N/A | N/A | N/A — static links |
| **Expedia/Travelocity** | 4-6% | 7 days | ✅ via Partner Central | Medium |
| **Klook** | 5-7% | Session | ✅ Affiliate API | Medium |
| **Amazon Associates** | 1-4% (gear) | 24 hours | ✅ Product API | Easy — for gear guides |

### 3.2 Primary Affiliate Strategy: Viator + GetYourGuide

**Why these two:**
- Viator is the largest tour aggregator — most Oahu operators list there
- GetYourGuide is #2 and growing fast, especially with international travelers
- Both offer reliable tracking, decent commissions (8%), and API access
- Covering both platforms ensures we can link to almost any Oahu tour

**How affiliate links work:**
1. User reads comparison page (e.g., "Best Oahu Kayak Tours")
2. Each operator listing has a "Check Price on Viator" or "Book on GetYourGuide" button
3. Click → user goes to Viator/GetYourGuide with affiliate tracking parameter
4. If user books anything within that session → we earn 8% commission
5. Average Oahu tour: $80-$150 → $6.40-$12.00 commission per booking

### 3.3 Direct FareHarbor Links (Non-Affiliate)

Some operators use FareHarbor for bookings (including Active Oahu). FareHarbor does not offer a public affiliate program, but we can:

1. Link directly to operator FareHarbor booking pages (no commission, but good for completeness)
2. Prioritize operators that ARE on Viator/GetYourGuide (affiliate linked)
3. Mark FareHarbor links as "Book Direct" (transparent — we may not earn commission)

### 3.4 FTC & Disclosure Compliance

**Every page with affiliate links must include:**

```html
<div class="affiliate-disclosure">
  <p><strong>Affiliate Disclosure:</strong> Your Hawaii Guide is reader-supported. 
  When you book through links on our site, we may earn an affiliate commission at 
  no extra cost to you. We only recommend operators we've researched and believe 
  offer quality experiences. <a href="/how-we-make-money/">Learn more</a>.</p>
</div>
```

Placement: above the fold on comparison pages, in footer on guide pages.

### 3.5 Revenue Projections (Conservative)

| Metric | Monthly (Year 1) | Monthly (Year 2) |
|--------|-----------------|-----------------|
| Organic traffic | 5,000 visits | 25,000 visits |
| Click-through to affiliate | 15% (750) | 18% (4,500) |
| Booking conversion (Viator) | 8% (60 bookings) | 8% (360 bookings) |
| Avg booking value | $100 | $100 |
| Commission rate | 8% | 8% |
| **Monthly revenue** | **$480** | **$2,880** |

**Year 1 goal: $5,760/year | Year 3 goal: $50,000+/year** (as content library grows and ranks)

---

## 4. Astro Architecture

### 4.1 Content Collections

YHG uses **Astro Content Collections** — markdown files with typed frontmatter schemas in `src/content/config.ts`.

```
src/content/
├── config.ts                  # Collection schemas
├── comparisons/               # Tour comparison pages
│   ├── best-oahu-kayak-tours.md
│   ├── best-oahu-snorkel-tours.md
│   ├── best-oahu-surf-lessons.md
│   └── ...
├── guides/                    # Activity & practical guides
│   ├── how-to-choose-snorkel-tour.md
│   ├── complete-guide-kayaking-oahu.md
│   ├── what-to-bring-kayaking.md
│   └── ...
├── regions/                   # Regional destination guides
│   ├── kailua-vs-waikiki-vs-north-shore.md
│   ├── north-shore-visitor-guide.md
│   └── ...
├── seasonal/                  # Seasonal & timing guides
│   ├── best-time-kayaking-oahu.md
│   ├── best-time-snorkeling-oahu.md
│   └── ...
└── pages/                     # Static informational pages
    ├── about.md
    ├── how-we-make-money.md
    ├── contact.md
    ├── cancellation-policy.md
    └── privacy-policy.md
```

### 4.2 Comparison Collection Schema

`src/content/config.ts` — Comparisons schema:

```typescript
const comparisonsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),                     // Meta description
    activityType: z.enum([
      'kayaking', 'snorkeling', 'surfing', 'sup', 'catamaran',
      'shark-diving', 'scuba', 'luau', 'helicopter', 'parasailing',
      'dolphin-tour', 'island-tour', 'photography', 'hiking'
    ]),
    region: z.enum(['oahu-all', 'north-shore', 'windward', 'waikiki', 'leeward']),
    lastUpdated: z.string(),                     // ISO date — signals freshness to Google
    heroImage: z.string(),                       // Path to hero image
    heroImageAlt: z.string(),

    // SEO
    seo: z.object({
      title: z.string(),                         // Title tag (may differ from page title)
      description: z.string(),
      keywords: z.array(z.string()),
    }),

    // Operators compared
    operators: z.array(z.object({
      name: z.string(),                          // e.g., "Active Oahu Tours"
      slug: z.string(),                          // URL-safe identifier
      description: z.string(),                   // 2-3 sentence overview
      rating: z.number().min(0).max(5),
      reviewCount: z.number(),
      reviewPlatform: z.enum(['tripadvisor', 'google', 'viator', 'getyourguide']),
      priceRange: z.string(),                    // e.g., "From $89/person"
      duration: z.string(),                      // e.g., "2-3 hours"
      location: z.string(),                      // e.g., "Kailua Beach"
      difficulty: z.enum(['beginner', 'intermediate', 'advanced', 'all-levels']),
      groupSize: z.string(),                     // e.g., "Max 12 people"
      pros: z.array(z.string()),
      cons: z.array(z.string()),
      bestFor: z.array(z.string()),              // e.g., ["Families", "Beginners"]
      features: z.array(z.string()),             // e.g., ["Guide included", "GoPro photos"]
      // Affiliate links
      viatorUrl: z.string().optional(),           // Viator affiliate link
      getYourGuideUrl: z.string().optional(),     // GetYourGuide affiliate link
      directUrl: z.string().optional(),           // Operator direct booking URL
      // Primary CTA
      primaryCTA: z.enum(['viator', 'getyourguide', 'direct']),
    })),

    // Comparison verdict
    verdict: z.object({
      bestOverall: z.string(),                   // Operator slug for best overall
      bestValue: z.string(),                     // Best budget pick
      bestForBeginners: z.string(),              // Most beginner-friendly
      bestForFamilies: z.string(),              // Most family-friendly
      bestForAdventure: z.string(),              // Most adventurous/thrilling
    }),

    // FAQ
    faqs: z.array(z.object({
      question: z.string(),
      answer: z.string(),
    })),

    // Quick comparison table data
    quickComparison: z.array(z.object({
      feature: z.string(),                       // e.g., "Duration", "Price", "Difficulty"
      values: z.record(z.string()),              // Map of operator slug → value
    })),

    featured: z.boolean().default(false),
  }),
});
```

### 4.3 Guides Collection Schema

```typescript
const guidesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum(['activity-guide', 'safety-gear', 'comparison']),
    activityType: z.string().optional(),          // e.g., "kayaking", "snorkeling"
    relatedComparison: z.string().optional(),     // Slug of related comparison page
    lastUpdated: z.string(),
    heroImage: z.string(),
    heroImageAlt: z.string(),
    readingTime: z.number(),                      // Minutes

    seo: z.object({
      title: z.string(),
      description: z.string(),
      keywords: z.array(z.string()),
    }),

    faqs: z.array(z.object({
      question: z.string(),
      answer: z.string(),
    })).default([]),

    featured: z.boolean().default(false),
  }),
});
```

### 4.4 Regions Collection Schema

```typescript
const regionsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    region: z.enum(['north-shore', 'windward', 'waikiki', 'leeward', 'oahu-all']),
    lastUpdated: z.string(),
    heroImage: z.string(),
    heroImageAlt: z.string(),

    // Activities available in region
    activities: z.array(z.string()),              // ["kayaking", "snorkeling", "surfing", ...]

    // Related comparisons
    relatedComparisons: z.array(z.string()),

    seo: z.object({
      title: z.string(),
      description: z.string(),
      keywords: z.array(z.string()),
    }),

    featured: z.boolean().default(false),
  }),
});
```

### 4.5 Pages Collection Schema

```typescript
const pagesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    template: z.enum(['default', 'wide', 'legal']).default('default'),
    lastModified: z.string(),

    seo: z.object({
      title: z.string(),
      description: z.string(),
    }),

    // For How We Make Money page
    affiliatePrograms: z.array(z.object({
      name: z.string(),
      commission: z.string(),
      disclosure: z.string(),
    })).default([]),
  }),
});
```

### 4.6 Route Structure (File-Based Routing)

```
src/pages/
├── index.astro                              # / — Homepage
├── 404.astro                                # Custom 404
│
│   # === COMPARISON PAGES (Money Pages) ===
├── comparisons/
│   ├── index.astro                          # /comparisons/ — All comparisons listing
│   └── [slug].astro                         # /comparisons/best-oahu-kayak-tours/
│
│   # === ACTIVITY GUIDES ===
├── guides/
│   ├── index.astro                          # /guides/ — All guides listing
│   └── [slug].astro                         # /guides/how-to-choose-snorkel-tour/
│
│   # === REGIONAL GUIDES ===
├── regions/
│   ├── index.astro                          # /regions/ — All regions
│   └── [slug].astro                         # /regions/north-shore-visitor-guide/
│
│   # === SEASONAL GUIDES ===
├── seasonal/
│   ├── index.astro                          # /seasonal/
│   └── [slug].astro                         # /seasonal/best-time-kayaking-oahu/
│
│   # === STATIC PAGES ===
├── about.astro                              # /about/
├── how-we-make-money.astro                  # /how-we-make-money/ (affiliate disclosure hub)
├── contact.astro                            # /contact/
│
│   # === POLICIES (Migrated from WP) ===
├── policies/
│   ├── cancellation.astro                   # /policies/cancellation/
│   ├── privacy.astro                        # /policies/privacy/
│   └── refunds.astro                        # /policies/refunds/
│
│   # === BLOG (Rebuilt from 26 old posts) ===
├── blog/
│   ├── index.astro                          # /blog/ — Adventure Log
│   └── [slug].astro                         # /blog/lanikai-pillboxes-hike/
│
│   # === TAXONOMY PAGES ===
├── activities/
│   └── [type].astro                         # /activities/kayaking/ — Filtered activity listing
│
│   # === REDIRECT-ONLY ROUTES (301s for old URLs) ===
│   # /activity-listing/ → 301 /comparisons/
│   # /activity-map/ → 301 /regions/
│   # /company-map/ → 301 /regions/
```

### 4.7 Template System

| Template | Pages Using It | Key Components |
|----------|---------------|----------------|
| `ComparisonLayout.astro` | All comparison pages | Pricing table, pros/cons cards, affiliate CTA buttons, FAQ accordion, map embed |
| `GuideLayout.astro` | Activity/seasonal/safety guides | Table of contents sidebar, related comparisons widget, CTA banner |
| `RegionLayout.astro` | Regional destination guides | Map hero, activity grid, weather widget, tour recommendations |
| `BaseLayout.astro` | All pages (base) | Header, footer, affiliate disclosure strip, GA4, schema wrapper |
| `BlogPostLayout.astro` | Blog posts | Article schema, author bio, related posts |

### 4.8 Shared Components

```
src/components/
├── AffiliateDisclosure.astro        # FTC-compliant disclosure banner
├── AffiliateButton.astro            # Styled CTA button (Viator/GetYourGuide/Direct)
├── PricingTable.astro               # Responsive comparison pricing table
├── ProsConsCard.astro               # Operator pros/cons display
├── RatingStars.astro                # Star rating visualization
├── VerdictBadge.astro               # "Best Overall" / "Best Value" badges
├── FAQAccordion.astro               # FAQ section with expandable answers
├── ComparisonCard.astro             # Operator listing card (for index pages)
├── GuideCard.astro                  # Guide listing card (for index pages)
├── RegionCard.astro                 # Region listing card
├── EmailCapture.astro               # Email signup for PDF guide
├── Breadcrumbs.astro                # Breadcrumb navigation component
├── TableOfContents.astro            # Auto-generated TOC from headings
├── RelatedComparisons.astro         # "You might also like" widget
└── schema/
    ├── ComparisonSchema.astro       # Review + FAQPage JSON-LD
    ├── ArticleSchema.astro          # Article JSON-LD
    ├── FAQSchema.astro              # FAQPage JSON-LD
    ├── BreadcrumbSchema.astro       # BreadcrumbList JSON-LD
    └── OrganizationSchema.astro     # Organization JSON-LD (site-wide)
```

### 4.9 Dynamic Route Implementation

`src/pages/comparisons/[slug].astro`:

```astro
---
import { getCollection } from 'astro:content';
import ComparisonLayout from '../../layouts/ComparisonLayout.astro';
import PricingTable from '../../components/PricingTable.astro';
import ProsConsCard from '../../components/ProsConsCard.astro';
import FAQAccordion from '../../components/FAQAccordion.astro';
import ComparisonSchema from '../../components/schema/ComparisonSchema.astro';
import BreadcrumbSchema from '../../components/schema/BreadcrumbSchema.astro';

export async function getStaticPaths() {
  const comparisons = await getCollection('comparisons');
  return comparisons.map((c) => ({
    params: { slug: c.id },
    props: { comparison: c },
  }));
}

const { comparison } = Astro.props;
const {
  title, description, operators, verdict, faqs, seo,
  activityType, lastUpdated, heroImage, heroImageAlt,
} = comparison.data;

const breadcrumbs = [
  { name: 'Home', url: '/' },
  { name: 'Tour Comparisons', url: '/comparisons/' },
  { name: title, url: null },
];
---

<ComparisonLayout
  title={seo.title}
  description={seo.description}
  image={heroImage}
  imageAlt={heroImageAlt}
  lastUpdated={lastUpdated}
>
  <!-- Affiliate Disclosure (above fold) -->
  <AffiliateDisclosure />

  <!-- Main Content from Markdown -->
  <article class="comparison-content">
    <h1>{title}</h1>
    <p class="comparison-intro">{description}</p>

    <!-- Quick Comparison Table -->
    <PricingTable operators={operators} comparison={comparison.data.quickComparison} />

    <!-- Individual Operator Breakdowns -->
    {
      operators.map((op) => (
        <section id={op.slug}>
          <h2>{op.name}</h2>
          <RatingStars rating={op.rating} count={op.reviewCount} platform={op.reviewPlatform} />

          <p>{op.description}</p>

          <ProsConsCard pros={op.pros} cons={op.cons} />

          <dl class="operator-details">
            <dt>Duration:</dt><dd>{op.duration}</dd>
            <dt>Price:</dt><dd>{op.priceRange}</dd>
            <dt>Location:</dt><dd>{op.location}</dd>
            <dt>Difficulty:</dt><dd>{op.difficulty}</dd>
            <dt>Best for:</dt><dd>{op.bestFor.join(', ')}</dd>
          </dl>

          <AffiliateButton
            url={op.primaryCTA === 'viator' ? op.viatorUrl : op.getYourGuideUrl || op.directUrl}
            platform={op.primaryCTA === 'viator' ? 'Viator' : op.primaryCTA === 'getyourguide' ? 'GetYourGuide' : 'Book Direct'}
          />
        </section>
      ))
    }

    <!-- Verdict Section -->
    <section id="verdict">
      <h2>Our Verdict</h2>
      <VerdictBadge label="Best Overall" operator={verdict.bestOverall} />
      <VerdictBadge label="Best Value" operator={verdict.bestValue} />
      <VerdictBadge label="Best for Beginners" operator={verdict.bestForBeginners} />
      <VerdictBadge label="Best for Families" operator={verdict.bestForFamilies} />
      <VerdictBadge label="Best for Adventure" operator={verdict.bestForAdventure} />
    </section>

    <!-- FAQ Section -->
    <FAQAccordion faqs={faqs} />

    <!-- Email Capture -->
    <EmailCapture
      title="Want the Full Oahu Tour Guide?"
      description="Get our free PDF with all top-rated tours, packing tips, and local secrets."
    />
  </article>

  <!-- Schema.org JSON-LD -->
  <ComparisonSchema comparison={comparison} />
  <BreadcrumbSchema items={breadcrumbs} />
</ComparisonLayout>
```

---

## 5. SEO Strategy

### 5.1 Keyword Strategy

#### Primary Keywords (Comparison Pages — HIGH commercial intent)

| Keyword | Target Page | Est. Monthly Volume | Competition |
|---------|-------------|---------------------|-------------|
| "best Oahu kayak tours" | /comparisons/best-oahu-kayak-tours/ | 1,300 | Medium |
| "Oahu snorkel comparison" | /comparisons/best-oahu-snorkel-tours/ | 480 | Low |
| "best snorkeling Oahu" | /comparisons/best-oahu-snorkel-tours/ | 2,400 | High |
| "Oahu surf lessons best" | /comparisons/best-oahu-surf-lessons/ | 720 | Medium |
| "best Oahu luau" | /comparisons/best-oahu-luau/ | 3,600 | High |
| "Oahu shark diving best" | /comparisons/best-oahu-shark-diving/ | 320 | Low |
| "Oahu sunset cruise best" | /comparisons/best-oahu-sunset-cruises/ | 590 | Medium |
| "best dolphin tour Oahu" | /comparisons/best-oahu-dolphin-tours/ | 880 | Medium |
| "Oahu helicopter tours best" | /comparisons/best-oahu-helicopter-tours/ | 1,100 | High |
| "best scuba diving Oahu" | /comparisons/best-oahu-scuba-diving/ | 440 | Medium |

#### Secondary Keywords (Guide Pages — research/informational intent)

| Keyword | Target Page | Est. Monthly Volume |
|---------|-------------|---------------------|
| "how to choose snorkel tour Oahu" | /guides/how-to-choose-snorkel-tour/ | 140 |
| "kayaking Oahu guide" | /guides/complete-guide-kayaking-oahu/ | 890 |
| "what to bring kayaking Oahu" | /guides/what-to-bring-kayaking/ | 210 |
| "Oahu kayaking for beginners" | /guides/complete-guide-kayaking-oahu/ | 390 |
| "best time kayak Oahu" | /seasonal/best-time-kayaking-oahu/ | 170 |
| "Oahu snorkeling safety" | /guides/is-snorkeling-safe-oahu/ | 90 |

#### Regional Keywords

| Keyword | Target Page | Est. Monthly Volume |
|---------|-------------|---------------------|
| "where to stay Oahu" | /regions/kailua-vs-waikiki-vs-north-shore/ | 4,400 |
| "North Shore Oahu guide" | /regions/north-shore-visitor-guide/ | 2,900 |
| "Kailua vs Waikiki" | /regions/kailua-vs-waikiki-vs-north-shore/ | 1,600 |
| "things to do North Shore Oahu" | /regions/north-shore-visitor-guide/ | 3,200 |

### 5.2 Schema.org Strategy (Critical for AI Search Visibility)

Every page type gets specific structured data to maximize AI search engine ingestion:

| Page Type | Schema Types | Priority |
|-----------|-------------|----------|
| **Comparison pages** | `Review` (aggregate comparison), `FAQPage`, `BreadcrumbList`, `WebPage` | 🔴 MUST |
| **Guide pages** | `Article`, `FAQPage`, `BreadcrumbList` | 🔴 MUST |
| **Region pages** | `Article`, `TouristDestination`, `FAQPage`, `BreadcrumbList` | 🟡 HIGH |
| **Seasonal pages** | `Article`, `FAQPage`, `BreadcrumbList` | 🟡 HIGH |
| **Static pages** | `AboutPage` (about), `ContactPage` (contact), `BreadcrumbList` | 🟢 STANDARD |
| **Site-wide** | `Organization`, `WebSite` with `SearchAction` | 🔴 MUST |
| **Blog posts** | `Article`, `BreadcrumbList` | 🟡 HIGH |

#### Comparison Page Schema Example (JSON-LD)

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "@id": "https://yourhawaiiguide.com/comparisons/best-oahu-kayak-tours/#webpage",
  "name": "Best Oahu Kayak Tours Compared 2026 — Honest Review",
  "description": "Compare the top 5 Oahu kayak tour operators side by side — pricing, difficulty, what's included, and honest pros/cons from local experts.",
  "about": {
    "@type": "TouristTrip",
    "name": "Oahu Kayak Tours",
    "touristType": ["Adventure Seekers", "Nature Lovers", "Families"]
  },
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "item": {
          "@type": "TouristAttraction",
          "name": "Active Oahu Tours",
          "description": "Self-guided kayak to Chinaman's Hat with equipment delivery",
          "offers": {
            "@type": "Offer",
            "price": "89.00",
            "priceCurrency": "USD"
          },
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "247"
          }
        }
      }
    ]
  },
  "subjectOf": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the best kayak tour on Oahu for beginners?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "For beginners, we recommend Active Oahu's Kailua Bay self-guided tour — calm, protected waters, stable sit-on-top kayaks, and a safety briefing included."
        }
      }
    ]
  }
}
```

### 5.3 Internal Linking Architecture

```
Homepage
├── → /comparisons/ (hub)
│   ├── → /comparisons/best-oahu-kayak-tours/
│   │   ├── → /guides/complete-guide-kayaking-oahu/
│   │   ├── → /guides/what-to-bring-kayaking/
│   │   ├── → /seasonal/best-time-kayaking-oahu/
│   │   └── → /regions/north-shore-visitor-guide/
│   ├── → /comparisons/best-oahu-snorkel-tours/
│   │   ├── → /guides/how-to-choose-snorkel-tour/
│   │   ├── → /guides/is-snorkeling-safe-oahu/
│   │   └── → /seasonal/best-time-snorkeling-oahu/
│   └── → ... (other comparisons)
├── → /guides/ (hub)
│   └── → individual guides → related comparison pages
├── → /regions/ (hub)
│   └── → regional guides → activity guides + comparisons
└── → /blog/ (supporting content → comparisons)
```

**Linking rules:**
1. Every comparison page links to at least 2 related guides
2. Every guide page links to its parent comparison page
3. Every region page links to 3-5 comparison pages
4. Blog posts link to relevant comparison pages (conversion funnel)
5. "Related comparisons" widget on every guide page

### 5.4 URL Slug Strategy

All new content uses descriptive, keyword-rich, short slugs:

| ✅ Good | ❌ Avoid |
|--------|---------|
| `/comparisons/best-oahu-kayak-tours/` | `/comparisons/2026-oahu-kayak-tour-compare-guide/` |
| `/guides/what-to-bring-kayaking/` | `/guides/kayaking-gear-checklist-and-packing-list-oahu/` |
| `/regions/north-shore-visitor-guide/` | `/regions/north-shore-oahu-hawaii-visitor-guide-2026/` |

**Rules:**
- Max 4-5 words in slug
- Include primary keyword
- No stop words unless grammatically required
- No year in slug (use `lastUpdated` frontmatter for freshness instead)

### 5.5 301 Redirects from Old WordPress URLs

Old YHG URLs with SEO value → new Astro URLs:

```text
# _redirects file (Cloudflare Pages)

# Blog posts (preserve old slug if possible, or redirect to closest match)
/blog/adventures/kayaking/      /comparisons/best-oahu-kayak-tours/     301
/blog/adventures/snorkeling/    /comparisons/best-oahu-snorkel-tours/   301
/blog/adventures/surfing/       /comparisons/best-oahu-surf-lessons/    301

# Activity listing → Comparisons hub
/activity-listing/              /comparisons/                           301
/things-to-do-oahu/             /comparisons/                           301

# Maps → Regions
/activity-map/                  /regions/                               301
/all-activities-map/            /regions/                               301
/company-map/                   /regions/                               301
/free-things-to-do-map/         /regions/                               301

# Old CPT activity pages (75) → individual comparison operator sections
# Use 301 to the main comparison page for that activity type
/activities/surfing-lessons/    /comparisons/best-oahu-surf-lessons/    301
/activities/turtle-canyons-snorkel-excursion/ /comparisons/best-oahu-snorkel-tours/ 301

# WordPress cleanup
/wp-admin/*                     /                                       410
/wp-content/*                   /                                       410
```

---

## 6. Conversion Funnel

### 6.1 User Journey

```
                    ┌─────────────────────────────────────┐
                    │                                     │
  Google Search ──→ │  "best Oahu kayak tours"            │
                    │                                     │
                    └───────────────┬─────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │  Comparison Page                    │
                    │  • Pricing table with 5 operators   │
                    │  • Pros/cons for each               │
                    │  • "Best for" recommendations       │
                    │  • FAQ section                      │
                    └───────────────┬─────────────────────┘
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                          ▼                   ▼
              ┌──────────────────┐  ┌──────────────────┐
              │ "Check Price on  │  │ Email Capture:    │
              │  Viator" (click) │  │ "Get Our Free     │
              │                  │  │  Oahu Tours PDF"  │
              └────────┬─────────┘  └────────┬─────────┘
                       │                     │
                       ▼                     ▼
              ┌──────────────────┐  ┌──────────────────┐
              │ Viator booking   │  │ Email sequence:   │
              │ page             │  │ • Welcome + PDF   │
              │                  │  │ • Top 5 Oahu recs │
              │ User books →     │  │ • Seasonal picks  │
              │ 💰 8% commission │  │ • "Book now" CTA  │
              └──────────────────┘  └──────────────────┘
```

### 6.2 Affiliate CTA Design

Each operator section on a comparison page has:

1. **Primary CTA button:** "Check Price on Viator" or "Book on GetYourGuide" (affiliate link)
2. **Secondary link:** "Book Direct" (operator website — no commission, but builds trust)
3. **Callout text:** "We may earn a commission if you book — at no extra cost to you"

### 6.3 Email Capture Strategy

**Lead magnet:** "Top 10 Oahu Tours — Free PDF Guide" (curated from our comparison pages)

**Placement:**
- Mid-page on comparison pages (after the first 3 operators)
- Bottom of guide pages
- Exit-intent popup (lightweight, no overlay)

**Email sequence (5 emails, 2-week drip):**
1. Welcome + PDF download + "How we pick the best tours"
2. Top 5 Kayak & Snorkel Tours (affiliate links)
3. Hidden Gems: Tours Most Visitors Miss (affiliate links)
4. Oahu Packing Guide + Gear Recommendations (Amazon affiliate)
5. "Still Planning? Here's Our Quick Picks" (urgency + affiliate links)

---

## 7. Visual & Brand System

### 7.1 Design Direction

| Element | Direction |
|---------|-----------|
| **Vibe** | Clean, tropical, trustworthy — not salesy |
| **Colors** | Ocean blue (#1B6B93), Coral (#FF6B6B), Sand (#F5E6D3), Deep Navy (#0D1B2A) |
| **Typography** | Headers: Playfair Display (elegant, travel vibe). Body: Inter (clean, readable) |
| **Imagery** | Real Oahu photos from Active Oahu media library + operator-provided images |
| **Trust Signals** | "Last updated [date]", author bios, review counts, FTC disclosure, privacy/cancellation links |

### 7.2 Homepage Layout

```
┌──────────────────────────────────────────────┐
│  HERO: Aerial Oahu shot                      │
│  "Your Honest Guide to Oahu Tours"           │
│  [Search tours]  [Browse by activity]        │
├──────────────────────────────────────────────┤
│  POPULAR COMPARISONS (grid of 6 cards)       │
│  Kayak | Snorkel | Surf | Luau | Shark | ... │
├──────────────────────────────────────────────┤
│  "How We Pick Tours" (trust section)         │
│  • Real research, not just commissions       │
│  • We compare pros AND cons                  │
│  • Updated regularly                         │
├──────────────────────────────────────────────┤
│  TOP REGIONS (grid of 4 region cards)        │
│  North Shore | Windward | Waikiki | Leeward  │
├──────────────────────────────────────────────┤
│  LATEST GUIDES (3-4 recent articles)         │
├──────────────────────────────────────────────┤
│  EMAIL CAPTURE (Free PDF guide)              │
├──────────────────────────────────────────────┤
│  FOOTER: About | How We Make Money |         │
│  Contact | Privacy | Cancellation            │
└──────────────────────────────────────────────┘
```

---

## 8. Tech Stack & Infrastructure

### 8.1 Build & Deploy

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Framework** | Astro 5 | Static site generation |
| **Content** | Markdown + Content Collections | Type-safe frontmatter |
| **Styling** | Tailwind CSS v4 | Same as Active Oahu Astro build |
| **Hosting** | Cloudflare Pages | Free tier, global CDN, `_redirects` support |
| **Analytics** | GA4 (new property for YHG) | Separate from Active Oahu GA4 |
| **Email** | ConvertKit or MailerLite | Email capture + sequences |
| **Search** | Pagefind | Client-side search for static sites |
| **Images** | Astro Image optimization | WebP, responsive srcsets |
| **Maps** | Leaflet (no Google Maps API cost) | Interactive Oahu tour map |
| **DNS** | yourhawaiiguide.com → Cloudflare | Already on Cloudflare via Google Domains DNS |

### 8.2 CI/CD Pipeline

```
GitHub (main branch)
  │
  ├── Push → GitHub Actions
  │   ├── npm ci
  │   ├── astro check (type-check frontmatter)
  │   ├── astro build
  │   └── Deploy to Cloudflare Pages
  │
  └── Cloudflare Pages
      ├── Auto-build on push
      ├── Preview deployments per branch
      └── Production: yourhawaiiguide.com
```

### 8.3 Analytics & Tracking

| Tool | Purpose | Setup |
|------|---------|-------|
| **GA4** | Traffic, conversions, user behavior | Global site tag |
| **Google Search Console** | Keyword rankings, indexing | Add YHG as new property |
| **Viator Partner Dashboard** | Affiliate clicks + commissions | Viator API tracking |
| **GetYourGuide Partner Dashboard** | Affiliate clicks + commissions | GYG tracking |
| **ConvertKit** | Email subscribers, sequence analytics | Embedded forms |

---

## 9. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Astro project scaffold (`npm create astro@latest`)
- [ ] Tailwind CSS v4 integration
- [ ] Content collection schemas (`config.ts`)
- [ ] Base layout + navigation
- [ ] Homepage design
- [ ] Static pages: About, How We Make Money, Contact, Policies
- [ ] GA4 + Search Console setup

### Phase 2: First Comparisons (Weeks 2-3)
- [ ] Build `ComparisonLayout.astro` + all components
- [ ] Write 5 comparison pages:
  1. Best Oahu Kayak Tours
  2. Best Oahu Snorkel Tours
  3. Best Oahu Surf Lessons
  4. Best Oahu Shark Diving
  5. Best Oahu Sunset Cruises
- [ ] Affiliate link integration (Viator + GetYourGuide)
- [ ] Schema.org implementation (Review + FAQ)

### Phase 3: Guides & Regions (Weeks 3-4)
- [ ] Build `GuideLayout.astro` + `RegionLayout.astro`
- [ ] Write 5 activity guides (kayaking, snorkeling, surfing, shark diving, SUP)
- [ ] Write 3 regional guides (North Shore, Kailua/Windward, Waikiki)
- [ ] Internal linking between comparisons → guides → regions
- [ ] Email capture integration

### Phase 4: Launch & Expand (Weeks 4-6)
- [ ] Cloudflare Pages deployment
- [ ] DNS cutover (yourhawaiiguide.com → new Cloudflare Pages)
- [ ] 301 redirects from old WordPress URLs
- [ ] XML sitemap submission to Google/Bing
- [ ] Remaining comparisons (10+ more)
- [ ] Blog rebuild (26 posts from old site titles)
- [ ] Seasonal & safety guides

### Phase 5: Growth (Months 2-6)
- [ ] New comparison pages monthly
- [ ] Monitor rankings, iterate on underperforming pages
- [ ] Build backlinks via outreach
- [ ] A/B test affiliate CTA placement
- [ ] Optimize email sequence conversion

---

## 10. Success Metrics

### 10.1 KPIs

| Metric | Month 1 Target | Month 6 Target | Month 12 Target |
|--------|---------------|----------------|-----------------|
| Organic traffic | 500 visits | 3,000 visits | 10,000 visits |
| Pages indexed | 20 | 45 | 55+ |
| Affiliate clicks | 50 | 400 | 2,000 |
| Affiliate bookings | 3 | 30 | 160 |
| Affiliate revenue | $24 | $240 | $1,280/mo |
| Email subscribers | 20 | 250 | 800 |
| Avg time on page | 3:00+ | 3:30+ | 4:00+ |

### 10.2 SEO Milestones

| Milestone | Expected Timeframe |
|-----------|-------------------|
| First page in Google index | Week 1 |
| Ranking top 100 for "best Oahu kayak tours" | Month 1 |
| Ranking top 30 for "best Oahu kayak tours" | Month 3 |
| Ranking top 10 for "best Oahu kayak tours" | Month 6 |
| Ranking #1-3 for long-tail comparison queries | Month 4-6 |
| AI Overview citations | Month 6+ |

---

## Appendix A: Content Templates

### A.1 Comparison Page Template (Markdown Frontmatter)

```markdown
---
title: "Best Oahu Kayak Tours Compared 2026"
description: "Compare the top 5 Oahu kayak tour operators — honest pros & cons, pricing, difficulty, and booking links."
activityType: "kayaking"
region: "oahu-all"
lastUpdated: "2026-05-29"
heroImage: "/images/comparisons/oahu-kayak-hero.webp"
heroImageAlt: "Kayakers paddling toward Chinaman's Hat off Oahu's windward coast at golden hour"

seo:
  title: "Best Oahu Kayak Tours 2026 — Honest Comparison & Reviews"
  description: "We compared 5 Oahu kayak tour operators. See honest pros/cons, pricing from $59-149, and which tour is best for beginners, families, and experienced paddlers."
  keywords:
    - best Oahu kayak tours
    - Oahu kayak comparison
    - kayak tours Oahu reviews
    - Oahu kayaking guide
    - Chinaman's Hat kayak

operators:
  - name: "Active Oahu Tours"
    slug: "active-oahu-tours"
    description: "Self-guided kayak adventures with equipment delivered to your launch point. Known for Chinaman's Hat and Kailua Bay tours with quality gear and flexible scheduling."
    rating: 4.9
    reviewCount: 247
    reviewPlatform: "tripadvisor"
    priceRange: "$89/person (self-guided)"
    duration: "4-5 hours"
    location: "Kailua Beach & Kualoa Regional Park"
    difficulty: "all-levels"
    groupSize: "No limit (self-guided)"
    pros:
      - "Best value — includes gear, briefing, and delivery"
      - "Freedom to explore at your own pace"
      - "Multiple launch locations (Kailua, Kualoa, Kaneohe)"
      - "TripAdvisor Travelers' Choice award winner"
    cons:
      - "No guide in the water with you"
      - "Must transport gear from meeting point to beach"
      - "No GoPro/photos included"
    bestFor:
      - "Independent adventurers"
      - "Budget-conscious travelers"
      - "Couples"
    features:
      - "Sit-on-top kayaks"
      - "Dry bags included"
      - "Safety briefing"
      - "Equipment delivery"
    viatorUrl: "https://www.viator.com/...?affiliate=..."
    getYourGuideUrl: ""
    directUrl: "https://activeoahutours.com/activities/chinamans-hat-self-guided-oahu-kayak-tour/"
    primaryCTA: "viator"

  - name: "Kailua Beach Adventures"
    slug: "kailua-beach-adventures"
    # ... (4 more operators)

verdict:
  bestOverall: "active-oahu-tours"
  bestValue: "kailua-beach-adventures"
  bestForBeginners: "kailua-beach-adventures"
  bestForFamilies: "twogood-kayaks"
  bestForAdventure: "kayak-kauai-oahu"

faqs:
  - question: "Do I need kayaking experience for Oahu kayak tours?"
    answer: "Most Oahu kayak tours welcome beginners. Sit-on-top kayaks are stable and easy to paddle. Self-guided tours include a safety briefing. Guided tours provide on-water instruction. The calm, protected waters of Kailua Bay and Kaneohe Bay are ideal for first-timers."
  - question: "What is the best time of year for kayaking on Oahu?"
    answer: "Oahu offers year-round kayaking, but May–October typically has calmer conditions on the windward (east) side where most kayak tours operate. Winter months (November–March) can bring larger swells. Morning tours (8-11am) generally have the calmest water and best visibility."
  - question: "How much do Oahu kayak tours cost?"
    answer: "Self-guided kayak rentals range from $59–89/person for a half-day. Guided tours range from $109–149/person. Multi-island tours (Mokulua Islands) are typically $129–169/person. Most operators offer discounts for groups of 4+."

quickComparison:
  - feature: "Price"
    values:
      active-oahu-tours: "$89/person"
      kailua-beach-adventures: "$79/person"
      twogood-kayaks: "$99/person"
      hawaii-beach-time: "$69/person"
      kayak-kauai-oahu: "$149/person"
  - feature: "Duration"
    values:
      active-oahu-tours: "4-5 hours"
      kailua-beach-adventures: "5 hours"
      twogood-kayaks: "5 hours"
      hawaii-beach-time: "3 hours"
      kayak-kauai-oahu: "5-6 hours"
  - feature: "Difficulty"
    values:
      active-oahu-tours: "All levels"
      kailua-beach-adventures: "Beginner+"
      twogood-kayaks: "Beginner+"
      hawaii-beach-time: "All levels"
      kayak-kauai-oahu: "Intermediate+"
  - feature: "Guide Included"
    values:
      active-oahu-tours: "Self-guided"
      kailua-beach-adventures: "Yes"
      twogood-kayaks: "Yes"
      hawaii-beach-time: "Self-guided"
      kayak-kauai-oahu: "Yes"
  - feature: "Location"
    values:
      active-oahu-tours: "Kailua/Kualoa"
      kailua-beach-adventures: "Kailua Beach"
      twogood-kayaks: "Kailua Beach"
      hawaii-beach-time: "Waikiki"
      kayak-kauai-oahu: "North Shore"

featured: true
---
```

---

## Appendix B: Sample Comparison Page

See separate file: `src/content/comparisons/best-oahu-kayak-tours.md`

---

## Appendix C: How We Make Money Page Outline

```
# How Your Hawaii Guide Makes Money

## We're Reader-Supported
Your Hawaii Guide is free for everyone. We don't charge for access, 
and we don't accept payment for favorable reviews.

## How We Earn Commission
When you click a "Check Price" or "Book Now" button and complete a 
booking on Viator or GetYourGuide, we may earn a small commission 
(typically 8% of the booking value) at NO extra cost to you.

## Why This Works
- Operators pay the same commission regardless (it's Viator's fee)
- We can recommend ANY operator, not just the ones that pay us directly
- Our recommendations are based on research, not kickbacks

## Affiliate Programs We Use
- Viator (TripAdvisor) — 8% commission
- GetYourGuide — 8% commission
- Amazon Associates — 1-4% (for gear recommendations)

## Direct Booking Links
Some operators we link to directly (no commission). We do this when 
an operator isn't on Viator/GetYourGuide but offers a great experience. 
We'll always note when a link is non-affiliate.

## Our Editorial Standards
1. We research every operator before including them
2. We list honest pros AND cons
3. We don't accept free tours or payment from operators for placement
4. We update pricing and reviews regularly
5. Operators cannot pay to be ranked higher

Questions? Contact us at hello@yourhawaiiguide.com
```

---

## Appendix D: Competitor Analysis (Affiliate Aggregator Space)

| Competitor | Model | Strengths | Weaknesses | YHG Opportunity |
|-----------|-------|-----------|------------|----------------|
| **Viator** (tripadvisor.com) | Marketplace | Massive inventory, brand trust | Overwhelming, no curation, reviews gamed | Curated picks, honest local perspective |
| **GetYourGuide** | Marketplace | Clean UX, good for EU travelers | Less Oahu coverage vs Viator | Fill Oahu coverage gaps |
| **HawaiiActivities.com** | Local aggregator | Oahu-focused, good SEO | Booking engine, not content-first | Better guides, more transparent comparisons |
| **Travel blogs** (The Blonde Abroad, etc.) | Affiliate lists | High DA, good photos | Shallow comparisons, obviously sponsored | Deeper research, local expertise |
| **Oahu-specific blogs** | Content sites | Authentic | Small scale, infrequent updates | Scale + systematic coverage |

**YHG's moat:** Be the site that genuinely researches and compares more Oahu operators than anyone — with honest pros/cons, actual pricing, and clear "who this is best for" recommendations. No other Oahu site does this systematically.

---

*Architecture designed for GRO-137. Next step: GRO-138 — Implementation: Astro Scaffold & Baseline.*
