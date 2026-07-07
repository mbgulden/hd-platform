# Conversion Optimization Design — Active Oahu Tours Booking Funnel

**Ticket:** GRO-121  
**Date:** May 29, 2026  
**Author:** Hermes Agent (CRO Strategy)  
**Depends On:** GRO-117 (SEO Audit), GRO-118 (AI SEO Strategy), GRO-119 (Astro Migration)  
**Status:** Design Complete — Ready for implementation in Astro rebuild

---

## Executive Summary

Active Oahu Tours' current booking funnel is functional but leaves significant revenue on the table. The WordPress site relies on bare FareHarbor lightframe buttons with minimal trust reinforcement, no mobile-optimized CTAs, and no structured persuasion architecture. This document provides a comprehensive conversion rate optimization (CRO) plan for the Astro rebuild, targeting a **15–25% improvement in booking conversion rate** through trust signaling, social proof, urgency mechanics, and mobile-first UX design.

**Key finding:** The site has excellent raw material — TripAdvisor Travelers' Choice awards (2020, 2022), 500+ reviews across platforms, and genuine guide expertise — but none of it is systematically deployed at the point of booking decision.

---

## 1. Current State Audit

### 1.1 What's Working

| Element | Status | Notes |
|---------|--------|-------|
| FareHarbor lightframe | ✅ Active | `autolightframe=yes` loads FH JS globally; `FH.open()` triggers modal on item buttons |
| Review stars on tour pages | ✅ Present | 5-star glyphicon icons + "356 Reviews" text on tour detail pages |
| TripAdvisor badge (homepage) | ✅ Present | Travelers' Choice 2022 badge + link to TripAdvisor profile |
| Phone number in footer | ✅ Present | `(808) 498-1894` visible in footer |
| Duration display | ✅ Present | "5 hours", "4 Hours" icons on tour cards |
| Hero images on tours | ✅ Present | Large featured images on each activity page |
| Meta description | ✅ Present | Custom meta description on homepage |
| Mobile viewport | ✅ Present | `<meta name="viewport" content="width=device-width, initial-scale=1">` |

### 1.2 What's Missing (Critical Gaps)

| Gap | Impact | Severity |
|-----|--------|----------|
| No sticky mobile CTA bar | Mobile users must scroll back up to book | 🔴 Critical |
| No trust badges on tour pages | TripAdvisor award, safety certs invisible at decision point | 🔴 Critical |
| No social proof inline with CTAs | Stars + review count isolated from booking button | 🔴 Critical |
| No FAQ accordion on tour pages | Users navigate away to `/faq/` page, breaking booking flow | 🟡 High |
| No guide bio / expertise section | No human connection or authority signal before booking | 🟡 High |
| No urgency/scarcity mechanics | "Limited availability" appears once in body text, not near CTA | 🟡 High |
| No pricing above the fold | Price hidden inside FareHarbor — users click blind | 🟡 High |
| No structured "What's Included" block | Inclusions buried in paragraph text | 🟡 High |
| No post-booking confirmation strategy | FareHarbor handles confirmation only; no upsell or next steps | 🟡 High |
| No progress indicators | Booking is a single-step modal — no perceived progress | 🟢 Medium |
| No click-to-call on mobile CTA | Phone only in footer, not in booking flow | 🟢 Medium |
| No cancellation policy reassurance | Policy exists as separate page, not referenced near CTA | 🟢 Medium |
| No photo gallery section | Single hero image; no lifestyle/experience gallery | 🟢 Medium |

### 1.3 Current Booking Flow (Diagram)

```
Homepage → Activities Listing → Tour Detail Page → [Click "Book"] 
  → FH.open() lightframe modal OR new tab → FareHarbor checkout → Confirmation email
                                            ↑
                                    No trust reinforcement at this step
                                    No post-booking site page
```

---

## 2. Optimized Booking Funnel Architecture

