#!/usr/bin/env python3
"""
RSS Feed Generator for Human Design Engine Podcast
====================================================
GRO-104: Distribution Channels

Scans hd-content/podcasts/ for episode markdown files and generates
a valid RSS 2.0 XML feed suitable for Apple Podcasts, Spotify, and
standard RSS readers.

Usage:
    python3 scripts/generate_rss_feed.py                    # generate + print
    python3 scripts/generate_rss_feed.py --write            # write to file
    python3 scripts/generate_rss_feed.py --validate         # validate existing feed

Configuration (env vars):
    PODCAST_BASE_URL    — root URL where podcast files are hosted
    PODCAST_DIR         — directory containing episode .md files
    RSS_OUTPUT_PATH     — where to write the RSS XML file
"""

import os
import sys
import re
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.dom import minidom

# ── Configuration ──────────────────────────────────────────────────────
PODCAST_BASE_URL = os.environ.get(
    "PODCAST_BASE_URL",
    "https://humandesignengine.com/podcast"
)
PODCAST_DIR = os.environ.get(
    "PODCAST_DIR",
    str(Path(__file__).resolve().parent.parent / "hd-content" / "podcasts")
)
RSS_OUTPUT_PATH = os.environ.get(
    "RSS_OUTPUT_PATH",
    str(Path(__file__).resolve().parent.parent / "docs" / "podcast.xml")
)

# ── Podcast Metadata ──────────────────────────────────────────────────
PODCAST_TITLE = "Human Design Engine Weekly"
PODCAST_DESCRIPTION = (
    "Weekly transit updates and Human Design insights powered by the "
    "Human Design Engine. Explore the cosmic weather through the lens "
    "of Human Design — gate activations, planetary transits, and practical "
    "experiments for living your design."
)
PODCAST_AUTHOR = "Human Design Engine"
PODCAST_EMAIL = "hello@humandesignengine.com"
PODCAST_LANGUAGE = "en-us"
PODCAST_CATEGORY = "Religion & Spirituality"
PODCAST_SUBCATEGORY = "Spirituality"
PODCAST_IMAGE_URL = f"{PODCAST_BASE_URL}/podcast-cover.jpg"
PODCAST_EXPLICIT = "no"

# Namespaces
NS_ITUNES = "http://www.itunes.com/dtds/podcast-1.0.dtd"
NS_CONTENT = "http://purl.org/rss/1.0/modules/content/"


# ── XML Helpers ────────────────────────────────────────────────────────
def _itunes(tag: str) -> str:
    """Return an iTunes namespace qualified tag."""
    return f"{{{NS_ITUNES}}}{tag}"


def _content(tag: str) -> str:
    """Return a content namespace qualified tag."""
    return f"{{{NS_CONTENT}}}{tag}"


