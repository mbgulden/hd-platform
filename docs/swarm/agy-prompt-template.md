# AGY / Antigravity CLI Prompt Template (GRO-79)

Use this template when delegating research, analysis, content strategy, or Drive/Takeout
investigation tasks to AGY. AGY is **not** for open-ended exploration — every prompt
must define a bounded scope.

---

## Template

```yaml
# ── AGY Prompt ──────────────────────────────────────────────
# Copy this block, fill in the blanks, and pass to AGY.

goal: >
  # [ONE SENTENCE] The specific research question or analysis to perform.
  # BAD:  "Look into competitor stuff."
  # GOOD: "Compare pricing pages of our top 3 competitors and identify
  #        features they offer that we don't."

output_format:
  # [REQUIRED] What shape should the deliverable take?
  # Options: markdown_report | spreadsheet | slide_deck | json_data | prose_summary
  # Example: markdown_report

bounded_scope:
  # [REQUIRED] Explicit boundaries. AGY is NOT open-ended.
  # Define what IS in scope and what IS NOT.
  in_scope:
    # - "Competitor A, B, and C public pricing pages only"
    # - "Q1 and Q2 2026 pricing data"
    # - "SaaS-specific features (ignore enterprise/on-prem)"
  out_of_scope:
    # - "Do NOT analyze free tiers"
    # - "Do NOT pull data from third-party review sites"
    # - "Do NOT contact competitors or use scrapers that require auth"
  stop_after: ""
    # [OPTIONAL] Hard stop condition.
    # Example: "3 hours wall-clock" or "after processing 50 competitor pages"

deliverable_path: ""
  # [REQUIRED] Where to write the final output.
  # Example: "output/research/q2-competitor-pricing.md"
  # AGY will create parent directories if needed.

max_sessions: 1
  # [OPTIONAL] Max sub-sessions AGY can spawn (default: 1).
  # Increase for large research tasks that benefit from parallel exploration.
  # Range: 1–5. Higher values = more API cost.

context_links:
  # [OPTIONAL] Reference material already gathered.
  # - "https://drive.google.com/file/d/xxx"  # Drive doc with background
  # - "https://linear.app/issue/REL-42"       # Related Linear issue
  # - "file://data/research/q1-pricing.json"  # Local data to build on

style_notes: ""
  # [OPTIONAL] Tone, audience, or formatting preferences.
  # Example: "Executive summary first, board-ready, no jargon"
```

---

## Field Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `goal` | **Yes** | Specific research question; must be answerable |
| `output_format` | **Yes** | Determines AGY's tool selection and output structure |
| `bounded_scope` | **Yes** | The single most important field — prevents scope creep |
| `deliverable_path` | **Yes** | Where the file lands; used by orchestrator for verification |
| `max_sessions` | Optional | Parallelism control; default 1 is safest |
| `context_links` | Recommended | Saves AGY from re-discovering known material |
| `style_notes` | Optional | Shapes the final deliverable for its audience |

---

## Example

### Competitor Analysis (typical AGY task)

```yaml
goal: >
  Analyze Q2 2026 pricing changes across our top 3 SaaS competitors
  (NexusCloud, DataForge, Streamline) and recommend adjustments to
  our Pro and Enterprise tiers.

output_format: markdown_report

bounded_scope:
  in_scope:
    - "Public pricing pages for NexusCloud, DataForge, Streamline"
    - "Q2 2026 changes only (April–June)"
    - "Pro and Enterprise equivalent tiers"
    - "Feature comparison: what do they include that we don't?"
  out_of_scope:
    - "Free tiers or starter plans"
    - "On-premise / self-hosted pricing"
    - "Historical pricing before Q2 2026"
    - "Third-party review sentiment"
  stop_after: "2 hours wall-clock"

deliverable_path: "output/research/q2-2026-competitor-pricing.md"
max_sessions: 3

context_links:
  - "https://drive.google.com/file/d/abc123"  # Q1 competitor baseline
  - "https://linear.app/issue/GRW-87"          # Board request issue

style_notes: >
  Board-ready executive summary first.
  Bullet points over paragraphs.
  Include a 2x2 price-vs-features matrix if data supports it.
```

### Content Audit (Drive/Takeout task)

```yaml
goal: >
  Audit our last 30 blog posts for SEO performance: identify the top 5
  by organic traffic and the bottom 5 that need rewriting.

output_format: spreadsheet

bounded_scope:
  in_scope:
    - "Blog posts published Jan–May 2026 (30 total)"
    - "Organic traffic from GSC only"
    - "Keyword rankings for primary target keyword of each post"
  out_of_scope:
    - "Social media traffic"
    - "Email-driven traffic"
    - "Redesign recommendations (just flag for rewrite)"
  stop_after: "1 hour wall-clock"

deliverable_path: "output/research/blog-seo-audit-may-2026.csv"
max_sessions: 1

context_links:
  - "https://drive.google.com/file/d/def456"  # GSC export CSV

style_notes: "CSV with columns: URL, title, organic_clicks, primary_kw, kw_position, action (keep/rewrite)"
```

---

## Anti-Patterns (Do NOT Do This)

```yaml
# ❌ BAD — open-ended, no scope, no deliverable path
goal: "Research the market and tell me what you find."
output_format: prose_summary
bounded_scope:
  in_scope: ["Everything interesting"]
  out_of_scope: []
deliverable_path: ""    # Where does this go?!

# ❌ BAD — scope is effectively unlimited
bounded_scope:
  in_scope:
    - "All competitors globally"
    - "All time periods"
    - "All product categories"
  out_of_scope: []
  # No stop_after — this runs until it runs out of tokens or crashes
```

Fix these by:
- Narrowing `goal` to a single answerable question
- Populating `out_of_scope` with at least 2 items
- Setting a `stop_after` wall-clock limit
- Specifying `deliverable_path`

---

## Integration with Orchestration Router

When the router delegates to AGY:
1. It translates `task-intake` fields into this AGY prompt format.
2. `goal` maps directly.
3. `output_format` is inferred from `verification_criteria` (e.g., if criteria mention
   "spreadsheet", router selects `spreadsheet`).
4. `bounded_scope.in_scope` is derived from `files_to_modify` + `context`.
5. `deliverable_path` follows the convention `output/research/<slug>.md`.
6. After AGY completes, the router runs the
   [verification checklist](./verification-checklist.md) against the deliverable.
