# Human Design Podcast Automation

This directory contains scripts for automating Human Design content generation.

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
