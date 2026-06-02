# Task Intake Template (GRO-78)

Use this template to submit a task to the Orchestration Router. Fill in every field
that applies; the router uses this structure to match the task to the best agent.

---

## Template

```yaml
# ── Task Intake ─────────────────────────────────────────────
# Copy this block and fill in the blanks.
# Delete fields that don't apply, but NEVER skip 'goal'.

goal: >
  # [ONE SENTENCE] What must be accomplished.
  # Example: "Deploy the updated landing page to production with
  #           the new hero image and A/B test flag enabled."

context: >
  # [OPTIONAL but recommended] Background the agent needs.
  # Links to Linear issues, PRs, Slack threads, Drive docs, etc.
  # Example: "Linear: ENG-421 | PR: #382 (merged) | Slack: #eng-deploys"

side_effects:
  # [OPTIONAL] Known side effects / blast radius.
  # Example:
  #   - "Restarts the web pod (5s downtime expected)"
  #   - "Touches the shared analytics schema"
  #   - "Sends Slack notification to #product"

files_to_modify:
  # [OPTIONAL] Files the agent is allowed (or expected) to touch.
  # Use globs or explicit paths relative to repo root.
  # Example:
  #   - "src/pages/landing.astro"
  #   - "public/assets/hero-*.webp"
  #   - "config/feature-flags.yaml"

deadline: ""
  # [OPTIONAL] ISO-8601 timestamp or human-readable.
  # Example: "2026-05-30T18:00:00Z" or "before standup tomorrow"
  # Leave empty if no deadline.

verification_criteria:
  # [REQUIRED when approval_required=true, otherwise recommended]
  # How do we know this is done AND correct?
  # Example:
  #   - "Landing page loads at / with new hero image"
  #   - "A/B test cookie 'hero_test_v2' is set on first visit"
  #   - "No 5xx in CloudWatch for 5 minutes after deploy"
  #   - "Lighthouse score >= 90 on mobile"

preferred_agent: ""
  # [OPTIONAL] Force a specific agent.
  # Options: hermes | jules | agy | codex | auto
  # "auto" (default) lets the router decide.

approval_required: false
  # [REQUIRED] true = orchestrator must get human approval before
  # delegating. Use for production deploys, schema changes,
  # customer-facing content, or anything with blast radius > 1 team.
```

---

## Field Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `goal` | **Yes** | Single-sentence task objective; the router matches on this |
| `context` | Recommended | Links, issue numbers, background — reduces back-and-forth |
| `side_effects` | Optional | Known blast radius so the router can gate on `approval_required` |
| `files_to_modify` | Optional | Constrains agent scope; prevents touching unrelated code |
| `deadline` | Optional | Used for priority ordering when multiple tasks are queued |
| `verification_criteria` | Conditional | Required when `approval_required: true`; gates the approval step |
| `preferred_agent` | Optional | Override auto-routing; use sparingly |
| `approval_required` | **Yes** | Boolean gate; `true` for anything risky |

---

## Examples

### Simple Code Change (auto-routed, no approval)

```yaml
goal: >
  Fix the broken "Contact Us" form — email submissions return 500.

context: >
  Error surfaced in #support-alerts. Stack trace shows null pointer in
  src/api/contact.ts:47. Related: Linear BUG-912.

files_to_modify:
  - "src/api/contact.ts"
  - "src/api/__tests__/contact.test.ts"

deadline: "before EOD"
verification_criteria:
  - "POST /api/contact returns 200 with valid payload"
  - "Email arrives in support@ inbox within 30s"
approval_required: false
```

### Production Deploy (requires approval)

```yaml
goal: >
  Deploy v2.4.1 to production — includes new checkout flow.

context: >
  Release train: v2.4.1. Staging passed all tests.
  Linear: REL-88. PRs: #401, #407, #412.

side_effects:
  - "Rolling restart of all web pods (~2 min, zero-downtime)"
  - "New DB migration runs on deploy (adds 'tax_id' column to orders)"
  - "Clears CDN cache for /checkout/*"

files_to_modify:
  - "k8s/production/deployment.yaml"    # image tag bump only

deadline: "2026-05-30T18:00:00Z"
verification_criteria:
  - "Health check /healthz returns 200 on all pods"
  - "Checkout flow completes end-to-end with test card"
  - "No DB migration errors in logs"
  - "P99 latency < 200ms for 10 min post-deploy"
preferred_agent: hermes
approval_required: true
```

### Research Task (AGY)

```yaml
goal: >
  Analyze competitor pricing changes in Q2 2026 and recommend
  adjustments to our SaaS tiers.

context: >
  Drive folder: Competitor Intel / Q2 2026.
  Three competitors raised prices; one introduced a free tier.
  Board wants a recommendation by Friday.

deadline: "2026-05-30T12:00:00Z"
verification_criteria:
  - "Spreadsheet with competitor-by-competitor breakdown"
  - "1-page summary with 3 concrete recommendations"
  - "Data sources cited for every claim"
preferred_agent: agy
approval_required: false
```

---

## Router Behavior

When this template is submitted:

1. **Parse** — Router extracts all fields and validates required ones.
2. **Classify** — `goal` + `files_to_modify` → task type (code / research / deploy / content).
3. **Match** — Task type + `preferred_agent` → best agent profile.
4. **Gate** — If `approval_required: true` and `verification_criteria` is empty, router
   rejects the task and asks the submitter to add criteria.
5. **Delegate** — Agent receives a prompt built from the appropriate prompt template
   (see: [agy-prompt-template](./agy-prompt-template.md),
   [jules-prompt-template](./jules-prompt-template.md),
   [hermes-prompt-template](./hermes-prompt-template.md)).
6. **Verify** — Agent output is checked against the
   [verification checklist](./verification-checklist.md).

---

## Tips

- **Be specific in `goal`.** "Fix the thing" routes poorly. "Fix 500 error on POST /api/contact" routes well.
- **Use `context` for links, not prose.** The agent can follow links; it doesn't need a novel.
- **`files_to_modify` is a safety rail.** If the agent tries to touch a file outside this list, the router can block it.
- **Verification criteria should be machine-checkable where possible.** "No 5xx for 5 min" is checkable. "Looks good" is not.
