# Financial validation gates

## Driver validation card

| Field | Requirement |
|---|---|
| Assumption ID | stable shared ID |
| Driver | exact definition, unit, denominator, period |
| Current range | Low/Base/High |
| Evidence stage | A, B, or C |
| Sensitivity | outcome change under a specified stress |
| Test | cheapest credible behavioral or operational test |
| Pass | result supporting current base/upside use |
| Iterate | result requiring a revised range or mechanism |
| Stop | result making the recommendation non-viable under constraints |
| Owner/deadline | accountable person and decision time |

Set thresholds before observing the result. Avoid moving a stop threshold after failure.

## Unit-economics gate

Do not pass a CAC/LTV claim unless:

- customer/account/order unit, cohort, currency, and period match;
- acquisition spend scope and attribution window are explicit;
- paid, attributable, and fully loaded CAC are not silently mixed;
- LTV uses contribution rather than revenue, unless prominently labeled otherwise;
- retention curve, horizon, gross-margin treatment, and discounting are explicit;
- payback uses the same CAC basis as LTV:CAC;
- MRR/ARR excludes non-recurring items and reconciles starting to ending MRR;
- GRR/NRR definitions state treatment of expansion, contraction, and churn;
- case-specific pass/iterate/stop thresholds and evidence IDs exist;
- cash runway is not inferred from accounting profit.

Fail the gate when the selected LTV:CAC or payback misses its precommitted threshold, or when payback lies beyond the observed/modeled horizon without an explicit risk response. A benchmark from another company never substitutes for the team's threshold logic.

## CFO operating-plan gate

Do not claim a plan is fundable or operationally manageable unless:

- recognized revenue and cash collections are explicitly separated by collection terms;
- each active-customer cohort is covered by a retention curve for the modeled horizon;
- revenue, contribution, operating result, net cash flow, ending cash, and accounts receivable reconcile each period;
- the lowest cash balance has a funding/spend-cap response;
- variable cost includes the binding service, inventory, staffing, or infrastructure cost where material;
- every planned spend item and actual variance is linked to `ASM`, `SRC`, or `MET` IDs;
- budget-release and downside triggers are set before performance is observed.

Fail the gate if cash timing is omitted, if a cash trough breaches the approved floor, or if annualized revenue is used to hide an unaffordable monthly plan.

## Typical validation methods

- Price: paid pilot, pre-order, refundable deposit, current spend evidence, price-choice experiment.
- Conversion: landing-page or event funnel with unique denominators and qualified traffic.
- Frequency/retention: repeat behavior over a relevant cycle, not stated intent.
- Cost: supplier quote, rate card, timed operational trial, measured API/resource usage.
- Capacity: throughput test including setup, queue, error, and recovery time.
- Channel reach: audience access proof and unique reachable count, not platform impressions.

## Roots and adaptation

The evidence-stage distinction and explicit kill-criteria emphasis were informed by the public validation and finance workflow in [startup-design](https://github.com/ferdinandobons/startup-skill/tree/main/startup-design). CaseKit expands it to three stages and connects thresholds to sensitivity and competition decisions.
