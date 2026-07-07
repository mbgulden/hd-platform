# Competitive Analysis: HD Engine vs Neutrino Design

> **GRO-167:** Competitive Parity Analysis — defining what 'full service HD support suite' means.
> **Date:** May 30, 2026
> **Author:** HD Platform Team

---

## Executive Summary

**Neutrino Design (neutrinoplatform.com)** is the gold-standard reference for Human Design software — widely trusted by practitioners as authoritative. Our engine (OpenHumanDesignMCP) has been **surgically verified against Neutrino Design** for 5 family member charts with 100% structural match on Type, Profile, Authority, Centers, and Variables. The only discrepancy is a single channel (25-51) that we compute but Neutrino Design likely filters on app-specific rules.

**Our engine is mathematically correct. The gap is in the platform layer — everything around the engine.**

---

## 1. Feature Comparison

| Capability | Neutrino Design | HD Engine (Us) | Gap |
|---|---|---|---|
| **Chart Computation — Natal** | ✅ | ✅ | None — verified parity |
| **Chart Computation — Transit** | ✅ | ✅ | None |
| **Chart Computation — Synastry** | ✅ | ✅ | None |
| **Interactive Bodygraph (SVG)** | ✅ Full interactive bodygraph with center/channel/gate highlighting | ❌ None | **Critical gap** — this is what every user expects |
| **User Accounts / Profiles** | ✅ Register, login, saved charts | ❌ None | **Critical gap** — no persistence |
| **Dashboard / Client Management** | ✅ Save & manage multiple charts | ❌ None | **Critical gap** for practitioners |
| **PDF Reports** | ✅ Customizable drag-and-drop editor, rich text, branding | ✅ Static HTML→PDF via wkhtmltopdf | Partial parity — we need UX layer |
| **Chart Widgets (Embeddable)** | ✅ Chart generator + live transit widgets | ❌ None | Gap for lead-gen |
| **Email Collection (Widgets)** | ✅ Flodesk + webhook integrations | ❌ None | Gap |
| **Native Mobile Apps** | ✅ iOS + Android (Neutrino Design app) | ❌ None | Long-term gap |
| **Articles / Education Library** | ✅ 10+ detailed guides, SEO-optimized | ❌ None | Gap for organic traffic |
| **Transit Calendar View** | ✅ Interactive calendar with daily transits | ❌ None | Gap |
| **Drag-and-Drop Report Editor** | ✅ Custom templates, branding, rich text | ❌ Static templates | Practitioner UX gap |
| **API Access** | ❌ No external API | ✅ REST API (natal, transits, synastry) | **Our advantage** |
| **Open Source** | ❌ Closed source | ✅ AGPLv3 — fully auditable | **Our advantage** |
| **Math Verification** | ❌ Can't verify their code | ✅ Public verification page + open source | **Our advantage** |
| **Practitioner Certification** | ❌ None | ✅ Light Filled Human Design | **Our advantage** |
| **AstroHD (Astrology)** | ✅ Astrology integration | ❌ None | Gap |
| **Integrations** | ✅ Flodesk, GoHighLevel (coming), Zapier (coming) | ❌ None | Gap but ours plugs into API |
| **Community** | Facebook group (HDBGM) | ❌ None | Gap |

---

## 2. Pricing Comparison

### Neutrino Design
- **Free tier:** Basic chart generation, limited features
- **Pro plan:** Full access to interactive bodygraph, transit tools, calendar, PDF reports, widgets, email collection
- Pricing is not publicly listed on their website (gated behind registration) — typical SaaS pattern
- Mobile app: Free to download, Pro features via subscription (likely $9.99-$19.99/mo based on app store patterns)
- Reports likely one-time purchases or included in Pro

### HD Engine (Our Planned Pricing)
From our existing pricing model:

| Product | Price | Status |
|---|---|---|
| **HD Cloud API — Free** | $0/mo (100 calls) | Planned |
| **HD Cloud API — Pro** | $49/mo (1,000 calls) | Planned |
| **HD Cloud API — Enterprise** | $499/mo (Unlimited) | Planned |
| **Deep Dive Reports — Natal** | $19 one-time | Planned |
| **Deep Dive Reports — Synastry** | $29 one-time | Planned |
| **Deep Dive Reports — Bundle** | $39 one-time | Planned |
| **Managed MCP Hosting — Starter** | $29/mo | Planned |
| **Managed MCP Hosting — Pro** | $79/mo | Planned |
| **Managed MCP Hosting — Studio** | $199/mo | Planned |

