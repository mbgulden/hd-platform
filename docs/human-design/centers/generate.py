#!/usr/bin/env python3
"""
Generate 9 Human Design Center SEO pages plus an index page.
Uses the same navy/gold design system as the gate and channel pages.
"""

import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)

CENTERS = {
    "Head": {
        "description": "The Head Center is the topmost center in the bodygraph and represents the pressure for inspiration, questions, and mental inquiry. It is a pressure center — always pushing us to ask 'why,' 'what if,' and 'how.' The Head Center does not answer questions; it only generates them. Its function is to create the mental pressure that fuels our search for meaning and understanding. When defined (colored), you have a consistent way of being inspired and asking questions. When undefined (white), you absorb and amplify the mental pressure and inspiration of others. The Head Center connects to the Ajna Center through three channels, creating the foundation of our mental architecture.",
        "function": "Pressure center — generates questions, inspiration, and mental pressure",
        "gates": [61, 63, 64],
        "channels": ["24-61 (Awareness)", "4-63 (Logic)", "47-64 (Abstraction)"],
        "connected_to": ["Ajna"],
    },
    "Ajna": {
        "description": "The Ajna Center is the awareness center responsible for conceptualization, opinions, and mental processing. Located between the Head and Throat centers, it receives the pressure of questions from above and works to formulate answers, concepts, and beliefs. The Ajna is where we process information, form opinions, and make sense of the world. When defined, you have a consistent and reliable way of thinking and conceptualizing. When undefined, your thinking is flexible and adaptive — you can see multiple perspectives and are not attached to any single viewpoint.",
        "function": "Awareness center — conceptualization, opinions, and mental processing",
        "gates": [4, 11, 17, 24, 43, 47],
        "channels": ["4-63 (Logic)", "11-56 (Curiosity)", "17-62 (Acceptance)", "24-61 (Awareness)", "23-43 (Structuring)", "47-64 (Abstraction)"],
        "connected_to": ["Head", "Throat"],
    },
    "Throat": {
        "description": "The Throat Center is the manifestation center — the nexus of expression in the bodygraph. Every energy in the body ultimately seeks expression through the Throat. It governs communication, action, and all forms of manifestation. The Throat is where thoughts become words, impulses become deeds, and inspiration becomes creation. When defined, you have a consistent way of expressing yourself and manifesting in the world. When undefined, your expression is variable and you may feel pressure to speak or act — learning to wait for the right timing is essential. The Throat connects to every other center through 11 channels, making it the most connected center in the bodygraph.",
        "function": "Manifestation center — communication, action, and expression",
        "gates": [8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62],
        "channels": ["1-8 (Inspiration)", "7-31 (The Alpha)", "10-20 (Awakening)", "12-22 (Openness)", "13-33 (The Prodigal)", "16-48 (Talent)", "17-62 (Acceptance)", "20-34 (Charisma)", "20-57 (Brainwave)", "21-45 (Money)", "23-43 (Structuring)", "31-7 (The Alpha)", "35-36 (Transitoriness)", "11-56 (Curiosity)"],
        "connected_to": ["G", "Ajna", "Sacral", "Spleen", "Solar Plexus", "Heart/Ego"],
    },
    "G": {
        "description": "The G Center, also known as the Identity Center, is the seat of the self — where direction, love, and identity reside. It is the magnetic monopole that holds the entire bodygraph together and guides us through life. The G Center governs who we are, where we're going, and who we love. When defined, you have a consistent sense of self, direction, and identity. You know who you are and where you belong. When undefined, you are here to experience many different versions of self — you are adaptable, fluid, and can sense the direction and identity of others. The G Center connects to the Throat, Sacral, Spleen, and Heart/Ego centers.",
        "function": "Identity center — direction, love, and sense of self",
        "gates": [1, 2, 7, 10, 13, 15, 25, 46],
        "channels": ["1-8 (Inspiration)", "2-14 (The Beat)", "7-31 (The Alpha)", "10-20 (Awakening)", "10-34 (Exploration)", "10-57 (Perfected Form)", "13-33 (The Prodigal)", "5-15 (Rhythm)", "25-51 (Initiation)", "29-46 (Discovery)"],
        "connected_to": ["Throat", "Sacral", "Spleen", "Heart/Ego"],
    },
    "Heart/Ego": {
        "description": "The Heart Center, also called the Ego Center, is the motor center that governs willpower, self-worth, and the capacity to make and keep commitments. It is the center of the material world — money, resources, and the ego's drive to prove itself. The Heart Center is about value: what we value, how we value ourselves, and what we're willing to commit to. When defined, you have consistent willpower and the capacity to make promises and deliver on them. When undefined, you are here to learn that your value does not come from proving yourself — you are worthy simply by being. This center connects to the Throat, G, Sacral, and Spleen centers.",
        "function": "Motor center — willpower, self-worth, and commitment",
        "gates": [21, 26, 40, 51],
        "channels": ["21-45 (Money)", "26-44 (Surrender)", "37-40 (Community)", "25-51 (Initiation)"],
        "connected_to": ["Throat", "G", "Sacral", "Spleen"],
    },
    "Sacral": {
        "description": "The Sacral Center is the most powerful motor center in the bodygraph — the source of life force energy, creativity, sexuality, and the capacity to work and build. It is the center of response: it does not initiate but responds to life with a clear 'yes' or 'no.' The Sacral is the engine that powers Generators and Manifesting Generators, who make up approximately 70% of the population. When defined, you have consistent access to sacral energy and can work sustainably when responding to what lights you up. When undefined, you amplify sacral energy and need to be careful not to overwork or burn out. The Sacral connects to the G, Throat, Spleen, Root, and Solar Plexus centers.",
        "function": "Motor center — life force, creativity, sexuality, and sustainable work energy",
        "gates": [3, 5, 9, 14, 27, 29, 34, 42, 59],
        "channels": ["3-60 (Mutation)", "5-15 (Rhythm)", "9-52 (Concentration)", "2-14 (The Beat)", "27-50 (Preservation)", "29-46 (Discovery)", "10-34 (Exploration)", "20-34 (Charisma)", "34-57 (Power)", "42-53 (Maturation)", "59-6 (Mating)"],
        "connected_to": ["G", "Throat", "Spleen", "Root", "Solar Plexus"],
    },
    "Spleen": {
        "description": "The Spleen Center is the body's primary awareness center for survival — housing intuition, instinct, immune function, and the sense of wellbeing in the present moment. It operates only in the now and does not store information or anticipate the future. The Spleen gives us instantaneous signals: this is safe, this is not; trust this, flee from that. It is the oldest center in evolutionary terms and governs our most fundamental survival mechanisms. When defined, you have a consistent and reliable intuitive sense that keeps you safe and healthy. When undefined, your immune system and sense of wellbeing are variable — you absorb and amplify the fears and health patterns of others. The Spleen connects to the Sacral, Root, Solar Plexus, G, Throat, and Heart/Ego centers.",
        "function": "Awareness center — intuition, instinct, immune system, and survival intelligence",
        "gates": [18, 28, 32, 44, 48, 50, 57],
        "channels": ["18-58 (Judgment)", "28-38 (Struggle)", "32-54 (Transformation)", "26-44 (Surrender)", "16-48 (Talent)", "27-50 (Preservation)", "10-57 (Perfected Form)", "20-57 (Brainwave)", "34-57 (Power)"],
        "connected_to": ["Sacral", "Root", "Solar Plexus", "G", "Throat", "Heart/Ego"],
    },
    "Solar Plexus": {
        "description": "The Solar Plexus Center is the emotional center — governing feelings, moods, desire, and the entire emotional wave. It is both a motor and an awareness center, making it uniquely powerful in the bodygraph. The Solar Plexus operates on an emotional wave cycle, meaning there is no truth in the now emotionally — clarity comes only over time through the movement of the wave. When defined, you have a rich emotional life that moves through natural cycles of high and low, and you make the best decisions when you wait for emotional clarity. When undefined, you are deeply empathic and can easily absorb the emotions of others — learning to distinguish what is yours from what is not is essential. The Solar Plexus connects to the Sacral, Spleen, Root, Throat, and Heart/Ego centers.",
        "function": "Motor and awareness center — emotions, feelings, desire, and the emotional wave",
        "gates": [6, 22, 30, 36, 37, 39, 49, 55],
        "channels": ["6-59 (Mating)", "12-22 (Openness)", "30-41 (Recognition)", "35-36 (Transitoriness)", "37-40 (Community)", "39-55 (Emoting)", "19-49 (Synthesis)"],
        "connected_to": ["Sacral", "Spleen", "Root", "Throat", "Heart/Ego"],
    },
    "Root": {
        "description": "The Root Center is the pressure center at the base of the bodygraph — the source of adrenaline, stress, and the pressure to move, act, and evolve. It is a motor center that fuels our drive to get things done, meet deadlines, and push through challenges. The Root Center generates the pressure that keeps life moving forward. When defined, you have a consistent way of processing and channeling pressure — you can handle stress and deadlines reliably. When undefined, you absorb the stress and pressure of others, which can feel overwhelming. Learning to not rush or act from external pressure is key for undefined Root centers. The Root connects to the Sacral, Spleen, and Solar Plexus centers.",
        "function": "Pressure and motor center — adrenaline, stress, and the drive to move forward",
        "gates": [19, 38, 41, 52, 53, 54, 58, 60],
        "channels": ["19-49 (Synthesis)", "28-38 (Struggle)", "30-41 (Recognition)", "9-52 (Concentration)", "42-53 (Maturation)", "32-54 (Transformation)", "18-58 (Judgment)", "3-60 (Mutation)", "39-55 (Emoting)"],
        "connected_to": ["Sacral", "Spleen", "Solar Plexus"],
    },
}

