---
name: casekit-strategy
description: Generate, compare, and choose evidence-led strategic options for a case competition, startup pitch, innovation challenge, or hackathon. Use after the problem is framed and before solution lock when a team needs alternatives, an explicit choice rationale, rubric-fit scoring, probability-aware confidence, rejected options, or a decision that finance, product, marketing, and pitch can share.
---

# CaseKit Strategy

Own the strategic choice between discovery and specialist execution. Do not let the first plausible idea become the recommendation by default.

## Workflow

1. Read the brief, rubric, discovery output, evidence ledger, assumptions, and metric tree.
2. State the decision, non-negotiable constraints, target segment, and desired outcome.
3. Generate 3–5 meaningfully different option cards. Change the segment, mechanism, business model, channel, or operating model; do not create cosmetic variants.
4. For each option, specify customer, mechanism, causal chain, required evidence, key assumptions, economics direction, execution dependencies, downside, fastest falsification test, and stop condition.
5. Score options with `option-portfolio.csv`. Use official rubric weights when available. Score `rubric_fit`, `impact`, `feasibility`, `viability`, `differentiation`, and `evidence_confidence` from 1–5. Explain every score below 4 or above 4.
6. Recommend one option. Record the rejected alternatives and the condition under which each would become preferable in `04-decision-log.csv`.
7. Pass only the chosen option's stable IDs, guardrails, and unresolved assumptions to Finance, Product/Tech, Marketing/Growth, and Operations.

## Confidence and probability

- Never invent a probability of winning, adoption, or clinical outcome.
- Use `High`, `Medium`, or `Low` confidence with the evidence limitation.
- Use a numerical probability only when a traceable base rate, experiment, or calibrated model exists; record its Source or Assumption ID and uncertainty range.
- Keep targets, forecasts, facts, and assumptions visually distinct.

## Choice gate

Do not lock an option until it has a named customer, observable pain, differentiated mechanism, viable economic path, delivery owner, critical-risk mitigation, and a test that could change the team's mind.

Read `references/option-method.md` for scoring rules. Copy `assets/option-portfolio.csv` into the project root when the template is unavailable.

## Handoff

End with the standard CaseKit handoff block plus:

- Chosen option and decision ID:
- Rejected options and revisit triggers:
- Highest-uncertainty score:
- Next test before deck freeze:
