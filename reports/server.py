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
from ephemeris_engine import init_ephemeris

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


def build_transit_report(natal: dict, transits: dict) -> str:
    """Generate a transit forecast report."""
    name = natal.get("name", "Friend")
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{name}'s Transit Forecast</title>{CSS}</head><body>
{make_cover(name, 'transit', date_str)}
<div class="page">

  <h2>🌟 Your Current Transit Snapshot</h2>
  <p class="section-intro">Planetary transits activate different parts of your chart each day. This report shows what's being lit up in your design right now — and how to work with it.</p>
  
  <div class="stat-grid">
    <div class="stat-card">
      <div class="label">Your Type</div>
      <div class="value">{natal.get('hd_type', 'Unknown')}</div>
    </div>
    <div class="stat-card">
      <div class="label">Your Authority</div>
      <div class="value">{natal.get('authority', 'Unknown')}</div>
    </div>
    <div class="stat-card">
      <div class="label">Transit Date</div>
      <div class="value">{date_str}</div>
    </div>
  </div>
  
  <div class="highlight-box">
    <h3>🌊 Working With Transits</h3>
    <p>Transits condition your open centers — they bring temporary definition and themes. Notice what you're feeling today and ask: is this my consistent energy, or is this a transit passing through?</p>
  </div>
  
  <div class="footer">
    <p>Report generated by <a href="https://humandesignengine.com">Human Design Engine</a></p>
    <p>AGPLv3</p>
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
        html = build_transit_report(chart, {})
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
        
        else:
            self._json({"error": "Not found"}, 404)
    
    def log_message(self, format, *args):
        log.info("%s %s", self.address_string(), args[0])


if __name__ == '__main__':
    log.info("🚀 HDE Report Server starting on port %d", PORT)
    log.info("   Engine: %s", ENGINE_PATH)
    log.info("   Endpoints: /ping /api/compute /api/compute-chart /api/public/compute-chart")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