CENTER_ORDER = ["Head", "Ajna", "Throat", "G", "Heart/Ego", "Sacral", "Spleen", "Solar Plexus", "Root"]

# Centers can be defined or undefined
DEFINITION_TYPES = {
    "Head": ("defined", "undefined"),
    "Ajna": ("defined", "undefined"),
    "Throat": ("defined", "undefined"),
    "G": ("defined", "undefined"),
    "Heart/Ego": ("defined", "undefined"),
    "Sacral": ("defined", "undefined"),
    "Spleen": ("defined", "undefined"),
    "Solar Plexus": ("defined", "undefined"),
    "Root": ("defined", "undefined"),
}

CSS = """  :root {
    --navy-deep: #060d1a;
    --navy: #0a1628;
    --navy-mid: #0f1d36;
    --navy-light: #162744;
    --navy-lighter: #1e3458;
    --gold: #c9a84c;
    --gold-light: #e0c468;
    --gold-bright: #d4af37;
    --gold-soft: rgba(201, 168, 76, 0.15);
    --gold-glow: rgba(201, 168, 76, 0.08);
    --text-primary: #e8e6e3;
    --text-secondary: #8899aa;
    --text-muted: #5a6a7a;
    --white: #ffffff;
    --card-bg: rgba(15, 29, 54, 0.7);
    --card-border: rgba(201, 168, 76, 0.12);
    --radius: 12px;
    --radius-lg: 20px;
    --shadow: 0 4px 24px rgba(0,0,0,0.3);
    --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html { scroll-behavior: smooth; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--navy-deep);
    color: var(--text-primary);
    line-height: 1.7;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse at 20% 10%, rgba(201,168,76,0.04) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 90%, rgba(201,168,76,0.03) 0%, transparent 60%),
      radial-gradient(ellipse at 50% 50%, rgba(15,29,54,0.8) 0%, var(--navy-deep) 100%);
    pointer-events: none;
    z-index: 0;
  }

  nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(6, 13, 26, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(201,168,76,0.1);
    padding: 0 20px;
  }
  .nav-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: relative;
    z-index: 1;
  }
  .nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--white);
    text-decoration: none;
    letter-spacing: -0.02em;
  }
  .nav-logo .icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--gold-bright), var(--gold));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    color: var(--navy-deep);
    font-weight: 900;
  }
  .nav-links { display: flex; gap: 24px; align-items: center; }
  .nav-links a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.88rem;
    font-weight: 500;
    transition: var(--transition);
  }
  .nav-links a:hover { color: var(--gold-light); }

  .container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 24px;
    position: relative;
    z-index: 1;
  }

  .breadcrumb {
    padding: 18px 0;
    font-size: 0.82rem;
    color: var(--text-muted);
  }
  .breadcrumb a {
    color: var(--gold);
    text-decoration: none;
    transition: var(--transition);
  }
  .breadcrumb a:hover { color: var(--gold-light); }
  .breadcrumb span { margin: 0 6px; }

  .hero {
    text-align: center;
    padding: 48px 24px 40px;
  }
  .hero-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 88px;
    height: 88px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(201,168,76,0.2), rgba(201,168,76,0.08));
    border: 2px solid rgba(201,168,76,0.35);
    font-size: 2rem;
    color: var(--gold-light);
    margin-bottom: 20px;
  }
  .hero h1 {
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 12px;
    background: linear-gradient(180deg, #ffffff 0%, #c0c8d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero .subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    max-width: 560px;
    margin: 0 auto;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 48px;
  }
  .info-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 20px 18px;
    text-align: center;
  }
  .info-card .label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--gold);
    font-weight: 600;
    margin-bottom: 6px;
  }
  .info-card .value {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .content {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 40px 36px;
    margin-bottom: 48px;
  }
  .content h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 20px;
    color: var(--white);
    letter-spacing: -0.02em;
  }
  .content h3 {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--gold-light);
    margin: 32px 0 14px;
    letter-spacing: -0.01em;
  }
  .content p {
    font-size: 1rem;
    color: var(--text-secondary);
    line-height: 1.75;
    margin-bottom: 16px;
  }
  .content .highlight {
    color: var(--gold-light);
    font-weight: 500;
  }
  .content ul {
    list-style: none;
    padding: 0;
    margin: 12px 0;
  }
  .content ul li {
    padding: 8px 0;
    font-size: 0.92rem;
    color: var(--text-secondary);
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .content ul li:before {
    content: "▸ ";
    color: var(--gold);
  }
  .content ul li a {
    color: var(--gold-light);
    text-decoration: none;
  }
  .content ul li a:hover { text-decoration: underline; }

  .nav-footer {
    display: flex;
    justify-content: space-between;
    padding: 20px 0 60px;
  }
  .nav-footer a {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--gold);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.92rem;
    transition: var(--transition);
    padding: 10px 18px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
  }
  .nav-footer a:hover {
    color: var(--gold-light);
    border-color: rgba(201,168,76,0.3);
  }

  footer {
    text-align: center;
    padding: 40px 24px 60px;
    color: var(--text-muted);
    font-size: 0.82rem;
    border-top: 1px solid rgba(255,255,255,0.04);
  }
  footer a { color: var(--gold); text-decoration: none; }
  footer a:hover { color: var(--gold-light); }
"""


