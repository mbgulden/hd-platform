#!/usr/bin/env python3
"""
Active Oahu Social Content Pipeline — GRO-129
==============================================
Connects the tagged media library to a ready-to-post social media content calendar.

Takes a tag filter (e.g. --tag kayaking, --tag drone) and:
  1. Selects the best media assets (prioritizing edited + high-res)
  2. Generates platform-specific content plans:
     - Instagram / Facebook : square photo + caption + hashtags
     - TikTok / Shorts       : vertical video clip reference
     - Story                 : portrait crop suggestion
  3. Outputs a content calendar JSON for a week of posts

Caption templates (4 content pillars):
  - Tour Promotion  : "Ready for the best [activity] on Oahu? 🌊"
  - Local Tips      : "Local secret: [fact]. Save this for your trip! 📍"
  - Scenic          : "This is why we live here. [location] never gets old. 🌅"
  - Safety          : "Before you paddle out, know this: [tip] 🛶"

Usage:
  python scripts/social_content_pipeline.py --tag kayaking
  python scripts/social_content_pipeline.py --tag drone --days 7 --out ./content
  python scripts/social_content_pipeline.py --tag kayaking --dry-run
"""

import argparse
import json
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

# ─── Paths ────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
MEDIA_TAGS_PATH = REPO_ROOT / "docs" / "active-oahu" / "media-tags.json"
DEFAULT_OUT_DIR = REPO_ROOT / "output" / "social-content"


# ─── Scoring weights ──────────────────────────────────────────────────────

# Tag bonuses — higher score = better social-media asset
TAG_SCORES = {
    "edited":     100,   # ready-to-use, polished
    "dslr":        80,   # high-res professional
    "drone":       65,   # epic aerial
    "gopro":       40,   # action / POV
    "underwater":  35,   # unique perspective
    "instructional": 30, # educational
    "raw-footage": -20,  # needs work
}

# Extension bonuses — processed formats preferred
EXT_SCORES = {
    ".jpg":   20,    # ready to post
    ".jpeg":  20,
    ".png":   20,
    ".cr2":   10,    # raw, high-quality but needs processing
    ".dng":   10,
    ".arw":   10,
    ".heic":   5,
    ".mp4":   15,    # video
    ".mov":   15,
    ".mts":   10,
    ".svg":    5,
}

# Photo vs video extensions
PHOTO_EXTS  = {".jpg", ".jpeg", ".png", ".cr2", ".dng", ".arw", ".heic", ".svg"}
VIDEO_EXTS  = {".mp4", ".mov", ".mts"}


# ─── Caption templates ────────────────────────────────────────────────────

CAPTION_TEMPLATES = {
    "tour_promotion": {
        "label": "Tour Promotion",
        "templates": [
            "Ready for the best {activity} on Oahu? 🌊 Book your spot — link in bio! 🔗",
            "Your {activity} adventure starts here. 🚣‍♂️ Oahu's #1 rated tours. Tag who you're bringing! 👇",
            "{location} is calling. 🌴 Experience {activity} like never before. DM us to book! 📩",
            "Weekend plans: sorted. ✅ {activity} at {location} — the ultimate island experience. 🌺",
            "Nothing beats {activity} on a sunny Oahu day. ☀️ Come see why we're 5-star rated! ⭐",
        ],
        "hashtags": ["#ActiveOahu", "#OahuAdventures", "#HawaiiLife", "#BookNow"],
        "default_activity": "kayaking",
        "default_location": "Kaneohe Bay",
    },
    "local_tips": {
        "label": "Local Tips",
        "templates": [
            "🌺 Local secret: {fact}. Save this for your trip! 📍",
            "🤫 Insider tip: {fact}. Most tourists never find this spot. You're welcome. 😉",
            "POV: you know about {fact}. 🏝️ Your Oahu trip just leveled up. Save for later! 📌",
            "Oahu locals know: {fact}. Now you do too. 🤙 Share with your travel buddy!",
            "The best part of Oahu? {fact}. Don't miss this on your next visit! 🌊",
        ],
        "hashtags": ["#OahuLocal", "#HawaiiTips", "#TravelHacks", "#HiddenHawaii"],
        "default_fact": "the best time to kayak to the Mokes is early morning before the trade winds pick up",
    },
    "scenic": {
        "label": "Scenic",
        "templates": [
            "This is why we live here. 🏝️ {location} never gets old. 🌅",
            "No filter needed. ✨ {location} showing off again. #ParadiseFound",
            "Views from {location} hit different at golden hour. 🌇 Who's coming with us?",
            "Just another day in paradise. 🌴 {location} — add this to your bucket list! 🪣",
            "Some places stay with you forever. {location} is one of them. 💙 #IslandVibes",
        ],
        "hashtags": ["#OahuViews", "#ParadiseFound", "#IslandVibes", "#HawaiiPhotography"],
        "default_location": "Kaneohe Bay",
    },
    "safety": {
        "label": "Safety",
        "templates": [
            "Before you paddle out, know this: {tip} 🛶 Safety first, adventure second. 🤙",
            "🧠 Pro tip: {tip}. A little preparation goes a long way on the water! 🌊",
            "Safety matters! 🦺 {tip}. Our guides have your back — always. 💪",
            "The ocean is amazing AND powerful. 🌊 {tip}. Respect the water, enjoy the ride! 🤙",
            "Adventure = preparation + stoke. 🏄 {tip}. Tag a friend who needs to hear this!",
        ],
        "hashtags": ["#OceanSafety", "#PaddleSmart", "#RespectTheOcean", "#StaySafe"],
        "default_tip": "always wear your life jacket and stay with your group — Kaneohe Bay conditions can change fast",
    },
}


