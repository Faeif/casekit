# CaseKit Test Infrastructure & 4-Tier Verification Framework

**Document Version:** 1.0.0  
**Target System:** CaseKit Open Source (Sprints 1–3, Features F01–F20)  
**Author:** suborch_e2e_testing (Lead Test Engineer / E2E Track)  
**Date:** 2026-09-02  
**Integrity Standard:** Agent Skills Specification (`https://agentskills.io/specification`)  

---

## 1. Architectural Overview & Test Strategy

CaseKit coordinates multi-agent venture strategy, bottom-up financial modeling, pitch rendering, adversarial evaluation, and live prototyping across diverse AI environments. The test infrastructure guarantees deterministic reliability, mathematical accuracy, referential integrity, and schema compliance across all 20 features (F01–F20).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CASEKIT TEST SUITE RUNNER                         │
│                    (scripts/validate_suite.py & tests/)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│     TIER 1       │          │     TIER 2       │          │     TIER 3       │
│ Feature Coverage │          │ Boundary & Corner│          │  Cross-Feature   │
│ (>=5 per feature)│          │ (>=5 per feature)│          │   Combinations   │
│ [100+ Tests]     │          │ [100+ Tests]     │          │ [15+ Workflows]  │
└──────────────────┘          └──────────────────┘          └──────────────────┘
         │                             │                             │
         └─────────────────────────────┼─────────────────────────────┘
                                       ▼
                              ┌──────────────────┐
                              │     TIER 4       │
                              │ Real-World E2E   │
                              │ Application Flow │
                              │ [8 Scenarios]    │
                              └──────────────────┘
```

---

## 2. The 4-Tier Test Matrix

| Tier | Name | Target Scope | Minimum Target Count | Primary Goal |
|---|---|---|---|---|
| **Tier 1** | **Feature Coverage** | Primary behavior, happy paths, schema contracts, file existence, and function outputs for F01–F20 | **>= 5 test cases per feature** (100+ test cases total) | Ensure all 20 features execute their core functional requirements without error |
| **Tier 2** | **Boundary & Corner Cases** | Edge cases, non-monotonic values, zero divisions, uncalculated formulas, search snippet rejections, invalid inputs | **>= 5 test cases per feature** (100+ test cases total) | Ensure graceful failure, informative error messages, and strict validation boundaries |
| **Tier 3** | **Cross-Feature Combinations** | Multi-module interactions (Spreadsheet Sync -> Metric Tree -> Deck Render -> Audit Gate; CLI Presets -> Obsidian -> Add Helpers -> Validator) | **>= 15 multi-module integration suites** | Verify data coherence across module boundaries and prevent multi-agent drift |
| **Tier 4** | **Real-World Application Scenarios** | Full end-to-end venture workflows (24h Hackathon, B2B SaaS Series A, Marketplace Liquidity, Enterprise ROI, YC Pitch Rehearsal, Airbnb/Stripe Case Studies) | **8 complete real-world scenarios** | Validate end-to-end user journeys under realistic high-stakes venture conditions |

---

## 3. Systematic Feature-by-Feature Test Specifications (F01–F20)

### F01: Baseline Bug Fix & Version Sync
- **Description**: Fix `KeyError: 'workstream'` in `skills/casekit-validator/scripts/audit_case.py` (line 347) and synchronize `VERSION` file to `1.1.0`.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f01_version_file_content`: Verify `/Users/phanlopth/casekit/VERSION` contains `1.1.0`.
  2. `test_f01_casekit_json_version_match`: Verify `casekit.json` version matches `VERSION` file (`1.1.0`).
  3. `test_f01_audit_case_idea_backlog_execution`: Verify `audit_case.py` executes against valid `idea-backlog.csv` without `KeyError`.
  4. `test_f01_audit_case_clean_exit`: Verify `audit_case.py` exits with code 0 on a valid fixture containing `idea-backlog.csv`.
  5. `test_f01_manifest_agent_skills_standard`: Verify `casekit.json` declares `"standard": "Agent Skills"`.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f01_b01_idea_backlog_missing_required_field`: Verify `audit_case.py` reports error when `title` is empty in `idea-backlog.csv`.
  2. `test_f01_b02_idea_backlog_extra_unexpected_columns`: Verify `audit_case.py` gracefully ignores extra optional metadata columns.
  3. `test_f01_b03_idea_backlog_empty_file`: Verify `audit_case.py` reports clean error on 0-byte `idea-backlog.csv`.
  4. `test_f01_b04_idea_backlog_accepted_for_case_without_decision`: Verify `audit_case.py` rejects `accepted-for-case` status when `decision_id` is missing.
  5. `test_f01_b05_version_file_trailing_newline_handling`: Verify version parser strips trailing newlines and whitespace safely.

---

### F02: 5 Multi-Tab Financial Models
- **Description**: Create 5 `.xlsx` workbooks (`b2b-saas.xlsx`, `marketplace.xlsx`, `hardware-iot.xlsx`, `d2c-retail.xlsx`, `corporate-roi.xlsx`) in `templates/financial-models/` with 4 standardized tabs.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f02_all_five_templates_exist`: Verify all 5 `.xlsx` files exist in `templates/financial-models/`.
  2. `test_f02_standard_tabs_presence`: Verify each workbook contains exactly `01_Assumptions`, `02_Unit_Economics`, `03_Three_Statements`, `04_Sensitivities`.
  3. `test_f02_b2b_saas_metrics_structure`: Verify `b2b-saas.xlsx` calculates MRR, ARR, NRR, GRR, and CAC Payback.
  4. `test_f02_marketplace_metrics_structure`: Verify `marketplace.xlsx` calculates GMV, Take Rate, and 2-sided CAC.
  5. `test_f02_corporate_roi_metrics_structure`: Verify `corporate-roi.xlsx` calculates NPV, IRR, and net annual labor savings.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f02_b01_xlsx_openpyxl_uncorrupted_load`: Verify `openpyxl.load_workbook` opens each template without XML corruption.
  2. `test_f02_b02_no_ref_errors_in_formulas`: Verify no cell in any template evaluates to `#REF!`, `#VALUE!`, or `#DIV/0!`.
  3. `test_f02_b03_churn_rate_bounds`: Verify SaaS template clamps churn rate between 0.0% and 100.0%.
  4. `test_f02_b04_negative_gross_margin_detection`: Verify unit economics detects and highlights negative gross margins.
  5. `test_f02_b05_hardware_scrap_rate_bounds`: Verify `hardware-iot.xlsx` handles 0% to 50% scrap rates monotonically.

