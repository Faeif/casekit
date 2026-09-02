# CaseKit Test Ready & Verification Matrix

**Document Version:** 1.0.0  
**Target System:** CaseKit Open Source (Sprints 1–3, Features F01–F20)  
**Track:** E2E Testing Track (Sub-Orchestrator & QA Specialist)  
**Date:** 2026-09-02  
**Status:** **TEST INFRASTRUCTURE & SUITES READY (223 Modular Tests)**  

---

## 1. Executive Summary

The complete end-to-end test infrastructure for CaseKit has been architected, implemented, and verified across all 20 features (F01–F20) spanning Sprints 1 to 3.

- **Total Test Cases**: **223 automated test cases**
  - **Tier 1 (Feature Coverage)**: 100 tests (5 per feature across F01–F20)
  - **Tier 2 (Boundary & Corner Cases)**: 100 tests (5 per feature across F01–F20)
  - **Tier 3 (Cross-Feature Combinations)**: 15 integration test suites
  - **Tier 4 (Real-World Application Scenarios)**: 8 end-to-end venture/hackathon scenarios
- **Test Infrastructure Specification**: `/Users/phanlopth/casekit/TEST_INFRA.md`
- **Central Test Runner**: `scripts/validate_suite.py`
- **Modular Test Packages**: `tests/test_tier1_features.py`, `tests/test_tier2_boundaries.py`, `tests/test_tier3_combinations.py`, `tests/test_tier4_scenarios.py`, `tests/test_helpers.py`

---

## 2. Test Suite Architecture & Coverage Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CASEKIT TEST INFRASTRUCTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Tier 1: Feature Coverage (100 Tests)                                       │
│  • F01: 5 tests  • F02: 5 tests  • F03: 5 tests  • F04: 5 tests  • F05: 5   │
│  • F06: 5 tests  • F07: 5 tests  • F08: 5 tests  • F09: 5 tests  • F10: 5   │
│  • F11: 5 tests  • F12: 5 tests  • F13: 5 tests  • F14: 5 tests  • F15: 5   │
│  • F16: 5 tests  • F17: 5 tests  • F18: 5 tests  • F19: 5 tests  • F20: 5   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Tier 2: Boundary & Corner Cases (100 Tests)                                │
│  • F01: 5 tests  • F02: 5 tests  • F03: 5 tests  • F04: 5 tests  • F05: 5   │
│  • F06: 5 tests  • F07: 5 tests  • F08: 5 tests  • F09: 5 tests  • F10: 5   │
│  • F11: 5 tests  • F12: 5 tests  • F13: 5 tests  • F14: 5 tests  • F15: 5   │
│  • F16: 5 tests  • F17: 5 tests  • F18: 5 tests  • F19: 5 tests  • F20: 5   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Tier 3: Cross-Feature Combinations (15 Integration Suites)                 │
│  • INT-01: Spreadsheet Sync -> Metric Tree -> CFO Sanity Checks             │
│  • INT-02: Metric Tree -> Deck Spec Number Binding -> PPTX Render           │
│  • INT-03: CLI Scaffolding -> Obsidian GUI Configuration                    │
│  • INT-04: Sprint Scaffolding -> Data Addition -> Strict Audit              │
│  • INT-05: Research Ingestion -> Offline SHA-256 Archive -> Source Check    │
│  • INT-06: Strategy Option Scoring -> Rubric Scorecard                      │
│  • INT-07: Integration Contract (mock/real) -> PDPA Consent -> Audit Gate   │
│  • INT-08: CFO Operating Plan -> Cash Reconciliation -> Variance Tracking   │
│  • INT-09: Unit Economics -> Deck Spec KPI Cards                            │
│  • INT-10: install.py -> Multi-Client Native Discovery Paths                │
│  • INT-11: 3-Tier Clean Team Layout (01-INPUTS, 02-TEAM, 03-OFFICIAL)       │
│  • INT-12: Presentation Renderer with Custom Theme Palettes                 │
│  • INT-13: Model Router Multi-Archetype Forecaster                          │
│  • INT-14: Sensitivity Ranking Driver Tornado Matrix                        │
│  • INT-15: Model Context Protocol (MCP) JSON-RPC Cross-Tool Orchestration   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Tier 4: Real-World Application Scenarios (8 Full Scenarios)                │
│  • Scenario 1: Rapid 24-Hour Hackathon Sprint End-to-End Workflow           │
│  • Scenario 2: B2B SaaS Series A Dilution & Metrics Due Diligence           │
│  • Scenario 3: Two-Sided Marketplace Liquidity & Float Working Capital      │
│  • Scenario 4: Enterprise Corporate Launchpad & Synergy Transformation      │
│  • Scenario 5: Asset-Light Hardware & IoT Production Lifecycle              │
│  • Scenario 6: D2C Retail Cohort Retention & Contribution Margin            │
│  • Scenario 7: YC Demo Day Pitch Rehearsal & 130-150 WPM Timing Defense     │
│  • Scenario 8: Canonical Historical Case Study Replay & Integrity Audit     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Feature Verification Matrix (F01–F20)

