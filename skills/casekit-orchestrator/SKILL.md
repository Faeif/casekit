---
name: casekit-orchestrator
description: Coordinate an evidence-led case competition or hackathon from challenge brief to final submission. Use when starting, structuring, managing, integrating, or quality-controlling a case, innovation challenge, business proposal, hackathon, pitch deck, or judge Q&A across research, finance, product/technology, marketing/growth, and pitching.
---

# CaseKit Orchestrator

Own one coherent recommendation. Treat specialist outputs as inputs, never as independent essays.

Match the user's working language. Keep IDs, formulas, units, and source metadata standardized so multilingual teammates can reconcile artifacts.

## Start

1. Read the challenge brief, official rules, required deliverables, time limit, and judging rubric.
2. Choose operating mode: `Sprint`, `Standard`, or `Deep` based on time and stakes.
3. Create a project workspace with `casekit.py init <destination>` when the CLI is available; it installs portable skills and creates an Obsidian-ready workspace. Otherwise copy `assets/project-template/`.
4. Fill `00-brief.md` before specialist work begins.
5. Record every external fact in `01-evidence-ledger.csv`, every uncertain input in `02-assumptions.csv`, and every KPI in `03-metric-tree.csv`.
6. Assign stable IDs. Never silently replace an existing value; update its status and log the decision.
7. Assign work with `10-team-charter.md` and map the official judging criteria in `11-rubric-scorecard.csv` before parallel work starts.

Read `references/workflow.md` for gates and timing. Read `references/data-contract.md` before integrating specialist outputs. Read `references/integrations.md` before routing work to external skill suites.

## Specialist sequence

Use sibling skills in this order unless the brief requires a different dependency:

1. `casekit-discovery`: problem event, stakeholder, premises, opportunity frames, validation gate.
2. `casekit-research`: market, customer, competitors, benchmarks, regulations, disconfirming evidence.
3. `casekit-strategy`: option portfolio, weighted choice, rejected alternatives, and decision lock.
4. `casekit-finance`: metric tree, revenue drivers, funnel, costs, scenarios, economics.
5. `casekit-product-tech`: user flow, MVP, architecture, implementation, demo, risks.
6. `casekit-engineering`: implementation slices, contracts, quality gates, CI, release, operations.
7. `casekit-marketing-growth`: positioning, channels, launch, funnel ownership, experiments.
8. `casekit-operations`: operating model, RACI, capacity, roadmap, gates, contingencies.
9. `casekit-pitch`: thesis, storyline, slide variants, script, transitions, appendix.
10. `casekit-validator`: traceability, cross-artifact integrity, weighted rubric, source and submission gates.
11. `casekit-deck`: canonical deck spec, editable presentation, notes, appendix, visual QA.
12. `casekit-red-team`: adversarial attacks, Q&A, prioritized repairs, and final rehearsal.

Run research and problem framing before locking the solution. Iterate finance, product, and marketing together because their assumptions are coupled.

## Non-negotiable gates

Do not advance a section when its gate fails:

- **Problem gate:** named customer, observable pain, current alternative, evidence, consequence.
- **Strategy gate:** explicit goal, chosen segment, differentiated mechanism, rejected alternatives.
- **Finance gate:** revenue formula precedes cost; units reconcile; base/upside/downside exist; top drivers have evidence or transparent derivations; applicable CAC/LTV/payback, recurring-revenue, and cash metrics reconcile to one cohort and decision threshold.
- **Execution gate:** owner, action, timing, dependency, cost, KPI, and failure response are specified.
- **Pitch gate:** each slide has one claim, one job, evidence, and a spoken takeaway.
- **Submission gate:** numbers match across model/deck/script; citations resolve; demo fallback exists; Q&A answers are rehearsed.
- **Validation gate:** every critical premise has a pass/iterate/stop threshold; failed kill criteria cannot be hidden by narrative polish.
- **Deck gate:** `12-deck-spec.json` passes referential checks before rendering; rendered slides pass visual inspection at presentation size.

## Integration rules

- Keep one source of truth. Specialists may propose changes but must not fork core values.
- Distinguish `fact`, `benchmark`, `derived estimate`, `team assumption`, and `target`.
- Use ranges for uncertain inputs. Avoid precision beyond the evidence.
- Map every recommendation to the judging rubric and quantify the expected effect.
- Separate outcome KPIs from driver KPIs and guardrail metrics.
- Flag contradictions immediately and identify which artifact owns the correction.
- Include `what would change our mind` for major decisions.

## Final package

Produce:

1. One-sentence thesis and executive recommendation.
2. Evidence-backed problem and customer definition.
3. Strategy and explicit choice rationale.
4. Driver-based economics with scenarios and sensitivity.
5. Product/MVP and technical feasibility.
6. Go-to-market and execution roadmap.
7. Operating model, ownership, capacity, scale gates, and contingencies.
8. Pitch deck, deck spec, script, demo plan, source map, and appendix.
9. Judge scorecard, validation report, top risks, Q&A bank, and unresolved items.

Report confidence as `High`, `Medium`, or `Low` and explain the limiting uncertainty. Never claim that a framework guarantees winning; optimize for rubric fit, rigor, clarity, feasibility, memorability, and delivery.
