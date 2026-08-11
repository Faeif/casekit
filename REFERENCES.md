# References and design provenance

CaseKit combines established strategy, experimentation, finance, product, and communication practices into one controlled competition workflow. References are inspirations and methodology anchors, not evidence for a specific competition case. Case-specific facts must still be entered in the Evidence Ledger.

## Open-source workflow references

### gstack

- Repository: https://github.com/garrytan/gstack
- Used as inspiration for: premise interrogation, scope modes, explicit artifact handoffs, engineering-plan review, design review, report-only QA, and optional technical execution routing.
- CaseKit adaptation: compressed into competition gates and connected to Claim/Source/Assumption/Metric IDs. gstack remains an optional separately installed build-and-QA layer.

### startup-skill

- Repository: https://github.com/ferdinandobons/startup-skill
- Used as inspiration for: light/standard/deep research modes, research waves, competitor/pricing/customer-language research, customer interview gates, evidence-stage finance, positioning checks, validation experiments, kill criteria, and multi-duration pitches.
- CaseKit adaptation: routes findings into one shared ledger and prioritizes official judging criteria, fixed deadlines, prototype feasibility, and slide-level traceability.

## Framework references

- Jobs to Be Done: use to define progress sought, context, current alternative, and switching forces.
- April Dunford positioning: use competitive alternatives → unique attributes → customer value → best-fit customer → market category.
- Unit economics: use incremental revenue, contribution, CAC, retention/LTV, break-even, and sensitivity where relevant.
- Experiment design: use falsifiable hypotheses, leading indicators, guardrails, pass/iterate/stop thresholds, and precommitted kill criteria.
- Threat modeling and QA: use only when the prototype or proposal carries material security, privacy, safety, or operational risk.

## Presentation tooling references

- python-pptx: https://python-pptx.readthedocs.io/ — default editable PowerPoint renderer.
- Typst PDF export: https://typst.app/docs/reference/pdf/ — optional deterministic PDF-first workflow.
- Touying: https://typst.app/universe/package/touying/ — optional Typst presentation framework.
- Marp: https://marp.app/ — optional Markdown-to-slide emergency workflow.
- Quarto PowerPoint: https://quarto.org/docs/presentations/powerpoint/ — optional reproducible data-heavy presentation workflow.
- PptxGenJS: https://github.com/gitbrent/PptxGenJS — evaluated as an optional renderer but not installed by CaseKit. Re-run its current dependency audit before adoption; the 2026-08-11 review detected unresolved `image-size` advisories [GHSA-w3rx-r6r6-pgpr](https://github.com/advisories/GHSA-w3rx-r6r6-pgpr) and [GHSA-5p2g-fcmc-qvqq](https://github.com/advisories/GHSA-5p2g-fcmc-qvqq).

## Agent portability references

- Agent Skills specification: https://agentskills.io/specification
- OpenAI Codex skills: https://developers.openai.com/codex/skills/
- Claude Code skills: https://code.claude.com/docs/en/skills
- Gemini CLI Agent Skills: https://geminicli.com/docs/cli/skills/
- Google Antigravity skills: https://antigravity.google/docs/skills

## Finance boundary references

- IFRS 15 Revenue from Contracts with Customers: https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/ — authoritative accounting boundary for contract revenue and incremental contract-acquisition costs. CaseKit's CAC/LTV model is managerial decision analysis and does not replace accounting policy.

## Attribution policy

- Cite an upstream project when CaseKit documentation explicitly adapts a distinctive workflow pattern from it.
- Preserve license and copyright notices when copying or modifying upstream source code or substantial text.
- Prefer original wording and CaseKit-native schemas instead of copying prompts.
- Do not treat methodology references as market evidence in a competition submission.
