# Swarm Workflow — How All Agents Work Together

## The Three-Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         LINEAR                              │
│  Task Ledger — every task has an issue                       │
│  Labels route work: agent:jules, agent:agy, agent:chatgpt55 │
└──────────────────┬───────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┐
    ▼              ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐
│  JULES  │  │   AGY    │  │CHATGPT5.5 │  │ HERMES/FRED  │
│  Coder  │  │Research  │  │ Reviewer  │  │ Orchestrator │
│ 300/day │  │ +Vision  │  │ +Auditor  │  │              │
└────┬────┘  └────┬─────┘  └─────┬─────┘  └──────┬───────┘
     │            │              │                │
     ▼            ▼              ▼                ▼
┌──────────────────────────────────────────────────────────────┐
│                       GITHUB                                 │
│  Code + PRs + Reviews — the durable ledger                   │
│  Feature branches per Linear issue                           │
│  Branch discipline enforced for ALL agents                   │
└──────────────────────────────────────────────────────────────┘
```

## Repo Map — Which Linear Project → Which GitHub Repo

| Linear Project | GitHub Repo | Nickname |
|---------------|-------------|----------|
| HD Engine Core, Reports, Growth, Creator, Coach, Consumer, Enterprise, Dating, Education, AI Lab | `mbgulden/hd-platform` | `hd-platform` |
| OpenHumanDesignMCP | `mbgulden/OpenHumanDesignMCP` | `hd-engine` |
| Agentic Swarm Ops | `mbgulden/agentic-swarm-ops` | `swarm-ops` |
| Sovereign Sentinel | `mbgulden/SovereignSentinel` | `sentinel` |
| Active Oahu Tours | `mbgulden/activeoahutours.com` | `active-oahu` |
| Project Honeybadger | `mbgulden/hd-platform` | `hd-platform` |
| AI Consulting | `mbgulden/ai-consulting` | `ai-consulting` |

## Branch Convention (ALL Agents — Mandatory)

Every agent MUST create a feature branch before modifying any file:

```
gro-XX/brief-description
```

**How each agent enforces this:**

| Agent | Branch Method |
|-------|--------------|
| **Jules** | Auto-creates branch on `jules new` |
| **AGY** | Prompt includes: "First, run: `source ops/branch-discipline.sh <repo> <ISSUE> <desc>`" |
| **Fred (Hermes)** | Runs `ops/branch-discipline.py` before any `write_file`/`patch` call |
| **ChatGPT5.5** | Prompt includes: "First, create branch: `git checkout -b <issue>/<desc>`" |

**The branch-discipline script** (`ops/branch-discipline.py`):
- Checks if already on a feature branch → no-op
- If on `main`: stashes changes, pulls latest, creates `gro-XX/description` branch, pops stash
- Safe to call repeatedly — idempotent

```bash
# Before any file edits:
python3 /home/ubuntu/work/agentic-swarm-ops/ops/branch-discipline.py hd-platform GRO-123 "fix payment bug"
```

**Why:** Prevents Fred, AGY, and Jules from editing the same files simultaneously. Each agent works in its own branch. Conflicts are resolved at PR time through the review pipeline.

Examples:
- `gro-100/weekly-podcast-automation`
- `gro-96/rapidapi-marketplace-listing`
- `gro-88/launch-hd-api`

**Never work directly on `main`.** Jules auto-creates branches when given repo access.

## How Jules Gets Assigned

### Method 1: Linear Label (Automated)
1. Add label `agent:jules` to any Linear issue in "Todo" or "In Progress"
2. The **Jules Session Manager** (cron every 15min) detects it
3. Automatically launches `jules new --repo OWNER/REPO "Linear: GRO-XX ..."`
4. Jules session ID posted as Linear comment
5. Session tracked in `/tmp/jules-session-tracker.json`

### Method 2: GitHub Issue Comment
1. On any GitHub issue in an orchestrated repo, comment `/agent jules`
2. The **Orchestration Router** GitHub Action fires
3. Classifies and routes to Jules
4. Decision artifact saved as workflow artifact

### Method 3: Direct CLI (Manual)
```bash
jules new --repo mbgulden/hd-platform "Linear: GRO-100 — Build weekly podcast automation"
```

## The Review Pipeline

```
Agent completes work → pushes to feature branch → opens PR
                        ↓
              PR Auto-Merger checks CI + tests
                        ↓
    ┌─ CI passes + approved → AUTO-MERGE to main
    │
    └─ CI fails → Linear comment with failure details
                        ↓
              Human or Hermes reviews and fixes
