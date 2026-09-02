# Project: CaseKit Open Source (Sprints 1-3) Full Multi-Agent Implementation

## Architecture

CaseKit is an open-source, evidence-led Venture & Hackathon Operating System adhering to the Agent Skills open standard (`https://agentskills.io/specification`). It coordinates multi-agent venture strategy, bottom-up financial modeling, pitch rendering, adversarial evaluation, and live prototyping.

```
                    ┌─────────────────────────┐
                    │       CaseKit CLI       │
                    │      (casekit.py)       │
                    └────────────┬────────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐            ┌──────────────┐
│  Sprint 1    │          │  Sprint 2    │            │  Sprint 3    │
│  Financial   │          │ Deep Research│            │ Master Deck  │
│  Models &    │          │ Progressive  │            │ 4-Judge Sim  │
│  YC Coach &  │          │ CLI & MCP    │            │ Prototype    │
│  Obsidian    │          │ Server       │            │ Case Vaults  │
└──────────────┘          └──────────────┘            └──────────────┘
     │                           │                           │
     └───────────────────────────┼───────────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │    Integrity Engine     │
                    │  (scripts/audit_case.py │
                    │   validate_suite.py)    │
                    └─────────────────────────┘
```

---

## Feature Inventory

| # | Feature | Description | Milestone | Source | Status |
|---|---|---|---|---|---|
| F01 | Baseline Bug Fix | Fix `KeyError: 'workstream'` in `skills/casekit-validator/scripts/audit_case.py` (line 346) and sync `VERSION` to `1.1.0`. | M1 | Survey | DONE |
| F02 | 5 Multi-Tab Financial Models | Create `b2b-saas.xlsx`, `marketplace.xlsx`, `hardware-iot.xlsx`, `d2c-retail.xlsx`, and `corporate-roi.xlsx` in `templates/financial-models/` with 4 standardized tabs (`01_Assumptions`, `02_Unit_Economics`, `03_Three_Statements`, `04_Sensitivities`). | M1 | R1 | DONE |
| F03 | Cap Table & Dilution Engine | Incorporate Founder Equity, 10-15% ESOP pool, and YC Post-Money SAFE note calculator into financial models. | M1 | R1 | DONE |
| F04 | Spreadsheet Sync & Named Ranges | Upgrade `skills/casekit-finance/scripts/spreadsheet_sync.py` and `casekit.py` to auto-discover Named Ranges and run CFO sanity checks (margin alerts, cash runway, payback period). | M1 | R1 | DONE |
| F05 | Socratic YC & Founder AI Coach Skill | Implement `skills/casekit-yc-coach/` (`SKILL.md`, `agents/openai.yaml`, `references/five-level-funnel.md`, `references/socratic-coaching-guide.md`) with 4 Pillars & 5-Level Funnel and auto-ledger updates. Register in `casekit.json`. | M1 | R2 | DONE |
| F06 | Obsidian No-Code Starter Pack | Create `templates/obsidian-config/.obsidian/community-plugins.json` and `templates/obsidian-config/00-DASHBOARD.md` with Dataview query tables. | M1 | R3 | DONE |
| F07 | Obsidian Auto-Scaffolding & Guide | Upgrade `casekit.py init` to automatically copy `.obsidian` configurations into initialized vaults, and update `OBSIDIAN.md` with 1-click plugin setup & Obsidian Git guide. | M1 | R3 | DONE |
| F08 | Primary Source Evidence Hierarchy | Update `skills/casekit-research/SKILL.md` to enforce the 4-Tier Evidence Hierarchy (SEC/regulatory > academic > central bank > triangulated). | M2 | R4 | IN_PROGRESS |
| F09 | Rule of 3 Triangulation & Post-Mortem | Update `skills/casekit-research/references/competitor-intelligence.md` and `skills/casekit-validator/scripts/audit_case.py` to validate 3-source triangulation and competitor post-mortem autopsies. | M2 | R4 | IN_PROGRESS |
| F10 | Auto-Archival Evidence Snapshots | Add URL snapshot and caching logic under `01-INPUTS/archive/` in `casekit-research` and `casekit.py`. | M2 | R4 | IN_PROGRESS |
| F11 | Progressive CLI Presets | Upgrade `casekit.py init` to support `--preset hackathon-sprint`, `--preset corporate-launchpad`, and `--preset full-deep-drill`. | M2 | R5 | IN_PROGRESS |
| F12 | Interactive CLI Helpers | Add CLI commands `casekit add claim`, `casekit add assumption`, `casekit add decision`, and `casekit check`. | M2 | R5 | IN_PROGRESS |
| F13 | CaseKit MCP Server Wrapper | Implement `scripts/casekit_mcp_server.py` exposing core CaseKit operations via Model Context Protocol JSON-RPC 2.0 stdio. | M2 | R5 | IN_PROGRESS |
| F14 | Master Presentation Polish | Upgrade `skills/casekit-deck/scripts/render_deck.py` with 16:9 widescreen layout, card hierarchy, stat banners, and clean typography. | M3 | R6 | DONE |
| F15 | 4-Judge Rehearsal Simulator | Create `skills/casekit-pitch/references/rehearsal-simulator.md` simulating Skeptical CFO, Deep-Tech CTO, Corporate BU Head, and YC Partner 3-minute rapid-fire drills. | M3 | R6 | DONE |
| F16 | Pitch Timing & Word-Count Enforcer | Implement 130-150 WPM pitch timing validation in `skills/casekit-pitch/`. | M3 | R6 | DONE |
| F17 | Standalone Minimalist HTML Prototype | Implement high-craft minimalist interactive prototype generator (`scripts/generate_prototype.py` and CLI integration `casekit prototype`) with clean typography, responsive layout, dark/light toggle, and zero AI-slop tropes. | M3 | R6 | DONE |
| F18 | Famous Case Study Vaults | Create `examples/airbnb-2008-pitch/` and `examples/stripe-developer-wedge/` with full valid cross-referenced ledgers and deck specs. | M3 | R6 | DONE |
| F19 | GitHub Actions PR Audit Workflow | Create `.github/workflows/casekit-audit.yml` for automated CI pull request validation. | M3 | R6 | DONE |
| F20 | E2E Test Suite & Full Suite Pass | Upgrade `scripts/validate_suite.py` to test all new templates, skills, presets, models, CLI helpers, MCP server, and prototypes, ensuring 100% pass rate. | M4 | Acceptance | IN_PROGRESS |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Sprint 1 Core: Financial Models, YC Coach, Obsidian Starter Pack | F01, F02, F03, F04, F05, F06, F07 | None | DONE |
| M2 | Sprint 2 Core: Deep Research, Progressive CLI Presets & MCP Server | F08, F09, F10, F11, F12, F13 | M1 | DONE |
| M3 | Sprint 3 Core: Presentation Polish, 4-Judge Sim, Live Prototype, Case Vaults & CI | F14, F15, F16, F17, F18, F19 | M1, M2 | DONE |
| M4 | Final E2E Test Suite Verification & Adversarial Coverage Hardening | F20 (100% test pass on `validate_suite.py`, `doctor --strict`, `validate test_sprint --strict`) | M1, M2, M3 | IN_PROGRESS |

