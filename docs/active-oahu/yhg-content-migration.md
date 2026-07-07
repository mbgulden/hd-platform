# Your Hawaii Guide — Content Migration Audit & Salvage Assessment

**Date**: 2026-05-29
**Task**: GRO-136
**Source**: yourhawaiiguide.com (WordPress on Flywheel)
**Target**: New YHG Astro site

---

## Executive Summary

The YHG WordPress site contains 26 blog posts (all **empty content**), 24 pages (mixed), 75 activity CPT entries, 34 company CPT entries, 39 categories, and 75 tags. Featured images survive for nearly all content. The blog is a total loss for body text but titles + slugs + image captions/sitemap data provide valuable SEO signals and topic scaffolding for reconstruction.

### Verdict by Content Type

| Content Type | Count | Status | Salvage Strategy |
|---|---|---|---|
| Blog Posts | 26 | ❌ Body empty | Reconstruct from titles + images; rewrite fresh |
| Pages (info) | 5 | ✅ Content intact | Migrate directly |
| Pages (templates) | 19 | ⚠️ Skeleton only | Rebuild in Astro |
| Activities (CPT) | 75 | ⚠️ Sitemap only | Use slugs/titles/images for listing rebuild |
| Companies (CPT) | 34 | ⚠️ Sitemap only | Use slugs/titles/images for directory |
| Categories | 39 | ✅ Intact | Port taxonomy; simplify |
| Tags | 75 | ✅ Intact | Consolidate; too granular |
| Images | ~200+ | ✅ Survive | Download and resizing pipeline |

---

## 1. Blog Posts — Complete Content Loss, Scaffolding Intact

### 1.1 What Survives

Every post has:
- **Title** (SEO-optimized, descriptive)
- **Slug** (URL path preserved)
- **Featured image** (with `srcset` and alt text from sitemap)
- **Publish date**
- **Category assignments** (useful for content mapping)
- **Tag assignments** (location/activity tags)

### 1.2 Complete Post Inventory

#### Food & Restaurants (2022 batch — likely Instagram-embed posts)
| ID | Title | Slug | Categories | Image Caption |
|---|---|---|---|---|
| 3156 | The pancakes are iconic | the-pancakes-are-iconic | restaurants, things-to-do | eggs n things breakfast oahu hawaii |
| 3123 | One of Waikiki's best kept secrets | one-waikikis-best-kept-secrets | eats, things-to-do | kulu kulu japanese bakery desserts cake oahu hawaii |
| 3111 | Some of the best ramen on Kalakaua | best-ramen-strip | restaurants, things-to-do | momosan waikiki oahu hawaii |
| 3074 | A Wednesday night at home | wednesday-night-home | eats, things-to-do | super pho waialae oahu hawaii honolulu takeout food |

#### Hiking & Adventures
| ID | Title | Slug | Categories | Image Caption |
|---|---|---|---|---|
| 1726 | 360 Degree View from the Lanikai Pillboxes Hike | lanikai-pillboxes-hike | adventures, blog, hike, hikes-adventures | ActiveOahu_Hailey_14 |
| 1856 | Hike through the Hauʻula Loop pine forest | hauula-loop-pine-forest | adventures | bridalberries |
| 1833 | Hike the mile to Makaua Falls | makaua-falls | adventures | Makaua3.hailey |
| 1723 | An intense and epic ridge hike near Kaʻaʻawa | an-intense-and-epic-ridge-hike | adventures | Mountain |
| 1923 | Rock climbing near Makapuʻu Lighthouse | rock-climbing-near-makapuu-lighthouse | adventures | Leiaclimbing.cropped.hailey |

#### Beaches & Coastal
| ID | Title | Slug | Categories | Image Caption |
|---|---|---|---|---|
| 1275 | Castle's Beach is One for Families and Beginner Surfers | castles-beach-for-beginner-surfers-families | adventures, beaches, things-to-do | Swing |
| 1289 | Hukilau Beach has smaller waves and grassy areas for yoga | hukilau-beach-smaller-waves-grassy-areas-yoga | adventures, beaches, blog, things-to-do | Hukilau beach2 |
| 1321 | Pounders throws waves for bodysurfing | pounders-throws-waves-for-bodysurfing | adventures, things-to-do | 1Pounders_bradley_panorama_HaileyMinton |
| 1360 | 3 low key beaches on the North Shore | 3-low-key-beaches-north-shore | adventures | Temple beach 8 |
| 1494 | The romantic and relaxing Kawela Bay | romantic-relaxing-kawela-bay | adventures | bon_19 |