---

### F03: Cap Table & Dilution Engine
- **Description**: Founder equity, 10–15% ESOP pool, YC Post-Money SAFE note calculator ($500k at $10M cap), and Series A dilution waterfall.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f03_safe_ownership_calculation`: Verify SAFE ownership equals `Investment / Post-Money Cap` (e.g. $500k / $10M = 5.0%).
  2. `test_f03_esop_pool_allocation`: Verify initial unallocated ESOP option pool is configured between 10.0% and 15.0%.
  3. `test_f03_founder_equity_split`: Verify founder shares account for 100% minus ESOP pool pre-financing.
  4. `test_f03_waterfall_totals_100_percent`: Verify sum of ownership across Founders, ESOP, SAFE, and Seed equals 100.0%.
  5. `test_f03_series_a_conversion_share_price`: Verify effective share price calculations during priced round conversions.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f03_b01_safe_investment_exceeds_cap`: Verify error when SAFE investment amount exceeds post-money valuation cap.
  2. `test_f03_b02_zero_founder_shares`: Verify rejection of 0 authorized founder shares.
  3. `test_f03_b03_unallocated_esop_depletion`: Verify behavior when option pool is exhausted (triggers pool refresh).
  4. `test_f03_b04_negative_valuation_rejection`: Verify rejection of negative or zero valuation caps.
  5. `test_f03_b05_ownership_rounding_precision`: Verify ownership precision sums to 1.0000 within floating point epsilon (1e-6).

---

### F04: Spreadsheet Sync & Named Ranges Engine
- **Description**: Auto-discover Named Ranges in `spreadsheet_sync.py` and `casekit.py` with real-time CFO sanity checks (margin alerts, cash runway, payback).
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f04_named_range_discovery`: Verify `spreadsheet_sync.py` discovers defined names from Excel workbooks.
  2. `test_f04_sync_named_range_to_metric_tree`: Verify mapped named range values update `03-metric-tree.csv` base scenario.
  3. `test_f04_inspect_spreadsheet_output`: Verify `casekit inspect-spreadsheet` generates structured markdown summary.
  4. `test_f04_cfo_sanity_check_margin_pass`: Verify CFO sanity check passes when gross margin >= 40%.
  5. `test_f04_cfo_sanity_check_runway_alert`: Verify CFO sanity check emits warning when cash runway < 6 months.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f04_b01_uncalculated_formula_rejection`: Verify sync halts when Excel formula cell lacks cached evaluation.
  2. `test_f04_b02_nonexistent_named_range`: Verify `ValueError` with list of available names when named range is not found.
  3. `test_f04_b03_multi_cell_named_range_handling`: Verify handling or explicit error for multi-cell defined ranges.
  4. `test_f04_b04_non_numeric_cell_value`: Verify error when mapped cell contains string text instead of a number.
  5. `test_f04_b05_cfo_payback_exceeds_horizon`: Verify warning when CAC payback exceeds 18 months or is unreachable.

---

### F05: Socratic YC & Founder AI Coach Skill
- **Description**: `skills/casekit-yc-coach/` with `SKILL.md`, `agents/openai.yaml`, references, 4 Pillars & 5-Level Funnel, auto ledger updates, `casekit.json` registration.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f05_skill_directory_and_manifest`: Verify `casekit-yc-coach` exists and is registered in `casekit.json`.
  2. `test_f05_skill_frontmatter_compliance`: Verify YAML frontmatter has `name: casekit-yc-coach` and description <= 1024 chars.
  3. `test_f05_skill_line_limit`: Verify `SKILL.md` is <= 500 lines with zero TODO placeholders.
  4. `test_f05_openai_agent_config`: Verify `agents/openai.yaml` exists and mentions `$casekit-yc-coach`.
  5. `test_f05_reference_guides_present`: Verify `references/five-level-funnel.md` and `references/socratic-coaching-guide.md` exist.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f05_b01_reject_top_down_market_size`: Verify Socratic coach prompt explicitly rejects top-down % market estimates.
  2. `test_f05_b02_enforce_economic_buyer_separation`: Verify framework enforces distinction between Economic Buyer and End User.
  3. `test_f05_b03_wtp_matrix_minimum_roi`: Verify WTP calculator rejects solutions with <5x customer value multiplier.
  4. `test_f05_b04_recommended_option_prefix`: Verify pre-computed choice prompts include `(Recommended)` tag.
  5. `test_f05_b05_no_provider_path_leakage`: Verify `SKILL.md` contains no `.codex/skills` or `.claude/skills` path leaks.

