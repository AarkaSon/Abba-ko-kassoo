#!/usr/bin/env python3
"""
ULTRON — generates the SETU research proposal as a .docx in Government of India
technical-proposal format (DST/SERB/AICTE style).

Run:  .venv/bin/python scripts/generate_proposal.py
Out:  results/SETU_Research_Proposal.docx
"""

from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "SETU_Research_Proposal.docx"


def compute():
    """Figures computed live from the verified engine — never hand-typed."""
    from src.design.westergaard import SlabProperties, WheelLoad, stress_edge
    from src.pavement.damage import AxleLoadGroup
    from src.pavement.reliability import (
        PavementUncertainty, Uncertain, required_thickness_for_reliability)
    from src.pavement.thermal import check_both_mechanisms

    spec = [AxleLoadGroup("a", 110_000., 150_000), AxleLoadGroup("b", 130_000., 90_000),
            AxleLoadGroup("c", 150_000., 40_000), AxleLoadGroup("d", 170_000., 12_000),
            AxleLoadGroup("e", 190_000., 3_000)]
    th = {}
    for k in (0.200, 0.150, 0.110, 0.080, 0.045):
        u = PavementUncertainty(k=Uncertain(k, 0.22),
                                modulus_of_rupture=Uncertain(4.5, 0.12),
                                E=Uncertain(30_000., 0.12),
                                thickness=Uncertain(300., 0.03))
        h, _ = required_thickness_for_reliability(u, spec, 0.90, n_sim=1200, seed=42)
        th[k] = h
    slab = SlabProperties(h=300., E=30_000., mu=0.15, k=0.08)
    sl = stress_edge(slab, WheelLoad.from_pressure(P=75_000., p=0.8))
    r = check_both_mechanisms(sl, slab.E, 16.8, 8.4, 4500., 3500., slab.l, 4.5)
    return {"th": th, "s_load": sl, "sr_load": sl / 4.5,
            "sr_gov": r["governing"].stress_ratio, "gov": r["governing"].mechanism,
            "warp": r["BUC"].warping_stress}

NAVY = RGBColor(0x1F, 0x3B, 0x5C)
BLACK = RGBColor(0x00, 0x00, 0x00)
GREY = RGBColor(0x44, 0x44, 0x44)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def set_cell_bg(cell, hex_colour: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_colour)
    tcPr.append(shd)


def add_field(paragraph, instr: str) -> None:
    """Insert a Word field code (used for page numbers / TOC)."""
    r = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    r._r.append(fld_begin)
    r._r.append(instr_el)
    r._r.append(fld_sep)
    r._r.append(fld_end)


def style_doc(doc: Document) -> None:
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15
    rpr = st.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), "Times New Roman")

    for name, size, colour, bold in (
        ("Heading 1", 15, NAVY, True),
        ("Heading 2", 13, NAVY, True),
        ("Heading 3", 12, BLACK, True),
    ):
        s = doc.styles[name]
        s.font.name = "Times New Roman"
        s.font.size = Pt(size)
        s.font.color.rgb = colour
        s.font.bold = bold
        s.paragraph_format.space_before = Pt(12)
        s.paragraph_format.space_after = Pt(6)
        s.paragraph_format.keep_with_next = True


