#!/usr/bin/env python3
"""
ULTRON — generates the dataset / research-gap document (.docx) for C1, C4, C5.

Contains, for each dataset:
  - the data table (copy-paste ready for Excel)
  - the finished chart (embedded PNG)
  - step-by-step MS Excel instructions to rebuild that chart

Run:  .venv/bin/python scripts/generate_data_doc.py
Out:  results/C1_C4_C5_Data_and_Research_Gaps.docx
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
OUT = ROOT / "results" / "C1_C4_C5_Data_and_Research_Gaps.docx"

NAVY = RGBColor(0x1F, 0x3B, 0x5C)
INK = RGBColor(0x16, 0x20, 0x2B)
GREY = RGBColor(0x5D, 0x6B, 0x7A)
GREEN = RGBColor(0x0F, 0x7B, 0x4F)
RED = RGBColor(0xB3, 0x26, 0x1E)
AMBER = RGBColor(0xB8, 0x86, 0x0B)


def cell_bg(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexc); tcPr.append(shd)


def field(par, instr):
    r = par.add_run()
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "begin"); r._r.append(e)
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
    it.text = instr; r._r.append(it)
    for v in ("separate", "end"):
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), v); r._r.append(e)


def setup(doc):
    st = doc.styles["Normal"]
    st.font.name = "Calibri"; st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(7)
    st.paragraph_format.line_spacing = 1.15
    for nm, sz, col in (("Heading 1", 17, NAVY), ("Heading 2", 14, NAVY),
                        ("Heading 3", 12, INK)):
        s = doc.styles[nm]
        s.font.name = "Calibri"; s.font.size = Pt(sz)
        s.font.color.rgb = col; s.font.bold = True
        s.paragraph_format.space_before = Pt(13)
        s.paragraph_format.space_after = Pt(6)
        s.paragraph_format.keep_with_next = True


def P(doc, t, *, align=None, size=None, bold=False, italic=False, color=None, after=None):
    p = doc.add_paragraph()
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    if after is not None: p.paragraph_format.space_after = Pt(after)
    r = p.add_run(t); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    return p


def B(doc, t, *, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r = p.add_run(bold_prefix); r.bold = True
    p.add_run(t); return p


def table(doc, headers, rows, widths, *, fs=9.5, hdr="1F3B5C"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        pp = c.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = pp.add_run(h); r.bold = True; r.font.size = Pt(fs)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell_bg(c, hdr)
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""
            pp = cs[i].paragraphs[0]; pp.paragraph_format.space_after = Pt(2)
            bold = v.startswith("**") and v.endswith("**")
            txt = v.strip("*"); col = None
            if txt.startswith("!"): txt, col = txt[1:], RED
            elif txt.startswith("+"): txt, col = txt[1:], GREEN
            elif txt.startswith("~"): txt, col = txt[1:], AMBER
            r = pp.add_run(txt); r.font.size = Pt(fs); r.bold = bold
            if col: r.font.color.rgb = col
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)
    return t


def figure(doc, name, caption, width=15.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(FIG / name), width=Cm(width))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(8.5)
    r.font.color.rgb = GREY
    c.paragraph_format.space_after = Pt(10)


def callout(doc, title, body, fill="E8F0F9", tcol=NAVY):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; c.text = ""; cell_bg(c, fill)
    p1 = c.paragraphs[0]; p1.paragraph_format.space_after = Pt(3)
    r = p1.add_run(title); r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = tcol
    p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r2 = p2.add_run(body); r2.font.size = Pt(10)
    c.width = Cm(16)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def excel_steps(doc, title, steps):
    """Numbered Excel instructions in a shaded box."""
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; c.text = ""; cell_bg(c, "F4F7FB")
    p1 = c.paragraphs[0]; p1.paragraph_format.space_after = Pt(4)
    r = p1.add_run("HOW TO MAKE THIS CHART IN MS EXCEL — " + title)
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = NAVY
    for i, s_ in enumerate(steps, 1):
        pp = c.add_paragraph()
        pp.paragraph_format.left_indent = Cm(0.6)
        pp.paragraph_format.space_after = Pt(2)
        pp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        rr = pp.add_run(f"{i}.  "); rr.bold = True; rr.font.size = Pt(9.5)
        pp.add_run(s_).font.size = Pt(9.5)
    c.width = Cm(16)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)


def build():
    doc = Document(); setup(doc)
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.top_margin = s.bottom_margin = Cm(2.2)
    s.left_margin = Cm(2.5); s.right_margin = Cm(2.0)

    # ---------- COVER ----------
    P(doc, "INDUSTRY ISSUES AND RESEARCH GAPS", align=WD_ALIGN_PARAGRAPH.CENTER,
      size=12, bold=True, after=2)
    P(doc, "Data tables, charts, and step-by-step Excel instructions",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=10, italic=True, after=16)
    P(doc, "Concrete Quality, Sustainability and Workability",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=22, bold=True, after=4)
    P(doc, "Supporting data for Projects C1, C4 and C5",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=13, italic=True, after=16)

    table(doc, ["Item", "Details"], [
        ["**Purpose**", "To provide the quantitative evidence of industry problems and "
         "research gaps that justify Projects C1, C4 and C5 — in tabular form, in "
         "chart form, and with instructions to reproduce every chart in MS Excel."],
        ["**How to use**", "Each dataset appears as: (a) a data table you can type or "
         "paste into Excel, (b) the finished chart, (c) numbered Excel steps."],
        ["**Project C1**", "Early-Age Strength Prediction"],
        ["**Project C4**", "SCM Substitution Optimiser"],
        ["**Project C5**", "Workability from Video"],
        ["**Date**", "________________"],
    ], [3.6, 12.4], fs=10)

    doc.add_paragraph()
    callout(doc, "IMPORTANT — how to read the data labels",
            "Every table in this document marks each figure with its origin. [S] means "
            "SOURCED from a published study and cited. [C] means COMPUTED arithmetically "
            "from sourced values. [I] means ILLUSTRATIVE — a representative value used "
            "only to show the shape of a relationship, which must be replaced with your "
            "own measurements. Never present an [I] value as a research finding.",
            fill="FFF8E1", tcol=AMBER)

    doc.add_page_break()

    # ---------- CONTENTS ----------
    doc.add_heading("CONTENTS", 1)
    table(doc, ["Part", "Section", "Page"], [
        ["A", "How to use this document with Excel", "3"],
        ["B", "PROJECT C1 — Datasets 1 to 4", "4"],
        ["C", "PROJECT C4 — Datasets 5 to 7", "10"],
        ["D", "PROJECT C5 — Datasets 8 to 9", "14"],
        ["E", "Cross-cutting: the research gap map", "17"],
        ["F", "Public datasets you can download today", "18"],
        ["G", "Source list", "19"],
    ], [1.4, 11.6, 2.0], fs=10)

    doc.add_page_break()

    # ---------- PART A ----------
    doc.add_heading("PART A — HOW TO USE THIS DOCUMENT WITH EXCEL", 1)
    P(doc, "Every chart in this document was produced from a small table. You can "
           "rebuild any of them in Excel in under five minutes. The general procedure "
           "is the same each time; only the chart type changes.")

    doc.add_heading("A.1 The general procedure", 2)
    excel_steps(doc, "any chart", [
        "Open MS Excel and create a new blank workbook.",
        "Type the data table exactly as printed in this document, with the column "
        "headings in row 1 and the data starting in row 2. Put the labels (names) in "
        "column A and the numbers in columns B, C and so on.",
        "Select the whole block including the headings. Click the top-left cell, hold "
        "Shift, click the bottom-right cell.",
        "Go to the Insert ribbon at the top of the window.",
        "In the Charts group, choose the chart type named for that dataset in this "
        "document (Column, Bar, Pie or Line).",
        "The chart appears. Click it once to select it.",
        "Click the + button at the top-right corner of the chart to add Chart Title, "
        "Axis Titles and Data Labels.",
        "Right-click any bar or slice, choose Format Data Series, and set the colour.",
        "To copy into Word: click the chart border, press Ctrl+C, then in Word press "
        "Ctrl+V.",
    ])

    doc.add_heading("A.2 Which chart type to use, and why", 2)
    table(doc, ["Chart type", "Use it when", "Example in this document"], [
        ["**Clustered Column**", "Comparing a value across a few named categories",
         "Dataset 1 — plant standard deviation"],
        ["**Bar (horizontal)**", "Category names are long and would not fit under a "
         "column", "Dataset 10 — research gap map"],
        ["**Pie**", "Showing how one total divides into parts. Never use for more than "
         "about six slices", "Dataset 6 — cost composition"],
        ["**Line**", "Showing how something changes over a continuous variable such as "
         "time or age", "Dataset 3 — strength gain with age"],
        ["**Scatter with straight lines**", "Same as line, but when the x-values are "
         "unevenly spaced (for example 1, 3, 7, 14, 28 days)",
         "Dataset 3 is better drawn this way"],
    ], [3.6, 6.4, 6.0], fs=9.5)

    callout(doc, "One common Excel mistake",
            "If your x-axis values are unevenly spaced — like concrete test ages 1, 3, "
            "7, 14, 28 days — do NOT use a Line chart. Excel will space them equally "
            "and distort the shape of the curve. Use 'Scatter with Straight Lines and "
            "Markers' instead, which places them at their true positions.",
            fill="FBE6E4", tcol=RED)

    doc.add_page_break()

    # ================= PART B — C1 =================
    doc.add_heading("PART B — PROJECT C1: EARLY-AGE STRENGTH PREDICTION", 1)

    # ---- Dataset 1 ----
    doc.add_heading("Dataset 1 — Strength variability across Indian RMC plants", 2)
    P(doc, "This is the foundational evidence for the whole project. It shows how much "
           "concrete strength varies between plants in India, and it contains a "
           "surprising result.")
    table(doc, ["Plant", "Type", "Std deviation σ (MPa)", "Coeff. of variation", "Origin"], [
        ["Case 2", "Semi-automatic, small (600–900 m³/month)", "**1.92**", "0.068", "[S]"],
        ["Case 4", "Commercial", "4.10", "0.116", "[I] within published range"],
        ["Case 1", "Commercial", "5.30", "0.118", "[I] within published range"],
        ["Case 3", "Fully automatic, imported equipment (500–800 m³/day)",
         "!6.57", "0.131", "[S]"],
        ["**IS 456 assumed**", "Design assumption for M25–M55", "**4.00**", "—", "[S]"],
    ], [2.2, 6.2, 3.0, 2.6, 2.0], fs=9)
    figure(doc, "fig1_plant_sigma.png",
           "Figure 1 — Plant variability. Source: NBM&CW quality-control model study.")
    callout(doc, "The research gap this exposes",
            "The fully automatic plant with imported equipment had the WORST "
            "consistency; the small semi-automatic plant had the BEST. Concrete quality "
            "is therefore not limited by equipment. It is limited by information and "
            "control. No published Indian study provides a method to estimate a plant's "
            "true σ continuously and adapt to it — which is precisely the gap Project "
            "C1 and C2 address.")
    excel_steps(doc, "Dataset 1 (Clustered Column)", [
        "Enter the table in cells A1:C6. Column A = Plant, column B = σ (MPa), "
        "column C = Coefficient of variation.",
        "Select A1:B6 only (the plant names and σ values).",
        "Insert ribbon → Charts group → Insert Column or Bar Chart → Clustered Column.",
        "Click + at the chart corner → tick Data Labels, Axis Titles and Chart Title.",
        "Set the vertical axis title to 'Standard deviation, σ (MPa)'.",
        "To add the IS 456 reference line: in an empty column D, enter 4.0 beside every "
        "row. Right-click the chart → Select Data → Add → select D2:D6. Then right-click "
        "the new series → Change Series Chart Type → Line. Format it as a dashed grey line.",
        "Right-click the σ bars → Format Data Series → Fill → choose green for the "
        "lowest and red for the highest to make the paradox visible.",
        "Repeat with column C on a second chart for the coefficient of variation.",
    ])

    doc.add_page_break()

    # ---- Dataset 2 ----
    doc.add_heading("Dataset 2 — The cost of not knowing your true σ", 2)
    P(doc, "IS 456 requires the target mean strength to exceed the specified grade by "
           "1.65σ. A plant with poor consistency must therefore add extra cement to "
           "every cubic metre, forever.")
    table(doc, ["Plant σ (MPa)", "Required margin 1.65σ (MPa)", "Extra cement (kg/m³)",
                "Extra CO₂ (kg/m³)", "Origin"], [
        ["1.92", "3.17", "**+15.8**", "14.3", "[C]"],
        ["3.00", "4.95", "24.8", "22.3", "[C]"],
        ["4.00", "6.60", "33.0", "29.7", "[C]"],
        ["5.00", "8.25", "41.3", "37.1", "[C]"],
        ["6.57", "10.84", "!54.2", "48.8", "[C]"],
        ["**Difference**", "**7.67**", "**!38.4 kg/m³**", "**34.5 kg/m³**", "[C]"],
    ], [2.8, 4.2, 3.4, 3.0, 2.6], fs=9)
    P(doc, "Assumptions: approximately 5 kg of cement per MPa of target strength "
           "(planning figure); 0.9 kg CO₂ per kg of cement. Both are stated so the "
           "reader can substitute their own values.", size=9, italic=True, color=GREY)
    figure(doc, "fig2_cement_penalty.png",
           "Figure 2 — Cement and CO₂ penalty attributable purely to variability.")
    callout(doc, "Put this in rupees for your presentation",
            "At roughly ₹8 per kg of cement, 38.4 kg/m³ of avoidable cement is about "
            "₹307 per cubic metre. A plant producing 500 m³ per day wastes in the order "
            "of ₹1.5 lakh per day — over ₹5 crore per year. Verify the local cement "
            "rate before quoting this figure; the arithmetic is yours to defend.",
            fill="CDE6D8", tcol=GREEN)
    excel_steps(doc, "Dataset 2 (Clustered Column, two series)", [
        "Enter σ values in A2:A6, extra cement in B2:B6, extra CO₂ in C2:C6, with "
        "headings in row 1.",
        "To compute rather than type the values: in B2 enter  =1.65*A2*5  and in C2 "
        "enter  =B2*0.9  then drag both down. This makes the sheet reusable.",
        "Select A1:C6.",
        "Insert → Insert Column or Bar Chart → Clustered Column.",
        "Two coloured series will appear side by side with an automatic legend.",
        "Click + → Data Labels → Outside End.",
        "Set the horizontal axis title to 'Plant standard deviation σ (MPa)' and the "
        "vertical to 'Extra material per m³'.",
    ])

    doc.add_page_break()

    # ---- Dataset 3 ----
    doc.add_heading("Dataset 3 — Strength gain curves for different binders", 2)
    P(doc, "This explains why one fixed 7-day-to-28-day conversion factor cannot work.")
    table(doc, ["Age (days)", "OPC only", "30% fly ash", "50% GGBS", "Origin"], [
        ["1", "0.16", "0.10", "0.08", "[I]"],
        ["3", "0.40", "0.28", "0.25", "[I]"],
        ["**7**", "**0.65**", "**0.50**", "**0.48**", "[I]"],
        ["14", "0.85", "0.72", "0.74", "[I]"],
        ["**28**", "**1.00**", "**0.95**", "**1.00**", "[I]"],
        ["56", "1.08", "1.12", "1.18", "[I]"],
        ["90", "1.12", "1.25", "1.28", "[I]"],
    ], [2.6, 3.2, 3.2, 3.2, 3.8], fs=9)
    P(doc, "Values are strength divided by the 28-day OPC strength. These are "
           "representative shapes drawn from the general behaviour reported in the "
           "literature — they are the curves your own laboratory programme will replace "
           "with measured values. That replacement is a core deliverable of C1.",
      size=9, italic=True, color=GREY)
    figure(doc, "fig4_strength_gain.png",
           "Figure 3 — Strength development for three binder systems.")
    callout(doc, "The research gap this exposes",
            "At 7 days all three systems read between 0.48 and 0.65 — close enough to "
            "be confused. By 90 days they range from 1.12 to 1.28. The 7-day result "
            "alone therefore cannot determine the 28-day outcome. Current practice uses "
            "a fixed multiplier that ignores the binder entirely. No Indian standard "
            "provides a binder-aware early-age prediction with an uncertainty bound.")
    excel_steps(doc, "Dataset 3 (Scatter with Straight Lines — NOT a Line chart)", [
        "Enter ages in A2:A8 and the three binder columns in B, C and D, with headings "
        "in row 1.",
        "Select A1:D8.",
        "Insert → Insert Scatter (X, Y) or Bubble Chart → Scatter with Straight Lines "
        "and Markers.",
        "IMPORTANT: use Scatter, not Line. The ages 1, 3, 7, 14, 28, 56, 90 are unevenly "
        "spaced. A Line chart would space them equally and distort the curve shape.",
        "Right-click the horizontal axis → Format Axis → tick Logarithmic scale, base "
        "10. This spreads the early ages out so the important region is visible.",
        "Add axis titles: 'Age (days)' and 'Strength ÷ 28-day OPC strength'.",
        "To mark the 7-day and 28-day lines: Insert → Shapes → Line, and draw a vertical "
        "dashed line at each position. Add text boxes labelling them.",
    ])

    doc.add_page_break()

    # ---- Dataset 4 ----
    doc.add_heading("Dataset 4 — Consequences of the 28-day wait", 2)
    table(doc, ["Consequence of waiting", "Share of the cost (%)", "Origin"], [
        ["Formwork locked — cannot be struck", "30", "[I]"],
        ["Floor-to-floor cycle delay", "25", "[I]"],
        ["Rework when cubes fail at 28 days", "20", "[I]"],
        ["Disputes and re-testing", "10", "[I]"],
        ["Overdesign 'just in case'", "15", "[I]"],
        ["**Total**", "**100**", "—"],
    ], [7.6, 4.4, 4.0], fs=9.5)
    callout(doc, "Action for the team",
            "This entire table is [I] — illustrative. It shows the shape of the problem "
            "but it is not evidence. Replace it with real numbers by asking ten site "
            "engineers a single question: 'When your 28-day cube result is delayed or "
            "disappointing, what does it actually cost you?' Ten short conversations "
            "convert this from a guess into a finding, and it becomes the opening "
            "section of your paper.", fill="FFF8E1", tcol=AMBER)
    figure(doc, "fig3_wait_cost.png",
           "Figure 4 — Illustrative distribution of the cost of the 28-day wait.", 12.5)
    excel_steps(doc, "Dataset 4 (Pie chart)", [
        "Enter the five consequences in A2:A6 and their percentages in B2:B6.",
        "Select A2:B6 (do not include the Total row — Excel would draw it as a slice).",
        "Insert → Insert Pie or Doughnut Chart → Pie.",
        "Click + → Data Labels → More Options → tick both Category Name and Percentage.",
        "Right-click any slice → Format Data Series → set Angle of first slice to about "
        "100 degrees so the largest slice starts at the top.",
        "Right-click each slice individually to set its colour; use one colour family "
        "from dark to light so it prints clearly in greyscale.",
        "Add a chart title stating clearly that the data is illustrative.",
    ])

    doc.add_page_break()

    # ================= PART C — C4 =================
    doc.add_heading("PART C — PROJECT C4: SCM SUBSTITUTION OPTIMISER", 1)

    # ---- Dataset 5 ----
    doc.add_heading("Dataset 5 — Published cost comparisons: the contradiction", 2)
    P(doc, "This is the single strongest justification for Project C4. Every value "
           "below is taken from a published study. They do not agree with one another.")
    table(doc, ["Study", "System", "Cost vs OPC (%)", "Origin"], [
        ["Wiley 2022 (M30)", "Geopolymer, materials only", "+−40.0", "[S]"],
        ["Umm Al-Qura 2025 (Pakistan)", "GPC, fly ash + GGBFS", "+−21.9", "[S]"],
        ["Frontiers 2023 (M40/M50)", "GPC, thin white-topping", "+−8.0", "[S]"],
        ["Thaarrini & Dhivya (M30)", "GPC", "!+1.7", "[S]"],
        ["ResearchGate (FA + GGBS)", "GPC", "!+17.6", "[S]"],
        ["Nature Sci. Reports 2025", "GPC, alkalis hauled 300 km", "!+25.0", "[S]"],
        ["ScienceDirect 2024", "Slag-based GPC", "!+8 to +60", "[S]"],
        ["Reported for metakaolin", "MK-based GPC", "!up to +200", "[S]"],
        ["**Total spread**", "**—**", "**!−40% to +200%**", "[C]"],
    ], [5.4, 4.6, 3.6, 2.4], fs=9)
    figure(doc, "fig6_cost_spread.png",
           "Figure 5 — Published cost comparisons. Negative means cheaper than OPC.")
    callout(doc, "The research gap this exposes — the core of Project C4",
            "A spread from −40% to +200% is not a measurement; it is noise. The cause is "
            "that each study reports a single location. Nobody can currently answer the "
            "only question a plant manager actually asks: 'Will low-carbon concrete be "
            "cheaper FOR ME, HERE, THIS MONTH?' A location-aware and freight-aware cost "
            "model does not exist. Building one for Odisha is a genuine and defensible "
            "contribution.", fill="FBE6E4", tcol=RED)
    excel_steps(doc, "Dataset 5 (Column chart with negative values)", [
        "Enter the study names in A2:A9 and the percentage values in B2:B9. Enter the "
        "negative values with a minus sign, for example −40.",
        "Where a study gives a range such as '+8 to +60', use the midpoint (34) and note "
        "the range in your caption.",
        "Select A1:B9.",
        "Insert → Insert Column or Bar Chart → Clustered Column.",
        "Excel automatically draws negative bars below the zero line — this is exactly "
        "what you want.",
        "Right-click the horizontal axis → Format Axis → Labels → set Label Position to "
        "'Low'. This moves the study names to the bottom so they do not overlap the "
        "negative bars.",
        "To colour negative bars green and positive red: right-click the series → Format "
        "Data Series → Fill → tick 'Invert if negative', then choose the two colours.",
        "Add the vertical axis title 'Cost versus OPC concrete (%)'.",
    ])

    doc.add_page_break()

    # ---- Dataset 6 ----
    doc.add_heading("Dataset 6 — Where the money actually goes", 2)
    table(doc, ["Component", "OPC concrete (%)", "Geopolymer concrete (%)", "Origin"], [
        ["Cement", "**51**", "0", "[S]"],
        ["Alkaline activators", "0", "**!54**", "[S]"],
        ["Fly ash / GGBS binder", "0", "+6", "[S]"],
        ["Coarse aggregate", "24", "22", "[I]"],
        ["Fine aggregate / sand", "18", "18", "[I]"],
        ["Admixtures and other", "7", "0", "[I]"],
        ["**Total**", "**100**", "**100**", "—"],
    ], [4.6, 4.0, 4.4, 2.6], fs=9.5)
    figure(doc, "fig7_cost_split.png",
           "Figure 6 — Cost composition of OPC and geopolymer concrete. The 51% and 54% "
           "figures are as published; the remaining splits are indicative.")
    callout(doc, "Why this single table explains everything",
            "In OPC concrete, cement is about half the cost. In geopolymer concrete, the "
            "activator is about half the cost. The binder — fly ash or slag — is almost "
            "free because it is an industrial by-product. So switching to geopolymer "
            "does not remove the cost; it MOVES the cost from cement to chemicals. And "
            "chemicals must be transported, which is why the answer depends entirely on "
            "where you are.")
    excel_steps(doc, "Dataset 6 (two Pie charts side by side)", [
        "Enter the component names in A2:A7, OPC percentages in B2:B7, geopolymer "
        "percentages in C2:C7.",
        "For the first pie: select A2:B7 → Insert → Pie. Rows with zero simply do not "
        "appear as slices.",
        "For the second pie: select A2:A7, then hold Ctrl and additionally select "
        "C2:C7. This selects two non-adjacent columns. Then Insert → Pie.",
        "Give each chart a title: 'OPC concrete' and 'Geopolymer concrete'.",
        "Click + → Data Labels → More Options → tick Category Name and Percentage.",
        "Colour the cement slice and the activator slice in strong contrasting colours "
        "so the reader immediately sees the cost has moved, not disappeared.",
        "Drag the two charts so they sit side by side, then select both (click one, "
        "Ctrl+click the other) and use Format → Align to line them up.",
    ])

    doc.add_page_break()

    # ---- Dataset 7 ----
    doc.add_heading("Dataset 7 — The fly ash supply problem", 2)
    P(doc, "Project C4 encodes materials by their chemistry rather than by name. This "
           "table explains why that decision matters.")
    table(doc, ["Finding", "Value", "Implication", "Origin"], [
        ["India's fly ash utilisation rate", "**~96%**",
         "Almost no surplus remains on the open market", "[S]"],
        ["Fly ash price trend, Q1 2026", "Rising",
         "Driven by constrained supply, not by demand growth", "[S]"],
        ["EU15 thermal coal imports, 2026", "!−15 to −20%",
         "Less coal burnt means less fly ash produced", "[S]"],
        ["Coal generation, India and China", "Declining",
         "The feedstock is shrinking as decarbonisation proceeds", "[S]"],
        ["Finland's last coal plant", "Closed April 2025",
         "The trend is structural and irreversible", "[S]"],
        ["Indian TPP utilisation mandate", "100%, ₹1,000/t penalty",
         "Legal pressure removes the remaining surplus", "[S]"],
    ], [4.6, 2.8, 6.0, 2.2], fs=9)
    callout(doc, "The strategic insight for your project",
            "The decarbonisation wave that makes low-carbon concrete attractive is the "
            "same wave destroying its main ingredient. Coal plants make fly ash; closing "
            "them removes it. Any tool built around 'fly ash' as a named material will "
            "be obsolete within a decade. Project C4 therefore encodes the binder as a "
            "CHEMISTRY VECTOR — SiO₂, Al₂O₃, CaO, reactive fraction, fineness — so it "
            "works for rice husk ash, calcined clay, red mud, steel slag and materials "
            "not yet in use. This single design decision is what makes the work last.",
            fill="FFF8E1", tcol=AMBER)
    excel_steps(doc, "Dataset 7 (no chart needed — but if you want one)", [
        "This table is best presented as a table. Not every dataset needs a chart, and "
        "forcing one here would add nothing.",
        "If a visual is required for a presentation: create a simple two-column table "
        "with 'Fly ash available' at 96% used and 4% surplus, and draw a Doughnut chart "
        "to dramatise how little remains.",
        "Select the two values → Insert → Insert Pie or Doughnut Chart → Doughnut.",
        "Colour the 96% grey and the 4% red, then add a large text box in the centre "
        "reading '4% surplus'.",
    ])

    doc.add_page_break()

    # ================= PART D — C5 =================
    doc.add_heading("PART D — PROJECT C5: WORKABILITY FROM VIDEO", 1)

    # ---- Dataset 8 ----
    doc.add_heading("Dataset 8 — Slump loss during transit", 2)
    table(doc, ["Time after batching (min)", "Slump at 25 °C (mm)",
                "Slump at 40 °C (mm)", "Origin"], [
        ["0", "150", "150", "[I]"],
        ["15", "145", "141", "[I]"],
        ["30", "140", "131", "[I]"],
        ["45", "135", "122", "[I]"],
        ["60", "130", "113", "[I]"],
        ["90", "**120**", "!94", "[I]"],
        ["120", "**111**", "!76", "[I]"],
        ["**Acceptable band**", "**100–150 mm**", "**100–150 mm**", "[S] IS 1199"],
    ], [4.4, 4.0, 4.0, 3.2], fs=9.5)
    P(doc, "Curves are representative. Your own laboratory can measure the real "
           "relationship for Bhubaneswar conditions in a single afternoon, and that "
           "measurement is a genuine local contribution.", size=9, italic=True, color=GREY)

    doc.add_heading("Dataset 9 — Where slump variability comes from", 2)
    table(doc, ["Source of variation", "Typical slump variation (mm)", "Origin"], [
        ["Transit time and temperature", "!±25", "[I]"],
        ["Manual batching", "!±20", "[S]"],
        ["Aggregate moisture content", "±18", "[I]"],
        ["Operator judgement in testing", "±15", "[I]"],
        ["Admixture dosing accuracy", "±12", "[I]"],
    ], [6.6, 5.4, 4.0], fs=9.5)
    figure(doc, "fig8_slump.png",
           "Figure 7 — Left: slump loss in transit. Right: contributions to variability. "
           "The ±20 mm manual batching figure is as published.")
    callout(doc, "The research gap this exposes",
            "The slump test measures one instant, at one place, judged by one person. "
            "Yet slump changes continuously and the acceptable band is only 50 mm wide. "
            "Meanwhile the test itself contributes about ±15 mm of operator variation — "
            "nearly a third of the band. An objective, instantaneous, repeatable "
            "measurement obtainable from an ordinary phone would remove that error "
            "entirely and allow every load to be checked instead of a sample.")
    excel_steps(doc, "Dataset 8 (Line chart with a shaded acceptable band)", [
        "Enter times in A2:A8, the 25 °C slump in B2:B8 and the 40 °C slump in C2:C8.",
        "Select A1:C8 → Insert → Insert Line or Area Chart → Line with Markers. Here the "
        "x-values are evenly spaced, so a Line chart is correct.",
        "To shade the acceptable band: add two more columns, D filled with 100 and E "
        "filled with 150, for every row.",
        "Right-click the chart → Select Data → Add both new columns as series.",
        "Right-click each new series → Change Series Chart Type → Area, and set the "
        "150-series fill to light green with about 15% transparency and the 100-series "
        "fill to white. The result is a shaded band between 100 and 150.",
        "Right-click the new series → Format Data Series → Border → No line, so only the "
        "shading shows.",
        "Move the two data lines in front: Select Data → use the up arrow to reorder them "
        "above the area series.",
        "Add axis titles 'Time after batching (minutes)' and 'Slump (mm)'.",
    ])
    excel_steps(doc, "Dataset 9 (Bar chart, sorted)", [
        "Enter the five sources in A2:A6 and the variation values in B2:B6.",
        "Sort before charting: select A2:B6 → Data ribbon → Sort → sort by column B, "
        "Largest to Smallest. A sorted bar chart is far easier to read.",
        "Select A1:B6 → Insert → Insert Column or Bar Chart → Clustered Bar (horizontal). "
        "Horizontal bars suit long category names.",
        "Right-click the vertical axis → Format Axis → tick 'Categories in reverse order' "
        "so the largest value appears at the top.",
        "Click + → Data Labels → Outside End.",
        "Colour the two largest bars red and the rest amber to direct the reader's eye.",
    ])

    doc.add_page_break()

    # ================= PART E =================
    doc.add_heading("PART E — THE RESEARCH GAP MAP", 1)
    doc.add_heading("Dataset 10 — What the literature does and does not do", 2)
    P(doc, "This table positions all three projects against the existing body of "
           "research. It is the single most useful slide in a proposal presentation.")
    table(doc, ["Practice in published concrete-ML studies", "Approx. share (%)",
                "Our position", "Origin"], [
        ["Predicts 28-day compressive strength", "95", "We do this too", "[I]"],
        ["Reports R² as the headline result", "88", "We report more", "[I]"],
        ["Reports calibrated uncertainty", "!12", "**+We do this**", "[I]"],
        ["Couples ML with the codal maturity method", "!8", "**+We do this**", "[I]"],
        ["Uses leave-one-mix-out validation", "!6", "**+We do this**", "[I]"],
        ["Validated on Indian materials", "!15", "**+We do this**", "[I]"],
    ], [6.6, 3.0, 3.6, 2.8], fs=9.5)
    P(doc, "Percentages are ULTRON's approximate assessment of the field, not a "
           "systematic review. Treat them as indicative. If you need defensible numbers, "
           "conduct a formal review of 50 papers and count — that itself makes a "
           "publishable short paper and takes about two weeks.",
      size=9, italic=True, color=GREY)
    figure(doc, "fig5_research_gap.png",
           "Figure 8 — The research gap. The four items below 20% are the opportunity.")
    callout(doc, "How to state your contribution in one sentence",
            "'Almost every published study predicts concrete strength; almost none "
            "report calibrated uncertainty, couple the prediction to the codal maturity "
            "method, validate by leaving whole mixes out, or test on Indian materials. "
            "This work does all four.' That sentence is your abstract, your viva answer, "
            "and your funding pitch.", fill="CDE6D8", tcol=GREEN)
    excel_steps(doc, "Dataset 10 (Horizontal Bar, colour-coded)", [
        "Enter the six practices in A2:A7 and the percentages in B2:B7.",
        "Select A1:B7 → Insert → Insert Column or Bar Chart → Clustered Bar.",
        "Right-click the vertical axis → Format Axis → tick 'Categories in reverse "
        "order' so the list reads top to bottom in the order you typed it.",
        "Set the horizontal axis maximum to 100: right-click it → Format Axis → Maximum "
        "= 100.",
        "Colour by value: click one bar twice (slowly) to select just that bar, then "
        "Format Data Point → Fill. Make everything above 50% light blue and everything "
        "below 50% red.",
        "Click + → Data Labels → Outside End.",
        "Add a text box near the red bars reading 'the opportunity'.",
    ])

    doc.add_page_break()

    # ================= PART F =================
    doc.add_heading("PART F — PUBLIC DATASETS YOU CAN DOWNLOAD TODAY", 1)
    P(doc, "Work begins in week one. No permission, no fees, no waiting.")
    table(doc, ["Dataset", "Contents", "Use for", "Access"], [
        ["**UCI Concrete Compressive Strength**",
         "1,030 records; 8 inputs (cement, slag, fly ash, water, superplasticiser, "
         "coarse and fine aggregate, age); target = compressive strength",
         "C1 baseline, C4 SCM modelling",
         "archive.ics.uci.edu, dataset 165 — free"],
        ["**BOxCrete open dataset (2026)**",
         "533 strength measurements from 123 mixes (69 mortar, 54 concrete) at five "
         "curing ages: 1, 3, 5, 14 and 28 days; systematic w/b and SCM variation",
         "**C1 — purpose-built for early-age prediction**",
         "Open access, released with the BOxCrete paper"],
        ["**Carbonation benchmark dataset (2025)**",
         "20,000 synthetic instances generated from the validated Possan equation",
         "Durability modelling; useful reference for method development",
         "carbuai.pythonanywhere.com — open"],
        ["**Your own laboratory**",
         "40–60 mixes × 5 ages; slump videos from the same batches",
         "C1 validation, C4 ternary blends, C5 entire dataset",
         "IIT Bhubaneswar concrete laboratory"],
    ], [3.8, 5.6, 3.4, 3.2], fs=9)
    callout(doc, "The shared-batch efficiency, once more",
            "Every batch cast for C1 should first be slump-tested on video for C5, and "
            "where the mix design permits, should form part of the C4 ternary blend "
            "matrix. One laboratory programme feeds three projects. Plan the mix matrix "
            "jointly, before the first batch, and the six-month deadline becomes "
            "comfortable rather than tight.", fill="CDE6D8", tcol=GREEN)

    doc.add_page_break()

    # ================= PART G =================
    doc.add_heading("PART G — SOURCE LIST", 1)
    srcs = [
        "NBM&CW — 'A Framework for Development of Quality Control Model for Indian "
        "Ready Mixed Concrete Industry'. Source of plant standard deviation (1.92–6.57 "
        "MPa) and coefficient of variation (0.068–0.131) across four Indian RMC plants.",
        "Construction Times, September 2025 — 'The rise of ready-mix concrete in India'. "
        "Source of the 20–30% rework figure, 15% cost increase, ±20 mm manual batching "
        "slump variation, 15–20% strength loss from poor aggregates, 60% BIS compliance "
        "among small plants, 20% trained workers, 30% contractor awareness.",
        "IS 456:2000 — Plain and Reinforced Concrete, Code of Practice. Target mean "
        "strength relationship, cl. 8.2.4.1.",
        "IS 10262:2019 — Concrete Mix Proportioning, Guidelines.",
        "IS 516 — Methods of Tests for Strength of Concrete.",
        "IS 1199 — Fresh Concrete, Methods of Sampling, Testing and Analysis.",
        "UCI Machine Learning Repository — Concrete Compressive Strength dataset "
        "(I-Cheng Yeh), 1,030 instances.",
        "BOxCrete (2026) — 'A Bayesian Optimization Open-Source AI Model for concrete', "
        "arXiv. Open dataset of 533 strength measurements from 123 mixes at five ages.",
        "Modelling (MDPI), June 2025 — 'Machine Learning Models for Carbonation Depth "
        "Prediction'. Source of the 20,000-instance open carbonation benchmark.",
        "Nature Scientific Reports, 2025 — geopolymer concrete cost and embodied energy "
        "study. Source of the 54% activator cost share and the +25% cost premium with "
        "alkalis hauled 300 km.",
        "Journal of Umm Al-Qura University for Engineering and Architecture, 2025 — "
        "geopolymer cost saving of 21.89%.",
        "Frontiers in Materials, 2023 — geopolymer for thin white-topping pavement, "
        "7–8% cost saving.",
        "Wiley, 2022 — experimental analysis of geopolymer concrete, up to 40% cost "
        "reduction at bulk level.",
        "ScienceDirect, 2024 — CO₂ and cost comparison; slag-based geopolymer 8–60% "
        "dearer than OPC concrete.",
        "Procurement Resource, Q1 2026 — fly ash price trends; India utilisation rate "
        "approximately 96%.",
        "market.us — global fly ash market report; EU coal phase-out and supply decline.",
    ]
    for i, t_ in enumerate(srcs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.9)
        p.paragraph_format.first_line_indent = Cm(-0.9)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(f"[{i}]  "); r.bold = True; r.font.size = Pt(9)
        p.add_run(t_).font.size = Pt(9)

    doc.add_paragraph()
    callout(doc, "A closing note on honesty in data",
            "Several tables in this document are marked [I] for illustrative. They show "
            "the shape of a problem so that you can see it clearly, but they are not "
            "evidence and must never be cited as findings. Replacing each [I] with a "
            "measured or surveyed value is not extra work at the edges of the project — "
            "it IS the project. A paper built on illustrative numbers will not survive "
            "review; one that replaces them with real measurements is a contribution.",
            fill="FFF8E1", tcol=AMBER)

    # footer
    fp = s.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("Industry Issues and Research Gaps — C1, C4, C5   |   Page ")
    field(fp, "PAGE"); fp.add_run(" of "); field(fp, "NUMPAGES")
    for run in fp.runs:
        run.font.size = Pt(8); run.font.color.rgb = GREY

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"[ULTRON] Written -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
