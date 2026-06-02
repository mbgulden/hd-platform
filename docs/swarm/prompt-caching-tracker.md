# Prompt Caching Prefill Tracker for Swarm (GRO-65)

## Problem Statement

Suboptimal prompt structure prevents LLM engines from reusing KV caches across turns and sessions, causing higher latency and cost. The orchestrator (deepseek-v4-pro on 1M context) sends the same ~2K token system prefix on every API call with zero cache reuse. Across 126 daily calls (30 sessions + 96 cron cycles), this wastes ~252K tokens/day on re-encoding identical content.

### Current State

- **prompt_caching.cache_ttl** is set to `5m` in all configs (orchestrator, deepseekv4, hermeslocal, qwenlocal)
- **Only Anthropic-protocol providers** get cache_control breakpoints (native Anthropic, OpenRouter Claude, MiniMax, Qwen/Alibaba on OpenCode)
- **DeepSeek (the primary provider)** gets **zero prompt caching** — no cache_control markers, no auto-caching detection
- **OpenAI Codex** uses session-level `prompt_cache_key` via `extra_headers`
- **Local models (Ollama/vLLM)** get whitespace normalization for KV cache reuse but no explicit caching hints

---

## How Prompt Caching Works Per Provider

### Anthropic (Native)

- **Mechanism**: `cache_control: { type: "ephemeral" }` on message content blocks
- **TTL**: 5m (1.25× write cost) or 1h (2× write cost)
- **Read discount**: ~90% cheaper than full input price (only 10% of original cost)
- **Breakpoints**: Up to 4 per request. System prompt + last 3 non-system messages.
- **Hermes status**: ✅ Fully supported. `apply_anthropic_cache_control()` injects `system_and_3` strategy for all Anthropic-protocol providers.

### OpenAI (Chat Completions)

- **Mechanism**: Automatic prefix caching — server-side, no client markers needed
- **TTL**: 5–10 minutes (undocumented, empirically observed)
- **Read discount**: 50% off input tokens for cache hits
- **Behavior**: Any repeated prefix across requests is cached. The first message (system prompt) is naturally cached after the first call in a session.
- **Limitations**: No control over TTL, no guaranteed cache hits. Works best when system prompt is identical between calls.
- **Hermes status**: ✅ Passive benefit. OpenAI models benefit from auto-caching when the system prompt prefix is stable.

### OpenAI Codex (Responses API)

- **Mechanism**: Session-scoped cache via `extra_headers: { session_id, x-client-request-id }` and body-level `prompt_cache_key`
- **TTL**: Session-scoped (persists across turns within a session)
- **Read discount**: Varies; semantic caching at the session level
- **Hermes status**: ✅ Fully supported. Codex transport injects session_id as `prompt_cache_key`.

### DeepSeek

- **Primary API** (`/v1/chat/completions`): OpenAI-compatible. DeepSeek has **not** publicly documented automatic prefix caching for this endpoint. Empirical evidence from community reports suggests no automatic caching.
- **Anthropic-compatible endpoint** (`/v1/anthropic`): Supports Anthropic-style `cache_control` markers — same breakpoint/TTL semantics. This is the endpoint Hermes already routes to when `api_mode: anthropic_messages`.
- **Current Hermes status**: ❌ **No caching applied.** Because:
  1. The default `api_mode` for DeepSeek is `chat_completions` (OpenAI wire format)
  2. `_anthropic_prompt_cache_policy()` only applies to `api_mode == 'anthropic_messages'` providers
  3. DeepSeek's chat_completions path has no automatic caching from DeepSeek's side
- **Fix options** (see Recommendations below)

### xAI (Grok)

- **Mechanism**: `extra_body.prompt_cache_key` + `extra_headers.x-grok-conv-id` via session_id
- **TTL**: Session-scoped
- **Hermes status**: ✅ Supported via Codex Responses transport.

### Local Models (Ollama, vLLM)

- **Mechanism**: KV cache reuse via prefix matching — deterministic when the same model+seed processes identical prefixes
- **Requirement**: Bit-perfect prefix matching. Hermes already normalizes whitespace in `api_messages` for this purpose.
- **Hermes status**: ✅ Passive. Whitespace normalization enables cache hits but no explicit breakpoint markers.

---

## Current Hermes Prompt Structure Analysis

### System Prompt Assembly (First Message)

The system prompt is the single message at `api_messages[0]` with `role: "system"`. It is assembled from these components in order:

