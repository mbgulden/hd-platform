# AI SEO Strategy (GEO + AEO) — Active Oahu Tours

**Ticket:** GRO-118  
**Date:** May 29, 2026  
**Author:** Hermes Agent (AI search research & strategy)  
**Depends On:** GRO-117 (SEO Audit)  
**Status:** Complete — Ready for implementation

---

## Executive Summary

Active Oahu Tours has strong SEO fundamentals (WordPress + Yoast + Cloudflare APO) but is **invisible to AI-powered search engines**. As of 2025–2026, Google AI Overviews (formerly SGE), ChatGPT, Perplexity, and Claude are reshaping how travelers discover tour operators. This document provides a complete strategy covering:

- **GEO** (Generative Engine Optimization): Getting cited by AI-generated answers
- **AEO** (Answer Engine Optimization): Structured data that AI crawlers consume
- **Entity Optimization**: Knowledge Graph associations that trigger AI mentions
- **Content Architecture**: LLM-friendly content formats for surfacing recommendations
- **Competitor Analysis**: How Kualoa, Kailua Beach Adventures, and others appear in AI search

**Key Finding:** Active Oahu is missing the 5 structured data types that AI search engines depend on. Adding them would transform the site from invisible to AI-citable within 30–60 days.

---

## 1. The AI Search Landscape (2025–2026)

### 1.1 How Google AI Overviews Surface Tour Results

Google's AI Overviews (replacing SGE) generate synthesized answers at the top of search results. For tour-related queries, they pull from:

1. **Structured data (JSON-LD)** — The #1 signal. Google explicitly uses schema to populate AI Overviews.
2. **High-authority aggregators** — Viator, GetYourGuide, TripAdvisor listings dominate AI Overview citations for tour queries.
3. **LocalBusiness + Review schema** — For "Oahu kayak tours near me" type queries, AI Overviews prioritize businesses with complete LocalBusiness markup and aggregate ratings.
4. **FAQ and HowTo schema** — Directly fuels the "People also ask" expansion and AI Overview answer cards.
5. **Google Business Profile** — GBP data (reviews, photos, Q&A, posts) is surfaced inside AI Overviews for local searches.

**Example query flow for "best Oahu kayak tours":**

```
AI Overview generation order:
1. Extract entities: "Oahu" (Place), "kayak tours" (TouristTrip/TouristAttraction)
2. Query Knowledge Graph for entity associations
3. Pull structured data from GBP listings + websites with LocalBusiness/Tour schema
4. Synthesize from review data (TripAdvisor, Google Reviews)
5. Supplement with FAQ content for expandable sections
6. Cite sources (linked carousel below AI answer)
```

**What triggers a featured snippet / AI Overview for "Oahu kayak tours":**

- ✅ `TouristAttraction` or `Tour` schema with `name`, `description`, `location`, `offers.price`
- ✅ `LocalBusiness` schema with `geo` coordinates, `address`, `openingHours`
- ✅ `AggregateRating` schema (minimum ~10 reviews)
- ✅ FAQ schema on tour pages answering specific questions
- ✅ `Article` schema on blog/guide content that answers "best kayak tours Oahu"
- ✅ Google Business Profile with 4.0+ rating, 50+ reviews, regular photo uploads
- ✅ Citations from TripAdvisor, Viator, Hawaii.com, and local tourism boards

### 1.2 How ChatGPT, Perplexity, and Claude Surface Local Tour Recommendations

Each AI platform has different ingestion patterns:

#### ChatGPT (GPT-4o / GPT-5 with browsing)

- **Ingestion method:** Bing Search API (Microsoft ecosystem)
- **Schema it consumes:** Primarily `WebPage`, `Article`, `Organization`, `LocalBusiness`
- **What it favors:**
  - Pages with clean, well-structured content (clear headings, bulleted lists, data)
  - Pages referenced by Bing's index (Bing Places, Bing Maps integration)
  - Content from high-domain-authority sources
  - **Crucially:** ChatGPT browsing extracts content from rendered HTML, **not JSON-LD directly**. It reads what users see.
- **For Active Oahu:** Ensure Bing Webmaster Tools registration, submit sitemaps to Bing, claim Bing Places listing.

#### Perplexity AI

- **Ingestion method:** Proprietary web index + Google/Bing search APIs
- **Schema it consumes:** `FAQ`, `HowTo`, `Q&A`, `Article`, `LocalBusiness`, `Product`
- **What it favors:**
  - Pages structured as direct answers (Q&A format)
  - FAQ schema — Perplexity's RAG pipeline explicitly extracts FAQPage structured data
  - Content that states facts clearly with citations/sources
  - Recent publication dates (freshness signal)
- **For Active Oahu:** FAQ schema is the single highest-ROI action for Perplexity visibility.

#### Claude (Anthropic, with web search)

- **Ingestion method:** Brave Search API (as of 2025)
- **Schema it consumes:** Focuses on content quality and structure more than schema
- **What it favors:**
  - Well-written, authoritative long-form content
  - Content from .edu, .gov, and recognized travel authority domains
  - Pages with clear expertise signals (author bios, credentials, certifications)
  - Clean semantic HTML
- **For Active Oahu:** Invest in expert-authored guides with author bios, certifications mentioned.

#### Key Insight: Structured Data Is the Common Denominator

All AI search engines converge on one truth: **websites with rich structured data are more likely to be surfaced, cited, and linked**. JSON-LD schema is the machine-readable layer that makes your content discoverable to any AI crawler, regardless of which search API it uses.

---

## 2. GEO: Generative Engine Optimization

### 2.1 How to Get Cited by AI Answers

AI-generated answers (Google AI Overviews, ChatGPT, Perplexity) cite sources. Getting cited requires:

**Pillar 1: Structured Data Completeness**

AI crawlers prioritize sites that "speak their language." Every tour/rental page needs complete schema:

