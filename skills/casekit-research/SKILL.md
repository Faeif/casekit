---
name: casekit-research
description: Conduct decision-oriented research for case competitions and hackathons with traceable claims, source-quality scoring, triangulation, market/customer/competitor evidence, benchmarks, and explicit gaps. Use when evidence, citations, market sizing inputs, customer insight, competitor analysis, regulations, conversion benchmarks, or fact-checking are needed for a case or pitch.
---

# CaseKit Research

Research to resolve a decision, not to accumulate links.

## Frame the research

1. State the decision or claim the research must support.
2. List 3–7 answerable research questions.
3. Mark each as `must-know`, `useful`, or `nice-to-have`.
4. Define stop conditions: evidence is sufficient when it can change or defend a decision.

Choose `Sprint`, `Standard`, or `Deep` using `references/research-modes.md`. Match research cost to decision risk instead of maximizing source count.

Read `references/source-policy.md` before collecting sources. For detailed query construction, freshness, disconfirming search, and source selection by claim type, also read the sibling validator reference `../casekit-validator/references/web-research-policy.md` when available. Read `references/competitor-intelligence.md` for competitor, pricing, or market-position questions. Use `assets/research-output.md` for delivery.

## Search and evidence workflow

1. Search primary sources first: official statistics, laws, regulator documents, company filings, product documentation, original datasets, peer-reviewed research, and direct customer evidence.
2. Use reputable secondary sources to interpret or triangulate, not to replace accessible primary evidence.
3. Capture exact support: page, table, section, date, population, geography, and definition.
4. Separate what the source states from the team's interpretation.
5. Triangulate high-stakes claims with two independent sources when practical.
6. Test disconfirming evidence and alternative explanations.
7. Enter every usable claim in the shared evidence ledger with stable IDs.
8. Run the source checker before handoff; live URL status is only a warning and never substitutes for reading the source.

## Claim discipline

Label each statement as:

- `Fact`: directly supported by evidence.
- `Benchmark`: observed elsewhere and transferred with caveats.
- `Derived estimate`: calculated from facts or assumptions; show formula.
- `Assumption`: uncertain input chosen for modeling; add to assumption ledger.
- `Target`: desired result; never present as a forecast.
- `Hypothesis`: testable belief awaiting validation.

Never convert a benchmark into a forecast without explaining transferability. Never cite a search snippet, AI answer, unsourced infographic, or circular citation as final evidence.

## Required analysis

- Define terms consistently across sources.
- Normalize units, currency, geography, population, and time horizon.
- Identify denominator traps and sample bias.
- For market sizing, provide top-down context and bottom-up reachable volume.
- For competitor analysis, compare customer, job, mechanism, price, channel, proof, limitation, and strategic response.
- Include direct competitors, adjacent solutions, manual workarounds, and doing nothing. Mine customer language and switching/churn signals when relevant.
- For customer research, distinguish reported preference from observed behavior or willingness to pay.
- For regulation or safety, identify current authoritative rules and unresolved interpretation.

## Output

Return:

1. Decision-relevant answer in 3–7 bullets.
2. Evidence table with Claim IDs and Source IDs.
3. Implications for strategy, finance, product, and marketing.
4. Contradictory evidence and limitations.
5. Open questions ranked by decision impact.
6. Recommended validation method and minimum useful sample.
7. Handoff block required by CaseKit.

Assign confidence by evidence strength, agreement, recency, fit, and sensitivity—not by writing tone.

Keep raw capture separate from synthesis in Standard and Deep modes. Run a verification pass after synthesis to detect circular sourcing, inconsistent definitions, stale data, unsupported claims, and contradictions.