# ─── Location / activity facts for tag-specific enrichment ─────────────────

TAG_CONTEXT = {
    "kayaking": {
        "activity": "kayaking",
        "location": "Kaneohe Bay",
        "facts": [
            "Kaneohe Bay is the only barrier reef in the Hawaiian Islands",
            "the Mokolua Islands are a protected seabird sanctuary — landing requires a permit",
            "Chinaman's Hat (Mokoli'i) is best visited at low tide when the sandbar emerges",
            "kayaking to the sandbar takes about 30-45 minutes from Kualoa Regional Park",
            "early morning paddlers often spot green sea turtles in the bay",
        ],
        "tips": [
            "always check wind conditions — afternoon trades can make the paddle back challenging",
            "wear reef-safe sunscreen to protect Kaneohe Bay's coral ecosystem",
            "bring a dry bag for your phone and snacks — things WILL get wet",
            "paddle with a buddy and let someone on shore know your float plan",
            "stay at least 50 feet from sea turtles and monk seals — it's the law!",
        ],
    },
    "drone": {
        "activity": "aerial photography",
        "location": "Oahu's Windward Coast",
        "facts": [
            "the Ko'olau mountain range creates dramatic windward cloud formations at sunrise",
            "Kaneohe Bay looks like a completely different world from above",
            "drone flights over Mokulua Islands reveal hidden tide pools on the backside",
            "the sandbar patterns shift with the tides — no two aerial shots are the same",
        ],
        "tips": [
            "always check FAA drone zones — parts of Kaneohe Bay are near MCBH airspace",
            "fly early morning for glassy water reflections and calm winds",
            "keep your drone in visual line of sight at all times",
        ],
    },
    "paddleboarding": {
        "activity": "paddleboarding",
        "location": "Kaneohe Bay",
        "facts": [
            "SUP offers a higher vantage point than kayaking — great for spotting marine life",
            "Kaneohe Bay's calm, shallow waters make it one of the best SUP spots on Oahu",
            "paddleboard yoga at the sandbar is a next-level island experience",
        ],
        "tips": [
            "start on your knees until you're past the shore break, then stand up in deeper water",
            "keep your feet parallel and shoulder-width apart for maximum stability",
        ],
    },
    "snorkeling": {
        "activity": "snorkeling",
        "location": "Kaneohe Bay Reef",
        "facts": [
            "Kaneohe Bay's patch reefs are home to over 400 species of fish",
            "the reef system spans over 30 square miles — one of Hawaii's largest",
        ],
        "tips": [
            "never touch the coral — even a light touch can kill centuries-old formations",
            "defog your mask with baby shampoo — works better than spit!",
        ],
    },
    "hiking": {
        "activity": "hiking",
        "location": "Oahu Trails",
        "facts": [
            "the Ko'olau summit trail offers 360-degree views on a clear day",
            "many Oahu trails follow ancient Hawaiian footpaths used for centuries",
        ],
        "tips": [
            "start early to beat the heat AND the crowds — trailheads fill up by 8 AM",
            "always bring more water than you think you need — Oahu humidity is no joke",
        ],
    },
    "surfing": {
        "activity": "surfing",
        "location": "Oahu's North Shore",
        "facts": [
            "Oahu's North Shore transforms into the surfing capital of the world every winter",
            "Waimea Bay waves can reach 30+ feet during big swells",
        ],
        "tips": [
            "know your limits — North Shore winter waves are NOT for beginners",
            "respect the lineup and wait your turn — surf etiquette matters in Hawaii",
        ],
    },
    "ebike": {
        "activity": "ebiking",
        "location": "Oahu's Scenic Routes",
        "facts": [
            "ebikes let you explore Oahu's hidden valleys without exhausting yourself on hills",
            "the North Shore bike path offers 7 miles of protected oceanfront riding",
        ],
        "tips": [
            "charge your battery fully before heading out — island rides can be longer than expected",
            "use bike lanes where available and always signal your turns",
        ],
    },
}

