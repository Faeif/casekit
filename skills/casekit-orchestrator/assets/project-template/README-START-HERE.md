# Start here — CaseKit + Obsidian

Open this folder directly as an Obsidian vault. This workspace is the team's source of truth; use links, comments, and Git history rather than private copies of numbers.

## First 20 minutes

1. Put the official brief, rubric, current deck, spreadsheets, and raw data in `inputs/`.
2. Complete `00-case-profile.md` and `00-brief.md`.
3. Map the judging rubric in `11-rubric-scorecard.csv` before dividing work.
4. Ask an AI: `Use casekit-orchestrator to read this workspace, list missing critical inputs, choose the operating mode, and create an assignment plan.`
5. Use `casekit-strategy` to fill `option-portfolio.csv` before locking a solution.
6. Complete `16-vision-growth-plan.md` before writing the vision slide or buying growth activity; distinguish current proof, next milestone, and long-term vision.
7. List every external dependency in `integration-contract.csv`; mark it Real, Sandbox, Mocked, Planned, or Blocked.
8. If the team will build code, use `casekit-engineering` to complete `engineering-delivery-plan.md` before implementation.

## Chat, ideas, and official work

- A chat response or AI-generated Markdown is a draft by default; it does not change the case record automatically.
- Keep throwaway brainstorming in chat. If an idea deserves team review, add one row to `idea-backlog.csv` with status `exploring` or `proposed`.
- Only promote an idea after a human decision: `accepted-for-test` needs an `EXP` ID; `accepted-for-case` needs a `DEC` ID and named affected artifacts.
- Promotion does not make an idea factual. Add `ASM`, `SRC`, `CLM`, and `MET` records as appropriate, then label assumptions and forecasts honestly.
- Ask an AI explicitly: `Record this as IDEA-001 for review only; do not update the model, ledgers, or deck.` Or: `Promote IDEA-001 to accepted-for-test and create the required experiment and assumptions.`

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
