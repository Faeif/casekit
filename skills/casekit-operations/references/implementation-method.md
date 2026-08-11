# Implementation method

## Initiative record

Each initiative must contain:

`initiative_id, outcome, deliverable, accountable_owner, contributors, dependencies, start, finish, effort, one_time_cost, recurring_cost, KPI, guardrail, premise_ids, experiment_ids, risk_ids, scale_gate, stop_gate`

## Sequence

1. Validate the problem and highest-sensitivity driver.
2. Build the smallest service/product slice that can test the causal mechanism.
3. Instrument before launch.
4. Pilot within a bounded cohort and capacity.
5. Compare actual against pass/iterate/stop thresholds.
6. Fix bottlenecks or stop; scale only after the gate passes.

## Capacity model

For each bottleneck calculate demand per period, processing time, available productive time, utilization limit, throughput per resource, required resources, queue or service-level risk, and contingency capacity. Feed the binding constraint back to Finance.

## Governance

- Daily during sprint: blockers, evidence changes, decision changes.
- Weekly during pilot: funnel, capacity, quality, guardrails, cash, risks.
- Gate review: continue, iterate, scale, pause, or stop with named evidence.
- Post-mortem: premise updates and reusable learning.

Avoid RACI ambiguity: one role is accountable for each outcome. If everyone owns it, nobody owns the decision.