| # | Component | Source | Static? | Est. Tokens | Notes |
|---|-----------|--------|---------|-------------|-------|
| 1 | **Agent Identity** | Hardcoded Hermes Agent persona | ✅ Static | ~250 | "You are Hermes Agent, an intelligent AI assistant..." |
| 2 | **Host/Environment Hints** | `build_environment_hints()` | ✅ Static per-host | ~80 | OS, user home, CWD |
| 3 | **Platform Hints** | Platform-specific (slack/telegram/etc.) | ✅ Static per-platform | ~150 | Markdown formatting, media delivery rules |
| 4 | **Skills Index** | `build_skills_system_prompt()` | ⚠️ Semi-static | ~1,200–2,500 | List of 41 skills with descriptions. Changes only when skills dir changes. |
| 5 | **Memory** | `MEMORY.md` (auto-generated) | ⚠️ Semi-static | ~550 | Daily-updated, 2,200 char limit |
| 6 | **User Profile** | `USER.md` (auto-generated) | ⚠️ Semi-static | ~320 | Rarely changes, 1,375 char limit |
| 7 | **Context Files** | `.hermes.md`, `HERMES.md`, `SOUL.md` in repo | ✅ Static | Variable | Project-specific instructions |
| 8 | **Ephemeral/Task Prompt** | Delegation instructions, task brief | 🔴 Dynamic | Variable | Changes every turn/delegation |

**Total system prompt**: ~2,000–3,500 tokens for the orchestrator.

### Where Cache Breakpoints Should Go

```
┌─────────────────────────────────────────────────┐
│ SYSTEM MESSAGE (api_messages[0])                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ CACHE BREAKPOINT 1: Agent Identity + Host   │ │ ← 250+80 tokens, fully static
│ │ + Platform Hints                            │ │
│ ├─────────────────────────────────────────────┤ │
│ │ Skills Index                                │ │ ← ~1,200–2,500 tokens, semi-static
│ │ CACHE BREAKPOINT 2: End of skills index     │ │   changes only on skill add/remove
│ ├─────────────────────────────────────────────┤ │
│ │ Memory + User Profile + Context Files       │ │ ← ~870+ tokens, semi-static
│ │ CACHE BREAKPOINT 3: End of static context   │ │   changes daily (memory) or rarely
│ ├─────────────────────────────────────────────┤ │
│ │ Dynamic task preamble (delegation prompt)   │ │ ← Variable, NOT cached
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘

TOOLS DEFINITION: Fully static per-session, ideal candidate for caching.
                  Anthropic supports cache_control on tool definitions.

LAST 3 TURN MESSAGES: Breakpoints on recent messages to keep conversation
                      cache warm across rapid turns.
```

### Why Current Structure Prevents Cache Hits

