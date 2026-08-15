#!/usr/bin/env python3
"""Revise the user-edited PPTX into the final pre-filing patent-approval deck.

The user-edited root-level PPTX is the source of truth. This script preserves its
manual wording edits, adds the requested patent/background/claim material,
standardizes typography and charts, and writes a new final deliverable.
"""
from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_DATA_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE, MSO_PATTERN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_VERTICAL_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "IITBBS_Impact_Dissipating_Crash_Barrier_Internal_Confidential.pptx"
OUTPUT = ROOT / "deliverables" / "IITBBS_Impact_Dissipating_Crash_Barrier_Patent_Approval_Final.pptx"
ARTICLE = ROOT / "Al-Amir_Research Article_R1.docx"
HERO = ROOT / "assets" / "crash_barrier_hud_hero.png"
BUILD = ROOT / ".build_patent_revision"
MEDIA = BUILD / "article_media"
PULSE_GIF = BUILD / "row_pulse.gif"
NOTES_TEMPLATE_SLIDE = None

sys.path.insert(0, str(ROOT / "scripts"))
import generate_patent_decks as g  # noqa: E402

g.FONT_HEAD = "Tahoma"
g.FONT_BODY = "Tahoma"
TAHOMA = "Tahoma"
BLACK = "000000"
NAVY = "17365D"
BLUE = "2E6F9E"
CYAN = "00A6C8"
TEAL = "2A9D8F"
GREEN = "5A8F62"
ORANGE = "F4A261"
RED = "C14953"
MAGENTA = "B5179E"
AMBER = "D99A27"
LIGHT_BLUE = "EAF1F6"
LIGHT_TEAL = "E8F4F2"
LIGHT_ORANGE = "FBF1E4"
LIGHT_RED = "F8E9EC"
WHITE = "FFFFFF"
GRID = "CCD6DE"
STATUS = "CONFIDENTIAL • PRE-FILING IITBBS IPR COMMITTEE EVALUATION • NOT YET FILED"

MIXES = ["NWC", "LWC00", "LWC05", "LWC10", "LWC15"]
N1_TRIALS = [[2, 2, 1], [0, 1, 1], [4, 5, 5], [13, 15, 17], [38, 30, 37]]
N2_TRIALS = [[4, 4, 3], [1, 2, 2], [17, 19, 24], [44, 49, 41], [238, 185, 240]]
N1_MEAN = [statistics.mean(x) for x in N1_TRIALS]
N2_MEAN = [statistics.mean(x) for x in N2_TRIALS]
N1_SD = [statistics.stdev(x) for x in N1_TRIALS]
N2_SD = [statistics.stdev(x) for x in N2_TRIALS]


def rgb(hex_value: str) -> RGBColor:
    return g.rgb(hex_value)


def delete_shape(shape) -> None:
    element = shape._element
    element.getparent().remove(element)


def ensure_notes_body(slide) -> None:
    """PowerPoint-authored source decks may omit placeholders on Python-added notes slides."""
    if slide.notes_slide.notes_text_frame is not None:
        return
    if NOTES_TEMPLATE_SLIDE is None:
        return
    from copy import deepcopy
    template_body = None
    for shape in NOTES_TEMPLATE_SLIDE.notes_slide.shapes:
        if shape.is_placeholder and str(shape.placeholder_format.type).startswith("BODY"):
            template_body = shape._element
            break
    if template_body is None:
        return
    sp_tree = slide.notes_slide._element.cSld.spTree
    sp_tree.append(deepcopy(template_body))


def add_notes_safe(slide, text: str) -> None:
    ensure_notes_body(slide)
    tf = slide.notes_slide.notes_text_frame
    if tf is None:
        return
    tf.clear(); tf.text = text.strip()


def extract_media() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    with ZipFile(ARTICLE) as zf:
        for name in zf.namelist():
            if name.startswith("word/media/"):
                (MEDIA / Path(name).name).write_bytes(zf.read(name))


