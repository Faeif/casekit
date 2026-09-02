# 4-Judge Rehearsal Simulator & Rapid-Fire Q&A Protocols

The CaseKit Rehearsal Simulator stress-tests venture narratives against four adversarial personas. Every team must survive 3-minute rapid-fire interrogation drills before presentation freeze.

---

## 1. The Four Adversarial Judge Personas

```
                               ┌────────────────────────────────┐
                               │    4-JUDGE ADVERSARIAL PANEL   │
                               └───────────────┬────────────────┘
                 ┌──────────────────┬──────────┴──────────┬──────────────────┐
                 ▼                  ▼                     ▼                  ▼
        ┌─────────────────┐┌─────────────────┐  ┌─────────────────┐┌─────────────────┐
        │  Skeptical CFO  ││  Deep-Tech CTO  │  │ Corporate BU Head││   YC Partner    │
        │ "Where is the   ││ "What breaks on │  │ "Why will sales ││ "How do you get │
        │  cash bleed?"   ││  504 timeouts?" │  │  adopt this?"   ││ 1,000 users $0?"│
        └─────────────────┘└─────────────────┘  └─────────────────┘└─────────────────┘
```

### Persona 1: The Skeptical CFO
- **Profile**: Institutional CFO / PE Partner focused on capital efficiency, working capital lag, fully-loaded costs, and gross margin integrity.
- **Primary Attack Vectors**:
  - Blended vs paid CAC obfuscation (omitting sales labor and tool overhead).
  - Working capital cash bleed (30–60 day accounts receivable lag).
  - CAC payback horizons exceeding 12 months.
  - Gross margin floor degradation under volume.
  - Revenue recognition vs cash collection timing.
- **High-Stakes Drill Questions**:
  1. *"What is your fully-loaded CAC when you include executive sales time, onboarding engineering, and paid acquisition tooling?"*
  2. *"In Month 7, when collections lag recognized revenue by 45 days, what is your maximum cash trough and does the company run out of cash?"*
  3. *"If monthly logo churn increases from 2.0% to 4.5%, how many months of cash runway remain under current burn?"*

### Persona 2: The Deep-Tech CTO
- **Profile**: Principal Distributed Systems Architect / VP Engineering auditing fault tolerance, data compliance, API boundaries, and architecture sizing.
- **Primary Attack Vectors**:
  - Single points of failure and third-party API rate limit throttling.
  - Unhandled 504 Gateway Timeouts, dropped webhooks, and lack of idempotency.
  - Premature distributed microservice complexity.
  - PDPA / GDPR encryption key custody, consent logs, and cross-border transfer.
  - Lack of automated rollback runbooks.
- **High-Stakes Drill Questions**:
  1. *"When the partner payment gateway returns 504 Gateway Timeout on 15% of checkout requests during peak load, how does your system guarantee idempotency and prevent double-charging?"*
  2. *"Where is customer personal data stored, who holds encryption keys, and what is your legal basis under PDPA?"*
  3. *"Why did you design a 12-microservice Kubernetes deployment for a system handling only 500 requests per minute?"*

### Persona 3: The Corporate BU Head
- **Profile**: Senior Executive Vice President / Business Unit MD balancing quarterly P&L, sales commission incentives, enterprise change management, and IT backlog queues.
- **Primary Attack Vectors**:
  - Internal sales commission cannibalization and branch pushback.
  - Enterprise IT procurement backlogs (12–18 month lead times).
  - Operational switching costs and employee workflow disruption.
  - Regulatory compliance approvals and audit risk.
  - Reputational fallout if a 6-month pilot fails.
- **High-Stakes Drill Questions**:
  1. *"Who in our branch network loses commission or has their daily workload increased if this software is deployed?"*
  2. *"Our enterprise IT backlog is 14 months long. How do you deploy without requiring a dedicated internal IT project sprint?"*
  3. *"If this pilot fails at 6 months, what is the reputation and operational damage to the business unit?"*

