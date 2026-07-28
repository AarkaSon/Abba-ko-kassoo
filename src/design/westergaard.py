"""
Analytical rigid-pavement slab response — Westergaard theory + IRC:58 constructs.

PURPOSE
-------
Licence-free verification baseline. Any future Abaqus / CalculiX slab model must
reproduce these closed-form results (within the known limits of the theory) before
its nonlinear output is trusted.

REFERENCES
----------
[1] Westergaard, H.M. (1926) "Stresses in Concrete Pavements Computed by Theoretical
    Analysis", Public Roads 7(2), 25-35.
[2] Ioannides, A.M., Thompson, M.R., Barenberg, E.J. (1985) "Westergaard Solutions
    Reconsidered", TRR 1043 — corrected edge/corner forms used here.
[3] IRC:58-2015, "Guidelines for the Design of Plain Jointed Rigid Pavements for
    Highways", Indian Roads Congress. Radius of relative stiffness, cl. 6.
[4] Teller, L.W. & Sutherland, E.C. (1935) — corner-load formulation.

UNITS (SI, consistent)
----------------------
    length  : mm
    force   : N
    stress  : MPa (N/mm^2)
    k       : MPa/mm  (= N/mm^3).  NOTE: 1 kg/cm^3 = 98.0665 MPa/mm.
                                   Typical IRC subgrade k = 0.03-0.30 MPa/mm.

No third-party dependencies — standard library only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "SlabProperties",
    "WheelLoad",
    "radius_of_relative_stiffness",
    "equivalent_radius_westergaard",
    "stress_interior",
    "stress_edge",
    "stress_corner",
    "deflection_interior",
    "deflection_corner",
    "modulus_of_subgrade_reaction_composite",
    "analyse",
]


# ----------------------------------------------------------------------------- #
# Data containers
# ----------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SlabProperties:
    """Concrete slab on a Winkler (dense-liquid) foundation."""

    h: float             # slab thickness                          [mm]
    E: float             # elastic modulus of concrete             [MPa]
    mu: float = 0.15     # Poisson's ratio (IRC:58 cl. 6.3 -> 0.15) [-]
    k: float = 0.08      # modulus of subgrade reaction            [MPa/mm]

    def __post_init__(self) -> None:
        if self.h <= 0 or self.E <= 0 or self.k <= 0:
            raise ValueError("h, E and k must be positive.")
        if not 0.0 <= self.mu < 0.5:
            raise ValueError("Poisson's ratio must lie in [0, 0.5).")

    @property
    def flexural_rigidity(self) -> float:
        """D = E h^3 / (12 (1 - mu^2))   [N.mm]"""
        return self.E * self.h ** 3 / (12.0 * (1.0 - self.mu ** 2))

    @property
    def l(self) -> float:
        """Radius of relative stiffness [mm]."""
        return radius_of_relative_stiffness(self.E, self.h, self.mu, self.k)


@dataclass(frozen=True)
class WheelLoad:
    """Single equivalent circular wheel load."""

    P: float             # total load on the contact area          [N]
    a: float             # radius of the circular contact area     [mm]

    def __post_init__(self) -> None:
        if self.P <= 0 or self.a <= 0:
            raise ValueError("P and a must be positive.")

    @property
    def tyre_pressure(self) -> float:
        """Contact pressure [MPa]."""
        return self.P / (math.pi * self.a ** 2)

    @classmethod
    def from_pressure(cls, P: float, p: float) -> "WheelLoad":
        """Build from load P [N] and tyre pressure p [MPa]."""
        if p <= 0:
            raise ValueError("Tyre pressure must be positive.")
        return cls(P=P, a=math.sqrt(P / (math.pi * p)))


# ----------------------------------------------------------------------------- #
# Fundamental quantities
# ----------------------------------------------------------------------------- #
def radius_of_relative_stiffness(E: float, h: float, mu: float, k: float) -> float:
    """
    l = [ E h^3 / (12 (1 - mu^2) k) ] ^ 0.25      [mm]      — Westergaard [1], IRC:58 [3]

    Physical meaning: the length over which the slab distributes a concentrated load
    into the subgrade. Larger l -> stiffer slab relative to subgrade -> wider load spread.
    """
    return (E * h ** 3 / (12.0 * (1.0 - mu ** 2) * k)) ** 0.25


def equivalent_radius_westergaard(a: float, h: float) -> float:
    """
    Westergaard's equivalent radius of resisting section, b [mm].

        b = sqrt(1.6 a^2 + h^2) - 0.675 h      for a < 1.724 h
        b = a                                  otherwise

    Corrects the singularity of plate theory under a concentrated load by accounting
    for the shear-deformable zone directly beneath the load.
    """
    return math.sqrt(1.6 * a * a + h * h) - 0.675 * h if a < 1.724 * h else a


# ----------------------------------------------------------------------------- #
# Stresses
# ----------------------------------------------------------------------------- #
def stress_interior(slab: SlabProperties, load: WheelLoad) -> float:
    """
    Maximum tensile bending stress at the *bottom* of the slab, load at slab interior.

        sigma_i = 3 P (1 + mu) / (2 pi h^2) * [ ln(l / b) + 0.6159 ]

    Ref: Westergaard [1]; form as corrected by Ioannides et al. [2].
    """
    b = equivalent_radius_westergaard(load.a, slab.h)
    return (3.0 * load.P * (1.0 + slab.mu) / (2.0 * math.pi * slab.h ** 2)) * (
        math.log(slab.l / b) + 0.6159
    )


def stress_edge(slab: SlabProperties, load: WheelLoad) -> float:
    """
    Maximum tensile stress at the bottom of the slab, load at a free edge
    (circular-load case) — the governing condition for bottom-up cracking in IRC:58.

        sigma_e = 3 P (1 + mu) / (pi (3 + mu) h^2)
                  * [ ln(E h^3 / (100 k a^4)) + 1.84 - 4mu/3 + (1-mu)/2 + 1.18 (1+2mu) a/l ]

    Ref: Westergaard, as presented in Ioannides et al. [2].
    """
    mu, h, k, E = slab.mu, slab.h, slab.k, slab.E
    a, P, l = load.a, load.P, slab.l
    term = (
        math.log(E * h ** 3 / (100.0 * k * a ** 4))
        + 1.84
        - 4.0 * mu / 3.0
        + (1.0 - mu) / 2.0
        + 1.18 * (1.0 + 2.0 * mu) * a / l
    )
    return 3.0 * P * (1.0 + mu) / (math.pi * (3.0 + mu) * h ** 2) * term


def stress_corner(slab: SlabProperties, load: WheelLoad) -> float:
    """
    Maximum tensile stress at the *top* of the slab near a corner.

        sigma_c = 3 P / h^2 * [ 1 - ( a_sqrt2 / l ) ^ 0.6 ] ,   a_sqrt2 = a * sqrt(2)

    Ref: Westergaard / Teller & Sutherland [4]. Governs top-down corner cracking.
    """
    a1 = load.a * math.sqrt(2.0)
    return (3.0 * load.P / slab.h ** 2) * (1.0 - (a1 / slab.l) ** 0.6)


# ----------------------------------------------------------------------------- #
# Deflections
# ----------------------------------------------------------------------------- #
def deflection_interior(slab: SlabProperties, load: WheelLoad) -> float:
    """
    Interior-load deflection [mm]:

        d_i = P / (8 k l^2) * { 1 + (1/2pi) [ ln(a/2l) + gamma - 5/4 ] (a/l)^2 }

    gamma = 0.5772157 (Euler-Mascheroni).
    """
    gamma = 0.5772156649
    a_l = load.a / slab.l
    return (load.P / (8.0 * slab.k * slab.l ** 2)) * (
        1.0 + (1.0 / (2.0 * math.pi)) * (math.log(a_l / 2.0) + gamma - 1.25) * a_l ** 2
    )


def deflection_corner(slab: SlabProperties, load: WheelLoad) -> float:
    """
    Corner-load deflection [mm]:

        d_c = P / (k l^2) * [ 1.1 - 0.88 (a_sqrt2 / l) ]
    """
    a1 = load.a * math.sqrt(2.0)
    return (load.P / (slab.k * slab.l ** 2)) * (1.1 - 0.88 * (a1 / slab.l))


# ----------------------------------------------------------------------------- #
# Foundation helpers
# ----------------------------------------------------------------------------- #
def modulus_of_subgrade_reaction_composite(k_subgrade: float, dgsb_thickness_mm: float) -> float:
    """
    Effective k on top of a granular sub-base — linear interpolation on IRC:58-2015
    Table 4 (DLC excluded; use the code table directly for cemented sub-bases).

    k_subgrade : MPa/mm ; dgsb_thickness_mm : mm  ->  effective k [MPa/mm]
    Justification note: interpolation is an engineering approximation of a tabulated
    relationship; for a submitted design, read the table value directly.
    """
    table = {  # k_subgrade -> {thickness: k_effective}   (MPa/mm)
        0.021: {0: 0.021, 150: 0.038, 225: 0.044, 300: 0.053},
        0.028: {0: 0.028, 150: 0.044, 225: 0.053, 300: 0.062},
        0.042: {0: 0.042, 150: 0.063, 225: 0.075, 300: 0.088},
        0.048: {0: 0.048, 150: 0.075, 225: 0.088, 300: 0.102},
        0.055: {0: 0.055, 150: 0.084, 225: 0.096, 300: 0.117},
        0.062: {0: 0.062, 150: 0.092, 225: 0.108, 300: 0.130},
    }
    ks = min(table, key=lambda x: abs(x - k_subgrade))
    row = table[ks]
    ts = sorted(row)
    t = max(ts[0], min(dgsb_thickness_mm, ts[-1]))
    for lo, hi in zip(ts, ts[1:]):
        if lo <= t <= hi:
            f = 0.0 if hi == lo else (t - lo) / (hi - lo)
            return row[lo] + f * (row[hi] - row[lo])
    return row[ts[-1]]


# ----------------------------------------------------------------------------- #
# Convenience driver
# ----------------------------------------------------------------------------- #
def analyse(slab: SlabProperties, load: WheelLoad) -> dict:
    """Return the full closed-form response set as a dict."""
    return {
        "l_mm": slab.l,
        "b_mm": equivalent_radius_westergaard(load.a, slab.h),
        "contact_pressure_MPa": load.tyre_pressure,
        "sigma_interior_MPa": stress_interior(slab, load),
        "sigma_edge_MPa": stress_edge(slab, load),
        "sigma_corner_MPa": stress_corner(slab, load),
        "deflection_interior_mm": deflection_interior(slab, load),
        "deflection_corner_mm": deflection_corner(slab, load),
    }


# ----------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Illustrative case — geopolymer SLWA slab, placeholder properties.
    # E and h to be replaced once Master's experimental / literature data is ingested.
    slab = SlabProperties(h=250.0, E=30_000.0, mu=0.15, k=0.08)
    load = WheelLoad.from_pressure(P=50_000.0, p=0.8)   # 5 t wheel, 0.8 MPa tyre pressure

    res = analyse(slab, load)

    print("=" * 62)
    print(" WESTERGAARD ANALYTICAL BASELINE — rigid pavement slab")
    print("=" * 62)
    print(f" Slab   : h = {slab.h:.0f} mm | E = {slab.E:,.0f} MPa | mu = {slab.mu} "
          f"| k = {slab.k} MPa/mm")
    print(f" Load   : P = {load.P/1000:.1f} kN | a = {load.a:.1f} mm "
          f"| p = {load.tyre_pressure:.2f} MPa")
    print("-" * 62)
    for key, val in res.items():
        print(f" {key:<26s} = {val:>12.4f}")
    print("=" * 62)
    print(" NOTE: verification baseline only. Warping/thermal stresses, load transfer")
    print("       across joints and material nonlinearity require the FEM model.")
