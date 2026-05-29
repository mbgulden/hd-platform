#!/usr/bin/env python3
"""
Generate 36 SEO-optimized channel pages + index for Human Design Engine.
Navy/gold theme matching existing landing pages.
Output: /home/ubuntu/work/hd-platform/docs/human-design/channels/
"""

import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Complete Human Design Channel Data ──────────────────────────────────────
CHANNELS = [
    # (gates, name, circuit, circuit_group, center_from, center_to, slug, meta_desc, plain_english)
    ("1-8", "Inspiration", "Individual", "Knowing",
     "G Center", "Throat Center",
     "1-8-inspiration",
     "Channel 1-8 Inspiration in Human Design connects the G Center to the Throat. Learn how this Individual Knowing channel fuels creative self-expression and authentic leadership.",
     "The Channel of Inspiration (1-8) connects your G Center (identity/direction) to your Throat (communication). It gives you a natural gift for creative self-expression that inspires others. When you speak from your authentic self, people listen. This channel is about being a role model — not by trying to lead, but by simply being who you are. Your creativity flows when you trust your unique direction."),

    ("2-14", "The Beat", "Individual", "Knowing",
     "G Center", "Sacral Center",
     "2-14-the-beat",
     "Channel 2-14 The Beat in Human Design links the G Center to the Sacral. Discover how this Individual Knowing channel drives you on a unique life path with sustainable energy.",
     "The Channel of The Beat (2-14) connects your G Center (direction) to your Sacral (life force energy). It gives you a unique inner compass — a pulse that guides you along your own path. You're not meant to follow the crowd; you're here to walk a distinctive route. This channel brings sustainable energy when you're moving in the right direction, and a clear sense of 'this is mine to do.' It's the beat of your own drum."),

    ("3-60", "Mutation", "Individual", "Knowing",
     "Root Center", "Sacral Center",
     "3-60-mutation",
     "Channel 3-60 Mutation in Human Design connects the Root to the Sacral. Explore how this Individual Knowing channel creates sudden change, innovation, and new beginnings from pressure.",
     "The Channel of Mutation (3-60) connects your Root Center (pressure/stress) to your Sacral (life force). This is the channel of sudden change — like a pulse that flips a switch and everything shifts. You experience bursts of creative energy that can radically alter your direction. The pressure builds until something new emerges. You're here to innovate, to disrupt patterns that no longer serve, and to bring fresh energy into stagnant situations."),

    ("4-63", "Logic", "Collective", "Understanding",
     "Crown Center", "Ajna Center",
     "4-63-logic",
     "Channel 4-63 Logic in Human Design connects the Crown to the Ajna. Learn how this Collective Understanding channel brings mental clarity through questioning, doubt, and logical analysis.",
     "The Channel of Logic (4-63) connects your Crown Center (inspiration) to your Ajna (mental processing). This is a powerful mental channel driven by questions and doubt. You're designed to scrutinize ideas, to ask 'Is this actually true?' Your skepticism isn't negativity — it's a gift that tests ideas so only what's solid survives. You bring clarity by challenging assumptions, and your logical mind helps the collective separate wishful thinking from reality."),

    ("5-15", "Rhythm", "Collective", "Understanding",
     "Sacral Center", "G Center",
     "5-15-rhythm",
     "Channel 5-15 Rhythm in Human Design links the Sacral to the G Center. Discover how this Collective Understanding channel creates natural timing and flow with life's rhythms.",
     "The Channel of Rhythm (5-15) connects your Sacral Center (life force energy) to your G Center (identity). This channel gives you an innate sense of timing — you naturally flow with the rhythms of life. You know when to act and when to wait, when to push forward and when to pause. Others may find you magnetic because you seem to be in the right place at the right time. Your gift is being in sync with the natural flow of existence."),

    ("6-59", "Intimacy", "Tribal", "Ego",
     "Sacral Center", "Solar Plexus Center",
     "6-59-intimacy",
     "Channel 6-59 Intimacy in Human Design connects the Sacral to the Solar Plexus. Explore how this Tribal Ego channel creates deep bonds, fertility, and emotional connection.",
     "The Channel of Intimacy (6-59) connects your Sacral Center (life force/sexuality) to your Solar Plexus (emotions). This is the channel of deep bonding and creative intimacy. You have a powerful ability to connect with others on an emotional and physical level. This isn't just about romance — it's about the capacity to create genuine closeness, to break down walls, and to generate new life whether literal (children) or metaphorical (projects, relationships, art)."),

    ("7-31", "The Alpha", "Collective", "Understanding",
     "G Center", "Throat Center",
     "7-31-the-alpha",
     "Channel 7-31 The Alpha in Human Design links the G Center to the Throat. Learn how this Collective Understanding channel enables democratic leadership and guiding the group.",
     "The Channel of The Alpha (7-31) connects your G Center (identity/direction) to your Throat (communication). This is the channel of collective leadership — but not the dictatorial kind. You're designed to lead only when recognized and invited by the group. Your role is to articulate the direction the collective already senses it needs to go. You speak for the future of the group, and your leadership works best when it's democratic and inclusive."),

    ("9-52", "Concentration", "Collective", "Understanding",
     "Sacral Center", "Root Center",
     "9-52-concentration",
     "Channel 9-52 Concentration in Human Design connects the Sacral to the Root. Discover how this Collective Understanding channel brings focused energy, stillness, and deep attention to detail.",
     "The Channel of Concentration (9-52) connects your Sacral Center (life force) to your Root Center (pressure). This channel gives you an extraordinary ability to focus. When you're locked in on something, you can sit still and apply sustained energy for long periods. It's the channel of the craftsman, the researcher, the meditator. Your gift is the capacity to concentrate deeply and see patterns others miss because they're too distracted to look."),

    ("10-20", "Awakening", "Individual", "Centering",
     "G Center", "Throat Center",
     "10-20-awakening",
     "Channel 10-20 Awakening in Human Design links the G Center to the Throat. Explore how this Individual Centering channel enables living fully in the present moment with self-love.",
     "The Channel of Awakening (10-20) connects your G Center (identity/self-love) to your Throat (expression). This is the channel of presence — of being fully awake and alive in the now. You have the ability to embody self-love and express it authentically. When you're aligned, you radiate a presence that reminds others what it looks like to truly accept yourself. You're not here to follow scripts; you're here to live moment-to-moment with awareness."),

    ("10-34", "Exploration", "Individual", "Centering",
     "G Center", "Sacral Center",
     "10-34-exploration",
     "Channel 10-34 Exploration in Human Design connects the G Center to the Sacral. Learn how this Individual Centering channel drives you to follow your own path with raw power.",
     "The Channel of Exploration (10-34) connects your G Center (identity) to your Sacral (life force). This channel gives you the power to follow your own convictions regardless of what others think. You have an independent spirit and a strong drive to explore life on your own terms. The energy is raw and self-directed — you're here to discover who you are through direct experience, not by following maps others have drawn."),

    ("10-57", "Perfected Form", "Individual", "Centering",
     "G Center", "Spleen Center",
     "10-57-perfected-form",
     "Channel 10-57 Perfected Form in Human Design links the G Center to the Spleen. Discover how this Individual Centering channel creates intuitive survival wisdom and embodied grace.",
     "The Channel of Perfected Form (10-57) connects your G Center (identity) to your Spleen (intuition/survival). This channel gives you an intuitive sense of what's right for your body and being. You have a natural grace, an instinct for survival that manifests as elegance in the present moment. You know in your bones what serves your well-being and what doesn't. It's the channel of the intuitive artist, the survivor who moves through life with fluid awareness."),

    ("11-56", "Curiosity", "Collective", "Sensing",
     "Ajna Center", "Throat Center",
     "11-56-curiosity",
     "Channel 11-56 Curiosity in Human Design connects the Ajna to the Throat. Explore how this Collective Sensing channel fuels storytelling, ideas, and the search for meaning.",
     "The Channel of Curiosity (11-56) connects your Ajna Center (mental awareness) to your Throat (communication). This is the channel of the storyteller, the seeker, the one who needs to know why. You have an insatiable curiosity and a gift for weaving ideas into narratives that captivate others. You're here to gather experiences, find meaning in them, and share those meanings with the collective. Your stories help people make sense of the world."),

    ("12-22", "Openness", "Individual", "Centering",
     "Throat Center", "Solar Plexus Center",
     "12-22-openness",
     "Channel 12-22 Openness in Human Design links the Throat to the Solar Plexus. Learn how this Individual Centering channel enables vulnerable, emotionally honest communication.",
     "The Channel of Openness (12-22) connects your Throat Center (expression) to your Solar Plexus (emotions). This channel gives you the ability to speak from your emotional depths. You can articulate feelings in a way that touches others and creates intimacy. Your gift is vulnerability — when you share what you truly feel, you give others permission to do the same. You're here to communicate emotion with authenticity and grace."),

    ("13-33", "The Prodigal", "Collective", "Sensing",
     "G Center", "Throat Center",
     "13-33-the-prodigal",
     "Channel 13-33 The Prodigal in Human Design connects the G Center to the Throat. Discover how this Collective Sensing channel enables witnessing, reflection, and sharing wisdom from experience.",
     "The Channel of The Prodigal (13-33) connects your G Center (identity) to your Throat (expression). This is the channel of the witness — you're here to listen, to observe, and to reflect back what you've learned. You collect stories and experiences and distill them into wisdom the collective can use. You may feel like you wander through life gathering pieces, but your gift is in the sharing of what you've witnessed. You help others learn from the journey."),

    ("16-48", "Talent", "Collective", "Sensing",
     "Throat Center", "Spleen Center",
     "16-48-talent",
     "Channel 16-48 Talent in Human Design links the Throat to the Spleen. Explore how this Collective Sensing channel brings mastery through repetition, practice, and deep intuitive skill.",
     "The Channel of Talent (16-48) connects your Throat Center (expression) to your Spleen (intuition). This channel is about skill and mastery that comes through repetition. You have a natural talent that deepens with practice — you may not even realize how good you are because the skill feels intuitive. Your gift is the capacity to refine your craft until it becomes second nature, and to express that mastery in the world."),

    ("17-62", "Acceptance", "Collective", "Understanding",
     "Ajna Center", "Throat Center",
     "17-62-acceptance",
     "Channel 17-62 Acceptance in Human Design connects the Ajna to the Throat. Learn how this Collective Understanding channel brings organized thinking and clear communication of complex ideas.",
     "The Channel of Acceptance (17-62) connects your Ajna Center (mental processing) to your Throat (communication). This channel gives you the ability to organize thoughts, opinions, and data into coherent frameworks. You can take complex information and structure it so others can understand. Your gift is the capacity to accept what is — to see things clearly without distortion — and to communicate that clarity with precision and care."),

    ("18-58", "Correction", "Collective", "Understanding",
     "Root Center", "Spleen Center",
     "18-58-correction",
     "Channel 18-58 Correction in Human Design links the Root to the Spleen. Discover how this Collective Understanding channel drives improvement, pattern recognition, and fixing what's broken.",
     "The Channel of Correction (18-58) connects your Root Center (pressure) to your Spleen (intuition/survival). This channel gives you an instinct for spotting what needs to be fixed. You can see the flaw in the pattern, the thing that isn't working, and you feel pressure to correct it. Your gift isn't criticism — it's service. You're here to improve systems, heal patterns, and make things better for everyone. The key is to correct with love, not judgment."),

    ("19-49", "Synthesis", "Tribal", "Ego",
     "Root Center", "Solar Plexus Center",
     "19-49-synthesis",
     "Channel 19-49 Synthesis in Human Design connects the Root to the Solar Plexus. Explore how this Tribal Ego channel creates emotional sensitivity, tribal belonging, and principled living.",
     "The Channel of Synthesis (19-49) connects your Root Center (pressure) to your Solar Plexus (emotions). This channel makes you deeply sensitive to the emotional dynamics of your tribe. You feel who belongs and who doesn't, what's fair and what's not. You have strong principles about relationships and community. Your gift is the ability to synthesize diverse people into a cohesive group by honoring emotional truth and creating a sense of belonging."),

    ("20-34", "Charisma", "Individual", "Centering",
     "Throat Center", "Sacral Center",
     "20-34-charisma",
     "Channel 20-34 Charisma in Human Design links the Throat to the Sacral. Learn how this Individual Centering channel enables powerful, magnetic self-expression through action.",
     "The Channel of Charisma (20-34) connects your Throat Center (expression) to your Sacral (life force). This channel gives you magnetic presence — when you're doing what you love, people notice. Your charisma isn't manufactured; it radiates naturally when you're aligned with your sacral response. You have the power to manifest through action, to turn your energy into tangible expression in the now. You're here to act on what feels right."),

    ("20-57", "Brainwave", "Individual", "Centering",
     "Throat Center", "Spleen Center",
     "20-57-brainwave",
     "Channel 20-57 Brainwave in Human Design connects the Throat to the Spleen. Discover how this Individual Centering channel enables intuitive knowing and spontaneous, truthful speech.",
     "The Channel of Brainwave (20-57) connects your Throat Center (expression) to your Spleen (intuition). This is the channel of intuitive speech — you know things in the moment and can articulate them instantly. Your intuition speaks through you before your mind has time to analyze. You have a gift for saying the right thing at the right time, for cutting through confusion with a single clear statement. Trust your spontaneous knowing."),

    ("21-45", "Money", "Tribal", "Ego",
     "Heart Center", "Throat Center",
     "21-45-money",
     "Channel 21-45 Money in Human Design links the Heart to the Throat. Explore how this Tribal Ego channel drives resource management, material success, and tribal prosperity.",
     "The Channel of Money (21-45) connects your Heart Center (willpower/ego) to your Throat (communication). This channel is about material resources and tribal prosperity. You have a natural ability to manage resources, to understand value, and to communicate about money and material matters. Your gift isn't greed — it's stewardship. You're here to ensure the tribe has what it needs to thrive, and you can lead others toward sustainable abundance."),

    ("23-43", "Structuring", "Individual", "Knowing",
     "Ajna Center", "Throat Center",
     "23-43-structuring",
     "Channel 23-43 Structuring in Human Design connects the Ajna to the Throat. Learn how this Individual Knowing channel brings breakthrough insights, genius ideas, and unique mental frameworks.",
     "The Channel of Structuring (23-43) connects your Ajna Center (mental awareness) to your Throat (communication). This is the channel of unique insight — you see things differently than others, and you can articulate your vision in novel ways. Sometimes called the 'genius to freak' channel, your ideas may seem strange until people catch up. You're here to express your unique knowing, to structure information in ways that break paradigms and open new possibilities."),

    ("24-61", "Awareness", "Individual", "Knowing",
     "Ajna Center", "Crown Center",
     "24-61-awareness",
     "Channel 24-61 Awareness in Human Design links the Ajna to the Crown. Discover how this Individual Knowing channel brings sudden inspiration, deep insight, and the drive to know universal truth.",
     "The Channel of Awareness (24-61) connects your Ajna Center (mental processing) to your Crown (inspiration). This channel gives you access to sudden bursts of insight — epiphanies that seem to come from nowhere. You're driven to understand the mysteries of existence, to know what's true at the deepest level. Your mind is a receiver for universal truths, and your gift is bringing these insights into conscious awareness so they can transform how we see reality."),

    ("25-51", "Initiation", "Individual", "Centering",
     "G Center", "Heart Center",
     "25-51-initiation",
     "Channel 25-51 Initiation in Human Design connects the G Center to the Heart. Explore how this Individual Centering channel drives spiritual awakening, competition, and courageous self-discovery.",
     "The Channel of Initiation (25-51) connects your G Center (identity/spirit) to your Heart Center (willpower). This channel is about spiritual courage — the willingness to leap into the unknown and trust that you'll land. You have a competitive spirit, but the real competition is with yourself. You're here to initiate yourself into higher levels of being through acts of courage, to transform through challenges, and to emerge renewed."),

    ("26-44", "Surrender", "Tribal", "Ego",
     "Heart Center", "Spleen Center",
     "26-44-surrender",
     "Channel 26-44 Surrender in Human Design links the Heart to the Spleen. Learn how this Tribal Ego channel enables intuitive sales, transmission of values, and knowing when to let go.",
     "The Channel of Surrender (26-44) connects your Heart Center (willpower/ego) to your Spleen (intuition). This channel gives you an intuitive gift for transmission — you can sense what people need and know how to deliver it. Often called the 'salesperson's channel,' it's really about knowing when to push and when to surrender. Your ego works best when it yields to intuition. You're here to transmit value in a way that serves the tribe."),

    ("27-50", "Preservation", "Tribal", "Ego",
     "Sacral Center", "Spleen Center",
     "27-50-preservation",
     "Channel 27-50 Preservation in Human Design connects the Sacral to the Spleen. Discover how this Tribal Ego channel drives nurturing, caregiving, and protecting tribal values.",
     "The Channel of Preservation (27-50) connects your Sacral Center (life force) to your Spleen (intuition/survival). This is the channel of nurturing and protection. You have a deep instinct to care for others, to preserve what's valuable in the tribe, and to ensure the well-being of those you love. Your gift is the ability to sustain and nourish — you're the one who makes sure the tribe's values, health, and resources are protected for future generations."),

    ("28-38", "Struggle", "Individual", "Knowing",
     "Spleen Center", "Root Center",
     "28-38-struggle",
     "Channel 28-38 Struggle in Human Design links the Spleen to the Root. Explore how this Individual Knowing channel drives the search for purpose and meaning through life's challenges.",
     "The Channel of Struggle (28-38) connects your Spleen Center (intuition/survival) to your Root (pressure). This channel gives you a drive to find meaning through challenge. You're not afraid of struggle — in fact, you need it to feel alive. You push against limits to discover what you're made of, and through this process, you find purpose. Your gift is the courage to face difficulty head-on and to emerge with wisdom that only comes through direct experience of adversity."),

    ("29-46", "Discovery", "Collective", "Sensing",
     "Sacral Center", "G Center",
     "29-46-discovery",
     "Channel 29-46 Discovery in Human Design connects the Sacral to the G Center. Learn how this Collective Sensing channel drives the joyful exploration of life and finding success in the right place.",
     "The Channel of Discovery (29-46) connects your Sacral Center (life force) to your G Center (identity). This channel gives you an adventurous spirit — a drive to say 'yes' to life and discover where that leads. You're here to explore the physical world, to travel, to experience, and to discover success by being in the right place at the right time. Your gift is the willingness to commit to experience without knowing the outcome, and to find meaning in the journey itself."),

    ("30-41", "Recognition", "Collective", "Sensing",
     "Solar Plexus Center", "Root Center",
     "30-41-recognition",
     "Channel 30-41 Recognition in Human Design links the Solar Plexus to the Root. Discover how this Collective Sensing channel drives emotional desire, dreaming, and the fuel for new experiences.",
     "The Channel of Recognition (30-41) connects your Solar Plexus Center (emotions) to your Root (pressure). This channel is about the fuel of desire — the emotional pressure to experience something new. You have powerful feelings that drive you toward new adventures. Your gift is the ability to feel deeply about what's possible, to dream, and to use that emotional energy as fuel for creation. You recognize what you want through feeling, and that recognition propels you forward."),

    ("32-54", "Transformation", "Tribal", "Ego",
     "Root Center", "Spleen Center",
     "32-54-transformation",
     "Channel 32-54 Transformation in Human Design connects the Root to the Spleen. Explore how this Tribal Ego channel drives ambition, material growth, and the instinct to rise in status.",
     "The Channel of Transformation (32-54) connects your Root Center (pressure) to your Spleen (intuition). This channel gives you ambition and the instinct to rise. You sense when it's time to transform your circumstances, to climb higher, to achieve more. Your gift is the ability to transform yourself and your tribe's material reality through persistent effort and intuitive timing. You're here to evolve and to bring others along on the journey upward."),

    ("34-57", "Power", "Individual", "Centering",
     "Sacral Center", "Spleen Center",
     "34-57-power",
     "Channel 34-57 Power in Human Design links the Sacral to the Spleen. Learn how this Individual Centering channel brings raw life force, intuitive action, and embodied power in the now.",
     "The Channel of Power (34-57) connects your Sacral Center (life force) to your Spleen (intuition). This channel gives you raw, archetypal power — the ability to act intuitively in the moment with full life force behind you. When your intuition says 'move,' you move with complete power. Your gift is the embodiment of pure, present-moment energy. You're here to trust your instincts completely and to act with the full force of your being."),

    ("35-36", "Transitoriness", "Collective", "Sensing",
     "Throat Center", "Solar Plexus Center",
     "35-36-transitoriness",
     "Channel 35-36 Transitoriness in Human Design connects the Throat to the Solar Plexus. Discover how this Collective Sensing channel creates the hunger for new experiences and emotional learning through change.",
     "The Channel of Transitoriness (35-36) connects your Throat Center (expression) to your Solar Plexus (emotions). This channel gives you an insatiable hunger for new experiences. You're not meant to stay in one place emotionally or physically — you're here to taste everything life has to offer. Your gift is the ability to feel the full spectrum of human emotion through continuous exploration. You teach others that change is not just inevitable but valuable."),

    ("37-40", "Community", "Tribal", "Ego",
     "Solar Plexus Center", "Heart Center",
     "37-40-community",
     "Channel 37-40 Community in Human Design links the Solar Plexus to the Heart. Explore how this Tribal Ego channel creates emotional bonds, community agreements, and mutual support.",
     "The Channel of Community (37-40) connects your Solar Plexus Center (emotions) to your Heart Center (willpower). This channel makes you the heart of your community. You have a deep need for emotional connection and mutual support. You understand the power of agreements, promises, and shared commitment. Your gift is the ability to create tribe — to build networks of mutual care where everyone contributes and everyone belongs. You're here to prove that together is better."),

    ("39-55", "Emoting", "Individual", "Knowing",
     "Root Center", "Solar Plexus Center",
     "39-55-emoting",
     "Channel 39-55 Emoting in Human Design connects the Root to the Solar Plexus. Learn how this Individual Knowing channel creates profound emotional depth, melancholy, and the fuel for artistic expression.",
     "The Channel of Emoting (39-55) connects your Root Center (pressure) to your Solar Plexus (emotions). This channel gives you extraordinary emotional depth. You feel everything intensely — the highs are transcendent and the lows can feel crushing. Your gift is the ability to channel this emotional spectrum into creativity, art, and expression that moves others deeply. You're here to prove that feeling deeply is a strength, and that melancholy can be the richest fuel for beauty."),

    ("42-53", "Maturation", "Collective", "Sensing",
     "Sacral Center", "Root Center",
     "42-53-maturation",
     "Channel 42-53 Maturation in Human Design links the Sacral to the Root. Discover how this Collective Sensing channel drives growth through cycles, completion, and the wisdom that comes with time.",
     "The Channel of Maturation (42-53) connects your Sacral Center (life force) to your Root (pressure). This channel drives cycles of growth — you start things, build momentum, bring them to completion, and then begin again. You understand that everything has a season and that wisdom comes through lived experience over time. Your gift is the patience to let things mature naturally and the drive to see things through to their proper end."),

    ("47-64", "Abstraction", "Collective", "Understanding",
     "Ajna Center", "Crown Center",
     "47-64-abstraction",
     "Channel 47-64 Abstraction in Human Design connects the Ajna to the Crown. Explore how this Collective Understanding channel brings pattern recognition, meaning-making, and mental clarity from confusion.",
     "The Channel of Abstraction (47-64) connects your Ajna Center (mental processing) to your Crown (inspiration). This channel gives you a mind that works by sifting through confusion to find meaning. You absorb a flood of impressions, memories, and inspiration, and over time, patterns emerge. Your gift is the ability to make sense of chaos — to abstract meaning from the mess of experience. You're here to help the collective understand itself by revealing the patterns hidden in the noise."),
]

