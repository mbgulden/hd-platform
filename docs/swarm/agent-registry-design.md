# Agent Registry Design — Roles, Models, Wrappers & State (GRO-36)

The Agent Registry is the canonical inventory of every role, model, provider, agent wrapper,
and their live state. It's the data backbone that powers the Agent Manager's Inventory Panel
and the Quick-Launch profile selector.

---

## 1. Role Taxonomy

Every agent in the swarm plays one or more **roles**. Roles determine what the agent is
capable of, which skills get loaded, and how the router classifies incoming tasks.

### Primary Role Lanes

| Role | Profile(s) | Primary Capabilities | Router Task Types |
|------|-----------|---------------------|-------------------|
| **orchestrator** | `orchestrator`, `hermeslocal`, `qwenlocal` | Multi-agent coordination, deployment supervision, incident response, task triage, verification, escalation | `deployment_supervision`, `multi_agent_validation`, `incident_response`, `code_review_coordination`, `research_coordination` |
| **planner** | `orchestrator` | Architecture design, system documentation, workflow design, project planning | (Sub-role of orchestrator — docs-first tasks) |
| **coder** | `jules` | Code creation/modification, PR management, test writing, refactoring, dependency management | Code tasks (`.ts`, `.py`, `.astro`, `.yaml`, etc.) |
| **reviewer** | `codex` | PR review, security audit, code quality assessment, architecture review, proactive scanning | Code review, security audit |
| **researcher** | `agy` | Document analysis, web research, Google Drive/Takeout processing, vision pipeline, content strategy, competitor analysis | Research, content, web scraping |
| **3D/modeling** | `orchestrator`, `hermeslocal`, `qwenlocal` (future) | Prompt/image-to-3D, 3D printing workflows, game asset generation, VM101 recovery | (Future lane — Asset Forge 3D workspace) |
| **summarizer** | `agy`, `orchestrator` | Session/intake summarization, meeting notes, podcast show notes, content condensation | (Auxiliary — used within other task types) |
| **pricing analyst** | `agy`, `orchestrator` | Competitor pricing analysis, market positioning, margin analysis, bid/ask modeling | (Specialized researcher lane — Sentinel IT Asset Logistics) |
| **infra-readonly** | `hermeslocal`, `qwenlocal` | Homelab inventory, GPU health checks, network topology docs, observability dashboards | (Local-only — no production write access) |

### Role Hierarchy

```
                    ┌─────────────────┐
                    │  ORCHESTRATOR   │  ← Can delegate to any role
                    │  (meta-role)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐      ┌──────▼──────┐      ┌─────▼─────┐
   │  PLANNER  │      │  RESEARCHER │      │  REVIEWER  │
   │ (docs,    │      │  (AGY)      │      │  (Codex)   │
   │  design)  │      └──────┬──────┘      └───────────┘
   └───────────┘             │
                    ┌────────┼────────┐
                    │        │        │
              ┌─────▼──┐ ┌──▼────┐ ┌─▼──────────┐
              │  CODER  │ │SUMMAR.│ │PRICING      │
              │ (Jules) │ │       │ │ANALYST      │
              └─────────┘ └───────┘ └─────────────┘

   ┌──────────────────┐        ┌──────────────────┐
   │  3D / MODELING   │        │  INFRA-READONLY  │
   │  (future lane)   │        │  (local only)    │
   └──────────────────┘        └──────────────────┘
```

### Cross-Role Overlaps

Some profiles can serve multiple roles:

| Profile | Can Act As |
|---------|-----------|
| `orchestrator` | orchestrator, planner, summarizer, pricing analyst, infra-readonly (limited) |
| `hermeslocal` | orchestrator (local), planner (local), infra-readonly |
| `qwenlocal` | orchestrator (light), infra-readonly |
| `agy` | researcher, summarizer, pricing analyst, content strategist |
| `codex` | reviewer |
| `jules` | coder |

---

## 2. Model Inventory

Every model available to the swarm, organized by provider and capability profile.

### Active Models

