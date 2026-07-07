# Jules CLI Evaluation (GRO-18)

How Jules receives Linear-linked repo tasks, the full session lifecycle, pull/apply/commit
workflow, PR creation and review cycle, and daily throughput tracking.

---

## How Jules Receives Tasks

Jules tasks originate in Linear and are picked up automatically via cron-driven polling.

### Method 1: Linear Label (Primary — Automated)

```
1. Task created in Linear with label agent:jules
2. Jules Session Manager (cron, every 15 min) detects it
3. Session launched: jules new --repo OWNER/REPO "Linear: GRO-XX title"
4. Session ID posted as Linear comment
5. Session tracked in /tmp/jules-session-tracker.json
```

**Requirements for auto-dispatch:**
- Linear issue in "Todo" or "In Progress" state
- Label `agent:jules` applied
- Target repo has green CI on `main`
- Jules below concurrent session cap (10)
- Jules below daily session cap (300)

### Method 2: Direct CLI (Manual)

```bash
jules new --repo mbgulden/hd-platform "Linear: GRO-100 — Add newsletter signup"
```

### Method 3: Orchestrator Dispatch (Hermes → Jules)

When Hermes coordinates a multi-agent task, it dispatches Jules with a filled
[Jules prompt template](./jules-prompt-template.md).

### Pre-Flight Checks (Run Before Every Dispatch)

The router runs three checks before dispatching to Jules:

| # | Check | Command/API | Pass Condition |
|---|-------|------------|---------------|
| 1 | CI green on `main` | `gh api /repos/$REPO/commits/main/check-runs` | No non-success conclusions |
| 2 | Repo accessible | `jules remote list --repo $REPO` | Exit code 0 |
| 3 | Lockfile recent | `find . -maxdepth 2 -name 'package-lock.json' -mtime -1` | File exists and <24h old |

If any pre-flight fails, dispatch is blocked and the failure is reported.

---

## Session Lifecycle: Create → Work → PR → Merge

```
┌─────────────────────────────────────────────────────────────────┐
│                    JULES SESSION LIFECYCLE                       │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────┤
│  CREATE  │  FETCH   │  BRANCH  │   WORK   │   TEST   │   PR    │
│ Session  │ Clone/   │ Create   │ Implement│ Run tests│ Open PR │
│ launched │ pull     │ feature  │ changes  │ → green  │ & report│
│          │ latest   │ branch   │          │          │         │
├──────────┼──────────┼──────────┼──────────┼──────────┼─────────┤
│  15 min  │  ~1 min  │  <1 min  │ Variable │  ~2-10m  │  ~1 min │
└──────────┴──────────┴──────────┴──────────┴──────────┴─────────┘
```

### Phase 1: CREATE — Session Initialization

1. Session Manager detects Linear issue with `agent:jules` label
2. Validates pre-flight checks (CI green, repo accessible, lockfile recent)
3. Extracts task metadata: repo, title, description, files_to_modify
4. Generates branch name: `gro-XX/short-description` (auto-slugged from title)
5. Launches `jules new` with full context
6. Posts Linear comment: "Jules session `ABC123` started — working on this."

### Phase 2: FETCH — Repository State

1. Jules clones or fetches the target repo at latest `base_branch` (default: `main`)
2. Jules reads existing code to understand context
3. Jules identifies related files, imports, test patterns
4. If `dependencies` specified, installs them

### Phase 3: BRANCH — Feature Branch

1. Jules creates branch from `base_branch`
2. Branch naming: `gro-XX/description` or `type/description`
3. Branch discipline enforced: Jules never works on `main`

### Phase 4: WORK — Implementation

1. Jules reads `description` and produces an internal implementation plan
2. Creates `files_to_create` in order
3. Modifies `files_to_modify` with targeted edits
4. Writes or updates tests if `tests_required: true`

**What Jules CAN do:**
- Create new files in any language
- Edit existing files with surgical precision
- Install packages (npm, pip, cargo)
- Run linters and formatters

