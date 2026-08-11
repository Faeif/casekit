# Contributing

CaseKit contributions should improve decision quality, evidence traceability, speed, or judge readiness without adding unnecessary prompt weight.

## Rules

1. Keep each `SKILL.md` under 500 lines and move detailed methodology into `references/`.
2. Use imperative instructions and preserve the shared CaseKit data contract.
3. Add no framework, metric, or template unless it changes a decision or prevents a recurring failure.
4. Never include fabricated benchmark values. Examples must be clearly synthetic.
5. Attribute adapted source code or substantial text in `THIRD_PARTY_NOTICES.md`.
6. Add or update validation whenever a deterministic rule is introduced.

## Before opening a pull request

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate_suite.py
```

Describe the competition failure mode addressed, files changed, expected behavior, evidence or rationale, and manual test performed.
