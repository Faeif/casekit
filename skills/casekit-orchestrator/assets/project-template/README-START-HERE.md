# Start here — CaseKit + Obsidian

Open this folder directly as an Obsidian vault. This workspace is the team's source of truth; use links, comments, and Git history rather than private copies of numbers.

## Start here — Easy Team Mode

You only need to remember three places:

| Put it here | What belongs there | Who edits it |
|---|---|---|
| `inputs/` | original brief, rubric, old deck, Excel, raw data | Captain |
| `00-INBOX/<your-name>/` | your notes, AI drafts, research, calculations, ideas | each teammate, only their own folder |
| root official files | the team's approved evidence, numbers, decisions, and deck | Integrator only |

1. Captain puts source files in `inputs/` and asks AI: `Use casekit-orchestrator to summarize the brief and create a simple assignment plan. Do not edit official files yet.`
2. Each person creates one folder, for example `00-INBOX/finance-may/`, and works only there.
3. When ready, push that draft so the team can see it. Tell the Integrator in chat: “Please review my Finance draft.”
4. The team discusses it. Only after the team says “use this” does the Integrator copy the relevant conclusion into official ledgers/model/deck.

Read `TEAM-WORKFLOW.md` for the exact copy-paste Git commands.

## Chat, ideas, and official work

- A chat response or AI-generated Markdown is a draft by default; it does not change the case record automatically.
- Keep throwaway brainstorming in chat or your own `00-INBOX/<your-name>/` folder. `idea-backlog.csv` is optional; use it only for ideas the whole team must remember or decide later.
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
