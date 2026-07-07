# Pre-Trust Verification Checklist (GRO-82)

Every agent output must pass this checklist before the orchestrator accepts it as
"done." Run these checks automatically — do NOT trust agent output without verification.

---

## Checklist

Run each check in order. A single ❌ blocks acceptance unless explicitly waived.

### 1. `file_exists` — Deliverables are on disk

```
[ ] Expected file(s) exist at the declared deliverable paths.
    - Check: ls <deliverable_path> returns the file.
    - Check (PRs): PR URL is accessible and returns HTTP 200.
    - Check (research): output file is non-empty (>0 bytes).
    - Waiver: None. No file, no acceptance.
```

**How to auto-check:**
```bash
# Single file
test -f "<deliverable_path>" && test -s "<deliverable_path>" && echo "PASS" || echo "FAIL"

# Multiple files (from expected_outputs)
for f in output/research/q2-report.md output/data/pricing.csv; do
  test -f "$f" && test -s "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```

### 2. `syntax_valid` — Files parse correctly

```
[ ] Markdown files pass markdownlint (or at least don't crash a parser).
[ ] JSON files pass `jq .` (valid JSON).
[ ] YAML files pass `yq eval .` (valid YAML).
[ ] CSV files have consistent column counts across all rows.
[ ] Code files: language-appropriate syntax check (e.g., `tsc --noEmit`, `ruff check`).
    - Waiver: None for structured formats. Prose-only .txt files skip.
```

**How to auto-check:**
```bash
# JSON
jq . "$file" > /dev/null 2>&1 && echo "PASS" || echo "FAIL: invalid JSON"

# YAML
yq eval . "$file" > /dev/null 2>&1 && echo "PASS" || echo "FAIL: invalid YAML"

# Markdown (basic — at minimum, the file opens without binary garbage)
file "$file" | grep -q "ASCII text\|UTF-8" && echo "PASS" || echo "FAIL"

# Python
python -m py_compile "$file" && echo "PASS" || echo "FAIL"

# TypeScript
npx tsc --noEmit "$file" && echo "PASS" || echo "FAIL"
```

### 3. `tests_pass` — Automated tests are green

```
[ ] If tests_required was true: test suite exited with code 0.
[ ] No skipped tests (flagged: agent may have commented out failing tests).
[ ] Test coverage did not decrease (compare to base branch if available).
    - Waiver: Only if tests_required was explicitly false in the task intake.
```

**How to auto-check:**
```bash
# Run tests and capture exit code (applies to Jules tasks)
npm test
test $? -eq 0 && echo "PASS" || echo "FAIL: tests failed"

# Check for skipped tests (suspicious pattern)
grep -r "it.skip\|test.skip\|xit\|xdescribe\|pytest.mark.skip" src/ && echo "WARNING: skipped tests found" || echo "OK: no skipped tests"
```

### 4. `secrets_clean` — No credentials, tokens, or keys in output

```
[ ] No API keys (sk-..., pk-..., github_pat_..., etc.).
[ ] No private keys (-----BEGIN RSA PRIVATE KEY-----, etc.).
[ ] No connection strings with embedded passwords.
[ ] No JWT tokens or session cookies.
[ ] No internal IP addresses or hostnames that shouldn't be public.
    - Waiver: None. A single secret found = automatic rejection.
```

**How to auto-check:**
```bash
# Common secret patterns — extend this list as new patterns emerge
PATTERNS=(
  'sk-[a-zA-Z0-9]{20,}'                    # OpenAI keys
  'github_pat_[a-zA-Z0-9_]{20,}'           # GitHub PAT
  '-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----'  # Private keys
  'mongodb(\+srv)?://[^:]+:[^@]+@'         # DB connection strings with passwords
  'eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}'  # JWT tokens
  '[a-z0-9]{32,}:[a-z0-9]{32,}@'           # user:pass@host
)

for pattern in "${PATTERNS[@]}"; do
  if grep -qE "$pattern" "$file"; then
    echo "FAIL: potential secret found matching: $pattern"
  fi
done
echo "PASS: no secrets detected"
```

### 5. `matches_spec` — Output satisfies the success criteria

```
[ ] Each item in success_criteria is affirmatively checked.
[ ] Numerical thresholds are verified (e.g., "P99 < 200ms" → check Datadog).
[ ] Qualitative criteria have at minimum a human-readable confirmation.
[ ] Output format matches what was requested (markdown_report ≠ spreadsheet).
    - Waiver: Individual criteria can be waived by human, but all must be
      addressed (pass, fail, or waived).
```

**How to auto-check:**
```bash
# This is the most context-dependent check. Example for deployment:
# "P99 latency < 200ms for 10 consecutive minutes"
# Use CloudWatch/Datadog CLI or API:
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name LatencyP99 \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 60 \
  --statistics Average \
  --query 'Datapoints[*].Average' \
  --output text | awk '{if ($1 > 200) exit 1}'

# For research / content output:
# Check that the deliverable mentions all required topics
for keyword in "NexusCloud" "DataForge" "Streamline"; do
  grep -qi "$keyword" "$deliverable" || echo "MISSING: $keyword not found in output"
done
```

### 6. `edge_cases_covered` — Output handles boundary conditions

```
[ ] Error states are handled (what happens on failure?).
[ ] Empty/null/missing data is handled gracefully.
[ ] Large inputs don't cause truncation or overflow.
[ ] Concurrent access / race conditions are addressed (if applicable).
[ ] Rollback path is documented (for deployments and schema changes).
    - Waiver: Only for trivial changes (typo fixes, formatting).
```