### Persona 4: The YC Partner
- **Profile**: Early-stage venture investor obsessed with organic pull, $0 CAC developer/user wedge, why now, and bottom-up market sizing ($ \text{Units} \times \text{Price} $).
- **Primary Attack Vectors**:
  - Top-down fake TAM sizing (quoting Gartner/IDC market percentages).
  - Lack of organic pull / dependency on paid Google & Meta ads.
  - "Vitamin vs Painkiller" problem urgency.
  - Defensibility against fast followers and incumbents.
  - Founder-market fit and speed of learning loop.
- **High-Stakes Drill Questions**:
  1. *"How did you acquire your first 10 paying customers without spending money on Google or Meta ads?"*
  2. *"If an incumbent copies your user interface in their next quarterly release, what is your structural moat?"*
  3. *"Why is this a billion-dollar venture opportunity rather than a featureset inside an existing SaaS tool?"*

---

## 2. The 4-Move Response Protocol

Every pitch Q&A answer must strictly follow this 4-step structure. Never waffle or give generic marketing responses.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MOVE 1: DIRECT ANSWER (< 15 Words)                                          │
│ State the exact number, decision status, or architectural choice immediately. │
├─────────────────────────────────────────────────────────────────────────────┤
│ MOVE 2: EVIDENCE / FORMULA ANCHOR                                            │
│ Cite specific CLM-xxx, SRC-xxx, MET-xxx, or exact formula.                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ MOVE 3: SENSITIVITY & CAVEAT BOUND                                          │
│ Acknowledge ASM-xxx low/high bounds and the operational constraint.          │
├─────────────────────────────────────────────────────────────────────────────┤
│ MOVE 4: VALIDATED NEXT ACTION                                               │
│ State the explicit experiment (EXP-xxx) or go-live gate that proves it.     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exemplary 4-Move Drill Response

**Judge (Skeptical CFO)**: *"What is your fully-loaded CAC, and when do you break even on a customer?"*

- **Move 1 (Direct Answer)**: *"Our fully-loaded CAC is THB 4,200, with a payback period of 4.8 months."*
- **Move 2 (Evidence Anchor)**: *"This is derived from `MET-004` (THB 1,800 paid marketing + THB 2,400 allocated onboarding labor from `CLM-003`)."*
- **Move 3 (Sensitivity Bound)**: *"Under `ASM-002` low-case conversion (1.8% vs 2.5% base), payback extends to 6.4 months, remaining well within our 12-month guardrail."*
- **Move 4 (Validated Action)**: *"`EXP-001` (100-user self-serve onboarding test) is scheduled in Sprint 1 to reduce labor overhead below THB 1,000."*

---

## 3. 3-Minute Rapid-Fire Drill Schedule

| Timecode | Phase | Focus Persona | Drill Objective |
|---|---|---|---|
| `0:00 - 0:45` | **Opening Volley** | Skeptical CFO | Fully-loaded CAC, unit margin floor, cash trough under 45-day AR lag. |
| `0:45 - 1:30` | **Growth & Wedge** | YC Partner | $0 acquisition wedge, organic pull, bottom-up TAM ($ \text{Units} \times \text{Price} $). |
| `1:30 - 2:15` | **Technical Defense**| Deep-Tech CTO | 504 timeout idempotency, PDPA encryption custody, architecture simplicity. |
| `2:15 - 3:00` | **Enterprise Reality**| Corporate BU Head| Commission alignment, 14-month IT queue workaround, rollback runbook. |

---

## 4. Rehearsal Anti-Patterns (Immediate Disqualification)

1. **The Preamble Stall**: *"That's a great question, let me explain our journey..."* (Fails Move 1).
2. **The Unanchored Number**: *"Our margins will be around 80% because software has high margins."* (Fails Move 2: Missing `MET` or `SRC` anchor).
3. **The False Certainty**: *"There is no downside risk because our algorithm is 100% accurate."* (Fails Move 3: Unbounded sensitivity).
4. **The Hand-Waving Promise**: *"We will figure out the partnership after we raise capital."* (Fails Move 4: Missing `EXP` or validation gate).
