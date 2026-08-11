# Architecture blueprint

Use the `engineering/` folder as a small but complete architecture packet.

| Artifact | Decision it forces |
|---|---|
| `architecture.md` | C4 context/container boundaries, request sequence, state ownership, degradation |
| `nfr-slo.md` | measurable reliability, latency, scale, recovery, privacy, and cost constraints |
| `threat-model.md` | assets, actors, trust boundaries, threat/control/residual risk |
| `data-lifecycle.md` | data purpose, classification, legal/consent basis, access, retention, deletion |
| `api-event-contracts.md` | request/event schema, authorization, validation, error/idempotency, versioning |
| `deployment-runbook.md` | environments, CI gates, secrets, migration, release, rollback, incident ownership |
| `test-matrix.csv` | critical rule and failure coverage across unit, integration, end-to-end, security/performance |
| `observability.md` | SLIs, logs/traces, dependency health, alerts, dashboards, cost monitoring |
| `production-readiness.csv` | deterministic go/no-go gate tied to evidence and risks |

Architecture quality is not more boxes. For each boundary, show who owns durable state, authorization, validation, retries, side effects, and recovery. Keep a modular monolith by default; split services only for a proven independent scaling, security, deployment, or ownership need.