**What Jules CANNOT do:**
- Access local files outside the repo
- Read environment variables or secrets
- Connect to databases
- Browse the web
- Access Google Drive

### Phase 5: TEST — Verification

1. Jules runs the test suite for affected files
2. If tests fail, Jules iterates: fix → retest (up to 3 cycles)
3. If `tests_required: false`, this phase is skipped
4. If tests pass, Jules proceeds to commit
5. If tests fail after 3 cycles, Jules reports failure and does NOT open PR

### Phase 6: PR — Pull Request

1. Jules stages changes and commits with conventional commit message
   - Format: `type: description` (e.g., `fix: contact form returns 500 on submit`)
2. Pushes branch to GitHub
3. Opens PR against `base_branch`
4. Adds "Closes GRO-XX" to PR body if `linear_issue` is set
5. Posts Linear comment: "PR #N opened — [link]"
6. Returns Jules handoff contract to orchestrator

---

## Pull / Apply / Commit Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                     JULES GIT WORKFLOW                            │
│                                                                   │
│  Remote (GitHub)                     Local (Jules session)        │
│  ┌─────────────┐                    ┌──────────────────────┐     │
│  │ main        │ ← git clone/fetch  │ Working directory     │     │
│  │ (green CI)  │                    │ /tmp/jules-session/   │     │
│  └─────────────┘                    └──────────┬───────────┘     │
│                                                │                  │
│                                     ┌──────────▼───────────┐     │
│                                     │ git checkout -b       │     │
│                                     │ gro-XX/description    │     │
│                                     └──────────┬───────────┘     │
│                                                │                  │
│                                     ┌──────────▼───────────┐     │
│                                     │ write_file / patch    │     │
│                                     │ npm test / pytest     │     │
│                                     └──────────┬───────────┘     │
│                                                │                  │
│  ┌─────────────┐                    ┌──────────▼───────────┐     │
│  │ gro-XX/...  │ ← git push        │ git add + git commit  │     │
│  │ (feature)   │                    │ conventional commit   │     │
│  └──────┬──────┘                    └──────────────────────┘     │
│         │                                                         │
│  ┌──────▼──────┐                                                  │
│  │ PR opened   │                                                  │
│  │ against main│                                                  │
│  └─────────────┘                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Commit Convention

All Jules commits follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use When | Example |
|--------|---------|---------|
| `fix:` | Bug fix | `fix: contact form returns 500 on submit` |
| `feat:` | New feature | `feat: add newsletter signup component` |
| `refactor:` | Code restructuring | `refactor: extract payment logic` |
| `test:` | Test changes | `test: add integration tests for checkout` |
| `docs:` | Documentation | `docs: add API endpoint descriptions` |
| `chore:` | Maintenance | `chore: update dependencies` |
| `ci:` | CI/CD changes | `ci: add Node 22 to test matrix` |

---

## PR Creation and Review Cycle

```
Jules opens PR
      │
      ▼
┌─────────────────┐
│ CI runs on PR   │
│ (lint, build,   │
│  test)          │
└────────┬────────┘
         │
    ┌────▼────┐
    │ CI pass? │
    └─┬─────┬─┘
      │Yes  │No
      ▼     ▼
┌──────────┐ ┌──────────────────┐
│ PR ready │ │ Jules fixes      │
│ for      │ │ (reads CI output,│
│ review   │ │  iterates)        │
└────┬─────┘ └──────────────────┘
     │
     ▼
┌──────────────────┐
│ Add label:       │
│ agent:chatgpt55  │ (optional — for Codex review)
└────────┬─────────┘
         │
    ┌────▼────┐
    │ Review? │
    └─┬─────┬─┘
      │Yes  │No
      ▼     ▼
┌──────────┐ ┌──────────────┐
│ Codex    │ │ PR Auto-Merger│
│ reviews  │ │ (cron, 60 min)│
└────┬─────┘ │ merges if CI  │
     │       │ green + no    │
     ▼       │ blocked label │
┌──────────┐ └──────────────┘
│ Approved?│
└─┬──┬──┬──┘
  │  │  │
  │  │  └── blocked → Hermes investigates
  │  └───── changes_requested → Jules revises
  └──────── approved → PR Auto-Merger merges
```