# ── Episode Parsing ────────────────────────────────────────────────────
def parse_episode_markdown(filepath: str) -> dict | None:
    """Parse a podcast episode markdown file and extract metadata."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"[warn] Could not read {filepath}: {e}", file=sys.stderr)
        return None

    # Extract title (first H1)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if not title_match:
        return None
    title = title_match.group(1).strip()

    # Extract episode date
    date_match = re.search(
        r"\*\*Episode Date:\*\*\s*(\d{4}-\d{2}-\d{2})", content
    )
    if not date_match:
        fname = Path(filepath).stem
        date_from_name = re.match(r"(\d{4}-\d{2}-\d{2})", fname)
        pub_date = date_from_name.group(1) if date_from_name else datetime.now().strftime("%Y-%m-%d")
    else:
        pub_date = date_match.group(1)

    # Extract intro paragraph as summary
    intro_match = re.search(r"## Intro\n(.+?)(?:\n##|\Z)", content, re.DOTALL)
    summary = ""
    if intro_match:
        summary = intro_match.group(1).strip()
        if len(summary) > 250:
            summary = summary[:247] + "..."

    # Extract transit highlights for keywords
    highlights = re.findall(r"###\s+(.+?)\s+\(Gate\s+(\d+)\)", content)
    keywords = ", ".join(f"{name} (Gate {num})" for name, num in highlights[:5])

    # Stable GUID
    guid = hashlib.sha256(f"{title}{pub_date}".encode()).hexdigest()[:32]

    # URL slug
    slug = f"{pub_date}-{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')}"

    # Convert markdown to plain text description
    desc = content
    desc = re.sub(r"^#\s+.+\n+", "", desc)
    desc = re.sub(r"\*\*(.+?)\*\*", r"\1", desc)
    desc = re.sub(r"\*(.+?)\*", r"\1", desc)
    desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc)
    desc = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if len(desc) > 4000:
        desc = desc[:3997] + "..."

    return {
        "title": title,
        "pub_date": pub_date,
        "summary": summary,
        "keywords": keywords,
        "guid": guid,
        "slug": slug,
        "description": desc,
        "audio_url": f"{PODCAST_BASE_URL}/episodes/{slug}.mp3",
        "episode_url": f"{PODCAST_BASE_URL}/episodes/{slug}",
        "duration": "15:00",
    }


def discover_episodes(podcast_dir: str) -> list[dict]:
    """Scan podcast directory for episode markdown files."""
    episodes = []
    p = Path(podcast_dir)
    if not p.is_dir():
        print(f"[warn] Podcast directory not found: {podcast_dir}", file=sys.stderr)
        return episodes
    for md_file in sorted(p.glob("*-episode.md"), reverse=True):
        episode = parse_episode_markdown(str(md_file))
        if episode:
            episodes.append(episode)
    return episodes


# ── RSS XML Generation ─────────────────────────────────────────────────
def generate_rss(episodes: list[dict]) -> str:
    """Generate a full RSS 2.0 XML feed with iTunes podcast tags."""
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    # ── Channel metadata ──
    ET.SubElement(channel, "title").text = PODCAST_TITLE
    ET.SubElement(channel, "link").text = PODCAST_BASE_URL
    ET.SubElement(channel, "language").text = PODCAST_LANGUAGE
    ET.SubElement(channel, "description").text = PODCAST_DESCRIPTION
    ET.SubElement(channel, _itunes("author")).text = PODCAST_AUTHOR
    ET.SubElement(channel, _itunes("summary")).text = PODCAST_DESCRIPTION
    ET.SubElement(channel, _itunes("explicit")).text = PODCAST_EXPLICIT
    ET.SubElement(channel, _itunes("type")).text = "episodic"
    ET.SubElement(channel, _itunes("image"), {"href": PODCAST_IMAGE_URL})

    # Owner
    owner = ET.SubElement(channel, _itunes("owner"))
    ET.SubElement(owner, _itunes("name")).text = PODCAST_AUTHOR
    ET.SubElement(owner, _itunes("email")).text = PODCAST_EMAIL

    # Category (nested)
    cat = ET.SubElement(channel, _itunes("category"), {"text": PODCAST_CATEGORY})
    ET.SubElement(cat, _itunes("category"), {"text": PODCAST_SUBCATEGORY})

    # RSS image
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = PODCAST_IMAGE_URL
    ET.SubElement(image, "title").text = PODCAST_TITLE
    ET.SubElement(image, "link").text = PODCAST_BASE_URL

    # ── Episodes ──
    for ep in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = ep["title"]
        ET.SubElement(item, "link").text = ep["episode_url"]
        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = ep["guid"]
        ET.SubElement(item, "pubDate").text = _format_rfc822(ep["pub_date"])
        ET.SubElement(item, "description").text = ep["summary"]
        ET.SubElement(item, _itunes("summary")).text = ep["description"]
        ET.SubElement(item, _itunes("author")).text = PODCAST_AUTHOR
        ET.SubElement(item, _itunes("duration")).text = ep["duration"]
        if ep["keywords"]:
            ET.SubElement(item, _itunes("keywords")).text = ep["keywords"]
        ET.SubElement(item, "enclosure", {
            "url": ep["audio_url"],
            "length": "0",
            "type": "audio/mpeg",
        })

    # ── Serialize ──
    # Register namespaces with clean prefixes
    ET.register_namespace("itunes", NS_ITUNES)
    ET.register_namespace("content", NS_CONTENT)

    xml_str = ET.tostring(rss, encoding="unicode")

    # ElementTree adds ns0/ns1 if not all prefixes declared. Strip those.
    xml_str = re.sub(r'\s*xmlns:ns\d+="[^"]*"', '', xml_str)

    # Wrap text content in CDATA (ElementTree doesn't support CDATA natively)
    xml_str = re.sub(
        r'(<(itunes:)?summary[^>]*>)(.*?)(</(itunes:)?summary>)',
        lambda m: f'{m.group(1)}<![CDATA[{m.group(3)}]]>{m.group(4)}',
        xml_str, flags=re.DOTALL
    )
    xml_str = re.sub(
        r'(<description[^>]*>)(.*?)(</description>)',
        lambda m: f'{m.group(1)}<![CDATA[{m.group(2)}]]>{m.group(3)}',
        xml_str, flags=re.DOTALL
    )

    # Pretty-print
    try:
        dom = minidom.parseString(xml_str)
        pretty = dom.toprettyxml(indent="  ", encoding="UTF-8")
        # Remove the xml declaration (we add our own)
        result = pretty.decode("utf-8").split("\n", 1)[1]
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + result
    except Exception:
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


def _format_rfc822(date_str: str) -> str:
    """Convert YYYY-MM-DD to RFC 822 date format."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%a, %d %b %Y 09:00:00 +0000")
    except ValueError:
        return datetime.now().strftime("%a, %d %b %Y 09:00:00 +0000")