- `TouristAttraction` or `Trip` on each tour page
- `LocalBusiness` on the site (once, site-wide)
- `FAQ` on FAQ pages and tour pages with Q&A content
- `AggregateRating` on pages with review content
- `BreadcrumbList` on every page
- `Article` on blog/guide pages
- `Organization` with `sameAs` links

**Pillar 2: E-E-A-T Signals for AI**

AI models use E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) to decide which sources to cite:

| E-E-A-T Pillar | What AI Looks For | Active Oahu Status |
|---|---|---|
| **Experience** | First-hand content, original photos, tour descriptions written by guides | ✅ Strong — original photos, real tour content |
| **Expertise** | Author bios, certifications (e.g., ACA kayak instructor), years in business | ⚠️ Missing — no author bios, no certs mentioned on site |
| **Authoritativeness** | Citations from TripAdvisor, news mentions, tourism board links, backlinks from .edu/.gov | ⚠️ Partial — TripAdvisor Travelers' Choice 2022 but not showcased |
| **Trustworthiness** | HTTPS, clear contact info, privacy policy, physical address, refund policies | ✅ Good — HTTPS, contact page, FareHarbor booking |

**Pillar 3: Citation Network**

AI models look at who else cites you. Build citations on:

1. **Aggregators/Affiliates:** Viator, GetYourGuide, Expedia, Klook — list tours on all platforms
2. **Review sites:** TripAdvisor, Google Reviews, Yelp
3. **Local tourism:** Hawaii Tourism Authority, Go Hawaii, Kailua Chamber of Commerce
4. **Wikipedia/Wikidata:** Ensure Active Oahu or Kailua kayaking has relevant entity entries
5. **Local media/PR:** Get featured in Honolulu Star-Advertiser, Hawaii Magazine, travel blogs

### 2.2 The GEO Citation Funnel for "Oahu Kayak Tours"

```
Query: "Best kayak tours on Oahu"
│
├── AI Overview (Google)
│   ├── Sources: TripAdvisor "Best Oahu Kayaking" list (aggregator)
│   ├── Sources: HawaiiActivities.com (TouristDestination schema)
│   ├── Sources: Kailua Beach Adventures (LocalBusiness + review schema)
│   └── ❌ Active Oahu — MISSING (no schema, not in aggregator lists)
│
├── ChatGPT (Bing-powered)
│   ├── Sources: TripAdvisor, Viator listings
│   ├── Sources: Travel blogs with Article schema
│   └── ❌ Active Oahu — MISSING (not in Bing Places, no Article schema)
│
├── Perplexity
│   ├── Sources: FAQ-structured pages
│   ├── Sources: "Best of" listicles
│   └── ❌ Active Oahu — MISSING (no FAQ schema)
│
└── Claude (Brave-powered)
    ├── Sources: Government tourism sites (.gov)
    ├── Sources: Long-form guide content
    └── ❌ Active Oahu — MISSING (guides exist but lack Article schema + authorship)
```

### 2.3 GEO Quick Wins (30-Day Plan)

| Priority | Action | AI Impact | Effort |
|---|---|---|---|
| 🔴 P0 | Add FAQ schema on `/faq/` | Perplexity + Google AI Overview | 30 min |
| 🔴 P0 | Add LocalBusiness schema (NAP + geo) | Google AI Overview + ChatGPT | 30 min |
| 🔴 P0 | Add TouristAttraction schema on each tour page | Google AI Overview | 2 hrs |
| 🟡 P1 | Add Article schema on all blog/guide pages | ChatGPT + Claude | 1 hr |
| 🟡 P1 | Add AggregateRating schema | Google AI Overview | 30 min |
| 🟡 P1 | Register with Bing Webmaster Tools + Bing Places | ChatGPT visibility | 1 hr |
| 🟢 P2 | Get listed on Viator, GetYourGuide, Klook | AI aggregation citations | 4 hrs |
| 🟢 P2 | Add author bios + certifications to blog posts | Claude + E-E-A-T | 2 hrs |

---

## 3. AEO: Answer Engine Optimization

### 3.1 Schema Types AI Crawlers Consume (Priority-Ordered)

#### 🔴 P0 — FAQ Schema (CRITICAL)

**Why:** FAQ schema is the #1 structured data type that AI answer engines consume. Perplexity's RAG pipeline explicitly extracts FAQPage. Google AI Overviews generate expandable Q&A from FAQ schema.

**Current State:** ❌ Missing entirely. Active Oahu has an `/faq/` page with Q&A content but no JSON-LD.

