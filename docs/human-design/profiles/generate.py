#!/usr/bin/env python3
"""
Generate 13 Human Design Profile SEO pages (12 profiles + index).
Uses the navy/gold design system with full SEO metadata.
Each profile page is ~400-600 lines of substantive content.
Run from profiles/ directory.
"""

import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)

# ── Line archetype descriptions ──
LINE_INFO = {
    1: {
        "name": "The Investigator",
        "conscious": "You need a solid foundation. You study, research, and dig deep before you feel ready. Your gift is depth of knowledge; your challenge is insecurity about not knowing enough. You are here to become an authority through patient investigation.",
        "unconscious": "You unconsciously radiate the energy of someone who has done the homework. Others instinctively seek you out for answers. Behind the scenes, the need for a foundation drives your every move — you feel most secure when you understand the bottom of things.",
        "life_role": "Building the foundation of knowledge that others will rely upon.",
    },
    2: {
        "name": "The Hermit",
        "conscious": "You have a natural gift — something you do effortlessly that others find remarkable. You may not even recognize it as talent because it comes so easily. The paradox: you need to be alone to develop your gift, but you need to be called out by others to share it. Don't initiate; wait to be recognized and asked.",
        "unconscious": "Your unconscious carries an innate talent that others see before you do. You project an aura of 'I've got something special' even when you're just being yourself. The call will come — trust that what's yours finds you.",
        "life_role": "Mastering your natural gift in solitude and sharing it when called upon.",
    },
    3: {
        "name": "The Martyr",
        "conscious": "You learn through direct experience — trial and error is your curriculum. You make and break bonds, try things that fail, and discover what works through lived experimentation. Your gift is resilience; your challenge is viewing 'failures' as mistakes rather than data. You are here to discover what works and share the findings.",
        "unconscious": "Your unconscious drives you into experiences before your conscious mind has time to analyze. You find yourself in situations that teach you precisely what you need. Pessimism is your teacher — when you anticipate what might go wrong, you're actually mapping the territory.",
        "life_role": "Discovering truths through direct experience and sharing what works.",
    },
    4: {
        "name": "The Opportunist",
        "conscious": "Your life moves through your network. Opportunities come through people you know — friends, colleagues, community. Your gift is warmth and approachability; your challenge is the vulnerability that comes with extending yourself. Build and nurture your network; it is your vehicle for impact.",
        "unconscious": "Your unconscious magnetism draws people toward you. You naturally create bonds and alliances without effort. Over time, a constellation of relationships forms around you — these are your channels for opportunity, influence, and love.",
        "life_role": "Transforming relationships into opportunities that benefit the collective.",
    },
    5: {
        "name": "The Heretic",
        "conscious": "You are a universalizer — you see the practical solution that works for everyone. Others project their expectations onto you, seeing you as either savior or scapegoat. Your gift is practical wisdom; your challenge is managing projection. Deliver your solution and step back — don't get entangled in others' expectations.",
        "unconscious": "Your unconscious carries a magnetic, almost messianic quality. People project onto you what they need to see — which can be overwhelming. You are here to deliver practical solutions and keep moving; staying too long invites distortion.",
        "life_role": "Delivering universal, practical solutions while navigating projection.",
    },
    6: {
        "name": "The Role Model",
        "conscious": "You live in three distinct phases: birth to ~30 (living as a 3rd line — trial and error), ~30 to ~50 (on the roof — observing, detaching, gaining perspective), and ~50 onward (Role Model — embodying wisdom). Your gift is earned wisdom; your challenge is the long arc of becoming. Trust the process.",
        "unconscious": "Your unconscious is on a trajectory that unfolds across decades. Even when you feel off-track, the deeper pattern is guiding you toward embodiment. In your later years, others naturally look to you as an example of living authentically.",
        "life_role": "Living the arc of trial, observation, and eventual embodied wisdom.",
    },
}

