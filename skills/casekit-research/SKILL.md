---
name: casekit-research
description: Conduct decision-oriented research for case competitions and hackathons with traceable claims, source-quality scoring, 4-tier primary source hierarchy, triangulation, competitor autopsies, and offline archival. Use when evidence, citations, market sizing inputs, competitor analysis, regulations, conversion benchmarks, or fact-checking are needed.
---

# CaseKit Research

Research to resolve a decision, not to accumulate links.

## Frame the research

1. State the decision or claim the research must support.
2. List 3–7 answerable research questions.
3. Mark each as `must-know`, `useful`, or `nice-to-have`.
4. Define stop conditions: evidence is sufficient when it can change or defend a decision.

Choose `Sprint`, `Standard`, or `Deep` using `references/research-modes.md`. Match research cost to decision risk instead of maximizing source count.

Read `references/source-policy.md` before collecting sources. For detailed query construction, freshness, disconfirming search, and source selection by claim type, also read the sibling validator reference `../casekit-validator/references/web-research-policy.md` when available. Read `references/competitor-intelligence.md` for competitor, pricing, market-position, and predecessor failure autopsies. Use `assets/research-output.md` for delivery.

## Primary Source Evidence Hierarchy

Anchor every factual claim in the highest available authority tier:

- **Tier 1: Authoritative Primary Sources** (Mandatory anchor for all high-stakes/material claims)
  - SEC 10-K, 10-Q, 8-K, S-1 filings (US) and Thai SEC 56-1 One Reports / audited financials.
  - Government Gazettes, Royal Decrees, enacted legislation, official regulator rules.
  - Central Bank statistical bulletins (Bank of Thailand, Federal Reserve, ECB).
  - National statistical offices (NESDC, US Census Bureau, Eurostat).
  - Multilateral economic datasets (World Bank, IMF, OECD, WHO).
  - Official first-party product API documentation, published pricing, and legal terms.
- **Tier 2: Peer-Reviewed & Systematic Research**
  - Peer-reviewed academic journals & systematic literature reviews (PubMed, IEEE).
  - Published university research datasets with disclosed methodology.
  - Independent laboratory benchmark datasets.
- **Tier 3: Triangulated Industry & Financial Benchmarks**
  - Major market data terminals (Bloomberg, Refinitiv, S&P Capital IQ, PitchBook).
  - Analyst reports with transparent methodology (Gartner, IDC, Canalys).
  - Directly documented customer/expert interviews (with recorded methodology).
- **Tier 4: Contextual & Qualitative Discovery** (Context only; never sole anchor)
  - Credible financial journalism (Financial Times, Wall Street Journal, Bloomberg).
  - Industry trade association surveys with documented sample size.
  - Verified company case studies & engineering blogs.
- **Banned as Final Evidence (Anti-Hallucination Rejection)**:
  - Search engine result snippets (Google, Bing, Baidu).
  - Direct AI chatbot answers without underlying primary URL citations.
  - Unsourced infographics, marketing pitch decks, social media posts.
  - Circular press releases quoting unverified third-party claims.

## Search and evidence workflow

1. Search Tier 1 primary sources first: official statistics, laws, regulator documents, company filings, product documentation, original datasets, peer-reviewed research, and direct customer evidence.
2. Use reputable secondary sources to interpret or triangulate, not to replace accessible primary evidence.
3. Capture exact support: page, table, section, date, population, geography, and definition.
4. Separate what the source states from the team's interpretation.
5. Apply the "Rule of 3" Triangulation Protocol for high-stakes claims (market sizing, core pricing, unit margins, legality): corroborate across Macro, Micro, and Proxy legs.
6. Auto-archive offline snapshots of referenced URLs under `01-INPUTS/archive/` (or `inputs/archive/`) with SHA-256 integrity hashes.
7. Test disconfirming evidence and alternative explanations.
8. Enter every usable claim in the shared evidence ledger with stable IDs (`CLM-xxx`, `SRC-xxx`).
9. Run the source checker before handoff; live URL status is only a warning and never substitutes for reading the source.

## Claim discipline

Label each statement as:

- `Fact`: directly supported by Tier 1 or Tier 2 evidence.
- `Benchmark`: observed elsewhere and transferred with caveats and explicit transfer discount.
- `Derived estimate`: calculated from facts or assumptions; show explicit formula (`Value = A * B`).
- `Assumption`: uncertain input chosen for modeling; add to assumption ledger with low/base/high bounds.
- `Target`: desired result; never present as a forecast or fact.
- `Hypothesis`: testable belief awaiting experimental validation.

Never convert a benchmark into a forecast without explaining transferability. Never cite a search snippet, AI answer, unsourced infographic, or circular citation as final evidence.

## Required analysis

- Define terms consistently across sources.
- Normalize units, currency, geography, population, and time horizon.
- Identify denominator traps and sample bias.
- For market sizing, provide top-down context (Macro) and bottom-up reachable volume (Micro: `Customers * Price * Frequency`).
- For competitor analysis, perform failure autopsies of predecessor ventures across the 6 Fatal Failure Traps and establish structural immunity.
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
