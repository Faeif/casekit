# CaseKit in Obsidian

CaseKit works as a normal Obsidian vault. Markdown notes hold the brief, decisions, integration, and narrative; CSV files hold structured ledgers; Excel remains suitable for wider financial models and imported data.

## Recommended setup

1. Clone CaseKit and create a new workspace with `python3 casekit.py init ./my-case`.
2. Open `my-case` in Obsidian with **Open folder as vault**.
3. Keep the CaseKit repository and each competition workspace in Git separately. Do not initialise a Git repository in a parent folder that also contains unrelated personal files.
4. Use Obsidian to edit Markdown and CSV. Keep spreadsheets under `inputs/` and map only presentation-ready values into the metric tree.
5. Track every API, partner, CRM, payment, identity, or external-data dependency in `integration-contract.csv`. `Mocked` is acceptable for a demo when labelled honestly.

## Updating a number

For a direct assumption, edit the appropriate value in `02-assumptions.csv` or `03-metric-tree.csv`, then ask the AI to explain its downstream effect and run the finance/model validation.

For Excel-backed values:

```bash
python3 /path/to/casekit/casekit.py inspect-spreadsheet inputs/model.xlsx --output inputs/model-inspection.md
python3 /path/to/casekit/casekit.py sync-spreadsheet . data-import-map.json --apply --report outputs/spreadsheet-sync-report.json
python3 /path/to/casekit/casekit.py validate . --strict
```

Excel formula results are read from the workbook's last saved calculation cache. Recalculate and save in Excel before syncing; CaseKit will reject a mapped formula with no cached result rather than silently use an incorrect number.

## Safe collaboration

- Assign one owner for every `MET`, `ASM`, and `DEC`.
- Resolve merge conflicts in ledger rows before deck work resumes.
- Preserve IDs; supersede a value instead of silently reusing an ID for a different definition.
- Commit at decision locks, and attach raw research or interview notes under `inputs/`.
