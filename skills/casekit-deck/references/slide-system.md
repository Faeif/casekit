# Slide system

## 16:9 Layout Templates

CaseKit renders widescreen 16:9 presentations (`13.333"` × `7.500"`) from `12-deck-spec.json` using standardized slide archetypes:

| Template Type | Layout Description | Best Used For |
|---|---|---|
| `cover` | Hero dark slate background, accent indicator, title, subhead, team badge | Presentation opening / title slide |
| `metric` | Left stat banner (40pt hero metric, comparison badge), right detail cards | Core revenue/unit economic proof points |
| `funnel` | Proportional width horizontal funnel bars with stage conversion rates | Acquisition, conversion, or throughput funnels |
| `timeline` | Multi-column milestone cards with phase objectives and validation gates | 30/60/90-day roadmaps and go-live gates |
| `closing` | Hero dark ask box with bold call-to-action, summary proof points card | Investment ask, pilot approval, committee sign-off |
| `card_grid` | 2, 3, or 4 column grid of modern structured component cards | Core pillars, product modules, value proposition grid |
| `split_content` | Side-by-side comparison layout (Problem vs Solution, Status Quo vs Proposed) | Direct contrast and competitive differentiation |
| `quote_stat` | Dark pull-quote card + right-side quantified impact stat banner | Customer voice, discovery findings, 10x ROI proof |
| `content` | Clean structured card container with conclusion headline and proof points | General decision and narrative slides |

## Visual encoding

- **Navy** (`#0F172A`): Stable structure, hero dark containers, primary slide titles.
- **Blue** (`#2563EB`): Primary strategy accent, driver metrics, chosen option.
- **Teal** (`#0D9488`): Validated empirical evidence, positive growth deltas, gate completions.
- **Amber** (`#D97706`): Modeled assumptions, uncertainty bounds, warning thresholds.
- **Red** (`#DC2626`): Downside risks, stop conditions, failure traps.
- **Card Background** (`#F8FAFC`) & **Border** (`#E2E8F0`): Modern light card container hierarchy.

Use color as a second signal, never the only signal. Label evidence state in text.

## Density limits

- Headline: One sentence, conclusion-first, preferably under 14 words.
- Body: 3–5 proof points or one visual system.
- Table: No more than 6 rows on a core slide; move detail to appendix.
- Source footer: Compact but readable, with source IDs (`CLM-xxx`, `SRC-xxx`, `MET-xxx`).

For displayed model numbers, include a raw numeric binding such as `{"metric_id":"MET-001","scenario":"base","value":1000000}`. Formatting such as `THB 1.0M` remains separate so changing the label cannot silently change the model.

## Fonts

The portable default is Arial because it has broad PowerPoint and cross-platform support. For Thai-first decks, Sarabun or Noto Sans Thai is recommended.
