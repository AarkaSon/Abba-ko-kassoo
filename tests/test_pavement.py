"""
Verification tests for the SETU pavement damage and reliability engine.

Directive III: the engine is only trustworthy if its physical invariants are pinned.
These tests encode engineering truths that must hold regardless of implementation.

Run:  python3 tests/test_pavement.py     (or: python3 -m pytest tests/ -v)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pavement.damage import (  # noqa: E402
    FATIGUE_ENDURANCE_LIMIT,
    AxleLoadGroup,
    allowable_repetitions_fatigue,
    cumulative_fatigue_damage,
    erosion_factor_proxy,
    fatigue_damage,
    residual_life_years,
    stress_ratio,
)
from src.pavement.reliability import (  # noqa: E402
    PavementUncertainty,
    Uncertain,
    monte_carlo_damage,
    required_thickness_for_reliability,
)

SPECTRUM = [
    AxleLoadGroup("10-12 t", 110_000.0, 150_000),
    AxleLoadGroup("12-14 t", 130_000.0, 90_000),
    AxleLoadGroup("14-16 t", 150_000.0, 40_000),
    AxleLoadGroup("16-18 t", 170_000.0, 12_000),
    AxleLoadGroup("18-20 t", 190_000.0, 3_000),
]


# --------------------------------------------------------------------------- #
# Fatigue relationship
# --------------------------------------------------------------------------- #
def test_endurance_limit_gives_unlimited_life():
    """Below SR = 0.45 the concrete must show unlimited allowable repetitions."""
    assert math.isinf(allowable_repetitions_fatigue(0.30))
    assert math.isinf(allowable_repetitions_fatigue(0.449))


def test_allowable_repetitions_decrease_with_stress_ratio():
    """Higher stress ratio must always mean fewer allowable repetitions."""
    srs = [0.46, 0.50, 0.55, 0.60, 0.70, 0.80]
    ns = [allowable_repetitions_fatigue(s) for s in srs]
    assert all(a > b for a, b in zip(ns, ns[1:])), ns


def test_fatigue_branches_are_continuous_at_055():
    """The two fatigue branches must not disagree wildly at the SR = 0.55 boundary."""
    lo = allowable_repetitions_fatigue(0.5499)
    hi = allowable_repetitions_fatigue(0.5501)
    assert 0.2 < lo / hi < 5.0, f"discontinuity at SR=0.55: {lo:.3e} vs {hi:.3e}"


def test_stress_ratio_basic():
    assert math.isclose(stress_ratio(2.25, 4.5), 0.5)


def test_damage_below_endurance_limit_is_zero():
    """Any number of repetitions below the endurance limit accrues no damage."""
    n_allow = allowable_repetitions_fatigue(0.40)
    assert fatigue_damage(1e9, n_allow) == 0.0


# --------------------------------------------------------------------------- #
# Cumulative damage
# --------------------------------------------------------------------------- #
def _stress_fn_factory(h: float, k: float = 0.08, mr_unused: float = 0.0):
    from src.design.westergaard import SlabProperties, WheelLoad, stress_edge

    slab = SlabProperties(h=h, E=30_000.0, mu=0.15, k=k)

    def f(load_N: float) -> float:
        return stress_edge(slab, WheelLoad.from_pressure(P=load_N / 2.0, p=0.8))

    return f


def test_thicker_slab_accumulates_less_damage():
    """The central design relationship: more thickness, less fatigue damage."""
    dmg = [
        cumulative_fatigue_damage(SPECTRUM, _stress_fn_factory(h), 4.5).total_damage
        for h in (250.0, 280.0, 300.0, 330.0)
    ]
    assert all(a > b for a, b in zip(dmg, dmg[1:])), dmg


def test_stronger_concrete_accumulates_less_damage():
    """Higher modulus of rupture must reduce damage."""
    f = _stress_fn_factory(280.0)
    dmg = [
        cumulative_fatigue_damage(SPECTRUM, f, mr).total_damage
        for mr in (3.5, 4.0, 4.5, 5.0)
    ]
    assert all(a > b for a, b in zip(dmg, dmg[1:])), dmg


def test_heavy_axles_dominate_damage():
    """
    Engineering truth: a small number of heavy axles causes more fatigue damage than
    a large number of light ones. If this fails, the fatigue law is wrong.
    """
    res = cumulative_fatigue_damage(SPECTRUM, _stress_fn_factory(280.0), 4.5)
    lightest = res.per_group[0]
    heaviest = res.per_group[-1]
    assert heaviest["applied_n"] < lightest["applied_n"] / 10
    assert heaviest["damage"] > lightest["damage"]


def test_damage_scales_linearly_with_repetitions():
    """Miner's rule is linear in applied repetitions."""
    f = _stress_fn_factory(280.0)
    a = cumulative_fatigue_damage(SPECTRUM, f, 4.5).total_damage
    doubled = [AxleLoadGroup(g.label, g.load_N, g.repetitions * 2) for g in SPECTRUM]
    b = cumulative_fatigue_damage(doubled, f, 4.5).total_damage
    assert math.isclose(b / a, 2.0, rel_tol=1e-9)


def test_acceptance_criterion():
    res = cumulative_fatigue_damage(SPECTRUM, _stress_fn_factory(330.0), 4.5)
    assert res.is_safe
    assert res.utilisation_pct == res.total_damage * 100.0


# --------------------------------------------------------------------------- #
# Residual life
# --------------------------------------------------------------------------- #
def test_residual_life_already_failed():
    assert residual_life_years(1.2, 0.05) == 0.0


def test_residual_life_basic():
    """0.5 damage remaining at 0.1/yr with no growth = 5 years."""
    assert math.isclose(residual_life_years(0.5, 0.1, 0.0), 5.0, rel_tol=1e-6)


