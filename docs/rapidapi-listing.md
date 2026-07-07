# RapidAPI Marketplace Listing — Human Design Engine API

> **Status:** Draft — assets prepared, not yet submitted to RapidAPI  
> **Jira:** GRO-96  
> **Date:** 2026-05-29

---

## 1. Listing Title

**Primary (SEO-optimized):**

> Human Design Chart API — Natal Charts, Transits & Synastry

**Alternative candidates:**

- Human Design API — Compute Accurate Birth Charts & Relationship Synastry
- Human Design Engine API — Natal, Transit & Compatibility Charts
- Human Design Chart Calculator API — Birth Charts, Transits, Relationship Synastry

**Recommendation:** Use the primary title. It front-loads the keyword "Human Design Chart API" and lists the three core capabilities (natal, transits, synastry) which match what developers search for.

---

## 2. Listing Description (SEO-Optimized)

```
Accurate Human Design API for computing natal (birth) charts, daily transit
overlays, and relationship synastry. Built on Swiss Ephemeris with accuracy
verified against Neutrino Design and Genetic Matrix — the same open-source
calculation engine used by humandesignengine.com.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔮 WHY HUMAN DESIGN ENGINE?

• Verified accuracy — calculations validated against Neutrino Design and
  Genetic Matrix, not approximate or simplified math
• Complete charts — type, strategy, authority, profile, incarnation cross,
  centers, channels, gates, variables, signature, and not-self theme
• Daily transits — see how current planetary positions condition any birth chart
• Relationship synastry — electromagnetic channels, compromise gates,
  composite channels, and relationship dynamics between two people
• Open-source engine (AGPLv3) — full transparency, no black-box calculations
• Built by Human Design practitioners, not just developers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 API ENDPOINTS

POST /natal — Full natal (birth) chart computation
POST /transits — Transit overlay for any date (past, present, future)
POST /synastry — Relationship composite between two birth charts
POST /public/compute-chart — Simplified chart (no auth, rate-limited)
GET /ping — Health check and version info

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 USE CASES

• Astrology & spirituality mobile/web apps
• Wellness and self-discovery platforms
• Dating app compatibility features
• Coaching and personal development dashboards
• Human Design education and course platforms
• Chatbot and AI agent integrations
• Widget embeds for websites and blogs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 AUTHENTICATION

Pass your RapidAPI key in the X-API-Key header. Sign up for a dedicated
dashboard key at https://humandesignengine.com/landing-api.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ RESPONSE FORMAT

All endpoints return clean JSON. A typical natal chart response includes:

{
  "success": true,
  "data": {
    "name": "Jane Doe",
    "hd_type": "Projector",
    "profile": "6/2",
    "authority": "Self-Projected",
    "strategy": "Wait for the Invitation",
    "definition": "Single",
    "incarnation_cross": { "name": "Left Angle Cross of...", "gates": {...} },
    "defined_centers": ["Ajna", "G", "Throat"],
    "undefined_centers": ["Root", "Sacral", "Solar Plexus", ...],
    "defined_channels": [...],
    "signature": "Success",
    "not_self_theme": "Bitterness",
    "variables": ["Cold Thirst", "Mountains Active", ...]
  }
}
```
```

---

## 3. Pricing Tiers

Configured in RapidAPI dashboard (not in the OpenAPI spec itself).

| Tier | Calls / Month | Price / Month | Overage | Description |
|------|--------------|---------------|---------|-------------|
| **Free** | 100 | $0 | Hard cap | Test the API, build demos, prototype integrations |
| **Pro** | 1,000 | $49 | Hard cap | Solo developers and small apps in production |
| **Enterprise** | Unlimited | $499 | N/A | High-volume platforms, dedicated infra available |

**RapidAPI commission:** 20% of revenue. Target audience: 30M+ developers on the platform.

**Note:** These prices are for RapidAPI marketplace. Direct API pricing (via humandesignengine.com) may differ.

---

## 4. Category

**Primary recommendation:** `Astrology / Spirituality`

RapidAPI's browse categories. "Astrology" and "Spirituality" are adjacent but distinct — pick whichever is available and closest to Human Design. If neither exists:

**Secondary recommendation:** `Data` → `Data as a Service`

**Fallback:** `Science` or `Health & Wellness`

**Discovery keywords** (these don't go in category but help ranking):
- human design, birth chart, natal chart, bodygraph, astrology, transit, synastry, compatibility, personality type, gene keys

---

## 5. Tags

```
Human Design, Astrology, Natal Chart, Birth Chart, Bodygraph, Transit,
Synastry, Compatibility, Spirituality, Wellness, Personality, Gene Keys,
Self-Discovery, Coaching, Dating
```

**Tag selection priority (RapidAPI allows ~8-12 tags):**

1. Human Design
2. Astrology
3. Natal Chart
4. Birth Chart
5. Transit
6. Synastry
7. Compatibility
8. Spirituality
9. Wellness
10. Personality

---

## 6. Screenshot Instructions

RapidAPI requires 1-5 screenshots (1280x720 or 1920x1080, PNG or JPG).

### Screenshot 1 — API Endpoint Demo (REQUIRED)
**Content:** Show the `/natal` endpoint being called from RapidAPI's test console with a successful JSON response visible. Include the request body fields (name, year, month, day, hour, lat, lon, timezone) and a portion of the response showing `hd_type`, `strategy`, `authority`, `defined_centers`.

**How to capture:**
1. Go to RapidAPI dashboard after listing is created (or use a local Swagger UI)
2. Open the `/natal` endpoint
3. Fill in example birth data
4. Click "Test Endpoint"
5. Screenshot the result showing both request and response

### Screenshot 2 — Chart Types Summary
**Content:** A visual showing the five Human Design types (Manifestor, Generator, Manifesting Generator, Projector, Reflector) with brief descriptions. Alternatively, a diagram showing the bodygraph with defined/undefined centers.

**How to capture:**
- Create a simple graphic in Canva/Figma showing the five types with their strategies
- Or use a bodygraph illustration from humandesignengine.com (with permission)

### Screenshot 3 — Use Case Example
**Content:** Mockup of a mobile app or dashboard consuming the API — showing a person's chart summary on screen.

**How to capture:**
- Use a device mockup template (e.g., https://shots.so or similar)
- Place a sample chart output in a clean UI layout

### Screenshot 4 — Synastry/Compatibility
**Content:** Show the synastry endpoint response or a visual representation of relationship compatibility data.

### Screenshot 5 — Logo/Branding (optional)
**Content:** Human Design Engine logo on a clean background.

---

## 7. OpenAPI Spec

The RapidAPI-optimized OpenAPI 3.0 spec is at:

```
api/rapidapi-openapi.yaml
```

**Key differences from the internal `api/openapi.yaml`:**

| Aspect | Internal | RapidAPI |
|--------|----------|----------|
| Servers | Production + localhost | Production only |
| `x-logo` | Not present | Added with logo URL |
| Description | Technical focus | Marketplace/SEO focus with use cases |
| Pricing | Mentioned inline | Listed in description for discoverability |
| Auth description | "from dashboard" | "RapidAPI key or dashboard key" |

The spec is self-contained and ready for import into RapidAPI's API listing flow.

---

## 8. Submission Checklist

- [x] OpenAPI spec validated (3.0.3, all required fields present)
- [x] RapidAPI-optimized spec created at `api/rapidapi-openapi.yaml`
- [x] Listing title prepared (SEO-optimized with keywords)
- [x] Listing description written (features, use cases, example response)
- [x] Pricing tiers defined (Free/Pro/Enterprise)
- [x] Category selected (Astrology / Spirituality)
- [x] Tags selected (10 high-relevance terms)
- [x] Screenshot plan documented
- [ ] Logo uploaded to RapidAPI (use https://humandesignengine.com/logo.png)
- [ ] Screenshots captured and uploaded
- [ ] API key provisioning integrated with RapidAPI billing
- [ ] Terms of service URL prepared
- [ ] Privacy policy URL prepared

---

## 9. Post-Submission Notes

- **RapidAPI takes 20% commission** — factor this into pricing
- **30M+ developers** on RapidAPI, significant exposure potential
- After listing goes live, add the RapidAPI proxy URL to the server list in `api/openapi.yaml`
- Monitor RapidAPI analytics for endpoint usage patterns
- Consider adding a RapidAPI-specific onboarding flow at `https://humandesignengine.com/rapidapi`

---

## 10. Contact & Links

- **API Homepage:** https://humandesignengine.com
- **API Signup:** https://humandesignengine.com/landing-api.html
- **Support Email:** api@humandesignengine.com
- **OpenAPI Spec (canonical):** `api/openapi.yaml`
- **OpenAPI Spec (RapidAPI):** `api/rapidapi-openapi.yaml`
- **License:** AGPLv3 — https://www.gnu.org/licenses/agpl-3.0.html
