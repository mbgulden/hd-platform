# Lane Capabilities — Verified Agent Inventory (GRO-77)

What each agent lane CAN and CANNOT do, plus constraints, rate limits, and known issues.
This is the single source of truth for agent capabilities used by the router.

---

## AGY — Research & Vision Agent

### ✅ Can Do

| Capability | Details | Verified |
|---|---|---|
| **Google Drive analysis** | Read/export Docs, Sheets, Slides; search files | ✅ |
| **Google Takeout processing** | Extract and analyze archive data | ✅ |
| **Web research** | Visit URLs, scrape public pages, analyze content | ✅ |
| **Document synthesis** | Cross-reference multiple documents into a single report | ✅ |
| **Vision/pipeline tasks** | Screenshots, diagrams, image analysis | ✅ |
| **Multi-session parallelism** | Up to 5 parallel sub-sessions (`max_sessions: 1–5`) | ✅ |
| **File output** | Write markdown, CSV, JSON to local filesystem (with branch discipline) | ✅ |
| **Content strategy** | SEO audits, content audits, competitor analysis | ✅ |
| **Long-running research** | `--print-timeout` up to 600s per session | ✅ |

### ❌ Cannot Do

| Limitation | Reason | Workaround |
|---|---|---|
| **GitHub PR creation** | No GitHub write access | Output artifacts; Jules or Hermes creates PR |
| **Code implementation** | Not a code-generation agent | Route code tasks to Jules |
| **Database operations** | No DB access | Pre-extract data; AGY analyzes the extract |
| **K8s/Infrastructure** | No cluster access | Route ops tasks to Hermes |
| **Open-ended exploration** | Bounded scope required | Define `in_scope`/`out_of_scope` in AGY prompt |
| **Terminal execution** | Output-only (writes files) | Commands run via Hermes, not AGY |
| **Real-time data** | No streaming APIs | Use snapshots/CSV exports |

### Constraints & Rate Limits

| Constraint | Value | Notes |
|---|---|---|
| **Max sub-sessions** | 5 | Configurable via `max_sessions`; default is 1 |
| **Session timeout** | 600s | `--print-timeout` hard cap |
| **Stop condition** | Configurable | Set `stop_after` in AGY prompt (e.g., "2 hours wall-clock") |
| **File write path** | `deliverable_path` only | AGY cannot write outside declared path |
| **Token budget** | ~120K tokens | See [context-window-pruning](./context-window-pruning.md) |

### Known Issues

1. **Scope creep:** AGY sometimes expands beyond `out_of_scope` when research is rich.
   Mitigation: Set aggressive `stop_after` and review `bounded_scope` before launch.

2. **Token exhaustion on large Drive exports:** Large Google Sheets (>10K rows) can exhaust
   the context window. Mitigation: Pre-filter in Sheets before AGY reads.

3. **Vision quality varies by model:** AGY's vision pipeline depends on the underlying model.
   Results are better with recent models. Verify visual outputs manually for accuracy.

---

## Jules — Code Implementation Agent

### ✅ Can Do

| Capability | Details | Verified |
|---|---|---|
| **Code creation** | New files, components, APIs in any language | ✅ |
| **Code modification** | Edit existing files with targeted changes | ✅ |
| **PR creation** | Auto-create PR with conventional commit message | ✅ |
| **Test writing** | Unit, integration, and E2E tests | ✅ |
| **Test execution** | Run test suites, iterate until green | ✅ |
| **Dependency management** | Install packages (npm, pip, cargo) | ✅ |
| **Refactoring** | Structural changes, extract methods, rename symbols | ✅ |
| **Documentation** | README, API docs, inline comments | ✅ |
| **Branch management** | Auto-create feature branches, push to GitHub | ✅ |
| **Conventional commits** | PRs follow `type: description` format | ✅ |

### ❌ Cannot Do