# Verify we have exactly 36
assert len(CHANNELS) == 36, f"Expected 36 channels, got {len(CHANNELS)}"

# ── CSS (shared across all pages) ───────────────────────────────────────────
CSS = """<style>
  :root {
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
    position: sticky; top: 0; z-index: 100;
    background: rgba(6,13,26,0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(201,168,76,0.1); padding: 0 20px;
  }
  .nav-inner {
    max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between;
    height: 64px; position: relative; z-index: 1;
  }
  .nav-logo {
    display: flex; align-items: center; gap: 10px; text-decoration: none; color: var(--gold);
    font-weight: 700; font-size: 1.2rem; letter-spacing: -0.01em;
  }
  .nav-logo span { color: var(--text-primary); font-weight: 400; }
  .nav-links { display: flex; gap: 24px; list-style: none; }
  .nav-links a {
    color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; transition: var(--transition);
  }
  .nav-links a:hover { color: var(--gold); }
  .container {
    max-width: 900px; margin: 0 auto; padding: 40px 24px 80px; position: relative; z-index: 1;
  }
  .breadcrumb { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 32px; }
  .breadcrumb a { color: var(--text-secondary); text-decoration: none; }
  .breadcrumb a:hover { color: var(--gold); }
  .channel-hero {
    background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius-lg);
    padding: 48px 40px; margin-bottom: 40px; text-align: center; position: relative; overflow: hidden;
  }
  .channel-hero::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, var(--navy-lighter), var(--gold), var(--navy-lighter));
  }
  .channel-number {
    font-size: 3rem; font-weight: 800; color: var(--gold); letter-spacing: -0.02em; line-height: 1.1;
  }
  .channel-name { font-size: 2rem; font-weight: 700; color: var(--white); margin-top: 8px; }
  .channel-circuit {
    display: inline-block; margin-top: 16px; padding: 6px 18px;
    background: var(--gold-soft); color: var(--gold-light); border-radius: 20px;
    font-size: 0.9rem; font-weight: 600;
  }
  .info-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; }
  @media (max-width: 640px) { .info-cards { grid-template-columns: 1fr; } }
  .info-card {
    background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius);
    padding: 24px;
  }
  .info-card h3 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 8px; }
  .info-card p { font-size: 1.05rem; color: var(--text-primary); }
  .content-section { margin-bottom: 40px; }
  .content-section h2 {
    font-size: 1.6rem; color: var(--gold); margin-bottom: 16px; font-weight: 700;
  }
  .content-section p { font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 16px; }
  .content-section ul { list-style: none; margin: 16px 0; }
  .content-section ul li {
    padding: 10px 0 10px 24px; position: relative; color: var(--text-secondary); font-size: 1.05rem;
  }
  .content-section ul li::before {
    content: '◆'; position: absolute; left: 0; color: var(--gold); font-size: 0.6rem; top: 14px;
  }
  .cta-box {
    background: linear-gradient(135deg, var(--navy-light), var(--navy-mid));
    border: 1px solid var(--card-border); border-radius: var(--radius-lg);
    padding: 40px; text-align: center; margin-top: 48px;
  }
  .cta-box h2 { color: var(--gold); font-size: 1.5rem; margin-bottom: 12px; }
  .cta-box p { color: var(--text-secondary); margin-bottom: 24px; font-size: 1.05rem; }
  .btn {
    display: inline-block; padding: 14px 32px; border-radius: 8px; font-weight: 600;
    font-size: 1rem; text-decoration: none; transition: var(--transition); cursor: pointer;
  }
  .btn-gold { background: var(--gold); color: var(--navy-deep); }
  .btn-gold:hover { background: var(--gold-light); transform: translateY(-1px); box-shadow: 0 8px 24px rgba(201,168,76,0.25); }
  .btn-outline { border: 2px solid var(--gold); color: var(--gold); }
  .btn-outline:hover { background: var(--gold-soft); }
  footer {
    border-top: 1px solid rgba(201,168,76,0.08); padding: 40px 20px; text-align: center;
    color: var(--text-muted); font-size: 0.85rem; position: relative; z-index: 1;
  }
  footer a { color: var(--text-secondary); text-decoration: none; }
  footer a:hover { color: var(--gold); }
  .related-channels { margin-top: 40px; }
  .related-channels h3 { color: var(--gold); margin-bottom: 16px; }
  .related-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
  .related-chip {
    display: block; padding: 12px 16px; background: var(--card-bg); border: 1px solid var(--card-border);
    border-radius: var(--radius); text-decoration: none; color: var(--text-secondary); font-size: 0.9rem;
    transition: var(--transition);
  }
  .related-chip:hover { border-color: var(--gold); color: var(--gold); }
  .faq-item { margin-bottom: 20px; }
  .faq-item h4 { color: var(--text-primary); font-size: 1.1rem; margin-bottom: 6px; }
  .faq-item p { color: var(--text-secondary); }
</style>"""


