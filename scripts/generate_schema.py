#!/usr/bin/env python3
"""
Schema Markup Generator — Active Oahu Tours (GRO-124)
======================================================
Generates production-ready JSON-LD for schema.org types consumed by
Google AI Overviews, ChatGPT, Perplexity, and Claude.

Supported types:
  faq              → FAQPage
  localbusiness    → LocalBusiness
  touristattraction→ TouristAttraction
  article          → Article
  breadcrumb       → BreadcrumbList
  howto            → HowTo

Usage:
  python generate_schema.py --type faq --input data/schema/faq-kayak.json
  python generate_schema.py --type localbusiness --input data/schema/localbusiness.json --output public/schema/localbusiness.json
  python generate_schema.py --type touristattraction --input data/schema/tour-mokulua.json

Each input file must conform to the expected structure for its type
(see data/schema/*.json for examples).
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path


# ── Schema.org context ──────────────────────────────────────────────
SCHEMA_CONTEXT = "https://schema.org"

# ── Type-specific validators & builders ─────────────────────────────

def _require_fields(data, required: list, label: str):
    """Validate that required top-level fields exist in data."""
    missing = [f for f in required if f not in data or data[f] is None]
    if missing:
        raise ValueError(f"{label}: missing required field(s): {', '.join(missing)}")


def build_faq(data: dict) -> dict:
    """FAQPage schema — #1 for Perplexity + Google AI Overviews."""
    _require_fields(data, ["questions"], "FAQPage")
    questions = data["questions"]
    if not isinstance(questions, list) or len(questions) == 0:
        raise ValueError("FAQPage: 'questions' must be a non-empty list")

    main_entity = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            raise ValueError(f"FAQPage: questions[{i}] must be an object with 'question' and 'answer'")
        _require_fields(q, ["question", "answer"], f"FAQPage questions[{i}]")
        main_entity.append({
            "@type": "Question",
            "name": q["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": q["answer"]
            }
        })

    return {
        "@context": SCHEMA_CONTEXT,
        "@type": "FAQPage",
        "mainEntity": main_entity
    }


def build_localbusiness(data: dict) -> dict:
    """LocalBusiness schema — #1 for Google AI Overviews local queries + ChatGPT."""
    _require_fields(data, ["name", "url", "address", "geo"], "LocalBusiness")

    addr = data["address"]
    _require_fields(addr, ["streetAddress", "addressLocality", "addressRegion", "postalCode", "addressCountry"], "LocalBusiness.address")

    geo = data["geo"]
    _require_fields(geo, ["latitude", "longitude"], "LocalBusiness.geo")

    result = {
        "@context": SCHEMA_CONTEXT,
        "@type": data.get("@type", "LocalBusiness"),
        "@id": data.get("@id", f"{data['url']}/#localbusiness"),
        "name": data["name"],
        "url": data["url"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": addr["streetAddress"],
            "addressLocality": addr["addressLocality"],
            "addressRegion": addr["addressRegion"],
            "postalCode": addr["postalCode"],
            "addressCountry": addr["addressCountry"]
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": geo["latitude"],
            "longitude": geo["longitude"]
        }
    }

    # Optional fields
    if "alternateName" in data:
        result["alternateName"] = data["alternateName"]
    if "description" in data:
        result["description"] = data["description"]
    if "telephone" in data:
        result["telephone"] = data["telephone"]
    if "email" in data:
        result["email"] = data["email"]
    if "image" in data:
        result["image"] = data["image"]
    if "logo" in data:
        result["logo"] = data["logo"]
    if "priceRange" in data:
        result["priceRange"] = data["priceRange"]
    if "currenciesAccepted" in data:
        result["currenciesAccepted"] = data["currenciesAccepted"]
    if "paymentAccepted" in data:
        result["paymentAccepted"] = data["paymentAccepted"]

    if "openingHoursSpecification" in data:
        result["openingHoursSpecification"] = data["openingHoursSpecification"]

    if "sameAs" in data:
        result["sameAs"] = data["sameAs"]

    if "areaServed" in data:
        result["areaServed"] = data["areaServed"]

    if "hasOfferCatalog" in data:
        result["hasOfferCatalog"] = data["hasOfferCatalog"]

    if "aggregateRating" in data:
        rating = data["aggregateRating"]
        result["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(rating["ratingValue"]),
            "reviewCount": str(rating["reviewCount"]),
            "bestRating": str(rating.get("bestRating", "5")),
            "worstRating": str(rating.get("worstRating", "1"))
        }

    return result