def safe_filename(name):
    return name.lower().replace(" ", "-").replace("/", "-")


def center_page_html(center_name, data, prev_center=None, next_center=None):
    """Generate HTML for a single center page."""
    slug = safe_filename(center_name)
    title = f"Human Design {center_name} Center — Complete Guide | Human Design Engine"
    desc = data["description"][:155] + "..."

    # Gate links
    gates_html = " ".join(
        f'<a href="/human-design/gates/gate-{g}/">{g}</a>'
        for g in data["gates"]
    )

    # Channel links
    channels_html = ""
    for ch in data["channels"]:
        ch_slug = ch.split(" (")[0].replace("-", "-").replace(" ", "-").lower()
        ch_name = ch.split(" (")[1].rstrip(")") if " (" in ch else ch
        channels_html += f'          <li><a href="/human-design/channels/{ch_slug}/">{ch}</a></li>\n'

    # Connected centers
    connected_html = " ".join(
        f'<a href="/human-design/centers/{safe_filename(c)}/">{c}</a>'
        for c in data["connected_to"]
    )

    prev_link = ""
    next_link = ""
    if prev_center:
        prev_link = f'<a href="/human-design/centers/{safe_filename(prev_center)}/">← {prev_center} Center</a>'
    else:
        prev_link = '<span></span>'
    if next_center:
        next_link = f'<a href="/human-design/centers/{safe_filename(next_center)}/">{next_center} Center →</a>'
    else:
        next_link = '<span></span>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="Human Design, {center_name} Center, {center_name}, Human Design centers, bodygraph, defined {center_name.lower()}, undefined {center_name.lower()}, Human Design Engine">
