# Routing Decision Matrix (GRO-76)

How the Orchestration Router decides which agent handles which task. This matrix
covers the primary decision tree, defaults, exceptions, and approval gates.

---

## Decision Tree

```
                    ┌──────────────────────┐
                    │  Task Intake Received  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ preferred_agent set?  │
                    └──────┬───────┬───────┘
                           │Yes    │No
                           ▼       ▼
                    ┌──────────┐ ┌──────────────────────┐
                    │ Use that │ │ Classify by goal +    │
                    │ agent    │ │ files_to_modify       │
                    └──────────┘ └──────────┬───────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              │                             │                             │
    ┌─────────▼─────────┐    ┌─────────────▼─────────────┐   ┌───────────▼───────────┐
    │ Task type: CODE   │    │ Task type: RESEARCH/DOCS  │   │ Task type: DEPLOY/OPS │
    │ .ts, .py, .astro, │    │ .md, .csv, analysis,     │   │ deploy, health check, │
    │ .yaml, etc.       │    │ Google Drive, websites    │   │ CI/CD, incident       │
    └─────────┬─────────┘    └─────────────┬─────────────┘   └───────────┬───────────┘
              │                            │                             │
    ┌─────────▼─────────┐    ┌─────────────▼─────────────┐   ┌───────────▼───────────┐
    │ → JULES            │    │ → AGY                     │   │ → HERMES              │
    │ Auto PR creation   │    │ Document analysis         │   │ Coordination +        │
    │ from GitHub state  │    │ Context extraction        │   │ validation            │
    └─────────┬─────────┘    └─────────────┬─────────────┘   └───────────┬───────────┘
              │                            │                             │
    ┌─────────▼─────────┐    ┌─────────────▼─────────────┐   ┌───────────▼───────────┐
    │ Task type: REVIEW  │    │ Task type: CONTENT/WEB    │   │ Task type: UNKNOWN    │
    │ PR review, security│    │ Web scraping, public      │   │ Can't classify —      │
    │ audit, code quality│    │ API calls, content gen     │   │ ambiguous goal        │
    └─────────┬─────────┘    └─────────────┬─────────────┘   └───────────┬───────────┘
              │                            │                             │
    ┌─────────▼─────────┐    ┌─────────────▼─────────────┐   ┌───────────▼───────────┐
    │ → CODEX            │    │ → AGY or MAIN AGENT       │   │ → HERMES              │
    │ Security + quality │    │ Depends on scope:         │   │ Triages, asks for     │
    │ pattern detection  │    │   Scoped → AGY            │   │ clarification         │
    └────────────────────┘    │   Open-ended → Hermes     │   └───────────────────────┘
                              └───────────────────────────┘
```

---

## Primary Routing Table

| Task Signature | Agent | Why | Example Goals |
|---|---|---|---|
| **Code creation/modification** — `.ts`, `.py`, `.astro`, `.yaml`, `.json` files | **Jules** | Only agent with GitHub write access; auto-PR flow | "Fix 500 error on POST /api/contact", "Add newsletter signup component" |
| **Research & analysis** — Documents, Drive, web research, competitor analysis | **AGY** | Vision pipeline, Drive access, bounded research | "Analyze Q2 competitor pricing changes", "Audit blog SEO performance" |
| **Code review & security audit** — PRs, codebase scans | **Codex** | Security pattern detection, quality heuristics | "Review PR #412 for security issues", "Audit repo for credential leaks" |
| **Deployment supervision** — K8s, health checks, rollbacks | **Hermes** | Coordination, multi-step validation | "Deploy v2.4.1 to production", "Rollback checkout-api if error rate > 0.1%" |
| **Multi-agent coordination** — Tasks requiring 2+ agents | **Hermes** | Orchestration, subagent dispatch | "Research competitor pricing then update our pricing page" |
| **Incident response** — Alerts, outages, root cause | **Hermes** | Triage + delegate fixes | "Checkout flow returning 503 for 15% of users" |
| **Web scraping / external API** — Public endpoints, content fetching | **AGY** or **main agent** | AGY for bounded scope; Hermes for one-off | "Scrape competitor feature lists", "Call weather API for sail report" |
| **Content generation** — Blog posts, podcast notes, marketing | **AGY** | Content strategy skills, bounded research | "Write blog post from podcast transcript", "Generate sail report" |

---

## Agent Selection Details

### Jules — Code Work
**Matches when:**
- `files_to_modify` includes `.ts`, `.py`, `.astro`, `.yaml`, `.js`, `.css`, `.html`, `.json`
- `goal` contains verbs: fix, build, implement, refactor, add, update, create (code context)
- Task requires a PR against a GitHub repo

