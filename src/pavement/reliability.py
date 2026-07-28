"""
SETU — Layer 2: probabilistic propagation (Monte Carlo reliability).

PURPOSE
-------
Conventional IRC:58 design treats k, flexural strength, temperature differential and
traffic as single deterministic values, then applies a blanket safety margin. In reality
each is a distribution that varies along the alignment. That mismatch is why concrete is
wasted where conditions are favourable and slabs fail early where they are not.

This module propagates input uncertainty through the mechanistic core and returns:
    - the distribution of cumulative fatigue damage,
    - the probability of failure  P(CFD > 1),
    - the reliability-based thickness required for a target reliability.

DESIGN NOTE (Directive III — justifiable actions)
-------------------------------------------------
This is a *reliability analysis built on top of* the IRC:58 deterministic framework.
It does not replace or contradict the code: at the mean of every input it reduces to
the standard calculation. It adds information the code does not provide — namely how
much margin actually exists. Any submitted design must still satisfy the deterministic
codal check; SETU output is decision support for where to add or remove material.

Dependencies: standard library only (uses `random`, not numpy, so it runs anywhere).
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

from .damage import (
    AxleLoadGroup,
    cumulative_fatigue_damage,
)

__all__ = [
    "Uncertain",
    "PavementUncertainty",
    "ReliabilityResult",
    "monte_carlo_damage",
    "required_thickness_for_reliability",
]


# --------------------------------------------------------------------------- #
# Uncertain quantities
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Uncertain:
    """
    A quantity described by a distribution rather than a single value.

    mean : central value
    cov  : coefficient of variation (std / mean), dimensionless
    dist : 'normal' | 'lognormal' | 'deterministic'

    Lognormal is the default for strictly positive engineering quantities
    (strength, stiffness) because it cannot produce negative samples.
    """

    mean: float
    cov: float = 0.0
    dist: str = "lognormal"

    def __post_init__(self) -> None:
        if self.cov < 0:
            raise ValueError("Coefficient of variation must be non-negative.")
        if self.dist not in ("normal", "lognormal", "deterministic"):
            raise ValueError(f"Unknown distribution: {self.dist}")

    def sample(self, rng: random.Random) -> float:
        """Draw one sample."""
        if self.cov == 0.0 or self.dist == "deterministic":
            return self.mean
        if self.dist == "normal":
            return rng.gauss(self.mean, self.cov * self.mean)
        # lognormal, parameterised by the mean and CoV of the underlying variable
        sigma_ln = math.sqrt(math.log(1.0 + self.cov ** 2))
        mu_ln = math.log(self.mean) - 0.5 * sigma_ln ** 2
        return math.exp(rng.gauss(mu_ln, sigma_ln))


@dataclass(frozen=True)
class PavementUncertainty:
    """
    Uncertainty description for one pavement segment.

    Typical coefficients of variation observed in practice (indicative; replace with
    project-specific values from the client's own test records wherever available):

        modulus of subgrade reaction k .... 0.20 - 0.35  (highly variable)
        flexural strength MR .............. 0.10 - 0.15
        elastic modulus E ................. 0.10 - 0.15
        slab thickness h .................. 0.02 - 0.05  (construction tolerance)
        traffic volume .................... 0.15 - 0.30  (projection error)
    """

    k: Uncertain
    modulus_of_rupture: Uncertain
    E: Uncertain
    thickness: Uncertain
    traffic_multiplier: Uncertain = Uncertain(1.0, 0.20, "lognormal")
    mu: float = 0.15


@dataclass
class ReliabilityResult:
    """Outcome of a Monte Carlo reliability analysis."""

    samples: list[float]
    probability_of_failure: float
    reliability: float
    mean_damage: float
    median_damage: float
    p90_damage: float
    n_simulations: int

    def percentile(self, p: float) -> float:
        """Return the p-th percentile (0-100) of the damage distribution."""
        if not 0.0 <= p <= 100.0:
            raise ValueError("Percentile must be in [0, 100].")
        s = sorted(self.samples)
        if len(s) == 1:
            return s[0]
        idx = (len(s) - 1) * p / 100.0
        lo, hi = int(math.floor(idx)), int(math.ceil(idx))
        if lo == hi:
            return s[lo]
        return s[lo] + (s[hi] - s[lo]) * (idx - lo)

    @property
    def reliability_index_beta(self) -> float:
        """
        Approximate reliability index beta for the limit state g = 1 - CFD.

        Uses the mean/std of the damage samples (first-order approximation).
        Returns +inf when no variability is present.
        """
        if len(self.samples) < 2:
            return float("inf")
        sd = statistics.pstdev(self.samples)
        if sd == 0.0:
            return float("inf")
        return (1.0 - self.mean_damage) / sd


# --------------------------------------------------------------------------- #
# Monte Carlo
# --------------------------------------------------------------------------- #
def monte_carlo_damage(
    unc: PavementUncertainty,
    spectrum: list[AxleLoadGroup],
    n_sim: int = 5000,
    seed: int | None = 42,
    tyre_pressure: float = 0.8,
) -> ReliabilityResult:
    """
    Propagate input uncertainty through the IRC:58 cumulative damage calculation.

    Returns the damage distribution and P(CFD > 1.0).

    `seed` is fixed by default so results are reproducible — essential for an
    auditable engineering report. Pass seed=None for a fresh stream.
    """
    # Imported here to keep the module importable without the design package on path
    from ..design.westergaard import SlabProperties, WheelLoad, stress_edge

    if n_sim < 1:
        raise ValueError("n_sim must be >= 1.")

    rng = random.Random(seed)
    samples: list[float] = []

    for _ in range(n_sim):
        h = unc.thickness.sample(rng)
        E = unc.E.sample(rng)
        k = unc.k.sample(rng)
        mr = unc.modulus_of_rupture.sample(rng)
        tm = unc.traffic_multiplier.sample(rng)

        # Guard against non-physical samples from heavy-tailed draws
        h = max(h, 50.0)
        E = max(E, 1_000.0)
        k = max(k, 0.005)
        mr = max(mr, 0.5)

        slab = SlabProperties(h=h, E=E, mu=unc.mu, k=k)

        def stress_fn(load_N: float, _slab=slab) -> float:
            return stress_edge(
                _slab, WheelLoad.from_pressure(P=load_N / 2.0, p=tyre_pressure)
            )

        scaled = [
            AxleLoadGroup(g.label, g.load_N, g.repetitions * tm) for g in spectrum
        ]
        res = cumulative_fatigue_damage(scaled, stress_fn, mr)
        # Cap at a large finite value so statistics remain computable
        samples.append(min(res.total_damage, 1e6))

    failures = sum(1 for s in samples if s > 1.0)
    pf = failures / len(samples)
    ordered = sorted(samples)

    return ReliabilityResult(
        samples=samples,
        probability_of_failure=pf,
        reliability=1.0 - pf,
        mean_damage=statistics.fmean(samples),
        median_damage=statistics.median(ordered),
        p90_damage=ordered[min(int(0.90 * (len(ordered) - 1)), len(ordered) - 1)],
        n_simulations=len(samples),
    )


def required_thickness_for_reliability(
    unc: PavementUncertainty,
    spectrum: list[AxleLoadGroup],
    target_reliability: float = 0.90,
    h_min: float = 150.0,
    h_max: float = 450.0,
    tol: float = 5.0,
    n_sim: int = 2000,
    seed: int | None = 42,
) -> tuple[float, ReliabilityResult]:
    """
    Bisection search for the minimum slab thickness meeting a target reliability.

    THIS IS THE COMMERCIAL CORE OF SETU PRODUCT (A).

    Instead of one deterministic thickness plus a blanket safety factor applied
    uniformly along the alignment, this returns the thickness actually required to
    achieve the specified reliability *given the local variability of this segment*.

    Where conditions are favourable the required thickness falls (concrete and CO2
    saved); where they are poor it rises (early failure prevented). The saving and
    the added safety come from the same computation.

    Returns (thickness_mm, reliability_result_at_that_thickness).
    Thickness is rounded up to the nearest `tol` mm for constructability.
    """
    if not 0.0 < target_reliability < 1.0:
        raise ValueError("target_reliability must be in (0, 1).")
    if h_min >= h_max:
        raise ValueError("h_min must be less than h_max.")

    def reliability_at(h: float) -> ReliabilityResult:
        trial = PavementUncertainty(
            k=unc.k,
            modulus_of_rupture=unc.modulus_of_rupture,
            E=unc.E,
            thickness=Uncertain(h, unc.thickness.cov, unc.thickness.dist),
            traffic_multiplier=unc.traffic_multiplier,
            mu=unc.mu,
        )
        return monte_carlo_damage(trial, spectrum, n_sim=n_sim, seed=seed)

    res_max = reliability_at(h_max)
    if res_max.reliability < target_reliability:
        # Even the thickest slab considered cannot meet the target: report honestly.
        return h_max, res_max

    lo, hi = h_min, h_max
    best = res_max
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        res = reliability_at(mid)
        if res.reliability >= target_reliability:
            hi, best = mid, res
        else:
            lo = mid

    thickness = math.ceil(hi / tol) * tol
    return thickness, best


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.pavement.damage import AxleLoadGroup as ALG  # noqa: E402

    spectrum = [
        ALG("Single axle 10-12 t", 110_000.0, 150_000),
        ALG("Single axle 12-14 t", 130_000.0, 90_000),
        ALG("Single axle 14-16 t", 150_000.0, 40_000),
        ALG("Single axle 16-18 t", 170_000.0, 12_000),
        ALG("Single axle 18-20 t", 190_000.0, 3_000),
    ]

    print("=" * 84)
    print(" SETU — RELIABILITY-BASED ANALYSIS  (Layer 2: Monte Carlo)")
    print("=" * 84)

    # Two segments of the same road, differing only in subgrade quality.
    segments = {
        "Ch. 0.0-4.2 km  (good subgrade)": Uncertain(0.11, 0.22),
        "Ch. 4.2-7.8 km  (poor subgrade)": Uncertain(0.045, 0.32),
    }

    baseline_h = 300.0  # what a uniform deterministic design would specify throughout
    total_saved = 0.0

    for name, k_unc in segments.items():
        unc = PavementUncertainty(
            k=k_unc,
            modulus_of_rupture=Uncertain(4.5, 0.12),
            E=Uncertain(30_000.0, 0.12),
            thickness=Uncertain(baseline_h, 0.03),
            traffic_multiplier=Uncertain(1.0, 0.20),
        )
        res = monte_carlo_damage(unc, spectrum, n_sim=3000)
        h_req, res_req = required_thickness_for_reliability(
            unc, spectrum, target_reliability=0.90, n_sim=1500
        )
        delta = baseline_h - h_req
        total_saved += delta

        print(f"\n {name}")
        print(f"   k = {k_unc.mean:.3f} MPa/mm (CoV {k_unc.cov:.0%})")
        print(f"   At uniform h = {baseline_h:.0f} mm:")
        print(f"       mean CFD ......... {res.mean_damage:.3f}")
        print(f"       median CFD ....... {res.median_damage:.3f}")
        print(f"       90th pct CFD ..... {res.p90_damage:.3f}")
        print(f"       P(failure) ....... {res.probability_of_failure:.1%}")
        print(f"       reliability ...... {res.reliability:.1%}")
        print(f"   Thickness for 90% reliability .... {h_req:.0f} mm  "
              f"({'SAVE' if delta > 0 else 'ADD'} {abs(delta):.0f} mm)")

    print("\n" + "-" * 84)
    print(" Uniform design applies one thickness everywhere. Reliability-based design")
    print(" moves material to where it is actually needed — saving concrete on good")
    print(" ground and preventing early failure on poor ground, from one computation.")
    print("=" * 84)
