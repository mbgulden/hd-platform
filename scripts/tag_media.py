#!/usr/bin/env python3
"""
Active Oahu Media Auto-Tagger v2 (GRO-127)
============================================
Fast folder-based tagger — walks the Synology mount collecting only file paths,
then tags based on folder structure. No EXIF parsing, no size calculation.

Output: media-tags.json with file → tags mapping
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

MOUNT = Path("/home/ubuntu/mounts/synology-photo/Dropbox Team Space")
OUTPUT = Path("/home/ubuntu/work/hd-platform/docs/active-oahu/media-tags.json")

KEY_FOLDERS = [
    "Photos and Videos",
    "Edited Photos",
    "Drone Movie",
    "Kailua Photos and Videos",
    "Waikiki Advertisement",
    "Instructional Videos",
]

MEDIA_EXTS = {'.jpg','.jpeg','.png','.gif','.webp','.heic','.arw','.cr2','.nef','.dng',
              '.mp4','.mov','.avi','.mkv','.wmv','.m4v','.webm','.3gp','.mts','.mpg','.mpeg',
              '.tif','.tiff','.bmp','.svg','.psd'}


def tag_from_path(filepath: str) -> list[str]:
    """Derive tags from filepath folder names and filename."""
    lower = filepath.lower()

    # Location
    tags = set()
    if 'kailua' in lower: tags.add('kailua')
    if 'waikiki' in lower: tags.add('waikiki')
    if 'kaneohe' in lower or 'kbay' in lower: tags.add('kaneohe-bay')
    if 'kahana' in lower: tags.add('kahana')
    if 'chinaman' in lower: tags.add('chinamans-hat')
    if 'mokulua' in lower or 'mokes' in lower: tags.add('mokulua-islands')
    if 'sandbar' in lower: tags.add('kaneohe-sandbar')
    if 'northshore' in lower or 'north shore' in lower: tags.add('north-shore')
    if 'lanikai' in lower: tags.add('lanikai')
    if 'wailea' in lower: tags.add('wailea-point')

    # Activity
    if 'kayak' in lower: tags.add('kayaking')
    if 'snorkel' in lower: tags.add('snorkeling')
    if 'ebike' in lower or 'e-bike' in lower or 'bike' in lower: tags.add('ebike')
    if 'surf' in lower: tags.add('surfing')
    if 'paddle' in lower or 'sup' in lower: tags.add('paddleboarding')
    if 'drone' in lower: tags.add('drone')
    if 'hike' in lower: tags.add('hiking')

    # Content type
    if 'edited' in lower: tags.add('edited')
    if 'instructional' in lower: tags.add('instructional')
    if 'raw' in lower: tags.add('raw-footage')
    if 'underwater' in lower: tags.add('underwater')
    if 'aerial' in lower: tags.add('aerial')

    # Camera
    if 'gopro' in lower or 'gopr' in lower: tags.add('gopro')
    if 'dji' in lower: tags.add('dji')
    if 'sony' in lower or '.arw' in lower: tags.add('dslr')

    return sorted(tags)


def walk_folders(root: Path, folders: list[str]):
    """Walk specific folders, collecting tagged file paths."""
    tagged = {}
    tag_counts = {}
    total = 0

    for folder_name in folders:
        folder_path = root / folder_name
        if not folder_path.exists():
            print(f"  [skip] {folder_name} not found", file=sys.stderr)
            continue

        print(f"  Walking: {folder_name} ...", file=sys.stderr)
        count = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            # Skip macOS/Synology metadata
            dirnames[:] = [d for d in dirnames if not d.startswith('@') and d != '__MACOSX']

            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in MEDIA_EXTS:
                    continue

                fullpath = os.path.join(dirpath, fname)
                relpath = str(Path(fullpath).relative_to(root))
                tags = tag_from_path(fullpath)

                if tags:
                    tagged[relpath] = {
                        "tags": tags,
                        "folder": folder_name,
                        "ext": ext,
                    }
                    for t in tags:
                        tag_counts[t] = tag_counts.get(t, 0) + 1
                    count += 1

                total += 1
                if total % 2000 == 0:
                    print(f"    ... {total} files processed, {len(tagged)} tagged", file=sys.stderr)

        print(f"    {count} tagged in {folder_name}", file=sys.stderr)

    return tagged, tag_counts


def main():
    print(f"Scanning {MOUNT} ...", file=sys.stderr)
    tagged, tag_counts = walk_folders(MOUNT, KEY_FOLDERS)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ticket": "GRO-127",
        "total_files_processed": sum(1 for _ in tagged),
        "total_tagged": len(tagged),
        "unique_tags": len(tag_counts),
        "tag_counts": dict(sorted(tag_counts.items(), key=lambda x: -x[1])),
        "files": tagged,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Done: {len(tagged)} files tagged with {len(tag_counts)} tags", file=sys.stderr)
    print(f"Saved: {OUTPUT}", file=sys.stderr)
    print(f"\nTop tags:")
    for tag, cnt in sorted(tag_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {tag:25s} {cnt:5d}")


if __name__ == "__main__":
    main()