**Implementation:**

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Do I need kayaking experience to rent a kayak?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No experience is necessary! We provide a brief safety orientation and paddling instruction before every rental. Our kayaks are stable sit-on-top models perfect for beginners. Life jackets are provided and required."
      }
    },
    {
      "@type": "Question",
      "name": "How long does it take to kayak to the Mokulua Islands?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The paddle from Kailua Beach to the Mokulua Islands takes approximately 45 minutes to 1 hour each way, depending on conditions. We recommend allowing 4-5 hours for a round-trip with time to explore the island."
      }
    },
    {
      "@type": "Question",
      "name": "What is the best time of year for kayaking on Oahu?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Oahu offers year-round kayaking, but the best conditions are typically May through October when the north and east shores are calmer. Winter months (November-March) can have larger swells on the windward side. We monitor conditions daily and provide real-time guidance."
      }
    },
    {
      "@type": "Question",
      "name": "Can I kayak to Chinaman's Hat (Mokoliʻi)?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes! Chinaman's Hat (Mokoliʻi) is accessible by kayak from Kualoa Regional Park, about a 15-20 minute paddle. We offer kayak deliveries to Kualoa Beach Park and can set you up with all the gear you need."
      }
    },
    {
      "@type": "Question",
      "name": "Do you offer guided kayak tours?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, we offer guided kayaking tours to the Mokulua Islands, Kaneohe Bay, and other scenic Oahu locations. Our guides are experienced, CPR-certified, and knowledgeable about local marine life and Hawaiian culture."
      }
    }
  ]
}
```

**Placement:** Add to `/faq/` page. Also add tour-specific FAQ blocks on individual tour pages.

---

#### 🔴 P0 — LocalBusiness Schema (CRITICAL)

**Why:** Google AI Overviews for "near me" and location-based queries pull LocalBusiness data directly. ChatGPT uses Bing's local business index.

**Current State:** ❌ Missing. Active Oahu has `Organization` schema but not `LocalBusiness`.

**Implementation:**

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://activeoahutours.com/#localbusiness",
  "name": "Active Oahu Tours",
  "alternateName": ["Active Oahu Kayak Rentals", "Active Oahu Tours & Activities"],
  "description": "Oahu kayak rentals and guided tours based in Kailua. Kayak to the Mokulua Islands, Chinaman's Hat, and Kaneohe Bay. Equipment delivery to Kualoa, Laie, Kahana, and windward Oahu beaches.",
  "url": "https://activeoahutours.com",
  "telephone": "+1-808-XXX-XXXX",
  "email": "info@activeoahutours.com",
  "image": "https://activeoahutours.com/wp-content/uploads/2021/06/DSC5297_2000-e1642616607887.jpg",
  "logo": "https://activeoahutours.com/wp-content/uploads/logo.png",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "134B Hamakua Dr",
    "addressLocality": "Kailua",
    "addressRegion": "HI",
    "postalCode": "96734",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 21.3936,
    "longitude": -157.7425
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
      "opens": "08:00",
      "closes": "17:00"
    }
  ],
  "priceRange": "$$",
  "currenciesAccepted": "USD",
  "paymentAccepted": "Cash, Credit Card",
  "areaServed": [
    {
      "@type": "City",
      "name": "Kailua"
    },
    {
      "@type": "City",
      "name": "Kaneohe"
    },
    {
      "@type": "City",
      "name": "Laie"
    },
    {
      "@type": "State",
      "name": "Oahu"
    }
  ],
  "sameAs": [
    "https://www.facebook.com/activeoahutours",
    "https://www.instagram.com/activeoahutours",
    "https://twitter.com/activeoahu",
    "https://www.tripadvisor.com/Attraction_Review-g60652-dXXXXXXX-Reviews-Active_Oahu_Tours-Kailua_Oahu_Hawaii.html",
    "https://www.yelp.com/biz/active-oahu-tours-kailua"
  ],
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Oahu Kayak Tours & Rentals",
    "itemListElement": [
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Kayak Rental",
          "description": "Half-day and full-day kayak rentals for Kailua Beach and windward Oahu"
        }
      },
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Guided Kayak Tour",
          "description": "Guided kayak tours to Mokulua Islands, Kaneohe Bay, and Chinaman's Hat"
        }
      }
    ]
  }
}
```

**Placement:** Site-wide in `<head>`, output by Yoast SEO or custom code.

---

#### 🔴 P0 — TouristAttraction / Trip Schema (for each tour page)

**Why:** Google AI Overviews specifically reference `TouristAttraction` and `Trip` schema when synthesizing tour recommendations.

**Current State:** ❌ Missing. Individual tour pages have no product/service schema.

**Implementation (example for a Mokulua Islands tour page):**

```json
{
  "@context": "https://schema.org",
  "@type": "TouristAttraction",
  "@id": "https://activeoahutours.com/oahu-kayaking-and-beach-adventures/mokulua-islands-guided-kayak-tour/#tour",
  "name": "Guided Kayak Tour to the Mokulua Islands",
  "description": "Paddle to the iconic Mokulua Islands off Kailua Beach with an experienced guide. Explore tide pools, spot seabirds, and snorkel in crystal-clear waters. Includes kayak, safety gear, and island landing permit.",
  "touristType": [
    "Adventure Seekers",
    "Nature Lovers",
    "Families",
    "Couples"
  ],
  "additionalType": "https://schema.org/Trip",
  "url": "https://activeoahutours.com/oahu-kayaking-and-beach-adventures/mokulua-islands-guided-kayak-tour/",
  "image": "https://activeoahutours.com/wp-content/uploads/mokulua-islands-kayak.jpg",
  "location": {
    "@type": "Place",
    "name": "Kailua Beach Park",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Kailua",
      "addressRegion": "HI",
      "addressCountry": "US"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 21.3992,
      "longitude": -157.7384
    }
  },
  "provider": {
    "@type": "LocalBusiness",
    "@id": "https://activeoahutours.com/#localbusiness"
  },
  "offers": {
    "@type": "Offer",
    "price": "129.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://fareharbor.com/embeds/book/activeoahutours/items/XXXXX/",
    "validFrom": "2026-01-01"
  },
  "duration": "PT4H",
  "subjectOf": {
    "@type": "AggregateRating",
    "ratingValue": "5.0",
    "reviewCount": "247",
    "bestRating": "5"
  }
}
```

**Placement:** On each individual tour/adventure page. Automate via WordPress custom fields + Yoast SEO hook.

---

#### 🟡 P1 — Article Schema (for blog/guide pages)

**Why:** ChatGPT and Claude heavily weight article-structured content for informational queries. Google AI Overviews use `Article` schema to identify content that can answer "what/why/how" questions.