---

## Interface Contracts

### 1. Financial Models & Named Ranges
- Standard Tabs: `01_Assumptions`, `02_Unit_Economics`, `03_Three_Statements`, `04_Sensitivities`.
- Standard Named Ranges:
  - `Revenue_Year1`, `Revenue_Year2`, `Revenue_Year3`, `Revenue_Year4`, `Revenue_Year5`
  - `Gross_Margin_Pct`, `CAC_Blended`, `LTV_Cohort`, `CAC_Payback_Months`, `Cash_Runway_Months`
  - `SAFE_Post_Money_Valuation`, `SAFE_Investment_Amount`, `Founder_Dilution_Pct`, `ESOP_Pool_Pct`
- CFO Sanity Checks in `spreadsheet_sync.py`:
  - Margin Floor: Warning if `Gross_Margin_Pct < 0.40` (SaaS/Platform) or `< 0.15` (Retail/Hardware).
  - Runway Alert: Critical Warning if `Cash_Runway_Months < 6.0`.
  - Payback Horizon: Warning if `CAC_Payback_Months > 18.0`.

### 2. Socratic YC Coach Skill (`skills/casekit-yc-coach/`)
- `SKILL.md`: Frontmatter `name: casekit-yc-coach`, description <= 1024 chars, <= 500 lines.
- `agents/openai.yaml`: Standard agent configuration.
- Persona: 1-2 sharp Socratic questions, pre-computed options prefixed with `(Recommended)`.
- Core Frameworks: 4 Pillars & 5-Level Funnel, strict Economic Buyer vs End User separation, WTP Matrix.

