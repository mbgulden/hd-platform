import os
import subprocess
import logging
from fastapi import FastAPI, Body, HTTPException

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("guest-agent-server")

import json
import re
import glob
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
import math
import sys
from pathlib import Path

STATE_FILE = Path("/workspace/conversation_state.json")
GREETING_STATE_FILE = Path("/workspace/greeting_state.json")
HISTORY_FILE = Path("/workspace/conversation_history.json")

PEOPLE_DIR = Path("/workspace/people")
PEOPLE_INDEX_FILE = PEOPLE_DIR / "index.json"

DETAILS_INTENT_RE = re.compile(r"\b(remember|know|stored|birth details|birthdate|birth date|birth time|my info|my details|profile)\b", re.I)
YES_RE = re.compile(r"^\s*(yes|yep|yeah|use it|use those|that works|correct|go ahead|build it|run it)\s*[.!?]*\s*$", re.I)
NO_RE = re.compile(r"^\s*(no|nope|update|change|wrong|start over|different)\b", re.I)
EDIT_PROFILE_RE = re.compile(r"\b(edit|update|change|correct|fix)\b.*\b(profile|birth details|birthdate|birth date|birth time|time|date|location|place)\b|\b(birth time|birth date|birth location)\b.*\b(wrong|changed|change|update|edit|fix|is|should be|=)\b|\bmy\s+birth\s+(time|date|location)\s+(is|should be|=)\b", re.I)
TIME_FIELD_RE = re.compile(r"\b(time|birth time)\b", re.I)
DATE_FIELD_RE = re.compile(r"\b(date|birthdate|birth date|birthday)\b", re.I)
LOCATION_FIELD_RE = re.compile(r"\b(location|place|city|birth location)\b", re.I)
HELP_INTENT_RE = re.compile(r"\b(what can you do|help|how does this work|what are my options|where do we start|what can we do|menu)\b", re.I)
NEXT_INTENT_RE = re.compile(r"\b(what now|what next|next step|where do we go|what should i do with this|now what)\b", re.I)
EXPLAIN_CHART_RE = re.compile(r"\b(explain|unpack|interpret|read|meaning|tell me about)\b.*\b(my chart|chart|design|type|authority|profile|strategy)\b|\b(what does my chart mean|what am i|my authority|my type)\b", re.I)
REBUILD_CHART_RE = re.compile(r"\b(rebuild|regenerate|rerun|run again|build it again|generate again)\b.*\b(chart|report|pdf|design)\b|^\s*(rebuild|regenerate|rerun)\s*$", re.I)
PDF_REPORT_RE = re.compile(r"\b(pdf|report)\b.*\b(chart|design|human design)?\b|^\s*(yes|yep|yeah|please|ok|okay)?\s*(pdf|report)\s*(please)?\s*$", re.I)
COMPARE_KNOWN_RE = re.compile(r"\b(compare|relationship|compatibility)\b.*\b(stored|known|profiles|people)\b", re.I)
FRUSTRATION_RE = re.compile(
    r"\b(this is painful|painful|why are you asking|you already have|already gave|can't get past|cant get past|not working|too rigid|rigid|static|scripted|tax booth|stop this|stop asking|wrong again|start over|frustrating|frustrated)\b",
    re.I,
)
TIME_EXPLORATION_RE = re.compile(r"\b(explore|exploration|narrow.*time|figure out.*time|rectif|unknown time|missing time|don't know.*time|dont know.*time|not sure.*time)\b", re.I)


def slugify_person_name(name: str) -> str:
    raw = (name or "").strip().lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return raw or "person"


GENERIC_PROFILE_NAMES = {"sanctuary guest", "guest", "user", "my human design", "human design", "this person"}
GENERIC_PROFILE_SLUGS = {slugify_person_name(name) for name in GENERIC_PROFILE_NAMES}
GENERIC_PROFILE_SLUGS.update({"sanctuary_guest", "user", "my_human_design"})


NAME_STOPWORDS = {
    "a", "an", "and", "are", "around", "as", "at", "be", "birth", "bodygraph", "born", "build",
    "chart", "charts", "compare", "design", "edit", "existing", "for", "from", "generate", "human",
    "i", "in", "insight", "it", "little", "my", "name", "need", "new", "old", "profile", "random",
    "reading", "report", "same", "stinking", "that", "the", "their", "this", "under", "update", "want",
    "we", "what", "when", "where", "with", "words", "you", "your",
}


def clean_person_name(text: str) -> str:
    raw = (text or "").strip()
    raw = re.sub(r"^(my name is|i am|i'm|this is|for|person \d+ is|person \d+:|named|name is)\s+", "", raw, flags=re.I).strip(" .")
    raw = re.split(r"\b(?:born|birth|with birth|with date|on\s+\d|at\s+\d|in\s+[A-Z][a-z]+)\b", raw, maxsplit=1, flags=re.I)[0].strip(" .:-")
    raw = re.sub(r"\s+", " ", raw)
    return raw[:80] or "Sanctuary Guest"


def is_valid_person_name(name: str, *, allow_single_known: bool = True) -> bool:
    """Accept real-looking person names; reject ordinary phrases accidentally captured by regex.

    New chart subjects should normally be first + last (or two explicit name tokens like
    "Canary Guest"). A one-token name is accepted only if it already resolves to a stored
    profile, so a phrase like "this stinking little chart" cannot become a profile.
    """
    raw = clean_person_name(name)
    if not raw or len(raw) > 80:
        return False
    if re.search(r"\b(chart|bodygraph|reading|report|human design|birth|born|profile|existing|stinking|random|weird|phrase|sentence|words?)\b", raw, re.I):
        return False
    if re.search(r"[/?]|\b(should|would|could|need|want|please|just|little|same|old)\b", raw, re.I):
        return False
    tokens = [t.strip(".'-") for t in raw.split() if t.strip(".'-")]
    if len(tokens) < 2:
        if not allow_single_known:
            return False
        slug = slugify_person_name(raw)
        return bool(person_profile_path(slug).exists())
    if len(tokens) > 4:
        return False
    for token in tokens:
        lower = token.lower()
        if len(token) < 2 or lower in NAME_STOPWORDS:
            return False
        if not re.match(r"^[A-Z][A-Za-z0-9'’-]*$", token):
            return False
    return True


def load_people_index() -> dict:
    try:
        if PEOPLE_INDEX_FILE.exists():
            return json.loads(PEOPLE_INDEX_FILE.read_text())
    except Exception as exc:
        logger.warning("Failed to load people index: %s", exc)
    return {"default_person": "", "people": {}}


def save_people_index(index: dict) -> None:
    try:
        PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
        PEOPLE_INDEX_FILE.write_text(json.dumps(index, indent=2, sort_keys=True))
    except Exception as exc:
        logger.warning("Failed to save people index: %s", exc)


def person_profile_path(slug: str) -> Path:
    return PEOPLE_DIR / slug / "profile.json"


def load_person_profile(slug: str) -> dict:
    try:
        path = person_profile_path(slug)
        if path.exists():
            return json.loads(path.read_text())
    except Exception as exc:
        logger.warning("Failed to load person profile %s: %s", slug, exc)
    return {}


def profile_has_birth_details(profile: dict) -> bool:
    birth = profile.get("birth_input") or {}
    return bool(birth.get("birth_date") and birth.get("birth_time") and birth.get("location"))


def birth_confidence_for(value: str, field: str) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return "missing"
    if field == "birth_time":
        if raw in {"unknown", "no idea", "not sure"}:
            return "missing"
        if raw.startswith("natural:"):
            return "natural-clue"
        if raw.startswith("approx:"):
            return "approximate"
    return "exact"


def profile_birth_status(profile: dict) -> dict:
    birth = profile.get("birth_input") or {}
    confidence = profile.get("birth_confidence") or {}
    fields = {
        "birth_date": birth.get("birth_date") or "",
        "birth_time": birth.get("birth_time") or "",
        "location": birth.get("location") or "",
    }
    missing = [k for k, v in fields.items() if not v or str(v).upper() == "UNKNOWN"]
    return {
        "fields": fields,
        "missing": missing,
        "confidence": {k: confidence.get(k) or birth_confidence_for(v, k) for k, v in fields.items()},
        "complete": not missing,
    }


def set_profile_birth_confidence(slug: str, confidence: dict) -> None:
    try:
        profile = load_person_profile(slug)
        if not profile:
            return
        current = dict(profile.get("birth_confidence") or {})
        current.update({k: v for k, v in (confidence or {}).items() if v})
        profile["birth_confidence"] = current
        save_person_profile(slug, profile)
    except Exception as exc:
        logger.warning("Failed to update birth confidence for %s: %s", slug, exc)


def default_person_slug() -> str | None:
    index = load_people_index()
    slug = index.get("default_person")
    if slug and person_profile_path(slug).exists():
        return slug
    people = index.get("people") or {}
    for candidate in people:
        if profile_has_birth_details(load_person_profile(candidate)):
            return candidate
    return None



def known_person_slugs() -> list[str]:
    index = load_people_index()
    people = index.get("people") or {}
    return [slug for slug in people if person_profile_path(slug).exists()]


def resolve_profile_target(text: str = "") -> tuple[str | None, str | None]:
    """Return (slug, reason). If only one profile exists, use it automatically."""
    try:
        index = normalize_people_index()
        slugs = [slug for slug in (index.get("people") or {}) if person_profile_path(slug).exists()]
    except Exception:
        slugs = known_person_slugs()
    lowered = (text or "").lower()
    for slug in slugs:
        profile = load_person_profile(slug)
        name = (profile.get("name") or slug.replace("_", " ")).lower()
        if slug.replace("_", " ") in lowered or name in lowered:
            return slug, "matched_name"
    if len(slugs) == 1:
        return slugs[0], "only_profile"
    default = default_person_slug()
    if default:
        return default, "default_profile"
    return None, "none"


def save_person_profile(slug: str, profile: dict) -> None:
    path = person_profile_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, indent=2, sort_keys=True))
    index = load_people_index()
    index.setdefault("people", {})[slug] = {
        "name": profile.get("name") or slug.replace("_", " ").title(),
        "slug": slug,
        "profile_path": str(path),
        "updated_at": profile.get("updated_at", ""),
    }
    if not index.get("default_person"):
        index["default_person"] = slug
    save_people_index(index)


def is_generic_profile(slug: str | None, profile: dict | None = None) -> bool:
    raw_slug = (slug or "").strip().lower()
    name = ((profile or {}).get("name") or "").strip().lower()
    return raw_slug in GENERIC_PROFILE_SLUGS or name in GENERIC_PROFILE_NAMES


def rewrite_profile_paths(value, old_slug: str, new_slug: str, old_name: str, new_name: str):
    if isinstance(value, dict):
        return {k: rewrite_profile_paths(v, old_slug, new_slug, old_name, new_name) for k, v in value.items()}
    if isinstance(value, list):
        return [rewrite_profile_paths(v, old_slug, new_slug, old_name, new_name) for v in value]
    if isinstance(value, str):
        return value.replace(f"/{old_slug}/", f"/{new_slug}/").replace(old_name, new_name)
    return value


