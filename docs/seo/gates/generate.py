#!/usr/bin/env python3
"""
Generate 64 Human Design gate SEO pages plus an index page.
Uses real HD data for gate names, I-Ching hexagrams, circuit groups,
meanings, and channel participation.
"""

import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Complete gate database ──────────────────────────────────────────────
# Format: (number, name, hexagram_name, hexagram_number, circuit_group, meaning_paragraph, channels_list)
GATES = [
    (1, "Self-Expression", "The Creative", 1, "Individual Knowing",
     "Gate 1 is the energy of creative self-expression. It carries the frequency of the artist, the innovator, and the individual who must bring something new into form. When this gate is defined, there is a natural urge to create — not for an audience, but because authentic expression demands it. This is the gate of divine inspiration made manifest. In its high expression, it produces work that is original, spontaneous, and alive. In its shadow, it can become chaotic, self-absorbed, or creatively blocked.",
     ["1-8 (The Channel of Inspiration)"]),
    (2, "Direction of Self", "The Receptive", 2, "Individual Centering",
     "Gate 2 is the energy of receptivity and direction. It is the grounding point for higher knowing — the ability to simply know the right direction without needing to understand why. People with this gate defined have an innate sense of where to go and when to move. This is not ambition or drive; it is attunement to a deeper navigational intelligence. The high expression is graceful, intuitive movement through life. The shadow is aimlessness or rigid attachment to a fixed path.",
     ["2-14 (The Channel of the Beat)"]),
    (3, "Ordering", "Difficulty at the Beginning", 3, "Individual Knowing",
     "Gate 3 is the energy of innovation through difficulty. It is the gate of mutation — where new things enter the world through struggle and perseverance. This energy knows that beginnings are inherently chaotic and that order emerges through engagement with difficulty. Those with Gate 3 carry a unique capacity to pioneer new forms. The challenge is learning to trust the process of difficulty rather than resisting it.",
     ["3-60 (The Channel of Mutation)"]),
    (4, "Formulization", "Youthful Folly", 4, "Collective Logic",
     "Gate 4 is the energy of answering and mental formulation. It represents the logical mind's drive to find answers, solve problems, and formulate coherent explanations. This gate brings the gift of deduction — the ability to piece together understanding from fragments. When aligned, it produces elegant solutions. In the shadow, it can become anxiously obsessive about having the right answer and may produce rigid, formulaic thinking that misses the living truth.",
     ["4-63 (The Channel of Logic)"]),
    (5, "Fixed Patterns", "Waiting", 5, "Collective Logic",
     "Gate 5 is the energy of waiting for the right timing. It carries the rhythm of natural cycles and the wisdom to know that some things cannot be rushed. This gate understands pattern and repetition — the seasonal, cyclical nature of life. Those with this gate activated have a deep attunement to when something is ready to emerge. Their gift is patience and the ability to hold steady. The shadow is stagnation or crippling inertia.",
     ["5-15 (The Channel of Rhythm)"]),
    (6, "Friction", "Conflict", 6, "Tribal Defense",
     "Gate 6 is the energy of friction and emotional boundary-setting. It governs the creation and regulation of intimacy through emotional clarity. This gate determines who gets close and when — it is the gatekeeper of the emotional body. When healthy, it produces clear, honest emotional boundaries that create deep trust. In its shadow, it can manifest as emotional manipulation, walls that shut everyone out, or conflict for its own sake.",
     ["6-59 (The Channel of Mating)"]),
    (7, "The Role of the Self in Interaction", "The Army", 7, "Collective Logic",
     "Gate 7 is the energy of leadership through service. It represents the self in its relationship with the collective — the capacity to lead by example and to wield influence not for personal power, but for the greater good. This gate understands that true leadership is a responsibility, not a privilege. Those with Gate 7 defined often find themselves in positions of authority naturally. The shadow is authoritarianism or abdication of responsibility.",
     [""]),
    (8, "Contribution", "Holding Together", 8, "Individual Knowing",
     "Gate 8 is the energy of contribution through authentic example. It is the gate of the role model — one who contributes not by instructing but by being. This frequency knows that the most powerful teaching is demonstration. When Gate 8 is defined, others naturally look to this person as an example of how to live authentically. The high expression is humble, embodied wisdom. The shadow is self-consciousness or performing for approval.",
     ["1-8 (The Channel of Inspiration)"]),
    (9, "Focus", "The Taming Power of the Small", 9, "Collective Logic",
     "Gate 9 is the energy of sustained focus and detailed attention. It is the capacity to commit to a single task or inquiry with unwavering concentration until it is complete. This is the gate of the specialist and the scholar — those who go deep rather than wide. The gift is mastery through dedication. The shadow is obsessive myopia — becoming so focused on details that you lose sight of the bigger picture or fail to connect with others.",
     ["9-52 (The Channel of Concentration)"]),
    (10, "Behavior of the Self", "Treading", 10, "Individual Centering",
     "Gate 10 is the energy of self-love and authentic behavior. It is the gate through which the self expresses its unique way of being in the world — not adapting to others, but standing in its own truth. This is the foundation of self-empowerment and represents the ability to love oneself unconditionally. The gift is authentic presence that gives others permission to also be themselves. The shadow is self-rejection masked as arrogance or people-pleasing.",
     ["10-20 (The Channel of Awakening)", "10-34 (The Channel of Exploration)", "10-57 (The Channel of Perfected Form)"]),
    (11, "Ideas", "Peace", 11, "Collective Sensing",
     "Gate 11 is the energy of ideas, imagination, and mental stimulation. It is the gate of the storyteller and the visionary — one who receives and transmits ideas for the collective. This is not logical analysis but rather the flow of inspiration through the abstract mind. Those with Gate 11 defined experience a constant stream of mental imagery and concepts. The gift is creativity and narrative intelligence. The shadow is mental restlessness or getting lost in fantasy.",
     ["11-56 (The Channel of Curiosity)"]),
    (12, "Caution", "Standstill", 12, "Individual Centering",
     "Gate 12 is the energy of caution and emotional articulation. It is the gate of the poet and the artist who transmutes deep emotional experience into language, sound, or form. This gate knows when to speak, when to be still, and how to wait for the right moment of expression. The gift is the articulation of feeling that touches others deeply. The shadow is emotional melodrama or complete withdrawal into silence.",
     ["12-22 (The Channel of Openness)"]),
    (13, "The Listener", "Fellowship with Men", 13, "Collective Sensing",
     "Gate 13 is the energy of the listener — the one who holds space for others' stories, secrets, and confessions. This gate carries the memory of human experience and the capacity to receive and hold what others share. It is deeply empathic and attuned to the emotional and narrative undercurrents of any interaction. The gift is profound listening that makes others feel truly heard. The shadow is emotional burden-taking or voyeuristic listening.",
     ["13-33 (The Channel of the Prodigal)"]),
    (14, "Power Skills", "Possession in Great Measure", 14, "Individual Centering",
     "Gate 14 is the energy of empowered skill and resource abundance. It represents the fuel that drives the individual's unique direction — the ability to generate and direct resources (material, energetic, or creative) in service of one's path. This is the gate of the entrepreneur who creates value through their unique gifts. When aligned, it produces sustainable prosperity. The shadow is addiction to work, burnout, or hoarding resources.",
     ["2-14 (The Channel of the Beat)"]),
    (15, "Extremes", "Modesty", 15, "Collective Logic",
     "Gate 15 is the energy of extremes in rhythm and behavior. It carries the full spectrum of human experience — the capacity to move between high and low, fast and slow, active and restful, without losing coherence. This gate teaches that life has natural extremes and that moderation emerges from embracing the full range. The gift is a profound love of life in all its variety. The shadow is dangerous extremes or erratic, unsustainable patterns.",
     ["5-15 (The Channel of Rhythm)"]),
    (16, "Skills", "Enthusiasm", 16, "Collective Logic",
     "Gate 16 is the energy of enthusiasm for skills and mastery. It is the gate of the performer, the craftsman, and anyone who derives joy from doing something well. This is not about natural talent but about the pleasure of practice, repetition, and refinement. Those with this gate have a contagious enthusiasm that inspires others to develop their own skills. The shadow is superficial dabbling or performance without substance.",
     ["16-48 (The Channel of Talent)"]),
    (17, "Opinions", "Following", 17, "Collective Logic",
     "Gate 17 is the energy of opinion formation and intellectual structuring. It represents the logical mind's need to build mental frameworks, formulate opinions, and organize information into coherent systems. This gate seeks to understand how things work and to share that understanding. The gift is mental clarity and the ability to see patterns others miss. The shadow is rigid dogmatism or the need to always be right.",
     ["17-62 (The Channel of Acceptance)"]),
    (18, "Correction", "Work on What Has Been Spoiled", 18, "Collective Logic",
     "Gate 18 is the energy of correction and improvement. It carries the instinct to identify what is not working and the drive to make it right. This is the gate of the editor, the quality assurance mind, and the social reformer. It sees flaws and inefficiencies clearly, not from a place of criticism, but from genuine care for what could be better. The gift is discernment that leads to positive change. The shadow is relentless fault-finding or perfectionism that paralyzes.",
     ["18-58 (The Channel of Judgment)"]),
    (19, "Wanting", "Approach", 19, "Tribal Ego",
     "Gate 19 is the energy of wanting and need. It is the gate that feels the fundamental needs of the tribe — for food, shelter, touch, and belonging — and brings these into the relational field. This is the energy of sensitivity to the material and emotional needs of the community. When healthy, it creates deep interdependence and mutual care. The shadow is neediness, emotional manipulation through need, or martyrdom.",
     ["19-49 (The Channel of Synthesis)"]),
    (20, "Contemplation", "Contemplation", 20, "Individual Centering",
     "Gate 20 is the energy of contemplation and presence in the now. It represents pure awareness — the capacity to be fully present in the moment without agenda or expectation. This is the gate of meditation, mindfulness, and the recognition that being is as important as doing. Those with Gate 20 bring a quality of grounded presence that allows others to slow down. The shadow is detachment from life or paralysis through overthinking.",
     ["10-20 (The Channel of Awakening)", "20-34 (The Channel of Charisma)", "20-57 (The Channel of the Brainwave)"]),
    (21, "The Hunter/Huntress", "Biting Through", 21, "Tribal Ego",
     "Gate 21 is the energy of the hunter or huntress — the one who controls resources and territory for the tribe. This gate carries the instinct for strategic control, financial management, and the protection of what belongs to the community. It is the gate of the CEO, the guardian, and the one who ensures the tribe has what it needs. The gift is responsible stewardship of collective resources. The shadow is possessiveness, greed, or control for its own sake.",
     ["21-45 (The Channel of Money)"]),
    (22, "Grace", "Grace", 22, "Individual Centering",
     "Gate 22 is the energy of grace and emotional beauty. It is the gate that transmutes emotional experience into something beautiful — whether through words, music, art, or simply the way one carries oneself. This gate understands that emotion is not something to suppress but to honor and transform. The gift is emotional radiance that opens hearts. The shadow is emotional melodrama, vanity, or the use of charm to manipulate.",
     ["12-22 (The Channel of Openness)"]),
    (23, "Assimilation", "Splitting Apart", 23, "Individual Knowing",
     "Gate 23 is the energy of assimilation and articulation of new understanding. It is the gate of the teacher who can translate complex, individual knowing into language others can receive. This is the voice of the heretic and the innovator — those who speak truths before the collective is ready. The gift is the ability to articulate what has not yet been said. The shadow is being dismissed as crazy, or becoming the stereotypical mad genius who cannot be understood.",
     ["23-43 (The Channel of Structuring)"]),
    (24, "Rationalization", "Return", 24, "Individual Knowing",
     "Gate 24 is the energy of rationalization and the return to source. It represents the mental process of making sense of experience — the drive to understand why things happen and to find meaning in events. This gate is associated with the Ajna center and the process of mental digestion. It cycles through confusion and clarity, always seeking new understanding. The gift is insight that arises from deep contemplation. The shadow is obsessive rumination or the inability to let go of a question.",
     ["24-61 (The Channel of Awareness)"]),
    (25, "Innocence", "Innocence", 25, "Individual Centering",
     "Gate 25 is the energy of innocence and universal love. It is the gate of the spirit — the capacity to love unconditionally, without agenda, judgment, or expectation. This energy moves through the world with an open heart, seeing the divine in all beings. In Human Design, this is the gate of the priest or priestess. The gift is unconditional love that heals. The shadow is naivety, spiritual bypass, or being taken advantage of.",
     ["25-51 (The Channel of Initiation)"]),
    (26, "The Egoist", "The Taming Power of the Great", 26, "Tribal Ego",
     "Gate 26 is the energy of the egoist — the capacity to sell, persuade, and influence through the power of personal will. This is the gate of the salesperson, the marketer, and the leader who galvanizes others through force of personality. It represents the ego's ability to gather resources and people behind a vision. The gift is the ability to inspire action and close deals. The shadow is manipulation, exaggeration, or using charisma for selfish ends.",
     ["26-44 (The Channel of Surrender)"]),
    (27, "Caring", "Nourishment", 27, "Tribal Defense",
     "Gate 27 is the energy of caring and nourishment. It is the gate of the mother, the caregiver, and anyone who derives fulfillment from tending to the physical and emotional needs of others. This energy understands that care is an action — it feeds, shelters, and protects. It is the foundation of tribal survival. The gift is generous, life-sustaining care. The shadow is over-giving, codependency, or using care as a means of control.",
     ["27-50 (The Channel of Preservation)"]),
    (28, "The Game Player", "Preponderance of the Great", 28, "Individual Knowing",
     "Gate 28 is the energy of the game player — the one who finds meaning through struggle and risk. This gate understands that life's greatest meaning comes through facing challenges and overcoming adversity. It carries the instinct to test limits and to discover purpose through direct experience of difficulty. The gift is the courage to face existential questions and emerge with deeper meaning. The shadow is recklessness, thrill-seeking, or finding meaning only in crisis.",
     ["28-38 (The Channel of Struggle)"]),
    (29, "Perseverance", "The Abysmal", 29, "Collective Sensing",
     "Gate 29 is the energy of perseverance and commitment. It is the gate that says 'yes' to experience — the capacity to commit fully to a path, relationship, or endeavor and to stay the course through difficulty. This is not stubbornness but a deep attunement to what deserves sustained commitment. The gift is the reliability and depth that come from staying power. The shadow is saying yes to everything indiscriminately or staying in situations long past their expiration.",
     ["29-46 (The Channel of Discovery)"]),
    (30, "Feelings", "The Clinging Fire", 30, "Collective Sensing",
     "Gate 30 is the energy of intense feelings and emotional desire. It is the gate of the burning heart — the capacity to feel deeply, desire strongly, and allow emotional fire to fuel transformation. This gate does not seek to control or suppress feeling; it burns with it. The gift is passionate engagement with life that transforms everything it touches. The shadow is emotional drama, destructive desire, or being consumed by one's own emotional intensity.",
     ["30-41 (The Channel of Recognition)"]),
    (31, "Leading", "Influence", 31, "Collective Logic",
     "Gate 31 is the energy of democratic leadership and influence through voice. It represents the capacity to speak for the collective — to synthesize the needs, values, and direction of a group and articulate them clearly. This is the gate of the elected leader or spokesperson. The gift is the ability to influence and guide through words spoken at the right time. The shadow is demagoguery, empty rhetoric, or using influence for personal gain.",
     [""]),
    (32, "Continuity", "Duration", 32, "Collective Logic",
     "Gate 32 is the energy of continuity and the instinct for what endures. It evaluates what has lasting value and what will pass away. This gate carries the wisdom of the elder — the ability to sense what traditions, relationships, and commitments are worth preserving across time. The gift is the capacity to build things that last generations. The shadow is fear of change, resistance to necessary endings, or hoarding the past.",
     ["32-54 (The Channel of Transformation)"]),
    (33, "Privacy", "Retreat", 33, "Collective Sensing",
     "Gate 33 is the energy of privacy, retreat, and the distillation of experience into wisdom. It represents the need to withdraw periodically to process and integrate lived experience. This is the gate of the hermit, the memoirist, and the elder who shares hard-won wisdom only when the time is right. The gift is the articulation of universal truths drawn from personal experience. The shadow is isolation, secrecy, or withdrawal that avoids genuine connection.",
     ["13-33 (The Channel of the Prodigal)"]),
    (34, "Power", "The Power of the Great", 34, "Individual Centering",
     "Gate 34 is the energy of pure generative power — the life force itself expressed through the Sacral center. This is the gate of raw vitality, sexuality, and the capacity to do, build, and create. It is the most powerful sacral gate and represents the fundamental creative energy of the universe in human form. The gift is immense creative and physical power channeled through authentic response. The shadow is burnout through indiscriminate use of energy or power exerted without purpose.",
     ["10-34 (The Channel of Exploration)", "20-34 (The Channel of Charisma)", "34-57 (The Channel of Power)"]),
    (35, "Change", "Progress", 35, "Collective Sensing",
     "Gate 35 is the energy of change and progress through experience. It carries the hunger for new experiences, new places, and new people — not for novelty's sake but because experience is how this gate learns and grows. This is the gate of the adventurer and the lifelong learner. The gift is adaptability and the wisdom gained through direct experience. The shadow is chronic restlessness, inability to commit, or the endless pursuit of the next thing.",
     ["35-36 (The Channel of Transitoriness)"]),
    (36, "Crisis", "Darkening of the Light", 36, "Collective Sensing",
     "Gate 36 is the energy of crisis and emotional depth. It carries the capacity to experience and navigate intense emotional states — depression, despair, longing — and to emerge with compassion and wisdom. This gate knows the darkness as a teacher. It can also manifest as sexual and creative intensity that arises from emotional depth. The gift is profound empathy and the ability to hold space for others in crisis. The shadow is chronic emotional turmoil or addiction to crisis.",
     ["35-36 (The Channel of Transitoriness)"]),
    (37, "Friendship", "The Family", 37, "Tribal Defense",
     "Gate 37 is the energy of friendship and community bonds. It is the gate of the extended family — the capacity to create and maintain harmonious relationships within a tribe. This gate understands the power of touch, shared meals, and daily rituals that bind people together. The gift is the creation of warm, supportive community wherever one goes. The shadow is codependency, cliquishness, or sacrificing authenticity for harmony.",
     ["37-40 (The Channel of Community)"]),
    (38, "The Fighter", "Opposition", 38, "Individual Knowing",
     "Gate 38 is the energy of the fighter — the one who stands for something and will not back down. This gate carries the instinct to oppose what is not aligned and to fight for meaning and purpose. It is the warrior energy that protects what matters. This is not aggression for its own sake but the capacity to hold a line when something is at stake. The gift is courage and the ability to inspire others to stand for themselves. The shadow is belligerence, picking unnecessary fights, or inability to let things go.",
     ["28-38 (The Channel of Struggle)"]),
    (39, "Provocation", "Obstruction", 39, "Individual Knowing",
     "Gate 39 is the energy of provocation and the spirit of the trickster. It tests others to see if they are authentic, grounded, and worthy of engagement. This gate pushes buttons — not to harm, but to reveal truth. It is the energy that challenges complacency and spiritual bypass. The gift is the ability to catalyze growth through challenge. The shadow is deliberate cruelty, chronic discontent, or the inability to receive because everything is suspect.",
     ["39-55 (The Channel of Emoting)"]),
    (40, "Aloneness", "Deliverance", 40, "Tribal Ego",
     "Gate 40 is the energy of aloneness and the right to rest. It represents the ego's need to deliver, work, and provide for the tribe — and then to be released from obligation. This gate honors the natural cycle of effort and rest. It understands that the ego has limits and that rest is not laziness but sacred necessity. The gift is the capacity to work hard and then truly rest without guilt. The shadow is workaholism, inability to receive support, or isolation disguised as independence.",
     ["37-40 (The Channel of Community)"]),
    (41, "Contraction", "Decrease", 41, "Collective Sensing",
     "Gate 41 is the energy of contraction and the initiation of new cycles. It is the gate of fantasy and the imagination of what could be — the seed of all new human experience. This gate dreams the future into being. It represents the necessary contraction before expansion, the fantasy before manifestation. The gift is visionary imagination that seeds new realities. The shadow is escapism, fantasy addiction, or a life spent in daydreams without action.",
     ["30-41 (The Channel of Recognition)"]),
    (42, "Growth", "Increase", 42, "Collective Sensing",
     "Gate 42 is the energy of growth and completion. It is the gate that brings things to fruition — the capacity to nurture potential through all its stages to full expression. This gate understands that growth is a process with natural cycles and that completion is its own reward. The gift is the ability to bring things to a satisfying conclusion. The shadow is forcing growth, premature completion, or inability to let things end naturally.",
     ["42-53 (The Channel of Maturation)"]),
    (43, "Insight", "Breakthrough", 43, "Individual Knowing",
     "Gate 43 is the energy of insight and breakthrough. It represents the moment when individual knowing crystallizes into a new understanding that can change everything. This is the gate of the genius — the flash of insight that arrives fully formed and must be expressed. It does not explain or argue; it simply sees. The gift is transformative new understanding that benefits the collective in time. The shadow is deafness to feedback, arrogance of insight, or inability to ground vision in practical reality.",
     ["23-43 (The Channel of Structuring)"]),
    (44, "Alertness", "Coming to Meet", 44, "Tribal Ego",
     "Gate 44 is the energy of alertness and instinctive pattern recognition. It carries the survival instinct of the tribe — the ability to sense danger, read people, and recognize patterns from the past. This gate is deeply connected to ancestral memory and the instinct to protect the tribe from threats. The gift is intuitive awareness that keeps communities safe. The shadow is paranoia, suspicion, or being haunted by past patterns to the point of paralysis.",
     ["26-44 (The Channel of Surrender)"]),
    (45, "Gathering", "Gathering Together", 45, "Tribal Ego",
     "Gate 45 is the energy of gathering and the role of the king or queen. It represents the capacity to gather resources, people, and influence for the benefit of the tribe — and to distribute them wisely. This gate understands that wealth is meant to flow through, not to hoard. The gift is benevolent leadership and resource stewardship. The shadow is greed, entitlement, or the abuse of positional power.",
     ["21-45 (The Channel of Money)"]),
    (46, "Determination of the Self", "Pushing Upward", 46, "Collective Sensing",
     "Gate 46 is the energy of embodied determination and love of the physical form. It represents the capacity to be fully present in the body and to find joy in physical experience. This gate is deeply sensual and attuned to the body's wisdom. It carries the determination to push upward — to grow, to thrive, to fully inhabit life. The gift is embodied vitality and the ability to enjoy life's pleasures without guilt. The shadow is over-identification with the body, hedonism, or neglect of the physical self.",
     ["29-46 (The Channel of Discovery)"]),
    (47, "Realization", "Oppression", 47, "Collective Logic",
     "Gate 47 is the energy of realization and mental oppression. It represents the mind's experience of being stuck — the frustration of not understanding — that ultimately leads to breakthrough and synthesis. This gate processes experience through logic and pattern, and when the pieces finally connect, realization dawns. The gift is the capacity for deep synthesis. The shadow is chronic mental anxiety, overthinking, or the feeling of being trapped in one's own mind.",
     ["47-64 (The Channel of Abstraction)"]),
    (48, "Depth", "The Well", 48, "Collective Logic",
     "Gate 48 is the energy of depth and the well of natural talent. It represents deep, innate knowing that may not always be accessible on demand — it must be drawn from when the timing is right. This gate carries profound knowledge and skill that exists below the surface of consciousness. The gift is access to resources of wisdom and talent that seem bottomless. The shadow is fear of inadequacy, imposter syndrome, or feeling that one's depth is never sufficient.",
     ["16-48 (The Channel of Talent)"]),
    (49, "Principles", "Revolution", 49, "Tribal Ego",
     "Gate 49 is the energy of principles and revolution. It carries the drive to restructure tribal relationships based on higher principles. This gate draws lines, sets boundaries, and says 'this is what I stand for.' It is the energy of social justice, divorce (in the sense of ending what is no longer aligned), and the willingness to cut ties in service of integrity. The gift is principled action that transforms relationships. The shadow is rejection, emotional cruelty, or rigid moralism.",
     ["19-49 (The Channel of Synthesis)"]),
    (50, "Values", "The Cauldron", 50, "Tribal Defense",
     "Gate 50 is the energy of values and the preservation of what matters. It represents the transmission of tribal values from one generation to the next — the wisdom of what to preserve and what to let go. This gate is associated with the cauldron of transformation: what goes in must be refined. The gift is the discernment to uphold meaningful values and transmit them with care. The shadow is rigid traditionalism, guilt-based morality, or corrupt guardianship.",
     ["27-50 (The Channel of Preservation)"]),
    (51, "Shock", "The Arousing", 51, "Individual Centering",
     "Gate 51 is the energy of shock and awakening. It represents the capacity to be shaken into higher consciousness — the lightning bolt that shatters old patterns and opens the way for new life. This is the gate of spiritual initiation through sudden, unexpected events. Those with this gate defined may experience or catalyze life-changing shocks. The gift is the ability to awaken others through one's own journey. The shadow is self-destructive behavior, shocking others for attention, or being perpetually destabilized.",
     ["25-51 (The Channel of Initiation)"]),
    (52, "Stillness", "Keeping Still", 52, "Collective Logic",
     "Gate 52 is the energy of stillness and the mountain. It represents the capacity to be completely still, to wait without agenda, and to allow action to arise from a place of deep groundedness. This is the gate of the meditator and the one who knows that inaction can be more powerful than action. The gift is profound peace and the ability to conserve and concentrate energy. The shadow is passivity, depression, or stillness that becomes stuckness.",
     ["9-52 (The Channel of Concentration)"]),
    (53, "Beginnings", "Development", 53, "Collective Sensing",
     "Gate 53 is the energy of beginnings. It carries the impulse to start new things — new projects, new relationships, new phases of life. This gate understands that every beginning contains the seed of its own development and trusts the natural unfolding of cycles. Nothing happens without a beginning, and Gate 53 is the initiator of all experiential learning cycles. The gift is the courage and enthusiasm to begin. The shadow is starting things but never finishing, or beginning as a way to avoid the stillness of completion.",
     ["42-53 (The Channel of Maturation)"]),
    (54, "Ambition", "The Marrying Maiden", 54, "Tribal Ego",
     "Gate 54 is the energy of ambition and the drive to rise. It carries the instinct to improve one's station, to transform through relationship and alliance, and to reach higher levels of material and social achievement. This gate understands that ambition is not inherently selfish — it can serve the tribe's elevation. The gift is driven transformation that benefits many. The shadow is ruthless ambition, using relationships as stepping stones, or perpetual dissatisfaction.",
     ["32-54 (The Channel of Transformation)"]),
    (55, "Spirit", "Abundance", 55, "Individual Knowing",
     "Gate 55 is the energy of spirit and emotional abundance. It represents the capacity to experience the full spectrum of emotional life — from the deepest sorrow to the highest ecstasy — and to trust that spirit pervades all of it. This is the gate of the mystic and the artist who channels spirit through emotional expression. The gift is emotional authenticity and spiritual freedom. The shadow is emotional instability, spiritual crisis, or the refusal to feel.",
     ["39-55 (The Channel of Emoting)"]),
    (56, "Stimulation", "The Wanderer", 56, "Collective Sensing",
     "Gate 56 is the energy of stimulation and the storyteller's gift. It carries the drive to wander, explore, and gather experiences — and then to return and share them as stories that stimulate and inspire others. This gate understands that human beings learn and grow through narrative. The gift is the ability to translate raw experience into compelling stories that teach. The shadow is restlessness, exaggeration, or the use of stories to distract rather than illuminate.",
     ["11-56 (The Channel of Curiosity)"]),
    (57, "Intuition", "The Gentle", 57, "Individual Knowing",
     "Gate 57 is the energy of intuitive clarity in the present moment. It represents the ability to know, instantly and without mental processing, what is correct in the now. This is the gate of the clairvoyant — the one who senses truth through the body rather than the mind. It operates in the Spleen center and carries a deep trust in instinct. The gift is instantaneous right knowing that cuts through confusion. The shadow is fearful hypersensitivity, jumping at shadows, or distrust of one's own intuition.",
     ["10-57 (The Channel of Perfected Form)", "20-57 (The Channel of the Brainwave)", "34-57 (The Channel of Power)"]),
    (58, "Aliveness", "The Joyous", 58, "Collective Logic",
     "Gate 58 is the energy of aliveness and the drive to improve life for everyone. It carries an innate dissatisfaction with anything less than the fullest expression of life — and a corresponding drive to make things better. This is the gate of the social reformer, the healer, and anyone who cannot rest while suffering exists. The gift is the capacity to challenge and improve systems for the collective good. The shadow is chronic dissatisfaction, inability to rest in what is good, or toxic criticism.",
     ["18-58 (The Channel of Judgment)"]),
    (59, "Sexuality", "Dispersion", 59, "Tribal Defense",
     "Gate 59 is the energy of sexuality, intimacy, and the breaking down of barriers between people. It carries the drive to connect, penetrate, and merge — whether physically, emotionally, or creatively. This is the gate of genetic continuity and the fundamental attraction force that brings people together. The gift is deep intimacy and the capacity to create life (literally or metaphorically). The shadow is promiscuity without connection, using sexuality to avoid intimacy, or violating boundaries.",
     ["6-59 (The Channel of Mating)"]),
    (60, "Acceptance", "Limitation", 60, "Individual Knowing",
     "Gate 60 is the energy of acceptance and limitation. It represents the capacity to accept what is — to work within real constraints and limitations and to discover that limitation itself is the creative force that gives form to life. This gate understands that without limits there is no form; a musical note is defined by its boundary. The gift is grounded acceptance and the creative power of working within real limits. The shadow is hopelessness, resignation, or the feeling of being trapped.",
     ["3-60 (The Channel of Mutation)"]),
    (61, "Mystery", "Inner Truth", 61, "Individual Knowing",
     "Gate 61 is the energy of mystery and the drive to know what cannot be known. It represents the mind's confrontation with the unknowable — the great existential questions that have no final answer. This gate is the mystic's mind, the philosopher's question, and the scientist's wonder. It knows that the mystery is not to be solved but to be honored. The gift is inspired wonder that fuels inquiry. The shadow is mental pressure to know the unknowable, leading to anxiety or delusion.",
     ["24-61 (The Channel of Awareness)"]),
    (62, "Detail", "Preponderance of the Small", 62, "Collective Logic",
     "Gate 62 is the energy of detail and the articulation of facts. It carries the capacity to observe, name, and organize specific details — and to communicate them with precision and clarity. This is the gate of the scientist, the editor, and anyone working with precise data. The gift is clear, factual communication that others can rely upon. The shadow is getting lost in minutiae, pedantry, or using details to obscure rather than illuminate.",
     ["17-62 (The Channel of Acceptance)"]),
    (63, "Doubt", "After Completion", 63, "Collective Logic",
     "Gate 63 is the energy of doubt and the logical mind's drive to question. It represents healthy skepticism — the refusal to accept things at face value and the commitment to testing all assumptions. This gate drives scientific inquiry and intellectual rigor. It understands that doubt, properly held, leads to deeper understanding. The gift is the capacity to question productively and arrive at more grounded truth. The shadow is chronic doubt, cynicism, or skepticism that destroys rather than clarifies.",
     ["4-63 (The Channel of Logic)"]),
    (64, "Confusion", "Before Completion", 64, "Collective Logic",
     "Gate 64 is the energy of confusion and the mental process that precedes clarity. It represents the fertile chaos of the creative mind — the state of having many pieces that do not yet form a coherent picture. This gate knows that confusion is not error; it is the necessary precondition for insight. The gift is the ability to hold complexity and ambiguity until clarity naturally emerges. The shadow is chronic confusion, mental overwhelm, or giving up before the pattern resolves.",
     ["47-64 (The Channel of Abstraction)"]),
]