---

### F06: Obsidian No-Code Starter Pack
- **Description**: Pre-configured `templates/obsidian-config/.obsidian/community-plugins.json` with 6 plugins and `00-DASHBOARD.md` Dataview query tables.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f06_template_obsidian_directory_exists`: Verify `templates/obsidian-config/.obsidian/` exists.
  2. `test_f06_community_plugins_manifest`: Verify `community-plugins.json` lists Edit CSV, Dataview, Obsidian Git, Advanced Tables, Excalidraw, and Advanced Slides.
  3. `test_f06_dashboard_markdown_exists`: Verify `templates/obsidian-config/00-DASHBOARD.md` exists.
  4. `test_f06_dashboard_dataview_queries`: Verify `00-DASHBOARD.md` contains Dataview queries for Claims, Assumptions, and Risks.
  5. `test_f06_dashboard_deck_slides_table`: Verify `00-DASHBOARD.md` contains deck slide status overview table.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f06_b01_valid_json_community_plugins`: Verify `community-plugins.json` is valid parseable JSON array of strings.
  2. `test_f06_b02_empty_csv_dataview_fallback`: Verify `00-DASHBOARD.md` handles 0-row CSVs without JavaScript crashes.
  3. `test_f06_b03_safe_mode_fallback_callout`: Verify `00-DASHBOARD.md` provides instructions for users with Safe Mode active.
  4. `test_f06_b04_relative_links_integrity`: Verify links in `00-DASHBOARD.md` reference valid relative workspace files.
  5. `test_f06_b05_plugin_id_spelling`: Verify all plugin IDs match official Obsidian Community Plugin registry IDs exactly.

---

### F07: Obsidian Auto-Scaffolding & Guide
- **Description**: Upgrade `casekit.py init` to automatically copy `.obsidian/` into new vaults; update `OBSIDIAN.md` with 1-click plugin setup & Git guide.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f07_init_copies_obsidian_folder`: Verify `casekit init` writes `.obsidian/` into initialized project directory.
  2. `test_f07_init_copies_dashboard`: Verify `casekit init` copies `00-DASHBOARD.md` or `00-START-HERE.md`.
  3. `test_f07_obsidian_md_updated`: Verify `OBSIDIAN.md` contains 1-click setup instructions and Obsidian Git guide.
  4. `test_f07_clean_layout_preserves_obsidian`: Verify `--layout clean` preserves `.obsidian/` configuration.
  5. `test_f07_obsidian_git_step_by_step`: Verify `OBSIDIAN.md` explains git commit/push synchronization for non-technical users.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f07_b01_do_not_overwrite_existing_obsidian`: Verify `init` preserves user custom settings if `.obsidian/` already exists.
  2. `test_f07_b02_empty_destination_path`: Verify `init` handles relative paths and nested subdirectories cleanly.
  3. `test_f07_b03_obsidian_md_word_count`: Verify `OBSIDIAN.md` is comprehensive (>50 lines, detailed instructions).
  4. `test_f07_b04_windows_path_separators`: Verify path resolution works across POSIX and Windows path separators.
  5. `test_f07_b05_hidden_directory_permissions`: Verify initialized `.obsidian/` has appropriate read/write permissions.

---

### F08: Primary Source Evidence Hierarchy
- **Description**: Update `skills/casekit-research/SKILL.md` to enforce the 4-Tier Evidence Hierarchy (SEC/regulatory > academic > central bank > triangulated).
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f08_research_skill_exists`: Verify `skills/casekit-research/SKILL.md` exists and satisfies Agent Skills specs.
  2. `test_f08_source_policy_reference`: Verify `skills/casekit-research/references/source-policy.md` or `SKILL.md` defines the 4-tier hierarchy.
  3. `test_f08_tier_1_authoritative_sources`: Verify Tier 1 explicitly includes SEC 10-K, 56-1 One Report, and central bank data.
  4. `test_f08_tier_e_prohibited_sources`: Verify search engine snippets and raw ungrounded AI chatbot outputs are banned.
  5. `test_f08_check_sources_search_host_rejection`: Verify `check_sources.py` rejects search engine hostnames (e.g. `google.com/search`).
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f08_b01_malformed_url_rejection`: Verify `check_sources.py` flags invalid or non-HTTP URL schemas.
  2. `test_f08_b02_missing_publisher_or_date`: Verify evidence ledger audit flags missing publisher or publication year.
  3. `test_f08_b03_empty_evidence_ledger`: Verify validator handles 0-row evidence ledger with appropriate warning.
  4. `test_f08_b04_tier4_context_only_rule`: Verify Tier 4 media sources are disallowed as sole justification for North Star metrics.
  5. `test_f08_b05_online_mode_timeout_handling`: Verify `check_sources.py --online` handles connection timeouts gracefully without crashing.