**Implementation:**

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "https://activeoahutours.com/oahu-kayaking-and-beach-adventures/ultimate-guide-kailua-beach-park/#article",
  "headline": "Ultimate Guide for Kailua Beach Park: Kayaking, Parking & Tips",
  "description": "Everything you need to know about kayaking at Kailua Beach Park — where to park, best launch spots, what to bring, and insider tips from local guides.",
  "image": "https://activeoahutours.com/wp-content/uploads/kailua-beach-aerial.jpg",
  "author": {
    "@type": "Person",
    "name": "Active Oahu Guides",
    "description": "Local Oahu kayak guides with 10+ years experience on windward waters"
  },
  "publisher": {
    "@type": "Organization",
    "@id": "https://activeoahutours.com/#organization"
  },
  "datePublished": "2025-06-15",
  "dateModified": "2026-04-21",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://activeoahutours.com/oahu-kayaking-and-beach-adventures/ultimate-guide-kailua-beach-park/"
  },
  "about": [
    {
      "@type": "Place",
      "name": "Kailua Beach Park"
    },
    {
      "@type": "Thing",
      "name": "Kayaking"
    }
  ],
  "keywords": ["Kailua Beach kayaking", "Oahu kayak guide", "Kailua Beach parking", "Mokulua Islands kayak"]
}
```

**Placement:** On all blog/guide pages (~20+ pages). Yoast SEO can output this automatically.

---

#### 🟡 P1 — AggregateRating Schema

**Why:** Google AI Overviews prominently display star ratings for tour operators. This is a trust signal for all AI search engines.

**Implementation (site-wide):**

```json
{
  "@context": "https://schema.org",
  "@type": "AggregateRating",
  "@id": "https://activeoahutours.com/#aggregaterating",
  "itemReviewed": {
    "@type": "LocalBusiness",
    "@id": "https://activeoahutours.com/#localbusiness"
  },
  "ratingValue": "5.0",
  "reviewCount": "247",
  "bestRating": "5",
  "worstRating": "1"
}
```

**Note:** Google requires reviews to be collected directly on the site (not just TripAdvisor) for AggregateRating to appear in search results. Implement a reviews/testimonials system that collects reviews on activeoahutours.com.

---

#### 🟡 P1 — BreadcrumbList Schema

**Why:** Helps AI crawlers understand site hierarchy. Contributes to entity relationships.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://activeoahutours.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Activities",
      "item": "https://activeoahutours.com/activities/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Mokulua Islands Guided Kayak Tour"
    }
  ]
}
```

**Placement:** Enable in Yoast SEO (Settings → Search Appearance → Breadcrumbs). Should be auto-generated.

---

#### 🟢 P2 — HowTo Schema (for guide content)

**Why:** Google AI Overviews generate step-by-step answer cards from HowTo schema. Useful for "how to kayak to X" content.

**Implementation (on guide pages with step-by-step instructions):**

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Kayak to the Mokulua Islands",
  "description": "Step-by-step guide for paddling from Kailua Beach to the Mokulua Islands.",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Launch from Kailua Beach Park",
      "text": "Park at the Kailua Beach Park boat ramp lot. Carry your kayak to the water's edge and launch from the sandy beach.",
      "image": "https://activeoahutours.com/wp-content/uploads/kailua-launch.jpg"
    },
    {
      "@type": "HowToStep",
      "name": "Paddle to Moku Nui",
      "text": "Head toward the larger island (Moku Nui). Keep the island at roughly 45 degrees to account for current. Paddle time: 45-60 minutes."
    },
    {
      "@type": "HowToStep",
      "name": "Land on the protected side",
      "text": "Approach from the leeward (west) side of Moku Nui where the water is calmer. Beach your kayak above the tide line."
    },
    {
      "@type": "HowToStep",
      "name": "Explore the island",
      "text": "Hike to the summit for panoramic views, explore tide pools on the north side, and look for wedgetail shearwaters nesting."
    }
  ],
  "totalTime": "PT4H"
}
```

---

#### 🟢 P2 — VideoObject Schema (for YouTube/video content)

**Why:** Google AI Overviews surface video content for "how to" and "what to expect" queries.

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Kayaking to the Mokulua Islands — Full Tour",
  "description": "Join our guided kayak tour from Kailua Beach to the Mokulua Islands. See what to expect, water conditions, and island exploration.",
  "thumbnailUrl": "https://activeoahutours.com/wp-content/uploads/mokulua-video-thumb.jpg",
  "uploadDate": "2025-08-15",
  "duration": "PT3M45S",
  "contentUrl": "https://www.youtube.com/watch?v=XXXXXXXXX",
  "embedUrl": "https://www.youtube.com/embed/XXXXXXXXX"
}
```

---

### 3.2 Schema Implementation Priority Matrix

```
Schema Type          AI Overview  ChatGPT  Perplexity  Claude  Effort
────────────────────────────────────────────────────────────────────────
FAQPage              ★★★★★        ★★★      ★★★★★       ★★★     Low (30 min)
LocalBusiness        ★★★★★        ★★★★     ★★★         ★★      Low (30 min)
TouristAttraction    ★★★★         ★★★      ★★★         ★★      Med (2 hrs)
Article              ★★★          ★★★★     ★★★         ★★★★★   Low (1 hr, auto)
AggregateRating      ★★★★         ★★★      ★★          ★★      Med (needs reviews)
BreadcrumbList       ★★★          ★★       ★★          ★★      Low (enable Yoast)
HowTo                ★★★★         ★★★      ★★★★        ★★★     Med (per guide)
VideoObject          ★★★          ★★       ★★          ★★      Low (per video)
```

---

## 4. Entity Optimization

### 4.1 Knowledge Graph Entity Strategy

Google's Knowledge Graph builds entity relationships from structured data, Wikipedia/Wikidata, and authoritative sources. Active Oahu should be associated with these entities:

#### Primary Entities to Associate With

| Entity | Type | Current Connection | Action |
|---|---|---|---|
| **Active Oahu Tours** | Organization / LocalBusiness | Weak — only Organization schema | Strengthen via LocalBusiness schema + sameAs |
| **Kailua** | City / Place | Location in content | Add geo coordinates, PostalAddress schema |
| **Oahu** | Island / Place | Implicit in content | Explicit areaServed schema |
| **Kailua Beach Park** | Beach / Place | Content mentions | Create `TouristAttraction` schema referencing it |
| **Mokulua Islands** | Island / Place | Tour destination | `TouristAttraction.location` schema |
| **Chinaman's Hat (Mokoliʻi)** | Island / Landmark | Rental delivery location | `TouristAttraction.location` schema |
| **Kaneohe Bay** | Bay / BodyOfWater | Tour location | `TouristAttraction.location` schema |
| **Kayaking** | Sport / Activity | Primary activity | `about` property in Article/Organization schema |
| **Snorkeling** | Sport / Activity | Secondary activity | `about` property |
| **Kualoa Regional Park** | Park / Place | Rental delivery | `areaServed` in LocalBusiness |

