# Competition workflow

## Gate 0 — Decode the game

Extract deliverables, time, presentation format, prohibited methods, scoring weights, mandatory themes, judge profiles, and tie-break criteria. Translate each rubric item into observable evidence the submission must show.

## Gate 1 — Discover and frame the problem

Define stakeholder, job-to-be-done, context, trigger, current behavior, quantified pain, root cause, and consequence. Use 5 Why, but stop when the next answer is outside the team's ability to influence or no longer supported.

Run the Premise Gate and choose Proceed, Proceed with validation, Reframe, or Stop before solution lock.

## Gate 2 — Choose

Generate 2–4 strategic options. Compare rubric fit, impact, feasibility, differentiation, evidence, cost, time-to-value, and risk. Record rejected options and the condition under which they become preferable.

Use `casekit-strategy` and `option-portfolio.csv` to make the choice observable. Do not turn confidence labels into fabricated probability claims.

## Gate 3 — Make the system cohere

Build one causal chain:

```text
Action → Driver KPI → Behavior change → Outcome KPI → Economic value → Strategic goal
```

Every product feature and campaign activity must appear in this chain or be removed.

## Gate 4 — Quantify

Estimate revenue before cost. Build bottom-up drivers, scenarios, sensitivity, break-even, and resource needs. Reconcile marketing funnel volume with operational and technical capacity.

## Gate 5 — Prove feasibility

Specify MVP, user journey, architecture, data, safety, implementation, owners, dependencies, test plan, and demo fallback.

## Gate 6 — Tell and test

Build the pitch around the decision, not around workstream order. Create the canonical deck spec, run structural and cross-artifact validation, render the deck, visually inspect it, red-team the argument, rehearse Q&A, time the script, and verify citations and formulas.

## Team topology

For six people, use Captain/Integrator, Discovery/Research, Finance, Product/Tech, GTM/Operations, and Story/Deck. Everyone rotates through Red Team; the author never gives final approval to their own critical output. For smaller teams combine adjacent roles, but keep one source-of-truth owner and an independent final checker.

Each assignment must state deliverable, input IDs, output IDs, acceptance gate, deadline, and handoff recipient. Do not assign vague topics such as “do marketing.”

## Idea promotion and chat boundary

Use three layers so the team can think freely without polluting the final case:

| Layer | Location | Meaning | May appear in deck/model? |
|---|---|---|---|
| Chat scratch | AI chat or personal note | rough prompt, alternative, or question; not shared truth | No |
| Team review | `idea-backlog.csv` | visible proposal with owner and next action | No, unless explicitly labeled as an option/assumption |
| Official case record | ledgers, decisions, experiments, model, deck spec | accepted work with IDs and a review gate | Yes |

Do not save every chat. Save an idea only when it is worth team attention, needs a test, changes an option, or may otherwise be forgotten. Use an explicit instruction such as: `Create IDEA-003 as exploring only; do not change the model, ledger, or deck.`

Promotion requires a human decision:

```text
exploring → proposed → accepted-for-test → accepted-for-case
                    ↘ rejected / parked
```

`accepted-for-test` requires an `EXP` ID and an explicit pass/stop threshold. `accepted-for-case` requires a `DEC` ID, named affected artifacts, and any resulting `ASM`, `MET`, or `CLM` records. Promotion does not convert an assumption into a fact.

## Multi-device Git rhythm

Start with **Easy Team Mode**. Use one private case repository. Each teammate works only inside `00-INBOX/<their-name>/`, then commits directly to `main`; this avoids conflicts because nobody shares a draft file. One Integrator owns all shared official files and promotes approved work after team discussion. Before any official promotion, the Integrator runs the project validator; after promotion, they validate and render the deck again.

Use a personal branch and pull request only when a teammate must directly edit a shared official file or when the team is comfortable reviewing code-style changes. Never push to another teammate's branch.

## Suggested sprint allocation

For a 24-hour challenge:

| Window | Primary output |
|---|---|
| 0–1h | rubric map, roles, brief |
| 1–4h | discovery, problem evidence, customer, premises |
| 4–6h | options and strategic choice |
| 6–12h | prototype, economics, GTM in parallel |
| 12–16h | integration, operations, and first validation |
| 16–20h | deck rendering, visual QA, and demo |
| 20–22h | independent validation, red team, and fixes |
| 22–24h | rehearsal, backup, submission |

Shorten proportionally for shorter events. Protect at least 15% of total time for integration and rehearsal.