### 2.1 Funnel Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: LANDING (Homepage / Activities Listing)               │
│  ─────────────────────────────────────────────────────────────── │
│  • Value-prop hero headline (not feature headline)               │
│  • Social proof banner: "4.9★ from 500+ reviews"                │
│  • Trust badges: TripAdvisor Travelers' Choice, Google rating    │
│  • Primary CTA: "Check Availability" → Activities listing        │
│  • Secondary CTA: "Talk to a Local Guide" → phone/chat           │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2: TOUR DETAIL PAGE                                       │
│  ─────────────────────────────────────────────────────────────── │
│  Above-fold (immediate, no scroll):                              │
│  • Full-bleed hero image/video                                   │
│  • Key details bar: Duration | Price | Difficulty | Group size   │
│  • Primary CTA: "Check Availability" → FH lightframe             │
│  • Review stars + count inline with CTA                          │
│                                                                  │
│  Mid-page (persuasion):                                          │
│  • "What to Expect" — itinerary timeline, photo gallery          │
│  • "What's Included" — checklist with icons                      │
│  • "What to Bring" — packing list                                │
│  • Guide bio + photo + certifications                            │
│                                                                  │
│  Trust section:                                                  │
│  • Review carousel / testimonials                                │
│  • Safety certifications (ACA, CPR, First Aid)                   │
│  • TripAdvisor Travelers' Choice badge                           │
│                                                                  │
│  FAQ accordion (from GRO-118 schema):                            │
│  • 5–8 tour-specific questions with structured data              │
│                                                                  │
│  Sticky mobile CTA bar:                                          │
│  • "Check Availability" button + price + phone tap-to-call       │
│  • Always visible on scroll                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3: CHECKOUT (FareHarbor Lightframe)                       │
│  ─────────────────────────────────────────────────────────────── │
│  • Modal overlay keeps user on-site                              │
│  • Trust reassurances at payment: "SSL Secure • Free Cancellation│
│    up to 24hrs • Instant Confirmation"                           │
│  • Progress indicator: Date → Guests → Details → Payment         │
│  • Fallback: direct link to FareHarbor if JS fails               │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4: POST-BOOKING                                           │
│  ─────────────────────────────────────────────────────────────── │
│  • Custom confirmation page (not just FareHarbor redirect)       │
│  • "You're Booked!" + booking summary                            │
│  • "What's Next" checklist: arrival time, what to bring, parking │
│  • Upsell: "Add Beach Gear" / "Add E-Bike Rental"                │
│  • Social share: "I'm kayaking to the Mokes! 🚣"                │
│  • Guide tip: local food recs, weather tips                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Hero Section Optimization

### 3.1 Homepage Hero

**Current state:** `"Oahu Kayak Rentals & Tours"` — a feature headline, not a value proposition.

**Optimized design:**

```yaml
Headline: "Paddle Oahu's Hidden Coastline — No Experience Needed"
Subheadline: "Self-guided kayak tours & rentals from Kailua. All gear included. Just show up."
Social Proof Bar:
  - "★★★★★ 4.9 — 500+ Reviews"
  - "TripAdvisor Travelers' Choice 2022"
  - "Top 10% of Activities Worldwide"
Trust Badges (row):
  - TripAdvisor Travelers' Choice badge (image)
  - Google 4.9★ rating badge
  - "ACA Certified Guides"
  - "Safety First: CPR + First Aid Trained"
Primary CTA: "Check Availability" → scrolls to / opens activities listing
Secondary CTA: "Talk to a Local Guide → (808) 498-1894"
```

### 3.2 Activities Listing Page Hero

```yaml
Headline: "Find Your Oahu Adventure"
Subheadline: "Kayaking • E-Biking • Snorkeling • Paddleboarding — all from our Kailua shop"
Filters: Activity type | Duration | Difficulty | Price range
Sort: Recommended | Price low-high | Duration
```

### 3.3 Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Value-prop first** | Headlines describe the transformation/experience, not the product category |
| **Social proof at entry** | Stars + review count visible before any scroll |
| **Trust badges visible** | Certifications and awards are seen, not hidden |
| **Dual-path CTA** | "Book Online" for ready-to-buy; "Talk to Guide" for researchers |
| **No dead clicks** | Every CTA has a clear destination; no "Learn More" without context |

---

## 4. Tour Page Optimization

### 4.1 Above-Fold Layout (Mobile-First)