# Fallback context for any tag not explicitly listed
DEFAULT_CONTEXT = {
    "activity": "adventure",
    "location": "Oahu",
    "facts": ["Oahu is known as 'The Gathering Place' — and for good reason"],
    "tips": ["always check weather conditions before any outdoor activity in Hawaii"],
}


# ─── Media scoring ──────────────────────────────────────────────────────────

def score_media(filepath: str, info: dict) -> dict:
    """
    Return a scored media entry with computed priority.
    Higher score = better for social media.
    """
    tags = set(info["tags"])
    ext  = info["ext"].lower()

    score = 0

    # Tag bonuses
    for tag, bonus in TAG_SCORES.items():
        if tag in tags:
            score += bonus

    # Extension bonus
    score += EXT_SCORES.get(ext, 0)

    # Determine media type
    if ext in VIDEO_EXTS:
        media_type = "video"
    elif ext in PHOTO_EXTS:
        media_type = "photo"
    else:
        media_type = "unknown"

    return {
        "path": filepath,
        "tags": sorted(tags),
        "ext": ext,
        "folder": info["folder"],
        "media_type": media_type,
        "score": score,
    }


def select_best_media(
    tag: str,
    media_type: Optional[str] = None,
    limit: int = 14,
) -> list:
    """
    Load media-tags.json, filter by tag, score, and return best entries.
    Optionally filter by media_type ('photo' or 'video').
    """
    with open(MEDIA_TAGS_PATH) as f:
        data = json.load(f)

    candidates = []
    for filepath, info in data["files"].items():
        if tag not in info["tags"]:
            continue
        entry = score_media(filepath, info)
        if media_type and entry["media_type"] != media_type:
            continue
        candidates.append(entry)

    # Sort by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:limit]


# ─── Platform content generation ────────────────────────────────────────────

def generate_instagram_post(
    entry: dict,
    content_type: str,
    context: dict,
) -> dict:
    """
    Generate an Instagram/Facebook post plan from a photo entry.
    Returns: platform, media_path, caption, hashtags, content_type
    """
    templates = CAPTION_TEMPLATES[content_type]

    # Pick a template (deterministic rotation by day of year for reproducibility)
    today = date.today()
    template_idx = (today.toordinal() + hash(content_type)) % len(templates["templates"])
    template = templates["templates"][template_idx]

    # Fill in template variables
    activity = context.get("activity", templates.get("default_activity", "adventure"))
    location = context.get("location", templates.get("default_location", "Oahu"))
    fact     = random.choice(context.get("facts", [templates.get("default_fact", "Oahu has something for everyone")]))
    tip      = random.choice(context.get("tips", [templates.get("default_tip", "be prepared and stay safe")]))

    caption = template.format(
        activity=activity,
        location=location,
        fact=fact,
        tip=tip,
    )

    # Assemble hashtags
    base_hashtags = templates["hashtags"]
    tag_hashtags  = [f"#{tag.replace('-', '')}" for tag in entry["tags"] if tag not in ("raw-footage", "edited")]
    all_hashtags  = base_hashtags + tag_hashtags[:4]

    return {
        "platform": "Instagram / Facebook",
        "format": "square (1:1)",
        "media_path": entry["path"],
        "media_type": entry["media_type"],
        "caption": caption,
        "hashtags": all_hashtags,
        "content_pillar": content_type,
        "template_used": template,
        "media_score": entry["score"],
    }


def generate_tiktok_reel(
    video_entry: dict,
    context: dict,
) -> dict:
    """
    Generate a TikTok/Shorts plan from a video entry.
    """
    activity = context.get("activity", "adventure")
    location = context.get("location", "Oahu")

    # Short, punchy caption for short-form video
    captions = [
        f"POV: {activity} in {location} 🎬🌊 #Oahu #Hawaii",
        f"This is your sign to go {activity} in {location} 🤙✨",
        f"Day in the life: {activity} edition. {location} showing off! 🌺",
        f"Add this to your Oahu bucket list: {activity} at {location} 🪣✅",
    ]
    caption = random.choice(captions)

    return {
        "platform": "TikTok / YouTube Shorts / Reels",
        "format": "vertical (9:16)",
        "media_path": video_entry["path"],
        "media_type": video_entry["media_type"],
        "caption": caption,
        "hashtags": ["#ActiveOahu", "#OahuHawaii", "#TravelTok", "#AdventureTime"],
        "content_pillar": "short_video",
        "media_score": video_entry["score"],
        "note": "Original video may need vertical crop/reframe for 9:16",
    }


