# HD Engine — Value Ladder & Revenue Path

## The Funnel: Free → Pro → Practitioner

```
         FREE TOOLS (traffic magnets)
              │
              ▼
         EMAIL CAPTURE (bodygraph or report)
              │
              ▼
         PRO TRIAL (7-day free)
              │
              ▼
         PRO ($19/mo) ──→ PRACTITIONER ($49/mo)
```

---

## Free Value (Lead Generation)

These exist to get people ON the site and give them their email.

| # | Tool | Status | Purpose |
|---|------|--------|---------|
| 1 | Free natal chart computation | ✅ Live (/api/public) | "What's my type?" |
| 2 | **Interactive bodygraph** | 🔧 Building | Visual "wow" moment |
| 3 | Daily transit email | ✅ Cron at 7am MT | Habit-forming daily touch |
| 4 | Gate of the day social graphic | ✅ Built | Social sharing = viral growth |
| 5 | Embeddable widget | ✅ Built | Bloggers embed = backlinks |
| 6 | "What's Your Type?" quiz | 🔜 Planned | Interactive on-boarding |
| 7 | Gate/Gene Key lookup | 🔜 Planned | Reference tool (SEO magnet) |
| 8 | HD basics PDF guide | 🔜 Planned | Downloadable lead magnet |

**Email capture trigger:** After bodygraph renders → "Want to save this chart? Create a free account."

---

## Pro ($19/month — "Knowledge Seeker")

| # | Feature | Why They Pay |
|---|---------|-------------|
| 1 | **Unlimited saved charts** | Family, friends, curiosity |
| 2 | **Full interactive bodygraph** | No watermark, full resolution |
| 3 | Transit overlay on bodygraph | "What's happening right now?" |
| 4 | **PDF reports** (natal, transit, synastry) | Downloadable, shareable |
| 5 | Shareable bodygraph links | Send to friends |
| 6 | Dark mode | Aesthetic preference |
| 7 | Export as PNG/SVG | Use in presentations |
| 8 | Daily transit email (custom) | Personalized to your chart |

**Why $19/mo?** Neutrino Design charges $14.99 for basic. We add API access + bodygraph + better UX. The extra $4 is justified by interactivity.

---

## Practitioner ($49/month — "Professional Tool")

| # | Feature | Why They Pay |
|---|---------|-------------|
| 1 | Everything in Pro | Baseline |
| 2 | **Client profiles** (unlimited) | Run a practice |
| 3 | **Run reports for clients** | Natal, transit, synastry per client |
| 4 | Bulk transit reports | "January transits for all clients" |
| 5 | **White-label PDFs** | Your logo, your brand |
| 6 | Client notes and tags | CRM-lite |
| 7 | API access (1,000 calls/mo) | Build custom tools |
| 8 | Session scheduler notes | Track client sessions |
| 9 | Export client data | CSV export |
| 10 | Priority support | Practitioner community |

**Why $49/mo?** Neutrino's practitioner plan is ~$35-45. Our API access + white-label + bulk features command premium. Practitioners bill $100-300/session — $49/mo is one session's revenue.

---

## Enterprise API ($99-499/mo)

For developers building HD apps.

| Tier | Calls/Month | Price |
|------|-------------|-------|
| Free | 100 | $0 |
| Developer | 1,000 | $49 |
| Business | 10,000 | $199 |
| Enterprise | Unlimited | $499 |

Already defined in `api/rapidapi-openapi.yaml`.

---

## Revenue Projections

| Subscribers | Pro ($19) | Practitioner ($49) | API | Monthly |
|-------------|-----------|-------------------|-----|---------|
| 30 | 25 ($475) | 5 ($245) | 0 | **$720** |
| 100 | 80 ($1,520) | 20 ($980) | 2 ($100) | **$2,600** |
| 500 | 400 ($7,600) | 80 ($3,920) | 20 ($1,000) | **$12,520** |
| 1,000 | 800 ($15,200) | 150 ($7,350) | 50 ($2,500) | **$25,050** |

**Target mix:** 80% Pro, 15% Practitioner, 5% API

**On competitors:** The Human Design market has ~5,000-10,000 active practitioners globally. Even 2% penetration = 100-200 practitioner accounts.

---

## Launch Sequence

### Phase 1: Free Value (Week 1-2)
- ✅ Free natal chart → interactive bodygraph
- Email capture on bodygraph view
- Lead magnet: "Your HD Blueprint" PDF
- Social: gate of the day graphics

### Phase 2: Pro Tier (Week 3-4)
- User accounts + Stripe Checkout
- Saved charts dashboard
- Bodygraph without watermark
- Transit overlay
- PDF downloads

### Phase 3: Practitioner (Week 5-6)
- Client management
- Bulk operations
- White-label PDFs
- API access

### Phase 4: Growth (Week 7-8)
- API marketplace (RapidAPI)
- Affiliate program (30% commission)
- Product Hunt launch
- SEO content program

---

## Key Decisions

1. **Free bodygraph IS the top of funnel.** No paywall on basic computation.
2. **Email capture before save.** "Create free account to save" → low friction.
3. **7-day Pro trial.** Credit card required, cancel anytime.
4. **Annual discount:** $15/mo Pro ($180/yr) and $39/mo Practitioner ($468/yr). 20% off.
5. **Practitioner onboarding:** 1-on-1 call for accounts > $49/mo. High-touch converts.
