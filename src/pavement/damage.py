"""
SETU — Cumulative damage models for concrete pavements.

PURPOSE
-------
Layer 1 of the SETU engine: the deterministic, code-traceable mechanistic core.
Implements the cumulative fatigue damage framework used for rigid pavement design,
run *forward in time* to estimate residual life rather than once at design stage.

METHOD (procedure implemented; refer to the standards for the authoritative text)
---------------------------------------------------------------------------------
[1] IRC:58 — Guidelines for the Design of Plain Jointed Rigid Pavements for Highways.
    Cumulative fatigue damage approach; bottom-up cracking (BUC) under the combination
    of axle load and negative/positive temperature differential, and top-down cracking
    (TDC). Stress ratio governs allowable repetitions.
[2] Portland Cement Association (1984), "Thickness Design for Concrete Highway and
    Street Pavements" — origin of the fatigue and erosion criteria adopted widely,
    including the stress-ratio fatigue relations used here.
[3] Miner, M.A. (1945) "Cumulative Damage in Fatigue", J. Appl. Mech. 12, A159-A164.
    Linear damage summation.
[4] IRC:SP:83 — Maintenance, Repair and Rehabilitation of Cement Concrete Pavements
    (distress classification vocabulary).

LEGAL / COPYRIGHT NOTE
----------------------
Copyright in Indian Standards and IRC publications vests in BIS / IRC respectively.
This module implements the *computational procedure and numerical relationships*
(which are facts, not protected expression). No table layout, clause text or
commentary is reproduced. Every output cites the governing clause and directs the
user to the standard itself. See docs/stage0/02_bis_permission_letter.md.

UNITS (SI, consistent with src/design/westergaard.py)
-----------------------------------------------------
    length : mm | force : N | stress : MPa | k : MPa/mm

No third-party dependencies — standard library only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

__all__ = [
    "FATIGUE_ENDURANCE_LIMIT",
    "allowable_repetitions_fatigue",
    "stress_ratio",
    "fatigue_damage",
    "AxleLoadGroup",
    "DamageResult",
    "cumulative_fatigue_damage",
    "residual_life_years",
    "erosion_factor_proxy",
]

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

#: Below this stress ratio the concrete is taken to have effectively unlimited
#: fatigue life (endurance limit). Ref [1], [2].
FATIGUE_ENDURANCE_LIMIT: float = 0.45

#: Sentinel for "unlimited" allowable repetitions.
UNLIMITED: float = float("inf")


# --------------------------------------------------------------------------- #
# Fatigue
# --------------------------------------------------------------------------- #
def stress_ratio(flexural_stress: float, modulus_of_rupture: float) -> float:
    """
    Stress Ratio, SR = sigma / MR.

    sigma  : flexural (tensile) stress induced by axle load + temperature warping [MPa]
    MR     : modulus of rupture (flexural strength) of the concrete               [MPa]

    SR is the single governing quantity for concrete fatigue. Ref [1], [2].
    """
    if modulus_of_rupture <= 0:
        raise ValueError("Modulus of rupture must be positive.")
    if flexural_stress < 0:
        raise ValueError("Flexural stress must be non-negative.")
    return flexural_stress / modulus_of_rupture


def allowable_repetitions_fatigue(sr: float) -> float:
    """
    Allowable load repetitions N for a given stress ratio SR.

    Three-branch relationship (Ref [1] cl. 6 / Ref [2]):

        SR <  0.45          ->  N = infinity          (endurance limit)
        0.45 <= SR <= 0.55  ->  N = [ 4.2577 / (SR - 0.4325) ] ^ 3.268
        SR >  0.55          ->  log10(N) = (0.9718 - SR) / 0.0828

    Returns allowable repetitions (float; may be inf).

    NOTE: verify the branch constants against the current edition of IRC:58 before
    using output in a submitted design. Constants are reproduced here as numerical
    relationships for computation only.
    """
    if sr <= 0:
        return UNLIMITED
    if sr < FATIGUE_ENDURANCE_LIMIT:
        return UNLIMITED
    if sr <= 0.55:
        denom = sr - 0.4325
        if denom <= 0:                       # numerical guard
            return UNLIMITED
        return (4.2577 / denom) ** 3.268
    # SR > 0.55
    exponent = (0.9718 - sr) / 0.0828
    # Guard against overflow/underflow for extreme SR
    if exponent < -30.0:
        return 0.0
    return 10.0 ** exponent


def fatigue_damage(applied: float, allowable: float) -> float:
    """
    Miner's linear damage increment, n/N. Ref [3].

    Returns 0.0 when allowable is infinite (below endurance limit),
    and inf when allowable is zero with applied load present.
    """
    if applied < 0:
        raise ValueError("Applied repetitions must be non-negative.")
    if math.isinf(allowable):
        return 0.0
    if allowable <= 0:
        return UNLIMITED if applied > 0 else 0.0
    return applied / allowable


# --------------------------------------------------------------------------- #
# Axle load spectrum
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class AxleLoadGroup:
    """
    One band of the axle load spectrum.

    label      : description, e.g. "Single axle 16-18 t"
    load_N     : representative axle load for the group                 [N]
    repetitions: expected number of repetitions over the analysis period
    """

    label: str
    load_N: float
    repetitions: float

    def __post_init__(self) -> None:
        if self.load_N <= 0:
            raise ValueError(f"{self.label}: axle load must be positive.")
        if self.repetitions < 0:
            raise ValueError(f"{self.label}: repetitions must be non-negative.")


@dataclass
class DamageResult:
    """Outcome of a cumulative damage computation."""

    total_damage: float
    per_group: list[dict] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        """Cumulative Fatigue Damage <= 1.0 is the design acceptance criterion."""
        return self.total_damage <= 1.0

    @property
    def utilisation_pct(self) -> float:
        """Damage expressed as a percentage of the design life consumed."""
        return 100.0 * self.total_damage


def cumulative_fatigue_damage(
    groups: list[AxleLoadGroup],
    stress_fn,
    modulus_of_rupture: float,
) -> DamageResult:
    """
    Cumulative Fatigue Damage (CFD) over an axle load spectrum. Ref [1], [3].

        CFD = sum_i ( n_i / N_i )

    groups             : axle load spectrum
    stress_fn          : callable(load_N) -> flexural stress [MPa]. Supply a function
                         that wraps the Westergaard edge-stress computation (or any
                         other stress model) for the slab under consideration.
    modulus_of_rupture : concrete flexural strength [MPa]

    Acceptance: CFD <= 1.0.
    """
    if modulus_of_rupture <= 0:
        raise ValueError("Modulus of rupture must be positive.")

    total = 0.0
    rows: list[dict] = []
    for g in groups:
        sigma = stress_fn(g.load_N)
        sr = stress_ratio(sigma, modulus_of_rupture)
        n_allow = allowable_repetitions_fatigue(sr)
        d = fatigue_damage(g.repetitions, n_allow)
        total += d
        rows.append(
            {
                "label": g.label,
                "load_kN": g.load_N / 1000.0,
                "stress_MPa": sigma,
                "stress_ratio": sr,
                "allowable_N": n_allow,
                "applied_n": g.repetitions,
                "damage": d,
            }
        )
    return DamageResult(total_damage=total, per_group=rows)


# --------------------------------------------------------------------------- #
# Residual life
# --------------------------------------------------------------------------- #
def residual_life_years(
    damage_to_date: float,
    annual_damage_rate: float,
    traffic_growth_rate: float = 0.0,
    max_years: int = 100,
) -> float:
    """
    Years remaining until cumulative damage reaches 1.0.

    damage_to_date      : CFD already accumulated                     [-]
    annual_damage_rate  : CFD accrued in the coming year              [1/yr]
    traffic_growth_rate : compound annual traffic growth, e.g. 0.05   [-]
    max_years           : cap on the search horizon

    Returns years to CFD = 1.0 (0.0 if already exceeded; max_years if not reached).

    With growth r, damage in year t is d0 * (1+r)^t, so the summation is a geometric
    series; solved here by direct accumulation for clarity and robustness.
    """
    if damage_to_date < 0 or annual_damage_rate < 0:
        raise ValueError("Damage values must be non-negative.")
    if damage_to_date >= 1.0:
        return 0.0
    if annual_damage_rate <= 0:
        return float(max_years)

    remaining = 1.0 - damage_to_date
    accumulated = 0.0
    d = annual_damage_rate
    for year in range(1, max_years + 1):
        if accumulated + d >= remaining:
            # linear interpolation within the year
            return (year - 1) + (remaining - accumulated) / d
        accumulated += d
        d *= 1.0 + traffic_growth_rate
    return float(max_years)


# --------------------------------------------------------------------------- #
# Erosion (proxy)
# --------------------------------------------------------------------------- #
def erosion_factor_proxy(
    deflection_mm: float,
    k_MPa_per_mm: float,
    slab_thickness_mm: float,
) -> float:
    """
    Proxy indicator for erosion / pumping potential at slab corners and edges.

    Erosion distress is driven by the rate of work done on the foundation by the
    deflecting slab. A widely used proxy is the corner deflection combined with
    foundation stiffness:

        P_erosion ~ k * w^2 / h        (relative index, not an absolute measure)

    Returns a dimensionless relative index for RANKING segments against one another.

    IMPORTANT: this is an ULTRON-defined *relative* index for prioritisation, NOT the
    PCA erosion factor and NOT a codal acceptance criterion. It must not be used as a
    design check. It exists so that segments can be ordered by erosion susceptibility
    when only deflection and foundation data are available. Calibrate against observed
    pumping/faulting before relying on it. Flagged as an assumption in every report.
    """
    if slab_thickness_mm <= 0:
        raise ValueError("Slab thickness must be positive.")
    if k_MPa_per_mm <= 0:
        raise ValueError("k must be positive.")
    if deflection_mm < 0:
        raise ValueError("Deflection must be non-negative.")
    return k_MPa_per_mm * deflection_mm ** 2 / slab_thickness_mm * 1000.0


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from design.westergaard import SlabProperties, WheelLoad, stress_edge  # noqa: E402

    slab = SlabProperties(h=280.0, E=30_000.0, mu=0.15, k=0.08)
    MR = 4.5  # MPa, 28-day flexural strength

    def edge_stress(load_N: float) -> float:
        """Wheel load = half the axle load, on a circular contact at 0.8 MPa."""
        return stress_edge(slab, WheelLoad.from_pressure(P=load_N / 2.0, p=0.8))

    spectrum = [
        AxleLoadGroup("Single axle 10-12 t", 110_000.0, 150_000),
        AxleLoadGroup("Single axle 12-14 t", 130_000.0, 90_000),
        AxleLoadGroup("Single axle 14-16 t", 150_000.0, 40_000),
        AxleLoadGroup("Single axle 16-18 t", 170_000.0, 12_000),
        AxleLoadGroup("Single axle 18-20 t", 190_000.0, 3_000),
    ]

    res = cumulative_fatigue_damage(spectrum, edge_stress, MR)

    print("=" * 88)
    print(" SETU — CUMULATIVE FATIGUE DAMAGE (IRC:58 framework)")
    print("=" * 88)
    print(f" Slab: h={slab.h:.0f} mm  E={slab.E:,.0f} MPa  k={slab.k} MPa/mm  "
          f"l={slab.l:.1f} mm  MR={MR} MPa")
    print("-" * 88)
    print(f"{'Axle group':<24}{'kN':>8}{'MPa':>9}{'SR':>8}"
          f"{'N allow':>15}{'n appl':>12}{'damage':>12}")
    print("-" * 88)
    for r in res.per_group:
        n_allow = "unlimited" if math.isinf(r["allowable_N"]) else f"{r['allowable_N']:.3e}"
        print(f"{r['label']:<24}{r['load_kN']:>8.0f}{r['stress_MPa']:>9.3f}"
              f"{r['stress_ratio']:>8.3f}{n_allow:>15}{r['applied_n']:>12,.0f}"
              f"{r['damage']:>12.4f}")
    print("-" * 88)
    print(f"{'CUMULATIVE FATIGUE DAMAGE':<60}{res.total_damage:>12.4f}")
    print(f"{'Design life consumed':<60}{res.utilisation_pct:>11.1f}%")
    print(f"{'Acceptance (CFD <= 1.0)':<60}{'PASS' if res.is_safe else 'FAIL':>12}")
    rl = residual_life_years(res.total_damage, 0.05, 0.06)
    print(f"{'Residual life @ 0.05/yr, 6% growth':<60}{rl:>10.1f} yr")
    print("=" * 88)
