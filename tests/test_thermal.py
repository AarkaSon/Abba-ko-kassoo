"""
Verification tests for the SETU thermal warping / dual-cracking module.

The Bradbury fit is ORIGINAL WORK approximating a published curve. Its accuracy is
therefore a claim that must be pinned by test, not asserted in a docstring.
(An earlier revision of this module claimed +/-0.03 while actually deviating by
0.308; that error was caught by this test and corrected. The test stays.)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.design.westergaard import SlabProperties, WheelLoad, stress_edge  # noqa: E402
from src.pavement.thermal import (  # noqa: E402
    DEFAULT_ALPHA,
    bradbury_coefficient,
    check_both_mechanisms,
    combined_stress_buc,
    combined_stress_tdc,
    warping_stress_edge,
    warping_stress_interior,
)

#: Classical Bradbury (1938) warping coefficient C against L/l.
PUBLISHED_BRADBURY = {
    1: 0.000, 2: 0.040, 3: 0.175, 4: 0.440, 5: 0.720, 6: 0.920, 7: 1.030,
    8: 1.075, 9: 1.080, 10: 1.075, 11: 1.050, 12: 1.000, 13: 0.975, 14: 0.960,
}

#: Tolerance the fit is documented to meet. Do not relax without re-fitting.
BRADBURY_TOL = 0.03


# --------------------------------------------------------------------------- #
# Bradbury coefficient
# --------------------------------------------------------------------------- #
def test_bradbury_fit_accuracy():
    """
    THE ACCURACY CLAIM UNDER TEST.
    The docstring promises +/-0.03 against the published curve over 1 <= L/l <= 14.
    """
    worst, worst_x = 0.0, None
    for x, pub in PUBLISHED_BRADBURY.items():
        got = bradbury_coefficient(x * 1000.0, 1000.0)
        err = abs(got - pub)
        if err > worst:
            worst, worst_x = err, x
    assert worst <= BRADBURY_TOL, (
        f"Bradbury fit deviates by {worst:.4f} at L/l={worst_x} "
        f"(tolerance {BRADBURY_TOL})"
    )


def test_bradbury_peaks_near_nine():
    """The curve must peak in the L/l = 8-10 band, as published."""
    vals = {x: bradbury_coefficient(x * 1000.0, 1000.0) for x in range(1, 15)}
    peak_x = max(vals, key=vals.get)
    assert 7 <= peak_x <= 11, f"peak at L/l={peak_x}, expected 8-10"


def test_bradbury_monotonic_rise_then_fall():
    """C must rise monotonically to the peak and then decline."""
    xs = [x / 2 for x in range(2, 29)]
    vals = [bradbury_coefficient(x * 1000.0, 1000.0) for x in xs]
    peak = vals.index(max(vals))
    assert all(a <= b + 1e-9 for a, b in zip(vals[:peak], vals[1:peak + 1]))
    assert all(a >= b - 1e-9 for a, b in zip(vals[peak:], vals[peak + 1:]))


def test_bradbury_short_slab_no_restraint():
    """A slab short relative to l is nearly free to curl -> negligible restraint."""
    assert bradbury_coefficient(500.0, 1000.0) < 0.05


def test_bradbury_never_negative():
    for x in (0.1, 0.5, 1, 5, 10, 20, 50):
        assert bradbury_coefficient(x * 1000.0, 1000.0) >= 0.0


def test_bradbury_is_continuous():
    """No discontinuity anywhere (required for the downstream optimiser)."""
    prev = bradbury_coefficient(100.0, 1000.0)
    for i in range(2, 300):
        cur = bradbury_coefficient(i * 100.0, 1000.0)
        assert abs(cur - prev) < 0.05, f"jump at L/l={i/10}"
        prev = cur


def test_bradbury_validation():
    for bad in (lambda: bradbury_coefficient(-1.0, 1000.0),
                lambda: bradbury_coefficient(1000.0, 0.0)):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError("invalid input accepted")


# --------------------------------------------------------------------------- #
# Warping stress
# --------------------------------------------------------------------------- #
def test_warping_stress_formula():
    """sigma = C E alpha dT / 2."""
    got = warping_stress_edge(E=30_000.0, alpha=10e-6, delta_T=20.0, C=1.0)
    assert math.isclose(got, 30_000.0 * 10e-6 * 20.0 / 2.0, rel_tol=1e-12)


def test_warping_scales_linearly_with_gradient():
    a = warping_stress_edge(30_000.0, DEFAULT_ALPHA, 10.0, 0.8)
    b = warping_stress_edge(30_000.0, DEFAULT_ALPHA, 20.0, 0.8)
    assert math.isclose(b / a, 2.0, rel_tol=1e-12)


def test_warping_sign_independent():
    """Magnitude only; the mechanism check applies the sense of the gradient."""
    a = warping_stress_edge(30_000.0, DEFAULT_ALPHA, 15.0, 0.8)
    b = warping_stress_edge(30_000.0, DEFAULT_ALPHA, -15.0, 0.8)
    assert math.isclose(a, b, rel_tol=1e-12)


def test_interior_warping_exceeds_edge_for_biaxial_restraint():
    """Biaxial restraint at the interior produces higher warping stress than uniaxial."""
    edge = warping_stress_edge(30_000.0, DEFAULT_ALPHA, 16.0, 1.0)
    interior = warping_stress_interior(30_000.0, DEFAULT_ALPHA, 16.0, 1.0, 1.0, 0.15)
    assert interior > edge


def test_higher_alpha_increases_warping():
    """Aggregate type matters: quartzite (high alpha) warps more than limestone."""
    low = warping_stress_edge(30_000.0, 8e-6, 16.0, 0.8)
    high = warping_stress_edge(30_000.0, 12e-6, 16.0, 0.8)
    assert high > low


# --------------------------------------------------------------------------- #
# Combined mechanisms
# --------------------------------------------------------------------------- #
def test_buc_adds_full_load_and_warping():
    assert math.isclose(combined_stress_buc(2.0, 1.5), 3.5, rel_tol=1e-12)


def test_tdc_uses_reduced_load_component():
    """In the TDC configuration only part of the edge-load stress is mobilised."""
    assert combined_stress_tdc(2.0, 1.5, 0.66) < combined_stress_buc(2.0, 1.5)


def test_tdc_axle_factor_validation():
    for f in (-0.1, 1.1):
        try:
            combined_stress_tdc(2.0, 1.0, f)
        except ValueError:
            continue
        raise AssertionError("invalid axle_factor accepted")


def test_thermal_effects_increase_stress_ratio():
    """
    THE CENTRAL FINDING: omitting thermal warping materially under-states the
    stress ratio, and therefore materially under-states fatigue damage.
    """
    slab = SlabProperties(h=300.0, E=30_000.0, mu=0.15, k=0.08)
    MR = 4.5
    sigma_load = stress_edge(slab, WheelLoad.from_pressure(P=75_000.0, p=0.8))
    res = check_both_mechanisms(
        load_edge_stress=sigma_load, E=slab.E,
        delta_T_day=16.8, delta_T_night=8.4,
        slab_length_mm=4500.0, slab_width_mm=3500.0,
        radius_rel_stiffness_mm=slab.l, modulus_of_rupture=MR,
    )
    assert res["governing"].stress_ratio > sigma_load / MR
    assert res["governing"].stress_ratio > 1.25 * (sigma_load / MR)


def test_buc_governs_under_large_day_gradient():
    slab = SlabProperties(h=300.0, E=30_000.0, mu=0.15, k=0.08)
    sigma = stress_edge(slab, WheelLoad.from_pressure(P=75_000.0, p=0.8))
    res = check_both_mechanisms(sigma, slab.E, 20.0, 5.0, 4500.0, 3500.0, slab.l, 4.5)
    assert res["governing"].mechanism == "BUC"


def test_zero_gradient_reduces_to_load_only():
    """
    CRITICAL: with no temperature differential the BUC check must return exactly
    the load-only stress. This proves the thermal layer extends rather than
    perturbs the existing engine.
    """
    slab = SlabProperties(h=300.0, E=30_000.0, mu=0.15, k=0.08)
    sigma = stress_edge(slab, WheelLoad.from_pressure(P=75_000.0, p=0.8))
    res = check_both_mechanisms(sigma, slab.E, 0.0, 0.0, 4500.0, 3500.0, slab.l, 4.5)
    assert math.isclose(res["BUC"].total_stress, sigma, rel_tol=1e-12)


def test_governing_flag_set_once():
    slab = SlabProperties(h=300.0, E=30_000.0, mu=0.15, k=0.08)
    sigma = stress_edge(slab, WheelLoad.from_pressure(P=75_000.0, p=0.8))
    res = check_both_mechanisms(sigma, slab.E, 16.8, 8.4, 4500.0, 3500.0, slab.l, 4.5)
    assert res["governing"].governs is True
    assert res["governing"].mechanism in ("BUC", "TDC")


def test_shorter_slab_reduces_warping():
    """
    Practical design lever: shortening the slab (closer joint spacing) reduces
    warping stress. This is why joint spacing matters.
    """
    slab = SlabProperties(h=300.0, E=30_000.0, mu=0.15, k=0.08)
    sigma = stress_edge(slab, WheelLoad.from_pressure(P=75_000.0, p=0.8))
    long_slab = check_both_mechanisms(sigma, slab.E, 16.8, 8.4, 5500.0, 3500.0,
                                      slab.l, 4.5)
    short_slab = check_both_mechanisms(sigma, slab.E, 16.8, 8.4, 3500.0, 3500.0,
                                       slab.l, 4.5)
    assert short_slab["BUC"].warping_stress < long_slab["BUC"].warping_stress


def test_modulus_of_rupture_validation():
    try:
        check_both_mechanisms(2.0, 30_000.0, 16.0, 8.0, 4500.0, 3500.0, 900.0, 0.0)
    except ValueError:
        return
    raise AssertionError("zero MR accepted")


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
