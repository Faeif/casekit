# Competitor Intelligence, Failure Autopsies & Triangulation

## 1. The "Rule of 3" Triangulation Protocol

For every **High-Stakes Claim** (Total Addressable Market sizing, Core Pricing / Willingness-to-Pay, Unit Contribution Margin, Regulatory Legality, or Primary Strategic Differentiation), CaseKit mandates corroboration across three independent methodological legs:

```
                          [ HIGH-STAKES CLAIM ]
                                    |
         +--------------------------+--------------------------+
         |                          |                          |
         v                          v                          v
    [ LEG A: MACRO ]           [ LEG B: MICRO ]          [ LEG C: PROXY ]
Top-down regulatory /      Bottom-up unit economics   Comparable peer actuals /
institutional statistics   (Target Customers x AOV    publicly audited filings
(e.g. BOT / NESDC data)    x Annual Frequency)        (e.g. 56-1 / 10-K filings)
```

### Triangulation Rules
1. **Source Independence**: The three sources must not share a common underlying citation. Detect and reject circular citations where Report B merely quotes Report A.
2. **Methodological Diversity**: The three legs must employ distinct estimation techniques (e.g., 1 institutional filing + 1 bottom-up unit calculation + 1 peer competitor audited report).
3. **Ledger Linking**: In `01-evidence-ledger.csv`, related claims must reference cross-corroborating `SRC-xxx` IDs. High-stakes outcome metrics in `03-metric-tree.csv` must link to at least 3 source/assumption IDs in `source_or_assumption_ids`.

---

## 2. Competitor Post-Mortem Autopsy Framework

Judges and investors invariably ask: *"Why has nobody succeeded at this before?"*
Every CaseKit venture proposal must conduct a systematic autopsy of predecessor failures to establish **Structural Immunity**.

### The 6 Fatal Failure Traps

| Trap | Failure Mechanism | Famous Historical Precedent | CaseKit Structural Immunity Defense |
|---|---|---|---|
| **1. Unit Margin Collapse** | Fully-loaded CAC and delivery/fulfillment COGS exceeded customer LTV; variable costs scaled linearly with volume. | Kozmo.com, Fast, Webvan | Maintain positive contribution margin on Day 1; zero-CAC organic developer wedge; automated low-touch onboarding. |
| **2. Premature Scaling** | Massive marketing spend deployed before proving cohort retention (NRR/GRR) or product-market fit. | Quibi, Better Place | Explicit validation gates (`09-experiments.csv`); no capital deployment to scale until pilot conversion threshold met. |
| **3. Distribution Lockout** | Incumbent platform changed API rules, increased take rate, or blocked channel access. | Zynga (Facebook dependent), Meerkat | Multi-homed distribution; direct developer integration; open API standards; self-hosted fallback. |
| **4. Regulatory Ambush** | Business model operated in legal grey zone and was shut down by regulatory injunction or licensing ban. | Napster, Aereo, Zenefits | Pre-vetted compliance with Royal Decrees / PDPA / SEC regulations; partner bank / licensed operator integration. |
| **5. Buyer vs User Disconnect** | End users loved the tool, but the enterprise Economic Buyer refused to approve procurement or pay. | EdTech B2B startups | Explicit separation of Economic Buyer (CFO/VP) from End User; quantified ROI / cost-reduction matrix. |
| **6. Hardware/CapEx Cash Bleed** | High upfront tooling and physical inventory cycles caused severe cash trough before software margins began. | Juicero, Pearl Automation | Asset-light modular hardware; standard off-the-shelf components; pre-orders funding manufacturing batches. |

---

## 3. Active Competitor Research Surface

For each direct, indirect, and status-quo alternative:

- **Customer and Job**: Target ICP and specific job hired for.
- **Product/Service Mechanism**: Core technology and key workflow.
- **Pricing & Packaging**: Price, value metric, tiers, discounting, and switching costs.
- **Distribution & GTM**: Sales motion, partner channels, and acquisition wedge.
- **Credible Traction**: Real revenue, customer counts, and verifiable adoption signals.
- **Customer Sentiment**: Customer praise, complaints, requested features, migration reasons, and churn signals.
- **Defensible Strengths & Limitations**: Moat depth vs known vulnerabilities.
- **Strategic Response**: Where they win, where CaseKit's recommendation wins, and where NOT to compete.

Use official pricing and audited filings for facts. Use customer reviews as qualitative signals with sample bias caveats.

---

## 4. Outputs

Produce an alternatives map, comparison matrix, pricing landscape, customer-language map, and one-page battle cards for competitors central to the decision. Do not create vanity feature matrices that reward superficial feature checklists.
