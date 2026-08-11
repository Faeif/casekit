# Shared data contract

## ID prefixes

| Object | Prefix | Example |
|---|---|---|
| Claim | CLM | CLM-001 |
| Source | SRC | SRC-001 |
| Assumption | ASM | ASM-001 |
| Metric | MET | MET-001 |
| Decision | DEC | DEC-001 |
| Risk | RSK | RSK-001 |
| Experiment | EXP | EXP-001 |
| Premise | PRM | PRM-001 |

## Evidence ledger

Required fields: `claim_id,claim,source_id,source_type,publisher,title,url,published_date,accessed_date,page_or_section,verbatim_support,interpretation,quality,recency,relevance,status,owner`.

`status` must be one of `verified`, `partially-verified`, `unverified`, `superseded`. Do not use a URL alone as evidence; capture the exact table, page, or supporting passage.

## Assumption ledger

Required fields: `assumption_id,variable,definition,unit,low,base,high,basis,source_ids,confidence,sensitivity,validation_method,owner,status`.

`basis` must be one of `primary-research`, `secondary-research`, `analogy`, `derived`, `management-target`, `team-judgment`.

## Metric tree

Required fields: `metric_id,parent_metric_id,metric,metric_type,formula,unit,time_horizon,low,base,high,source_or_assumption_ids,owner`.

`metric_type` must be one of `north-star`, `outcome`, `driver`, `guardrail`, `diagnostic`, `capacity`.

## Deck contract

`12-deck-spec.json` is the canonical presentation representation. Every slide needs `type` and `headline`; `evidence_ids` must resolve to existing CaseKit IDs. Displayed model values use `metric_bindings` with `metric_id`, `scenario`, and raw numeric `value`; funnel stages may carry the same fields directly. The validator compares the raw value to the corresponding ledger scenario before rendering.

## Rubric contract

`11-rubric-scorecard.csv` requires `criterion,weight,score,max_score,evidence,gap,owner,status`. Use official weights when provided. Do not manufacture precision when judging criteria are qualitative; explain scoring uncertainty.

## Unit-economics contract

When acquisition, retention, repeat value, recurring revenue, or cash affects the recommendation, generate `14-unit-economics.json` with `casekit-finance/scripts/unit_economics.py`. Its global `source_or_assumption_ids` must resolve to the shared ledgers. Add displayed CAC, LTV, payback, MRR/ARR, GRR/NRR, burn, and runway values to `03-metric-tree.csv` with stable `MET` IDs before binding them into the deck.

## Premise and experiment contract

Premises require `premise_id,premise,type,evidence_ids,confidence,decision_impact,falsification_test,owner,status`. Experiments require `experiment_id,premise_ids,method,leading_metric,guardrail,pass_threshold,iterate_band,stop_threshold,owner,deadline,status`.

## Handoff block

Every specialist output ends with:

```markdown
## Handoff
- Decisions made:
- Claims added or changed:
- Assumptions added or changed:
- Metrics added or changed:
- Dependencies on other workstreams:
- Contradictions found:
- Highest-sensitivity unknown:
- Next validation action:
```