#### Ocean & Water Sports
| ID | Title | Slug | Categories | Image Caption |
|---|---|---|---|---|
| 1762 | The Surreal Experience of Paddling Through a Rain Forest in Oahu | rainforest-kayak-experience-oahu | adventures | Oahu Kayak Tours_13 |
| 1368 | Jump on the Turtle Canyon Snorkel Tour and Sail | jump-on-the-makini-catamaran-turtle-tour | adventures | Makini Cat turtles |
| 2286 | Snorkeling with Wild Dolphins in Oahu | snorkeling-wild-dolphins-oahu | adventures, blog, diving-snorkeling | IMG_5670 |
| 2136 | Swim with Sharks in the Open Ocean | swim-with-sharks-in-the-open-with-shark-behavior-experts | blog, diving-snorkeling | Shark Dive |
| 2102 | Revel at the Beauty of Sharks from a Shark Cage | oahu-shark-cage-diving-revel-at-the-beauty-of-sharks | adventures | 916-053 |
| 1401 | Beginner surf lessons on an isolated beach | surf-hnl-teaches-beginner-surf-lessons-on-an-isolated-beach | adventures | IMG_1800 |
| 1638 | Longboard surfing at Kahana Bay | longboard-surfing-at-kahana-bay | adventures | Kahanabay |

#### Activities & Sights
| ID | Title | Slug | Categories | Image Caption |
|---|---|---|---|---|
| 1589 | Feel the thrill of sunset skydiving on Oahu | sunsetskydiving_oahu_north_shore | adventures | Untitled_000119_edited |
| 1820 | 6 things you don't want to miss at Kahana State Park | explore-the-kahana-bay-state-park | adventures | Oahu-Kayak-Tours_11_thumb |
| 1654 | Discover the Byodo-In Temple | discover-byodo-temple | adventures | Valley of the temples_HaileyMinton_RGB |
| 1689 | Energize yourself at the Hoʻomaluhia Gardens | visit-ho-omaluhia-botanical-gardens | adventures | Botanical Gardens |
| 725 | 4 Ways to Activate Your Adrenaline at Laie Point | activate-your-adrenaline-at-laie-point | blog | Laie Point_11 |

### 1.3 Salvage Strategy for Blog Posts