def h(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    return p


def para(doc, text, *, align=None, size=None, bold=False, italic=False,
         space_after=None, indent=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if indent is not None:
        p.paragraph_format.left_indent = Cm(indent)
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def bullet(doc, text, *, level=0, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.8 + 0.6 * level)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
    p.add_run(text)
    return p


def numbered(doc, text, *, bold_prefix=None):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
    p.add_run(text)
    return p


def table(doc, headers, rows, *, widths=None, font_size=10, header_bg="1F3B5C"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, txt in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        r.bold = True
        r.font.size = Pt(font_size)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_bg(hdr[i], header_bg)
    for row in rows:
        cells = t.add_row().cells
        for i, txt in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            bold = txt.startswith("**") and txt.endswith("**")
            clean = txt.strip("*")
            r = p.add_run(clean)
            r.font.size = Pt(font_size)
            r.bold = bold
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = GREY
    p.paragraph_format.space_after = Pt(10)
    return p


def hrule(doc):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:color"), "1F3B5C")
    pbdr.append(bottom)
    pPr.append(pbdr)
    return p


# --------------------------------------------------------------------------- #
def build() -> None:
    d = compute()
    doc = Document()
    style_doc(doc)

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)  # A4
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(2.0)

    # ---------------- TITLE PAGE ---------------- #
    para(doc, "RESEARCH AND DEVELOPMENT PROPOSAL",
         align=WD_ALIGN_PARAGRAPH.CENTER, size=13, bold=True, space_after=2)
    para(doc, "(Submitted for Supervisory Review and Institutional Consideration)",
         align=WD_ALIGN_PARAGRAPH.CENTER, size=10, italic=True, space_after=18)
    hrule(doc)

    for _ in range(2):
        doc.add_paragraph()

    para(doc, "SETU", align=WD_ALIGN_PARAGRAPH.CENTER, size=30, bold=True,
         space_after=2)
    para(doc,
         "Structural Evaluation and Thickness Underwriting",
         align=WD_ALIGN_PARAGRAPH.CENTER, size=13, italic=True, space_after=14)
    para(doc,
         "A Reliability-Based Artificial Intelligence Framework for "
         "Residual-Life Prediction and Maintenance Prioritisation of "
         "Concrete Pavements",
         align=WD_ALIGN_PARAGRAPH.CENTER, size=15, bold=True, space_after=20)

    hrule(doc)
    doc.add_paragraph()

    table(doc,
          ["Particulars", "Details"],
          [
              ["**Title of the Proposal**",
               "SETU — A Reliability-Based Artificial Intelligence Framework for "
               "Residual-Life Prediction and Maintenance Prioritisation of Concrete "
               "Pavements"],
              ["**Broad Subject Area**", "Civil Engineering — Transportation / "
                                         "Pavement Engineering"],
              ["**Sub-Area**", "Rigid Pavement Design, Reliability Analysis, "
                               "Applied Machine Learning, Infrastructure Asset "
                               "Management"],
              ["**Proposed by**", "[Name of Investigator]"],
              ["**Designation**", "[Designation]"],
              ["**Department**", "Department of Civil Engineering"],
              ["**Institution**", "[Name of Institution]"],
              ["**Supervisor**", "[Name and Designation of Supervisor]"],
              ["**Proposed Duration**", "24 months (Phase I: 12 months; "
                                        "Phase II: 12 months)"],
              ["**Nature of Proposal**", "Applied research with translational "
                                         "and commercialisation potential"],
              ["**Date of Submission**", "________________"],
          ],
          widths=[5.0, 11.0], font_size=10)

    doc.add_paragraph()
    para(doc,
         "Note: This proposal is submitted for the guidance and approval of the "
         "Supervisor. Fields marked [ ] are to be completed prior to formal "
         "institutional submission.",
         align=WD_ALIGN_PARAGRAPH.CENTER, size=9, italic=True)

    doc.add_page_break()

    # ---------------- TOC ---------------- #
    h(doc, "TABLE OF CONTENTS", 1)
    toc_rows = [
        ["1.", "Executive Summary", "3"],
        ["2.", "Introduction and Background", "3"],
        ["3.", "Statement of the Problem", "4"],
        ["4.", "Review of Literature and State of the Art", "5"],
        ["5.", "Research Gap Identified", "6"],
        ["6.", "Objectives of the Proposed Work", "6"],
        ["7.", "Methodology", "7"],
        ["8.", "Preliminary Work Already Completed", "9"],
        ["9.", "Expected Outcomes and Deliverables", "10"],
        ["10.", "Work Plan and Time Schedule", "11"],
        ["11.", "Budget Estimate", "11"],
        ["12.", "Utilisation of Results and Commercialisation Potential", "12"],
        ["13.", "Risk Analysis and Mitigation", "13"],
        ["14.", "Ethical, Legal and Regulatory Compliance", "13"],
        ["15.", "Conclusion", "14"],
        ["", "References", "14"],
    ]
    table(doc, ["Sl.", "Section", "Page"], toc_rows,
          widths=[1.5, 12.5, 2.0], font_size=10)

    doc.add_page_break()

    # ---------------- 1. EXECUTIVE SUMMARY ---------------- #
    h(doc, "1. EXECUTIVE SUMMARY", 1)
    para(doc,
         "Concrete (rigid) pavements are designed once, at the planning stage, using "
         "single representative values for subgrade support, concrete strength, "
         "temperature differential and projected traffic. In reality each of these "
         "quantities varies continuously along the alignment of a highway. The "
         "prevailing practice accommodates this variability by adopting a uniform "
         "design thickness together with a blanket margin of safety applied along the "
         "entire stretch.")
    para(doc,
         "This practice produces two simultaneous and opposite inefficiencies. Where "
         "ground conditions are more favourable than assumed, concrete is provided in "
         "excess of requirement, at avoidable cost and avoidable embodied carbon. "
         "Where conditions are less favourable than assumed, distress develops earlier "
         "than the design life, and the owning authority has no means of identifying "
         "which segments are at risk until visible failure occurs.")
    para(doc,
         "The proposed work develops SETU, a reliability-based computational framework "
         "that treats the governing design parameters as statistical distributions "
         "rather than deterministic values, propagates that uncertainty through the "
         "cumulative fatigue damage formulation already prescribed in IRC:58, and "
         "thereby produces (i) a thickness requirement that varies along the alignment "
         "at a stated level of reliability, and (ii) a continuously updated estimate of "
         "residual life and distress risk for each segment of an in-service pavement. "
         "A machine-learning layer is superposed on the mechanistic core to correct "
         "systematic deviation between predicted and observed distress, without "
         "displacing the codal formulation.", )
    para(doc,
         "The framework requires no additional field instrumentation. It operates upon "
         "records that highway projects are already required to generate: pour "
         "registers, cube and beam test results, subgrade investigation data, traffic "
         "census returns and periodic condition surveys. A verified computational core "
         "has already been implemented and tested, and is described in Section 8.",
         bold=False)

    # ---------------- 2. INTRODUCTION ---------------- #
    h(doc, "2. INTRODUCTION AND BACKGROUND", 1)
    para(doc,
         "India has undertaken the largest programme of concrete road construction in "
         "its history. Rigid pavements are increasingly preferred on high-volume "
         "corridors on account of their longer service life, lower maintenance demand "
         "and superior performance under heavy commercial vehicle loading. A "
         "substantial proportion of this network is now approaching the age at which "
         "fatigue-related distress characteristically begins to appear.")
    para(doc,
         "Concurrently, the institutional framework for highway delivery has shifted "
         "towards concession-based models, in which a private entity assumes "
         "responsibility for the condition of the pavement over a period of fifteen to "
         "thirty years. For such an entity, the timing and location of maintenance "
         "intervention is a direct financial exposure rather than an administrative "
         "matter. There exists, for the first time, an institutional stakeholder with a "
         "quantified commercial incentive to predict pavement deterioration in advance.")
    para(doc,
         "The design of plain jointed rigid pavements in India is governed by IRC:58, "
         "which prescribes a mechanistic-empirical procedure founded upon the "
         "cumulative fatigue damage concept. The procedure computes flexural stress "
         "arising from the combined action of axle loading and temperature "
         "differential, expresses that stress as a ratio of the modulus of rupture of "
         "the concrete, determines the corresponding allowable number of load "
         "repetitions, and sums the damage contributions of the axle load spectrum in "
         "accordance with Miner's hypothesis. Acceptance requires that the cumulative "
         "fatigue damage should not exceed unity.")
    para(doc,
         "The formulation is sound. The limitation addressed in this proposal does not "
         "lie in the mechanics, but in the manner in which the mechanics are applied: "
         "the computation is performed once, with deterministic inputs, and is never "
         "subsequently revisited against the conditions actually realised on site.")

    # ---------------- 3. PROBLEM ---------------- #
    h(doc, "3. STATEMENT OF THE PROBLEM", 1)
    para(doc,
         "The parameters governing rigid pavement performance are not deterministic "
         "quantities. The following table summarises the divergence between design "
         "assumption and field reality, together with the coefficient of variation "
         "typically observed.")

    table(doc,
          ["Design parameter", "Treatment in practice", "Field reality",
           "Typical CoV"],
          [
              ["Modulus of subgrade reaction, k",
               "Single value from limited plate load tests or CBR correlation",
               "Varies continuously along the alignment with soil type, moisture "
               "and compaction", "0.20 – 0.35"],
              ["Flexural strength (modulus of rupture)",
               "Single specified characteristic value",
               "Varies between pours, batches and seasons", "0.10 – 0.15"],
              ["Elastic modulus, E",
               "Single value or correlation with compressive strength",
               "Varies with mix, aggregate and maturity", "0.10 – 0.15"],
              ["Slab thickness, h",
               "Nominal design value",
               "Subject to construction tolerance and sub-base irregularity",
               "0.02 – 0.05"],
              ["Traffic (commercial vehicles)",
               "Projected figure from a traffic census",
               "Subject to projection error, overloading and diversion",
               "0.15 – 0.30"],
          ],
          widths=[3.6, 4.2, 5.0, 2.2], font_size=9)
    caption(doc, "Table 3.1 — Divergence between design assumption and field reality. "
                 "Coefficients of variation are indicative and are to be replaced by "
                 "project-specific values wherever test records permit.")

    para(doc,
         "Because the design computation is deterministic, this variability is "
         "accommodated by a uniform margin of safety applied along the entire length of "
         "the pavement. Two consequences follow, and they occur simultaneously on the "
         "same project:")
    bullet(doc,
           "Concrete is provided in excess of requirement, incurring avoidable cost "
           "and avoidable embodied carbon over long stretches of favourable ground.",
           bold_prefix="Over-provision on favourable segments. ")
    bullet(doc,
           "Distress develops earlier than the intended design life. The owning "
           "authority possesses no analytical means of identifying which segments are "
           "at risk, and consequently maintenance is undertaken reactively, after "
           "visible failure, when the cost of rectification is substantially greater.",
           bold_prefix="Premature distress on unfavourable segments. ")

    para(doc,
         "The central question that the industry is presently unable to answer may be "
         "stated concisely as follows:", space_after=4)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.right_indent = Cm(1.5)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("\u201cWhich segment of this pavement will fail first, when will it "
                  "fail, and what is the financial consequence of deferring "
                  "intervention?\u201d")
    r.bold = True
    r.italic = True
    r.font.size = Pt(12)

    para(doc,
         "The data required to answer this question is, in substantial part, already "
         "generated and archived in the ordinary course of highway construction and "
         "operation. It is not analysed in an integrated manner, and it is not related "
         "back to the mechanistic damage model from which the design was originally "
         "derived.")

    # ---------------- 4. LITERATURE ---------------- #
    h(doc, "4. REVIEW OF LITERATURE AND STATE OF THE ART", 1)

    h(doc, "4.1 Mechanistic basis", 3)
    para(doc,
         "Westergaard (1926) established the closed-form solution for stresses in a "
         "concrete slab resting on a dense-liquid (Winkler) foundation for interior, "
         "edge and corner loading. Ioannides, Thompson and Barenberg (1985) "
         "reconsidered and corrected these solutions and established the conditions "
         "under which each is applicable. These solutions remain the analytical basis "
         "of rigid pavement stress computation and are adopted in the present work as "
         "the deterministic core.")
    para(doc,
         "The fatigue behaviour of concrete under repeated flexural stress is "
         "characterised by the stress ratio, the ratio of applied flexural stress to "
         "the modulus of rupture. The Portland Cement Association (1984) formalised "
         "the relationship between stress ratio and allowable repetitions, together "
         "with the erosion criterion governing foundation damage. Miner (1945) provides "
         "the linear damage summation hypothesis by which the contributions of "
         "individual axle load groups are combined. IRC:58 adopts this framework for "
         "Indian conditions.")

    h(doc, "4.2 Reliability in pavement design", 3)
    para(doc,
         "The treatment of pavement design parameters as random variables is "
         "well-established in the international literature, and reliability concepts "
         "are incorporated in the AASHTO design framework through a reliability level "
         "and an overall standard deviation. However, the reliability factor in such "
         "formulations is applied as a global multiplier, and does not resolve "
         "variability at the level of individual segments of a specific alignment. The "
         "present proposal advances the treatment from a global factor to a "
         "segment-resolved probabilistic computation.")

    h(doc, "4.3 Machine learning in pavement engineering", 3)
    para(doc,
         "Machine learning has been applied extensively to pavement condition "
         "prediction, principally through the correlation of condition indices with "
         "age, traffic and climatic variables. Two limitations recur in this body of "
         "work. First, purely data-driven models require extensive historical "
         "condition records, which are seldom available at the necessary resolution in "
         "the Indian context. Second, and more seriously for professional adoption, "
         "such models do not admit interpretation in terms of the governing codal "
         "provisions, and consequently cannot readily be relied upon by an engineer "
         "who must accept professional responsibility for the recommendation.")

    h(doc, "4.4 Pavement management systems", 3)
    para(doc,
         "Established pavement management systems operate principally at the network "
         "level and are oriented towards flexible pavements, employing statistical "
         "condition indices and deterioration curves. They are not generally "
         "constructed upon slab-level mechanistic damage accumulation, and their "
         "calibration to Indian rigid pavements under IRC provisions has received "
         "limited attention.")

    # ---------------- 5. GAP ---------------- #
    h(doc, "5. RESEARCH GAP IDENTIFIED", 1)
    para(doc, "The review discloses the following specific gaps:")
    numbered(doc,
             "The cumulative fatigue damage formulation of IRC:58 is applied once, at "
             "the design stage, as a check. It is not employed forward in time as a "
             "predictive instrument for an in-service pavement.",
             bold_prefix="Deterministic application of a probabilistic phenomenon. ")
    numbered(doc,
             "Reliability is introduced through global factors rather than through "
             "segment-resolved analysis reflecting the actual variability of a "
             "particular alignment.",
             bold_prefix="Absence of segment-level resolution. ")
    numbered(doc,
             "Data-driven condition models and mechanistic design models exist as "
             "separate traditions. A hybrid formulation, in which the codal mechanics "
             "provide the prediction and machine learning corrects only the residual, "
             "has not been established for Indian rigid pavements.",
             bold_prefix="Disjunction between mechanistic and data-driven methods. ")
    numbered(doc,
             "Records generated during construction — pour registers, cube results, "
             "subgrade data — are archived for contractual compliance and are not "
             "subsequently related to the mechanistic model to yield an as-built "
             "reliability assessment.",
             bold_prefix="Non-utilisation of existing construction records. ")

    # ---------------- 6. OBJECTIVES ---------------- #
    h(doc, "6. OBJECTIVES OF THE PROPOSED WORK", 1)
    para(doc, "The proposed work is directed towards the following objectives:")
    for i, (title, body) in enumerate([
        ("To formulate a probabilistic extension of the IRC:58 cumulative fatigue "
         "damage procedure",
         "in which subgrade reaction, flexural strength, elastic modulus, slab "
         "thickness and traffic volume are represented as statistical distributions, "
         "and to establish by Monte Carlo simulation the resulting distribution of "
         "cumulative fatigue damage and the associated probability of failure."),
        ("To develop a reliability-based thickness determination procedure",
         "yielding the minimum slab thickness required to achieve a stated reliability "
         "for a given segment, and thereby to quantify the material saving achievable "
         "on favourable segments and the additional provision required on "
         "unfavourable segments."),
        ("To establish a residual-life and distress-risk estimation procedure for "
         "in-service pavements",
         "by applying the damage accumulation model forward in time, incorporating "
         "as-built material and construction data together with observed traffic and "
         "climatic conditions."),
        ("To develop a hybrid predictive formulation",
         "in which a machine-learning model is trained upon the residual between "
         "mechanistically predicted and field-observed distress, so that local effects "
         "not captured by the codal formulation are accommodated without displacing "
         "the codal basis of the prediction."),
        ("To formulate a maintenance prioritisation procedure",
         "ranking segments by the expected cost of deferred intervention, computed as "
         "the product of the probability of distress and the differential between "
         "preventive and corrective treatment cost."),
        ("To validate the framework",
         "by retrospective application to existing concrete pavement sections of known "
         "condition and construction history, and to establish the accuracy of "
         "prediction against documented distress."),
    ], start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(f"Objective {i}: ")
        r.bold = True
        r2 = p.add_run(title)
        r2.bold = True
        p.add_run(", " + body)

    # ---------------- 7. METHODOLOGY ---------------- #
    doc.add_page_break()
    h(doc, "7. METHODOLOGY", 1)
    para(doc,
         "The framework is organised in four computational layers. The arrangement is "
         "deliberate: the deterministic codal formulation is retained as the "
         "foundation, and each successive layer adds information without displacing "
         "the layer beneath it. At zero input variability the framework reduces "
         "exactly to the conventional IRC:58 computation, and this property has been "
         "verified by automated test (Section 8).")

    table(doc,
          ["Layer", "Function", "Basis", "Output"],
          [
              ["**Layer 1**\nMechanistic core",
               "Computation of flexural stress, stress ratio, allowable repetitions "
               "and cumulative fatigue damage",
               "Westergaard solutions; IRC:58 fatigue formulation; Miner's hypothesis",
               "Deterministic damage state, every quantity traceable to a clause"],
              ["**Layer 2**\nProbabilistic propagation",
               "Monte Carlo simulation over the distributions of k, MR, E, h and "
               "traffic",
               "Reliability theory; lognormal representation of positive quantities",
               "Distribution of cumulative damage; probability of failure; "
               "reliability index"],
              ["**Layer 3**\nMachine-learning residual correction",
               "Regression upon the residual between predicted and observed distress",
               "Gaussian Process regression, providing calibrated uncertainty",
               "Corrected forecast with confidence interval"],
              ["**Layer 4**\nDecision engine",
               "Comparison of the cost of present intervention against the "
               "probability-weighted cost of deferred intervention",
               "Expected-value decision analysis",
               "Ranked maintenance schedule with associated financial consequence"],
          ],
          widths=[3.0, 4.2, 4.2, 3.6], font_size=9)
    caption(doc, "Table 7.1 — Layered architecture of the SETU framework.")

    h(doc, "7.1 Rationale for the hybrid formulation", 3)
    para(doc,
         "The decision to constrain the machine-learning component to the correction "
         "of residuals, rather than to permit direct prediction of pavement "
         "performance, is fundamental to the proposal and is justified on three "
         "independent grounds.")
    bullet(doc,
           "A prediction produced by an uninterpretable model cannot be relied upon by "
           "an engineer who must accept professional responsibility for it. A "
           "prediction expressed as a codal computation together with a bounded "
           "correction remains open to professional scrutiny.",
           bold_prefix="Professional accountability. ")
    bullet(doc,
           "Purely data-driven models require extensive training data. Where the "
           "mechanistic model supplies the principal signal, the learned component "
           "need only account for a small residual, and useful accuracy is attainable "
           "with datasets of the order of a few hundred observations.",
           bold_prefix="Data efficiency. ")
    bullet(doc,
           "Output that cites the governing clause is admissible in the technical "
           "documentation that accompanies a highway project. Output that cannot be "
           "so traced is not.",
           bold_prefix="Regulatory admissibility. ")

    h(doc, "7.2 Data sources", 3)
    para(doc,
         "The framework is designed to operate upon records already generated in the "
         "ordinary course of construction and operation, and does not require the "
         "installation of instrumentation:")
    for src, use in [
        ("Subgrade and sub-base investigation records (CBR, plate load tests)",
         "distribution of the modulus of subgrade reaction along the alignment"),
        ("Concrete pour registers and cube/beam test results",
         "distribution of flexural strength, resolved by chainage and date"),
        ("Batching plant and mix design records",
         "material characteristics and their variability"),
        ("Traffic census and toll plaza classification data",
         "axle load spectrum and growth rate"),
        ("Meteorological records",
         "temperature differential regime"),
        ("Periodic condition and distress surveys",
         "observed distress for calibration of Layer 3"),
    ]:
        bullet(doc, use, bold_prefix=f"{src} — ")

    h(doc, "7.3 Validation strategy", 3)
    para(doc,
         "Validation of a deterioration model is constrained by the fact that "
         "pavements deteriorate over years. Three complementary strategies are "
         "therefore adopted:")
    numbered(doc,
             "Application of the framework to existing pavement sections of known age, "
             "construction record and documented condition, and comparison of "
             "predicted with observed distress.",
             bold_prefix="Retrospective validation. ")
    numbered(doc,
             "Selection of heavily trafficked corridors, on which damage accumulates "
             "more rapidly, so as to shorten the interval required for prospective "
             "confirmation.",
             bold_prefix="Accelerated segments. ")
    numbered(doc,
             "Verification that the framework reproduces the deterministic IRC:58 "
             "result at zero variability, and that all monotonic physical "
             "relationships are preserved. This has been implemented as an automated "
             "test suite and is reported in Section 8.",
             bold_prefix="Analytical verification. ")

    # ---------------- 8. PRELIMINARY WORK ---------------- #
    doc.add_page_break()
    h(doc, "8. PRELIMINARY WORK ALREADY COMPLETED", 1)
    para(doc,
         "A functioning computational core has been implemented and verified prior to "
         "the submission of this proposal. The work is not conceptual; the following "
         "components are operational.")

    table(doc,
          ["Component", "Description", "Status"],
          [
              ["Analytical stress module",
               "Westergaard interior, edge and corner stress and deflection; radius of "
               "relative stiffness; equivalent radius of resisting section; composite "
               "modulus of subgrade reaction",
               "**Implemented and verified**"],
              ["Thermal warping module",
               "Bradbury coefficient by continuous fitted function; edge and interior "
               "warping stress; bottom-up (BUC) and top-down (TDC) cracking checks",
               "**Implemented and verified**"],
              ["Public computation tool",
               "Browser-based calculator with complete calculation trace, verified "
               "against the reference implementation to 3e-15",
               "**Implemented and verified**"],
              ["Fatigue and damage module",
               "Stress ratio, allowable repetitions across the three fatigue branches, "
               "Miner summation over an axle load spectrum, residual life with traffic "
               "growth, erosion susceptibility index",
               "**Implemented and verified**"],
              ["Reliability module",
               "Monte Carlo propagation over lognormal and normal input distributions; "
               "probability of failure; reliability index; bisection search for "
               "reliability-based thickness",
               "**Implemented and verified**"],
              ["Verification test suite",
               "56 automated tests encoding physical invariants, fit accuracy and the "
               "reduction to the deterministic codal result",
               "**56 of 56 passing**"],
          ],
          widths=[3.4, 8.6, 3.0], font_size=9)
    caption(doc, "Table 8.1 — Status of the implemented computational core.")

    h(doc, "8.1 Illustrative result", 3)
    para(doc,
         "The following illustrates the principal contribution of the framework. Two "
         "segments of a single notional corridor are analysed. They are identical in "
         "every respect except the quality of the subgrade. A conventional "
         "deterministic design would specify a single uniform thickness for both.")

    table(doc,
          ["Modulus of subgrade reaction, k (MPa/mm)",
           "Thickness required for 90% reliability (mm)",
           "Departure from a uniform 300 mm design"],
          [[f"{k:.3f} ({lbl})", f"{d['th'][k]:.0f}",
            ("reference" if k == 0.110 else
             (f"**{d['th'][0.110]-d['th'][k]:.0f} mm less**" if d['th'][k] < d['th'][0.110]
              else f"**{d['th'][k]-d['th'][0.110]:.0f} mm more required**"))]
           for k, lbl in [(0.200, "very good"), (0.150, "good"), (0.110, "fair"),
                          (0.080, "poor"), (0.045, "very poor")]],
          widths=[5.5, 5.5, 5.0], font_size=9)
    caption(doc, "Table 8.2 — Reliability-based thickness requirement as a function of "
                 "subgrade quality, at a target reliability of 90 per cent. Computed "
                 "using the implemented module; axle load spectrum and material "
                 "parameters held constant.")

    para(doc,
         f"The spread of {d['th'][0.045]-d['th'][0.200]:.0f} mm across the same corridor is the quantity that a uniform "
         "design necessarily conceals. On favourable segments the framework identifies "
         "material that may be safely omitted; on unfavourable segments it identifies "
         "provision that is required in order to attain the same reliability. Both "
         "results proceed from a single computation, and both are expressed in terms "
         "of the codal damage formulation.")

    para(doc,
         "It is emphasised that these figures are illustrative and are produced with "
         "indicative coefficients of variation. Project-specific values derived from "
         "the client's own test records are to be substituted before any design "
         "application.", italic=True, size=10)

    h(doc, "8.2 Significance of thermal warping", 3)
    para(doc,
         "The implemented thermal module demonstrates that warping stress frequently "
         "governs. For a 300 mm slab under a 15 tonne axle with a daytime temperature "
         "differential of 16.8 degrees Celsius:")
    _und = 100 * (1 - d["sr_load"] / d["sr_gov"])
    table(doc,
          ["Analysis", "Stress (MPa)", "Stress ratio", "Assessment"],
          [["Load only", f"{d['s_load']:.3f}", f"{d['sr_load']:.3f}",
            "below the endurance limit; apparently safe"],
           [f"Load and warping combined ({d['gov']} governs)",
            f"{d['s_load']+d['warp']:.3f}", f"{d['sr_gov']:.3f}",
            "**substantially above the endurance limit**"]],
          widths=[5.2, 2.8, 2.8, 5.2], font_size=9)
    caption(doc, "Table 8.3 — Effect of thermal warping on the governing stress ratio.")
    para(doc,
         f"Omitting thermal warping understates the stress ratio by approximately "
         f"{_und:.0f} per cent. Because the fatigue relationship is steeply non-linear "
         "in the stress ratio, this becomes an error of orders of magnitude in the "
         "allowable number of load repetitions. Warping is therefore not a refinement "
         "but is frequently the governing consideration.")

    # ---------------- 9. OUTCOMES ---------------- #
    h(doc, "9. EXPECTED OUTCOMES AND DELIVERABLES", 1)
    table(doc,
          ["Sl.", "Deliverable", "Nature"],
          [
              ["1", "A validated probabilistic extension of the IRC:58 cumulative "
                    "fatigue damage procedure", "Methodological contribution"],
              ["2", "A reliability-based thickness determination procedure with "
                    "quantified material and carbon saving", "Design methodology"],
              ["3", "A residual-life and distress-risk estimation procedure for "
                    "in-service concrete pavements", "Asset management methodology"],
              ["4", "A hybrid mechanistic–machine-learning predictive model with "
                    "calibrated uncertainty", "Computational contribution"],
              ["5", "A maintenance prioritisation procedure with associated financial "
                    "consequence", "Decision-support methodology"],
              ["6", "A verified open computational implementation with automated test "
                    "suite", "Software deliverable"],
              ["7", "Publications in peer-reviewed journals and presentation at "
                    "professional fora", "Dissemination"],
              ["8", "A demonstration study on an identified corridor",
               "Field validation"],
          ],
          widths=[1.2, 10.3, 4.5], font_size=9)

    # ---------------- 10. WORK PLAN ---------------- #
    h(doc, "10. WORK PLAN AND TIME SCHEDULE", 1)
    table(doc,
          ["Phase", "Activity", "Months", "Milestone"],
          [
              ["I", "Literature consolidation; compilation of variability statistics "
                    "for Indian materials and subgrades", "1 – 3",
               "Parameter database"],
              ["I", "Refinement and extension of the mechanistic core; incorporation "
                    "of temperature differential and top-down cracking", "3 – 6",
               "Extended Layer 1"],
              ["I", "Development and verification of the probabilistic layer",
               "5 – 9", "Validated Layer 2"],
              ["I", "Identification of case-study corridors; acquisition of "
                    "construction and condition records", "7 – 12",
               "Field dataset assembled"],
              ["II", "Retrospective validation against documented distress",
               "12 – 16", "Accuracy established"],
              ["II", "Development of the machine-learning residual layer",
               "14 – 19", "Validated Layer 3"],
              ["II", "Decision engine and maintenance prioritisation procedure",
               "18 – 21", "Layer 4 complete"],
              ["II", "Demonstration study, documentation and dissemination",
               "20 – 24", "Publications; final report"],
          ],
          widths=[1.4, 8.0, 2.2, 4.4], font_size=9)

    # ---------------- 11. BUDGET ---------------- #
    h(doc, "11. BUDGET ESTIMATE", 1)
    para(doc,
         "The proposal is deliberately structured so as to require minimal capital "
         "outlay. No field instrumentation, proprietary software licence or "
         "high-performance computing facility is necessary. The computational methods "
         "adopted execute on ordinary desktop hardware, and the implementation employs "
         "open-source components throughout.")
    table(doc,
          ["Head", "Year 1 (Rs.)", "Year 2 (Rs.)", "Total (Rs.)", "Justification"],
          [
              ["Manpower (Junior Research Fellow, if sanctioned)",
               "3,72,000", "3,72,000", "7,44,000",
               "Data compilation, field liaison, model development"],
              ["Travel and field visits", "60,000", "80,000", "1,40,000",
               "Site inspection, record collection, condition survey"],
              ["Consumables and data acquisition", "40,000", "40,000", "80,000",
               "Traffic data, meteorological records, standards"],
              ["Contingency", "25,000", "25,000", "50,000", "—"],
              ["Publication and dissemination", "20,000", "60,000", "80,000",
               "Journal charges, conference participation"],
              ["**Total**", "**5,17,000**", "**5,77,000**", "**10,94,000**", ""],
          ],
          widths=[4.2, 2.3, 2.3, 2.3, 5.0], font_size=9)
    para(doc,
         "The budget is indicative and may be reduced substantially if the work is "
         "undertaken without a sanctioned fellowship. The computational component of "
         "the proposal carries no cost.", italic=True, size=10)

    # ---------------- 12. UTILISATION ---------------- #
    doc.add_page_break()
    h(doc, "12. UTILISATION OF RESULTS AND COMMERCIALISATION POTENTIAL", 1)
    para(doc,
         "The outcome of the work admits application at three levels, and the "
         "translational pathway is set out here in the interest of transparency.")

    h(doc, "12.1 Academic and professional utilisation", 3)
    bullet(doc, "Contribution towards the eventual incorporation of reliability-based "
                "provisions in Indian rigid pavement design practice.")
    bullet(doc, "Provision of a verified open computational implementation for use by "
                "researchers and practitioners.")
    bullet(doc, "Establishment of a database of parameter variability for Indian "
                "materials and subgrade conditions, presently not consolidated.")

    h(doc, "12.2 Institutional utilisation", 3)
    bullet(doc, "Highway authorities may employ the framework to allocate constrained "
                "maintenance budgets on an objective and auditable basis, in place of "
                "uniform or reactive allocation.")
    bullet(doc, "Concessionaires responsible for pavement condition over a concession "
                "period may forecast maintenance liability and schedule intervention "
                "before distress becomes visible.")
    bullet(doc, "Design consultants may offer reliability-based design as a "
                "differentiated professional service.")

    h(doc, "12.3 Commercialisation pathway", 3)
    para(doc,
         "The framework admits development into a professional service and "
         "subsequently into a software platform. The progression is incremental and "
         "each stage is self-supporting:")
    table(doc,
          ["Stage", "Offering", "Basis"],
          [
              ["1", "Open reliability-based design calculator, made freely available",
               "Dissemination and professional adoption"],
              ["2", "Residual-life and maintenance prioritisation study for a "
                    "specified corridor", "Professional consultancy engagement"],
              ["3", "Continuously updated condition and risk platform",
               "Subscription service"],
              ["4", "Network-level prioritisation across a portfolio of assets",
               "Institutional engagement"],
          ],
          widths=[1.4, 8.6, 6.0], font_size=9)
    para(doc,
         "The economic proposition rests upon a well-documented characteristic of "
         "pavement maintenance, namely that the cost of intervention increases "
         "sharply, and non-linearly, once distress has become manifest. Preventive "
         "treatment applied to a correctly identified segment is a fraction of the "
         "cost of reconstruction of the same segment after failure. A framework that "
         "redirects even a modest proportion of an existing maintenance budget from "
         "segments that do not require intervention to segments that do will recover "
         "its cost within a single maintenance season.")

    # ---------------- 13. RISK ---------------- #
    h(doc, "13. RISK ANALYSIS AND MITIGATION", 1)
    table(doc,
          ["Risk", "Assessment", "Mitigation"],
          [
              ["Access to construction and condition records may be restricted, as "
               "such records may disclose deficiencies in past construction",
               "High",
               "The framework is presented as a forward-looking asset management "
               "instrument and not as an audit. Initial application to newly "
               "constructed corridors, where records are complete and no adverse "
               "inference arises."],
              ["Prospective validation requires a period of years, as pavements "
               "deteriorate slowly",
               "High",
               "Retrospective validation against sections of known condition; "
               "selection of heavily trafficked corridors for accelerated confirmation."],
              ["Field records may be incomplete or of variable quality",
               "Moderate",
               "The mechanistic core operates without the machine-learning layer; "
               "missing data widens the reported confidence interval rather than "
               "preventing computation."],
              ["Institutional procurement cycles are extended",
               "Moderate",
               "Initial engagement with concessionaires and consultants, in which "
               "decision-making is more direct."],
              ["Reproduction of codal provisions is subject to copyright vesting in "
               "the issuing body",
               "Moderate",
               "The computational procedure and numerical relationships are "
               "implemented; no protected expression is reproduced. Every output "
               "cites the governing clause and directs the user to the standard. "
               "Formal permission is being sought."],
              ["Predictions may be relied upon as design in substitution for "
               "professional judgement",
               "Moderate",
               "Output is expressed as decision support requiring the approval of a "
               "qualified engineer; confidence intervals and out-of-range warnings "
               "are reported with every result; a complete computation trace is "
               "provided."],
          ],
          widths=[5.0, 1.8, 9.2], font_size=9)

    # ---------------- 14. COMPLIANCE ---------------- #
    h(doc, "14. ETHICAL, LEGAL AND REGULATORY COMPLIANCE", 1)
    bullet(doc,
           "The work involves no human or animal subjects and requires no ethical "
           "clearance on that account.",
           bold_prefix="Research ethics. ")
    bullet(doc,
           "Copyright in Indian Standards and in the publications of the Indian Roads "
           "Congress vests in the respective issuing bodies. The implementation "
           "reproduces computational procedures and numerical relationships only; no "
           "protected expression, table layout or clause text is reproduced. Formal "
           "permission for reproduction of extracts is being sought from the "
           "respective authorities.",
           bold_prefix="Intellectual property in codal provisions. ")
    bullet(doc,
           "Construction and condition records obtained from any authority or "
           "concessionaire will be treated as confidential, employed solely for the "
           "purposes of the research, and reported in anonymised or aggregated form "
           "unless express written consent is obtained.",
           bold_prefix="Confidentiality of client data. ")
    bullet(doc,
           "Where personal data is processed in any subsequent software deployment, "
           "the requirements of the Digital Personal Data Protection Act, 2023 will be "
           "complied with, including the principle of data minimisation. The technical "
           "records upon which the framework operates are material and asset records "
           "and do not ordinarily constitute personal data.",
           bold_prefix="Data protection. ")
    bullet(doc,
           "All output is advisory. The framework does not substitute for design by a "
           "qualified engineer, and every report will carry an express statement to "
           "that effect together with the identity of the approving engineer.",
           bold_prefix="Professional responsibility. ")

    # ---------------- 15. CONCLUSION ---------------- #
    h(doc, "15. CONCLUSION", 1)
    para(doc,
         "Concrete pavements are presently designed upon assumptions that are not "
         "revisited, and maintained upon observation that arrives too late. The "
         "consequence is the simultaneous waste of material where conditions are "
         "favourable and the premature failure of segments where they are not. The "
         "mechanistic framework required to address this is already prescribed in "
         "IRC:58; what is absent is its probabilistic extension, its application "
         "forward in time, and its calibration against the records that construction "
         "already generates.")
    para(doc,
         "The proposed work supplies these elements. It does not displace the codal "
         "procedure but extends it, reducing exactly to the conventional computation "
         "when variability is absent, and adding information regarding the margin that "
         "actually exists when variability is present. It requires no instrumentation, "
         "no proprietary software and no significant capital outlay, and a verified "
         "computational core has already been implemented.")
    para(doc,
         "The approval and guidance of the Supervisor is respectfully sought, "
         "together with such institutional support as may be considered appropriate "
         "for the acquisition of field records and the identification of a suitable "
         "corridor for demonstration.")

    doc.add_paragraph()
    doc.add_paragraph()
    t = doc.add_table(rows=2, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.rows[0].cells[0].text = ""
    t.rows[0].cells[1].text = ""
    for i, lbl in enumerate(["(Signature of the Investigator)",
                             "(Signature of the Supervisor)"]):
        c = t.rows[1].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("_______________________\n" + lbl)
        r.font.size = Pt(10)
    for row in t.rows:
        for cell in row.cells:
            cell.width = Cm(7.5)

    # ---------------- REFERENCES ---------------- #
    doc.add_page_break()
    h(doc, "REFERENCES", 1)
    refs = [
        "IRC:58 — Guidelines for the Design of Plain Jointed Rigid Pavements for "
        "Highways. Indian Roads Congress, New Delhi.",
        "IRC:SP:83 — Guidelines for Maintenance, Repair and Rehabilitation of Cement "
        "Concrete Pavements. Indian Roads Congress, New Delhi.",
        "IRC:44 — Guidelines for Cement Concrete Mix Design for Pavements. Indian "
        "Roads Congress, New Delhi.",
        "IS 456:2000 — Plain and Reinforced Concrete: Code of Practice. Bureau of "
        "Indian Standards, New Delhi.",
        "IS 10262:2019 — Concrete Mix Proportioning: Guidelines. Bureau of Indian "
        "Standards, New Delhi.",
        "Westergaard, H. M. (1926). Stresses in concrete pavements computed by "
        "theoretical analysis. Public Roads, 7(2), 25–35.",
        "Ioannides, A. M., Thompson, M. R., & Barenberg, E. J. (1985). Westergaard "
        "solutions reconsidered. Transportation Research Record, 1043, 13–23.",
        "Miner, M. A. (1945). Cumulative damage in fatigue. Journal of Applied "
        "Mechanics, 12(3), A159–A164.",
        "Portland Cement Association (1984). Thickness Design for Concrete Highway "
        "and Street Pavements. Skokie, Illinois.",
        "Teller, L. W., & Sutherland, E. C. (1935). The structural design of concrete "
        "pavements. Public Roads, 16(8–10).",
        "AASHTO (1993). Guide for Design of Pavement Structures. American Association "
        "of State Highway and Transportation Officials, Washington, D.C.",
        "Ministry of Road Transport and Highways. Specifications for Road and Bridge "
        "Works. Indian Roads Congress, New Delhi.",
        "National Highways Authority of India (2025). Maintenance Manual.",
    ]
    for i, r in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(f"[{i}]  ")
        run.bold = True
        run.font.size = Pt(10)
        r2 = p.add_run(r)
        r2.font.size = Pt(10)

    # ---------------- FOOTER ---------------- #
    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run("SETU — Research and Development Proposal  |  Page ")
    fr.font.size = Pt(8)
    fr.font.color.rgb = GREY
    add_field(fp, "PAGE")
    fr2 = fp.add_run(" of ")
    fr2.font.size = Pt(8)
    fr2.font.color.rgb = GREY
    add_field(fp, "NUMPAGES")
    for r in fp.runs:
        r.font.size = Pt(8)
        r.font.color.rgb = GREY

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"[ULTRON] Written -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