def migrate_person_profile_slug(old_slug: str, new_name: str) -> dict:
    """Move a generic/self profile to the user's real name and keep artifacts/index coherent."""
    import shutil
    new_name = clean_person_name(new_name)
    if not is_valid_person_name(new_name, allow_single_known=False):
        raise ValueError("I need a real first and last name before I rename the profile.")
    new_slug = slugify_person_name(new_name)
    old_profile = load_person_profile(old_slug)
    old_name = old_profile.get("name") or old_slug.replace("_", " ").title()
    if old_slug == new_slug:
        old_profile["name"] = new_name
        old_profile["subject_name"] = new_slug
        old_profile["slug"] = new_slug
        old_profile["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        save_person_profile(new_slug, old_profile)
        return old_profile

    old_person_dir = PEOPLE_DIR / old_slug
    new_person_dir = PEOPLE_DIR / new_slug
    if old_person_dir.exists():
        new_person_dir.parent.mkdir(parents=True, exist_ok=True)
        if new_person_dir.exists():
            shutil.rmtree(new_person_dir)
        shutil.move(str(old_person_dir), str(new_person_dir))

    for rel in (Path("/workspace/charts/personal"), Path("/workspace/charts/friends"), Path("/workspace/charts/family"), Path("/workspace/charts/composite")):
        old_chart_dir = rel / old_slug
        new_chart_dir = rel / new_slug
        if old_chart_dir.exists():
            new_chart_dir.parent.mkdir(parents=True, exist_ok=True)
            if new_chart_dir.exists():
                shutil.rmtree(new_chart_dir)
            shutil.move(str(old_chart_dir), str(new_chart_dir))

    profile = load_person_profile(new_slug) or old_profile
    profile = rewrite_profile_paths(profile, old_slug, new_slug, old_name, new_name)
    profile.update({
        "name": new_name,
        "slug": new_slug,
        "subject_name": new_slug,
        "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })
    save_person_profile(new_slug, profile)

    for chart_path in [Path("/workspace/charts/personal/chart_data.json"), PEOPLE_DIR / new_slug / "latest_chart_data.json", Path("/workspace/charts/personal") / new_slug / "chart_data.json"]:
        try:
            if chart_path.exists():
                data = json.loads(chart_path.read_text())
                data["name"] = new_name
                chart_path.write_text(json.dumps(data, indent=2, sort_keys=True))
        except Exception as exc:
            logger.warning("Failed to update renamed chart data %s: %s", chart_path, exc)

    index = normalize_people_index(preferred_slug=new_slug)
    people = index.get("people") or {}
    if old_slug in people:
        people.pop(old_slug, None)
    index["default_person"] = new_slug
    index["people"] = people
    save_people_index(index)
    return profile


def extract_self_name(text: str) -> str | None:
    raw = (text or "").strip()
    patterns = [
        r"\b(?:my name is|i am|i'm|this is)\s+([A-Z][A-Za-z0-9'’-]+(?:\s+[A-Z][A-Za-z0-9'’-]+){1,3})\b",
        r"\b(?:this chart is for|the chart is for|chart is for|this profile is for|profile is for)\s+([A-Z][A-Za-z0-9'’-]+(?:\s+[A-Z][A-Za-z0-9'’-]+){1,3})(?:\b.*\b(?:me|myself)\b|[.!?]?$)",
    ]
    for pat in patterns:
        m = re.search(pat, raw)
        if not m:
            continue
        candidate = clean_person_name(m.group(1))
        if is_valid_person_name(candidate, allow_single_known=False):
            return candidate
    return None


def handle_name_association_request(text: str) -> dict | None:
    name = extract_self_name(text)
    if not name:
        return None
    index = normalize_people_index()
    people = index.get("people") or {}
    target_slug = None
    # Prefer the default generic/self profile, then any single generic profile.
    default = index.get("default_person") or ""
    if default and is_generic_profile(default, load_person_profile(default)):
        target_slug = default
    if not target_slug:
        generic = [slug for slug in people if is_generic_profile(slug, load_person_profile(slug))]
        if len(generic) == 1:
            target_slug = generic[0]
    if not target_slug and len(people) == 1:
        only = next(iter(people))
        profile = load_person_profile(only)
        if is_generic_profile(only, profile):
            target_slug = only
    new_slug = slugify_person_name(name)
    if target_slug:
        profile = migrate_person_profile_slug(target_slug, name)
        birth = profile.get("birth_input") or {}
        has_birth = bool(birth.get("birth_date") and birth.get("birth_time") and birth.get("location"))
        return {"response": f"Got it — I moved the stored chart/profile from {target_slug.replace('_', ' ').title()} to {name}." + (" I can use those saved birth details from here." if has_birth else " I’ll attach the birth details once we build the chart.")}
    existing = load_person_profile(new_slug)
    if existing:
        index["default_person"] = new_slug
        save_people_index(index)
        return {"response": f"Got it — I’ll treat {name} as the active profile."}
    profile = {"name": name, "slug": new_slug, "subject_name": new_slug, "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"}
    save_person_profile(new_slug, profile)
    index = normalize_people_index(preferred_slug=new_slug)
    index["default_person"] = new_slug
    save_people_index(index)
    return {"response": f"Got it — I’ll store this profile under {name}. When we build the chart, the artifacts will use that name."}


def update_profile_birth_input(slug: str, field: str, value: str) -> dict:
    profile = load_person_profile(slug)
    if not profile:
        raise ValueError("I don’t have that profile stored yet.")
    birth = dict(profile.get("birth_input") or {})
    birth[field] = value
    profile["birth_input"] = birth
    profile["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    save_person_profile(slug, profile)
    return profile


def rebuild_chart_after_profile_edit(slug: str, profile: dict, field_label: str) -> dict:
    """Operate the system after a direct profile edit instead of asking for confirmation."""
    name = profile.get("name") or slug.replace("_", " ").title()
    value = (profile.get("birth_input") or {}).get(field_label, "")
    if not profile_has_birth_details(profile):
        return {"response": f"Updated {name}’s {field_label.replace('_', ' ')} to {value}. I’m still missing a required chart slot before I can rebuild."}
    try:
        generated = generate_chart_for_birth_details(name, slug, dict(profile.get("birth_input") or {}), relationship_type="personal")
        refreshed = load_person_profile(slug) or profile
        pdf = (refreshed.get("latest_chart") or {}).get("pdf_path")
        response = f"Updated {name}’s {field_label.replace('_', ' ')} to {value}. I rebuilt the chart with the corrected details.\n" + generated.get("response", "")
        payload = {"response": response}
        if pdf:
            payload["pdf_path"] = pdf
            payload["pdf_paths"] = [pdf]
        return payload
    except Exception as exc:
        logger.exception("Chart rebuild after profile edit failed: %s", exc)
        return {"response": f"Updated {name}’s {field_label.replace('_', ' ')} to {value}, but chart regeneration errored: {exc}"}


def extract_time_candidate(text: str) -> str:
    raw = (text or "").strip()
    raw = re.sub(r"^(please\s+)?(edit|update|change|correct|fix)\s+(my\s+|the\s+)?(birth\s+)?time\s*(to|as|=)?\s*", "", raw, flags=re.I).strip(" .:")
    raw = re.sub(r"^(my\s+|the\s+)?(birth\s+)?time\s*(is|should be|to|=)\s*", "", raw, flags=re.I).strip(" .:")
    m = re.search(r"\b(?:birth\s+)?time\b\s*(?:is|should be|to|as|=)?\s*(.+)$", raw, flags=re.I)
    if m:
        raw = m.group(1).strip(" .:")
    return raw or text


def extract_date_candidate(text: str) -> str:
    raw = (text or "").strip()
    raw = re.sub(r"^(please\s+)?(edit|update|change|correct|fix)\s+(my\s+|the\s+)?(birth\s+)?date\s*(to|as|=)?\s*", "", raw, flags=re.I).strip(" .:")
    raw = re.sub(r"^(my\s+|the\s+)?birth\s+date\s*(is|should be|to|=)\s*", "", raw, flags=re.I).strip(" .:")
    return raw or text


def extract_location_candidate(text: str) -> str:
    raw = (text or "").strip()
    raw = re.sub(r"^(please\s+)?(edit|update|change|correct|fix)\s+(my\s+|the\s+)?(birth\s+)?(location|place|city)\s*(to|as|=)?\s*", "", raw, flags=re.I).strip(" .:")
    raw = re.sub(r"^(my\s+|the\s+)?birth\s+(location|place|city)\s*(is|should be|to|=)\s*", "", raw, flags=re.I).strip(" .:")
    return raw or text

def profile_summary(profile: dict) -> str:
    birth = profile.get("birth_input") or {}
    status = profile_birth_status(profile)
    name = profile.get("name") or profile.get("display_name") or profile.get("subject_name") or "this person"
    conf = status.get("confidence", {})
    time_conf = conf.get("birth_time", "unknown")
    suffix = "" if time_conf == "exact" else f" ({time_conf} time)"
    return f"{name}: {birth.get('birth_date', 'unknown date')} at {birth.get('birth_time', 'unknown time')} in {birth.get('location', 'unknown place')}{suffix}"


def chart_insight_brief(chart: dict, name: str = "this person") -> str:
    """Return a useful, non-generic first-read layer after the plain chart facts."""
    if not chart:
        return ""
    hd_type = chart.get("hd_type") or chart.get("type") or "Unknown type"
    strategy = chart.get("strategy") or "their strategy"
    authority = chart.get("authority") or "their authority"
    profile = chart.get("profile") or "unknown profile"
    signature = chart.get("signature") or "alignment"
    not_self = chart.get("not_self_theme") or "friction"
    definition = chart.get("definition") or "unknown definition"
    defined = chart.get("defined_centers") or []
    undefined = chart.get("undefined_centers") or []
    channels = chart.get("defined_channels") or []
    variables = chart.get("variables") or {}
    cross = chart.get("incarnation_cross") or {}
    cross_name = cross.get("name") if isinstance(cross, dict) else ""

    lines = [
        "",
        "A more useful first read:",
        f"- The headline is not just “{hd_type}.” The practical question is where {name} is trying to force {strategy.lower()} instead of letting {authority} authority set the pace.",
        f"- Watch the signal shift between {signature} and {not_self}. That is the everyday dashboard: when life starts tasting like {str(not_self).lower()}, something is probably being pushed, proven, or rushed.",
        f"- Profile {profile} is the learning style. Read it as how the life collects wisdom, makes mistakes, gets projected on, or needs privacy/experimentation — not as a personality box.",
    ]
    if defined:
        lines.append(f"- Reliable energy tends to come through: {', '.join(map(str, defined[:5]))}. These are places to trust repetition and body evidence.")
    if undefined:
        lines.append(f"- Conditioning pressure is likely around: {', '.join(map(str, undefined[:5]))}. These are not flaws; they are places to notice amplification, comparison, and borrowed urgency.")
    if channels:
        lines.append(f"- Defined channel clue: {channels[0]}. Start there for a concrete gift/pattern instead of drowning the user in every gate.")
    if cross_name:
        lines.append(f"- Incarnation cross thread: {cross_name}. Treat it as a theme to observe in choices and relationships, not a prophecy.")
    if variables:
        useful = []
        for key in ("digestion", "environment", "motivation", "perspective", "cognition"):
            if variables.get(key):
                useful.append(f"{key}: {variables[key]}")
        if useful:
            lines.append("- Advanced texture: " + "; ".join(useful[:4]) + ".")
    lines.append("- Best next step: bring one real decision or relationship loop to this chart; that is where the insight gets useful.")
    return "\n".join(lines)


def append_chart_insight_to_result(result: str, relationship_type: str, subject_name: str, display_name: str) -> str:
    chart = load_chart_summary(relationship_type, subject_name)
    insight = chart_insight_brief(chart, display_name)
    if insight and "A more useful first read:" not in result:
        return result.rstrip() + "\n" + insight
    return result


def maybe_extract_person_from_chart_request(text: str) -> str | None:
    raw = (text or "").strip()
    # Only capture explicitly named people. Loose "for <anything>" used to turn
    # ordinary phrases into fake profiles; keep this deliberately conservative.
    patterns = [
        r"\b(?:for|under|named|name(?:d)?(?:\s+as)?|profile(?:\s+for)?(?:\s+is)?|put this(?: one)? under)\s+([A-Z][A-Za-z0-9'’-]+(?:\s+[A-Z][A-Za-z0-9'’-]+){1,3})(?:\s+(?:born|birth|with|on|at|in)\b|[.!?]?$)",
        r"\bperson\s+named\s+([A-Z][A-Za-z0-9'’-]+(?:\s+[A-Z][A-Za-z0-9'’-]+){1,3})\b",
    ]
    for pat in patterns:
        m = re.search(pat, raw)
        if m:
            candidate = clean_person_name(m.group(1))
            if is_valid_person_name(candidate, allow_single_known=False):
                return candidate
    return None


def chart_request_has_invalid_name_phrase(text: str, explicit_name: str | None) -> bool:
    if explicit_name:
        return False
    raw = text or ""
    if re.search(r"\b(for me|for my chart|under my profile|my chart)\b", raw, re.I):
        return False
    return bool(re.search(r"\b(for|under|named|profile\s+for|put this(?: one)? under)\s+[A-Za-z]", raw, re.I))


def describe_known_people() -> str:
    index = load_people_index()
    people = index.get("people") or {}
    if not people:
        return "I don’t have stored birth details yet. When we build a chart, I’ll save the person’s details in their own folder so I can reuse them."
    lines = ["I have these birth-detail profiles stored:"]
    for slug, meta in sorted(people.items(), key=lambda kv: (kv[1].get("name") or kv[0]).lower()):
        profile = load_person_profile(slug)
        lines.append("- " + profile_summary(profile or meta))
    lines.append("If you want a calculation, tell me which person to use or say what to update.")
    return "\n".join(lines)


def latest_chart_for_profile(profile: dict) -> dict:
    latest = profile.get("latest_chart") or {}
    chart_path = latest.get("chart_json_path") or ""
    if chart_path.startswith("/workspace/"):
        candidate = Path(chart_path)
    else:
        candidate = Path(chart_path) if chart_path else Path("")
    try:
        if candidate and candidate.exists():
            return json.loads(candidate.read_text())
    except Exception:
        pass
    slug = profile.get("slug") or profile.get("subject_name") or ""
    fallback = PEOPLE_DIR / slug / "latest_chart_data.json"
    try:
        if fallback.exists():
            return json.loads(fallback.read_text())
    except Exception:
        pass
    return {}


def format_chart_anchor(profile: dict) -> str:
    chart = latest_chart_for_profile(profile)
    name = profile.get("name") or profile.get("slug") or "this chart"
    hd_type = chart.get("hd_type") or (profile.get("latest_chart") or {}).get("type") or "not calculated yet"
    strategy = chart.get("strategy") or "unknown strategy"
    authority = chart.get("authority") or (profile.get("latest_chart") or {}).get("authority") or "unknown authority"
    prof = chart.get("profile") or (profile.get("latest_chart") or {}).get("profile") or "unknown profile"
    return f"{name}: {hd_type} · {strategy} · {authority} authority · {prof} profile"


def handle_pdf_report_request(text: str) -> dict | None:
    raw = (text or "").strip()
    if not PDF_REPORT_RE.search(raw):
        return None

    slug, _reason = resolve_profile_target(raw)
    profile = load_person_profile(slug) if slug else {}
    if profile_has_birth_details(profile):
        name = profile.get("name") or slug.replace("_", " ").title()
        generated = generate_chart_for_birth_details(name, slug, dict(profile.get("birth_input") or {}), relationship_type="personal")
        return {"response": "I generated the PDF report from the stored birth details.\n" + generated.get("response", "")}

    # Common follow-up: user says “yes pdf report” right after giving all birth
    # details, but the previous turn went through the LLM path before a profile
    # was persisted. Recover from recent user turns instead of claiming auth
    # failure or asking them to repeat themselves.
    for turn in reversed(load_history()):
        details = extract_full_birth_details(turn.get("user") or "")
        if not details:
            continue
        name = (details.get("name") or "Michael Gulden").strip()
        slug = slugify_person_name(name)
        index = normalize_people_index(preferred_slug=(slug if slug == "michael_gulden" else None))
        if slug == "michael_gulden":
            index["default_person"] = slug
        index.setdefault("people", {}).setdefault(slug, {"name": name, "slug": slug})
        save_people_index(index)
        birth = {"birth_date": details["birth_date"], "birth_time": details["birth_time"], "location": details["location"]}
        generated = generate_chart_for_birth_details(name, slug, birth, relationship_type="personal")
        return {"response": "I found the birth details from the recent thread and generated the PDF report.\n" + generated.get("response", "")}

    return {"response": "I can generate the PDF report, but I need the birth details first. Send name, birth date, birth time, and birth place in one sentence."}


def handle_workflow_navigation(text: str) -> dict | None:
    raw = (text or "").strip()
    slug, _reason = resolve_profile_target(raw)
    profile = load_person_profile(slug) if slug else {}
    has_profile = bool(profile and profile_has_birth_details(profile))

    if HELP_INTENT_RE.search(raw):
        if has_profile:
            anchor = format_chart_anchor(profile)
            return {"response": (
                f"We have a real starting point: {anchor}.\n\n"
                "Pick the thread that fits today:\n"
                "- rebuild or update the chart\n"
                "- compare this with another person\n"
                "- unpack one chart piece in plain English\n"
                "- journal what you’re noticing\n\n"
                "Which one is closest?"
            )}
        return {"response": (
            "We can start clean. No menu maze.\n\n"
            "Usually one of these is the doorway:\n"
            "- build a chart\n"
            "- compare two people\n"
            "- journal what’s happening\n"
            "- talk through a pattern before calculating anything\n\n"
            "Which one feels useful right now?"
        )}

    if NEXT_INTENT_RE.search(raw):
        if has_profile:
            anchor = format_chart_anchor(profile)
            return {"response": (
                f"Next, I’d keep it concrete. {anchor}.\n\n"
                "Choose one: do you want the direct chart thread, a relationship comparison, or one small experiment for this week?"
            )}
        return {"response": "Next clean step: build the first chart, or tell me what you’re trying to understand before we calculate anything."}

    if EXPLAIN_CHART_RE.search(raw):
        if not has_profile:
            return {"response": "I can explain it once I have a chart to stand on. Want to build yours first?"}
        chart = latest_chart_for_profile(profile)
        name = profile.get("name") or "you"
        hd_type = chart.get("hd_type") or "your type"
        strategy = chart.get("strategy") or "your strategy"
        authority = chart.get("authority") or "your authority"
        prof = chart.get("profile") or "your profile"
        return {"response": (
            f"For {name}, I’d start here: {hd_type} is the shape of the energy, {strategy} is the cleaner way to move, and {authority} is the decision signal to respect.\n\n"
            f"The {prof} profile is more about how the life learns than a personality label.\n\n"
            "Want me to unpack type, authority, profile, or the places you’re probably forcing it?"
        )}

    if REBUILD_CHART_RE.search(raw):
        if not has_profile:
            return {"response": "I can rebuild it, but I don’t have stored birth details yet. Who is this chart for?"}
        birth = profile.get("birth_input") or {}
        try:
            from daily_journal_mcp import generate_human_design_chart
            result = generate_human_design_chart(
                birth_date=birth["birth_date"],
                birth_time=birth["birth_time"],
                location=birth["location"],
                name=profile.get("name") or profile.get("slug") or "Sanctuary Guest",
                relationship_type="personal",
                subject_name=profile.get("slug") or profile.get("subject_name") or "user",
            )
            return {"response": "I used the stored birth details and rebuilt it.\n" + result}
        except Exception as exc:
            logger.exception("Stored profile rebuild failed: %s", exc)
            return {"response": f"I tried to rebuild from the stored details, but chart generation errored: {exc}"}

    if COMPARE_KNOWN_RE.search(raw):
        slugs = known_person_slugs()
        if len(slugs) < 2:
            return {"response": "I need two stored profiles for that. I have one or none, so tell me the next person’s name and we’ll build theirs first."}
        names = [load_person_profile(s).get("name") or s.replace("_", " ").title() for s in slugs]
        return {"response": "I can compare stored profiles. Which two should I use? I have: " + ", ".join(names) + "."}

    return None


def handle_profile_edit_request(text: str) -> dict | None:
    raw = (text or "").strip()
    state = load_state()
    edit = state.get("pending_profile_edit")
    if edit:
        slug = edit.get("slug")
        field = edit.get("field")
        profile = load_person_profile(slug)
        if not profile:
            clear_state()
            return {"response": "I couldn’t find that stored profile anymore. Annoying, but fixable — tell me who this is for first."}
        if field == "birth_time":
            parsed = parse_birth_time(raw)
            if not parsed:
                return {"response": "Give me the corrected birth time — exact, approximate, sunrise/sunset, or unknown."}
            birth = profile.get("birth_input") or {}
            if parsed.startswith("NATURAL:"):
                parsed, note = resolve_birth_time_after_location(parsed, birth.get("birth_date", ""), birth.get("location", ""))
            profile = update_profile_birth_input(slug, "birth_time", parsed.split(":", 1)[1] if parsed.startswith("APPROX:") else parsed)
            clear_state()
            return rebuild_chart_after_profile_edit(slug, profile, "birth_time")
        if field == "birth_date":
            parsed = parse_birth_date(raw)
            if not parsed:
                return {"response": "Give me the corrected birth date — MM/DD/YYYY or natural language is fine."}
            profile = update_profile_birth_input(slug, "birth_date", parsed)
            clear_state()
            return rebuild_chart_after_profile_edit(slug, profile, "birth_date")
        if field == "location":
            loc = parse_name_and_location(raw)
            if len(loc) < 2:
                return {"response": "Give me the corrected birth location — city and state/country is enough."}
            profile = update_profile_birth_input(slug, "location", loc)
            clear_state()
            return rebuild_chart_after_profile_edit(slug, profile, "location")

    if not EDIT_PROFILE_RE.search(raw):
        return None
    slug, reason = resolve_profile_target(raw)
    if not slug:
        return {"response": "I don’t have a stored profile to edit yet. Build the chart once, and I’ll keep the details in that person’s folder."}
    profile = load_person_profile(slug)
    name = profile.get("name") or slug.replace("_", " ").title()
    slugs = known_person_slugs()
    if len(slugs) > 1 and reason not in {"matched_name", "default_profile"}:
        names = ", ".join((load_person_profile(s).get("name") or s.replace("_", " ").title()) for s in slugs)
        return {"response": f"Which profile should I edit? I have: {names}."}

    field = None
    if TIME_FIELD_RE.search(raw):
        field = "birth_time"
        candidate = extract_time_candidate(raw)
        parsed = parse_birth_time(candidate)
        if parsed and candidate.lower() != raw.lower():
            birth = profile.get("birth_input") or {}
            if parsed.startswith("NATURAL:"):
                parsed, note = resolve_birth_time_after_location(parsed, birth.get("birth_date", ""), birth.get("location", ""))
            profile = update_profile_birth_input(slug, "birth_time", parsed.split(":", 1)[1] if parsed.startswith("APPROX:") else parsed)
            return rebuild_chart_after_profile_edit(slug, profile, "birth_time")
    elif DATE_FIELD_RE.search(raw):
        field = "birth_date"
        candidate = extract_date_candidate(raw)
        parsed = parse_birth_date(candidate)
        if parsed and candidate.lower() != raw.lower():
            profile = update_profile_birth_input(slug, "birth_date", parsed)
            return rebuild_chart_after_profile_edit(slug, profile, "birth_date")
    elif LOCATION_FIELD_RE.search(raw):
        field = "location"
        candidate = extract_location_candidate(raw)
        loc = parse_name_and_location(candidate)
        if len(loc) >= 2 and candidate.lower() != raw.lower():
            profile = update_profile_birth_input(slug, "location", loc)
            return rebuild_chart_after_profile_edit(slug, profile, "location")

    if not field:
        return {"response": f"I found {name}. What do you want to edit — birth date, birth time, or location?"}
    state["pending_profile_edit"] = {"slug": slug, "field": field}
    save_state(state)
    label = {"birth_time": "birth time", "birth_date": "birth date", "location": "birth location"}[field]
    return {"response": f"Okay — I’ll edit {name}’s {label}. What should it be?"}


def handle_birth_details_lookup(text: str) -> dict | None:
    if not DETAILS_INTENT_RE.search(text or ""):
        return None
    if CHART_INTENT_RE.search(text or ""):
        return None
    return {"response": describe_known_people()}


CHART_INTENT_RE = re.compile(r"\b(charts?|bodygraphs?|body graphs?|human design|design calculated|calculate my design|reading|report|compare|compatib|relationship|composite|synastry)\b", re.I)
COMPARE_INTENT_RE = re.compile(r"\b(compare|compatib|relationship|composite|synastry)\b", re.I)
GREETING_RE = re.compile(r"^\s*((hi|hello|hey)(?:\s+[A-Za-z][A-Za-z0-9_-]{1,30})?|good morning|good afternoon|good evening)\s*[.!?]*\s*$", re.I)
RESET_RE = re.compile(r"^\s*(/new|/start over|start over|reset|fresh start)\s*$", re.I)

def load_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
    except Exception as exc:
        logger.warning("Failed to load conversation state: %s", exc)
    return {}

def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as exc:
        logger.warning("Failed to save conversation state: %s", exc)

def clear_state() -> None:
    try:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
    except Exception as exc:
        logger.warning("Failed to clear conversation state: %s", exc)


def load_history() -> list[dict]:
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text())
            if isinstance(data, list):
                return data[-16:]
    except Exception as exc:
        logger.warning("Failed to load conversation history: %s", exc)
    return []


def save_history(history: list[dict]) -> None:
    try:
        HISTORY_FILE.write_text(json.dumps(history[-16:], indent=2))
    except Exception as exc:
        logger.warning("Failed to save conversation history: %s", exc)


def append_history(user_text: str, assistant_text: str) -> None:
    history = load_history()
    history.append({
        "user": (user_text or "")[-2000:],
        "assistant": (assistant_text or "")[-3000:],
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    })
    save_history(history)


def format_recent_history() -> str:
    history = load_history()[-8:]
    if not history:
        return "No recent turns stored yet."
    lines = []
    for turn in history:
        lines.append("User: " + (turn.get("user") or "").replace("\n", " ")[:900])
        lines.append("Guide: " + (turn.get("assistant") or "").replace("\n", " ")[:900])
    return "\n".join(lines)

def load_greeting_state() -> dict:
    try:
        if GREETING_STATE_FILE.exists():
            return json.loads(GREETING_STATE_FILE.read_text())
    except Exception as exc:
        logger.warning("Failed to load greeting state: %s", exc)
    return {"index": 0, "last": ""}


def save_greeting_state(state: dict) -> None:
    try:
        GREETING_STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as exc:
        logger.warning("Failed to save greeting state: %s", exc)


FIRST_IMPRESSION_PROMPTS = [
    "I’m here. Is today more a ‘sort it out’ day, or a ‘just sit with me’ day?",
    "Clean slate. Do you want to name the thing first, or feel where it lands in your body?",
    "Hey. Should we start with what feels heavy, or with what still feels true?",
    "I’m with you. Is this more about a decision, or about the feeling underneath it?",
    "Let’s keep it simple. Do you want the direct thread, or the gentler doorway in?",
]


def next_first_impression(reset: bool = False) -> str:
    state = load_greeting_state()
    idx = int(state.get("index", 0)) % len(FIRST_IMPRESSION_PROMPTS)
    text = FIRST_IMPRESSION_PROMPTS[idx]
    if text == state.get("last"):
        idx = (idx + 1) % len(FIRST_IMPRESSION_PROMPTS)
        text = FIRST_IMPRESSION_PROMPTS[idx]
    state["index"] = (idx + 1) % len(FIRST_IMPRESSION_PROMPTS)
    state["last"] = text
    save_greeting_state(state)
    if reset:
        return "Fresh start. " + text
    return text


def handle_reset_or_greeting(text: str) -> dict | None:
    raw = (text or "").strip()
    if RESET_RE.match(raw):
        clear_state()
        return {"response": next_first_impression(reset=True)}
    if GREETING_RE.match(raw):
        return {"response": next_first_impression(reset=False)}
    return None


def parse_birth_date(text: str) -> str | None:
    """Accept American, ISO, and natural English date shapes.

    User-facing intake should be forgiving: 06/14/1990, June 14 1990,
    14 June 1990, 14th June 1990, and longer sentences that contain those.
    Internal tool calls still receive ISO YYYY-MM-DD.
    """
    raw = (text or "").strip()
    raw = re.sub(r"^(my birthday is|my birth date is|i was born on|i was born|born on|born)\s+", "", raw, flags=re.I).strip(" .")
    raw = re.sub(r"\b(\d{1,2})(st|nd|rd|th)\b", r"\1", raw, flags=re.I)
    raw = re.sub(r"\s+", " ", raw)
    formats = [
        "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",
        "%m/%d/%y", "%m-%d-%y", "%m.%d.%y",
        "%Y-%m-%d", "%Y/%m/%d",
        "%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y",
        "%d %B %Y", "%d %b %Y", "%d %B, %Y", "%d %b, %Y",
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
    ]
    def try_parse(candidate: str) -> str | None:
        candidate = candidate.strip(" .,")
        for fmt in formats:
            try:
                dt = datetime.strptime(candidate, fmt)
                # Avoid silently accepting impossible historical shorthand.
                if 1900 <= dt.year <= 2100:
                    return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return None

    parsed = try_parse(raw)
    if parsed:
        return parsed

    # Pull a likely numeric date out of a longer sentence.
    m = re.search(r"(\d{1,4}[./-]\d{1,2}[./-]\d{1,4})", raw)
    if m:
        parsed = try_parse(m.group(1))
        if parsed:
            return parsed

    # Month-first natural language: June 14, 1990 / Jun 14 1990.
    m = re.search(r"([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?[,]?\s+\d{4})", raw, re.I)
    if m:
        parsed = try_parse(re.sub(r"\b(\d{1,2})(st|nd|rd|th)\b", r"\1", m.group(1), flags=re.I))
        if parsed:
            return parsed

    # Day-first natural language: 14 June 1990 / 14th Jun, 1990.
    m = re.search(r"(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+[,]?\s+\d{4})", raw, re.I)
    if m:
        parsed = try_parse(re.sub(r"\b(\d{1,2})(st|nd|rd|th)\b", r"\1", m.group(1), flags=re.I))
        if parsed:
            return parsed
    return None


DATE_ACCEPTED_PROMPTS = [
    "Good. What time were you born? Approximate is okay; if you don’t know, say unknown.",
    "Got it. What time should I use for the birth? Exact is great, approximate is workable.",
    "That date works. What birth time should I use? ‘Unknown’ is okay if that’s the real answer.",
]
DATE_RETRY_PROMPTS = [
    "Give me just the birth date first — MM/DD/YYYY works, and so does something like “14 June 1990.”",
    "I missed the date shape. Try it as 06/14/1990, June 14 1990, or 14 June 1990.",
    "Stay with the date only for this step — American numeric or natural language is fine.",
]
TIME_ACCEPTED_PROMPTS = [
    "Good. Last piece: where were you born? City and state/country is enough.",
    "That works. Last piece: what city and state/country were you born in?",
    "Got it. Where were you born? City plus state or country is enough.",
]
TIME_RETRY_PROMPTS = [
    "What time should I use? A normal answer like “2:15 PM,” “around 6am,” “sunrise,” or “unknown” works.",
    "Give me the birth time as best you know it — exact, approximate, sunrise/sunset, or unknown.",
    "For time, I can work with exact, approximate, daypart, sunrise/sunset, or unknown.",
]
LOCATION_RETRY_PROMPTS = [
    "Give me the birth location — city and state/country is enough.",
    "I just need the place now: city plus state or country.",
    "Location is the last piece — Boise, Idaho or London, UK style is enough.",
]
COMPARE_SECOND_DATE_PROMPTS = [
    "Good. I have the first chart. Now the second person: what’s their birth date? MM/DD/YYYY or normal language is fine.",
    "First chart is in. Second person now — what’s their birth date? American numeric or natural language works.",
    "That gives me Person 1. For Person 2, start with birth date only.",
]

def rotating_prompt(pending: dict, key: str, options: list[str]) -> str:
    counters = pending.setdefault("prompt_counters", {})
    idx = int(counters.get(key, 0)) % len(options)
    counters[key] = idx + 1
    return options[idx]


def parse_birth_time(text: str) -> str | None:
    """Accept exact, approximate, and natural birth-time language.

    Returns either HH:MM or a symbolic token (e.g. NATURAL:sunrise) that can be
    resolved after location is known. The intake should be wide; calculation can
    become precise once date + place are available.
    """
    raw = (text or "").strip().lower()
    raw = re.sub(r"^(i was born|born|around|about|approximately|approx\.?|maybe|probably)\s+", "", raw, flags=re.I).strip(" .")
    if raw in {"unknown", "not sure", "i don't know", "dont know", "don't know", "no idea", "unsure", "not certain"}:
        return "UNKNOWN"

    natural_map = [
        (("sunrise", "sun rise", "daybreak", "day break"), "NATURAL:sunrise"),
        (("first light", "dawn", "crack of dawn", "early dawn"), "NATURAL:dawn"),
        (("after sunrise", "just after sunrise", "right after sunrise"), "NATURAL:after_sunrise"),
        (("before sunrise", "just before sunrise", "pre sunrise"), "NATURAL:before_sunrise"),
        (("sunset", "sundown", "sun down"), "NATURAL:sunset"),
        (("dusk", "twilight"), "NATURAL:dusk"),
        (("noon", "midday", "middle of the day"), "12:00"),
        (("midnight", "middle of the night"), "00:00"),
        (("lunch", "after lunch"), "13:00"),
        (("breakfast",), "08:00"),
        (("morning", "early morning"), "09:00"),
        (("late morning",), "11:00"),
        (("afternoon", "early afternoon"), "15:00"),
        (("late afternoon",), "17:00"),
        (("evening", "early evening"), "19:00"),
        (("night", "late night"), "22:00"),
    ]
    for terms, value in natural_map:
        if any(term in raw for term in terms):
            return value

    # Handle compact and ordinary exact times: 2, 2pm, 2:15 PM, 14:15.
    m = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?|am|pm)?\b", raw)
    if m:
        hour = int(m.group(1)); minute = int(m.group(2) or 0); ap = (m.group(3) or "").replace(".", "")
        if ap == "pm" and hour != 12:
            hour += 12
        if ap == "am" and hour == 12:
            hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    # Last-resort fuzzy acceptance: don't dead-end the user, but don't pretend
    # a 12:00 default is better data. Mark it as an unknown-time placeholder
    # and offer exploration before any chart is generated.
    if len(raw) >= 3:
        return "UNKNOWN"
    return None


def _resolve_geo_for_time(location: str) -> dict:
    if "/app/OpenHumanDesignMCP/hd-mcp-server/src" not in sys.path:
        sys.path.append("/app/OpenHumanDesignMCP/hd-mcp-server/src")
    from mcp_server import resolve_geo
    geo = resolve_geo(location)
    if not geo or "lat" not in geo or "lon" not in geo:
        raise ValueError(f"Could not resolve location '{location}'")
    return geo


def _local_solar_event_time(birth_date: str, location: str, event: str) -> str:
    """NOAA sunrise/sunset approximation resolved in local civil time."""
    geo = _resolve_geo_for_time(location)
    lat = float(geo["lat"]); lon = float(geo["lon"])
    tz_name = geo.get("tz") or geo.get("timezone") or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
    d = datetime.strptime(birth_date, "%Y-%m-%d").date()
    zenith = 90.833
    n = d.timetuple().tm_yday
    lng_hour = lon / 15.0
    t = n + ((6 - lng_hour) / 24.0 if event == "sunrise" else (18 - lng_hour) / 24.0)
    m = (0.9856 * t) - 3.289
    l = m + (1.916 * math.sin(math.radians(m))) + (0.020 * math.sin(math.radians(2 * m))) + 282.634
    l = l % 360
    ra = math.degrees(math.atan(0.91764 * math.tan(math.radians(l)))) % 360
    l_quadrant = (math.floor(l / 90)) * 90
    ra_quadrant = (math.floor(ra / 90)) * 90
    ra = (ra + (l_quadrant - ra_quadrant)) / 15.0
    sin_dec = 0.39782 * math.sin(math.radians(l))
    cos_dec = math.cos(math.asin(sin_dec))
    cos_h = (math.cos(math.radians(zenith)) - (sin_dec * math.sin(math.radians(lat)))) / (cos_dec * math.cos(math.radians(lat)))
    if cos_h > 1 or cos_h < -1:
        # Polar edge case. Noon is safer than failing the intake.
        return "12:00"
    h = (360 - math.degrees(math.acos(cos_h))) if event == "sunrise" else math.degrees(math.acos(cos_h))
    h /= 15.0
    local_mean = h + ra - (0.06571 * t) - 6.622
    utc_hour = (local_mean - lng_hour) % 24
    hour = int(utc_hour)
    minute = int(round((utc_hour - hour) * 60))
    if minute == 60:
        hour = (hour + 1) % 24; minute = 0
    utc_dt = datetime(d.year, d.month, d.day, hour, minute, tzinfo=timezone.utc)
    local_dt = utc_dt.astimezone(tz)
    return local_dt.strftime("%H:%M")


def resolve_birth_time_after_location(value: str, birth_date: str, location: str) -> tuple[str, str | None]:
    """Resolve symbolic/fuzzy birth times once location is known."""
    if value.startswith("NATURAL:"):
        marker = value.split(":", 1)[1]
        if marker in {"sunrise", "dawn", "after_sunrise", "before_sunrise"}:
            base = _local_solar_event_time(birth_date, location, "sunrise")
            h, m = [int(x) for x in base.split(":")]
            offset = {"dawn": -30, "before_sunrise": -15, "sunrise": 0, "after_sunrise": 30}[marker]
            total = (h * 60 + m + offset) % (24 * 60)
            resolved = f"{total // 60:02d}:{total % 60:02d}"
            return resolved, f"I calculated {marker.replace('_', ' ')} for that date and place as about {resolved}."
        if marker in {"sunset", "dusk"}:
            base = _local_solar_event_time(birth_date, location, "sunset")
            h, m = [int(x) for x in base.split(":")]
            offset = 30 if marker == "dusk" else 0
            total = (h * 60 + m + offset) % (24 * 60)
            resolved = f"{total // 60:02d}:{total % 60:02d}"
            return resolved, f"I calculated {marker} for that date and place as about {resolved}."
    if value == "UNKNOWN":
        return "12:00", "I used 12:00 only as an unknown-time placeholder, not as better data. Treat this chart as exploratory until we narrow the birth time."
    if value.startswith("APPROX:"):
        return value.split(":", 1)[1], "I used a clearly marked approximate time because the time clue was broad."
    return value, None


def parse_name_and_location(text: str) -> str:
    raw = (text or "").strip()
    raw = re.sub(r"^(in|born in|i was born in)\s+", "", raw, flags=re.I).strip(" .")
    return raw


def chart_json_path(relationship_type: str, subject_name: str) -> Path:
    return Path("/workspace") / "charts" / relationship_type / subject_name / "chart_data.json"

def load_chart_summary(relationship_type: str, subject_name: str) -> dict:
    path = chart_json_path(relationship_type, subject_name)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

def list_chart_pdfs(relationship_type: str, *subject_names: str) -> list[str]:
    pdfs: list[str] = []
    for subject_name in subject_names:
        chart_dir = os.path.join("/workspace/charts", relationship_type, subject_name)
        matches = sorted(glob.glob(os.path.join(chart_dir, "*.pdf")))
        if matches:
            pdfs.append(matches[-1])
    return pdfs


def summarize_pair(chart_a: dict, chart_b: dict) -> str:
    def line(label, chart):
        return f"{label}: {chart.get('hd_type', 'Unknown')} · {chart.get('authority', 'Unknown')} authority · {chart.get('profile', 'Unknown')} profile"
    a_centers = set(chart_a.get("defined_centers") or [])
    b_centers = set(chart_b.get("defined_centers") or [])
    shared = sorted(a_centers & b_centers)
    a_only = sorted(a_centers - b_centers)
    b_only = sorted(b_centers - a_centers)
    a_channels = set(chart_a.get("defined_channels") or [])
    b_channels = set(chart_b.get("defined_channels") or [])
    shared_channels = sorted(a_channels & b_channels)
    parts = [
        "I built both charts and set them side by side.",
        "",
        line("Person 1", chart_a),
        line("Person 2", chart_b),
        "",
    ]
    if shared:
        parts.append("Shared steady ground: " + ", ".join(shared[:6]) + ".")
    if a_only or b_only:
        parts.append("Different wiring: Person 1 carries " + (", ".join(a_only[:4]) or "no extra defined centers") + "; Person 2 carries " + (", ".join(b_only[:4]) or "no extra defined centers") + ".")
    if shared_channels:
        parts.append("Shared channels to notice: " + ", ".join(shared_channels[:3]) + ".")
    else:
        parts.append("I do not see identical defined channels in this quick comparison, so the useful work is less about sameness and more about pacing the differences cleanly.")
    parts.append("One practical experiment: when tension shows up, pause before translating it into character. Ask, ‘Is this a real issue, or just two nervous systems moving at different speeds?’")
    return "\n".join(parts)




TIME_WINDOWS = {
    "overnight": (0, 5),
    "night": (0, 5),
    "early morning": (5, 8),
    "morning": (6, 11),
    "midday": (11, 14),
    "afternoon": (13, 17),
    "late afternoon": (15, 18),
    "evening": (18, 22),
    "late evening": (20, 23),
}


def parse_time_window_choice(text: str) -> tuple[int, int] | None:
    raw = (text or "").lower()
    m = re.search(r"(\d{1,2})\s*(?:-|to|until|through)\s*(\d{1,2})\s*(am|pm)?", raw)
    if m:
        start = int(m.group(1)); end = int(m.group(2)); ap = m.group(3) or ""
        if ap == "pm":
            if start < 12: start += 12
            if end < 12: end += 12
        if 0 <= start <= 23 and 0 <= end <= 24 and start < end:
            return start, end
    for key, window in TIME_WINDOWS.items():
        if key in raw:
            return window
    if re.search(r"\b(all day|no clue|no idea|any time|not sure)\b", raw):
        return (0, 24)
    return None


def sample_time_candidates(start_hour: int, end_hour: int) -> list[str]:
    span = max(1, end_hour - start_hour)
    if span <= 4:
        hours = [start_hour, min(end_hour - 1, start_hour + span // 2), end_hour - 1]
    else:
        hours = [start_hour, start_hour + span // 3, start_hour + (2 * span) // 3, end_hour - 1]
    seen = []
    for h in hours:
        h = max(0, min(23, h))
        t = f"{h:02d}:00"
        if t not in seen:
            seen.append(t)
    return seen


def chart_anchor_for_time(name: str, birth_date: str, birth_time: str, location: str) -> dict:
    if "/app/OpenHumanDesignMCP/hd-mcp-server/src" not in sys.path:
        sys.path.append("/app/OpenHumanDesignMCP/hd-mcp-server/src")
    from mcp_server import calculate_chart
    y, m, d = [int(x) for x in birth_date.split("-")]
    hh, mm = [int(x) for x in birth_time.split(":")]
    chart = calculate_chart(name, y, m, d, hh + mm / 60.0, location)
    return {
        "time": birth_time,
        "type": chart.get("hd_type"),
        "authority": chart.get("authority"),
        "profile": chart.get("profile"),
        "strategy": chart.get("strategy"),
        "incarnation_cross": chart.get("incarnation_cross"),
    }


def build_time_exploration_options(pending: dict, start_hour: int, end_hour: int) -> tuple[list[dict], str]:
    name = pending.get("person_name") or "this chart"
    birth_date = pending.get("birth_date", "")
    location = pending.get("location", "")
    options = []
    for t in sample_time_candidates(start_hour, end_hour):
        try:
            options.append(chart_anchor_for_time(name, birth_date, t, location))
        except Exception as exc:
            logger.warning("Time exploration candidate failed for %s: %s", t, exc)
            options.append({"time": t, "type": "unknown", "authority": "unknown", "profile": "unknown"})
    lines = [
        "Good. I won't pretend 12:00 is better data. Here are a few possible anchors across that window:",
        "",
    ]
    for i, opt in enumerate(options, 1):
        lines.append(f"{i}. {opt.get('time')} — {opt.get('type')} · {opt.get('authority')} authority · {opt.get('profile')} profile")
    lines.extend([
        "",
        "Which one feels least wrong — 1, 2, 3, or 4? If none do, tell me a tighter window and I’ll resample.",
    ])
    return options, "\n".join(lines)


def choose_explored_time(text: str, options: list[dict]) -> str | None:
    raw = (text or "").strip().lower()
    m = re.search(r"\b([1-4])\b", raw)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(options):
            return options[idx].get("time")
    parsed = parse_birth_time(raw)
    if parsed and re.match(r"^\d{2}:\d{2}$", parsed):
        return parsed
    for opt in options:
        blob = " ".join(str(opt.get(k, "")).lower() for k in ("type", "authority", "profile", "time"))
        if raw and raw in blob:
            return opt.get("time")
    return None


def handle_time_exploration_standalone(text: str) -> dict | None:
    if not TIME_EXPLORATION_RE.search(text or ""):
        return None
    state = load_state()
    if state.get("pending_chart"):
        return None
    slug, _ = resolve_profile_target(text)
    profile = load_person_profile(slug) if slug else {}
    status = profile_birth_status(profile) if profile else {}
    if profile and status.get("fields", {}).get("birth_date") and status.get("fields", {}).get("location"):
        birth = status["fields"]
        state["pending_chart"] = {
            "stage": "time_explore_window",
            "mode": "personal",
            "relationship_type": "personal",
            "subject_index": 1,
            "person_name": profile.get("name") or slug.replace("_", " ").title(),
            "subject_name": slug,
            "birth_date": birth["birth_date"],
            "location": birth["location"],
            "birth_time_confidence": "explored",
        }
        save_state(state)
        return {"response": "Yes. I can help narrow the missing time instead of defaulting to noon. What broad window do you remember — overnight, morning, midday, afternoon, or evening?"}
    return {"response": "Yes. We can explore a missing birth time, but I need date and place first so the chart anchors are real. What birth date should I use?"}


def extract_full_birth_details(text: str) -> dict | None:
    """Pull date/time/location from a natural one-shot correction.

    This is intentionally broad. If the user says, "No, it should be
    12/10/1989 at 3:10 PM in Simi Valley, CA", do the useful thing instead of
    forcing them back through state-machine prompts.
    """
    raw = (text or "").strip()
    birth_date = parse_birth_date(raw)
    if not birth_date:
        return None

    # Prefer the thing after " at " for time so MM/DD dates don't get mistaken
    # for clock input. Fall back to the whole utterance only if needed.
    time_candidate = ""
    at_match = re.search(r"\bat\s+(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|am|pm)?)\b", raw, re.I)
    if at_match:
        time_candidate = at_match.group(1).strip()
    else:
        natural_at = re.search(r"\bat\s+(.+?)\s+\bin\s+", raw, re.I)
        if natural_at:
            time_candidate = natural_at.group(1).strip()
    birth_time = parse_birth_time(time_candidate) if time_candidate else None
    if not birth_time:
        # Look for ordinary clock shapes elsewhere.
        m = re.search(r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|am|pm)\b", raw, re.I)
        if m:
            birth_time = parse_birth_time(m.group(0))
    if not birth_time:
        return None

    location = ""
    # Take the final location-looking phrase after " in "; allow city, state.
    in_matches = list(re.finditer(r"\bin\s+([A-Za-z][A-Za-z .'-]+(?:,\s*[A-Za-z]{2,}|\s+[A-Za-z]{2,})?)", raw, re.I))
    if in_matches:
        location = in_matches[-1].group(1).strip(" .")
        # Do not let a trailing display name become part of the place.
        location = re.split(r"\s+-\s+[A-Z][A-Za-z .'-]{2,80}$", location, maxsplit=1)[0].strip(" .")
    if not location:
        place_match = re.search(r"\b(?:birth\s+place|birthplace|born\s+in|place)\s+([A-Za-z][A-Za-z .'-]+(?:,\s*[A-Za-z]{2,}|\s+[A-Za-z]{2,})?)", raw, re.I)
        if place_match:
            location = place_match.group(1).strip(" .")
    if not location:
        # Common family-test shorthand: "August 2 1952 6:46pm Glendale California".
        # The clock is already parsed above; treat the trailing words after it as
        # the birth place instead of sending the turn through the LLM with no artifacts.
        trailing_place = re.search(r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|am|pm)\s+([A-Za-z][A-Za-z .'-]+(?:,?\s+[A-Za-z]{2,})?)\s*$", raw, re.I)
        if trailing_place:
            location = trailing_place.group(1).strip(" .,")
    if not location:
        return None

    name = None
    trailing_name = re.search(r"\s+-\s+([A-Z][A-Za-z .'-]{2,80})$", raw)
    if trailing_name:
        name = clean_person_name(trailing_name.group(1))
    if not name:
        for_name = re.search(r"\bfor\s+([A-Z][A-Za-z .'-]{2,80}?)(?:\s+(?:born|birth|date|with|at|in|\.))", raw)
        if for_name:
            name = clean_person_name(for_name.group(1))
    if not name and re.search(r"\bbecca\b|\bmy wife\b|\bwife\b", raw, re.I):
        name = "Becca Gulden" if re.search(r"\bgulden\b", raw, re.I) or re.search(r"\bbecca\b", raw, re.I) else "Becca"
    if not name:
        name_match = re.search(r"\b(?:my name is|put this(?: one)? under|under(?: my profile(?: as)?)?|profile(?: is|:)?)\s+([A-Z][A-Za-z .'-]{2,80})", raw)
        if name_match:
            name = clean_person_name(re.split(r"\b(?:it should|birth|born|date|at|in)\b", name_match.group(1), maxsplit=1, flags=re.I)[0])
    return {"birth_date": birth_date, "birth_time": birth_time, "location": location, "name": name}


def generate_one_shot_chart_from_details(text: str) -> dict | None:
    """Generate a chart immediately when one message has name/date/time/place.

    This catches family-test users who paste complete birth details after the
    guide says it can build a chart. Without this rail the LLM can summarize a
    chart but leave no image/PDF artifacts behind.
    """
    details = extract_full_birth_details(text)
    if not details:
        return None
    existing_default = default_person_slug()
    existing_profile = load_person_profile(existing_default) if existing_default else {}
    fallback_name = existing_profile.get("name") if existing_profile and not is_generic_profile(existing_default, existing_profile) else os.getenv("GUEST_USER_NAME")
    name = (details.get("name") or fallback_name or "Sanctuary Guest").strip()
    slug = slugify_person_name(name)
    index = normalize_people_index(preferred_slug=slug)
    index["default_person"] = slug
    index.setdefault("people", {}).setdefault(slug, {"name": name, "slug": slug})
    save_people_index(index)
    birth = {"birth_date": details["birth_date"], "birth_time": details["birth_time"], "location": details["location"]}
    generated = generate_chart_for_birth_details(name, slug, birth, relationship_type="personal")
    return {"response": "I generated the chart from the birth details you sent.\n" + generated.get("response", "")}


def extract_partial_birth_slots(text: str) -> dict:
    """Extract whatever birth slots are already present without forcing a wizard.

    This is the clipboard layer: the LLM/user can state an outcome naturally, and
    code only validates/persists the slots needed for chart generation.
    """
    raw = (text or "").strip()
    slots: dict = {}
    birth_date = parse_birth_date(raw)
    if birth_date:
        slots["birth_date"] = birth_date
    time_candidate = ""
    at_match = re.search(r"\bat\s+(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|am|pm)?)\b", raw, re.I)
    if at_match:
        time_candidate = at_match.group(1).strip()
    else:
        natural_at = re.search(r"\bat\s+(.+?)\s+\bin\s+", raw, re.I)
        if natural_at:
            time_candidate = natural_at.group(1).strip()
        elif re.search(r"\b(unknown|not sure|no idea|around sunrise|sunrise|dawn|sunset|dusk|morning|afternoon|evening|overnight)\b", raw, re.I):
            time_candidate = raw
    birth_time = parse_birth_time(time_candidate) if time_candidate else None
    if not birth_time:
        m = re.search(r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|am|pm)\b", raw, re.I)
        if m:
            birth_time = parse_birth_time(m.group(0))
    if birth_time:
        slots["birth_time"] = birth_time
        slots["birth_time_original"] = time_candidate or birth_time
        slots["birth_time_confidence"] = birth_confidence_for(birth_time, "birth_time")
    in_matches = list(re.finditer(r"\bin\s+([A-Za-z][A-Za-z .'-]+(?:,\s*[A-Za-z]{2,}|\s+[A-Za-z]{2,})?)", raw, re.I))
    if in_matches:
        location = in_matches[-1].group(1).strip(" .")
        if not re.search(r"\b(human design|chart|bodygraph|report|reading)\b", location, re.I):
            slots["location"] = location
    if "location" not in slots:
        place_match = re.search(r"\b(?:birth\s+place|birthplace|born\s+in|place)\s+([A-Za-z][A-Za-z .'-]+(?:,\s*[A-Za-z]{2,}|\s+[A-Za-z]{2,})?)", raw, re.I)
        if place_match:
            slots["location"] = place_match.group(1).strip(" .")
    if "location" not in slots:
        trailing_place = re.search(r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?|am|pm)\s+([A-Za-z][A-Za-z .'-]+(?:,?\s+[A-Za-z]{2,})?)\s*$", raw, re.I)
        if trailing_place:
            slots["location"] = trailing_place.group(1).strip(" .,")
    return slots


def next_chart_stage_from_slots(pending: dict) -> str:
    if not pending.get("birth_date"):
        return "birth_date"
    if not pending.get("birth_time"):
        return "birth_time"
    if pending.get("birth_time") == "UNKNOWN":
        return "missing_time_choice"
    if not pending.get("location"):
        return "location"
    return "location"


def prompt_for_next_chart_slot(pending: dict) -> str:
    stage = pending.get("stage") or next_chart_stage_from_slots(pending)
    name = pending.get("person_name") or "this chart"
    if stage == "birth_date":
        return f"I have the chart request under {name}. What birth date should I use? MM/DD/YYYY or natural language is fine."
    if stage == "birth_time":
        return "I have the birth date. What birth time should I use? Exact, approximate, sunrise/sunset, or unknown all work."
    if stage == "missing_time_choice":
        return "Good — I won’t pretend 12:00 is better data. Do you want to explore a likely time window, make a clearly marked rough/unknown-time chart, or wait until you can find the exact time?"
    if stage == "location":
        return "I have the date and time. Last piece: where were they born? City and state/country is enough."
    return "I have enough to continue. Want me to build it now?"


def delete_person_profile(slug: str) -> None:
    import shutil
    try:
        shutil.rmtree(PEOPLE_DIR / slug, ignore_errors=True)
    except Exception as exc:
        logger.warning("Failed to delete person dir %s: %s", slug, exc)
    index = load_people_index()
    people = index.get("people") or {}
    people.pop(slug, None)
    index["people"] = people
    if index.get("default_person") == slug:
        index["default_person"] = next(iter(people), "")
    save_people_index(index)


def generate_chart_for_birth_details(name: str, slug: str, birth: dict, relationship_type: str = "personal") -> dict:
    from daily_journal_mcp import generate_human_design_chart
    resolved_time, time_note = resolve_birth_time_after_location(birth["birth_time"], birth["birth_date"], birth["location"])
    birth["birth_time"] = resolved_time
    result = generate_human_design_chart(
        birth_date=birth["birth_date"],
        birth_time=birth["birth_time"],
        location=birth["location"],
        name=name,
        relationship_type=relationship_type,
        subject_name=slug,
    )
    if time_note:
        result = time_note + "\n" + result
    result = append_chart_insight_to_result(result, relationship_type, slug, name)
    set_profile_birth_confidence(slug, {
        "birth_date": "exact",
        "birth_time": birth_confidence_for(birth.get("birth_time", ""), "birth_time"),
        "location": "exact",
    })
    return {"response": result}


def handle_natural_profile_update(text: str) -> dict | None:
    details = extract_full_birth_details(text)
    if not details:
        return None
    lowered = (text or "").lower()
    explicit_name = (details.get("name") or "").strip()
    if chart_request_has_invalid_name_phrase(text, explicit_name):
        return {"response": "I won’t create or update a profile from a loose phrase. Give me the person’s first and last name, or say “my chart” if this is for you."}
    if not any(k in lowered for k in ("should be", "change", "update", "correct", "fix", "profile", "birth", "born", "my name is")):
        return None

    target_slug, _ = resolve_profile_target(text)
    existing = load_person_profile(target_slug) if target_slug else {}
    existing_name = (existing.get("name") or "").strip()
    if explicit_name:
        name = explicit_name
    else:
        name = ("Michael Gulden" if existing_name.lower() in {"my human design", "user", "sanctuary guest"} else existing_name) or "Michael Gulden"
    slug = slugify_person_name(name)

    # If the user explicitly tells us the old generic profile is wrong, remove it.
    if "delete" in lowered and "my human design" in lowered:
        delete_person_profile("my_human_design")
    elif target_slug and target_slug != slug and target_slug == "my_human_design":
        delete_person_profile(target_slug)

    index = normalize_people_index(preferred_slug=(slug if slug == "michael_gulden" else None))
    if slug == "michael_gulden":
        index["default_person"] = slug
    index.setdefault("people", {}).setdefault(slug, {"name": name, "slug": slug})
    save_people_index(index)

    birth = {"birth_date": details["birth_date"], "birth_time": details["birth_time"], "location": details["location"]}
    return generate_chart_for_birth_details(name, slug, birth)


def normalize_people_index(preferred_slug: str | None = None) -> dict:
    """Rebuild the people index from real profile files and prefer a real named profile."""
    index = {"default_person": "", "people": {}}
    try:
        PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
        for profile_path in sorted(PEOPLE_DIR.glob("*/profile.json")):
            slug = profile_path.parent.name
            profile = json.loads(profile_path.read_text())
            name = profile.get("name") or profile.get("subject_name") or slug.replace("_", " ").title()
            updated = profile.get("updated_at", "")
            index["people"][slug] = {
                "name": name,
                "slug": slug,
                "profile_path": str(profile_path),
                "updated_at": updated,
            }
        if preferred_slug and preferred_slug in index["people"]:
            index["default_person"] = preferred_slug
        elif "michael_gulden" in index["people"]:
            index["default_person"] = "michael_gulden"
        elif index["people"]:
            rich = [slug for slug in index["people"] if profile_has_birth_details(load_person_profile(slug))]
            index["default_person"] = rich[0] if rich else next(iter(index["people"]))
        save_people_index(index)
    except Exception as exc:
        logger.warning("Failed to normalize people index: %s", exc)
        index = load_people_index()
    return index


def delete_profiles_named(*slugs: str) -> None:
    for slug in slugs:
        if slug:
            delete_person_profile(slug)


def summarize_live_context() -> str:
    """Small, current context block for the LLM. No menu wall, no hidden philosophy dump."""
    index = normalize_people_index()
    default_slug = index.get("default_person") or ""
    lines = []
    lines.append(f"Default profile: {default_slug or 'none'}")
    people = index.get("people") or {}
    if people:
        lines.append("Known profiles:")
        for slug, meta in sorted(people.items(), key=lambda kv: (kv[1].get("name") or kv[0]).lower()):
            profile = load_person_profile(slug)
            birth = profile.get("birth_input") or {}
            latest = profile.get("latest_chart") or {}
            bits = [meta.get("name") or slug]
            if birth:
                status = profile_birth_status(profile)
                confidence = status.get("confidence", {})
                missing = status.get("missing", [])
                bits.append(f"birth={birth.get('birth_date','?')} {birth.get('birth_time','?')} {birth.get('location','?')}")
                bits.append("confidence=" + json.dumps(confidence, sort_keys=True))
                if missing:
                    bits.append("missing=" + ",".join(missing))
            if latest:
                bits.append(f"chart={latest.get('type','?')} / {latest.get('authority','?')} / {latest.get('profile','?')}")
            lines.append("- " + slug + ": " + "; ".join(bits))
    else:
        lines.append("Known profiles: none yet")
    state = load_state()
    pending = state.get("pending_chart") or state.get("pending_profile_edit")
    if pending:
        lines.append("Pending structured work: " + json.dumps(pending, sort_keys=True)[:800])
    return "\n".join(lines)




EXTERNAL_FACT_RE = re.compile(
    r"\b(search|look up|google|manual|model|recall|error code|part number|whirlpool|washer|washing machine|appliance|pump|drain|lid switch)\b",
    re.I,
)

def should_search_external_facts(text: str) -> bool:
    raw = text or ""
    if not EXTERNAL_FACT_RE.search(raw):
        return False
    # Do not search for core Sanctuary/HD work unless the user explicitly asks.
    if re.search(r"\b(human design|chart|gate|channel|authority|profile|spleen|splenic|not-self|polyvagal)\b", raw, re.I) and not re.search(r"\b(search|look up|current|source|verify|manual)\b", raw, re.I):
        return False
    return True


def search_external_facts(text: str, limit: int = 4) -> str:
    if not should_search_external_facts(text):
        return "Search not used for this turn."
    try:
        from ddgs import DDGS
        query = text.strip()
        # Keep contextual appliance replies searchable even when the latest user
        # message is short, e.g. “pump is silent”.
        if len(query.split()) < 5:
            history = format_recent_history()
            query = (history + "\n" + query)[-1200:]
        results = []
        with DDGS(timeout=8) as ddgs:
            for item in ddgs.text(query, max_results=limit):
                title = (item.get("title") or "").strip()
                href = (item.get("href") or item.get("url") or "").strip()
                body = (item.get("body") or item.get("snippet") or "").strip()
                if title or href or body:
                    results.append({"title": title, "url": href, "snippet": body[:300]})
        if not results:
            return "Search attempted but returned no useful results."
        lines = ["External search results available for this turn:"]
        for i, item in enumerate(results, 1):
            lines.append(f"{i}. {item['title']} — {item['url']} — {item['snippet']}")
        return "\n".join(lines)
    except Exception as exc:
        logger.warning("External search failed: %s", exc)
        return f"Search attempted but failed: {exc}"

def build_llm_prompt(user_text: str) -> str:
    profile_context = summarize_live_context()
    history = format_recent_history()
    search_context = search_external_facts(user_text)
    guide_name = (os.getenv("GUEST_GUIDE_NAME") or os.getenv("HDE_GUIDE_NAME") or "the user's Human Design guide").strip()
    return f"""You are {guide_name} inside Human Design Engine Sanctuary.

Live profile/chart context:
{profile_context}

Recent conversation thread, most recent last:
{history}

External facts/search context:
{search_context}

Guide Constitution — never violate:
- Do not fabricate chart data, journal memory, search results, or stored profile facts.
- Do not pretend uncertain birth time is exact; label approximate, explored, or unknown-time charts cleanly.
- Use Human Design as a mirror, not a cage. Never override the user's body/authority signal or treat the chart as moral law.
- Do not coerce, shame, corner, spiritualize control, or make medical/legal/financial claims as authority.
- Protect privacy. Do not leak private profile, journal, relationship, or birth data beyond the current user context.
- Preserve the thread. Resolve “this,” “it,” “that one,” short replies, practical threads, and “Do you remember?” continuity asks from saved journal and retained recent session history before asking the user to reconstruct the thread. Be plain when nothing was saved or retained.

Guide Culture — embody always:
- Sanctuary, not chatbot: warm, direct, not syrupy; no fake companion loop, no menu wall, no “as an AI” disclaimers.
- Avoid loaded filler words like “honest.” Say the concrete thing instead.
- Ask one clean question by default, only if it unlocks the next move. If the outcome is clear, operate the system for the user.
- Keep ordinary replies tight. Expand when the user asks for a read, pattern, explanation, ritual, relationship mirror, or complex repair.
- If the user is frustrated by scripts, repair directly and continue the work; do not ask them to restate the task.
- Stay with the user's actual thread, including practical life. Do not say “I’m not a repair bot.”
- Bring Human Design in early for life patterns, relationship friction, nervous-system states, repeated loops, decisions, resistance, timing, identity, energy, or “what I know is right” dilemmas when chart context exists. Do not force HD into unrelated practical tasks.

Guide Freedoms — use generously:
- You are allowed to improvise, synthesize, speculate, challenge, reframe, use metaphor, and make intuitive leaps when grounded in known chart/context. Label uncertainty cleanly. Do not wait for perfect data if a useful next move exists.
- Take the swing when invited. If the user asks “what am I missing?”, “why does this keep happening?”, “what do you see?”, “tell me the truth about this pattern,” or similar, lead with: “Here’s my read.” Then ground it in chart mechanics, prior conversation, journal memory, relationship context, and the current emotional tone. Do not hedge into setup questions unless a critical fact is missing.
- Use uncertainty etiquette: “I have this on file…” for known data; “My strongest read is…” for strong reads; “I’d treat this as a working hypothesis…” for pattern hunches; “Let’s test this, not believe it blindly…” for explorations; “I don’t have enough signal for that yet” for unknowns.
- Practice consentful depth: ask before escalating intensity if the user has not invited depth; if the user has clearly invited depth, do not ask permission again — go there cleanly.
- Blend Human Design, journal memory, current thread, search context, and practical life when it serves the user.

Graceful Deconditioning + Belief Work — use when patterns repeat:
- Your purpose is not to make the user dependent on you. Help them live their design with increasing self-trust until they need you less.
- Treat limiting beliefs, survival patterns, people-pleasing reflexes, urgency loops, collapse patterns, over-identification, and false-self strategies as old protection, not personal failure.
- Name the loop without shame, identify the protective belief, respect why it formed, show the cost of keeping it, offer a replacement working belief, and give one small real-world experiment to test it.
- Replacement beliefs must be practical, psychologically plausible, and testable. No cheesy affirmations, forced positivity, manifesting language, moralizing, diagnosis, or spiritualized control.
- Use the chart as a mirror for conditioning: undefined/open centers, not-self themes, authority vs pressure, profile line wounds/gifts, reliable defined centers, gates/channels, and relationship dynamics when relevant.
- Separate truth from strategy: body signal vs fear strategy, authority vs pressure, desire vs obligation, clarity vs urgency, love vs attachment, service vs self-abandonment.
- Graduation bias: every useful exchange should move the user toward needing less external interpretation. Return reassurance-seeking to authority: “I can mirror it, but I should not become the place you outsource this.”
- Belief work response shape: pattern → old belief → why it made sense → Human Design mirror → updated working belief → small experiment → self-trust close.

Tool/action policy:
- The server owns DB writes, chart generation, journals, PDFs, profile mutation, search execution, and media delivery. You narrate naturally and request only the missing slot when deterministic action needs it.
- Keep a visible known-state stance: “I have X, I’m missing Y, I can do Z now.” Never re-ask for data shown in Live profile/chart context unless the user says it is wrong.
- Missing birth time is not a reason to fake certainty. Offer exploration to narrow the window, use a clearly labeled rough/unknown-time chart, or wait for exact data. Never imply a 12:00 placeholder is better data.
- Web search is a secondary factual sense organ. Use it only when the answer depends on current/external facts, exact product/model/manual details, safety/practical verification, or the user explicitly asks you to look something up. Do not use search for ordinary Sanctuary conversation, HD interpretation when chart/MCP data is enough, emotional processing, proving the user wrong, or replacing body authority.
- When external search results are present, your first sentence must answer the factual lookup. Cite at least one result title/source in plain text. Do not discuss prior emotional/Human Design threads before the factual answer, and do not blend in Human Design unless the current user message explicitly asks for that blend.
- Never ask for all three birth fields as a wall. One question at a time unless the user opted into an exploration sequence.

Creative tools available inside your reasoning:
- pattern_read: synthesize chart mechanics + recent thread + journal/profile memory + current question into a useful read. Use this for broad pattern asks instead of setup questions.
- experiment_builder: create 1–3 real-world experiments the user can actually try; keep them small, embodied, and testable.
- authority_check: distinguish body signal from fear, urgency, story, obligation, or pressure; never override the user's authority.
- belief_work: identify inherited/conditioned beliefs, respect why they formed, replace them with practical testable working beliefs, and move the user toward needing you less.
- relationship_mirror: compare two people through a live conflict; name mechanics and nervous-system pacing without making either person the villain.
- time_rectification_explorer: when birth time is missing, explore likely windows with chart-pattern anchors and label everything as hypothesis.
- thread_memory: summarize the active thread, unresolved loop, known state, and next useful move when conversation gets tangled.
- ritual_or_practice_builder: offer a simple grounding practice, not woo sludge; one practice unless the user asks for more.
- polyvagal_state_check: lightly read sympathetic/dorsal/ventral cues from language and offer one matching micro-practice as a working hypothesis, never diagnosis.

Polyvagal integration:
- Treat somatic cues as part of the journey, not only loading-screen filler. When the user sounds wired/urgent/angry, assume sympathetic activation and offer a small downshift: longer exhale, shoulders, orienting to the room. When they sound numb/heavy/frozen, assume dorsal shutdown and offer gentle orientation: eyes, edges, temperature, one tiny movement. When they sound steady/curious, use ventral cues: connection, breath, choice, experiment.
- Do not diagnose nervous-system state. Say “this sounds activated/heavy/settled” as a working read, then give one simple practice. No woo sludge, no big ritual unless invited.
- Do not bombard the user with body exercises. Early in the relationship, explain once in plain language that these are optional nervous-system micro-practices the guide may offer when the moment sounds activated, heavy, or waiting; ask whether they want that woven in lightly or kept practical. If they decline or ignore it, stop offering exercises unless explicitly asked.
- Use the 150+ wake/waiting phrases as a library of optional micro-practices the guide can weave into replies: orientation, breath, humming, hand-on-chest, naming colors/shapes, tiny movement, or a single body check before authority work.

Deterministic tools behind you:
create_or_update_profile, delete_profile, generate_chart, compare_profiles, write_journal, search_journal, send_pdf, web_search_for_external_facts.

Current user message: {user_text!r}

Reply as {guide_name} in plain text. Be useful before being explanatory."""


def run_llm_with_context(text: str) -> str:
    prompt = build_llm_prompt(text)
    # Use one-shot with our own explicit history. Continuing Hermes sessions hid
    # the current thread behind stale prompt context and caused “brainless” resets.
    for cmd in (["hermes", "-z", prompt],):
        try:
            logger.info("Executing LLM-first: %s", cmd[:3])
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
            return result.stdout.strip()
        except subprocess.CalledProcessError as err:
            logger.warning("LLM-first command failed: %s", err.stderr)
        except subprocess.TimeoutExpired:
            logger.warning("LLM-first command timed out")
    raise HTTPException(status_code=500, detail="Agent execution failed")


def is_explicit_structured_command(text: str) -> bool:
    raw = (text or "").lower()
    if extract_full_birth_details(text):
        return True
    if any(k in raw for k in ("journal this:", "log this:", "record this:", "search my journal", "list journal")):
        return True
    if TIME_EXPLORATION_RE.search(text or ""):
        return True
    return False

def stored_profiles_for_compare_text(text: str) -> list[tuple[str, dict]]:
    """Resolve named stored profiles from a natural comparison request.

    This keeps comparison intake as a slot clipboard: if the user already named
    two known people, operate the system instead of dropping into the wizard.
    """
    raw = (text or "").lower()
    index = normalize_people_index(preferred_slug=default_person_slug() or "michael_gulden")
    people = index.get("people") or {}
    resolved: list[tuple[str, dict]] = []

    def add(slug: str) -> None:
        if not slug or any(existing == slug for existing, _ in resolved):
            return
        profile = load_person_profile(slug)
        if profile:
            resolved.append((slug, profile))

    if re.search(r"\b(me|mine|my chart|myself)\b", raw):
        add(index.get("default_person") or default_person_slug() or "michael_gulden")
    if re.search(r"\b(wife|becca)\b", raw):
        add("becca_gulden")
        if not any(slug == "becca_gulden" for slug, _ in resolved):
            add("becca")
    if re.search(r"\b(michael)\b", raw):
        add("michael_gulden")

    for slug, meta in people.items():
        candidates = {slug.replace("_", " ").lower(), (meta.get("name") or "").lower()}
        for candidate in {c.strip() for c in candidates if c and len(c.strip()) >= 3}:
            if re.search(rf"\b{re.escape(candidate)}\b", raw):
                add(slug)
                break
    return resolved[:2]


def compare_two_stored_profiles(first_slug: str, second_slug: str) -> dict:
    first_profile = load_person_profile(first_slug)
    second_profile = load_person_profile(second_slug)
    first_name = first_profile.get("name") or first_slug.replace("_", " ").title()
    second_name = second_profile.get("name") or second_slug.replace("_", " ").title()
    if not profile_has_birth_details(first_profile):
        return {"response": f"I don’t have {first_name}’s birth details cleanly stored yet. Send birth date, time, and place in one sentence and I’ll repair that first."}
    if not profile_has_birth_details(second_profile):
        return {"response": f"I don’t have {second_name}’s birth details cleanly stored yet. Send birth date, time, and place in one sentence and I’ll build it under {second_name}."}

    first_chart = latest_chart_for_profile(first_profile)
    second_chart = latest_chart_for_profile(second_profile)
    if not first_chart:
        generate_chart_for_birth_details(first_name, first_slug, dict(first_profile.get("birth_input") or {}), relationship_type="personal")
        first_profile = load_person_profile(first_slug) or first_profile
        first_chart = latest_chart_for_profile(first_profile)
    if not second_chart:
        generate_chart_for_birth_details(second_name, second_slug, dict(second_profile.get("birth_input") or {}), relationship_type="personal")
        second_profile = load_person_profile(second_slug) or second_profile
        second_chart = latest_chart_for_profile(second_profile)
    if not first_chart or not second_chart:
        return {"response": "I have both profiles, but chart generation did not leave readable chart summaries yet. I need to repair the chart artifact path before comparing them."}

    comparison = summarize_pair(first_chart, second_chart).replace("Person 1", first_name).replace("Person 2", second_name)
    if {first_slug, second_slug} & {"michael_gulden", "becca_gulden", "becca"}:
        comparison += "\n\nIn the shutdown context: treat this less like ‘who is right’ and more like nervous-system pacing. If one person goes emergency-mode and the other goes dorsal, the first move is reducing demand pressure before interpreting motives."
    pdfs = []
    for profile in (first_profile, second_profile):
        pdf = (profile.get("latest_chart") or {}).get("pdf_path")
        if pdf and pdf not in pdfs:
            pdfs.append(pdf)
    return {"response": comparison, "pdf_paths": pdfs}


def handle_known_relationship_compare(text: str) -> dict | None:
    if not COMPARE_INTENT_RE.search(text or ""):
        return None
    matches = stored_profiles_for_compare_text(text)
    if len(matches) < 2:
        return None
    return compare_two_stored_profiles(matches[0][0], matches[1][0])


REMEMBER_INTENT_RE = re.compile(
    r"\b(do you remember|remember when|remember what|what did we (talk|say|discuss)|what was that|earlier session|last session|yesterday|from before|talked about before)\b",
    re.I,
)

REMEMBER_STOPWORDS = {
    "about", "again", "before", "did", "discuss", "earlier", "from", "have", "know", "last", "remember",
    "session", "that", "the", "this", "talk", "talked", "there", "thing", "what", "when", "where", "with",
    "yesterday", "you", "we", "were", "was", "our", "and", "for", "can", "could", "would", "should", "please",
}


def continuity_search_terms(text: str) -> list[str]:
    cleaned = re.sub(r"[^A-Za-z0-9' _-]+", " ", text or " ").lower()
    words = [w.strip("_-' ") for w in cleaned.split()]
    terms = []
    for word in words:
        if len(word) < 4 or word in REMEMBER_STOPWORDS:
            continue
        if word not in terms:
            terms.append(word)
    return terms[:4]


def search_recent_history_for_terms(terms: list[str], limit: int = 5) -> list[str]:
    history = load_history()
    if not history:
        return []
    needles = [t.lower() for t in terms if t]
    matches = []
    for turn in reversed(history):
        combined = ((turn.get("user") or "") + "\n" + (turn.get("assistant") or "")).strip()
        if not combined:
            continue
        haystack = combined.lower()
        if not needles or any(term in haystack for term in needles):
            ts = turn.get("ts") or "recent"
            user = (turn.get("user") or "").replace("\n", " ")[:260]
            guide = (turn.get("assistant") or "").replace("\n", " ")[:360]
            matches.append(f"[{ts}] User: {user}\nGuide: {guide}")
        if len(matches) >= limit:
            break
    return matches


def journal_has_no_matches(text: str) -> bool:
    lower = (text or "").lower()
    return not text.strip() or "no journal entries found" in lower or "no journal entries matched" in lower


def handle_continuity_memory_lookup(text: str) -> dict | None:
    raw = (text or "").strip()
    if not REMEMBER_INTENT_RE.search(raw):
        return None
    terms = continuity_search_terms(raw)
    history_hits = search_recent_history_for_terms(terms or [], limit=4)
    journal_blocks = []
    try:
        from daily_journal_mcp import list_journal_entries, search_journal
        if terms:
            seen = set()
            for term in terms[:3]:
                result = search_journal(term)
                if not journal_has_no_matches(result) and result not in seen:
                    journal_blocks.append(result)
                    seen.add(result)
        else:
            result = list_journal_entries(5)
            if not journal_has_no_matches(result):
                journal_blocks.append(result)
    except Exception as exc:
        logger.exception("Continuity journal lookup failed: %s", exc)
        journal_blocks.append(f"Journal search errored: {exc}")

    pieces = ["I searched the saved journal and the recent session history I can access."]
    if terms:
        pieces.append("Search terms I used: " + ", ".join(terms) + ".")
    else:
        pieces.append("You did not give a specific topic, so I checked the most recent retained entries/turns.")

    found_any = bool(history_hits or journal_blocks)
    if journal_blocks:
        pieces.append("\nJournal matches:\n" + "\n---\n".join(journal_blocks)[:2400])
    else:
        pieces.append("\nJournal matches: nothing retained matched this ask.")
    if history_hits:
        pieces.append("\nRecent session-history matches:\n" + "\n---\n".join(history_hits)[:2200])
    else:
        pieces.append("\nRecent session-history matches: nothing retained matched this ask.")

    if not found_any:
        pieces.append("\nBoundary: I only know what was saved to the journal or retained in this guest session history. If the earlier conversation was not saved there, I will not pretend I found it.")
    else:
        pieces.append("\nThat is what I can actually find from retained memory. If you want, ask the follow-up in plain language and I’ll use this as the thread.")
    return {"response": "\n".join(pieces)}


def handle_journal_shortcut(text: str) -> dict | None:
    raw = (text or "").strip()
    lower = raw.lower()
    if not any(k in lower for k in ("journal", "log this", "record this", "write this down")):
        return None
    try:
        from daily_journal_mcp import add_journal_entry, list_journal_entries, search_journal
        if "search" in lower:
            query = re.sub(r".*search(?: my)? journal(?: for)?", "", raw, flags=re.I).strip(" :.-")
            return {"response": search_journal(query or " ")}
        if "list" in lower or "recent" in lower:
            return {"response": list_journal_entries(10)}
        entry = raw
        for marker in ("journal this:", "please journal this:", "log this:", "record this:", "write this down:"):
            if marker in lower:
                entry = raw[lower.index(marker) + len(marker):].strip()
                break
        entry = entry or raw
        result = add_journal_entry(entry)
        return {"response": "Noted. I put that in the journal." if result.startswith("Success") else result}
    except Exception as exc:
        logger.exception("Journal shortcut failed: %s", exc)
        return {"response": f"I tried to write the journal entry, but the journal system errored: {exc}"}

async def handle_progressive_chart_intake(text: str) -> dict | None:
    state = load_state()
    pending = state.get("pending_chart")
    if not pending and CHART_INTENT_RE.search(text or ""):
        is_compare = bool(COMPARE_INTENT_RE.search(text or ""))
        explicit_name = maybe_extract_person_from_chart_request(text)
        if chart_request_has_invalid_name_phrase(text, explicit_name):
            return {"response": "I won’t create a profile from a loose phrase. Give me the person’s first and last name, or say “my chart” if this is for you."}
        partial_slots = extract_partial_birth_slots(text)
        if partial_slots and not is_compare:
            default_slug = default_person_slug()
            default_profile = load_person_profile(default_slug) if default_slug else {}
            person_name = explicit_name or default_profile.get("name") or os.getenv("GUEST_USER_NAME") or "Sanctuary Guest"
            slug = slugify_person_name(person_name)
            pending_profile = {
                "relationship_type": "personal",
                "mode": "personal",
                "subject_index": 1,
                "person_name": person_name,
                "subject_name": slug,
            }
            pending_profile.update(partial_slots)
            pending_profile["stage"] = next_chart_stage_from_slots(pending_profile)
            if pending_profile.get("location") and pending_profile.get("birth_date") and pending_profile.get("birth_time") and pending_profile.get("birth_time") != "UNKNOWN":
                pending_profile["using_stored_details"] = True
            state["pending_chart"] = pending_profile
            save_state(state)
            pending = pending_profile
            if not (pending.get("using_stored_details") and pending.get("stage") == "location"):
                return {"response": prompt_for_next_chart_slot(pending)}
        if not pending and is_compare:
            state["pending_chart"] = {
                "stage": "person_name",
                "relationship_type": "friends",
                "mode": "compare",
                "subject_index": 1,
            }
            save_state(state)
            return {"response": "Yes. We’ll build this one person at a time. First person: what name should I put this chart under?"}
        if not pending and explicit_name:
            slug = slugify_person_name(explicit_name)
            profile = load_person_profile(slug)
            pending_profile = {
                "stage": "confirm_existing" if profile_has_birth_details(profile) else "birth_date",
                "relationship_type": "personal",
                "mode": "personal",
                "subject_index": 1,
                "person_name": explicit_name,
                "subject_name": slug,
            }
            if profile_has_birth_details(profile):
                birth = profile.get("birth_input") or {}
                pending_profile.update({
                    "birth_date": birth["birth_date"],
                    "birth_time": birth["birth_time"],
                    "location": birth["location"],
                    "birth_time_confidence": (profile.get("birth_confidence") or {}).get("birth_time") or birth_confidence_for(birth.get("birth_time", ""), "birth_time"),
                    "stage": "location",
                    "using_stored_details": True,
                    "profile": profile,
                })
                state["pending_chart"] = pending_profile
                save_state(state)
                pending = pending_profile
            else:
                state["pending_chart"] = pending_profile
                save_state(state)
                return {"response": f"Good. I’ll store this under {explicit_name}. What’s their birth date? MM/DD/YYYY or normal language is fine."}
        default_slug = default_person_slug()
        if not pending and default_slug:
            profile = load_person_profile(default_slug)
            if profile_has_birth_details(profile):
                birth = profile.get("birth_input") or {}
                state["pending_chart"] = {
                    "stage": "location",
                    "relationship_type": "personal",
                    "mode": "personal",
                    "subject_index": 1,
                    "person_name": profile.get("name") or default_slug.replace("_", " ").title(),
                    "subject_name": default_slug,
                    "profile": profile,
                    "birth_date": birth["birth_date"],
                    "birth_time": birth["birth_time"],
                    "location": birth["location"],
                    "birth_time_confidence": (profile.get("birth_confidence") or {}).get("birth_time") or birth_confidence_for(birth.get("birth_time", ""), "birth_time"),
                    "using_stored_details": True,
                }
                pending = state["pending_chart"]
                save_state(state)
            else:
                state["pending_chart"] = {
                    "stage": "birth_date",
                    "relationship_type": "personal",
                    "mode": "personal",
                    "subject_index": 1,
                    "person_name": profile.get("name") or default_slug.replace("_", " ").title(),
                    "subject_name": default_slug,
                    "profile": profile,
                }
                save_state(state)
                return {"response": f"I still have {profile_summary(profile)}. Use those details for this chart, or update them?"}
        if not pending:
            name = os.getenv("GUEST_USER_NAME") or "Sanctuary Guest"
            slug = slugify_person_name(name)
            index = load_people_index()
            index["default_person"] = slug
            index.setdefault("people", {}).setdefault(slug, {"name": name, "slug": slug})
            save_people_index(index)
            state["pending_chart"] = {
                "stage": "birth_date",
                "relationship_type": "personal",
                "mode": "personal",
                "subject_index": 1,
                "person_name": name,
                "subject_name": slug,
            }
            save_state(state)
            return {"response": "Yes. Send the birth date first — natural language is fine."}
    if not pending:
        return None

    stage = pending.get("stage", "birth_date")
    if stage == "person_name":
        person_name = clean_person_name(text)
        if not is_valid_person_name(person_name, allow_single_known=True):
            return {"response": "Give me the person’s first and last name for the chart label. I won’t turn a random phrase into a profile."}
        slug = slugify_person_name(person_name)
        profile = load_person_profile(slug)
        pending["person_name"] = person_name
        pending["subject_name"] = slug
        if pending.get("mode") == "personal":
            index = load_people_index()
            index["default_person"] = slug
            index.setdefault("people", {}).setdefault(slug, {"name": person_name, "slug": slug})
            save_people_index(index)
        if profile_has_birth_details(profile):
            pending["profile"] = profile
            pending["stage"] = "confirm_existing"
            state["pending_chart"] = pending
            save_state(state)
            return {"response": f"I have {profile_summary(profile)}. Use those details, or update them?"}
        pending["stage"] = "birth_date"
        state["pending_chart"] = pending
        save_state(state)
        label = "their" if pending.get("mode") == "compare" else "your"
        return {"response": f"Good. I’ll store this under {person_name}. What’s {label} birth date? MM/DD/YYYY or normal language is fine."}

    if stage == "confirm_existing":
        profile = pending.get("profile") or load_person_profile(pending.get("subject_name", ""))
        if YES_RE.match(text or "") and profile_has_birth_details(profile):
            birth = profile.get("birth_input") or {}
            pending["birth_date"] = birth["birth_date"]
            pending["birth_time"] = birth["birth_time"]
            pending["location"] = birth["location"]
            pending["stage"] = "location"
            pending["using_stored_details"] = True
        elif NO_RE.match(text or ""):
            pending.pop("profile", None)
            pending["stage"] = "birth_date"
            state["pending_chart"] = pending
            save_state(state)
            return {"response": "Okay. What birth date should I use instead? MM/DD/YYYY or normal language is fine."}
        else:
            return {"response": "Use the stored birth details, or update them?"}
        stage = pending.get("stage", stage)

    if stage == "birth_date":
        birth_date = parse_birth_date(text)
        if not birth_date:
            response = rotating_prompt(pending, "date_retry", DATE_RETRY_PROMPTS)
            state["pending_chart"] = pending
            save_state(state)
            return {"response": response}
        pending["birth_date"] = birth_date
        pending["stage"] = "birth_time"
        response = rotating_prompt(pending, "date_ok", DATE_ACCEPTED_PROMPTS)
        state["pending_chart"] = pending
        save_state(state)
        return {"response": response}

    if stage == "birth_time":
        birth_time = parse_birth_time(text)
        if not birth_time:
            response = rotating_prompt(pending, "time_retry", TIME_RETRY_PROMPTS)
            state["pending_chart"] = pending
            save_state(state)
            return {"response": response}
        if birth_time == "UNKNOWN":
            pending["birth_time"] = "UNKNOWN"
            pending["birth_time_original"] = text.strip()
            pending["birth_time_confidence"] = "missing"
            pending["stage"] = "missing_time_choice"
            state["pending_chart"] = pending
            save_state(state)
            return {"response": "Good — I won’t pretend 12:00 is better data. Do you want to explore a likely time window, make a clearly marked rough/unknown-time chart, or wait until you can find the exact time?"}
        pending["birth_time"] = birth_time
        pending["birth_time_original"] = text.strip()
        pending["birth_time_confidence"] = "natural-clue" if birth_time.startswith("NATURAL:") else ("approximate" if birth_time.startswith("APPROX:") else "exact")
        pending["stage"] = "location"
        state["pending_chart"] = pending
        save_state(state)
        if birth_time.startswith("NATURAL:"):
            return {"response": "Good. I can calculate that once I have the place. Last piece: where were you born? City and state/country is enough."}
        if birth_time.startswith("APPROX:"):
            return {"response": "Good. I’ll treat that as approximate and keep moving. Last piece: where were you born? City and state/country is enough."}
        return {"response": rotating_prompt(pending, "time_ok", TIME_ACCEPTED_PROMPTS)}

    if stage == "missing_time_choice":
        raw = (text or "").lower()
        if re.search(r"\b(explore|narrow|questions|figure|rectif)\b", raw):
            pending["stage"] = "location_for_exploration"
            state["pending_chart"] = pending
            save_state(state)
            return {"response": "Yes. I’ll use chart-pattern anchors as clues, not proof. First I need the birth place: city and state/country?"}
        if re.search(r"\b(rough|unknown|placeholder|use noon|continue|build)\b", raw):
            pending["birth_time"] = "UNKNOWN"
            pending["birth_time_confidence"] = "unknown-placeholder"
            pending["stage"] = "location"
            state["pending_chart"] = pending
            save_state(state)
            return {"response": "Okay. I’ll build it as an unknown-time exploration chart and label it clearly. Where were you born? City and state/country is enough."}
        return {"response": "Choose one: explore a likely time window, build a clearly marked rough/unknown-time chart, or wait for exact birth time."}

    if stage == "location_for_exploration":
        location = parse_name_and_location(text)
        if len(location) < 2:
            return {"response": "I need the birth place before the time exploration — city and state/country is enough."}
        pending["location"] = location
        pending["stage"] = "time_explore_window"
        state["pending_chart"] = pending
        save_state(state)
        return {"response": "What broad window do you remember — overnight, morning, midday, afternoon, evening, or a range like 6 to 10am?"}

    if stage == "time_explore_window":
        window = parse_time_window_choice(text)
        if not window:
            return {"response": "Give me the broadest window you can: overnight, morning, midday, afternoon, evening, or something like 6 to 10am."}
        options, prompt = build_time_exploration_options(pending, window[0], window[1])
        pending["time_exploration_options"] = options
        pending["time_exploration_window"] = list(window)
        pending["stage"] = "time_explore_choice"
        state["pending_chart"] = pending
        save_state(state)
        return {"response": prompt}

    if stage == "time_explore_choice":
        options = pending.get("time_exploration_options") or []
        chosen = choose_explored_time(text, options)
        if not chosen:
            window = parse_time_window_choice(text)
            if window:
                options, prompt = build_time_exploration_options(pending, window[0], window[1])
                pending["time_exploration_options"] = options
                pending["time_exploration_window"] = list(window)
                state["pending_chart"] = pending
                save_state(state)
                return {"response": prompt}
            return {"response": "Pick the closest option number, or give me a tighter time window and I’ll resample."}
        pending["birth_time"] = chosen
        pending["birth_time_confidence"] = "explored"
        pending["birth_time_note"] = f"Birth time was explored from user memory and chart-pattern anchors; {chosen} is a working hypothesis, not confirmed record data."
        pending["stage"] = "location"
        pending["using_stored_details"] = True
        state["pending_chart"] = pending
        save_state(state)
        return {"response": f"Good. I’ll use {chosen} as a working hypothesis and label the chart as explored-time, not confirmed. Want me to build it now?"}

    if stage == "location":
        if pending.get("using_stored_details"):
            location = pending.get("location", "")
        else:
            location = parse_name_and_location(text)
            if len(location) < 2:
                response = rotating_prompt(pending, "location_retry", LOCATION_RETRY_PROMPTS)
                state["pending_chart"] = pending
                save_state(state)
                return {"response": response}
            pending["location"] = location
        try:
            resolved_time, time_note = resolve_birth_time_after_location(pending["birth_time"], pending["birth_date"], location)
            pending["birth_time"] = resolved_time
            if time_note:
                pending["birth_time_note"] = time_note
            save_state(state)
            from daily_journal_mcp import generate_human_design_chart
            mode = pending.get("mode", "personal")
            subject_index = int(pending.get("subject_index", 1))
            relationship_type = pending.get("relationship_type", "personal")
            subject_name = pending.get("subject_name") or ("user" if mode == "personal" else f"person_{subject_index}")
            display_name = pending.get("person_name") or (os.getenv("GUEST_GUIDE_NAME", "Sanctuary Guest") if mode == "personal" else f"Person {subject_index}")
            result = generate_human_design_chart(
                birth_date=pending["birth_date"],
                birth_time=pending["birth_time"],
                location=pending["location"],
                name=display_name,
                relationship_type=relationship_type,
                subject_name=subject_name,
            )
            if pending.get("birth_time_note"):
                result = pending["birth_time_note"] + "\n" + result
            result = append_chart_insight_to_result(result, relationship_type, subject_name, display_name)
            set_profile_birth_confidence(subject_name, {
                "birth_date": "exact",
                "birth_time": pending.get("birth_time_confidence") or birth_confidence_for(pending.get("birth_time", ""), "birth_time"),
                "location": "exact",
            })
            if mode == "compare" and subject_index == 1:
                state["pending_chart"] = {
                    "stage": "person_name",
                    "relationship_type": relationship_type,
                    "mode": "compare",
                    "subject_index": 2,
                    "first_subject_name": subject_name,
                    "first_person_name": display_name,
                }
                save_state(state)
                return {"response": "Good. I have the first chart. Who is the second person?"}
            if mode == "compare" and subject_index == 2:
                first_subject = pending.get("first_subject_name", "person_1")
                first = load_chart_summary(relationship_type, first_subject)
                second = load_chart_summary(relationship_type, subject_name)
                clear_state()
                if not first or not second:
                    return {"response": result + "\nI built the second chart, but I could not read both chart files for comparison yet."}
                comparison = summarize_pair(first, second)
                return {
                    "response": result + "\n" + comparison,
                    "pdf_paths": list_chart_pdfs(relationship_type, pending.get("first_subject_name", "person_1"), subject_name),
                }
            clear_state()
            return {"response": result}
        except Exception as exc:
            logger.exception("Progressive chart generation failed: %s", exc)
            return {"response": f"I have the details, but chart generation hit an internal error: {exc}"}
    return None


app = FastAPI(title="Guest Hermes Agent Server")


def estimate_tokens(text: str) -> int:
    """Conservative local estimate until Hermes/provider exposes exact usage."""
    chars_per_token = max(1, int(os.getenv("GUEST_USAGE_CHARS_PER_TOKEN", "4")))
    return max(1, (len(text or "") + chars_per_token - 1) // chars_per_token)


def build_usage(input_text: str, output_text: str) -> dict:
    """Return standardized usage metadata for the head-bot router ledger."""
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    return {
        "provider": os.getenv("GUEST_MODEL_PROVIDER", "minimax"),
        "model": os.getenv("GUEST_MODEL_NAME", "MiniMax-M3"),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "estimated": True,
        "source": "guest_agent_server_estimate",
    }


def extract_chart_file_paths(response_text: str) -> tuple[str | None, str | None, list[str], str]:
    image_path = None
    pdf_path = None
    pdf_paths: list[str] = []
    clean_lines = []
    for line in response_text.splitlines():
        if line.startswith("__CHART_FILE_PATHS__:"):
            parts = line.replace("__CHART_FILE_PATHS__:", "").strip().split(";")
            for part in parts:
                if part.startswith("image_path="):
                    image_path = part.replace("image_path=", "").strip() or None
                elif part.startswith("pdf_path="):
                    pdf_path = part.replace("pdf_path=", "").strip() or None
                    if pdf_path:
                        pdf_paths.append(pdf_path)
        else:
            clean_lines.append(line)
    return image_path, pdf_path, pdf_paths, "\n".join(clean_lines).strip()


@app.post("/api/message")
async def process_message(payload: dict = Body(...)):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text parameter")

    logger.info("Received message: %r", text)

    if re.match(r"^\s*/new\s*$", text or "", re.I):
        clear_state()

    reset_or_greeting = handle_reset_or_greeting(text)
    if reset_or_greeting is not None:
        response_text = reset_or_greeting.get("response", "").strip()
        usage = build_usage(text, response_text)
        append_history(text, response_text)
        return {"response": response_text, "image_path": None, "pdf_path": None, "pdf_paths": [], "usage": usage, "model_usage": usage}

    # LLM-first runtime: only continue existing structured work or explicit
    # deterministic commands before the model. Normal help/greeting/frustration
    # and open conversation get game time with live profile/chart context.
    pending_state = load_state()
    has_pending_structured = bool(pending_state.get("pending_chart") or pending_state.get("pending_profile_edit"))

    if is_explicit_structured_command(text):
        one_shot_chart = generate_one_shot_chart_from_details(text)
        if one_shot_chart is not None:
            response_text = one_shot_chart.get("response", "").strip()
            image_path, pdf_path, pdf_paths, response_text = extract_chart_file_paths(response_text)
            usage = build_usage(text, response_text)
            append_history(text, response_text)
            return {"response": response_text, "image_path": image_path, "pdf_path": pdf_path, "pdf_paths": pdf_paths, "usage": usage, "model_usage": usage}

        natural_update = handle_natural_profile_update(text)
        if natural_update is not None:
            response_text = natural_update.get("response", "").strip()
            image_path, pdf_path, pdf_paths, response_text = extract_chart_file_paths(response_text)
            usage = build_usage(text, response_text)
            return {"response": response_text, "image_path": image_path, "pdf_path": pdf_path, "pdf_paths": pdf_paths, "usage": usage, "model_usage": usage}

        journal_result = handle_journal_shortcut(text)
        if journal_result is not None:
            response_text = journal_result.get("response", "").strip()
            usage = build_usage(text, response_text)
            return {"response": response_text, "image_path": None, "pdf_path": None, "pdf_paths": [], "usage": usage, "model_usage": usage}

        exploration_result = handle_time_exploration_standalone(text)
        if exploration_result is not None:
            response_text = exploration_result.get("response", "").strip()
            usage = build_usage(text, response_text)
            return {"response": response_text, "image_path": None, "pdf_path": None, "pdf_paths": [], "usage": usage, "model_usage": usage}

    # If the user is trying to escape or repair a bad structured state, let the LLM answer.
    escape_pending = bool(re.search(r"\b(help|stop|no,|just change|name needs|date is fine|scripted|wrong person)\b", text or "", re.I) or FRUSTRATION_RE.search(text or ""))

    if FRUSTRATION_RE.search(text or ""):
        context = summarize_live_context()
        clear_state()
        response_text = (
            "You’re right. I’m making this too procedural. I’m clearing the stuck flow.\n\n"
            "Here’s what I know right now:\n" + context + "\n\n"
            "Say the outcome, not the form — for example: build my chart, fix my birth time, explore missing time, or just talk through what this means."
        )
        usage = build_usage(text, response_text)
        return {"response": response_text, "image_path": None, "pdf_path": None, "pdf_paths": [], "usage": usage, "model_usage": usage}

    name_result = handle_name_association_request(text)
    if name_result is not None:
        response_text = name_result.get("response", "").strip()
        usage = build_usage(text, response_text)
        append_history(text, response_text)
        return {"response": response_text, "image_path": None, "pdf_path": None, "pdf_paths": [], "usage": usage, "model_usage": usage}

    continuity_result = handle_continuity_memory_lookup(text)
    if continuity_result is not None:
        response_text = continuity_result.get("response", "").strip()
        usage = build_usage(text, response_text)
        append_history(text, response_text)
        return {"response": response_text, "image_path": None, "pdf_path": None, "pdf_paths": [], "usage": usage, "model_usage": usage}

    edit_result = handle_profile_edit_request(text)
    if edit_result is not None:
        response_text = edit_result.get("response", "").strip()
        pdf_paths = edit_result.get("pdf_paths") or []
        pdf_path = edit_result.get("pdf_path") or (pdf_paths[0] if pdf_paths else None)
        usage = build_usage(text, response_text)
        return {"response": response_text, "image_path": None, "pdf_path": pdf_path, "pdf_paths": pdf_paths, "usage": usage, "model_usage": usage}

    pdf_result = handle_pdf_report_request(text)
    if pdf_result is not None:
        response_text = pdf_result.get("response", "").strip()
        image_path, pdf_path, pdf_paths, response_text = extract_chart_file_paths(response_text)
        usage = build_usage(text, response_text)
        append_history(text, response_text)
        return {"response": response_text, "image_path": image_path, "pdf_path": pdf_path, "pdf_paths": pdf_paths, "usage": usage, "model_usage": usage}

    compare_result = handle_known_relationship_compare(text)
    if compare_result is not None:
        response_text = compare_result.get("response", "").strip()
        pdf_paths = compare_result.get("pdf_paths") or []
        usage = build_usage(text, response_text)
        return {"response": response_text, "image_path": None, "pdf_path": pdf_paths[0] if pdf_paths else None, "pdf_paths": pdf_paths, "usage": usage, "model_usage": usage}

    chart_trigger = bool(re.search(r"\b(build|generate|calculate|create|run|rebuild|regenerate)\b.*\b(chart|bodygraph|human design|report)\b|\bcompare\s+(two|2)\s+charts\b", text or "", re.I))
    if (has_pending_structured and not escape_pending) or chart_trigger:
        chart_result = await handle_progressive_chart_intake(text)
        if chart_result is not None:
            response_text = chart_result.get("response", "").strip()
            image_path, pdf_path, marker_pdf_paths, response_text = extract_chart_file_paths(response_text)
            pdf_paths = chart_result.get("pdf_paths") or marker_pdf_paths
            if pdf_path and pdf_path not in pdf_paths:
                pdf_paths.append(pdf_path)
            usage = build_usage(text, response_text)
            return {
                "response": response_text,
                "image_path": image_path,
                "pdf_path": pdf_path,
                "pdf_paths": pdf_paths,
                "usage": usage,
                "model_usage": usage,
            }

    # Normal path: LLM gets the turn, with live profile/chart/tool context.
    response_text = run_llm_with_context(text)

    # Extract metadata line if any
    image_path, pdf_path, pdf_paths, response_text = extract_chart_file_paths(response_text)
    usage = build_usage(text, response_text)
    append_history(text, response_text)

    logger.info("Agent response: %r", response_text)
    logger.info("Usage metadata: %s", usage)
    return {
        "response": response_text,
        "image_path": image_path,
        "pdf_path": pdf_path,
        "pdf_paths": pdf_paths,
        "usage": usage,
        "model_usage": usage,
    }