# ── Validation ─────────────────────────────────────────────────────────
def validate_feed(feed_path: str) -> bool:
    """Basic validation of an RSS feed. Returns True if valid."""
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
        channel = root.find("channel")
        if channel is None:
            print("[fail] No <channel> element found")
            return False
        title = channel.find("title")
        if title is None or not title.text:
            print("[fail] Missing <title> in channel")
            return False
        items = channel.findall("item")
        print(f"[ok] Channel title: {title.text}")
        print(f"[ok] Episodes: {len(items)}")
        for item in items:
            item_title = item.find("title")
            enclosure = item.find("enclosure")
            if item_title is not None:
                print(f"  - {item_title.text}")
            if enclosure is None:
                print(f"    [warn] Missing <enclosure> (audio file)")
        return True
    except ET.ParseError as e:
        print(f"[fail] XML parse error: {e}")
        return False
    except Exception as e:
        print(f"[fail] Validation error: {e}")
        return False


# ── Main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Generate RSS feed for Human Design Engine Podcast"
    )
    parser.add_argument("--write", action="store_true", help="Write RSS XML to file")
    parser.add_argument("--validate", action="store_true", help="Validate existing RSS feed")
    parser.add_argument("--output", type=str, default=None, help="Override output file path")
    args = parser.parse_args()

    output_path = args.output or RSS_OUTPUT_PATH

    if args.validate:
        if Path(output_path).is_file():
            ok = validate_feed(output_path)
            sys.exit(0 if ok else 1)
        else:
            print(f"[fail] Feed file not found: {output_path}")
            sys.exit(1)

    episodes = discover_episodes(PODCAST_DIR)
    if not episodes:
        print("[warn] No episodes found. Generating template with placeholder.")
        episodes = [{
            "title": "Sample Episode — Your First Transit Update",
            "pub_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "This is a placeholder episode. Real episodes will appear here once generated.",
            "keywords": "Human Design, Transit, Gates",
            "guid": "sample-episode-001",
            "slug": "sample-episode",
            "description": "Placeholder episode for RSS feed validation.",
            "audio_url": f"{PODCAST_BASE_URL}/episodes/sample.mp3",
            "episode_url": f"{PODCAST_BASE_URL}/episodes/sample",
            "duration": "00:30",
        }]

    rss_xml = generate_rss(episodes)

    if args.write:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rss_xml)
        print(f"[✓] RSS feed written to {output_path}")
        print(f"    Episodes: {len(episodes)}")
        print(f"    Validate: python3 scripts/generate_rss_feed.py --validate")
        print(f"\n[info] Submit this URL to podcast directories:")
        print(f"    Apple:  https://podcastsconnect.apple.com/")
        print(f"    Spotify: https://podcasters.spotify.com/")
        print(f"    Feed URL: {PODCAST_BASE_URL}/podcast.xml")
    else:
        print(rss_xml)
        print(f"\n[info] {len(episodes)} episodes discovered")
        print("[info] Use --write to save to file")


if __name__ == "__main__":
    main()
