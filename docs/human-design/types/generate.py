#!/usr/bin/env python3
"""Generate Human Design Type SEO pages. Run from types/ directory."""
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

TYPES = {
    "manifestor": {
        "title": "The Manifestor",
        "strategy": "To Inform",
        "signature": "Peace",
        "not_self": "Anger",
        "aura": "Closed and Repelling",
        "pct": "~8%",
        "desc": "Manifestors are the initiators. With a motor connected to the Throat, you're designed to act independently and impact others. Your closed aura means people feel your presence before you speak. Inform before you act to remove resistance and create peace.",
        "practical": "Before you take any action today, tell at least one person who'll be affected. Notice how informing changes the energy.",
    },
    "generator": {
        "title": "The Generator",
        "strategy": "To Respond",
        "signature": "Satisfaction",
        "not_self": "Frustration",
        "aura": "Open and Enveloping",
        "pct": "~37%",
        "desc": "Generators are the life force of the planet. With a defined Sacral center, you have sustainable energy and a powerful gut response. Your strategy is to wait for life to come to you, then respond with your sacral sound — the uh-huh (yes) or uh-uh (no). Trust your gut before your mind.",
        "practical": "For one day, only say yes to things that give you a literal gut response. Notice how much energy you have when you're responding to what lights you up vs forcing things.",
    },
    "manifesting_generator": {
        "title": "The Manifesting Generator",
        "strategy": "To Respond, then Inform",
        "signature": "Satisfaction",
        "not_self": "Frustration",
        "aura": "Open and Enveloping",
        "pct": "~33%",
        "desc": "Manifesting Generators combine the Generator's sacral energy with the Manifestor's speed. You're designed to be multi-passionate, fast, and efficient. Your strategy is two-step: first Respond to what excites you, then Inform those who need to know before you leap. Don't let anyone tell you to slow down or pick just one thing.",
        "practical": "Identify one thing you've been forcing. Stop. Wait for something to respond to instead. When you feel the sacral yes, inform your key people, then go.",
    },
    "projector": {
        "title": "The Projector",
        "strategy": "Wait for the Invitation",
        "signature": "Success",
        "not_self": "Bitterness",
        "aura": "Focused and Absorbing",
        "pct": "~21%",
        "desc": "Projectors are the guides. Without a defined Sacral, you're not here to work like a Generator — you're here to see, guide, and manage energy. Your focused aura allows you to read people with remarkable depth. Recognition must come before your guidance is received. Rest is not laziness — it's your design.",
        "practical": "Today, notice where you're offering advice without being asked. Practice waiting. When someone genuinely invites your perspective, notice how it feels different.",
    },
    "reflector": {
        "title": "The Reflector",
        "strategy": "Wait a Lunar Cycle",
        "signature": "Surprise",
        "not_self": "Disappointment",
        "aura": "Sampling and Reflecting",
        "pct": "~1%",
        "desc": "Reflectors are the rarest type — the mirrors of humanity. With no defined centers, you sample and reflect the energy of everyone around you. Your strategy is to wait a full lunar cycle (28 days) before making major decisions. Your wellbeing is the community's barometer. Protect your environment fiercely.",
        "practical": "For your next decision (even a medium one), give yourself a week. Notice how clarity arrives through the lunar cycle rather than through mental pressure.",
    },
}