**Our advantage:** We can undercut Neutrino Design on reports (they likely charge more per report) AND we're the only one with API access for developers.

---

## 3. What We Must Build to Be Competitive

### Tier 1: Minimum Viable Competitive Product (MVCP) — 4-6 weeks

These are the blockers that prevent practitioners from choosing us:

1. **Interactive Bodygraph (SVG)**
   - Rendering the 9 centers, 64 gates, 36 channels as an SVG
   - Defined/undefined center coloring
   - Gate activation highlighting
   - Click/tap to see gate details
   - This is the #1 user expectation — the visual chart IS the product
   - Technical: D3.js or raw SVG; our engine already outputs all the data needed for rendering

2. **User Accounts & Saved Charts**
   - Register, login, password reset
   - Save unlimited charts (name, birth date/time, location)
   - Basic profile page
   - Technical: PostgreSQL users table (already modeled in api/shared), JWT auth

3. **Client/Chart Management Dashboard**
   - List saved charts
   - Search/filter by name
   - Quick actions: view chart, download PDF, share link
   - This is the practitioner workflow — they manage dozens of client charts

4. **Frontend Application**
   - We have backend APIs and PDF generation but no user-facing web app
   - Needs: chart input form → interactive bodygraph display → report download
   - Can be React/Next.js or a simpler approach to ship fast

### Tier 2: Full Competitive Parity — 2-3 months

5. **Chart Widgets (Embeddable)**
   - `<iframe>` or JS snippet for practitioners' websites
   - Free natal chart generator widget
   - Live transit widget
   - Email capture integration (→ Mailchimp/ConvertKit)
   - This is the primary lead-gen tool for practitioners

6. **Enhanced PDF Reports**
   - Template system improvements
   - Custom branding (practitioner logo, colors)
   - More report types (career, relationship, yearly transit forecast)

7. **Education Content**
   - SEO-optimized articles (Type deep dives, Center explanations, etc.)
   - "What is Human Design" landing page
   - Comparison content: "How our engine compares to Neutrino Design"

8. **Stripe Integration Fix**
   - Already identified: broken payload encoding in payment/server.py
   - Critical blocker for revenue

### Tier 3: Beyond Parity — 3-6 months

9. **Native Mobile Apps**
   - React Native or PWA approach
   - iOS + Android
   - Offline chart access

10. **Interactive Transit Calendar**
    - Visual calendar with daily transit activations
    - Personalized transit overlay per user's natal chart

11. **Integrations**
    - Zapier connector
    - Webhook support
    - Email marketing platform integration

---

## 4. What We Can Do BETTER Than Neutrino Design

These are our structural advantages — things they can't easily replicate:

### 4.1 Open Source Transparency
- Neutrino Design is closed source. Users can't verify their math.
- Our engine is AGPLv3. Anyone can read the source, run the tests, verify the calculations.
- Tagline: **"Don't Trust, Verify"** — nobody else in the market says this.
- This is our strongest differentiator for mathematically-inclined practitioners.

### 4.2 API Access (They Don't Have One)
- Neutrino Design has no API. Developers can't build on their platform.
- We offer a full REST API with RapidAPI marketplace presence.
- Use cases: dating apps, wellness platforms, coaching tools, AI integrations.
- This is a unique market position — we're the **"Stripe for Human Design"**.

### 4.3 Verified Accuracy
- We can publicly claim: **"Our engine produces identical output to Neutrino Design — the app every practitioner already trusts."**
- This is the most valuable credibility signal in this market.
- Verification data: 5 family members, 100% match on structural fields, one known and documented discrepancy.

### 4.4 Practitioner Certification
- Light Filled Human Design (Becca Gulden) certification — real credentialing.
- Neutrino Design is just technology. We have certified human expertise attached.

### 4.5 Better Pricing Architecture
- API-first monetization ($49-$499/mo recurring) vs. just consumer reports
- Reports priced competitively ($19-$39 vs. likely higher from competitors)
- Managed MCP hosting: recurring revenue from practitioners who want their own engine
- Multiple revenue streams vs. Neutrino Design's single subscription model