def build_touristattraction(data: dict) -> dict:
    """TouristAttraction schema — for individual tour/activity pages."""
    _require_fields(data, ["name", "description", "url", "location"], "TouristAttraction")

    loc = data["location"]
    _require_fields(loc, ["name"], "TouristAttraction.location")

    result = {
        "@context": SCHEMA_CONTEXT,
        "@type": "TouristAttraction",
        "@id": data.get("@id", f"{data['url']}/#tour"),
        "name": data["name"],
        "description": data["description"],
        "url": data["url"],
        "location": {
            "@type": "Place",
            "name": loc["name"]
        }
    }

    if "address" in loc:
        result["location"]["address"] = {
            "@type": "PostalAddress",
            **loc["address"]
        }

    if "geo" in loc:
        result["location"]["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": loc["geo"]["latitude"],
            "longitude": loc["geo"]["longitude"]
        }

    # Optional tour fields
    if "image" in data:
        result["image"] = data["image"]
    if "touristType" in data:
        result["touristType"] = data["touristType"]
    if "additionalType" in data:
        result["additionalType"] = data["additionalType"]
    if "provider" in data:
        result["provider"] = data["provider"]
    if "duration" in data:
        result["duration"] = data["duration"]

    if "offers" in data:
        result["offers"] = {
            "@type": "Offer",
            **data["offers"]
        }
        # Ensure priceCurrency is present
        if "priceCurrency" not in result["offers"]:
            result["offers"]["priceCurrency"] = "USD"

    if "aggregateRating" in data:
        rating = data["aggregateRating"]
        result["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating["ratingValue"],
            "reviewCount": rating["reviewCount"],
            "bestRating": rating.get("bestRating", "5")
        }

    if "subjectOf" in data:
        result["subjectOf"] = data["subjectOf"]

    return result


def build_article(data: dict) -> dict:
    """Article schema — for blog/guide pages."""
    _require_fields(data, ["headline", "url", "datePublished"], "Article")

    result = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Article",
        "@id": data.get("@id", f"{data['url']}/#article"),
        "headline": data["headline"],
        "url": data["url"],
        "datePublished": data["datePublished"],
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": data["url"]
        }
    }

    if "description" in data:
        result["description"] = data["description"]
    if "image" in data:
        result["image"] = data["image"]
    if "dateModified" in data:
        result["dateModified"] = data["dateModified"]
    if "author" in data:
        result["author"] = data["author"]
    if "publisher" in data:
        result["publisher"] = data["publisher"]
    if "about" in data:
        result["about"] = data["about"]
    if "keywords" in data:
        result["keywords"] = data["keywords"]

    return result


def build_breadcrumb(data: dict) -> dict:
    """BreadcrumbList schema — site-wide hierarchy."""
    _require_fields(data, ["items"], "BreadcrumbList")
    items = data["items"]
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("BreadcrumbList: 'items' must be a non-empty list")

    item_list = []
    for i, item in enumerate(items):
        entry = {
            "@type": "ListItem",
            "position": i + 1,
            "name": item["name"]
        }
        if "item" in item and item["item"]:
            entry["item"] = item["item"]
        item_list.append(entry)

    return {
        "@context": SCHEMA_CONTEXT,
        "@type": "BreadcrumbList",
        "itemListElement": item_list
    }


def build_howto(data: dict) -> dict:
    """HowTo schema — for step-by-step guide content."""
    _require_fields(data, ["name", "steps"], "HowTo")
    steps = data["steps"]
    if not isinstance(steps, list) or len(steps) == 0:
        raise ValueError("HowTo: 'steps' must be a non-empty list")

    howto_steps = []
    for i, step in enumerate(steps):
        _require_fields(step, ["name", "text"], f"HowTo steps[{i}]")
        entry = {
            "@type": "HowToStep",
            "name": step["name"],
            "text": step["text"]
        }
        if "image" in step:
            entry["image"] = step["image"]
        howto_steps.append(entry)

    result = {
        "@context": SCHEMA_CONTEXT,
        "@type": "HowTo",
        "name": data["name"],
        "step": howto_steps
    }

    if "description" in data:
        result["description"] = data["description"]
    if "totalTime" in data:
        result["totalTime"] = data["totalTime"]
    if "image" in data:
        result["image"] = data["image"]

    return result


# ── Builder dispatch ────────────────────────────────────────────────

BUILDERS = {
    "faq":                build_faq,
    "localbusiness":      build_localbusiness,
    "touristattraction":  build_touristattraction,
    "article":            build_article,
    "breadcrumb":         build_breadcrumb,
    "howto":              build_howto,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate schema.org JSON-LD for Active Oahu Tours (GRO-124)"
    )
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=list(BUILDERS.keys()),
        help="Schema type to generate"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to JSON input file with data for the schema"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write JSON-LD output (default: stdout)"
    )
    parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        default=True,
        help="Pretty-print output (default: true)"
    )
    parser.add_argument(
        "--compact", "-c",
        action="store_true",
        help="Compact/uglify output"
    )

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Build schema
    builder = BUILDERS[args.type]
    try:
        schema = builder(data)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Serialize
    indent = 2 if (args.pretty and not args.compact) else None
    json_str = json.dumps(schema, indent=indent, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)
            f.write("\n")  # trailing newline
        print(f"✅ Generated {args.type} schema → {output_path}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