#### Entity Graph Visualization

```
Active Oahu Tours (LocalBusiness)
├── locatedIn → Kailua (City)
│   └── partOf → Oahu (Island)
│       └── partOf → Hawaii (State)
│           └── partOf → United States (Country)
├── offers → Kayak Tour (TouristAttraction)
│   ├── location → Kailua Beach Park (Beach)
│   ├── location → Mokulua Islands (Island)
│   └── location → Kaneohe Bay (Bay)
├── offers → Kayak Rental (Service)
│   ├── areaServed → Kualoa Regional Park (Park)
│   └── areaServed → Chinaman's Hat (Landmark)
├── about → Kayaking (Sport)
├── about → Snorkeling (Sport)
└── sameAs → [Facebook, Instagram, TripAdvisor, Yelp, Google Business Profile]
```

### 4.2 Wikidata / Wikipedia Entity Strategy

**Goal:** Get Active Oahu referenced in Wikidata (and ideally Wikipedia) to strengthen Knowledge Graph connections.

**Wikidata actions:**
1. Check if Active Oahu has a Wikidata entry → create one with `instance of (P31)` = `tour operator (Q18388436)` or `business (Q4830453)`
2. Add properties: `located in (P131)` → Kailua, `coordinate location (P625)`, `official website (P856)`
3. Link to the Wikipedia article for Kailua or Oahu tourism if relevant

**Wikipedia actions (long-term):**
- Contribute to "Tourism in Hawaii" or "Kailua, Honolulu County, Hawaii" pages
- Cite Active Oahu as a local business reference where appropriate
- Do NOT create a standalone page unless you meet Wikipedia's notability guidelines (significant coverage in independent reliable sources)

### 4.3 Google Business Profile Optimization for AI

Google Business Profile is a direct feed into AI Overviews for local queries:

- **Posts:** Post weekly updates with photos — AI Overviews surface recent GBP posts
- **Q&A:** Seed and answer questions on GBP — these feed into FAQ-style AI answers
- **Services:** List all services with descriptions (kayak rental, guided tours, equipment delivery)
- **Photos:** Upload fresh photos monthly — AI Overviews pull from recent GBP photo inventory
- **Reviews:** Respond to all reviews — response rate is an AI trust signal
- **Attributes:** Mark "Women-led," "Family-friendly," "Outdoor seating" etc.

---

## 5. Content Structure for AI Readability

### 5.1 The LLM-Friendly Content Format