| Model ID | Provider | Context Window | Strengths | Cost Profile | Best For |
|----------|----------|---------------|-----------|-------------|----------|
| **deepseek-v4-pro** | deepseek | 1,000,000 | Massive context, strong reasoning, tool use, compression-friendly | ~$1.40/M input tokens | Orchestration, multi-agent coordination, docs, large-context analysis |
| **deepseek-v4-flash** | deepseek | 1,000,000 | Fast, cheap, good for summarization/compression | Lower cost | Context compression, fast auxiliary tasks, fallback |
| **gpt-5.5** | openai-codex | 272,000 | Deep code review, security pattern detection, architecture analysis | Higher cost | Code review, security audit, quality assessment |
| **gpt-5.4-mini** | openai-codex | — | Vision, extraction, title generation, triage | Low cost | Auxiliary tasks: image analysis, web extraction, session titles |
| **gpt-5.4-nano** | openai-codex | 400,000 | Lightweight, high-throughput compression | Lowest cost | Context compression for local models |
| **hermes3:70b-llama3.1-q4_K_M** | ollama-hermes | 65,536 (default) / 131,072 (extended) | Local execution, no API cost, good general reasoning | Free (local GPU) | Local orchestration, infra-readonly tasks, private data |
| **qwen3:32b-q4_K_M** | ollama-qwen | 65,536 (default) | Fast local inference, lightweight | Free (local GPU) | Lightweight local tasks, health checks |
| **qwen3:32b-q4_K_M-256k** | ollama-qwen | 262,144 | Extended context for local use | Free (local GPU) | Local document analysis (when 65K is insufficient) |
| **qwen3:32b-q4_K_M-1M** | ollama-qwen | 1,048,576 | Massive local context | Free (local GPU) | Local large-context tasks (experimental) |
| **chat-latest** | openai-direct | — | General purpose, latest features | Standard | Ad-hoc general tasks |

### Future / Planned Models

| Model ID | Provider | Context | Status | Use Case |
|----------|----------|---------|--------|----------|
| **hermes-3-70b (full weights)** | local (vllm) | 131K+ | 🔮 Planned | High-quality local orchestration without quantization loss |
| **hermes-3-405b** | local (vllm) | — | 🔮 Planned | Maximum-capability local model (when hardware allows) |
| **qwen3-235b** | local (vllm) | — | 🔮 Planned | High-capability local alternative |
| **Custom fine-tuned models** | local (vllm) | — | 🔮 Planned | Domain-specific fine-tunes for pricing, 3D, human design |

### Model Selection Logic

The router and Quick-Launch select models based on:

1. **Task type** → role required → profile → default model
2. **Context budget** — Is the task likely to exceed the model's context window?
3. **Cost sensitivity** — High-cost models (gpt-5.5) reserved for review/audit only
4. **Privacy requirements** — Local models for sensitive data (infra-readonly)
5. **Availability** — Fallback chain if primary model is rate-limited or down

### Fallback Chains

| Primary Model | Fallback 1 | Fallback 2 | Fallback 3 |
|--------------|------------|------------|------------|
| deepseek-v4-pro | gpt-5.5 | hermes3:70b | qwen3:32b |
| gpt-5.5 | deepseek-v4-flash | hermes3:70b | qwen3:32b |
| hermes3:70b | qwen3:32b | deepseek-v4-flash | gpt-5.4-mini |
| qwen3:32b | hermes3:70b | deepseek-v4-flash | — |

---

## 3. Provider / Backend Registry

Every API endpoint and local inference server the swarm can use.

### Active Providers

| Provider Key | Type | Endpoint | Auth Method | Default Model | Timeout | Status |
|-------------|------|----------|-------------|---------------|---------|--------|
| `deepseek` | Cloud API | api.deepseek.com/v1 | API key (`${DEEPSEEK_API_KEY}`) | deepseek-v4-pro | 300s | ✅ Active |
| `openai-codex` | Cloud API | api.openai.com/v1 | API key (`${OPENAI_API_KEY}`) | gpt-5.5 | 300s | ✅ Active |
| `openai-direct` | Cloud API | api.openai.com/v1 | API key (`${OPENAI_API_KEY}`) | chat-latest | 300s | ✅ Active |
| `ollama-hermes` | Local GPU | http://100.78.237.7:31435/v1 | None (local) | hermes3:70b-q4_K_M | 600s | ✅ Active |
| `ollama-qwen` | Local GPU | http://100.78.237.7:31434/v1 | None (local) | qwen3:32b-q4_K_M | 600s | ✅ Active |

### Health Check Parameters