def test_traffic_growth_shortens_life():
    no_growth = residual_life_years(0.3, 0.05, 0.00)
    growth = residual_life_years(0.3, 0.05, 0.08)
    assert growth < no_growth


def test_zero_damage_rate_returns_horizon():
    assert residual_life_years(0.3, 0.0, 0.0, max_years=50) == 50.0


# --------------------------------------------------------------------------- #
# Erosion proxy
# --------------------------------------------------------------------------- #
def test_erosion_proxy_increases_with_deflection():
    a = erosion_factor_proxy(0.5, 0.08, 300.0)
    b = erosion_factor_proxy(1.0, 0.08, 300.0)
    assert b > a
    # quadratic in deflection
    assert math.isclose(b / a, 4.0, rel_tol=1e-9)


# --------------------------------------------------------------------------- #
# Reliability
# --------------------------------------------------------------------------- #
def test_zero_variability_reproduces_deterministic_result():
    """
    CRITICAL: at zero CoV the Monte Carlo must collapse exactly onto the
    deterministic IRC:58 calculation. This proves SETU extends the code
    rather than replacing it.
    """
    unc = PavementUncertainty(
        k=Uncertain(0.08, 0.0),
        modulus_of_rupture=Uncertain(4.5, 0.0),
        E=Uncertain(30_000.0, 0.0),
        thickness=Uncertain(280.0, 0.0),
        traffic_multiplier=Uncertain(1.0, 0.0),
    )
    mc = monte_carlo_damage(unc, SPECTRUM, n_sim=50)
    det = cumulative_fatigue_damage(
        SPECTRUM, _stress_fn_factory(280.0, 0.08), 4.5
    ).total_damage
    assert math.isclose(mc.mean_damage, det, rel_tol=1e-9), (mc.mean_damage, det)
    assert mc.probability_of_failure in (0.0, 1.0)


def test_monte_carlo_is_reproducible():
    """A fixed seed must give identical results — required for auditable reports."""
    unc = PavementUncertainty(
        k=Uncertain(0.08, 0.25),
        modulus_of_rupture=Uncertain(4.5, 0.12),
        E=Uncertain(30_000.0, 0.12),
        thickness=Uncertain(280.0, 0.03),
    )
    a = monte_carlo_damage(unc, SPECTRUM, n_sim=300, seed=7)
    b = monte_carlo_damage(unc, SPECTRUM, n_sim=300, seed=7)
    assert a.mean_damage == b.mean_damage
    assert a.probability_of_failure == b.probability_of_failure


def test_more_variability_lowers_reliability():
    """Greater input uncertainty must reduce reliability at fixed thickness."""

    def rel(cov: float) -> float:
        unc = PavementUncertainty(
            k=Uncertain(0.08, cov),
            modulus_of_rupture=Uncertain(4.5, cov),
            E=Uncertain(30_000.0, 0.10),
            thickness=Uncertain(290.0, 0.03),
        )
        return monte_carlo_damage(unc, SPECTRUM, n_sim=1500, seed=3).reliability

    assert rel(0.10) > rel(0.35)


def test_required_thickness_decreases_with_better_subgrade():
    """
    THE COMMERCIAL CLAIM UNDER TEST: stronger ground must require less concrete
    at the same reliability. This is where SETU's material saving comes from.
    """
    def h_for(k_mean: float) -> float:
        unc = PavementUncertainty(
            k=Uncertain(k_mean, 0.22),
            modulus_of_rupture=Uncertain(4.5, 0.12),
            E=Uncertain(30_000.0, 0.12),
            thickness=Uncertain(300.0, 0.03),
        )
        h, _ = required_thickness_for_reliability(
            unc, SPECTRUM, target_reliability=0.90, n_sim=800, seed=11
        )
        return h

    strong, weak = h_for(0.20), h_for(0.045)
    assert strong < weak, f"strong subgrade {strong} !< weak subgrade {weak}"


def test_higher_target_reliability_requires_more_thickness():
    unc = PavementUncertainty(
        k=Uncertain(0.08, 0.25),
        modulus_of_rupture=Uncertain(4.5, 0.12),
        E=Uncertain(30_000.0, 0.12),
        thickness=Uncertain(300.0, 0.03),
    )
    h80, _ = required_thickness_for_reliability(unc, SPECTRUM, 0.80, n_sim=800, seed=5)
    h95, _ = required_thickness_for_reliability(unc, SPECTRUM, 0.95, n_sim=800, seed=5)
    assert h95 >= h80


def test_percentile_ordering():
    unc = PavementUncertainty(
        k=Uncertain(0.08, 0.25),
        modulus_of_rupture=Uncertain(4.5, 0.12),
        E=Uncertain(30_000.0, 0.12),
        thickness=Uncertain(280.0, 0.03),
    )
    r = monte_carlo_damage(unc, SPECTRUM, n_sim=1000, seed=2)
    assert r.percentile(10) <= r.percentile(50) <= r.percentile(90)
    assert math.isclose(r.percentile(50), r.median_damage, rel_tol=0.02)


def test_input_validation():
    for bad in (
        lambda: Uncertain(1.0, -0.1),
        lambda: Uncertain(1.0, 0.1, "weibull"),
        lambda: AxleLoadGroup("x", -1.0, 10),
        lambda: AxleLoadGroup("x", 1.0, -10),
        lambda: stress_ratio(1.0, 0.0),
        lambda: erosion_factor_proxy(1.0, 0.08, 0.0),
    ):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError("invalid input accepted")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"  FAIL  {fn.__name__}: {exc}")
    print(f"\n{len(fns) - fails}/{len(fns)} passed")
    sys.exit(1 if fails else 0)