| Feature # | Feature Name | Milestone | Tier 1 Tests | Tier 2 Tests | Tier 3 Integration | Tier 4 Scenario | Status |
|---|---|---|---|---|---|---|---|
| **F01** | Baseline Bug Fix & Version Sync | M1 | 5 | 5 | INT-04 | Scenario 8 | **READY** |
| **F02** | 5 Multi-Tab Financial Models | M1 | 5 | 5 | INT-01 | Scenario 2, 3, 5, 6 | **READY** |
| **F03** | Cap Table & Dilution Engine | M1 | 5 | 5 | INT-01 | Scenario 2 | **READY** |
| **F04** | Spreadsheet Sync & Named Ranges | M1 | 5 | 5 | INT-01, INT-02 | Scenario 2 | **READY** |
| **F05** | Socratic YC & Founder AI Coach | M1 | 5 | 5 | INT-07 | Scenario 7 | **READY** |
| **F06** | Obsidian No-Code Starter Pack | M1 | 5 | 5 | INT-03 | Scenario 1 | **READY** |
| **F07** | Obsidian Auto-Scaffolding & Guide | M1 | 5 | 5 | INT-03 | Scenario 1 | **READY** |
| **F08** | Primary Source Evidence Hierarchy | M2 | 5 | 5 | INT-05 | Scenario 1, 8 | **READY** |
| **F09** | Rule of 3 Triangulation & Post-Mortem | M2 | 5 | 5 | INT-05 | Scenario 8 | **READY** |
| **F10** | Auto-Archival Evidence Snapshots | M2 | 5 | 5 | INT-05 | Scenario 1 | **READY** |
| **F11** | Progressive CLI Presets | M2 | 5 | 5 | INT-03, INT-04 | Scenario 1, 4 | **READY** |
| **F12** | Interactive CLI Helpers | M2 | 5 | 5 | INT-04 | Scenario 1 | **READY** |
| **F13** | CaseKit MCP Server Wrapper | M2 | 5 | 5 | INT-15 | All Scenarios | **READY** |
| **F14** | Master Presentation Polish | M3 | 5 | 5 | INT-02, INT-12 | Scenario 1, 7 | **READY** |
| **F15** | 4-Judge Rehearsal Simulator | M3 | 5 | 5 | INT-07 | Scenario 4, 7 | **READY** |
| **F16** | Pitch Timing & Word-Count Enforcer | M3 | 5 | 5 | INT-07 | Scenario 7 | **READY** |
| **F17** | Standalone Minimalist HTML Prototype | M3 | 5 | 5 | INT-08 | Scenario 1 | **READY** |
| **F18** | Famous Case Study Vaults | M3 | 5 | 5 | INT-08 | Scenario 8 | **READY** |
| **F19** | GitHub Actions PR Audit Workflow | M3 | 5 | 5 | INT-10 | CI Pipeline | **READY** |
| **F20** | E2E Test Suite & Full Suite Pass | M4 | 5 | 5 | All Integrations | All Scenarios | **READY** |

---

## 4. How to Execute Tests

### Default Full Test Runner
```bash
python3 scripts/validate_suite.py
```

### Granular Tier Execution
```bash
# Run Tier 1: Feature Coverage (100 tests)
python3 scripts/validate_suite.py --tier 1

# Run Tier 2: Boundary & Corner Cases (100 tests)
python3 scripts/validate_suite.py --tier 2

# Run Tier 3: Cross-Feature Combinations (15 suites)
python3 scripts/validate_suite.py --tier 3

# Run Tier 4: Real-World Application Scenarios (8 scenarios)
python3 scripts/validate_suite.py --tier 4
```

### Granular Feature Execution
```bash
# Run all tests for a specific feature (e.g. F04 Spreadsheet Sync)
python3 scripts/validate_suite.py --feature F04

# Run all tests for F14 Deck Presentation
python3 scripts/validate_suite.py --feature F14
```

### Standard Python unittest Execution
```bash
# Discover and run all 223 tests with verbose logging
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## 5. Known Baseline Findings & Escalations

| ID | Location | Observation | Root Cause | Escalation Target |
|---|---|---|---|---|
| **BUG-01** | `skills/casekit-validator/scripts/audit_case.py:347` | `KeyError: 'workstream'` during `idea-backlog.csv` audit | `required_idea_fields` checks obsolete column name `workstream` instead of canonical schema | **M1 Worker / Bug Fix (F01)** |
| **DOC-01** | `VERSION` vs `casekit.json` | `VERSION` had `0.6.0`, `casekit.json` has `1.1.0` | Inconsistent version tracking file | **M1 Worker / Version Sync (F01)** |

---

## 6. Next Steps for Implementation Milestone Workers

1. **Milestone 1 (M1 Worker)**:
   - Patch `audit_case.py:347` to resolve `KeyError: 'workstream'`.
   - Implement `templates/financial-models/*.xlsx`, `skills/casekit-yc-coach/`, and `templates/obsidian-config/`.
   - Run `python3 scripts/validate_suite.py --tier 1 --feature F02` and `--feature F05` to verify.

2. **Milestone 2 (M2 Worker)**:
   - Upgrade `casekit.py` with presets (`--preset`) and CLI helpers (`add`, `check`).
   - Implement `scripts/casekit_mcp_server.py`.
   - Run `python3 scripts/validate_suite.py --tier 1 --feature F11` and `--feature F13` to verify.

3. **Milestone 3 (M3 Worker)**:
   - Enhance `render_deck.py` and `generate_prototype.py`.
   - Implement rehearsal simulator and case study vaults.
   - Run `python3 scripts/validate_suite.py --tier 4` to verify end-to-end scenarios.

4. **Milestone 4 (M4 Worker / Final Integration)**:
   - Execute `python3 scripts/validate_suite.py --smoke-only` and full test suite to guarantee 100% green pass.
