# Financial model router

Choose the model whose causal unit matches how value is created and paid for. Do not force every case into a generic market-share model.

| Case | Revenue/value equation | Critical constraints |
|---|---|---|
| Launch/event | eligible × reach × response × qualify × purchase × AOV × frequency | venue, inventory, activity throughput, staff |
| Subscription/SaaS | leads × trial × paid × recurring revenue × retained periods | onboarding, cohort retention, CAC, GRR/NRR, support, cash |
| Marketplace | active buyers × orders/buyer × AOV × take rate | liquidity, supply, repeat, refunds |
| Retail | footfall × conversion × units/order × price | stock, store capacity, returns, margin |
| Telco/bundle | eligible base × adoption × ARPU uplift × active months | eligibility, churn, subsidy, network/service capacity |
| Internal transformation | users × adoption × hours saved × loaded hourly cost | realization rate, implementation cost, change capacity |
| Social impact | eligible × reach × participation × completion × outcome rate | measurement validity, equity, delivery capacity |
| Partnership/new product | partner reach × activation × conversion × value/order × retained share | contract, attribution, partner incentive, dependency |

## Router questions

1. Who pays, or whose measurable value changes?
2. What is the atomic transaction, subscription period, saved hour, or outcome?
3. Which observed behavior creates the value?
4. Which capacity or policy caps it?
5. Which costs vary with the atomic unit?
6. What timing separates booking, revenue, cash, and realized benefit?

Use `forecast.py` for launch/event models. `model_router.py` supports a first-pass subscription, marketplace, retail, telco, internal transformation, and partnership model. Use `unit_economics.py` whenever acquisition, retention, repeat behavior, recurring revenue, or cash affects the decision. Build social-impact outcomes directly from the table because monetization is often inappropriate. Then add case-specific adjustments such as tax, refunds, churn cohorts, working capital, subsidy, cannibalization, or opportunity cost.

## Required visual handoff

- Core slide: outcome metric plus 3–5 causal drivers.
- Economics slide: revenue/value bridge, contribution, and break-even.
- Risk slide or appendix: Low/Base/High plus top sensitivity switch point.
- Every displayed value references `MET` and `ASM` IDs.
