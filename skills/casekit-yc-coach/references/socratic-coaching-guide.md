# Socratic YC Partner Coaching Guide & Dialogue Scripts

This guide provides the core conversational scripts, WTP calculation models, Buyer-User separation checks, and ledger synchronization rules for the `casekit-yc-coach` skill.

---

## 1. Socratic Questioning Framework

When coaching founders, apply structured Socratic inquiry:

### A. Testing Problem Reality (The Hair-on-Fire Test)
- **Question**: *"What is the exact financial and operational penalty your customer pays today if they completely ignore this problem for the next 6 months?"*
- **Structured Choices**:
  - `A) (Recommended) Direct regulatory non-compliance fines ($10k/month) or revenue loss from customer churn.`
  - `B) Wasted employee hours on manual spreadsheet reconciliation ($4,000/month loaded payroll cost).`
  - `C) General inefficiency or dissatisfaction without quantified economic damage.`

### B. Testing Real Demand (The Desperate Workaround Test)
- **Question**: *"How are your first 5 prospective customers solving this right now, and what messy workarounds have they built?"*
- **Structured Choices**:
  - `A) (Recommended) They built a custom 12-tab Google Sheet maintained by 2 full-time analysts.`
  - `B) They hired an offshore agency / VA team spending $3,000/month on manual copy-pasting.`
  - `C) They are using a patchwork of 3 generic SaaS tools that don't talk to each other.`
  - `D) They are doing nothing and living with the problem (Warning: Weak demand signal).`

### C. Testing Willingness-to-Pay (The WTP Multiplier Test)
- **Question**: *"If your solution costs $10,000/year, what is the exact status-quo workaround cost you eliminate to prove a 5x-10x ROI?"*
- **Structured Choices**:
  - `A) (Recommended) Eliminates 15 hours/week of senior engineer time ($75k/year value) -> 7.5x ROI multiplier.`
  - `B) Replaces 2 legacy point solutions costing $24,000/year -> 2.4x ROI multiplier.`
  - `C) Unquantified productivity boost (Warning: High sales friction with CFO).`

---

## 2. Willingness-to-Pay (WTP) Mathematical Formula

Always enforce the quantitative WTP Cost-Benefit Matrix:

$$\text{Status Quo Annual Cost} = (\text{Wasted Hours/Week} \times 50 \text{ Weeks} \times \text{Loaded Hourly Wage}) + \text{Legacy Licenses} + \text{Error Losses}$$

$$\text{Net Annual Value Delivered} = \text{Status Quo Annual Cost} - \text{Annual Solution Price}$$

$$\text{Cost-Benefit Multiplier} = \frac{\text{Status Quo Annual Cost}}{\text{Annual Solution Price}}$$

- **Hurdle**: The Cost-Benefit Multiplier must be **>= 5.0x** (ideally 10.0x). If the multiplier is under 3.0x, enterprise deals stall in procurement.

---

## 3. Economic Buyer vs End User Separation Guide

Never allow founders to confuse the product user with the contract signer.

| Stage | Economic Buyer Alignment | End User Alignment |
|---|---|---|
| **Intake** | Who owns the P&L budget for this department? (VP Eng, CFO, Head of Ops) | Who logs in every morning to perform the core workflow? (Senior Dev, Clerk) |
| **Value Pitch** | *"Saves $150k in annual contractor spend and guarantees SOC 2 compliance."* | *"Zero-click keyboard shortcuts, auto-complete, dark mode, no crashes."* |
| **Sales Gate** | Security review, ROI calculation, contract term, payment terms. | Usability test, ergonomic trial, team adoption rate. |
| **Failure Mode** | Buyer says *"Looks nice, but we don't have budget for this category."* | User says *"Management bought this tool, but it slows down my work so I don't use it."* |

---

## 4. Bottom-Up TAM / SAM / SOM Calculation Rules

- **Strictly Prohibited**: Top-Down market percentages (e.g. *"If we capture 1% of the $100B global healthcare market, we are a unicorn"*).
- **Mandatory Bottom-Up Formula**:
  $$\text{TAM} = \text{Total Verified Entities in Defined Category} \times \text{Annual Contract Value (ACV)}$$
  $$\text{SAM} = \text{Entities Reachable within Regulatory/Technical Footprint} \times \text{ACV}$$
  $$\text{SOM} = \text{Beachhead ICP Entities Targetable in Years 1-2} \times \text{ACV}$$

---

## 5. CaseKit Ledger Auto-Synchronization Rules

During coaching sessions, translate founder answers into structured updates for CaseKit ledger files:

```
Founder Response
      │
      ▼
[ Coach Extraction Engine ]
      ├─► 00-case-profile.md: Update Value Prop, Buyer, ICP, Trigger Event
      ├─► 01-evidence-ledger.csv: Append CLM-xxx & SRC-xxx with quotes/URLs
      ├─► 02-assumptions.csv: Append ASM-xxx with low/base/high bounds
      ├─► 03-metric-tree.csv: Link MET-xxx bottom-up revenue drivers
      ├─► 04-decision-log.csv: Record DEC-xxx strategic choices
      └─► 05-risk-register.csv: Record RSK-xxx identified risk factors
```

Ensure all generated IDs follow standard CaseKit regex patterns:
- `CLM-[0-9]{3}` (Claims)
- `SRC-[0-9]{3}` (Sources)
- `ASM-[0-9]{3}` (Assumptions)
- `MET-[0-9]{3}` (Metrics)
- `DEC-[0-9]{3}` (Decisions)
- `RSK-[0-9]{3}` (Risks)