CENTERS = {
    "Head": [61, 63, 64],
    "Ajna": [4, 11, 17, 24, 43, 47],
    "Throat": [8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62],
    "G": [1, 2, 7, 10, 13, 15, 25, 46],
    "Ego": [21, 26, 40, 51],
    "Sacral": [3, 5, 9, 14, 27, 29, 34, 42, 59],
    "Spleen": [18, 28, 32, 44, 48, 50, 57],
    "Solar Plexus": [6, 22, 30, 36, 37, 39, 49, 55],
    "Root": [19, 38, 41, 52, 53, 54, 58, 60],
}


def find_center(gate_num):
    for center, gates in CENTERS.items():
        if gate_num in gates:
            return center
    return "Unknown"


def gate_page_html(g):
    num, name, hex_name, hex_num, circuit, meaning, channels = g
    center = find_center(num)
    channels_html = ""
    if channels and channels[0]:
        channels_html = "<ul class=\"gate-channels\">\n"
        for ch in channels:
            channels_html += f'          <li><a href="https://humandesignengine.com/seo/gates/">{ch}</a></li>\n'
        channels_html += "        </ul>"
    else:
        channels_html = "<p class=\"gate-channels\"><em>This gate participates in multiple channel potentials and forms part of the bodygraph's foundational architecture.</em></p>\n"

    pad = str(num).zfill(2)
    title = f"Human Design Gate {num} — {name} | Human Design Engine"
    desc = f"Gate {num} ({name}): I-Ching Hexagram {hex_num}, {circuit} circuit. {meaning[:155]}..."

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="Human Design, Gate {num}, {name}, I-Ching Hexagram {hex_num}, {circuit}, Human Design Engine, HD gates, bodygraph">
<link rel="canonical" href="https://humandesignengine.com/seo/gates/gate-{num}/">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://humandesignengine.com/seo/gates/gate-{num}/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Human Design Gate {num}: {name}",
  "description": "{desc}",
  "author": {{ "@type": "Organization", "name": "Human Design Engine" }},
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }}
}}
</script>
<style>
  :root {{
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
  }}

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html {{ scroll-behavior: smooth; }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--navy-deep);
    color: var(--text-primary);
    line-height: 1.7;
    overflow-x: hidden;
  }}

  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse at 20% 10%, rgba(201,168,76,0.04) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 90%, rgba(201,168,76,0.03) 0%, transparent 60%),
      radial-gradient(ellipse at 50% 50%, rgba(15,29,54,0.8) 0%, var(--navy-deep) 100%);
    pointer-events: none;
    z-index: 0;
  }}

  nav {{
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(6, 13, 26, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(201,168,76,0.1);
    padding: 0 20px;
  }}
  .nav-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: relative;
    z-index: 1;
  }}
  .nav-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--white);
    text-decoration: none;
    letter-spacing: -0.02em;
  }}
  .nav-logo .icon {{
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--gold-bright), var(--gold));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    color: var(--navy-deep);
    font-weight: 900;
  }}
  .nav-links {{ display: flex; gap: 24px; align-items: center; }}
  .nav-links a {{
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.88rem;
    font-weight: 500;
    transition: var(--transition);
  }}
  .nav-links a:hover {{ color: var(--gold-light); }}

  .container {{
    max-width: 900px;
    margin: 0 auto;
    padding: 0 24px;
    position: relative;
    z-index: 1;
  }}

  /* Breadcrumb */
  .breadcrumb {{
    padding: 18px 0;
    font-size: 0.82rem;
    color: var(--text-muted);
  }}
  .breadcrumb a {{
    color: var(--gold);
    text-decoration: none;
    transition: var(--transition);
  }}
  .breadcrumb a:hover {{ color: var(--gold-light); }}
  .breadcrumb span {{ margin: 0 6px; }}

  /* Gate Hero */
  .gate-hero {{
    text-align: center;
    padding: 48px 24px 40px;
    position: relative;
    z-index: 1;
  }}
  .gate-number {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 88px;
    height: 88px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(201,168,76,0.2), rgba(201,168,76,0.08));
    border: 2px solid rgba(201,168,76,0.35);
    font-size: 2rem;
    font-weight: 800;
    color: var(--gold-light);
    margin-bottom: 20px;
    letter-spacing: -0.02em;
  }}
  .gate-hero h1 {{
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 12px;
    background: linear-gradient(180deg, #ffffff 0%, #c0c8d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .gate-hero .gate-subtitle {{
    font-size: 1.05rem;
    color: var(--text-secondary);
    max-width: 560px;
    margin: 0 auto;
  }}

  /* Info Grid */
  .gate-info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 48px;
  }}
  .gate-info-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 20px 18px;
    text-align: center;
  }}
  .gate-info-card .label {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--gold);
    font-weight: 600;
    margin-bottom: 6px;
  }}
  .gate-info-card .value {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
  }}

  /* Content */
  .gate-content {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 40px 36px;
    margin-bottom: 48px;
  }}
  .gate-content h2 {{
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 20px;
    color: var(--white);
    letter-spacing: -0.02em;
  }}
  .gate-content h3 {{
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--gold-light);
    margin: 32px 0 14px;
    letter-spacing: -0.01em;
  }}
  .gate-content p {{
    font-size: 1rem;
    color: var(--text-secondary);
    line-height: 1.75;
    margin-bottom: 16px;
  }}
  .gate-content .highlight {{
    color: var(--gold-light);
    font-weight: 500;
  }}
  .gate-channels {{
    list-style: none;
    padding: 0;
    margin: 12px 0 0;
  }}
  .gate-channels li {{
    padding: 8px 0;
    font-size: 0.92rem;
    color: var(--text-secondary);
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }}
  .gate-channels li a {{
    color: var(--gold-light);
    text-decoration: none;
    transition: var(--transition);
  }}
  .gate-channels li a:hover {{ text-decoration: underline; }}

  /* Navigation */
  .gate-nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 0 48px;
    gap: 16px;
    flex-wrap: wrap;
  }}
  .gate-nav a {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 10px 20px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.88rem;
    font-weight: 500;
    transition: var(--transition);
  }}
  .gate-nav a:hover {{
    border-color: rgba(201,168,76,0.35);
    color: var(--gold-light);
  }}

  /* CTA */
  .cta-section {{
    text-align: center;
    padding: 48px 24px 64px;
    position: relative;
    z-index: 1;
  }}
  .cta-section h2 {{
    font-size: clamp(1.3rem, 2.5vw, 1.7rem);
    font-weight: 700;
    margin-bottom: 12px;
    letter-spacing: -0.02em;
  }}
  .cta-section p {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 480px;
    margin: 0 auto 24px;
  }}
  .btn {{
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
  }}
  .btn-primary {{
    background: linear-gradient(135deg, var(--gold-bright), var(--gold));
    color: var(--navy-deep);
    box-shadow: 0 4px 20px rgba(201,168,76,0.3);
  }}
  .btn-primary:hover {{
    box-shadow: 0 6px 30px rgba(201,168,76,0.45);
    transform: translateY(-2px);
  }}

  /* FAQ */
  .faq {{
    padding: 48px 0 64px;
  }}
  .faq h2 {{
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 32px;
    letter-spacing: -0.02em;
  }}
  .faq-item {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 24px 28px;
    margin-bottom: 12px;
  }}
  .faq-item h3 {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--gold-light);
    margin-bottom: 8px;
  }}
  .faq-item p {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.65;
  }}

  footer {{
    background: rgba(6, 13, 26, 0.6);
    border-top: 1px solid rgba(201,168,76,0.08);
    padding: 28px 20px;
    text-align: center;
    position: relative;
    z-index: 1;
  }}
  .footer-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }}
  .footer-inner .left {{ display: flex; flex-direction: column; gap: 4px; text-align: left; }}
  .footer-inner .brand {{ font-weight: 600; color: var(--text-primary); font-size: 0.88rem; }}
  .footer-inner .license {{ font-size: 0.76rem; color: var(--text-muted); }}
  .footer-links {{ display: flex; gap: 18px; }}
  .footer-links a {{
    font-size: 0.8rem;
    color: var(--text-muted);
    text-decoration: none;
    transition: var(--transition);
  }}
  .footer-links a:hover {{ color: var(--gold-light); }}

  @media (max-width: 768px) {{
    .nav-links {{ gap: 12px; }}
    .nav-links a {{ font-size: 0.78rem; }}
    .gate-content {{ padding: 28px 20px; }}
    .footer-inner {{ flex-direction: column; text-align: center; }}
  }}
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
      <a href="/seo/gates/">All Gates</a>
      <a href="/api">API</a>
      <a href="/reports">Reports</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    <a href="/seo/gates/">Human Design Gates</a> <span>›</span>
    Gate {num}: {name}
  </div>

  <section class="gate-hero">
    <div class="gate-number">{num}</div>
    <h1>Gate {num}: {name}</h1>
    <p class="gate-subtitle">I-Ching Hexagram {hex_num}: {hex_name} — {circuit} Circuit</p>
  </section>

  <div class="gate-info-grid">
    <div class="gate-info-card">
      <div class="label">Gate Number</div>
      <div class="value">{num}</div>
    </div>
    <div class="gate-info-card">
      <div class="label">I-Ching Hexagram</div>
      <div class="value">{hex_num} — {hex_name}</div>
    </div>
    <div class="gate-info-card">
      <div class="label">Circuit Group</div>
      <div class="value">{circuit}</div>
    </div>
    <div class="gate-info-card">
      <div class="label">Center</div>
      <div class="value">{center}</div>
    </div>
  </div>

  <article class="gate-content">
    <h2>What Human Design Gate {num} Means</h2>
    <p>{meaning}</p>

    <h3>Gate {num} in the Bodygraph</h3>
    <p>Gate {num} is located in the <span class="highlight">{center} Center</span> and is part of the <span class="highlight">{circuit} circuit</span>. The energy of this gate flows through specific channels that connect it to other centers, creating the unique architecture of your bodygraph. When this gate is defined (colored) in your chart, its energy is consistent and reliable. When it is undefined (white), you experience and amplify this energy from others.</p>

    <h3>Channels Involving Gate {num}</h3>
    {channels_html}

    <h3>The Gift and Shadow of Gate {num}</h3>
    <p>Every gate carries both a gift frequency (its high expression) and a shadow frequency (its low expression). The gift of Gate {num} emerges when the energy flows naturally according to your Strategy and Authority. The shadow manifests when we try to force, control, or override this energy with the mind. Learning to trust the natural rhythm of Gate {num} is part of the journey of living your design.</p>
  </article>

  <div class="gate-nav">
    {f'<a href="gate-{num-1}.html">← Gate {num-1}</a>' if num > 1 else '<a href="gate-64.html">← Gate 64</a>'}
    <a href="index.html">All 64 Gates</a>
    {f'<a href="gate-{num+1}.html">Gate {num+1} →</a>' if num < 64 else '<a href="gate-1.html">Gate 1 →</a>'}
  </div>

  <section class="faq">
    <h2>Frequently Asked Questions</h2>
    <div class="faq-item">
      <h3>What does it mean to have Gate {num} defined?</h3>
      <p>When Gate {num} is defined (colored) in your bodygraph, the energy of {name} operates consistently in your life. You carry this frequency as a fixed part of your design, and others can rely on you for this quality.</p>
    </div>
    <div class="faq-item">
      <h3>What happens when Gate {num} is undefined?</h3>
      <p>An undefined (white) Gate {num} means you are open to experiencing and amplifying the energy of {name} from others and from transits. This can be a source of wisdom — you understand this gate deeply through your experiences with it — but it is not a consistent part of your design.</p>
    </div>
    <div class="faq-item">
      <h3>How does Gate {num} relate to the I-Ching?</h3>
      <p>Human Design maps the 64 hexagrams of the I-Ching directly onto the 64 gates of the bodygraph. Gate {num} corresponds to <strong>Hexagram {hex_num}: {hex_name}</strong>, carrying the archetypal energy and wisdom of this ancient symbol into the modern Human Design system.</p>
    </div>
  </section>

  <section class="cta-section">
    <h2>Want to See Your Full Bodygraph?</h2>
    <p>Discover which gates are defined in your unique Human Design chart. Get your free bodygraph and deep-dive report from Human Design Engine.</p>
    <a href="/reports" class="btn btn-primary">Get Your Free Chart →</a>
  </section>