---

### F09: Rule of 3 Triangulation & Post-Mortem
- **Description**: Update `competitor-intelligence.md` and `audit_case.py` to validate 3-source triangulation and competitor post-mortem autopsies.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f09_competitor_intelligence_reference`: Verify `skills/casekit-research/references/competitor-intelligence.md` exists.
  2. `test_f09_six_failure_traps_documented`: Verify documentation covers all 6 Fatal Failure Traps (Margin, Scaling, Distribution, Regulatory, Buyer vs User, CapEx).
  3. `test_f09_triangulation_protocol_definition`: Verify Rule of 3 triangulation protocol is documented with 3 independent legs.
  4. `test_f09_audit_case_rule_of_3_check`: Verify `audit_case.py` checks that North Star metrics reference >= 3 distinct source IDs.
  5. `test_f09_post_mortem_defense_in_case_profile`: Verify `00-case-profile.md` contains structural immunity defense against predecessor traps.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f09_b01_circular_citation_detection`: Verify validator rejects 3 claims that cite the same underlying source ID.
  2. `test_f09_b02_north_star_with_single_source`: Verify `audit_case.py` emits warning when outcome metric has only 1 source.
  3. `test_f09_b03_post_mortem_empty_mechanism`: Verify audit warning when competitor autopsy lacks root cause failure mechanism.
  4. `test_f09_b04_triangulation_mixed_valid_invalid_ids`: Verify handling when 2 source IDs exist and 1 is unresolved.
  5. `test_f09_b05_case_without_predecessor_defense`: Verify audit score reduction when pitch lacks "Why now / Why others failed" defense.

---

### F10: Auto-Archival Evidence Snapshots
- **Description**: Add URL text/PDF snapshot caching logic under `01-INPUTS/archive/` with SHA-256 hashes in `casekit-research` and `casekit.py`.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f10_archive_directory_structure`: Verify `01-INPUTS/archive/` (or `inputs/archive/`) is created by initialization.
  2. `test_f10_snapshot_filename_format`: Verify snapshot files follow `SRC-{id}_{slug}.md` naming convention.
  3. `test_f10_snapshot_frontmatter_sha256`: Verify archived snapshot contains `source_id`, `url`, and `content_hash_sha256`.
  4. `test_f10_pdf_text_extraction`: Verify `pypdf` extracts structured text from archived PDF documents.
  5. `test_f10_check_sources_archive_verification`: Verify `check_sources.py` validates matching snapshot hashes when present.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f10_b01_404_url_handling`: Verify archival engine records fetch failure without crashing CLI or workspace.
  2. `test_f10_b02_existing_snapshot_no_overwrite`: Verify existing snapshot is preserved unless `--force` is specified.
  3. `test_f10_b03_corrupted_pdf_handling`: Verify graceful fallback when PDF file is damaged or password-protected.
  4. `test_f10_b04_special_characters_in_slug`: Verify URL sanitization removes illegal filesystem characters (`/`, `?`, `&`, `:`).
  5. `test_f10_b05_offline_validation_mode`: Verify test suite operates fully offline without requiring live internet requests.

---

### F11: Progressive CLI Presets
- **Description**: Upgrade `casekit.py init` to support presets: `hackathon-sprint`, `corporate-launchpad`, `full-deep-drill`.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f11_preset_hackathon_sprint_init`: Verify `casekit init <dest> --preset hackathon-sprint` creates exactly 4 core files + `.obsidian/`.
  2. `test_f11_preset_corporate_launchpad_init`: Verify `casekit init <dest> --preset corporate-launchpad` creates core files + synergy matrix, architecture, Q&A bank.
  3. `test_f11_preset_full_deep_drill_init`: Verify `casekit init <dest> --preset full-deep-drill` creates complete 20+ file suite with 3-tier layout.
  4. `test_f11_status_reports_correct_preset`: Verify `casekit status` displays the active project preset.
  5. `test_f11_sprint_preset_passes_validation`: Verify `casekit validate <sprint_dest> --strict` passes without missing-file errors for optional files.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f11_b01_invalid_preset_name_rejection`: Verify `casekit init --preset invalid-preset` exits with code 1 and lists valid presets.
  2. `test_f11_b02_existing_directory_collision`: Verify `casekit init` refuses to overwrite non-empty target directory.
  3. `test_f11_b03_default_preset_fallback`: Verify `casekit init` without `--preset` defaults to standard full template or documented default.
  4. `test_f11_b04_sprint_preset_missing_core_file`: Verify validator detects if `12-deck-spec.json` is deleted from sprint preset.
  5. `test_f11_b05_preset_with_custom_team_members`: Verify `--preset full-deep-drill --team Alice,Bob` scaffolds team directories in `02-TEAM/`.

---

