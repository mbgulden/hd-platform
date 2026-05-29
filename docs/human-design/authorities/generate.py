#!/usr/bin/env python3
"""
Generate 8 Human Design Authority SEO pages (7 authorities + index).
Uses the navy/gold design system with full SEO metadata.
Each authority page is ~400-600 lines of substantive content.
Run from authorities/ directory.
"""

import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)

# ── Authority data ──
AUTHORITIES = {
    "emotional": {
        "title": "Emotional (Solar Plexus) Authority",
        "short_title": "Emotional Authority",
        "slug": "emotional",
        "center": "Solar Plexus",
        "icon": "☉",
        "pct": "~47% of the population (most common authority)",
        "mechanic": "You have a defined Solar Plexus, which operates as a motor and awareness center. This means you generate emotional waves — a continuous cycle of moods, feelings, and emotional states that rise and fall like a tide. Your authority is not in any single feeling but in the clarity that emerges over time as the wave passes through its full cycle. No single moment on the wave is 'the truth' — only the pattern across time reveals what is correct for you.",
        "how_to_use": "You make decisions by riding your emotional wave over time. When a decision presents itself, feel into it at different points on your wave — when you're up, when you're down, when you're neutral. Don't make a decision from any single emotional state. Wait for clarity, which is a calm, settled knowing that persists regardless of where you are on the wave. Clarity is not a high or a low — it's the still point that emerges after the wave has been fully processed.",
        "waiting_period": "There is no fixed waiting period for Emotional Authority. For small decisions, clarity may come in hours. For major life decisions — relationships, career moves, relocations — waiting at least a few days (or even a full emotional cycle) is recommended. The key is not the clock but the felt sense: do you feel the same 'yes' or 'no' at multiple points on your wave? If the answer changes depending on your mood, you're not yet at clarity. Wait longer.",
        "common_mistakes": [
            "Making decisions in the high of excitement — The emotional high feels like a full-body YES, but it's just one point on the wave. When the low comes, that 'yes' may dissolve. Wait.",
            "Making decisions in the low to escape discomfort — The emotional low makes everything feel like NO, including things that might be correct. Don't reject opportunities from the trough of the wave.",
            "Confusing nervous system activation with emotional clarity — Butterflies, anxiety, or intensity are not clarity. They're just one flavor of the wave.",
            "Rushing because others pressure you — People without Emotional Authority may make fast decisions and pressure you to do the same. Their timing is not your timing. You need the wave.",
            "Thinking 'no clarity' is clarity — If you feel confused or uncertain, that's not a no. It means the wave hasn't resolved yet. Keep waiting.",
        ],
        "types_have_it": "Generators, Manifesting Generators, Projectors, and Manifestors can all have Emotional Authority — it's the most common authority because the Solar Plexus is one of the most commonly defined centers. If you have a defined Solar Plexus (colored in on your chart), you have Emotional Authority — regardless of your Type.",
        "faq": [
            ("What's the difference between Emotional Authority and just being emotional?", "Everyone has emotions. Emotional Authority is specifically about having a defined Solar Plexus — meaning your emotional wave is consistent and reliable. Your emotions aren't just reactions to life; they're a built-in decision-making system. The difference is mechanical: with a defined Solar Plexus, your emotions follow a predictable wave pattern that generates clarity over time. Without it, emotions are more transient and reactive."),
            ("How do I know when I've reached clarity?", "Clarity feels calm, settled, and consistent. It doesn't oscillate with your mood. When you check in at different points on your wave — happy, sad, neutral — and the answer stays the same, that's clarity. It's a quiet knowing, not an intense feeling. Many people describe it as 'the volume turning down' on the decision rather than a loud YES or NO."),
            ("What if I need to make a fast decision and don't have time to ride the wave?", "For true emergencies, you do what you must. But most 'urgent' decisions aren't actually emergencies — they're pressure from others or from your own discomfort with uncertainty. Practice discerning real urgency from imagined urgency. For day-to-day speed, you'll learn over time that your initial wave response contains information — but never commit from it alone. Buy yourself even an hour when you can."),
            ("Can I speed up the emotional wave with practices like journaling or meditation?", "You can't speed up the wave's natural cycle, but you can create conditions for clarity to emerge more cleanly. Journaling helps you track your decision across the wave — you can look back and see patterns. Meditation quiets the mental noise so you can actually feel the wave. But neither replaces time. The wave has its own intelligence and pace."),
            ("What if I share Emotional Authority with my partner/family/colleagues?", "When multiple Emotional Beings are involved in a decision, everyone needs time. The person who initiated the decision may reach clarity first, but others may still be on their wave. Respect the slowest wave in any group decision. This is why Emotional Authority people often benefit from communicating: 'I need time with this. I'll come back to you.'"),
        ],
        "experiments": [
            "Track your wave for a week — Note your emotional state morning, afternoon, and evening. Look for your personal pattern: fast waves? slow waves? Are you more up in the morning or evening? Knowledge of your wave is power.",
            "Practice 'I'll sleep on it' — For every decision this week (even small ones), add a minimum overnight waiting period. Notice how many 'urgent yeses' dissolve by morning. Notice which ones persist.",
            "When clarity comes, write it down — Record what clarity actually feels like for you. Is it a body sensation? A quiet voice? A settled feeling in your gut? This becomes your reference point for future decisions.",
            "Say no to time pressure — Next time someone pushes for an immediate answer, say: 'I need time to feel into this. I'll get back to you by [specific time].' Then actually take that time.",
        ],
        "mechanics_detail": "Mechanically, the defined Solar Plexus is a motor that generates emotional energy and an awareness center that processes it. The wave has three possible configurations in your chart: individual (melancholic/passion wave — sudden spikes and depths), tribal (romantic/sensitivity wave — gradual rolling), or collective (experiential wave — peaks of anticipation and troughs of experience). Your specific wave pattern is determined by which gates and channels activate your Solar Plexus. All waves produce clarity — but at different rhythms.",
        "signature_alignment": "When you're making decisions correctly through your Emotional Authority, your life begins to flow with less resistance. You won't feel perpetually calm — the wave still moves — but your relationship to it changes. You stop fighting the lows and mistaking the highs for truth. Your emotional life becomes a trusted compass rather than something to escape or control. This is the signature of living your design.",
    },
    "sacral": {
        "title": "Sacral Authority",
        "short_title": "Sacral Authority",
        "slug": "sacral",
        "center": "Sacral",
        "icon": "⚡",
        "pct": "~35% of the population",
        "mechanic": "You have a defined Sacral center with no defined Solar Plexus. Your Sacral is a pure motor — it generates sustainable life-force energy and is the only center that responds with an immediate, binary 'yes' or 'no' in the present moment. This response is not emotional, not mental, not strategic — it's a gut-level, somatic response that happens in the now. The Sacral speaks through sounds (uh-huh for yes, uh-uh for no), through body movement (leaning in or pulling back), and through the felt sense of expansion or contraction around a decision.",
        "how_to_use": "Your decision-making is in-the-moment. You don't need time to process (unlike Emotional Authority). You need to be presented with something to respond to, then listen for the sacral response. The key is: you cannot initiate from your Sacral — you can only respond. Life must come to you, and then your gut answers. This means your most powerful tool is putting yourself in situations where life can ask you questions. Ask someone to ask you yes/no questions. Notice the immediate body response before your mind jumps in with analysis.",
        "waiting_period": "There is no waiting period for Sacral Authority. The response is immediate — it happens in the now. The 'waiting' is not about the response itself but about waiting for life to present you with something to respond to. You are not designed to go out and make things happen; you are designed to respond to what comes to you. The discipline is in the waiting for the stimulus, not in the response time. Once asked, your Sacral answers instantly.",
        "common_mistakes": [
            "Initiating instead of responding — Sacral beings are here to respond to life, not to push or force things into being. When you initiate, you burn sacral energy on things that may not be correct for you.",
            "Letting your mind override your gut — Your mind will produce logical reasons to say yes or no. But your Sacral already knows. The moment you start 'thinking about it,' you've left your authority.",
            "Not giving your Sacral something concrete to respond to — Abstract questions ('Should I pursue my passion?') don't elicit clear sacral responses. Concrete yes/no questions work best: 'Do you want to call Sarah today?'",
            "Confusing fear/excitement with sacral response — Fear is mental/emotional. Sacral response is physical — a literal opening or closing in the gut. Learn the difference.",
            "Staying in dead-end situations — Your Sacral can burn out if it keeps responding 'yes' to a situation that no longer serves you. The response is always in the now — what was correct yesterday may not be correct today.",
        ],
        "types_have_it": "Sacral Authority is exclusive to Generators and Manifesting Generators who do NOT have a defined Solar Plexus. If you're a Generator or Manifesting Generator without a colored-in Solar Plexus center, you have Sacral Authority. Projectors, Manifestors, and Reflectors cannot have Sacral Authority because they don't have a defined Sacral center.",
        "faq": [
            ("What does a sacral response actually feel like?", "For most people, the sacral 'yes' feels like expansion, openness, leaning forward, a physical 'mm-hmm' sound wanting to come out, or a sense of energy rising. The 'no' feels like contraction, pulling back, heaviness, or a literal 'nuh-uh' sensation. Some people feel it as a gut sensation of opening or closing. It's not an emotion — it's a physical, somatic response that happens faster than thought."),
            ("How do I know it's my Sacral and not my mind?", "The Sacral responds FIRST, then the mind jumps in. The Sacral response is immediate and wordless. The mind's response comes with words, reasons, fears, and stories — usually within a second or two. Practice catching that first flash of sensation before the narrative arrives. That's your Sacral."),
            ("Can I ask myself sacral questions?", "You can, but it works best when someone else asks you. There's something about being asked externally that elicits a cleaner sacral response. For self-questioning, try speaking out loud: 'Do I want to go to that party tonight?' and listen for the body response. Writing yes/no questions and feeling into each one can also work."),
            ("What if I don't feel anything — no yes, no no?", "A neutral or absent sacral response is a no for now. It could mean: this isn't for you, or you don't have enough information yet to respond. Don't push for an answer. Wait for something clearer to respond to. The Sacral doesn't do 'maybe' — if it's not a clear yes, treat it as a no."),
            ("How is Sacral Authority different from Emotional Authority?", "Emotional Authority requires waiting over time for clarity across the emotional wave. Sacral Authority provides an immediate, in-the-moment response. Emotional beings should never decide in the moment; Sacral beings should never delay once the response is clear. The two are fundamentally different operating systems. If you have a defined Solar Plexus, you have Emotional Authority regardless of your Sacral definition."),
        ],
        "experiments": [
            "The yes/no game — Ask a friend to ask you 20 rapid-fire yes/no questions about real things ('Do you want pizza tonight?' 'Do you want to call your mom?'). Answer with the first sound or body sensation. Don't think. Notice the pattern.",
            "One day of pure response — For one full day, don't initiate anything. Only do things someone asks you to do or that life directly presents. Notice how different it feels to move through the world as a responder.",
            "Sacral journal — For a week, note every time your gut said one thing and your mind overrode it. What happened? This builds evidence for trusting the Sacral.",
            "Sacral sounds — Practice making the sacral sounds out loud: 'uh-huh' for yes, 'uh-uh' for no. Let them be guttural, wordless, physical. Notice how satisfying it feels to let your Sacral speak audibly.",
        ],
        "mechanics_detail": "The defined Sacral center is the powerhouse of the bodygraph — it's the only center that generates sustainable life-force energy. It's connected to the reproductive system and the body's fundamental capacity for work and creativity. The Sacral responds to frequency, not logic. It can't be reasoned with, convinced, or negotiated with — it simply opens or closes based on what is correct in the moment. Your Sacral is a binary system: yes or no. Learning to trust this binary is the entire path of Sacral Authority.",
        "signature_alignment": "When you follow your Sacral Authority, you experience satisfaction — the signature of the Generator. Your energy becomes sustainable rather than depleting. You go to bed tired but fulfilled, not exhausted and frustrated. Life feels like a series of 'yeses' to things that genuinely light you up. When you ignore your Sacral, you experience frustration — the not-self theme. Frustration is your signal that you're initiating instead of responding, or responding to things your gut said no to.",
    },
    "splenic": {
        "title": "Splenic (Spleen) Authority",
        "short_title": "Splenic Authority",
        "slug": "splenic",
        "center": "Spleen",
        "icon": "✦",
        "pct": "~11% of the population",
        "mechanic": "You have a defined Spleen center and neither a defined Solar Plexus nor a defined Sacral (as Projectors) OR you have a defined Spleen as a Manifestor without Emotional or Sacral definition. The Spleen is the oldest awareness center — it operates on pure instinct, intuition, and survival intelligence. It speaks once, quietly, in the present moment, and it never repeats itself. The splenic voice is a whisper: a subtle knowing, a body sense, a flash of taste or smell, a sudden 'this is safe' or 'this is not.' It is lightning-fast and absolutely binary — yes or no, safe or unsafe.",
        "how_to_use": "You make decisions by attuning to the subtle, instantaneous signals of your spleen. The splenic voice is quiet — it doesn't argue, repeat, or justify. You must be present and sensitive enough to catch it. The splenic hit comes once, and then it's gone. If you miss it, you cannot retrieve it by thinking harder. The practice is cultivating stillness, presence, and trust in those first-moment flashes. You also need to act on splenic hits quickly — the window of opportunity is narrow because the spleen only speaks to what is immediately happening or about to happen.",
        "waiting_period": "There is no waiting period for Splenic Authority — the response is instantaneous. In fact, waiting or deliberating is counterproductive because the splenic voice has already spoken and moved on. If you wait too long, you enter mental territory and lose the splenic signal entirely. However, you may need to wait for something to respond TO — the spleen responds to life as it arises, not to abstract questions. Put yourself in situations and environments where your spleen has something to read.",
        "common_mistakes": [
            "Waiting for the spleen to repeat itself — It won't. The spleen speaks once. If you heard it and didn't act, you cannot summon it back. The lesson is to catch it the first time next time.",
            "Confusing fear with splenic warning — The spleen's survival signal is momentary, specific, and information-rich ('don't walk down that alley right now'). Fear is persistent, generalized, and mental ('what if something bad happens?'). Learn the difference.",
            "Overthinking the splenic hit — The spleen is pre-verbal. When you start analyzing 'why do I feel this way?' you've left the spleen and entered the mind. Act first; analyze later (or never).",
            "Letting others talk you out of your instinct — Splenic people often know something before they can explain it. Others may demand rationale. Don't let the demand for explanation override the knowing.",
            "Living in a noisy, overstimulating environment — The spleen needs relative quiet to be heard. Constant stimulation (social media, busy cities, packed schedules) drowns out the splenic whisper.",
        ],
        "types_have_it": "Splenic Authority is available to Manifestors and Projectors who have a defined Spleen and do NOT have a defined Solar Plexus or Sacral. For Manifestors, the splenic hit initiates action; for Projectors, the splenic hit often signals who and what is correct for them in the context of invitations. Generators and Manifesting Generators have Sacral Authority if their Solar Plexus is undefined; if their Spleen is also defined, the Sacral overrides it as the primary authority.",
        "faq": [
            ("What does a splenic hit actually feel like?", "It varies by person, but common descriptions include: a sudden knowing that arrives without reasoning, a physical sensation (goosebumps, a shiver, a subtle shift in the gut or chest), an olfactory flash (smelling something that isn't there), a taste in the mouth, an auditory whisper, or a visual flash. For many, it's simply a quiet but undeniable 'I just know.' It doesn't feel emotional or dramatic — it's neutral and clear."),
            ("How do I develop sensitivity to my splenic voice?", "Spend time in silence daily. Reduce stimulants (caffeine, social media, constant music). Practice being present in your body. When you get a splenic hit — even a small one about which route to drive or which food to order — act on it immediately and note the result. Trust builds through small confirmations."),
            ("What if I missed the splenic signal?", "If you missed it, you missed it. Don't chase it. The spleen will speak again about something else in the future. The self-recrimination ('why didn't I listen?!') is mental noise that further obscures the splenic channel. Forgive yourself and stay present for the next hit."),
            ("Can the spleen help with long-term decisions like career or relationships?", "The spleen operates in the now, not in the future. It can guide you moment to moment: 'talk to this person now,' 'don't take that meeting today,' 'take this route.' Over time, following these moment-to-moment splenic hits accumulates into the right long-term outcomes. The spleen doesn't do 5-year plans, but it gets you to the right people and places that shape your future correctly."),
            ("Is splenic authority the same as being 'psychic' or highly intuitive?", "Not exactly. Everyone has intuition, but Splenic Authority means your spleen is consistently defined and reliable as a decision-making mechanism. Your splenic intelligence is always online. Non-splenic authorities may experience intuition sporadically; for you, it's the primary operating system. Call it instinct rather than psychic ability — it's grounded in the body's ancient survival intelligence."),
        ],
        "experiments": [
            "The first flash journal — For one week, carry a small notebook. Every time you get a sudden knowing about something, write it down immediately, then note what happened when you followed it (or didn't).",
            "Silence practice — Commit to 15 minutes of complete silence daily. No phone, no music, no talking. Just sit and feel your body. This is like turning up the volume on your spleen.",
            "Act fast drill — The next three times you get a splenic hit about something small (which tea to order, which seat to take, whether to answer a call), act on it within 5 seconds. Notice the feeling of immediate alignment.",
            "Body scan check — When you get a splenic hit, scan your body: where do you feel it? Is it in your gut? Your heart area? Your skin? Mapping the sensation helps you recognize it faster next time.",
        ],
        "mechanics_detail": "The Spleen is the center of body consciousness — it governs the immune system, intuition, instinct, survival, and the sense of wellbeing in the present moment. It is the oldest awareness center evolutionarily, operating on frequency rather than logic. The defined Spleen processes information about safety, timing, and health in real-time without mental processing. It is connected to the lymphatic system and operates 24/7 as a body-level radar. The Spleen has three types of awareness channels: survival (fight/flight/freeze), taste (what is nourishing vs toxic), and intuition (pattern recognition below the level of conscious thought).",
        "signature_alignment": "When you follow your Splenic Authority, you experience a deep sense of safety and right-timing. Life flows with uncanny precision — you show up at the right place, meet the right person, avoid the wrong situation. Your immune system strengthens. When you override your spleen, you experience anxiety, health issues, and a pervasive sense of being 'out of sync' with life's timing. The body quite literally tells you through illness or exhaustion when you're ignoring the splenic wisdom.",
    },
    "ego": {
        "title": "Ego (Heart) Authority",
        "short_title": "Ego Authority",
        "slug": "ego",
        "center": "Heart (Ego)",
        "icon": "♛",
        "pct": "~1% of the population (rare)",
        "mechanic": "You have a defined Heart (Ego) center with a motor connection to the Throat — specifically, the channel 25-51 (the Channel of Initiation) or 21-45 (the Channel of Money). The Ego center is the motor of willpower, material resources, and self-worth. Ego Authority means your decisions come from a deep, embodied sense of what you have the will and resources to commit to. It operates on a simple principle: you agree to what you have the will for, and you say no to what you don't. The Ego doesn't negotiate, doesn't process emotionally, and doesn't work on instinct — it speaks from sheer willpower and self-knowledge.",
        "how_to_use": "When faced with a decision, check in with your will: 'Do I have the energy and heart for this?' The answer is not a feeling or an intuition but a simple assessment of your willpower reserves. The Ego speaks in commitments — when you commit, you deliver. When you overcommit, your will burns out. The practice is brutally honest self-assessment: What do I actually have the will to do? What do I genuinely want to invest my heart in? Your yes is sacred — you don't have unlimited willpower, and every yes that isn't fully yours depletes you. Learn to say no to protect your will.",
        "waiting_period": "The Ego Authority doesn't require a formal waiting period, but it benefits from a moment of honest self-inquiry: 'Do I really have the will for this? Am I saying yes from genuine desire or from obligation/pressure?' This check-in takes seconds or minutes, not days. The Ego knows immediately whether it has the will or not. However, major commitments (business partnerships, long-term promises) may benefit from sleeping on it — not because the Ego needs the wave, but because willpower clarity should be confirmed when you're rested and not depleted.",
        "common_mistakes": [
            "Saying yes from obligation rather than genuine will — You may feel social pressure to agree to things. Every obligated 'yes' drains willpower that could go toward your true commitments.",
            "Overcommitting — Because your willpower feels strong in the moment, you may take on too much. Remember: willpower is a finite resource. Pace yourself.",
            "Confusing ego willpower with emotional desire — You may WANT something emotionally, but not have the WILL to follow through. The Ego Authority distinction: want ≠ will.",
            "Not honoring financial/material limits — The Ego center governs resources including money. Committing willpower beyond your material capacity creates unsustainable pressure.",
            "Assuming your will is limitless — It's not. Even defined Ego centers have limits. Rest, recovery, and saying no are essential to maintaining a healthy Ego center.",
        ],
        "types_have_it": "Ego Authority is available to Manifestors with a defined Heart center and connecting channel to the Throat, who do NOT have a defined Solar Plexus, Sacral, or Spleen as their authority. It's one of the rarest authorities. Manifesting Generators can also technically have Ego Authority if their Sacral is undefined but this is extremely rare. The Ego must be connected to the Throat through channels 25-51 or 21-45 to function as an authority.",
        "faq": [
            ("How is Ego Authority different from just being 'strong-willed'?", "Everyone can be strong-willed. Ego Authority is mechanical: it means your defined Heart center, connected to the Throat, is your consistent, reliable decision-making mechanism. Your willpower isn't a personality trait — it's a biological constant. The difference is that your willpower regenerates reliably (unlike someone with an undefined Ego, whose willpower fluctuates based on who they're with)."),
            ("What happens when my willpower runs out?", "With a defined Ego center, your willpower regenerates — but it needs rest. When depleted, you'll feel heart-level exhaustion, not just physical tiredness. You may become cynical, feel undervalued, or lose the sense of purpose. Recovery requires actual rest from commitments and saying no to everything non-essential until your will recharges."),
            ("How do I say no without feeling guilty?", "The guilt you feel about saying no is conditioning, not your design. Your Ego Authority gives you the right — the mechanical right — to only commit your will to what is correct for you. Every no to what isn't yours is a yes to what is. Practice saying: 'That's not mine to carry.' You're not being selfish; you're being mechanically correct."),
            ("Can I use my Ego Authority for career and money decisions?", "Yes — this is where Ego Authority excels. The Heart center governs the material world, resources, and the will to compete and succeed. Your authority naturally guides you toward the work, partnerships, and financial commitments that align with your will. Trust your sense of 'I have the heart for this' in business contexts. It's more reliable than spreadsheets."),
            ("What's the relationship between Ego Authority and self-worth?", "The defined Ego center is the seat of self-worth that comes from within — not from achievements or external validation. When you're following your Ego Authority, your self-worth is naturally sustained. When you override it (saying yes when your will says no), your self-worth erodes because you're betraying your own heart. Ego Authority is fundamentally about honoring your own value."),
        ],
        "experiments": [
            "Willpower audit — For one week, before saying yes to any request, pause and ask: 'Do I have the actual will for this?' Notice how many things you've been agreeing to out of obligation.",
            "Track your commitments — List everything you're currently committed to. For each, ask: Is my heart truly in this? Cross off or renegotiate anything that doesn't have your full will behind it.",
            "Practice the sacred no — Say no to three things this week that you'd normally agree to out of politeness. Notice the relief in your chest/heart area. That's your Ego center thanking you.",
            "Material alignment check — Review your financial commitments. Does each one have your will behind it? If not, what needs to change? Your Ego Authority extends to how you allocate resources.",
        ],
        "mechanics_detail": "The Heart (Ego) center is the smallest of the four motors in the bodygraph, but it's intensely powerful. It governs willpower, ego, the material world, and the heart's desires. For Ego Authority specifically, the Heart must be connected to the Throat center via a defined channel — this is what gives the heart's willpower a voice. Without the Throat connection, the Ego has motor energy but no direct expression channel for decision-making. The two channels that create Ego Authority are: 25-51 (Channel of Initiation — the will to shock, initiate transformation, and compete) and 21-45 (Channel of Money — the will to manage resources and lead in the material realm).",
        "signature_alignment": "When you follow your Ego Authority, you feel powerful, grounded, and aligned. Your commitments feel effortless because your will is behind them. You attract resources and opportunities naturally because you're not leaking willpower into things that aren't yours. When you override your Ego Authority, you experience burnout, resentment, and a collapse of self-worth — the heart quite literally 'isn't in it.' Your body signals through fatigue, chest tightness, and a pervading sense of being undervalued or exploited.",
    },
    "self-projected": {
        "title": "Self-Projected (G Center) Authority",
        "short_title": "Self-Projected Authority",
        "slug": "self-projected",
        "center": "G Center (Identity)",
        "icon": "◎",
        "pct": "~1-2% of the population (rare, primarily Projectors)",
        "mechanic": "You have a defined G Center connected to the Throat through one of the G-to-Throat channels (7-31, 1-8, 13-33, 10-20), and you do not have a defined Solar Plexus, Sacral, or Spleen. Self-Projected Authority means your truth emerges when you hear yourself speak it aloud to another person. You don't know what you think or feel until you verbalize it. The G Center is your identity, direction, and sense of self — and it can only know itself through expression. Talking is not just communication for you; it's how you discover what is correct.",
        "how_to_use": "You must talk through decisions with trusted, non-judgmental listeners. These people don't need to advise you — they just need to listen, to give you space to hear yourself. The process: you speak, you hear your own words, and in hearing them, you know whether they are true. The right words will feel resonant, settled, and aligned — a sense of 'that's me.' The wrong words will feel hollow, off, or dissonant. The listener is a mirror; you are the one seeing your reflection. This is not about seeking others' opinions — it's about using their presence to access your own authority.",
        "waiting_period": "There is no fixed waiting period. The clarity comes in the moment of speaking — or shortly after, as you reflect on what you said. However, you may need multiple conversations over time for big decisions. The first conversation may reveal one layer; subsequent conversations reveal deeper layers. Trust the process: keep talking it through until you feel the 'click' of alignment. Also important: wait until you have the right listener. Talking to someone who interrupts, advises, judges, or dominates the conversation will not access your authority.",
        "common_mistakes": [
            "Talking to the wrong people — If your listener interrupts, criticizes, offers unsolicited advice, or makes the conversation about themselves, you won't hear yourself. Choose listeners carefully.",
            "Confusing others' approval with your own truth — Just because someone validates what you said doesn't make it correct. The measure is: did it feel true when it came out of your mouth?",
            "Isolating yourself during big decisions — Your authority requires another person. Trying to figure it out alone, in your head or journal, bypasses your decision-making mechanism entirely.",
            "Speaking too fast or performing — If you're performing for the listener (trying to sound smart, impressive, or certain), you won't hear your authentic voice. Speak slowly and let words emerge naturally.",
            "Not trusting what you heard yourself say — You may dismiss your own words after the conversation ('that was just talk'). But what came out spontaneously is your truth. Trust it.",
        ],
        "types_have_it": "Self-Projected Authority is almost exclusively a Projector authority — specifically, Projectors with a defined G Center connected to the Throat who have no defined Solar Plexus, Sacral, or Spleen. It's rare because most Projectors have Splenic Authority or Emotional Authority (if their Solar Plexus is defined). A very small number of Manifestors or Reflectors may technically have Self-Projected Authority, but this is extremely uncommon.",
        "faq": [
            ("Why do I need another person? Can't I just talk to myself?", "Talking to yourself helps, but it's not the same mechanism. The presence of another person — even someone silent — creates a relational field where the G Center can access itself differently. The G Center is inherently about direction and identity in relation to others. A mirror reflects; your journal doesn't reflect in the same way. You need the energetic presence of another human."),
            ("What kind of listener should I choose?", "Choose someone who is patient, non-judgmental, and comfortable with silence. Someone who doesn't jump in with solutions, who lets you ramble, who receives your words without needing to fix anything. It could be a friend, a coach, a therapist, or even a stranger in the right context. The key qualities: they listen more than they speak, and they don't make it about themselves."),
            ("What if I say something and immediately feel it's wrong?", "That's actually a success — you've accessed your authority. Hearing yourself say something 'wrong' gives you clarity about what IS right. The wrong words point toward the right ones. Stay with the conversation: 'Actually, that's not quite it. Let me try again.' Keep talking until the words land true."),
            ("Can I use voice notes or recording myself instead of a live person?", "Live interaction is optimal because the energetic presence matters. But voice notes to a trusted person (who will listen later) can work as a bridge — you're still speaking to someone, just asynchronously. Recording yourself with no intended listener is less effective because the relational field isn't there. The G Center needs another to orient toward."),
            ("Is Self-Projected Authority the same as 'processing out loud'?", "Similar, but with one key distinction: Self-Projected Authority is your DECISION-MAKING mechanism, not just a communication style. Many people process out loud. For you, it's not optional — it's how you discover what's correct. You literally cannot make aligned decisions in silence. This isn't a preference; it's a mechanical requirement."),
        ],
        "experiments": [
            "Identify your listeners — Make a list of 3-5 people who are excellent, non-judgmental listeners. Let them know: 'I sometimes need to talk through decisions. Can I call you when that happens? You don't need to advise — just listen.'",
            "Talk it out for one decision — Pick a medium-sized decision you're facing. Schedule a conversation with a trusted listener. Speak freely. Afterward, journal: 'What did I hear myself say that felt true?'",
            "Notice the difference — Next time you try to figure something out alone (in your head or journal), notice the frustration or circularity. Then talk it through with someone. Feel the release and clarity. This contrast builds trust in your authority.",
            "Practice with small decisions — Don't save this for life-changing choices. Talk through small things: 'Which restaurant should I pick?' 'Should I go to that event?' Build the muscle on low-stakes decisions.",
        ],
        "mechanics_detail": "The G Center is the seat of identity, direction, love, and the magnetic monopole — the force that holds your life together and pulls you toward your correct path. When the G Center is defined and connected to the Throat, your identity has a voice. Self-Projected Authority works because the act of speaking activates the G-to-Throat channel, allowing your directional intelligence to be heard — by you. The channels that enable Self-Projected Authority are: 7-31 (Channel of the Alpha — leadership and collective direction), 1-8 (Channel of Inspiration — creative self-expression), 13-33 (Channel of the Prodigal — witnessing and storytelling), and 10-20 (Channel of Awakening — living your truth in the now).",
        "signature_alignment": "When you follow Self-Projected Authority, you experience a deep sense of recognition — 'Ah, that's who I am.' Your life direction clarifies naturally. You feel seen and understood, and your relationships deepen because you're communicating authentically. When you don't follow it (isolating with decisions, letting others decide for you), you experience a loss of identity — a sense of being lost, directionless, or not knowing who you really are. This is your not-self signal: when you feel confused about yourself, find someone to talk to.",
    },
    "environmental": {
        "title": "Environmental (Mental) Authority",
        "short_title": "Environmental Authority",
        "slug": "environmental",
        "center": "Mind/Ajna (indirectly — through environment)",
        "icon": "◈",
        "pct": "~2-3% of the population (primarily Projectors)",
        "mechanic": "Environmental (Mental) Authority is unique: it operates through your surroundings, not through any internal motor or awareness center. You have no defined Solar Plexus, Sacral, Spleen, or Heart (for Manifestors), and your G Center is not connected to the Throat. This means you don't have an internal decision-making mechanism in the traditional sense. Instead, your authority is in the environment: you make correct decisions by being in the right place, with the right people, and then observing how your mind processes things differently in different environments. Your clarity comes from external cues and environmental resonance, not from internal signals.",
        "how_to_use": "When facing a decision, don't try to figure it out internally. Instead, change your environment and observe how your thinking shifts. Go to different places: a quiet café, a park, a library, a friend's living room, a walk through the city. Talk to different people. Notice: in which environment does the decision feel clearer? Where does your mind settle? Where do solutions emerge naturally? The right environment doesn't tell you the answer — it creates the conditions where your mental process can reach clarity. You may also notice that certain environments make you feel expansive (correct) while others make you feel contracted (incorrect) — these body-level responses to place are your authority speaking.",
        "waiting_period": "Environmental Authority requires exploration time — not emotional waiting, but the time it takes to experience different environments and recognize which one produces clarity. For small decisions, this might mean walking to a different room in your house. For major decisions, it could mean visiting different cities, offices, or communities. Give yourself permission to 'try on' different contexts. The waiting period isn't for an internal process to complete; it's for you to sample enough environments to find the one where the decision resolves.",
        "common_mistakes": [
            "Trying to 'think your way' to clarity in a single, stagnant environment — If you're stuck in the same room staring at the same wall, your mind will loop. Move your body to move your mind.",
            "Ignoring body-level responses to environments — If you walk into a space and your body tightens, that's information. If another space makes you exhale and relax, that's also information. Pay attention.",
            "Letting others choose your environment for you — Someone else's perfect workspace or decision-making ritual may be wrong for you. You must discover your own resonant environments.",
            "Confusing environmental preference with environmental authority — You might prefer being at home, but your best clarity might come in a bustling coffee shop. Experiment beyond comfort zones.",
            "Rushing — Environmental Authority can't be rushed. The process of sampling environments takes the time it takes. Pressure to decide quickly (from yourself or others) short-circuits your authority.",
        ],
        "types_have_it": "Environmental Authority is primarily a Projector authority — specifically, Projectors without a defined Solar Plexus, Sacral, Spleen, or G-to-Throat connection. These are sometimes called 'Mental Projectors.' A small number of Manifestors may also have Environmental Authority if they lack all other authority definitions. Reflectors technically have their own distinct authority (Lunar), not Environmental, even though environment is also critical for them.",
        "faq": [
            ("How is Environmental Authority different from just liking certain places?", "Everyone has environmental preferences. Environmental Authority is mechanical: it means your correct decision-making process IS the process of moving through environments and reading their effect on your clarity. You don't just prefer certain places — your clarity literally depends on being in the right environment. Without environmental movement, you cannot access correct decisions."),
            ("What if I can't physically change my environment?", "Even micro-changes matter: move from the desk to the couch, from indoors to outdoors, from silence to music (or vice versa). Talk to someone in a different context. Change the lighting. Walk around the block. The principle is shifting your context. If you're truly stuck (hospital, prison, caregiving), find ways to alter one environmental variable at a time."),
            ("How do I know which environment is 'right' for a particular decision?", "Your body and mind will tell you. In the right environment, your thinking clarifies, your body relaxes, and the decision feels simpler. You may experience a sudden insight, a release of tension, or a natural resolution. Sample 2-3 different environments for each significant decision. The contrast will reveal which one serves the decision."),
            ("Is Environmental Authority the same as needing variety or being indecisive?", "No. This isn't about being flaky or restless. It's about recognizing that your decision-making mechanism is relational to place. Just as Emotional Authority needs time and Sacral Authority needs response, you need environmental sampling. It's not a flaw — it's your design operating correctly."),
            ("Can I combine Environmental Authority with talking things through like Self-Projected Authority?", "Yes — many people with Environmental Authority find that talking things through in different environments is doubly clarifying. The combination of the right listener AND the right place can be powerful. However, don't confuse the two. Your primary authority is environmental. If talking helps, it's a supplement, not a replacement."),
        ],
        "experiments": [
            "Environment sampling — For your next decision, visit three different places and sit with the decision in each. Journal about how your perspective shifts. Which environment produced the clearest thinking?",
            "Body-environment scan — Enter a new space and pause. Notice what happens in your body: shoulders, jaw, breath, gut. Tightness or expansion? This is your environmental radar. Practice reading it daily.",
            "Create your clarity spaces — Identify 2-3 environments where you consistently think well. A specific café, a park bench, a library corner. Make accessing these spaces part of your decision-making practice.",
            "Change one thing — When stuck, change one environmental variable at a time: stand instead of sit, go outside, put on music, turn off music, dim the lights. Notice what shifts your mental state.",
        ],
        "mechanics_detail": "Environmental Authority arises from the absence of defined internal authority centers (no Solar Plexus, Sacral, Spleen, or Ego-Throat connection). In the bodygraph, this means the decision-making intelligence is externalized — it lives in the field between you and your environment. The mind is not the enemy here (as it can be for other authorities); it's your instrument, but it requires the right acoustic (environment) to play in tune. Your defined centers (often the Ajna, Throat, or Head) process information, but the CLARITY comes from the resonance between your mind and the environment. Think of it as needing the right signal-to-noise ratio: the right environment reduces noise so your mental signal becomes clear.",
        "signature_alignment": "When you follow Environmental Authority, you experience a sense of being in the right place at the right time. Your mind feels clear, creative, and decisive. You recognize yourself as someone who 'processes through context' rather than someone who is indecisive. When you ignore this authority — staying in stagnant or wrong environments, forcing decisions without movement — you experience mental fog, indecision, anxiety, and a pervasive sense of being stuck. Your not-self signal is mental confusion that doesn't resolve no matter how much you think about it.",
    },
    "lunar": {
        "title": "Lunar (Reflector) Authority",
        "short_title": "Lunar Authority",
        "slug": "lunar",
        "center": "None (Reflector — all centers undefined)",
        "icon": "☽",
        "pct": "~1% of the population (Reflectors exclusively)",
        "mechanic": "Lunar Authority is unique to Reflectors — the only type with no defined centers at all. Without a consistent internal decision-making mechanism, the Reflector's authority is the transit of the Moon through the 64 gates of the bodygraph over approximately 28.5 days (a full lunar cycle). As the Moon moves, it temporarily defines different centers in the Reflector's chart, creating different 'flavors' of experience and perspective. By tracking how a decision feels across the lunar cycle, the Reflector samples every possible perspective on that decision, and the clarity that emerges is absolute — because it's been informed by all angles.",
        "how_to_use": "When a significant decision arises, you don't decide immediately. You hold the question and notice how you feel about it as the Moon moves through the cycle — day by day, week by week. Some days the decision will feel clearly right; other days clearly wrong; other days you'll feel entirely differently about it. The practice is to observe without attaching to any single day's perspective. After approximately 28 days, you will have sampled the full spectrum, and a stable, integrated knowing will emerge. This is not your opinion — it's the wisdom of having seen the decision from every angle the lunar cycle offers. This takes patience, but the clarity is unshakable.",
        "waiting_period": "A full lunar cycle — approximately 28.5 days. This is non-negotiable for major life decisions. For smaller decisions, you may not need the full cycle — a week may suffice — but the principle remains: don't decide from a single day's perspective. Reflectors who consistently make fast decisions eventually experience the pain of discovering that 'what felt right on Tuesday' was completely wrong by the following week. The lunar cycle is your protection. Use it.",
        "common_mistakes": [
            "Making decisions from a single day's clarity — Tuesday-you feels 100% certain. But Tuesday-you is only sampling one gate's worth of lunar definition. By Thursday, you may feel completely opposite. Wednesday's certainty is not the full picture.",
            "Letting others pressure you into faster decisions — Almost nobody else has a 28-day decision cycle. They will find your pace unbearably slow and may push you. Holding your boundary here is essential to your wellbeing.",
            "Confusing the lunar cycle with procrastination — You're not avoiding the decision; you're completing the process. Procrastination has an energy of avoidance. Lunar Authority has an energy of patient, deliberate observation.",
            "Not tracking your experience across the cycle — If you don't journal or note how you feel day to day, you lose the data. The lunar cycle only works if you pay attention to the moving perspective.",
            "Isolating during the lunar cycle — Reflectors sample the energy of people around them. Being around the same people or isolating completely limits the data you receive. Variety of human contact enriches the lunar process.",
        ],
        "types_have_it": "Lunar Authority is exclusive to Reflectors. By definition, all Reflectors have Lunar Authority — it's the only authority available because Reflectors have no defined centers that could provide a different authority. If you are a Reflector, you have Lunar Authority. Period. No exceptions.",
        "faq": [
            ("Do I really have to wait 28 days for every decision?", "For major life decisions (moving, career changes, relationship commitments, big purchases): yes, the full cycle. For medium decisions (saying yes to a project, planning a trip): at least a week. For small daily decisions (what to eat, which route to take): you can respond in the moment — but know that even daily preferences may shift across the cycle."),
            ("What if I can't wait 28 days because of an external deadline?", "For true external deadlines, you do what you must — but know that you're making the decision without your full authority. When possible, negotiate for more time: 'I need a month to feel into this. Can we revisit then?' Many deadlines are more flexible than they appear. For decisions others impose on you, ask: is the urgency real or manufactured?"),
            ("How do I track my lunar cycle effectively?", "Keep a simple journal. Each day, write the date and a one-sentence check-in on the decision: 'Today: feels like a clear yes.' 'Today: uncertain, leaning no.' 'Today: completely different perspective — seeing the risks.' At the end of the cycle, review your journal. The pattern across 28 entries reveals the integrated truth."),
            ("What if the lunar cycle ends and I still don't feel clear?", "Sometimes one cycle isn't enough for extremely complex decisions — give yourself a second cycle. But also check: are you truly uncertain, or are you afraid of the answer? Lunar clarity is quiet and steady. It doesn't arrive with fanfare. If you're waiting for a dramatic revelation, you may have already received your clarity and dismissed it."),
            ("Does the lunar cycle mean my life moves slowly?", "Not slowly — rhythmically. Reflectors who embrace the lunar cycle find that their lives move with surprising precision. They avoid big mistakes that others (who decide quickly) stumble into. They may appear to move slowly from the outside, but internally they're running a sophisticated, complete decision process that produces remarkably accurate results."),
        ],
        "experiments": [
            "Start a lunar journal — Pick one decision you're holding and track it daily for a full lunar cycle. One sentence per day. At the end, read back through and look for the pattern. This single experiment can transform your relationship with your authority.",
            "Map your cycle — Download a lunar calendar app. Start noticing which days of the lunar cycle you tend to feel expansive/clear vs contracted/confused. Over a few months, you'll identify your personal rhythm within the cycle.",
            "Tell people your timeline — Next time someone asks for a decision, say: 'I move on a lunar cycle — I'll get back to you in about 28 days.' Notice who respects this and who pushes. The pushers are revealing that they don't respect your design.",
            "Sample different environments across the cycle — Since you're sampling lunar definition, also sample different physical environments and social circles. Spend time in nature, in the city, with friends, alone. The richer the sampling, the richer the clarity.",
        ],
        "mechanics_detail": "The Reflector is the only type with zero defined centers. This means the Reflector has no consistent internal energy to draw on for decision-making and this is by design. The Reflector authority center is the entire transit field, with the Moon as the primary timer. The Moon takes approximately 28.5 days to transit all 64 gates, creating temporary definitions. By waiting the full cycle, the Reflector integrates all lenses into a holographic understanding. Authority and Strategy are perfectly aligned.",
        "signature_alignment": "When you follow Lunar Authority, you experience Surprise — the signature of the Reflector. Surprise is the delight of discovering what's really correct after the cycle completes — often something you would never have chosen from any single day's perspective. Your life becomes an unfolding revelation rather than a forced march. When you ignore Lunar Authority, you experience Disappointment — the not-self theme. Disappointment is the feeling of having committed to something that the full picture would have revealed as wrong. The lunar cycle is your protection against disappointment.",
    },
}

