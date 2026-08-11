---
name: casekit-deck
description: Design and render editable, evidence-linked pitch decks for case competitions, hackathons, innovation challenges, and executive proposals. Use when converting an approved narrative and CaseKit ledgers into slide architecture, charts, diagrams, source footers, speaker notes, appendix slides, PowerPoint output, PDF-first Typst output, or visual QA.
---

# CaseKit Deck

Translate the approved argument into a visual decision document. Preserve the shared numbers and evidence IDs; do not invent content to fill a layout.

## Workflow

1. Validate the project with `casekit-validator`. Stop on unresolved blocker findings.
2. Build `12-deck-spec.json` from the approved thesis and storyboard. Treat this JSON as the canonical intermediate representation.
3. Select slide archetypes from `references/slide-system.md`; choose the visual that exposes the reasoning most directly.
4. Render editable PowerPoint with:

   ```bash
   python3 scripts/render_deck.py 12-deck-spec.json submission.pptx
   ```

5. Inspect every slide at presentation size. Check clipping, contrast, hierarchy, chart scales, source markers, number consistency, and Thai/English font fallback.
6. Export PDF only after the editable deck passes QA. Read `references/renderers.md` when selecting PptxGenJS, Typst/Touying, Marp, or Quarto.

Use `assets/deck-spec.example.json` as the schema example. The renderer requires `python-pptx` 1.x; install the repository's `requirements.txt` when it is not already available.

## Design constraints

- One slide has one decision job and one conclusion headline.
- Use assertion–evidence structure: conclusion first, proof second.
- Label every number as actual, forecast, target, benchmark, or assumption.
- Put `CLM`, `SRC`, `ASM`, and `MET` markers in the slide footer or speaker notes.
- Prefer direct labels to legends, consistent scales to dramatic scales, and rounded values to false precision.
- Use a table only when exact lookup matters; use a chart when comparison or change matters; use a flow when causality or sequence matters.
- Reserve appendix slides for methodology, source detail, model inputs, alternatives, and Q&A—not unsupported overflow.
- Never shrink body text to rescue an overloaded slide. Split the claim.

## Required deck package

Produce the editable deck, PDF when requested, deck spec, source map, speaker notes, appendix, demo fallback, and a slide QA report. Report any missing fonts, renderer limitations, or assets that require manual replacement.
