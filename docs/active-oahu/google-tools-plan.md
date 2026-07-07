# Google Tools Integration Plan — Active Oahu Media Library

**Ticket:** GRO-128  
**Date:** May 29, 2026  
**Author:** Hermes Agent (research & planning)  
**Status:** Draft — pending review

---

## Executive Summary

Active Oahu Tours has a massive media library (9,592 files, ~698 GB) of drone footage, GoPro underwater content, kayaking tours, and Oahu scenic photography. Google's creative AI tools can dramatically accelerate content production, SEO optimization, and social media output. This plan evaluates three Google AI tools for integration, provides cost estimates, and recommends an implementation order.

**Key Finding:** The three tools requested are:
1. **Google Flow** (called "Flow Studio" in the ticket) — AI filmmaking web app (no API)
2. **Gemini API + Omni capabilities** — multimodal analysis (auto-caption, alt text, video understanding)
3. **Veo 3.1** — AI video generation from photos/text (API available)

**Critical Note:** No Gemini API key exists yet. One must be created at [Google AI Studio](https://aistudio.google.com).

---

## 1. Media Library Context

| Metric | Value |
|---|---|
| Total files | 9,592 |
| Photos | 8,425 |
| Videos | 1,167 |
| Total size | 698.50 GB |
| Source | Synology NAS, Dropbox Team Space |
| Mount path | `/home/ubuntu/mounts/synology-photo/Dropbox Team Space` |

### Key Asset Categories

| Content Type | Examples | AI Opportunity |
|---|---|---|
| **Drone footage** | Kaneohe Bay (June 2022), 28 videos + 209 aerial photos | Veo3 transitions, auto-captioning |
| **Kayaking tours** | KBay kayaking, snorkeling, paddle-throughs | Gemini Omni scene analysis |
| **Underwater GoPro** | KBay underwater raw photos (102 images) | Auto alt-text, color grading suggestions |
| **Scenic/landmark** | Chinaman's Hat, Mokoliʻi, Kualoa backdrop | Promo clip generation from stills |
| **Tour photos** | 7,321 photos in main library | Batch SEO captioning |

---

## 2. Tool Analysis

### 2.1 Google Flow (formerly "Flow Studio")

**What it is:** An AI filmmaking web application by Google Labs that uses Veo (DeepMind's video model) to generate cinematic clips and scenes. It's a **creative studio for humans**, not an API.

**URL:** [flow.google](https://flow.google) (redirects to labs.google/fx/tools/flow)  
**Tagline:** "An AI creative studio built with and for creatives"

**Capabilities for Active Oahu:**
- Generate cinematic b-roll from text descriptions of Oahu scenery
- Create transitions between drone clips using AI
- Experiment with "what if" scenes (e.g., kayaking at sunset we didn't capture)
- Style-transfer existing footage with cinematic looks
- Generate short-form social clips for Instagram Reels / YouTube Shorts

**Integration Path:**
- **No API exists.** Flow is a web-based creative tool only.
- Workflow: Manually upload clips/images → generate AI clips → download results → import into your editing workflow.
- Not suitable for batch/automated processing.

**Pricing:**
- Part of Google Labs — currently free (experimental)
- Likely requires Google account
- Generated content may have watermarks or usage limits

**Limitations for our use case:**
- ❌ No programmatic API
- ❌ Cannot batch process 9,592 files
- ❌ Manual upload/download workflow
- ✅ Great for creating a few hero promo clips
- ✅ Free to experiment

---

### 2.2 Gemini API + Omni Capabilities (Multimodal Analysis)

**What it is:** Google's multimodal AI models (Gemini 2.5 Flash, Gemini 3.5 Flash) available via REST API. The "Gemini Omni" brand represents the convergence of reasoning + multimodal creation, but the practical integration uses the standard Gemini API models with vision and video understanding.

**API Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`  
**Docs:** [ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)

**Key Models for Our Use Case:**

| Model | Best For | Max Input |
|---|---|---|
| `gemini-2.5-flash` | Image captioning, alt text, photo analysis | 1M tokens |
| `gemini-2.5-pro` | Complex video analysis, scene breakdown | 2M tokens |
| `gemini-3.5-flash` | Latest multimodal, best quality | 1M tokens |

**Capabilities for Active Oahu:**

1. **Auto-caption photos** — Pass images to Gemini, get descriptive captions
   - Input: drone photo of Kaneohe Bay
   - Output: "Aerial view of Kaneohe Bay with Mokulua Islands in the distance, turquoise water, kayakers visible near sandbar"

2. **Generate alt text for SEO** — Every image on activeoahutours.com needs descriptive alt text
   - Current SEO audit shows missing alt text on key pages
   - Gemini can batch-generate SEO-optimized alt text

3. **Analyze video content** — Process video frames, identify scenes, objects, activities
   - Input: 2-minute drone video
   - Output: Scene breakdown, timestamps of key moments, activity tags

4. **Transcribe and caption videos** — For YouTube/social video content
   - Audio track → text transcription
   - Scene descriptions for accessibility

5. **Content categorization** — Analyze all 8,425 photos, tag by activity, location, quality

**Integration Path:**
- ✅ Full REST API available
- ✅ Python SDK: `google-genai` package
- ✅ Authentication: API key or OAuth
- ✅ Can process images inline (base64 or URL)
- ✅ Videos via file upload to File API, then referenced in prompt

**Sample Code (Python):**

```python
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")

# Photo captioning
model = genai.GenerativeModel("gemini-2.5-flash")
photo = genai.upload_file("drone_kaneohe_bay.jpg")
response = model.generate_content([
    "Describe this photo for use as alt text on a kayak tour website. "
    "Include location, activity, and scenic elements. Keep under 125 chars.",
    photo
])
print(response.text)

# Video analysis
video = genai.upload_file("kayak_tour.mp4")
response = model.generate_content([
    "Analyze this video. List: 1) Key scenes with timestamps, "
    "2) Activities shown, 3) Best frames for thumbnail, "
    "4) Suggested Instagram caption",
    video
])
```

**Pricing (Gemini API, May 2026):**

| Tier | Gemini 2.5 Flash | Gemini 2.5 Pro |
|---|---|---|
| Free tier | 1,500 requests/day | 50 requests/day |
| Pay-as-you-go (input) | $0.15 / 1M tokens | $1.25 / 1M tokens |
| Pay-as-you-go (output) | $0.60 / 1M tokens | $5.00 / 1M tokens |
| Image input | ~258 tokens per image | ~258 tokens per image |
| Video input | ~258 tokens/sec | ~258 tokens/sec |

**Estimated cost for full library processing:**

| Task | Volume | Est. Tokens | Est. Cost (Flash) |
|---|---|---|---|
| Caption all photos | 8,425 images × ~500 output tokens | ~4.2M output | **~$2.52** |
| Alt text generation | 8,425 images × ~125 chars output | ~2.1M output | **~$1.26** |
| Video scene analysis | 1,167 videos × 60s avg × ~258 tok/s | ~18M input + ~2M output | **~$3.90** |
| **Total estimated** | | | **~$7.68** |

> 💡 **Very cost-effective.** The free tier alone can handle a significant portion of initial processing.

---

### 2.3 Veo 3.1 (AI Video Generation)

**What it is:** Google DeepMind's leading video generation model. Generates high-quality video clips from text prompts, images, or a combination. Available via the Gemini API.

**API Models:**
| Model ID | Status | Best For |
|---|---|---|
| `veo-3.1-generate-preview` | Preview | Highest quality, newest features |
| `veo-3.1-lite-generate-preview` | Preview | Faster generation, lower cost |
| `veo-2.0-generate-001` | Stable | Production use, predictable output |

**Docs:** [ai.google.dev/gemini-api/docs/video](https://ai.google.dev/gemini-api/docs/video)

**Capabilities for Active Oahu:**

1. **Generate promo clips from still photos** — Turn our best drone stills into short animated promo videos
   - Input: Drone photo of Mokulua Islands
   - Output: 5-8 second clip with subtle camera movement (pan, zoom, parallax)

2. **Create "day to sunset" transitions** — Generate atmospheric transitions between tour segments
   - Input: Morning kayak photo
   - Prompt: "Golden hour light transitioning over the same scene, cinematic"

3. **Generate weather variations** — Show tours in ideal conditions from any photo
   - Useful for marketing materials showing "perfect day" conditions

4. **Social media short-form content** — Generate Instagram Reels / YouTube Shorts directly
   - Veo is integrated with YouTube Shorts

5. **Animate static logo/brand elements** — Subtle motion for website hero sections

**Integration Path:**
- ✅ REST API via Gemini API
- 🔒 **Requires paid tier** (Veo is not available on free tier)
- 🔒 May require allowlist / access approval for preview models
- Input: Image (base64) + text prompt describing desired motion
- Output: Video file (MP4), typically 4-8 seconds

**Sample Code (Python):**

```python
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")

# Generate video from still photo
model = genai.GenerativeModel("veo-3.1-lite-generate-preview")
photo = genai.upload_file("chinamans_hat_sunset.jpg")

response = model.generate_content([
    "Create a 6-second cinematic promo clip. "
    "Slow drone-like parallax movement across the scene. "
    "Warm sunset lighting. Text overlay zone on right third.",
    photo
])

# Response contains generated video
# Save the output video
with open("promo_chinamans_hat.mp4", "wb") as f:
    f.write(response.generated_video)
```

**Pricing (Veo via Gemini API, May 2026):**

| Model | Generation Cost | Typical Clip |
|---|---|---|
| Veo 3.1 Generate | ~$0.50–$1.00 / second | 4–8 seconds |
| Veo 3.1 Lite Generate | ~$0.25–$0.50 / second | 4–8 seconds |
| Veo 2.0 Generate | ~$0.35–$0.70 / second | 4–8 seconds |

> ⚠️ **Note:** Veo pricing is approximate. Google doesn't publish exact Veo API pricing publicly; these are estimates based on known compute costs and Vertex AI pricing patterns. Plan for $30–$100/month for regular social media clip generation.

**Estimated monthly cost for Active Oahu:**

| Use Case | Clips/Month | Seconds/Clip | Cost (Lite) |
|---|---|---|---|
| Instagram Reels | 20 | 6s each | ~$30–$60 |
| YouTube Shorts | 10 | 8s each | ~$20–$40 |
| Website promos | 5 | 6s each | ~$7.50–$15 |
| Ad creative | 10 | 5s each | ~$12.50–$25 |
| **Monthly total** | **45 clips** | | **~$70–$140/month** |

---

## 3. API Availability & Authentication

### 3.1 Current State

| Key | Status |
|---|---|
| `GEMINI_API_KEY` | ❌ **Not found** — No key in `~/.hermes/.env` |
| `GOOGLE_API_KEY` | ❌ **Not found** |
| `GOOGLE_DRIVE_CLIENT_SECRET` | ✅ Present (Drive/Workspace OAuth, not AI) |
| Google account | ✅ `mbgulden@gmail.com` |

### 3.2 How to Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Sign in with `mbgulden@gmail.com`
3. Click "Get API Key" → Create API key
4. Store in `~/.hermes/.env`:
   ```bash
   GEMINI_API_KEY=AIza...your-key-here
   ```

### 3.3 API Access Details

| Aspect | Detail |
|---|---|
| Base URL | `https://generativelanguage.googleapis.com/v1beta/` |
| Auth header | `x-goog-api-key: AIza...` or `?key=AIza...` |
| Python SDK | `pip install google-genai` |
| Rate limits (free) | 1,500 req/day (Flash), 50 req/day (Pro) |
| Rate limits (paid) | 2,000 req/min (Flash), 1,000 req/min (Pro) |
| File upload size | Up to 2 GB per file |
| Supported formats | Images: JPEG, PNG, WEBP, GIF; Video: MP4, MOV, AVI, MKV |

---

## 4. Implementation Priority & Roadmap

### Priority 1: Gemini Multimodal Analysis (Week 1–2)

**Why first:** Zero cost to start, immediate SEO value, builds foundational metadata.

**Tasks:**
1. ✅ Create Gemini API key at aistudio.google.com
2. ✅ Install Python SDK: `pip install google-genai`
3. Build batch photo captioning script for the media library
4. Generate alt text for all 8,425 photos
5. Analyze top 50 videos for scene/activity metadata
6. Export metadata JSON for WordPress integration
7. Update WordPress media library with AI-generated alt text

**Effort:** ~3–5 days  
**Cost:** $0–$8 (mostly free tier)  
**Quick wins:** Alt text on activeoahutours.com product pages, better image SEO

---

### Priority 2: Veo3 Promo Clip Generation (Week 3–4)

**Why second:** Higher cost, requires paid tier, but high marketing value.

**Tasks:**
1. Upgrade to paid Gemini API tier
2. Curate 50 best drone/tour photos for Veo generation
3. Create prompt templates for different clip types:
   - Cinematic drone flyover
   - Kayak action montage
   - Sunset transition
   - Logo animation
4. Generate initial batch of 45 clips (one month supply)
5. A/B test Veo 3.1 Lite vs Veo 2.0 for quality/cost
6. Integrate generated clips into social media calendar
7. Create video templates/storyboards document

**Effort:** ~5–7 days  
**Cost:** ~$70–$140/month  
**Quick wins:** Instagram Reels content, website hero video, YouTube Shorts

---

### Priority 3: Google Flow Creative Experiments (Ongoing)

**Why third:** No API, manual tool, best for one-off premium content.

**Tasks:**
1. Set up Google Flow access (Google account)
2. Experiment with drone footage → cinematic sequences
3. Create 3–5 hero promotional videos using Flow + Veo
4. Document workflow: Export media → Flow → Edit → Publish
5. Compare Flow quality vs direct Veo API generation

**Effort:** Ongoing (1–2 days per video)  
**Cost:** Free (experimental)  
**Quick wins:** Premium YouTube channel trailer, homepage hero video

---

## 5. What Stays Original vs AI-Augmented

| Content Type | Original | AI-Augmented |
|---|---|---|
| **Tour photos** | Original raw photos preserved | AI-generated alt text + captions added as metadata |
| **Drone footage** | Original 4K video preserved | AI-generated scene descriptions, timestamps |
| **Promotional video** | — | AI-generated from still photos (clearly labeled) |
| **Social clips** | — | AI-generated with Veo, human-reviewed before posting |
| **Website images** | Original photos | AI alt text for SEO; original photos unchanged |
| **Blog posts** | Human-written content | AI-suggested image pairings from library |
| **Thumbnails** | — | AI-generated from video keyframes |
| **Brand elements** | Original logo | AI-animated variants for video intros |

**Principle:** AI augments metadata and creates *new derivative content* from originals. Raw media files are never altered. AI-generated video content is always labeled as such.

---

## 6. Technical Architecture

### 6.1 Recommended Integration Flow

```
Media Library (Synology NAS)
    │
    ├──► Batch Processing Script
    │       │
    │       ├──► Gemini API (captioning, alt text, analysis)
    │       │       └──► Metadata DB / JSON export
    │       │
    │       └──► Veo API (promo clip generation)
    │               └──► /output/promo-clips/
    │
    ├──► WordPress Media Library Update
    │       └──► Alt text, captions, descriptions
    │
    └──► Social Media Pipeline
            └──► Instagram, YouTube, Facebook
```

### 6.2 Script Architecture

```
hd-platform/
└── scripts/
    └── active-oahu/
        ├── gemini_caption.py       # Batch photo captioning
        ├── gemini_alt_text.py      # SEO alt text generator
        ├── gemini_video_analyze.py # Video scene analysis
        ├── veo_promo_gen.py        # Promo clip from photos
        ├── flow_workflow.md        # Manual Google Flow guide
        └── config.py               # API keys, paths, prompts
```

### 6.3 Environment

```bash
# Required env vars (add to ~/.hermes/.env)
GEMINI_API_KEY=AIza...your-key-here

# Optional: if using Vertex AI instead of Gemini API
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

---

## 7. Cost Summary

| Tool | Setup Cost | Monthly Cost | Annual Estimate |
|---|---|---|---|
| **Gemini API (analysis)** | $0 | $0–$5 | $0–$60 |
| **Veo 3.1 (video gen)** | $0 | $70–$140 | $840–$1,680 |
| **Google Flow** | $0 | $0 | $0 |
| **Total** | **$0** | **$70–$145** | **$840–$1,740** |

**Cost-saving notes:**
- Use `gemini-2.5-flash` (cheapest) for bulk analysis
- Free tier covers ~1,500 images/day — process library over 6 days for $0
- Veo Lite is 50% cheaper than full Veo for social content
- Batch video analysis in off-peak hours when rate limits are more generous

---

## 8. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Veo API requires allowlist/approval | Medium | Apply early; fall back to Veo 2.0 (stable) which may be more accessible |
| Video generation quality inconsistent | Medium | Human review before publishing; maintain brand-appropriate prompt templates |
| Rate limits slow batch processing | Low | Spread processing over multiple days; use paid tier for burst processing |
| Generated alt text needs human review | High | Spot-check 10% of outputs; build review queue into script |
| API costs exceed estimates | Low | Set budget alerts; cap daily spend via API console |
| Google Flow deprecation/change | Medium | Don't build workflows that depend on Flow; treat as experimental |

---

## 9. Next Steps (Action Items)

1. **[ ] Create Gemini API Key** — Michael to create at aistudio.google.com using mbgulden@gmail.com
2. **[ ] Install SDK** — `pip install google-genai` on the Hermes host
3. **[ ] Store API key** — Add `GEMINI_API_KEY` to `~/.hermes/.env`
4. **[ ] Verify Veo access** — Check if Veo 3.1 preview is available for the account
5. **[ ] Build captioning script** — `scripts/active-oahu/gemini_caption.py`
6. **[ ] Process top 100 photos** — Validate quality before full library processing
7. **[ ] Review this plan** — Confirm priority order and budget approval

---

## Appendix A: Key URLs

| Resource | URL |
|---|---|
| Google AI Studio (get API key) | https://aistudio.google.com |
| Gemini API Docs | https://ai.google.dev/gemini-api/docs |
| Gemini API Pricing | https://ai.google.dev/gemini-api/docs/pricing |
| Veo API Docs (video generation) | https://ai.google.dev/gemini-api/docs/video |
| Video Understanding Docs | https://ai.google.dev/gemini-api/docs/video-understanding |
| Google DeepMind — Gemini Omni | https://deepmind.google/models/gemini-omni/ |
| Google DeepMind — Veo | https://deepmind.google/models/veo/ |
| Google Flow | https://flow.google |
| Python SDK (google-genai) | https://pypi.org/project/google-genai/ |

## Appendix B: Current API Key Status

```
GEMINI_API_KEY   ❌ NOT FOUND in ~/.hermes/.env
GOOGLE_API_KEY   ❌ NOT FOUND in ~/.hermes/.env
Gemini endpoint  ✅ Reachable (generativelanguage.googleapis.com responds)
Google account   ✅ mbgulden@gmail.com
Drive client     ✅ GOOGLE_DRIVE_CLIENT_SECRET present (not usable for AI APIs)
```

---

> **This plan is ready for review. Once the Gemini API key is provisioned, the Priority 1 scripts can be built and executed immediately.**
