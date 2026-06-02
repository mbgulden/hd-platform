# Repo Mapping Policy (GRO-20)

Rule: each Linear project maps to a GitHub repository or directory. README standards,
project notes, `.cursorrules`, and current project-to-repo mappings.

---

## Core Rule

> **One Linear Project → One GitHub Repository (or directory within a monorepo)**

Every piece of work done by the swarm must have a clear canonical location. No ambiguity
about where code lives, where docs go, or where to open PRs.

---

## Current Project-to-Repo Mapping

| Linear Project | GitHub Repo | Local Path | Nickname | Notes |
|---------------|-------------|------------|----------|-------|
| HD Engine Core | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Monorepo: API, reports, content, docs |
| Reports | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Lives in monorepo under `reports/` |
| Growth | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Marketing, landing pages, content |
| Creator | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Creator tools and dashboards |
| Coach | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Coaching platform features |
| Consumer | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Consumer-facing reports and tools |
| Enterprise | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Enterprise tier features |
| Dating | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Dating app integration |
| Education | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Educational content and tools |
| AI Lab | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | AI experiments and research |
| OpenHumanDesignMCP | `mbgulden/OpenHumanDesignMCP` | `/home/ubuntu/work/OpenHumanDesignMCP` | `hd-engine` | Core HD computation engine |
| Agentic Swarm Ops | `mbgulden/agentic-swarm-ops` | `/home/ubuntu/work/agentic-swarm-ops` | `swarm-ops` | Swarm orchestration and ops scripts |
| Sovereign Sentinel | `mbgulden/SovereignSentinel` | `/home/ubuntu/work/SovereignSentinel` | `sentinel` | Security and monitoring |
| Active Oahu Tours | `mbgulden/activeoahutours.com` | `/home/ubuntu/work/activeoahutours.com` | `active-oahu` | Active Oahu Tours website |
| Project Honeybadger | `mbgulden/hd-platform` | `/home/ubuntu/work/hd-platform` | `hd-platform` | Stealth project in monorepo |
| AI Consulting | `mbgulden/ai-consulting` | `/home/ubuntu/work/ai-consulting` | `ai-consulting` | AI consulting deliverables |

---

## Monorepo Directory Map (`hd-platform`)

Since most Linear projects map to the `hd-platform` monorepo, here's where each project's
files live within that repo:

```
/home/ubuntu/work/hd-platform/
├── api/                    # HD Engine Core — FastAPI application
├── reports/                # Reports project — report templates, generation
├── hd-content/             # Growth project — content, blog, podcasts
├── docs/
│   ├── swarm/              # Agentic Swarm Ops — documentation (cross-repo)
│   └── active-oahu/        # Active Oahu Tours — planning docs
├── ops/                    # Agentic Swarm Ops — scripts (shared)
├── src/                    # Creator + Consumer — frontend components
├── scripts/                # Shared automation scripts
├── tests/                  # Shared test suites
├── docker/                 # Enterprise — Docker configurations
├── k8s/                    # Enterprise — Kubernetes manifests
└── README.md               # Top-level project overview
```

---

## README Standards

Every repo and every major directory within the monorepo must have a README.md that
answers these questions:

### Top-Level Repo README

```markdown
# Project Name

## What This Is
[1-2 sentence description of the project]

## Quick Start
```bash
# How to get running in <5 minutes
git clone ...
cd ...
# install + run
```

## Architecture
[High-level diagram or description of components]

## Development
- Branch convention: [link to SWARM-WORKFLOW.md]
- PR process: [link to relevant docs]
- Testing: [how to run tests]

## Deployment
[Where it's deployed, how to deploy]

## Links
- Linear: [project board link]
- Slack: [#channel]
- Docs: [link to docs directory]
```

### Directory README (Monorepo Subdirectories)

```markdown
# Directory Name

## Purpose
[What lives here]

## Key Files
- `file1.py` — [what it does]
- `file2.yaml` — [what it configures]

## Related
- Parent project: [link to Linear project]
- Dependencies: [what this depends on]
- Consumers: [what depends on this]
```

### Minimum Viable README

At a minimum, every directory with >3 files must have a README.md with:
- **Purpose:** 1 sentence on what this directory is for
- **Entry point:** Which file to read first
- **Related:** Link to at least one related doc or Linear project

---

## Project Notes (`.project-notes.md`)

Each repo root should have a `.project-notes.md` file (gitignored) for ephemeral
project context that doesn't belong in the README.

```markdown
# Project Notes — [Date Range]

## Active Context
- What we're working on right now
- Current sprint focus
- Blocked items and why

## Decisions Made
- [Date] Decision and rationale
- [Date] Decision and rationale

## Open Questions
- Question? (asked by: @who, date)
- Question? (asked by: @who, date)

## Agent Activity Log
- [Date] Jules GRO-100: Added podcast automation (PR #42)
- [Date] AGY GRO-77: Q2 competitor pricing analysis
- [Date] Hermes GRO-85: Router operator quickstart docs
```

**Rules for `.project-notes.md`:**
- Gitignored — never committed
- Written by agents automatically (append-only)
- Human-readable scratchpad
- Trimmed periodically (archive entries > 30 days old)

---

## `.cursorrules` Standards

Every repo should have a `.cursorrules` file for AI-assisted development in Cursor IDE.
These rules bootstrap agent context and enforce conventions.

### Required Sections

