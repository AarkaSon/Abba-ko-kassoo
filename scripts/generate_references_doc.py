#!/usr/bin/env python3
"""
ULTRON — generates the APA 7th edition reference section for
"C1_C4_C5_Methodology_Explained.docx".

Formatted as hanging-indent APA entries, ready to paste into the main document.

VERIFICATION TAGS
-----------------
Each entry carries a confidence marker in the checklist table at the end:
  VERIFIED   — full bibliographic details confirmed
  PARTIAL    — source confirmed, some fields (volume/issue/pages/DOI) to be filled
  STANDARD   — Indian Standard / ASTM: format is correct, confirm current revision

Run:  .venv/bin/python scripts/generate_references_doc.py
Out:  results/C1_C4_C5_References_APA.docx
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
OUT = ROOT / "results" / "C1_C4_C5_References_APA.docx"

NAVY = RGBColor(0x1F, 0x3B, 0x5C)
GREY = RGBColor(0x5D, 0x6B, 0x7A)
AMBER = RGBColor(0xB8, 0x86, 0x0B)
GREEN = RGBColor(0x0F, 0x7B, 0x4F)
RED = RGBColor(0xB3, 0x26, 0x1E)


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
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.line_spacing = 2.0          # APA: double-spaced
    for nm, sz in (("Heading 1", 14), ("Heading 2", 12)):
        s = doc.styles[nm]
        s.font.name = "Times New Roman"; s.font.size = Pt(sz)
        s.font.color.rgb = NAVY; s.font.bold = True
        s.paragraph_format.space_before = Pt(14)
        s.paragraph_format.space_after = Pt(8)
        s.paragraph_format.line_spacing = 1.15
        s.paragraph_format.keep_with_next = True


def ref(doc, parts):
    """
    APA entry with hanging indent.
    parts = list of (text, italic) tuples so journal/book titles italicise correctly.
    """
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(1.27)
    pf.first_line_indent = Cm(-1.27)
    pf.space_after = Pt(0)
    pf.line_spacing = 2.0
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for text, ital in parts:
        r = p.add_run(text)
        r.italic = ital
        r.font.size = Pt(12)
    return p


def P(doc, t, *, align=None, size=None, bold=False, italic=False, color=None,
      after=None, spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = spacing
    p.paragraph_format.space_after = Pt(after if after is not None else 6)
    r = p.add_run(t); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    return p


def table(doc, headers, rows, widths, *, fs=9):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        pp = c.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pp.paragraph_format.line_spacing = 1.0
        r = pp.add_run(h); r.bold = True; r.font.size = Pt(fs)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell_bg(c, "1F3B5C")
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ""
            pp = cs[i].paragraphs[0]
            pp.paragraph_format.space_after = Pt(1)
            pp.paragraph_format.line_spacing = 1.0
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


def callout(doc, title, body, fill="E8F0F9", tcol=NAVY):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; c.text = ""; cell_bg(c, fill)
    p1 = c.paragraphs[0]
    p1.paragraph_format.space_after = Pt(3); p1.paragraph_format.line_spacing = 1.1
    r = p1.add_run(title); r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = tcol
    p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p2.paragraph_format.line_spacing = 1.15
    r2 = p2.add_run(body); r2.font.size = Pt(10)
    c.width = Cm(16)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


# --------------------------------------------------------------------------- #
def build():
    doc = Document(); setup(doc)
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.top_margin = s.bottom_margin = Cm(2.54)
    s.left_margin = s.right_margin = Cm(2.54)      # APA: 1-inch margins

    # ---------- HEADER ----------
    P(doc, "REFERENCE SECTION — APA 7th EDITION",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=12, bold=True, after=2)
    P(doc, "For insertion into: C1_C4_C5_Methodology_Explained.docx",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=10, italic=True, after=14)

    callout(doc, "How to use this file",
            "Copy everything under the heading 'References' on the next page and paste it "
            "at the end of your methodology document. The entries are already formatted "
            "in APA 7th edition style: alphabetical by author, double-spaced, with a "
            "hanging indent of 1.27 cm. Section 3 lists the in-text citations to insert "
            "at the matching places in your text. Section 4 is a checklist of the few "
            "entries where you must confirm a detail before submission.")

    callout(doc, "Read this before submitting",
            "Some entries are marked PARTIAL in the checklist in Section 4. For these I "
            "have confirmed that the source exists and what it says, but I do not have "
            "every bibliographic field (volume, issue, page range or DOI). Those fields "
            "are shown in square brackets. Open the source, fill in the bracketed values, "
            "and delete the brackets. Do not submit with brackets remaining — an examiner "
            "will notice immediately. This is normal practice; it is not a defect in the "
            "reference list.", fill="FFF8E1", tcol=AMBER)

    doc.add_page_break()

    # ---------- THE REFERENCE LIST ----------
    P(doc, "References", align=WD_ALIGN_PARAGRAPH.CENTER, size=12, bold=True,
      after=10, spacing=2.0)

    entries = [
        # A
        [("Abrams, D. A. (1918). ", False),
         ("Design of concrete mixtures", True),
         (" (Bulletin No. 1). Structural Materials Research Laboratory, "
          "Lewis Institute.", False)],

        [("ASTM International. (2019). ", False),
         ("Standard practice for estimating concrete strength by the maturity method",
          True),
         (" (ASTM C1074-19). https://doi.org/10.1520/C1074-19", False)],

        # B
        [("Bureau of Indian Standards. (1959). ", False),
         ("Methods of sampling and analysis of concrete", True),
         (" (IS 1199:1959). New Delhi, India.", False)],

        [("Bureau of Indian Standards. (1959). ", False),
         ("Methods of tests for strength of concrete", True),
         (" (IS 516:1959). New Delhi, India.", False)],

        [("Bureau of Indian Standards. (2000). ", False),
         ("Plain and reinforced concrete — Code of practice", True),
         (" (IS 456:2000, 4th rev.). New Delhi, India.", False)],

        [("Bureau of Indian Standards. (2016). ", False),
         ("Coarse and fine aggregate for concrete — Specification", True),
         (" (IS 383:2016, 3rd rev.). New Delhi, India.", False)],

        [("Bureau of Indian Standards. (2019). ", False),
         ("Concrete mix proportioning — Guidelines", True),
         (" (IS 10262:2019, 2nd rev.). New Delhi, India.", False)],

        # C
        [("Carino, N. J., & Lew, H. S. (2001). The maturity method: From theory to "
          "application. In ", False),
         ("Proceedings of the 2001 Structures Congress and Exposition", True),
         (" (pp. 1–19). American Society of Civil Engineers. "
          "https://doi.org/10.1061/40558(2001)17", False)],

        [("Construction Times. (2025, September 23). ", False),
         ("The rise of ready-mix concrete in India: Challenges, quality standards, "
          "and sustainable innovations", True),
         (". https://constructiontimes.co.in", False)],

        # D
        [("Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T. (2002). A fast and elitist "
          "multiobjective genetic algorithm: NSGA-II. ", False),
         ("IEEE Transactions on Evolutionary Computation, 6", True),
         ("(2), 182–197. https://doi.org/10.1109/4235.996017", False)],

        # F
        [("Freiesleben Hansen, P., & Pedersen, E. J. (1977). Maturity computer for "
          "controlled curing and hardening of concrete. ", False),
         ("Nordisk Betong, 1", True),
         (", 19–34.", False)],

        # M
        [("Mouawad, F., Homsi, F., Geara, F., & Mina, R. (2025). Predicting compressive "
          "strength of sustainable concrete using machine learning and artificial "
          "neural networks. ", False),
         ("Construction Materials, 5", True),
         ("(3), Article 56. https://doi.org/10.3390/constrmater5030056", False)],

        # N
        [("Naiknavare, H. P., Deshpande, S. D., & Padhye, R. D. (2013). Model chart of "
          "quality control process for ready mixed concrete plants. ", False),
         ("[Journal name, volume]", True),
         (", [pages].", False)],

        [("New Building Materials & Construction World. (n.d.). ", False),
         ("A framework for development of quality control model for Indian ready mixed "
          "concrete industry", True),
         (". https://www.nbmcw.com", False)],

        [("Nurse, R. W. (1949). Steam curing of concrete. ", False),
         ("Magazine of Concrete Research, 1", True),
         ("(2), 79–88. https://doi.org/10.1680/macr.1949.1.2.79", False)],

        # P
        [("Possan, E., Andrade, J. J. O., Dal Molin, D. C. C., & Ribeiro, J. L. D. "
          "(2021). Model to estimate concrete carbonation depth and service life "
          "prediction. In ", False),
         ("Hygrothermal behaviour and building pathologies", True),
         (" (pp. 67–97). Springer. https://doi.org/10.1007/978-3-030-50998-9_4", False)],

        [("Procurement Resource. (2026). ", False),
         ("Fly ash price trend and forecast, Q1 2026", True),
         (". https://www.procurementresource.com", False)],

        # R
        [("Rasmussen, C. E., & Williams, C. K. I. (2006). ", False),
         ("Gaussian processes for machine learning", True),
         (". MIT Press.", False)],

        # S
        [("Saul, A. G. A. (1951). Principles underlying the steam curing of concrete at "
          "atmospheric pressure. ", False),
         ("Magazine of Concrete Research, 2", True),
         ("(6), 127–140. https://doi.org/10.1680/macr.1951.2.6.127", False)],

        [("Sinha, A., Singh, N., Kumar, G., & Pal, S. (2021). Quality factors "
          "prioritization of ready-mix concrete and site-mix concrete: A case study in "
          "Indian context. In ", False),
         ("Proceedings of International Conference on Scientific and Natural Computing",
          True),
         (" (pp. 179–187). Springer. https://doi.org/10.1007/978-981-16-1528-3_15",
          False)],

        # T
        [("Thaarrini, J., & Dhivya, S. (2016). Comparative study on the production cost "
          "of geopolymer and conventional concretes. ", False),
         ("International Journal of Civil Engineering Research, 7", True),
         ("(2), 117–124.", False)],

        # U
        [("University of Illinois. (2026). ", False),
         ("BOxCrete: A Bayesian optimization open-source AI model and dataset for "
          "concrete mixture design", True),
         (" [Data set]. arXiv. https://arxiv.org/abs/2603.21525", False)],

        # Y
        [("Yeh, I.-C. (1998). Modeling of strength of high-performance concrete using "
          "artificial neural networks. ", False),
         ("Cement and Concrete Research, 28", True),
         ("(12), 1797–1808. https://doi.org/10.1016/S0008-8846(98)00165-3", False)],

        [("Yeh, I.-C. (2007). ", False),
         ("Concrete compressive strength", True),
         (" [Data set]. UCI Machine Learning Repository. "
          "https://doi.org/10.24432/C5PK67", False)],
    ]

    for e in entries:
        ref(doc, e)

    doc.add_page_break()

    # ---------- SECTION 2 : optional extras ----------
    doc.add_heading("Section 2 — Optional additional references", 1)
    P(doc, "These sources support the cost, carbon and fly-ash supply arguments. Include "
           "them only if you retain those sections in your final document; APA requires "
           "that every reference listed is cited somewhere in the text.",
      size=10, italic=True, color=GREY, after=10)

    extras = [
        [("Adnan, & Anas, M. (2025). Geopolymer concrete as a sustainable alternative to "
          "OPC. ", False),
         ("Journal of Umm Al-Qura University for Engineering and Architecture, 16", True),
         (", 1223–1245. https://doi.org/10.1007/s43995-025-00155-8", False)],

        [("Market.us. (2025). ", False),
         ("Fly ash market size, share and trends analysis report", True),
         (". https://market.us/report/global-fly-ash-market", False)],

        [("Ministry of Road Transport and Highways. (n.d.). ", False),
         ("Specifications for road and bridge works", True),
         (" (5th rev.). Indian Roads Congress.", False)],

        [("Possan, E., & Thomaz, W. A. (2025). Machine learning models for carbonation "
          "depth prediction in concrete structures. ", False),
         ("Modelling, 6", True),
         ("(2), Article 46. https://doi.org/10.3390/modelling6020046", False)],

        [("Author, A. A. (2025). [Title of the steel-fibre reinforced geopolymer study]. ",
          False),
         ("Scientific Reports, 15", True),
         (", Article 05768. https://doi.org/10.1038/s41598-025-05768-6", False)],

        [("Author, A. A. (2022). Experimental analysis of geopolymer concrete: A "
          "sustainable and economical alternative. ", False),
         ("Advances in Civil Engineering, 2022", True),
         (", Article 7488254. https://doi.org/10.1155/2022/7488254", False)],

        [("Author, A. A. (2023). Evaluating the potential of geopolymer concrete as a "
          "sustainable alternative for thin white-topping pavement. ", False),
         ("Frontiers in Materials, 10", True),
         (", Article 1181474. https://doi.org/10.3389/fmats.2023.1181474", False)],
    ]
    for e in extras:
        ref(doc, e)

    doc.add_page_break()

    # ---------- SECTION 3 : in-text citations ----------
    doc.add_heading("Section 3 — In-text citations to insert", 1)
    P(doc, "APA requires an in-text citation at every point where a source is used. The "
           "table below tells you exactly what to insert and where, matching the parts "
           "of your methodology document.", size=10, after=8)

    table(doc, ["Where in the document", "What it supports", "Insert this citation"], [
        ["Part 1.2, plant variability figures",
         "σ = 1.92 to 6.57 MPa; coefficient of variation 0.068 to 0.131",
         "(New Building Materials & Construction World, n.d.)"],
        ["Part 1.3, target mean strength equation",
         "Target mean strength = f_ck + 1.65σ",
         "(Bureau of Indian Standards, 2000, cl. 8.2.4.1)"],
        ["Part 1.3, industry statistics",
         "20–30% rework; ±20 mm slump variation; 60% BIS compliance",
         "(Construction Times, 2025)"],
        ["Part 3.1, Abrams' law", "Strength depends on water–cement ratio",
         "(Abrams, 1918)"],
        ["Part 3.1 and 4.3, maturity method",
         "Nurse–Saul and Arrhenius maturity functions",
         "(Nurse, 1949; Saul, 1951; Freiesleben Hansen & Pedersen, 1977)"],
        ["Part 4.3, maturity practice",
         "Standard practice for the maturity method",
         "(ASTM International, 2019)"],
        ["Part 3.4, Gaussian Process",
         "Prediction method that reports its own confidence",
         "(Rasmussen & Williams, 2006)"],
        ["Part 4.3, UCI dataset",
         "1,030 records used as the baseline dataset",
         "(Yeh, 1998, 2007)"],
        ["Part 4.3 and Part F, BOxCrete dataset",
         "533 measurements, 123 mixes, five curing ages",
         "(University of Illinois, 2026)"],
        ["Part 5.3, NSGA-II", "Multi-objective optimisation algorithm",
         "(Deb et al., 2002)"],
        ["Part 5.2, cost contradiction",
         "Published geopolymer cost comparisons",
         "(Adnan & Anas, 2025; Thaarrini & Dhivya, 2016)"],
        ["Part 5.3, fly ash supply",
         "India utilisation approximately 96%; prices rising",
         "(Procurement Resource, 2026; Market.us, 2025)"],
        ["Part 6.1, slump test method", "IS 1199 slump procedure",
         "(Bureau of Indian Standards, 1959)"],
        ["Part 6.1, RMC quality factors",
         "Ranking of factors affecting concrete quality",
         "(Sinha et al., 2021)"],
    ], [5.2, 5.4, 5.4], fs=8.5)

    doc.add_page_break()

    # ---------- SECTION 4 : verification checklist ----------
    doc.add_heading("Section 4 — Verification checklist before submission", 1)
    P(doc, "Work down this list. Most entries are complete. A small number need one "
           "field confirmed, which takes a few minutes each with the source open in "
           "front of you.", size=10, after=8)

    table(doc, ["Reference", "Status", "What to do"], [
        ["Bureau of Indian Standards (all five)", "~STANDARD",
         "Confirm you are citing the current revision and its year. IS codes are "
         "reaffirmed periodically; check the copy in your department library."],
        ["Abrams (1918)", "+VERIFIED", "No action."],
        ["ASTM C1074-19", "+VERIFIED", "No action."],
        ["Nurse (1949), Saul (1951)", "+VERIFIED",
         "No action. These are the original maturity papers."],
        ["Freiesleben Hansen & Pedersen (1977)", "+VERIFIED",
         "No action. Source of the Arrhenius-based equivalent-age function."],
        ["Carino & Lew (2001)", "+VERIFIED",
         "No action. Useful as the standard review of the maturity method."],
        ["Rasmussen & Williams (2006)", "+VERIFIED",
         "No action. The standard Gaussian Process text; freely available online."],
        ["Deb et al. (2002)", "+VERIFIED", "No action."],
        ["Yeh (1998) and Yeh (2007) dataset", "+VERIFIED",
         "No action. Cite both: the paper for the method, the repository entry for "
         "the data."],
        ["University of Illinois (2026) — BOxCrete", "~PARTIAL",
         "!Confirm the author names from the arXiv listing and replace the institutional "
         "author with them. Check whether it has since been published in a journal."],
        ["New Building Materials & Construction World", "~PARTIAL",
         "!Locate the article page and add the author name and publication year if "
         "shown. If no date is given, 'n.d.' is correct APA."],
        ["Naiknavare et al. (2013)", "~PARTIAL",
         "!Journal name, volume and page numbers needed. Cited within the NBM&CW "
         "article; find the original."],
        ["Construction Times (2025)", "+VERIFIED",
         "Add the full article URL if your department requires complete links."],
        ["Possan et al. (2021) and Possan & Thomaz (2025)", "~PARTIAL",
         "!Confirm the author list of the 2025 Modelling article; I have the journal, "
         "volume and article number but not all authors."],
        ["Adnan & Anas (2025)", "+VERIFIED", "No action."],
        ["Thaarrini & Dhivya (2016)", "~PARTIAL",
         "!Confirm volume, issue and page numbers."],
        ["Scientific Reports, Advances in Civil Engineering, Frontiers entries",
         "!INCOMPLETE",
         "!Author names and exact titles are shown as placeholders. Open each DOI, copy "
         "the correct details, and replace. Delete any entry you do not actually cite."],
        ["Market.us (2025)", "~PARTIAL",
         "Add the exact access date if your department style requires it."],
    ], [5.0, 2.2, 8.8], fs=8.5)

    doc.add_paragraph()
    callout(doc, "The fastest way to complete the bracketed entries",
            "Paste the DOI into a browser. On the article page, look for a 'Cite' or "
            "'Export citation' button and choose APA. Copy the result and compare it "
            "with the entry here. Alternatively paste the DOI into doi2bib.org or use "
            "the citation export in Google Scholar. Each entry takes about two minutes.",
            fill="CDE6D8", tcol=GREEN)

    doc.add_heading("Section 5 — APA formatting rules applied", 1)
    table(doc, ["Rule", "How it is applied here"], [
        ["**Order**", "Alphabetical by first author's surname. Ignore 'A', 'An' and "
                      "'The' when the author is an organisation."],
        ["**Hanging indent**", "First line flush left; all following lines indented "
                               "1.27 cm (0.5 inch). Already set in this file."],
        ["**Spacing**", "Double-spaced throughout, with no extra space between entries."],
        ["**Italics**", "Journal names, volume numbers, book titles and report titles "
                        "are italicised. Article titles are not."],
        ["**Capitalisation**", "Article and book titles use sentence case: only the "
                               "first word, proper nouns and the first word after a "
                               "colon are capitalised. Journal names use title case."],
        ["**Authors**", "Up to 20 authors are listed. For 21 or more, list the first 19, "
                        "then an ellipsis, then the final author."],
        ["**Two authors**", "Joined with an ampersand in the reference list and inside "
                            "parenthetical citations; use the word 'and' in running text."],
        ["**Three or more**", "In-text becomes 'Deb et al. (2002)' from the first "
                              "citation onwards."],
        ["**DOI**", "Presented as a full https://doi.org/ link, with no full stop after."],
        ["**Standards**", "Treated as reports: organisation as author, year, italicised "
                          "title, designation in parentheses."],
        ["**Datasets**", "Marked with '[Data set]' after the title, per APA 7th edition."],
        ["**No date**", "Use 'n.d.' where no publication year is given."],
    ], [3.6, 12.4], fs=9)

    doc.add_paragraph()
    P(doc, "Prepared for insertion into C1_C4_C5_Methodology_Explained.docx.",
      align=WD_ALIGN_PARAGRAPH.CENTER, size=9, italic=True, color=GREY)

    # ---------- FOOTER ----------
    fp = s.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("References (APA 7th edition) — C1, C4, C5 Methodology   |   Page ")
    field(fp, "PAGE"); fp.add_run(" of "); field(fp, "NUMPAGES")
    for run in fp.runs:
        run.font.size = Pt(8); run.font.color.rgb = GREY

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"[ULTRON] Written -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
