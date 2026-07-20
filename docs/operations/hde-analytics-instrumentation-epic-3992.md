# HDE Analytics + Conversion Instrumentation Epic — GRO-3992

Status snapshot for the site-wide analytics/conversion green-state epic.

Latest refresh: `2026-07-20T01:31:21Z` from Ned cron redispatch. Linear had drifted this parent back to Backlog with `dispatch:ready`; this document is refreshed so finalization can restore the parent to review without pretending the epic is green.

## Current state

This epic is not production-green yet. The implementation children have been split into independently reviewed branches/PRs so each surface can be verified and merged without losing evidence. Current Linear state is mixed/stale from redispatch: GRO-3993 through GRO-3996 are Backlog again, GRO-3997 is Done, and the PRs remain open with Pages checks green plus stale Workers build failures.

| Child | Scope | Branch / PR | Current evidence | Green gate |
|---|---|---|---|---|
| GRO-3993 | Canonical GA4/GTM loader across Astro + legacy static pages | `ned/GRO-3993` / PR #23 | Linear drifted to Backlog with `dispatch:ready`; PR remains open; Cloudflare Pages check passed; stale Workers build check failed | Restore review/merge/deploy loader, then crawl all sitemap pages |
| GRO-3994 | Checkout funnel events | `ned/GRO-3994` / PR #22 | Linear drifted to Backlog with `dispatch:ready`; PR remains open; Cloudflare Pages check passed; stale Workers build check failed | Restore review/merge/deploy checkout instrumentation; smoke events without a real charge |
| GRO-3995 | Free-reading + Sanctuary daily-work events | `ned/GRO-3995` / PR #21 | Linear drifted to Backlog with `dispatch:ready` + `agent:needs-human-review`; PR remains open; Cloudflare Pages check passed; stale Workers build check failed | Restore review/merge/deploy daily-work/free-reading/Sanctuary events |
| GRO-3996 | Analytics verification in PWP proof | `feature/gro-3996` / PR pending/branch evidence | Linear drifted to Backlog with `dispatch:ready` + `agent:needs-human-review`; branch evidence exists | Restore review, open/attach PR if needed, and require PWP proof to fail red sites/pass tagged sites |
| GRO-3997 | Live production analytics coverage verifier | `ned/GRO-3997` / PR #20 | Linear is Done, but PR #20 remains open; live verifier previously showed production red: 36 sitemap pages missing GA4, 3/3 funnel routes missing expected events, 0 duplicate GA/GTM snippets | Re-run live crawl after implementation deploys and require `ok=true` |

## Production evidence from the latest live crawl

The latest GRO-3997 crawl against `https://humandesignengine.com` returned red, correctly:

- Sitemap URLs crawled: `171`
- Pages missing GA4 `G-Q6TPL08VM7`: `36`
- Funnel routes missing expected events: `3/3`
  - `/buy-report/` missing `begin_checkout`
  - `/checkout/pay/` missing `add_payment_info`
  - `/success/` missing `purchase`
- Duplicate GA4 snippets: `0`
- Duplicate GTM snippets: `0`
- GTM containers detected: `0`
- `/affiliates.html` still has the same crawler fetch/redirect-loop class later covered by SEO cleanup.

## Non-green blockers

1. Child implementation PRs are open, not merged into production.
2. Linear child states drifted after finalization: GRO-3993 through GRO-3996 are Backlog again; the parent also returned to Backlog with `dispatch:ready`. This is workflow drift, not proof that the code disappeared.
3. Cloudflare Pages checks are passing on child PRs, but the stale `Workers Builds: hd-platform` trigger is still failing and should not be mistaken for the Pages deployment path.
4. Production has not yet been recrawled with all child implementation branches merged/deployed.
5. Google Admin/GTM/Search Console scope work remains separate under the Google-auth epic and must be completed before authenticated dashboard/API proof can be called green.

## Green definition for this epic

GRO-3992 can move to Done only after all of the following are true with fresh tool output:

1. GA4/GTM loader is deployed on every sitemap page or the page is intentionally excluded.
2. Checkout funnel events are visible in shipped HTML/JS for report selection, checkout click/session creation, Stripe redirect, and success/purchase.
3. Free-reading, daily-work, and Sanctuary invitation CTAs emit documented events.
4. PWP proof includes analytics assertions.
5. The live production analytics coverage verifier returns `ok=true` against `https://humandesignengine.com`.
6. Authenticated Google/GA/GTM/GSC proof is attached when required credentials/scopes are available.

## Operator note

Do not mark the epic green from intent. Merge/deploy the children, run the live verifier, then attach the command output. Servers do not care how close the plan looked in Linear.