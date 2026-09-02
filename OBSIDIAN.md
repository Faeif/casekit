# CaseKit in Obsidian — No-Code GUI & Team Workspace Guide

CaseKit works natively as an Obsidian vault, providing a high-performance visual cockpit for venture design, hackathons, and enterprise strategy. Markdown files maintain narrative strategy and decisions; CSV files serve as structured evidence and assumption ledgers; and Excel spreadsheets power bottom-up financial models.

---

## 1. 1-Click Vault Setup & Community Plugins

Every new CaseKit workspace created via `casekit.py init` automatically includes pre-configured `.obsidian` settings with essential community plugins.

### Quick Start:
1. Initialize your workspace:
   ```bash
   python3 casekit.py init ./my-startup-vault
   ```
2. Download and launch **Obsidian** ([obsidian.md](https://obsidian.md)).
3. Click **Open folder as vault** and select `./my-startup-vault`.
4. When prompted by Obsidian, click **Turn on community plugins**.

### Pre-Configured Community Plugins:
- **Edit CSV (`edit-csv`)**: Interactive Excel-like spreadsheet editor embedded directly inside Obsidian for editing CSV ledgers without quotation-mark corruption.
- **Dataview (`dataview`)**: Real-time dynamic querying and summary tables for project progress.
- **Obsidian Git (`obsidian-git`)**: Automated background Git backup and push/pull synchronization for effortless team collaboration.
- **Advanced Tables (`table-editor-markdown`)**: Clean auto-formatting and keyboard navigation (`Tab`, `Enter`) for standard Markdown tables.
- **Excalidraw (`obsidian-excalidraw-plugin`)**: Infinite canvas for architecture diagrams, wireframes, and customer journey maps.
- **Advanced Slides (`obsidian-advanced-slides`)**: Live Markdown slide deck rendering directly in Obsidian.

---

## 2. Real-Time Dashboard (`00-DASHBOARD.md`)

Opening `00-DASHBOARD.md` inside Obsidian gives you an executive cockpit powered by **Dataview**:
- **🎯 Case Overview & 5-Level Funnel**: Displays case type, stage, beachhead ICP, and last modified timestamps.
- **🧪 Active Assumptions**: Filterable table of all `ASM-xxx` entries ranked by sensitivity.
- **🔍 Evidence Ledger**: Real-time triangulation status and source quality ratings for all `CLM-xxx` claims.
- **⚠️ Risk Register**: Matrix of identified business and technical risks ranked by severity.
- **📑 Pitch Deck Progress**: Slide-by-slide completion status and owner assignments.

---

## 3. No-Code Tabular Ledger Editing with Edit CSV

Non-developer teammates can edit structured ledgers without touching terminal commands:
1. In the Obsidian file tree, right-click any ledger (e.g. `02-assumptions.csv`, `01-evidence-ledger.csv`, `05-risk-register.csv`).
2. Select **Open as CSV Table**.
3. Add rows, edit Low/Base/High values, sort by sensitivity, or filter by owner in an intuitive spreadsheet grid.
4. Press `Cmd + S` (or `Ctrl + S`) to save cleanly formatted CSV.

---

## 4. 1-Click Team Cloud Sync with Obsidian Git

Collaborate with teammates without running command-line Git:
1. Open the Obsidian Command Palette (`Cmd + P` on macOS or `Ctrl + P` on Windows/Linux).
2. Type `Git: Open Source Control View` to see all modified ledgers and notes.
3. To sync changes:
   - Click **Backup / Commit and Push** to upload your work to the team repository.
   - Click **Pull** to fetch teammates' latest numbers and decisions.
4. **Auto-Backup**: Configure automatic background saves every 10-15 minutes in **Settings -> Community Plugins -> Obsidian Git -> Auto Backup**.

---

## 5. Visual System Architecture & Wireframing with Excalidraw

1. In Obsidian, right-click any folder and select **New Excalidraw drawing**.
2. Sketch system block diagrams, user flowcharts, or pitch deck visuals on the infinite vector canvas.
3. Embed drawings into strategy notes or pitch deck slides using standard WikiLinks: `![[architecture-diagram]]`.

---

## 6. Financial Model Spreadsheet Synchronization

CaseKit includes 5 production-grade multi-tab Excel models in `templates/financial-models/` (`b2b-saas.xlsx`, `marketplace.xlsx`, `hardware-iot.xlsx`, `d2c-retail.xlsx`, `corporate-roi.xlsx`).

To inspect or synchronize numbers into your case workspace:

```bash
# Inspect defined Named Ranges and run CFO sanity checks
python3 casekit.py inspect-spreadsheet inputs/b2b-saas.xlsx

# Sync mapped Named Ranges into 03-metric-tree.csv
python3 casekit.py sync-spreadsheet . data-import-map.json --apply

# Validate case integrity before deck freeze
python3 casekit.py validate . --strict
```

---

## 7. Safe Team Collaboration Protocols

- **Owner Attribution**: Every Metric (`MET`), Assumption (`ASM`), Decision (`DEC`), and Risk (`RSK`) must have a clear owner.
- **Immutable Historical Records**: Never reuse or delete an ID. If an assumption changes, supersede the value or record a new decision in `04-decision-log.csv`.
- **Integrity Validation**: Always run `python3 casekit.py validate . --strict` prior to final deck freeze and rendering.