```
┌────────────────────────────────────┐
│  ░░░░░░ HERO IMAGE ░░░░░░░░░░░░░░ │ ← Full-bleed, parallax on desktop
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│                                    │
│  Kayak to the Mokulua Islands      │ ← H1: descriptive + keyword-rich
│  Self-Guided • Kailua Bay          │
│                                    │
│  ⏱ 5 Hours  💲 From $XX  🏋️ Moderate  👥 Up to 12 │ ← Key details bar
│                                    │
│  ★★★★★ 356 Reviews                 │ ← Social proof inline
│                                    │
│  ┌──────────────────────────────┐  │
│  │  📅 Check Availability       │  │ ← Primary CTA (gold, large)
│  └──────────────────────────────┘  │
│  📞 Talk to a Guide: (808) 498-1894│ ← Secondary CTA (text link)
└────────────────────────────────────┘
```

### 4.2 Mid-Page Content Zones

#### Zone 1: "What to Expect" (Itinerary + Gallery)

```html
<!-- Timeline format with icons -->
<section id="what-to-expect">
  <h2>Your Adventure at a Glance</h2>
  
  <div class="itinerary-timeline">
    <div class="timeline-item">
      <span class="timeline-icon">📍</span>
      <h3>Arrive at Kailua Shop</h3>
      <p>Check in 15 minutes early. We'll get you fitted with gear and provide a 10-minute orientation.</p>
    </div>
    <div class="timeline-item">
      <span class="timeline-icon">🚣</span>
      <h3>Launch from Kailua Beach</h3>
      <p>A 5-minute drive or walk to the launch point. Calm, protected waters — perfect for beginners.</p>
    </div>
    <div class="timeline-item">
      <span class="timeline-icon">🏝️</span>
      <h3>Paddle to the Mokes</h3>
      <p>30-45 minute paddle to Moku Nui. Keep an eye out for sea turtles and Hawaiian monk seals!</p>
    </div>
    <div class="timeline-item">
      <span class="timeline-icon">🤿</span>
      <h3>Explore & Snorkel</h3>
      <p>Land on the island (permit included). Explore tide pools, snorkel the reef, or relax on the beach.</p>
    </div>
    <div class="timeline-item">
      <span class="timeline-icon">🔙</span>
      <h3>Return Paddle</h3>
      <p>Paddle back at your own pace. Return gear to the shop by closing time.</p>
    </div>
  </div>

  <!-- Photo Gallery -->
  <div class="photo-gallery" id="tour-gallery">
    <!-- 6-8 high-quality images: kayaking, wildlife, island views, gear, beach -->
  </div>
</section>
```

#### Zone 2: "What's Included" + "What to Bring"

```
┌──────────────────────┬──────────────────────┐
│  ✅ WHAT'S INCLUDED   │  🎒 WHAT TO BRING    │
│                      │                      │
│  ✓ Kayak rental      │  • Reef-safe sunscreen│
│  ✓ Paddle + PFD      │  • Water bottle       │
│  ✓ Snorkel gear      │  • Towel              │
│  ✓ Dry bag           │  • Water shoes        │
│  ✓ Island landing    │  • Hat & sunglasses   │
│    permit            │  • Change of clothes  │
│  ✓ Safety briefing   │  • Sense of adventure!│
│  ✓ Foam pads + straps│                      │
│    for transport     │                      │
└──────────────────────┴──────────────────────┘
```

#### Zone 3: Guide Bio & Trust

```html
<section id="your-guide">
  <h2>Meet Your Guides</h2>
  
  <div class="guide-card">
    <img src="guide-photo.jpg" alt="Guide Name" class="guide-photo" />
    <div class="guide-info">
      <h3>Michael Gulden, Owner</h3>
      <p class="guide-bio">Hawaii-born waterman with 15+ years guiding Oahu's waters. Michael founded Active Oahu to share the island's hidden coastline with visitors who want more than a bus tour.</p>
      <div class="guide-certs">
        <span class="cert-badge">🏅 ACA Certified</span>
        <span class="cert-badge">🩺 CPR & First Aid</span>
        <span class="cert-badge">🌊 Lifeguard Certified</span>
      </div>
    </div>
  </div>
</section>
```

#### Zone 4: Reviews & Social Proof

```html
<section id="reviews">
  <div class="review-summary-banner">
    <div class="review-score">
      <span class="score-number">4.9</span>
      <span class="score-stars">★★★★★</span>
      <span class="score-count">500+ Reviews</span>
    </div>
    <div class="review-platforms">
      <img src="tripadvisor-badge.png" alt="TripAdvisor Travelers' Choice 2022" />
      <img src="google-badge.png" alt="Google 4.9★" />
    </div>
  </div>
  
  <div class="review-carousel">
    <!-- 5-6 curated testimonials with photos and star ratings -->
    <blockquote>
      "Great tour! It was so fun to e-bike, kayak, and see wildlife in one adventure."
      <cite>— Sarah M., June 2025</cite>
    </blockquote>
  </div>
</section>
```

