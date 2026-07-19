# GRO-3996 Workers build proof

GRO-3996 adds an analytics proof to the PWP verification pipeline and also keeps the pull-request deployment checks green.

The Cloudflare Pages check uses the existing Pages build output (`dist`). The branch also declares the same directory as Wrangler static assets so the repository-level Workers Builds trigger (`npx wrangler versions upload`) has an explicit upload target instead of failing with `Missing entry-point to Worker script or to assets directory`.

Verification commands for this change:

```bash
npm run pwp:verify
npx wrangler versions upload --dry-run
```

Expected evidence:

- PWP proof writes analytics evidence to `okf/output/pwp-visual-qa/analytics.json`.
- Wrangler dry-run accepts the static assets configuration for `./dist`.