# ── All 12 profiles ──
PROFILES = {
    "1-3": {
        "title": "The Investigator / Martyr",
        "slug": "1-3",
        "conscious": 1,
        "unconscious": 3,
        "theme": "Knowledge Built on Experience",
        "pct": "~14% of the population (second most common profile)",
        "interaction": "You are here to study, dig deep, build your foundation, and then test everything through direct experience. You don't take anything on faith — you need to know the theory AND run the experiment.",
        "personality_desc": "The 1st line in your Personality (conscious) Sun means you approach life with the need for a solid foundation of knowledge. You research, read, investigate, and won't feel ready until you've done your homework. This makes you reliable and authoritative — when you speak, you know what you're talking about. The shadow? Insecurity. You may feel you never know enough, delaying your contribution while you gather more data.",
        "design_desc": "The 3rd line in your Design (unconscious) means your body learns through trial and error. You don't learn from theory alone — you must experience things firsthand, make mistakes, adapt, and discover what actually works. Your unconscious keeps throwing you into situations that test your knowledge. This can feel chaotic, but it's how you build real-world wisdom others can trust.",
        "faq": [
            ("Why do I feel like I never know enough?", "This is the 1st line's shadow — insecurity about the foundation not being deep enough. The truth: you will never feel fully ready, and that's by design. Your 3rd line is designed to learn by doing, not by waiting until you've read every book. Trust that your foundation is sufficient to begin experimenting — the experiments themselves will complete your education."),
            ("Am I supposed to fail so much?", "Yes — from the 3rd line's perspective, what looks like failure is data collection. Every bond you break, every project that doesn't work, every path that dead-ends is teaching you what actually holds up. The 1st line documents the findings; the 3rd line generates them. You're the researcher who also does the field work."),
            ("How does the 1/3 profile navigate relationships?", "You bring depth and reliability (line 1) combined with a willingness to experiment (line 3). In relationships, you may test bonds — not out of malice but to discover what's real. Your partners need to understand that your need to 'figure things out' includes the relationship itself. Communication about this dynamic is essential."),
        ],
        "experiments": [
            "Permission to start before you're ready — Pick one thing you've been researching and take the first experimental step today, even if you don't feel 100% prepared.",
            "Reframe your 'failures' — For one week, every time something doesn't work, write it down as 'Discovery #X: This approach doesn't work.' Feel the difference between failure and discovery.",
            "Share your research — As a 1st line, your foundation of knowledge is meant to be shared. Write a summary, teach a friend, or post your findings. Your 3rd line experiments give your research credibility.",
        ],
    },
    "1-4": {
        "title": "The Investigator / Opportunist",
        "slug": "1-4",
        "conscious": 1,
        "unconscious": 4,
        "theme": "Knowledge Shared Through Connection",
        "pct": "~2% of the population",
        "interaction": "You build a foundation of deep knowledge and then share it through your network of trusted relationships. Your authority grows not through broadcasting but through intimate, meaningful connections with people who value your expertise.",
        "personality_desc": "The 1st line in your Personality Sun means you approach life as a student. You need to understand the fundamentals — deeply. You're the one who reads the manual cover to cover, who researches before committing, who builds unshakeable foundations. Your authority comes from genuine mastery, not charisma. The challenge is the insecurity loop: feeling you can never know enough.",
        "design_desc": "The 4th line in your Design means your life unfolds through relationships. Opportunities don't come from strangers or cold outreach — they come from people in your network: friends, colleagues, community. Your unconscious magnetism draws people toward you. You naturally create bonds, and through these bonds, your carefully built knowledge finds its audience.",
        "faq": [
            ("How do I balance isolation (studying) with connection (networking)?", "The rhythm for a 1/4 is: study alone, share with your circle. You don't need to be networking constantly. Your 4th line means the right people find you naturally. Your job is to be ready with deep knowledge when they do. Treat your study time as sacred preparation for the connections that will come."),
            ("Why do I feel vulnerable in social situations?", "The 4th line, despite being the 'Opportunist,' is surprisingly vulnerable. Extending yourself into relationships requires trust. This is amplified by the 1st line's fear of not knowing enough — you worry you'll be exposed. Remember: your network doesn't need perfection; they need your genuine depth and reliability."),
            ("What's the best career path for a 1/4?", "Anything where deep expertise meets trusted relationships. Teaching, consulting, therapy, specialized crafts, or any role where your knowledge is valued within a community rather than in a mass-market context. You thrive in environments where reputation builds slowly through word-of-mouth."),
        ],
        "experiments": [
            "Map your network — List the 10 people you trust most. Next to each, note one piece of knowledge you could offer them. Then actually offer it.",
            "Study-then-share rhythm — For one project, alternate: one week of deep research (line 1), one week of sharing/discussing what you learned with your network (line 4). Notice when you feel most alive.",
            "Trust your readiness — The next time someone asks you a question, resist the urge to say 'I need to research that more.' Answer from what you already know. See what happens.",
        ],
    },
    "2-4": {
        "title": "The Hermit / Opportunist",
        "slug": "2-4",
        "conscious": 1,
        "unconscious": 3,
        "theme": "Natural Talent Shared Through Community",
        "pct": "~14% of the population (tied for second most common)",
        "interaction": "You carry an innate, effortless gift — something you do so naturally you may not even recognize it as special. Your life's work is to honor the call to solitude (where your gift develops) AND the call from your community (where your gift is recognized and shared). You are here to be discovered.",
        "personality_desc": "The 2nd line in your Personality Sun means you have a natural genius. It's not something you worked for — it was born in you. You may not even see it because it's so effortless for you. Others, however, will see it clearly and call it out. Your job is not to push your gift onto the world but to cultivate it in solitude and respond when genuinely called upon.",
        "design_desc": "The 4th line in your Design means your gift finds its audience through relationships. Your network is the vehicle through which your natural talent reaches the world. When people in your community recognize what you can do and invite you to share it — that's the signal to emerge from your hermitage. Not before.",
        "faq": [
            ("Why do I feel torn between wanting to be alone and wanting connection?", "This is the 2/4 tension: the Hermit needs solitude to cultivate the gift; the Opportunist needs people to share it. Neither is wrong. The rhythm for a 2/4 is: honor the hermit phase without guilt, then honor the connection phase when the call comes. You are designed to oscillate."),
            ("How do I know what my natural gift is?", "Ask the people who know you well. Your 2nd line gift is often invisible to you precisely because it's effortless. What do people consistently compliment you on? What do they come to you for? What can you do for hours without noticing time pass? The answer is likely your natural talent."),
            ("Should I promote myself or wait to be discovered?", "Wait. The 2nd line is fundamentally not here to initiate self-promotion. When you push your gift, it creates resistance. When you're genuinely called out by your community (4th line), your gift lands with power. Trust the call — it will come through the people who already know and value you."),
        ],
        "experiments": [
            "Ask 5 trusted people: 'What do I do naturally that you find remarkable?' — Listen without dismissing. You may discover your gift.",
            "For one week, don't initiate any offers of help. Wait. Notice who reaches out to you and for what. This is the call your design recognizes.",
            "Protect your hermit time — Block 2 hours daily of uninterrupted solitude. Use it to do what you love without an agenda. Let your natural talent breathe.",
        ],
    },
    "2-5": {
        "title": "The Hermit / Heretic",
        "slug": "2-5",
        "conscious": 2,
        "unconscious": 5,
        "theme": "Natural Gift Projected as Universal Solution",
        "pct": "~2% of the population",
        "interaction": "You have a natural, effortless gift (line 2) that others project universal significance onto (line 5). You are here to cultivate your talent in solitude, then deliver practical solutions when called — while skillfully managing the projection that comes with being seen as a savior.",
        "personality_desc": "The 2nd line in your Personality Sun gives you a natural talent so innate you may overlook it. You need solitude to develop this gift — not to hide, but to let it mature naturally. When you're called out by others, your gift shines. When you try to push it, it feels forced and produces resistance.",
        "design_desc": "The 5th line in your Design means you carry the projection field of the Heretic. Others see you as someone with answers — a practical problem-solver, even a savior. This can feel flattering or overwhelming. Your unconscious responds by offering solutions that work universally. The skill: deliver the solution and step back without getting entangled in others' expectations.",
        "faq": [
            ("Why do people keep projecting things onto me that aren't true?", "This is the 5th line's universal projection field. People see in you what they need to see — a savior, a genius, a threat. It's not personal; it's a mechanics of your aura. The 2/5 response: deliver your practical gift when called, but maintain clear boundaries. You are not here to fulfill everyone's projections."),
            ("How do I handle the 'savior' expectation?", "First, recognize it's a projection, not a truth. You are not anyone's savior. You have a practical gift and can offer solutions. Second, communicate clearly about what you can and cannot do. Third, step away after delivering — lingering invites deeper projection. The 2/5 gift is a clean delivery, not a lifetime commitment to every person you help."),
            ("Is my natural talent really special or do people just project that?", "Both. Your 2nd line gift is genuinely remarkable — others can see it even when you can't. AND the 5th line amplifies that recognition into projection. The truth lies in the practical impact your gift has. When you deliver, people's lives improve. That's real. The projection is just the packaging."),
        ],
        "experiments": [
            "Deliver and step back — Next time someone asks for your help, give them one clear, practical solution and then say: 'Try this and let me know how it goes.' Don't get drawn into managing their whole journey.",
            "Notice the projection — When someone treats you as unusually special or unusually threatening, pause and ask: 'What are they seeing in me that's really about them?' Journal about it.",
            "Honor the hermit cycle — After any significant interaction where you've been 'the solution,' take a day of solitude. Let your 2nd line reset.",
        ],
    },
    "3-5": {
        "title": "The Martyr / Heretic",
        "slug": "3-5",
        "conscious": 3,
        "unconscious": 5,
        "theme": "Practical Solutions Forged in Experience",
        "pct": "~14% of the population (tied for second most common)",
        "interaction": "You learn everything through direct, often challenging experience — then offer the hard-won practical wisdom to others. Your authority is earned through trial and error, making your solutions deeply credible. You are here to discover what actually works and then universalize it.",
        "personality_desc": "The 3rd line in your Personality Sun means you learn by doing, breaking, and rebuilding. Your path is paved with experiments — some succeed, many don't. The key insight: these aren't failures; they are discoveries. You are mapping the territory of what works through direct experience. Pessimism is your hidden ally — by anticipating what could go wrong, you navigate more skillfully than optimists.",
        "design_desc": "The 5th line in your Design means others project onto you the expectation of practical solutions. They see you as someone who can fix things, who knows the way. This projection can feel heavy — especially when you're in the middle of your own trial-and-error process. But your hard-won experience makes you genuinely qualified to help. The 5th line universalizes what the 3rd line discovers.",
        "faq": [
            ("Why does my life feel like a constant series of trials?", "Because it is — by design. The 3rd line learns through experience, full stop. You don't read the manual; you take the thing apart and put it back together. If it breaks, you learned something the manual couldn't teach. Resilience is your superpower. Every 'mistake' is data for the practical wisdom you'll later universalize."),
            ("How do I cope with people expecting me to have all the answers?", "The 5th line projection is real and can be exhausting. Key survival strategy: be honest about your process. Say: 'Here's what I've learned from my own experience, and here's what I'm still figuring out.' Authenticity disarms projection more effectively than pretending to have it all together."),
            ("Isn't the 3/5 profile exhausting?", "It can be. But it's also incredibly potent. No other profile combines the experimental rigor of the 3rd line with the universal reach of the 5th. Your solutions, when they come, are battle-tested. The world needs people who've actually been through it — and that's you."),
        ],
        "experiments": [
            "The discovery log — For 30 days, write down every 'mistake' as a discovery. At the end of the month, review your log. You'll see a pattern of real-world data that no book could give you.",
            "Boundary practice — When someone projects a savior expectation onto you, say: 'I can share what's worked for me, but your path is yours.' Notice the relief.",
            "Share your process, not just your solutions — People project onto finished products. Let them see the messy middle. It reduces projection and makes your wisdom more accessible.",
        ],
    },
    "3-6": {
        "title": "The Martyr / Role Model",
        "slug": "3-6",
        "conscious": 3,
        "unconscious": 6,
        "theme": "Wisdom Earned Across a Lifetime of Experience",
        "pct": "~2% of the population",
        "interaction": "Your life is a three-act journey: intense trial-and-error experimentation (birth to ~30), a period of observation and integration (~30 to ~50), and finally embodied wisdom as a Role Model (~50+). You learn through direct experience, then spend decades making sense of it — and then the world looks to you as an example.",
        "personality_desc": "The 3rd line in your Personality Sun means your conscious self is a born experimenter. You don't learn by reading — you learn by doing, breaking things, and discovering what survives. This can make your early years feel chaotic and filled with 'mistakes,' but each experience is laying the foundation for deep, embodied wisdom.",
        "design_desc": "The 6th line in your Design is on a long timeline. Before ~30, you live intensely — making and breaking bonds, trying everything, accumulating data. From ~30 to ~50, you move 'onto the roof' — pulling back, observing, detaching, and making sense of all that experience. After ~50, you come down from the roof as an embodied Role Model — not because you're perfect, but because you've truly lived through it all.",
        "faq": [
            ("Why does my early life feel so chaotic compared to others?", "The 3/6 profile's first three decades are designed to be intense. You are living the 3rd line's trial-and-error curriculum while your 6th line is gathering raw material for later wisdom. It's not chaos for its own sake — it's data collection. Trust that every experience is building toward something you can't yet see."),
            ("What happens 'on the roof' (age ~30-50)?", "The roof phase is a natural withdrawal. You may feel less social, more contemplative, more interested in observing than participating. This is correct. You are integrating decades of experience into coherent wisdom. Don't fight the pull toward solitude — it's preparing you for your role model phase."),
            ("Do I really become a Role Model after 50?", "Yes — not because you're flawless, but because you've genuinely lived through the full arc. The 3rd line trials, the 6th line observation, and your accumulated perspective create a quality of embodied wisdom that others naturally recognize and look toward. You don't need to try to be a role model; you simply become one."),
        ],
        "experiments": [
            "Life chapter reflection — Write a brief timeline of your life's major 'trial and error' moments. For each, note what you learned. You may see the pattern preparing you for the roof.",
            "If under 30: Give yourself permission to experiment. If on the roof (~30-50): Give yourself permission to withdraw. If over 50: Give yourself permission to let others look to you — you've earned it.",
            "Find a 6th-line elder — Someone over 50 with a 6th line in their profile. Ask them about their arc. Their story will illuminate your own trajectory.",
        ],
    },
    "4-6": {
        "title": "The Opportunist / Role Model",
        "slug": "4-6",
        "conscious": 4,
        "unconscious": 6,
        "theme": "Community-Built Wisdom Over a Lifetime",
        "pct": "~14% of the population (tied for second most common)",
        "interaction": "Your life unfolds through relationships and community — and over time, your network becomes the stage where your earned wisdom is recognized. You are warm, approachable, and deeply connected, and your long arc transforms you from network-builder into community role model.",
        "personality_desc": "The 4th line in your Personality Sun means relationships are your vehicle. Opportunities, growth, and impact all come through people you know. You are naturally warm and approachable — your aura invites connection. The vulnerability of the 4th line is the price of its gift: extending yourself into relationships requires opening your heart, and that can hurt. But the rewards are profound.",
        "design_desc": "The 6th line in your Design carries you through the three-phase life arc. Before ~30, you live as a 3rd line — experimenting in relationships, learning through trial and error. From ~30 to ~50, you move 'onto the roof' — becoming more observational in your community role. After ~50, you embody the Role Model — your network now looks to you for wisdom, guidance, and example.",
        "faq": [
            ("Why are relationships so central to my life?", "Because the 4th line is the line of the Opportunist — and in Human Design, opportunity comes through people. Your network is not just a social asset; it's your primary vehicle for impact, income, and fulfillment. Investing in relationships is investing in your life's work."),
            ("How do I handle the vulnerability of caring so much about my community?", "The 4th line's vulnerability is real — every relationship is an open door through which hurt can enter. The practice is not to close the door but to develop discernment: not everyone in your network deserves equal access to your heart. Your 6th line wisdom, developing over decades, will help you distinguish between genuine connection and opportunistic access."),
            ("What if I'm under 30 and don't feel like a 'community builder' yet?", "Your 6th line is in its experimental phase — you're discovering who belongs in your network and who doesn't. This is correct. The community that will carry you through life is being forged in your twenties through trial and error. Don't rush to define your 'network'; let it form naturally through shared experience."),
        ],
        "experiments": [
            "Network audit — List your closest 15 relationships. Note who energizes you and who drains you. Your 4th line thrives with the right people and suffers with the wrong ones.",
            "Say yes to one social invitation you'd normally decline — The 4th line discovers opportunity through unexpected connections. One conversation can change the trajectory.",
            "If over 30: Reflect on how your community role has shifted. Are you naturally stepping into more of a mentoring/observational position? This is the roof calling.",
        ],
    },
    "4-1": {
        "title": "The Opportunist / Investigator",
        "slug": "4-1",
        "conscious": 4,
        "unconscious": 1,
        "theme": "Deep Knowledge Built Through and For Community",
        "pct": "~1% of the population (rare)",
        "interaction": "Your life is a beautiful fusion: relationships (line 4) drive you to build deep foundations of knowledge (line 1), and your knowledge, in turn, deepens your relationships. You are here to become an expert whose expertise is shared through trusted community connections.",
        "personality_desc": "The 4th line in your Personality Sun means you are fundamentally oriented toward people. Your warmth draws others in, and your network is your vehicle for everything — opportunity, learning, impact. You're the person others feel comfortable approaching, the natural connector who builds bonds that last.",
        "design_desc": "The 1st line in your Design means your body operates with an unconscious drive for deep understanding. You find yourself researching, studying, and building foundations without always knowing why — it's just how you're wired. This gives your relationships unusual depth; you're not just connecting socially but building your knowledge base through those connections.",
        "faq": [
            ("Am I a people person or a researcher?", "Both — and that's the magic of 4/1. Your research is fueled by the questions your community brings you. Your community is enriched by the depth of knowledge you bring to relationships. You are the expert who people actually want to talk to — warm and brilliant."),
            ("How do I manage the fear of not knowing enough while staying socially active?", "The 1st line insecurity loop can make you want to retreat and study more. But your 4th line needs people. The solution: study in community. Join study groups, attend conferences, learn alongside others. Your foundation-building doesn't have to be solitary — in fact, it's most powerful when shared."),
            ("What career paths suit a 4/1?", "Any role where deep expertise is valued within a community context: community educator, specialized consultant, research lead in a collaborative setting, therapist with deep theoretical grounding, or any position where your knowledge is your product and your network is your distribution channel."),
        ],
        "experiments": [
            "Create a study group — Pick something you want to learn and invite 3-5 people to learn it with you. Your 4th line thrives in collaborative study; your 1st line gets the foundation it craves.",
            "Teach what you're learning — For any new subject you're researching, commit to teaching one person what you've discovered within a week. This satisfies both lines simultaneously.",
            "Trust your body's knowing — Your unconscious 1st line knows more than your conscious mind gives it credit for. Next time you're in a conversation, notice how often you have the relevant knowledge without having 'prepared.'",
        ],
    },
    "5-1": {
        "title": "The Heretic / Investigator",
        "slug": "5-1",
        "conscious": 5,
        "unconscious": 1,
        "theme": "Authoritative Solutions Grounded in Deep Knowledge",
        "pct": "~14% of the population (tied for second most common)",
        "interaction": "Others project onto you the expectation of practical, universal solutions — and your deep, foundational knowledge (line 1) means you can actually deliver. You are here to be the authority whose solutions work because they're built on genuine mastery, not charisma.",
        "personality_desc": "The 5th line in your Personality Sun means you carry the projection of the universal problem-solver. People see you and think: 'They can fix this.' This can be exhausting, but it's also your calling. You are genuinely here to deliver practical, scalable solutions. The skill is learning to manage projection without hardening your heart.",
        "design_desc": "The 1st line in your Design gives you an unconscious, unshakeable foundation of knowledge. Your body knows things deeply — you've done the homework, built the foundation, and your research runs deep. This is what makes the 5th line projection sustainable: when people project 'expert' onto you, the foundation is actually there. You're not a fraud; you're the real thing.",
        "faq": [
            ("How do I know if someone's projection of me is accurate?", "Check against your 1st line foundation. If someone projects 'expert in X' onto you and you genuinely have deep knowledge of X — that's not projection, that's recognition. Accept it. If they project expertise you don't have, the 1st line knows and will feel uncomfortable. Trust that discomfort as a signal to clarify boundaries."),
            ("Why do people either love me or distrust me immediately?", "This is the 5th line's universal projection field at work. The 5th line is seen as either savior or threat — rarely neutral. It's not personal; it's a mechanics of their perception. Your job is to stay grounded in your actual knowledge (1st line) and let your work speak. The right people recognize you."),
            ("Is the 5/1 profile meant to be a leader?", "Yes — but not in the conventional sense. You're not a leader because you seek followers; you're a leader because your solutions work. The 5/1 leads through practical impact. When people adopt your solutions and their lives improve, leadership happens naturally. You don't need to perform 'leadership'; you need to keep deepening your foundation and delivering."),
        ],
        "experiments": [
            "Clarify your lane — Write down the 3 areas where you have genuine, deep knowledge (1st line). Commit to only offering solutions within these areas. When projected outside them, say: 'That's not my area of expertise.'",
            "Solution delivery practice — The next time someone brings you a problem, give them ONE clear, actionable solution drawn from your foundation. Then stop. Don't over-explain or manage their implementation. Trust your depth.",
            "Projection journal — For one week, note every time someone projects something onto you (good or bad). At the end, ask: 'Which of these projections align with what I actually know?'",
        ],
    },
    "5-2": {
        "title": "The Heretic / Hermit",
        "slug": "5-2",
        "conscious": 5,
        "unconscious": 2,
        "theme": "Universal Solutions From Natural Genius",
        "pct": "~2% of the population",
        "interaction": "You have a natural, almost effortless gift (line 2) that others project universal significance onto (line 5). You are here to deliver practical solutions that feel like magic to others but are simply your nature — while skillfully navigating the savior projection and protecting your need for solitude.",
        "personality_desc": "The 5th line in your Personality Sun means you are seen as someone with answers. The projection field is strong: people expect you to solve their problems, often before you've even spoken. This can feel like pressure, but it's also your purpose — delivering practical, universal solutions is what you're here for.",
        "design_desc": "The 2nd line in your Design carries your natural genius. It's something you do effortlessly, almost unconsciously. Others see it clearly — even when you don't. Your gift doesn't need to be forced or promoted; it needs to be cultivated in solitude and shared when you're genuinely called out. The 5th line projection creates the call; the 2nd line gift answers it.",
        "faq": [
            ("How do I know which calls to answer and which to ignore?", "The litmus test: does the call engage your natural gift (2nd line) or does it ask you to be something you're not? When your effortless talent is what's being requested, say yes. When people are projecting a savior role that requires you to perform outside your genius, say no. Your body knows the difference — it feels light vs. heavy."),
            ("Can the 5/2 profile handle fame?", "Carefully. The 5th line invites public attention; the 2nd line needs retreat. Fame that allows for prolonged solitude between public appearances can work. Fame that demands constant public presence will burn you out. Many 5/2s find success in fields where they can 'appear, deliver brilliance, and disappear' — consulting, writing, performance art."),
            ("What if I can't identify my natural gift?", "Your 2nd line gift is often invisible to you precisely because it's so natural. Look at what others consistently ask you for. Look at what you do that feels effortless but impressed others. Look at what you'd do for free because it doesn't feel like work. That's your gift. The 5th line will amplify its reach."),
        ],
        "experiments": [
            "Gift discovery — Ask 5 people who know you well: 'What do I make look easy that others find difficult?' Write down their answers. Patterns will emerge.",
            "Say no to one projection — This week, when someone projects a savior expectation that doesn't align with your natural gift, practice saying: 'That's not really my thing, but I can point you to someone who might help.'",
            "Hermit retreat — Schedule a 24-hour solitude window with no obligations. Spend it doing whatever your 2nd line naturally gravitates toward. Notice what emerges.",
        ],
    },
    "6-2": {
        "title": "The Role Model / Hermit",
        "slug": "6-2",
        "conscious": 6,
        "unconscious": 2,
        "theme": "Embodied Wisdom From Natural Genius",
        "pct": "~14% of the population (tied for second most common)",
        "interaction": "You have a natural, effortless gift (line 2) AND you're on the long arc of the Role Model (line 6). Your life unfolds across decades: early experimentation, mid-life observation, and later embodied wisdom — all anchored by a natural talent that's been there from the start. You are here to be a living example of what's possible when natural genius matures into wisdom.",
        "personality_desc": "The 6th line in your Personality Sun sets you on a three-phase journey. Before ~30, you live intensely — experimenting, making bonds, breaking them, gathering raw experience. From ~30 to ~50, you move 'onto the roof' — pulling back, observing, integrating. After ~50, you embody the Role Model — others naturally look to you for guidance, not because you sought it, but because you've genuinely walked the path.",
        "design_desc": "The 2nd line in your Design means you carry a natural genius — a talent so innate it's almost unconscious. This gift has been with you from birth and persists through all three phases of your 6th line journey. In your early years, the gift may surface unpredictably. On the roof, you learn to harness it consciously. As a Role Model, your natural talent, now matured by decades of integration, becomes a beacon others follow.",
        "faq": [
            ("Why does my natural gift feel inconsistent early in life?", "The 6th line's first phase (~0-30) is inherently experimental. You're trying out your 2nd line gift in different contexts, seeing where it lands, making discoveries. It feels inconsistent because you're in the laboratory of life. After 30, as you move onto the roof, the gift stabilizes and deepens."),
            ("How do I handle the pressure of being a Role Model before I feel ready?", "If you're under 50ish, you're not supposed to be a Role Model yet. You're in the laboratory or on the roof. The world may push you into role model position early — especially with the 2nd line's visible talent — but your design says: not yet. Give yourself permission to be unfinished. Your time will come."),
            ("What's the gift of being a 6/2 specifically?", "The 6/2 combines two of the most magnetic lines in Human Design. The 2nd line's natural genius draws people; the 6th line's long arc creates genuine wisdom. Over time, you become someone whose mere presence is instructive — not because you lecture, but because you embody a life fully lived. That's rare."),
        ],
        "experiments": [
            "Phase check — Which phase are you in? Lab (under 30), roof (30-50), or Role Model (50+)? Align your expectations with your current phase. Don't rush the process.",
            "Protect your 2nd line — No matter your phase, schedule regular solitude. Your natural genius needs time alone to breathe and develop. This is non-negotiable.",
            "If on the roof — Keep a 'wisdom journal.' Each week, write one insight gained from observing life rather than participating. These insights will become your role model curriculum.",
        ],
    },
    "6-3": {
        "title": "The Role Model / Martyr",
        "slug": "6-3",
        "conscious": 6,
        "unconscious": 3,
        "theme": "Wisdom Forged Through a Lifetime of Discovery",
        "pct": "~2% of the population",
        "interaction": "You are the profile that has seen it all. The 6th line's long arc of becoming — from intense experimentation, through withdrawal and observation, to embodied wisdom — is powered by the 3rd line's relentless drive to learn through direct experience. By the time you're a Role Model, you've genuinely been through the fire. Your wisdom is not theoretical; it's forged.",
        "personality_desc": "The 6th line in your Personality Sun carries you through three acts. Before ~30, you live like a 3rd line — diving into experience with intensity, making discoveries through trial and error. From ~30 to ~50, you ascend 'onto the roof' — pulling back, observing, integrating everything you've lived through. After ~50, you come down as an embodied Role Model — not because you're perfect but because you've genuinely covered the territory.",
        "design_desc": "The 3rd line in your Design means your body is wired for discovery. Pessimism is your hidden strength — by anticipating what could go wrong, you navigate more skillfully than optimists. Your unconscious throws you into experiences that teach you what works. Every 'mistake' is data. Combined with the 6th line's long arc, this means you accumulate more real-world data than almost any other profile — and then spend decades making sense of it.",
        "faq": [
            ("Why does my life feel harder than most people's?", "The 6/3 profile carries a heavy curriculum — both lines learn through experience, and the 6th line adds the weight of becoming a Role Model. It can feel like life gives you the hardest tests. The reframe: you're not being punished; you're being prepared. The depth of wisdom required to truly embody a Role Model demands a depth of experience, and you're getting it."),
            ("Will life ever get easier?", "Yes — and no. After ~50, the struggle changes. It's no longer about trial and error; it's about living from integrated wisdom. The experiences don't stop, but your relationship to them transforms. You stop being tossed by the waves and become the shore. Many 6/3s report that their later years are the most peaceful and satisfying."),
            ("How do I survive the trial-and-error phase without burning out?", "Three survival strategies: (1) Give yourself permission to rest between experiments — the 3rd line needs recovery. (2) Journal your discoveries — seeing the accumulated wisdom reduces the sense of chaos. (3) Find other 6th line people who understand the arc. You're not alone in this."),
        ],
        "experiments": [
            "The discovery archive — Start a running document of everything you've learned through direct experience. This is your curriculum. In Role Model phase, it becomes your gift to the world.",
            "Pessimism as a tool — Next time you anticipate what could go wrong, don't suppress it. Use it: map out the risks, then plan around them. This is your 3rd line genius at work.",
            "Find a 6/3 elder — Someone over 60 with this profile. Ask them about their journey. Their perspective on the full arc will contextualize everything you're going through.",
        ],
    },
}

