# HDE staging report generation auth recovery

## Problem

A tester can ask for a PDF report after providing birth details, but if the prior full birth-detail sentence went through the LLM path instead of the deterministic profile/chart path, the next short message (`yes pdf report`) did not operate the chart system. The guide could then report a generic authorization failure even when the report service key was actually valid.

## Fix shape

- Treat `pdf report` / `yes pdf report` as a deterministic report-generation request before LLM fallback.
- If a stored profile has birth details, rebuild/generate from those details and return chart media metadata for the router to upload.
- If no profile is stored, scan recent user turns for a complete birth-detail sentence and persist/generate from that instead of asking the user to repeat themselves.
- If a user pastes a complete one-shot birth-detail sentence (`name + date + time + place`) after the guide invited chart generation, generate the chart immediately before LLM fallback. Do not let the LLM summarize a chart without leaving PDF/image artifacts.
- Accept natural one-shot phrasing such as `for Alicia Gulden ... birth place Provo, UT`; explicit names and `birth place` should not be rejected as loose profile phrases.
- Accept terse family-test shorthand such as `August 2 1952 6:46pm Glendale California`; once date and clock are parsed, trailing city/state text should become the birth place and still generate artifacts.
- Chart mechanics must come from the Human Design calculation engine/API. Do not use per-person profile/profile-line overrides to force expected results; fix location/time/timezone parsing and calculation plumbing instead.
- Keep the reports API key in environment only; do not print or embed it.

## Coach dashboard route note

`/coach/dashboard` should render the portal shell at staging even when Cloudflare Access is not matching the path. Client data APIs remain protected by backend auth: Cloudflare Access email headers or the legacy coach token. This avoids a plain Nginx `403` hiding the page while still keeping customer data gated.

## Durable template checkpoint

The report-follow-up runtime is now snapshotted in the staging repo under `scripts/guest_hermes_template/`. The orchestrator defaults to that repo-local template when provisioning new guest containers, falling back to `/home/ubuntu/guest_hermes_bot` only if the repo template is absent. This keeps future staging provisions from depending on an untracked host directory.

## Verification checklist

1. Compile `scripts/guest_hermes_template/guest_agent_server.py` and the live `/home/ubuntu/guest_hermes_bot/guest_agent_server.py`.
2. Probe reports server from `guest-hermes-2` with the container env key; expect `/api/compute` status `200`.
3. Exercise `/api/message` with a full birth-detail message followed by `Yes pdf report`; expect a PDF path in the response metadata.
4. Verify `https://staging.humandesignengine.com/coach/dashboard` returns HTML shell `200`.
5. Verify `/api/coach/session` still returns `401` without auth and `200` for simulated allowed Cloudflare Access email.
