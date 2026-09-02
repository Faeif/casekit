#!/usr/bin/env python3
"""Render a CaseKit deck specification to an executive-ready 16:9 widescreen PowerPoint presentation."""

import argparse
import json
import re
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


DEFAULT_COLORS = {
    "navy": "0F172A",       # Slate 900
    "blue": "2563EB",       # Blue 600 (Primary accent)
    "teal": "0D9488",       # Teal 600 (Validated evidence)
    "amber": "D97706",      # Amber 600 (Assumptions & warnings)
    "red": "DC2626",        # Red 600 (Risks & downside)
    "light": "F8FAFC",      # Slate 50 (Card background)
    "card_bg": "F8FAFC",    # Slate 50
    "card_border": "E2E8F0",# Slate 200
    "ink": "0F172A",        # Slate 900 (Main text)
    "muted": "64748B",      # Slate 500 (Subtext & footers)
    "white": "FFFFFF",
}


def rgb(value):
    value = str(value or "000000").lstrip("#")
    if len(value) != 6:
        value = "000000"
    return RGBColor.from_string(value.upper())


def add_box(slide, x, y, w, h, fill, line=None, rounded=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(1.0)
    else:
        shape.line.color.rgb = rgb(fill)
        shape.line.width = Pt(0)
    return shape


def add_text(slide, text, x, y, w, h, *, size=16, color="0F172A", bold=False,
             font="Arial", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.MIDDLE):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(0.04)
    frame.margin_top = frame.margin_bottom = Inches(0.02)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = str(text or "")
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(color)
    return box


def add_bullets(slide, items, x, y, w, h, *, font, color="0F172A", size=15, space_after=8):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(0.06)
    frame.vertical_anchor = MSO_ANCHOR.TOP
    for index, item in enumerate(items or []):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = f"• {item}" if not re.match(r"^\d+\.", str(item)) else str(item)
        paragraph.font.name = font
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = rgb(color)
        paragraph.space_after = Pt(space_after)
    return box


def set_background(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(color)


def fmt(value):
    if isinstance(value, float):
        return f"{value:,.1f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def render(spec):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    
    theme_cfg = spec.get("theme", {})
    if isinstance(theme_cfg, str):
        colors = {**DEFAULT_COLORS}
    else:
        colors = {**DEFAULT_COLORS, **theme_cfg}
        
    meta = spec.get("meta", {})
    font_head = meta.get("font_head", "Arial")
    font_body = meta.get("font_body", "Arial")

    slides_data = spec.get("slides", [])
    if not isinstance(slides_data, list) or not slides_data:
        raise SystemExit("slides must be a non-empty array")

    for number, item in enumerate(slides_data, 1):
        if not item.get("headline"):
            raise SystemExit(f"slide {number} is missing headline")

        slide = prs.slides.add_slide(blank)
        set_background(slide, colors["white"])
        slide_type = item.get("type") or item.get("slide_type", "content")

        if slide_type == "cover":
            # Cover Slide (Hero Dark Slate Background)
            set_background(slide, colors["navy"])
            # Decorative top accent pill
            add_box(slide, 0.8, 1.2, 1.2, 0.1, colors["teal"], rounded=True)
            # Main Title / Headline
            add_text(slide, item["headline"], 0.8, 1.6, 11.5, 2.4, size=38, color="FFFFFF", bold=True, font=font_head, valign=MSO_ANCHOR.TOP)
            # Subtitle
            subhead = item.get("subhead", meta.get("subtitle", ""))
            if subhead:
                add_text(slide, subhead, 0.82, 4.2, 11.0, 1.0, size=20, color="CBD5E1", font=font_body, valign=MSO_ANCHOR.TOP)
            # Team / Metadata Badge
            team_text = meta.get("team", "CaseKit Venture")
            add_box(slide, 0.82, 6.2, 3.5, 0.5, "1E293B", rounded=True)
            add_text(slide, f"Presented by: {team_text}", 0.95, 6.25, 3.2, 0.4, size=13, color="94A3B8", bold=True, font=font_body)
            if meta.get("currency"):
                add_text(slide, f"Currency: {meta['currency']} | Aspect Ratio: 16:9", 8.5, 6.25, 4.0, 0.4, size=12, color="64748B", align=PP_ALIGN.RIGHT, font=font_body)

        else:
            # Standard 16:9 Layout
            # Left vertical indicator bar
            add_box(slide, 0, 0, 0.12, 7.5, colors["blue"])
            
            # Header section
            category = item.get("category") or item.get("kicker", "")
            if category:
                add_text(slide, category.upper(), 0.65, 0.35, 11.8, 0.25, size=11, color=colors["blue"], bold=True, font=font_head)
                headline_y = 0.65
            else:
                headline_y = 0.45

            add_text(slide, item["headline"], 0.65, headline_y, 11.8, 0.75, size=24, color=colors["navy"], bold=True, font=font_head, valign=MSO_ANCHOR.TOP)

            # Body Layout Dispatcher
            if slide_type == "metric":
                # Stat Banner / Hero Card on Left, Bullets / Details on Right
                add_box(slide, 0.65, 1.6, 4.4, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                # Accent Header within Card
                add_box(slide, 0.65, 1.6, 4.4, 0.08, colors["blue"])
                metric_val = item.get("metric", "—")
                add_text(slide, metric_val, 0.85, 2.1, 4.0, 1.3, size=40, color=colors["blue"], bold=True, font=font_head, align=PP_ALIGN.CENTER)
                add_text(slide, item.get("label", "Key Metric"), 0.85, 3.4, 4.0, 0.6, size=16, color=colors["navy"], bold=True, font=font_body, align=PP_ALIGN.CENTER)
                comp = item.get("comparison", "")
                if comp:
                    add_box(slide, 1.1, 4.2, 3.5, 0.5, "ECFDF5", "A7F3D0", rounded=True)
                    add_text(slide, comp, 1.15, 4.25, 3.4, 0.4, size=13, color=colors["teal"], bold=True, font=font_body, align=PP_ALIGN.CENTER)
                
                # Right side details / insights card
                add_box(slide, 5.3, 1.6, 7.3, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                add_box(slide, 5.3, 1.6, 7.3, 0.08, colors["teal"])
                add_text(slide, "Supporting Evidence & Analysis", 5.6, 1.85, 6.7, 0.4, size=16, color=colors["navy"], bold=True, font=font_head)
                add_bullets(slide, item.get("body", []), 5.6, 2.4, 6.7, 3.8, font=font_body, color=colors["ink"], size=15, space_after=12)

            elif slide_type == "funnel":
                # Interactive Funnel Flow
                stages = item.get("stages", [])
                max_val = max([float(s.get("value", 0)) for s in stages] or [1])
                row_h = min(0.9, 4.8 / max(len(stages), 1))
                
                add_box(slide, 0.65, 1.6, 11.95, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                for index, stage in enumerate(stages):
                    val = float(stage.get("value", 0))
                    pct_width = max(val / max_val, 0.15) if max_val > 0 else 0.15
                    bar_w = 6.8 * pct_width
                    bar_x = 0.95
                    bar_y = 1.9 + index * row_h
                    
                    bar_color = colors["teal"] if index == len(stages) - 1 else colors["blue"]
                    add_box(slide, bar_x, bar_y, bar_w, row_h - 0.15, bar_color, rounded=True)
                    
                    # Stage label & value
                    stage_label = stage.get("label", f"Stage {index+1}")
                    add_text(slide, stage_label, bar_x + 0.15, bar_y, bar_w - 0.3, row_h - 0.15, size=14, color="FFFFFF", bold=True, font=font_body)
                    
                    val_str = fmt(stage.get("value", ""))
                    add_text(slide, val_str, 8.2, bar_y, 2.0, row_h - 0.15, size=16, color=colors["ink"], bold=True, font=font_body, align=PP_ALIGN.RIGHT)
                    
                    if index < len(stages) - 1 and max_val > 0:
                        next_val = float(stages[index+1].get("value", 0))
                        conv_pct = f"{(next_val / val * 100):.1f}%" if val > 0 else "—"
                        add_text(slide, f"↓ {conv_pct}", 10.4, bar_y, 1.8, row_h - 0.15, size=12, color=colors["muted"], font=font_body)

            elif slide_type == "timeline":
                # Milestone Roadmap Cards
                phases = item.get("phases", [])
                col_w = 11.6 / max(len(phases), 1)
                for index, phase in enumerate(phases):
                    px = 0.65 + index * col_w
                    card_w = col_w - 0.25
                    add_box(slide, px, 1.6, card_w, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                    add_box(slide, px, 1.6, card_w, 0.08, colors["blue"] if index == 0 else colors["teal"])
                    
                    phase_title = phase.get("label", f"Phase {index+1}")
                    add_text(slide, phase_title, px + 0.15, 1.85, card_w - 0.3, 0.5, size=17, color=colors["blue"], bold=True, font=font_head)
                    
                    add_bullets(slide, phase.get("items", []), px + 0.15, 2.45, card_w - 0.3, 3.2, font=font_body, color=colors["ink"], size=13, space_after=8)
                    
                    gate = phase.get("gate", "")
                    if gate:
                        add_box(slide, px + 0.15, 5.8, card_w - 0.3, 0.6, "F1F5F9", colors["card_border"], rounded=True)
                        add_text(slide, f"Gate: {gate}", px + 0.2, 5.85, card_w - 0.4, 0.5, size=11, color=colors["teal"], bold=True, font=font_body)

            elif slide_type == "card_grid" or slide_type == "grid":
                # Multi-Column Card Grid (e.g. 2, 3, or 4 pillars)
                cards = item.get("cards", item.get("columns", []))
                if not cards:
                    # Fallback to body items as individual cards
                    cards = [{"title": f"Point {i+1}", "body": [b]} for i, b in enumerate(item.get("body", []))]
                col_w = 11.6 / max(len(cards), 1)
                for index, card in enumerate(cards):
                    cx = 0.65 + index * col_w
                    card_w = col_w - 0.25
                    add_box(slide, cx, 1.6, card_w, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                    card_accent = colors["blue"] if index % 2 == 0 else colors["teal"]
                    add_box(slide, cx, 1.6, card_w, 0.08, card_accent)
                    
                    card_title = card.get("title") or card.get("headline", f"Card {index+1}")
                    add_text(slide, card_title, cx + 0.15, 1.85, card_w - 0.3, 0.5, size=17, color=colors["navy"], bold=True, font=font_head)
                    
                    card_body = card.get("body", [])
                    if isinstance(card_body, str):
                        card_body = [card_body]
                    add_bullets(slide, card_body, cx + 0.15, 2.45, card_w - 0.3, 3.8, font=font_body, color=colors["ink"], size=13, space_after=8)

            elif slide_type == "split_content" or slide_type == "split":
                # Side-by-Side Comparison Layout (Problem vs Solution, Status Quo vs Proposed)
                left = item.get("left", {})
                right = item.get("right", {})
                
                # Left Card
                add_box(slide, 0.65, 1.6, 5.8, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                add_box(slide, 0.65, 1.6, 5.8, 0.08, colors["amber"])
                left_title = left.get("title", "Status Quo / Problem")
                add_text(slide, left_title, 0.85, 1.85, 5.4, 0.5, size=18, color=colors["amber"], bold=True, font=font_head)
                add_bullets(slide, left.get("body", item.get("body", [])[:len(item.get("body", []))//2]), 0.85, 2.45, 5.4, 3.8, font=font_body, color=colors["ink"], size=14)

                # Right Card
                add_box(slide, 6.8, 1.6, 5.8, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                add_box(slide, 6.8, 1.6, 5.8, 0.08, colors["teal"])
                right_title = right.get("title", "CaseKit Solution / Value")
                add_text(slide, right_title, 7.0, 1.85, 5.4, 0.5, size=18, color=colors["teal"], bold=True, font=font_head)
                add_bullets(slide, right.get("body", item.get("body", [])[len(item.get("body", []))//2:]), 7.0, 2.45, 5.4, 3.8, font=font_body, color=colors["ink"], size=14)

            elif slide_type == "quote_stat" or slide_type == "quote":
                # Large Pull Quote + Stat Banner
                add_box(slide, 0.65, 1.6, 6.8, 5.0, colors["navy"], rounded=True)
                quote_text = item.get("quote", item.get("headline", ""))
                add_text(slide, f"“{quote_text}”", 0.95, 2.0, 6.2, 3.0, size=24, color="FFFFFF", bold=True, font=font_head)
                author = item.get("author", "Customer Discovery Interview")
                add_text(slide, f"— {author}", 0.95, 5.2, 6.2, 0.5, size=14, color="94A3B8", font=font_body)

                add_box(slide, 7.8, 1.6, 4.8, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                add_box(slide, 7.8, 1.6, 4.8, 0.08, colors["blue"])
                metric_val = item.get("metric", "10x")
                add_text(slide, metric_val, 8.0, 2.2, 4.4, 1.2, size=44, color=colors["blue"], bold=True, font=font_head, align=PP_ALIGN.CENTER)
                add_text(slide, item.get("label", "Quantified Impact"), 8.0, 3.5, 4.4, 0.6, size=16, color=colors["navy"], bold=True, font=font_body, align=PP_ALIGN.CENTER)
                add_bullets(slide, item.get("body", []), 8.0, 4.2, 4.4, 2.0, font=font_body, color=colors["ink"], size=13)

            elif slide_type == "closing":
                # Closing Ask & Action Slide
                ask_text = item.get("ask", "Approve Recommendation & Next Phase")
                add_box(slide, 0.65, 1.6, 11.95, 1.5, colors["navy"], rounded=True)
                add_text(slide, "THE ASK & IMMEDIATE DECISION", 0.95, 1.8, 11.35, 0.3, size=12, color=colors["teal"], bold=True, font=font_head)
                add_text(slide, ask_text, 0.95, 2.15, 11.35, 0.8, size=22, color="FFFFFF", bold=True, font=font_head)
                
                # Bottom proof points card
                add_box(slide, 0.65, 3.35, 11.95, 3.25, colors["card_bg"], colors["card_border"], rounded=True)
                add_box(slide, 0.65, 3.35, 11.95, 0.08, colors["teal"])
                add_text(slide, "Decision Rationale & Go-Live Gates", 0.95, 3.55, 11.35, 0.4, size=16, color=colors["navy"], bold=True, font=font_head)
                add_bullets(slide, item.get("body", []), 0.95, 4.05, 11.35, 2.3, font=font_body, color=colors["ink"], size=15, space_after=10)

            else:
                # Default "content" Slide
                if item.get("ask"):
                    add_box(slide, 0.65, 1.6, 11.95, 1.3, colors["navy"], rounded=True)
                    add_text(slide, item["ask"], 0.95, 1.8, 11.35, 0.9, size=22, color="FFFFFF", bold=True, font=font_head, align=PP_ALIGN.CENTER)
                    add_box(slide, 0.65, 3.1, 11.95, 3.5, colors["card_bg"], colors["card_border"], rounded=True)
                    add_bullets(slide, item.get("body", []), 0.95, 3.3, 11.35, 3.1, font=font_body, color=colors["ink"], size=15, space_after=10)
                else:
                    add_box(slide, 0.65, 1.6, 11.95, 5.0, colors["card_bg"], colors["card_border"], rounded=True)
                    add_box(slide, 0.65, 1.6, 11.95, 0.08, colors["blue"])
                    add_bullets(slide, item.get("body", []), 0.95, 1.9, 11.35, 4.4, font=font_body, color=colors["ink"], size=16, space_after=14)

            # Slide Footer
            # Subtle divider line
            slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(6.9), Inches(11.95), Inches(0.01)).fill.solid()
            evidence_ids = item.get("evidence_ids", [])
            if evidence_ids:
                add_text(slide, "Evidence: " + " · ".join(evidence_ids), 0.65, 6.98, 10.5, 0.3, size=9.5, color=colors["muted"], font=font_body)
            add_text(slide, str(number), 12.0, 6.98, 0.6, 0.3, size=9.5, color=colors["muted"], font=font_body, align=PP_ALIGN.RIGHT)

        # Speaker notes
        if item.get("speaker_notes"):
            try:
                slide.notes_slide.notes_text_frame.text = str(item["speaker_notes"])
            except Exception:
                pass

    return prs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="Path to 12-deck-spec.json")
    parser.add_argument("output", type=Path, help="Output .pptx path")
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    if not isinstance(spec.get("slides"), list) or not spec["slides"]:
        raise SystemExit("slides must be a non-empty array")
    for index, slide in enumerate(spec["slides"], 1):
        if not slide.get("headline"):
            raise SystemExit(f"slide {index} is missing headline")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    render(spec).save(args.output)
    print(f"Rendered {len(spec['slides'])} slides (16:9 widescreen) -> {args.output}")


if __name__ == "__main__":
    main()
