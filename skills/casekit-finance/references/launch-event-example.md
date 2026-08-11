# Launch-event worked structure

## Goal

Assume the business wants incremental launch-event revenue, qualified leads, and trial experience while protecting brand quality and service capacity.

## Metric tree

```text
Incremental contribution
├── Net event revenue
│   ├── unique reachable audience
│   ├── event attendance rate
│   ├── qualified attendee rate
│   ├── purchase conversion
│   └── net revenue per order
├── Direct variable cost
└── Attributable event cost
    ├── venue/production
    ├── staff
    ├── giveaways redeemed
    └── media/invitations
```

Guardrails may include wait time, complaint rate, stock-out rate, opt-in consent, demo failure, and attendee satisfaction.

## Revenue-first questions

1. What is the revenue or customer-acquisition goal and period?
2. How many orders are required at the proposed net revenue per order?
3. What purchase conversion is plausible for qualified attendees?
4. How many qualified attendees and total attendees are required?
5. How much unique reach/invitation volume is required to produce attendance?
6. Can venue, staffing, inventory, and demo stations serve that volume?
7. Which activity changes conversion rather than merely entertaining?

## Experience and cost

For each activity, calculate capacity per hour, participation rate, completion time, staffing, consumables, giveaway eligibility, redemption rate, and expected change in a funnel driver. Tie giveaway quantity to expected eligible completions plus a documented buffer, not to total reach.

## Example formulas

```text
Required orders = Revenue target ÷ Net revenue per order
Required qualified attendees = Required orders ÷ Purchase conversion
Required attendees = Required qualified attendees ÷ Qualified rate
Required invitations = Required attendees ÷ Attendance rate
Activity stations = Ceiling(Participants × Minutes per activity ÷ Event minutes)
Expected giveaways = Attendees × participation rate × completion rate × redemption rate
```

Use context-specific researched ranges for every rate. This example provides structure, not benchmark values.

