# Distribution Channels — Setup Guide

> **GRO-104:** Set up distribution channels for Human Design Engine content.
> Last updated: 2025-05-29

## Quick Reference — Channels Matrix

| Channel | Status | Setup Required |
|---------|--------|---------------|
| **Telegram Daily Briefing** | ✅ Code Ready | Set `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` env vars |
| **RSS Feed** | ✅ Code Ready | Run `generate_rss_feed.py --write`, host on humandesignengine.com |
| **Apple Podcasts** | 📋 Planned | Submit RSS feed URL to Podcasts Connect |
| **Spotify for Podcasters** | 📋 Planned | Submit RSS feed URL to Spotify |
| **YouTube** | 📋 Planned | YouTube Data API setup + upload script |
| **Docs Site** | ✅ Live | HTML docs at `docs/` (deploy to humandesignengine.com) |

---

## 1. Telegram — Daily Transit Briefing

### What Exists

The script `scripts/daily_transit_briefing.py` already:
- Computes daily planetary transits through Human Design gates
- Formats a Telegram-compatible HTML message
- Sends via Telegram Bot API when `--send` is passed

### Setup Steps

#### Step 1: Create a Telegram Bot
```bash
# In Telegram, message @BotFather:
/newbot

# Follow prompts:
# 1. Name: Human Design Engine
# 2. Username: @HDEngineBot (or similar)
# 3. Save the token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### Step 2: Create a Telegram Channel
```bash
# In Telegram:
# 1. New Channel → "Human Design Daily Transit"
# 2. Set to Public (optional but recommended for growth)
# 3. Add your bot as an Administrator
# 4. Get the Chat ID:
#    - For public channels: use @channelusername
#    - For private: send a message, then GET:
#      https://api.telegram.org/bot<TOKEN>/getUpdates
```

#### Step 3: Configure Environment
```bash
# Add to your .env or crontab:
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="@HDEngineChannel"   # or the numeric chat ID
```

#### Step 4: Test
```bash
cd /home/ubuntu/work/hd-platform
python3 scripts/daily_transit_briefing.py --send
```

#### Step 5: Schedule (Cron)
```bash
# In crontab: daily at 6 AM Mountain = 13:00 UTC
# crontab -e
0 13 * * * cd /home/ubuntu/work/hd-platform && python3 scripts/daily_transit_briefing.py --send >> /var/log/hd-transit.log 2>&1
```

### Current Cron Job
The cron job `9ab96b126a97` already handles this — verify with:
```bash
crontab -l | grep daily_transit_briefing
```

---

## 2. RSS Feed — Weekly Podcast

### What Exists

The script `scripts/generate_rss_feed.py`:
- Scans `hd-content/podcasts/` for episode `.md` files
- Generates a valid RSS 2.0 XML feed with Apple Podcasts (iTunes) tags
- Handles CDATA wrapping, GUIDs, enclosures, and categories
- Validatable via `--validate` flag

### Setup Steps

#### Step 1: Generate the Feed
```bash
cd /home/ubuntu/work/hd-platform
python3 scripts/generate_rss_feed.py --write
# Output: docs/podcast.xml
```

#### Step 2: Host the Feed
The RSS XML file needs to be served at a public URL. Options:
- **Option A** (Static): Serve `docs/podcast.xml` via nginx/Apache alongside existing docs
- **Option B** (Dynamic): Generate on-the-fly via the reports API server
- **Option C** (Cron): Regenerate nightly and upload to CDN

Add this nginx location block if using static hosting:
```nginx
location /podcast.xml {
    alias /var/www/humandesignengine.com/docs/podcast.xml;
    add_header Content-Type "application/rss+xml; charset=utf-8";
    add_header Cache-Control "public, max-age=3600";
}
```

#### Step 3: Auto-Regenerate (Cron)
```bash
# Regenerate RSS feed nightly at 2 AM
0 2 * * * cd /home/ubuntu/work/hd-platform && python3 scripts/generate_rss_feed.py --write >> /var/log/hd-rss.log 2>&1
```

#### Step 4: Validate
```bash
python3 scripts/generate_rss_feed.py --validate

# Or use external validators:
# https://www.castfeedvalidator.com/
# https://podba.se/validate/
```

### Feed URL (when hosted)
```
https://humandesignengine.com/podcast.xml
```

---

## 3. Apple Podcasts Submission

### Prerequisites
- Apple ID with two-factor authentication
- Valid RSS feed hosted at a public URL
- Podcast cover art: 1400×1400 to 3000×3000 JPG/PNG, < 512KB
- At least one published episode in the feed

### Steps

1. Go to [podcastsconnect.apple.com](https://podcastsconnect.apple.com/)
2. Sign in with your Apple ID
3. Click "+" → "New Show"
4. Choose "Add a show with an RSS feed"
5. Enter your RSS feed URL: `https://humandesignengine.com/podcast.xml`
6. Review metadata, confirm everything looks correct
7. Submit for review (typically 24-48 hours)

### Post-Approval
- Each new episode in your RSS feed will auto-appear in Apple Podcasts
- You can manage show details, analytics, and availability in Podcasts Connect

---

## 4. Spotify for Podcasters Submission

### Steps

