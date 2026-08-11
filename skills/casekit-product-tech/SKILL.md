---
name: casekit-product-tech
description: Translate a competition strategy into a credible product, service, MVP, prototype, pilot, or production-ready technical plan. Use for hackathon builds, digital products, AI solutions, service design, feasibility analysis, feature prioritization, architecture diagrams, technical roadmaps, build-vs-buy choices, production-readiness reviews, security/privacy design, testing, reliability, observability, deployment, or demo planning.
---

# CaseKit Product & Tech

Design the smallest credible system that proves the strategic thesis within the competition constraints. Select the correct delivery level; a competition demo must not pretend to be a production service.

## Delivery level

Classify the requested output before architecture work:

| Level | Goal | Minimum proof |
|---|---|---|
| `Concept` | Explain the mechanism | journey, scope, dependencies, risks |
| `Prototype` | Demonstrate the decisive experience | working vertical slice, seeded data, fallback demo |
| `Pilot` | Learn with bounded real users | consent, measurement, support owner, stop criteria |
| `Production` | Serve real users reliably | security, operations, testing, observability, rollout and recovery |

Do not upgrade a level merely because it has an architecture diagram. State the chosen level visibly in the deck and plan.

## Workflow

1. Restate the target user, job, context, pain, desired outcome, and strategic mechanism.
2. Define the end-to-end user journey and the decisive moment where value is created.
3. Convert the thesis into testable product hypotheses.
4. Prioritize scope using `must prove`, `supports proof`, and `later`.
5. Specify architecture, data flow, integrations, security/privacy/safety, failure modes, and human fallback.
6. For `Pilot` or `Production`, define non-functional requirements, threat model, reliability controls, observability, testing, deployment, rollback, and operational ownership.
7. Estimate build effort, dependencies, operating constraints, capacity, and variable technical cost.
8. Design a demo that proves the core mechanism with a reliable backup.
9. Reconcile capacity and cost assumptions with Finance and acquisition/usage assumptions with Marketing.

Read `references/feasibility-gates.md`. For every external system, fill `integration-contract.csv`; label it `real`, `sandbox`, `mocked`, `planned`, or `blocked`. For `Pilot` or `Production`, read `references/production-readiness.md`. Read `references/gstack-handoff.md` when a team has gstack installed or needs a coded prototype reviewed. Use `assets/product-tech-output.md`.

## MVP rules

- Include a feature only if it proves desirability, feasibility, viability, differentiation, or a mandatory rubric item.
- Distinguish working functionality, mocked functionality, conceptual roadmap, and external dependency.
- Never claim access to a partner API, CRM, billing system, identity provider, health record, or internal data set without a named owner and approved status in the integration contract.
- Never imply production readiness from a prototype.
- For AI, state model/provider, inputs, outputs, evaluation, latency, unit cost, data handling, failure behavior, and human escalation.
- For AI in `Pilot` or `Production`, version prompts/models, test representative and adversarial cases, monitor quality drift, minimize retained data, and provide a deterministic fallback for high-risk paths.
- For regulated or safety-sensitive cases, constrain claims and identify validation and approval paths.
- Prefer a thin vertical slice through the full user journey over disconnected features.

## Output

Provide problem-to-feature traceability, delivery level, user flow, MVP scope, architecture decision records, data contract, non-functional requirements, build plan, resource estimate, cost handoff, risks/controls, test plan, release/rollback plan where applicable, demo script, fallback demo, roadmap, and CaseKit handoff.