</div>

<footer>
  <div class="footer-inner">
    <div class="left">
      <span class="brand">Human Design Engine</span>
      <span class="license">Verified chart data — open-source computation engine.</span>
    </div>
    <div class="footer-links">
      <a href="/seo/gates/">All Gates</a>
      <a href="/api">API</a>
      <a href="/reports">Reports</a>
      <a href="/privacy">Privacy</a>
    </div>
  </div>
</footer>

</body>
</html>'''


def index_page_html():
    """Generate the index page listing all 64 gates."""
    gate_cards = ""
    for num, name, hex_name, hex_num, circuit, meaning, channels in GATES:
            center = find_center(num)
            snippet = meaning[:120] + "..."
            gate_cards += f'''      <a href="gate-{num}.html" class="gate-card">
        <div class="gate-card-number">{num}</div>
        <div class="gate-card-body">
          <h3>{name}</h3>
          <p class="gate-card-hex">Hexagram {hex_num}: {hex_name}</p>
          <p class="gate-card-circuit">{circuit} · {center} Center</p>
          <p class="gate-card-snippet">{snippet}</p>
        </div>
        <span class="arrow">→</span>
      </a>
'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 64 Gates of Human Design — Complete Guide | Human Design Engine</title>
<meta name="description" content="Explore all 64 Human Design gates. Each gate explained with I-Ching hexagram, circuit group, center location, meaning, gift, and shadow. Comprehensive gate reference from Human Design Engine.">
<meta name="keywords" content="Human Design gates, 64 gates, gate meanings, I-Ching, bodygraph, gate reference, Human Design Engine">
<link rel="canonical" href="https://humandesignengine.com/seo/gates/">
<meta property="og:title" content="The 64 Gates of Human Design — Complete Guide | Human Design Engine">
<meta property="og:description" content="Explore every Human Design gate with detailed explanations. Learn the I-Ching hexagram, circuit, center, gift, and shadow for all 64 gates.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://humandesignengine.com/seo/gates/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="The 64 Gates of Human Design — Complete Guide">
<meta name="twitter:description" content="Complete reference for all 64 Human Design gates with I-Ching hexagrams, circuits, and meanings.">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "The 64 Gates of Human Design",
  "description": "A complete guide to all 64 gates in the Human Design bodygraph, including I-Ching hexagrams, circuit groups, centers, and detailed meanings.",
  "url": "https://humandesignengine.com/seo/gates/",
  "publisher": {{ "@type": "Organization", "name": "Human Design Engine", "url": "https://humandesignengine.com" }}
}}
</script>
<style>
  :root {{
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
  }}

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html {{ scroll-behavior: smooth; }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--navy-deep);
    color: var(--text-primary);
    line-height: 1.7;
    overflow-x: hidden;
  }}

  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse at 20% 10%, rgba(201,168,76,0.04) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 90%, rgba(201,168,76,0.03) 0%, transparent 60%),
      radial-gradient(ellipse at 50% 50%, rgba(15,29,54,0.8) 0%, var(--navy-deep) 100%);
    pointer-events: none;
    z-index: 0;
  }}

  nav {{
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(6, 13, 26, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(201,168,76,0.1);
    padding: 0 20px;
  }}
  .nav-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: relative;
    z-index: 1;
  }}
  .nav-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--white);
    text-decoration: none;
    letter-spacing: -0.02em;
  }}
  .nav-logo .icon {{
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--gold-bright), var(--gold));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    color: var(--navy-deep);
    font-weight: 900;
  }}
  .nav-links {{ display: flex; gap: 24px; align-items: center; }}
  .nav-links a {{
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.88rem;
    font-weight: 500;
    transition: var(--transition);
  }}
  .nav-links a:hover {{ color: var(--gold-light); }}

  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    position: relative;
    z-index: 1;
  }}

  .breadcrumb {{
    padding: 18px 0;
    font-size: 0.82rem;
    color: var(--text-muted);
  }}
  .breadcrumb a {{
    color: var(--gold);
    text-decoration: none;
    transition: var(--transition);
  }}
  .breadcrumb a:hover {{ color: var(--gold-light); }}
  .breadcrumb span {{ margin: 0 6px; }}

  /* Hero */
  .gate-index-hero {{
    text-align: center;
    padding: 64px 24px 48px;
    position: relative;
    z-index: 1;
  }}
  .gate-index-hero h1 {{
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 16px;
    background: linear-gradient(180deg, #ffffff 0%, #c0c8d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .gate-index-hero p {{
    font-size: 1.1rem;
    color: var(--text-secondary);
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.7;
  }}

  /* Stats */
  .stats-row {{
    display: flex;
    justify-content: center;
    gap: 32px;
    flex-wrap: wrap;
    padding: 24px 0 48px;
  }}
  .stat-item {{
    text-align: center;
  }}
  .stat-number {{
    font-size: 2rem;
    font-weight: 800;
    color: var(--gold-light);
    letter-spacing: -0.02em;
  }}
  .stat-label {{
    font-size: 0.8rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}

  /* Circuit Tabs */
  .circuit-nav {{
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 40px;
  }}
  .circuit-nav a {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 50px;
    padding: 8px 18px;
    font-size: 0.82rem;
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
  }}
  .circuit-nav a:hover {{
    border-color: rgba(201,168,76,0.4);
    color: var(--gold-light);
    background: var(--gold-soft);
  }}

  /* Gate Cards Grid */
  .gate-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 20px;
    padding-bottom: 64px;
  }}
  .gate-card {{
    display: flex;
    align-items: flex-start;
    gap: 16px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 22px 20px;
    text-decoration: none;
    color: inherit;
    transition: var(--transition);
    position: relative;
  }}
  .gate-card:hover {{
    border-color: rgba(201,168,76,0.35);
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0,0,0,0.3);
  }}
  .gate-card-number {{
    flex-shrink: 0;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(201,168,76,0.2), rgba(201,168,76,0.06));
    border: 1.5px solid rgba(201,168,76,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--gold-light);
  }}
  .gate-card-body h3 {{
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 4px;
    color: var(--white);
    letter-spacing: -0.01em;
  }}
  .gate-card-body .gate-card-hex {{
    font-size: 0.78rem;
    color: var(--gold-light);
    margin-bottom: 2px;
  }}
  .gate-card-body .gate-card-circuit {{
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 6px;
  }}
  .gate-card-body .gate-card-snippet {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.5;
  }}
  .gate-card .arrow {{
    position: absolute;
    bottom: 18px;
    right: 18px;
    font-size: 1rem;
    color: var(--gold);
    opacity: 0;
    transition: var(--transition);
  }}
  .gate-card:hover .arrow {{ opacity: 1; }}

  /* CTA */
  .cta-section {{
    text-align: center;
    padding: 48px 24px 72px;
    position: relative;
    z-index: 1;
  }}
  .cta-section h2 {{
    font-size: clamp(1.4rem, 3vw, 1.8rem);
    font-weight: 700;
    margin-bottom: 12px;
    letter-spacing: -0.02em;
  }}
  .cta-section p {{
    color: var(--text-secondary);
    font-size: 1rem;
    max-width: 500px;
    margin: 0 auto 24px;
    line-height: 1.7;
  }}
  .btn {{
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
  }}
  .btn-primary {{
    background: linear-gradient(135deg, var(--gold-bright), var(--gold));
    color: var(--navy-deep);
    box-shadow: 0 4px 20px rgba(201,168,76,0.3);
  }}
  .btn-primary:hover {{
    box-shadow: 0 6px 30px rgba(201,168,76,0.45);
    transform: translateY(-2px);
  }}

  footer {{
    background: rgba(6, 13, 26, 0.6);
    border-top: 1px solid rgba(201,168,76,0.08);
    padding: 28px 20px;
    text-align: center;
    position: relative;
    z-index: 1;
  }}
  .footer-inner {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
  }}
  .footer-inner .left {{ display: flex; flex-direction: column; gap: 4px; text-align: left; }}
  .footer-inner .brand {{ font-weight: 600; color: var(--text-primary); font-size: 0.88rem; }}
  .footer-inner .license {{ font-size: 0.76rem; color: var(--text-muted); }}
  .footer-links {{ display: flex; gap: 18px; }}
  .footer-links a {{
    font-size: 0.8rem;
    color: var(--text-muted);
    text-decoration: none;
    transition: var(--transition);
  }}
  .footer-links a:hover {{ color: var(--gold-light); }}

  @media (max-width: 768px) {{
    .nav-links {{ gap: 12px; }}
    .nav-links a {{ font-size: 0.78rem; }}
    .gate-grid {{ grid-template-columns: 1fr; }}
    .footer-inner {{ flex-direction: column; text-align: center; }}
  }}
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
      <a href="/seo/gates/" style="color:var(--gold-light);">All Gates</a>
      <a href="/api">API</a>
      <a href="/reports">Reports</a>
    </div>
  </div>