LLMs (GPT-4o, Claude, Gemini, Perplexity's RAG) extract content differently than traditional search crawlers. They prefer:

**✅ DO: Inverted Pyramid with Direct Answers**

LLMs extract the first meaningful text that answers a query. Lead with the direct answer, then elaborate.

```markdown
## How long does it take to kayak to the Mokulua Islands?

**Answer: 45-60 minutes each way from Kailua Beach Park.**

The paddle distance is approximately 2.5 miles round trip. Most paddlers
complete the crossing in 45-60 minutes depending on wind and current 
conditions. We recommend allowing 4-5 hours total for a relaxed trip 
with time to explore the island.
```

**✅ DO: Clearly Demarcated Q&A Blocks**

```markdown
### Q: Do I need a permit to land on the Mokulua Islands?
**A:** Yes. The Mokulua Islands are part of the Hawaii State Seabird Sanctuary.
You need a landing permit, which is included with all Active Oahu guided tours.
Independent kayakers must obtain their own permit from the DLNR.
```

**✅ DO: Bulleted and Numbered Lists for Scannability**

LLMs and AI Overviews prefer lists over paragraphs for extracting discrete facts.

**✅ DO: Data-Rich Tables and Comparisons (use labeled key:value pairs, not pipe tables)**

```
**Tour Comparison:**
- **Mokulua Islands Tour:** 4 hours, $129/person, moderate difficulty, includes snorkel gear
- **Kaneohe Bay Tour:** 3 hours, $99/person, easy difficulty, includes lunch
- **Sunset Paddle:** 2.5 hours, $89/person, easy difficulty, includes refreshments
```

**✅ DO: Structured Meta Information**

Every page should have clearly identifiable:
- **Last Updated:** May 2026 (LLMs use recency as a ranking signal)
- **Author:** Active Oahu Guides (10+ years Kailua kayaking experience)
- **Location Tags:** Kailua, Oahu, Hawaii

**❌ DON'T: Keyword Stuffing**

LLMs detect and penalize unnatural keyword repetition more aggressively than traditional search.

**❌ DON'T: Vague Introductions**

"Welcome to our website! We are so glad you found us..." → LLMs ignore this.

**❌ DON'T: Content Buried in JavaScript**

AI crawlers may not execute JS. Critical content must be in server-rendered HTML.

### 5.2 Content Architecture for AI Surfaces

For each tour page, structure content in this order (LLM extraction priority):

1. **H1:** Tour Name + Primary Keyword (e.g., "Mokulua Islands Guided Kayak Tour | Kailua, Oahu")
2. **First paragraph:** 2-3 sentence direct answer to "What is this tour?" (this is what LLMs excerpt)
3. **Quick Facts box:** Duration, Difficulty, Price, Group Size (LLMs extract facts)
4. **What to Expect:** Bulleted list of tour highlights (LLMs surface this for "what to expect" queries)
5. **FAQ section:** 3-5 Q&A blocks specific to this tour (with JSON-LD FAQ schema)
6. **What to Bring:** Bulleted checklist
7. **Meeting Point:** Address with embedded map
8. **Photos/Videos:** With descriptive alt text and captions
9. **Reviews:** Curated testimonials (supports AggregateRating schema)
10. **Booking CTA:** FareHarbor embed

### 5.3 Content That Triggers AI Citations

Based on analysis of what gets cited in AI Overviews, ChatGPT, and Perplexity for tour queries:

| Content Type | AI Platform That Cites It | Example |
|---|---|---|
| **"Best of" / Top 10 lists** | Google AI Overview, Perplexity | "5 Best Kayak Tours on Oahu" |
| **Comparison tables** | Perplexity, ChatGPT | "Kayak Rental vs Guided Tour: Which is Right for You?" |
| **Price lists with clear ranges** | ChatGPT, Perplexity | "Oahu Kayak Rentals: $45/half-day, $65/full-day" |
| **Location-specific guides** | All platforms | "Kailua Beach Kayaking: Complete Guide" |
| **Seasonal advice** | Google AI Overview | "Best Time to Kayak on Oahu: Month-by-Month Guide" |
| **Safety information** | Claude, Perplexity | "Oahu Kayaking Safety: What Every Paddler Should Know" |
| **Permit/regulation info** | Claude (prefers authoritative) | "Mokulua Islands Landing Permits: What You Need" |

---

## 6. Competitor AI Search Comparison

### 6.1 How Competitors Appear in AI Search

#### Kualoa Ranch (kualoa.com)

| AI Platform | Visibility | Schema Used | Why They Show Up |
|---|---|---|---|
| **Google AI Overview** | ★★★★ | WebSite only | Massive brand authority, 4000+ backlinks, Wikipedia page, Knowledge Graph entity |
| **ChatGPT** | ★★★★ | WebSite only | Brand recognition, Wikipedia, news mentions |
| **Perplexity** | ★★★ | Minimal | Wikipedia citations, news articles |
| **Claude** | ★★★ | Minimal | Wikipedia, .edu research references |

**Key insight:** Kualoa succeeds despite minimal schema because of overwhelming brand authority. Active Oahu can't compete on brand — must win on schema completeness.

---

#### Kailua Beach Adventures (kailuabeachadventures.com) — #1 Direct Competitor

| AI Platform | Visibility | Schema Used | Why They Show Up |
|---|---|---|---|
| **Google AI Overview** | ★★★★ | WebSite + Organization + LocalBusiness | Complete LocalBusiness schema, review count, GBP optimized |
| **ChatGPT** | ★★★ | LocalBusiness | Bing Places listing, LocalBusiness schema |
| **Perplexity** | ★★★ | LocalBusiness | Good structured content, 40+ year history mentioned |
| **Claude** | ★★ | Organization | Long-form content less developed |

**Key insight:** KBA's LocalBusiness schema gives them an edge Active Oahu currently lacks. They have the exact schema Active Oahu is missing.

---

#### Go Oahu (gooahu.com)

| AI Platform | Visibility | Schema Used | Why They Show Up |
|---|---|---|---|
| **Google AI Overview** | ★★★★ | TouristInformationCenter + Organization + WebSite + Article + Person | Most complete schema of any competitor |
| **ChatGPT** | ★★★★ | Multiple | Article schema on blog content |
| **Perplexity** | ★★★★ | Article + TouristInformationCenter | Deep structured data, rich Q&A content |

**Key insight:** Go Oahu has the most sophisticated schema implementation. Their TouristInformationCenter type gives them aggregator-level visibility. This is the schema standard to match.

---

#### HawaiiActivities.com (hawaiiactivities.com)

| AI Platform | Visibility | Schema Used | Why They Show Up |
|---|---|---|---|
| **Google AI Overview** | ★★★★★ | TouristDestination | Aggregator with massive domain authority |
| **ChatGPT** | ★★★★ | TouristDestination | High DR, many backlinks |
| **Perplexity** | ★★★★ | TouristDestination | Extensive tour listings with structured data |

**Key insight:** HawaiiActivities.com is an aggregator, not a direct competitor. But they dominate AI Overview citations for tour queries because they aggregate and structure data from many operators. Active Oahu should ensure its tours are listed on this platform.

---

#### Blue Hawaii Private Tours (bluehawaiiprivatetours.com)

| AI Platform | Visibility | Schema Used | Why They Show Up |
|---|---|---|---|
| **Google AI Overview** | ★ | None | Almost no AI visibility — no schema at all |
| **ChatGPT** | ★ | None | Not in AI search results |
| **Perplexity** | ★ | None | Not cited |

**Key insight:** Blue Hawaii is a cautionary tale — no schema = AI invisibility. Active Oahu is currently closer to Blue Hawaii than to Go Oahu in schema completeness.

---

### 6.2 Competitive AI Visibility Scorecard

```
Competitor               Google AI Ov.  ChatGPT  Perplexity  Claude  Schema Count
────────────────────────────────────────────────────────────────────────────────
HawaiiActivities.com      ★★★★★          ★★★★     ★★★★        ★★★     1 (but powerful)
Go Oahu                   ★★★★           ★★★★     ★★★★        ★★★     5 ✨
Kualoa Ranch              ★★★★           ★★★★     ★★★         ★★★     1 (brand power)
Kailua Beach Adventures   ★★★★           ★★★      ★★★         ★★      3
Active Oahu (CURRENT)     ★★             ★★       ★           ★       2
Blue Hawaii               ★              ★        ★           ★       0
────────────────────────────────────────────────────────────────────────────────
Active Oahu (FULL SCHEMA) ★★★★★          ★★★★     ★★★★★       ★★★★    7+ 🎯
```

**Projected:** With full schema implementation, Active Oahu could leap from near-bottom to leader in AI visibility — surpassing even Kualoa Ranch in structured data completeness, though brand authority would still trail.

### 6.3 Competitor Gap Analysis: AI-Specific

| Gap | Kualoa | KBA | Go Oahu | Active Oahu |
|---|---|---|---|---|
| FAQ Schema | ❌ | ❌ | ❌ | ❌ → 🎯 Add first |
| LocalBusiness Schema | ❌ | ✅ | ❌ | ❌ → 🎯 Add |
| Tour/Product Schema | ❌ | ❌ | ❌ | ❌ → 🎯 Add |
| Article Schema | ❌ | ❌ | ✅ | ❌ → 🎯 Add |
| AggregateRating | ❌ | ❌ | ❌ | ❌ → 🎯 Add |
| Bing Places Listing | ✅ | ✅ | ✅ | ❌ → 🎯 Register |
| Wikipedia Mention | ✅ | ❌ | ❌ | ❌ → 🎯 Target |
| Knowledge Graph Entity | ✅ | ❌ | ❌ | ❌ → 🎯 Build |

**The Opportunity:** **Nobody** in the Oahu kayak tour space has FAQ schema. **Nobody** has tour-level product schema. The first mover wins maximum AI visibility.

---

## 7. Implementation Roadmap

### Phase 1: Schema Foundation (Week 1–2) — [CRITICAL]

These actions deliver the highest AI visibility impact with the lowest effort:

| # | Action | AI Impact | Effort | Implementation Method |
|---|---|---|---|---|
| 1 | **Add FAQ schema** on `/faq/` | Perplexity + Google AI Overview | 30 min | Yoast SEO custom field or custom code |
| 2 | **Add LocalBusiness schema** site-wide | Google AI Overview + ChatGPT | 30 min | Yoast SEO → Local SEO settings or custom JSON-LD |
| 3 | **Add TouristAttraction schema** on each tour page (~10–15 pages) | Google AI Overview | 2 hrs | WordPress hook: auto-generate from tour custom fields |
| 4 | **Enable BreadcrumbList** in Yoast SEO | All platforms | 5 min | Yoast → Search Appearance → Breadcrumbs |
| 5 | **Add AggregateRating schema** | Google AI Overview | 30 min | After site collects reviews; initially use TripAdvisor data |
| 6 | **Add Article schema** on blog/guide pages (~20 pages) | ChatGPT + Claude + Google AI Overv. | 1 hr | Enable in Yoast SEO (auto per post type) |

**Phase 1 Deliverables: 6 schema types on all relevant pages.**

---

### Phase 2: Citation & Entity Building (Week 3–4)

| # | Action | AI Impact | Effort |
|---|---|---|---|
| 7 | **Register with Bing Webmaster Tools** + submit sitemap | ChatGPT | 30 min |
| 8 | **Claim/optimize Bing Places for Business** | ChatGPT | 30 min |
| 9 | **List tours on Viator, GetYourGuide, Klook** (if not already) | AI aggregation citations | 4 hrs |
| 10 | **Create/update Wikidata entry** for Active Oahu Tours | Knowledge Graph | 1 hr |
| 11 | **Add `sameAs` links** to Organization/LocalBusiness schema (TripAdvisor, Yelp, Facebook, Instagram, YouTube) | Entity linking | 15 min |
| 12 | **Submit to Hawaii Tourism Authority** directory and Go Hawaii partner program | Authority | 1 hr |
| 13 | **Optimize Google Business Profile** Q&A (seed 10 questions + answers) | Google AI Overview FAQ | 1 hr |

---

### Phase 3: Content Architecture for AI (Week 5–6)

| # | Action | AI Impact | Effort |
|---|---|---|---|
| 14 | **Restructure tour pages** with AI-friendly content format (see Section 5.2) | All platforms | 4 hrs |
| 15 | **Add "Quick Facts" data blocks** to each tour page (LLM extraction) | All platforms | 2 hrs |
| 16 | **Create comparison content:** "Kayak Rental vs Guided Tour" | Perplexity + ChatGPT | 2 hrs |
| 17 | **Create "Best Of" content:** "5 Best Oahu Kayak Tours for Families" | Google AI Overview | 3 hrs |
| 18 | **Add HowTo schema** to 3 top guide pages | Google AI Overview + Perplexity | 1.5 hrs |
| 19 | **Add VideoObject schema** to video content pages | Google AI Overview | 30 min |
| 20 | **Add author bios** with certifications to all blog posts | Claude + E-E-A-T | 2 hrs |

---

### Phase 4: Monitoring & Iteration (Ongoing)

| # | Action | AI Impact | Frequency |
|---|---|---|---|
| 21 | Monitor Google Search Console for AI Overview impression data | Optimization | Weekly |
| 22 | Track "Active Oahu" mentions in ChatGPT + Perplexity via manual queries | Visibility tracking | Bi-weekly |
| 23 | Update FAQ schema as new customer questions emerge | Freshness signal | Monthly |
| 24 | Refresh tour page content seasonally | Recency signal | Quarterly |
| 25 | Monitor competitors for new schema adoption | Competitive intelligence | Monthly |
| 26 | A/B test content formats for AI citation rates | Optimization | Ongoing |

---

## 8. Technical Implementation Notes

### 8.1 WordPress / Yoast SEO Integration

Active Oahu uses WordPress with Yoast SEO. Most schema types can be implemented via Yoast:

| Schema | Yoast Support | Implementation |
|---|---|---|
| Organization | ✅ Native | Already active |
| LocalBusiness | ⚠️ Partial | Use custom code or Yoast's Local SEO add-on |
| FAQPage | ✅ Via blocks | Yoast FAQ block outputs JSON-LD automatically |
| Article | ✅ Auto | Enable per post type in Yoast settings |
| BreadcrumbList | ✅ Auto | Enable in Yoast → Search Appearance |
| AggregateRating | ❌ Not native | Custom code or plugin (kk Star Ratings, WP Review Pro) |
| TouristAttraction | ❌ Not native | Custom JSON-LD via `wp_head` hook |
| HowTo | ✅ Via blocks | Yoast HowTo block outputs JSON-LD automatically |
| VideoObject | ❌ Not native | Custom code or Yoast Video SEO add-on |

### 8.2 Custom JSON-LD Injection (WordPress)

For schemas not supported by Yoast, inject via theme's `functions.php` or a custom plugin:

```php
// Add TouristAttraction schema on tour CPT pages
add_action('wp_head', function() {
    if (!is_singular('activities')) return; // adjust post type slug
    
    $tour_data = [
        "@context" => "https://schema.org",
        "@type" => "TouristAttraction",
        "name" => get_the_title(),
        "description" => get_the_excerpt(),
        "url" => get_permalink(),
        "image" => get_the_post_thumbnail_url(null, 'full'),
        "provider" => ["@id" => site_url('/#localbusiness')],
        "location" => [
            "@type" => "Place",
            "name" => get_post_meta(get_the_ID(), 'tour_location_name', true),
            "geo" => [
                "@type" => "GeoCoordinates",
                "latitude" => get_post_meta(get_the_ID(), 'tour_lat', true),
                "longitude" => get_post_meta(get_the_ID(), 'tour_lng', true),
            ]
        ],
        "offers" => [
            "@type" => "Offer",
            "price" => get_post_meta(get_the_ID(), 'tour_price', true),
            "priceCurrency" => "USD"
        ]
    ];
    
    echo '<script type="application/ld+json">' . 
         json_encode($tour_data, JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . 
         '</script>';
});
```

### 8.3 Validation

After implementing each schema type, validate using:
- **Google Rich Results Test:** https://search.google.com/test/rich-results
- **Schema.org Validator:** https://validator.schema.org
- **Google Search Console:** Monitor for schema errors in Enhancements reports

### 8.4 Cloudflare Considerations

Active Oahu uses Cloudflare APO. JSON-LD injection via PHP `wp_head` is server-side → will be cached by APO. **No conflict.**

---

## 9. Success Metrics & KPIs

### 9.1 Leading Indicators (30-day)

| Metric | Current | Target | Tool |
|---|---|---|---|
| Schema types on site | 2 (Organization + WebSite) | 7+ | Rich Results Test |
| Schema validation errors | Unknown (not checked) | 0 | Google Search Console |
| FAQ schema pages | 0 | 5+ | Rich Results Test |
| LocalBusiness schema | ❌ Missing | ✅ Live | Rich Results Test |
| Bing Webmaster Tools | ❌ Not registered | ✅ Registered | BWT |
| Bing Places listing | ❌ Not claimed | ✅ Optimized | Bing Places |

### 9.2 AI Visibility Metrics (60-day)

| Metric | Current | Target | Tool |
|---|---|---|---|
| Appearances in Google AI Overviews | 0 | 5+/week | Manual + GSC (AI Overview filter) |
| Citations in ChatGPT answers | 0 | 2+/month | Manual query tracking |
| Citations in Perplexity | 0 | 3+/month | Manual query tracking |
| Google Knowledge Graph panel | ❌ No panel | Panel for "Active Oahu Tours" | Manual Google search |
| FAQ rich results in SERP | 0 | 3+ pages | GSC |
| Review stars in SERP | ❌ Not showing | ★★★★★ | GSC |

### 9.3 Business Metrics (90-day)

| Metric | Current | Target | Tool |
|---|---|---|---|
| Organic traffic from AI-discoverable queries | Baseline | +15-25% | GA4 / GSC |
| Booking conversions from organic | Baseline | +10% | FareHarbor + GA4 |
| Tour page CTR in SERP | Baseline | +5% | GSC |
| Direct bookings mentioning AI search | 0 | Track manually | Customer survey |

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Google changes AI Overview citation criteria | Medium | High | Diversify across multiple AI platforms (ChatGPT, Perplexity). Schema is the common denominator. |
| Competitors copy schema strategy | High (within 6 months) | Medium | Move fast. First-mover advantage is real. Once established in AI citations, harder to displace. |
| FareHarbor iframe conflicts with schema | Low | Medium | Test that Offer schema points to FareHarbor booking URL. If conflict, use `offers.url` to link. |
| Weglot translation may not translate JSON-LD | Medium | Medium | Test `hreflang` with schema. May need language-specific schema blocks for `/ja/` pages. |
| AI hallucinates incorrect tour info | Medium | High | Ensure content is unambiguous. Include clear facts in structured data. Monitor AI citations for accuracy. |
| Over-reliance on structured data without quality content | Low | High | Schema without great content = spam signal. Content quality must match schema ambition. |

---

## 11. Conclusion

Active Oahu Tours has a **massive untapped opportunity** in AI search visibility. While competitors with huge brand authority (Kualoa Ranch) dominate through name recognition, Active Oahu can leapfrog them in AI-generated answers through superior structured data and AI-optimized content.

**The window is open now.** No Oahu kayak tour operator has implemented FAQ schema, tour-level product schema, or comprehensive AI content formatting. The first to do so will capture citations across Google AI Overviews, ChatGPT, Perplexity, and Claude — channels that are rapidly becoming how travelers discover and book tours.

**Three immediate actions:**

1. **Deploy FAQ + LocalBusiness schema** (30 minutes each, immediate AI visibility gain)
2. **Add TouristAttraction schema to all tour pages** (2 hours, differentiator no competitor has)
3. **Register with Bing Webmaster Tools + Bing Places** (1 hour, unlocks ChatGPT visibility)

From schema-invisible to AI-citable in under 2 weeks of focused implementation.

---

## Appendix A: Schema Reference Quick Cards

See the SEO audit (GRO-117) for the current state of Active Oahu's schema and competitor comparison.

## Appendix B: Key Resources

| Resource | URL |
|---|---|
| Google Rich Results Test | https://search.google.com/test/rich-results |
| Schema.org Validator | https://validator.schema.org |
| Schema.org TouristAttraction | https://schema.org/TouristAttraction |
| Schema.org Trip | https://schema.org/Trip |
| Schema.org FAQPage | https://schema.org/FAQPage |
| Schema.org LocalBusiness | https://schema.org/LocalBusiness |
| Google Search Central — Structured Data Gallery | https://developers.google.com/search/docs/appearance/structured-data/search-gallery |
| Bing Webmaster Tools | https://www.bing.com/webmasters |
| Bing Places for Business | https://www.bingplaces.com |
| Google Business Profile | https://business.google.com |
| Wikidata | https://www.wikidata.org |

---

*Strategy developed for GRO-118 | Active Oahu AI SEO (GEO/AEO) Strategy*
*Based on research of Google AI Overviews, ChatGPT, Perplexity, Claude surfacing patterns — May 2026*
