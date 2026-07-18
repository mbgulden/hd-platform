#!/usr/bin/env python3
"""Audit built Human Design Engine SEO/index hygiene surfaces.

This is intentionally read-only. It gives the SEO remediation epic a repeatable
measurement harness before child fixes mutate routing, metadata, OG images, or
Search Console submission state.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

SITE = "https://humandesignengine.com"
PRIVATE_ROUTE_FRAGMENTS = (
    "cron-health",
    "coach_dashboard",
    "coach-dashboard",
    "dashboard",
    "landing-index",
    "active-oahu",
    "media-tags-sample",
)


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_chunks: list[str] = []
        self.canonical: str | None = None
        self.description: str | None = None
        self.robots: str | None = None
        self.og_image: str | None = None
        self.og_title: str | None = None
        self.og_description: str | None = None
        self.twitter_image: str | None = None
        self.refresh: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "link" and attrs_dict.get("rel", "").lower() == "canonical":
            self.canonical = attrs_dict.get("href") or None
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            http_equiv = attrs_dict.get("http-equiv", "").lower()
            if name == "description":
                self.description = content or None
            elif name == "robots":
                self.robots = content or None
            elif prop == "og:image":
                self.og_image = content or None
            elif prop == "og:title":
                self.og_title = content or None
            elif prop == "og:description":
                self.og_description = content or None
            elif name == "twitter:image":
                self.twitter_image = content or None
            elif http_equiv == "refresh":
                self.refresh = content or None

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_chunks.append(data)

    @property
    def title(self) -> str | None:
        title = " ".join(part.strip() for part in self.title_chunks if part.strip()).strip()
        return title or None


@dataclass
class HtmlFinding:
    route: str
    source: str
    missing: list[str]
    robots: str | None
    canonical: str | None
    redirect_target: str | None
    private_candidate: bool


def walk_html(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("*.html"))


def route_for_html(dist: Path, html: Path) -> str:
    rel = "/" + html.relative_to(dist).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[:-10] or "/"
    return rel


def parse_redirect_target(refresh: str | None) -> str | None:
    if not refresh:
        return None
    match = re.search(r"url\s*=\s*([^;]+)$", refresh, re.I)
    return match.group(1).strip().strip('"\'') if match else None


def private_candidate(route: str) -> bool:
    lowered = route.lower()
    return any(fragment in lowered for fragment in PRIVATE_ROUTE_FRAGMENTS)


def route_from_loc(loc: str) -> str:
    parsed = urlparse(loc)
    return parsed.path or "/"


def parse_sitemap(dist: Path) -> list[str]:
    sitemap = dist / "sitemap.xml"
    if not sitemap.exists():
        return []
    text = sitemap.read_text(encoding="utf-8", errors="replace")
    return [route_from_loc(loc) for loc in re.findall(r"<loc>(.*?)</loc>", text)]


def parse_redirects(dist: Path) -> dict[str, str]:
    redirects = dist / "_redirects"
    out: dict[str, str] = {}
    if not redirects.exists():
        return out
    for line in redirects.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            out[parts[0]] = parts[1]
    return out


def audit(repo: Path) -> dict[str, object]:
    dist = repo / "dist"
    sitemap_routes = parse_sitemap(dist)
    redirects = parse_redirects(dist)
    html_findings: list[HtmlFinding] = []
    redirect_loops: list[dict[str, str]] = []

    for source, target in redirects.items():
        if source.rstrip("/") == target.rstrip("/"):
            redirect_loops.append({"source": source, "target": target})

    for html in walk_html(dist):
        route = route_for_html(dist, html)
        parser = HeadParser()
        parser.feed(html.read_text(encoding="utf-8", errors="replace"))
        redirect_target = parse_redirect_target(parser.refresh)
        is_redirect = bool(redirect_target)
        robots = (parser.robots or "").lower()
        is_noindex = "noindex" in robots
        missing: list[str] = []
        if not is_redirect and not is_noindex:
            if not parser.title:
                missing.append("title")
            if not parser.description:
                missing.append("description")
            if not parser.canonical:
                missing.append("canonical")
            if not parser.og_title:
                missing.append("og:title")
            if not parser.og_description:
                missing.append("og:description")
            if not parser.og_image:
                missing.append("og:image")
            if not parser.twitter_image:
                missing.append("twitter:image")
        if missing or private_candidate(route) or is_redirect:
            html_findings.append(
                HtmlFinding(
                    route=route,
                    source=str(html.relative_to(repo)),
                    missing=missing,
                    robots=parser.robots,
                    canonical=parser.canonical,
                    redirect_target=redirect_target,
                    private_candidate=private_candidate(route),
                )
            )

    sitemap_private = [route for route in sitemap_routes if private_candidate(route)]
    sitemap_redirect_sources = sorted(set(sitemap_routes).intersection(redirects))
    noindex_private = [f.route for f in html_findings if f.private_candidate and f.robots and "noindex" in f.robots.lower()]
    indexable_private = [f.route for f in html_findings if f.private_candidate and f.route not in noindex_private and not f.redirect_target]

    missing_counts: dict[str, int] = {}
    for finding in html_findings:
        for item in finding.missing:
            missing_counts[item] = missing_counts.get(item, 0) + 1

    return {
        "status": "ok",
        "repo": str(repo),
        "dist_exists": dist.exists(),
        "html_count": len(list(walk_html(dist))),
        "sitemap_route_count": len(sitemap_routes),
        "redirect_count": len(redirects),
        "critical": {
            "redirect_loops": redirect_loops,
            "sitemap_private_routes": sitemap_private,
            "sitemap_redirect_sources": sitemap_redirect_sources,
            "indexable_private_routes": indexable_private,
        },
        "metadata_gap_counts": missing_counts,
        "sample_findings": [asdict(f) for f in html_findings[:60]],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Repository root containing built dist/")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    parser.add_argument("--fail-on-critical", action="store_true", help="Exit non-zero when critical index pollution is present")
    args = parser.parse_args()

    result = audit(Path(args.repo).resolve())
    critical = result["critical"]
    assert isinstance(critical, dict)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("HDE SEO/index hygiene audit")
        print(f"repo={result['repo']}")
        print(f"html_count={result['html_count']}")
        print(f"sitemap_route_count={result['sitemap_route_count']}")
        print(f"redirect_count={result['redirect_count']}")
        print("critical=" + json.dumps(critical, sort_keys=True))
        print("metadata_gap_counts=" + json.dumps(result["metadata_gap_counts"], sort_keys=True))
    has_critical = any(critical.values())
    return 2 if args.fail_on_critical and has_critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