def generate_story_suggestion(
    photo_entry: dict,
    context: dict,
) -> dict:
    """
    Generate a Story (portrait) suggestion from a photo.
    Stories are vertical, ephemeral, and more casual.
    """
    location = context.get("location", "Oahu")
    activity = context.get("activity", "adventure")

    story_texts = [
        f"Out here living the dream 🌅 {location}",
        f"Morning magic at {location} ✨",
        f"Quick peek at today's {activity} conditions 👀",
        f"Behind the scenes: {activity} prep 🎬",
        f"Can't get over this view 😍 {location}",
    ]

    return {
        "platform": "Instagram / Facebook Story",
        "format": "portrait (9:16) — crop suggestion",
        "media_path": photo_entry["path"],
        "media_type": photo_entry["media_type"],
        "overlay_text": random.choice(story_texts),
        "sticker_suggestions": ["📍 Location tag", "⏰ Time sticker", "🎵 Music"],
        "content_pillar": "story",
        "media_score": photo_entry["score"],
        "note": "Crop center 9:16 — center the subject vertically, leave sky + water for text overlay",
    }


# ─── Content calendar builder ───────────────────────────────────────────────

def build_content_calendar(
    tag: str,
    days: int = 7,
    start_date: Optional[date] = None,
) -> dict:
    """
    Build a week (or N days) of content for a given tag.
    Rotates through content pillars for variety.
    """
    if start_date is None:
        start_date = date.today()

    # Load context for this tag
    context = TAG_CONTEXT.get(tag, DEFAULT_CONTEXT)

    # Select best photos and videos
    photos = select_best_media(tag, media_type="photo", limit=days * 3)
    videos = select_best_media(tag, media_type="video", limit=days + 2)

    if not photos:
        return {
            "error": f"No photo media found for tag '{tag}'",
            "tag": tag,
            "total_photos": 0,
            "total_videos": len(videos),
            "calendar": [],
        }

    # Content pillar rotation — mix it up through the week
    pillars = ["tour_promotion", "local_tips", "scenic", "safety"]
    pillar_cycle = [pillars[i % len(pillars)] for i in range(days)]

    calendar_entries = []
    photo_idx = 0
    video_idx = 0

    for day_offset in range(days):
        post_date = start_date + timedelta(days=day_offset)
        pillar = pillar_cycle[day_offset]

        # Instagram / Facebook (photo post)
        if photo_idx < len(photos):
            photo = photos[photo_idx]
            photo_idx += 1
            ig_post = generate_instagram_post(photo, pillar, context)
            ig_post["date"] = post_date.isoformat()
            ig_post["day"] = post_date.strftime("%A")
            calendar_entries.append(ig_post)

        # TikTok / Shorts (video, every 2-3 days)
        if day_offset % 3 == 0 and video_idx < len(videos):
            video = videos[video_idx]
            video_idx += 1
            tiktok = generate_tiktok_reel(video, context)
            tiktok["date"] = post_date.isoformat()
            tiktok["day"] = post_date.strftime("%A")
            calendar_entries.append(tiktok)

        # Story suggestion (every day, use next photo)
        if photo_idx < len(photos):
            story_photo = photos[photo_idx]
            photo_idx += 1
            story = generate_story_suggestion(story_photo, context)
            story["date"] = post_date.isoformat()
            story["day"] = post_date.strftime("%A")
            calendar_entries.append(story)

    return {
        "pipeline": "Active Oahu Social Content Pipeline (GRO-129)",
        "generated_at": datetime.now().isoformat(),
        "tag": tag,
        "tag_labels": list(context.keys()),
        "date_range": {
            "start": start_date.isoformat(),
            "end": (start_date + timedelta(days=days - 1)).isoformat(),
        },
        "days": days,
        "total_posts": len(calendar_entries),
        "media_stats": {
            "photos_available": len(photos),
            "videos_available": len(videos),
        },
        "calendar": calendar_entries,
    }


# ─── Output formatters ──────────────────────────────────────────────────────