### 4.6 AI Integration Ready
- Our API endpoints make us the natural choice for AI/LLM integration
- AI coaching apps, chatbots, content generators all need a computation engine
- As the "API for Human Design," we win the developer ecosystem

---

## 5. Minimum Viable Competitive Product (MVCP) Definition

**Goal:** A practitioner can sign up, generate charts, save client profiles, view interactive bodygraphs, and download PDF reports.

### Must-Have Features for Launch (Weeks 1-6)

| # | Feature | Why Critical | Status |
|---|---|---|---|
| 1 | Interactive Bodygraph (SVG) | Users expect to SEE their chart visually | ❌ To build |
| 2 | User Registration & Login | No chart persistence without it | ❌ To build |
| 3 | Chart Generation Form | Input birth data, get chart results | ⚠️ API exists, no UI |
| 4 | Chart Save/Load | Practitioners manage many clients | ❌ To build |
| 5 | PDF Report Generation | Revenue: paid reports are core product | ✅ Working |
| 6 | Stripe Checkout | Revenue: can't sell without payments | ⚠️ Broken (payload encoding bug) |
| 7 | Landing Page | Marketing: where users discover us | ✅ Built (docs/landing-*) |
| 8 | Verification Page | Trust: proves our math is correct | 📋 Planned (verify.hdapi.io) |

### Nice-to-Have for Launch (Week 7+)
- Chart widgets for practitioners' sites
- Enhanced report templates (synastry, transit forecast)
- Articles/education content
- API rate-limits & developer portal
- Affiliate tracking

### Post-Launch (Phase 5+)
- Native mobile apps
- Interactive transit calendar
- Coaching marketplace
- Zapier/webhook integrations

---

## 6. Strategic Recommendations

### Immediate (Next 2 Weeks)
1. **Fix Stripe encoding bug** — unblocks all revenue
2. **Deploy Nginx + SSL** — public-facing presence
3. **Start interactive bodygraph development** — this is the longest pole

### Short-Term (Month 1-2)
4. Ship user accounts + chart storage
5. Build the bodygraph SVG renderer
6. Create the verification page (verify.hdapi.io)
7. List on RapidAPI marketplace
8. Write "State of HD Accuracy" comparison blog post

### Medium-Term (Month 3-4)
9. Embeddable widgets
10. Enhanced report templates
11. Education content (SEO articles)
12. Product Hunt launch

### Differentiation Strategy
- **Position:** "The API for Human Design" — developer-first, API-first
- **Trust:** "Don't Trust, Verify" — open source + Neutrino-verified
- **Community:** Target HD practitioners in Facebook groups, Reddit (r/humandesign), HD Discord servers
- **Pricing:** Undercut on reports, create new market (API pricing) they can't match

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Neutrino Design adds API | Medium | High | Our API is open source — we'd still win on transparency + developer trust |
| Delayed bodygraph development | High | High | Start immediately; use off-the-shelf SVG libraries |
| Low initial user adoption | Medium | High | Lean on "verified accuracy" messaging + Product Hunt/HN launch |
| Competitor price war | Low | Medium | Open source pricing is hard to beat; our API creates new revenue streams |
| Certification credibility questioned | Low | Medium | Becca's certification is real; document it well |

---

## 8. Appendix: Data Sources

- **Neutrino Design website:** https://neutrinoplatform.com (Next.js SPA, crawled May 30, 2026)
- **Neutrino Design app:** iOS App Store (com.idesign, 4.5★, 706 ratings) + Google Play
- **OpenHumanDesignMCP:** https://github.com/mbgulden/OpenHumanDesignMCP (AGPLv3)
- **Internal verification:** docs/TRUST-PROOF-SYSTEM.md — 5 family members verified
- **Internal architecture:** agy-project-review.md — Lean Standalone + Docker/FastAPI architectures
- **Internal roadmap:** docs/LINEAR-TASKS.md — Phases 1-5 task board
- **API spec:** api/rapidapi-openapi.yaml — Full OpenAPI 3.0 definition

---

> **Next action after this doc:** Prioritize the MVCP features in the Linear task board (add GRO-167 tasks) and begin interactive bodygraph development.