### F12: Interactive CLI Helpers
- **Description**: Add CLI commands `casekit add claim`, `casekit add assumption`, `casekit add decision`, and `casekit check`.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f12_add_claim_appends_row`: Verify `casekit add claim` appends validated row to `01-evidence-ledger.csv` with auto-incremented `CLM-xxx`.
  2. `test_f12_add_assumption_appends_row`: Verify `casekit add assumption` appends row to `02-assumptions.csv` with auto-incremented `ASM-xxx`.
  3. `test_f12_add_decision_appends_row`: Verify `casekit add decision` appends row to `04-decision-log.csv` with auto-incremented `DEC-xxx`.
  4. `test_f12_check_command_execution`: Verify `casekit check <dest>` runs diagnostics and prints health summary.
  5. `test_f12_check_command_exit_codes`: Verify `casekit check` exits with code 0 on healthy project and code 1 on broken project with `--strict`.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f12_b01_add_assumption_non_monotonic_rejection`: Verify `casekit add assumption` rejects inputs where `low > base` or `base > high`.
  2. `test_f12_b02_add_claim_missing_required_flags`: Verify `casekit add claim` exits with error when `--claim` or `--publisher` is missing.
  3. `test_f12_b03_add_decision_invalid_status`: Verify `casekit add decision` rejects unknown status values.
  4. `test_f12_b04_add_claim_search_engine_url`: Verify `casekit add claim` rejects Google/Bing search result URLs.
  5. `test_f12_b05_add_to_nonexistent_project`: Verify CLI helper prints clear error when target project path does not exist.

---

### F13: CaseKit MCP Server Wrapper
- **Description**: Implement `scripts/casekit_mcp_server.py` exposing core CaseKit operations via Model Context Protocol JSON-RPC 2.0 stdio.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f13_mcp_server_script_exists`: Verify `scripts/casekit_mcp_server.py` exists and is executable.
  2. `test_f13_mcp_tools_list`: Verify JSON-RPC `tools/list` returns the full registry of CaseKit tools (`status`, `validate`, `add_claim`, etc.).
  3. `test_f13_mcp_call_status_tool`: Verify JSON-RPC `tools/call` for `casekit_status` returns structured workspace health counts.
  4. `test_f13_mcp_call_validate_tool`: Verify JSON-RPC `tools/call` for `casekit_validate` returns error/warning summary.
  5. `test_f13_mcp_call_render_deck_tool`: Verify JSON-RPC `tools/call` for `casekit_render_deck` renders `.pptx` file.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f13_b01_mcp_invalid_json_rpc`: Verify server returns JSON-RPC error `-32700` (`Parse error`) on malformed JSON payload.
  2. `test_f13_b02_mcp_unknown_method`: Verify server returns JSON-RPC error `-32601` (`Method not found`) on unsupported methods.
  3. `test_f13_b03_mcp_missing_required_param`: Verify server returns JSON-RPC error `-32602` (`Invalid params`) when required arguments are missing.
  4. `test_f13_b04_mcp_invalid_project_path`: Verify tool call returns clear failure result when project path does not exist.
  5. `test_f13_b05_mcp_concurrent_tool_invocations`: Verify sequential processing of multiple JSON-RPC requests over stdio stream.

---

### F14: Master Presentation Polish
- **Description**: Upgrade `skills/casekit-deck/scripts/render_deck.py` with 16:9 widescreen layout (13.333"x7.5"), card hierarchy, stat banners, clean typography.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f14_widescreen_16_9_dimensions`: Verify output `.pptx` slide dimensions are 13.333 inches width × 7.500 inches height.
  2. `test_f14_render_all_slide_types`: Verify renderer handles `cover`, `metric`, `funnel`, `timeline`, `closing`, and card grid layouts.
  3. `test_f14_stat_banner_rendering`: Verify large stat text, metric label, and delta badge are positioned in card component.
  4. `test_f14_color_token_palette`: Verify slate/navy, blue, teal, amber, and red color token applications.
  5. `test_f14_pptx_zip_package_integrity`: Verify output `.pptx` is valid ZIP containing `ppt/presentation.xml` and slide XMLs.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f14_b01_missing_headline_in_slide`: Verify renderer exits with error and non-zero code when a slide lacks `headline`.
  2. `test_f14_b02_empty_slides_array`: Verify renderer rejects `12-deck-spec.json` with 0 slides.
  3. `test_f14_b03_special_characters_escaping`: Verify XML special characters (`<`, `>`, `&`, `"`, `'`) in headlines and bullets do not corrupt PPTX.
  4. `test_f14_b04_very_long_headline_handling`: Verify text box wrapping for headlines exceeding 100 characters.
  5. `test_f14_b05_missing_output_path_directory`: Verify renderer creates parent directories if target output directory does not exist.

---