# ── CSS shared across all authority pages (same as profiles) ──
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
  .hero .authority-tag {
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

  .mistake-list li {
    padding: 10px 0;
    line-height: 1.65;
  }
  .mistake-list li strong {
    color: var(--gold-light);
  }

  .experiment-list li {
    padding: 12px 0 !important;
  }
  .experiment-list li strong {
    color: var(--gold-light);
  }

  .related-authorities {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 40px 36px;
    margin-bottom: 48px;
  }
  .related-authorities h2 {
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

  .authority-index-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 60px;
  }
  .authority-index-card {
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
  .authority-index-card:hover {
    border-color: rgba(201,168,76,0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(201,168,76,0.08);
  }
  .authority-index-icon {
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
  .authority-index-card h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--white);
    letter-spacing: -0.01em;
  }
  .authority-index-desc {
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.5;
  }
  .authority-index-meta {
    display: flex;
    gap: 16px;
    font-size: 0.78rem;
    color: var(--gold);
    font-weight: 500;
  }

  @media (max-width: 768px) {
    .nav-links { gap: 12px; }
    .nav-links a { font-size: 0.78rem; }
    .content, .related-authorities { padding: 28px 20px; }
    .footer-inner { flex-direction: column; text-align: center; }
  }
"""


def authority_page_html(data):
    """Generate complete HTML for a single authority page."""
    slug = data["slug"]
    title = data["title"]
    short_title = data["short_title"]
    icon = data["icon"]
    center = data["center"]
    pct = data["pct"]

    page_title = f"Human Design {short_title} — {center} | Complete Guide"
    meta_desc = f"Complete guide to {short_title} in Human Design: how the {center} works mechanically, how to use your {short_title} for decisions, the waiting period, common mistakes, practical experiments, which Types have it, and FAQs."
    og_desc = f"Deep dive into {short_title} in Human Design. Learn how your {center} operates as your inner authority, the waiting period, common mistakes, which Types share this authority, and practical daily experiments."

    # Build mistake list
    mistakes_html = ""
    for m in data["common_mistakes"]:
        parts = m.split(" — ", 1) if " — " in m else (m, "")
        mistakes_html += f'      <li><strong>{parts[0]}</strong>{" — " + parts[1] if len(parts) > 1 else ""}</li>\n'

    # Build experiments list
    exp_html = ""
    for exp in data["experiments"]:
        parts = exp.split(" — ", 1) if " — " in exp else (exp, "")
        exp_html += f'      <li><strong>{parts[0]}</strong>{" — " + parts[1] if len(parts) > 1 else ""}</li>\n'

    # Build FAQ HTML
    faq_html = ""
    for q, a in data["faq"]:
        faq_html += f"""    <div class="faq-item">
      <h3>{q}</h3>
      <p>{a}</p>
    </div>
"""

    # Build related authorities
    related_html = ""
    for a_slug, a_data in AUTHORITIES.items():
        if a_slug == slug:
            continue
        related_html += f'      <a href="{a_slug}.html" class="related-chip">{a_data["icon"]} {a_data["short_title"]}</a>\n'
    related_html += f'      <a href="index.html" class="related-chip">All 7 Authorities →</a>\n'

    # Mechanics section heading
    mechanics_section = f"""    <h3>How the {center} Works Mechanically</h3>
    <p>{data['mechanics_detail']}</p>"""

    # Signature section
    signature_section = f"""    <h3>Living in Alignment: The Signature</h3>
    <p>{data['signature_alignment']}</p>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title} | Human Design Engine</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="Human Design, {short_title}, {center}, inner authority, Human Design authority types, how {slug} authority works, Human Design decision making, Human Design Engine">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://humandesignengine.com/human-design/authorities/{slug}/">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://humandesignengine.com/human-design/authorities/{slug}/">
<meta property="og:site_name" content="Human Design Engine">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page_title}">
<meta name="twitter:description" content="{og_desc}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{short_title} in Human Design: Complete Guide",
  "description": "{meta_desc}",
  "author": {{ "@type": "Organization", "name": "Human Design Engine" }},
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }},
  "mainEntityOfPage": {{ "@type": "WebPage", "@id": "https://humandesignengine.com/human-design/authorities/{slug}/" }}
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
      <a href="/human-design/profiles/">Profiles</a>
      <a href="/human-design/authorities/">Authorities</a>
      <a href="/human-design/centers/">Centers</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/gates/">Gates</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    <a href="/human-design/authorities/">Authorities</a> <span>›</span>
    {short_title}
  </div>

  <section class="hero">
    <div class="hero-icon">{icon}</div>
    <h1>{short_title}</h1>
    <p class="subtitle">Your decision-making authority is located in your <span class="highlight">{center}</span>. Learn how it works, how to use it, and why trusting it is the most important skill you can develop in Human Design.</p>
    <div class="authority-tag">{pct}</div>
  </section>

  <div class="info-grid">
    <div class="info-card">
      <div class="label">Authority Center</div>
      <div class="value">{center}</div>
    </div>
    <div class="info-card">
      <div class="label">Waiting Period</div>
      <div class="value">{'None — immediate response in the now' if data['waiting_period'].startswith('There is no waiting') else data['waiting_period'][:70]}...</div>
    </div>
    <div class="info-card">
      <div class="label">Population</div>
      <div class="value">{pct.split('(')[0].strip() if '(' in pct else pct}</div>
    </div>
    <div class="info-card">
      <div class="label">Types With This Authority</div>
      <div class="value">{data['types_have_it'].split('.')[0] if '.' in data['types_have_it'] else data['types_have_it'][:80]}</div>
    </div>
  </div>

  <article class="content">
    <h2>What Is {short_title}?</h2>
    <p>{data['mechanic']}</p>

