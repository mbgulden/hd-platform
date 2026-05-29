# Human Design Content Automation

This directory contains scripts for automating Human Design content generation and distribution.

## scripts/weekly-podcast.py

This script generates a weekly Human Design podcast script based on planetary transits. It identifies major transit highlights for the upcoming week and formats them into a structured markdown file.

### Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- (Optional) Reports engine running on `localhost:8081`

### Usage

Run the script without arguments to generate an episode for the current date:

```bash
python3 scripts/weekly-podcast.py
```

To generate an episode for a specific start date:

```bash
python3 scripts/weekly-podcast.py --date 2024-06-15
```

To also regenerate the RSS feed after creating an episode:

```bash
python3 scripts/weekly-podcast.py --rss
```

### Configuration

The script uses the following environment variables:

- `REPORTS_ENGINE_URL`: URL of the HDE Reports Engine (default: `http://localhost:8081`).
- `PODCASTS_DIR`: Output directory for generated scripts (default: `hd-content/podcasts`).

### Output

Generated scripts are saved to `hd-content/podcasts/` in Markdown format, named by their start date: `YYYY-MM-DD-episode.md`.

Each script includes:
- Intro/Outro sections
- 3 Transit Highlights (Sun gate movements)
- 1 Practical Experiment for the week
- Call to Action (CTA) to humandesignengine.com

---

## scripts/generate_rss_feed.py

Generates a valid RSS 2.0 XML feed for podcast distribution. Compatible with Apple Podcasts, Spotify for Podcasters, and standard RSS readers.

### Usage

```bash
# Preview the feed
python3 scripts/generate_rss_feed.py

# Write to file (docs/podcast.xml)
python3 scripts/generate_rss_feed.py --write

# Validate an existing feed
python3 scripts/generate_rss_feed.py --validate
```

### Configuration

- `PODCAST_BASE_URL`: Base URL for podcast files (default: `https://humandesignengine.com/podcast`)
- `PODCAST_DIR`: Directory containing episode .md files (default: `hd-content/podcasts`)
- `RSS_OUTPUT_PATH`: Where to write the RSS XML (default: `docs/podcast.xml`)

### Distribution

Submit the generated `podcast.xml` URL to:
- **Apple Podcasts**: https://podcastsconnect.apple.com/
- **Spotify for Podcasters**: https://podcasters.spotify.com/

See `docs/DISTRIBUTION-CHANNELS.md` for full setup instructions.

---

## scripts/daily_transit_briefing.py

Computes today's planetary transits through Human Design gates and formats a Telegram-compatible message.

### Usage

```bash
# Compute and print
python3 scripts/daily_transit_briefing.py

# Compute and send to Telegram
python3 scripts/daily_transit_briefing.py --send

# Output raw JSON
python3 scripts/daily_transit_briefing.py --json
```

### Environment

- `TELEGRAM_BOT_TOKEN`: From BotFather
- `TELEGRAM_CHAT_ID`: Target channel/chat
- `ENGINE_PATH`: Path to OpenHumanDesignMCP/src
