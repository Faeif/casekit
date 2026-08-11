# Unit economics and recurring revenue

## Metric contract

Define the unit before calculating: paying customer, account, subscriber, buyer, seller, order, location, or device. Keep acquisition and value on the same unit, cohort, currency, and period.

### CAC bases

```text
Channel CAC = channel-attributable spend ÷ new customers attributed to that channel
Paid CAC = paid-channel spend ÷ new customers attributed to paid channels
Attributable CAC = directly attributable acquisition spend ÷ all new customers
Fully loaded CAC = acquisition-related media + sales/marketing labor + tools + agency + incentives ÷ all new customers
```

Report at least two applicable bases instead of presenting one ambiguous `CAC`. State attribution window, treatment of organic customers, salaries, discounts, referrals, brand spend, sales commissions, and reactivated customers.

### Preferred LTV

Use a finite observed or explicitly assumed cohort:

```text
Contribution per active unit[t]
  = revenue per active unit[t] × gross margin rate[t]
  − incremental service cost excluded from gross margin[t]

Contribution LTV
  = Σ retention-to-original-cohort[t]
      × contribution per active unit[t]
      ÷ (1 + discount rate per period)^(t−1)
```

Do not subtract a service cost twice. Set the incremental service cost to zero when gross margin already includes it.

The shortcut `ARPU × gross margin ÷ churn` is allowed only as a labeled steady-state heuristic when churn is constant, cohorts are homogeneous, contribution remains constant, expansion is absent, and the infinite-horizon assumption is acceptable. Do not use it as the default competition model.

### Decision metrics

```text
LTV:CAC = contribution LTV ÷ selected CAC basis
CAC payback = first period where cumulative contribution per acquired unit ≥ selected CAC
```

Set case-specific pass/iterate/stop thresholds before observing results. Do not insert a universal “good” LTV:CAC or payback threshold; capital cost, cash constraints, risk, retention maturity, and growth strategy differ.

## Recurring revenue

```text
Ending MRR = Starting MRR + New MRR + Expansion MRR − Contraction MRR − Churned MRR
GRR = (Starting MRR − Contraction MRR − Churned MRR) ÷ Starting MRR
NRR = (Starting MRR + Expansion MRR − Contraction MRR − Churned MRR) ÷ Starting MRR
ARR run rate = Ending MRR × periods per year
```

Define recurring revenue policy: exclude one-time setup, usage spikes not contractually recurring, taxes, pass-through fees, and bookings that are not recognized recurring revenue. Label ARR/MRR as management metrics when applicable and reconcile them to financial statements or transaction data.

## Cash

```text
Net burn per period = max(cash outflow − cash inflow, 0)
Runway = cash balance ÷ net burn per period
```

Separate accounting profit, contribution, bookings, recognized revenue, invoicing, collections, and cash. Add working-capital timing when inventory, receivables, payables, deposits, or annual prepayment are material.

## Business-model adaptations

- SaaS/subscription: logo retention, MRR/ARR, GRR/NRR, onboarding cost, support, expansion, payback.
- Marketplace: buyer CAC and seller CAC separately; contribution per order after incentives, payment, refunds, trust/safety, and support.
- Retail/D2C: new-customer CAC, repeat cohort, contribution per order, return rate, fulfillment, inventory and working capital.
- Telco: subscriber acquisition/subsidy, ARPU uplift, service/network cost, churn, contract length, bad debt.
- Event/campaign: incremental acquired customers and post-event repeat value; do not call event spend CAC without attribution.
- Internal transformation: adoption cost per active user, realized value per user, implementation payback; customer LTV may be inapplicable.

## Evidence maturity

- Stage A: ranges from explicit assumptions; call the result `modeled LTV`, never observed LTV.
- Stage B: at least one material acquisition or retention input comes from a behavioral test, paid pilot, or concrete current spend.
- Stage C: use actual channel and cohort data; report cohort count, observation horizon, censoring, and segment differences.

Run `scripts/unit_economics.py` with `assets/unit-economics-input.example.json`. Its threshold values are synthetic examples, not benchmarks.

Write the result into a CaseKit project when applicable:

```bash
python3 scripts/unit_economics.py input.json --output 14-unit-economics.json
```

Then create `MET` rows for values shown in the pitch; do not bind deck labels directly to an untracked JSON value.

## Accounting boundary

CaseKit metrics are managerial decision models, not financial reporting policy. Acquisition costs can receive different accounting treatment depending on facts and applicable standards. For contract acquisition cost requirements, consult the current authoritative standard and finance owner; see [IFRS 15](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/).