{mechanics_section}

    <h2>How to Use Your {short_title} for Decisions</h2>
    <p>{data['how_to_use']}</p>

    <h2>The Waiting Period</h2>
    <p>{data['waiting_period']}</p>

    <h2>Common Mistakes</h2>
    <p>Even when you understand your authority intellectually, actually living it requires unlearning deeply conditioned patterns. Here are the most common mistakes people with {short_title} make — and why they derail your decision-making.</p>
    <ul class="mistake-list">
{mistakes_html}    </ul>

    <h2>Which Types Have {short_title}?</h2>
    <p>{data['types_have_it']}</p>

    <h2>Practical Experiments</h2>
    <p>Human Design is not a belief system — it's an experiment. These practices are designed to help you discover firsthand how your {short_title} operates. Approach them with curiosity, not expectation.</p>
    <ul class="experiment-list">
{exp_html}    </ul>

{signature_section}
  </article>

  <section class="related-authorities">
    <h2>Explore All 7 Authorities</h2>
    <p style="color:var(--text-secondary);margin-bottom:20px;">Each Human Design Authority is a distinct decision-making mechanism. Understanding all seven helps you see how your authority fits into the full spectrum — and how to interact with people who have different authorities.</p>
    <div class="related-grid">
{related_html}    </div>
  </section>

  <section class="faq">
    <h2>Frequently Asked Questions — {short_title}</h2>
{faq_html}  </section>

  <section class="cta-section">
    <h2>Discover Your Unique Authority</h2>
    <p>Your Inner Authority is revealed in your full Human Design chart — along with your Type, Profile, defined Centers, Channels, Gates, and Incarnation Cross. Get your personalized 70+ page report and learn exactly how your authority operates in your unique design.</p>
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
      <a href="/human-design/authorities/">Authorities</a>
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
    """Generate the authorities index page."""
    cards = ""
    # Order for index display
    index_order = ["emotional", "sacral", "splenic", "ego", "self-projected", "environmental", "lunar"]
    for slug in index_order:
        data = AUTHORITIES[slug]
        short_wait = data['waiting_period'].split('.')[0] if '.' in data['waiting_period'] else data['waiting_period'][:80]
        cards += f"""    <a href="{slug}.html" class="authority-index-card">
      <div class="authority-index-icon">{data['icon']}</div>
      <h3>{data['short_title']}</h3>
      <p class="authority-index-desc">Center: {data['center']}. {short_wait}.</p>
      <div class="authority-index-meta">
        <span>{data['pct'].split('(')[0].strip() if '(' in data['pct'] else data['pct']}</span>
      </div>
    </a>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 7 Human Design Authorities — Complete Guide to Inner Authority | Human Design Engine</title>
<meta name="description" content="Explore all 7 Human Design authorities: Emotional, Sacral, Splenic, Ego, Self-Projected, Environmental, and Lunar. Learn how each inner authority works, which Types have them, waiting periods, and how to use your authority for correct decision-making.">
<meta name="keywords" content="Human Design authorities, inner authority, Emotional Authority, Sacral Authority, Splenic Authority, Ego Authority, Self-Projected Authority, Environmental Authority, Lunar Authority, Human Design decision making, Human Design Engine">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://humandesignengine.com/human-design/authorities/">
<meta property="og:title" content="The 7 Human Design Authorities — Complete Guide | Human Design Engine">
<meta property="og:description" content="Complete reference for all 7 Human Design inner authorities: Emotional, Sacral, Splenic, Ego, Self-Projected, Environmental, and Lunar. Learn how each operates and which Types carry them.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://humandesignengine.com/human-design/authorities/">
<meta property="og:site_name" content="Human Design Engine">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="The 7 Human Design Authorities — Complete Guide">
<meta name="twitter:description" content="Complete reference for all 7 Human Design inner authorities with waiting periods, center mechanics, and practical experiments for each authority.">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "The 7 Human Design Authorities",
  "description": "A complete guide to all 7 Human Design inner authorities: Emotional (Solar Plexus), Sacral, Splenic (Spleen), Ego (Heart), Self-Projected (G Center), Environmental (Mental), and Lunar (Reflector). Each authority is a distinct decision-making mechanism determined by which centers are defined in your chart.",
  "url": "https://humandesignengine.com/human-design/authorities/",
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
      <a href="/human-design/profiles/">Profiles</a>
      <a href="/human-design/authorities/">Authorities</a>
      <a href="/human-design/centers/">Centers</a>
      <a href="/human-design/channels/">Channels</a>
      <a href="/human-design/gates/">Gates</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    Authorities
  </div>

  <div class="page-header">
    <h1>The 7 Authorities of Human Design</h1>
    <p>Your Inner Authority is your personal decision-making mechanism — the most reliable compass you have for navigating life correctly. It's not a philosophy or a preference. It's mechanical: determined by which centers are defined in your bodygraph and how they connect. Learning to trust your authority is the single most transformative practice in Human Design.</p>
    <p style="margin-top:16px;">The seven authorities are: <span class="highlight">Emotional (Solar Plexus), Sacral, Splenic (Spleen), Ego (Heart), Self-Projected (G Center), Environmental (Mental), and Lunar (Reflector)</span>. Each has its own center, rhythm, waiting period, and way of speaking. Discover yours below.</p>
  </div>

  <div class="authority-index-grid">
{cards}  </div>

  <article class="content">
    <h2>Why Your Authority Matters More Than Your Strategy</h2>
    <p>Your Strategy (To Respond, To Inform, Wait for the Invitation, Wait a Lunar Cycle) tells you <span class="highlight">how to engage with life</span>. Your Authority tells you <span class="highlight">what is correct for you</span> — it's the internal 'yes' or 'no' that your Strategy relies on. Without following your Authority, your Strategy is blind.</p>

    <p>Think of it this way: your Strategy is the vehicle, and your Authority is the navigation system. You can be driving the right vehicle (following your Strategy) but still make wrong turns if you're not reading the navigation system (ignoring your Authority). The two must work together.</p>

    <h3>How Your Authority Is Determined</h3>
    <p>Your Inner Authority is not chosen — it's revealed in your chart. The hierarchy is:</p>
    <ul>
      <li><strong>If your Solar Plexus is defined</strong> → Emotional Authority (regardless of other definitions)</li>
      <li><strong>If your Solar Plexus is undefined but your Sacral is defined</strong> → Sacral Authority (Generators and Manifesting Generators)</li>
      <li><strong>If Solar Plexus and Sacral are undefined but Spleen is defined</strong> → Splenic Authority (Manifestors & Projectors)</li>
      <li><strong>If Solar Plexus, Sacral, and Spleen are undefined but Heart is connected to Throat</strong> → Ego Authority (rare, Manifestors)</li>
      <li><strong>If G Center is connected to Throat with no motor authorities</strong> → Self-Projected Authority (Projectors)</li>
      <li><strong>If no internal authority centers are defined but Ajna/Head are</strong> → Environmental (Mental) Authority (Projectors)</li>
      <li><strong>If no centers are defined at all</strong> → Lunar Authority (Reflectors exclusively)</li>
    </ul>

    <h2>The Authority Spectrum: Internal vs. External</h2>
    <p>Authorities exist on a spectrum from fastest to slowest. <span class="highlight">Splenic Authority</span> is the fastest — an instantaneous, one-time whisper. <span class="highlight">Sacral Authority</span> is also immediate — a gut response in the now. <span class="highlight">Ego Authority</span> requires a moment of honest self-assessment. <span class="highlight">Self-Projected Authority</span> requires finding a listener and talking it through. <span class="highlight">Environmental Authority</span> requires sampling different places. <span class="highlight">Emotional Authority</span> requires riding the emotional wave — hours to days. <span class="highlight">Lunar Authority</span> is the slowest — a full 28.5-day lunar cycle.</p>

    <p>There is no 'best' authority. Each is perfectly designed for the being who carries it. The only problem is when you try to use someone else's authority — making fast gut decisions when you're Emotional, or waiting for clarity when your Sacral already answered.</p>

    <h3>Authority in Relationships</h3>
    <p>One of the most practical applications of understanding authorities is in relationships. When you know your partner's authority is Emotional and yours is Sacral, you understand that they <em>need time</em> while you need <em>in-the-moment response</em>. You stop pressuring them for immediate answers. You stop second-guessing yourself when your gut says yes but they haven't reached clarity yet. Respecting different authorities is one of the most profound acts of love in Human Design.</p>
  </article>

  <section class="cta-section">
    <h2>Find Your Inner Authority</h2>
    <p>Your exact authority is determined by the unique configuration of defined centers in your chart. Generate your full personalized 70+ page Human Design report and discover not just your Authority but your complete blueprint: Type, Profile, Centers, Channels, Gates, and Incarnation Cross.</p>
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
      <a href="/human-design/authorities/">Authorities</a>
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

    # Generate individual authority pages
    for slug, data in AUTHORITIES.items():
        filename = f"{slug}.html"
        filepath = os.path.join(OUT_DIR, filename)
        html = authority_page_html(data)
        with open(filepath, "w") as f:
            f.write(html)
        print(f"Wrote {filename} ({len(html)} bytes, ~{html.count(chr(10))} lines)")

    print("\nDone. Generated 1 index + 7 authority pages.")
