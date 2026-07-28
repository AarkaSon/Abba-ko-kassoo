"""
Verification tests for the analytical rigid-pavement baseline.

Directive III (JUSTIFIABLE ACTIONS): the FEM model is only trustworthy if the
closed-form baseline it is checked against is itself verified. These tests pin
the analytical layer against published values and physical invariants.

Run:  python3 -m pytest tests/ -v      (or: python3 tests/test_westergaard.py)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from design.westergaard import (  # noqa: E402
    SlabProperties,
    WheelLoad,
    analyse,
    equivalent_radius_westergaard,
    radius_of_relative_stiffness,
)


# --------------------------------------------------------------------------- #
# Reference case — Yoder & Witczak / IRC:58 worked-example scale
#   h = 250 mm, E = 30 GPa, mu = 0.15, k = 0.08 MPa/mm, P = 50 kN, p = 0.8 MPa
# --------------------------------------------------------------------------- #
def _ref():
    return (
        SlabProperties(h=250.0, E=30_000.0, mu=0.15, k=0.08),
        WheelLoad.from_pressure(P=50_000.0, p=0.8),
    )


def test_radius_of_relative_stiffness_known_value():
    """l for the reference slab must be ~840 mm (hand check of the closed form)."""
    l = radius_of_relative_stiffness(30_000.0, 250.0, 0.15, 0.08)
    assert 830.0 < l < 850.0, f"l = {l:.1f} mm outside expected band"


def test_l_scales_as_h_to_the_three_quarters():
    """l ~ h^0.75 : doubling thickness must raise l by 2^0.75 = 1.6818."""
    l1 = radius_of_relative_stiffness(30_000.0, 200.0, 0.15, 0.08)
    l2 = radius_of_relative_stiffness(30_000.0, 400.0, 0.15, 0.08)
    assert math.isclose(l2 / l1, 2.0 ** 0.75, rel_tol=1e-9)


def test_equivalent_radius_branches():
    """b = a once a >= 1.724 h; b < a for a small relative to h (shear correction)."""
    h = 250.0
    thresh = 1.724 * h                                              # = 431.0 mm
    assert equivalent_radius_westergaard(a=141.0, h=h) < 141.0      # a < 1.724h branch
    assert equivalent_radius_westergaard(a=thresh + 50.0, h=h) == thresh + 50.0  # a >= branch


def test_stress_hierarchy_edge_governs():
    """
    Physical invariant: for a free-edge slab the edge-load stress exceeds the
    interior-load stress. This is why IRC:58 designs for the edge condition.
    """
    r = analyse(*_ref())
    assert r["sigma_edge_MPa"] > r["sigma_interior_MPa"] > 0.0


def test_corner_deflection_exceeds_interior():
    """A corner is supported on two free edges -> must deflect more than the interior."""
    r = analyse(*_ref())
    assert r["deflection_corner_mm"] > r["deflection_interior_mm"] > 0.0


def test_stress_inverse_square_in_thickness():
    """
    sigma ~ 1/h^2 dominates: thicker slab -> lower stress. Monotonic decrease is a
    hard requirement for any thickness-optimisation routine built on top of this.
    """
    load = WheelLoad.from_pressure(P=50_000.0, p=0.8)
    sig = [
        analyse(SlabProperties(h=h, E=30_000.0, mu=0.15, k=0.08), load)["sigma_edge_MPa"]
        for h in (200.0, 250.0, 300.0, 350.0)
    ]
    assert all(a > b for a, b in zip(sig, sig[1:])), sig


def test_stiffer_subgrade_reduces_deflection():
    load = WheelLoad.from_pressure(P=50_000.0, p=0.8)
    d_soft = analyse(SlabProperties(250.0, 30_000.0, 0.15, 0.03), load)["deflection_interior_mm"]
    d_stiff = analyse(SlabProperties(250.0, 30_000.0, 0.15, 0.15), load)["deflection_interior_mm"]
    assert d_soft > d_stiff


def test_load_linearity():
    """Westergaard is linear-elastic: doubling P must double every response."""
    slab = SlabProperties(250.0, 30_000.0, 0.15, 0.08)
    a = WheelLoad(P=50_000.0, a=141.0)
    b = WheelLoad(P=100_000.0, a=141.0)
    ra, rb = analyse(slab, a), analyse(slab, b)
    for key in ("sigma_interior_MPa", "sigma_edge_MPa", "sigma_corner_MPa",
                "deflection_corner_mm"):
        assert math.isclose(rb[key] / ra[key], 2.0, rel_tol=1e-9), key


def test_input_validation():
    for bad in (
        lambda: SlabProperties(h=-1, E=30_000.0),
        lambda: SlabProperties(h=250.0, E=30_000.0, mu=0.6),
        lambda: WheelLoad(P=0.0, a=100.0),
        lambda: WheelLoad.from_pressure(P=50_000.0, p=0.0),
    ):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError("invalid input was accepted")


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
