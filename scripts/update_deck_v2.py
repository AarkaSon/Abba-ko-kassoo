#!/usr/bin/env python3
"""Apply the requested revisions to the user-edited internal crash-barrier deck.

1. Insert a new slide 2, "Background", covering crash-barrier types/uses, how the
   present invention differs from commercial barriers, low-carbon binder
   efficiency and sintered lightweight aggregate properties -- as infographic
   cards, a native chart and comparison tables.
2. Replace the slide-1 photograph with the AI-generated HUD concept visual.
3. Rebuild the "Methods overview" slide: photographs for each of the five stages,
   larger type throughout, no source line (inventor-manuscript attribution
   removed; internet-sourced attributions are retained on the other slides).

The script edits the user's own PPTX in place, so every manual edit already made
to the other slides is preserved.
"""

from __future__ import annotations

import copy
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageEnhance, ImageOps
from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_DATA_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_VERTICAL_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "IITBBS_Impact_Dissipating_Crash_Barrier_Internal_Confidential.pptx"
ARTICLE = ROOT / "Al-Amir_Research Article_R1.docx"
LOGO = ROOT / "assets" / "iitbbs_logo_official.png"
HERO = ROOT / "assets" / "ai_hero_crash_barrier_hud_v2.png"
BUILD = ROOT / ".build"
MEDIA = BUILD / "media"
PANELS = BUILD / "panels"

# ---------------------------------------------------------------- palette ----
NAVY = "17365D"
INK = "202B33"
MUTED = "5D6972"
WHITE = "FFFFFF"
GRID = "CCD6DE"
BLUE = "2E6F9E"
CYAN = "4A89A3"
TEAL = "3F7E73"
GREEN = "557A60"
ORANGE = "B37A30"
RED = "9A4651"
LIGHT_BLUE = "EAF1F6"
LIGHT_CYAN = "EAF2F3"
LIGHT_ORANGE = "F6EFE4"
LIGHT_RED = "F6EAEC"
LIGHT_GREEN = "ECF2ED"

FONT_HEAD = "Cambria"
FONT_BODY = "Aptos"

STATUS = "CONFIDENTIAL • PRE-FILING IITBBS IPR COMMITTEE EVALUATION • NOT YET FILED"


def rgb(value: str) -> RGBColor:
    value = value.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


# ------------------------------------------------------------- primitives ----
def set_run(run, size=12, color=INK, bold=False, font=FONT_BODY, italic=False):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = rgb(color)