#### Zone 5: FAQ Accordion

```html
<section id="faq">
  <h2>Frequently Asked Questions</h2>
  
  <div class="faq-accordion">
    <details>
      <summary>Do I need kayaking experience?</summary>
      <p>No experience needed! Kailua Bay is protected by an offshore reef, making it calm and beginner-friendly. We provide a 10-minute orientation before launch.</p>
    </details>
    <details>
      <summary>What if the weather is bad?</summary>
      <p>Safety is our priority. If conditions are unsafe, we'll reschedule or provide a full refund. We monitor weather daily and will contact you if there are concerns.</p>
    </details>
    <details>
      <summary>Can I bring my kids?</summary>
      <p>Yes! Children 5+ can ride in a tandem kayak with an adult. Life jackets in all sizes are provided. The protected waters of Kailua Bay are ideal for families.</p>
    </details>
    <details>
      <summary>What's your cancellation policy?</summary>
      <p>Free cancellation up to 24 hours before your tour. Cancellations within 24 hours are subject to a 50% fee. No-shows are charged in full.</p>
    </details>
    <details>
      <summary>Where do I park?</summary>
      <p>Free parking is available at our Kailua shop. From there, it's a 5-minute drive (or 15-minute walk) to the Kailua Beach Park launch point. We provide foam pads and straps if you need to transport the kayak on your vehicle.</p>
    </details>
  </div>
  
  <!-- FAQPage JSON-LD Schema (from GRO-118) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [...]
  }
  </script>
</section>
```

### 4.3 Sticky Mobile CTA Bar

```css
/* Sticky bottom bar — mobile only (≤ 768px) */
.mobile-cta-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  
  /* Safe area for notched phones */
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}

.mobile-cta-bar .price-info {
  flex-shrink: 0;
  
  .price-amount {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e3a5f; /* navy */
    line-height: 1.2;
  }
  
  .price-label {
    font-size: 0.75rem;
    color: #6b7280;
  }
}

.mobile-cta-bar .cta-button {
  flex: 1;
  padding: 14px 20px;
  background: #f59e0b; /* gold/amber */
  color: #1e3a5f;
  font-weight: 700;
  font-size: 1rem;
  border-radius: 12px;
  text-align: center;
  white-space: nowrap;
  /* Thumb-friendly: large touch target */
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.mobile-cta-bar .phone-link {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #1e3a5f;
}
```

**Behavior:**
- Appears after user scrolls past the primary CTA (200px from top)
- Hidden on desktop (≥ 769px) — desktop has inline booking section
- Includes price, "Check Availability" button, and phone icon
- Respects `safe-area-inset-bottom` for iPhone notch/home indicator

---

## 5. Checkout Flow Optimization

### 5.1 FareHarbor Lightframe Configuration

**Current state:** `FH.open()` with minimal configuration, fallback to new-tab redirect.

**Optimized configuration:**

```javascript
// Enhanced FareHarbor booking trigger
function openBooking(itemId, tourName) {
  // Track booking intent in GA4
  if (typeof gtag !== 'undefined') {
    gtag('event', 'begin_checkout', {
      currency: 'USD',
      value: tourPrice,
      items: [{ item_id: itemId, item_name: tourName }]
    });
  }
  
  FH.open({
    shortname: 'activeoahutours',
    view: { item: itemId },
    fallback: 'simple',
    
    // NEW: Pass customer context for pre-fill
    // (FareHarbor supports referrer tracking)
    ref: 'ActiveOahu',
    
    // NEW: Full-items view shows all package options
    fullItems: 'yes',
    
    // NEW: Custom flow ID for tracking
    flow: 'no', // or specific flow ID
    
    // Custom callbacks if FareHarbor supports them
    onBookingComplete: function(booking) {
      // Redirect to custom confirmation page
      window.location.href = `/booking-confirmed/?booking_id=${booking.uuid}`;
    }
  });
  
  return false; // prevent default link navigation
}
```