<link rel="canonical" href="https://humandesignengine.com/human-design/centers/{slug}/">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://humandesignengine.com/human-design/centers/{slug}/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Human Design {center_name} Center: Complete Guide",
  "description": "{desc}",
  "author": {{ "@type": "Organization", "name": "Human Design Engine" }},
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }}
}}
</script>
<style>
{CSS}
</style>
</head>
<body>

<nav>
  <div class="nav-inner">
    <a class="nav-logo" href="/">
      <span class="icon">HD</span>
      Human Design Engine
    </a>
    <div class="nav-links">
      <a href="/human-design/gates/">Gates</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/centers/">Centers</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    <a href="/human-design/centers/">Centers</a> <span>›</span>
    {center_name}
  </div>

  <div class="hero">
    <div class="hero-icon">{data["gates"][0]}</div>
    <h1>Human Design {center_name} Center</h1>
    <p class="subtitle">{data["function"]}. Explore the {center_name} Center's gates, channels, and how it shapes your design.</p>
  </div>

  <div class="info-grid">
    <div class="info-card">
      <div class="label">Type</div>
      <div class="value">{data.get('type_hint', 'Awareness / Motor / Pressure')}</div>
    </div>
    <div class="info-card">
      <div class="label">Gates</div>
      <div class="value">{gates_html}</div>
    </div>
    <div class="info-card">
      <div class="label">Connected To</div>
      <div class="value">{connected_html}</div>
    </div>
  </div>

  <article class="content">
    <h2>Understanding the {center_name} Center</h2>
    <p>{data["description"]}</p>

    <h3>Function in the Bodygraph</h3>
    <p>{data["function"]}. The {center_name} Center contains {len(data["gates"])} gates: {", ".join(f"Gate {g}" for g in data["gates"])}. These gates connect to other centers through {len(data["channels"])} channels, forming the energetic architecture of your unique design.</p>

    <h3>Defined vs. Undefined {center_name} Center</h3>
    <p><span class="highlight">Defined {center_name} Center:</span> When this center is colored in your bodygraph, you have consistent, reliable access to its energy. For the {center_name} Center, this means you operate with a fixed and dependable way of processing this aspect of your design. You are here to express this energy consistently and authentically.</p>
    <p><span class="highlight">Undefined {center_name} Center:</span> When this center is white in your bodygraph, you do not have consistent access to its energy. Instead, you amplify and experience this energy through others. Your wisdom lies in becoming deeply aware of how this energy moves through you from external sources, and learning not to identify with it as your own. This makes you incredibly wise about the {center_name} Center's themes.</p>

    <h3>Gates of the {center_name} Center</h3>
    <ul>
{chr(10).join(f"      <li><a href=\"/human-design/gates/gate-{g}/\">Gate {g}</a></li>" for g in data["gates"])}
    </ul>

    <h3>Channels Through the {center_name} Center</h3>
    <ul>
{channels_html.rstrip()}
    </ul>
  </article>

  <div class="nav-footer">
    {prev_link}
    <a href="index.html">All 9 Centers</a>
    {next_link}
  </div>