| Limitation | Reason | Workaround |
|---|---|---|
| **Local file access** | GitHub-state only | Push before assigning; Jules sees committed state |
| **Environment variables** | No access to secrets | Use GitHub Secrets in CI; never pass to Jules |
| **Secrets/credentials** | No env var access | Pre-configure in CI/CD; Jules uses service accounts |
| **Database access** | GitHub-only | Jules works on code that connects to DB; doesn't access DB directly |
| **Google Drive** | No Drive integration | Route Drive tasks to AGY |
| **Web research** | No browsing capability | Pre-research with AGY; feed results to Jules |
| **Production deploys** | No cluster access | Jules writes code; Hermes deploys |
| **Multi-agent coordination** | Single-agent scope | Route coordination to Hermes |

### Constraints & Rate Limits

| Constraint | Value | Notes |
|---|---|---|
| **Max sessions/day** | **300** | Hard cap; spillover goes to Hermes |
| **Max concurrent** | 10 | Configurable in session manager |
| **Session timeout** | Varies by task | Jules iterates until done or times out |
| **Repo requirement** | Clean `main` branch | CI must be green on main before Jules can work |
| **PR requirement** | Tests pass | Tests must be green to open PR (if `tests_required: true`) |
| **Branch convention** | `gro-XX/description` or `type/description` | Enforced; see [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md) |

### Known Issues

1. **CI/CD broken repos:** Jules cannot work on repos where `main` has red CI. Fix CI first.
2. **Large monorepos:** Jules may time out on very large codebases (>10K files). Break into
   smaller, focused tasks.
3. **Session capacity spikes:** At 300/day, sessions queue. The session manager auto-throttles.
4. **Branch conflicts:** If two Jules sessions touch the same file, merge conflicts occur.
   Mitigation: Use `files_to_modify` to constrain scope and avoid overlap.

---

## Codex — Code Review & Security Agent

### ✅ Can Do

| Capability | Details | Verified |
|---|---|---|
| **PR review** | Read diff, comment on logic, style, correctness | ✅ |
| **Security audit** | Detect credentials, injection vectors, auth flaws | ✅ |
| **Code quality** | Style, patterns, maintainability assessment | ✅ |
| **Architecture review** | High-level design feedback | ✅ |
| **Proactive scanning** | Periodic repo scans for improvement opportunities | ✅ |
| **Test coverage analysis** | Flag untested paths, suggest test cases | ✅ |

### ❌ Cannot Do

| Limitation | Reason | Workaround |
|---|---|---|
| **Write code** | Review-only agent | Route implementation to Jules |
| **Deploy changes** | No ops access | Route deployment to Hermes |
| **Approve PRs** | Advisory only | Human or Hermes approves based on review |
| **Fix issues** | No write access | File issues; Jules implements fixes |
| **Local file access** | API-based review | All reviews operate on GitHub PR diffs |
| **Long-running tasks** | Token limit | 3-hour refresh cycle |

### Constraints & Rate Limits

| Constraint | Value | Notes |
|---|---|---|
| **Token refresh cycle** | ~3 hours | When exhausted, falls back to deepseek-v4-flash |
| **Review capacity** | ~20 PRs/cycle | Estimate; varies by PR size |
| **Fallback model** | deepseek-v4-flash | Automatically used when tokens exhausted |
| **Review depth** | Configurable | Shallow (quick scan) vs. deep (full audit) |

### Known Issues

1. **Token exhaustion mid-review:** If tokens run out during a review, the review is partial.
   Mitigation: Schedule deep reviews early in the refresh cycle.

2. **False positives on security:** Codex can flag benign patterns as security risks.
   Mitigation: Human review of all 🔴 Blocked findings before action.

3. **Proactive scan noise:** Periodic scans can generate low-signal issues.
   Mitigation: Filter by severity; address High and Critical only.

---

## Hermes — Orchestrator Agent

### ✅ Can Do

