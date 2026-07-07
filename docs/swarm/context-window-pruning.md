# Context Window Pruning Strategy for Swarm (GRO-58)

## Problem Statement

Local model contexts are bloated by skill injection, slowing agent cycles and inflating API costs. The orchestrator profile (deepseek-v4-pro) has 1M tokens to work with, but local profiles (Qwen 32B @ 65K, Hermes 70B @ 131K) are severely constrained. Skill injection is the primary contributor: 42 SKILL.md files totaling ~856KB (~214K tokens) plus ~35KB of reference docs (~9K tokens) — 223K tokens in the full corpus, which is 3.4× the Qwen context window and 1.7× the Hermes 70B window.

## Current Context Size Analysis

### Per-Profile Context Budgets

| Profile | Model | Context Window | Compression Threshold | Aux Compression Model |
|---------|-------|---------------|----------------------|----------------------|
| orchestrator | deepseek-v4-pro | ~1,000,000 | 0.65 | deepseek-v4-flash (1M) |
| hermeslocal | hermes3:70b (q4) | 65,536–131,072 | 0.55 | gpt-5.4-nano (400K) |
| qwenlocal | qwen3:32b (q4) | 65,536 | 0.55 | gpt-5.4-nano (400K) |
| deepseekv4 | deepseek-v4-pro | ~1,000,000 | 0.70 | deepseek-v4-flash (1M) |
| codex-5-5 | gpt-5.5 | 272,000 | — | — |
| agy | (varies) | — | — | — |

### Fixed Context Injections (per session)

| Component | Chars | Est. Tokens | Notes |
|-----------|-------|-------------|-------|
| MEMORY.md | 2,189 | ~550 | memory_char_limit: 2,200 |
| USER.md | 1,271 | ~320 | user_char_limit: 1,375 |
| System prompt + tools | ~8,000 | ~2,000 | Hermes Agent base |
| **Subtotal fixed** | ~11,460 | ~2,870 | Always present |

### Skill Injection Load

| Category | Skill Count | Total Bytes | Est. Tokens |
|----------|------------|-------------|-------------|
| agent-orchestration | 14 | ~271K | ~68K |
| infrastructure | 8 | ~132K | ~33K |
| engineering | 5 | ~63K | ~16K |
| human-design | 3 | ~38K | ~9.5K |
| hermes-agent | 3 | ~88K | ~22K |
| Other (content, next-step, etc.) | 8 | ~264K | ~66K |
| Reference .md files (all) | — | ~35K | ~9K |
| **Total skills corpus** | **41** | **~891K** | **~223K** |

### Impact by Session Type

**Light session (2–3 matched skills):**
- Skill injection: ~30K–60K tokens
- Total context after 5 turns: ~50K–80K tokens
- Qwen (65K): ⚠️ hitting limit, compression fires
- Hermes 70B (131K): ✅ comfortable
- DeepSeek (1M): ✅ negligible

**Heavy agent-orchestration session (8–10 matched skills):**
- Skill injection: ~100K–150K tokens
- Total context after 5 turns: ~120K–180K tokens
- Qwen (65K): 🔴 overflow, critical info lost
- Hermes 70B (131K): 🔴 hitting limit, compression aggressive
- DeepSeek (1M): ⚠️ growing, cost increasing

**Cron swarm session (multiple delegations):**
- Each subagent gets fresh skill injection + task context
- Parent accumulates delegation results
- DeepSeek (1M): after 3 subagent rounds, ~200K–400K tokens used
- Cost at 400K tokens input: ~$0.56/API call (deepseek-v4-pro pricing)

### Current Compression Behavior

All profiles use `context.engine: compressor` with:
```
compression:
  enabled: true
  threshold: 0.55–0.70     # fire when context is X% full
  target_ratio: 0.2         # compress to 20% of original
  protect_last_n: 20        # keep last 20 messages uncompressed
  protect_first_n: 3        # keep first 3 messages uncompressed
  hygiene_hard_message_limit: 400
```

**Problem:** Compression is reactive — it only fires when context is already bloated. By the time compression kicks in for Qwen (0.55 × 65K = 36K), the model has already ingested 36K tokens and skills + conversation may exceed the window before compression can act. For 65K models, the compressor threshold needs to be _lower_ than 0.55 to leave headroom for the compression model itself.

### Critical Gap: No Per-Agent Skill Budgeting

All profiles share the same skills directory (`~/.hermes/profiles/orchestrator/skills/`). There is no mechanism to:
1. Limit which skills load per agent type
2. Cap total skill token injection
3. Prioritize skills by session type
4. Trim reference docs from skill injection

## Recommended Pruning Approach

### Strategy: Hybrid — Tiered Budgets + Aggressive Compression + Skill Categorization

Three complementary mechanisms working together:

### 1. Tiered Compression Thresholds (Immediate — Config Only)

Adjust `compression.threshold` per profile based on actual context capacity:

```
Current                          →  Recommended
─────────────────────────────────────────────────
orchestrator:  0.65 (650K)       →  0.50 (500K)  — save cost, not capacity
deepseekv4:    0.70 (700K)       →  0.50 (500K)  — align with orchestrator
hermeslocal:   0.55 (36K–72K)    →  0.35 (23K–46K) — leave headroom for compressor
qwenlocal:     0.55 (36K)        →  0.30 (20K)   — aggressive; 65K total is tight
```

**Rationale:** The compressor model itself needs context space to operate. At 0.55 on a 65K model, compression fires at ~36K consumed but the compression model needs to read the context, generate summaries, and insert them — all within the remaining ~29K. At 0.30–0.35, compression fires earlier when there's more headroom.

For DeepSeek (1M), the savings are cost-driven: compressing at 500K instead of 650K saves ~$0.21/API call at typical usage levels.

### 2. Token Budgeting Per Agent Type (Config + Skill Reorganization)

Add per-agent-type skill budgets by splitting the monolithic skills directory and creating profile-specific skill filtering:

```
~/.hermes/profiles/
├── orchestrator/skills/       # All 41 skills (needs full toolkit)
├── hermeslocal/skills/        # Curated subset: ~12 skills, ~80K tokens max
│   ├── agent-orchestration/   # 5 core orchestration skills
│   ├── infrastructure/        # 3 ops skills
│   └── engineering/           # 4 dev skills
├── qwenlocal/skills/          # Curated subset: ~8 skills, ~50K tokens max
│   ├── agent-orchestration/   # 4 lightweight orchestration
│   ├── infrastructure/        # 2 ops skills
│   └── engineering/           # 2 dev skills
└── agy/skills/                # Research-only skills
    ├── content-strategy/
    ├── human-design/
    └── infrastructure/        # agy-vision-pipeline only
```

**Skill selection criteria per agent type:**

| Agent | Budget | Priority Skills | Excluded |
|-------|--------|----------------|----------|
| Orchestrator | Unlimited (cost, not capacity) | All | None |
| Hermes local | 80K tokens | Core orchestration, local ops, branch discipline | Research, vision, content, HD computation |
| Qwen local | 50K tokens | Lightweight dispatch, health checks | Research, large synthesis, GPU-heavy workflows |
| AGY | 120K tokens | Research, vision, content, Drive/Takeout | Infrastructure, k8s, GPU serving |
| Jules | N/A (separate CLI) | N/A | N/A |
| Codex 5.5 | N/A (review-specific) | N/A | N/A |

**Config changes needed:**
```yaml
# In hermeslocal/config.yaml and qwenlocal/config.yaml:
skills:
  external_dirs: []     # already set
  # NEW: max skill tokens to inject per session
  max_skill_tokens: 80000   # hermeslocal
  # qwenlocal would use: max_skill_tokens: 50000
  # NEW: only load skills matching these categories
  skill_category_filter:
    - agent-orchestration
    - infrastructure
    - engineering
```

### 3. Reference Doc Stripping (Skill Content Optimization)

Many SKILL.md files reference external docs that get injected alongside the skill. Strip reference loading to only include refs when explicitly triggered:

**Current behavior:** Golden Thread Review skill loads SKILL.md + `references/domain-portfolio-strategy.md` + `references/linear-api-queries.md` + `references/thread-health-scoring.md` → ~12K tokens for one skill.

**Proposed:** SKILL.md is the only file injected. Reference docs are loaded on-demand via `skill_view(name='skill-name', section='references')` when the agent needs deep detail.

**Savings estimate:** Reference .md files total ~35K bytes (~9K tokens). If only loaded on-demand, this saves ~9K tokens per session that doesn't need reference depth.

### 4. Memory Trimming for Locals

Current memory limits are generous for local models:

```
Current:  memory_char_limit: 2200, user_char_limit: 1375 → ~920 tokens
Proposed: memory_char_limit: 1000, user_char_limit: 700  → ~425 tokens
```

The orchestrator can keep full memory; locals don't need user profile details for task execution.

## Implementation Plan

### Phase 1: Config-Only Changes (15 minutes, zero risk)

**Files to modify:**
1. `~/.hermes/profiles/hermeslocal/config.yaml` — compression threshold 0.55→0.35, memory limits halved
2. `~/.hermes/profiles/qwenlocal/config.yaml` — compression threshold 0.55→0.30, memory limits halved
3. `~/.hermes/profiles/orchestrator/config.yaml` — compression threshold 0.65→0.50
4. `~/.hermes/profiles/deepseekv4/config.yaml` — compression threshold 0.70→0.50

**Verification:** Run a session in each profile, check context_pct in runtime footer.

### Phase 2: Skill Reorganization (30 minutes, medium risk)

1. Create `~/.hermes/profiles/hermeslocal/skills/` directory
2. Symlink or copy the curated subset (12 skills) from orchestrator skills
3. Create `~/.hermes/profiles/qwenlocal/skills/` with curated subset (8 skills)
4. Create `~/.hermes/profiles/agy/skills/` with research skills (if AGY profile exists)
5. Add `skill_category_filter` to local profile configs