def add_text(slide, x, y, w, h, text, size=14, color=INK, bold=False,
             font=FONT_BODY, align=PP_ALIGN.LEFT, valign=MSO_VERTICAL_ANCHOR.TOP,
             margin=0.04, line_spacing=1.0, name=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        box.name = name
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    set_run(r, size, color, bold, font)
    return box


def add_lines(slide, x, y, w, h, items, size=9.5, gap=0.05, line_spacing=1.02):
    """items: list of (lead, rest) or plain strings; lead is bolded."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0)
    tf.margin_top = tf.margin_bottom = Inches(0)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap * 72)
        p.line_spacing = line_spacing
        if isinstance(item, tuple):
            lead, rest = item[0], item[1]
            lead_color = item[2] if len(item) > 2 else NAVY
            r1 = p.add_run(); r1.text = lead; set_run(r1, size, lead_color, True)
            r2 = p.add_run(); r2.text = rest; set_run(r2, size, INK, False)
        else:
            r = p.add_run(); r.text = str(item); set_run(r, size, INK, False)
    return box


def add_bullets(slide, x, y, w, h, bullets, size=9.5, bullet_color=CYAN, gap=0.05):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0)
    tf.margin_top = tf.margin_bottom = Inches(0)
    for i, item in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap * 72)
        p.line_spacing = 1.02
        r0 = p.add_run(); r0.text = "▪  "; set_run(r0, size - 1.2, bullet_color, True)
        if isinstance(item, tuple):
            r1 = p.add_run(); r1.text = item[0]; set_run(r1, size, NAVY, True)
            r2 = p.add_run(); r2.text = item[1]; set_run(r2, size, INK, False)
        else:
            r1 = p.add_run(); r1.text = str(item); set_run(r1, size, INK, False)
    return box


def add_rect(slide, x, y, w, h, fill=WHITE, line=GRID, line_width=0.8, name=None,
             shape=MSO_SHAPE.RECTANGLE):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        shp.name = name
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_width)
    shp.shadow.inherit = False
    return shp


def add_line(slide, x1, y1, x2, y2, color=GRID, width=1.0):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1),
                                    Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(width)
    return ln


def add_pill(slide, x, y, w, h, text, fill=LIGHT_BLUE, color=BLUE, size=9.5, line=None):
    add_rect(slide, x, y, w, h, fill, line or fill, line_width=0.6)
    add_text(slide, x + 0.06, y, w - 0.12, h, text, size, color, True,
             align=PP_ALIGN.CENTER, valign=MSO_VERTICAL_ANCHOR.MIDDLE, margin=0,
             line_spacing=1.0)


def table_cell_style(cell, size=9.0, color=INK, bold=False, align=PP_ALIGN.CENTER):
    cell.margin_left = cell.margin_right = Inches(0.05)
    cell.margin_top = cell.margin_bottom = Inches(0.02)
    cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
    for p in cell.text_frame.paragraphs:
        p.alignment = align
        for r in p.runs:
            set_run(r, size, color, bold, FONT_BODY)


def add_table(slide, x, y, w, h, rows, col_widths=None, font_size=9.0,
              first_col_left=True, header_fill=NAVY, highlight_rows=None):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                                   Inches(w), Inches(h))
    table = shape.table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            table.columns[i].width = Inches(w * cw / total)
    highlight_rows = highlight_rows or {}
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.cell(ri, ci)
            cell.text = str(val)
            cell.fill.solid()
            if ri == 0:
                cell.fill.fore_color.rgb = rgb(header_fill)
                color, bold = WHITE, True
            else:
                cell.fill.fore_color.rgb = rgb(
                    highlight_rows.get(ri, WHITE if ri % 2 else "F8FAFB"))
                color, bold = INK, ci == 0
            table_cell_style(cell, font_size, color, bold,
                             PP_ALIGN.LEFT if (first_col_left and ci == 0) else PP_ALIGN.CENTER)
    return table


def _ensure_notes_body(notes_slide):
    """Some notes masters omit the body placeholder; synthesise one if needed."""
    if notes_slide.notes_text_frame is not None:
        return notes_slide.notes_text_frame
    from pptx.oxml.ns import nsdecls
    from pptx.oxml import parse_xml

    spTree = notes_slide.shapes._spTree
    used = [int(e.get("id")) for e in spTree.iter() if e.tag.endswith("}cNvPr")]
    new_id = max(used) + 1 if used else 2
    sp = parse_xml(
        f'<p:sp {nsdecls("p", "a")}>'
        f'  <p:nvSpPr>'
        f'    <p:cNvPr id="{new_id}" name="Notes Placeholder {new_id}"/>'
        f'    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f'    <p:nvPr><p:ph type="body" idx="1"/></p:nvPr>'
        f'  </p:nvSpPr>'
        f'  <p:spPr/>'
        f'  <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>'
        f'</p:sp>'
    )
    spTree.append(sp)
    return notes_slide.notes_text_frame


def add_notes(slide, text):
    tf = _ensure_notes_body(slide.notes_slide)
    tf.clear()
    first = True
    for line in text.strip().split("\n"):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = line
        set_run(r, 12, INK, False, FONT_BODY)


# ------------------------------------------------------------ image utils ----
def extract_media():
    MEDIA.mkdir(parents=True, exist_ok=True)
    with ZipFile(ARTICLE) as zf:
        for name in zf.namelist():
            if name.startswith("word/media/"):
                (MEDIA / Path(name).name).write_bytes(zf.read(name))


PANEL_BOXES = {
    "raw": (18, 14, 443, 347),
    "mixing": (478, 14, 905, 347),
    "slump": (936, 14, 1366, 347),
    "compaction": (18, 420, 443, 753),
    "cast": (478, 420, 905, 753),
    "curing": (936, 420, 1366, 753),
}


def build_panels():
    """Split the manuscript's six-panel process montage into individual photos."""
    PANELS.mkdir(parents=True, exist_ok=True)
    src = Image.open(MEDIA / "image4.png").convert("RGB")
    for key, box in PANEL_BOXES.items():
        (PANELS / f"{key}.png").write_bytes(b"") if False else None
        src.crop(box).save(PANELS / f"{key}.png")


def cover(src: Path, key: str, w_in: float, h_in: float, enhance=True) -> Path:
    """Crop-to-fill at a sensible pixel density."""
    PANELS.mkdir(parents=True, exist_ok=True)
    size = (max(1, int(w_in * 200)), max(1, int(h_in * 200)))
    dst = BUILD / "fit" / f"{key}.jpg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im = ImageOps.fit(im, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    if enhance:
        im = ImageEnhance.Contrast(im).enhance(1.06)
        im = ImageEnhance.Color(im).enhance(0.95)
    im.save(dst, quality=93, optimize=True)
    return dst


def contain(src: Path, key: str, w_in: float, h_in: float, bg=(255, 255, 255)) -> Path:
    size = (max(1, int(w_in * 200)), max(1, int(h_in * 200)))
    dst = BUILD / "fit" / f"{key}.jpg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    fitted = ImageOps.contain(im, size, method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, bg)
    canvas.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    canvas.save(dst, quality=94, optimize=True)
    return dst


# ------------------------------------------------------------ deck chrome ----
def add_logo(slide):
    add_rect(slide, 12.20, 0.12, 0.84, 0.66, WHITE, None)
    slide.shapes.add_picture(str(LOGO), Inches(12.34), Inches(0.18),
                             width=Inches(0.58), height=Inches(0.54))


def add_header(slide, title, section, slide_no):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(WHITE)
    add_rect(slide, 0.0, 0.0, 0.10, 7.5, NAVY, None)
    add_text(slide, 0.68, 0.17, 3.15, 0.22, section.upper(), 8.2, BLUE, True, margin=0)
    size = 22.0 if len(title) <= 58 else 20.2
    add_text(slide, 0.68, 0.36, 10.90, 0.67, title, size, NAVY, True, FONT_HEAD,
             margin=0, valign=MSO_VERTICAL_ANCHOR.MIDDLE, line_spacing=0.92)
    add_logo(slide)
    add_line(slide, 0.68, 1.08, 12.62, 1.08, NAVY, 1.15)
    add_line(slide, 0.68, 7.08, 12.62, 7.08, GRID, 0.65)
    add_text(slide, 0.70, 7.16, 10.9, 0.18, STATUS, 7.2, RED, True, margin=0)
    add_text(slide, 12.00, 7.14, 0.60, 0.19, f"{slide_no:02d}", 8.1, MUTED, True,
             align=PP_ALIGN.RIGHT, margin=0)


def band_title(slide, x, y, w, letter, text, accent=NAVY):
    add_rect(slide, x, y, 0.24, 0.24, accent, None)
    add_text(slide, x, y, 0.24, 0.24, letter, 9.5, WHITE, True, FONT_HEAD,
             align=PP_ALIGN.CENTER, valign=MSO_VERTICAL_ANCHOR.MIDDLE, margin=0)
    add_text(slide, x + 0.32, y - 0.01, w - 0.32, 0.26, text, 11.4, NAVY, True,
             FONT_HEAD, margin=0, valign=MSO_VERTICAL_ANCHOR.MIDDLE)


# ======================================================= 1. BACKGROUND ========
def build_background_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide,
               "Background: barrier practice, binder efficiency and lightweight aggregate",
               "Background", 2)

    # ---- Band A: barrier taxonomy + how ours differs -------------------------
    band_title(slide, 0.72, 1.16, 11.9,
               "A", "Crash-barrier families — deflection governs both containment and occupant severity (IRC:119-2015)")

    cards = [
        dict(title="FLEXIBLE", sub="Wire-rope / cable",
             accent=GREEN, fill=LIGHT_GREEN,
             rows=[("Deflection:  ", "1.6–2.6 m"),
                   ("Occupant severity:  ", "Lowest"),
                   ("Used for:  ", "wide, flat medians; long rural runs")],
             foot="Needs large clear space; re-tensioning and repair after most hits."),
        dict(title="SEMI-RIGID", sub="W-beam / thrie-beam steel",
             accent=ORANGE, fill=LIGHT_ORANGE,
             rows=[("Deflection:  ", "0.9–1.8 m"),
                   ("Occupant severity:  ", "Moderate"),
                   ("Used for:  ", "general roadside, bridge approaches")],
             foot="Corrosion-prone; damaged rail sections must be replaced after impact."),
        dict(title="RIGID", sub="Concrete New Jersey / F-profile",
             accent=RED, fill=LIGHT_RED,
             rows=[("Deflection:  ", "≈ 0 — redirects by mass"),
                   ("Occupant severity:  ", "highest of the three"),
                   ("Used for:  ", "narrow medians, urban roads, bridges")],
             foot="Least maintenance, but brittle spalling and fragmentation under impact."),
        dict(title="THIS WORK", sub="SFA lightweight steel-fibre concrete",
             accent=BLUE, fill=LIGHT_BLUE,
             rows=[("Form:  ", "rigid NJ geometry retained"),
                   ("Response:  ", "energy absorbed in the material"),
                   ("Measured:  ", "55.3× prism failure energy; 3.0× barrier deformation")],
             foot="Rigid where it must be, semi-absorbing where it helps — at −19.4% density."),
    ]
    for i, c in enumerate(cards):
        x = 0.72 + i * 2.99
        w = 2.91
        add_rect(slide, x, 1.48, w, 1.82, WHITE, GRID, 0.7)
        add_rect(slide, x, 1.48, w, 0.40, c["accent"], None)
        add_text(slide, x + 0.10, 1.50, w - 0.20, 0.21, c["title"], 9.6, WHITE, True, margin=0)
        add_text(slide, x + 0.10, 1.69, w - 0.20, 0.18, c["sub"], 7.8, "E8EFF4", False, margin=0)
        add_lines(slide, x + 0.11, 1.96, w - 0.22, 0.86, c["rows"], size=8.6, gap=0.035)
        add_rect(slide, x + 0.01, 2.86, w - 0.02, 0.43, c["fill"], None)
        add_text(slide, x + 0.11, 2.88, w - 0.22, 0.40, c["foot"], 8.0,
                 NAVY if i == 3 else INK, i == 3, margin=0,
                 valign=MSO_VERTICAL_ANCHOR.MIDDLE, line_spacing=1.0)

    # ---- Band B: binder efficiency ------------------------------------------
    band_title(slide, 0.72, 3.44, 5.6, "B", "Low-carbon binder efficiency")
    add_rect(slide, 0.72, 3.74, 5.62, 1.92, WHITE, GRID, 0.7)

    data = ChartData()
    data.categories = ["Conventional\nOPC concrete", "Alkali-activated /\ngeopolymer route"]
    data.add_series("kg CO₂e per m³", (345.3, 146.4))
    frame = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.80),
                                   Inches(3.98), Inches(2.60), Inches(1.30), data)
    chart = frame.chart
    chart.font.name = FONT_BODY
    chart.font.size = Pt(8)
    chart.font.color.rgb = rgb(MUTED)
    chart.has_legend = False
    s = chart.series[0]
    for point, colour in zip(s.points, [RED, TEAL]):
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = rgb(colour)
        point.format.line.color.rgb = rgb(colour)
    chart.plots[0].gap_width = 70
    chart.value_axis.minimum_scale = 0
    chart.value_axis.maximum_scale = 420
    chart.value_axis.has_major_gridlines = True
    chart.value_axis.major_gridlines.format.line.color.rgb = rgb(GRID)
    chart.value_axis.tick_labels.font.size = Pt(7)
    chart.category_axis.tick_labels.font.size = Pt(7.4)
    chart.value_axis.format.line.color.rgb = rgb(GRID)
    chart.category_axis.format.line.color.rgb = rgb(GRID)
    plot = chart.plots[0]
    plot.has_data_labels = True
    labels = plot.data_labels
    labels.position = XL_DATA_LABEL_POSITION.OUTSIDE_END
    labels.show_value = True
    labels.number_format = "0"
    labels.font.size = Pt(8.5)
    labels.font.bold = True
    labels.font.color.rgb = rgb(INK)
    add_text(slide, 0.82, 3.80, 2.56, 0.20, "Embodied CO₂e, kg per m³", 8.2, NAVY, True,
             FONT_HEAD, margin=0, align=PP_ALIGN.CENTER)

    add_pill(slide, 0.84, 5.32, 2.52, 0.26, "≈ 58% lower embodied CO₂e", LIGHT_CYAN, TEAL, 8.8)
    add_bullets(slide, 3.52, 3.86, 2.72, 1.70, [
        ("Why it matters:  ", "clinker is the dominant emission term in a barrier segment; binder substitution is the largest single lever."),
        ("Reported range:  ", "30–80% lower CO₂e depending on activator dosage, curing and transport — not a fixed figure."),
        ("This embodiment:  ", "20% GGBS replacement of binder — a partial-substitution step, with a full alkali-activated barrier binder as the forward route."),
    ], size=8.4, bullet_color=TEAL, gap=0.05)

    # ---- Band C: sintered lightweight aggregate ------------------------------
    band_title(slide, 6.62, 3.44, 6.0, "C", "Sintered fly-ash aggregate vs natural coarse aggregate")
    add_rect(slide, 6.62, 3.74, 6.00, 1.92, WHITE, GRID, 0.7)
    rows = [
        ["Property", "Natural coarse agg.", "Sintered fly-ash agg.", "Consequence in the barrier"],
        ["Specific gravity", "2.4 – 2.7", "1.5 – 1.8", "16–46% lighter segment"],
        ["Loose bulk density", "≈ 1,467 kg/m³", "≈ 778 kg/m³", "Lower crane / transport demand"],
        ["Water absorption", "≈ 1%", "15 – 20%", "Internal curing → denser ITZ"],
        ["Crushing value", "≈ 15.7%", "≈ 15.6%", "Structural grade retained"],
        ["Pore structure", "Dense, non-porous", "Vesicular, sintered shell", "Aggregate crushing absorbs impact energy"],
    ]
    add_table(slide, 6.72, 3.82, 5.80, 1.76, rows, [1.30, 1.20, 1.30, 2.00],
              font_size=8.2, highlight_rows={5: LIGHT_CYAN})

    # ---- Band D: differentiation --------------------------------------------
    band_title(slide, 0.72, 5.74, 11.9, "D",
               "How this differs from the barriers used commercially today")
    diffs = [
        ("Rigid form, non-rigid response",
         "New Jersey geometry and containment are kept; the dissipation is moved into the material.", BLUE),
        ("Fragmentation control",
         "Hooked-end fibres bridge cracks: 186 post-crack blows vs 2 for the NWC reference.", TEAL),
        ("Closed material loop",
         "100% sintered fly-ash coarse aggregate + GGBS: no natural coarse aggregate consumed.", GREEN),
        ("Precast-ready weight",
         "−19.4% density eases handling, lifting and transport of cast-yard segments.", ORANGE),
    ]
    for i, (t, b, accent) in enumerate(diffs):
        x = 0.72 + i * 2.99
        add_rect(slide, x, 6.04, 2.91, 0.62, WHITE, GRID, 0.6)
        add_rect(slide, x, 6.04, 0.045, 0.62, accent, None)
        add_text(slide, x + 0.14, 6.07, 2.70, 0.19, t, 8.6, accent, True, margin=0)
        add_text(slide, x + 0.14, 6.26, 2.70, 0.37, b, 7.8, INK, margin=0, line_spacing=1.0)

    add_text(slide, 0.73, 6.74, 11.85, 0.19,
             "Source: IRC:119-2015 barrier classification and deflection guidance; EN 1317 / IS 17090 containment and working-width framework; "
             "Nadesan & Dinakar (2017), Case Stud. Constr. Mater.; sintered-aggregate property ranges from published characterisation studies; "
             "geopolymer LCA range from published comparative life-cycle assessments. Performance figures for the present material are laboratory-scale observations.",
             6.6, MUTED, margin=0)

    add_notes(slide, """
BACKGROUND — approximately 90 seconds

• Band A frames the problem the way the road authority does. IRC:119-2015 classifies safety barriers by how much they deflect: flexible cable systems deflect 1.6 to 2.6 metres and are gentlest on occupants but need a wide median; semi-rigid steel beam systems deflect roughly 0.9 to 1.8 metres; rigid concrete barriers effectively do not deflect at all.
• That is the trade-off the industry has lived with. Rigid concrete is chosen wherever space is tight — narrow medians, urban roads, bridges — and wherever heavy-vehicle containment matters, precisely because it does not deflect. The price paid is the highest occupant impact severity of the three, plus brittle spalling and debris.
• The fourth card is the contribution. We keep the rigid New Jersey geometry, so containment, working width and installation practice are unchanged, but we move the energy dissipation inside the material. Measured at prism scale, failure energy rose 55.3 times; at one-third barrier scale, deformation rose 3.0 times, at 19.4% lower density.
• Band B addresses the binder. Published life-cycle assessments put alkali-activated and geopolymer binders at roughly 146 versus 345 kilograms of CO2-equivalent per cubic metre — about 58% lower — although the literature range is wide, 30 to 80%, and depends heavily on activator dosage and curing. Be honest here: the tested embodiment uses 20% GGBS replacement, which is a partial step on that path, not a full geopolymer. The full alkali-activated barrier binder is the forward research route.
• Band C explains why the aggregate is doing real mechanical work, not just saving weight. Sintered fly-ash aggregate is 16 to 46% lighter than natural coarse aggregate and absorbs 15 to 20% water against about 1%. That absorption is not a defect: it provides internal curing and produces a denser interfacial transition zone. Its vesicular structure crushes progressively under impact, which is the dissipation mechanism.
• Band D is the one-line answer if a committee member asks what is actually new: rigid form with non-rigid response, fragmentation control, a closed by-product loop, and a lighter precast segment.
""")
    return slide