### F15: 4-Judge Rehearsal Simulator
- **Description**: Create `skills/casekit-pitch/references/rehearsal-simulator.md` simulating Skeptical CFO, Deep-Tech CTO, Corporate BU Head, and YC Partner.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f15_rehearsal_simulator_doc_exists`: Verify `skills/casekit-pitch/references/rehearsal-simulator.md` exists.
  2. `test_f15_all_four_judge_personas`: Verify documentation defines Skeptical CFO, Deep-Tech CTO, Corporate BU Head, and YC Partner personas.
  3. `test_f15_four_move_response_formula`: Verify the 4-Move Response Protocol (Direct Answer, Evidence Anchor, Sensitivity Bound, Validated Action) is specified.
  4. `test_f15_rapid_fire_drill_protocols`: Verify 3-minute rapid fire drill questions are provided for each persona.
  5. `test_f15_scoring_rubric_integration`: Verify integration with `11-rubric-scorecard.csv` defense dimensions.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f15_b01_response_lacking_evidence_id`: Verify evaluation flags answers lacking specific `CLM-xxx` / `MET-xxx` citations.
  2. `test_f15_b02_unbounded_sensitivity_answer`: Verify evaluation flags answers that fail to acknowledge downside risks / low scenarios.
  3. `test_f15_b03_evasive_long_preamble`: Verify rejection of evasive answers exceeding 2 sentences before stating the direct metric.
  4. `test_f15_b04_persona_specific_trap_coverage`: Verify CFO drill covers working capital lag and CTO drill covers idempotency/PDPA.
  5. `test_f15_b05_no_handwaving_enforcement`: Verify simulator bans buzzwords ("AI-powered", "revolutionary") without underlying mechanics.

---

### F16: Pitch Timing & Word-Count Enforcer
- **Description**: Implement 130–150 WPM pitch timing validation in `skills/casekit-pitch/`.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f16_timing_budget_table`: Verify timing benchmarks for 1m, 2m, 3m, 5m, and 10m pitch variants.
  2. `test_f16_wpm_calculation`: Verify speech rate calculation: `WPM = (word_count / duration_minutes)`.
  3. `test_f16_valid_speech_rate_pass`: Verify pitch passing within 130–150 WPM receives pass status.
  4. `test_f16_slide_duration_allocation`: Verify slide-level time allocation sums to total pitch duration.
  5. `test_f16_speaker_notes_word_counting`: Verify speaker notes word extraction strips markdown syntax before counting.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f16_b01_excessive_wpm_warning`: Verify warning emitted when speaker notes exceed 150 WPM ceiling.
  2. `test_f16_b02_insufficient_wpm_warning`: Verify warning emitted when speaker notes drop below 120 WPM floor.
  3. `test_f16_b03_empty_speaker_notes`: Verify warning or handling when a slide has 0 words in speaker notes.
  4. `test_f16_b04_zero_duration_rejection`: Verify rejection of 0 or negative pitch duration parameter.
  5. `test_f16_b05_multilingual_word_count`: Verify handling of Thai/mixed-script speaker notes word segmentation.

---