def make_page(channel, all_channels, canonical_path):
    """Build a complete HTML page for one channel."""
    gates, name, circuit, circuit_group, from_center, to_center, slug, meta_desc, plain = channel
    title = f"Channel {gates} {name} — Human Design {circuit} {circuit_group} Channel | Human Design Engine"

    # Related channels (same circuit group)
    related = [c for c in all_channels if c[3] == circuit_group and c[6] != slug][:4]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://humandesignengine.com/human-design/channels/{canonical_path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://humandesignengine.com/human-design/channels/{canonical_path}">
<meta property="og:site_name" content="Human Design Engine">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{meta_desc}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Human Design Channel {gates} — {name}",
  "description": "{meta_desc}",
  "author": {{ "@type": "Organization", "name": "Human Design Engine" }},
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }}
}}
</script>
{CSS}
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/" class="nav-logo">✦ Human Design <span>Engine</span></a>
    <ul class="nav-links">
      <li><a href="/">Home</a></li>
      <li><a href="/human-design/channels/">All Channels</a></li>
    </ul>
  </div>
</nav>

<main class="container">
  <div class="breadcrumb">
    <a href="/">Home</a> &rsaquo; <a href="/human-design/channels/">Human Design Channels</a> &rsaquo; Channel {gates} {name}
  </div>

  <div class="channel-hero">
    <div class="channel-number">Channel {gates}</div>
    <div class="channel-name">{name}</div>
    <div class="channel-circuit">{circuit} &bull; {circuit_group} Circuit</div>
  </div>

  <div class="info-cards">
    <div class="info-card">
      <h3>Circuit Group</h3>
      <p>{circuit} &mdash; {circuit_group} Circuit</p>
    </div>
    <div class="info-card">
      <h3>Gate 1</h3>
      <p>Gate {gates.split('-')[0]} &mdash; located in the {from_center}</p>
    </div>
    <div class="info-card">
      <h3>Gate 2</h3>
      <p>Gate {gates.split('-')[1]} &mdash; located in the {to_center}</p>
    </div>
    <div class="info-card">
      <h3>Centers Connected</h3>
      <p>{from_center} &harr; {to_center}</p>
    </div>
  </div>

  <div class="content-section">
    <h2>What the Channel of {name} ({gates}) Means</h2>
    <p>{plain}</p>
  </div>

  <div class="content-section">
    <h2>Key Themes of Channel {gates}</h2>
    <ul>
      <li><strong>Circuit:</strong> {circuit} &mdash; {circuit_group} Circuit</li>
      <li><strong>Centers:</strong> Connects the {from_center} to the {to_center}</li>
      <li><strong>Energy Type:</strong> {'Generated (Sacral)' if 'Sacral' in (from_center + to_center) else 'Projected' if 'G Center' in (from_center + to_center) and 'Throat' in (from_center + to_center) else 'Manifested' if 'Throat' in (from_center + to_center) and 'Heart' not in (from_center + to_center) else 'Manifested/Projected'}</li>
      <li><strong>Core Gift:</strong> {name} — the energy of this channel expressed through your design</li>
      <li><strong>Not-Self Expression:</strong> When not aligned, this energy may manifest as frustration, inconsistency, or feeling stuck</li>
    </ul>
  </div>

  <div class="content-section">
    <h2>How to Live Your Channel of {name}</h2>
    <p>Living in alignment with Channel {gates} means honoring your unique design. Here are some practical tips:</p>
    <ul>
      <li><strong>Trust Your Authority:</strong> Let your inner authority — not your mind — guide decisions that involve this channel's energy.</li>
      <li><strong>Honor Your Rhythm:</strong> This channel has its own timing. Don't force it; let the energy move naturally.</li>
      <li><strong>Embrace Your Gift:</strong> Whether others understand it or not, this channel is part of your unique contribution to the world.</li>
      <li><strong>Notice the Signs:</strong> Pay attention to signals of alignment (satisfaction, peace, success, or surprise) versus misalignment (frustration, anger, bitterness, or disappointment).</li>
    </ul>
  </div>

  <div class="content-section">
    <h2>Frequently Asked Questions About Channel {gates}</h2>
    <div class="faq-item">
      <h4>What does Channel {gates} mean in Human Design?</h4>
      <p>Channel {gates} — The Channel of {name} — is a {circuit} {circuit_group} channel that connects the {from_center} to the {to_center}. It represents a consistent, defined energy in your chart that shapes how you express yourself, interact with others, and navigate life. This channel is part of the {circuit} circuit, which means it serves {circuit.lower()} purposes.</p>
    </div>
    <div class="faq-item">
      <h4>What happens when Channel {gates} is defined in my chart?</h4>
      <p>When Channel {gates} is defined, the {from_center} and {to_center} are both colored in (defined). This means you have consistent, reliable access to the energy of {name}. It operates as a theme in your life — something you can count on when you're living correctly according to your Strategy and Authority.</p>
    </div>
    <div class="faq-item">
      <h4>What if Channel {gates} is undefined or open in my chart?</h4>
      <p>If either gate, or the entire channel, is undefined, you don't have consistent access to this energy — and that's perfectly fine. Instead, you experience this channel's themes when you're around people who have it defined, and you can develop wisdom about it. The undefined experience can actually bring deeper insight into the channel's nature.</p>
    </div>
  </div>
