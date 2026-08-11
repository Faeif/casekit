# Production readiness

Use this reference only for a Pilot or Production claim. A prototype does not need every control; explain what is deliberately deferred.

## Architecture decision record

For each consequential choice record: context, options, chosen option, trade-off, owner, revisit trigger, and Decision ID. Prefer managed services when they reduce operational risk without weakening the strategic proof.

## Minimum gates

| Area | Required decision or proof |
|---|---|
| Reliability | availability target, latency target, capacity assumption, timeout/retry/idempotency, dependency fallback |
| Security | threat model, authentication/authorization, secrets handling, encryption, audit trail, abuse/rate limit controls |
| Privacy/data | legal basis or consent, data minimization, classification, retention/deletion, access boundary, vendor/data residency review |
| AI quality | task-specific evaluation set, success threshold, false-positive/negative impact, human escalation, versioning, drift monitoring |
| Testing | unit, integration, end-to-end, critical regression, failure/edge case, acceptance criteria |
| Observability | product, service, cost, and safety metrics; logs/traces/alerts; accountable responder |
| Operations | runbook, support owner, incident severity/response, on-call or bounded support window, manual fallback |
| Delivery | environments, CI checks, migration/backward compatibility, staged rollout, kill switch, rollback owner |
| Economics | cost per active user/request, cloud/provider limit, staffing and support capacity, downside scenario |

## Architecture baseline

Use a thin vertical slice with explicit boundaries:

```text
Client → authenticated API → application/service → queue or workflow → data store
                         ↘ observability/audit     ↘ third-party adapters
```

Name the component responsible for validation, authorization, durable state, asynchronous work, and recovery. Do not add a queue, event bus, microservice, or ML pipeline without a failure mode or scale requirement that justifies it.

## Production readiness output

Create a table with requirement, target, measurement, owner, failure response, and evidence/assumption ID. A target without a measurement plan is a wish. A measured metric without an owner is not an operational control.

## Competition translation

On a slide, show only the 3–5 controls that neutralize the judges' largest feasibility objections. Put the complete matrix in an appendix. State whether the demo uses simulated integrations or production-capable paths.