**Does NOT match when:**
- Task is research-only (no code output)
- Files are `.md`, `.csv`, or documentation-only
- Task requires Google Drive access
- Repo has broken CI/CD (Jules needs green main)

### AGY — Research & Planning
**Matches when:**
- `goal` contains: analyze, research, audit, compare, investigate, extract, review (content)
- `context_links` includes Google Drive URLs
- `output_format` is `markdown_report`, `spreadsheet`, or `prose_summary`
- Task is bounded in scope (has `in_scope`/`out_of_scope`)

**Does NOT match when:**
- Task requires writing code or opening PRs
- Task is open-ended with no boundaries
- Task requires K8s/Docker/CI operations

### Hermes — Local Orchestration
**Matches when:**
- `task_type` is `deployment_supervision`, `multi_agent_validation`, `incident_response`
- Task requires coordinating 2+ agents
- Task has `approval_required: true`
- `subagent_allocations` is populated
- Task type is ambiguous/unknown and needs triage

**Does NOT match when:**
- A single agent can handle the entire task independently
- Task has `preferred_agent` set to a specific agent

### Codex — Code Review
**Matches when:**
- `goal` contains: review, audit, check, scan, inspect (code context)
- Inputs include PR URLs or branch names
- Task is explicitly a review (not implementation)

**Does NOT match when:**
- Task requires writing new code
- Task requires deployment or infrastructure changes

---

## Defaults & Fallbacks

| Situation | Default | Fallback |
|---|---|---|
| No agent matched | **Hermes** — triage and re-route | Hermes asks for clarification, delegates after classification |
| Jules unavailable (at capacity) | Wait 15 min, retry once | Route to Hermes for manual implementation or delay |
| AGY unavailable (token exhaustion) | Wait, retry once | Route to Hermes with AGY's partial results |
| Codex unavailable (3hr token refresh) | Wait for refresh | Hermes performs manual review |
| Unknown file type | **Hermes** — investigate then delegate | Hermes identifies type, re-routes |
| `preferred_agent` conflicts with task type | **preferred_agent wins** but router warns | Log conflict; follow [operator quickstart](./operator-quickstart.md) escalation |

---

## Approval Gates

The router enforces an approval gate when `approval_required: true`:

```
Task matched → Agent selected → APPROVAL GATE
                                    │
                         ┌──────────▼──────────┐
                         │ verification_criteria │
                         │ populated?            │
                         └──────┬───────┬───────┘
                                │Yes    │No
                                ▼       ▼
                         ┌──────────┐ ┌──────────────┐
                         │ Proceed   │ │ REJECT        │
                         │ to agent  │ │ Task returned  │
                         └──────────┘ │ with: "Add     │
                                      │ verification   │
                                      │ criteria"     │
                                      └──────────────┘
```

**Always gated (cannot skip approval):**
- Production deploys
- Database schema changes
- Customer-facing content changes
- Any task with `side_effects` that mention credentials, PII, or billing

**Never gated (auto-approved):**
- Research tasks with no code output
- Typo/formatting fixes
- Draft PRs (not targeting `main`)

---

## Exceptions & Overrides

1. **Force-routing:** Set `preferred_agent` in the [task intake template](./task-intake-template.md) to override
   auto-classification. The router will use that agent regardless of task type, but logs a warning.

2. **Split tasks:** If a single task requires both research and implementation, the router splits it:
   - Research phase → AGY
   - Implementation phase → Jules
   - Coordination → Hermes
   Use `subagent_allocations` in the [hermes prompt template](./hermes-prompt-template.md) to pre-assign.

3. **Emergency overrides:** Tasks labeled `priority: urgent` bypass classification and go directly
   to Hermes for immediate triage, regardless of task type.

4. **Jules capacity spillover:** When Jules hits 300 sessions/day, code tasks spill over to
   Hermes (manual implementation) with a flag for Jules to review after.

5. **AGY timeouts:** If AGY exceeds `stop_after` wall-clock limit, Hermes picks up partial
   results and completes the task or escalates.

---

## Cross-References

- Submit tasks via [task-intake-template](./task-intake-template.md)
- See agent constraints in [lane-capabilities](./lane-capabilities.md)
- Verify output with [verification-checklist](./verification-checklist.md)
- Understand escalation in [hermes-prompt-template](./hermes-prompt-template.md)
- See pilot results in [router-pilot-report](./router-pilot-report.md)
- Review refinements in [routing-refinements](./routing-refinements.md)