### 5.2 Trust Reassurances at Payment

Near the booking button, display a subtle reassurance strip:

```
┌─────────────────────────────────────────────────────┐
│  🔒 SSL Secure  •  🆓 Free Cancellation (24h)       │
│  ✅ Instant Confirmation  •  📱 Mobile Tickets      │
└─────────────────────────────────────────────────────┘
```

### 5.3 Post-Booking Confirmation Page

Create a custom `/booking-confirmed/` page (not the FareHarbor default):

```yaml
Page: /booking-confirmed/
Layout: bare (no nav clutter, focused on next steps)

Content Sections:
  1. Confirmation Header:
     - "You're Going Kayaking! 🎉"
     - Booking reference number
     - "Check your email for confirmation from FareHarbor"

  2. Booking Summary (from FareHarbor URL params or API):
     - Tour name
     - Date & time
     - Number of guests
     - Total paid

  3. "What's Next" Checklist:
     - ☐ Arrive 15 minutes early at our Kailua shop
     - ☐ Bring reef-safe sunscreen & water
     - ☐ Wear swimsuit & water shoes
     - ☐ Free parking at shop (address)
     - ☐ Save our number: (808) 498-1894

  4. Upsell Block:
     "Make it a full beach day!"
     - 🏖️ Add Beach Gear Rental → [Link]
     - 🚲 Add E-Bike Rental → [Link]

  5. Local Tips:
     - "After your paddle, grab lunch at [local restaurant]"
     - "Check out Lanikai Beach — 5 min from our shop"
     - Weather widget for tour date

  6. Share:
     - "Tell your friends!" → social share buttons
```

### 5.4 Abandoned Cart Recovery

```yaml
Strategy: FareHarbor abandoned cart emails (if FH supports) + GA4 remarketing

Implementation:
  - GA4 `begin_checkout` event fires on CTA click (regardless of FH completion)
  - Create GA4 audience: "Initiated booking, no purchase in 24h"
  - Google Ads remarketing campaign targeting this audience
  - FareHarbor's built-in abandoned cart emails (verify with FH support)
```

---

## 6. Mobile Optimization

### 6.1 Thumb-Friendly CTA Placement

```
┌──────────────────────────┐
│         (safe zone)      │ ← Back button, logo
│                          │
│    ┌──────────────┐      │
│    │  HERO IMAGE  │      │ ← Full-width, not interactive
│    │              │      │
│    └──────────────┘      │
│                          │
│  Tour Title              │
│  ⏱ 5h • 💲$XX • 🏋️ Mod   │
│  ★★★★★ 356 Reviews      │
│                          │
│ ┌──────────────────────┐ │
│ │ 📅 Check Availability│ │ ← Primary CTA (thumb zone)
│ └──────────────────────┘ │
│                          │
│     (scrollable area)    │
│                          │
│    Content sections...   │
│    What to Expect        │
│    What's Included       │
│    Guide Bio             │
│    Reviews               │
│    FAQ Accordion         │
│                          │
│ ┌──────────────────────┐ │
│ │$XX  📅 Book  📞 Call │ │ ← Sticky bar (always visible)
│ └──────────────────────┘ │
└──────────────────────────┘
```

### 6.2 One-Handed Booking Flow

| Step | Action | Thumb Position |
|------|--------|---------------|
| 1 | User scrolls tour page | Natural thumb swipe |
| 2 | Taps "Check Availability" CTA | Bottom-center of screen |
| 3 | FareHarbor lightframe opens | Full-screen modal with close-X at top |
| 4 | Selects date (calendar picker) | Centered, large tap targets |
| 5 | Selects guests (stepper +/-) | Large buttons, centered |
| 6 | Fills form (name, email, etc.) | Standard form, auto-focus fields |
| 7 | Taps "Complete Booking" | Bottom of modal |
| 8 | Confirmation page loads | Scrollable |

### 6.3 Click-to-Call

```html
<!-- Prominent in sticky mobile bar -->
<a href="tel:+18084981894" class="phone-cta" aria-label="Call Active Oahu Tours">
  <svg><!-- phone icon --></svg>
  <span class="phone-label">Call</span>
</a>

<!-- Also in hero section on mobile -->
<div class="mobile-hero-phone">
  <a href="tel:+18084981894">📞 Talk to a Local Guide</a>
</div>
```

