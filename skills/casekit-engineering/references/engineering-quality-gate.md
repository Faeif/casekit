# Engineering quality gate

## Plan before code

Define the vertical slice, owner, acceptance test, data classification, integration status, and user-visible proof. Record build-vs-buy and architecture trade-offs in the decision log.

## Contract and code quality

| Area | Required outcome |
|---|---|
| Boundaries | modules own one responsibility; external systems are adapters |
| API/events | typed or documented request, response, error, idempotency, and version behavior |
| Data | ownership, validation, authorization, retention, migration and rollback plan |
| Configuration | environment-specific config, no secrets in source, explicit feature flags |
| Review | small changes, readable names, error paths, no dead prototype path presented as live |

## Test gate

Run the smallest relevant set: unit tests for business rules, integration tests for adapters/contracts, end-to-end tests for the decisive journey, and regression tests for known case-critical failures. Include one unhappy path, one permission/privacy path, and one dependency failure when material.

## CI and release gate

Automate format/lint, type/build, tests, dependency/security checks appropriate to the stack, and artifact generation. Before a pilot or production release, define environment separation, database migration, feature flag or staged rollout, monitoring, rollback, and accountable owner.

## Operational gate

Define SLO/SLI targets only when they are measurable. Monitor user outcome, error rate, latency, dependency health, and unit cost. Create a short runbook for the highest-impact incident and a manual fallback for the decisive user action.

## Competition translation

Show judges the one proof that matters: a working vertical slice, the real/mock boundary, an edge-case response, and the 2–3 controls that make scale credible. Keep full engineering artifacts in the appendix or repository.
