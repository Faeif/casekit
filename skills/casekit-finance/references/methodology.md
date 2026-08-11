# Finance methodology

## Core formulas

### Revenue

```text
Orders = Eligible audience × Reach rate × Response rate × Qualification rate × Purchase rate
Gross revenue = Orders × Average order value × Purchase frequency
Net revenue = Gross revenue − discounts − refunds − taxes collected for authorities
```

When stages use different denominators, state them explicitly. Do not multiply rates that refer to incompatible populations.

### Economics

```text
Variable cost = Units sold × Variable cost per unit
Contribution = Net revenue − Variable cost − directly attributable channel cost
Contribution margin % = Contribution ÷ Net revenue
Operating result = Contribution − fixed and one-time operating costs
Break-even units = Fixed attributable cost ÷ Contribution per unit
Break-even revenue = Fixed attributable cost ÷ Contribution margin %
CAC = Explicit acquisition-spend basis ÷ New paying units on the same attribution basis
Finite cohort contribution LTV = Σ retained share × contribution per active unit ÷ discount factor
LTV:CAC = Contribution LTV ÷ Selected CAC basis
CAC payback = First period cumulative contribution per acquired unit covers Selected CAC
ROAS = Attributable gross revenue ÷ Media spend
ROI = (Incremental benefit − Incremental cost) ÷ Incremental cost
```

State whether metrics use gross revenue or contribution. Prefer incremental analysis: compare against what happens without the initiative.

Read `unit-economics.md` before using CAC, LTV, MRR/ARR, GRR/NRR, churn, payback, burn, or runway. Do not use a universal benchmark threshold.

### Required performance

Work backward from target revenue:

```text
Required orders = Target net revenue ÷ Net revenue per order
Required qualified leads = Required orders ÷ Purchase conversion
Required responses = Required qualified leads ÷ Qualification rate
Required reach = Required responses ÷ Response rate
Required eligible audience = Required reach ÷ Reach rate
```

If required eligible audience exceeds the available market or capacity, the strategy is infeasible without changing price, conversion, frequency, channel, or target.

## Scenario construction

Do not set every input optimistic in the upside and pessimistic in the downside without considering correlation. Build coherent stories:

- Low: weak reach/response or operational friction, lower conversion, normal cost.
- Base: most defensible input set.
- High: validated channel traction, stronger conversion, sufficient capacity; include added variable cost.

Avoid probability-weighted expected value unless probabilities have a credible basis. Otherwise report the range and decision robustness.

## Sensitivity

Change one input at a time around the base case and rank impact on contribution or target attainment. Prioritize validating inputs with both high sensitivity and low confidence.

## Cost taxonomy

- Variable: payment fee, materials, fulfillment, per-user API, giveaway redeemed.
- Semi-variable: staff shift, transport batch, infrastructure tier.
- Fixed attributable: venue, creative production, campaign setup.
- One-time investment: development, equipment, integration.
- Opportunity: staff or inventory diverted from alternatives.
- Sunk: already incurred and unchanged by the decision; exclude from forward choice.

## Market sizing

Use top-down TAM for context, bottom-up SAM for serviceability, and operational SOM for near-term capture. SOM must reconcile to channel reach, funnel conversion, capacity, and time—not an arbitrary market-share percentage.
