# Renderer selection

## Default: python-pptx

Use the bundled renderer when the team needs editable `.pptx`, native text/shapes, PowerPoint handoff, or rapid automated updates. CaseKit pins a tested python-pptx 1.x release in the repository.

## Optional: PptxGenJS

Use only after reviewing the current dependency audit. It is strong for native PowerPoint generation and slide masters, but CaseKit does not install it because the 2026-08-11 audit found unresolved high-severity denial-of-service advisories in its image parser dependency. Re-check before adoption and never process untrusted images through an affected parser.

## PDF-first: Typst + Touying

Use when typography, mathematical layout, version control, and deterministic PDF are more important than native PowerPoint editing. Keep the same deck spec and source map. Export a PDF and disclose that animation or editability may differ from PowerPoint.

## Emergency: Marp

Use when the team must draft and export rapidly from Markdown with a CSS theme. Expect more manual work for dense business diagrams.

## Data-heavy: Quarto

Use when reproducible analysis, code-generated charts, and tables dominate. It can produce PowerPoint, but the custom reference template and approved layouts must be tested before competition day.

Do not choose a renderer for novelty. Choose based on editability, export reliability, team skill, available runtime, Thai font support, and submission format.
