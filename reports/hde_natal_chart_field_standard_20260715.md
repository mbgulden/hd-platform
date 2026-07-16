# HDE Natal Chart Field Standard

**Date:** 2026-07-15
**Branch:** `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15`
**Status:** 🟡 Implemented in staging report/bodygraph generators; broader guest skill/content propagation still needs follow-up if those surfaces render separate natal summaries.

## Source correction

Michael approved the staging design direction, then flagged two requirements:

1. Fix mojibake / wrong characters such as `Youâ€Tvre`.
2. Make natal chart output useful for coaching, education, and HDE content by including the important Human Design fields with short, organized descriptions rather than a cluttered dump.

## Field groups now represented

### Core mechanics

- Profile
- Type
- Definition
- Authority
- Strategy
- Signature
- Not-Self Theme
- Incarnation Cross

### Advanced orientation

- Variables
- Environment
- View / Perspective
- Distraction
- Sense
- Trajectory
- Cognition
- Motivation
- Transference
- Determination

### Coaching / education lenses

- Bridging Gates
- Melancholy
- Fears
- Penta Qualities
- Genetic Trauma
- AstroHD Star Archetype

### Timing and transparency

- Birth Date
- Birth Date (UTC)
- Design Date
- Design Date (UTC)
- Location
- Time Zone
- Saturn Return (UTC)
- Second Saturn Return (UTC)
- Uranus Opposition (UTC)
- Chiron Return (UTC)

## Planet + gate requirement

Becca’s requirement is now reflected in the report generator: natal reports include a **Gates + Planets: Professional Activation Map** with:

- Personality vs Design side,
- Planet,
- Gate.Line,
- Center,
- Gate theme,
- a short planet-significance description.

This is the right foundation for coaching-call prep, web education content, and deeper relationship/current-circumstance interpretation beyond over-focusing on Type or Incarnation Cross.

## Implementation notes

- `reports/server.py` now repairs common mojibake before display, including `Youâ€Tvre` → `You're`.
- `reports/server.py` renders all required fields as compact cards with short descriptions.
- `reports/server.py` preserves the staging cream/sage visual system.
- `api/routes/bodygraph.py` now exposes the same field descriptions in `meta.field_descriptions` and adds a structured `activations` array for professional planet/gate rendering.

## Remaining scope

- Some requested fields depend on upstream engine data. When a field is not yet returned by the calculation engine, the report renders `Pending in engine` instead of hiding the field.
- Guest runtime, skills, and education pages should consume the same field vocabulary next so all HDE-oriented activities stay consistent.
- Final design approval and paid Telegram `/start` proof remain separate launch gates.
