#!/usr/bin/env python3
"""
Daily Social Graphic Generator — GRO-101
=========================================
Computes today's dominant gate (Sun transit) and generates a 1080×1080
social media graphic suitable for Instagram, Facebook, and Telegram.

Usage:
    python3 daily_social_graphic.py              # generate + save
    python3 daily_social_graphic.py --json       # also print JSON summary
    python3 daily_social_graphic.py --out /path  # custom output directory

Output:
    /tmp/hde-social/daily-gate-YYYY-MM-DD.png   (default)
    /tmp/hde-social/daily-gate-YYYY-MM-DD.json  (with --json)

Brand:
    Background: deep navy #1a1a3e
    Accent:     gold #d4a574
    Text:       white #ffffff
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

# ── Engine import ──────────────────────────────────────────────────────
ENGINE_PATH = os.environ.get(
    "ENGINE_PATH",
    "/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src"
)
sys.path.insert(0, ENGINE_PATH)

from ephemeris_engine import init_ephemeris
from transit_engine import calculate_transit_positions
from cosmic_calculator import GATE_NAMES  # dict: int → str

init_ephemeris()

# ── Gate snippets (one-liner descriptions) ─────────────────────────────
# Sourced from gates_data.json — first sentence or condensed meaning
GATE_SNIPPETS: dict[int, str] = {
    1:  "Creative self-expression — the urge to bring something new into form",
    2:  "Receptivity and inner direction — knowing where to go without needing to know why",
    3:  "Innovation through difficulty — mutation that births new forms",
    4:  "Mental formulation — the logical mind's drive to find answers",
    5:  "Fixed rhythms — waiting for the right timing in natural cycles",
    6:  "Emotional boundary-setting — the gatekeeper of intimacy and connection",
    7:  "Leadership through service — wielding influence for the greater good",
    8:  "Contribution by example — teaching through embodied demonstration",
    9:  "Sustained focus — the capacity to go deep with unwavering concentration",
    10: "Authentic self-love — standing in your own truth without apology",
    11: "Ideas and imagination — the flow of creative inspiration",
    12: "Caution and emotional articulation — knowing when to speak and when to be still",
    13: "The listener — holding space for others' stories and confessions",
    14: "Empowered skill and resource abundance — directing energy in service of your path",
    15: "Extremes in rhythm — embracing the full spectrum of human experience",
    16: "Enthusiasm for skills — the joy of practice, repetition, and refinement",
    17: "Opinions and mental projection — formulating concepts for the collective",
    18: "Correction and improvement — spotting what needs to be made better",
    19: "Sensitivity to need — attunement to what the tribe requires",
    20: "Contemplation in the now — pure presence and self-awareness",
    21: "Control and resource management — the hunter/huntress energy",
    22: "Grace and openness — the capacity to receive spirit through beauty",
    23: "Assimilation and articulation — breaking complex ideas into simple truth",
    24: "Rationalization and return — the mind's drive to find closure and meaning",
    25: "Innocence and spirit — the energy of universal love",
    26: "The egoist and the salesperson — the power of persuasion",
    27: "Caring and nourishment — the energy of the mother/father archetype",
    28: "The game player — finding meaning through struggle and risk",
    29: "Persistence and commitment — saying yes and seeing it through",
    30: "Desire and feeling — the fuel of emotional experience",
    31: "Leading and influence — the voice that guides the collective",
    32: "Continuity and adaptation — knowing when to change and when to endure",
    33: "Privacy and retreat — the wisdom of withdrawing to reflect",
    34: "Power and potency — raw life force expressing through the sacral",
    35: "Change and progress — the appetite for new experience",
    36: "Crisis and emotional depth — the wisdom that emerges through difficulty",
    37: "Friendship and community — the energy of the extended family",
    38: "The fighter — standing up for purpose and meaning",
    39: "Provocation and emotional clarity — stirring the pot to release stuck energy",
    40: "Aloneness and deliverance — the strength to stand alone and then deliver",
    41: "Contraction and fantasy — the seed of new beginnings in the imagination",
    42: "Growth and completion — bringing cycles to their natural end",
    43: "Insight and breakthrough — the flash of knowing that changes everything",
    44: "Alertness and pattern recognition — sensing who and what belongs",
    45: "The gatherer — bringing resources together for the collective",
    46: "Determination and embodiment — the love of being in a body",
    47: "Realization and mental clarity — making sense of past experience",
    48: "Depth and resource — the well of wisdom that others draw from",
    49: "Principles and revolution — the energy of emotional transformation",
    50: "Values and the cauldron — preserving what nourishes the tribe",
    51: "Shock and awakening — the energy that wakes you up to your path",
    52: "Stillness and inaction — the mountain that cannot be moved",
    53: "Beginnings and development — the pressure to start something new",
    54: "Ambition and drive — the energy of the young maiden rising",
    55: "Spirit and emotional abundance — the fullness of feeling alive",
    56: "Stimulation and the wanderer — seeking experience through movement",
    57: "Intuitive clarity — the gentle knowing that penetrates all things",
    58: "Aliveness and vitality — the joy of correction through living fully",
    59: "Sexuality and creativity — the energy that breaks through barriers to bond",
    60: "Acceptance and limitation — the wisdom of working within constraints",
    61: "Mystery and inner truth — the pressure to know the unknowable",
    62: "Detail and articulation — expressing complex understanding in simple language",
    63: "Doubt and logical inquiry — questioning assumptions to reach clarity",
    64: "Confusion and completion — the pressure to make sense before moving on",
}


def compute_dominant_gate() -> dict:
    """Compute today's transits and return the Sun's gate as dominant."""
    positions = calculate_transit_positions()
    sun_data = positions.get("Sun", {})
    earth_data = positions.get("Earth", {})

    sun_gate = sun_data.get("gate", 1)
    earth_gate = earth_data.get("gate", 1)

    gate_name = GATE_NAMES.get(int(sun_gate), f"Gate {sun_gate}")
    snippet = GATE_SNIPPETS.get(int(sun_gate), "The energy of authentic being")

    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "date_display": datetime.now(timezone.utc).strftime("%A, %B %d, %Y"),
        "dominant_gate": int(sun_gate),
        "gate_name": gate_name,
        "snippet": snippet,
        "sun": {
            "gate": sun_gate,
            "line": sun_data.get("line", 1),
            "retrograde": sun_data.get("retrograde", False),
        },
        "earth": {
            "gate": earth_gate,
            "line": earth_data.get("line", 1),
        },
    }


def generate_graphic(data: dict, output_path: str) -> str:
    """
    Generate a 1080×1080 social media graphic using Pillow.

    Layout (vertical, centered):
      ┌──────────────────────────┐
      │                          │
      │     🌌  GATE  42  🌌    │   ← large gold number
      │     Growth              │   ← gate name, white, medium
      │     ─────────           │   ← gold rule
      │     "one-line desc"     │   ← snippet, white, small
      │                          │
      │    🌐 Human Design       │   ← footer
      │    Daily Transit         │
      │    May 29, 2026         │
      └──────────────────────────┘
    """
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1080, 1080
    BG_COLOR = "#1a1a3e"       # deep navy
    GOLD = "#d4a574"           # warm gold
    WHITE = "#ffffff"
    DIM_WHITE = "#8a8aa0"

    # ── Fonts ──────────────────────────────────────────────────────
    font_dir = "/usr/share/fonts/truetype/dejavu"
    try:
        font_number = ImageFont.truetype(f"{font_dir}/DejaVuSans-Bold.ttf", 220)
        font_name = ImageFont.truetype(f"{font_dir}/DejaVuSans-Bold.ttf", 52)
        font_snippet = ImageFont.truetype(f"{font_dir}/DejaVuSans.ttf", 34)
        font_footer = ImageFont.truetype(f"{font_dir}/DejaVuSans.ttf", 24)
        font_date = ImageFont.truetype(f"{font_dir}/DejaVuSans.ttf", 28)
    except OSError:
        # Fallback: use default font
        font_number = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_snippet = ImageFont.load_default()
        font_footer = ImageFont.load_default()
        font_date = ImageFont.load_default()

    # ── Canvas ─────────────────────────────────────────────────────
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    def text_size(font, text):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def draw_centered(y, text, font, fill):
        tw, th = text_size(font, text)
        x = (W - tw) // 2
        draw.text((x, y), text, font=font, fill=fill)
        return th

    def draw_centered_multiline(y, text, font, fill, line_spacing=8):
        lines = text.split("\n")
        heights = []
        for line in lines:
            th = draw_centered(y, line, font, fill)
            y += th + line_spacing
            heights.append(th)
        return sum(heights) + line_spacing * (len(lines) - 1)

    # ── Render ─────────────────────────────────────────────────────
    gate_num = data["dominant_gate"]
    gate_name = data["gate_name"]
    snippet = data["snippet"]
    date_display = data["date_display"]

    # Helper to wrap snippet text to fit within margins
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            tw, _ = text_size(font, test_line)
            if tw <= max_width and len(current_line) < 12:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    # Calculate vertical positioning — center the whole block
    gate_str = f"GATE {gate_num}"
    mw = W - 160  # horizontal margins

    # Measure total block height
    _, num_h = text_size(font_number, gate_str)
    _, name_h = text_size(font_name, gate_name)
    rule_h = 20
    snippet_lines = wrap_text(snippet, font_snippet, mw)
    snippet_h = len(snippet_lines) * (text_size(font_snippet, "Ag")[1] + 6)

    total_block = num_h + name_h + rule_h + snippet_h + 40  # gaps
    start_y = (H - total_block) // 2  # roughly centered

    # Gate number (gold)
    y = start_y
    y += draw_centered(y, gate_str, font_number, GOLD)
    y += 16

    # Gate name (white)
    y += draw_centered(y, gate_name, font_name, WHITE)
    y += 24

    # Gold rule
    rule_width = 280
    rule_x = (W - rule_width) // 2
    draw.rectangle([rule_x, y, rule_x + rule_width, y + 3], fill=GOLD)
    y += 28

    # Snippet (white, wrapped)
    for line in snippet_lines:
        tw, th = text_size(font_snippet, line)
        x = (W - tw) // 2
        draw.text((x, y), line, font=font_snippet, fill=DIM_WHITE)
        y += th + 6

    # ── Footer ─────────────────────────────────────────────────────────
    footer_y = H - 140
    draw_centered(footer_y, "HUMAN DESIGN", font_footer, GOLD)
    footer_y += 30
    draw_centered(footer_y, "Daily Transit", font_footer, DIM_WHITE)
    footer_y += 32
    draw_centered(footer_y, date_display, font_date, DIM_WHITE)

    # ── Top accent line ─────────────────────────────────────────────────
    draw.rectangle([60, 50, W - 60, 52], fill=GOLD)

    # ── Save ────────────────────────────────────────────────────────────
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Daily Social Graphic Generator")
    parser.add_argument("--out", default="/tmp/hde-social",
                        help="Output directory (default: /tmp/hde-social)")
    parser.add_argument("--json", action="store_true",
                        help="Also write a JSON summary alongside the image")
    args = parser.parse_args()

    # Compute today's dominant gate
    data = compute_dominant_gate()

    # Derive output filename
    date_slug = data["date"]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    img_path = out_dir / f"daily-gate-{date_slug}.png"

    # Generate image
    result = generate_graphic(data, str(img_path))
    print(f"✓ Graphic saved: {result}")

    # JSON summary
    if args.json:
        json_path = out_dir / f"daily-gate-{date_slug}.json"
        json_path.write_text(json.dumps(data, indent=2))
        print(f"✓ JSON saved:   {json_path}")

    # Print summary
    print(f"\n🌌 Today's Dominant Gate: {data['dominant_gate']} — {data['gate_name']}")
    print(f"   {data['snippet']}")
    print(f"   Date: {data['date_display']}")


if __name__ == "__main__":
    main()