```yaml
# .cursorrules — Project Conventions

# 1. Branch Discipline
# ALWAYS create a feature branch before editing files.
# Format: gro-XX/brief-description
# Use ops/branch-discipline.py before any write_file/patch call.

# 2. Commit Convention
# Use Conventional Commits: type: description
# Types: fix, feat, refactor, test, docs, chore, ci

# 3. Testing
# Write tests for all new code.
# Run tests before opening PR.
# Target: 80%+ coverage on new code.

# 4. Code Style
# [Language-specific rules — e.g., Prettier for TS, Black for Python]

# 5. File Organization
# [Where different types of files go]

# 6. Linear Integration
# Reference Linear issue keys in commits and PRs.
# Format: "Closes GRO-XX" in PR body.

# 7. Agent Workflow
# See docs/swarm/ for agent routing rules.
# Jules handles code. AGY handles research. Codex reviews. Hermes coordinates.
```

### Repo-Specific `.cursorrules` Examples

**`hd-platform` (monorepo, TypeScript/Python/Astro):**
```yaml
# .cursorrules — hd-platform
language: typescript, python, astro
test_framework: pytest, vitest
formatter: prettier, black
package_manager: npm, pip
branch_prefix: gro-XX/
base_branch: main
ci_required: true
```

**`OpenHumanDesignMCP` (Python MCP server):**
```yaml
# .cursorrules — OpenHumanDesignMCP
language: python
test_framework: pytest
formatter: black
package_manager: pip
branch_prefix: gro-XX/
base_branch: main
ci_required: true
additional_rules:
  - "All ephemeris data is read-only — do not modify"
  - "Chart computation must match Neutrino Design output"
  - "Validate against verification dataset before PR"
```

**`agentic-swarm-ops` (ops scripts, docs):**
```yaml
# .cursorrules — agentic-swarm-ops
language: python, bash, markdown
test_framework: pytest (Python), shellcheck (Bash)
formatter: black, shfmt
branch_prefix: gro-XX/
base_branch: main
ci_required: false
additional_rules:
  - "Scripts must be idempotent — safe to run repeatedly"
  - "All ops scripts go in ops/ directory"
  - "Docs go in docs/swarm/ in hd-platform repo (cross-repo)"
```

---

## Mapping Rules

### Rule 1: One Owner Per Repo

Each GitHub repo has a designated primary agent responsible for its health:
- `hd-platform` → Hermes (orchestrator, main work area)
- `OpenHumanDesignMCP` → Jules (primary coding agent)
- `agentic-swarm-ops` → Hermes (orchestrator, ops scripts)
- `SovereignSentinel` → Hermes (security)
- `activeoahutours.com` → AGY + Jules (research + implementation)
- `ai-consulting` → Hermes (orchestrator)

### Rule 2: No Cross-Repo File Moves Without Hermes

If a task requires moving files between repos (e.g., extracting a library from the
monorepo into its own repo), Hermes must coordinate. No single agent moves files
across repo boundaries.

### Rule 3: Monorepo Projects Use Directory Ownership

Within `hd-platform`, each Linear project owns specific directories. When Jules works
on a task, `files_to_modify` must stay within the project's directory boundaries.
Cross-project file changes require Hermes coordination.

### Rule 4: New Projects Get New Repos (or Monorepo Directories)

- **New independent service** → New GitHub repo
- **New feature of existing service** → Monorepo directory
- **New experiment** → Monorepo directory under `experiments/`
- **New content site** → Consider existing repo or new repo based on tech stack

### Rule 5: Docs Live Near Code

- Per-repo docs → `docs/` in that repo
- Swarm ops docs → `docs/swarm/` in `hd-platform` (central reference)
- Project planning docs → `docs/<project>/` in `hd-platform`

---

## Adding a New Project

When a new Linear project is created, follow this checklist:

1. **Choose location:**
   - [ ] New GitHub repo or monorepo directory? (Rule 4)
   - [ ] If new repo: create it under `mbgulden/`
   - [ ] If monorepo: create directory in `hd-platform`

2. **Initialize structure:**
   - [ ] README.md (follow README standards above)
   - [ ] `.cursorrules` (follow standards above)
   - [ ] `.project-notes.md` (gitignored, empty)
   - [ ] `.gitignore` (if new repo)
   - [ ] CI/CD pipeline (GitHub Actions)

3. **Register mapping:**
   - [ ] Add row to the mapping table in this document
   - [ ] Add to SWARM-WORKFLOW.md repo map
   - [ ] Register with `jules remote list --repo` (for Jules-accessible repos)

4. **Configure agent access:**
   - [ ] Jules: `jules remote add` the new repo
   - [ ] AGY: Add repo context to AGY prompt template
   - [ ] Codex: Add repo to proactive scan list
   - [ ] Hermes: Add to orchestrator repo registry

5. **Create Linear project:**
   - [ ] Create in Linear with appropriate team
   - [ ] Add standard labels: `agent:jules`, `agent:agy`, `agent:chatgpt55`
   - [ ] Link to GitHub repo in Linear project settings

---

## Repo Health Checks (Automated)

The orchestrator runs these checks daily on all registered repos:

| Check | Frequency | Alert if... |
|-------|-----------|------------|
| CI green on `main` | Every 30 min | Red for >1 hour |
| README exists | Daily | Missing from repo root |
| `.cursorrules` exists | Daily | Missing from repo root |
| Branch protection on `main` | Daily | Disabled |
| Open PRs > 7 days old | Daily | Any found |
| Stale branches (>30 days) | Weekly | >5 found |
| Secrets scan | Weekly | Any found |

---

## Cross-References

- Swarm architecture: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)
- Jules evaluation: [jules-cli-evaluation](./jules-cli-evaluation.md)
- Branch discipline: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md#branch-convention-all-agents--mandatory)
- Agent capabilities: [lane-capabilities](./lane-capabilities.md)