"""

    if related:
        html += """  <div class="related-channels">
    <h3>Related Channels in the """ + circuit_group + """ Circuit</h3>
    <div class="related-grid">
"""
        for rc in related:
            rgates, rname, _, _, _, _, rslug, _, _ = rc
            html += f"""      <a href="/human-design/channels/{rslug}" class="related-chip">Channel {rgates} &mdash; {rname}</a>
"""
        html += """    </div>
  </div>
"""

    html += f"""
  <div class="cta-box">
    <h2>Want to See Channel {gates} in Your Chart?</h2>
    <p>Run your full Human Design chart on Human Design Engine to see exactly how Channel {gates} — and all 36 channels — show up in your unique design.</p>
    <a href="/" class="btn btn-gold">Get Your Free Chart</a>
  </div>

</main>

<footer>
  <p>&copy; 2026 <a href="/">Human Design Engine</a> &mdash; The Engine Behind Every Chart. All rights reserved.</p>
  <p style="margin-top:8px;"><a href="/human-design/channels/">Browse all 36 Human Design Channels</a></p>
</footer>
</body>
</html>"""
    return html


def make_index(all_channels):
    """Build the index page listing all 36 channels."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All 36 Human Design Channels — Complete Guide | Human Design Engine</title>
<meta name="description" content="Complete guide to all 36 Human Design channels. Browse every channel by circuit group — Individual, Collective, and Tribal. Learn what each channel means, which centers it connects, and its key themes.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://humandesignengine.com/human-design/channels/">
<meta property="og:title" content="All 36 Human Design Channels — Complete Guide | Human Design Engine">
<meta property="og:description" content="Complete guide to all 36 Human Design channels. Browse every channel by circuit group — Individual, Collective, and Tribal.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://humandesignengine.com/human-design/channels/">
<meta property="og:site_name" content="Human Design Engine">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="All 36 Human Design Channels — Complete Guide">
<meta name="twitter:description" content="Complete guide to all 36 Human Design channels. Browse by circuit group.">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "headline": "All 36 Human Design Channels — Complete Guide",
  "description": "Complete guide to all 36 Human Design channels. Browse every channel by circuit group — Individual, Collective, and Tribal.",
  "publisher": { "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" },
  "mainEntity": { "@type": "ItemList", "numberOfItems": 36 }
}
</script>
""" + CSS + """
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/" class="nav-logo">✦ Human Design <span>Engine</span></a>
    <ul class="nav-links">
      <li><a href="/">Home</a></li>
      <li><a href="/human-design/channels/">All Channels</a></li>
    </ul>
  </div>
