# Jules CLI Prompt Template (GRO-80)

Use this template when delegating code implementation tasks to Jules. Jules operates
on a specific repo and branch, creates/modifies files, runs tests, and opens PRs.

---

## Template

```yaml
# ── Jules Prompt ────────────────────────────────────────────
# Copy this block, fill in the blanks, and pass to Jules.

repo: ""
  # [REQUIRED] GitHub repo (owner/name format).
  # Example: "nous-research/active-oahu-tours"

branch: ""
  # [REQUIRED] Branch to work on.
  # Jules will create this branch if it doesn't exist.
  # Use naming convention: <type>/<short-description>
  # Example: "fix/contact-form-500-error"
  # Example: "feat/add-newsletter-signup"

description: >
  # [REQUIRED] What change to make, in plain English.
  # Jules uses this to plan the implementation.
  # Be specific about behavior, not implementation details.
  # BAD:  "Add a useEffect hook to the form component."
  # GOOD: "When the contact form submits successfully, show a green
  #        toast that says 'Message sent!' and clear the form fields.
  #        On error, show a red toast with the error message."

files_to_create:
  # [OPTIONAL] New files to scaffold.
  # Example:
  #   - "src/components/Toast.tsx"
  #   - "src/components/__tests__/Toast.test.tsx"

files_to_modify:
  # [OPTIONAL] Existing files to edit.
  # Example:
  #   - "src/pages/contact.astro"
  #   - "src/styles/toast.css"

tests_required: true
  # [REQUIRED] Whether Jules must write/update tests.
  # true  = block PR until tests pass
  # false = skip tests (use ONLY for trivial changes like typos)

pr_title: ""
  # [REQUIRED] PR title (becomes the GitHub PR title).
  # Example: "fix: contact form returns 500 on submit"

pr_body: ""
  # [OPTIONAL] Additional PR description beyond the auto-generated summary.
  # Jules auto-generates a summary; this is for extra context.

linear_issue: ""
  # [OPTIONAL] Linear issue key for auto-linking.
  # Example: "BUG-912"
  # Jules will add "Closes BUG-912" to the PR body.

base_branch: "main"
  # [OPTIONAL] Branch to target in the PR (default: main).
  # Example: "staging" or "release/v2.4"

dependencies:
  # [OPTIONAL] Packages to install before implementation.
  # Example:
  #   - "react-hot-toast@latest"
  #   - "@types/react-hot-toast@latest"
```

---

## Field Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `repo` | **Yes** | Target repository; Jules clones/fetches this |
| `branch` | **Yes** | Working branch; Jules creates it if needed |
| `description` | **Yes** | Behavioral description of the change |
| `files_to_create` | Optional | New files to scaffold; constrains scope |
| `files_to_modify` | Optional | Existing files to touch; constrains scope |
| `tests_required` | **Yes** | Boolean gate on test execution |
| `pr_title` | **Yes** | Becomes the GitHub PR title |
| `pr_body` | Optional | Extra context beyond auto-summary |
| `linear_issue` | Optional | Auto-links PR to Linear |
| `base_branch` | Optional | PR target; defaults to `main` |
| `dependencies` | Optional | NPM/pip/cargo packages to install first |

---

## Examples

### Bug Fix (simple, no new files)

```yaml
repo: "nous-research/active-oahu-tours"
branch: "fix/contact-form-500-error"
description: >
  The contact form at /contact returns a 500 error when submitted.
  The error originates in src/api/contact.ts line 47 — the email
  sender is receiving a null recipient address. Fix the null check
  and ensure a proper error message is returned for missing fields.
files_to_modify:
  - "src/api/contact.ts"
  - "src/api/__tests__/contact.test.ts"
tests_required: true
pr_title: "fix: contact form returns 500 on submit"
linear_issue: "BUG-912"
```

### Feature (new component + page)

```yaml
repo: "nous-research/active-oahu-tours"
branch: "feat/newsletter-email-signup"
description: >
  Add an email newsletter signup form to the homepage below the hero
  section. It should have a single email input and a "Subscribe" button.
  On success, show a green toast "You're subscribed!".
  On error, show a red toast with the error message.
  On duplicate email, show a yellow toast "You're already subscribed!".
  The form should POST to /api/newsletter/subscribe.
files_to_create:
  - "src/components/NewsletterSignup.astro"
  - "src/components/__tests__/NewsletterSignup.test.ts"
  - "src/pages/api/newsletter/subscribe.ts"
files_to_modify:
  - "src/pages/index.astro"
  - "src/styles/global.css"
dependencies:
  - "react-hot-toast@latest"
tests_required: true
pr_title: "feat: add newsletter email signup to homepage"
linear_issue: "GRW-104"
```

### Trivial Change (skip tests)

```yaml
repo: "nous-research/active-oahu-tours"
branch: "chore/fix-typo-footer"
description: >
  Fix a typo in the footer: "Contat Us" → "Contact Us".
files_to_modify:
  - "src/components/Footer.astro"
tests_required: false
pr_title: "chore: fix typo in footer"
```

---

## Jules Workflow (What Happens)

1. **Clone/Fetch** — Jules ensures `repo` is cloned at the latest `base_branch`.
2. **Branch** — Creates `branch` from `base_branch`.
3. **Install** — Runs package manager install + any `dependencies`.
4. **Plan** — Jules reads `description` and existing code, produces an implementation plan.
5. **Implement** — Creates `files_to_create`, modifies `files_to_modify`.
6. **Test** — If `tests_required: true`, runs the test suite and iterates until green.
7. **Commit & Push** — Commits with conventional commit message derived from `pr_title`.
8. **Open PR** — Creates PR against `base_branch` with auto-generated summary + `pr_body`.
   If `linear_issue` is set, adds "Closes <key>" to the description.
9. **Report** — Returns PR URL to the orchestrator.

---

## Integration with Orchestration Router

When the router delegates to Jules:
1. `task-intake.goal` → `jules.description`
2. `task-intake.files_to_modify` → `jules.files_to_modify`
3. `task-intake.context` → parsed for repo, issue key, branch naming hints
4. Branch name is auto-generated if not specified: `<type>/<slug-from-goal>`
5. PR title follows conventional commits: `type: short description`
6. After Jules completes, the router runs the
   [verification checklist](./verification-checklist.md) against the PR.