### 3. Progressive CLI Scaffolding (`casekit.py`)
- `casekit.py init <dest> [--preset <hackathon-sprint|corporate-launchpad|full-deep-drill>]`
  - `hackathon-sprint`: 4 core files (`00-case-profile.md`, `01-evidence-ledger.csv`, `02-assumptions.csv`, `12-deck-spec.json`) + `.obsidian/`.
  - `corporate-launchpad`: Sprint core + `03-metric-tree.csv`, `04-decision-log.csv`, `05-risk-register.csv`, `qna-bank.csv`, `option-portfolio.csv`, `integration-contract.csv`, `engineering/architecture.md`, `engineering/nfr-slo.md`, `engineering/threat-model.md`.
  - `full-deep-drill`: Complete 36+ files and folders.
- Helpers:
  - `casekit.py add claim <project_dir> --text "..." --source "..." --tier <1-4>`
  - `casekit.py add assumption <project_dir> --name "..." --low <num> --base <num> --high <num> --unit "..."`
  - `casekit.py add decision <project_dir> --title "..." --status "<proposed|accepted|rejected>"`
  - `casekit.py check <project_dir>` (runs lightweight audit and doctor checks).

### 4. CaseKit MCP Server (`scripts/casekit_mcp_server.py`)
- Standard stdio JSON-RPC 2.0 MCP server exposing:
  - `init_project(dest, preset)`
  - `audit_case(project_dir, strict)`
  - `sync_spreadsheet(project_dir, excel_file, apply)`
  - `render_deck(project_dir, output_path)`
  - `generate_prototype(project_dir, output_path)`
  - `add_claim(project_dir, text, source, tier)`
  - `add_assumption(project_dir, name, low, base, high, unit)`
  - `add_decision(project_dir, title, status)`
  - `doctor(strict)`
  - `score_rubric(project_dir)`

### 5. Interactive HTML Prototype Generator (`scripts/generate_prototype.py`)
- Standalone HTML5 single-file output with embedded Tailwind CSS, Inter/system font typography, light/dark mode switch, responsive sidebar/header navigation, interactive tabs (Overview, Live Metrics, Financial Scenarios, Architecture, Rehearsal Q&A), zero external unpkg script dependencies that could break offline, zero AI-slop visual tropes.

---

## Code Layout & File Boundaries

| Subdirectory / File | Exclusive Owner | Purpose |
|---|---|---|
| `templates/financial-models/` | M1 Worker | 5 Excel financial models |
| `templates/obsidian-config/` | M1 Worker | Obsidian configuration & dashboard |
| `skills/casekit-yc-coach/` | M1 Worker | Socratic YC Coach skill & references |
| `skills/casekit-finance/scripts/spreadsheet_sync.py` | M1 Worker | Spreadsheet sync & CFO sanity checks |
| `skills/casekit-validator/scripts/audit_case.py` | M1 Worker (Fix) / M2 Worker (Ext) | Case integrity audit engine |
| `skills/casekit-research/` | M2 Worker | Research skill, evidence hierarchy, references |
| `casekit.py` | M1 (init/obsidian) -> M2 (presets/add/check) -> M3 (prototype CLI) | Main CLI entry point |
| `scripts/casekit_mcp_server.py` | M2 Worker | MCP Server implementation |
| `skills/casekit-deck/scripts/render_deck.py` | M3 Worker | PowerPoint 16:9 renderer |
| `skills/casekit-pitch/` | M3 Worker | Rehearsal simulator & pitch enforcer |
| `scripts/generate_prototype.py` | M3 Worker | Interactive HTML/Tailwind generator |
| `examples/airbnb-2008-pitch/` | M3 Worker | Airbnb 2008 pitch case study |
| `examples/stripe-developer-wedge/` | M3 Worker | Stripe developer wedge case study |
| `.github/workflows/casekit-audit.yml` | M3 Worker | GitHub Actions PR audit workflow |
| `scripts/validate_suite.py` | E2E Testing Track / M4 Worker | Test harness and acceptance verification |
| `OBSIDIAN.md` | M1 Worker | Obsidian setup documentation |
| `casekit.json` & `VERSION` | M1 / M4 Worker | Manifest registration and version sync |

---