| Check | Interval | Timeout | Failure Threshold | Recovery Threshold |
|-------|----------|---------|-------------------|-------------------|
| Endpoint reachable (HTTP 200) | 60s | 10s | 3 consecutive failures → `endpoint-down` | 2 consecutive successes → `active` |
| Model loaded (Ollama `/api/tags`) | 120s | 10s | 2 consecutive failures → `degraded` | 1 success → `active` |
| Inference test (simple ping prompt) | 300s | 30s | 1 failure → `degraded` | 1 success → `active` |
| Auth verification (API key valid) | 3600s | 10s | 1 failure → `auth-unverified` | 1 success → `active` |
| Rate limit status | On 429 response | — | Immediate → `rate-limited` | Cooldown expiry → previous state |

### Provider Status State Machine

```
                    ┌──────────┐
                    │  ACTIVE  │
                    └────┬─────┘
                         │
          ┌──────────────┼──────────────────┐
          │              │                  │
    health check    health check       API 429
       fails          degrades          response
          │              │                  │
          ▼              ▼                  ▼
   ┌────────────┐  ┌──────────┐    ┌─────────────┐
   │ENDPOINT-   │  │ DEGRADED │    │ RATE-LIMITED│
   │DOWN        │  │ (model   │    │ (token      │
   │            │  │  missing)│    │  refresh)   │
   └─────┬──────┘  └────┬─────┘    └──────┬──────┘
         │              │                  │
    endpoint back   model loaded      cooldown
         │              │              expires
         ▼              ▼                  │
    ┌────────┐    ┌──────────┐             │
    │ ACTIVE │    │  ACTIVE  │◄────────────┘
    └────────┘    └──────────┘

   ┌──────────────────┐
   │ AUTH-UNVERIFIED  │  ← API key check fails
   └────────┬─────────┘
            │
      key updated & verified
            │
            ▼
       ┌────────┐
       │ ACTIVE │
       └────────┘
```

### Planned Providers

| Provider Key | Type | Status | Notes |
|-------------|------|--------|-------|
| `vllm-hermes` | Local GPU (vLLM) | 🔮 Planned | OpenAИ-compatible API on local GPU for Hermes full weights |
| `vllm-qwen` | Local GPU (vLLM) | 🔮 Planned | OpenAИ-compatible API for Qwen full weights |
| `vllm-mistral` | Local GPU (vLLM) | 🔮 Planned | Open for future Mistral local models |
| `local-openai-compat` | Local GPU (any) | 🔮 Planned | Generic OpenAИ-compatible endpoint for custom models |

---

## 4. Agent Wrapper Registry

How each agent is invoked, configured, and produces output. The wrapper is the
mechanical interface between "we have a model" and "we can dispatch work to it."

### Wrapper Catalog

| Wrapper ID | Type | Profile/CLI | Invocation | Output | Session Tracked |
|-----------|------|------------|-----------|--------|-----------------|
| `hermes-profile` | Profile session | Any Hermes profile (orchestrator, hermeslocal, qwenlocal) | `hermes -p <profile>` or gateway message | File edits, terminal output, handoff contract | `sessions/session_*.json` |
| `agy-cli` | CLI agent | agy | `agy --print '/goal ...' --print-timeout 600s` | Research documents, analysis reports | AGY sub-sessions tracked in its own log |
| `jules-cli` | CLI agent | jules | `jules new --repo OWNER/REPO "task description"` | GitHub PR, branch, commit | `/tmp/jules-session-tracker.json` |
| `codex-cli` | CLI agent | codex | `hermes -p codex-5-5 -z "Review PR #X"` | Review report, severity counts, verdict | `sessions/session_*.json` |
| `cron-job` | Scheduled | Any profile | `cron/jobs.json` entry → auto-dispatched | Cron output markdown files | `sessions/session_cron_*.json` |
| `gateway` | Channel session | orchestrator | Telegram/Slack message | Conversational response, tool calls | `sessions/session_*.json` |

### Wrapper Details

#### hermes-profile
```yaml
wrapper: hermes-profile
profiles:
  - id: orchestrator
    config: ~/.hermes/profiles/orchestrator/config.yaml
    skills: 41 SKILL.md files (~223K tokens)
    channels: [telegram, slack, cron]
    session_pattern: session_{date}_{time}_{random}.json
  - id: hermeslocal
    config: ~/.hermes/profiles/hermeslocal/config.yaml
    skills: ~12 curated (~80K tokens)
    channels: [cron]
    session_pattern: session_{date}_{time}_{random}.json
  - id: qwenlocal
    config: ~/.hermes/profiles/qwenlocal/config.yaml
    skills: ~8 curated (~50K tokens)
    channels: [cron]
    session_pattern: session_{date}_{time}_{random}.json
```

