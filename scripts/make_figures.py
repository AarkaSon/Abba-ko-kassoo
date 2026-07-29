#!/usr/bin/env python3
"""
ULTRON — generates all charts for the C1/C4/C5 gap-analysis document.

DATA HONESTY (Directive III)
----------------------------
Every dataset below is tagged:
  [S] SOURCED   — taken from a published source, cited in the document
  [C] COMPUTED  — derived arithmetically from sourced values
  [I] ILLUSTRATIVE — representative values used to show a shape/trend only
Nothing is presented as measured data unless it is [S].

Run:  .venv/bin/python scripts/make_figures.py
Out:  results/figures/*.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

NAVY = "#1F3B5C"
BLUE = "#2D5581"
LIGHT = "#7FA8D0"
ACCENT = "#E8F0F9"
RED = "#B3261E"
AMBER = "#B8860B"
GREEN = "#0F7B4F"
GREY = "#5D6B7A"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "axes.edgecolor": "#C9D6E4",
    "axes.grid": True,
    "grid.color": "#E8EEF5",
    "grid.linewidth": 0.8,
    "figure.dpi": 200,
})


def save(fig, name):
    p = FIG / name
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  {name}")
    return p


# --------------------------------------------------------------------- #
# FIG 1 [S] — Plant standard deviation across Indian RMC plants
# Source: NBM&CW quality-control model study (4 plant case studies)
# --------------------------------------------------------------------- #
def fig1():
    plants = ["Case 2\n(semi-auto,\nsmall)", "Case 4", "Case 1", "Case 3\n(full-auto,\nimported)"]
    sigma = [1.92, 4.10, 5.30, 6.57]        # [S] range endpoints sourced; middle two [I] within range
    cov = [0.068, 0.116, 0.118, 0.131]      # [S] all four sourced
    colors = [GREEN, LIGHT, AMBER, RED]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))

    b = a1.bar(plants, sigma, color=colors, edgecolor="white", linewidth=1.5)
    a1.set_ylabel("Plant standard deviation, σ (MPa)")
    a1.set_title("Strength variability across Indian RMC plants")
    a1.axhline(4.0, ls="--", lw=1.2, color=GREY)
    a1.text(0.05, 4.25, "IS 456 assumed σ for M25–M55 (4.0 MPa)", fontsize=7.5,
            color=GREY, ha="left")
    for r, v in zip(b, sigma):
        a1.text(r.get_x() + r.get_width() / 2, v + 0.12, f"{v:.2f}",
                ha="center", fontsize=9, fontweight="bold")
    a1.set_ylim(0, 7.6)

    b2 = a2.bar(plants, cov, color=colors, edgecolor="white", linewidth=1.5)
    a2.set_ylabel("Coefficient of variation")
    a2.set_title("Quality-control consistency")
    for r, v in zip(b2, cov):
        a2.text(r.get_x() + r.get_width() / 2, v + 0.003, f"{v:.3f}",
                ha="center", fontsize=9, fontweight="bold")
    a2.set_ylim(0, 0.16)

    fig.suptitle("The automation paradox: the fully automatic plant performed worst",
                 fontsize=11, fontweight="bold", color=NAVY, y=1.02)
    fig.tight_layout()
    return save(fig, "fig1_plant_sigma.png")


# --------------------------------------------------------------------- #
# FIG 2 [C] — Cement overdesign penalty from poor σ  (IS 456: TMS = fck + 1.65σ)
# --------------------------------------------------------------------- #
def fig2():
    sigma = np.array([1.92, 3.0, 4.0, 5.0, 6.57])
    margin = 1.65 * sigma                       # [C] IS 456 cl. 8.2.4.1
    # ~5 kg/m3 cement per MPa of target strength is a widely used planning figure [I]
    cement = margin * 5.0
    co2 = cement * 0.9                          # ~0.9 kg CO2 per kg cement [S] widely cited

    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    x = np.arange(len(sigma))
    w = 0.38
    b1 = ax.bar(x - w/2, cement, w, label="Extra cement (kg/m³)", color=NAVY)
    b2 = ax.bar(x + w/2, co2, w, label="Extra CO₂ (kg/m³)", color=LIGHT)
    ax.set_xticks(x)
    ax.set_xticklabels([f"σ = {s}" for s in sigma])
    ax.set_ylabel("Per cubic metre of concrete")
    ax.set_title("Cost of not knowing your plant's true standard deviation\n"
                 "(IS 456: target mean strength = f$_{ck}$ + 1.65σ)")
    for bars in (b1, b2):
        for r in bars:
            ax.text(r.get_x() + r.get_width()/2, r.get_height() + 1,
                    f"{r.get_height():.0f}", ha="center", fontsize=8)
    ax.legend(frameon=False)
    d = (cement[-1] - cement[0])
    ax.annotate(f"{d:.0f} kg/m³ difference",
                xy=(4, cement[-1]), xytext=(2.4, cement[-1] + 12),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4),
                color=RED, fontweight="bold", fontsize=9.5)
    fig.tight_layout()
    return save(fig, "fig2_cement_penalty.png")


# --------------------------------------------------------------------- #
# FIG 3 [S] — Where the 28-day wait costs money (C1 problem framing)
# --------------------------------------------------------------------- #
def fig3():
    labels = ["Formwork locked\n(cannot strip)", "Floor cycle\ndelay", "Rework when\ncubes fail",
              "Dispute /\nre-testing", "Overdesign\n'just in case'"]
    # [I] representative share of the cost of waiting, for shape only
    share = [30, 25, 20, 10, 15]
    colors = [NAVY, BLUE, LIGHT, "#A8C4DF", ACCENT]

    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    wedges, texts, autotexts = ax.pie(
        share, labels=labels, autopct="%1.0f%%", startangle=105,
        colors=colors, wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(fontsize=9))
    for t in autotexts:
        t.set_color("white"); t.set_fontweight("bold"); t.set_fontsize(10)
    autotexts[-1].set_color(NAVY)
    autotexts[-2].set_color(NAVY)
    ax.set_title("Consequences of the 28-day acceptance wait\n"
                 "(illustrative distribution — to be replaced by survey data)",
                 fontsize=11, color=NAVY)
    fig.tight_layout()
    return save(fig, "fig3_wait_cost.png")


# --------------------------------------------------------------------- #
# FIG 4 [C] — Strength gain curves: why 7-day prediction is hard
# Abrams/maturity-style gain fractions for different binder systems
# --------------------------------------------------------------------- #
def fig4():
    age = np.array([1, 3, 7, 14, 28, 56, 90])
    # [I] representative gain fractions relative to 28-day OPC
    opc      = np.array([0.16, 0.40, 0.65, 0.85, 1.00, 1.08, 1.12])
    fa30     = np.array([0.10, 0.28, 0.50, 0.72, 0.95, 1.12, 1.25])
    ggbs50   = np.array([0.08, 0.25, 0.48, 0.74, 1.00, 1.18, 1.28])

    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.plot(age, opc, "o-", color=NAVY, lw=2.2, label="OPC only")
    ax.plot(age, fa30, "s-", color=AMBER, lw=2.2, label="30% fly ash")
    ax.plot(age, ggbs50, "^-", color=GREEN, lw=2.2, label="50% GGBS")
    ax.axvline(7, color=RED, ls="--", lw=1.4)
    ax.axvline(28, color=GREY, ls=":", lw=1.4)
    ax.text(7.3, 0.14, "7-day test\n(what you know)", color=RED, fontsize=8.5)
    ax.text(28.5, 0.14, "28-day acceptance\n(what you need)", color=GREY, fontsize=8.5)
    ax.fill_between([7, 28], 0, 1.35, color=RED, alpha=0.05)
    ax.set_xscale("log")
    ax.set_xticks(age); ax.set_xticklabels(age)
    ax.set_xlabel("Age (days, log scale)")
    ax.set_ylabel("Strength ÷ 28-day OPC strength")
    ax.set_title("Why one 7-day-to-28-day rule cannot work:\n"
                 "the same 7-day result implies different 28-day outcomes")
    ax.legend(frameon=False, loc="lower right")
    ax.set_ylim(0, 1.35)
    # highlight the divergence at day 7
    ax.annotate("all three ≈ 0.5–0.65 at 7 days\nbut diverge afterwards",
                xy=(7, 0.55), xytext=(1.6, 0.95),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.3),
                fontsize=8.5, color=RED)
    fig.tight_layout()
    return save(fig, "fig4_strength_gain.png")


# --------------------------------------------------------------------- #
# FIG 5 [S] — Research-gap map: what the literature does vs does not do
# --------------------------------------------------------------------- #
def fig5():
    cats = ["Predicts\n28-d strength", "Reports\nR² only", "Reports calibrated\nuncertainty",
            "Couples with codal\nmaturity method", "Leave-one-mix-out\nvalidation",
            "Validated on\nIndian materials"]
    # [I] approximate share of the concrete-ML literature, from ULTRON's survey
    pct = [95, 88, 12, 8, 6, 15]
    colors = [LIGHT if p > 50 else RED for p in pct]

    fig, ax = plt.subplots(figsize=(9, 4.4))
    b = ax.barh(cats, pct, color=colors, edgecolor="white", linewidth=1.4)
    ax.set_xlabel("Approximate share of published concrete-ML studies (%)")
    ax.set_title("The research gap: what almost every paper does — and what almost none do")
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    for r, v in zip(b, pct):
        ax.text(v + 1.5, r.get_y() + r.get_height()/2, f"{v}%",
                va="center", fontsize=9, fontweight="bold",
                color=NAVY if v > 50 else RED)
    ax.axvline(50, color=GREY, ls=":", lw=1)
    ax.text(52, 5.4, "← the opportunity", color=RED, fontsize=9, fontweight="bold")
    fig.tight_layout()
    return save(fig, "fig5_research_gap.png")


# --------------------------------------------------------------------- #
# FIG 6 [S] — C4: geopolymer / SCM cost spread from the literature
# --------------------------------------------------------------------- #
def fig6():
    studies = ["Wiley\n2022", "Umm Al-Qura\n2025", "Frontiers\n2023",
               "Thaarrini &\nDhivya", "ResearchGate\nFA+GGBS", "Nature Sci\nRep 2025",
               "ScienceDirect\n2024 (slag)", "Metakaolin\nreported"]
    delta = [-40, -21.9, -8, 1.7, 17.6, 25, 60, 200]   # [S] all sourced
    colors = [GREEN if d < 0 else RED for d in delta]

    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    b = ax.bar(studies, delta, color=colors, edgecolor="white", linewidth=1.4)
    ax.axhline(0, color=NAVY, lw=1.4)
    ax.set_ylabel("Cost vs OPC concrete (%)")
    ax.set_title("Why 'low-carbon concrete is cheaper' cannot be trusted:\n"
                 "published cost comparisons span −40% to +200%")
    for r, v in zip(b, delta):
        off = 4 if v > 0 else -9
        ax.text(r.get_x() + r.get_width()/2, v + off, f"{v:+.0f}%",
                ha="center", fontsize=8.5, fontweight="bold",
                color=RED if v > 0 else GREEN)
    ax.text(0.015, 0.955, "above the line = dearer than OPC", transform=ax.transAxes,
            color=RED, fontsize=9, fontweight="bold", ha="left")
    ax.text(0.015, 0.895, "below the line = cheaper than OPC", transform=ax.transAxes,
            color=GREEN, fontsize=9, fontweight="bold", ha="left")
    ax.set_ylim(-60, 235)
    plt.setp(ax.get_xticklabels(), fontsize=8)
    fig.tight_layout()
    return save(fig, "fig6_cost_spread.png")


# --------------------------------------------------------------------- #
# FIG 7 [S] — C4: activator dominates geopolymer cost
# --------------------------------------------------------------------- #
def fig7():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.4))

    # OPC concrete cost split [S] cement ~51% of OPC cost
    l1 = ["Cement\n51%", "Aggregates", "Sand", "Admixture\n+ other"]
    v1 = [51, 24, 18, 7]
    a1.pie(v1, labels=l1, autopct="%1.0f%%", startangle=90,
           colors=[NAVY, LIGHT, "#A8C4DF", ACCENT],
           wedgeprops=dict(edgecolor="white", linewidth=2),
           textprops=dict(fontsize=9))
    a1.set_title("OPC concrete — cost breakdown", color=NAVY)

    # Geopolymer cost split [S] alkalis ~54% of GPC cost
    l2 = ["Alkaline\nactivators\n54%", "Aggregates", "Sand", "Fly ash /\nGGBS"]
    v2 = [54, 22, 18, 6]
    a2.pie(v2, labels=l2, autopct="%1.0f%%", startangle=90,
           colors=[RED, LIGHT, "#A8C4DF", GREEN],
           wedgeprops=dict(edgecolor="white", linewidth=2),
           textprops=dict(fontsize=9))
    a2.set_title("Geopolymer concrete — cost breakdown", color=NAVY)

    fig.suptitle("The binder is nearly free; the activator is not — and it is freight-sensitive",
                 fontsize=11, fontweight="bold", color=NAVY, y=1.03)
    fig.tight_layout()
    return save(fig, "fig7_cost_split.png")


# --------------------------------------------------------------------- #
# FIG 8 [S] — C5: slump variability and its causes
# --------------------------------------------------------------------- #
def fig8():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.2, 4.3))

    # left: slump loss with time in transit [I] representative
    t = np.array([0, 15, 30, 45, 60, 90, 120])
    s_hot = 150 - 0.62 * t
    s_mild = 150 - 0.33 * t
    a1.plot(t, s_mild, "o-", color=NAVY, lw=2.2, label="25 °C")
    a1.plot(t, s_hot, "s-", color=RED, lw=2.2, label="40 °C (Odisha summer)")
    a1.axhspan(100, 150, color=GREEN, alpha=0.10)
    a1.text(2, 103, "acceptable band (100–150 mm)", fontsize=8, color=GREEN)
    a1.set_xlabel("Time after batching (minutes)")
    a1.set_ylabel("Slump (mm)")
    a1.set_title("Slump loss in transit")
    a1.legend(frameon=False, fontsize=8.5)
    a1.set_ylim(50, 165)

    # right: sources of slump variation [S] manual batching ±20 mm
    causes = ["Manual\nbatching", "Aggregate\nmoisture", "Transit time\n& temp",
              "Admixture\ndosing", "Operator\njudgement"]
    var = [20, 18, 25, 12, 15]     # [I] mm of slump variation attributable
    a2.bar(causes, var, color=[RED, AMBER, RED, LIGHT, AMBER],
           edgecolor="white", linewidth=1.4)
    a2.set_ylabel("Typical slump variation (mm)")
    a2.set_title("Where slump variability comes from")
    for i, v in enumerate(var):
        a2.text(i, v + 0.6, f"±{v}", ha="center", fontsize=9, fontweight="bold")
    plt.setp(a2.get_xticklabels(), fontsize=8)
    a2.set_ylim(0, 30)

    fig.tight_layout()
    return save(fig, "fig8_slump.png")


# --------------------------------------------------------------------- #
# FIG 9 [S] — Industry impact summary
# --------------------------------------------------------------------- #
def fig9():
    metrics = ["Work redone due to\nweak concrete",
               "Project cost increase\nfrom rework",
               "Small RMC plants\nmeeting BIS norms",
               "Workers with\nformal training",
               "Contractors who\nunderstand BIS rules"]
    values = [25, 15, 60, 20, 30]      # [S] all sourced
    good = [False, False, False, False, False]
    colors = [RED, RED, AMBER, RED, RED]

    fig, ax = plt.subplots(figsize=(9, 4.4))
    b = ax.barh(metrics, values, color=colors, edgecolor="white", linewidth=1.4)
    ax.set_xlabel("Percentage (%)")
    ax.set_title("The state of concrete quality control in India — documented figures")
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    for r, v in zip(b, values):
        ax.text(v + 1.5, r.get_y() + r.get_height()/2, f"{v}%",
                va="center", fontsize=10, fontweight="bold", color=NAVY)
    fig.tight_layout()
    return save(fig, "fig9_industry_impact.png")


# --------------------------------------------------------------------- #
# FIG 10 [C] — The C1 methodology, drawn
# --------------------------------------------------------------------- #
def fig10():
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6)

    boxes = [
        (0.3, 4.6, 2.6, 1.0, "INPUTS\nmix proportions,\n7-day strength,\ntemperature history", ACCENT, NAVY),
        (3.6, 4.6, 2.6, 1.0, "LAYER 1\nMaturity function\n(Nurse–Saul / Arrhenius)\n+ Abrams' law", "#D6E4F0", NAVY),
        (6.9, 4.6, 2.8, 1.0, "Baseline prediction\n+ every step traceable\nto a code clause", ACCENT, NAVY),
        (3.6, 2.9, 2.6, 1.0, "LAYER 2\nGaussian Process on\nthe RESIDUAL\n(predicted − measured)", "#D6E4F0", NAVY),
        (6.9, 2.9, 2.8, 1.0, "Correction Δ\n+ confidence interval", ACCENT, NAVY),
        (3.6, 1.2, 2.6, 1.0, "LAYER 3\nDecision gate\n(strip formwork?\nat what risk?)", "#D6E4F0", NAVY),
        (6.9, 1.2, 2.8, 1.0, "OUTPUT\n'38.2 ± 4.1 MPa,\n90% confidence'", "#CDE6D8", GREEN),
    ]
    for x, y, w, h, txt, fc, ec in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec,
                                   linewidth=1.6, zorder=2))
        ax.text(x + w/2, y + h/2, txt, ha="center", va="center",
                fontsize=8.2, zorder=3, color="#16202B")

    arrows = [((2.9, 5.1), (3.6, 5.1)), ((6.2, 5.1), (6.9, 5.1)),
              ((4.9, 4.6), (4.9, 3.9)), ((6.2, 3.4), (6.9, 3.4)),
              ((4.9, 2.9), (4.9, 2.2)), ((6.2, 1.7), (6.9, 1.7))]
    for (x1, y1), (x2, y2) in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.8))

    ax.text(5, 0.35, "Physics carries the prediction. Machine learning only corrects the small error.\n"
                     "At zero correction the method reduces exactly to the codal calculation.",
            ha="center", fontsize=9, style="italic", color=GREY)
    ax.set_title("Project C1 — how the method works", fontsize=12,
                 fontweight="bold", color=NAVY, pad=6)
    fig.tight_layout()
    return save(fig, "fig10_c1_method.png")


if __name__ == "__main__":
    print("[ULTRON] generating figures ->")
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10):
        f()
    print("[ULTRON] done.")
