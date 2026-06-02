# Memory Tiering & Knowledge Base Architecture (GRO-67)

## Problem Statement

Long-running orchestrator sessions accumulate conversation history linearly. After 2+
hours of multi-agent delegation, the context window fills with:

- Completed task handoffs (detailed YAML blocks, often 500–2000 tokens each)
- Agent-to-agent routing decisions and their justifications
- Intermediate log output and error traces
- Repeatedly re-injected skill definitions that were already used

This dilutes the model's effective working memory. Key symptoms:

| Symptom | Root Cause | Observed In |
|---------|-----------|-------------|
| Model "forgets" early decisions | Middle-context degradation | Sessions >1h |
| Repeatedly asks for already-provided context | Token budget consumed by stale data | Sessions >200K tokens |
| Makes contradictory routing choices | Lost context about earlier task outcomes | Multi-batch sessions |
| API costs spiral (DeepSeek 1M → $0.56/call at 400K tokens) | No pruning of dead history | All long sessions |

The solution: a **three-tier memory architecture** that moves information from
ephemeral working memory through progressively cooler, more durable storage tiers —
mirroring how human memory works (working → short-term → long-term).

---

## Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      MEMORY TIERS                           │
│                                                             │
│  🔥 HOT (session context)                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Current task + active subagent contexts              │   │
│  │ Skills matched to current task                      │   │
│  │ Last N messages (uncompressed)                      │   │
│  │                                     Lifetime: <1h   │   │
│  │                                     Size: <80K tok  │   │
│  └──────────────────────────┬──────────────────────────┘   │
│                             │                               │
│               Compression + summarization                   │
│               (triggered at 0.50 context threshold)         │
│                             │                               │
│                             ▼                               │
│  🌤️ WARM (daily journal)                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Compressed summaries of completed tasks              │   │
│  │ Routing decision log (which agent did what, why)     │   │
│  │ Key decisions + rationale                           │   │
│  │ Searchable via embeddings (all-MiniLM-L6-v2)         │   │
│  │                                     Lifetime: 30d   │   │
│  │                                     Size: ~5K/day   │   │
│  └──────────────────────────┬──────────────────────────┘   │
│                             │                               │
│               Archival + dedup + indexing                   │
│               (nightly cron or session-end trigger)         │
│                             │                               │
│                             ▼                               │
│  ❄️ COLD (durable knowledge base)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Skill definitions (SKILL.md corpus, 42 files)        │   │
│  │ Docs/ reference material                             │   │
│  │ Archived session summaries (searchable)              │   │
│  │ Learned patterns (successful routing templates)      │   │
│  │                                     Lifetime: ∞     │   │
│  │                                     Size: ~1MB      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1. 🔥 Hot Memory — Current Session Context

Hot memory is the model's immediate working memory: everything actively in the
conversation context.

**What lives in hot memory:**

| Component | Typical Size | Lifecycle |
|-----------|-------------|-----------|
| System prompt + tool definitions | ~2,000 tokens | Entire session |
| Matched skills for current lane | ~10,000–30,000 tokens | Until task switch |
| Last 20 uncompressed messages | varies | Protected by compressor |
| Current task handoff contract | ~500–2,000 tokens | Until task completes |
| Active subagent contexts | ~5,000–20,000 each | Until subagent returns |
| MEMORY.md (personalization) | ~550 tokens | Entire session |
| USER.md (preferences) | ~320 tokens | Entire session |

**Eviction policy:**

Hot memory is managed by the existing context compression engine
([context-window-pruning.md](./context-window-pruning.md)). When the token count
exceeds 50% of the context window (compression threshold: 0.50), the compressor:

1. **Protects:** Last 20 messages, first 3 messages, current task definition
2. **Summarizes:** Older messages into compressed bullet-point summaries
3. **Promotes to warm:** Completed task handoffs are extracted, formatted, and
   appended to the daily journal
4. **Drops:** Old log output, error traces (unless marked critical), verbose
   intermediate results

```yaml
# Hot memory eviction rules
compression:
  threshold: 0.50           # Fire at 50% context window
  protect_last_n: 20        # Keep recent messages intact
  protect_first_n: 3        # Keep initial context
  protect_current_task: true # Never compress the active task definition
  promote_to_warm:
    - type: "completed_task_handoff"
      format: "yaml"
    - type: "routing_decision"
      format: "json"
    - type: "error_with_resolution"
      format: "markdown"
  drop_immediately:
    - "stdout_log_lines"     # Verbose agent output
    - "intermediate_results" # Superseded by final handoff
    - "retry_attempts"       # Only keep the successful attempt
```