**Keep (rewrite fresh):** All 26 posts. The titles give clear direction. These map to high-value SEO topics:
- **Hiking**: Lanikai Pillboxes, Hauʻula Loop, Makaua Falls, Kaʻaʻawa Ridge
- **Beaches**: Hukilau, Pounders, Castle's, Kawela Bay, North Shore beaches
- **Water Activities**: Kayaking, snorkeling, shark diving, surfing, skydiving
- **Food**: Pancakes (Eggs 'n Things), Ramen (Momosan), Kulu Kulu Bakery, Super Pho
- **Sights**: Byodo-In Temple, Hoʻomaluhia Gardens, Laie Point

**Archive:** None — all titles are viable topics.

**Process for each:**
1. Check Wayback Machine for original content (unlikely to have full text but worth a try)
2. Rewrite fresh using title + image as guide
3. Use original slug (preserves any backlinks)
4. Preserve original publish date for historical context
5. Add proper meta descriptions (currently missing on all posts)

---

## 2. Pages — Mixed Salvage

### 2.1 Pages with Intact Content (Migrate)

| Page | Slug | Content Quality | Action |
|---|---|---|---|
| About | /about/ | **Rich** — company story, team, mission | Migrate directly, update dates |
| Adventure Log (Blog) | /blog/ | Intro text intact | Keep as blog index intro |
| Cancellation Policy | /cancellation-policy/ | Full policy text | Migrate, update if needed |
| Privacy Policy | /privacy-policy/ | Full policy text | Migrate directly |
| How to Cancel/Refund | /how-to-cancel-or-request-a-refund/ | Detailed guide with screenshots | Migrate, update screenshots |

### 2.2 Template Pages (Rebuild in Astro)

| Page | Slug | Notes |
|---|---|---|
| Home | / | Empty content, likely ACF-driven |
| Activity Listing | /activity-listing/ | Empty shell |
| Activity Map | /activity-map/ | Custom template, Google Maps |
| All Activities Map | /all-activities-map/ | Custom template |
| Company Map | /company-map/ | Custom template |
| Free Things To Do Map | /free-things-to-do-map/ | Custom template |
| Bucket List | /bucket-list/ | Favorites plugin, empty |
| Search | /search/ | Plugin-driven |
| Member Directory | /member-directory/ | Plugin-driven, has embedded users |
| My Profile | /my-profile/ | Plugin template |
| Log In, Sign Up, My Account | various | Membership plugin pages |
| Checkout, Order Confirmation, Order Failed | various | E-commerce plugin pages |

**Recommendation**: All template/membership/e-commerce pages should be **archived** (not migrated). The new Astro site won't use WordPress plugins or FareHarbor booking. Only migrate the 5 content-rich pages.

---

## 3. Activity Listings — Skeleton Data Only

### 3.1 What's Available from Sitemap

The 75 activity CPT entries are not exposed via REST API (`show_in_rest` is false). The XML sitemap reveals:
- **Slugs** (URL paths)
- **Last modified dates** (mostly April–July 2022, some Sept 2023)
- **Featured images** (URLs with alt captions)

### 3.2 Activity Categories (from slugs/captions)

**Surfing:**
- /activities/surfing-lessons/ — Laie surf lessons
- /activities/surf-hnl-surf-lessons/ — Surf HNL
- /activities/1hr-group-surfing-lessons-ala-moana/ — Ala Moana
- /activities/1hr-group-lessons-kapolei/ — Kapolei
- /activities/2hr-semi-private-group-lessons/ — Waikiki

**Snorkeling & Diving:**
- /activities/turtle-canyons-snorkel-excursion/ — Turtle Canyon
- /activities/turtle-reef-snorkel-sail/ — Turtle Reef
- /activities/turtles-snorkeling-lunch/ — Turtles + lunch cruise
- /activities/turtle-snorkel-adventure/ — Turtle snorkel
- /activities/hanauma-bay-snorkeling/ — Hanauma Bay
- /activities/beginner-advanced-scuba/ — Scuba diving
- /activities/shark-cage-diving/ — Shark cage
- /activities/shark-research-snorkel/ — Shark research snorkel
- /activities/dolphin-snorkel/ — Dolphin snorkel
- /activities/dolphin-tour-snorkel-cruise/ — Dolphin tour

**Kayaking:**
- /activities/chinamans-hat-oahu-kayak-tours/ — Chinaman's Hat
- /activities/rainforest-kayak-self-guided-tour/ — Rainforest kayak

**Catamaran / Boat Cruises:**
- /activities/waikiki-sunset-cruise/ — Sunset cruise
- /activities/sunset-cocktail-cruise/ — Cocktail cruise
- /activities/sunset-catamaran-cruise-waikiki/ — Catamaran sunset
- /activities/catamaran-cruise-snorkeling-tour/ — Catamaran + snorkel
- /activities/afternoon-sail-on-the-south-shore/ — Afternoon sail
- /activities/sunset-dinner-sail-on-the-south-shore/ — Dinner sail
- /activities/waikiki-swimnsail/ — Swim & sail
- /activities/sunset-sail/ — Sunset sail
- /activities/afternoon-adventure/ — Whale watching cruise
- /activities/morning-calm/ — Morning dolphin cruise
- /activities/oahu-snorkel-tour-sunset/ — Snorkel sunset
- /activities/oahu-daytime-tour/ — Glass bottom boat daytime
- /activities/sunset-cruise-honolulu/ — Glass bottom sunset

**SUP / Yoga:**
- /activities/haleiwa-paddleboarding/ — Haleiwa SUP
- /activities/sup-yoga-oahu/ — SUP yoga
- /activities/light-night-sup-yoga/ — Glow SUP yoga
- /activities/yoga-paddle-combo/ — Yoga + paddle
- /activities/family-yoga-paddle/ — Family SUP yoga
- /activities/sup-yoga-paddle-bliss/ — SUP yoga bliss
- /activities/learn-art-sup-oahu/ — Learn SUP
- /activities/sup-open-group-lesson/ — SUP group lesson
- /activities/sup-private-lesson/ — SUP private
- /activities/sunset-sup-session/ — Sunset SUP
- /activities/twilight-glow-paddle/ — Night glow paddle
- /activities/morning-waikiki-beach-front-yoga-session/ — Beach yoga

**Land Tours / Sightseeing:**
- /activities/private-island-tour/ — Private island tour
- /activities/north-shore-eats-waterfall-tour/ — North Shore eats + waterfall
- /activities/northshore-circle-island-adventure/ — Circle island
- /activities/hawaiis-original-private-island-tours-snorkeling/ — Private island + snorkel
- /activities/sights-bites-tour/ — Sights & bites
- /activities/north-shore-adventure-tour/ — North Shore adventure
- /activities/grand-circle-island-snorkeling/ — Grand circle island
- /activities/diamond-head-crater-shuttle-self-guided-hike/ — Diamond Head shuttle
- /activities/rainforest-waterfall-movie-sites-hike/ — Waterfall movie sites hike

**Specialty / Extreme:**
- /activities/complete-island-sunrise-photo-adventure/ — Photo tour
- /activities/beautiful-colors-hawaii-photo-tour/ — Photo tour
- /activities/hawaii-food-photo-tour/ — Food photo tour
- /activities/hawaii-sunset-tour-east-oahu/ — Sunset photo tour
- /activities/waikiki-e-scooter-private-tour/ — E-scooter tour
- /activities/historical-honolulu-tour/ — Hoverboarding tour
- /activities/magic-island-ala-moana-beach-park-ala-wai-canal-fort-derussy-beach/ — Hoverboarding Waikiki
- /activities/waikiki-hoverboarding-signature-wiki-tour/ — Hoverboarding
- /activities/waikiki-hoverboarding-signature-aloha-tour/ — Hoverboarding
- /activities/hawaiian-foodie-bike-tour/ — Foodie bike tour
- /activities/coast-mountain-loop/ — Slingshot coast loop
- /activities/north-shore-adventure/ — Slingshot North Shore
- /activities/off-beaten-path-hawaii-food-tour/ — Food tour
- /activities/da-locals-food-tour/ — Local food tour
- /activities/standard-class/ — Cooking class
- /activities/premium-class/ — Cooking class
- /activities/moana-celebrity/ — Luau celebrity
- /activities/moana-splash/ — Luau splash
- /activities/moana-classic/ — Luau classic
- /activities/jet-ski-in-waikiki/ — Jet ski
- /activities/fly-high-parasail/ — Parasailing
- /activities/flyboard-along-oahu-coast/ — Flyboard
- /activities/rent-beach-gear-equipment-rentals/ — Beach gear rentals

### 3.3 Salvage Strategy for Activities

**Keep as topics (not pages):** Activity slugs provide an excellent content brief for what tours/experiences to cover on the new site. However, individual activity detail pages with FareHarbor booking embeds should NOT be recreated.

**Content mapping:**
1. Group activities by category (Surf, Snorkel, Kayak, Cruise, SUP, Tours, Extreme)
2. Create **category hub pages** that cover all relevant tours
3. Use activity titles as **section headers** within hub pages
4. Featured images can be reused for hero banners and cards

---

## 4. Company Profiles — Directory Data Only

### 4.1 Company Inventory (34 from sitemap)

```
Active Oahu Tours          — Kayak tours, equipment rentals
Surf HNL                   — Surf lessons (multiple locations)
Aaron's Dive Shop          — Scuba diving
Hawaii Shark Encounters    — Shark cage diving
One Ocean Diving           — Shark research / free swimming
Aloha Hawaii Tours         — Island tours
Hawaii Ocean Charters      — Boat charters
Hawaii Turtle Tours        — Turtle snorkel tours
Kaimana Tours              — Hiking/waterfall tours
Yoga Floats                — SUP yoga
Port Waikiki Cruise        — Boat cruises
HI5 Tours                  — Adventure tours
Yoga Under the Palms       — Beach yoga
Living Ocean Tours         — Ocean tours
Ka Moana Luau              — Luau shows
Oahu Photography Tours     — Photo tours
Hawaii Hoverboarding Tours — Hoverboarding
Cloud9 Hawaii Tours        — Segway/e-scooter tours
Hawaiian Style Cooking Class — Cooking classes
Hawaii Free Tours          — Free walking tours
Island Paddle Bliss        — SUP yoga
Hawaii Glass Bottom Boat   — Glass bottom boat tours
Bike Tour Hawaii           — Bike tours
Ohana Surf Project         — Surf lessons
Dolphin Excursions         — Dolphin tours
Makani Catamaran           — Catamaran sails
Moana Sailing Company      — Catamaran sails
Mike's Surf School         — SUP/surf
Ocean Joy Cruises          — Whale watching / snorkel
And You Creations          — Dolphin/snorkel tours
X-Treme Watersports        — Parasail/jet ski
Jet Ski Oahu               — Jet ski rentals
Aloha Motorsports          — Slingshot rentals
```

### 4.2 Salvage Strategy for Companies

**Archived as-is.** The company directory is outdated (last updated 2022). For the new Astro site:
- Create a **"Tour Operators We Recommend"** page with curated, up-to-date listings
- Verify each company is still operating before including
- Link to company websites directly (no FareHarbor embeds)
- Retain company names + slugs for potential affiliate/referral content

---

## 5. Category & Tag Taxonomy

### 5.1 Categories (39 total)

**Well-structured categories:**
```
Adventures (27)           Blog (32)               Beaches (33)
Things to do (30)         Food (31)              Eats (120)
Restaurants (119)         Diving/Snorkeling (106) Hikes (99, 102, 103)
Surf Lessons (2)          Kayak Tours (7)        Standup Paddleboard (20)
Yoga & Wellness (24)      Catamaran Sail (107)    Sightseeing (108)
Extreme Sports (95)       Rentals (96, 98)       Equipment Rentals (98)
Cooking Class (112)       Food Tour (116)         Photo Tour (111)
Scooter Tour (114)        Adventure Tour (113)    Marine Life Viewing (115)
Vehicle Rental (117)      Shows & Attractions (118)
Snorkel & Scuba (1)       Hikes & Eco Tours (6)
Ocean/River (25)          Land/Trail (26)         Beach Gear (97)
SUP Yoga (109)            Gunstock Ranch (29)     Rainbow Watersports (28)
Active Oahu Tours (9)     Beach (104)
```

**Issues:**
- Duplicate hiking categories: 99 (Hikes), 102 (Hike), 103 (Hikes-Adventures), 6 (Hikes & Eco Tours)
- Beaches duplicated: 33 (Beaches), 104 (Beach), 105 (Beaches-Things-to-Do)
- Food categories overlap: 31 (Food), 120 (Eats), 119 (Restaurants)

### 5.2 Tags (75 total)

Tags are granular and location-specific (e.g., "beaches-near-hauula", "beaches-near-kahuku", "beaches-near-laie"). Most tags have only 1-2 posts.

### 5.3 Salvage Strategy for Taxonomy

**Categories — simplify to ~15:**
- Adventures & Tours
- Hiking & Nature
- Beaches & Coastline
- Surfing
- Kayaking & Paddleboarding
- Snorkeling & Diving
- Boat Cruises & Sailing
- Yoga & Wellness
- Food & Restaurants
- Cultural Experiences (Luau, temples)
- Photography Tours
- Extreme Sports
- Equipment Rentals
- Family Activities
- Free Things to Do

**Tags — archive all 75.** Replace with a cleaner system:
- Location tags: North Shore, East Oahu, Waikiki/Honolulu, Windward, Leeward
- Activity tags: Beginner-Friendly, Family-Friendly, Adrenaline, Relaxing, Romantic

---

## 6. Content Map: YHG WordPress → Astro Site

### 6.1 Proposed Astro Site Structure

```
/
├── index.astro                          (Homepage — rebuilt)
├── about.astro                          (Migrated from /about/)
├── blog/
│   ├── index.astro                      (Migrated intro from /blog/)
│   ├── [slug].astro                     (26 rebuilt posts)
│   └── category/[category].astro        (Category listing pages)
├── adventures/
│   ├── index.astro                      (Category hub — all tours/activities)
│   ├── hiking.astro                     (Hiking hub page)
│   ├── beaches.astro                    (Beaches hub page)
│   ├── snorkeling-diving.astro          (Water activities hub)
│   ├── surfing.astro                    (Surf lessons/beaches)
│   ├── kayaking-paddleboarding.astro    (Kayak + SUP)
│   ├── boat-cruises.astro               (Catamarans, sunset sails)
│   ├── yoga-wellness.astro              (Beach yoga, SUP yoga)
│   ├── food-tours.astro                 (Food tours, cooking classes)
│   ├── extreme-sports.astro             (Skydiving, jet ski, parasail)
│   └── free-things-to-do.astro          (Free activities)
├── operators/
│   └── index.astro                      (Curated tour operator directory)
├── policies/
│   ├── cancellation.astro               (Migrated from /cancellation-policy/)
│   ├── privacy.astro                     (Migrated from /privacy-policy/)
│   └── refunds.astro                     (Migrated from /how-to-cancel/)
└── contact.astro                        (New — extracted from footer info)
```

### 6.2 Content Migration Map

| WordPress Source | Astro Destination | Action |
|---|---|---|
| `/` (Home, ID 970) | `/index.astro` | Rebuild fresh |
| `/about/` | `/about.astro` | Migrate content, update |
| `/blog/` (Adventure Log) | `/blog/index.astro` | Migrate intro text |
| 26 blog posts | `/blog/[slug].astro` | Rewrite from titles |
| `/cancellation-policy/` | `/policies/cancellation.astro` | Migrate directly |
| `/privacy-policy/` | `/policies/privacy.astro` | Migrate directly |
| `/how-to-cancel-or-request-a-refund/` | `/policies/refunds.astro` | Migrate, update screenshots |
| `/activity-listing/` | `/adventures/index.astro` | Rebuild as category hub |
| `/activity-map/` | `/adventures/index.astro` (embedded map) | New map component |
| `/things-to-do-oahu/` | `/adventures/index.astro` | Merge into hub |
| Company CPTs (34) | `/operators/index.astro` | Curated directory |
| Activity CPTs (75) | Category hub pages | Group and describe |
| `/bucket-list/` | ❌ Archived | No equivalent |
| `/search/` | ❌ Archived | Astro has search differently |
| Membership pages | ❌ Archived | No membership in new site |
| Checkout/Order pages | ❌ Archived | No e-commerce in new site |
| Map variant pages | ❌ Archived | Single map if needed |

### 6.3 Image Migration

**Featured images for all 26 blog posts** survive on the WordPress server:
- Download via `wp-content/uploads/` paths from sitemap
- Optimize: convert to WebP, generate responsive sizes
- Rename to match Astro conventions: `/public/images/blog/[slug].webp`

**Activity/company images** (~150+ images):
- Download from sitemap URLs
- Map to category hub pages
- Use as card thumbnails and hero images

---

## 7. Recommendations

### 7.1 Immediate Actions

1. **Download all images** from `yourhawaiiguide.com/wp-content/uploads/` — paths available in XML sitemaps
2. **Scrape Wayback Machine** for any surviving blog content at archive.org (low probability but worth checking)
3. **Extract all post metadata**: titles, slugs, dates, categories, tags, featured image URLs → JSON file for Astro content generation

### 7.2 Content Creation Pipeline

1. **Phase 1 — Core Pages** (Week 1): Home, About, Policies (5 pages, mostly migrated)
2. **Phase 2 — Blog Posts** (Weeks 2-4): Rewrite 26 posts from titles. Prioritize:
   - SEO-heavy: "Snorkeling with Wild Dolphins in Oahu", "Lanikai Pillboxes Hike", "Hukilau Beach"
   - Evergreen: "3 low key beaches on the North Shore", "Beginner surf lessons"
   - Food: "The pancakes are iconic", "Some of the best ramen on Kalakaua"
3. **Phase 3 — Hub Pages** (Weeks 3-5): Category pages grouping all 75 activities
4. **Phase 4 — Operator Directory** (Week 5): Verified, curated list

### 7.3 What to Archive (Don't Migrate)

- All membership/e-commerce template pages
- Map variant pages (consolidate into one map component)
- Bucket list functionality
- Old FareHarbor booking integration
- jQuery 2.2.2 / Bootstrap 3.3.5 frontend code
- Redundant WordPress plugins (Favorites, WP User Avatar, etc.)
- 75 granular tags → simplify to ~10
- 39 overlapping categories → simplify to ~15

### 7.4 Content Quality Notes

- Blog posts from 2017-2019 likely had substantial content (500-1500 words based on topic depth)
- 2022 posts were likely short-form (Instagram/TikTok embeds that broke when embeds expired)
- The image captions in sitemap XML reveal specific businesses referenced: Eggs 'n Things, Momosan, Kulu Kulu, Super Pho — valuable for food post reconstruction
- Activity sitemap captions identify tour operators, activities, and locations — useful for hub page content

---

## 8. Data Sources

- WordPress REST API: `yourhawaiiguide.com/wp-json/wp/v2/posts?per_page=50`
- WordPress REST API: `yourhawaiiguide.com/wp-json/wp/v2/pages?per_page=50`
- WordPress REST API: `yourhawaiiguide.com/wp-json/wp/v2/categories?per_page=100`
- WordPress REST API: `yourhawaiiguide.com/wp-json/wp/v2/tags?per_page=100`
- XML Sitemaps: `/post-sitemap.xml`, `/page-sitemap.xml`, `/activities-sitemap.xml`, `/company-sitemap.xml`
- Individual page inspection via REST API content.rendered
- Previous audit: `docs/active-oahu/yhg-audit.md` (GRO-133)
