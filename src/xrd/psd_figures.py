"""
Publication-Quality Figure Generator for PSD-Strength Correlation Analysis
============================================================================
Generates all figures for the manuscript:
  Fig. 1: Integrated Area PSD stacked bars
  Fig. 2: Peak Intensity PSD stacked bars
  Fig. 3: CS vs Amorphous PSD
  Fig. 4: CS vs Crystalline PSD
  Fig. 5: IA vs PI predictive power comparison
  Fig. 6: NASH vs CASH bubble chart
  Fig. 7: Amorphous fraction vs CS
  Fig. 8: Correlation heatmap
  Fig. 9: Performance radar
  Fig. 10: Total PSD vs CS distinction

All figures: 300 dpi, colourblind-friendly palette.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from typing import List
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
from psd_calculator import (
    PSDCalculator, PSDResult, compute_correlations,
    CorrelationMetrics, MIXES
)

# ---- Colourblind-friendly palette ----
C_QUARTZ   = '#E69F00'
C_MULLITE  = '#56B4E9'
C_CALCITE  = '#009E73'
C_NASH     = '#CC79A7'
C_CASH     = '#0072B2'
C_CRYSTAL  = '#999999'
C_AMORPH   = '#D55E00'
C_REGRESS  = '#CC3311'
C_BEST     = '#004488'

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 10,
    'axes.titlesize': 12, 'axes.labelsize': 11,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 8, 'figure.dpi': 300,
    'savefig.dpi': 300, 'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})


def get_results() -> List[PSDResult]:
    return PSDCalculator().compute_all()


def save_fig(fig, name: str, outdir: str = "results/figures"):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")


# =====================================================
# FIG 1: Integrated Area PSD stacked bars
# =====================================================
def fig1(results: List[PSDResult]):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6),
                                     gridspec_kw={'width_ratios': [2, 1]})
    labels = [r.label for r in results]
    x = np.arange(len(labels))
    w = 0.55

    q = np.array([r.q_ia for r in results])
    m = np.array([r.m_ia for r in results])
    c = np.array([r.c_ia for r in results])
    n = np.array([r.nash_ia for r in results])
    ch = np.array([r.cash_ia for r in results])

    ax1.bar(x, q, w, label='Quartz', color=C_QUARTZ, edgecolor='white', lw=0.3)
    ax1.bar(x, m, w, bottom=q, label='Mullite', color=C_MULLITE, edgecolor='white', lw=0.3)
    ax1.bar(x, c, w, bottom=q+m, label='Calcite', color=C_CALCITE, edgecolor='white', lw=0.3)
    ax1.bar(x, n, w, bottom=q+m+c, label='N-A-S-H', color=C_NASH, edgecolor='white', lw=0.3)
    ax1.bar(x, ch, w, bottom=q+m+c+n, label='C-A-S-H', color=C_CASH, edgecolor='white', lw=0.3)

    for i, r in enumerate(results):
        ax1.text(i, r.total_ia + 300, f'{r.total_ia:.0f}', ha='center', va='bottom',
                fontsize=6.5, fontweight='bold', color='#333')

    ax1.set_xticks(x); ax1.set_xticklabels(labels)
    ax1.set_ylabel('Integrated Area PSD (a.u.)', fontweight='bold')
    ax1.set_title('(a) Phase-wise Integrated Area PSD', fontweight='bold', loc='left')
    ax1.legend(loc='upper right', ncol=3, framealpha=0.9, edgecolor='grey')
    ax1.set_ylim(0, max(r.total_ia for r in results) * 1.2)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}k'))

    # Panel (b): Crystalline vs Amorphous
    cryst_tot = np.array([r.crystalline_ia for r in results])
    amor_tot = np.array([r.amorphous_ia for r in results])
    ax2.bar(x, cryst_tot, w, label='Crystalline (Q+M+C)', color=C_CRYSTAL, edgecolor='white', lw=0.3)
    ax2.bar(x, amor_tot, w, bottom=cryst_tot, label='Amorphous (NASH+CASH)', color=C_AMORPH, edgecolor='white', lw=0.3)
    for i, r in enumerate(results):
        ax2.text(i, r.total_ia + 300, f'{r.amor_frac*100:.1f}%', ha='center', va='bottom',
                fontsize=7, fontweight='bold', color=C_AMORPH)
    ax2.set_xticks(x); ax2.set_xticklabels(labels)
    ax2.set_ylabel('Integrated Area PSD (a.u.)', fontweight='bold')
    ax2.set_title('(b) Crystalline vs Amorphous', fontweight='bold', loc='left')
    ax2.legend(loc='upper right', framealpha=0.9, edgecolor='grey')
    ax2.set_ylim(0, max(r.total_ia for r in results) * 1.2)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}k'))

    fig.suptitle('Fig. 1: Integrated Area PSD — Complete Phase Deconvolution',
                 fontweight='bold', fontsize=13, y=1.01)
    plt.tight_layout()
    save_fig(fig, 'fig1_integrated_area_psd.png')


# =====================================================
# FIG 2: Peak Intensity PSD stacked bars
# =====================================================
def fig2(results: List[PSDResult]):
    fig, ax = plt.subplots(1, 1, figsize=(10, 5.5))
    labels = [r.label for r in results]
    x = np.arange(len(labels)); w = 0.55

    q = np.array([r.q_pi for r in results])
    m = np.array([r.m_pi for r in results])
    c = np.array([r.c_pi for r in results])
    n = np.array([r.nash_pi for r in results])
    ch = np.array([r.cash_pi for r in results])

    ax.bar(x, q, w, label='Quartz', color=C_QUARTZ, edgecolor='white', lw=0.3)
    ax.bar(x, m, w, bottom=q, label='Mullite', color=C_MULLITE, edgecolor='white', lw=0.3)
    ax.bar(x, c, w, bottom=q+m, label='Calcite', color=C_CALCITE, edgecolor='white', lw=0.3)
    ax.bar(x, n, w, bottom=q+m+c, label='N-A-S-H', color=C_NASH, edgecolor='white', lw=0.3)
    ax.bar(x, ch, w, bottom=q+m+c+n, label='C-A-S-H', color=C_CASH, edgecolor='white', lw=0.3)

    for i, r in enumerate(results):
        ax.text(i, r.total_pi + 40, f'{r.total_pi:.0f}', ha='center', va='bottom',
                fontsize=7, fontweight='bold', color='#333')
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel('Peak Intensity PSD (a.u.)', fontweight='bold')
    ax.set_title('Fig. 2: Peak Intensity Photon Scattering Density', fontweight='bold')
    ax.legend(loc='upper left', ncol=5, framealpha=0.9, edgecolor='grey')
    ax.set_ylim(0, max(r.total_pi for r in results) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    save_fig(fig, 'fig2_peak_intensity_psd.png')


# =====================================================
# FIG 3: CS vs Amorphous PSD — THE MONEY PLOT
# =====================================================
def fig3(results: List[PSDResult], corr: CorrelationMetrics):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    cs = np.array([r.cs_mean for r in results])
    cs_std = np.array([r.cs_std for r in results])
    amor_ia = np.array([r.amorphous_ia for r in results])
    amor_pi = np.array([r.amorphous_pi for r in results])
    labels = [r.label for r in results]

    from numpy.polynomial.polynomial import polyfit

    # IA
    b_ia, m_ia = polyfit(amor_ia, cs, 1)
    xf = np.linspace(min(amor_ia)*0.9, max(amor_ia)*1.1, 100)
    ax1.errorbar(amor_ia, cs, yerr=cs_std, fmt='o', capsize=4, markersize=10,
                markerfacecolor=C_AMORPH, markeredgecolor='black', markeredgewidth=0.8,
                elinewidth=1.2, capthick=1.2, zorder=5)
    ax1.plot(xf, m_ia*xf + b_ia, '-', color=C_REGRESS, lw=2, alpha=0.7,
             label=f'Linear fit (R²={corr.r2_cs_vs_amorphous_ia:.3f})')
    for i, lbl in enumerate(labels):
        ax1.annotate(lbl, (amor_ia[i], cs[i]), textcoords="offset points",
                    xytext=(6, 2.5 if i%2==0 else -2.5), fontsize=8, fontweight='bold', color='#444')
    ax1.set_xlabel('Amorphous PSD — Integrated Area (a.u.)', fontweight='bold')
    ax1.set_ylabel('28-day Compressive Strength (MPa)', fontweight='bold')
    ax1.set_title(f'(a) IA Method: r = {corr.r_cs_vs_amorphous_ia:+.3f}', fontweight='bold', loc='left')
    ax1.legend(loc='lower right', framealpha=0.9); ax1.grid(alpha=0.3, linestyle='--')

    # PI
    b_pi, m_pi = polyfit(amor_pi, cs, 1)
    xf2 = np.linspace(min(amor_pi)*0.9, max(amor_pi)*1.1, 100)
    ax2.errorbar(amor_pi, cs, yerr=cs_std, fmt='s', capsize=4, markersize=10,
                markerfacecolor=C_BEST, markeredgecolor='black', markeredgewidth=0.8,
                elinewidth=1.2, capthick=1.2, zorder=5)
    ax2.plot(xf2, m_pi*xf2 + b_pi, '-', color=C_REGRESS, lw=2, alpha=0.7,
             label=f'Linear fit (R²={corr.r2_cs_vs_amorphous_pi:.3f})')
    for i, lbl in enumerate(labels):
        ax2.annotate(lbl, (amor_pi[i], cs[i]), textcoords="offset points",
                    xytext=(6, 2.5 if i%2==0 else -2.5), fontsize=8, fontweight='bold', color='#444')
    ax2.set_xlabel('Amorphous PSD — Peak Intensity (a.u.)', fontweight='bold')
    ax2.set_ylabel('28-day Compressive Strength (MPa)', fontweight='bold')
    ax2.set_title(f'(b) PI Method: r = {corr.r_cs_vs_amorphous_pi:+.3f}', fontweight='bold', loc='left')
    ax2.legend(loc='lower right', framealpha=0.9); ax2.grid(alpha=0.3, linestyle='--')

    fig.suptitle('Fig. 3: Compressive Strength vs Amorphous Gel PSD',
                 fontweight='bold', fontsize=13, y=1.01)
    plt.tight_layout()
    save_fig(fig, 'fig3_cs_vs_amorphous_psd.png')


# =====================================================
# FIG 4: CS vs Crystalline PSD
# =====================================================
def fig4(results: List[PSDResult], corr: CorrelationMetrics):
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))
    cs = np.array([r.cs_mean for r in results])
    cryst_ia = np.array([r.crystalline_ia for r in results])
    amor_frac = np.array([r.amor_frac for r in results])
    sc = ax.scatter(cryst_ia, cs, c=amor_frac, cmap='RdYlGn', s=200,
                   edgecolors='black', linewidth=0.8, zorder=5, vmin=0, vmax=0.3)
    for i, lbl in enumerate([r.label for r in results]):
        ax.annotate(lbl, (cryst_ia[i], cs[i]), textcoords="offset points",
                   xytext=(7, 4), fontsize=9, fontweight='bold', color='#333')
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8); cbar.set_label('Amorphous Fraction', fontweight='bold', fontsize=9)
    ax.set_xlabel('Crystalline PSD — Integrated Area (a.u.)', fontweight='bold')
    ax.set_ylabel('28-day Compressive Strength (MPa)', fontweight='bold')
    ax.set_title(f'Fig. 4: CS vs Crystalline PSD (r = {corr.r_cs_vs_crystalline_ia:+.3f})', fontweight='bold')
    ax.grid(alpha=0.3, linestyle='--')
    ax.annotate('High crystalline PSD →\nlow strength (L07)', xy=(22000, 25), fontsize=9, fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    ax.annotate('Low crystalline PSD →\nhigh strength (L03–L05)', xy=(9500, 50), fontsize=9, fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    plt.tight_layout()
    save_fig(fig, 'fig4_cs_vs_crystalline_psd.png')


# =====================================================
# FIG 5: IA vs PI predictive power
# =====================================================
def fig5(results: List[PSDResult], corr: CorrelationMetrics):
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    metrics = ['CS vs\nTotal PSD', 'CS vs\nAmorphous PSD', 'CS vs\nCrystalline PSD']
    ia_vals = [corr.r_cs_vs_total_ia, corr.r_cs_vs_amorphous_ia, corr.r_cs_vs_crystalline_ia]
    pi_vals = [corr.r_cs_vs_total_pi, corr.r_cs_vs_amorphous_pi, corr.r_cs_vs_crystalline_pi]
    x = np.arange(len(metrics)); w = 0.35
    b1 = ax.bar(x-w/2, ia_vals, w, label='Integrated Area PSD', color=C_AMORPH, edgecolor='black', lw=0.5)
    b2 = ax.bar(x+w/2, pi_vals, w, label='Peak Intensity PSD', color=C_BEST, edgecolor='black', lw=0.5)
    for bar in b1:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2., h+0.02*(1 if h>0 else -1), f'{h:+.3f}',
                ha='center', va='bottom' if h>0 else 'top', fontsize=9, fontweight='bold')
    for bar in b2:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2., h+0.02*(1 if h>0 else -1), f'{h:+.3f}',
                ha='center', va='bottom' if h>0 else 'top', fontsize=9, fontweight='bold')
    ax.axhline(y=0, color='black', lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(metrics)
    ax.set_ylabel("Pearson's r with Compressive Strength", fontweight='bold')
    ax.set_title('Fig. 5: Predictive Power — IA vs PI PSD', fontweight='bold')
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--'); ax.set_ylim(-1.0, 1.05)
    plt.tight_layout()
    save_fig(fig, 'fig5_ia_vs_pi_comparison.png')


# =====================================================
# FIG 6: NASH vs CASH bubble chart
# =====================================================
def fig6(results: List[PSDResult]):
    fig, ax = plt.subplots(1, 1, figsize=(8, 6.5))
    nash_ia = np.array([r.nash_ia for r in results])
    cash_ia = np.array([r.cash_ia for r in results])
    cs = np.array([r.cs_mean for r in results])
    fa_pct = np.array([m.fa_ggbs[0] for m in MIXES])
    sc = ax.scatter(nash_ia, cash_ia, s=cs*10, c=fa_pct, cmap='RdYlBu',
                   alpha=0.75, edgecolors='black', lw=0.8, vmin=55, vmax=85)
    for i, lbl in enumerate([r.label for r in results]):
        ax.annotate(f'{lbl}\n({cs[i]:.0f} MPa)', (nash_ia[i], cash_ia[i]),
                   textcoords="offset points", xytext=(8, 4), fontsize=8, fontweight='bold')
    xmax = max(nash_ia)*1.15; ymax = max(cash_ia)*1.15
    ax.plot([0, xmax], [0, ymax], '--', color='grey', alpha=0.4)
    ax.plot([0, xmax], [0, ymax*0.5], ':', color='grey', alpha=0.3)
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8); cbar.set_label('Fly Ash Content (%)', fontweight='bold', fontsize=9)
    ax.set_xlabel('N-A-S-H PSD — Integrated Area (a.u.)', fontweight='bold')
    ax.set_ylabel('C-A-S-H PSD — Integrated Area (a.u.)', fontweight='bold')
    ax.set_title('Fig. 6: NASH vs CASH Gel Formation (bubble ∝ CS)', fontweight='bold')
    ax.set_xlim(-100, xmax); ax.set_ylim(-10, ymax); ax.grid(alpha=0.3, linestyle='--')
    plt.tight_layout()
    save_fig(fig, 'fig6_nash_vs_cash_bubble.png')


# =====================================================
# FIG 7: Amorphous Fraction vs CS
# =====================================================
def fig7(results: List[PSDResult]):
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))
    cs = np.array([r.cs_mean for r in results])
    amor_frac = np.array([r.amor_frac for r in results])
    nc_ratio = np.array([min(r.nash_cash_ratio, 50) for r in results])
    from numpy.polynomial.polynomial import polyfit
    b, m = polyfit(amor_frac, cs, 1)
    xf = np.linspace(0, max(amor_frac)*1.1, 100)
    ss_res = np.sum((cs - (m*amor_frac + b))**2)
    ss_tot = np.sum((cs - np.mean(cs))**2)
    r2 = 1 - ss_res/ss_tot
    sc = ax.scatter(amor_frac, cs, c=nc_ratio, cmap='coolwarm', s=200,
                   edgecolors='black', lw=0.8, zorder=5)
    ax.plot(xf, m*xf + b, '-', color=C_REGRESS, lw=2.5, alpha=0.6, label=f'Linear fit (R²={r2:.3f})')
    for i, lbl in enumerate([r.label for r in results]):
        ax.annotate(lbl, (amor_frac[i], cs[i]), textcoords="offset points",
                   xytext=(6, 4), fontsize=9, fontweight='bold', color='#333')
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8); cbar.set_label('NASH/CASH Ratio', fontweight='bold', fontsize=9)
    ax.set_xlabel('Amorphous Gel Fraction of Total PSD', fontweight='bold')
    ax.set_ylabel('28-day Compressive Strength (MPa)', fontweight='bold')
    ax.set_title('Fig. 7: Amorphous Gel Fraction vs Compressive Strength', fontweight='bold')
    ax.legend(loc='lower right', framealpha=0.9); ax.grid(alpha=0.3, linestyle='--')
    plt.tight_layout()
    save_fig(fig, 'fig7_amorphous_fraction_vs_cs.png')


# =====================================================
# FIG 8: Correlation Heatmap
# =====================================================
def fig8(results: List[PSDResult]):
    fig, ax = plt.subplots(1, 1, figsize=(9, 7))
    cs = np.array([r.cs_mean for r in results])
    data = np.column_stack([cs,
        [r.q_ia for r in results], [r.m_ia for r in results], [r.c_ia for r in results],
        [r.nash_ia for r in results], [r.cash_ia for r in results],
        [r.crystalline_ia for r in results], [r.amorphous_ia for r in results],
        [r.total_ia for r in results], [r.amor_frac for r in results]])
    var_names = ['CS\n(MPa)', 'Quartz\nIA', 'Mullite\nIA', 'Calcite\nIA',
                 'NASH\nIA', 'CASH\nIA', 'Cryst.\nTotal', 'Amor.\nTotal', 'Total\nPSD', 'Amor.\nFrac']
    corr_mat = np.corrcoef(data.T)
    im = ax.imshow(corr_mat, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')
    for i in range(len(var_names)):
        for j in range(len(var_names)):
            if i >= j:
                val = corr_mat[i, j]
                color = 'white' if abs(val) > 0.65 else 'black'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=8,
                       fontweight='bold', color=color)
    ax.set_xticks(range(len(var_names))); ax.set_yticks(range(len(var_names)))
    ax.set_xticklabels(var_names, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(var_names, fontsize=8)
    ax.set_title('Fig. 8: Pearson Correlation Matrix — PSD Components vs Strength', fontweight='bold', fontsize=11)
    plt.colorbar(im, ax=ax, shrink=0.8, label="Pearson's r")
    plt.tight_layout()
    save_fig(fig, 'fig8_correlation_heatmap.png')


# =====================================================
# FIG 9: Performance Radar (Top 3)
# =====================================================
def fig9(results: List[PSDResult]):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), subplot_kw=dict(polar=True))
    sorted_r = sorted(results, key=lambda r: r.cs_mean, reverse=True)
    top3 = sorted_r[:3]
    dims = ['Compressive\nStrength', 'Amorphous\nPSD (IA)', 'NASH PSD', 'CASH PSD',
            'Amorphous\nFraction', 'S/N Ratio\n(CS)', 'Crystalline\nDissolution']
    all_cs = np.array([r.cs_mean for r in results])
    all_amor = np.array([r.amorphous_ia for r in results])
    all_nash = np.array([r.nash_ia for r in results])
    all_cash = np.array([r.cash_ia for r in results])
    all_frac = np.array([r.amor_frac for r in results])
    all_cryst = np.array([r.crystalline_ia for r in results])
    max_cryst = max(all_cryst)
    all_diss = 1 - all_cryst/max_cryst
    sn_ratios = {'L01':23.665,'L02':29.455,'L03':34.380,'L04':34.222,'L05':34.217,
                 'L06':31.779,'L07':26.863,'L08':33.614,'L09':32.589}
    all_sn = np.array([sn_ratios[r.label] for r in results])

    def norm(vals, all_vals):
        mn, mx = min(all_vals), max(all_vals)
        return (vals-mn)/(mx-mn) if mx>mn else np.ones_like(vals)*0.5

    angles = np.linspace(0, 2*np.pi, len(dims), endpoint=False).tolist()
    angles += angles[:1]
    colors = [C_BEST, C_AMORPH, C_CALCITE]
    for idx, r in enumerate(top3):
        vals = [norm(np.array([r.cs_mean]), all_cs)[0],
                norm(np.array([r.amorphous_ia]), all_amor)[0],
                norm(np.array([r.nash_ia]), all_nash)[0],
                norm(np.array([r.cash_ia]), all_cash)[0],
                norm(np.array([r.amor_frac]), all_frac)[0],
                norm(np.array([sn_ratios[r.label]]), all_sn)[0],
                norm(np.array([1-r.crystalline_ia/max_cryst]), all_diss)[0]]
        vals += vals[:1]
        ax.fill(angles, vals, alpha=0.15, color=colors[idx])
        ax.plot(angles, vals, 'o-', lw=2, color=colors[idx], label=f'{r.label} (CS={r.cs_mean:.0f} MPa)', markersize=6)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(dims, fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.set_title('Fig. 9: Multi-Dimensional Performance Radar — Top 3 Mixes', fontweight='bold', fontsize=12, pad=25)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), framealpha=0.9); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_fig(fig, 'fig9_performance_radar.png')


# =====================================================
# FIG 10: Total PSD vs CS — critical distinction
# =====================================================
def fig10(results: List[PSDResult], corr: CorrelationMetrics):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    cs = np.array([r.cs_mean for r in results])
    total_ia = np.array([r.total_ia for r in results])
    total_pi = np.array([r.total_pi for r in results])
    amor_frac = np.array([r.amor_frac for r in results])
    labels = [r.label for r in results]

    sc1 = ax1.scatter(total_ia, cs, c=amor_frac, cmap='RdYlGn', s=180,
                     edgecolors='black', lw=0.8, zorder=5, vmin=0, vmax=0.3)
    for i, lbl in enumerate(labels):
        ax1.annotate(lbl, (total_ia[i], cs[i]), textcoords="offset points",
                    xytext=(6, 4), fontsize=8, fontweight='bold')
    ax1.set_xlabel('Total PSD — Integrated Area (a.u.)', fontweight='bold')
    ax1.set_ylabel('28-day Compressive Strength (MPa)', fontweight='bold')
    ax1.set_title(f'(a) Total PSD (IA): r = {corr.r_cs_vs_total_ia:+.3f}', fontweight='bold', loc='left')
    ax1.grid(alpha=0.3, linestyle='--')
    cbar1 = plt.colorbar(sc1, ax=ax1, shrink=0.8); cbar1.set_label('Amor. Frac.', fontsize=8)

    sc2 = ax2.scatter(total_pi, cs, c=amor_frac, cmap='RdYlGn', s=180,
                     edgecolors='black', lw=0.8, zorder=5, vmin=0, vmax=0.3)
    for i, lbl in enumerate(labels):
        ax2.annotate(lbl, (total_pi[i], cs[i]), textcoords="offset points",
                    xytext=(6, 4), fontsize=8, fontweight='bold')
    ax2.set_xlabel('Total PSD — Peak Intensity (a.u.)', fontweight='bold')
    ax2.set_ylabel('28-day Compressive Strength (MPa)', fontweight='bold')
    ax2.set_title(f'(b) Total PSD (PI): r = {corr.r_cs_vs_total_pi:+.3f}', fontweight='bold', loc='left')
    ax2.grid(alpha=0.3, linestyle='--')
    cbar2 = plt.colorbar(sc2, ax=ax2, shrink=0.8); cbar2.set_label('Amor. Frac.', fontsize=8)

    fig.suptitle('Fig. 10: Total PSD vs Compressive Strength — Why Deconvolution Matters',
                 fontweight='bold', fontsize=13, y=1.01)
    plt.tight_layout()
    save_fig(fig, 'fig10_total_psd_vs_cs.png')


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    print("Computing PSD results...")
    results = get_results()
    corr = compute_correlations(results)
    print("\nGenerating publication-quality figures (300 dpi)...\n")
    fig1(results)
    fig2(results)
    fig3(results, corr)
    fig4(results, corr)
    fig5(results, corr)
    fig6(results)
    fig7(results)
    fig8(results)
    fig9(results)
    fig10(results, corr)
    print(f"\nAll 10 figures saved in results/figures/")
    print(f"\nKey finding: Amorphous gel PSD dominates CS prediction")
    print(f"  IA: r = {corr.r_cs_vs_amorphous_ia:+.4f}, R² = {corr.r2_cs_vs_amorphous_ia:.4f}")
    print(f"  PI: r = {corr.r_cs_vs_amorphous_pi:+.4f}, R² = {corr.r2_cs_vs_amorphous_pi:.4f}")
    print(f"  Crystalline PSD vs CS: r = {corr.r_cs_vs_crystalline_ia:+.4f} (negative!)")
