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
DESC_RE = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']{40,}["\']', re.IGNORECASE)
CANONICAL_RE = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']https://humandesignengine\.com/[^"\']*["\']', re.IGNORECASE)


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
        if not DESC_RE.search(head):
            problems.append("description")
        if not CANONICAL_RE.search(head):
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