### 2. 🌤️ Warm Memory — Daily Journal Summaries

Warm memory is the bridge between ephemeral session context and permanent knowledge.
It's implemented through the **hermes-daily-memory-journal** skill and stored as
structured entries.

**Journal entry format:**

```yaml
# Daily Memory Journal Entry
# Stored at: ~/.hermes-agent/memory/journal/YYYY-MM-DD.yaml
# or: docs/swarm/session-journals/YYYY-MM-DD.yaml

date: "2026-05-29"
session_count: 4
total_tasks_completed: 12
total_tokens_used: 847000
estimated_cost: 3.41

sessions:
  - session_id: "sess_2026-05-29T1423_a3f2"
    duration: "1h12m"
    orchestrator: "deepseek-v4-pro"
    tasks:
      - task_id: "gro-61"
        agent: "hermes"
        lane: "documentation"
        status: "completed"
        handoff_summary: >
          Designed BroadcastChannel-based cross-tab synchronization
          for swarm dashboard. Leader election with heartbeat protocol,
          localStorage state sharing, viewer mode UX.
        key_decisions:
          - "Chose BroadcastChannel over SharedWorker (simpler, no service worker)"
          - "Bully algorithm for leader election (deterministic, no coordinator)"
        files_produced:
          - "docs/swarm/cross-tab-sync.md"
        routing_quality: "good"  # self-assessed by orchestrator

      - task_id: "gro-66"
        agent: "hermes"
        lane: "documentation"
        status: "completed"
        handoff_summary: >
          Multiplexed SSE stream design: single endpoint fanning in
          multiple PTY/agent backends. Client-side demuxer into
          multi-column dashboard view.
        key_decisions:
          - "SSE over WebSocket (simpler HTTP infra, auto-reconnect)"
          - "30s heartbeat per task to prevent silent stalls"
        files_produced:
          - "docs/swarm/multiplexed-sse-streams.md"
        routing_quality: "good"

  - session_id: "sess_2026-05-29T1536_b7e1"
    duration: "58m"
    orchestrator: "deepseek-v4-pro"
    tasks:
      - task_id: "gro-67"
        agent: "agy"
        lane: "research"
        parent_task: "gro-67-memory-tiering"
        status: "completed"
        handoff_summary: >
          Researched memory tiering patterns from LangChain, MemGPT,
          and ChromaDB ecosystems. Identified 3-tier model as best fit
          for swarm's context constraints.
        key_decisions:
          - "Recommend 3-tier (hot/warm/cold) over 2-tier (loss of searchability)"
          - "Warm tier: daily YAML journals with embeddings"
        routing_quality: "good"

routing_patterns_learned:
  # Patterns that emerged during the day's sessions
  - pattern: "Documentation tasks"
    best_agent: "hermes"
    avg_duration: "35m"
    success_rate: 1.0
    notes: "Hermes produces the cleanest, most cross-referenced docs"

  - pattern: "Research-before-code tasks"
    best_pipeline: ["agy:research", "hermes:design", "jules:implement"]
    avg_duration: "2h10m"
    notes: "AGY's context_links cut Hermes discovery time by ~40%"

errors_and_resolutions:
  - error: "AGY scope breach on GRO-67 (added implementation details)"
    resolution: "Accepted benign breach; updated scope_adherence in handoff contract"
    contract_update: "handoff-contracts.md"
```

**Search and retrieval:**

Warm memory is indexed with embeddings for semantic search:

```typescript
// Embedding model: all-MiniLM-L6-v2 (384 dimensions, fast on CPU)
interface WarmMemoryIndex {
  // Built at journal-write time
  entries: {
    id: string;              // "YYYY-MM-DD:task_id"
    embedding: Float32Array; // 384-dim
    metadata: {
      date: string;
      taskId: string;
      agent: string;
      status: string;
      topics: string[];      // Extracted via simple keyword + TF-IDF
    };
    summary: string;         // handoff_summary text
  }[];
}

function searchWarmMemory(
  query: string,
  topK: number = 5,
  filters?: { agent?: string; dateRange?: [string, string] }
): WarmMemoryEntry[] {
  const queryEmbedding = embed(query);
  let candidates = warmMemoryIndex.entries;
  if (filters?.agent) {
    candidates = candidates.filter(e => e.metadata.agent === filters.agent);
  }
  return topKBy(vectorSimilarity(candidates, queryEmbedding), topK);
}
```

**When warm memory is queried:**

- **At session start:** The orchestrator checks warm memory for related prior tasks
  (top-3 by semantic similarity) and injects summaries into the context.