1. Go to [podcasters.spotify.com](https://podcasters.spotify.com/)
2. Log in or create a Spotify account
3. Click "Get Started" → "Add Your Podcast"
4. Paste your RSS feed URL: `https://humandesignengine.com/podcast.xml`
5. Verify ownership (Spotify sends a confirmation email to the address in your RSS)
6. Review and publish

### Spotify-Specific Notes
- Spotify reads iTunes tags from your RSS feed (already implemented)
- Episode descriptions render in Spotify's app
- Analytics available in Spotify for Podcasters dashboard

---

## 5. YouTube — Setup Guide

### Option A: YouTube Data API (Automated Upload)

#### Step 1: Enable YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials → Desktop application
5. Download the client secret JSON file

#### Step 2: Install Tools
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### Step 3: Authentication Script
Create a one-time auth script to get a refresh token:

```python
#!/usr/bin/env python3
"""One-time YouTube OAuth flow to get refresh token."""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.environ.get("YOUTUBE_CLIENT_SECRET", "youtube_client_secret.json")

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
credentials = flow.run_local_server(port=8080)

print(f"Refresh token: {credentials.refresh_token}")
# Save this token securely as YOUTUBE_REFRESH_TOKEN env var
```

#### Step 4: Upload Script
The weekly podcast automation could be extended to:
1. Generate episode markdown (`weekly-podcast.py`)
2. Convert to audio (TTS pipeline — future feature)
3. Upload video/audio to YouTube via API
4. Add YouTube video URL to RSS enclosure

### Option B: Manual Upload
For now, manually upload:
1. Go to [studio.youtube.com](https://studio.youtube.com/)
2. Create → Upload videos
3. Upload the podcast audio with a static image background
4. Set title: "Human Design Weekly: [Date] — [Gate Highlights]"
5. Add to "Human Design Engine" playlist

---

## 6. Docs Site — Current State

The `docs/` directory contains a comprehensive static site:
```
docs/
├── index.html                    # Main landing page
├── landing-api.html              # API product landing
├── landing-reports.html          # Reports product landing
├── landing-sheplantedatree.html  # Becca's coaching page
├── buy-report.html               # Report purchase flow
├── success.html                  # Post-purchase page
├── affiliates.html               # Affiliate program
├── podcast.xml                   # RSS feed (generated)
├── widget.js / widget.src.js     # Embeddable widget
├── widget-demo.html              # Widget demo page
├── SWARM-WORKFLOW.md             # Agent workflow docs
├── TRUST-PROOF-SYSTEM.md         # Verification methodology
├── LINEAR-TASKS.md               # Task board
├── rapidapi-listing.md           # API marketplace listing
├── human-design/                 # HD encyclopedia
│   ├── types/                    # 5 type pages
│   ├── authorities/              # 7 authority pages
│   ├── profiles/                 # 12 profile pages
│   ├── centers/                  # 9 center pages
│   ├── gates/                    # 64 gate pages
│   └── channels/                 # Channel pages
└── affiliates/
    ├── signup.html
    └── dashboard.html
```

### Deployment
These are static HTML files. Deploy via:
- GitHub Pages (free)
- Netlify (free tier)
- nginx on existing VPS
- Cloudflare Pages (free, fast CDN)

---

## 7. Integration Points

### weekly-podcast.py → RSS → Distribution

```
┌─────────────────────────────────────────────────────┐
│  weekly-podcast.py                                   │
│  Generates: hd-content/podcasts/YYYY-MM-DD-episode.md│
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  generate_rss_feed.py                                │
│  Reads all episode .md files → podcast.xml           │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Distribution Channels                               │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Apple    │  │ Spotify      │  │ RSS Readers   │  │
│  │ Podcasts │  │ for          │  │ (Feedly, etc) │  │
│  │          │  │ Podcasters   │  │               │  │
│  └──────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────┘
```

### daily_transit_briefing.py → Telegram

```
┌─────────────────────────────────────────────────────┐
│  daily_transit_briefing.py                           │
│  Computes: today's transit gates                    │
│  Formats: HTML Telegram message                     │
│  Sends: via Telegram Bot API                        │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Telegram Channel                                    │
│  "@HDEngineChannel"                                  │
│  Daily message at 6 AM Mountain                     │
└─────────────────────────────────────────────────────┘
```

---

## 8. Environment Variables Summary

```bash
# ── Telegram ──────────────────────────
TELEGRAM_BOT_TOKEN=     # From @BotFather
TELEGRAM_CHAT_ID=       # Channel username or numeric ID

# ── RSS / Podcast ─────────────────────
PODCAST_BASE_URL=       # https://humandesignengine.com/podcast
PODCAST_DIR=            # Path to hd-content/podcasts (default auto-detected)
RSS_OUTPUT_PATH=        # Path to write podcast.xml (default: docs/podcast.xml)

# ── YouTube (future) ──────────────────
YOUTUBE_CLIENT_SECRET=  # Path to OAuth client secret JSON
YOUTUBE_REFRESH_TOKEN=  # OAuth refresh token (from one-time auth flow)

# ── Engine ────────────────────────────
ENGINE_PATH=            # /home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src
```

---

## 9. Checklist — GRO-104 Completion

- [x] Telegram daily transit briefing script (`daily_transit_briefing.py`)
- [x] Telegram send functionality with `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`
- [x] RSS feed generator script (`generate_rss_feed.py`) — valid RSS 2.0 + iTunes tags
- [x] Podcast episode markdown template (sample: `hd-content/podcasts/2024-05-20-episode.md`)
- [x] Weekly podcast generator script (`weekly-podcast.py`)
- [ ] Deploy `docs/podcast.xml` to public URL
- [ ] Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` env vars in production
- [ ] Submit RSS feed to Apple Podcasts Connect
- [ ] Submit RSS feed to Spotify for Podcasters
- [ ] Set up YouTube channel (manual or API)
- [ ] Add cron job for nightly RSS regeneration
- [ ] Add podcast cover art (1400×1400 JPG) to docs/podcast-cover.jpg
- [ ] Verify cron job `9ab96b126a97` is active for daily transit briefing
