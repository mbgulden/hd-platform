"""
LLM interpretation layer for Human Design charts.

Generates personalized narrative interpretation (type/authority/strategy,
gates/channels, life themes) using Anthropic Claude (Sonnet 3.5).
Caches results for 30 days per birth data hash using Redis (with local disk fallback).
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx
from shared.redis_client import get_redis

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TTL = 30 * 24 * 3600  # 30 days in seconds
LOCAL_CACHE_DIR = Path("/tmp/interpretation_cache")


def compute_birth_data_hash(birth_data: Dict[str, Any]) -> str:
    """
    Compute a stable SHA-256 hash of birth data.
    
    Normalizes coordinates and timezone to ensure consistency.
    """
    lat = birth_data.get("lat")
    lon = birth_data.get("lon")
    
    canonical = {
        "year": int(birth_data.get("year", 0)),
        "month": int(birth_data.get("month", 1)),
        "day": int(birth_data.get("day", 1)),
        "hour": int(birth_data.get("hour", 0)),
        "minute": int(birth_data.get("minute", 0)),
        "lat": round(float(lat), 4) if lat is not None else 0.0,
        "lon": round(float(lon), 4) if lon is not None else 0.0,
        "timezone": str(birth_data.get("timezone") or "UTC").strip()
    }
    canonical_str = json.dumps(canonical, sort_keys=True)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


async def get_cached_interpretation(birth_hash: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached interpretation from Redis, falling back to local disk cache.
    """
    # 1. Try Redis
    try:
        redis = await get_redis()
        cached = await redis.get(f"interpretation:{birth_hash}")
        if cached:
            logger.info("Cache hit in Redis for birth hash: %s", birth_hash)
            return json.loads(cached)
    except Exception as exc:
        logger.warning("Failed to query Redis cache: %s", exc)

    # 2. Try Local Disk Fallback
    try:
        local_path = LOCAL_CACHE_DIR / f"{birth_hash}.json"
        if local_path.exists():
            logger.info("Cache hit in Local Disk for birth hash: %s", birth_hash)
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as exc:
        logger.warning("Failed to query Local Disk cache: %s", exc)

    return None


async def save_cached_interpretation(birth_hash: str, payload: Dict[str, Any]) -> None:
    """
    Cache interpretation payload in Redis and local disk for 30 days.
    """
    serialized = json.dumps(payload)
    
    # 1. Save to Redis
    try:
        redis = await get_redis()
        await redis.set(f"interpretation:{birth_hash}", serialized, ex=CACHE_TTL)
        logger.info("Saved interpretation in Redis for hash: %s", birth_hash)
    except Exception as exc:
        logger.warning("Failed to save to Redis cache: %s", exc)

    # 2. Save to Local Disk
    try:
        LOCAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        local_path = LOCAL_CACHE_DIR / f"{birth_hash}.json"
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        logger.info("Saved interpretation on Local Disk for hash: %s", birth_hash)
    except Exception as exc:
        logger.warning("Failed to save to Local Disk cache: %s", exc)


def _generate_template_fallback(chart_data: Dict[str, Any]) -> str:
    """
    Generate a high-quality personalized narrative interpretation as a local fallback.
    """
    name = chart_data.get("name", "Seeker")
    hd_type = chart_data.get("hd_type", chart_data.get("type", "Projector"))
    profile = chart_data.get("profile", "6/2")
    authority = chart_data.get("authority", "Self-Projected")
    strategy = chart_data.get("strategy", "To Wait for Invitation")
    signature = chart_data.get("signature", "Success")
    not_self_theme = chart_data.get("not_self_theme", "Bitterness")
    
    cross = chart_data.get("incarnation_cross", {})
    cross_name = cross.get("name", "Unknown Cross") if isinstance(cross, dict) else str(cross)
    
    defined_centers = chart_data.get("defined_centers", ["G", "Throat"])
    undefined_centers = chart_data.get("undefined_centers", ["Head", "Ajna", "Sacral"])
    
    channels = chart_data.get("defined_channels", [])
    channel_names = [c.get("name", "") for c in channels if isinstance(c, dict)]
    channel_str = ", ".join(channel_names) if channel_names else "none currently defined"

    # Core Alignment section
    core_text = (
        f"As a **{hd_type}** with a **{profile}** profile, you are designed to operate as a guide and a role model. "
        f"Your decision-making style is **{authority}** (Inner Authority), and your core strategy is **{strategy}**. "
        f"When you align with this flow, your signature feeling is **{signature}**. "
        f"If you find yourself initiating without an invitation or ignoring your authority, you will experience the "
        f"warning signal of your not-self theme: **{not_self_theme}**.\n\n"
        f"Practically, this means you should not push your ideas or seek to convince others out of the blue. "
        f"Instead, focus on honing your gifts, staying visible, and waiting for others to recognize and invite your guidance. "
        f"When an invitation arrives, check in with your inner sense of resonance ({authority}) before committing."
    )

    # Energy patterns section
    patterns_text = (
        f"You carry consistent energy in your defined centers: **{', '.join(defined_centers)}**. "
        f"These are the areas where you project energy reliably out into the world and have constant access to these traits. "
        f"Your defined channels (**{channel_str}**) bridge these centers, forming your primary strengths and natural gifts. "
        f"For instance, they show how you express your insights and speak from your identity core.\n\n"
        f"Conversely, your open or undefined centers (**{', '.join(undefined_centers)}**) represent your windows of empathy. "
        f"Here, you pick up and amplify the emotional, mental, and physical states of those around you. "
        f"The challenge is to observe this incoming energy without identifying with it or trying to fix it."
    )

    # Life Purpose section
    purpose_text = (
        f"Your broader life theme is defined by the **{cross_name}**. "
        f"This cross governs the overarching trajectory of your life. "
        f"With your specific configuration, your journey centers on observing the patterns of the world, "
        f"integrating them during your early stages, and eventually standing as a beacon of objective wisdom. "
        f"By honoring your strategy of waiting for the right invitations, your life purpose naturally unfolds "
        f"without the friction of trying to force outcomes."
    )

    return f"""## Core Alignment (Type, Authority & Strategy)
{core_text}

## Key Energy Patterns & Gifts (Channels & Centers)
{patterns_text}

## Life Theme & Purpose (Incarnation Cross)
{purpose_text}"""


