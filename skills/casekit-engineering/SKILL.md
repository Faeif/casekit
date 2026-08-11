---
name: casekit-engineering
description: Turn an approved CaseKit product scope into a high-quality implementation and release plan. Use when a team will write, review, test, demo, deploy, or operate code for a hackathon, pilot, startup, or production service and needs repository structure, API/data contracts, quality gates, CI, security, observability, release, rollback, or engineering handoff.
---

# CaseKit Engineering

Own delivery quality after Product & Tech locks the vertical slice. Build only what proves the strategy; leave a clear path from prototype to pilot or production.

## Start

1. Read `00-brief.md`, the chosen decision, product/tech output, metric tree, risks, integration contract, and delivery level.
2. Set `engineering/00-engineering-profile.json`, then complete the architecture blueprint files in `engineering/`. Separate `now`, `before pilot`, and `before production`.
3. Define the smallest end-to-end slice, its acceptance tests, and what is deliberately simulated.
4. Choose the simplest stack that satisfies the scope, existing team skills, integration constraints, and non-functional requirements. Record a Decision ID and trade-offs.
5. Create contracts before implementation: API/request-response, data ownership, authorization, events/webhooks, error behavior, and migration/compatibility plan.
6. Implement in thin slices. Keep business rules testable and isolate external providers behind adapters.
7. Run the quality gate before demo, merge, or release. Fix blockers; do not hide them behind UI polish.

Read `references/engineering-quality-gate.md`. Read `references/architecture-blueprint.md` before an architecture review. Use `assets/engineering-delivery-plan.md` and the generated `engineering/` templates.

## Non-negotiable rules

- Do not put credentials, personal data, or production exports in the repository, prompt, fixtures, logs, screenshots, or deck.
- Treat every external integration as `real`, `sandbox`, `mocked`, `planned`, or `blocked` according to `integration-contract.csv`.
- Make validation, authorization, and audit-relevant state changes explicit; never rely on the client UI to enforce a critical rule.
- Test the business rule and failure mode that matter to the case, not merely the happy-path screen.
- Add a deterministic demo mode, seeded data, and a fallback recording before the final rehearsal.
- Production claims require measurable SLOs, monitored dependencies, migration/rollback behavior, support ownership, and a security/privacy review proportionate to risk.
- Set `delivery_level` to `production` only after every required row in `engineering/production-readiness.csv` is `passed`; CaseKit validates this gate.

## Handoff

Report:

- Delivery level and vertical slice:
- Architecture, data, security, and deployment artifacts completed:
- Architecture decisions and trade-offs:
- Real versus mocked components:
- Contracts and data boundaries:
- Tests run and remaining risk:
- Release/demo status and fallback:
- Cost/capacity changes for Finance:
- Operations and security actions before pilot/production:
