# HD Platform — Linear Task Board

> Equivalent to a Linear project board. Each section = a phase, each item = a task with priority, estimate, and dependencies.

## Phase 1: API (Weeks 1-2) 🔴 HIGH PRIORITY

### P1-1: Shared Foundation
- [ ] **P1-1.1** Initialize monorepo with Docker Compose stack (PostgreSQL, Redis, FastAPI, n8n) `[4h]`
- [ ] **P1-1.2** Database models: users, api_keys, subscriptions, api_usage_log `[3h]`
- [ ] **P1-1.3** Alembic migrations setup + initial migration `[2h]`
- [ ] **P1-1.4** Stripe integration: customer creation, subscription management, webhook handler `[4h]`
- [ ] **P1-1.5** API key generation + hashing + validation middleware `[3h]`
- [ ] **P1-1.6** Rate limiting with Redis (token bucket algorithm) `[3h]`

### P1-2: HD API Endpoints
- [ ] **P1-2.1** POST /v1/natal — compute natal chart `[3h]`
- [ ] **P1-2.2** POST /v1/transits — compute transit overlay `[2h]`
- [ ] **P1-2.3** POST /v1/synastry — compute relationship composite `[2h]`
- [ ] **P1-2.4** GET /v1/gate/{number} — gate lookup `[1h]`
- [ ] **P1-2.5** GET /v1/ping — health check with AGPLv3 notice `[1h]`
- [ ] **P1-2.6** Response caching (Redis) for identical chart requests `[2h]`

### P1-3: Developer Experience
- [ ] **P1-3.1** OpenAPI/Swagger docs auto-generated from FastAPI `[2h]`
- [ ] **P1-3.2** Developer portal page (simple HTML: signup, API key, docs link, pricing) `[3h]`
- [ ] **P1-3.3** Quickstart guides: Python, JavaScript, curl examples `[2h]`
- [ ] **P1-3.4** Usage dashboard (user sees their API call count) `[3h]`

### P1-4: Deployment
- [ ] **P1-4.1** Docker Compose production config with Traefik reverse proxy `[3h]`
- [ ] **P1-4.2** GitHub Actions CI: lint, test, build Docker image, deploy `[3h]`
- [ ] **P1-4.3** SSL certificates via Traefik + Let's Encrypt `[1h]`
- [ ] **P1-4.4** UptimeRobot monitoring + health check endpoint `[1h]`

**Phase 1 total: ~45 hours**

---

## Phase 2: Reports (Weeks 3-5) 🟡 MEDIUM PRIORITY

### P2-1: Report Engine
- [ ] **P2-1.1** Report template system (Jinja2 HTML templates with CSS for PDF) `[4h]`
- [ ] **P2-1.2** Natal chart report template — 4 sections, branded with "Light Filled HD" badge `[4h]`
- [ ] **P2-1.3** Synastry report template — electromagnetic, compromise, dominance `[3h]`
- [ ] **P2-1.4** Gemini prompt engineering for plain-English HD interpretations `[3h]`
- [ ] **P2-1.5** WeasyPrint PDF rendering pipeline `[2h]`

### P2-2: Purchase Flow
- [ ] **P2-2.1** Stripe Checkout product pages (Natal $19, Synastry $29, Bundle $39) `[2h]`
- [ ] **P2-2.2** Birth data collection form (fields: name, date, time, location) `[2h]`
- [ ] **P2-2.3** Stripe webhook → job queue → report generation pipeline `[3h]`
- [ ] **P2-2.4** Redis job queue for async report generation `[2h]`
- [ ] **P2-2.5** Email delivery with PDF attachment (Resend API) `[1h]`
- [ ] **P2-2.6** Download page with expiring link (24h) for purchased reports `[2h]`

### P2-3: Landing Page
- [ ] **P2-3.1** Product landing page: sample report preview, pricing, "Get Yours" CTA `[4h]`
- [ ] **P2-3.2** Sample chart display (synthetic data) showing report quality `[2h]`
- [ ] **P2-3.3** Testimonials section (placeholder → real as they come in) `[1h]`
- [ ] **P2-3.4** FAQ + trust signals (certification badge, accuracy claims, methodology link) `[1h]`

**Phase 2 total: ~38 hours**

---

## Phase 3: Managed MCP Hosting (Weeks 6-8) 🟢 LOWER PRIORITY

### P3-1: Provisioning Engine
- [ ] **P3-1.1** Docker container provisioning script (create container, assign port, start MCP server) `[3h]`
- [ ] **P3-1.2** Subdomain routing via Traefik (username.mcp.hdapi.io → container) `[2h]`
- [ ] **P3-1.3** Resource limits per container (CPU, memory caps) `[1h]`
- [ ] **P3-1.4** Container lifecycle management (start, stop, restart, delete on cancel) `[2h]`
- [ ] **P3-1.5** Ephemeris data volume sharing (all containers share one ephemeris mount — read only) `[1h]`

### P3-2: Subscription Flow
- [ ] **P3-2.1** Stripe subscription products ($29 Starter, $79 Pro, $199 Studio) `[1h]`
- [ ] **P3-2.2** Auto-provision on subscription creation webhook `[2h]`
- [ ] **P3-2.3** Auto-decommission on subscription cancellation `[1h]`
- [ ] **P3-2.4** Onboarding email with connection instructions + --print-config output `[1h]`
- [ ] **P3-2.5** Usage dashboard (charts/month, uptime) `[3h]`

