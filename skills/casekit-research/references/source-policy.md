# Source and evidence policy

## Source hierarchy

| Tier | Name | Typical sources | Default use |
|---|---|---|---|
| 1 | Authoritative Primary Sources | SEC 10-K/10-Q/8-K/S-1, Thai SEC 56-1 One Report, laws, royal decrees, regulator rules, central bank stats (BOT, Fed, ECB), national stats (NESDC, Census), multilateral datasets (World Bank, IMF), official product API docs & pricing | Mandatory anchor for high-stakes and material claims |
| 2 | Peer-Reviewed & Systematic Research | Peer-reviewed journal studies (PubMed, IEEE), systematic reviews, published university research datasets with disclosed method, lab benchmarks | Support, validate, and triangulate |
| 3 | Triangulated Industry & Benchmarks | Market terminals (Bloomberg, Refinitiv, PitchBook, S&P Capital IQ), analyst reports with transparent sample method (Gartner, IDC, Canalys), documented customer interviews | Context, peer comparisons, and proxy benchmarks |
| 4 | Contextual & Qualitative Discovery | Reputable financial journalism (FT, WSJ, Bloomberg), trade association surveys, verified company engineering blogs | Discovery, trends, and qualitative context; never sole anchor |
| Banned | Anti-Hallucination Rejection | Anonymous posts, direct AI chatbot output, search engine result snippets, unsourced infographics, circular press releases | Prohibited as final evidence |

Quality is contextual. A company website is authoritative for its own price but weak evidence for its product's independent effectiveness.

## Quality score

Score each dimension 0–2:

- Authority
- Method transparency
- Directness to claim
- Recency for the decision
- Geographic/population fit
- Independence

Interpret total: `10–12 High`, `7–9 Medium`, `0–6 Low`. A low score may still be used for a low-stakes directional assumption if clearly labeled.

## Benchmark transfer test

Before applying an external conversion rate or unit cost, compare:

1. Audience intent and awareness.
2. Channel and placement.
3. Offer and price.
4. Geography and purchasing power.
5. Brand strength.
6. Funnel definition and denominator.
7. Measurement window.

Adjust the range wider when transferability is weak. Record the adjustment as a derived assumption.

## Citation minimum

Capture publisher, title, URL, publication date, access date, exact page/section, supporting passage or table, interpretation, and SHA-256 content hash in snapshot archive. For PDFs, include page number. For datasets, include table name, variable definition, filter, and retrieval date.
