# CFO operating controls

Use this reference when a case claims it can be funded, launched, or scaled. The aim is a decision-grade operating plan, not a fake three-statement model.

## Minimum monthly bridge

For every modeled period, reconcile:

```text
Active customers × price = recognized revenue
Recognized revenue shifted by collection terms = cash collections
Cash collections − variable cost − fixed cost − acquisition spend − one-time spend = net cash flow
Opening cash + net cash flow = ending cash
Recognized revenue − cumulative cash collections = accounts receivable
```

Model cohorts separately when retention matters. Do not use exit-period ARR as proof that the team can fund the months before it.

## Required CFO decision controls

| Control | Required decision use |
|---|---|
| Cash trough | Funding or spend cap before the next cash inflow |
| Contribution margin | Whether each extra customer improves cash generation |
| Collection terms and AR | Whether booked revenue is actually financeable |
| Capacity-linked cost | Whether staffing, inventory, service, or API cost breaks the forecast |
| Budget gate | Maximum approved spend and KPI needed to release the next tranche |
| Variance review | Planned versus actual revenue, cash, and spend; owner and reforecast trigger |
| Downside trigger | Observable condition that pauses, reduces, or redirects spend |
| Audit trail | Every material driver linked to `ASM`, `SRC`, or `MET` IDs |

## Suggested board/judge view

Show no more than one page containing: three operating milestones, cumulative spend, ending cash by scenario, the lowest-cash month, target contribution margin, and the KPI required before releasing the next budget tranche. A useful recommendation includes a stop condition, not merely a desired outcome.

## Variance discipline

Keep `plan`, `actual`, and `variance` separately. A variance should trigger a defined action:

| Variance | Example trigger | Action |
|---|---|---|
| Collections below plan | cash collection < 90% of plan | freeze discretionary acquisition spend and reforecast cash |
| Contribution below plan | gross margin below approved floor | re-price, reduce variable cost, or stop scaling |
| Acquisition above plan | CAC above approved threshold | shift channel or stop the tranche |
| Capacity misses | service level outside guardrail | limit demand until capacity is restored |

Thresholds are case-specific. They must be set before the data arrives and linked to an owner and review date.