#### agy-cli
```yaml
wrapper: agy-cli
binary: agy
mode: PTY (pseudo-terminal required)
input: YAML prompt (see agy-prompt-template.md)
output: Markdown report, CSV, or JSON at deliverable_path
sub_sessions: 1–5 parallel
timeout: --print-timeout (default 600s)
constraints:
  - Bounded scope required (in_scope/out_of_scope)
  - Cannot write outside deliverable_path
  - No GitHub write access
  - No terminal execution
tracking: AGY maintains its own session log at ~/.gemini/antigravity-cli/log/
```

#### jules-cli
```yaml
wrapper: jules-cli
binary: jules
mode: CLI (non-PTY)
input: CLI args + YAML prompt (see jules-prompt-template.md)
output: GitHub PR URL, branch, commit SHA
session_cap: 300/day
concurrent_cap: 10
constraints:
  - GitHub-state only (push before assigning)
  - No local file access
  - No environment variables or secrets
  - Repo CI must be green on main
  - Branch convention enforced: gro-XX/description or type/description
tracking: /tmp/jules-session-tracker.json
pre_flight_checks:
  - CI green on main
  - Repo accessible via jules remote list
  - Lockfile recent (<24h old)
```

#### codex-cli
```yaml
wrapper: codex-cli
profile: codex-5-5
binary: hermes -p codex-5-5
mode: CLI/Profile
input: CLI args or prompt
output: Review report, verdict (approved|changes_requested|blocked), severity counts
token_refresh: ~3 hours (falls back to deepseek-v4-flash)
review_capacity: ~20 PRs per refresh cycle
constraints:
  - Read-only (advisory reviews)
  - Cannot write code or approve PRs
  - Token exhaustion = partial review
```

#### cron-job
```yaml
wrapper: cron-job
config: ~/.hermes/profiles/orchestrator/cron/jobs.json
dispatch: Hermes Agent cron scheduler
mode: Background, non-interactive
output: Markdown files in cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
jobs:
  - jules-session-manager: every 15m (Linear → Jules bridge)
  - pr-auto-merger: every 60m (auto-merge approved PRs)
  - jules-monitor: every 30m (pull completed Jules sessions)
  - agy-reporter: every 60m (check AGY research progress)
```

#### gateway
```yaml
wrapper: gateway
channels:
  - platform: telegram
    chat_id: "8190664947"
    type: dm
  - platform: slack
    channels: [C0B4SQUCT1D, C0B4UEHSVEK, C0B53FLB18T]
mode: Interactive, multi-turn
profile: orchestrator (default gateway profile)
session_lifecycle:
  - created on first message
  - idle between user messages (gateway_auto_continue_freshness: 3600s)
  - completed on explicit close or timeout
```

---

## 5. State Tracking

Every agent, profile, model, provider, and session has a live state. The state system
is the heartbeat of the Agent Manager — it tells operators what's healthy, what's
degraded, and what needs attention.

### State Values

| State | Icon | Semantics | Applies To |
|-------|------|-----------|------------|
| `active` | 🟢 | Operating normally, accepting work | Profiles, models, providers, cron jobs |
| `busy` | 🔵 | At capacity, queuing new work | Profiles (all sessions active), jules (near 300/day) |
| `available` | 🟢 | Idle, ready for immediate dispatch | Profiles, models |
| `inactive` | ⚫ | Configured but not currently running | Local models (GPU off), optional profiles |
| `endpoint-down` | 🔴 | Provider endpoint unreachable after retries | Providers (HTTP health check failure × 3) |
| `auth-unverified` | 🟡 | API key needs verification or rotation | Providers (auth check failure) |
| `rate-limited` | 🟡 | Token refresh cycle active, reduced capacity | codex (3hr cycle), any cloud model during 429 |
| `degraded` | 🟠 | Running but with fallback model or reduced capabilities | Profiles (primary model down, using fallback) |
| `error` | 🔴 | Failed health check or runtime crash, needs intervention | Profiles, cron jobs, providers |
| `running` | 🔵 | Session is actively executing tool calls | Sessions |
| `idle` | 🟢 | Session alive, waiting for next user message | Gateway sessions |
| `completed` | ✅ | Session finished successfully with handoff contract | Sessions |
| `failed` | ❌ | Session terminated with error | Sessions |
| `timed_out` | ⏰ | Session exceeded timeout_minutes | Sessions |
| `cancelled` | 🚫 | Operator cancelled the session | Sessions |
| `escalated` | 🔴 | Session hit escalation path, needs human | Sessions |