| Capability | Details | Verified |
|---|---|---|
| **Task triage** | Classify, route, and gate incoming tasks | ✅ |
| **Multi-agent coordination** | Dispatch to Jules, AGY, Codex; aggregate results | ✅ |
| **Deployment supervision** | K8s health checks, canary monitoring, rollbacks | ✅ |
| **Verification** | Run [verification checklist](./verification-checklist.md) against all agent outputs | ✅ |
| **Direct file edits** | Write/patch files (with branch discipline) | ✅ |
| **Incident response** | Triage, delegate fixes, verify resolution | ✅ |
| **Escalation** | PagerDuty, Slack alerts, human notification | ✅ |
| **Research coordination** | Delegate research to AGY, implement via Jules | ✅ |
| **Code review coordination** | Delegate review to Codex, aggregate feedback | ✅ |

### ❌ Cannot Do

| Limitation | Reason | Workaround |
|---|---|---|
| **GitHub PR creation** | Jules-only capability | Delegate PR creation to Jules |
| **Google Drive access** | AGY-only capability | Delegate Drive tasks to AGY |
| **Specialized code review** | Codex has deeper security patterns | Delegate deep review to Codex |
| **Human approval** | Must escalate for gated tasks | Use `approval_required` + `escalation_path` |

### Constraints & Rate Limits

| Constraint | Value | Notes |
|---|---|---|
| **Context window** | ~1M tokens (deepseek-v4-pro) | Largest window of all agents |
| **Compression threshold** | 0.50 (500K tokens) | See [context-window-pruning](./context-window-pruning.md) |
| **Token budget** | Unlimited (cost-constrained, not capacity) | Full skills corpus loaded |
| **Subagent timeout** | Configurable per task | Default 30 min; max 120 min |
| **Parallel dispatch** | Configurable | Set `parallel: true` in Hermes prompt |

### Known Issues

1. **Subagent stalls:** If a delegated agent (Jules/AGY) hangs, Hermes waits until timeout.
   Mitigation: Set realistic `timeout_minutes` per task type.

2. **Verification false negatives:** The verification script can reject valid outputs on
   edge cases (e.g., non-standard file extensions). Mitigation: Manual override for waived checks.

3. **Context accumulation in swarm sessions:** After 3+ delegations, context usage grows
   significantly. Mitigation: Compression at 500K tokens; prune between delegations.

---

## Capability Comparison Matrix

| Capability | Jules | AGY | Codex | Hermes |
|---|---|---|---|---|
| Write code | ✅ | ❌ | ❌ | ✅ (limited) |
| Create PRs | ✅ | ❌ | ❌ | ❌ |
| Run tests | ✅ | ❌ | ❌ | ✅ |
| Research/analysis | ❌ | ✅ | ❌ | ✅ (coordinator) |
| Google Drive | ❌ | ✅ | ❌ | ❌ |
| Web browsing | ❌ | ✅ | ❌ | ✅ (limited) |
| Security audit | ❌ | ❌ | ✅ | ❌ |
| Code review | ❌ | ❌ | ✅ | ✅ (basic) |
| Deploy to prod | ❌ | ❌ | ❌ | ✅ |
| Health checks | ❌ | ❌ | ❌ | ✅ |
| Incident response | ❌ | ❌ | ❌ | ✅ |
| Multi-agent orchestration | ❌ | ❌ | ❌ | ✅ |
| File output (local) | ❌ | ✅ | ❌ | ✅ |
| Max sessions/day | 300 | 5 sub-sessions | ~20 reviews | Unlimited |
| Context window | N/A (CLI) | Varies | 272K | 1M |

---

## Cross-References

- Route tasks using [routing-decision-matrix](./routing-decision-matrix.md)
- Submit tasks via [task-intake-template](./task-intake-template.md)
- Verify outputs with [verification-checklist](./verification-checklist.md)
- Agent prompt templates: [AGY](./agy-prompt-template.md), [Jules](./jules-prompt-template.md), [Hermes](./hermes-prompt-template.md)
- Full architecture: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)