</div>

<footer>
  <p>&copy; 2026 <a href="https://humandesignengine.com">Human Design Engine</a>. Explore your unique design. All 9 centers, 64 gates, and 36 channels.</p>
</footer>

</body>
</html>'''


def index_page_html():
    """Generate the centers index page."""
    cards = ""
    for center_name in CENTER_ORDER:
        data = CENTERS[center_name]
        slug = safe_filename(center_name)
        gate_list = ", ".join(f"Gate {g}" for g in data["gates"])
        cards += f'''
    <a href="/human-design/centers/{slug}/" class="center-card">
      <div class="center-number">{data["gates"][0]}</div>
      <h3>{center_name} Center</h3>
      <p class="center-function">{data["function"][:80]}...</p>
      <div class="center-meta">
        <span>{len(data["gates"])} gates</span>
        <span>{len(data["channels"])} channels</span>
      </div>
      <div class="center-gates">{gate_list}</div>
    </a>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 9 Centers of Human Design — Complete Guide | Human Design Engine</title>
<meta name="description" content="Explore all 9 Human Design centers. Each center explained with function, gates, channels, and the difference between defined and undefined. Comprehensive center reference from Human Design Engine.">
<meta name="keywords" content="Human Design centers, 9 centers, Head Center, Ajna, Throat, G Center, Heart, Sacral, Spleen, Solar Plexus, Root, bodygraph, defined, undefined, Human Design Engine">
<link rel="canonical" href="https://humandesignengine.com/human-design/centers/">
<meta property="og:title" content="The 9 Centers of Human Design — Complete Guide | Human Design Engine">
<meta property="og:description" content="Explore every Human Design center with detailed explanations. Learn about defined vs. undefined, gates, channels, and functions for all 9 centers.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://humandesignengine.com/human-design/centers/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="The 9 Centers of Human Design — Complete Guide">
<meta name="twitter:description" content="Complete reference for all 9 Human Design centers with functions, gates, and channels.">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "The 9 Centers of Human Design",
  "description": "A complete guide to all 9 centers in the Human Design bodygraph, including functions, gates, channels, and the difference between defined and undefined states.",
  "url": "https://humandesignengine.com/human-design/centers/",
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }}
}}
</script>
<style>
{CSS}

  .page-header {{
    text-align: center;
    padding: 60px 24px 48px;
  }}
  .page-header h1 {{
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 16px;
    background: linear-gradient(180deg, #ffffff 0%, #c0c8d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .page-header p {{
    font-size: 1.1rem;
    color: var(--text-secondary);
    max-width: 640px;
    margin: 0 auto;
  }}

  .center-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 60px;
  }}

  .center-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 28px 24px;
    text-decoration: none;
    transition: var(--transition);
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .center-card:hover {{
    border-color: rgba(201,168,76,0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(201,168,76,0.08);
  }}
  .center-number {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(201,168,76,0.2), rgba(201,168,76,0.06));
    border: 1.5px solid rgba(201,168,76,0.3);
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--gold-light);
  }}
  .center-card h3 {{
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--white);
    letter-spacing: -0.01em;
  }}
  .center-function {{
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.5;
  }}
  .center-meta {{
    display: flex;
    gap: 16px;
    font-size: 0.78rem;
    color: var(--gold);
    font-weight: 500;
  }}
  .center-gates {{
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.5;
  }}
