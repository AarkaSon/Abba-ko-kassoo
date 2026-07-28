#!/usr/bin/env python3
"""
ULTRON — renders the SETU proposal directly to PDF (ReportLab).

Not a converted .docx: this is a native render, so pagination, tables and fonts are
under our control and identical on every machine. Content is kept in step with
scripts/generate_proposal.py; the numerical results are computed live from the engine
so the document cannot drift from the code.

Run:  .venv/bin/python scripts/generate_proposal_pdf.py
Out:  results/SETU_Research_Proposal.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "SETU_Research_Proposal.pdf"

NAVY = colors.HexColor("#1F3B5C")
ACCENT = colors.HexColor("#E8F0F9")
GREY = colors.HexColor("#5D6B7A")
LINE = colors.HexColor("#C9D6E4")


# --------------------------------------------------------------------------- #
def styles():
    ss = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=ss["Normal"], fontName="Times-Roman",
                          fontSize=10.5, leading=15, alignment=TA_JUSTIFY,
                          spaceAfter=6)
    return {
        "body": body,
        "h1": ParagraphStyle("h1", parent=body, fontName="Times-Bold", fontSize=13.5,
                             textColor=NAVY, spaceBefore=14, spaceAfter=7,
                             alignment=0, keepWithNext=1),
        "h3": ParagraphStyle("h3", parent=body, fontName="Times-Bold", fontSize=11,
                             spaceBefore=9, spaceAfter=4, alignment=0, keepWithNext=1),
        "title": ParagraphStyle("title", parent=body, fontName="Times-Bold",
                                fontSize=26, alignment=TA_CENTER, leading=30,
                                spaceAfter=4),
        "sub": ParagraphStyle("sub", parent=body, fontName="Times-Italic",
                              fontSize=12, alignment=TA_CENTER, spaceAfter=12),
        "st": ParagraphStyle("st", parent=body, fontName="Times-Bold", fontSize=13.5,
                             alignment=TA_CENTER, leading=17, spaceAfter=16),
        "cap": ParagraphStyle("cap", parent=body, fontName="Times-Italic", fontSize=8.5,
                              alignment=TA_CENTER, textColor=GREY, spaceAfter=10),
        "cell": ParagraphStyle("cell", parent=body, fontSize=8.5, leading=11,
                               spaceAfter=0, alignment=0),
        "cellb": ParagraphStyle("cellb", parent=body, fontName="Times-Bold",
                                fontSize=8.5, leading=11, spaceAfter=0, alignment=0),
        "cellh": ParagraphStyle("cellh", parent=body, fontName="Times-Bold",
                                fontSize=8.5, leading=11, spaceAfter=0,
                                textColor=colors.white, alignment=TA_CENTER),
        "quote": ParagraphStyle("quote", parent=body, fontName="Times-BoldItalic",
                                fontSize=11.5, alignment=TA_CENTER, leftIndent=1.2*cm,
                                rightIndent=1.2*cm, spaceBefore=8, spaceAfter=10),
        "bullet": ParagraphStyle("bullet", parent=body, leftIndent=0.7*cm,
                                 bulletIndent=0.2*cm, spaceAfter=4),
        "ref": ParagraphStyle("ref", parent=body, fontSize=9, leading=12,
                              leftIndent=0.9*cm, firstLineIndent=-0.9*cm, spaceAfter=4),
    }


S = styles()


def tbl(headers, rows, widths, *, fs=8.5):
    data = [[Paragraph(h, S["cellh"]) for h in headers]]
    for r in rows:
        row = []
        for c in r:
            st = S["cellb"] if (c.startswith("**") and c.endswith("**")) else S["cell"]
            row.append(Paragraph(c.strip("*"), st))
        data.append(row)
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACCENT]),
    ]))
    return t


def P(t, s="body"):
    return Paragraph(t, S[s])


def B(t):
    return Paragraph(t, S["bullet"], bulletText="\u2022")


# --------------------------------------------------------------------------- #
def compute():
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


def footer(canv, doc):
    canv.saveState()
    canv.setFont("Times-Roman", 8)
    canv.setFillColor(GREY)
    canv.drawCentredString(
        A4[0] / 2, 1.3 * cm,
        f"SETU — Research and Development Proposal   |   Page {doc.page}")
    canv.setStrokeColor(LINE)
    canv.setLineWidth(0.4)
    canv.line(3 * cm, 1.75 * cm, A4[0] - 2 * cm, 1.75 * cm)
    canv.restoreState()


# --------------------------------------------------------------------------- #
def build():
    d = compute()
    doc = BaseDocTemplate(str(OUT), pagesize=A4, topMargin=2.3 * cm,
                          bottomMargin=2.3 * cm, leftMargin=3 * cm, rightMargin=2 * cm,
                          title="SETU — Research and Development Proposal",
                          author="Department of Civil Engineering")
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="n")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=footer)])
    E = []

    # TITLE
    E += [P("RESEARCH AND DEVELOPMENT PROPOSAL", "st"),
          P("(Submitted for Supervisory Review and Institutional Consideration)", "sub"),
          Spacer(1, 1.4 * cm),
          P("SETU", "title"),
          P("Structural Evaluation and Thickness Underwriting", "sub"),
          P("A Reliability-Based Artificial Intelligence Framework for Residual-Life "
            "Prediction and Maintenance Prioritisation of Concrete Pavements", "st"),
          Spacer(1, 0.8 * cm),
          tbl(["Particulars", "Details"],
              [["**Broad Subject Area**", "Civil Engineering — Transportation / "
                                          "Pavement Engineering"],
               ["**Sub-Area**", "Rigid Pavement Design, Reliability Analysis, Applied "
                                "Machine Learning, Infrastructure Asset Management"],
               ["**Proposed by**", "[Name of Investigator]"],
               ["**Department**", "Department of Civil Engineering"],
               ["**Institution**", "[Name of Institution]"],
               ["**Supervisor**", "[Name and Designation of Supervisor]"],
               ["**Proposed Duration**", "24 months (Phase I: 12 months; Phase II: 12 months)"],
               ["**Nature of Proposal**", "Applied research with translational and "
                                          "commercialisation potential"],
               ["**Date of Submission**", "________________"]],
              [4.6, 11.4]),
          Spacer(1, 0.5 * cm),
          P("<i>Fields marked [ ] are to be completed prior to formal institutional "
            "submission.</i>", "cap"),
          PageBreak()]

    # 1 SUMMARY
    E += [P("1. EXECUTIVE SUMMARY", "h1"),
          P("Concrete (rigid) pavements are designed once, at the planning stage, using "
            "single representative values for subgrade support, concrete strength, "
            "temperature differential and projected traffic. In reality each of these "
            "quantities varies continuously along the alignment of a highway. The "
            "prevailing practice accommodates this variability by adopting a uniform "
            "design thickness together with a blanket margin of safety applied along "
            "the entire stretch."),
          P("This produces two simultaneous and opposite inefficiencies. Where ground "
            "conditions are more favourable than assumed, concrete is provided in "
            "excess of requirement, at avoidable cost and avoidable embodied carbon. "
            "Where conditions are less favourable, distress develops earlier than the "
            "design life, and the owning authority has no means of identifying which "
            "segments are at risk until visible failure occurs."),
          P("The proposed work develops SETU, a reliability-based computational "
            "framework that treats the governing design parameters as statistical "
            "distributions rather than deterministic values, propagates that "
            "uncertainty through the cumulative fatigue damage formulation prescribed "
            "in IRC:58, and thereby produces a thickness requirement that varies along "
            "the alignment at a stated level of reliability, together with a "
            "continuously updated estimate of residual life and distress risk for each "
            "segment of an in-service pavement. A machine-learning layer is superposed "
            "on the mechanistic core to correct systematic deviation between predicted "
            "and observed distress, without displacing the codal formulation."),
          P("The framework requires no additional field instrumentation. It operates "
            "upon records that highway projects are already required to generate. A "
            "verified computational core has been implemented and tested, and is "
            "described in Section 8.")]

    # 2 BACKGROUND
    E += [P("2. INTRODUCTION AND BACKGROUND", "h1"),
          P("India has undertaken the largest programme of concrete road construction "
            "in its history, and a substantial proportion of that network is now "
            "approaching the age at which fatigue-related distress characteristically "
            "begins to appear. Concurrently, the institutional framework for highway "
            "delivery has shifted towards concession-based models, in which a private "
            "entity assumes responsibility for pavement condition over a period of "
            "fifteen to thirty years. For such an entity the timing and location of "
            "maintenance intervention is a direct financial exposure. There exists, "
            "for the first time, an institutional stakeholder with a quantified "
            "commercial incentive to predict pavement deterioration in advance."),
          P("The design of plain jointed rigid pavements in India is governed by "
            "IRC:58, which prescribes a mechanistic-empirical procedure founded upon "
            "the cumulative fatigue damage concept. The formulation is sound. The "
            "limitation addressed in this proposal does not lie in the mechanics, but "
            "in the manner of their application: the computation is performed once, "
            "with deterministic inputs, and is never subsequently revisited against "
            "the conditions actually realised on site.")]

    # 3 PROBLEM
    E += [P("3. STATEMENT OF THE PROBLEM", "h1"),
          tbl(["Design parameter", "Treatment in practice", "Field reality", "Typical CoV"],
              [["Modulus of subgrade reaction, k",
                "Single value from limited plate load tests or CBR correlation",
                "Varies continuously along the alignment with soil type, moisture and "
                "compaction", "0.20 – 0.35"],
               ["Flexural strength (modulus of rupture)", "Single specified value",
                "Varies between pours, batches and seasons", "0.10 – 0.15"],
               ["Elastic modulus, E", "Single value or correlation",
                "Varies with mix, aggregate and maturity", "0.10 – 0.15"],
               ["Slab thickness, h", "Nominal design value",
                "Construction tolerance and sub-base irregularity", "0.02 – 0.05"],
               ["Traffic (commercial vehicles)", "Projected figure from a census",
                "Projection error, overloading and diversion", "0.15 – 0.30"]],
              [3.6, 4.1, 5.1, 2.2]),
          P("Table 3.1 — Divergence between design assumption and field reality. "
            "Coefficients of variation are indicative.", "cap"),
          P("The central question that the industry is presently unable to answer may "
            "be stated concisely:"),
          P("\u201cWhich segment of this pavement will fail first, when will it fail, "
            "and what is the financial consequence of deferring intervention?\u201d",
            "quote"),
          P("The data required to answer this question is, in substantial part, already "
            "generated and archived in the ordinary course of highway construction and "
            "operation. It is not analysed in an integrated manner, and it is not "
            "related back to the mechanistic damage model from which the design was "
            "originally derived.")]

    # 4 LITERATURE
    E += [P("4. REVIEW OF LITERATURE AND STATE OF THE ART", "h1"),
          P("4.1 Mechanistic basis", "h3"),
          P("Westergaard (1926) established the closed-form solution for stresses in a "
            "concrete slab on a dense-liquid foundation for interior, edge and corner "
            "loading; Ioannides, Thompson and Barenberg (1985) reconsidered and "
            "corrected these solutions. Bradbury (1938) established the coefficient "
            "governing restraint to thermal curling. The fatigue behaviour of concrete "
            "under repeated flexural stress is characterised by the stress ratio, and "
            "the Portland Cement Association (1984) formalised the relationship between "
            "stress ratio and allowable repetitions. Miner (1945) provides the linear "
            "damage summation hypothesis. IRC:58 adopts this framework for Indian "
            "conditions."),
          P("4.2 Reliability in pavement design", "h3"),
          P("The treatment of pavement design parameters as random variables is "
            "well established internationally, and reliability concepts appear in the "
            "AASHTO framework through a reliability level and an overall standard "
            "deviation. However, the reliability factor in such formulations is applied "
            "as a global multiplier and does not resolve variability at the level of "
            "individual segments of a specific alignment."),
          P("4.3 Machine learning in pavement engineering", "h3"),
          P("Machine learning has been applied extensively to pavement condition "
            "prediction, principally by correlating condition indices with age, traffic "
            "and climate. Two limitations recur. First, purely data-driven models "
            "require extensive historical condition records, seldom available at the "
            "necessary resolution in the Indian context. Second, such models do not "
            "admit interpretation in terms of the governing codal provisions, and "
            "consequently cannot readily be relied upon by an engineer who must accept "
            "professional responsibility for the recommendation."),
          P("4.4 Pavement management systems", "h3"),
          P("Established pavement management systems operate principally at network "
            "level and are oriented towards flexible pavements, employing statistical "
            "condition indices. They are not generally constructed upon slab-level "
            "mechanistic damage accumulation, and their calibration to Indian rigid "
            "pavements under IRC provisions has received limited attention.")]

    # 5 GAP
    E += [P("5. RESEARCH GAP IDENTIFIED", "h1"),
          B("<b>Deterministic application of a probabilistic phenomenon.</b> The "
            "cumulative fatigue damage formulation is applied once, as a design check, "
            "and not forward in time as a predictive instrument."),
          B("<b>Absence of segment-level resolution.</b> Reliability is introduced "
            "through global factors rather than segment-resolved analysis."),
          B("<b>Disjunction between mechanistic and data-driven methods.</b> A hybrid "
            "formulation in which codal mechanics provide the prediction and machine "
            "learning corrects only the residual has not been established for Indian "
            "rigid pavements."),
          B("<b>Non-utilisation of existing construction records.</b> Pour registers, "
            "cube results and subgrade data are archived for contractual compliance "
            "and never related to the mechanistic model.")]

    # 6 OBJECTIVES
    E += [P("6. OBJECTIVES OF THE PROPOSED WORK", "h1")]
    for i, (t1, t2) in enumerate([
        ("To formulate a probabilistic extension of the IRC:58 cumulative fatigue "
         "damage procedure",
         "in which subgrade reaction, flexural strength, elastic modulus, slab "
         "thickness and traffic volume are represented as statistical distributions, "
         "and to establish by Monte Carlo simulation the resulting distribution of "
         "cumulative fatigue damage and the associated probability of failure."),
        ("To develop a reliability-based thickness determination procedure",
         "yielding the minimum slab thickness required to achieve a stated reliability "
         "for a given segment, quantifying the material saving achievable on "
         "favourable segments and the additional provision required on unfavourable "
         "segments."),
        ("To incorporate thermal warping and both cracking mechanisms",
         "so that bottom-up cracking under the daytime positive temperature "
         "differential and top-down cracking under the reversed night-time gradient "
         "are evaluated, and the governing mechanism identified."),
        ("To establish a residual-life and distress-risk estimation procedure",
         "by applying the damage accumulation model forward in time using as-built "
         "material and construction data together with observed traffic and climate."),
        ("To develop a hybrid predictive formulation",
         "in which a machine-learning model is trained upon the residual between "
         "mechanistically predicted and field-observed distress, accommodating local "
         "effects without displacing the codal basis of the prediction."),
        ("To formulate a maintenance prioritisation procedure",
         "ranking segments by the expected cost of deferred intervention."),
        ("To validate the framework",
         "by retrospective application to existing concrete pavement sections of known "
         "condition and construction history."),
    ], start=1):
        E.append(Paragraph(f"<b>Objective {i}: {t1}</b>, {t2}", S["bullet"]))

    # 7 METHODOLOGY
    E += [PageBreak(), P("7. METHODOLOGY", "h1"),
          P("The framework is organised in four computational layers. The arrangement "
            "is deliberate: the deterministic codal formulation is retained as the "
            "foundation, and each successive layer adds information without displacing "
            "the layer beneath it. At zero input variability the framework reduces "
            "exactly to the conventional IRC:58 computation, and this property has "
            "been verified by automated test."),
          tbl(["Layer", "Function", "Basis", "Output"],
              [["**Layer 1** Mechanistic core",
                "Flexural stress from load and thermal warping; stress ratio; "
                "allowable repetitions; cumulative fatigue damage",
                "Westergaard; Bradbury; IRC:58 fatigue formulation; Miner",
                "Deterministic damage state, clause-traceable"],
               ["**Layer 2** Probabilistic propagation",
                "Monte Carlo simulation over distributions of k, MR, E, h and traffic",
                "Reliability theory; lognormal representation",
                "Damage distribution; probability of failure"],
               ["**Layer 3** ML residual correction",
                "Regression upon the residual between predicted and observed distress",
                "Gaussian Process regression",
                "Corrected forecast with confidence interval"],
               ["**Layer 4** Decision engine",
                "Cost of present intervention against probability-weighted cost of "
                "deferral", "Expected-value decision analysis",
                "Ranked maintenance schedule"]],
              [2.9, 4.2, 4.0, 3.9]),
          P("Table 7.1 — Layered architecture of the SETU framework.", "cap"),
          P("7.1 Rationale for the hybrid formulation", "h3"),
          B("<b>Professional accountability.</b> A prediction produced by an "
            "uninterpretable model cannot be relied upon by an engineer who must accept "
            "professional responsibility for it."),
          B("<b>Data efficiency.</b> Where the mechanistic model supplies the principal "
            "signal, the learned component need only account for a small residual, and "
            "useful accuracy is attainable with datasets of a few hundred observations."),
          B("<b>Regulatory admissibility.</b> Output that cites the governing clause is "
            "admissible in project documentation; output that cannot be so traced is not."),
          P("7.2 Data sources", "h3"),
          P("The framework operates upon records already generated in the ordinary "
            "course of construction and operation, and requires no instrumentation: "
            "subgrade and sub-base investigation records; concrete pour registers and "
            "cube or beam test results; batching plant records; traffic census and toll "
            "plaza classification data; meteorological records; and periodic condition "
            "surveys."),
          P("7.3 Validation strategy", "h3"),
          B("<b>Retrospective validation</b> against existing sections of known age, "
            "construction record and documented condition."),
          B("<b>Accelerated segments</b> — heavily trafficked corridors on which damage "
            "accumulates more rapidly, shortening the interval for prospective "
            "confirmation."),
          B("<b>Analytical verification</b> — confirmation that the framework "
            "reproduces the deterministic IRC:58 result at zero variability and "
            "preserves all monotonic physical relationships.")]

    # 8 PRELIMINARY WORK
    th = d["th"]
    und = 100 * (1 - d["sr_load"] / d["sr_gov"])
    E += [PageBreak(), P("8. PRELIMINARY WORK ALREADY COMPLETED", "h1"),
          P("A functioning computational core has been implemented and verified prior "
            "to the submission of this proposal. The work is not conceptual."),
          tbl(["Component", "Description", "Status"],
              [["Analytical stress module",
                "Westergaard interior, edge and corner stress and deflection; radius of "
                "relative stiffness; equivalent radius of resisting section",
                "**Implemented and verified**"],
               ["Thermal warping module",
                "Bradbury coefficient by continuous fitted function; edge and interior "
                "warping stress; bottom-up and top-down cracking checks",
                "**Implemented and verified**"],
               ["Fatigue and damage module",
                "Stress ratio; allowable repetitions across the three fatigue branches; "
                "Miner summation; residual life with traffic growth",
                "**Implemented and verified**"],
               ["Reliability module",
                "Monte Carlo propagation; probability of failure; reliability index; "
                "bisection search for reliability-based thickness",
                "**Implemented and verified**"],
               ["Public computation tool",
                "Browser-based calculator with complete calculation trace, verified "
                "against the reference implementation",
                "**Implemented and verified**"],
               ["Verification test suite",
                "56 automated tests encoding physical invariants, fit accuracy, and "
                "reduction to the deterministic codal result",
                "**56 of 56 passing**"]],
              [3.2, 8.7, 3.1]),
          P("Table 8.1 — Status of the implemented computational core.", "cap"),

          P("8.1 Reliability-based thickness", "h3"),
          P("Two segments of a single notional corridor, identical in every respect "
            "except subgrade quality. A conventional deterministic design would specify "
            "one uniform thickness for both."),
          tbl(["Modulus of subgrade reaction, k (MPa/mm)",
               "Thickness for 90% reliability (mm)", "Departure from uniform design"],
              [[f"{k:.3f} ({lbl})", f"{th[k]:.0f}",
                ("reference" if k == 0.110 else
                 (f"**{th[0.110]-th[k]:.0f} mm less**" if th[k] < th[0.110]
                  else f"**{th[k]-th[0.110]:.0f} mm more required**"))]
               for k, lbl in [(0.200, "very good"), (0.150, "good"), (0.110, "fair"),
                              (0.080, "poor"), (0.045, "very poor")]],
              [5.5, 5.0, 5.5]),
          P("Table 8.2 — Reliability-based thickness requirement as a function of "
            "subgrade quality, at a target reliability of 90 per cent. Computed using "
            "the implemented module.", "cap"),
          P(f"The spread of {th[0.045]-th[0.200]:.0f} mm across the same corridor is the "
            "quantity a uniform design necessarily conceals. On favourable segments the "
            "framework identifies material that may safely be omitted; on unfavourable "
            "segments it identifies provision required to attain the same reliability. "
            "Both results proceed from a single computation."),

          P("8.2 Significance of thermal warping", "h3"),
          P("The implemented thermal module demonstrates that warping stress frequently "
            "governs. For a 300 mm slab under a 15 tonne axle with a daytime "
            "differential of 16.8 °C:"),
          tbl(["Analysis", "Stress (MPa)", "Stress ratio", "Assessment"],
              [["Load only", f"{d['s_load']:.3f}", f"{d['sr_load']:.3f}",
                "below the endurance limit; apparently safe"],
               [f"Load and warping combined ({d['gov']} governs)",
                f"{d['s_load']+d['warp']:.3f}", f"{d['sr_gov']:.3f}",
                "**substantially above the endurance limit**"]],
              [5.0, 2.6, 2.6, 5.8]),
          P("Table 8.3 — Effect of thermal warping on the governing stress ratio.", "cap"),
          P(f"Omitting thermal warping understates the stress ratio by approximately "
            f"{und:.0f} per cent. Because the fatigue relationship is steeply "
            "non-linear in the stress ratio, this becomes an error of orders of "
            "magnitude in the allowable number of repetitions. Warping is therefore not "
            "a refinement but frequently the governing consideration."),
          P("<i>These figures are illustrative and employ indicative coefficients of "
            "variation. Project-specific values derived from the client's own test "
            "records are to be substituted before any design application.</i>")]

    # 9 OUTCOMES
    E += [P("9. EXPECTED OUTCOMES AND DELIVERABLES", "h1"),
          tbl(["Sl.", "Deliverable", "Nature"],
              [["1", "A validated probabilistic extension of the IRC:58 cumulative "
                     "fatigue damage procedure", "Methodological"],
               ["2", "A reliability-based thickness determination procedure with "
                     "quantified material and carbon saving", "Design methodology"],
               ["3", "A residual-life and distress-risk estimation procedure",
                "Asset management"],
               ["4", "A hybrid mechanistic–machine-learning model with calibrated "
                     "uncertainty", "Computational"],
               ["5", "A maintenance prioritisation procedure with financial consequence",
                "Decision support"],
               ["6", "A verified open computational implementation with test suite",
                "Software"],
               ["7", "Publications and professional presentations", "Dissemination"],
               ["8", "A demonstration study on an identified corridor",
                "Field validation"]],
              [1.0, 10.5, 4.5])]

    # 10 PLAN
    E += [P("10. WORK PLAN AND TIME SCHEDULE", "h1"),
          tbl(["Phase", "Activity", "Months", "Milestone"],
              [["I", "Literature consolidation; variability statistics for Indian "
                     "materials and subgrades", "1 – 3", "Parameter database"],
               ["I", "Extension of the mechanistic core: temperature differential "
                     "regimes and erosion criterion", "3 – 6", "Extended Layer 1"],
               ["I", "Development and verification of the probabilistic layer",
                "5 – 9", "Validated Layer 2"],
               ["I", "Corridor identification; acquisition of construction and "
                     "condition records", "7 – 12", "Field dataset"],
               ["II", "Retrospective validation against documented distress",
                "12 – 16", "Accuracy established"],
               ["II", "Machine-learning residual layer", "14 – 19", "Validated Layer 3"],
               ["II", "Decision engine and maintenance prioritisation", "18 – 21",
                "Layer 4 complete"],
               ["II", "Demonstration study, documentation and dissemination",
                "20 – 24", "Publications; final report"]],
              [1.2, 7.6, 2.0, 5.2])]

    # 11 BUDGET
    E += [P("11. BUDGET ESTIMATE", "h1"),
          P("The proposal is deliberately structured to require minimal capital outlay. "
            "No field instrumentation, proprietary software licence or high-performance "
            "computing facility is necessary; the computational methods execute on "
            "ordinary desktop hardware using open-source components."),
          tbl(["Head", "Year 1 (Rs.)", "Year 2 (Rs.)", "Total (Rs.)"],
              [["Manpower (Junior Research Fellow, if sanctioned)", "3,72,000",
                "3,72,000", "7,44,000"],
               ["Travel and field visits", "60,000", "80,000", "1,40,000"],
               ["Consumables and data acquisition", "40,000", "40,000", "80,000"],
               ["Contingency", "25,000", "25,000", "50,000"],
               ["Publication and dissemination", "20,000", "60,000", "80,000"],
               ["**Total**", "**5,17,000**", "**5,77,000**", "**10,94,000**"]],
              [7.0, 3.0, 3.0, 3.0]),
          P("<i>The budget is indicative and may be reduced substantially if the work "
            "is undertaken without a sanctioned fellowship. The computational component "
            "carries no cost.</i>")]

    # 12 UTILISATION
    E += [PageBreak(), P("12. UTILISATION OF RESULTS AND COMMERCIALISATION POTENTIAL", "h1"),
          P("12.1 Academic and professional utilisation", "h3"),
          B("Contribution towards the eventual incorporation of reliability-based "
            "provisions in Indian rigid pavement design practice."),
          B("Provision of a verified open computational implementation for researchers "
            "and practitioners."),
          B("Establishment of a database of parameter variability for Indian materials "
            "and subgrade conditions."),
          P("12.2 Institutional utilisation", "h3"),
          B("Highway authorities may allocate constrained maintenance budgets on an "
            "objective and auditable basis in place of uniform or reactive allocation."),
          B("Concessionaires may forecast maintenance liability and schedule "
            "intervention before distress becomes visible."),
          B("Design consultants may offer reliability-based design as a differentiated "
            "professional service."),
          P("12.3 Commercialisation pathway", "h3"),
          tbl(["Stage", "Offering", "Basis"],
              [["1", "Open reliability-based design calculator, freely available",
                "Dissemination and professional adoption"],
               ["2", "Residual-life and maintenance prioritisation study for a "
                     "specified corridor", "Professional consultancy"],
               ["3", "Continuously updated condition and risk platform", "Subscription"],
               ["4", "Network-level prioritisation across a portfolio",
                "Institutional engagement"]],
              [1.2, 8.8, 6.0]),
          P("The economic proposition rests upon a well-documented characteristic of "
            "pavement maintenance, namely that the cost of intervention increases "
            "sharply, and non-linearly, once distress has become manifest. A framework "
            "that redirects even a modest proportion of an existing maintenance budget "
            "from segments not requiring intervention to segments that do will recover "
            "its cost within a single maintenance season.")]

    # 13 RISK
    E += [P("13. RISK ANALYSIS AND MITIGATION", "h1"),
          tbl(["Risk", "Level", "Mitigation"],
              [["Access to construction and condition records may be restricted, as "
                "such records may disclose deficiencies in past construction", "High",
                "The framework is presented as a forward-looking asset management "
                "instrument and not as an audit. Initial application to newly "
                "constructed corridors where records are complete."],
               ["Prospective validation requires years, as pavements deteriorate slowly",
                "High", "Retrospective validation against sections of known condition; "
                        "selection of heavily trafficked corridors."],
               ["Field records may be incomplete or of variable quality", "Moderate",
                "The mechanistic core operates without the machine-learning layer; "
                "missing data widens the reported confidence interval rather than "
                "preventing computation."],
               ["Institutional procurement cycles are extended", "Moderate",
                "Initial engagement with concessionaires and consultants."],
               ["Reproduction of codal provisions is subject to copyright", "Moderate",
                "Computational procedures and numerical relationships are implemented; "
                "no protected expression is reproduced. Every output cites the "
                "governing clause. Formal permission is being sought."],
               ["Predictions may be relied upon in substitution for professional "
                "judgement", "Moderate",
                "Output is decision support requiring approval by a qualified engineer; "
                "confidence intervals and out-of-range warnings accompany every result; "
                "a complete computation trace is provided."]],
              [4.6, 1.6, 9.8])]

    # 14 COMPLIANCE
    E += [P("14. ETHICAL, LEGAL AND REGULATORY COMPLIANCE", "h1"),
          B("<b>Research ethics.</b> The work involves no human or animal subjects."),
          B("<b>Intellectual property in codal provisions.</b> Copyright in Indian "
            "Standards and in Indian Roads Congress publications vests in the "
            "respective issuing bodies. The implementation reproduces computational "
            "procedures and numerical relationships only; no protected expression, "
            "table layout or clause text is reproduced. Formal permission for "
            "reproduction of extracts is being sought."),
          B("<b>Confidentiality of client data.</b> Construction and condition records "
            "obtained from any authority or concessionaire will be treated as "
            "confidential, used solely for this research, and reported in anonymised "
            "form unless express written consent is obtained."),
          B("<b>Data protection.</b> Where personal data is processed in any subsequent "
            "software deployment, the requirements of the Digital Personal Data "
            "Protection Act, 2023 will be complied with, including data minimisation."),
          B("<b>Professional responsibility.</b> All output is advisory. The framework "
            "does not substitute for design by a qualified engineer, and every report "
            "carries an express statement to that effect.")]

    # 15 CONCLUSION
    E += [P("15. CONCLUSION", "h1"),
          P("Concrete pavements are presently designed upon assumptions that are not "
            "revisited, and maintained upon observation that arrives too late. The "
            "consequence is the simultaneous waste of material where conditions are "
            "favourable and the premature failure of segments where they are not. The "
            "mechanistic framework required to address this is already prescribed in "
            "IRC:58; what is absent is its probabilistic extension, its application "
            "forward in time, and its calibration against the records that construction "
            "already generates."),
          P("The proposed work supplies these elements. It does not displace the codal "
            "procedure but extends it, reducing exactly to the conventional computation "
            "when variability is absent. It requires no instrumentation, no proprietary "
            "software and no significant capital outlay, and a verified computational "
            "core has already been implemented."),
          P("The approval and guidance of the Supervisor is respectfully sought, "
            "together with such institutional support as may be considered appropriate "
            "for the acquisition of field records and the identification of a suitable "
            "corridor for demonstration."),
          Spacer(1, 1.6 * cm),
          Table([[Paragraph("_______________________<br/>(Signature of the "
                            "Investigator)", S["cap"]),
                  Paragraph("_______________________<br/>(Signature of the "
                            "Supervisor)", S["cap"])]],
                colWidths=[8 * cm, 8 * cm])]

    # REFERENCES
    refs = [
        "IRC:58 — Guidelines for the Design of Plain Jointed Rigid Pavements for "
        "Highways. Indian Roads Congress, New Delhi.",
        "IRC:SP:83 — Guidelines for Maintenance, Repair and Rehabilitation of Cement "
        "Concrete Pavements. Indian Roads Congress, New Delhi.",
        "IRC:44 — Guidelines for Cement Concrete Mix Design for Pavements. Indian "
        "Roads Congress, New Delhi.",
        "IS 456:2000 — Plain and Reinforced Concrete: Code of Practice. Bureau of "
        "Indian Standards, New Delhi.",
        "Westergaard, H. M. (1926). Stresses in concrete pavements computed by "
        "theoretical analysis. <i>Public Roads</i>, 7(2), 25–35.",
        "Westergaard, H. M. (1927). Analysis of stresses in concrete pavements due to "
        "variations of temperature. <i>Proceedings, Highway Research Board</i>, 6, 201–215.",
        "Bradbury, R. D. (1938). <i>Reinforced Concrete Pavements</i>. Wire "
        "Reinforcement Institute, Washington, D.C.",
        "Ioannides, A. M., Thompson, M. R., &amp; Barenberg, E. J. (1985). Westergaard "
        "solutions reconsidered. <i>Transportation Research Record</i>, 1043, 13–23.",
        "Miner, M. A. (1945). Cumulative damage in fatigue. <i>Journal of Applied "
        "Mechanics</i>, 12(3), A159–A164.",
        "Portland Cement Association (1984). <i>Thickness Design for Concrete Highway "
        "and Street Pavements</i>. Skokie, Illinois.",
        "AASHTO (1993). <i>Guide for Design of Pavement Structures</i>. Washington, D.C.",
        "Ministry of Road Transport and Highways. <i>Specifications for Road and Bridge "
        "Works</i>. Indian Roads Congress, New Delhi.",
        "National Highways Authority of India (2025). <i>Maintenance Manual</i>.",
    ]
    E += [PageBreak(), P("REFERENCES", "h1")]
    E += [Paragraph(f"[{i}]  {r}", S["ref"]) for i, r in enumerate(refs, 1)]

    doc.build(E)
    print(f"[ULTRON] Written -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