**How to check manually (hard to auto-check fully):**
- Review the output for error handling sections.
- Check that error states from `escalation_path` are reflected in the output.
- For code: check that edge case tests exist (`describe('when input is empty', ...)`).
- For deployments: verify the rollback plan is present and executable.

---

## Verification Summary

After running all 6 checks, produce a summary:

```yaml
verification_result:
  task_id: "<task identifier>"
  agent: "<hermes | jules | agy | codex>"
  timestamp: "<ISO-8601>"

  checks:
    file_exists:    pass | fail | waived
    syntax_valid:   pass | fail | waived
    tests_pass:     pass | fail | waived
    secrets_clean:  pass | fail | waived
    matches_spec:   pass | fail | waived
    edge_cases_covered: pass | fail | waived

  overall: pass | fail
  # pass = all checks pass or waived
  # fail = one or more checks failed

  failures:
    # If overall is fail, list every failed check with details.
    # Example:
    #   - check: secrets_clean
    #     details: "Found OpenAI API key pattern in output/research/report.md line 42"
    #     remediation: "Rotate key immediately, strip from file, re-run agent"

  waived:
    # If any checks were waived, list them with justification.
    # Example:
    #   - check: tests_pass
    #     justification: "Trivial typo fix — tests_required was false in task intake"
```

---

## Integration with Orchestration Router

```mermaid
graph TD
    A[Agent completes task] --> B{file_exists?}
    B -->|fail| R[REJECT: no deliverable]
    B -->|pass| C{syntax_valid?}
    C -->|fail| R2[REJECT: malformed output]
    C -->|pass| D{tests_pass?}
    D -->|fail| R3[REJECT: broken code]
    D -->|pass/waived| E{secrets_clean?}
    E -->|fail| R4[REJECT + ALERT: secrets leak]
    E -->|pass| F{matches_spec?}
    F -->|fail| R5[REJECT: spec not met]
    F -->|pass| G{edge_cases_covered?}
    G -->|fail| W[WARN: accept with notes]
    G -->|pass/waived| ACP[ACCEPT: task complete]
```

- **Reject** returns the task to the agent with failure details for retry.
- **Reject + Alert** (secrets) also pings the escalation channel immediately.
- **Warn** accepts the output but flags gaps for the human reviewer.

---

## Usage with Specific Agents

| Agent | Typical Checks | Notes |
|-------|---------------|-------|
| **Jules** | All 6 | `tests_pass` is the gate; `secrets_clean` is critical for PRs |
| **AGY** | 1, 2, 4, 5, 6 | No `tests_pass` unless the output is code |
| **Hermes** | 1, 2, 4, 5 | Orchestration outputs are coordination artifacts |
| **Codex** | 2, 4, 5 | Review comments — syntax validity of inline suggestions |

---

## Quick Copy-Paste: Full Verification Script Skeleton

```bash
#!/usr/bin/env bash
# verification.sh — Run against any agent deliverable.
# Usage: ./verification.sh <deliverable_path> <task_type>

DELIVERABLE="$1"
TASK_TYPE="${2:-code}"  # code | research | deploy

PASS=0
FAIL=0

# 1. file_exists
if [ -f "$DELIVERABLE" ] && [ -s "$DELIVERABLE" ]; then
  echo "[PASS] file_exists: $DELIVERABLE"
  ((PASS++))
else
  echo "[FAIL] file_exists: $DELIVERABLE missing or empty"
  ((FAIL++))
fi

# 2. syntax_valid
case "${DELIVERABLE##*.}" in
  json) jq . "$DELIVERABLE" > /dev/null 2>&1 && echo "[PASS] syntax_valid" || { echo "[FAIL] syntax_valid: invalid JSON"; ((FAIL++)); };;
  yaml|yml) yq eval . "$DELIVERABLE" > /dev/null 2>&1 && echo "[PASS] syntax_valid" || { echo "[FAIL] syntax_valid: invalid YAML"; ((FAIL++)); };;
  md|txt) file "$DELIVERABLE" | grep -q "ASCII text\|UTF-8" && echo "[PASS] syntax_valid" || { echo "[FAIL] syntax_valid: non-text file"; ((FAIL++)); };;
  *) echo "[SKIP] syntax_valid: unknown extension .${DELIVERABLE##*.}";;
esac

# 3. tests_pass (code tasks only)
if [ "$TASK_TYPE" = "code" ]; then
  npm test > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "[PASS] tests_pass"
    ((PASS++))
  else
    echo "[FAIL] tests_pass: test suite failed"
    ((FAIL++))
  fi
else
  echo "[SKIP] tests_pass: not a code task"
fi

# 4. secrets_clean
if grep -qE 'sk-[a-zA-Z0-9]{20,}|-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----|eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}' "$DELIVERABLE"; then
  echo "[FAIL] secrets_clean: potential secret detected — REJECT IMMEDIATELY"
  ((FAIL++))
else
  echo "[PASS] secrets_clean"
  ((PASS++))
fi

# 5 & 6. matches_spec + edge_cases_covered require human review
echo "[MANUAL] matches_spec: review against success_criteria"
echo "[MANUAL] edge_cases_covered: check error handling, null cases, rollback plan"

echo "---"
echo "Automated checks: $PASS passed, $FAIL failed"
if [ $FAIL -gt 0 ]; then
  echo "RESULT: FAIL — do not accept"
  exit 1
else
  echo "RESULT: PASS (pending manual checks 5 & 6)"
  exit 0
fi
```
