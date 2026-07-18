# HDE Analytics + Conversion Instrumentation Epic — GRO-3992

Status snapshot for the site-wide analytics/conversion green-state epic.

## Current state

This epic is not production-green yet. The implementation children have been split into independently reviewed branches/PRs so each surface can be verified and merged without losing evidence.

| Child | Scope | Branch / PR | Current evidence | Green gate |
|---|---|---|---|---|
| GRO-3993 | Canonical GA4/GTM loader across Astro + legacy static pages | `ned/GRO-3993` / PR #23 | `npm run build` passed; Cloudflare Pages check passed; stale Workers build check failed | Merge/deploy loader, then crawl all sitemap pages |
| GRO-3994 | Checkout funnel events | `ned/GRO-3994` / PR #22 | `npm run build` passed; Cloudflare Pages check passed; stale Workers build check failed | Production checkout pages expose `begin_checkout`, `add_payment_info`, and Stripe redirect/session events without real charge |
| GRO-3995 | Free-reading + Sanctuary daily-work events | `ned/GRO-3995` / PR #21 | `npm run build` passed; Cloudflare Pages check passed; stale Workers build check failed | Production daily-work/free-reading/Sanctuary CTAs emit documented events |
| GRO-3996 | Analytics verification in PWP proof | `feature/gro-3996` / PR pending/branch evidence | PWP verifier branch exists with analytics assertion work | PWP proof fails red sites and passes only tagged/evented sites |
| GRO-3997 | Live production analytics coverage verifier | `ned/GRO-3997` / PR #20 | Live verifier showed production red: 36 sitemap pages missing GA4, 3/3 funnel routes missing expected events, 0 duplicate GA/GTM snippets | Re-run live crawl after implementation deploys and require `ok=true` |

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
2. Cloudflare Pages checks are passing on child PRs, but the stale `Workers Builds: hd-platform` trigger is still failing and should not be mistaken for the Pages deployment path.
3. Production has not yet been recrawled with all child implementation branches merged/deployed.
4. Google Admin/GTM/Search Console scope work remains separate under the Google-auth epic and must be completed before authenticated dashboard/API proof can be called green.

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