async def call_anthropic_api(prompt: str) -> Optional[str]:
    """
    Call the Anthropic Messages API with Sonnet 3.5.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info("No ANTHROPIC_API_KEY environment variable set. Skipping Claude API call.")
        return None

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1200,
        "temperature": 0.7,
        "system": (
            "You are an expert, warm, and highly intuitive Human Design interpreter. "
            "Your task is to translate complex charts into life-affirming, actionable advice. "
            "Strictly write your output in standard Markdown format, adhering to the requested header structures. "
            "Never use dense esoteric jargon without immediately explaining it in plain English."
        ),
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                text = data["content"][0]["text"]
                return text
            else:
                logger.error("Anthropic API returned error %d: %s", response.status_code, response.text)
                return None
    except Exception as exc:
        logger.exception("Exception occurred while calling Anthropic API: %s", exc)
        return None


async def generate_interpretation(
    chart_data: Dict[str, Any],
    birth_data: Dict[str, Any]
) -> Tuple[str, str]:
    """
    Generate personalized interpretation from chart data.
    
    Attempts cached lookup first. On miss, calls Claude API or templates fallback.
    Returns a tuple of (markdown_content, provider_name).
    """
    birth_hash = compute_birth_data_hash(birth_data)
    
    # 1. Attempt cache lookup
    cached = await get_cached_interpretation(birth_hash)
    if cached:
        return cached["interpretation"], cached["provider"]

    # 2. Compile prompt
    name = chart_data.get("name", "Seeker")
    hd_type = chart_data.get("hd_type", chart_data.get("type", "Unknown"))
    profile = chart_data.get("profile", "Unknown")
    authority = chart_data.get("authority", "Unknown")
    strategy = chart_data.get("strategy", "Unknown")
    
    cross = chart_data.get("incarnation_cross", {})
    cross_name = cross.get("name", "Unknown Cross") if isinstance(cross, dict) else str(cross)
    
    defined_centers = chart_data.get("defined_centers", [])
    undefined_centers = chart_data.get("undefined_centers", [])
    
    channels = chart_data.get("defined_channels", [])
    channel_names = [c.get("name", "") for c in channels if isinstance(c, dict)]
    
    signature = chart_data.get("signature", "Unknown")
    not_self_theme = chart_data.get("not_self_theme", "Unknown")
    active_gates = chart_data.get("all_active_gates", [])

    prompt = f"""Generate a personalized, narrative Human Design interpretation.

Chart Details:
- Name: {name}
- Type: {hd_type}
- Profile: {profile}
- Decision-Making Style (Authority): {authority}
- Strategy: {strategy}
- Life Theme (Incarnation Cross): {cross_name}
- Defined Centers: {', '.join(defined_centers)}
- Undefined Centers: {', '.join(undefined_centers)}
- Defined Channels: {', '.join(channel_names) if channel_names else 'None'}
- Active Gates: {', '.join(map(str, active_gates))}
- Signature (Feeling of alignment): {signature}
- Not-Self Theme (Warning signal): {not_self_theme}

Please organize your response under the following exact headings:
## Core Alignment (Type, Authority & Strategy)
## Key Energy Patterns & Gifts (Channels & Centers)
## Life Theme & Purpose (Incarnation Cross)

Provide an insightful, cohesive plain-English analysis. Help the seeker understand their design and how to apply it in their daily life. Keep it encouraging and direct.
"""

    # 3. Call Claude
    interpretation = await call_anthropic_api(prompt)
    provider = "anthropic-claude"

    # 4. Fallback if API fails or key not configured
    if not interpretation:
        logger.info("API call skipped or failed. Using template-based fallback.")
        interpretation = _generate_template_fallback(chart_data)
        provider = "template-fallback"

    # 5. Cache result
    cache_payload = {
        "interpretation": interpretation,
        "provider": provider,
        "hash": birth_hash
    }
    await save_cached_interpretation(birth_hash, cache_payload)

    return interpretation, provider