# ============================================= 2. TITLE-SLIDE IMAGE SWAP =====
def replace_title_picture(prs):
    slide = prs.slides[0]
    pictures = [s for s in slide.shapes
                if s.shape_type == 13 and s.width and s.height]
    if not pictures:
        raise RuntimeError("Could not locate the slide-1 feature photograph.")
    # The feature photo is by far the largest picture; the other is the logo.
    target = max(pictures, key=lambda s: s.width * s.height)
    left, top, width, height = target.left, target.top, target.width, target.height
    target._element.getparent().remove(target._element)

    fitted = cover(HERO, "hero_ai", width / 914400, height / 914400, enhance=False)
    pic = slide.shapes.add_picture(str(fitted), left, top, width, height)
    pic.name = "Picture 14"

    for shape in slide.shapes:
        if shape.has_text_frame and "pendulum-impact apparatus" in shape.text_frame.text:
            tf = shape.text_frame
            existing = tf.paragraphs[0].runs[0] if tf.paragraphs[0].runs else None
            size = (existing.font.size if existing is not None and existing.font.size
                    else Pt(7.5))
            try:
                colour = existing.font.color.rgb
            except (AttributeError, TypeError):
                colour = rgb(MUTED)
            tf.clear()
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = ("Concept visualisation: instrumented energy-dissipating barrier "
                      "(AI-generated illustration, not experimental data)")
            r.font.name = FONT_BODY
            r.font.size = size
            r.font.bold = False
            r.font.color.rgb = colour
            break
    return slide