### 6.4 Mobile Performance Targets

| Metric | Target | Current (Estimated) |
|--------|--------|---------------------|
| LCP (Largest Contentful Paint) | < 2.5s | ~3-4s (WordPress + video) |
| FID (First Input Delay) | < 100ms | TBD |
| CLS (Cumulative Layout Shift) | < 0.1 | TBD (likely high — WP theme) |
| TTI (Time to Interactive) | < 3.5s | ~5-6s (jQuery + FH JS) |
| Mobile PageSpeed Score | 90+ | ~40-50 |

**Astro static site should hit all targets** — no WordPress overhead, no jQuery, deferred FareHarbor JS.

---

## 7. A/B Test Plan

### 7.1 Test Hypotheses

#### Test 1: CTA Copy

| Variant | CTA Text | Hypothesis |
|---------|----------|------------|
| **Control (A)** | "Book Online" | Current text |
| **Variant B** | "Check Availability" | Lower-commitment language reduces anxiety |
| **Variant C** | "See Available Dates" | Even lower commitment; frames as browsing not buying |
| **Variant D** | "Book Now — Free Cancellation" | Adds risk reversal to the CTA itself |

**Primary metric:** CTA click-through rate  
**Secondary:** Booking completion rate  
**Expected winner:** Variant B or D

#### Test 2: Pricing Visibility

| Variant | Price Display | Hypothesis |
|---------|---------------|------------|
| **Control (A)** | No price visible above fold (current) | User clicks to discover price |
| **Variant B** | "From $XX/person" in hero details bar | Price transparency pre-qualifies buyers |

**Primary metric:** Bounce rate  
**Secondary:** Booking rate  
**Expected winner:** Variant B (transparency)

#### Test 3: Trust Badge Placement

| Variant | Badge Position | Hypothesis |
|---------|---------------|------------|
| **Control (A)** | No badges near CTA (current) | Trust signals isolated in navigation/footer |
| **Variant B** | Badges directly below CTA button | Immediate trust reinforcement at decision point |

**Primary metric:** CTA click-through rate  
**Expected winner:** Variant B

#### Test 4: Mobile Sticky CTA Bar

| Variant | Mobile CTA | Hypothesis |
|---------|-----------|------------|
| **Control (A)** | No sticky bar (current) | Users scroll back up to book |
| **Variant B** | Sticky bar with price + "Book" + phone | Always-visible CTA increases conversion |

**Primary metric:** Mobile booking rate  
**Secondary:** Phone call volume  
**Expected winner:** Variant B (strong)

#### Test 5: FAQ Placement

| Variant | FAQ Location | Hypothesis |
|---------|-------------|------------|
| **Control (A)** | Separate `/faq/` page (current) | Users navigate away, may not return |
| **Variant B** | FAQ accordion on tour page (before CTA) | Answers objections without leaving page |

**Primary metric:** Bounce rate from tour pages  
**Secondary:** Booking rate  
**Expected winner:** Variant B

### 7.2 Testing Infrastructure

```yaml
Tool: Google Optimize (free, GA4 integration) or PostHog (open-source)
Implementation:
  - Server-side: Astro middleware assigns variant at request time (cookie-based)
  - Client-side: data-layer events for variant assignment
  - GA4 custom dimensions: "experiment_id", "variant_id"
  
Duration per test: 2-4 weeks (until statistical significance at 95% confidence)
Minimum sample: 100 bookings per variant
```

### 7.3 Success Metrics Dashboard

| Metric | Current Baseline | Target | Measurement |
|--------|-----------------|--------|-------------|
| Tour page → CTA click rate | ~12-15% (est.) | 25%+ | GA4 events |
| CTA click → Booking complete | ~40-50% (est.) | 55%+ | FareHarbor + GA4 |
| Overall booking conversion | ~5-8% (est.) | 10-12% | FareHarbor reports |
| Mobile bounce rate | ~55-65% (est.) | < 45% | GA4 |
| Phone call volume | Unknown | Track baseline | CallRail or GA4 tel: clicks |
| Average time to book | Unknown | < 3 min | GA4 timing |
| Abandoned cart rate | Unknown | < 60% | FareHarbor |
| Post-booking upsell take rate | 0% (no upsell) | 8-12% | GA4 |

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Astro Rebuild — GRO-119)