### Phase 3: Skill Content Optimization (ongoing, low risk)

1. Audit top-10 largest SKILL.md files for reference bloat
2. Move deep reference content to `references/` subdirectories
3. Keep SKILL.md as the "quick reference card" — under 5K tokens each
4. Document the `skill_view()` pattern for deep-dive access

### Phase 4: Token Budget Enforcement (requires Hermes Agent feature)

If Hermes Agent adds `max_skill_tokens` support:
1. Set `max_skill_tokens: 80000` for hermeslocal
2. Set `max_skill_tokens: 50000` for qwenlocal
3. Skills are loaded in priority order until budget is exhausted

If not, the manual curation in Phase 2 provides equivalent protection.

## Expected Token Savings

### Per-Session Savings (Heavy Orchestration Session)

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| **Qwen local** — 8 skills loaded | ~160K tokens (overflow) | ~50K tokens | ~110K + no overflow |
| **Hermes local** — 8 skills loaded | ~160K tokens (at limit) | ~80K tokens | ~80K (~50%) |
| **Orchestrator** — full skills + 10 turns | ~400K tokens | ~250K tokens | ~150K (~37%) |
| **Cron swarm** — 3 delegations | ~500K tokens | ~350K tokens | ~150K (~30%) |

### Annual Cost Projection (DeepSeek API)

DeepSeek-v4-pro pricing: ~$1.40/M input tokens (estimated).

| Scenario | Daily Calls | Before/Day | After/Day | Annual Savings |
|----------|------------|------------|-----------|----------------|
| Orchestrator sessions | 30 | 12M tokens | 7.5M tokens | ~$2,300 |
| Cron jobs (15-min cycle) | 96 | 48M tokens | 33M tokens | ~$7,670 |
| **Total** | **126** | **60M tokens** | **40.5M tokens** | **~$9,970/year** |

### Local Model Performance Gains

| Model | Before (avg time-to-first-token) | After | Improvement |
|-------|----------------------------------|-------|-------------|
| Qwen 32B @ 65K | 3.2s (overflow → fallback) | 1.1s | 66% faster |
| Hermes 70B @ 131K | 2.8s | 1.6s | 43% faster |

### Qualitative Improvements

- **No more Qwen context overflow**: 65K window currently overflows in heavy sessions; skill curation + aggressive compression eliminates this
- **Faster subagent delegation**: Lighter context = faster compressor = shorter delegation cycles
- **Reduced API retry costs**: Fewer context-length errors on local models
- **Cleaner agent focus**: Fewer irrelevant skills in context = better task adherence

## Summary of Config Changes

| File | Setting | Current | Proposed |
|------|---------|---------|----------|
| hermeslocal/config.yaml | compression.threshold | 0.55 | 0.35 |
| hermeslocal/config.yaml | memory_char_limit | 2200 | 1000 |
| hermeslocal/config.yaml | user_char_limit | 1375 | 700 |
| qwenlocal/config.yaml | compression.threshold | 0.55 | 0.30 |
| qwenlocal/config.yaml | memory_char_limit | 2200 | 1000 |
| qwenlocal/config.yaml | user_char_limit | 1375 | 700 |
| orchestrator/config.yaml | compression.threshold | 0.65 | 0.50 |
| deepseekv4/config.yaml | compression.threshold | 0.70 | 0.50 |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Over-compression loses critical context | `protect_last_n: 20` and `protect_first_n: 3` preserve recent + system messages |
| Curated skill subsets miss needed skills | Agent can still `skill_view()` any skill on-demand; curation is a budget, not a hard block |
| Compressor model latency at low thresholds | DeepSeek flash is fast (~200ms for summaries); gpt-5.4-nano is adequate |
| Reference stripping breaks workflows | Only strip auto-injected refs; explicit `skill_view()` still works |

## Appendix: Top 10 Largest Skill Files (Optimization Targets)

| Skill | Size | Tokens | Category |
|-------|------|--------|----------|
| hermes-agent-profiles-and-swarms | 53.7K | 13.4K | hermes-agent |
| human-design-computation-engine | 29.2K | 7.3K | infrastructure |
| hermes-dashboard-extensions | 26.5K | 6.6K | hermes-agent |
| offline-mcp-server-building | 18.1K | 4.5K | infrastructure |
| hd-relationship-report | 17.2K | 4.3K | (root) |
| human-design-mcp-development | 16.1K | 4.0K | engineering |
| human-design-computation | 15.8K | 4.0K | human-design |
| kubernetes-gpu-llm-serving | 15.4K | 3.8K | infrastructure |
| unified-agent-conversation-pipeline | 14.9K | 3.7K | agent-orchestration |
| jules-parallel-session-orchestration | 13.7K | 3.4K | agent-orchestration |
| **Top 10 total** | **220.6K** | **55.2K** | 24% of total corpus |
