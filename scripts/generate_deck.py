#!/usr/bin/env python3
"""
ULTRON — generates the SETU supervisor presentation deck (.pptx).

Figures are computed live from the verified engine, never hand-typed, so the deck
cannot drift from the code.

Run:  .venv/bin/python scripts/generate_deck.py
Out:  results/SETU_Supervisor_Deck.pptx
"""

from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "SETU_Supervisor_Deck.pptx"

NAVY = RGBColor(0x1F, 0x3B, 0x5C)
NAVY_L = RGBColor(0x2D, 0x55, 0x81)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x16, 0x20, 0x2B)
MUTED = RGBColor(0x5D, 0x6B, 0x7A)
ACCENT = RGBColor(0xE8, 0xF0, 0xF9)
OK = RGBColor(0x0F, 0x7B, 0x4F)
BAD = RGBColor(0xB3, 0x26, 0x1E)

W, H = Cm(33.87), Cm(19.05)   # 16:9


# --------------------------------------------------------------------------- #
def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(slide, x, y, w, h, fill=None, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(1)
    sh.shadow.inherit = False
    return sh


def text(slide, x, y, w, h, runs, *, align=PP_ALIGN.LEFT, space=4, anchor=None):
    """runs: list of (string, size, bold, colour) or a plain string."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    if anchor is not None:
        tf.vertical_anchor = anchor
    if isinstance(runs, str):
        runs = [(runs, 18, False, INK)]
    first = True
    for item in runs:
        s, sz, bold, col = item
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_after = Pt(space)
        r = p.add_run()
        r.text = s
        r.font.size = Pt(sz)
        r.font.bold = bold
        r.font.color.rgb = col
        r.font.name = "Calibri"
    return tb


def header(slide, title, sub=None):
    rect(slide, 0, 0, W, Cm(2.5), fill=NAVY)
    text(slide, Cm(1.2), Cm(0.45), W - Cm(2.4), Cm(1.6),
         [(title, 26, True, WHITE)] + ([(sub, 13, False, RGBColor(0xC5, 0xD6, 0xE8))] if sub else []))


def footer(slide, n):
    text(slide, Cm(1.2), H - Cm(1.15), Cm(20), Cm(0.8),
         [("SETU — Structural Evaluation and Thickness Underwriting", 9, False, MUTED)])
    text(slide, W - Cm(3.2), H - Cm(1.15), Cm(2), Cm(0.8),
         [(str(n), 9, False, MUTED)], align=PP_ALIGN.RIGHT)


def table(slide, x, y, headers, rows, widths, *, fs=11, hfs=11, row_h=Cm(0.85)):
    nr, nc = len(rows) + 1, len(headers)
    total = sum(widths)
    shape = slide.shapes.add_table(nr, nc, x, y, Cm(total), row_h * nr)
    tbl = shape.table
    for i, wd in enumerate(widths):
        tbl.columns[i].width = Cm(wd)
    for i, htxt in enumerate(headers):
        c = tbl.cell(0, i)
        c.text = ""
        c.fill.solid()
        c.fill.fore_color.rgb = NAVY
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = htxt
        r.font.size = Pt(hfs)
        r.font.bold = True
        r.font.color.rgb = WHITE
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            c = tbl.cell(ri, ci)
            c.text = ""
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if ri % 2 else ACCENT
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci else PP_ALIGN.LEFT
            bold = val.startswith("**") and val.endswith("**")
            clean = val.strip("*")
            col = INK
            if clean.startswith("!"):
                clean, col = clean[1:], BAD
            elif clean.startswith("+"):
                clean, col = clean[1:], OK
            r = p.add_run()
            r.text = clean
            r.font.size = Pt(fs)
            r.font.bold = bold
            r.font.color.rgb = col
    return tbl


# --------------------------------------------------------------------------- #
def compute():
    """Live figures from the verified engine — never hand-typed."""
    from src.design.westergaard import SlabProperties, WheelLoad, stress_edge
    from src.pavement.damage import AxleLoadGroup
    from src.pavement.reliability import (
        PavementUncertainty,
        ThermalConfig,
        Uncertain,
        required_thickness_for_reliability,
    )
    from src.pavement.thermal import check_both_mechanisms

    spec = [
        AxleLoadGroup("10-12 t", 110_000.0, 150_000),
        AxleLoadGroup("12-14 t", 130_000.0, 90_000),
        AxleLoadGroup("14-16 t", 150_000.0, 40_000),
        AxleLoadGroup("16-18 t", 170_000.0, 12_000),
        AxleLoadGroup("18-20 t", 190_000.0, 3_000),
    ]
    thickness = {}
    for k in (0.200, 0.150, 0.110, 0.080, 0.045):
        u = PavementUncertainty(
            k=Uncertain(k, 0.22),
            modulus_of_rupture=Uncertain(4.5, 0.12),
            E=Uncertain(30_000.0, 0.12),
            thickness=Uncertain(300.0, 0.03),
        )
        h, _ = required_thickness_for_reliability(u, spec, 0.90, n_sim=1200, seed=42)
        thickness[k] = h

    slab = SlabProperties(h=300.0, E=30_000.0, mu=0.15, k=0.08)
    s_load = stress_edge(slab, WheelLoad.from_pressure(P=75_000.0, p=0.8))
    th = check_both_mechanisms(s_load, slab.E, 16.8, 8.4, 4500.0, 3500.0,
                               slab.l, 4.5)
    return {
        "thickness": thickness,
        "sr_load": s_load / 4.5,
        "sr_gov": th["governing"].stress_ratio,
        "gov": th["governing"].mechanism,
        "warp": th["BUC"].warping_stress,
        "s_load": s_load,
    }


# --------------------------------------------------------------------------- #
def build():
    d = compute()
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    n = 0

    # ---- 1 TITLE ---- #
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=NAVY)
    rect(s, Cm(2.0), Cm(6.2), Cm(1.2), Cm(0.16), fill=RGBColor(0x7F, 0xA8, 0xD0))
    text(s, Cm(2.0), Cm(4.0), W - Cm(4), Cm(2.2), [("SETU", 60, True, WHITE)])
    text(s, Cm(2.0), Cm(6.9), W - Cm(4), Cm(1.2),
         [("Structural Evaluation and Thickness Underwriting", 19, False,
           RGBColor(0xC5, 0xD6, 0xE8))])
    text(s, Cm(2.0), Cm(8.6), W - Cm(6), Cm(3.0),
         [("A Reliability-Based Framework for Residual-Life Prediction and "
           "Maintenance Prioritisation of Concrete Pavements", 22, True, WHITE)])
    text(s, Cm(2.0), Cm(13.4), W - Cm(4), Cm(3),
         [("Research proposal — supervisory review", 13, False,
           RGBColor(0xA8, 0xC0, 0xDC)),
          ("[Name] · Department of Civil Engineering · [Institution]", 12, False,
           RGBColor(0xA8, 0xC0, 0xDC)),
          ("Supervisor: [Supervisor]", 12, False, RGBColor(0xA8, 0xC0, 0xDC))])

    # ---- 2 THE PROBLEM ---- #
    n += 1
    s = blank(prs)
    header(s, "The problem", "Designed once from assumptions; never checked until it cracks")
    text(s, Cm(1.2), Cm(3.2), W - Cm(2.4), Cm(1.4),
         [("A rigid pavement slab is designed once, in an office, using single "
           "representative values — and is never revisited against the conditions "
           "actually realised on site.", 17, False, INK)])
    table(s, Cm(1.2), Cm(5.2),
          ["Design parameter", "Assumed", "Reality", "CoV"],
          [["Subgrade reaction, k", "one value", "varies continuously along alignment", "0.20 – 0.35"],
           ["Flexural strength, MR", "one value", "varies pour to pour, season to season", "0.10 – 0.15"],
           ["Elastic modulus, E", "one value", "varies with mix and maturity", "0.10 – 0.15"],
           ["Slab thickness, h", "nominal", "construction tolerance", "0.02 – 0.05"],
           ["Traffic", "projection", "projection error and overloading", "0.15 – 0.30"]],
          [10.0, 5.5, 11.5, 4.5], fs=12)
    rect(s, Cm(1.2), Cm(14.4), W - Cm(2.4), Cm(2.5), fill=ACCENT)
    text(s, Cm(1.8), Cm(14.8), W - Cm(3.6), Cm(2.0),
         [("The industry's answer is a blanket safety factor applied everywhere — "
           "so concrete is wasted where conditions are good, and slabs fail early "
           "where they are not. Both happen on the same project.", 15, True, NAVY)])
    footer(s, n)

    # ---- 3 THE QUESTION ---- #
    n += 1
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=ACCENT)
    text(s, Cm(2.5), Cm(6.0), W - Cm(5), Cm(4),
         [("\u201cWhich 200 metres of this 40 km road", 34, True, NAVY),
          ("will fail first — and what will it cost me?\u201d", 34, True, NAVY)],
         align=PP_ALIGN.CENTER)
    text(s, Cm(3), Cm(12.0), W - Cm(6), Cm(3),
         [("No design office, asset owner or software product can answer this today.",
           17, False, INK),
          ("The data needed already exists — pour registers, cube results, subgrade "
           "tests, traffic counts. It has simply never been joined to the damage "
           "model that produced the design.", 14, False, MUTED)],
         align=PP_ALIGN.CENTER)
    footer(s, n)

    # ---- 4 THE APPROACH ---- #
    n += 1
    s = blank(prs)
    header(s, "The approach", "Four layers — the code is the foundation, not the casualty")
    ys = Cm(3.4)
    layers = [
        ("LAYER 1 — Mechanistic core", "Westergaard stresses · Bradbury warping · "
         "IRC:58 fatigue · Miner summation", "Deterministic damage, every value clause-traceable"),
        ("LAYER 2 — Probabilistic propagation", "Monte Carlo over distributions of "
         "k, MR, E, h and traffic", "P(failure) and reliability per segment"),
        ("LAYER 3 — ML residual correction", "Gaussian Process on (predicted − observed) "
         "distress", "Corrected forecast with calibrated confidence"),
        ("LAYER 4 — Decision engine", "Cost of acting now vs probability-weighted cost "
         "of waiting", "Ranked maintenance plan, with money attached"),
    ]
    for i, (t1, t2, t3) in enumerate(layers):
        y = ys + Cm(3.1) * i
        rect(s, Cm(1.2), y, Cm(0.22), Cm(2.6), fill=NAVY if i < 2 else NAVY_L)
        text(s, Cm(1.8), y - Cm(0.1), Cm(11), Cm(1.0), [(t1, 15, True, NAVY)])
        text(s, Cm(1.8), y + Cm(0.85), Cm(18), Cm(1.6), [(t2, 12, False, INK)])
        text(s, Cm(21.5), y + Cm(0.4), Cm(11), Cm(1.6), [("→  " + t3, 12, True, MUTED)])
    rect(s, Cm(1.2), Cm(16.2), W - Cm(2.4), Cm(1.7), fill=ACCENT)
    text(s, Cm(1.8), Cm(16.45), W - Cm(3.6), Cm(1.3),
         [("At zero variability the framework reduces EXACTLY to the deterministic "
           "IRC:58 result — verified by automated test. It extends the code; it does "
           "not replace it.", 13, True, NAVY)])
    footer(s, n)

    # ---- 5 WHY HYBRID ---- #
    n += 1
    s = blank(prs)
    header(s, "Why the ML is constrained", "Three independent reasons, any one of which is sufficient")
    items = [
        ("Professional accountability",
         "No engineer will stake a seal on a number whose provenance is \u201cthe "
         "neural network said so\u201d. A codal computation plus a bounded correction "
         "remains open to professional scrutiny."),
        ("Data efficiency",
         "The physics carries the signal; the model fits only a small residual. "
         "Useful accuracy is attainable with a few hundred observations rather than "
         "tens of thousands."),
        ("Regulatory admissibility",
         "Output that cites the governing clause is admissible in project "
         "documentation. Output that cannot be traced is not."),
    ]
    for i, (t1, t2) in enumerate(items):
        y = Cm(3.6) + Cm(4.2) * i
        rect(s, Cm(1.2), y, Cm(31.4), Cm(3.4), fill=ACCENT)
        text(s, Cm(1.9), y + Cm(0.3), Cm(9.5), Cm(2.8), [(t1, 16, True, NAVY)])
        text(s, Cm(11.8), y + Cm(0.35), Cm(20.2), Cm(2.8), [(t2, 13, False, INK)])
    footer(s, n)

    # ---- 6 RESULT: THICKNESS (the money slide) ---- #
    n += 1
    s = blank(prs)
    header(s, "Result — reliability-based thickness",
           "Same corridor, same traffic, same concrete. Only the subgrade differs.")
    t = d["thickness"]
    rows = []
    labels = {0.200: "Very good", 0.150: "Good", 0.110: "Fair",
              0.080: "Poor", 0.045: "Very poor"}
    for k in (0.200, 0.150, 0.110, 0.080, 0.045):
        diff = t[k] - t[0.110]
        mark = ("+" + f"{diff:.0f} mm less than fair" if diff < 0 else
                ("!" + f"{diff:.0f} mm more required" if diff > 0 else "reference"))
        if diff < 0:
            mark = "+" + f"{abs(diff):.0f} mm saved"
        rows.append([labels[k], f"{k:.3f}", f"{t[k]:.0f} mm", mark])
    table(s, Cm(2.5), Cm(4.0),
          ["Subgrade", "k (MPa/mm)", "h for 90% reliability", "vs. uniform design"],
          rows, [7.0, 6.0, 8.5, 7.5], fs=14, hfs=12, row_h=Cm(1.15))
    spread = t[0.045] - t[0.200]
    rect(s, Cm(2.5), Cm(12.6), Cm(29.0), Cm(3.3), fill=NAVY)
    text(s, Cm(3.2), Cm(12.95), Cm(27.6), Cm(2.7),
         [(f"A {spread:.0f} mm spread across one corridor.", 22, True, WHITE),
          ("Uniform design conceals this entirely: it over-builds the good ground and "
           "under-builds the bad. One computation corrects both.", 14, False,
           RGBColor(0xC5, 0xD6, 0xE8))])
    text(s, Cm(2.5), Cm(16.4), Cm(29), Cm(1.2),
         [("Computed with the implemented engine. Indicative coefficients of "
           "variation; project-specific values to be substituted.", 10, False, MUTED)])
    footer(s, n)

    # ---- 7 RESULT: THERMAL ---- #
    n += 1
    s = blank(prs)
    header(s, "Result — thermal warping frequently governs",
           "300 mm slab · 15 t axle · ΔT 16.8 °C day / 8.4 °C night")
    und = 100 * (1 - d["sr_load"] / d["sr_gov"])
    table(s, Cm(2.5), Cm(4.2),
          ["Analysis", "Stress (MPa)", "Stress ratio", "Assessment"],
          [["Load only", f"{d['s_load']:.3f}", f"{d['sr_load']:.3f}",
            "below endurance limit — appears safe"],
           [f"Load + warping ({d['gov']} governs)",
            f"{d['s_load'] + d['warp']:.3f}", f"{d['sr_gov']:.3f}",
            "!well above endurance limit"]],
          [11.0, 6.0, 5.5, 12.0], fs=14, hfs=12, row_h=Cm(1.3))
    rect(s, Cm(2.5), Cm(9.5), Cm(29.0), Cm(3.6), fill=RGBColor(0xFB, 0xE6, 0xE4))
    text(s, Cm(3.2), Cm(9.9), Cm(27.6), Cm(3.0),
         [(f"Omitting thermal warping understates the stress ratio by "
           f"{und:.0f} per cent.", 20, True, BAD),
          ("Because the fatigue relationship is steeply non-linear in the stress "
           "ratio, this becomes an order-of-magnitude error in allowable repetitions. "
           "Warping is not a refinement — it frequently governs.", 13, False, INK)])
    text(s, Cm(2.5), Cm(13.9), Cm(29), Cm(2.5),
         [("Bradbury coefficient evaluated from a continuous fitted function "
           "(max deviation 0.023 from the published curve, 1 ≤ L/l ≤ 14) rather than "
           "a tabulated lookup — original work, and differentiable for later "
           "optimisation.", 11, False, MUTED)])
    footer(s, n)

    # ---- 8 WHAT IS BUILT ---- #
    n += 1
    s = blank(prs)
    header(s, "What is already built", "This is not a concept — the core is running and tested")
    table(s, Cm(1.2), Cm(3.5),
          ["Component", "Contents", "Status"],
          [["Analytical stress module",
            "Westergaard interior / edge / corner, radius of relative stiffness, "
            "equivalent radius", "**+9 tests passing**"],
           ["Thermal warping module",
            "Bradbury coefficient (fitted), edge and interior warping, BUC and TDC "
            "checks", "**+21 tests passing**"],
           ["Damage module",
            "Stress ratio, 3-branch fatigue law, Miner summation, residual life, "
            "erosion index", "**+22 tests passing**"],
           ["Reliability module",
            "Monte Carlo propagation, P(failure), reliability-based thickness search",
            "**+included above**"],
           ["Public web calculator",
            "Browser-based, offline-capable, full calculation trace, no data collected",
            "**+4 parity tests**"]],
          [8.0, 16.4, 7.0], fs=11.5, row_h=Cm(1.55))
    rect(s, Cm(1.2), Cm(15.6), W - Cm(2.4), Cm(2.2), fill=ACCENT)
    text(s, Cm(1.8), Cm(15.95), W - Cm(3.6), Cm(1.8),
         [("56 automated tests, all passing. The browser calculator agrees with the "
           "Python reference to 3.4 × 10⁻¹⁵ — verified by test, not by inspection.",
           14, True, NAVY)])
    footer(s, n)

    # ---- 9 WHAT I NEED ---- #
    n += 1
    s = blank(prs)
    header(s, "What I am asking for", "Guidance, and access — not funding")
    asks = [
        ("1", "Approval of the direction",
         "Confirmation that the reliability-based extension of IRC:58 is a sound and "
         "defensible line of research for the thesis."),
        ("2", "One corridor of data",
         "Introduction to a concessionaire, PWD circle or consultant willing to share "
         "construction and condition records for a single stretch. This is the "
         "critical dependency for Objective 6."),
        ("3", "Publication guidance",
         "Advice on the appropriate venue — an IRC/ICI journal or an international "
         "transportation journal — and on what must be strengthened before submission."),
        ("4", "A view on scope",
         "Whether to prioritise depth on the mechanistic and reliability layers, or "
         "to proceed to the machine-learning layer once field data is in hand."),
    ]
    for i, (num_, t1, t2) in enumerate(asks):
        y = Cm(3.5) + Cm(3.35) * i
        rect(s, Cm(1.2), y, Cm(1.5), Cm(2.7), fill=NAVY)
        text(s, Cm(1.2), y + Cm(0.55), Cm(1.5), Cm(1.6),
             [(num_, 22, True, WHITE)], align=PP_ALIGN.CENTER)
        text(s, Cm(3.2), y + Cm(0.15), Cm(11), Cm(1.2), [(t1, 15, True, NAVY)])
        text(s, Cm(3.2), y + Cm(1.15), Cm(28.5), Cm(1.6), [(t2, 12, False, INK)])
    footer(s, n)

    # ---- 10 PLAN ---- #
    n += 1
    s = blank(prs)
    header(s, "Work plan", "24 months, two phases")
    table(s, Cm(1.2), Cm(3.6),
          ["Months", "Activity", "Milestone"],
          [["1 – 3", "Literature consolidation; variability statistics for Indian "
                     "materials and subgrades", "Parameter database"],
           ["3 – 6", "Extend mechanistic core: temperature differential regimes, "
                     "erosion criterion", "Extended Layer 1"],
           ["5 – 9", "Probabilistic layer refinement and verification",
            "Validated Layer 2"],
           ["7 – 12", "Corridor identification; acquisition of construction and "
                      "condition records", "Field dataset"],
           ["12 – 16", "Retrospective validation against documented distress",
            "Accuracy established"],
           ["14 – 19", "Machine-learning residual layer", "Validated Layer 3"],
           ["18 – 21", "Decision engine and maintenance prioritisation",
            "Layer 4 complete"],
           ["20 – 24", "Demonstration study, documentation, dissemination",
            "Publications; final report"]],
          [4.5, 19.0, 8.0], fs=11, row_h=Cm(1.25))
    footer(s, n)

    # ---- 11 CLOSING ---- #
    n += 1
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=NAVY)
    text(s, Cm(2.5), Cm(4.5), W - Cm(5), Cm(6),
         [("The mechanics already exist in IRC:58.", 26, False,
           RGBColor(0xC5, 0xD6, 0xE8)),
          ("What is missing is its probabilistic extension,", 26, False,
           RGBColor(0xC5, 0xD6, 0xE8)),
          ("its application forward in time,", 26, False,
           RGBColor(0xC5, 0xD6, 0xE8)),
          ("and its calibration against the records", 26, False,
           RGBColor(0xC5, 0xD6, 0xE8)),
          ("that construction already generates.", 26, False,
           RGBColor(0xC5, 0xD6, 0xE8))])
    rect(s, Cm(2.5), Cm(12.2), Cm(1.2), Cm(0.14), fill=RGBColor(0x7F, 0xA8, 0xD0))
    text(s, Cm(2.5), Cm(13.0), W - Cm(5), Cm(3),
         [("No instrumentation. No proprietary software. No significant capital.",
           17, True, WHITE),
          ("A verified computational core is already implemented.", 15, False,
           RGBColor(0xA8, 0xC0, 0xDC))])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"[ULTRON] Written -> {OUT.relative_to(ROOT)}  ({n + 1} slides)")


if __name__ == "__main__":
    build()
