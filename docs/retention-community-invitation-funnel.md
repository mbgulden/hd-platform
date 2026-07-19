# GRO-4013 — Retention / Community Invitation Funnel

## Shipped surface

- Public route: `/community/`
- Primary promise: “Bring others to become with you.”
- Funnel job: convert Human Design Engine from a one-time report purchase into a repeat practice loop.

## Loop design

1. **Practice out loud** — the user completes one daily authority/body check and shares one observation.
2. **Invite one real relationship** — the product asks who would understand them better with a map too.
3. **Map the relationship field** — relationship charts become practical prompts for repair, space, timing, and energy hygiene.
4. **Return tomorrow together** — community prompts create a lightweight weekly retention ritual.

## Instrumentation plan

| Stage | Event | Success signal |
| --- | --- | --- |
| Practice | `practice_shared` | First shared practice within 24h |
| Invite | `relationship_invite_created` | One invite generated per active member |
| Chart | `relationship_chart_opened` | Relationship chart opened or requested |
| Return | `community_checkin_completed` | Weekly shared check-in completed |

## Implementation notes

- This pass ships the product surface and documented event contract without adding storage or credentials.
- Existing HD Platform primitives already include `Invitation` records and the `/api/public/relationship` relationship chart endpoint; the next backend pass should connect referral-code creation to those primitives rather than inventing a parallel system.
- No secrets, runtime artifacts, backups, `dist/`, or user data are committed.

## Verification

Fresh verification should include:

```bash
npm run build
```

Expected proof: Astro builds `/community/index.html` and the route-complete postbuild step exits successfully.