</nav>

<main class="container">
  <div class="breadcrumb">
    <a href="/">Home</a> &rsaquo; Human Design Channels
  </div>

  <div class="channel-hero">
    <div class="channel-number">The 36 Channels</div>
    <div class="channel-name">Complete Human Design Channel Guide</div>
    <div class="channel-circuit">Individual &bull; Collective &bull; Tribal</div>
  </div>

  <div class="content-section">
    <h2>What Are Human Design Channels?</h2>
    <p>In Human Design, a <strong>channel</strong> is formed when two gates — one at each end — are both defined in your chart. When both gates are activated, the entire channel becomes defined, and the two centers it connects become colored in (defined). There are exactly 36 channels in the Human Design system, and each one represents a specific archetypal energy, theme, or gift.</p>
    <p>Channels are grouped into three <strong>circuit groups</strong> — Individual, Collective, and Tribal — and further subdivided into <strong>circuits</strong> (Knowing, Centering, Understanding, Sensing, and Ego). Each circuit serves a different purpose in the human experience: Individual circuits empower and mutate, Collective circuits share and structure, and Tribal circuits bond and sustain.</p>
  </div>

  <div class="content-section">
    <h2>Channels by Circuit Group</h2>
"""

    # Group channels by circuit
    circuits = {}
    for c in all_channels:
        key = (c[2], c[3])
        circuits.setdefault(key, []).append(c)

    for (circuit, group), ch_list in circuits.items():
        html += f"""
    <h3 style="color:var(--gold);margin-top:32px;">{circuit} &mdash; {group} Circuit ({len(ch_list)} channels)</h3>
    <p style="color:var(--text-secondary);">"""
        if circuit == "Individual":
            if group == "Knowing":
                html += "The Individual Knowing Circuit channels empower personal mutation, creative insight, and unique self-expression. These channels drive you to know and express your truth."
            elif group == "Centering":
                html += "The Individual Centering Circuit channels center you in your own authority, intuition, and present-moment awareness. These channels empower self-directed living."
        elif circuit == "Collective":
            if group == "Understanding":
                html += "The Collective Understanding Circuit channels bring logical clarity, pattern recognition, and structured thinking to the collective. These channels help us make sense of the world together."
            elif group == "Sensing":
                html += "The Collective Sensing Circuit channels connect us through shared human experience, storytelling, and emotional wisdom. These channels help us learn from living."
        elif circuit == "Tribal":
            html += "The Tribal Ego Circuit channels create bonds, sustain communities, manage resources, and build the structures of mutual support. These channels are about belonging and shared prosperity."
        html += "</p>\n"
        html += """    <div class="related-grid" style="margin-top:16px;">\n"""
        for c in ch_list:
            gates, name, _, _, _, _, slug, _, _ = c
            html += f"""      <a href="/human-design/channels/{slug}" class="related-chip">Channel {gates} &mdash; {name}</a>\n"""
        html += """    </div>\n"""

    html += """  </div>

  <div class="content-section">
    <h2>How to Use This Guide</h2>
    <p>Click any channel above to learn more about it — including its circuit group, which centers it connects, what it means in plain English, and how to live in alignment with its energy. If you're not sure which channels are defined in your chart, <a href="/" style="color:var(--gold);">run your free Human Design chart</a> on Human Design Engine to find out.</p>
  </div>

  <div class="cta-box">
    <h2>Discover Your Defined Channels</h2>
    <p>Run your free Human Design chart to see exactly which of these 36 channels are defined in your unique design — and what they mean for your life.</p>
    <a href="/" class="btn btn-gold">Get Your Free Chart</a>
  </div>

</main>

<footer>
  <p>&copy; 2026 <a href="/">Human Design Engine</a> &mdash; The Engine Behind Every Chart. All rights reserved.</p>
</footer>
</body>
</html>"""
    return html


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    # Generate index
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_path, "w") as f:
        f.write(make_index(CHANNELS))
    print(f"✓ Index: {index_path}")

    # Generate channel pages
    for ch in CHANNELS:
        slug = ch[6]
        canonical = slug
        page_html = make_page(ch, CHANNELS, canonical)
        filepath = os.path.join(OUTPUT_DIR, f"{slug}.html")
        with open(filepath, "w") as f:
            f.write(page_html)
        print(f"✓ Channel {ch[0]} {ch[1]}: {filepath}")

    print(f"\n✅ Done! Generated index + {len(CHANNELS)} channel pages in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