### F17: Standalone Minimalist HTML Prototype
- **Description**: Implement high-craft minimalist interactive prototype generator (`scripts/generate_prototype.py` and `casekit prototype`) with clean typography and responsive layout.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f17_prototype_script_exists`: Verify `scripts/generate_prototype.py` exists and is executable.
  2. `test_f17_cli_prototype_subcommand`: Verify `casekit prototype <dest>` generates `prototype.html`.
  3. `test_f17_standalone_single_file_html`: Verify output is a single self-contained HTML file without external local assets.
  4. `test_f17_embedded_tailwind_and_typography`: Verify embedded Tailwind CSS and modern system typography (Inter/Geist).
  5. `test_f17_dark_light_mode_toggle`: Verify JavaScript dark/light mode toggle logic is embedded and functional.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f17_b01_zero_console_errors`: Verify HTML/JS contains no undefined variables or syntax errors.
  2. `test_f17_b02_empty_metric_tree_sanitization`: Verify generator handles empty or partial `03-metric-tree.csv` gracefully.
  3. `test_f17_b03_offline_capability`: Verify HTML prototype opens and functions in offline browser environment without internet.
  4. `test_f17_b04_no_ai_slop_tropes`: Verify absence of generic AI-slop visual tropes (floating purple gradients, spinning 3D spheres).
  5. `test_f17_b05_responsive_mobile_viewport`: Verify HTML contains `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.

---

### F18: Famous Case Study Vaults
- **Description**: Create `examples/airbnb-2008-pitch/` and `examples/stripe-developer-wedge/` with full valid cross-referenced ledgers and deck specs.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f18_airbnb_vault_exists`: Verify `examples/airbnb-2008-pitch/` exists with all required core ledgers.
  2. `test_f18_stripe_vault_exists`: Verify `examples/stripe-developer-wedge/` exists with all required core ledgers.
  3. `test_f18_airbnb_audit_passes_strict`: Verify `audit_case.py` passes with 0 errors on `examples/airbnb-2008-pitch/` in `--strict` mode.
  4. `test_f18_stripe_audit_passes_strict`: Verify `audit_case.py` passes with 0 errors on `examples/stripe-developer-wedge/` in `--strict` mode.
  5. `test_f18_case_vaults_render_deck`: Verify `render_deck.py` renders valid PowerPoint presentations from both example deck specs.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f18_b01_airbnb_historical_metrics`: Verify Airbnb metric tree reflects historical 2008 metrics ($84M TAM, 10.6M trips, $20-$25 avg fee).
  2. `test_f18_b02_stripe_7_lines_of_code`: Verify Stripe developer wedge integration contract details 7-lines-of-code API simplicity.
  3. `test_f18_b03_zero_number_drift_in_examples`: Verify deck specs in both example vaults match their respective metric tree base scenarios exactly.
  4. `test_f18_b04_all_source_urls_syntactically_valid`: Verify `check_sources.py` passes on all citations in both example vaults.
  5. `test_f18_b05_example_immutability_in_test_runs`: Verify test execution copies example vaults to temp directories to prevent accidental mutation.

---

### F19: GitHub Actions PR Audit Workflow
- **Description**: Create `.github/workflows/casekit-audit.yml` for automated CI pull request validation.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f19_workflow_file_exists`: Verify `.github/workflows/casekit-audit.yml` exists.
  2. `test_f19_valid_yaml_syntax`: Verify workflow file is valid parseable YAML.
  3. `test_f19_triggers_on_push_and_pr`: Verify workflow triggers on `push` and `pull_request` to `main` branch.
  4. `test_f19_runs_validate_suite`: Verify workflow executes `python3 scripts/validate_suite.py`.
  5. `test_f19_runs_doctor_strict`: Verify workflow executes `python3 casekit.py doctor --strict`.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f19_b01_python_version_matrix`: Verify workflow tests against Python 3.10+ (e.g. 3.10, 3.11, 3.12, 3.13).
  2. `test_f19_b02_dependency_installation_step`: Verify `pip install -r requirements.txt` step is present.
  3. `test_f19_b03_preset_initialization_verification`: Verify workflow tests initialization of all 3 presets.
  4. `test_f19_b04_example_vaults_validation`: Verify workflow validates all example vaults with `--strict`.
  5. `test_f19_b05_fail_fast_configuration`: Verify workflow configuration prevents masking of test failures.

---

### F20: E2E Test Suite & Full Suite Pass
- **Description**: Upgrade `scripts/validate_suite.py` to test all new templates, skills, presets, models, CLI helpers, MCP server, and prototypes, ensuring 100% pass rate.
- **Tier 1 (Feature Coverage >=5)**:
  1. `test_f20_validate_suite_executable`: Verify `python3 scripts/validate_suite.py` runs without uncaught exceptions.
  2. `test_f20_all_14_skills_validated`: Verify all 14 skills (including `casekit-yc-coach`) pass Agent Skills standard checks.
  3. `test_f20_doctor_strict_passes`: Verify `python3 casekit.py doctor --strict` reports 0 missing dependencies or broken paths.
  4. `test_f20_all_presets_init_and_validate`: Verify `init` and `validate --strict` pass across `hackathon-sprint`, `corporate-launchpad`, and `full-deep-drill`.
  5. `test_f20_zero_warnings_in_strict_audit`: Verify fixture and example audits pass with 0 errors and 0 warnings under `--strict`.
- **Tier 2 (Boundary & Corner Cases >=5)**:
  1. `test_f20_b01_exit_code_1_on_any_failure`: Verify test runner exits with code 1 if any test case in any tier fails.
  2. `test_f20_b02_clean_temporary_file_cleanup`: Verify temp directories and files created during tests are deleted after execution.
  3. `test_f20_b03_tier_selection_flag`: Verify test runner supports running specific tiers (e.g. `--tier 1`, `--tier 2`).
  4. `test_f20_b04_feature_selection_flag`: Verify test runner supports running specific features (e.g. `--feature F04`).
  5. `test_f20_b05_deterministic_execution`: Verify running the test suite multiple times consecutively produces identical pass/fail outcomes.

---

## 4. Tier 3: Cross-Feature Integration Contracts

Tier 3 verifies the interaction between disparate modules and ensures that data flows smoothly across the multi-agent pipeline:

| Integration ID | Features Involved | Interaction Pipeline | Expected Outcome |
|---|---|---|---|
| **INT-01** | F02, F04, F20 | `openpyxl` Financial Models -> Named Range Discovery -> `spreadsheet_sync.py` -> `03-metric-tree.csv` -> CFO Sanity Check | Mapped metrics update without formula loss; CFO checks pass or emit documented warnings |
| **INT-02** | F04, F14, F20 | Synced Metric Tree -> `12-deck-spec.json` Number Reconciliation -> `render_deck.py` -> `.pptx` Export | Number drift between model and slide deck is detected; PPTX renders matching numbers |
| **INT-03** | F11, F06, F07 | `casekit init --preset <preset>` -> `.obsidian/` Auto-Scaffolding -> `00-DASHBOARD.md` Dataview Query Validation | Initialized vault contains working Obsidian GUI starter pack without file permission errors |
| **INT-04** | F11, F12, F01 | `casekit init --preset hackathon-sprint` -> `casekit add claim/assumption/decision` -> `audit_case.py` Strict Audit | Appended records maintain valid regex IDs and monotonic bounds; audit passes cleanly |
| **INT-05** | F08, F09, F10 | `casekit-research` -> Evidence URL Ingestion -> `01-INPUTS/archive/` Hash Caching -> Rule of 3 Triangulation Check | Primary sources are classified by tier, archived offline with SHA-256 hashes, and triangulated |
| **INT-06** | F13, F11, F12, F17 | MCP Server stdio JSON-RPC -> `casekit_init` -> `casekit_add_claim` -> `casekit_sync_spreadsheet` -> `casekit_generate_prototype` | Full venture lifecycle managed end-to-end via Model Context Protocol tools |
| **INT-07** | F05, F15, F16 | `casekit-yc-coach` (4 Pillars & 5-Level Funnel) -> `casekit-pitch` (4-Judge Rehearsal & WPM Timing) -> Deck Storyboard | Coach-generated bottom-up metrics and ICP beachheads feed directly into 130–150 WPM pitch defense |
| **INT-08** | F17, F18, F20 | Historical Case Study Vaults (`airbnb`, `stripe`) -> `scripts/generate_prototype.py` -> HTML Prototype Validation | Prototypes generate cleanly from historical vaults with active metric sliders and scenario toggles |

---

## 5. Tier 4: Real-World End-to-End Application Scenarios

Tier 4 tests complete, realistic end-to-end user journeys representing typical high-stakes venture and hackathon use cases:

1. **Scenario 1 — Rapid 24-Hour Hackathon Sprint**:
   - Initialize workspace with `casekit init hackathon-demo --preset hackathon-sprint`.
   - Add 3 verified primary claims with `casekit add claim`.
   - Add 2 monotonic assumptions with `casekit add assumption`.
   - Run `casekit check hackathon-demo`.
   - Render slide deck with `casekit render hackathon-demo`.
   - Generate live interactive prototype with `casekit prototype hackathon-demo`.
   - Verify all artifacts exist, are valid, and pass `audit_case.py --strict`.

2. **Scenario 2 — B2B SaaS Series A Dilution & Metrics Due Diligence**:
   - Load `templates/financial-models/b2b-saas.xlsx`.
   - Verify MRR Bridge, NRR (>=100%), GRR (>=90%), and CAC Payback (<18 months).
   - Verify Cap Table post-SAFE ($500k at $10M cap) and Series A ($10M at $40M pre-money).
   - Sync metrics into `03-metric-tree.csv` via Named Ranges.
   - Run CFO sanity check and ensure zero cash insolvency over 60 months.

3. **Scenario 3 — Two-Sided Marketplace Liquidity & Float Economics**:
   - Load `templates/financial-models/marketplace.xlsx`.
   - Verify GMV, Take Rate (10-20%), and 2-Sided CAC payback.
   - Verify 7-14 day seller payout float cash flow balance.
   - Test sensitivity table for Take Rate vs AOV.

4. **Scenario 4 — Enterprise Corporate Launchpad & Synergy Transformation**:
   - Initialize workspace with `casekit init enterprise-case --preset corporate-launchpad`.
   - Populate `corporate-roi.xlsx` with labor savings and NPV/IRR.
   - Validate `integration-contract.csv` with mock/real systems and PDPA legal consent.
   - Run 4-Judge Rehearsal drill against Corporate BU Head persona.

5. **Scenario 5 — Asset-Light Hardware & IoT Production Lifecycle**:
   - Load `templates/financial-models/hardware-iot.xlsx`.
   - Verify BOM cost, scrap rate (6-12%), and hardware gross margin (>=20%).
   - Verify recurring IoT cloud subscription attachment (60-90%).
   - Verify working capital inventory trough 90 days before launch.

6. **Scenario 6 — D2C Retail Cohort Retention & Contribution Margin**:
   - Load `templates/financial-models/d2c-retail.xlsx`.
   - Verify AOV, blended CAC, return rate (5-15%), and 12-month cohort repeat curve.
   - Verify contribution margin 1 (first order) and LTV:CAC >= 3.0x.

7. **Scenario 7 — YC Demo Day Pitch Rehearsal & Timing Defense**:
   - Load `12-deck-spec.json` with 8 slides.
   - Verify total speaker notes word count is within 650–750 words (5 minutes @ 130–150 WPM).
   - Run simulated drill against Skeptical CFO and YC Partner personas.
   - Verify all 4 moves in the response formula are satisfied.

8. **Scenario 8 — Canonical Historical Case Study Replay**:
   - Execute strict audit and deck rendering on `examples/airbnb-2008-pitch/`.
   - Execute strict audit and deck rendering on `examples/stripe-developer-wedge/`.
   - Verify zero number drift and 100% referential integrity across all historical ledgers.

---

## 6. Test Runner Mechanics & Execution Commands

### Test Execution Commands

```bash
# 1. Run full package validation & all smoke tests (Default test runner)
python3 scripts/validate_suite.py

# 2. Run modular test suites via Python unittest
python3 -m unittest discover -s tests -p "test_*.py" -v

# 3. Run specific test tiers
python3 -m unittest tests/test_tier1_features.py -v
python3 -m unittest tests/test_tier2_boundaries.py -v
python3 -m unittest tests/test_tier3_combinations.py -v
python3 -m unittest tests/test_tier4_scenarios.py -v

# 4. Run tests for a specific feature (e.g. F04 Spreadsheet Sync)
python3 -m unittest tests.test_tier1_features.TestTier1Features.test_f04_named_range_discovery

# 5. Run CaseKit Doctor in strict mode
python3 casekit.py doctor --strict
```

### Test Isolation & Independence Rules
1. **Isolated Filesystem**: Every test that manipulates vaults or files MUST use `tempfile.TemporaryDirectory()`.
2. **Deterministic Outputs**: Test assertions compare against derived mathematical invariants and schema specifications.
3. **Clean Teardown**: No residual files or directories shall remain in `/tmp` or the repository after test completion.
4. **Offline First**: All test cases run completely offline with zero mandatory internet network requests.