def print_human_readable(calendar: dict):
    """Print a human-friendly content calendar to stdout."""
    print()
    print("=" * 72)
    print(f"  📅 ACTIVE OAHU SOCIAL CONTENT CALENDAR")
    print(f"  Tag: {calendar['tag']}  |  "
          f"{calendar['date_range']['start']} → {calendar['date_range']['end']}")
    print(f"  Photos: {calendar['media_stats']['photos_available']}  |  "
          f"Videos: {calendar['media_stats']['videos_available']}")
    print("=" * 72)

    current_day = None
    for entry in calendar["calendar"]:
        if entry["date"] != current_day:
            current_day = entry["date"]
            print(f"\n  📆 {current_day} ({entry['day']})")
            print(f"  {'─' * 60}")

        platform = entry["platform"]
        pillar   = entry.get("content_pillar", "").replace("_", " ").title()

        print(f"\n  🔹 [{platform}] — {pillar}")
        print(f"     Format:  {entry.get('format', 'N/A')}")
        print(f"     Media:   {entry.get('media_path', 'N/A')}")
        print(f"     Score:   {entry.get('media_score', 'N/A')}")

        if "caption" in entry:
            print(f"     Caption: \"{entry['caption']}\"")
        if "overlay_text" in entry:
            print(f"     Overlay: \"{entry['overlay_text']}\"")
        if "hashtags" in entry:
            print(f"     Hashtags: {' '.join(entry['hashtags'][:6])}")
        if "note" in entry:
            print(f"     ⚠ Note:  {entry['note']}")
        if "sticker_suggestions" in entry:
            print(f"     Stickers: {', '.join(entry['sticker_suggestions'])}")

    print(f"\n{'=' * 72}")
    print(f"  ✅ {calendar['total_posts']} posts generated for {calendar['days']} days")
    print(f"{'=' * 72}\n")


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Active Oahu Social Content Pipeline (GRO-129)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a week of kayaking content
  python scripts/social_content_pipeline.py --tag kayaking

  # 5 days of drone content, custom output directory
  python scripts/social_content_pipeline.py --tag drone --days 5 --out ./my-content

  # Preview only (no file output)
  python scripts/social_content_pipeline.py --tag kayaking --dry-run

  # Output JSON to stdout for piping
  python scripts/social_content_pipeline.py --tag kayaking --json
        """,
    )

    parser.add_argument(
        "--tag", default=None,
        help="Tag to filter media by (e.g. kayaking, drone, paddleboarding)")
    parser.add_argument(
        "--days", type=int, default=7,
        help="Number of days to generate content for (default: 7)")
    parser.add_argument(
        "--start-date",
        help="Start date in YYYY-MM-DD format (default: today)")
    parser.add_argument(
        "--out", default=str(DEFAULT_OUT_DIR),
        help=f"Output directory for JSON calendar (default: {DEFAULT_OUT_DIR})")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print calendar to stdout only, don't save files")
    parser.add_argument(
        "--json", action="store_true",
        help="Print JSON to stdout (for piping)")
    parser.add_argument(
        "--list-tags", action="store_true",
        help="List all available tags and exit")

    args = parser.parse_args()

    # ── List tags mode ─────────────────────────────────────────────────
    if args.list_tags:
        with open(MEDIA_TAGS_PATH) as f:
            data = json.load(f)
        print("\nAvailable tags:")
        for tag, count in sorted(data["tag_counts"].items(), key=lambda x: -x[1]):
            has_context = "✅" if tag in TAG_CONTEXT else "  "
            print(f"  {has_context} {tag:20s} ({count:5d} files)")
        print(f"\n  ✅ = has specialized caption context")
        return

    if not args.tag:
        parser.error("--tag is required (unless --list-tags)")

    # ── Parse start date ───────────────────────────────────────────────
    start_date = None
    if args.start_date:
        try:
            start_date = date.fromisoformat(args.start_date)
        except ValueError:
            print(f"ERROR: Invalid date format: {args.start_date}. Use YYYY-MM-DD.")
            sys.exit(1)

    # ── Build calendar ─────────────────────────────────────────────────
    calendar = build_content_calendar(
        tag=args.tag,
        days=args.days,
        start_date=start_date,
    )

    if "error" in calendar:
        print(f"\n❌ {calendar['error']}")
        sys.exit(1)

    # ── Output ─────────────────────────────────────────────────────────
    if args.json:
        print(json.dumps(calendar, indent=2))
    else:
        print_human_readable(calendar)

    if not args.dry_run:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        tag_slug = args.tag.replace(" ", "-")
        filename = f"content-calendar-{tag_slug}-{calendar['date_range']['start']}.json"
        out_path = out_dir / filename
        out_path.write_text(json.dumps(calendar, indent=2))
        print(f"\n📁 Calendar saved to: {out_path}")


if __name__ == "__main__":
    main()