```

To request a Jules review of completed work:
1. Add label `agent:jules-review` to the Linear issue
2. Jules Session Manager launches a review session
3. Jules reviews the PR, adds comments, reports findings

## Agent Role Matrix

| Agent | Profile/CLI | Best For | How to Invoke | Fallback |
|-------|-----------|----------|---------------|----------|
| **Jules** | `jules` CLI | Coding, PRs, docs, tests, refactors | Label `agent:jules` on Linear | — |
| **AGY** | `agy` CLI (PTY mode) | Research, Google Docs analysis, vision, broad synthesis, Drive/Takeout extraction | Label `agent:agy` on Linear or `/goal` prompt | — |
| **ChatGPT5.5** | `codex-5-5` profile | **Code Review + Security Audit**: Reviews PRs for correctness, security, style. Audits codebases. Provides proactive improvement advice. Second set of eyes after Jules completes work. | Label `agent:chatgpt55` on Linear | deepseek-v4-flash (3hr token refresh) |
| **Hermes/Fred** | `orchestrator` profile | Orchestration, planning, validation, cross-agent coordination, direct file edits | Default — no label needed | deepseek-v4-flash |

## AGY — Research & Vision Agent

**Role:** Broad research, document analysis, vision tasks, and long-running synthesis.

**Strengths:**
- Google Docs/Drive analysis and extraction
- Google Takeout archive processing
- Multi-document cross-referencing
- Vision/pipeline tasks (screenshots, diagrams)
- Long-running research sessions (--print-timeout)

**How to assign:**
1. Add label `agent:agy` to a Linear issue with a clear research question
2. Or launch directly: `agy --print '/goal Research: <topic>' --print-timeout 600s`
3. AGY writes artifacts to the repo (with branch discipline)
4. Hermes/Fred picks up the artifact for next steps

**Branch discipline:** AGY prompts include: `source /home/ubuntu/work/agentic-swarm-ops/ops/branch-discipline.sh <repo> <ISSUE>`

## ChatGPT5.5 — Code Reviewer & Security Auditor

**Role:** Reviews code, audits for security issues, and provides proactive improvement suggestions.

**Strengths:**
- PR review with detailed feedback
- Security vulnerability scanning
- Code quality and style assessment
- Architecture and design pattern review
- Proactive advice: "I noticed X could be improved by Y"

**Token limit:** ~3-hour refresh cycle. When tokens exhausted, falls back to deepseek-v4-flash automatically.

**How to assign:**
1. Add label `agent:chatgpt55` to a Linear issue with an open PR
2. ChatGPT5.5 reviews the PR diff and posts findings as Linear comments
3. Or launch the `codex-5-5` profile: `hermes -p codex-5-5 -z "Review PR #X in repo Y"`

**Review workflow:**
```
Jules completes PR → add label agent:chatgpt55
    ↓
ChatGPT5.5 reviews diff, checks:
  - Logic correctness
  - Security (credentials, injection, auth)
  - Code style and patterns
  - Test coverage
    ↓
Posts review with: ✅ Approved / ⚠️ Changes Requested / 🔴 Blocked
    ↓
If approved → PR auto-merger merges
If changes requested → Jules revises
If blocked → Hermes/Fred investigates
```

**Proactive mode:** ChatGPT5.5 periodically scans repos for improvement opportunities and files issues or suggestions without being asked.

## Jules Capacity & Limits

- **Max: 300 sessions/day**
- **Max concurrent: 10** (configurable in session manager)
- Jules works from **GitHub state only** — push before assigning
- Jules cannot touch local files, env vars, or secrets
- Repos with broken CI/CD should not be routed to Jules

## How to Use This System

### To assign work to Jules:
```
1. Create a Linear issue with a clear title and description
2. Add label "agent:jules"
3. The system handles the rest:
   - Session launched within 15 minutes
   - Branch created, code written, PR opened
   - CI runs, PR auto-merged if approved
```

### To have Jules review completed work:
```
1. Add label "agent:jules-review" to the Linear issue
2. Ensure the PR is open and linked to the issue
3. Jules reviews and comments within 15 minutes
```

### Active Cron Jobs That Power This:

| Job | Interval | What It Does |
|-----|----------|-------------|
| `jules-session-manager` | Every 15min | Linear → Jules bridge |
| `pr-auto-merger` | Every 60min | Auto-merge approved PRs, route conflicts |
| `jules-monitor` | Every 30min | Pull completed Jules sessions |
| `agy-reporter` | Every 60min | Check AGY research progress |

## Repo Health Requirements

Before routing work to Jules, the target repo must:
1. Have a clean `main` branch (CI passing)
2. Be accessible via `jules remote list --repo`
3. Not have uncommitted local-only files that Jules needs
4. Have clear issue descriptions (Jules works from Linear text)