For DeepSeek's chat_completions endpoint:
1. The system prompt is assembled with dynamic content **interleaved with** static content — memory and user profile sit inside the same system message, not after it
2. The skills index is recalculated every session from filesystem state — even when nothing changed
3. No breakpoint markers are placed (DeepSeek doesn't accept Anthropic markers on chat_completions)
4. The delegation/ephemeral prompt is appended at the end of the system message, changing the message body and invalidating any prefix cache

---

## Recommended Cache Breakpoints

### Strategy: Split Static + Semi-static Into Prefix, Dynamic Into Suffix

Rather than shoving everything into one system message, restructure the prompt so cacheable sections form clean prefixes:

```
Message 1 (system, CACHED): Agent Identity + Host + Platform
Message 2 (system, CACHED): Skills Index
Message 3 (system, CACHED): Memory + User Profile
Message 4 (system, NOT CACHED): Dynamic task preamble
```

### For DeepSeek Specifically

Two approaches:

#### Approach A: Use DeepSeek `/v1/anthropic` Endpoint (Recommended)

Switch DeepSeek to `api_mode: anthropic_messages` with base_url `https://api.deepseek.com/v1/anthropic`:

- **Pros**: Gets full Anthropic cache_control support (4 breakpoints, 5m/1h TTL, 90% read discount)
- **Cons**: Requires Hermes config change; DeepSeek's Anthropic endpoint enforces thinking token round-trip contract
- **Hermes already handles this**: The `anthropic_adapter.py` has explicit `_is_deepseek_anthropic_endpoint()` detection for thinking block round-tripping

#### Approach B: Leverage OpenAI Auto-caching on chat_completions

Keep the existing `api_mode: chat_completions` but restructure the prompt to maximize prefix stability:

- **Pros**: No endpoint migration; no config changes needed
- **Cons**: Only gets 50% discount (vs 90% with Anthropic caching); no TTL control; DeepSeek may not implement auto-caching at all
- **Risk**: DeepSeek's auto-caching behavior is undocumented — this may yield zero benefit

#### Approach C: Pre-compute Skills Prompt Snapshot (Complementary)

Hermes already has a `_write_skills_snapshot()` function that caches the skills index to disk. Currently this is used for in-process caching but the system prompt is rebuilt per-session. 

- Cache the full `build_skills_system_prompt()` output to disk (already done: `.skills_prompt_snapshot.json`)
- Use the cached string verbatim in the system prompt rather than re-assembling it
- This ensures the skills portion is a stable string, improving prefix matching for any caching mechanism

---

## Expected Savings

### DeepSeek-v4-pro Pricing Assumptions

Based on community reports and published estimates:
- Input: ~$1.40/M tokens (standard), ~$0.14/M tokens (cache hit at 90% discount)
- Output: ~$5.60/M tokens

### Per-Session Savings (Orchestrator, 10-turn session)

| Scenario | System Tokens/Turn | Cache Hit? | Input Cost/Turn | Annual @ 30/day |
|----------|-------------------|------------|-----------------|-----------------|
| **Current** (no caching) | ~2,500 | No | $0.0035 | $38.33 |
| **Approach A** (DeepSeek Anthropic endpoint, 90% discount) | ~2,500 | Yes (system) | $0.00035 (system) + $0.0035 (non-cached) | ~$15–20 |
| **Approach B** (OpenAI auto-cache, 50% discount) | ~2,500 | Maybe | $0.00175 (system) + $0.0035 (non-cached) | ~$25–30 |
| **Approach C** (prompt restructuring + auto-cache) | ~2,500 | Better hit rate | Similar to B but more reliable | ~$20–25 |

### Cumulative Swarm Impact

With the orchestrator handling ~126 calls/day (30 sessions × ~10 turns + 96 cron jobs × ~3 turns):

| Approach | Daily System Token Savings | Annual Cost Savings |
|----------|---------------------------|---------------------|
| A (DeepSeek Anthropic) | ~280K tokens/day | ~$50–75/year |
| B+C (Restructure + auto-cache) | ~140K tokens/day | ~$25–35/year |
| Combined with context pruning (GRO-58) | Additive — pruning reduces total tokens, caching reduces unit cost | ~$75–110/year total |

### Latency Savings

Cache hits eliminate prompt encoding time. For a 2,500-token system prefix:

| Provider | Encoding Latency (est.) | Cache Hit Latency |
|----------|------------------------|-------------------|
| DeepSeek-v4-pro | ~200–400ms | ~0ms (skipped) |
| Claude (Anthropic) | ~300–500ms | ~0ms |
| GPT-5.x (OpenAI) | ~150–300ms | ~0ms |

In a 10-turn orchestration session, this saves **2–4 seconds** total — meaningful for user-facing interactions.

---

## Implementation Plan

### Phase 1: Config-Only Changes (5 minutes, zero risk)

**Switch DeepSeek to the Anthropic-compatible endpoint** to enable full prompt caching:

```yaml
# ~/.hermes/profiles/orchestrator/config.yaml
providers:
  deepseek:
    # Switch to Anthropic-compatible endpoint for cache_control support
    api: https://api.deepseek.com/v1/anthropic
    api_mode: anthropic_messages  # ADD THIS LINE
```

This change:
- ✅ Hermes already handles DeepSeek's Anthropic endpoint thinking round-trips (`_is_deepseek_anthropic_endpoint()` in `anthropic_adapter.py`)
- ✅ `_anthropic_prompt_cache_policy()` auto-detects Anthropic-wire + Claude-named models → but DeepSeek models don't have "claude" in name!
- ⚠️ **Gap**: The policy function gates caching on `is_claude` for third-party Anthropic gateways (line 3594). DeepSeek models are named `deepseek-v4-pro`, not `claude-*`, so they would NOT auto-get caching.

**Required code fix**: Update `_anthropic_prompt_cache_policy()` in `run_agent.py` to also match DeepSeek models when `api_mode == 'anthropic_messages'`:

```python
# After line 3593:
# Add DeepSeek check before the generic is_claude gate
model_is_deepseek = "deepseek" in model_lower
if is_anthropic_wire and model_is_deepseek:
    return True, True  # native layout on DeepSeek's /anthropic endpoint
```

### Phase 2: Prompt Structure Optimization (requires Hermes Agent feature)

Restructure the system prompt assembly so cacheable components form clean prefixes:

1. **Split static from dynamic** in the system message:
   - Static part: Agent identity + host + platform + skills → cacheable prefix
   - Separator message or section boundary before dynamic content
   
2. **Use snapshot-cached skills prompt** rather than rebuilding per session:
   - Hermes already writes `.skills_prompt_snapshot.json` to disk
   - Use the precomputed string verbatim in system prompt assembly

3. **Add explicit cache_control breakpoints** for providers that support them:
   - System prompt: 1 breakpoint at end of static prefix
   - Tools definition: 1 breakpoint (Anthropic supports cache_control on tools)
   - Last 2-3 assistant/user turns: remaining breakpoints

### Phase 3: Extend to All DeepSeek Profiles

Apply the same caching configuration to `deepseekv4` and any other profiles using `provider: deepseek`:

```yaml
# ~/.hermes/profiles/deepseekv4/config.yaml
prompt_caching:
  cache_ttl: 5m  # Already present, keep

# If using anthropic endpoint:
providers:
  deepseek:
    api_mode: anthropic_messages
```

### Phase 4: Cache Hit Monitoring

Add a runtime footer field or dashboard metric showing cache hit rate:

```yaml
# ~/.hermes/config.yaml
display:
  runtime_footer:
    enabled: true
    fields:
      - model
      - context_pct
      - cache_pct  # NEW: show cached token percentage
```

---

## Summary of Required Changes

### Config Changes

| File | Setting | Current | Proposed | Risk |
|------|---------|---------|----------|------|
| orchestrator/config.yaml | `providers.deepseek.api_mode` | (default: chat_completions) | `anthropic_messages` | Low |
| orchestrator/config.yaml | `providers.deepseek.api` | `https://api.deepseek.com/v1` | `https://api.deepseek.com/v1/anthropic` | Low |
| deepseekv4/config.yaml | Same as above | Same | Same | Low |

### Code Changes (Hermes Agent)

| File | Change | Priority |
|------|--------|----------|
| `run_agent.py:_anthropic_prompt_cache_policy()` | Add `is_deepseek` check for Anthropic-wire DeepSeek models | **Critical** — without this, DeepSeek on /anthropic won't get caching |
| `prompt_builder.py:build_skills_system_prompt()` | Use snapshot-cached string for stable prefix | Medium |
| `prompt_builder.py:build_environment_hints()` | Make consistently ordered (already is) | Low — verify |

### No Changes Needed

- **hermeslocal/qwenlocal**: Already benefit from whitespace normalization for KV cache reuse on Ollama/vLLM
- **openai-codex**: Already has session-scoped prompt_cache_key
- **anthropic**: Already fully supported with system_and_3 strategy
- **xAI**: Already has prompt_cache_key in extra_body

---

## Cross-Reference: Interaction with GRO-58 (Context Pruning)

GRO-58 (Context Window Pruning) and GRO-65 (Prompt Caching) are complementary:

- **GRO-58** reduces **total tokens** sent → less to cache, lower write costs, more cache entries fit in provider limits
- **GRO-65** reduces **re-encoding cost** of tokens that are still sent → lower latency, lower cost per token

When combined:
- A 50% reduction in system prompt size (from GRO-58 skill curation) means 50% less cache storage and 50% lower cache write costs
- Caching ensures the remaining 50% is only paid for once per TTL window

---

## Appendix: Provider Caching Reference

| Provider | Mechanism | TTL | Read Discount | Hermes Support | Notes |
|----------|-----------|-----|---------------|----------------|-------|
| Anthropic (native) | `cache_control` breakpoints | 5m / 1h | ~90% | ✅ Full | Up to 4 breakpoints |
| Anthropic (OpenRouter) | Envelope `cache_control` | 5m | ~90% | ✅ Full | Claude models on OR |
| DeepSeek (/anthropic) | `cache_control` breakpoints | Unknown | Unknown | ❌ Need to add | Uses Anthropic protocol |
| DeepSeek (/v1) | Automatic? (undocumented) | Unknown | Unknown | ❌ None | May auto-cache like OpenAI |
| OpenAI (chat) | Automatic prefix caching | ~5–10m | 50% | ✅ Passive | No markers needed |
| OpenAI Codex (responses) | `prompt_cache_key` + session headers | Session-scoped | Varies | ✅ Full | Session-level |
| xAI Grok (responses) | `prompt_cache_key` + conv-id header | Session-scoped | ~90% | ✅ Full | |
| Ollama | Prefix matching (deterministic) | Per-session | 100% (local) | ✅ Passive | Whitespace normalization enables |
| vLLM | PagedAttention prefix sharing | Per-session | 100% (local) | ✅ Passive | Same prefix → shared KV blocks |
| Qwen (OpenCode/DashScope) | Envelope `cache_control` | 5m | Varies | ✅ Full | Alibaba family |
| MiniMax (/anthropic) | `cache_control` breakpoints | 5m | 10% of original | ✅ Full | Documented support |

---

## Task Summary

- **GRO-65** identified a gap: DeepSeek (primary orchestrator provider) gets zero prompt caching benefit
- **Root cause**: Hermes's `_anthropic_prompt_cache_policy()` only applies caching to Anthropic-protocol providers with Claude-named models. DeepSeek uses `chat_completions` mode by default and is not recognized by the policy function.
- **Fix**: Two-part: (1) Switch DeepSeek to its `/v1/anthropic` endpoint (config change), (2) Add `is_deepseek` detection in the cache policy function (code change)
- **Expected benefit**: ~90% input cost reduction on system prompt tokens (the ~2,500 token static prefix), saving ~$50–75/year at current usage levels
- **Latency benefit**: ~200–400ms saved per turn from skipping prompt encoding