# ── CSS shared across all profile pages ──
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
    position: relative;
    z-index: 1;
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
  .hero .profile-tag {
    display: inline-block;
    margin-top: 16px;
    padding: 6px 18px;
    background: var(--gold-soft);
    color: var(--gold-light);
    border-radius: 20px;
    font-size: 0.88rem;
    font-weight: 600;
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
    padding: 10px 0;
    font-size: 0.92rem;
    color: var(--text-secondary);
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .content ul li::before {
    content: "▸ ";
    color: var(--gold);
  }

  .profile-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 48px;
  }
  .profile-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 28px 24px;
  }
  .profile-card .line-number {
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
    margin-bottom: 12px;
  }
  .profile-card h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: 10px;
  }
  .profile-card p {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.65;
  }

  .related-profiles {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 40px 36px;
    margin-bottom: 48px;
  }
  .related-profiles h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 20px;
    color: var(--white);
    letter-spacing: -0.02em;
  }
  .related-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
  }
  .related-chip {
    display: block;
    padding: 12px 16px;
    background: rgba(201,168,76,0.06);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    text-decoration: none;
    color: var(--text-secondary);
    font-size: 0.88rem;
    transition: var(--transition);
    text-align: center;
  }
  .related-chip:hover {
    border-color: var(--gold);
    color: var(--gold-light);
  }

  .faq {
    padding: 0 0 24px;
  }
  .faq h2 {
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 32px;
    letter-spacing: -0.02em;
  }
  .faq-item {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 24px 28px;
    margin-bottom: 12px;
  }
  .faq-item h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--gold-light);
    margin-bottom: 8px;
  }
  .faq-item p {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.65;
  }

  .experiment-list li {
    padding: 12px 0 !important;
  }
  .experiment-list li strong {
    color: var(--gold-light);
  }

  .cta-section {
    text-align: center;
    padding: 48px 24px 64px;
    position: relative;
    z-index: 1;
  }
  .cta-section h2 {
    font-size: clamp(1.3rem, 2.5vw, 1.7rem);
    font-weight: 700;
    margin-bottom: 12px;
    letter-spacing: -0.02em;
  }
  .cta-section p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 480px;
    margin: 0 auto 24px;
  }
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 13px 28px;
    border-radius: 10px;
    font-size: 0.92rem;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    border: none;
    transition: var(--transition);
    letter-spacing: -0.01em;
  }
  .btn-primary {
    background: linear-gradient(135deg, var(--gold-bright), var(--gold));
    color: var(--navy-deep);
    box-shadow: 0 4px 20px rgba(201,168,76,0.3);
  }
  .btn-primary:hover {
    box-shadow: 0 6px 30px rgba(201,168,76,0.45);
    transform: translateY(-2px);
  }

  footer {
    background: rgba(6, 13, 26, 0.6);
    border-top: 1px solid rgba(201,168,76,0.08);
    padding: 28px 20px;
    text-align: center;
    position: relative;
    z-index: 1;
  }
  .footer-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }
  .footer-inner .left { display: flex; flex-direction: column; gap: 4px; text-align: left; }
  .footer-inner .brand { font-weight: 600; color: var(--text-primary); font-size: 0.88rem; }
  .footer-inner .license { font-size: 0.76rem; color: var(--text-muted); }
  .footer-links { display: flex; gap: 18px; }
  .footer-links a {
    font-size: 0.8rem;
    color: var(--text-muted);
    text-decoration: none;
    transition: var(--transition);
  }
  .footer-links a:hover { color: var(--gold-light); }

  @media (max-width: 768px) {
    .nav-links { gap: 12px; }
    .nav-links a { font-size: 0.78rem; }
    .content, .related-profiles { padding: 28px 20px; }
    .profile-grid { grid-template-columns: 1fr; }
    .footer-inner { flex-direction: column; text-align: center; }
  }

  /* Index page extras */
  .page-header {
    text-align: center;
    padding: 60px 24px 48px;
  }
  .page-header h1 {
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 16px;
    background: linear-gradient(180deg, #ffffff 0%, #c0c8d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .page-header p {
    font-size: 1.1rem;
    color: var(--text-secondary);
    max-width: 640px;
    margin: 0 auto;
  }

  .profile-index-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 60px;
  }
  .profile-index-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 28px 24px;
    text-decoration: none;
    transition: var(--transition);
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .profile-index-card:hover {
    border-color: rgba(201,168,76,0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(201,168,76,0.08);
  }
  .profile-index-number {
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
  }
  .profile-index-card h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--white);
    letter-spacing: -0.01em;
  }
  .profile-index-theme {
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.5;
  }
  .profile-index-meta {
    display: flex;
    gap: 16px;
    font-size: 0.78rem;
    color: var(--gold);
    font-weight: 500;
  }