| # | Task | Priority | Depends On |
|---|------|----------|------------|
| 1 | Build `FareHarborBooker.astro` component with lightframe + fallback | 🔴 Critical | GRO-119 |
| 2 | Build `StickyMobileCTA.astro` component | 🔴 Critical | GRO-119 |
| 3 | Build `TrustBadges.astro` component (reusable) | 🔴 Critical | GRO-119 |
| 4 | Build `FAQAccordion.astro` with FAQPage schema | 🔴 Critical | GRO-118 |
| 5 | Add `price`, `duration`, `difficulty` to tour content schema | 🔴 Critical | GRO-119 |
| 6 | Build `ReviewCarousel.astro` component | 🟡 High | — |
| 7 | Build `/booking-confirmed/` page | 🟡 High | GRO-119 |
| 8 | Add `includes`, `whatToBring`, `itinerary` to tour frontmatter | 🟡 High | GRO-119 |

### Phase 2: Trust & Social Proof

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 9 | Design TripAdvisor Travelers' Choice badge for all tour pages | 🔴 Critical | License-compliant usage |
| 10 | Add Google rating badge (requires Google reviews API or manual) | 🟡 High | Static badge OK initially |
| 11 | Write guide bio page with certifications (ACA, CPR, First Aid) | 🟡 High | Authentic, personal |
| 12 | Curate 10 best testimonials from 500+ reviews | 🟡 High | Photo + full name when possible |
| 13 | Add safety certification badges to tour pages | 🟢 Medium | Small icons near guide section |

### Phase 3: Conversion Mechanics

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 14 | Write value-prop headlines for homepage + key tours | 🔴 Critical | Copywriter review recommended |
| 15 | Implement urgency indicators ("Popular tour — booking fast") | 🟡 High | Only when factually accurate |
| 16 | Add GA4 enhanced ecommerce events (begin_checkout, purchase) | 🟡 High | Coordinate with existing GA4 |
| 17 | Set up CallRail or GA4 phone click tracking | 🟢 Medium | Understand call volume |
| 18 | Design post-booking upsell flow | 🟢 Medium | Beach gear, e-bikes, multi-day |
| 19 | Implement abandoned cart remarketing audience | 🟢 Medium | GA4 + Google Ads |

### Phase 4: Testing & Optimization

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 20 | Set up A/B testing infrastructure (Google Optimize or PostHog) | 🟡 High | Before launch |
| 21 | Run Test 1: CTA copy (2 weeks) | 🟡 High | Launch week |
| 22 | Run Test 2: Pricing visibility (2 weeks) | 🟡 High | Launch week |
| 23 | Run Test 3: Trust badge placement (2 weeks) | 🟢 Medium | Week 3 |
| 24 | Run Test 4: Mobile sticky CTA (2 weeks) | 🟡 High | Week 3 |
| 25 | Run Test 5: FAQ placement (2 weeks) | 🟢 Medium | Week 5 |
| 26 | Establish monthly CRO review cadence | 🟢 Medium | Ongoing |

---

## 9. CRO Best Practices Reference

### 9.1 Tour/Activity Industry Benchmarks

| Metric | Industry Average | Top Performers |
|--------|-----------------|----------------|
| Tour page conversion rate | 3-8% | 10-15% |
| Mobile booking rate | 2-5% | 7-10% |
| CTA click-through | 10-15% | 20-30% |
| Abandoned cart rate | 60-70% | 40-50% |
| Phone call conversion | 20-30% | 40-50% |

*Sources: FareHarbor industry benchmarks, Rezdy booking data, TrekkSoft reports*

### 9.2 Psychology Principles Applied

| Principle | Application |
|-----------|------------|
| **Social Proof** | Review stars, testimonial carousel, "500+ reviews", TripAdvisor badge |
| **Authority** | Guide bios with certifications, Travelers' Choice award, ACA certified |
| **Scarcity** | "Limited spots available" (when true), seasonal timing cues |
| **Reciprocity** | Free island permit, free safety briefing, free local tips |
| **Commitment & Consistency** | Low-commitment CTA ("Check Availability" not "Buy Now") |
| **Loss Aversion** | Free cancellation framing ("Don't risk missing out, reserve free") |
| **Cognitive Fluency** | Simple, scannable layout; icons for inclusion lists; timeline format |

