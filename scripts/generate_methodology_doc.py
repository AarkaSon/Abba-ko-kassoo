#!/usr/bin/env python3
"""
ULTRON — generates the beginner-friendly methodology document (.docx)
for projects C1, C4 and C5.

Written for a reader with NO prior exposure to machine learning.
Run:  .venv/bin/python scripts/generate_methodology_doc.py
Out:  results/C1_C4_C5_Methodology_Explained.docx
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
OUT = ROOT / "results" / "C1_C4_C5_Methodology_Explained.docx"

NAVY = RGBColor(0x1F, 0x3B, 0x5C)
INK = RGBColor(0x16, 0x20, 0x2B)
GREY = RGBColor(0x5D, 0x6B, 0x7A)
GREEN = RGBColor(0x0F, 0x7B, 0x4F)
RED = RGBColor(0xB3, 0x26, 0x1E)


def cell_bg(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def field(par, instr):
    r = par.add_run()
    for tag, attr, val in (("w:fldChar", "w:fldCharType", "begin"),):
        e = OxmlElement(tag); e.set(qn(attr), val); r._r.append(e)
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
    it.text = instr; r._r.append(it)
    for val in ("separate", "end"):
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), val); r._r.append(e)


def setup(doc):
    st = doc.styles["Normal"]
    st.font.name = "Calibri"; st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(7)
    st.paragraph_format.line_spacing = 1.18
    for nm, sz, col in (("Heading 1", 17, NAVY), ("Heading 2", 14, NAVY),
                        ("Heading 3", 12, INK)):
        s = doc.styles[nm]
        s.font.name = "Calibri"; s.font.size = Pt(sz)
        s.font.color.rgb = col; s.font.bold = True
        s.paragraph_format.space_before = Pt(14)
        s.paragraph_format.space_after = Pt(6)
        s.paragraph_format.keep_with_next = True


def P(doc, t, *, align=None, size=None, bold=False, italic=False, color=None,
      after=None, indent=None):
    p = doc.add_paragraph()
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if indent is not None: p.paragraph_format.left_indent = Cm(indent)
    r = p.add_run(t); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    return p


def rich(doc, parts, *, indent=None, after=None, align=None):
    """parts = list of (text, bold, italic, color|None)"""
    p = doc.add_paragraph()
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent is not None: p.paragraph_format.left_indent = Cm(indent)
    if after is not None: p.paragraph_format.space_after = Pt(after)
    for t, b, i, c in parts:
        r = p.add_run(t); r.bold = b; r.italic = i
        if c: r.font.color.rgb = c
    return p


def B(doc, t, *, bold_prefix=None, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.8 + 0.6 * level)
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r = p.add_run(bold_prefix); r.bold = True
    p.add_run(t)
    return p


def N(doc, t, *, bold_prefix=None):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r = p.add_run(bold_prefix); r.bold = True
    p.add_run(t)
    return p


def table(doc, headers, rows, widths, *, fs=9.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        pp = c.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = pp.add_run(h); r.bold = True; r.font.size = Pt(fs)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell_bg(c, "1F3B5C")
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""
            pp = cs[i].paragraphs[0]; pp.paragraph_format.space_after = Pt(2)
            bold = v.startswith("**") and v.endswith("**")
            txt = v.strip("*")
            col = None
            if txt.startswith("!"): txt, col = txt[1:], RED
            elif txt.startswith("+"): txt, col = txt[1:], GREEN
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
    c.paragraph_format.space_after = Pt(12)


def callout(doc, title, body, fill="E8F0F9", tcol=NAVY):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; c.text = ""
    cell_bg(c, fill)
    p1 = c.paragraphs[0]; p1.paragraph_format.space_after = Pt(3)
    r = p1.add_run(title); r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = tcol
    p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r2 = p2.add_run(body); r2.font.size = Pt(10)
    t.rows[0].cells[0].width = Cm(16)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t


def build():
    doc = Document(); setup(doc)
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.top_margin = s.bottom_margin = Cm(2.2)
    s.left_margin = Cm(2.5); s.right_margin = Cm(2.0)

    # ---------------- COVER ----------------
    P(doc, "PROJECT METHODOLOGY — EXPLAINED SIMPLY",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=12, bold=True, after=2)
    P(doc, "A guide for students beginning research in concrete technology and AI",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=10, italic=True, after=16)

    P(doc, "Predicting Concrete Behaviour Before It Happens",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=24, bold=True, after=4)
    P(doc, "Projects C1, C4 and C5", align=WD_ALIGN_PARAGRAPH.CENTER,
      size=14, italic=True, after=18)

    table(doc, ["Item", "Details"], [
        ["**Document purpose**", "To explain, in plain language, what these three "
         "projects do, how they work step by step, what they will produce, and why "
         "the construction industry should care."],
        ["**Intended reader**", "A student or engineer with no previous exposure to "
         "machine learning. No mathematics beyond first-year engineering is assumed."],
        ["**Project C1**", "Early-Age Strength Prediction — knowing the 28-day "
         "strength of concrete from a 7-day test"],
        ["**Project C4**", "SCM Substitution Optimiser — choosing the best mix of "
         "cement replacements for strength, cost and carbon"],
        ["**Project C5**", "Workability from Video — measuring slump from an "
         "ordinary smartphone recording"],
        ["**Team**", "4 B.Tech students + 2 PhD scholars"],
        ["**Duration**", "6 months"],
        ["**Institution**", "Department of Civil Engineering, IIT Bhubaneswar"],
        ["**Date**", "________________"],
    ], [4.0, 12.0], fs=10)

    doc.add_page_break()

    # ---------------- CONTENTS ----------------
    doc.add_heading("CONTENTS", 1)
    table(doc, ["Part", "Section", "Page"], [
        ["1", "Understanding the problem: why concrete is unpredictable", "3"],
        ["2", "What is machine learning? A plain explanation", "4"],
        ["3", "Our core method: physics first, AI second", "5"],
        ["4", "Project C1 — Early-Age Strength Prediction", "7"],
        ["5", "Project C4 — SCM Substitution Optimiser", "11"],
        ["6", "Project C5 — Workability from Video", "14"],
        ["7", "Expected results and outputs", "17"],
        ["8", "Impact on the construction industry", "18"],
        ["9", "Common mistakes to avoid", "20"],
        ["10", "Glossary of terms", "21"],
    ], [1.5, 11.5, 2.0], fs=10)

    doc.add_page_break()

    # ---------------- PART 1 ----------------
    doc.add_heading("PART 1 — UNDERSTANDING THE PROBLEM", 1)

    doc.add_heading("1.1 Concrete is not a manufactured product", 2)
    P(doc, "A steel beam leaves the factory with a known strength. Concrete does not. "
           "Concrete is mixed from sand, stone, cement and water that vary from one "
           "truckload to the next, then hardens slowly for weeks under whatever "
           "weather happens to occur. Two batches made from the same written recipe, "
           "on the same day, in the same plant, will not have the same strength.")
    P(doc, "This is not a failure of workmanship. It is the nature of the material. "
           "The entire discipline of concrete quality control exists because of it.")

    doc.add_heading("1.2 How much does it actually vary?", 2)
    P(doc, "A study of four Indian ready-mixed concrete (RMC) plants measured the "
           "spread of strength results at each plant. The spread is described by the "
           "standard deviation, written as σ (sigma). A small σ means a consistent "
           "plant; a large σ means an unpredictable one.")

    figure(doc, "fig1_plant_sigma.png",
           "Figure 1 — Strength variability at four Indian RMC plants. "
           "Source: NBM&CW quality-control model study. The middle two σ values are "
           "interpolated within the published range; the coefficients of variation "
           "are as published.")

    callout(doc, "The most important fact in this document",
            "The plant with the WORST consistency (σ = 6.57 MPa) was fully automatic "
            "with imported equipment. The plant with the BEST consistency (σ = 1.92 MPa) "
            "was a small semi-automatic plant. Buying better machines did not produce "
            "better concrete. This tells us that concrete quality is not an equipment "
            "problem — it is an information problem. And information problems are "
            "exactly what these three projects are designed to solve.")

    doc.add_heading("1.3 Why variability costs money", 2)
    P(doc, "Indian Standard IS 456 requires the concrete producer to aim higher than "
           "the strength the customer ordered, to allow for variability. The rule is:")
    P(doc, "Target mean strength  =  f_ck  +  1.65 × σ",
      align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, after=8)
    P(doc, "In words: aim above the required strength by 1.65 times your plant's "
           "standard deviation. A plant that is inconsistent must therefore add extra "
           "cement to every single cubic metre it makes — forever.")

    figure(doc, "fig2_cement_penalty.png",
           "Figure 2 — Extra cement and extra CO₂ required per cubic metre, purely "
           "because of variability. Computed from IS 456 cl. 8.2.4.1 using an "
           "approximate planning figure of 5 kg cement per MPa and 0.9 kg CO₂ per kg "
           "of cement.")

    P(doc, "The consequences show up throughout the industry:")
    B(doc, "20–30% of construction work is redone because of weak concrete, "
           "increasing project cost by roughly 15%.")
    B(doc, "Manual batching causes slump to vary by up to 20 mm.")
    B(doc, "Poor-quality aggregates produce concrete 15–20% weaker than required.")
    B(doc, "Only about 60% of small RMC plants meet BIS requirements; only about "
           "20% of their workers have formal training.")

    figure(doc, "fig9_industry_impact.png",
           "Figure 3 — Documented state of concrete quality control in India. "
           "Source: Construction Times, September 2025.")

    doc.add_page_break()

    # ---------------- PART 2 ----------------
    doc.add_heading("PART 2 — WHAT IS MACHINE LEARNING?", 1)

    doc.add_heading("2.1 The idea, without jargon", 2)
    P(doc, "Suppose you have tested 500 concrete cubes. For each one you know the "
           "recipe (how much cement, water, sand, stone) and you know the strength "
           "that resulted. Machine learning is simply a method of finding the pattern "
           "that connects the recipe to the strength — automatically, from the data, "
           "rather than by deriving an equation by hand.")
    P(doc, "Once the pattern is found, you can give the computer a new recipe it has "
           "never seen and it will estimate the strength.")

    callout(doc, "An everyday comparison",
            "An experienced concrete technologist can look at a mix design and say "
            "'that will give you about 35 MPa'. He is not solving equations. He has "
            "seen thousands of mixes and learned the pattern. Machine learning does "
            "the same thing, but it can hold far more examples in memory than a person "
            "can, and it never forgets.")

    doc.add_heading("2.2 Three terms you will hear constantly", 2)
    table(doc, ["Term", "What it means", "Concrete example"], [
        ["**Feature**", "An input — something you know before the test",
         "Cement content, water-cement ratio, curing temperature, age"],
        ["**Target**", "The output — the thing you want to predict",
         "28-day compressive strength in MPa"],
        ["**Training**", "Showing the computer many examples so it can learn the pattern",
         "Feeding it 500 past mix designs with their known strengths"],
        ["**Validation**", "Testing the learned pattern on data it has never seen, "
         "to check it actually works", "Holding back 100 mixes, then checking the "
         "predictions against their real strengths"],
        ["**Uncertainty**", "How sure the prediction is",
         "'38.2 MPa' is a guess. '38.2 ± 4.1 MPa' is engineering."],
    ], [2.6, 6.0, 7.4], fs=9.5)

    doc.add_heading("2.3 Why plain machine learning is not enough for concrete", 2)
    P(doc, "It is tempting to feed all the data into a neural network and let it "
           "decide. For concrete this is a mistake, for four reasons that a beginner "
           "should understand from the start:")
    N(doc, "A structural engineer must sign the design. He cannot sign a number whose "
           "only justification is 'the computer said so'. It is not defensible in "
           "front of a client, an insurer, or a court.",
      bold_prefix="Accountability. ")
    N(doc, "Neural networks need tens of thousands of examples. A student project will "
           "have a few hundred. With small data, a complex model memorises instead of "
           "learning, and then fails confidently on anything new.",
      bold_prefix="Data hunger. ")
    N(doc, "Indian Standards define how mix design must be done. A prediction that "
           "cannot be traced back to a code clause cannot be used in project "
           "documentation.", bold_prefix="Codal compliance. ")
    N(doc, "If the model gives a wrong answer, you must be able to see why. A black "
           "box gives you nothing to investigate.", bold_prefix="Diagnosability. ")

    doc.add_page_break()

    # ---------------- PART 3 ----------------
    doc.add_heading("PART 3 — OUR CORE METHOD: PHYSICS FIRST, AI SECOND", 1)

    P(doc, "All three projects use the same underlying approach. Learn it once and "
           "you understand all of them. It is called a hybrid or physics-constrained "
           "model, and the idea is simple.")

    callout(doc, "The whole method in one sentence",
            "Use the established engineering equation to make the prediction, then use "
            "machine learning only to correct the small error that the equation leaves "
            "behind.", fill="CDE6D8", tcol=GREEN)

    doc.add_heading("3.1 Why this works so well", 2)
    P(doc, "Established equations such as Abrams' law and the maturity method already "
           "capture most of the behaviour of concrete. They are not perfect — they "
           "were derived from particular materials in particular conditions — but they "
           "get you most of the way there.")
    P(doc, "The difference between what the equation predicts and what the laboratory "
           "actually measures is called the residual. The residual is small, and it "
           "contains everything the equation missed: the peculiarities of your local "
           "aggregate, your particular fly ash, your plant's habits.")
    rich(doc, [("Machine learning is very good at learning small patterns from small "
                "amounts of data. So we let the equation do the heavy lifting, and we "
                "train the model on the residual only.", False, False, None)])

    doc.add_heading("3.2 The three layers", 2)
    table(doc, ["Layer", "What it does", "Why it matters"], [
        ["**Layer 1 — Physics**",
         "Applies the codal equation (maturity method, Abrams' law, IS 10262 procedure)",
         "Every number can be traced to a clause. Works even with zero data."],
        ["**Layer 2 — Correction**",
         "A Gaussian Process model learns the residual (predicted minus measured)",
         "Captures local effects. Works with only a few hundred data points. "
         "Also reports how confident it is."],
        ["**Layer 3 — Decision**",
         "Converts the prediction plus its uncertainty into an engineering decision",
         "'Strip the formwork' is a decision. '38 MPa' is only a number."],
    ], [3.4, 6.4, 6.2], fs=9.5)

    figure(doc, "fig10_c1_method.png",
           "Figure 4 — The three-layer method, shown for Project C1. The same structure "
           "is used in C4 and C5.")

    doc.add_heading("3.3 The property that makes this defensible", 2)
    callout(doc, "Remember this for your viva",
            "If the correction layer predicts zero, the whole system reduces exactly to "
            "the standard codal calculation. This means the method can never be worse "
            "than current practice — it can only add information. That single property "
            "is what makes it acceptable to a practising engineer, and it is the "
            "strongest sentence in your thesis defence.")

    doc.add_heading("3.4 What a Gaussian Process is (briefly)", 2)
    P(doc, "A Gaussian Process is a prediction method with one unusual and very "
           "valuable feature: as well as giving an answer, it tells you how confident "
           "it is in that answer.")
    P(doc, "When you ask it about a mix similar to ones it has seen, it answers "
           "confidently — a narrow range. When you ask about something unfamiliar, it "
           "widens the range, effectively saying 'I do not know this territory; test it "
           "before you trust me'.")
    rich(doc, [("For engineering this is essential. ", True, False, None),
               ("An honest wide interval is far more useful than a confident wrong "
                "number, because it tells the engineer when to run a physical trial.",
                False, False, None)])

    doc.add_page_break()

    # ---------------- PART 4 : C1 ----------------
    doc.add_heading("PART 4 — PROJECT C1: EARLY-AGE STRENGTH PREDICTION", 1)

    doc.add_heading("4.1 The problem in one paragraph", 2)
    P(doc, "Concrete is accepted on its 28-day strength. But construction cannot wait "
           "28 days. Formwork must be struck, the next floor must be cast, the "
           "structure must be loaded. So a 7-day test is taken as an indication — but "
           "the relationship between 7-day and 28-day strength is not fixed. It depends "
           "on the binder, the temperature and the curing. A mix with 50% GGBS behaves "
           "completely differently from plain OPC.")

    figure(doc, "fig4_strength_gain.png",
           "Figure 5 — Three different binder systems can give almost the same 7-day "
           "result and then diverge substantially by 28 days and beyond. This is why a "
           "single conversion factor cannot work. Curves are representative shapes for "
           "explanation.")

    doc.add_heading("4.2 What the project will do", 2)
    P(doc, "Build a system that takes the 7-day strength, the mix proportions and the "
           "recorded temperature history, and predicts the 28-day strength with a "
           "stated confidence interval.")

    doc.add_heading("4.3 Step-by-step working method", 2)
    steps = [
        ("Obtain the data", "Download two public datasets: the UCI Concrete "
         "Compressive Strength dataset (1,030 records, 8 inputs) and the BOxCrete 2026 "
         "open dataset (533 measurements from 123 mixes at five curing ages: 1, 3, 5, "
         "14 and 28 days). Both are free. Work begins on day one, before any concrete "
         "is cast."),
        ("Reproduce a published baseline", "Before inventing anything, reproduce a "
         "result someone else has already published on the same dataset. If you cannot, "
         "something in your pipeline is wrong and you must find it now, not in month five."),
        ("Implement the maturity method", "Code the Nurse–Saul and Arrhenius maturity "
         "functions. These convert a temperature-versus-time record into a single "
         "'maturity' number, then relate maturity to strength. This is Layer 1."),
        ("Measure the residual", "For every record, compute: residual = measured "
         "strength − maturity-predicted strength. Plot the residuals. Look for pattern: "
         "are they larger for high fly-ash mixes? At low temperatures? This inspection "
         "is real engineering insight, and it belongs in the thesis."),
        ("Train the correction model", "Fit a Gaussian Process to predict the residual "
         "from the mix features. This is Layer 2. It is a few lines of scikit-learn."),
        ("Validate honestly", "Use leave-one-mix-out validation (explained in Part 9). "
         "Report the error and the width of the confidence intervals."),
        ("Run the laboratory programme", "Cast 40–60 mixes in the IIT Bhubaneswar "
         "concrete laboratory, varying water-cement ratio, SCM replacement and curing "
         "temperature. Test at 1, 3, 7, 14 and 28 days. Log temperature throughout."),
        ("Re-validate on your own data", "Test the model trained on public data against "
         "your own mixes. This answers the real question: does a model trained on "
         "foreign materials work on Indian materials? Whatever the answer, it is a "
         "publishable finding."),
        ("Build the decision layer", "Convert the prediction into a formwork-stripping "
         "recommendation at a stated confidence level. This is Layer 3, and it is what "
         "makes the work useful rather than merely interesting."),
        ("Write up", "Paper, thesis chapter, and a simple working tool."),
    ]
    for i, (title, body) in enumerate(steps, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.7); p.paragraph_format.space_after = Pt(5)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(f"Step {i} — {title}. "); r.bold = True
        p.add_run(body)

    doc.add_heading("4.4 Who does what", 2)
    table(doc, ["Member", "Responsibility"], [
        ["**B.Tech 1 & 2**", "Laboratory programme: mix design, casting, curing, "
         "testing at all ages, temperature logging, data recording in a fixed schema"],
        ["**B.Tech 3 & 4**", "Data pipeline, implementation of maturity functions, "
         "model training, benchmarking, the software tool"],
        ["**PhD 1**", "Methodological contribution: the hybrid maturity + Gaussian "
         "Process formulation. Lead author on the main paper."],
        ["**PhD 2**", "Uncertainty quantification and the decision framework: at what "
         "confidence level should formwork be struck?"],
    ], [3.0, 13.0], fs=9.5)

    doc.add_heading("4.5 Expected output", 2)
    B(doc, "A tool that takes 7-day data and returns, for example: "
           "\u201c38.2 ± 4.1 MPa at 90% confidence\u201d.")
    B(doc, "A quantified answer to whether models trained on international data "
           "transfer to Indian materials.")
    B(doc, "A formwork-stripping decision chart at chosen risk levels.")
    B(doc, "One journal paper and one conference paper.")

    doc.add_page_break()

    # ---------------- PART 5 : C4 ----------------
    doc.add_heading("PART 5 — PROJECT C4: SCM SUBSTITUTION OPTIMISER", 1)

    doc.add_heading("5.1 The problem", 2)
    P(doc, "SCM stands for Supplementary Cementitious Material — fly ash, GGBS "
           "(ground granulated blast-furnace slag), silica fume. Replacing part of the "
           "cement with these reduces cost and carbon dioxide emissions. Cement "
           "manufacture releases roughly 0.9 kg of CO₂ for every kilogram produced, so "
           "the environmental case is strong.")
    P(doc, "But replacement affects strength gain rate, workability, setting time and "
           "durability all at once, and in different directions. Engineers therefore "
           "use rules of thumb — 30% fly ash, 50% GGBS — which are rarely optimal for "
           "the particular materials available.")

    doc.add_heading("5.2 The finding that makes this project important", 2)
    P(doc, "It is widely claimed that low-carbon concrete is cheaper. We checked every "
           "credible published cost comparison. The results do not agree with each other.")

    figure(doc, "fig6_cost_spread.png",
           "Figure 6 — Published cost comparisons of geopolymer and SCM concrete "
           "against ordinary Portland cement concrete. The range is −40% to +200%. "
           "All values are as published in the cited studies.")

    callout(doc, "Why the studies disagree",
            "The binder (fly ash, slag) is nearly free — it is an industrial "
            "by-product. But the chemical activators and admixtures are expensive, and "
            "they must be transported. One study paid a 25% premium purely because the "
            "alkalis were sourced 300 km away. Cost is therefore dominated by local "
            "supply and freight — which means a single national answer does not exist.",
            fill="FBE6E4", tcol=RED)

    figure(doc, "fig7_cost_split.png",
           "Figure 7 — Cost composition. In OPC concrete, cement is about 51% of cost. "
           "In geopolymer concrete, the alkaline activators are about 54%. Source: "
           "Nature Scientific Reports 2025 and related studies.")

    doc.add_heading("5.3 Step-by-step working method", 2)
    steps4 = [
        ("Build the property dataset", "The UCI dataset already contains blast-furnace "
         "slag and fly ash as explicit variables. Supplement with published Indian data."),
        ("Encode chemistry, not names", "This is the key design decision. Do not record "
         "the input as 'fly ash'. Record it as its chemistry: SiO₂, Al₂O₃, CaO content "
         "and fineness. Then the model works for any new material, including ones that "
         "do not exist yet. This matters because India already uses about 96% of its "
         "fly ash — the surplus is disappearing, and the industry will be forced onto "
         "other materials."),
        ("Cast ternary blends", "Laboratory programme: OPC + fly ash + GGBS at three "
         "replacement levels and three water-binder ratios. Restrict the matrix "
         "deliberately — a full factorial will not fit in six months."),
        ("Build the prediction models", "Predict strength, workability and durability "
         "indicators from the chemistry vector."),
        ("Build the local cost and carbon database", "Telephone Odisha suppliers. Record "
         "the price and the transport distance for cement, fly ash, GGBS and admixtures. "
         "This small database is genuinely novel — nobody has assembled it."),
        ("Optimise", "Apply NSGA-II, a multi-objective optimisation algorithm, to find "
         "the set of mixes that cannot be improved in one objective without worsening "
         "another. This set is called the Pareto front."),
        ("Answer the real question", "Is low-carbon concrete actually cheaper in Odisha? "
         "Give a number, with the transport assumptions stated."),
    ]
    for i, (t_, b_) in enumerate(steps4, 1):
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.space_after = Pt(5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(f"Step {i} — {t_}. "); r.bold = True; p.add_run(b_)

    doc.add_heading("5.4 What a Pareto front means", 2)
    P(doc, "You cannot have maximum strength, minimum cost and minimum carbon all at "
           "once. The Pareto front is the set of best possible compromises: for each "
           "one, you cannot improve any objective without sacrificing another. The "
           "engineer then chooses from that set according to what the project needs.")

    doc.add_heading("5.5 Expected output", 2)
    B(doc, "A tool that returns optimal SCM combinations for a stated target.")
    B(doc, "The first regional cost and carbon database for concrete materials in Odisha.")
    B(doc, "A defensible answer to whether low-carbon concrete saves money locally.")

    doc.add_page_break()

    # ---------------- PART 6 : C5 ----------------
    doc.add_heading("PART 6 — PROJECT C5: WORKABILITY FROM VIDEO", 1)

    doc.add_heading("6.1 The problem", 2)
    P(doc, "The slump test (IS 1199) is the universal check on fresh concrete. It is "
           "cheap and quick, but it has three weaknesses: it is destructive of time, it "
           "depends on the operator, and it measures one instant only. Meanwhile slump "
           "changes continuously during transit, especially in hot weather.")

    figure(doc, "fig8_slump.png",
           "Figure 8 — Left: slump loss during transit at two ambient temperatures "
           "(representative curves). Right: typical contributions to slump variability. "
           "The ±20 mm figure for manual batching is as published; the others are "
           "indicative.")

    doc.add_heading("6.2 What the project will do", 2)
    P(doc, "Estimate slump — and, more ambitiously, the underlying rheological "
           "properties — from an ordinary smartphone video of the slump cone being "
           "lifted, or of concrete discharging from the mixer.")

    callout(doc, "Why this project is the safest of the three",
            "It generates 100% of its own data. Every slump test the laboratory already "
            "performs becomes one labelled training example: the video is the input, "
            "the measured slump is the answer. Two hundred samples is a few weeks of "
            "routine work. No external permission, no data request, no dependency on "
            "anyone.", fill="CDE6D8", tcol=GREEN)

    doc.add_heading("6.3 Step-by-step working method", 2)
    steps5 = [
        ("Fix the recording protocol", "Decide once: camera height, distance, angle, "
         "lighting, background. Write it down. Every video must follow it. Inconsistent "
         "recording is the single fastest way to ruin this project."),
        ("Collect while doing normal work", "Every time the laboratory performs a slump "
         "test for any purpose, record it. Note the measured slump, the mix, the time "
         "since batching and the temperature."),
        ("Extract the motion", "From the video, track how the concrete deforms: the "
         "rate of collapse, the final shape, whether it slumps evenly or shears. Simple "
         "computer-vision operations — background subtraction and edge detection — are "
         "sufficient. You do not need a large neural network."),
        ("Predict the slump", "Train a model to predict the measured slump from these "
         "extracted motion features. Because you use features rather than raw video, "
         "the model is small and trains on a laptop."),
        ("Go beyond slump", "This is the research contribution. The rate and shape of "
         "collapse are governed by the concrete's yield stress and plastic viscosity. "
         "Relate the observed kinematics to these rheological parameters. Slump is one "
         "number; rheology explains the behaviour."),
        ("Test robustness", "Vary lighting, angle and mix colour deliberately. Report "
         "where the method fails. An honest failure boundary is worth more than an "
         "inflated accuracy figure."),
    ]
    for i, (t_, b_) in enumerate(steps5, 1):
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.space_after = Pt(5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(f"Step {i} — {t_}. "); r.bold = True; p.add_run(b_)

    doc.add_heading("6.4 The shared-batch efficiency", 2)
    callout(doc, "How C1 and C5 run together at almost no extra cost",
            "The same batch of concrete that is cast into cubes for Project C1 is first "
            "subjected to a slump test for Project C5. One laboratory session, one set "
            "of materials, two datasets, two papers. This is why running C1 and C5 in "
            "parallel is recommended: the marginal cost of the second project is close "
            "to zero.")

    doc.add_page_break()

    # ---------------- PART 7 ----------------
    doc.add_heading("PART 7 — EXPECTED RESULTS AND OUTPUTS", 1)

    table(doc, ["Project", "Tangible output", "Academic output", "Success measure"], [
        ["**C1**", "Software tool predicting 28-day strength from 7-day data with "
         "confidence intervals; formwork-stripping decision chart",
         "1 journal + 1 conference paper",
         "Prediction error smaller than the maturity method alone, on mixes never seen "
         "during training"],
        ["**C4**", "SCM optimisation tool; Odisha materials cost and carbon database",
         "1 journal paper",
         "Identifies mixes with lower cost or carbon at equal strength, verified in the "
         "laboratory"],
        ["**C5**", "Smartphone-based slump estimation tool",
         "1 journal paper",
         "Slump estimated within the tolerance of the manual test itself"],
    ], [1.6, 5.6, 3.4, 5.4], fs=9)

    doc.add_heading("7.1 What a good result looks like", 2)
    P(doc, "Do not aim for a headline accuracy figure. Aim for these four things, "
           "which is what a reviewer and an examiner will actually look for:")
    N(doc, "The method beats the existing codal approach by a stated margin, on data it "
           "has never seen.", bold_prefix="Improvement over the baseline. ")
    N(doc, "The stated confidence intervals actually contain the true value about as "
           "often as they claim to. A 90% interval should be right about 90% of the "
           "time.", bold_prefix="Honest uncertainty. ")
    N(doc, "You can explain why the model failed where it failed.",
      bold_prefix="Explainable failures. ")
    N(doc, "The output changes a decision that a site engineer actually makes.",
      bold_prefix="Practical relevance. ")

    doc.add_page_break()

    # ---------------- PART 8 ----------------
    doc.add_heading("PART 8 — IMPACT ON THE CONSTRUCTION INDUSTRY", 1)

    doc.add_heading("8.1 The research gap being filled", 2)
    P(doc, "Hundreds of papers already predict concrete strength using machine "
           "learning. Very few do the things that would make the work usable on a "
           "real project.")

    figure(doc, "fig5_research_gap.png",
           "Figure 9 — What the concrete machine-learning literature does and does not "
           "do. Percentages are ULTRON's approximate assessment from a survey of the "
           "field and should be treated as indicative, not measured.")

    P(doc, "The gap is not accuracy. It is trustworthiness. That is where these "
           "projects sit.")

    doc.add_heading("8.2 Impact of Project C1", 2)
    table(doc, ["Who benefits", "How"], [
        ["**Site contractor**", "Formwork can be struck earlier when it is safe to do "
         "so, and held longer when it is not. Faster floor cycles on large projects."],
        ["**RMC producer**", "Early warning of a batch that will fail at 28 days, while "
         "corrective action is still possible."],
        ["**Client / consultant**", "Fewer disputes: strength expectations are stated "
         "with a confidence level rather than argued about."],
        ["**Regulator**", "A traceable, code-linked basis for early-age decisions."],
    ], [3.6, 12.4], fs=9.5)

    doc.add_heading("8.3 Impact of Project C4", 2)
    table(doc, ["Who benefits", "How"], [
        ["**Concrete producer**", "Lower binder cost at the same strength, with the "
         "saving quantified for the producer's own local supply situation."],
        ["**Environment**", "Cement is responsible for roughly 8% of global CO₂ "
         "emissions. Every kilogram replaced is a direct reduction."],
        ["**Industry as a whole**", "An honest local answer to whether low-carbon "
         "concrete is affordable — replacing marketing claims that range from −40% to "
         "+200%."],
        ["**Future-proofing**", "Because materials are encoded by chemistry rather than "
         "by name, the tool keeps working as fly ash becomes scarce and new "
         "supplementary materials appear."],
    ], [3.6, 12.4], fs=9.5)

    doc.add_heading("8.4 Impact of Project C5", 2)
    table(doc, ["Who benefits", "How"], [
        ["**Site engineer**", "Workability checked in seconds, on every load, with a "
         "phone — instead of occasionally, with a cone."],
        ["**RMC producer**", "Objective evidence of the condition of concrete at "
         "delivery, ending the routine dispute over whether the load was acceptable."],
        ["**Quality control**", "Continuous monitoring rather than spot checks. Slump "
         "loss during transit becomes visible and manageable."],
    ], [3.6, 12.4], fs=9.5)

    doc.add_heading("8.5 The combined effect", 2)
    callout(doc, "What these three projects add up to",
            "Concrete quality control in India today is retrospective: you discover the "
            "problem after the concrete has hardened, or after the structure has "
            "cracked. These three projects together make it predictive — strength known "
            "in advance, mix optimised before batching, workability checked "
            "continuously. Recall Figure 1: the fully automatic plant performed worst. "
            "The missing ingredient was never equipment. It was information, delivered "
            "in time to act on it.")

    doc.add_page_break()

    # ---------------- PART 9 ----------------
    doc.add_heading("PART 9 — COMMON MISTAKES TO AVOID", 1)

    P(doc, "Every one of these has ruined a real student project. Read this section "
           "before you start, not afterwards.")

    doc.add_heading("9.1 The validation mistake that invalidates published papers", 2)
    callout(doc, "Random splitting — do not do it",
            "The usual practice is to shuffle the data and hold back 20% for testing. "
            "For concrete this is WRONG. One mix produces results at 1, 3, 7, 14 and 28 "
            "days. If a random split puts the 7-day result in training and the 28-day "
            "result in testing, the model has already seen that mix. The reported "
            "accuracy is then fictional. Use LEAVE-ONE-MIX-OUT validation: hold out all "
            "records belonging to a mix. A large share of the published concrete "
            "machine-learning literature makes this error. Avoiding it, and saying so, "
            "is itself a contribution.", fill="FBE6E4", tcol=RED)

    doc.add_heading("9.2 The other seven", 2)
    table(doc, ["Mistake", "Consequence", "Prevention"], [
        ["Starting with data collection", "Three months gone before any modelling",
         "Both public datasets are downloaded in week one"],
        ["No baseline defined", "No way to know whether the model is any good",
         "Write down the target metric before writing any model code"],
        ["Changing the data schema mid-project", "Forty mixes recorded in an "
         "incompatible format", "Fix the recording spreadsheet before the first batch"],
        ["Reporting only R²", "A high R² can hide systematic bias",
         "Report error, bias, and interval coverage as well"],
        ["Chasing a complex model", "Overfitting on small data",
         "Start simple. Only add complexity if it measurably helps"],
        ["Ignoring units", "Silent, catastrophic errors",
         "One unit system, declared in the schema, checked on import"],
        ["Leaving the write-up to month six", "A rushed, weak paper",
         "Draft the methods section in month two, while it is fresh"],
    ], [4.4, 5.4, 6.2], fs=9)

    doc.add_page_break()

    # ---------------- PART 10 ----------------
    doc.add_heading("PART 10 — GLOSSARY", 1)
    table(doc, ["Term", "Plain meaning"], [
        ["**Abrams' law**", "The classical rule that concrete strength depends "
         "principally on the water-cement ratio"],
        ["**Baseline**", "The simple method your new method must beat to be worth anything"],
        ["**Coefficient of variation**", "Standard deviation divided by the mean; a "
         "measure of consistency that is independent of the size of the numbers"],
        ["**Confidence interval**", "A range within which the true value is expected to "
         "lie, with a stated probability"],
        ["**f_ck**", "Characteristic compressive strength — the grade of concrete "
         "specified, e.g. 30 MPa for M30"],
        ["**Feature**", "An input variable used to make a prediction"],
        ["**Gaussian Process**", "A prediction method that also reports how confident it is"],
        ["**GGBS**", "Ground granulated blast-furnace slag, a by-product of steel making "
         "used to replace cement"],
        ["**Maturity method**", "A technique that combines temperature and time into a "
         "single index to estimate strength development"],
        ["**NSGA-II**", "An algorithm for finding the best compromises among several "
         "competing objectives"],
        ["**Overfitting**", "When a model memorises the training data instead of "
         "learning the pattern, and then fails on anything new"],
        ["**Pareto front**", "The set of solutions where no objective can be improved "
         "without worsening another"],
        ["**Residual**", "The difference between what the equation predicted and what "
         "was actually measured"],
        ["**Rheology**", "The study of how a material flows; for fresh concrete, "
         "described by yield stress and plastic viscosity"],
        ["**SCM**", "Supplementary Cementitious Material: fly ash, GGBS, silica fume "
         "and similar cement replacements"],
        ["**Sigma (σ)**", "Standard deviation; how spread out the results are"],
        ["**Slump**", "The standard measure of the workability of fresh concrete, in mm"],
        ["**Target mean strength**", "The strength a producer must aim for, above the "
         "specified grade, to allow for variability"],
    ], [3.8, 12.2], fs=9.5)

    doc.add_paragraph()
    P(doc, "Prepared for the project team, Department of Civil Engineering, "
           "IIT Bhubaneswar.", align=WD_ALIGN_PARAGRAPH.CENTER, size=9,
      italic=True, color=GREY)

    # ---------------- FOOTER ----------------
    fp = s.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("Project Methodology Explained — C1, C4, C5   |   Page ")
    field(fp, "PAGE")
    fp.add_run(" of ")
    field(fp, "NUMPAGES")
    for run in fp.runs:
        run.font.size = Pt(8); run.font.color.rgb = GREY

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"[ULTRON] Written -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
