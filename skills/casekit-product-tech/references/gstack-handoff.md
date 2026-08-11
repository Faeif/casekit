# Optional gstack technical handoff

Use gstack as a separately installed execution layer when the case includes a coded prototype. CaseKit remains authoritative for scope, assumptions, cost, and judging evidence.

## Handoff package

Provide:

- Chosen opportunity frame and decisive value moment.
- Must-prove vertical slice and explicit out-of-scope list.
- Architecture, data flow, integrations, and external dependencies.
- Acceptance tests, edge cases, privacy/security/safety controls.
- Demo happy path, seeded data, and fallback.
- Time budget and irreversible constraints.
- Relevant Risk, Assumption, Metric, and Decision IDs.

## Suggested routing

Use product/CEO challenge before scope lock, engineering review before build, design review for critical user experience, report-only QA near submission, and security review when sensitive data or consequential actions are involved. Do not run a heavyweight release workflow when a disposable prototype is sufficient.

Return defects and scope changes to CaseKit. Update Finance when implementation changes unit cost, staffing, capacity, or timeline.

Project and current installation instructions: https://github.com/garrytan/gstack. This integration contains no vendored gstack code.

