# Start here — CaseKit + Obsidian

Open this folder directly as an Obsidian vault. This workspace is the team's source of truth; use links, comments, and Git history rather than private copies of numbers.

## First 20 minutes

1. Put the official brief, rubric, current deck, spreadsheets, and raw data in `inputs/`.
2. Complete `00-case-profile.md` and `00-brief.md`.
3. Map the judging rubric in `11-rubric-scorecard.csv` before dividing work.
4. Ask an AI: `Use casekit-orchestrator to read this workspace, list missing critical inputs, choose the operating mode, and create an assignment plan.`
5. Use `casekit-strategy` to fill `option-portfolio.csv` before locking a solution.
6. List every external dependency in `integration-contract.csv`; mark it Real, Sandbox, Mocked, Planned, or Blocked.
7. If the team will build code, use `casekit-engineering` to complete `engineering-delivery-plan.md` before implementation.

## Edit numbers safely

- Edit assumptions in `02-assumptions.csv` and metrics in `03-metric-tree.csv`; preserve IDs.
- Put external facts in `01-evidence-ledger.csv`, never only in a slide.
- For Excel, put the workbook in `inputs/`, run the cloned CaseKit CLI with `python3 /path/to/casekit/casekit.py inspect-spreadsheet`, then map selected cells in `data-import-map.json`.
- Run `python3 /path/to/casekit/casekit.py sync-spreadsheet . data-import-map.json --apply` after changing the workbook, then run `python3 /path/to/casekit/casekit.py validate . --strict` before deck freeze.
- Do not edit a deck number directly when it has a `metric_binding`; update its metric, re-render, and validate.
- Never present a partner integration as real unless the integration contract has an owner, approved data boundary, and tested path.

## Obsidian conventions

- Use `[[00-brief]]`, `[[07-final-integrated-case]]`, and relative links to navigate.
- Keep meeting notes in `inputs/notes/`; move only verified findings into shared ledgers.
- Treat a number without `SRC`, `ASM`, or `MET` ID as a draft, not presentation-ready.
- Use Git commits at each decision lock: brief, strategy, model, deck, and submission.

## Final commands

```bash
python3 /path/to/casekit/casekit.py validate . --strict
python3 /path/to/casekit/casekit.py render .
```
