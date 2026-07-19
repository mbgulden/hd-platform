# GRO-3996 deployment-check follow-up

GRO-3996's analytics proof is implemented in the PWP verification pipeline. The canonical HD Engine Pages deployment requires the Pages-compatible Wrangler setting:

```json
{
  "pages_build_output_dir": "dist"
}
```

Do **not** add `assets.directory` to the root `wrangler.jsonc` for this Pages project. Cloudflare Pages rejects that field during preview deployment validation with:

```text
Configuration file for Pages projects does not support "assets"
```

Local verification for the analytics proof remains:

```bash
npm run pwp:verify
```

The repository-level `Workers Builds: hd-platform` GitHub check is a separate Cloudflare Workers Builds trigger configured to run `npx wrangler versions upload`. That trigger expects a Workers-style `main` or `assets.directory`, which conflicts with Pages config validation for this repo. Leave the issue In Review until the external Workers Builds trigger is disabled or pointed at a separate Worker config by the Cloudflare project owner.