"""


def profile_page_html(data):
    """Generate complete HTML for a single profile page."""
    slug = data["slug"]
    title = data["title"]
    c_line = data["conscious"]
    u_line = data["unconscious"]
    c_name = LINE_INFO[c_line]["name"]
    u_name = LINE_INFO[u_line]["name"]

    page_title = f"Human Design Profile {slug} — {title} | Complete Guide"
    meta_desc = f"Explore the {slug} Profile ({title}) in Human Design. Life theme: {data['theme']}. Learn the {c_name} and {u_name} line meanings, interaction style, and practical experiments for living your {slug} design."
    og_desc = f"Complete guide to Human Design Profile {slug} ({title}). Theme: {data['theme']}. Covers {c_name} (Personality) and {u_name} (Design) line meanings, FAQs, and practical experiments."

    # Build FAQ HTML
    faq_html = ""
    for q, a in data["faq"]:
        faq_html += f"""    <div class="faq-item">
      <h3>{q}</h3>
      <p>{a}</p>
    </div>
"""

    # Build experiments list
    exp_html = ""
    for exp in data["experiments"]:
        exp_html += f'      <li><strong>{exp.split(" — ")[0]}</strong> — {exp.split(" — ")[1] if " — " in exp else exp}</li>\n'

    # Build related profiles
    related = []
    for p_slug, p_data in PROFILES.items():
        if p_slug == slug:
            continue
        # Show profiles sharing a line
        if c_line in (p_data["conscious"], p_data["unconscious"]) or u_line in (p_data["conscious"], p_data["unconscious"]):
            related.append((p_slug, p_data["title"]))
    # Limit to 8 and add "All Profiles"
    related = related[:8]
    related_html = ""
    for r_slug, r_title in related:
        related_html += f'      <a href="{r_slug}.html" class="related-chip">{r_slug} — {r_title}</a>\n'
    related_html += f'      <a href="index.html" class="related-chip">All 12 Profiles →</a>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title} | Human Design Engine</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="Human Design, Profile {slug}, {title}, {c_name}, {u_name}, Human Design profiles, {slug} profile, Human Design Engine">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://humandesignengine.com/human-design/profiles/{slug}/">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://humandesignengine.com/human-design/profiles/{slug}/">
<meta property="og:site_name" content="Human Design Engine">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page_title}">
<meta name="twitter:description" content="{og_desc}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Human Design Profile {slug} — {title}: Complete Guide",
  "description": "{meta_desc}",
  "author": {{ "@type": "Organization", "name": "Human Design Engine" }},
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }},
  "mainEntityOfPage": {{ "@type": "WebPage", "@id": "https://humandesignengine.com/human-design/profiles/{slug}/" }}
}}
</script>
<style>
{CSS}
</style>
</head>
<body>

<nav>
  <div class="nav-inner">
    <a href="/" class="nav-logo">
      <div class="icon">◆</div>
      Human Design Engine
    </a>
    <div class="nav-links">
      <a href="/human-design/types/">Types</a>
      <a href="/human-design/centers/">Centers</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/gates/">Gates</a>
      <a href="/human-design/profiles/">Profiles</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    <a href="/human-design/profiles/">Profiles</a> <span>›</span>
    Profile {slug} — {title}
  </div>

  <section class="hero">
    <div class="hero-icon">{slug}</div>
    <h1>Profile {slug}: {title}</h1>
    <p class="subtitle">{data['interaction']}</p>
    <div class="profile-tag">{data['pct']}</div>
  </section>

  <div class="info-grid">
    <div class="info-card">
      <div class="label">Life Theme</div>
      <div class="value">{data['theme']}</div>
    </div>
    <div class="info-card">
      <div class="label">Personality (Conscious)</div>
      <div class="value">Line {c_line} — {c_name}</div>
    </div>
    <div class="info-card">
      <div class="label">Design (Unconscious)</div>
      <div class="value">Line {u_line} — {u_name}</div>
    </div>
    <div class="info-card">
      <div class="label">Population</div>
      <div class="value">{data['pct'].split('(')[0].strip() if '(' in data['pct'] else data['pct']}</div>
    </div>
  </div>

  <div class="profile-grid">
    <div class="profile-card">
      <div class="line-number">{c_line}</div>
      <h3>Personality Line {c_line}: {c_name}</h3>
      <p>{data['personality_desc']}</p>
    </div>
    <div class="profile-card">
      <div class="line-number">{u_line}</div>
      <h3>Design Line {u_line}: {u_name}</h3>
      <p>{data['design_desc']}</p>
    </div>
  </div>

  <article class="content">
    <h2>Living as a {slug} Profile</h2>
    <p>Your profile in Human Design is the costume you wear in this lifetime — it's how you're seen and how you see yourself. The {slug} profile combines the <span class="highlight">{c_name}</span> (your conscious Personality — what you identify with) and the <span class="highlight">{u_name}</span> (your unconscious Design — the body's intelligence that you may not recognize but others see clearly). Together, these two lines create your unique life geometry.</p>

    <p>The {c_name} line shapes how you consciously approach life. {LINE_INFO[c_line]['conscious'][:200]}... This is the part of yourself you're most aware of — but it's only half the story.</p>

    <p>The {u_name} line shapes your unconscious, embodied intelligence. {LINE_INFO[u_line]['unconscious'][:200]}... This operates below your awareness but powerfully influences how others experience you and how opportunities find you.</p>

    <p>Together, the {slug} profile creates a life theme of <span class="highlight">{data['theme']}</span>. The interaction between these two lines is where the richness lives — the {c_name} and {u_name} don't just coexist; they dance. Understanding the dance is the key to living your profile correctly.</p>

    <h3>Your Interaction Style: How Others Experience You</h3>
    <p>{data['interaction']}</p>

    <h3>Practical Experiments for Profile {slug}</h3>
    <p>Human Design is not a belief system — it's an experiment. These practices are designed to help you discover firsthand how your {slug} profile operates. Try them with curiosity, not expectation.</p>
    <ul class="experiment-list">
{exp_html}    </ul>

    <h3>The Shadow and Gift of Each Line</h3>
    <p><span class="highlight">Line {c_line} ({c_name}) Gift:</span> {LINE_INFO[c_line]['life_role']}. The shadow emerges when this line is operating from not-self: for the {c_name}, this might look like <span class="highlight">{LINE_INFO[c_line]['conscious'].split('. Your challenge is ')[1].split('.')[0] if '. Your challenge is ' in LINE_INFO[c_line]['conscious'] else 'operating from conditioning rather than authenticity'}</span>.</p>

    <p><span class="highlight">Line {u_line} ({u_name}) Gift:</span> {LINE_INFO[u_line]['life_role']}. The shadow emerges unconsciously — others may experience you as withdrawn, difficult to reach, or unpredictable. When you're living your design, these 'shadows' transform into the very qualities that make your profile magnetic.</p>

    <h3>How Profile {slug} Relates to Your Type and Authority</h3>
    <p>Your profile doesn't exist in isolation. It's layered with your Type and Authority to create your complete design. For example, a {slug} Generator will live this profile very differently from a {slug} Projector. The Generator's sacral response colors how the {c_name} and {u_name} lines express. The Projector's need for invitation shapes when and how the profile's gifts are recognized. Always read your profile <em>through</em> the lens of your Type, Strategy, and Authority.</p>
  </article>

  <section class="related-profiles">
    <h2>Explore Related Profiles</h2>
    <p style="color:var(--text-secondary);margin-bottom:20px;">These profiles share at least one line with the {slug} profile. Understanding related profiles deepens your grasp of how each line expresses in different combinations.</p>
    <div class="related-grid">
{related_html}    </div>
  </section>

  <section class="faq">
    <h2>Frequently Asked Questions — Profile {slug}</h2>
{faq_html}  </section>

  <section class="cta-section">
    <h2>Discover Your Complete Human Design Chart</h2>
    <p>Your profile is just one piece. Your full chart reveals your Type, Authority, defined Centers, Channels, Gates, and Incarnation Cross — the complete blueprint of your design. Get your personalized 70+ page report.</p>
    <a href="/buy-report.html" class="btn btn-primary">Get Your Full Personalized Report →</a>
  </section>

</div>

<footer>
  <div class="footer-inner">
    <div class="left">
      <span class="brand">Human Design Engine</span>
      <span class="license">Verified chart data — open-source computation engine.</span>
    </div>
    <div class="footer-links">
      <a href="/human-design/types/">Types</a>
      <a href="/human-design/profiles/">Profiles</a>
      <a href="/human-design/centers/">Centers</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/gates/">Gates</a>
      <a href="/privacy">Privacy</a>
    </div>
  </div>
</footer>

</body>
</html>"""


