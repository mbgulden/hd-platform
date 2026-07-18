#!/usr/bin/env python3
"""Verify static HTML pages have canonical and meta description tags.

Used by GRO-4000 to guard legacy/generated HD Engine pages that are copied into
Cloudflare Pages output by scripts/route-complete-build.mjs.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

HEAD_RE = re.compile(r"<head[^>]*>(.*?)</head>", re.IGNORECASE | re.DOTALL)
DESC_TAG_RE = re.compile(r"<meta\\b[^>]*>", re.IGNORECASE)
CANONICAL_TAG_RE = re.compile(r"<link\\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r"([:\\w-]+)\\s*=\\s*(['\"])(.*?)\\2", re.IGNORECASE | re.DOTALL)


def attrs_for(tag: str) -> dict[str, str]:
    return {name.lower(): value for name, _quote, value in ATTR_RE.findall(tag)}


def has_description(head: str) -> bool:
    for tag in DESC_TAG_RE.findall(head):
        attrs = attrs_for(tag)
        if attrs.get("name", "").lower() == "description" and len(attrs.get("content", "").strip()) >= 40:
            return True
    return False


def has_canonical(head: str) -> bool:
    for tag in CANONICAL_TAG_RE.findall(head):
        attrs = attrs_for(tag)
        if attrs.get("rel", "").lower() == "canonical" and attrs.get("href", "").startswith("https://humandesignengine.com/"):
            return True
    return False


def tracked_html(root: Path) -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "*.html"], cwd=root, text=True)
    return [root / line for line in output.splitlines() if line]


def dist_html(root: Path) -> list[Path]:
    dist = root / "dist"
    if not dist.exists():
        return []
    return sorted(dist.rglob("*.html"))


def missing_for(files: list[Path], root: Path) -> list[str]:
    missing: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = HEAD_RE.search(text)
        if not match:
            continue
        head = match.group(1)
        problems: list[str] = []
        if not has_description(head):
            problems.append("description")
        if not has_canonical(head):
            problems.append("canonical")
        if problems:
            missing.append(f"{path.relative_to(root)}: missing {', '.join(problems)}")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify HD Engine HTML SEO metadata")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--include-dist", action="store_true", help="Also check dist/**/*.html when present")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = tracked_html(root)
    if args.include_dist:
        files.extend(dist_html(root))
    missing = missing_for(files, root)
    if missing:
        print("SEO metadata gaps found:")
        for line in missing:
            print(f"- {line}")
        print(f"Checked {len(files)} HTML files; failures={len(missing)}")
        return 1
    print(f"SEO metadata verified: {len(files)} HTML files include description + canonical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