</nav>

<div class="container">

  <div class="breadcrumb">
    <a href="/">Home</a> <span>›</span>
    Human Design Gates
  </div>

  <section class="gate-index-hero">
    <h1>The 64 Gates of Human Design</h1>
    <p>A complete guide to every gate in the Human Design bodygraph. Each gate maps to an I-Ching hexagram and carries specific energy, a gift frequency, and a shadow pattern. Click any gate for a detailed explanation.</p>
  </section>

  <div class="stats-row">
    <div class="stat-item">
      <div class="stat-number">64</div>
      <div class="stat-label">Gates</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">9</div>
      <div class="stat-label">Centers</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">36</div>
      <div class="stat-label">Channels</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">6</div>
      <div class="stat-label">Circuit Groups</div>
    </div>
  </div>

  <div class="circuit-nav">
    <a href="#individual">Individual Circuit</a>
    <a href="#tribal">Tribal Circuit</a>
    <a href="#collective">Collective Circuit</a>
  </div>

  <h2 id="individual" style="font-size:1.4rem;font-weight:700;margin-bottom:20px;letter-spacing:-0.02em;">Individual Circuit Gates</h2>
  <p style="color:var(--text-muted);font-size:0.9rem;margin-bottom:28px;">The Individual Circuit empowers, mutates, and brings new energy into the world. These gates drive authenticity, creativity, and personal transformation.</p>
  <div class="gate-grid">
{gate_cards}
  </div>

  <section class="cta-section">
    <h2>Want to Know Which Gates Are Defined in Your Chart?</h2>
    <p>Your bodygraph reveals which of the 64 gates are consistently active in your design. Get your free Human Design chart today.</p>
    <a href="/reports" class="btn btn-primary">Get Your Free Chart →</a>
  </section>

</div>

<footer>
  <div class="footer-inner">
    <div class="left">
      <span class="brand">Human Design Engine</span>
      <span class="license">Verified chart data — open-source computation engine.</span>
    </div>
    <div class="footer-links">
      <a href="/seo/gates/">All Gates</a>
      <a href="/api">API</a>
      <a href="/reports">Reports</a>
      <a href="/privacy">Privacy</a>
    </div>
  </div>
</footer>

</body>
</html>'''


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Generate index page
    idx_path = os.path.join(OUT_DIR, "index.html")
    with open(idx_path, "w") as f:
        f.write(index_page_html())
    print(f"✓ Generated index page: {idx_path}")

    # Generate all 64 gate pages
    for g in GATES:
        num = g[0]
        path = os.path.join(OUT_DIR, f"gate-{num}.html")
        with open(path, "w") as f:
            f.write(gate_page_html(g))
        print(f"  Gate {num}: {path}")

    print(f"\n✓ Done! Generated 64 gate pages + 1 index page in {OUT_DIR}")


if __name__ == "__main__":
    main()
