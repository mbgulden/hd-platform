# GRO-154: Interactive Human Design Bodygraph Engine — Design Document

**Status:** Design Blueprint  
**Dependencies:** `compute_natal_chart()` (OpenHumanDesignMCP engine → `api/routes/natal.py`)  
**Feeds into:** GRO-159 (Bodygraph API endpoint), Frontend Web Component implementation  
**Last updated:** 2026-05-30

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [SVG Architecture & Rendering Strategy](#2-svg-architecture--rendering-strategy)
3. [Layout Specifications](#3-layout-specifications)
4. [Color Scheme & Visual Semantics](#4-color-scheme--visual-semantics)
5. [Data Model — Engine Output to Visual Mapping](#5-data-model--engine-output-to-visual-mapping)
6. [The `bodygraph-payload` JSON Contract (GRO-159 output)](#6-the-bodygraph-payload-json-contract)
7. [Interactive Features Specification](#7-interactive-features-specification)
8. [Technology Choices](#8-technology-choices)
9. [Web Component API Design](#9-web-component-api-design)
10. [Performance & Mobile Considerations](#10-performance--mobile-considerations)
11. [Implementation Plan](#11-implementation-plan)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    ENGINE (Python)                            │
│  cosmic_calculator.py → calculate_natal_chart()              │
│  matrix_mapper.py     → GATE_NAMES, GATE_CENTER, CHANNELS   │
└─────────────────────┬────────────────────────────────────────┘
                      │ full chart dict
                      ▼
┌──────────────────────────────────────────────────────────────┐
│              GRO-159: Bodygraph API Endpoint                  │
│  /v1/natal/:id/bodygraph                                     │
│  Transforms engine output → bodygraph-payload JSON           │
└─────────────────────┬────────────────────────────────────────┘
                      │ bodygraph-payload (JSON)
                      ▼
┌──────────────────────────────────────────────────────────────┐
│         <hd-bodygraph> Web Component (Frontend)              │
│  Renders interactive SVG from payload                        │
│  Handles hover, tap, zoom, tooltips                          │
│  Emits custom events for gateway to detail pages             │
└──────────────────────────────────────────────────────────────┘
```

The interactive bodygraph is a **pure SVG rendered in the browser** via a Web Component. It receives a JSON payload defining what's active/inactive/defined in the chart, and the SVG layout is pre-defined with all 9 centers, 64 gates, and 36 channels positioned in `data-*` attributes. Active elements get CSS classes that drive the color scheme.

---

## 2. SVG Architecture & Rendering Strategy

### 2.1 Why SVG (not Canvas)

| Concern | SVG | Canvas |
|---------|-----|--------|
| **Interactive hit-testing** | Native — elements are DOM nodes with event handlers | Manual — need spatial index to map pixel coords to gates |
| **Tooltips/DOM overlays** | Trivial — attach to SVG elements | Requires projected coordinate math |
| **Responsive scaling** | `viewBox` handles resize automatically | Manual resize + redraw |
| **Accessibility** | ARIA roles, focusable elements, screen-reader labels | Requires shadow DOM fallback layer |
| **Styling by chart data** | CSS classes on SVG elements; inline via CSS custom properties | All styling done in draw calls |
| **Zoom/pan** | CSS `transform` or viewBox manipulation | Manual matrix transforms |

**Decision: SVG.** The bodygraph has exactly 109 interactive elements (9 centers + 64 gates + 36 channels) — well within SVG DOM performance limits. Canvas would be premature optimization.

### 2.2 SVG Structure

```xml
<svg viewBox="0 0 400 600" class="bodygraph" role="img" aria-label="Human Design Bodygraph">
  <!-- Static definitions (reusable) -->
  <defs>
    <!-- Center shape definitions -->
    <!-- Drop-shadow filters for defined centers -->
    <!-- Hatch patterns for half-defined channels -->
    <filter id="glow-defined">...</filter>
  </defs>

  <!-- Layer 1: Channels (lines, drawn first — behind everything) -->
  <g class="channels-layer">
    <line class="channel channel-1-8" data-channel="1-8" data-from="1" data-to="8" ... />
    <!-- 36 channels total -->
  </g>

  <!-- Layer 2: Gates (circles around center perimeters) -->
  <g class="gates-layer">
    <circle class="gate gate-1" data-gate="1" data-center="G" data-side="personality" ... />
    <!-- 64 gates total, each appears once -->
  </g>

  <!-- Layer 3: Gate number labels -->
  <g class="gate-labels-layer">
    <text class="gate-label gate-label-1" ...>1</text>
    <!-- 64 labels -->
  </g>

  <!-- Layer 4: Center shapes (drawn on top so channel lines are behind) -->
  <g class="centers-layer">
    <path class="center center-head" data-center="Head" ... />
    <!-- 9 centers -->
  </g>

  <!-- Layer 5: Center labels -->
  <g class="center-labels-layer">
    <text class="center-label center-label-head" ...>HEAD</text>
    <!-- 9 labels -->
  </g>

  <!-- Layer 6: Tooltip overlay (positioned via JS) -->
  <foreignObject class="tooltip" visibility="hidden">...</foreignObject>
</svg>
```

### 2.3 Class-Based Styling Strategy

The SVG is pre-rendered with **all elements present** (all 64 gates, all 36 channels, all 9 centers). Active/inactive state is controlled entirely via CSS classes applied by the Web Component based on the payload:

```html
<!-- Defined center → colored with glow -->
<path class="center center-head defined" data-center="Head" />

<!-- Undefined center → white outline -->
<path class="center center-sacral undefined" data-center="Sacral" />

<!-- Open center → white, no outline emphasis -->
<path class="center center-root open" data-center="Root" />

<!-- Active gate with personality (conscious) activation — black -->
<circle class="gate gate-1 active personality" data-gate="1" />

<!-- Active gate with design (unconscious) activation — red -->
<circle class="gate gate-5 active design" data-gate="5" />

<!-- Gate active in BOTH personality and design — split fill -->
<circle class="gate gate-10 active both" data-gate="10" />

<!-- Inactive gate — dimmed -->
<circle class="gate gate-64 inactive" data-gate="64" />

<!-- Defined channel (both gates active) — solid colored line -->
<line class="channel channel-1-8 defined" data-channel="1-8" />

<!-- Half-defined channel (one gate active) — dashed partial line -->
<line class="channel channel-7-31 half-defined hanging-7" data-channel="7-31" />

<!-- Undefined channel — transparent/hidden -->
<line class="channel channel-10-20 undefined" data-channel="10-20" />
```

---

## 3. Layout Specifications

### 3.1 ViewBox Coordinate System

- **ViewBox:** `0 0 400 600`
- **Origin:** Top-left
- **Y-axis:** Top-to-bottom (Head at top, Root at bottom)
- **All coordinates** specified in this 400×600 space. The SVG scales responsively via `viewBox` — no media queries needed for layout, only for tooltip font sizes and touch targets.

### 3.2 Center Positions & Shapes

Each center is one of three shapes: **triangle** (Head, Root), **square/diamond** (Ajna, Throat, G, Sacral, Spleen, Solar Plexus), or **small triangle** (Heart/Ego).

| Center | Shape | Center (x, y) | Width | Height | Notes |
|--------|-------|---------------|-------|--------|-------|
| **Head** | Triangle (pointing up) | (200, 40) | 80 | 60 | Flat base at bottom, apex at top |
| **Ajna** | Diamond | (200, 120) | 90 | 55 | Rounded diamond, horizontally oriented |
| **Throat** | Square | (200, 220) | 100 | 70 | Rounded square, gateway of expression |
| **G** | Diamond | (200, 310) | 72 | 72 | Rotated 45°, identity seat |
| **Heart/Ego** | Small triangle | (135, 360) | 50 | 40 | Right of G, pointing right |
| **Sacral** | Square | (200, 420) | 72 | 72 | Large square, life-force engine |
| **Spleen** | Triangle (pointing left) | (100, 370) | 50 | 65 | Left of Sacral |
| **Solar Plexus** | Triangle (pointing right) | (300, 370) | 50 | 65 | Right of Sacral |
| **Root** | Triangle (pointing down) | (200, 530) | 80 | 60 | Flat base at top, apex at bottom |

### 3.3 Gate Positions

Gates are positioned as small circles (radius=8) on the perimeter of their parent center. Each gate sits on the edge of the center shape at a specific angular position.

**Gate-to-Center Mapping** (from `matrix_mapper.py:GATE_CENTER`):

| Center | Gates | Count |
|--------|-------|-------|
| Head | 61, 63, 64 | 3 |
| Ajna | 4, 11, 17, 24, 43, 47 | 6 |
| Throat | 8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62 | 11 |
| G | 1, 2, 7, 10, 13, 15, 25, 46 | 8 |
| Heart/Ego | 21, 26, 40, 51 | 4 |
| Sacral | 3, 5, 9, 14, 27, 29, 34, 42, 59 | 9 |
| Spleen | 18, 28, 32, 44, 48, 50, 57 | 7 |
| Solar Plexus | 6, 22, 30, 36, 37, 39, 49, 55 | 8 |
| Root | 19, 38, 41, 52, 53, 54, 58, 60 | 8 |

Each gate's position is computed as:

```
angle = gate_index / total_gates_for_center * 2π + center_rotation_offset
gate_x = center_x + (center_width/2 + gate_radius + 2) * cos(angle)
gate_y = center_y + (center_height/2 + gate_radius + 2) * sin(angle)
```

Gate indices are numbered sequentially around the center in clockwise order (see full gate position table in implementation appendix).

### 3.4 Channel Paths

36 channels connect gates between centers. A channel is a **bezier curve** (`<path d="M... C...">`) from the source gate position to the destination gate position. Straight lines look too mechanical — gentle curves give the bodygraph its organic feel.

**Channel Data** (from `matrix_mapper.py:CHANNELS`, 36 total):

Key channels and their endpoints:

| Channel | Gate A | Center A | Gate B | Center B |
|---------|--------|----------|--------|----------|
| 1-8 Inspiration | 1 | G | 8 | Throat |
| 2-14 The Beat | 2 | G | 14 | Sacral |
| 3-60 Mutation | 3 | Sacral | 60 | Root |
| 4-63 Logic | 4 | Ajna | 63 | Head |
| 5-15 Rhythm | 5 | Sacral | 15 | G |
| 6-59 Mating | 6 | Solar Plexus | 59 | Sacral |
| 7-31 The Alpha | 7 | G | 31 | Throat |
| 9-52 Concentration | 9 | Sacral | 52 | Root |
| 10-20 Awakening | 10 | G | 20 | Throat |
| 10-34 Exploration | 10 | G | 34 | Sacral |
| 10-57 Perfected Form | 10 | G | 57 | Spleen |
| 11-56 Curiosity | 11 | Ajna | 56 | Throat |
| 12-22 Openness | 12 | Throat | 22 | Solar Plexus |
| 13-33 The Prodigal | 13 | G | 33 | Throat |
| 16-48 Talent | 16 | Throat | 48 | Spleen |
| 17-62 Acceptance | 17 | Ajna | 62 | Throat |
| 18-58 Judgment | 18 | Spleen | 58 | Root |
| 19-49 Synthesis | 19 | Root | 49 | Solar Plexus |
| 20-34 Charisma | 20 | Throat | 34 | Sacral |
| 20-57 Brainwave | 20 | Throat | 57 | Spleen |
| 21-45 Money | 21 | Heart/Ego | 45 | Throat |
| 23-43 Structuring | 23 | Throat | 43 | Ajna |
| 24-61 Awareness | 24 | Ajna | 61 | Head |
| 25-51 Initiation | 25 | G | 51 | Heart/Ego |
| 26-44 Surrender | 26 | Heart/Ego | 44 | Spleen |
| 27-50 Preservation | 27 | Sacral | 50 | Spleen |
| 28-38 Struggle | 28 | Spleen | 38 | Root |
| 29-46 Discovery | 29 | Sacral | 46 | G |
| 30-41 Recognition | 30 | Solar Plexus | 41 | Root |
| 32-54 Transformation | 32 | Spleen | 54 | Root |
| 34-57 Power | 34 | Sacral | 57 | Spleen |
| 35-36 Transitoriness | 35 | Throat | 36 | Solar Plexus |
| 37-40 Community | 37 | Solar Plexus | 40 | Heart/Ego |
| 39-55 Emoting | 39 | Solar Plexus | 55 | Solar Plexus |
| 42-53 Maturation | 42 | Sacral | 53 | Root |
| 47-64 Abstraction | 47 | Ajna | 64 | Head |

### 3.5 Incarnation Cross Display

Below the bodygraph, a text element displays:
```
Incarnation Cross: Right Angle Cross of the Sphinx (1/2 | 7/13)
```

Position: centered below the Root center at y=590, font-size: 11px.

### 3.6 Labels: Type, Authority, Strategy, Profile

Four labels displayed as a row above the bodygraph (or below on narrow mobile):

```
Type: Generator  ·  Authority: Sacral  ·  Strategy: To Respond  ·  Profile: 3/5
```

---

## 4. Color Scheme & Visual Semantics

### 4.1 Design Tokens (CSS Custom Properties)

```css
:root {
  /* Defined centers — rich color per center type */
  --color-head:          #F5E960;   /* Yellow */
  --color-ajna:          #4CAF50;   /* Green */
  --color-throat:        #9C27B0;   /* Purple */
  --color-g:             #FF9800;   /* Orange */
  --color-heart-ego:     #E91E63;   /* Pink */
  --color-sacral:        #D32F2F;   /* Red */
  --color-spleen:        #795548;   /* Brown */
  --color-solar-plexus:  #2196F3;   /* Blue */
  --color-root:          #607D8B;   /* Blue-grey */

  /* Activation colors */
  --color-personality:   #1a1a2e;   /* Black — conscious/sun */
  --color-design:        #c62828;   /* Dark red — unconscious/design */
  --color-both:          #4a148c;   /* Deep purple — both active */

  /* Undefined/open */
  --color-undefined:     #ffffff;
  --color-undefined-stroke: #bdbdbd;
  --color-open:          #fafafa;
  --color-open-stroke:   #e0e0e0;

  /* Inactive */
  --color-inactive-gate: #e0e0e0;
  --color-inactive-channel: #e8e8e8;

  /* Hanging gate */
  --color-hanging-gate:  #ffb74d;   /* Amber accent */
}
```

### 4.2 Center Fill Rules

| State | Fill | Stroke | Stroke Width | Glow |
|-------|------|--------|-------------|------|
| **Defined** | Center color at 85% opacity | Center color at 100% | 2px | `drop-shadow(0 0 6px center-color)` |
| **Undefined** | `#ffffff` | `#bdbdbd` | 1.5px | None |
| **Open** | `#fafafa` | `#e0e0e0` | 1px | None |

A center is **defined** if any channel connecting it is defined (both gates active).  
A center is **undefined** if it has active gates but no defined channel.  
A center is **open** if it has no active gates at all.

### 4.3 Gate Fill Rules

| State | Fill | Stroke | Radius |
|-------|------|--------|--------|
| **Active — Personality only** | `#1a1a2e` (black) | none | 8 |
| **Active — Design only** | `#c62828` (red) | none | 8 |
| **Active — Both** | Split: left half `#1a1a2e`, right half `#c62828` | none | 8 |
| **Inactive** | `#e0e0e0` | `#bdbdbd` | 6 |
| **Hanging gate** (one gate of channel active, partner inactive) | Accent ring outside normal circle | `#ffb74d` ring | 8 (+ 3px ring) |

### 4.4 Channel Line Rules

| State | Stroke | Stroke Width | Dash | Opacity |
|-------|--------|-------------|------|---------|
| **Defined** | `#1a1a2e` (or center color blend) | 2.5px | none | 1.0 |
| **Half-defined** | Gradient from active gate color → faded | 2px | `4,4` (dashed) | 0.6 |
| **Undefined** | `#e0e0e0` | 1px | none | 0.3 |

For defined channels, the line color is a blend:
- Channel connecting two defined centers → black (`#1a1a2e`)
- Channel within same center → center color
- A natural midpoint gradient feels optional; simple black works well and is the Jovian Archive standard.

### 4.5 Dark Mode

A `data-theme="dark"` attribute on the `<hd-bodygraph>` component toggles:
- Background: `#1a1a2e`
- Undefined center fill: `#2d2d44`
- Open center fill: `#262638`
- Inactive gates: `#3a3a5c`
- Defined channel lines: `#f5f5f5`
- Personality (conscious): `#ffffff` (white)
- Design (unconscious): `#ef5350` (bright red)

---

## 5. Data Model — Engine Output to Visual Mapping

### 5.1 Source: `calculate_natal_chart()` Output

The engine returns a dict with these bodygraph-relevant fields:

```python
{
    # Core identity
    "hd_type": "Generator",
    "strategy": "To Respond",
    "authority": "Sacral",
    "signature": "Satisfaction",
    "not_self_theme": "Frustration",
    "profile": "3/5",
    "definition": "Single",

    # Centers
    "defined_centers": ["Sacral", "G", "Throat"],
    "undefined_centers": ["Head", "Ajna", "Heart/Ego", "Spleen", "Solar Plexus", "Root"],

    # Channels
    "defined_channels": [
        {"gates": (1, 8), "name": "Inspiration (Individual)"},
        {"gates": (10, 20), "name": "Awakening (Individual)"},
    ],

    # Gates — just the numbers
    "all_active_gates": [1, 5, 8, 10, 14, 20, 34, 42, 59],
    "personality_gates": [1, 8, 10, 14, 42],
    "design_gates": [5, 10, 20, 34, 59],

    # Planetary detail (for advanced tooltips)
    "personality_planets": {
        "Sun": {"gate": 1, "line": 3, "color": 4, "tone": 2, "base": 1, "gate_name": "Self-Expression", "center": "G", "longitude": 12.345},
        "Earth": {"gate": 2, "line": 3, ...},
        "Moon": {"gate": 14, "line": 5, ...},
        ...
    },
    "design_planets": {
        "Sun": {"gate": 10, "line": 6, ...},
        ...
    },

    # Incarnation Cross
    "incarnation_cross": {
        "name": "Right Angle Cross of the Sphinx",
        "sun_gate": 1,
        "earth_gate": 2,
        "design_sun_gate": 7,
        "design_earth_gate": 13,
        "population_percent": "~1.5%"
    },

    # Variables
    "variables": ["PRL", "DRL", ...],
    "digestion": "Alternating",
    "environment": "Mountains Active",
    "perspective": "Personal",
    "motivation": "Hope",
}
```

### 5.2 Mapping Engine Output → SVG Classes

```
ENGINE FIELD                    → SVG CLASS / RENDERING
─────────────────────────────────────────────────────────
defined_centers                 → .center.defined (colored fill)
undefined_centers               → .center.undefined (white outline)
(centers not in either list)    → .center.open (white, faint outline)

defined_channels[n].gates       → .channel.channel-{a}-{b}.defined (solid colored line)

personality_gates               → .gate.gate-{n}.active.personality
design_gates minus personality  → .gate.gate-{n}.active.design
personality_gates ∩ design_gates → .gate.gate-{n}.active.both

Hanging gates:
  gate in all_active_gates AND
  gate is part of a channel where
  partner gate NOT in all_active_gates
                                → .gate.gate-{n}.active.hanging

(Gates not in all_active_gates) → .gate.gate-{n}.inactive

Channels where exactly one gate
is active:
                                → .channel.channel-{a}-{b}.half-defined.hanging-{gate}
```

### 5.3 Hanging Gate Detection Algorithm

```python
def find_hanging_gates(all_active_gates, channels):
    """Return gates that have a channel partner but lack the partner."""
    hanging = set()
    active_set = set(all_active_gates)
    for (g1, g2), channel_name in channels.items():
        if g1 in active_set and g2 not in active_set:
            hanging.add(g1)
        elif g2 in active_set and g1 not in active_set:
            hanging.add(g2)
    return hanging
```

---

## 6. The `bodygraph-payload` JSON Contract

This is what GRO-159 (`/v1/natal/:id/bodygraph`) returns. It's a **pre-computed** version of the engine output, flattened into what the frontend needs — no duplicate logic in JavaScript.

```jsonc
{
  "name": "Alice Example",
  "hd_type": "Generator",
  "strategy": "To Respond",
  "authority": "Sacral",
  "signature": "Satisfaction",
  "not_self_theme": "Frustration",
  "profile": "3/5",
  "definition": "Single",

  "incarnation_cross": {
    "name": "Right Angle Cross of the Sphinx",
    "population_percent": "~1.5%"
  },

  // Centers: one entry per of the 9 centers
  "centers": [
    { "name": "Head",    "state": "undefined" },
    { "name": "Ajna",    "state": "open" },
    { "name": "Throat",  "state": "defined" },
    { "name": "G",       "state": "defined" },
    { "name": "Heart/Ego", "state": "undefined" },
    { "name": "Sacral",  "state": "defined" },
    { "name": "Spleen",  "state": "open" },
    { "name": "Solar Plexus", "state": "undefined" },
    { "name": "Root",    "state": "undefined" }
  ],

  // Gates: one entry per active gate
  "gates": [
    { "gate": 1,  "activation": "personality", "hanging": false, "center": "G",       "name": "Self-Expression", "line": 3 },
    { "gate": 5,  "activation": "design",      "hanging": false, "center": "Sacral",  "name": "Fixed Rhythms", "line": 5 },
    { "gate": 8,  "activation": "personality", "hanging": false, "center": "Throat",  "name": "Contribution", "line": 5 },
    { "gate": 10, "activation": "both",        "hanging": false, "center": "G",       "name": "Behavior of the Self", "line": 3 },
    { "gate": 14, "activation": "personality", "hanging": false, "center": "Sacral",  "name": "Power Skills", "line": 2 },
    { "gate": 20, "activation": "design",      "hanging": false, "center": "Throat",  "name": "The Now", "line": 6 },
    { "gate": 34, "activation": "design",      "hanging": false, "center": "Sacral",  "name": "Power", "line": 1 },
    { "gate": 42, "activation": "personality", "hanging": false, "center": "Sacral",  "name": "Growth", "line": 4 },
    { "gate": 59, "activation": "design",      "hanging": true,  "center": "Sacral",  "name": "Sexuality", "line": 3 }
  ],

  // Channels: one entry per channel definition
  "channels": [
    { "gates": "1-8",   "name": "Inspiration",       "state": "defined" },
    { "gates": "10-20", "name": "Awakening",          "state": "defined" },
    { "gates": "5-15",  "name": "Rhythm",             "state": "half-defined", "hanging_gate": 5 },
    { "gates": "2-14",  "name": "The Beat",           "state": "half-defined", "hanging_gate": 14 },
    // ... remaining 32 channels with state: "undefined"
  ],

  // Variables (for detail display)
  "variables": {
    "digestion": "Alternating",
    "environment": "Mountains Active"
  }
}
```

**`state` enum for centers:** `"defined"` | `"undefined"` | `"open"`  
**`activation` enum for gates:** `"personality"` | `"design"` | `"both"`  
**`state` enum for channels:** `"defined"` | `"half-defined"` | `"undefined"`  

---

## 7. Interactive Features Specification

### 7.1 Gate Hover/Tap → Tooltip

**Trigger:** `pointerenter` / `pointerleave` on `.gate` elements  
**Mobile fallback:** `click` toggles tooltip; `click` elsewhere dismisses  

**Tooltip content:**
```
Gate 10: Behavior of the Self
Line 3: Treading
Center: G (Identity)
Activation: Personality + Design (conscious & unconscious)
```

Tooltip is a `<foreignObject>` positioned near the gate, containing formatted HTML. The tooltip data is pre-computed in the payload (gate names, line numbers, center names are all in `gates[]`).

### 7.2 Channel Hover → Channel Info

**Trigger:** `pointerenter` on `.channel` elements  
**Content:**
```
Channel 10-20: Awakening (Individual)
Connects: G Center → Throat Center
Status: Defined
```

### 7.3 Center Click → Center Detail

**Trigger:** `click` on `.center` elements  
**Action:** Emits custom event `bodygraph:center-click` with `{ center: "Sacral", state: "defined" }`. Parent page can listen and show a detail panel. Falls back to dispatching a navigation or opening a modal.

### 7.4 Zoom/Pan (Mobile)

**Implementation:** CSS `transform: scale()` on the SVG container.  
- Pinch-to-zoom: touch event handler modifies scale factor (0.5× to 3×).  
- Single-finger pan: `translate()` offset when zoomed in.  
- Double-tap: toggle between 1× and 2× zoom.  
- Reset button: returns to fit-to-container view.

Alternatively, this can leverage a wrapper library like `panzoom` (3KB) for better gesture handling.

### 7.5 Keyboard Accessibility

- **Tab navigation:** Each gate, center, and channel is focusable (`tabindex="0"`).
- **Enter/Space on gate:** Show tooltip.
- **Enter/Space on center:** Trigger center detail.
- **Escape:** Dismiss any open tooltip.
- **Arrow keys:** Navigate between adjacent gates.
- **`role="application"`** with `aria-label` describing the chart type and name.

### 7.6 Hover Visual Feedback

- **Gate hover:** Stroke highlight ring (gold, 2px) + subtle scale(1.15) transition.
- **Channel hover:** Stroke width increases from 2.5px → 4px, color brightens.
- **Center hover:** Slight glow intensification.
- All transitions: `200ms ease-out`.

---

## 8. Technology Choices

### 8.1 Web Component (`<hd-bodygraph>`)

A self-contained Custom Element (no framework dependency):

```html
<hd-bodygraph
  payload='{...}'
  theme="light"
  interactive="true"
  show-cross="true"
  show-variables="true">
</hd-bodygraph>
```

**Why Web Component:**
- Framework-agnostic — works in React, Vue, Svelte, or plain HTML
- Encapsulated via Shadow DOM (no style leaks)
- The HD Platform can embed it in marketing pages, dashboards, and widgets identically
- Smaller bundle than dragging in a full UI framework
- Native lazy-loading: define + register once, use everywhere

### 8.2 Implementation Options

| Approach | Bundle Size | Complexity | Recommendation |
|----------|------------|------------|----------------|
| **Vanilla JS + Custom Elements v1** | ~8KB gzipped | Medium | ✅ **Preferred** |
| **Lit (lit.dev)** | ~5KB + ~5KB Lit core | Low | Good if team knows Lit |
| **React component** | Depends on React | Low | Only if frontend is already React |
| **Canvas (Konva/Fabric)** | ~50KB+ | High | ❌ Overkill for 109 elements |

### 8.3 Build Pipeline

- **Source:** TypeScript (`.ts`) compiled to ES2020 JS module
- **Bundler:** esbuild (fast, small output)
- **Output:** Single `.js` file (`hd-bodygraph.js`), ~15KB gzipped
- **CSS:** Inlined in the component via `constructible stylesheets` or `<style>` in shadow root
- **No runtime dependencies** beyond the component itself

### 8.4 Static SVG Fallback

For non-interactive contexts (email, PDF, static site), the bodygraph can also be rendered server-side as a flat SVG image (no JavaScript). The GRO-159 endpoint can optionally return the SVG string directly when requested with `Accept: image/svg+xml` or `?format=svg`.

---

## 9. Web Component API Design

### 9.1 Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `payload` | JSON string | Required | The bodygraph-payload (see §6) |
| `theme` | `"light"` \| `"dark"` | `"light"` | Color theme |
| `interactive` | boolean | `true` | Enable tooltips, click handlers |
| `show-cross` | boolean | `true` | Show incarnation cross label |
| `show-labels` | boolean | `true` | Show center name labels |
| `zoomable` | boolean | `true` | Enable pinch/pan zoom |
| `compact` | boolean | `false` | Compact mode — smaller, fewer labels (for widget embedding) |

### 9.2 Custom Events

| Event | Detail | When |
|-------|--------|------|
| `bodygraph:gate-click` | `{ gate, name, center, activation }` | Gate clicked/tapped |
| `bodygraph:center-click` | `{ center, state }` | Center clicked |
| `bodygraph:channel-click` | `{ channel, name, state }` | Channel clicked |
| `bodygraph:ready` | `{}` | Component mounted and rendered |

### 9.3 Methods (optional, accessed via `element.method()`)

| Method | Description |
|--------|-------------|
| `updatePayload(json)` | Replace chart data without re-creating component |
| `resetZoom()` | Reset to default view |
| `zoomToFit()` | Zoom to fit container |
| `getSVGString()` | Export current SVG as string (for sharing/saving) |
| `toDataURL()` | Export as PNG data URL (via canvas conversion) |

### 9.4 Usage Example

```html
<!-- In any HTML page -->
<script type="module" src="/components/hd-bodygraph.js"></script>

<hd-bodygraph
  id="my-chart"
  theme="dark"
  interactive="true">
</hd-bodygraph>

<script>
  const chart = document.getElementById('my-chart');

  // Load chart data
  fetch('/v1/natal/alice/bodygraph')
    .then(res => res.json())
    .then(data => {
      chart.payload = JSON.stringify(data);
    });

  // Listen for interactions
  chart.addEventListener('bodygraph:gate-click', (e) => {
    console.log('Gate clicked:', e.detail);
    showGateDetailPanel(e.detail.gate);
  });
</script>
```

---

## 10. Performance & Mobile Considerations

### 10.1 SVG DOM Size

- 9 center paths
- 64 gate circles + 64 text labels = 128 elements
- 36 channel lines/paths
- 1 tooltip `<foreignObject>`
- **Total: ~175 DOM nodes** — trivially fast on any device from 2015+

### 10.2 Responsive Strategy

The `viewBox="0 0 400 600"` on the SVG handles all scaling. The component observes its container width via `ResizeObserver` and sets the SVG to 100% width with auto height:

```css
:host {
  display: block;
  width: 100%;
  max-width: 500px;  /* cap for large screens */
  margin: 0 auto;
}
svg {
  width: 100%;
  height: auto;
}
```

### 10.3 Touch Targets

- Gates: default radius 8px → 16px diameter. At 400px viewBox width on a 375px phone screen, this is ~15 CSS px. **Increase touch target with a transparent outer circle (radius 14) that handles events**, with the visible circle at radius 8.
- Channels: thin lines are hard to tap. **Add a transparent wider stroke** (`stroke-width="12" stroke="transparent"`) behind each visible channel to increase the hit area.

### 10.4 Initial Load

- Component size: ~15KB gzipped
- Payload size: ~3-5KB for a typical chart
- **Total: ~20KB** — loads in under 100ms on 4G
- No API call needed if payload is server-rendered into the page (SSR/SSG)

### 10.5 Re-render Optimization

When `payload` changes (e.g., transit overlay), the component diffs the old and new states:
- Only change CSS classes (add/remove `defined`, `undefined`, etc.) — no DOM rebuild
- This is near-instant (<1ms for classList changes on 175 elements)

---

## 11. Implementation Plan

### Phase 1: Layout Constants & Reference SVG

1. Produce a **static reference SVG** with all 9 centers, 64 gates, and 36 channels correctly positioned using the coordinate system in §3.
2. Hard-code all gate positions (x, y) — ~64 values. Generate from the angular-positioning formula.
3. Hard-code all channel paths (bezier curves) — ~36 values.
4. Verify the reference SVG renders correctly at 400×600 viewBox.

### Phase 2: GRO-159 Bodygraph Payload Endpoint

1. Create `/v1/natal/{chart_id}/bodygraph` endpoint in `api/routes/natal.py`.
2. Accept a previously computed chart (stored in DB or passed as reference) and transform it to the `bodygraph-payload` format defined in §6.
3. Implement hanging gate detection and center state classification.
4. Embed gate metadata (name, line, center) from `GATE_NAMES` and `GATE_CENTER`.

### Phase 3: `<hd-bodygraph>` Web Component

1. Create `hd-bodygraph.ts` (TypeScript → compiled to JS).
2. Implement SVG template with all static elements + `data-*` attributes.
3. Implement `applyPayload()` — maps payload to CSS classes on SVG elements.
4. Implement tooltip system (pointer events, keyboard).
5. Implement zoom/pan (optional, can be v1.1).

### Phase 4: Integration & Polish

1. Add dark mode CSS.
2. Add transition animations (gate hover, center glow).
3. Add keyboard navigation.
4. Add static SVG export (`?format=svg`).
5. Performance testing and mobile touch-target tuning.

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `docs/hd-engine/interactive-bodygraph-design.md` | This document |
| `api/routes/bodygraph.py` | GRO-159: Bodygraph payload endpoint |
| `frontend/src/components/hd-bodygraph.ts` | Web Component source |
| `frontend/src/components/hd-bodygraph.css` | Component styles (or inline) |
| `frontend/dist/hd-bodygraph.js` | Built component |
| `docs/hd-engine/bodygraph-reference.svg` | Static reference SVG for testing |

---

## Appendix A: Full Gate Position Table

Each gate's approximate position on its parent center (angles in degrees, 0° = right, clockwise). Precise positions will be computed in the reference SVG generator.

*(Full 64-row table to be generated in Phase 1 implementation.)*

## Appendix B: Gate Descriptions Reference

Gate descriptions are stored in `scripts/gates_data.json` (64 entries, each with `name`, `hex`, and `snippet` fields). These power the tooltip content. The `bodygraph-payload` includes a subset (gate name); full snippet text is only loaded if the user clicks through to a detail page.

## Appendix C: Engine Field Reference

See `cosmic_calculator.py:calculate_natal_chart()` return dict (lines 929-990) for the full engine output schema. See `matrix_mapper.py` (lines 1-150) for `GATE_NAMES`, `GATE_CENTER`, and `CHANNELS` constants used in payload construction.