- **During routing:** If a new task resembles a prior pattern (e.g., "build a pipeline
  for X" → `jules` with `agy` pre-research), the orchestrator uses warm memory to
  accelerate routing decisions.
- **After errors:** Search warm memory for similar errors and their resolutions.

### 3. ❄️ Cold Memory — Durable Knowledge Base

Cold memory is the permanent store: skills, documentation, session archives, and
learned patterns that survive indefinitely.

**What lives in cold memory:**

| Store | Location | Content | Update Frequency |
|-------|----------|---------|------------------|
| Skills corpus | `~/.hermes-agent/skills/` | 42 SKILL.md files | Manual edits via AGY |
| Docs/ | `docs/` | Architecture, process, designs | Continuous (Jules/Hermes) |
| Session archives | `docs/swarm/session-journals/` | All daily journals, compressed | Nightly |
| Routing templates | `docs/swarm/routing-*.md` | Proven agent → task patterns | Weekly |
| Prompt templates | `docs/swarm/*-prompt-template.md` | Agent prompt blueprints | As refined |

**Cold memory query:**

Cold memory is NOT loaded into context windows by default (it's too large: ~1MB).
Instead, it's accessed through:

1. **Skill matching (existing):** The skill loader matches SKILL.md files by regex
   against the user's message and injects matched skills into hot memory. This is
   unchanged.
2. **Semantic search:** When the orchestrator encounters a novel situation, it queries
   cold memory embeddings (same `all-MiniLM-L6-v2` model) for relevant docs, session
   summaries, and routing templates. Results are injected as compressed context
   snippets (~500 tokens max).
3. **Explicit reference:** Task definitions can include `context_links` pointing to
   cold memory docs (e.g., `"docs/swarm/routing-decision-matrix.md"`). The orchestrator
   loads and injects these.

### 4. Tiering Policy: What Moves When and How

```
┌──────────┐     Compressor fires      ┌──────────┐    Nightly cron    ┌──────────┐
│   🔥     │ ─────────────────────────► │   🌤️     │ ────────────────► │   ❄️     │
│   HOT    │   Promote completed        │   WARM   │   Archive >30d    │   COLD   │
│          │   task handoffs            │          │   old journals    │          │
│          │   + routing decisions      │          │   Dedup entries   │          │
│          │                            │          │   Extract patterns│          │
└──────────┘                            └──────────┘                   └──────────┘
      ▲                                       │                              │
      │                                       │                              │
      │    Session start: search warm         │   On-demand:                  │
      │    memory for related tasks           │   search cold memory          │
      │    (top-3 results injected)           │   (max 500 tokens)            │
      │                                       │                              │
      └───────────────────────────────────────┴──────────────────────────────┘
```

**Promotion triggers:**

| From → To | Trigger | Action |
|-----------|---------|--------|
| Hot → Warm | Compressor fires (0.50 threshold) | Extract completed task handoffs, routing decisions; append to daily journal |
| Hot → Warm | Session ends (user closes or `stream:eos`) | Flush all remaining hot task summaries to warm journal |
| Warm → Cold | Nightly cron (02:00 UTC) | Journals older than 30 days are compressed (gzip), moved to `session-journals/archive/`, and embeddings are re-indexed |
| Warm → Cold | Manual "archive" command | Operator triggers archival of a specific session or day |
| Cold → Hot | Session start | Semantic search for related past tasks; inject top-3 summaries into context |
| Cold → Hot | Task dispatch | `context_links` in task definition trigger doc load + injection |
| Cold → Hot | Routing decision | Search routing templates for similar task patterns |

**Deduplication:**

When promoting from Warm → Cold, the nightly cron:
- Identifies duplicate or near-duplicate session summaries (same task pattern, same outcome)
- Merges them into a single entry with `occurrence_count` and `last_seen` fields
- Keeps the most detailed version and links to the rest

```yaml
# Example deduped cold memory entry
pattern: "documentation_task_hermes"
occurrence_count: 47
first_seen: "2026-04-01"
last_seen: "2026-05-29"
canonical_summary: >
  Hermes-produced documentation tasks follow a predictable pattern:
  1. Read existing docs for consistency
  2. Write complete design with YAML configs + TypeScript examples
  3. Cross-reference related docs
  4. Include implementation checklists
  Avg duration: 35m. Success rate: 98%.
```

### 5. Integration with hermes-daily-memory-journal Skill

The existing `hermes-daily-memory-journal` skill handles the Hot → Warm promotion.
This design extends it with:

**New journal fields:**

```yaml
# Additions to existing hermes-daily-memory-journal format
# (see skill at ~/.hermes-agent/skills/hermes-daily-memory-journal/SKILL.md)

# NEW: Warm memory indexing metadata
warm_index:
  embedding_model: "all-MiniLM-L6-v2"
  embedding_dim: 384
  last_indexed: "2026-05-29T23:00:00Z"
  entry_count: 127

# NEW: Routing pattern extraction
routing_patterns_learned:
  - pattern: "string"
    best_agent: "jules | agy | hermes | codex | pipeline"
    pipeline_steps: ["agent:lane", ...]  # for multi-agent patterns
    avg_duration: "string"
    success_rate: 0.0–1.0
    notes: "string"

# NEW: Error resolution library
errors_and_resolutions:
  - error: "string"          # Error signature
    count: 3                 # How many times encountered
    resolution: "string"     # What fixed it
    contract_update: "string" # If a handoff contract was updated

# NEW: Cold memory archive pointer
cold_archive:
  archived_journals: 12      # Number of journals >30d old
  archive_path: "docs/swarm/session-journals/archive/"
  total_compressed_size: "156KB"
```

**Skill behavior changes:**

- On session end, skill now also computes embeddings for new journal entries (fast:
  <50ms per entry with all-MiniLM-L6-v2 on CPU).
- Skill maintains a small vector index file (`~/.hermes-agent/memory/journal/index.json`)
  that can be mmap'd for fast search.
- Skill provides a `search-memory` function callable by the orchestrator at session
  start:

```bash
# Orchestrator calls this before dispatching tasks
hermes memory search "cross-tab synchronization dashboard" --top-k 3 --agent hermes
# Returns: top-3 warm memory entries with summaries, timestamps, and outcome
```

---

## Token Budget Impact

| Scenario | Without Tiering | With Tiering | Savings |
|----------|----------------|--------------|---------|
| 2h session, 8 tasks | ~350K tokens | ~180K tokens | 49% |
| 4h session, 15 tasks | ~650K tokens | ~280K tokens | 57% |
| 8h session, 30 tasks | Would overflow (1M+) | ~420K tokens | — |
| Session restart (next day) | 0 prior context | Top-3 warm results (~1.5K tokens injected) | Adds context cheaply |

**Cost impact (DeepSeek v4-pro, $1.40/M input tokens):**

| Session length | Without tiering | With tiering | Daily savings |
|---------------|----------------|--------------|---------------|
| 2h | $0.49 | $0.25 | $0.24 |
| 4h | $0.91 | $0.39 | $0.52 |
| 8h | ~$1.50+ | $0.59 | ~$0.91 |

At 30 sessions/month averaging 2h: ~$7.20/month savings on API costs alone.
Additional benefit: higher-quality outputs from cleaner context.

---

## Implementation Steps

### Phase 1: Warm Memory Journal (Week 1)
- [ ] Extend `hermes-daily-memory-journal` SKILL.md with new fields (routing patterns, errors, warm index)
- [ ] Add `handoff_summary` extraction to orchestrator's compression handler
- [ ] Write journal on session end (both graceful and crash-recovery)
- [ ] Implement embedding computation for journal entries (all-MiniLM-L6-v2)

### Phase 2: Search & Retrieval (Week 2)
- [ ] Build vector index for warm memory entries (~/.hermes-agent/memory/journal/index.json)
- [ ] Implement `search-memory` CLI in the skill
- [ ] Wire session-start query: orchestrator searches warm memory for related tasks
- [ ] Wire routing query: orchestrator checks warm memory before assigning agent lanes

### Phase 3: Cold Archival (Week 3)
- [ ] Nightly cron: archive journals >30d old to `session-journals/archive/`
- [ ] Dedup logic for pattern extraction
- [ ] Cold memory embedding index for docs/ and archived sessions
- [ ] `context_links` integration: auto-load referenced cold docs into hot memory

---

## Cross-References

- [Context Window Pruning (GRO-58)](./context-window-pruning.md) — the compression
  engine that triggers Hot → Warm promotion
- [Handoff Contracts (GRO-84)](./handoff-contracts.md) — the `handoff_summary` field
  feeds warm memory
- [Routing Decision Matrix](./routing-decision-matrix.md) — warm memory routing
  patterns populate and refine this matrix over time
- [Routing Refinements (GRO-86)](./routing-refinements.md) — error resolution patterns
  from warm memory inform routing rule updates
- [hermes-daily-memory-journal skill](https://hermes-agent.nousresearch.com/docs) —
  existing skill that this design extends