# ================================================ 3. METHODS OVERVIEW ========
def rebuild_methods_slide(prs, index):
    slide = prs.slides[index]

    keep_prefixes = ("Rectangle 1", "Rectangle 4", "Picture 5", "Connector 6",
                     "Connector 7", "TextBox 2", "TextBox 3", "TextBox 8", "TextBox 9")
    for shape in list(slide.shapes):
        name = shape.name
        keep = (name in keep_prefixes) or "Pentagon" in name
        if not keep:
            shape._element.getparent().remove(shape._element)

    steps = [
        dict(n="1", title="MATERIALS", img=PANELS / "raw.png", key="m_raw",
             body="XRF oxide analysis; specific gravity and absorption of sintered fly-ash aggregate; hooked-end fibre geometry."),
        dict(n="2", title="MIX DESIGN", img=PANELS / "mixing.png", key="m_mix",
             body="NWC reference plus four lightweight variants; steel-fibre dosage stepped 0 → 1.5% by concrete volume."),
        dict(n="3", title="STATIC TESTS", img=PANELS / "slump.png", key="m_slump",
             body="Slump; reported density; 28-day cube compression and cylinder splitting tensile strength."),
        dict(n="4", title="PRISM IMPACT", img=MEDIA / "image5.jpeg", key="m_prism",
             body="13.5 kg repeated drop mass; first-crack N₁ and failure N₂; acceleration integrated to displacement."),
        dict(n="5", title="BARRIER MODEL", img=MEDIA / "image8.jpeg", key="m_barrier",
             body="1:3 New Jersey barrier; 40 kg pendulum at 0.35 m rise; NWC compared with the selected LWC15 mix."),
    ]

    card_w, card_h, top = 2.30, 3.06, 1.30
    for i, st in enumerate(steps):
        x = 0.72 + i * 2.38
        add_rect(slide, x, top, card_w, card_h, WHITE, GRID, 0.8)
        add_rect(slide, x, top, card_w, 0.38, NAVY, None)
        add_rect(slide, x + 0.09, top + 0.07, 0.24, 0.24, CYAN, None)
        add_text(slide, x + 0.09, top + 0.07, 0.24, 0.24, st["n"], 9.5, WHITE, True,
                 FONT_HEAD, align=PP_ALIGN.CENTER, valign=MSO_VERTICAL_ANCHOR.MIDDLE, margin=0)
        add_text(slide, x + 0.40, top + 0.08, card_w - 0.48, 0.22, st["title"], 10.2,
                 WHITE, True, margin=0, valign=MSO_VERTICAL_ANCHOR.MIDDLE)

        img_w, img_h = card_w - 0.16, 1.52
        fitted = cover(st["img"], st["key"], img_w, img_h)
        slide.shapes.add_picture(str(fitted), Inches(x + 0.08), Inches(top + 0.47),
                                 Inches(img_w), Inches(img_h))
        add_rect(slide, x + 0.08, top + 0.47, img_w, img_h, None, GRID, 0.6)

        add_text(slide, x + 0.11, top + 2.08, card_w - 0.22, 0.90, st["body"], 9.8, INK,
                 margin=0, line_spacing=1.05, valign=MSO_VERTICAL_ANCHOR.TOP)

        if i < 4:
            add_rect(slide, x + card_w + 0.02, top + 1.11, 0.18, 0.24, GRID, None,
                     shape=MSO_SHAPE.CHEVRON)

    evidence_rows = [
        ["Evidence level", "Specimens / comparison", "Primary response", "Interpretive limitation"],
        ["Material", "Five concrete mixtures", "Density, f\u1d9c, f\u209c", "Density terminology unresolved"],
        ["Repeated impact", "Four beams reportedly cast per mix", "N₁, N₂, E₁, E₂, displacement", "N₁/N₂ dispersion not reported"],
        ["Barrier scale", "1 NWC + 1 selected LWC", "Failure blows, E₂, deformation, debris", "Preliminary; no population inference"],
    ]
    add_table(slide, 0.72, 4.52, 11.90, 1.92, evidence_rows, [1.55, 2.75, 3.10, 3.05],
              font_size=10.4, highlight_rows={3: LIGHT_RED})

    add_rect(slide, 0.72, 6.52, 11.90, 0.46, LIGHT_RED, RED, 0.6)
    add_text(slide, 0.94, 6.53, 11.46, 0.44,
             "Statistical boundary: the reported ratios are experimental observations; barrier-scale confidence intervals cannot be inferred from n = 1.",
             10.0, RED, True, margin=0, valign=MSO_VERTICAL_ANCHOR.MIDDLE)

    add_notes(slide, """
EXPERIMENTAL LOGIC — approximately 75 seconds

• The evidence was built in five layers, shown left to right: constituent characterization, mixture design, static mechanical tests, repeated drop-weight impact on prisms, and a one-third-scale barrier comparison. Each photograph is from our own laboratory programme.
• Four lightweight mixtures were evaluated with fibre volume increasing from zero to 1.5%, alongside an M40 normal-weight reference.
• Static tests set the strength and density boundary. The repeated impact test provides the key post-cracking energy evidence; acceleration signals were processed to derive displacement. The best-performing mixture was then cast as a New Jersey barrier model and compared with NWC under a 40 kg pendulum.
• This is a coherent reduction-to-practice chain and is valuable for enablement. The uncertainty reporting, however, is incomplete: three cubes, three cylinders and four beams were cast per mix, but the impact tables do not report N1/N2 dispersion, and only one barrier per mix was cast.
• The deck therefore treats measured ratios as experimental observations, not as statistically generalized performance guarantees.
""")
    return slide


# ------------------------------------------------------------- reordering ----
def move_slide(prs, from_index, to_index):
    sldIdLst = prs.slides._sldIdLst
    slides = list(sldIdLst)
    sldIdLst.remove(slides[from_index])
    sldIdLst.insert(to_index, slides[from_index])


def renumber_footers(prs):
    for i, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if not shape.has_text_frame or shape.left is None:
                continue
            text = shape.text_frame.text.strip()
            if re.fullmatch(r"\d{1,2}", text) and shape.left > Inches(11.5) and shape.top > Inches(6.9):
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        r.text = f"{i:02d}"
                        break
                    break


def main():
    for path in (DECK, ARTICLE, LOGO, HERO):
        if not path.exists():
            raise FileNotFoundError(path)
    BUILD.mkdir(exist_ok=True)
    extract_media()
    build_panels()

    prs = Presentation(str(DECK))

    replace_title_picture(prs)

    build_background_slide(prs)                 # appended at the end
    move_slide(prs, len(prs.slides._sldIdLst) - 1, 1)   # then moved to position 2

    # "Methods overview" is now one slide later than it was.
    methods_index = None
    for i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip().upper() == "METHODS OVERVIEW":
                methods_index = i
                break
        if methods_index is not None:
            break
    if methods_index is None:
        raise RuntimeError("Methods overview slide not found.")
    rebuild_methods_slide(prs, methods_index)

    renumber_footers(prs)
    prs.save(str(DECK))

    # python-pptx re-serialises PowerPoint Morph transitions with an invalid
    # empty default namespace on mc:Fallback, which makes PowerPoint refuse to
    # open the file. Repair the saved package before handing it over.
    from repair_pptx import repair, verify
    stats = repair(DECK)
    verify(DECK)
    print(f"updated: {DECK}  ({len(prs.slides)} slides); "
          f"repaired {stats['fallback']} mc:Fallback, {stats['notes']} notes pages")


if __name__ == "__main__":
    main()