### State Determination Logic

#### Provider State
```python
def provider_state(provider_key: str) -> State:
    health = health_check(provider_key)  # HTTP GET /v1/models
    if health.consecutive_failures >= 3:
        return State.ENDPOINT_DOWN
    if auth_check(provider_key).failed:
        return State.AUTH_UNVERIFIED
    if rate_limit_active(provider_key):
        return State.RATE_LIMITED
    if health.model_missing:
        return State.DEGRADED
    return State.ACTIVE
```

#### Profile State
```python
def profile_state(profile_id: str) -> State:
    config = load_config(profile_id)
    model_state = provider_state(config.model.provider)

    if model_state == State.ENDPOINT_DOWN:
        if fallback_available(config):
            return State.DEGRADED  # Running on fallback
        return State.ERROR

    if model_state == State.RATE_LIMITED:
        return State.DEGRADED

    active_sessions = count_active_sessions(profile_id)
    if active_sessions >= max_concurrent(profile_id):
        return State.BUSY

    return State.ACTIVE
```

#### Session State
```python
def session_state(session_id: str) -> State:
    session = load_session(session_id)

    if session.cancelled:
        return State.CANCELLED
    if session.escalated:
        return State.ESCALATED
    if session.completed:
        return State.COMPLETED if session.success else State.FAILED
    if session.timed_out:
        return State.TIMED_OUT
    if session.last_activity_age > IDLE_THRESHOLD:
        return State.IDLE
    return State.RUNNING
```

### State Transitions That Trigger Alerts

| Transition | Alert Channel | Severity |
|-----------|--------------|----------|
| Any provider → `endpoint-down` | `#eng-alerts` | 🔴 Critical |
| Any provider → `auth-unverified` | `#eng-alerts` | 🔴 Critical |
| `orchestrator` → `degraded` | `#eng-deploys` | 🟡 High |
| `jules` → `busy` (300/300) | `#eng-deploys` | 🟡 High |
| Any session → `failed` × 3 in 1 hour | `#eng-alerts` | 🟡 High |
| Any session → `escalated` | `#eng-alerts` | 🔴 Critical |
| `secrets_clean` fail | `#eng-alerts` + key rotation | 🔴 Immediate |

---

## 6. Role + Model Pairing Recommendations

Which model to use for which role, with rationale and fallbacks.

### Pairing Matrix

| Role | Primary Model | Rationale | Fallback Model | When to Use Fallback |
|------|-------------|-----------|----------------|---------------------|
| **Orchestrator** | deepseek-v4-pro | 1M context for multi-agent coordination, strong reasoning, all 41 skills | gpt-5.5 | DeepSeek endpoint down; higher cost but strong reasoning |
| **Orchestrator (local)** | hermes3:70b | Free local inference, good for infra-readonly and private data | qwen3:32b | Hermes 70B GPU down; Qwen faster but less capable |
| **Orchestrator (lightweight)** | qwen3:32b | Fast, free, good for health checks and simple cron | hermes3:70b | Qwen 32B GPU down; Hermes 70B heavier but more capable |
| **Planner** | deepseek-v4-pro | 1M context for architecture docs, cross-referencing | hermes3:70b | DeepSeek down; local but smaller context |
| **Coder** | jules (CLI, model varies) | Jules selects its own model; designed for code gen | N/A | Jules manages its own fallback |
| **Reviewer** | gpt-5.5 | Best-in-class code review and security pattern detection | deepseek-v4-flash | Token refresh cycle exhausted; faster but less thorough |
| **Researcher** | agy (CLI, model varies) | AGY selects based on task: vision needs, context size | N/A | AGY manages its own model selection |
| **Summarizer** | deepseek-v4-flash | Cheap, fast, 1M context for large document summaries | gpt-5.4-mini | DeepSeek down; smaller context but adequate |
| **Pricing Analyst** | deepseek-v4-pro | Needs strong reasoning and cross-referencing | hermes3:70b | DeepSeek down; local but private data safe |
| **3D/Modeling** | (future) | No current 3D-specific model | — | — |
| **Infra-readonly** | hermes3:70b | Local only (no cloud), private network data, zero API cost | qwen3:32b | Hermes 70B down; Qwen 32B lighter |

### Pairing Rules

