"""
Human Design Engine — REST Bridge + Report Generator
=====================================================
Imports the OpenHumanDesignMCP calculation engine directly (no MCP transport needed).
Exposes REST endpoints for charts, transits, synastry — and generates beautiful PDF reports.

Run: python3 server.py          (starts on port 8081)
Env:  ENGINE_PATH=/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src
"""

import os
import sys
import json
import time
import logging
import subprocess
import tempfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO
from functools import wraps
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("hde-reports")

# ── Engine import ────────────────────────────────────────────────────
ENGINE_PATH = os.environ.get(
    "ENGINE_PATH",
    "/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src"
)
sys.path.insert(0, ENGINE_PATH)

from cosmic_calculator import calculate_natal_chart
from synastry_engine import calculate_composite, calculate_penta
from matrix_mapper import GATE_NAMES, GATE_CENTER, CHANNELS
from ephemeris_engine import init_ephemeris, get_planet_position, SUN
from transit_engine import (
    compute_transit_overlay,
    calculate_transit_positions,
    datetime_to_jd,
)

init_ephemeris()
log.info("Ephemeris initialized — engine ready.")

# ── Config ───────────────────────────────────────────────────────────
PORT = int(os.environ.get("REPORTS_PORT", "8081"))
API_KEY = os.environ.get("HDE_API_KEY", "hde-dev-key-change-me")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "reports@humandesignengine.com")
REPORTS_DIR = Path("/tmp/hde-reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Report database (simple JSON file) ────────────────────────────────
ORDERS_FILE = REPORTS_DIR / "orders.json"

def _load_orders():
    if ORDERS_FILE.exists():
        return json.loads(ORDERS_FILE.read_text())
    return []

def _save_order(order):
    orders = _load_orders()
    orders.append(order)
    ORDERS_FILE.write_text(json.dumps(orders, indent=2))

# ── HTML/CSS Report Templates ────────────────────────────────────────
CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Playfair+Display:wght@400;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', -apple-system, sans-serif; color: #1a1a2e; line-height: 1.7; font-size: 11pt; }
  .cover { min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 40px; }
  .cover h1 { font-family: 'Playfair Display', serif; font-size: 42pt; margin-bottom: 16px; font-weight: 700; }
  .cover .subtitle { font-size: 18pt; opacity: 0.9; margin-bottom: 8px; }
  .cover .meta { font-size: 12pt; opacity: 0.7; margin-top: 40px; }
  .cover .brand { font-size: 10pt; opacity: 0.6; margin-top: 20px; }
  .page { padding: 50px 60px; page-break-after: always; }
  .page:last-child { page-break-after: avoid; }
  h2 { font-family: 'Playfair Display', serif; font-size: 24pt; color: #667eea; margin: 30px 0 14px; padding-bottom: 8px; border-bottom: 2px solid #e8e8f0; }
  h3 { font-size: 14pt; color: #764ba2; margin: 20px 0 10px; }
  .section-intro { color: #666; font-style: italic; margin-bottom: 16px; }
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 20px 0; }
  .stat-card { background: #f8f7ff; border-radius: 12px; padding: 16px; border-left: 4px solid #667eea; }
  .stat-card .label { font-size: 9pt; text-transform: uppercase; letter-spacing: 1px; color: #888; margin-bottom: 4px; }
  .stat-card .value { font-size: 14pt; font-weight: 600; color: #1a1a2e; }
  .center-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 20px 0; }
  .center-box { padding: 20px; border-radius: 12px; }
  .defined { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border: 1px solid #a5d6a7; }
  .undefined { background: linear-gradient(135deg, #fff3e0, #ffe0b2); border: 1px solid #ffcc80; }
  .center-box h3 { margin-top: 0; }
  .center-box ul { list-style: none; padding: 0; }
  .center-box li { padding: 6px 0; font-size: 11pt; }
  .center-box li:before { content: "▸ "; color: #667eea; }
  .gate-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
  .gate-badge { background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 10pt; font-weight: 600; }
  .channel-row { display: flex; align-items: center; gap: 12px; padding: 10px; background: #f8f7ff; border-radius: 8px; margin: 8px 0; }
  .channel-name { font-weight: 600; flex: 1; }
  .channel-gates { color: #667eea; font-size: 10pt; }
  .highlight-box { background: linear-gradient(135deg, #f3e5f5, #e1bee7); border-radius: 12px; padding: 24px; margin: 20px 0; border-left: 4px solid #9c27b0; }
  .highlight-box h3 { color: #6a1b9a; margin-top: 0; }
  .experiment-box { background: #e8eaf6; border-radius: 12px; padding: 24px; margin: 20px 0; }
  .experiment-box h3 { color: #283593; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  th { background: #667eea; color: white; padding: 10px 14px; text-align: left; font-size: 10pt; }
  td { padding: 10px 14px; border-bottom: 1px solid #e8e8f0; font-size: 10pt; }
  tr:nth-child(even) td { background: #fafaff; }
  .footer { text-align: center; padding: 40px; color: #999; font-size: 9pt; }
  .footer a { color: #667eea; }
  .badge { display: inline-block; background: #667eea; color: white; padding: 2px 10px; border-radius: 12px; font-size: 9pt; margin-left: 8px; vertical-align: middle; }
  .cert-badge { text-align: center; margin: 30px 0; padding: 12px; background: #f8f7ff; border-radius: 12px; font-size: 9pt; color: #888; }
  @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
</style>
"""

def make_cover(name, report_type, date_str):
    titles = {
        "natal": "Your Human Design Natal Chart",
        "relationship": "Your Relationship Blueprint",
        "transit": "Your Transit Forecast",
        "composite": "Your Composite Design",
    }
    return f"""
    <div class="cover">
      <h1>{titles.get(report_type, "Your Human Design Report")}</h1>
      <div class="subtitle">A personalized guide for {name}</div>
      <div class="meta">Generated {date_str}</div>
      <div class="brand">Human Design Engine — humandesignengine.com</div>
    </div>
    """

# ── Report Builders ──────────────────────────────────────────────────

def build_natal_report(chart: dict) -> str:
    """Generate a comprehensive natal chart report as HTML."""
    name = chart.get("name", "Friend")
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{name}'s Natal Chart</title>{CSS}</head><body>
{make_cover(name, 'natal', date_str)}
<div class="page">
"""
    
    # ── Section 1: Overview ──
    html += f"""
  <h2>🎯 Your Design at a Glance</h2>
  <p class="section-intro">Your Human Design chart reveals your unique energetic blueprint — how you're designed to make decisions, interact with others, and navigate life in alignment.</p>
  
  <div class="stat-grid">
    <div class="stat-card">
      <div class="label">Type</div>
      <div class="value">{chart.get('hd_type', 'Unknown')}</div>
    </div>
    <div class="stat-card">
      <div class="label">Profile</div>
      <div class="value">{chart.get('profile', 'Unknown')}</div>
    </div>
    <div class="stat-card">
      <div class="label">Authority</div>
      <div class="value">{chart.get('authority', 'Unknown')}</div>
    </div>
    <div class="stat-card">
      <div class="label">Strategy</div>
      <div class="value">{chart.get('strategy', 'Unknown')}</div>
    </div>
    <div class="stat-card">
      <div class="label">Definition</div>
      <div class="value">{chart.get('definition', 'Unknown')}</div>
    </div>
    <div class="stat-card">
      <div class="label">Incarnation Cross</div>
      <div class="value">{(chart.get('incarnation_cross') or {}).get('name', 'Unknown')}</div>
    </div>
  </div>
  
  <div class="highlight-box">
    <h3>✨ Your Signature Theme</h3>
    <p>When you're living in alignment with your design, you feel <strong>{chart.get('signature', 'fulfilled and satisfied')}</strong>. When you're not, you experience <strong>{chart.get('not_self_theme', 'frustration')}</strong> — this is your built-in feedback system.</p>
  </div>
"""
    
    # ── Section 2: Type Deep Dive ──
    type_name = (chart.get('hd_type') or "").lower()
    type_descriptions = {
        "manifestor": "As a <strong>Manifestor</strong>, you're here to initiate and impact. You don't need to wait — your strategy is to <strong>Inform</strong> before you act. Your closed and repelling aura means people can feel your presence before you speak. When you inform those who'll be affected by your decisions, you remove resistance and create peace.",
        "generator": "As a <strong>Generator</strong>, you're the life force of the planet. Your strategy is to <strong>Respond</strong> — not to initiate, but to wait for life to come to you, then respond with your sacral yes or no. Your open and enveloping aura draws opportunities. Trust your gut sound (uh-huh / uh-uh) — it knows before your mind does.",
        "manifesting generator": "As a <strong>Manifesting Generator</strong>, you have the energy of a Generator with the speed of a Manifestor. Your strategy is to <strong>Respond</strong>, then <strong>Inform</strong> before you leap into action. You're designed to be multi-passionate and fast — don't let anyone tell you to slow down or pick just one thing. Trust your sacral response, then move.",
        "projector": "As a <strong>Projector</strong>, you're here to guide, manage, and see deeply into others. You don't have consistent generating energy — your strategy is to <strong>Wait for the Invitation</strong>. Recognition must come before your guidance is received. Your focused and absorbing aura allows you to read people with remarkable accuracy. Rest is not laziness — it's your design.",
        "reflector": "As a <strong>Reflector</strong>, you're the rarest type — a mirror of the community. Your strategy is to <strong>Wait a Lunar Cycle</strong> (28 days) before major decisions. With no defined centers, you sample and reflect the energy around you. Your wellbeing is the community's barometer. Protect your environment fiercely.",
    }
    desc = type_descriptions.get(type_name, f"You are uniquely designed with the strategy of <strong>{chart.get('strategy', 'being yourself')}</strong>.")
    html += f"""
  <h2>🔮 Understanding Your Type</h2>
  <p>{desc}</p>
"""
    
    # ── Section 3: Defined Centers ──
    defined = chart.get('defined_centers', [])
    undefined = chart.get('undefined_centers', [])
    
    center_descriptions = {
        "Head": "Mental pressure and inspiration — you have consistent access to ideas and questions that inspire others.",
        "Ajna": "Conceptualization and certainty — you process information in a fixed, reliable way.",
        "Throat": "Communication and manifestation — you have a consistent voice and way of expressing yourself.",
        "G": "Identity and direction — you carry a stable sense of self and life direction.",
        "Heart/Ego": "Willpower and value — you have consistent access to willpower and a sense of self-worth on the material plane.",
        "Sacral": "Life force and response — you have sustainable generating energy and reliable gut responses.",
        "Spleen": "Intuition and survival — you have consistent access to instinctual awareness about health and safety.",
        "Solar Plexus": "Emotions and clarity — you experience emotional waves that bring depth and eventual clarity.",
        "Root": "Pressure and drive — you have a consistent pulse of adrenaline to get things done.",
    }
    
    html += """
  <h2>🔮 Your Defined Centers</h2>
  <p class="section-intro">Defined centers carry consistent, reliable energy. These are your natural gifts — the ways you consistently show up and impact others.</p>
  """
    if defined:
        for c in defined:
            html += f'  <p><strong>{c}</strong>: {center_descriptions.get(c, "")}</p>\n'
    else:
        html += "  <p><em>No centers defined — you're a Reflector, sampling and reflecting the world's energy.</em></p>\n"
    
    html += """
  <h2>🌊 Your Open Centers</h2>
  <p class="section-intro">Undefined and open centers are where you're deeply perceptive — and where you take in and amplify the energy of others. This is your wisdom, not a weakness.</p>
  """
    if undefined:
        open_wisdom = {
            "Head": "You're deeply curious and can entertain infinite perspectives — just don't let mental pressure force you into decisions.",
            "Ajna": "You can hold multiple truths at once — your open mind is a gift for seeing all angles. Don't feel pressured to be certain.",
            "Throat": "You can speak in many voices — adapt your communication to any audience. Wait to be recognized before speaking.",
            "G": "You're a chameleon of identity — you can find home anywhere. Don't worry about 'finding yourself'; you find yourself through the right people and places.",
            "Heart/Ego": "You have nothing to prove — your worth isn't measured by achievements. Rest when you need to.",
            "Sacral": "You amplify others' energy — don't overwork trying to keep up with generators. Your not-knowing is healthy.",
            "Spleen": "You're deeply attuned to others' wellbeing — but don't hold onto what's not yours. Let go freely.",
            "Solar Plexus": "You feel everything, including others' emotions — learn to ask: is this mine? Avoid confrontation when emotionally charged.",
            "Root": "You amplify urgency — don't let others' stress become yours. Practice doing things at your own pace.",
        }
        for c in undefined:
            html += f'  <p><strong>{c}</strong>: {open_wisdom.get(c, "")}</p>\n'
    
    # ── Section 4: Channels ──
    channels = chart.get('defined_channels', [])
    html += f"""
  <h2>🔗 Your Defined Channels ({len(channels)})</h2>
  <p class="section-intro">Channels are the energetic pathways connecting your centers. Each carries a specific theme and gift.</p>
"""
    if channels:
        for ch in channels:
            gates = ch.get('gates', (0,0))
            name = ch.get('name', 'Unknown Channel')
            html += f"""
  <div class="channel-row">
    <span class="channel-name">{name}</span>
    <span class="channel-gates">Gates {gates[0]}–{gates[1]}</span>
  </div>"""
    else:
        html += "  <p><em>You have no defined channels — all your gates hang individually, creating a unique openness.</em></p>\n"
    
    # ── Section 5: Gates ──
    personality_gates = chart.get('personality_gates', [])
    design_gates = chart.get('design_gates', [])
    all_gates = sorted(set(
        (g.get('gate') if isinstance(g, dict) else g) 
        for g in (personality_gates + design_gates) 
        if (isinstance(g, dict) and g.get('gate')) or isinstance(g, (int, float))
    ))
    
    if all_gates:
        html += f"""
  <h2>🧬 Your Activated Gates ({len(all_gates)})</h2>
  <p class="section-intro">Each activated gate represents a specific energetic frequency in your chart. Together they form the unique symphony of your design.</p>
  <div class="gate-list">
"""
        for g in all_gates:
            gname = GATE_NAMES.get(int(g), f"Gate {g}")
            html += f'    <span class="gate-badge">Gate {g}: {gname}</span>\n'
        html += "  </div>\n"
    
    # ── Section 6: Variables ──
    variables = chart.get('variables', [])
    if isinstance(variables, list) and len(variables) >= 7:
        var_labels = ["Digestion", "Environment", "Perspective", "Motivation", "Sense", "Cognition", "Trajectory"]
        html += """
  <h2>🧭 Your Variables (The Four Transformations)</h2>
  <p class="section-intro">Variables describe how you digest life, your ideal environment, how you see the world, and what drives you.</p>
  <table>
    <tr><th>Transformation</th><th>Your Configuration</th></tr>
"""
        for i, label in enumerate(var_labels[:4]):
            html += f"    <tr><td><strong>{label}</strong></td><td>{variables[i] if i < len(variables) else 'Unknown'}</td></tr>\n"
        html += "  </table>\n"
        
        # Additional variables
        extra_vars = [
            ("Sense", chart.get('sense', '')),
            ("Cognition", chart.get('cognition', '')),
            ("Trajectory", chart.get('trajectory', '')),
        ]
        html += """
  <h3>Advanced Variables</h3>
  <table>
    <tr><th>Aspect</th><th>Configuration</th></tr>
"""
        for label, val in extra_vars:
            if val:
                html += f"    <tr><td><strong>{label}</strong></td><td>{val}</td></tr>\n"
        html += "  </table>\n"
    
    # ── Section 7: Incarnation Cross ──
    cross = chart.get('incarnation_cross', {})
    if cross:
        html += f"""
  <h2>✝️ Your Incarnation Cross</h2>
  <p class="section-intro">Your incarnation cross represents your life theme — the purpose your vehicle carries through this lifetime.</p>
  <div class="highlight-box">
    <h3>{cross.get('name', 'Your Life Theme')}</h3>
    <p>This cross is carried by approximately {cross.get('population_percent', 'a small')}% of the population.</p>
  </div>
"""
    
    # ── Section 8: Living Your Design ──
    html += f"""
  <h2>🚀 Living Your Design: Practical Experiments</h2>
  <p class="section-intro">Human Design isn't a belief system — it's an experiment. Here are practical ways to test your design in daily life.</p>
  
  <div class="experiment-box">
    <h3>Experiment 1: Follow Your Strategy</h3>
    <p>For the next 3 days, practice <strong>{chart.get('strategy', 'your strategy')}</strong>. Notice what changes.</p>
  </div>
  
  <div class="experiment-box">
    <h3>Experiment 2: Notice Your Signature</h3>
    <p>Pay attention to when you feel <strong>{chart.get('signature', 'aligned')}</strong> vs <strong>{chart.get('not_self_theme', 'off')}</strong>. These are your internal compass directions.</p>
  </div>
  
  <div class="experiment-box">
    <h3>Experiment 3: Observe Your Open Centers</h3>
    <p>Notice when you're amplifying energy from others. Ask: is this mine, or am I picking it up?</p>
  </div>
  
  <div class="cert-badge">
    🌿 Verified by OpenHumanDesignMCP — open-source calculations (AGPLv3) <span class="badge">Certified by Light Filled Human Design</span>
  </div>
  
  <div class="footer">
    <p>Report generated by <a href="https://humandesignengine.com">Human Design Engine</a></p>
    <p>Calculations powered by OpenHumanDesignMCP v0.3.0 · <a href="https://github.com/mbgulden/OpenHumanDesignMCP">github.com/mbgulden/OpenHumanDesignMCP</a></p>
    <p>AGPLv3 — Free Software</p>
  </div>
</div>
</body></html>"""
    
    return html


def build_relationship_report(chart_a: dict, chart_b: dict, composite: dict) -> str:
    """Generate a relationship / synastry report as HTML."""
    name_a = chart_a.get("name", "Person A")
    name_b = chart_b.get("name", "Person B")
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{name_a} & {name_b} Relationship</title>{CSS}</head><body>
{make_cover(f'{name_a} & {name_b}', 'relationship', date_str)}
<div class="page">

  <h2>💞 Your Connection at a Glance</h2>
  <p class="section-intro">Every relationship is a unique energetic dance. This report reveals how your designs interact — where you lift each other up, and where you need to give each other space.</p>
  
  <div class="center-grid">
    <div class="center-box defined">
      <h3>{name_a}</h3>
      <ul>
        <li><strong>Type:</strong> {chart_a.get('hd_type', 'Unknown')}</li>
        <li><strong>Profile:</strong> {chart_a.get('profile', 'Unknown')}</li>
        <li><strong>Authority:</strong> {chart_a.get('authority', 'Unknown')}</li>
        <li><strong>Strategy:</strong> {chart_a.get('strategy', 'Unknown')}</li>
      </ul>
    </div>
    <div class="center-box defined">
      <h3>{name_b}</h3>
      <ul>
        <li><strong>Type:</strong> {chart_b.get('hd_type', 'Unknown')}</li>
        <li><strong>Profile:</strong> {chart_b.get('profile', 'Unknown')}</li>
        <li><strong>Authority:</strong> {chart_b.get('authority', 'Unknown')}</li>
        <li><strong>Strategy:</strong> {chart_b.get('strategy', 'Unknown')}</li>
      </ul>
    </div>
  </div>
"""
    
    # Composite data
    if composite:
        comp_data = composite.get('result', composite)
        channels = comp_data.get('composite_channels', comp_data.get('defined_channels', []))
        gates = comp_data.get('composite_gates', comp_data.get('all_active_gates', []))
        shared = comp_data.get('shared_gates', [])
        electromagnetics = comp_data.get('electromagnetic_channels', [])
        compromises = comp_data.get('compromise_gates', [])
        
        html += f"""
  <h2>🔗 Your Composite Channels ({len(channels)})</h2>
  <p class="section-intro">When your charts combine, these channels emerge — representing the shared energy and purpose of your relationship.</p>
"""
        if channels:
            for ch in channels:
                if isinstance(ch, dict):
                    html += f"""
  <div class="channel-row">
    <span class="channel-name">{ch.get('name', 'Unknown')}</span>
    <span class="channel-gates">Gates {ch.get('gates', (0,0))}</span>
  </div>"""
        else:
            html += "  <p><em>Your composite chart doesn't define any channels — your relationship is more about openness and learning than fixed dynamics.</em></p>\n"
        
        gates_display = [g for g in gates if isinstance(g, (int, float)) or (isinstance(g, dict) and g.get('gate'))]
        if gates_display:
            html += f"""
  <h2>🧬 Shared Gates ({len(gates_display)})</h2>
  <div class="gate-list">
"""
            for g in gates_display[:30]:
                gval = g.get('gate') if isinstance(g, dict) else int(g)
                gname = GATE_NAMES.get(int(gval), f"Gate {gval}")
                html += f'    <span class="gate-badge">Gate {gval}: {gname}</span>\n'
            html += "  </div>\n"
        
        if electromagnetics:
            html += f"""
  <h2>⚡ Electromagnetic Channels ({len(electromagnetics)})</h2>
  <p class="section-intro">These channels form when one of you has one gate and the other has the complementary gate. They create powerful attraction — and can be your relationship's greatest source of both connection and friction.</p>
"""
            for em in electromagnetics:
                html += f'  <p>⚡ <strong>Channel {em}</strong></p>\n'
        
        if compromises:
            html += f"""
  <h2>🤝 Compromise Gates ({len(compromises)})</h2>
  <p class="section-intro">Where one chart's definition dominates — an opportunity for the dominant person to hold space, and the other to be held.</p>
"""
            for cg in compromises:
                html += f'  <p>🤝 Gate {cg}</p>\n'
    
    html += """
  <div class="experiment-box">
    <h3>💡 Relationship Wisdom</h3>
    <p>In Human Design, differences aren't problems to fix — they're the mechanics of how you grow each other. Your partner's 'not-you' is their gift to you. Your differences are the curriculum.</p>
  </div>
  
  <div class="cert-badge">
    🌿 Verified by OpenHumanDesignMCP · <span class="badge">Light Filled Human Design</span>
  </div>
  
  <div class="footer">
    <p>Report generated by <a href="https://humandesignengine.com">Human Design Engine</a></p>
    <p>AGPLv3 — Free Software</p>
  </div>
</div>
</body></html>"""
    
    return html


def compute_30day_solar_transits() -> list:
    """Compute solar gate positions for the next 30 days.
    Groups consecutive days with the same gate into date-range entries.
    Returns list of {start_date, end_date, gate, gate_name, center} dicts."""
    from datetime import datetime, timezone, timedelta
    
    raw = []
    for i in range(30):
        dt = datetime.now(timezone.utc) + timedelta(days=i)
        jd = datetime_to_jd(dt)
        try:
            pos = get_planet_position(jd, SUN)
            from matrix_mapper import longitude_to_gate_line
            hd = longitude_to_gate_line(pos["longitude"])
            raw.append({
                "date_str": dt.strftime("%B %d"),
                "iso_date": dt.strftime("%Y-%m-%d"),
                "gate": hd["gate"],
                "gate_name": hd["gate_name"],
                "center": hd["center"],
            })
        except Exception:
            continue
    
    if not raw:
        return []
    
    # Group consecutive days with the same gate
    grouped = []
    current = dict(raw[0], start_date=raw[0]["date_str"], end_date=raw[0]["date_str"])
    for entry in raw[1:]:
        if entry["gate"] == current["gate"]:
            current["end_date"] = entry["date_str"]
        else:
            grouped.append({
                "start_date": current["start_date"],
                "end_date": current["end_date"],
                "gate": current["gate"],
                "gate_name": current["gate_name"],
                "center": current["center"],
            })
            current = dict(entry, start_date=entry["date_str"], end_date=entry["date_str"])
    grouped.append({
        "start_date": current["start_date"],
        "end_date": current["end_date"],
        "gate": current["gate"],
        "gate_name": current["gate_name"],
        "center": current["center"],
    })
    return grouped


def build_transit_report(natal: dict, overlay: dict, solar_forecast: list = None) -> str:
    """Generate a comprehensive transit forecast report."""
    name = natal.get("name", "Friend")
    date_str = datetime.now().strftime("%B %d, %Y")
    
    # ── Extract data ──────────────────────────────────────────────────
    overlay = overlay or {}
    conditioning = overlay.get("conditioning", {})
    conditioned_channels = conditioning.get("conditioned_channels", [])
    conditioned_centers = conditioning.get("conditioned_centers", [])
    new_transit_gates = conditioning.get("new_transit_gates", [])
    interpretation_hints = overlay.get("interpretation_hints", [])
    
    # Get full transit positions (with retrograde, longitude for the table)
    try:
        full_positions = calculate_transit_positions()
    except Exception:
        full_positions = {}
    
    # Get simplified transit positions from overlay
    transit_positions = overlay.get("transit_positions", full_positions)
    
    natal_type = natal.get("hd_type", "Unknown")
    natal_authority = natal.get("authority", "Unknown")
    natal_strategy = natal.get("strategy", "Unknown")
    natal_signature = natal.get("signature", "fulfillment")
    natal_not_self = natal.get("not_self_theme", "frustration")
    natal_defined = set(natal.get("defined_centers", []))
    natal_undefined = set(natal.get("undefined_centers", []))
    
    # All transit gates for the badge display
    all_transit_gates = sorted(set(
        p.get("gate") for p in transit_positions.values() if p.get("gate")
    ))
    
    # Conditioned but normally undefined centers
    conditioned_open = [c for c in conditioned_centers if c not in natal_defined]
    
    # Solar forecast data
    solar_forecast = solar_forecast or []
    current_solar_gate = solar_forecast[0] if solar_forecast else None
    
    # ── HTML Generation ───────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{name}'s Transit Forecast</title>{CSS}</head><body>
{make_cover(name, 'transit', date_str)}
<div class="page">

  <h2>🌟 Your Current Transit Snapshot</h2>
  <p class="section-intro">Planetary transits are like cosmic weather — they activate different parts of your chart each day. This report shows what's being lit up in your unique design right now, how it's conditioning your open centers, and what themes the coming month holds for you.</p>
  
  <div class="stat-grid">
    <div class="stat-card">
      <div class="label">Your Type</div>
      <div class="value">{natal_type}</div>
    </div>
    <div class="stat-card">
      <div class="label">Your Authority</div>
      <div class="value">{natal_authority}</div>
    </div>
    <div class="stat-card">
      <div class="label">Your Strategy</div>
      <div class="value">{natal_strategy}</div>
    </div>
    <div class="stat-card">
      <div class="label">Transit Date</div>
      <div class="value">{date_str}</div>
    </div>
    <div class="stat-card">
      <div class="label">Channels Being Conditioned</div>
      <div class="value">{conditioning.get('total_conditioned_channels', 0)}</div>
    </div>
    <div class="stat-card">
      <div class="label">Centers Being Conditioned</div>
      <div class="value">{len(conditioned_centers)}</div>
    </div>
  </div>
  
  <div class="highlight-box">
    <h3>🌊 What Are Transits?</h3>
    <p>As the planets move through the sky, they pass through different gates — activating specific themes and energies. For your <strong>{natal_type}</strong> design, transits temporarily condition your undefined centers. They bring experiences and flavors that aren't consistently yours — like visiting a new city. The key is awareness: <em>is this my energy, or am I sampling something passing through?</em> Your signature of <strong>{natal_signature}</strong> is your compass. When you feel <strong>{natal_not_self}</strong>, a transit may be pulling you off-center.</p>
  </div>
  
  <h2>🪐 Current Planetary Positions</h2>
  <p class="section-intro">Each planet carries a unique frequency as it moves through the gates. Below are the exact positions at the moment this report was generated.</p>
  <table>
    <tr><th>Planet</th><th>Gate</th><th>Gate Name</th><th>Line</th><th>Center</th><th>Rx</th></tr>
"""
    
    # Build planet position rows
    planet_order = ["Sun", "Earth", "Moon", "North Node", "South Node", 
                    "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                    "Uranus", "Neptune", "Pluto", "Chiron", "Mean Lilith", "True Lilith"]
    for planet_name in planet_order:
        pos = full_positions.get(planet_name)
        if pos and pos.get("gate"):
            retro = "℞" if pos.get("retrograde") else ""
            html += f"""    <tr>
      <td><strong>{planet_name}</strong></td>
      <td>Gate {pos['gate']}</td>
      <td>{pos.get('gate_name', '')}</td>
      <td>Line {pos['line']}</td>
      <td>{pos.get('center', '')}</td>
      <td>{retro}</td>
    </tr>
"""
    
    # Any remaining planets not in our order
    for planet_name, pos in full_positions.items():
        if planet_name not in planet_order and pos.get("gate"):
            retro = "℞" if pos.get("retrograde") else ""
            html += f"""    <tr>
      <td><strong>{planet_name}</strong></td>
      <td>Gate {pos['gate']}</td>
      <td>{pos.get('gate_name', '')}</td>
      <td>Line {pos['line']}</td>
      <td>{pos.get('center', '')}</td>
      <td>{retro}</td>
    </tr>
"""
    
    html += """  </table>
  
  <h2>🧬 All Activated Transit Gates</h2>
  <p class="section-intro">These are all the gates currently being activated by planetary transits. When a transit gate matches one in your natal chart, it amplifies your natural expression. When it's new to you, it introduces a temporary theme to explore.</p>
  <div class="gate-list">
"""
    for g in all_transit_gates:
        gname = GATE_NAMES.get(int(g), f"Gate {g}")
        html += f'    <span class="gate-badge">Gate {g}: {gname}</span>\n'
    html += """  </div>
  
"""
    
    # ── Section 2: Conditioning Analysis ──
    html += """  <h2>🔮 How Transits Are Conditioning Your Chart</h2>
  <p class="section-intro">Transits interact with your natal design in specific, measurable ways. Below is a personalized analysis of what's being conditioned in your chart right now.</p>
"""
    
    # Conditioned channels
    if conditioned_channels:
        html += f"""  
  <h3>🔗 Temporarily Completed Channels ({len(conditioned_channels)})</h3>
  <p class="section-intro">When a transit provides the missing gate to one of your hanging gates, a full channel temporarily lights up. This is <em>borrowed definition</em> — energy available to you right now that isn't consistently yours.</p>
"""
        for ch in conditioned_channels:
            gates = ch.get("gates", (0, 0))
            name = ch.get("name", "Unknown Channel")
            natal_has = ch.get("natal_has", gates[0])
            transit_provides = ch.get("transit_provides", gates[1])
            html += f"""  <div class="channel-row">
    <span class="channel-name">{name}</span>
    <span class="channel-gates">Your Gate {natal_has} + Transit Gate {transit_provides} → Gates {gates[0]}–{gates[1]}</span>
  </div>
"""
    else:
        html += """  <h3>🔗 Temporarily Completed Channels</h3>
  <p><em>No channels are being completed by transits at this time. Your hanging gates remain open — this is a time of pure self, without borrowed definition.</em></p>
"""
    
    # Conditioned open centers
    if conditioned_open:
        open_wisdom = {
            "Head": "You may feel extra mental pressure or sudden inspiration. Notice: is this idea yours, or is it the transit speaking? Let questions arise but don't feel pressured to answer them immediately.",
            "Ajna": "Your mind may feel unusually certain right now — or flooded with competing ideas. This is borrowed conceptual energy. Hold ideas lightly; your open mind's gift is seeing all perspectives, not being locked into one.",
            "Throat": "You may feel a strong urge to speak, initiate, or be heard. Is it your truth, or are you amplifying the transit's need to express? Wait for recognition before speaking — your words land differently under transit influence.",
            "G": "Your sense of identity or direction may feel temporarily clear — or suddenly confused. Transits through the G center can make you feel like you've 'found yourself' or lost yourself entirely. Both are temporary. Trust your environment to hold you.",
            "Heart/Ego": "You may feel a surge of willpower or a pressure to prove your worth. Remember: your value is inherent, not measured by what you accomplish during this transit window. Rest is still valid.",
            "Sacral": "You may feel an unusual burst of sustainable energy — or absolutely drained. Transits through an undefined Sacral can make you overwork trying to 'keep up' with borrowed life force. Your not-knowing what to do is healthy. Wait to respond.",
            "Spleen": "Your intuition may feel sharper, or you may feel inexplicably anxious about health and safety. Transits through the Spleen give you access to instinctual awareness you don't normally carry. Trust the hits, but don't hold onto fear that isn't yours.",
            "Solar Plexus": "Emotions may feel intense, dramatic, or unusually clear. You're sampling the emotional wave of the transit. Ask: is this feeling mine, or am I amplifying something from outside? Wait for clarity before making emotional decisions.",
            "Root": "You may feel a surge of urgency or pressure to act immediately. This is borrowed adrenaline. Practice doing things at your own pace — the pressure will pass with the transit.",
        }
        html += f"""  
  <h3>🌊 Conditioned Open Centers ({len(conditioned_open)})</h3>
  <p class="section-intro">These are your normally undefined centers that are being temporarily conditioned by current transits. This is where you're most likely to feel something <em>different</em> today.</p>
"""
        for c in conditioned_open:
            wisdom = open_wisdom.get(c, "This center is being temporarily conditioned — notice what feels different and ask yourself if it's truly yours.")
            html += f"""  <div class="highlight-box">
    <h3>✦ {c} Center</h3>
    <p>{wisdom}</p>
  </div>
"""
    
    # Interpretation hints
    if interpretation_hints:
        html += """  
  <h3>💡 Key Transit Messages for You</h3>
"""
        for hint in interpretation_hints:
            html += f'  <p>▸ {hint}</p>\n'
    
    # New transit gates
    if new_transit_gates:
        html += f"""  
  <h3>🆕 Gates New to Your Design ({len(new_transit_gates)})</h3>
  <p class="section-intro">These gates are being activated by transits but don't appear in your natal chart. They represent themes that are visiting you — temporary flavors to sample and learn from.</p>
  <div class="gate-list">
"""
        for g in new_transit_gates:
            gname = GATE_NAMES.get(int(g), f"Gate {g}")
            html += f'    <span class="gate-badge">Gate {g}: {gname}</span>\n'
        html += """  </div>
"""
    
    # ── Section 3: 30-Day Solar Transit Forecast ──
    html += """  
  <h2>📅 Your 30-Day Solar Transit Forecast</h2>
  <p class="section-intro">The Sun moves approximately one degree per day, spending about 5–6 days in each gate. As it shifts, different themes light up in your chart. Below is your forecast for the coming month.</p>
"""
    
    if solar_forecast:
        html += """  <table>
    <tr><th>Period</th><th>Gate</th><th>Theme</th><th>Center</th></tr>
"""
        for entry in solar_forecast:
            period = entry["start_date"]
            if entry["start_date"] != entry["end_date"]:
                period += f" – {entry['end_date']}"
            html += f"""    <tr>
      <td><strong>{period}</strong></td>
      <td>Gate {entry['gate']}</td>
      <td>{entry['gate_name']}</td>
      <td>{entry['center']}</td>
    </tr>
"""
        html += """  </table>
"""
        
        # Current solar gate theme
        if current_solar_gate:
            html += f"""  
  <div class="highlight-box">
    <h3>☀️ Current Solar Theme: Gate {current_solar_gate['gate']} — {current_solar_gate['gate_name']}</h3>
    <p>Right now, the Sun is activating <strong>Gate {current_solar_gate['gate']} ({current_solar_gate['gate_name']})</strong> in the <strong>{current_solar_gate['center']}</strong> center. This sets the collective tone — the question or theme that humanity as a whole is working with. For you personally, this gate {'is part of your consistent definition — it may feel amplified and familiar' if current_solar_gate['gate'] in (natal.get('all_active_gates', []) or []) else 'is not in your natal chart — it brings a visiting theme that you get to explore and learn from temporarily'}.</p>
  </div>
"""
    else:
        html += """  <p><em>Solar transit forecast data is being calculated. Check back shortly for your personalized 30-day forecast.</em></p>
"""
    
    # ── Section 4: Practical Guidance ──
    html += f"""  
  <h2>🧭 Practical Guidance for Current Transits</h2>
  <p class="section-intro">Transits are not here to derail you — they're here to awaken you. Here's how to navigate current cosmic weather as your unique design type.</p>
"""
    
    # Type-specific transit advice
    type_advice = {
        "manifestor": {
            "strategy": "Inform before you act — even under transit influence, your power lies in clearing the path by communicating your intentions.",
            "practice": "Before taking action on any transit-inspired impulse, pause and inform at least one person who'll be affected. Notice if the urge is truly yours or transit-driven.",
            "gift": "Transits can amplify your natural initiating power. Use borrowed definition to start things, but don't get attached — the energy may leave when the transit does.",
        },
        "generator": {
            "strategy": "Respond, don't initiate — transits may create mental pressure to start something new, but your power is in answering what life brings you.",
            "practice": "When a transit lights up a new gate, wait for something in your outer reality to ask something of you before engaging. Trust your sacral sound: uh-huh (yes) or uh-uh (no).",
            "gift": "Transits through your undefined centers give you a taste of other ways of being. Notice what feels satisfying vs. frustrating — this is feedback about alignment.",
        },
        "manifesting generator": {
            "strategy": "Respond, then inform — transits may accelerate your already-fast nature. Don't skip the response step — wait for the sacral yes before leaping.",
            "practice": "When a transit lights you up with a new idea or direction, check in with your gut first. Then inform those who need to know before you move at your natural speed.",
            "gift": "Transits can give you access to even more life force. Channel borrowed energy into what already lights you up, not into new commitments you can't sustain.",
        },
        "projector": {
            "strategy": "Wait for the invitation — transits may make you feel like a Generator, but your success still comes through recognition and invitation.",
            "practice": "If a transit makes you want to work harder or initiate more, pause. Ask: have I been recognized and invited for this specific thing? Your guidance is most potent when asked for.",
            "gift": "Transits through your open centers give you a deeper read on others. Use this temporary clarity to see more, but don't feel you must act on everything you perceive.",
        },
        "reflector": {
            "strategy": "Wait a full lunar cycle (28 days) — transits ARE your definition. You're designed to sample everything. Don't make big decisions based on temporary definition.",
            "practice": "Track how you feel as the Moon and Sun move through different gates. Your experience literally changes with the transit weather — this isn't inconsistency, it's your design.",
            "gift": "You're the most transit-sensitive type. Use this report to understand WHY you feel different day to day. Your wellbeing is a barometer of the collective.",
        },
    }
    
    type_key = natal_type.lower().replace(" ", " ").strip()
    # Normalize lookup
    type_lookup = {
        "manifestor": "manifestor", "generator": "generator",
        "manifesting generator": "manifesting generator", "manifesting-generator": "manifesting generator",
        "projector": "projector", "reflector": "reflector",
    }
    advice_key = type_lookup.get(type_key, "generator")
    advice = type_advice.get(advice_key, type_advice["generator"])
    
    html += f"""  
  <div class="experiment-box">
    <h3>🎯 Your Strategy Under Transits: {natal_strategy}</h3>
    <p>{advice['strategy']}</p>
  </div>
  
  <div class="experiment-box">
    <h3>🧪 Practical Experiment for This Transit Period</h3>
    <p>{advice['practice']}</p>
  </div>
  
  <div class="experiment-box">
    <h3>🎁 The Gift of Current Transits for Your Design</h3>
    <p>{advice['gift']}</p>
  </div>
"""
    
    # Conditioned center-specific practices
    if conditioned_open:
        html += """  
  <h3>🔬 Working With Your Currently Conditioned Open Centers</h3>
"""
        for c in conditioned_open:
            center_practices = {
                "Head": "When you feel mental pressure, write down the questions but don't answer them yet. Let inspiration marinate.",
                "Ajna": "Practice saying 'I'm not sure yet' — your open mind's honesty is more powerful than borrowed certainty.",
                "Throat": "Notice when you're speaking to fill silence vs. speaking from truth. A simple pause before speaking changes everything.",
                "G": "If you feel lost or found, don't cling to either state. Let your environment and the right people guide you home.",
                "Heart/Ego": "Practice resting in the middle of productive energy. Take a break even when you feel driven — prove to yourself that your worth isn't in doing.",
                "Sacral": "Set a timer for work periods and honor it. When the timer goes off, stop — even if you still feel energized. This builds trust with your body.",
                "Spleen": "If you feel fear or intuitive hits, write them down and revisit in 24 hours. What was truly intuitive will persist; what was transit noise will fade.",
                "Solar Plexus": "Delay emotional decisions by at least one sleep cycle. Tell people: 'I need to feel through this before I know what's true.'",
                "Root": "When urgency strikes, ask: will this matter in a week? A month? Most transit-driven urgency dissolves when examined.",
            }
            practice = center_practices.get(c, "Notice what feels different. Ask: is this mine to carry, or can I let it pass through?")
            html += f"""  <p><strong>{c}:</strong> {practice}</p>
"""
    
    # ── Section 5: Monthly Themes ──
    html += """  
  <h2>🌙 Monthly Transit Themes</h2>
  <p class="section-intro">Zooming out, here's the broader transit landscape for the coming month — the energetic weather report for your journey.</p>
"""
    
    if solar_forecast and len(solar_forecast) >= 2:
        # Get unique centers being activated by upcoming solar transits
        upcoming_centers = sorted(set(e["center"] for e in solar_forecast if e.get("center")))
        upcoming_gates = [e["gate"] for e in solar_forecast]
        
        html += f"""  
  <div class="highlight-box">
    <h3>🗓️ Centers Being Highlighted This Month</h3>
    <p>Over the next 30 days, the Sun will move through these centers: <strong>{', '.join(upcoming_centers)}</strong>. Each center brings its own flavor of experience and conditioning. Pay special attention to days when the Sun activates a center that is undefined in your chart — those are the days you'll feel the transit most strongly.</p>
  </div>
  
  <div class="highlight-box">
    <h3>🔢 Gate Count This Month</h3>
    <p>The Sun will activate <strong>{len(set(upcoming_gates))} distinct gates</strong> over {len(solar_forecast)} transit periods. Some gates may feel more resonant than others — those that match your natal gates will amplify what's already you. Those that don't are your curriculum for the month.</p>
  </div>
"""
    
    # General monthly guidance
    html += f"""  
  <div class="experiment-box">
    <h3>📓 Your Transit Journal Prompt for This Month</h3>
    <p>For the next 30 days, each morning ask yourself: <em>"What center am I feeling most today?"</em> Write down one word and one observation. At the end of the month, look back — you'll see the transit weather written in your own experience. This practice builds self-awareness that no report can give you.</p>
  </div>
  
  <div class="experiment-box">
    <h3>🌿 A Note on Timing</h3>
    <p>Remember: transits are temporary. The energy you feel today will shift within days. Don't make permanent decisions based on temporary conditioning — especially if you're a <strong>Reflector</strong> (wait 28 days) or <strong>Projector</strong> (wait for the invitation). Use transits as a spotlight: they show you what's available to learn, not what you must become.</p>
  </div>
  
  <div class="cert-badge">
    🌿 Verified by OpenHumanDesignMCP — open-source calculations (AGPLv3) <span class="badge">Certified by Light Filled Human Design</span>
  </div>
  
  <div class="footer">
    <p>Report generated by <a href="https://humandesignengine.com">Human Design Engine</a></p>
    <p>Calculations powered by OpenHumanDesignMCP v0.3.0 · <a href="https://github.com/mbgulden/OpenHumanDesignMCP">github.com/mbgulden/OpenHumanDesignMCP</a></p>
    <p>Transit positions calculated at {date_str} · Forecast covers 30 days from today</p>
    <p>AGPLv3 — Free Software</p>
  </div>
</div>
</body></html>"""
    
    return html


# ── PDF Generation ────────────────────────────────────────────────────

def html_to_pdf(html_content: str, output_path: Path) -> Path:
    """Convert HTML to PDF using wkhtmltopdf."""
    html_path = output_path.with_suffix('.html')
    html_path.write_text(html_content)
    
    result = subprocess.run(
        ["wkhtmltopdf", "--quiet", "--enable-local-file-access",
         "--page-size", "Letter", "--margin-top", "0", "--margin-bottom", "0",
         "--margin-left", "0", "--margin-right", "0",
         "--no-stop-slow-scripts", "--javascript-delay", "1000",
         str(html_path), str(output_path)],
        capture_output=True, text=True, timeout=60
    )
    
    if result.returncode != 0:
        log.error("wkhtmltopdf failed: %s", result.stderr[:500])
        raise RuntimeError(f"PDF generation failed: {result.stderr[:200]}")
    
    return output_path


def compute_and_render(metadata: dict) -> dict:
    """Full pipeline: compute chart → render HTML → generate PDF → return path."""
    name = metadata.get("name", "Unknown")
    report_type = metadata.get("report", "natal")
    birthdate = metadata.get("birthdate", "2000-01-01")
    birthtime = metadata.get("birthtime", "12:00")
    location = metadata.get("location", "UTC")
    lat = float(metadata.get("lat", 0))
    lon = float(metadata.get("lon", 0))
    timezone = metadata.get("timezone", "UTC")
    
    # Parse birth data
    y, m, d = map(int, birthdate.split("-"))
    h, mi = map(int, birthtime.split(":"))
    birth_dt = datetime(y, m, d, h, mi)
    
    # Compute
    chart = calculate_natal_chart(
        name=name,
        birth_dt=birth_dt,
        lat=lat, lon=lon,
        timezone=timezone,
    )
    
    # Generate HTML
    if report_type == "natal":
        html = build_natal_report(chart)
    elif report_type == "transit":
        # Compute actual transit overlay
        overlay = compute_transit_overlay(chart)
        solar_forecast = compute_30day_solar_transits()
        html = build_transit_report(chart, overlay, solar_forecast)
    elif report_type == "relationship":
        partner = metadata.get("partner", {})
        if isinstance(partner, str) and partner:
            try:
                partner = json.loads(partner)
            except:
                partner = {}
        if partner:
            chart_b = calculate_natal_chart(
                name=partner.get("name", "Partner"),
                birth_dt=datetime(
                    int(partner.get("year", 2000)), int(partner.get("month", 1)),
                    int(partner.get("day", 1)), int(partner.get("hour", 12)), 0
                ),
                lat=float(partner.get("lat", 0)), lon=float(partner.get("lon", 0)),
                timezone=partner.get("timezone", "UTC"),
            )
            composite = {}
            try:
                composite = calculate_composite(
                    name_a=name, birth_a=chart,
                    name_b=partner.get("name", "Partner"), birth_b=chart_b
                )
            except Exception as e:
                log.warning("Composite calculation failed: %s", e)
            html = build_relationship_report(chart, chart_b, composite)
        else:
            html = build_natal_report(chart)
    else:
        html = build_natal_report(chart)
    
    # PDF
    safe_name = "".join(c if c.isalnum() else "_" for c in name)
    pdf_path = REPORTS_DIR / f"{safe_name}_{report_type}_{int(time.time())}.pdf"
    html_to_pdf(html, pdf_path)
    
    log.info("Generated PDF: %s (%d bytes)", pdf_path, pdf_path.stat().st_size)
    
    return {
        "pdf_path": str(pdf_path),
        "name": name,
        "report_type": report_type,
        "chart_summary": {
            "type": chart.get("hd_type"),
            "profile": chart.get("profile"),
            "authority": chart.get("authority"),
            "cross": (chart.get("incarnation_cross") or {}).get("name"),
        }
    }


def send_email(to_email: str, name: str, report_type: str, pdf_path: str):
    """Send PDF report via SMTP."""
    if not SMTP_USER:
        log.warning("SMTP not configured — skipping email to %s", to_email)
        return
    
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    import smtplib
    
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = f"Your Human Design {report_type.title()} Report is Ready, {name}!"
    
    body = f"""Hi {name},

Your Human Design {report_type.title()} Report is attached as a PDF.

This report was computed using verified, open-source calculations — the same engine trusted by developers and practitioners worldwide.

If you have any questions about your chart, we're here to help. Just reply to this email.

With gratitude,
The Human Design Engine Team
humandesignengine.com"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    with open(pdf_path, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=f'{name}_HD_{report_type}_Report.pdf')
        msg.attach(attachment)
    
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    
    log.info("Email sent to %s", to_email)


# ── HTTP Server ───────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    
    def _require_auth(self):
        key = self.headers.get('X-API-Key', '')
        if key != API_KEY:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized", "license": "AGPLv3"}).encode())
            return False
        return True
    
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
    
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self._json({})
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/ping':
            self._json({
                "status": "ok",
                "service": "hde-reports",
                "version": "0.1.0",
                "license": "AGPLv3",
                "engine": "OpenHumanDesignMCP v0.3.0",
            })
        elif path == '/api/reports':
            self._json({"reports": _load_orders()[-20:]})
        else:
            self._json({"error": "Not found"}, 404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        if path == '/api/compute':
            if not self._require_auth():
                return
            
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            
            try:
                result = compute_and_render(body)
                
                # Save order
                _save_order({
                    "name": body.get("name"),
                    "report": body.get("report"),
                    "email": body.get("email"),
                    "pdf_path": result["pdf_path"],
                    "timestamp": time.time(),
                })
                
                # Send email if requested
                email = body.get("email", "").strip()
                if email and SMTP_USER:
                    try:
                        send_email(email, body.get("name", "Friend"), body.get("report", "natal"), result["pdf_path"])
                    except Exception as e:
                        log.error("Email failed: %s", e)
                
                self._json({"success": True, **result})
            except Exception as e:
                log.exception("Compute failed")
                self._json({"success": False, "error": str(e)}, 500)
        
        elif path == '/api/compute-chart':
            # Simplified endpoint — just compute, no PDF
            if not self._require_auth():
                return
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            
            try:
                birth_dt = datetime(
                    body.get("year", 2000), body.get("month", 1), body.get("day", 1),
                    body.get("hour", 12), body.get("minute", 0)
                )
                chart = calculate_natal_chart(
                    name=body.get("name", "Unknown"),
                    birth_dt=birth_dt,
                    lat=body.get("lat", 0), lon=body.get("lon", 0),
                    timezone=body.get("timezone", "UTC"),
                )
                # Filter down to returnable keys
                keys = ['name', 'hd_type', 'profile', 'authority', 'strategy', 'definition',
                        'incarnation_cross', 'signature', 'not_self_theme',
                        'defined_centers', 'undefined_centers', 'defined_channels',
                        'sun_gate', 'sun_line', 'earth_gate', 'personality_gates', 'design_gates',
                        'variables']
                result = {k: chart.get(k) for k in keys if k in chart}
                self._json({"success": True, "data": result})
            except Exception as e:
                log.exception("Compute chart failed")
                self._json({"success": False, "error": str(e)}, 500)
        
        elif path == '/api/public/compute-chart':
            # Public endpoint — no auth required, for the embeddable widget
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            
            try:
                birth_dt = datetime(
                    body.get("year", 2000), body.get("month", 1), body.get("day", 1),
                    body.get("hour", 12), body.get("minute", 0)
                )
                chart = calculate_natal_chart(
                    name=body.get("name", "Unknown"),
                    birth_dt=birth_dt,
                    lat=body.get("lat", 0), lon=body.get("lon", 0),
                    timezone=body.get("timezone", "UTC"),
                )
                # Filter down to key data for the public widget
                keys = ['name', 'hd_type', 'profile', 'authority', 'strategy', 'definition',
                        'incarnation_cross', 'signature', 'not_self_theme',
                        'defined_centers', 'undefined_centers', 'defined_channels',
                        'sun_gate', 'sun_line', 'earth_gate', 'personality_gates', 'design_gates',
                        'variables']
                result = {k: chart.get(k) for k in keys if k in chart}
                self._json({"success": True, "data": result})
            except Exception as e:
                log.exception("Public compute chart failed")
                self._json({"success": False, "error": str(e)}, 500)
        
        elif path == '/api/public/bodygraph':
            # Public endpoint — compute chart and return SVG bodygraph
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            
            try:
                import subprocess, tempfile
                
                birth_dt = datetime(
                    body.get("year", 2000), body.get("month", 1), body.get("day", 1),
                    body.get("hour", 12), body.get("minute", 0)
                )
                chart = calculate_natal_chart(
                    name=body.get("name", "Unknown"),
                    birth_dt=birth_dt,
                    lat=body.get("lat", 0), lon=body.get("lon", 0),
                    timezone=body.get("timezone", "UTC"),
                )
                
                # Map to Gonzih ChartData
                pers_gates = set()
                des_gates = set()
                for p, d in chart.get("personality_planets", {}).items():
                    if isinstance(d, dict) and d.get("gate"):
                        pers_gates.add(d["gate"])
                for p, d in chart.get("design_planets", {}).items():
                    if isinstance(d, dict) and d.get("gate"):
                        des_gates.add(d["gate"])
                
                both_gates = sorted(pers_gates & des_gates)
                pers_only = sorted(pers_gates - des_gates)
                des_only = sorted(des_gates - pers_gates)
                
                def _act(planets_dict):
                    result = {}
                    for planet, data in planets_dict.items():
                        if isinstance(data, dict):
                            g = data.get("gate", "")
                            l = data.get("line", "")
                            if g:
                                result[planet.lower().replace(" ", "")] = f"{g}.{l}" if l else str(g)
                    return result
                
                center_map = {"Heart": "Ego", "Heart/Ego": "Ego"}
                gonzih_data = {
                    "definedCenters": [center_map.get(c, c) for c in chart.get("defined_centers", [])],
                    "personalityGates": pers_only,
                    "designGates": des_only,
                    "bothGates": both_gates,
                    "channels": [
                        ch["gates"] for ch in chart.get("defined_channels", [])
                        if len(ch.get("gates", ())) == 2
                    ],
                    "type": chart.get("hd_type", ""),
                    "profile": str(chart.get("profile", "")),
                    "definition": chart.get("definition", ""),
                    "authority": chart.get("authority", ""),
                    "strategy": chart.get("strategy", ""),
                    "activations": {
                        "design": _act(chart.get("design_planets", {})),
                        "personality": _act(chart.get("personality_planets", {})),
                    },
                }
                
                # Call Node.js renderer
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                    json.dump(gonzih_data, f)
                    tmp = f.name
                
                try:
                    result = subprocess.run(
                        ["node", "/home/ubuntu/work/hd-bodygraph/render-cli.mjs", tmp, "canonical"],
                        capture_output=True, text=True, timeout=15,
                        cwd="/home/ubuntu/work/hd-bodygraph",
                    )
                    if result.returncode != 0:
                        raise RuntimeError(f"Renderer failed: {result.stderr}")
                    svg = result.stdout
                finally:
                    os.unlink(tmp)
                
                self.send_response(200)
                self.send_header("Content-Type", "image/svg+xml")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(svg.encode())
                return
                
            except Exception as e:
                log.exception("Bodygraph generation failed")
                self._json({"success": False, "error": str(e)}, 500)
        
        elif path == '/api/public/capture-lead':
            # Public endpoint — capture lead email + birth data from free chart widget
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            
            email = body.get('email', '').strip()
            if not email:
                self._json({"success": False, "error": "Email required"}, 400)
                return
            
            lead = {
                "email": email,
                "name": body.get("name", ""),
                "birth_date": body.get("birth_date", ""),
                "birth_time": body.get("birth_time", ""),
                "location": body.get("location", ""),
                "source": body.get("source", "free-chart-widget"),
                "page": body.get("page", ""),
                "timestamp": datetime.now().isoformat(),
                "ip": self.client_address[0],
            }
            
            # Save to leads file
            leads_file = REPORTS_DIR / "leads.json"
            leads = []
            if leads_file.exists():
                try:
                    leads = json.loads(leads_file.read_text())
                except Exception:
                    pass
            leads.append(lead)
            leads_file.write_text(json.dumps(leads, indent=2))
            
            log.info("Lead captured: %s from %s", email, lead["source"])
            self._json({"success": True, "message": "Lead captured"})
        
        else:
            self._json({"error": "Not found"}, 404)
    
    def log_message(self, format, *args):
        log.info("%s %s", self.address_string(), args[0])


if __name__ == '__main__':
    log.info("🚀 HDE Report Server starting on port %d", PORT)
    log.info("   Engine: %s", ENGINE_PATH)
    log.info("   Endpoints: /ping /api/compute /api/compute-chart /api/public/compute-chart /api/public/capture-lead")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