# ── Index page ──
links = "\n".join(
    f'          <li><a href="{slug}.html">{data["title"]} ({data["pct"]} of population)</a> — {data["strategy"]}</li>'
    for slug, data in TYPES.items()
)

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 5 Human Design Types — Complete Guide | Human Design Engine</title>
<meta name="description" content="Explore all 5 Human Design types: Manifestor, Generator, Manifesting Generator, Projector, and Reflector. Learn strategies, signatures, and auras for each type.">
<link rel="canonical" href="https://humandesignengine.com/human-design/types/">
<meta property="og:title" content="The 5 Human Design Types — Complete Guide">
<meta property="og:description" content="Complete reference for all 5 Human Design types with strategies, auras, and practical experiments. From Human Design Engine.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://humandesignengine.com/human-design/types/">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "The 5 Human Design Types",
  "description": "A complete guide to all 5 Human Design types: Manifestor, Generator, Manifesting Generator, Projector, and Reflector.",
  "url": "https://humandesignengine.com/human-design/types/",
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }}
}}
</script>
<style>
  :root {{
    --navy-deep: #060d1a; --navy: #0a1628; --navy-mid: #0f1d36;
    --gold: #c9a84c; --gold-light: #e0c468; --text-primary: #e8e6e3;
    --text-secondary: #8899aa; --card-bg: rgba(15,29,54,0.7);
    --radius: 12px;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--navy-deep); color: var(--text-primary); line-height:1.7; }}
  .container {{ max-width:800px; margin:0 auto; padding:60px 24px; }}
  h1 {{ font-size:2.5rem; color:var(--gold); margin-bottom:.5em; }}
  .lead {{ color:var(--text-secondary); font-size:1.15rem; margin-bottom:2em; }}
  ul {{ list-style:none; padding:0; }}
  li {{ background:var(--card-bg); border-radius:var(--radius); padding:20px 24px; margin-bottom:12px; border:1px solid rgba(201,168,76,0.12); }}
  li a {{ color:var(--gold-light); text-decoration:none; font-size:1.1rem; font-weight:600; }}
  li a:hover {{ text-decoration:underline; }}
  .nav {{ margin-bottom:40px; }}
  .nav a {{ color:var(--text-secondary); margin-right:16px; text-decoration:none; }}
  .nav a:hover {{ color:var(--gold); }}
  .cta {{ margin-top:40px; padding:24px; background:var(--card-bg); border-radius:var(--radius); text-align:center; border:2px solid rgba(201,168,76,0.2); }}
  .cta a {{ color:var(--gold-light); font-weight:600; }}
</style>
</head>
<body>
<div class="container">
  <nav class="nav">
    <a href="/">← Home</a>
    <a href="/human-design/centers/">Centers</a>
    <a href="/human-design/gates/">Gates</a>
    <a href="/human-design/channels/">Channels</a>
  </nav>
  <h1>The 5 Human Design Types</h1>
  <p class="lead">Your Type is the foundation of your Human Design — it determines your strategy for making decisions, your aura mechanics, and the signature of living in alignment. Discover each type below.</p>
  <ul>
{links}
  </ul>
  <div class="cta">
    <p>Not sure what type you are?</p>
    <a href="/buy-report.html">Get your full personalized report →</a>
  </div>