1. **Cloud vs. Local split:**
   - Tasks with sensitive data → local models only (hermes3:70b, qwen3:32b)
   - Tasks needing large context or strong reasoning → cloud models
   - Tasks that are cost-sensitive and non-urgent → local first, cloud fallback

2. **Cost hierarchy (cheapest first):**
   ```
   qwen3:32b (free) < hermes3:70b (free) < deepseek-v4-flash < deepseek-v4-pro < gpt-5.4-mini < gpt-5.5
   ```

3. **Context window hierarchy (largest first):**
   ```
   deepseek-v4-pro (1M) = deepseek-v4-flash (1M) > gpt-5.4-nano (400K) > gpt-5.5 (272K)
   > qwen3:32b-256k (262K) > hermes3:70b (65-131K) > qwen3:32b (65K)
   ```

4. **Automatic model selection by task characteristics:**

   | Characteristic | Selected Model |
   |---------------|---------------|
   | Task context > 200K tokens | deepseek-v4-pro (only model with sufficient headroom) |
   | Task context 100K–200K | deepseek-v4-pro or gpt-5.5 |
   | Task context < 100K, private data | hermes3:70b |
   | Task context < 65K, cost-critical | qwen3:32b |
   | Task requires vision analysis | gpt-5.4-mini (vision auxiliary) |
   | Task is code review / security audit | gpt-5.5 (no substitutes for security) |
   | Task is fast compression/summary | deepseek-v4-flash |
   | Task is cron/periodic, low urgency | Local model when available, else cheapest cloud |

---

## 7. Registry Data Model

The registry is backed by the existing Hermes Agent configuration files plus
runtime health data. No new data store is required — the registry is a **view**
over existing state.

### Data Sources

```yaml
registry_sources:
  profiles:
    source: "~/.hermes/profiles/*/config.yaml"
    fields: [model.default, model.provider, compression, skills, delegation, context]
  
  providers:
    source: "config.yaml → providers{}"
    fields: [api, api_key_env, default_model, context_length, request_timeout]
  
  models:
    source: "models_dev_cache.json"
    fields: [id, name, family, limit.context, cost, modalities]
    refresh: "24h from https://hermes-agent.nousresearch.com/docs/api/model-catalog.json"
  
  workspaces:
    source: "config.yaml → workspaces[]"
    fields: [id, name, description, local_paths, github_repos, linear_projects, 
             default_profile, allowed_profiles, tags]
  
  sessions:
    source: "sessions/sessions.json + sessions/session_*.json"
    fields: [id, profile, model, provider, status, workspace, channel, 
             created_at, completed_at, tool_calls, tokens_used]
  
  cron_jobs:
    source: "cron/jobs.json"
    fields: [id, schedule, profile, last_run, last_status, output_path]
  
  channel_directory:
    source: "channel_directory.json"
    fields: [platform, channels with id/name/type]
  
  health_checks:
    source: "runtime (live polling)"
    fields: [provider_status, model_loaded, auth_valid, rate_limit_remaining]
```

### Registry Query Patterns

| Query | Implementation |
|-------|---------------|
| "Which models can handle 500K tokens?" | Filter models where `limit.context >= 500000` |
| "What's the cheapest model for a research task?" | Filter researcher-eligible models, sort by `cost.input` |
| "Is Jules available for a new task?" | Check `jules` sessions today < 300 AND concurrent < 10 |
| "Which workspaces use ollama-hermes?" | Filter workspaces where `allowed_profiles` includes `hermeslocal` |
| "Show me all failed sessions today" | Filter sessions where `status=failed AND date=today` |
| "Which providers are currently degraded?" | Filter providers where `health_check.state ∈ [degraded, endpoint-down, auth-unverified]` |

---

## Cross-References

- **Agent Manager Architecture** — [agent-manager-architecture.md](./agent-manager-architecture.md) (GRO-34) —
  the UI/information architecture that consumes this registry
- **Plugin Design** — [agent-manager-plugin-design.md](./agent-manager-plugin-design.md) (GRO-37) —
  dashboard UI skeleton that renders registry data
- **Lane Capabilities** — [lane-capabilities.md](./lane-capabilities.md) — verified agent "can/cannot do" inventory
- **Routing Decision Matrix** — [routing-decision-matrix.md](./routing-decision-matrix.md) —
  how task types map to roles/models
- **Context Window Pruning** — [context-window-pruning.md](./context-window-pruning.md) —
  per-model context budgets and token management
- **Swarm Workflow** — [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md) — overall agent architecture
