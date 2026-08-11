---
name: casekit-finance
description: Build and defend revenue-first, driver-based financial forecasts and unit economics for case competitions, hackathons, launches, campaigns, products, and strategic proposals. Use when selecting metrics; forecasting revenue, reach, conversion, activity, and cost; estimating CAC, cohort LTV, LTV:CAC, CAC payback, MRR, ARR, GRR, NRR, churn, retention, burn, runway, contribution, break-even, ROI, scenarios, sensitivity, budgets, market capture, or answering judge questions about where numbers came from.
---

# CaseKit Finance

Build a causal model that explains what must happen, how much it produces, what it costs, and which assumptions could break the recommendation.

Declare the evidence stage before modeling:

- `Stage A — Assumption-led`: no direct behavioral or transaction evidence anchors major drivers; projections are hypotheses.
- `Stage B — Evidence-anchored`: interviews with concrete current spend, pre-orders, transactions, usage, or experiments anchor at least one material driver.
- `Stage C — Actual-led`: operating data anchors most material drivers; forecast from cohorts or observed funnel behavior.

Do not upgrade a stage based on stated interest alone. State which drivers remain unvalidated at every stage.

## Two-step mandate

### Step 1 — Select the numbers that matter

Start from the stated goal. Translate it into a metric tree:

```text
Business goal
└── Outcome metric
    ├── Revenue driver
    │   ├── Funnel driver
    │   └── Capacity driver
    └── Guardrail metric
```

For each metric define name, business meaning, formula, unit, period, denominator, owner, data source, and decision it informs. Keep only metrics that can change a decision or diagnose performance.

Separate:

- `Target`: result the team wants.
- `Forecast`: result implied by assumptions.
- `Actual`: measured result.
- `Benchmark`: external observation.

Never make the forecast equal the target by construction. If the forecast misses the target, calculate the driver improvement required.

### Step 2 — Forecast those numbers

Estimate revenue before cost:

```text
Eligible audience
× reachable share
× effective reach rate
× response/visit rate
× qualified rate
× purchase conversion
× average order value
× purchase frequency
= gross revenue
```

Change the funnel to fit the business model, but define every transition and denominator. Then estimate variable, semi-variable, fixed, one-time, and opportunity costs.

Select the model before calculating. Read `references/model-router.md`, then use `scripts/model_router.py` for supported patterns. For acquisition, retention, recurring revenue, or cash questions, read `references/unit-economics.md` and run `scripts/unit_economics.py`. Read `references/methodology.md` for formulas, `references/five-why-defense.md` for judge defense, and `references/validation-gates.md` for thresholds and kill criteria. Use `assets/finance-output.md` for delivery. For a launch event, read `references/launch-event-example.md`.

## Assumption protocol

For each uncertain input:

1. Assign an Assumption ID.
2. Give Low/Base/High values.
3. State basis: primary research, secondary research, analogy, derivation, target, or judgment.
4. Link Source IDs when evidence exists.
5. Explain transferability from benchmark to context.
6. Assign confidence and sensitivity separately.
7. State a validation method, owner, timing, and update trigger.

Use a range wider than the source uncertainty when the context transfer is weak. Use round numbers consistent with uncertainty; do not show false precision.

## Required model checks

- Reconcile units and time periods.
- Prevent overlapping funnel stages or double-counted customers.
- Separate unique people, impressions, visits, leads, orders, and units.
- Constrain sales by inventory, staffing, venue, service, and technical capacity.
- Separate gross billings, net revenue, gross profit, contribution, and cash flow.
- Include refunds, discounts, tax, platform fees, spoilage, or churn when material.
- Calculate break-even and required reach/conversion to hit the target.
- Run Low/Base/High scenarios and one-way sensitivity on the top 3–5 inputs.
- Show at least one judge-readable visual: driver tree, funnel, revenue bridge, cost waterfall, unit-economics card, break-even curve, scenario matrix, or sensitivity tornado.
- Include expected value only when scenario probabilities have a defensible basis.
- State what would change the recommendation.
- Define the acquisition/value unit and cohort before reporting CAC or LTV.
- Report applicable CAC bases separately; never mix customer CAC with account or order value.
- Prefer finite cohort contribution LTV over the `ARPU × margin ÷ churn` shortcut.
- Calculate LTV:CAC and payback with an explicitly selected CAC basis and case-specific thresholds.
- For recurring models, reconcile MRR movement, GRR, NRR, ARR run rate, churn, and ending MRR.
- For cash-constrained cases, show burn, runway, collection timing, and working-capital effects when material.

## Strategy and activity linkage

Every proposed activity must show:

```text
Activity → audience → behavioral mechanism → driver KPI → outcome KPI → revenue impact → cost → owner → measurement
```

For events, specify attendee capacity, invitation/reach volume, attendance conversion, activity throughput, giveaway quantity, redemption rule, staffing, unit cost, expected purchase conversion, and post-event follow-up. Reject vanity reach that has no defensible path to the outcome.

## 5 Why numeric defense

Apply 5 Why to the most sensitive numbers, not mechanically to every cell. Continue until reaching a source, observable mechanism, contractual constraint, arithmetic identity, or explicit assumption that can be tested. If a Why has no answer, mark it as an evidence gap; do not invent one.

## Output order

1. Goal, decision, audience, period, and currency.
2. Metric tree: outcome, driver, guardrail.
3. Revenue model and funnel before any cost table.
4. Required-performance calculation versus forecast.
5. Cost model and capacity constraints.
6. Unit economics: CAC bases, cohort contribution LTV, LTV:CAC, CAC payback, recurring-revenue retention, contribution, break-even, cash/runway, and ROI when applicable.
7. Low/Base/High scenarios.
8. Sensitivity and highest-value validation tests.
9. 5 Why defense for critical inputs.
10. Recommendation, risks, what changes the decision, and CaseKit handoff.

Include pass/iterate/stop thresholds for the highest-sensitivity assumptions. A failed stop threshold must trigger reframe, cost reduction, channel change, or recommendation withdrawal—not a rewritten optimistic narrative.

Run `scripts/forecast.py` for detailed launch/event funnels and `scripts/model_router.py` for the supported model families in `references/model-router.md`. Run `scripts/unit_economics.py` for cohort acquisition/value, recurring revenue, and cash metrics. Run `scripts/sensitivity.py` to rank first-order numeric drivers around a selected scenario. Do not let script output replace reasoning or source validation.