</div>
</body>
</html>"""

with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
    f.write(index_html)
print(f"Wrote index.html ({len(index_html)} bytes)")

# ── Individual type pages ──
for slug, data in TYPES.items():
    filename = f"{slug}.html"
    filepath = os.path.join(OUT_DIR, filename)
    if os.path.exists(filepath):
        print(f"  {filename} already exists, skipping")
        continue
    
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data['title']} Human Design Type — Strategy: {data['strategy']} | Human Design Engine</title>
<meta name="description" content="{data['title']}: {data['desc'][:160]}">
<link rel="canonical" href="https://humandesignengine.com/human-design/types/{slug}/">
<meta property="og:title" content="{data['title']} Human Design Type">
<meta property="og:description" content="{data['desc'][:200]}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{data['title']} Human Design Type",
  "description": "{data['desc'][:200]}",
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine" }}
}}
</script>
<style>
  :root {{ --navy-deep:#060d1a;--navy:#0a1628;--navy-mid:#0f1d36;--gold:#c9a84c;--gold-light:#e0c468;--text-primary:#e8e6e3;--text-secondary:#8899aa;--card-bg:rgba(15,29,54,0.7);--radius:12px; }}
  * {{ margin:0;padding:0;box-sizing:border-box; }}
  body {{ font-family:system-ui,-apple-system,sans-serif;background:var(--navy-deep);color:var(--text-primary);line-height:1.8; }}
  .hero {{ text-align:center;padding:80px 24px 60px;background:linear-gradient(180deg,var(--navy-mid),var(--navy-deep)); }}
  .hero h1 {{ font-size:3rem;color:var(--gold);margin-bottom:16px; }}
  .hero .subtitle {{ color:var(--text-secondary);font-size:1.2rem;max-width:600px;margin:0 auto; }}
  .stat-bar {{ display:flex;justify-content:center;gap:32px;flex-wrap:wrap;margin-top:32px; }}
  .stat {{ text-align:center; }}
  .stat .label {{ font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-secondary); }}
  .stat .value {{ font-size:1.3rem;font-weight:700;color:var(--gold-light); }}
  .container {{ max-width:720px;margin:0 auto;padding:40px 24px; }}
  h2 {{ color:var(--gold);font-size:1.6rem;margin:40px 0 16px; }}
  .card {{ background:var(--card-bg);border-radius:var(--radius);padding:24px;margin-bottom:20px;border:1px solid rgba(201,168,76,0.1); }}
  .card h3 {{ color:var(--gold-light);margin-bottom:12px; }}
  .nav {{ padding:20px 24px; }}
  .nav a {{ color:var(--text-secondary);margin-right:16px;text-decoration:none; }}
  .nav a:hover {{ color:var(--gold); }}
  .cta {{ margin:40px 0;padding:32px;background:var(--card-bg);border-radius:var(--radius);text-align:center;border:2px solid rgba(201,168,76,0.2); }}
  .cta a {{ display:inline-block;margin-top:12px;padding:12px 32px;background:var(--gold);color:var(--navy-deep);border-radius:8px;text-decoration:none;font-weight:700; }}
  .cta a:hover {{ background:var(--gold-light); }}
</style>
</head>
<body>
<nav class="nav">
  <a href="/">← Home</a>
  <a href="/human-design/types/">All Types</a>
  <a href="/human-design/centers/">Centers</a>
  <a href="/human-design/gates/">Gates</a>
</nav>
<section class="hero">
  <h1>{data['title']}</h1>
  <p class="subtitle">{data['desc']}</p>
  <div class="stat-bar">
    <div class="stat">
      <div class="label">Strategy</div>
      <div class="value">{data['strategy']}</div>
    </div>
    <div class="stat">
      <div class="label">Signature</div>
      <div class="value">{data['signature']}</div>
    </div>
    <div class="stat">
      <div class="label">Not-Self Theme</div>
      <div class="value">{data['not_self']}</div>
    </div>
    <div class="stat">
      <div class="label">Aura</div>
      <div class="value">{data['aura']}</div>
    </div>
    <div class="stat">
      <div class="label">Population</div>
      <div class="value">{data['pct']}</div>
    </div>
  </div>
</section>
<div class="container">
  <h2>Understanding the {data['title']} Aura</h2>
  <div class="card">
    <p>Every Human Design type has a distinct aura mechanic — the energetic field that others feel around you. The {data['title']} aura is <strong>{data['aura'].lower()}</strong>. This is not something you do; it's something you are. Understanding your aura is the first step to working with your design rather than against it.</p>
  </div>

  <h2>Your Strategy: {data['strategy']}</h2>
  <div class="card">
    <p>Your strategy is your built-in navigation system — the way you're designed to move through life with the least resistance. For {data['title']}s, that means: <strong>{data['strategy']}</strong>. When you follow your strategy, you experience <strong>{data['signature']}</strong>. When you don't, you feel <strong>{data['not_self']}</strong> — that's your dashboard warning light.</p>
    <p>This isn't philosophy. It's mechanics. Your strategy works whether you believe in it or not. The only question is whether you'll experiment with it.</p>
  </div>

  <h2>Practical Experiment</h2>
  <div class="card">
    <h3>Try this for 3 days:</h3>
    <p>{data['practical']}</p>
  </div>

  <h2>Famous {data['title']}s</h2>
  <div class="card">
    <p>Many influential figures throughout history have embodied the {data['title']} energy. While we can't verify historical charts with certainty, the archetypal patterns are recognizable. When you see a {data['title']} living their design, you witness <strong>{data['signature']}</strong> in action.</p>
  </div>

  <div class="cta">
    <h3>Want your complete chart?</h3>
    <p>Your Type is just the beginning. Discover your Profile, Authority, Centers, Channels, Gates, and Incarnation Cross.</p>
    <a href="/buy-report.html">Get Your Full Report →</a>
  </div>
</div>
</body>
</html>"""
    
    with open(filepath, "w") as f:
        f.write(page)
    print(f"Wrote {filename} ({len(page)} bytes)")

print("Done. Generated index + missing type pages.")