def index_page_html():
    """Generate the profiles index page."""
    cards = ""
    for slug, data in PROFILES.items():
        cards += f"""    <a href="{slug}.html" class="profile-index-card">
      <div class="profile-index-number">{slug}</div>
      <h3>{data['title']}</h3>
      <p class="profile-index-theme">{data['theme']}</p>
      <div class="profile-index-meta">
        <span>Line {data['conscious']} + Line {data['unconscious']}</span>
        <span>{data['pct'].split('(')[0].strip() if '(' in data['pct'] else data['pct']}</span>
      </div>
    </a>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 12 Human Design Profiles — Complete Guide | Human Design Engine</title>
<meta name="description" content="Explore all 12 Human Design profiles: Investigator, Hermit, Martyr, Opportunist, Heretic, and Role Model in their 12 combinations. Learn line meanings, life themes, and interaction styles for every profile.">
<meta name="keywords" content="Human Design profiles, 12 profiles, 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3, Investigator, Hermit, Martyr, Opportunist, Heretic, Role Model, Human Design Engine">
<link rel="canonical" href="https://humandesignengine.com/human-design/profiles/">
<meta property="og:title" content="The 12 Human Design Profiles — Complete Guide | Human Design Engine">
<meta property="og:description" content="Complete reference for all 12 Human Design profiles: life themes, line meanings, interaction styles, FAQ, and practical experiments for every profile combination.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://humandesignengine.com/human-design/profiles/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="The 12 Human Design Profiles — Complete Guide">
<meta name="twitter:description" content="Complete reference for all 12 Human Design profiles with life themes, line meanings, and practical experiments.">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "The 12 Human Design Profiles",
  "description": "A complete guide to all 12 Human Design profiles, including the 6 lines (Investigator, Hermit, Martyr, Opportunist, Heretic, Role Model) in their 12 unique combinations with life themes, interaction styles, and practical experiments.",
  "url": "https://humandesignengine.com/human-design/profiles/",
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
    <a href="/" class="nav-logo">
      <div class="icon">◆</div>
      Human Design Engine
    </a>
    <div class="nav-links">
      <a href="/human-design/types/">Types</a>
      <a href="/human-design/centers/">Centers</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/gates/">Gates</a>
      <a href="/human-design/profiles/">Profiles</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    Profiles
  </div>

  <div class="page-header">
    <h1>The 12 Profiles of Human Design</h1>
    <p>Your Profile is the costume you wear in this lifetime — the role you play and the geometry of how you interact with the world. It combines your conscious Personality line (who you think you are) with your unconscious Design line (the body's wisdom others see in you).</p>
    <p style="margin-top:16px;">The six lines — <span class="highlight">Investigator (1), Hermit (2), Martyr (3), Opportunist (4), Heretic (5), Role Model (6)</span> — combine into 12 unique profiles. Each one is a distinct life path with its own theme, interaction style, and purpose.</p>
  </div>

  <div class="profile-index-grid">
{cards}  </div>

  <section class="content">
    <h2>Understanding the Six Lines</h2>
    <p>Every Human Design profile is built from two of the six lines below. The first number is your <span class="highlight">Personality (conscious) line</span> — this is who you think you are, what you identify with. The second number is your <span class="highlight">Design (unconscious) line</span> — this is the body's intelligence that operates below your awareness but that others experience powerfully.</p>

    <h3>Line 1 — The Investigator</h3>
    <p>The Investigator needs a solid foundation. You study, research, and dig deep before feeling ready to contribute. Your authority comes from genuine depth of knowledge. The shadow is insecurity — feeling you never know enough. Your gift is becoming a reliable, authoritative source others can trust.</p>

    <h3>Line 2 — The Hermit</h3>
    <p>The Hermit carries a natural, effortless genius — a talent so innate you may not recognize it as special. You need solitude to cultivate your gift and must wait to be "called out" by others before sharing it. The shadow is hiding. The gift is that your talent, when recognized and shared, is magnetic and transformative.</p>

    <h3>Line 3 — The Martyr</h3>
    <p>The Martyr learns through direct experience — trial and error is your curriculum. You make and break bonds, discover what works and what doesn't, and emerge with hard-won wisdom. The shadow is seeing failures as mistakes rather than data. The gift is resilience and the ability to say with authority: "This works. I've tested it."</p>

    <h3>Line 4 — The Opportunist</h3>
    <p>The Opportunist's life moves through relationships. Opportunities, growth, and impact come through your network of trusted connections. Your warmth draws people in. The shadow is vulnerability — extending yourself into relationships opens you to hurt. The gift is a rich, supportive community that carries you through life.</p>

    <h3>Line 5 — The Heretic</h3>
    <p>The Heretic is a universalizer — you see the practical solution that works for everyone. Others project onto you, seeing you as either savior or scapegoat. The shadow is getting entangled in projection. The gift is delivering solutions that actually work, at scale, because they're grounded in practical truth.</p>

    <h3>Line 6 — The Role Model</h3>
    <p>The Role Model lives a three-phase life: experimentation (birth to ~30), observation and integration (~30 to ~50), and embodied wisdom (~50+). The shadow is impatience with the long arc. The gift is becoming a living example of wisdom earned through a fully lived life.</p>
  </section>

  <section class="cta-section">
    <h2>Find Your Profile</h2>
    <p>Your Human Design chart reveals your exact profile — the combination of your Personality Sun/Earth line and your Design Sun/Earth line. Discover your full design with a personalized 70+ page report.</p>
    <a href="/buy-report.html" class="btn btn-primary">Get Your Full Personalized Report →</a>
  </section>

</div>

<footer>
  <div class="footer-inner">
    <div class="left">
      <span class="brand">Human Design Engine</span>
      <span class="license">Verified chart data — open-source computation engine.</span>
    </div>
    <div class="footer-links">
      <a href="/human-design/types/">Types</a>
      <a href="/human-design/profiles/">Profiles</a>
      <a href="/human-design/centers/">Centers</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/gates/">Gates</a>
      <a href="/privacy">Privacy</a>
    </div>
  </div>
</footer>

</body>
</html>"""


# ═══════════════════════════════════════════
# GENERATION
# ═══════════════════════════════════════════

if __name__ == "__main__":
    # Generate index page
    index_path = os.path.join(OUT_DIR, "index.html")
    index_html = index_page_html()
    with open(index_path, "w") as f:
        f.write(index_html)
    print(f"Wrote index.html ({len(index_html)} bytes, ~{index_html.count(chr(10))} lines)")

    # Generate individual profile pages
    for slug, data in PROFILES.items():
        filename = f"{slug}.html"
        filepath = os.path.join(OUT_DIR, filename)
        html = profile_page_html(data)
        with open(filepath, "w") as f:
            f.write(html)
        print(f"Wrote {filename} ({len(html)} bytes, ~{html.count(chr(10))} lines)")

    print("\nDone. Generated 1 index + 12 profile pages.")