</style>
</head>
<body>

<nav>
  <div class="nav-inner">
    <a class="nav-logo" href="/">
      <span class="icon">HD</span>
      Human Design Engine
    </a>
    <div class="nav-links">
      <a href="/human-design/gates/">Gates</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/centers/">Centers</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    Centers
  </div>

  <div class="page-header">
    <h1>The 9 Centers of Human Design</h1>
    <p>Every Human Design bodygraph contains 9 geometric centers. Some are defined (colored in), others are undefined (white). Defined centers represent consistent, reliable energy — your inherent gifts and fixed way of operating. Undefined centers are where you take in, amplify, and gain wisdom from the world around you.</p>
  </div>

  <div class="center-grid">
{cards}
  </div>

</div>

<footer>
  <p>&copy; 2026 <a href="https://humandesignengine.com">Human Design Engine</a>. Explore your unique design. All 9 centers, 64 gates, and 36 channels.</p>
</footer>

</body>
</html>'''


def main():
    # Generate index
    index_path = os.path.join(OUT_DIR, "index.html")
    with open(index_path, "w") as f:
        f.write(index_page_html())
    print(f"✓ {index_path}")

    # Generate center pages
    for i, center_name in enumerate(CENTER_ORDER):
        data = CENTERS[center_name]
        # Add type hint
        if center_name in ("Head", "Root"):
            data["type_hint"] = "Pressure Center"
        elif center_name in ("Sacral", "Heart/Ego", "Solar Plexus", "Root"):
            # Root is both, but we already classified it
            if center_name == "Root":
                data["type_hint"] = "Pressure & Motor Center"
            elif center_name == "Solar Plexus":
                data["type_hint"] = "Awareness & Motor Center"
            elif center_name in ("Sacral",):
                data["type_hint"] = "Motor Center"
            else:
                data["type_hint"] = "Motor Center"
        else:
            data["type_hint"] = "Awareness Center"

        prev_center = CENTER_ORDER[i - 1] if i > 0 else None
        next_center = CENTER_ORDER[i + 1] if i < len(CENTER_ORDER) - 1 else None

        slug = safe_filename(center_name)
        page_path = os.path.join(OUT_DIR, f"{slug}.html")
        with open(page_path, "w") as f:
            f.write(center_page_html(center_name, data, prev_center, next_center))
        print(f"✓ {page_path}")

    print(f"\n✅ Generated {len(CENTER_ORDER)} center pages + index")


if __name__ == "__main__":
    main()
