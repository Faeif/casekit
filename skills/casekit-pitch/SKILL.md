---
name: casekit-pitch
description: Convert evidence, strategy, economics, product, and go-to-market analysis into a concise judge-focused pitch narrative, slide storyboard, demo sequence, speaker script, 130-150 WPM pitch timing enforcer, 4-judge rehearsal simulator, appendix, and Q&A transitions. Use when creating or revising competition decks, hackathon presentations, executive pitches, vision stories, slide headlines, scripts, or timed delivery.
---

# CaseKit Pitch

Make the recommendation easy to understand, believe, remember, and act on.

## Build the story

1. Identify the judging decision: what must judges believe to award the team?
2. Write the thesis: `For [stakeholder], we will achieve [outcome] by [distinct mechanism], producing [quantified value] within [time].`
3. State a vision that has all three parts: future state, category/customer change, and the mechanism the team will earn it through. Label it as vision, not current proof.
4. Build a claim sequence: tension → evidence → insight → choice → mechanism → current proof → growth loop → economics → execution → earned vision → ask.
5. Map each claim to rubric criterion, evidence/assumption IDs, and likely objection.
6. Design slides only after the claim sequence works in plain text.

Read `references/story-and-slide-rules.md`. Use `assets/pitch-storyboard.md`.

Create the official competition version first, then derive—not independently rewrite—5-minute, 2-minute, 1-minute, and two-sentence variants when useful. All variants must preserve the same thesis, values, evidence labels, and ask.

## Slide rules

- One slide, one job, one conclusion-style headline.
- Show evidence visually; put detailed methodology and sources in appendix.
- Distinguish actuals, forecasts, targets, and benchmarks in labels.
- Distinguish current proof, validated next milestone, and long-term vision in labels.
- Use the same names, units, periods, and values as the shared ledgers.
- Prefer causal diagrams, funnels, unit-economics bridges, timelines, and before/after flows when they clarify reasoning.
- Remove generic framework slides unless they change the decision.
- Keep source markers visible and resolvable.

## Pitch Timing & 130–150 WPM Word Budgeting

Spoken pitch delivery degrades sharply above 150 words per minute. Enforce strict pacing across slide `speaker_notes`:

$$\text{Word Budget} = \text{Target Duration (Minutes)} \times 140\text{ WPM (Target Average)}$$

| Pitch Format | Target Duration | Word Budget Range | Slide Count | Average Words / Slide |
|---|---|---|---|---|
| **Executive Elevator** | 1 Minute | 130 – 150 words | 1 – 2 slides | ~75 words |
| **Rapid Lightning** | 2 Minutes | 260 – 300 words | 3 – 4 slides | ~75 words |
| **Standard Hackathon** | 3 Minutes | 390 – 450 words | 5 – 6 slides | ~70 words |
| **Demo Day / YC** | 5 Minutes | 650 – 750 words | 8 – 10 slides | ~75 words |
| **Board / Investment** | 10 Minutes | 1,300 – 1,500 words | 12 – 15 slides | ~95 words |

### Timing Validation Rules
1. Calculate words per slide: `words = len(speaker_notes.split())`.
2. Estimated slide duration: `slide_seconds = (words / 140.0) * 60.0`.
3. Pacing warnings:
   - **Rushing alert (> 150 WPM)**: High risk of buzzer cutoff or unintelligible delivery. Cut text.
   - **Dragging alert (< 120 WPM)**: Low information density or excessive pauses. Add concrete proof.

## 4-Judge Rehearsal Simulator

Before final deck freeze, stress-test the argument against the 4 adversarial judge personas:
- **The Skeptical CFO**: Attack vectors on fully-loaded CAC, 45-day AR cash trough, margin floors, churn.
- **The Deep-Tech CTO**: Attack vectors on 504 timeout idempotency, dropped webhooks, PDPA encryption, rollback runbooks.
- **The Corporate BU Head**: Attack vectors on sales commission cannibalization, 14-month IT queue, reputation risk.
- **The YC Partner**: Attack vectors on $0 acquisition wedge, organic developer pull, bottom-up TAM ($ \text{Units} \times \text{Price} $).

Execute the **4-Move Response Sequence**: Direct Answer (< 15 words) → Evidence Anchor (`CLM`/`MET`) → Sensitivity Bound (`ASM`) → Validated Action (`EXP`).

Read `references/rehearsal-simulator.md` for complete 3-minute rapid-fire drill protocols and question banks.

## Delivery package

Produce thesis, narrative spine, official slide storyboard, exact headlines, key visuals, evidence IDs, speaker notes, transitions, demo choreography, fallback, appendix map, timing, closing line, requested short variants, and CaseKit handoff. Do not invent traction, partnerships, customer quotes, or validation.

Read `references/pitch-variants.md` when producing compressed formats or rehearsal material.