### PR Auto-Merger (Cron, Every 60 min)

The auto-merger checks all open PRs:
1. CI is green (all checks passing)
2. PR is not draft
3. No `blocked` label
4. If Codex review was requested: verdict is `approved`
5. If all conditions met → squash-merge to `main`

### Jules Review Mode

Jules can also review PRs (different from Codex review):

1. Add label `agent:jules-review` to a Linear issue with an open PR
2. Jules Session Manager launches a review session
3. Jules reviews the diff, comments on the PR
4. Review findings posted as Linear comment

Use `agent:jules-review` for:
- Second pair of eyes on non-security code
- Style and convention checks
- Test coverage assessment

---

## Daily Throughput Tracking

### Capacity Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Max sessions/day | **300** | Hard cap; spillover goes to Hermes |
| Max concurrent | **10** | Configurable in session manager |
| Session timeout | Varies | Jules iterates until done or times out |
| Retry limit | **3 cycles** | Per task; after 3 failures, escalates |

### Tracking Location

Session state is tracked in `/tmp/jules-session-tracker.json`:

```json
{
  "daily_stats": {
    "date": "2026-05-29",
    "sessions_completed": 47,
    "sessions_failed": 3,
    "sessions_active": 8,
    "prs_opened": 44,
    "prs_merged": 38,
    "avg_time_minutes": 12.3
  },
  "concurrent": 8,
  "queue_depth": 2
}
```

### Monitoring Metrics

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Daily session count | `jules-session-tracker.json` | > 280 (near cap) |
| Concurrent sessions | Session manager | > 9 (near cap) |
| Failure rate | Session tracker | > 10% in 24h |
| PR merge rate | GitHub API | < 70% in 24h |
| Avg session time | Session tracker | > 30 min (stalling) |
| Queue depth | Session manager | > 5 (backlog building) |

### Capacity Spillover

When Jules approaches capacity:

1. **280+ sessions/day:** Router warns; new code tasks get `jules_at_capacity` flag
2. **300 sessions/day:** Router stops dispatching to Jules
   - CODE tasks spill over to Hermes for manual implementation
   - Hermes work is flagged for Jules review afterward
   - Tasks wait in queue for next day's cycle

### Throughput Report (Automated)

The Jules Monitor cron job (every 30 min) produces a throughput summary:

```
Jules Throughput — 2026-05-29 14:00 UTC
├─ Completed today: 47 sessions
├─ Failed: 3 (6.0%)
├─ Active: 8
├─ PRs opened: 44
├─ PRs merged: 38
├─ Avg time: 12.3 min
├─ Queue: 2 pending
└─ Status: HEALTHY
```

---

## Common Failure Modes & Resolution

| Failure | Symptom | Jules Action | Orchestrator Action |
|---------|---------|-------------|-------------------|
| CI broken on main | Pre-flight fails | N/A (not dispatched) | Fix CI; re-dispatch |
| Test failure | Tests red after implementation | Retries up to 3× | If 3 fails → escalate |
| Lockfile stale | Pre-flight fails | N/A (not dispatched) | Run `npm install`; re-dispatch |
| Repo not accessible | Pre-flight fails | N/A (not dispatched) | Verify `jules remote add` |
| Branch conflict | Merge conflict on PR | N/A (reported) | Hermes resolves or re-dispatches |
| Session timeout | Exceeds timeout | Returns partial work | Hermes reviews; re-dispatches if incomplete |
| At capacity (300/day) | Queue full | N/A (queued) | Hermes implements directly |

---

## Cross-References

- Jules prompt template: [jules-prompt-template](./jules-prompt-template.md)
- Jules capabilities: [lane-capabilities](./lane-capabilities.md)
- Routing rules: [routing-decision-matrix](./routing-decision-matrix.md)
- Verification checklist: [verification-checklist](./verification-checklist.md)
- Full architecture: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)
