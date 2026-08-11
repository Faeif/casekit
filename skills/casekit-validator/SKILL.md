---
name: casekit-validator
description: Audit a case competition or hackathon submission for evidence traceability, source quality, numeric consistency, financial logic, strategic coherence, feasibility, deck clarity, rubric fit, and delivery readiness. Use before integrating workstreams, freezing numbers, rendering slides, rehearsing, or submitting; also use to diagnose contradictory claims, broken references, unsupported assumptions, or weak judge defenses.
---

# CaseKit Validator

Act as an independent quality gate. Find decision-changing defects and return a repair queue; do not merely praise completeness.

## Audit sequence

1. Identify the official rubric, constraints, deadline, and submission format.
2. Run `scripts/audit_case.py <project>` for structural, referential, enum, range, and deck-spec checks.
3. Run `scripts/check_sources.py <project>` offline. Use `--online` only when network checks are useful; an unreachable URL is a warning, not proof that a claim is false.
4. Score the official rubric with `scripts/score_rubric.py <rubric.csv>` when weights exist.
5. Perform the seven judgment layers below and classify each finding `Blocker`, `Major`, `Minor`, or `Polish`.
6. Re-run checks after repairs. Freeze the deck only when no blocker remains and every major issue has an owner and disposition.

Read `references/validation-layers.md` for criteria and `references/web-research-policy.md` before reviewing external evidence. Use `assets/validation-report.md` for the human-readable report.

## Seven validation layers

- Structure: required artifacts, IDs, owners, statuses, and deadlines exist.
- Evidence: claims resolve to sources; assumptions are labeled; source quality, freshness, relevance, and transferability are explicit.
- Financial: formulas, units, periods, denominators, scenarios, capacity constraints, sensitivity, break-even, CAC scope, cohort LTV, payback, recurring-revenue retention, and cash reconcile.
- Strategy: goal, segment, choice, mechanism, alternatives, and trade-offs form one causal argument.
- Feasibility: product, technology, operations, legal, partner, data, and adoption dependencies have tests and fallbacks.
- Deck: one claim per slide, correct chart type, readable hierarchy, visible source markers, and no number drift.
- Judge delivery: rubric coverage, timing, demo fallback, Q&A defense, ask, and closing are rehearsed.

## Evidence rules

- Never cite a search-result snippet as support. Open the source and capture the exact page, table, or section.
- Prefer primary sources for facts: regulator, law, official statistics, company filing, product documentation, original research, or first-party experiment.
- Use industry reports and news for context or triangulation, not as automatic truth.
- Use interviews, reviews, and community posts as qualitative evidence; do not convert them into population rates without a sampling argument.
- Search for disconfirming evidence and failure cases before assigning `High` confidence.
- For time-sensitive facts, verify currency as of the project date.

## Output contract

Return:

1. Readiness verdict: `Not ready`, `Conditional`, or `Ready`.
2. Rubric-weighted score and scoring uncertainty.
3. Blockers and major findings with artifact, ID, consequence, owner, and repair.
4. Contradiction matrix for any value or claim that differs across artifacts.
5. Unsupported claims and unresolved source/assumption references.
6. Top sensitivities and what would change the recommendation.
7. Submission checklist and residual risks.

Never imply that passing validation guarantees winning. Passing means the package is internally coherent, traceable, defensible, and ready for human judgment.