def make_material_collage() -> Path:
    dst = BUILD / "materials_collage.jpg"
    a = Image.open(MEDIA / "image1.jpeg").convert("RGB")
    b = Image.open(MEDIA / "image3.jpeg").convert("RGB")
    canvas = Image.new("RGB", (1000, 520), "white")
    for im, x in [(a, 0), (b, 500)]:
        im.thumbnail((480, 430), Image.Resampling.LANCZOS)
        canvas.paste(im, (x + (500-im.width)//2, 20 + (430-im.height)//2))
    d = ImageDraw.Draw(canvas)
    d.text((190, 466), "SFA", fill=(23,54,93))
    d.text((665, 466), "Hooked steel fibres", fill=(23,54,93))
    canvas.save(dst, quality=93)
    return dst


def make_pulse_gif() -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    frames = []
    width, height = 1400, 90
    for i in range(28):
        phase = (1 - math.cos(2 * math.pi * i / 27)) / 2
        margin = int(14 - 8 * phase)
        border = int(3 + 3 * phase)
        im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        # Transparent interior; only the expanding amber/navy outline pulses.
        color = (217, 154, 39, 230)
        d.rounded_rectangle((margin, margin, width-margin-1, height-margin-1),
                            radius=12, outline=color, width=border)
        frames.append(im)
    frames[0].save(PULSE_GIF, save_all=True, append_images=frames[1:], duration=80,
                   loop=0, disposal=2, transparency=0)
    return PULSE_GIF


def slide_id_element_map(prs: Presentation):
    result = {}
    for sld_id in prs.slides._sldIdLst:
        slide = prs.part.related_slide(sld_id.rId)
        result[id(slide)] = sld_id
    return result


def reorder_slides(prs: Presentation, ordered_slides) -> None:
    mapping = slide_id_element_map(prs)
    lst = prs.slides._sldIdLst
    for item in list(lst):
        lst.remove(item)
    for slide in ordered_slides:
        lst.append(mapping[id(slide)])


def remove_body(slide) -> None:
    for sh in list(slide.shapes):
        top = sh.top / 914400
        if 1.12 < top < 7.0:
            delete_shape(sh)


def remove_sources(slide) -> None:
    for sh in list(slide.shapes):
        if getattr(sh, "has_text_frame", False):
            text = sh.text.strip().lower()
            if text.startswith("source:"):
                delete_shape(sh)


def add_header_footer(prs, title, section, slide_no="00"):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    g.add_header(slide, title, section, int(slide_no), STATUS)
    return slide


def add_barrier_icon(slide, kind: str, x: float, y: float, color: str) -> None:
    if kind == "flexible":
        for dx in [0.12, 0.70, 1.28]:
            g.add_line(slide, x+dx, y+0.05, x+dx, y+0.62, color, 2.0)
        for dy in [0.20, 0.36, 0.52]:
            g.add_line(slide, x+0.08, y+dy, x+1.33, y+dy, color, 1.3)
    elif kind == "semi":
        for dx in [0.16, 0.76, 1.34]:
            g.add_line(slide, x+dx, y+0.16, x+dx, y+0.65, color, 2.0)
        # W-beam represented by two offset diagonal bands.
        g.add_line(slide, x+0.04, y+0.24, x+1.42, y+0.46, color, 4.0)
        g.add_line(slide, x+0.04, y+0.43, x+1.42, y+0.24, color, 4.0)
    else:
        pts = [(x+0.18, y+0.66), (x+0.34, y+0.30), (x+0.55, y+0.18),
               (x+0.55, y+0.04), (x+1.03, y+0.04), (x+1.03, y+0.18),
               (x+1.24, y+0.30), (x+1.40, y+0.66)]
        shp = slide.shapes.add_freeform(Inches(pts[0][0]), Inches(pts[0][1])) if False else None
        # A trapezoid and base provide a clean editable New Jersey symbol.
        g.add_rect(slide, x+0.48, y+0.06, 0.52, 0.40, color, color, radius=False, line_width=0)
        trap = slide.shapes.add_shape(MSO_SHAPE.TRAPEZOID, Inches(x+0.18), Inches(y+0.38),
                                      Inches(1.12), Inches(0.32))
        trap.fill.solid(); trap.fill.fore_color.rgb = rgb(color)
        trap.line.color.rgb = rgb(color)


def add_background_slide(prs: Presentation):
    slide = add_header_footer(prs, "Background: crash barriers and material rationale", "Background")
    # Barrier taxonomy.
    g.add_text(slide, 0.68, 1.24, 3.55, 0.30, "CRASH-BARRIER TAXONOMY AND USE", 12, NAVY, True, TAHOMA, margin=0)
    types = [
        ("flexible", "Flexible / cable", "Large deflection; open medians; energy absorbed by system movement", BLUE),
        ("semi", "Semi-rigid / W-beam", "Moderate deflection; roadside and median protection; repair after impact", TEAL),
        ("rigid", "Rigid / concrete", "Near-zero working width; bridges, medians and high-containment locations", ORANGE),
    ]
    for i, (kind, title, body, colr) in enumerate(types):
        y = 1.66 + i*1.10
        g.add_rect(slide, 0.68, y, 3.55, 0.96, WHITE, GRID, radius=False, line_width=0.6)
        add_barrier_icon(slide, kind, 0.82, y+0.12, colr)
        g.add_text(slide, 2.35, y+0.10, 1.65, 0.25, title, 10.5, NAVY, True, TAHOMA, margin=0)
        g.add_text(slide, 2.35, y+0.39, 1.65, 0.47, body, 10, BLACK, False, TAHOMA, margin=0)
    g.add_rect(slide, 0.68, 5.12, 3.55, 0.75, LIGHT_BLUE, BLUE, radius=False, line_width=0.6)
    g.add_text(slide, 0.86, 5.28, 3.18, 0.44,
               "Primary function: contain, redirect and shield vehicles from opposing traffic, edges and fixed hazards.",
               10, BLACK, True, TAHOMA, margin=0)

    # Commercial rigid barrier versus invention.
    g.add_text(slide, 4.45, 1.24, 4.15, 0.30, "COMMERCIAL RIGID BARRIER VS PROPOSED MATERIAL", 12, NAVY, True, TAHOMA, margin=0)
    compare = [
        ["Attribute", "Conventional RC", "Proposed LWC15"],
        ["Reported density", "≈2,400–2,466 kg/m³", "1,987 kg/m³"],
        ["Dissipation mode", "Vehicle deformation + brittle cracking", "SFA crushing + fibre pull-out"],
        ["Fragmentation", "Large local fragments possible", "Finer/dispersed debris observed*"],
        ["Strength", "M40 class", "55.4 MPa at 28 d"],
        ["Validation", "Mature/full-scale systems", "Laboratory + one-third-scale proof"],
    ]
    g.add_table(slide, 4.45, 1.64, 4.15, 3.52, compare, [1.25, 1.50, 1.50],
                font_size=10, first_col_left=True, highlight_rows={2: LIGHT_ORANGE, 3: LIGHT_TEAL})
    g.add_rect(slide, 4.45, 5.28, 4.15, 0.59, LIGHT_RED, RED, radius=False, line_width=0.6)
    g.add_text(slide, 4.63, 5.41, 3.79, 0.35,
               "*Qualitative; full-scale containment, ASI/THIV and debris velocity remain untested.",
               10, RED, True, TAHOMA, margin=0)

    # Circular materials and geopolymer context.
    g.add_text(slide, 8.83, 1.24, 3.84, 0.30, "MATERIAL EDGE AND LOW-CARBON CONTEXT", 12, NAVY, True, TAHOMA, margin=0)
    g.add_text(slide, 8.83, 1.63, 3.84, 0.24, "SFA versus crushed stone (experimental inputs)", 10.5, NAVY, True, TAHOMA, margin=0)
    # Specific gravity bars.
    g.add_text(slide, 8.83, 1.98, 1.20, 0.20, "Specific gravity", 10, BLACK, True, TAHOMA, margin=0)
    for j, (lab, val, colr) in enumerate([("SFA", 1.43, TEAL), ("Stone", 2.73, NAVY)]):
        yy = 2.24 + j*0.34
        g.add_text(slide, 8.83, yy, 0.55, 0.18, lab, 10, BLACK, False, TAHOMA, margin=0)
        g.add_rect(slide, 9.44, yy+0.02, 1.65*(val/2.73), 0.16, colr, colr, radius=False, line_width=0)
        g.add_text(slide, 11.20, yy, 0.60, 0.18, f"{val:.2f}", 10, BLACK, True, TAHOMA, margin=0)
    g.add_text(slide, 8.83, 2.96, 1.20, 0.20, "Water absorption", 10, BLACK, True, TAHOMA, margin=0)
    for j, (lab, val, colr) in enumerate([("SFA", 18.0, ORANGE), ("Stone", 1.38, BLUE)]):
        yy = 3.22 + j*0.34
        g.add_text(slide, 8.83, yy, 0.55, 0.18, lab, 10, BLACK, False, TAHOMA, margin=0)
        g.add_rect(slide, 9.44, yy+0.02, max(0.12, 1.65*(val/18.0)), 0.16, colr, colr, radius=False, line_width=0)
        g.add_text(slide, 11.20, yy, 0.72, 0.18, f"{val:.2f}%", 10, BLACK, True, TAHOMA, margin=0)
    g.add_text(slide, 8.83, 3.93, 3.62, 0.45,
               "Edge: lower mass and internal damping. Trade-off: high absorption and lower aggregate toughness require moisture/workability control.",
               10, BLACK, False, TAHOMA, margin=0)

    g.add_text(slide, 8.83, 4.50, 3.65, 0.23, "Geopolymer efficiency context—not the present binder", 10.5, NAVY, True, TAHOMA, margin=0)
    g.add_text(slide, 8.83, 4.83, 0.70, 0.18, "OPC", 10, BLACK, True, TAHOMA, margin=0)
    g.add_rect(slide, 9.52, 4.83, 2.35, 0.18, NAVY, NAVY, radius=False, line_width=0)
    g.add_text(slide, 11.95, 4.80, 0.50, 0.22, "100", 10, BLACK, True, TAHOMA, margin=0)
    g.add_text(slide, 8.83, 5.15, 0.70, 0.18, "GPC", 10, BLACK, True, TAHOMA, margin=0)
    g.add_rect(slide, 9.52, 5.15, 2.35*0.91, 0.18, TEAL, TEAL, radius=False, line_width=0)
    g.add_text(slide, 11.95, 5.12, 0.50, 0.22, "91", 10, BLACK, True, TAHOMA, margin=0)
    g.add_text(slide, 8.83, 5.48, 3.65, 0.50,
               "Relative CO₂-e index from Turner & Collins: 9% lower for GPC. Published outcomes are system-dependent. Present patent mix is OPC–GGBS, not geopolymer; product LCA is pending.",
               10, RED, True, TAHOMA, margin=0)
    g.add_source(slide, 0.72, 6.40, 11.90,
                 "Zain & Mohammed (2015); Turner & Collins (2013), doi:10.1016/j.conbuildmat.2013.01.023; Habert et al. (2011), doi:10.1016/j.jclepro.2011.03.012; ACI 213R / ASTM C567.",
                 size=10)
    add_notes_safe(slide, """
BACKGROUND — speaking points

• Crash barriers are flexible, semi-rigid or rigid according to their working width and energy-management mechanism. Cable systems dissipate energy through large movement; W-beams combine deformation and redirection; concrete barriers are selected where working width is restricted and durable containment is needed.
• Commercial concrete barriers are strong and low-maintenance, but their high stiffness means that collision energy is largely managed by vehicle deformation and local concrete fracture. The proposed material adds internal dissipation through porous aggregate crushing and fibre pull-out while retaining M40-plus strength.
• SFA has approximately half the specific gravity of crushed stone, which supports lower self-weight. Its 18% absorption and higher aggregate-impact value are not pure advantages: they demand moisture conditioning, workability control and quality assurance.
• Geopolymer concrete is shown only as wider low-carbon background. Turner and Collins found a 9% CO2-equivalent reduction in a comprehensive case, while other studies vary substantially. Our tested patent embodiment contains OPC and GGBS and must not be called geopolymer concrete. Its environmental claim requires a product-specific LCA.
""")
    return slide


def rebuild_methods(slide) -> None:
    remove_body(slide)
    g.add_text(slide, 0.70, 1.22, 11.85, 0.30,
               "Five linked experimental stages establish composition, response and application-scale proof.",
               11, NAVY, True, TAHOMA, margin=0)
    materials_img = make_material_collage()
    panels = [
        ("1  MATERIALS", materials_img, "OPC, GGBS, SFA and hooked fibres", "XRF • physical properties • absorption"),
        ("2  MIX DESIGN", MEDIA / "image4.png", "NWC + LWC00/05/10/15", "ACI 211.2 / IS 10262 • five formulations"),
        ("3  STATIC TESTS", MEDIA / "image9.jpeg", "Slump, density, compression, split tension", "3 cubes + 3 cylinders per mix stated"),
        ("4  PRISM IMPACT", MEDIA / "image5.jpeg", "N₁, N₂, E₁, E₂ and displacement", "Four beams reportedly cast per mix"),
        ("5  BARRIER MODEL", MEDIA / "image8.jpeg", "1:3 New Jersey pendulum impact", "1 NWC + 1 LWC15 barrier"),
    ]
    for i, (title, img, body, evidence) in enumerate(panels):
        x = 0.65 + i*2.52
        g.add_rect(slide, x, 1.68, 2.28, 4.72, WHITE, GRID, radius=False, line_width=0.7)
        g.add_rect(slide, x, 1.68, 2.28, 0.42, NAVY, NAVY, radius=False, line_width=0)
        g.add_text(slide, x+0.10, 1.78, 2.08, 0.22, title, 10, WHITE, True, TAHOMA,
                   align=PP_ALIGN.CENTER, margin=0)
        g.add_picture_contain(slide, img, x+0.10, 2.20, 2.08, 1.58, f"methods_{i}")
        g.add_text(slide, x+0.14, 3.95, 2.00, 0.68, body, 10.5, NAVY, True, TAHOMA,
                   align=PP_ALIGN.CENTER, valign=MSO_VERTICAL_ANCHOR.MIDDLE, margin=0)
        g.add_rect(slide, x+0.12, 4.78, 2.04, 1.08, LIGHT_BLUE if i % 2 == 0 else LIGHT_TEAL,
                   GRID, radius=False, line_width=0.5)
        g.add_text(slide, x+0.22, 4.96, 1.84, 0.72, evidence, 10, BLACK, False, TAHOMA,
                   align=PP_ALIGN.CENTER, valign=MSO_VERTICAL_ANCHOR.MIDDLE, margin=0)
        if i < 4:
            g.add_chevron(slide, x+2.31, 3.66, 0.17, 0.32, GRID)
    g.add_rect(slide, 0.72, 6.53, 11.86, 0.32, LIGHT_RED, RED, radius=False, line_width=0.5)
    g.add_text(slide, 0.90, 6.61, 11.50, 0.18,
               "Evidence hierarchy: material/static tests → repeated-impact screening → preliminary barrier-scale validation.",
               10, RED, True, TAHOMA, align=PP_ALIGN.CENTER, margin=0)


def add_claim_range_slide(prs: Presentation):
    slide = add_header_footer(prs, "Tested experimental claim window: LWC05–LWC15", "Proposed claim range")
    g.add_text(slide, 0.72, 1.22, 11.85, 0.28,
               "Proposed experimental window—valid only for the three tested embodiments in this presentation; not a legal claim.",
               10.5, RED, True, TAHOMA, margin=0)
    composition = [
        ["Constituent / parameter", "LWC05", "LWC10", "LWC15", "Test-supported window"],
        ["OPC (kg/m³)", "422.4", "422.4", "422.4", "422.4 fixed"],
        ["GGBS (kg/m³)", "105.6", "105.6", "105.6", "105.6 fixed; 20% binder"],
        ["Fine aggregate (kg/m³)", "466.46", "466.46", "466.46", "466.46 fixed"],
        ["SFA coarse aggregate (kg/m³)", "596.31", "596.31", "596.31", "596.31; 100% coarse replacement"],
        ["Hooked steel fibre (kg/m³)", "39.25", "78.50", "117.80", "39.25–117.80 (0.5–1.5 vol%)"],
        ["PCE (kg/m³)", "2.79", "2.79", "2.79", "2.79 fixed"],
    ]
    g.add_table(slide, 0.72, 1.62, 11.88, 2.62, composition,
                [2.65, 1.20, 1.20, 1.20, 3.05], font_size=10, first_col_left=True,
                highlight_rows={5: LIGHT_ORANGE})
    performance = [
        ["Performance response", "LWC05", "LWC10", "LWC15", "Observed range"],
        ["Reported density (kg/m³)", "1,923", "1,951", "1,987", "1,923–1,987"],
        ["28 d compression (MPa)", "53.7", "56.8", "55.4", "53.7–56.8"],
        ["Split tension (MPa)", "4.77", "5.92", "7.60", "4.77–7.60"],
        ["Failure energy E₂ (N·m)", "264.87", "595.96", "2,927.81", "264.87–2,927.81"],
        ["Cost / E₂ [₹/(N·m)]", "31.47", "20.57", "5.53", "5.53–31.47"],
    ]
    g.add_table(slide, 0.72, 4.47, 11.88, 1.72, performance,
                [2.65, 1.20, 1.20, 1.20, 3.05], font_size=10, first_col_left=True,
                highlight_rows={4: LIGHT_TEAL, 5: LIGHT_BLUE})
    g.add_rect(slide, 0.72, 6.34, 11.88, 0.44, LIGHT_RED, RED, radius=False, line_width=0.6)
    g.add_text(slide, 0.92, 6.44, 11.48, 0.24,
               "Claim boundary: no interpolation beyond the tested range; extra-water protocol and density basis must be reconciled before drafting.",
               10, RED, True, TAHOMA, align=PP_ALIGN.CENTER, margin=0)
    add_notes_safe(slide, """
PROPOSED EXPERIMENTAL CLAIM WINDOW — speaking points

• This window is derived only from LWC05, LWC10 and LWC15; NWC and unreinforced LWC00 are deliberately excluded from the proposed reinforced-product range.
• The constant matrix contains 422.4 kg/m3 OPC, 105.6 kg/m3 GGBS, 596.31 kg/m3 SFA and 466.46 kg/m3 fine aggregate. The experimentally varied parameter is hooked steel fibre from 0.5 to 1.5 percent by concrete volume.
• The three tested embodiments preserve compressive strength above M40 while producing a tunable impact-energy range from about 265 to 2,928 N-m.
• This is an evidence-support map, not final legal claim language. Counsel must determine defensible endpoints and fallback positions. Intermediate dosages were not separately tested, and the water/density records must be corrected before filing.
""")
    return slide


def add_comparative_claims_slide(prs: Presentation):
    slide = add_header_footer(prs, "Evidence-based claims relative to published approaches", "Comparative claims")
    top = [
        ["Tested product tier", "28 d compression", "Prism E₂", "E₂ / NWC", "Cost / E₂", "Potential commercial role"],
        ["LWC05", "53.7 MPa", "264.87 N·m", "5.0×", "₹31.47/(N·m)", "Moderate-impact / lower fibre input"],
        ["LWC10", "56.8 MPa", "595.96 N·m", "11.3×", "₹20.57/(N·m)", "Balanced strength–impact tier"],
        ["LWC15", "55.4 MPa", "2,927.81 N·m", "55.3×", "₹5.53/(N·m)", "Highest tested impact-demand tier"],
    ]
    g.add_table(slide, 0.72, 1.34, 11.88, 1.78, top,
                [1.50, 1.55, 1.55, 1.15, 1.40, 3.25], font_size=10,
                first_col_left=True, highlight_rows={3: LIGHT_TEAL})
    lit = [
        ["Published approach", "Published benchmark", "Specific distinction supported here", "Citation"],
        ["Steel-fibre rubcrete barrier", "Up to 3× impact energy vs conventional concrete", "Within-study prism ratios: 5.0×, 11.3× and 55.3× for LWC05/10/15", "Raj et al. (2020)"],
        ["AAS no-fines safety concrete", "≈20 MPa with high absorption / fragmentability", "53.7–56.8 MPa across proposed reinforced window", "Shen et al. (2014)"],
        ["Steel-fibre lightweight concrete", "Improved static and dynamic response", "Specific SFA–GGBS–hooked-fibre barrier embodiment and 1:3 proof", "Wang & Wang (2013)"],
        ["Lightweight barrier elements", "Application concept predates this work", "Composition, dual mechanism, tested range and cost/E₂ package are narrower", "Bonin et al. (2004)"],
    ]
    g.add_table(slide, 0.72, 3.40, 11.88, 2.37, lit,
                [2.00, 2.45, 5.00, 1.55], font_size=10, first_col_left=True,
                highlight_rows={1: LIGHT_ORANGE, 2: LIGHT_BLUE})
    g.add_rect(slide, 0.72, 5.97, 11.88, 0.48, LIGHT_BLUE, BLUE, radius=False, line_width=0.6)
    g.add_text(slide, 0.94, 6.07, 11.44, 0.28,
               "Claim utility: fibre dosage provides a three-tier energy-absorption product family; cost per absorbed N·m improves as the tested impact tier increases.",
               10, NAVY, True, TAHOMA, align=PP_ALIGN.CENTER, margin=0)
    g.add_rect(slide, 0.72, 6.52, 11.88, 0.28, LIGHT_RED, RED, radius=False, line_width=0.5)
    g.add_text(slide, 0.94, 6.57, 11.44, 0.18,
               "Cross-study values are directional only because specimen geometry and impact protocols differ.",
               10, RED, True, TAHOMA, align=PP_ALIGN.CENTER, margin=0)
    g.add_source(slide, 0.72, 6.82, 11.88,
                 "Published comparators: Raj et al. (2020); Shen et al. (2014); Wang & Wang (2013); Bonin et al. (2004). Full details and DOIs are listed in the references.",
                 size=10)
    add_notes_safe(slide, """
COMPARATIVE CLAIMS — speaking points

• The primary claim supported by our own data is a tunable reinforced lightweight-concrete product family. LWC05, LWC10 and LWC15 all retain M40-plus strength, but span progressively higher repeated-impact energy and lower cost per absorbed N-m.
• LWC05 is the moderate-impact option, LWC10 provides the highest compressive strength and a balanced impact tier, and LWC15 is the highest tested energy-absorption option.
• Published rubcrete work reported up to three times conventional impact energy. Our within-study prism ratios are larger, but no direct cross-paper superiority claim should be made because test configurations differ.
• Shen's safety concrete achieved energy absorption at around 20 MPa. Our specific distinction is structural-grade strength together with impact endurance, a defined composition window and scaled-barrier validation.
• The cost-to-impact metric converts the materials premium into engineering utility: LWC15 costs more per cubic metre, yet has the lowest tested cost per unit of absorbed prism energy.
""")
    return slide


def add_reference_line(slide, chart_shape, value, axis_max, color, dash="dash") -> None:
    left = chart_shape.left/914400 + 0.62
    top = chart_shape.top/914400 + 0.62
    right = (chart_shape.left+chart_shape.width)/914400 - 0.20
    bottom = (chart_shape.top+chart_shape.height)/914400 - 0.64
    y = bottom - (value/axis_max)*(bottom-top)
    ln = g.add_line(slide, left, y, right, y, color, 1.45, dash=(dash != "solid"))
    if dash == "dot":
        ln.line.dash_style = MSO_LINE_DASH_STYLE.ROUND_DOT
    elif dash == "dashdot":
        ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH_DOT


def add_error_bars(slide, chart_shape, means_by_series, sds_by_series, axis_max, colors) -> None:
    left = chart_shape.left/914400 + 0.67
    top = chart_shape.top/914400 + 0.58
    right = (chart_shape.left+chart_shape.width)/914400 - 0.22
    bottom = (chart_shape.top+chart_shape.height)/914400 - 0.68
    plot_w, plot_h = right-left, bottom-top
    ncat = len(means_by_series[0]); nser = len(means_by_series)
    group = plot_w/ncat
    offsets = [-0.13, 0.13] if nser == 2 else [0]
    for si, (means, sds, color) in enumerate(zip(means_by_series, sds_by_series, colors)):
        for i, (mean, sd) in enumerate(zip(means, sds)):
            x = left + group*(i+0.5) + offsets[si]
            y_hi = bottom - min(axis_max, mean+sd)/axis_max*plot_h
            y_lo = bottom - max(0, mean-sd)/axis_max*plot_h
            g.add_line(slide, x, y_hi, x, y_lo, color, 1.2)
            g.add_line(slide, x-0.055, y_hi, x+0.055, y_hi, color, 1.2)
            g.add_line(slide, x-0.055, y_lo, x+0.055, y_lo, color, 1.2)


def format_chart(chart, chart_index=0) -> None:
    chart.font.name = TAHOMA
    chart.font.size = Pt(10)
    chart.font.color.rgb = rgb(BLACK)
    palette = ["0077B6", "00A6C8", "2A9D8F", "F4A261", "E76F51"]
    patterns = [MSO_PATTERN.WIDE_DOWNWARD_DIAGONAL, MSO_PATTERN.WIDE_UPWARD_DIAGONAL,
                MSO_PATTERN.DASHED_DOWNWARD_DIAGONAL, MSO_PATTERN.DIAGONAL_CROSS,
                MSO_PATTERN.DARK_UPWARD_DIAGONAL]
    for si, series in enumerate(chart.series):
        series.format.line.color.rgb = rgb(palette[si % len(palette)])
        for pi, point in enumerate(series.points):
            f = point.format.fill
            f.patterned(); f.pattern = patterns[(pi+si) % len(patterns)]
            f.fore_color.rgb = rgb(palette[(pi + si*2) % len(palette)])
            f.back_color.rgb = rgb(WHITE)
            point.format.line.color.rgb = rgb(palette[(pi + si*2) % len(palette)])
    try:
        chart.category_axis.tick_labels.font.name = TAHOMA
        chart.category_axis.tick_labels.font.size = Pt(10)
        chart.category_axis.tick_labels.font.color.rgb = rgb(BLACK)
        chart.value_axis.tick_labels.font.name = TAHOMA
        chart.value_axis.tick_labels.font.size = Pt(10)
        chart.value_axis.tick_labels.font.color.rgb = rgb(BLACK)
        if chart.value_axis.has_title:
            tf = chart.value_axis.axis_title.text_frame
            for p in tf.paragraphs:
                for r in p.runs:
                    r.font.name = TAHOMA; r.font.size = Pt(11); r.font.color.rgb = rgb(BLACK)
    except Exception:
        pass
    if chart.has_legend:
        chart.legend.font.name = TAHOMA
        chart.legend.font.size = Pt(10)
        chart.legend.font.color.rgb = rgb(BLACK)
    for plot in chart.plots:
        if plot.has_data_labels:
            dl = plot.data_labels
            dl.font.name = TAHOMA; dl.font.size = Pt(11); dl.font.bold = True
            dl.font.color.rgb = rgb(BLACK)
            dl.show_value = True


def update_impact_chart(slide) -> None:
    charts = [sh for sh in slide.shapes if getattr(sh, "has_chart", False)]
    if len(charts) < 2:
        return
    count_shape = charts[1]
    data = ChartData(); data.categories = MIXES
    data.add_series("First crack N₁", N1_MEAN)
    data.add_series("Failure N₂", N2_MEAN)
    count_shape.chart.replace_data(data)
    plot = count_shape.chart.plots[0]
    plot.has_data_labels = True
    plot.data_labels.show_value = True
    plot.data_labels.position = XL_DATA_LABEL_POSITION.OUTSIDE_END
    plot.data_labels.number_format = "0.0"
    format_chart(count_shape.chart)
    add_error_bars(slide, count_shape, [N1_MEAN, N2_MEAN], [N1_SD, N2_SD], 250, [CYAN, NAVY])
    g.add_rect(slide, 0.92, 6.27, 5.64, 0.33, LIGHT_RED, RED, radius=False, line_width=0.5)
    g.add_text(slide, 1.06, 6.35, 5.36, 0.18,
               "ACI 544 defines the test method; it gives no N₁/N₂/E₂ acceptance threshold.",
               10, RED, True, TAHOMA, align=PP_ALIGN.CENTER, margin=0)
    g.add_rect(slide, 7.52, 6.27, 4.68, 0.33, LIGHT_BLUE, BLUE, radius=False, line_width=0.5)
    g.add_text(slide, 7.66, 6.35, 4.40, 0.18, "Error bars: mean ± 1 sample SD; n = 3", 10, BLACK, True,
               TAHOMA, align=PP_ALIGN.CENTER, margin=0)


def add_standard_overlays(slide8, slide11, slide12, slide14) -> None:
    charts8 = [sh for sh in slide8.shapes if getattr(sh, "has_chart", False)]
    if len(charts8) >= 3:
        density, compression, tensile = charts8[:3]
        for sh in slide8.shapes:
            if getattr(sh, "has_text_frame", False) and sh.text.strip().startswith("Workability trade-off"):
                sh.text_frame.clear()
                sh.text_frame.paragraphs[0].text = (
                    "Workability: slump decreased from 165 to 87 mm; fibre dispersion and compaction are scale-up controls."
                )
        add_reference_line(slide8, density, 1920, 2700, BLUE, "dash")
        add_reference_line(slide8, density, 2000, 2700, RED, "solid")
        add_reference_line(slide8, density, 2400, 2700, "6B7280", "dot")
        add_reference_line(slide8, compression, 40, 65, RED, "solid")
        add_reference_line(slide8, compression, 48.25, 65, ORANGE, "dash")
        add_reference_line(slide8, tensile, 4.32, 9, BLUE, "dashdot")
        g.add_rect(slide8, 0.80, 6.34, 11.76, 0.55, WHITE, GRID, radius=False, line_width=0.6)
        g.add_text(slide8, 0.98, 6.42, 11.40, 0.38,
                   "Reference lines — Density: 1,920 ACI 213R equilibrium limit; 2,000 project target; 2,400 typical NWC (ASTM C567 basis unresolved). Compression: 40 MPa IRC:119 M40; 48.25 MPa IRC:44 target. Tensile: NWC baseline only.",
                   10, BLACK, False, TAHOMA, margin=0)
    charts11 = [sh for sh in slide11.shapes if getattr(sh, "has_chart", False)]
    if charts11:
        add_reference_line(slide11, charts11[0], 0.28, 1.0, BLUE, "dash")
        g.add_text(slide11, 0.90, 4.06, 1.15, 0.20, "NWC baseline", 10, BLACK, True, TAHOMA, margin=0)
    charts12 = [sh for sh in slide12.shapes if getattr(sh, "has_chart", False)]
    if len(charts12) >= 2:
        add_reference_line(slide12, charts12[1], 93.36, 185, BLUE, "dash")
        g.add_text(slide12, 10.90, 3.00, 1.18, 0.20, "NWC baseline", 10, BLACK, True, TAHOMA, margin=0)
    charts14 = [sh for sh in slide14.shapes if getattr(sh, "has_chart", False)]
    if len(charts14) >= 2:
        add_reference_line(slide14, charts14[0], 1373, 3100, BLUE, "dash")
        add_reference_line(slide14, charts14[1], 4.22, 15, BLUE, "dash")
        g.add_text(slide14, 8.05, 2.92, 1.20, 0.20, "NWC baseline", 10, BLACK, True, TAHOMA, margin=0)
        g.add_text(slide14, 11.28, 3.24, 1.20, 0.20, "NWC baseline", 10, BLACK, True, TAHOMA, margin=0)


def format_text_frame(tf, minimum=10, fixed=None, color_gray_to_black=True) -> None:
    for p in tf.paragraphs:
        for r in p.runs:
            r.font.name = TAHOMA
            if fixed is not None:
                r.font.size = Pt(fixed)
            elif r.font.size is None or r.font.size.pt < minimum:
                r.font.size = Pt(minimum)
            if color_gray_to_black:
                try:
                    c = tuple(r.font.color.rgb)
                    if max(c)-min(c) < 32 and 55 < sum(c)/3 < 245:
                        r.font.color.rgb = rgb(BLACK)
                except Exception:
                    pass


def enforce_tahoma(prs: Presentation) -> None:
    for slide in prs.slides:
        for sh in slide.shapes:
            if getattr(sh, "has_text_frame", False):
                format_text_frame(sh.text_frame, 10)
            if getattr(sh, "has_table", False):
                for row in sh.table.rows:
                    for cell in row.cells:
                        format_text_frame(cell.text_frame, 10)
            if getattr(sh, "has_chart", False):
                format_chart(sh.chart)
        if slide.has_notes_slide:
            format_text_frame(slide.notes_slide.notes_text_frame, 10)


def remove_internal_source_sections(slides) -> None:
    # Keep only source sections based on published/online materials.
    for key in ["synopsis", "mix", "static", "prism_results", "economic", "barrier_method", "barrier_results", "claim_map", "conclusion"]:
        remove_sources(slides[key])
    # Method overview: explicit user request to remove the source section entirely.
    remove_sources(slides["methods"])
    # Retain published mechanism papers, but remove internal disclosure attribution.
    remove_sources(slides["mechanism"])
    g.add_source(slides["mechanism"], 0.82, 6.69, 11.55,
                 "Wang & Wang (2013), doi:10.1016/j.conbuildmat.2012.09.016; Nadesan & Dinakar (2017), doi:10.1016/j.cscm.2017.09.005; Sahoo et al. (2020), doi:10.1016/j.cemconcomp.2020.103712.", size=10)
    # Dynamic-response mechanism references are published; experimental source label removed.
    remove_sources(slides["dynamic"])
    g.add_source(slides["dynamic"], 0.73, 6.43, 11.65,
                 "Mechanism context: Wang & Wang (2013); Gao et al. (1997), doi:10.1016/S0958-9465(97)00023-1; Sahoo et al. (2020).", size=10)
    # Impact method retains only the published standard basis.
    remove_sources(slides["impact_method"])
    g.add_source(slides["impact_method"], 0.73, 6.48, 11.65,
                 "ACI 544.2R-89, Measurement of Properties of Fiber Reinforced Concrete.", size=10)
    # Future-work standards are public; remove inventor-questionnaire wording.
    remove_sources(slides["future"])
    g.add_source(slides["future"], 0.73, 6.68, 11.65,
                 "Standards context: IRC:119-2015; EN 1317; AASHTO MASH. Timing is an author-proposed validation sequence.", size=10)


def replace_title_image(slide) -> None:
    # Remove old frame, apparatus picture and caption; retain logo.
    for sh in list(slide.shapes):
        if sh.name in {"Rectangle 13", "Picture 14", "TextBox 15"}:
            delete_shape(sh)
    # Rebalance the title column and create a landscape AI concept panel.
    for sh in slide.shapes:
        text = sh.text if getattr(sh, "has_text_frame", False) else ""
        if text.startswith("Novel concrete composition"):
            sh.width = Inches(6.25); sh.height = Inches(1.78)
            format_text_frame(sh.text_frame, 10)
            for p in sh.text_frame.paragraphs:
                for r in p.runs: r.font.size = Pt(27)
        elif text.startswith("Steel-fibre-reinforced"):
            sh.width = Inches(6.20)
        elif text.startswith("Haruna Al-Amir"):
            sh.width = Inches(6.25)
        elif text.startswith("School of Infrastructure"):
            sh.width = Inches(6.25)
        elif text.startswith("Status: not yet filed"):
            sh.width = Inches(5.78)
        elif sh.shape_type == 9 and abs(sh.top/914400 - 4.08) < 0.05:
            sh.width = Inches(6.10)
    frame = g.add_rect(slide, 7.28, 1.42, 5.46, 3.12, WHITE, GRID, radius=False, line_width=0.8)
    # Crop 16:9 image into matching frame while retaining road and HUD cutaway.
    img = Image.open(HERO).convert("RGB")
    dst = BUILD / "hero_cropped.jpg"
    target = (1400, 800)
    scale = max(target[0]/img.width, target[1]/img.height)
    resized = img.resize((int(img.width*scale), int(img.height*scale)), Image.Resampling.LANCZOS)
    left = (resized.width-target[0])//2; top = (resized.height-target[1])//2
    resized.crop((left, top, left+target[0], top+target[1])).save(dst, quality=94)
    slide.shapes.add_picture(str(dst), Inches(7.38), Inches(1.52), width=Inches(5.26), height=Inches(2.92))
    g.add_text(slide, 7.38, 4.66, 5.26, 0.26,
               "AI-generated concept visualization: containment • internal dissipation • controlled damage",
               10, BLACK, True, TAHOMA, align=PP_ALIGN.CENTER, margin=0)
    # Small technical callout under the image, using experimental claims only.
    g.add_rect(slide, 7.38, 5.05, 5.26, 0.78, LIGHT_BLUE, BLUE, radius=False, line_width=0.6)
    g.add_text(slide, 7.58, 5.20, 4.86, 0.50,
               "Design hypothesis\nPorous aggregate crushing + hooked-fibre pull-out → higher impact-energy dissipation",
               10, NAVY, True, TAHOMA, align=PP_ALIGN.CENTER, margin=0)


def add_pulse_to_gap(slide) -> None:
    gif = make_pulse_gif()
    slide.shapes.add_picture(str(gif), Inches(0.66), Inches(4.53), width=Inches(12.02), height=Inches(0.66))


def add_transitions(prs: Presentation) -> None:
    p_ns = "http://schemas.openxmlformats.org/presentationml/2006/main"
    for slide in prs.slides:
        root = slide._element
        for old in root.findall(f"{{{p_ns}}}transition"):
            root.remove(old)
        transition = OxmlElement("p:transition")
        transition.set("spd", "fast")
        transition.set("advClick", "1")
        transition.append(OxmlElement("p:fade"))
        # Schema order: cSld, clrMapOvr?, transition, timing...
        insert_at = 1
        if len(root) > 1 and root[1].tag == qn("p:clrMapOvr"):
            insert_at = 2
        root.insert(insert_at, transition)


def update_slide_numbers(prs: Presentation) -> None:
    for i, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if getattr(sh, "has_text_frame", False):
                text = sh.text.strip()
                if len(text) == 2 and text.isdigit() and sh.top/914400 > 6.9:
                    sh.text_frame.paragraphs[0].runs[0].text = f"{i:02d}"


def append_conclusion_notes(slide) -> None:
    tf = slide.notes_slide.notes_text_frame
    existing = tf.text.strip()
    detail = """

IPR DECISION TABLE — DETAILED REASONING

1. APPROVE PATENT FILING
Requirement: authorize a professional patentability/FTO search, claim drafting and filing before further disclosure.
Reason: the present record contains a specific composition, three reinforced embodiments, an unexpected repeated-impact response and a barrier-scale reduction to practice. Approval does not certify commercial safety; it preserves the opportunity to protect the integrated composition–process–barrier concept.

2. MAINTAIN CONFIDENTIALITY
Requirement: coordinate the submitted manuscript, presentations, industry discussions and data sharing with the IPR section until filing.
Reason: no patent has yet been filed. Public enabling disclosure may prejudice novelty in some jurisdictions. Exact formulations, process controls and claim ranges should therefore be shared externally only under IPR-approved conditions.

3. ENDORSE STAGED VALIDATION
Requirement: support replicated barrier tests, specimen-level uncertainty analysis, quantitative debris assessment, calibrated FE modelling and a standards-compliant full-scale crash programme.
Reason: material-level results are strong, but the barrier comparison uses one specimen per mix and does not measure vehicle containment, redirection, ASI or THIV. These tests are needed for certification and commercialization, not necessarily to establish initial patent utility.

4. ENABLE CONTROLLED TECHNOLOGY TRANSFER
Requirement: permit engagement with CRRI/NHAI, accredited crash-test facilities, precast producers and barrier manufacturers after filing or under appropriate confidentiality controls.
Reason: external partners provide facilities, manufacturing QA and field-validation capability unavailable at laboratory scale. Controlled engagement converts protected know-how into a certifiable product without premature disclosure.
"""
    tf.text = existing + detail


def build_references(slide1, slide2) -> None:
    refs = [
        "World Health Organization. (2023). Global Status Report on Road Safety 2023. https://www.who.int/publications/i/item/9789240086517",
        "UNEP. (2022). Sand and Sustainability: 10 Strategic Recommendations to Avert a Crisis. https://wedocs.unep.org/20.500.11822/38362",
        "U.S. Geological Survey. (2025). Mineral Commodity Summaries 2025—Cement. https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-cement.pdf",
        "International Energy Agency. (2023). Cement—Tracking Clean Energy Progress. https://www.iea.org/energy-system/industry/cement",
        "Reid, I., Carpenter, A.M., & Masili, A. (2020). Beneficial Uses of Coal Fly Ash. IEA CCC/303. ISBN 978-92-9029-626-3.",
        "IRC:119-2015. Guidelines for Traffic Safety Barriers. Indian Roads Congress, New Delhi.",
        "IRC:6-2016. Standard Specifications and Code of Practice for Road Bridges. Indian Roads Congress.",
        "IRC:44-2017. Guidelines for Cement Concrete Mix Design for Pavements. Indian Roads Congress.",
        "ACI 213R-14. Guide for Structural Lightweight-Aggregate Concrete. American Concrete Institute.",
        "ASTM C567/C567M-23. Standard Test Method for Determining Density of Structural Lightweight Concrete. doi:10.1520/C0567_C0567M-23.",
        "ACI 211.2-98. Standard Practice for Selecting Proportions for Structural Lightweight Concrete. American Concrete Institute.",
        "ACI 544.2R-89. Measurement of Properties of Fiber Reinforced Concrete. American Concrete Institute.",
        "IS 9142 (Part 2):2018. Artificial Lightweight Aggregates—Sintered Fly Ash Aggregate. Bureau of Indian Standards.",
        "Turner, L.K., & Collins, F.G. (2013). CO2-e emissions: geopolymer versus OPC concrete. Constr. Build. Mater., 43, 125–130. doi:10.1016/j.conbuildmat.2013.01.023.",
        "Habert, G., d’Espinose de Lacaillerie, J.B., & Roussel, N. (2011). Environmental evaluation of geopolymer concrete. J. Clean. Prod., 19, 1229–1238. doi:10.1016/j.jclepro.2011.03.012.",
        "Raj, A., Nagarajan, P., & Pallikkara, S.A. (2020). Application of fiber-reinforced rubcrete for crash barriers. J. Mater. Civ. Eng., 32, 04020358. doi:10.1061/(ASCE)MT.1943-5533.0003454.",
        "Shen, W. et al. (2014). Investigation on safety concrete for highway crash barriers. Constr. Build. Mater., 70, 394–398. doi:10.1016/j.conbuildmat.2014.07.060.",
        "Zain, M.F.M., & Mohammed, H.J. (2015). Concrete road barriers subjected to impact loads: an overview. Lat. Am. J. Solids Struct., 12, 1824–1858. doi:10.1590/1679-78251783.",
        "Wang, H.T., & Wang, L.C. (2013). Static and dynamic properties of steel-fibre lightweight concrete. Constr. Build. Mater., 38, 1146–1151. doi:10.1016/j.conbuildmat.2012.09.016.",
        "Sahoo, S., Selvaraju, A.K., & Suriya Prakash, S. (2020). Structural lightweight concrete with SFA and fibres. Cem. Concr. Compos., 113, 103712. doi:10.1016/j.cemconcomp.2020.103712.",
        "Nadesan, M.S., & Dinakar, P. (2017). Mix design and properties of fly-ash waste lightweight aggregates. Case Stud. Constr. Mater., 7, 336–347. doi:10.1016/j.cscm.2017.09.005.",
        "Kim, W. et al. (2019). Concrete barriers with novel shock absorbers under impact. Arch. Civ. Mech. Eng., 19, 657–671. doi:10.1016/j.acme.2019.01.004.",
        "Yang, J. et al. (2019). Crash performance of a movable median guardrail. Eng. Struct., 182, 459–472. doi:10.1016/j.engstruct.2018.12.090.",
        "Abid, S.R. et al. (2020). Repeated drop-weight impact tests on microsteel-fibre concrete. Heliyon, 6, e03198. doi:10.1016/j.heliyon.2020.e03198.",
        "Li, N., Park, B.B., & Lambert, J.H. (2018). Guardrails and fatal/severe freeway injuries. J. Transp. Saf. Secur., 10, 455–470. doi:10.1080/19439962.2017.1297970.",
        "Mohammed, H.J., & Zain, M.F.M. (2016). EPS concrete in a prototype concrete barrier. Constr. Build. Mater., 124, 312–342. doi:10.1016/j.conbuildmat.2016.07.105.",
        "Grzebieta, R.H. et al. (2005). Roadside Hazard and Barrier Crashworthiness Issues. Proc. 19th ESV Conference, Paper 05-0149-O.",
        "Bonin, G., Cantisani, G., Loprencipe, G., & Ranzo, A. (2004). Road safety barriers with short lightweight-concrete elements. Proc. II Int’l Congress SIIV.",
        "Xue, W. et al. (2025). Safety performance evaluation of a UHPC semi-assembled barrier. Applied Sciences, 15, 3156. doi:10.3390/app15063156.",
        "Pachocki, Ł., & Bruski, D. (2020). Modelling and validation of a TB41 concrete restraint-system crash test. Arch. Civ. Mech. Eng. doi:10.1007/s43452-020-00065-7.",
        "Elango, K.S. et al. (2021). Properties of lightweight concrete—a state-of-the-art review. Mater. Today Proc., 46, 4059–4062. doi:10.1016/j.matpr.2021.02.571.",
        "Gao, J., Suqa, W., & Morino, K. (1997). Steel-fibre-reinforced high-strength lightweight concrete. Cem. Concr. Compos., 19, 307–313. doi:10.1016/S0958-9465(97)00023-1.",
    ]
    numbered = [f"{i+1}. {r}" for i, r in enumerate(refs)]
    for slide, title, offset in [(slide1, "References: standards, datasets and sustainability", 0),
                                 (slide2, "References: peer-reviewed barrier and material studies", 16)]:
        # Retain header, logo and footer only.
        for sh in list(slide.shapes):
            top = sh.top/914400
            if 1.12 < top < 7.0:
                delete_shape(sh)
        # Update title and section label.
        for sh in slide.shapes:
            if getattr(sh, "has_text_frame", False):
                if sh.text.strip().upper() == "SOURCES": sh.text_frame.paragraphs[0].runs[0].text = "REFERENCES"
                elif sh.top/914400 < 1.05 and sh.width/914400 > 8 and not sh.text.strip().isdigit():
                    # Long title box; section label is much narrower.
                    if sh.text.strip() not in {"REFERENCES"}:
                        sh.text_frame.paragraphs[0].runs[0].text = title
        subset = numbered[offset:offset+16]
        left_refs, right_refs = subset[:8], subset[8:]
        for x, items in [(0.72, left_refs), (6.72, right_refs)]:
            box = slide.shapes.add_textbox(Inches(x), Inches(1.30), Inches(5.75), Inches(5.62))
            tf = box.text_frame; tf.clear(); tf.word_wrap = True
            tf.margin_left = tf.margin_right = Inches(0.04)
            tf.margin_top = tf.margin_bottom = Inches(0.02)
            for j, item in enumerate(items):
                p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                p.text = item; p.space_after = Pt(5); p.line_spacing = 1.0
                pPr = p._p.get_or_add_pPr(); pPr.set("marL", str(228600)); pPr.set("hanging", str(228600))
                for r in p.runs:
                    r.font.name = TAHOMA; r.font.size = Pt(12); r.font.color.rgb = rgb(BLACK)


def main() -> None:
    global NOTES_TEMPLATE_SLIDE
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)
    if not HERO.exists():
        raise FileNotFoundError(HERO)
    extract_media(); BUILD.mkdir(parents=True, exist_ok=True)
    prs = Presentation(INPUT)
    original = list(prs.slides)
    if len(original) != 19:
        raise ValueError(f"Expected the 19-slide user-edited deck, found {len(original)} slides")
    slides = {
        "title": original[0], "synopsis": original[1], "global": original[2], "gap": original[3],
        "mechanism": original[4], "methods": original[5], "mix": original[6], "static": original[7],
        "impact_method": original[8], "prism_results": original[9], "dynamic": original[10],
        "economic": original[11], "barrier_method": original[12], "barrier_results": original[13],
        "claim_map": original[14], "future": original[15], "conclusion": original[16],
        "refs1": original[17], "refs2": original[18],
    }
    NOTES_TEMPLATE_SLIDE = slides["synopsis"]

    background = add_background_slide(prs)
    claim_range = add_claim_range_slide(prs)
    comparative_claims = add_comparative_claims_slide(prs)

    replace_title_image(slides["title"])
    remove_internal_source_sections(slides)
    rebuild_methods(slides["methods"])

    # Study synopsis is deliberately moved to position 15.
    desired = [
        slides["title"], background, slides["global"], slides["gap"], slides["mechanism"],
        slides["methods"], slides["mix"], slides["static"], slides["impact_method"],
        slides["prism_results"], slides["dynamic"], slides["economic"],
        slides["barrier_method"], slides["barrier_results"], slides["synopsis"],
        slides["claim_map"], claim_range, comparative_claims, slides["future"],
        slides["conclusion"], slides["refs1"], slides["refs2"],
    ]
    reorder_slides(prs, desired)

    # Standard lines, replicate variability, patterns and chart typography.
    update_impact_chart(slides["prism_results"])
    add_standard_overlays(slides["static"], slides["dynamic"], slides["economic"], slides["barrier_results"])
    for slide in prs.slides:
        for sh in slide.shapes:
            if getattr(sh, "has_chart", False):
                format_chart(sh.chart)

    add_pulse_to_gap(slides["gap"])
    append_conclusion_notes(slides["conclusion"])
    build_references(slides["refs1"], slides["refs2"])
    update_slide_numbers(prs)
    add_transitions(prs)
    enforce_tahoma(prs)

    # Explicitly force the two reference slides to Tahoma 12 after global formatting.
    for slide in [slides["refs1"], slides["refs2"]]:
        for sh in slide.shapes:
            if getattr(sh, "has_text_frame", False) and 1.12 < sh.top/914400 < 7.0:
                format_text_frame(sh.text_frame, fixed=12, color_gray_to_black=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