### P3-3: Practitioner Tools
- [ ] **P3-3.1** Web dashboard to manage their MCP instance (restart, view logs, get config) `[4h]`
- [ ] **P3-3.2** Family profile management (upload family.json, compute charts for all members) `[3h]`
- [ ] **P3-3.3** White-label option: practitioner's own domain pointed to their instance `[2h]`

**Phase 3 total: ~26 hours**

---

## Phase 4: Trust & Proof System (Ongoing) 🔵 INFRASTRUCTURE

### P4-1: Public Verification
- [ ] **P4-1.1** `verify.hdapi.io` — public verification page `[3h]`
- [ ] **P4-1.2** Display engine accuracy metrics: "Our engine matches Neutrino Design on Type, Profile, Authority, Centers, Channels, and Variable arrows" `[1h]`
- [ ] **P4-1.3** Synthetic benchmark: compute 1,000+ charts, verify structural correctness `[2h]`
- [ ] **P4-1.4** Methodology whitepaper: link to OpenHumanDesignMCP, explain corrected math `[2h]`
- [ ] **P4-1.5** "Try it live" — public test endpoint that computes a synthetic chart instantly `[1h]`

### P4-2: Certification Badge
- [ ] **P4-2.1** "Powered by Light Filled Human Design" badge design (Becca's certification) `[1h]`
- [ ] **P4-2.2** Add badge to all report PDFs, API docs, and landing pages `[1h]`
- [ ] **P4-2.3** About page: Becca's story, her certification, why it matters `[2h]`
- [ ] **P4-2.4** "Advisor" credit on website + reports `[1h]`

### P4-3: Social Proof
- [ ] **P4-3.1** Public roadmap (GitHub Projects or simple markdown) showing what's built + what's next `[1h]`
- [ ] **P4-3.2** Changelog page: every update, every fix, every improvement `[1h]`
- [ ] **P4-3.3** "Used by" counter: number of charts computed, number of developers, number of reports delivered `[2h]`
- [ ] **P4-3.4** Open source transparency: link to OpenHumanDesignMCP repo, show AGPLv3 license `[0.5h]`

**Phase 4 total: ~19.5 hours**

---

## 🚀 Future: Coaching Platform (Phase 5+) 🟣 MOONSHOT

Only after Phases 1-4 are generating revenue. This is the high-touch product.

- [ ] **P5-1** Reader marketplace: certified practitioners list their services, clients book sessions
- [ ] **P5-2** Integrated video call + shared chart viewing (Zoom API or Jitsi)
- [ ] **P5-3** Session notes + follow-up report automation
- [ ] **P5-4** Client CRM: track client charts, session history, transit alerts
- [ ] **P5-5** "Light Filled Human Design" branded coaching tier (premium, Becca-led)
- [ ] **P5-6** Affiliate program: practitioners earn commission on report sales

---

## 📊 Priority Matrix

| Task Group | Impact | Effort | Priority | Phase |
|---|---|---|---|---|
| API Endpoints | 🔴 Critical | 11h | P0 | 1 |
| Developer Experience | 🔴 Critical | 10h | P0 | 1 |
| Deployment + CI | 🔴 Critical | 8h | P0 | 1 |
| Shared Foundation | 🔴 Critical | 19h | P0 | 1 |
| Report Engine | 🟡 High | 16h | P1 | 2 |
| Purchase Flow | 🟡 High | 12h | P1 | 2 |
| Landing Page | 🟡 High | 8h | P1 | 2 |
| Provisioning Engine | 🟢 Medium | 9h | P2 | 3 |
| Subscription Flow | 🟢 Medium | 8h | P2 | 3 |
| Practitioner Tools | 🟢 Medium | 9h | P2 | 3 |
| Public Verification | 🔵 Trust | 9h | P1 | 4 |
| Certification Badge | 🔵 Trust | 5h | P1 | 4 |
| Social Proof | 🔵 Trust | 4.5h | P2 | 4 |

---

## 🧠 ADHD Sprint Plan

### Sprint 1 (This Week): Ship the API
**Goal:** Someone can curl your API and get a chart back. Stripe charges them.

- [ ] Mon-Wed: P1-1 (Shared Foundation) + P1-2 (API Endpoints)
- [ ] Thu-Fri: P1-3 (Developer Experience) + P1-4 (Deployment)
- [ ] Saturday: Deploy to production server. Test with real Stripe checkout.
- [ ] Sunday: Share on Hacker News, Reddit, HD Facebook groups, Discord servers

### Sprint 2 (Next Week): Ship Reports
**Goal:** Someone pays $19, gets a PDF in their inbox within 5 minutes.

- [ ] Mon-Tue: P2-1 (Report Engine)
- [ ] Wed-Thu: P2-2 (Purchase Flow)
- [ ] Fri-Sat: P2-3 (Landing Page) + P4-1 (Public Verification)
- [ ] Sunday: Launch on Product Hunt, share with HD practitioner community

### Sprint 3 (Week 3+): Trust + Polish
**Goal:** The platform looks credible. People trust the accuracy. Revenue grows.

- [ ] P4-2 (Certification Badge) + P4-3 (Social Proof)
- [ ] Collect first testimonials from users
- [ ] Write "State of HD Accuracy" blog post comparing engine vs Neutrino Design

---

*Import this into Linear, or track here. Each checkbox = one task. Start from the top.*
