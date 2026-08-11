# Validation layers

## Severity

- `Blocker`: can invalidate the recommendation, violate rules, break submission, or expose fabricated/contradictory evidence.
- `Major`: materially lowers rubric performance or judge confidence.
- `Minor`: weakens clarity, traceability, or execution but has a bounded effect.
- `Polish`: visual or wording improvement after substance is stable.

## Layer gates

### Structure

Pass when required files exist, IDs are unique, references resolve, status values are controlled, and each critical artifact has an owner.

### Evidence

Pass when material external claims have resolvable support; source quality, date, section, and interpretation are recorded; estimates are not mislabeled as facts; and disconfirming evidence has been sought.

### Financial

Pass when revenue follows a driver model, costs are complete enough for the decision, units and periods reconcile, capacity caps demand, scenarios are coherent, and the recommendation survives or explicitly reacts to sensitivity tests.

### Strategy

Pass when the target segment and choice are explicit, alternatives are rejected with criteria, activities change named drivers, and the model explains why the outcome should occur.

### Feasibility

Pass when critical technical, operating, legal, partner, and adoption premises have evidence or tests, with owners and fallbacks.

### Deck

Pass when every slide has one job, evidence IDs resolve, numbers match the ledgers, labels distinguish evidence states, visuals reveal rather than hide assumptions, and the deck remains readable at presentation scale.

### Delivery

Pass when time is below 90% of the limit, transitions and roles are rehearsed, the demo has a fallback, likely attacks have direct answers, and the close states decision and ask.

## Stop rule

Do not spend time polishing slides while a blocker remains in evidence, economics, rules, or feasibility. Repair in this order: rule compliance → recommendation validity → numeric integrity → execution → story → visual polish.