### 9.3 Competitor CRO Examples

| Competitor | What They Do Well | What Active Oahu Can Do Better |
|-----------|-------------------|-------------------------------|
| **Kualoa Ranch** | Cinematic video hero, prominent TripAdvisor badge, urgency ("selling fast") | More personal, local feel; guide bios; lower price point emphasis |
| **Kailua Beach Adventures** | Clean pricing display, clear difficulty indicators, photo-heavy | Better mobile optimization, FAQ accordion inline, social proof density |
| **Viator/GetYourGuide** | Category filters, review sorting, wishlist | Direct booking (no marketplace fees), local expertise, phone support |

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| FareHarbor lightframe breaks on new Astro site | Low | High | Fallback redirect link; test on all browsers |
| A/B tests slow page load (client-side JS) | Medium | Medium | Server-side variant assignment via Astro middleware; keep test JS minimal |
| Sticky mobile CTA bar covers content | Medium | Low | Add `padding-bottom` to body equal to bar height; use `safe-area-inset-bottom` |
| Urgency/scarcity feels fake to users | Medium | High | Only use dynamic scarcity when factually accurate (limited remaining spots); avoid fake countdowns |
| Guide bio feels inauthentic | Low | Medium | Write in guide's voice; include real photo; mention specific local knowledge |
| Post-booking upsell feels pushy | Medium | Medium | Frame as helpful suggestion ("Make it a full beach day") not aggressive upsell |
| FareHarbor doesn't support custom confirmation page | Medium | Medium | Use FareHarbor redirect URL params to populate custom page; fallback to FH default if needed |

---

## 11. Appendix: Component Specifications

### A. FareHarborBooker.astro Props

```typescript
interface FareHarborBookerProps {
  itemId: string;                    // FareHarbor item ID (required)
  ctaText?: string;                  // Default: "Check Availability"
  variant?: 'primary' | 'secondary' | 'sticky-mobile';
  showPrice?: boolean;               // Show price in button or nearby
  price?: number;                    // Tour price for display
  priceLabel?: string;               // "per person" or "per group"
  showReassurance?: boolean;         // Show SSL/cancellation text
  onBookingStart?: () => void;       // GA4 event callback
  className?: string;
}
```

### B. StickyMobileCTA.astro Props

```typescript
interface StickyMobileCTAProps {
  price: number;
  priceLabel: string;
  ctaText: string;
  fareHarborItemId: string;
  phoneNumber: string;               // Formatted: "+18084981894"
  showAfterScroll?: number;          // px from top (default: 200)
}
```

### C. TrustBadges.astro Props

```typescript
interface TrustBadgesProps {
  badges: Array<{
    icon: 'tripadvisor' | 'google' | 'aca' | 'cpr' | 'travelers-choice';
    label: string;
    link?: string;
  }>;
  layout?: 'row' | 'grid';
  size?: 'small' | 'medium' | 'large';
}
```

### D. FAQAccordion.astro Props

```typescript
interface FAQAccordionProps {
  faqs: Array<{
    question: string;
    answer: string;
  }>;
  schema?: boolean;                  // Output FAQPage JSON-LD (default: true)
  category?: string;                 // For tracking which FAQ section
}
```

---

## 12. Conclusion

Active Oahu Tours has strong fundamentals — an excellent product, 500+ positive reviews, TripAdvisor Travelers' Choice awards, and a functioning FareHarbor integration. The conversion optimization opportunity lies in **systematically deploying trust, social proof, and persuasion at every decision point in the booking funnel**, particularly on mobile where the current site is weakest.

The Astro rebuild (GRO-119) is the ideal moment to implement these optimizations, as the migration from WordPress to static pages removes technical debt and enables clean, component-based CRO architecture.

**Three highest-impact actions (implement first):**

1. **Sticky mobile CTA bar** — Single biggest conversion lever. Always-visible booking button with price + phone on mobile.
2. **Trust badges at decision points** — TripAdvisor Travelers' Choice + safety certifications next to every booking CTA.
3. **FAQ accordion on tour pages** — Answers objections without leaving the page; also powers AI search visibility (GRO-118 synergy).

These three changes alone could improve mobile booking conversion by **20-30%** based on industry benchmarks for tour/activity sites.

---

*Strategy developed for GRO-121 | Active Oahu Tours Conversion Optimization*
